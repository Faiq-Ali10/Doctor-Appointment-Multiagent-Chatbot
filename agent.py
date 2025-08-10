from typing import Literal, cast
from pydantic import BaseModel
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from utils.llm import LLM_Model
from toolkit.tools import *
from prompts import supervisor, booking, information 
import json
import re
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from typing import Sequence
import traceback

class SupervisorOutput(BaseModel):
    next: str
    reasoning: str

class AgentState(MessagesState, total=False):
    query: str
    next: str
    reasoning: str
    id: int
    step_count: int 

class DoctorAppointmentAgent:
    def __init__(self, supervisor_temperature=0.1, information_temperature=0.1, booking_temperature=0.1):
        """
        Initialize the Doctor Appointment Agent with configurable temperatures.
        Lower temperature values make responses more deterministic.
        """
        self.supervisor_prompt = self._create_supervisor_prompt()
        
        self.supervisor_model = LLM_Model(supervisor_temperature).get_model()
        self.information_llm = LLM_Model(information_temperature).get_model()
        self.booking_llm = LLM_Model(booking_temperature).get_model()
    
    def _create_supervisor_prompt(self) -> PromptTemplate:
        """Create the supervisor prompt with proper formatting."""
        
        return PromptTemplate.from_template(
            supervisor.system_prompt + "\n\n{input}"
        )
    
    def format_messages_to_text(self, messages: Sequence[BaseMessage]) -> str:
        """Converts a list of LangChain messages into a clean string format for prompting."""
        lines = []
        for message in messages:
            role = message.type.capitalize()
            content = message.content

            name = getattr(message, 'name', '')
            if name:
                role = f"{role} ({name})"
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
    
    def supervisor_node(self, state: AgentState) -> Command[Literal["information_node", "booking_node", "__end__"]]:
        """
        Supervisor node that routes conversations to appropriate specialized agents.
        """
        try:

            if "step_count" not in state:
                state["step_count"] = 0
            
            state["step_count"] += 1
            
            if state["step_count"] > 10:
                print("[⚠️ Warning] Maximum steps reached, forcing FINISH")
                return Command(
                    goto="__end__",
                    update={
                        "reasoning": "Maximum conversation steps reached. Please start a new conversation if you need further assistance.",
                        "next": "__end__"
                    }
                )
            
            messages = []
            if "query" in state and state["query"]:
                messages.append(HumanMessage(content=state["query"]))
            
            if "messages" in state and state["messages"]:
                messages.extend(state["messages"])
            
            filtered_messages = [msg for msg in messages if isinstance(msg, BaseMessage)]
            formatted_input = self.supervisor_prompt.format(input=self.format_messages_to_text(filtered_messages))
            
            print(f"[🔍 Debug] Formatted input to LLM:\n{formatted_input}")
            
            raw_response = self.supervisor_model.invoke(formatted_input)
            print(f"[🔍 Debug] Raw LLM response type: {type(raw_response)}")
            print(f"[🔍 Debug] Raw LLM response: {raw_response}")
            
            if hasattr(raw_response, 'content'):
                response_content = raw_response.content
            elif isinstance(raw_response, str):
                response_content = raw_response
            else:
                response_content = str(raw_response)
            
            print(f"[🔍 Debug] Response content: {response_content}")
            

            result = self._parse_supervisor_response(str(response_content))
            
            print(f"[🎯 Supervisor Decision] Step {state['step_count']}: next={result.next}, reasoning={result.reasoning}")
            
            next_step = result.next.strip().upper()
            state["reasoning"] = result.reasoning
            
            # Determine next route
            if next_step == "FINISH":
                state["next"] = "__end__"
                goto = "__end__"
            else:
                state["next"] = result.next
                goto = result.next
            
            # Validate route
            valid_routes = ["information_node", "booking_node", "__end__"]
            if goto not in valid_routes:
                print(f"[❌ Invalid Route] '{goto}' is not valid, defaulting to __end__")
                goto = "__end__"
            
            goto = cast(Literal["information_node", "booking_node", "__end__"], goto)
            
            # Add user ID context for first message
            update_dict = {"reasoning": state["reasoning"], "step_count": state["step_count"]}
            if len(state.get("messages", [])) == 0 and state.get("id"):
                update_dict["messages"] = [HumanMessage(content=f"User ID: {state.get('id')}")]
            
            return Command(goto=goto, update=update_dict)
            
        except Exception as e:
            print(f"[❌ Supervisor Error] {str(e)}")
            print(f"[❌ Full traceback] {traceback.format_exc()}")
            return Command(
                goto="__end__",
                update={
                    "reasoning": "An error occurred while processing your request. Please try again.",
                    "next": "__end__"
                }
            )
    
    def _parse_supervisor_response(self, response_content: str) -> SupervisorOutput:
        """
        Robust JSON parsing for supervisor responses with multiple fallback strategies.
        """
        try:
            parsed_json = json.loads(response_content)
            return SupervisorOutput(**parsed_json)
        except json.JSONDecodeError:
            json_matches = re.findall(r'\{[^}]*\}', response_content)
            
            for json_match in json_matches:
                try:
                    parsed_json = json.loads(json_match)
                    if 'next' in parsed_json and 'reasoning' in parsed_json:
                        return SupervisorOutput(**parsed_json)
                except json.JSONDecodeError:
                    continue
            
            next_match = re.search(r'"next":\s*"([^"]+)"', response_content)
            reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', response_content)
            
            if next_match and reasoning_match:
                return SupervisorOutput(next=next_match.group(1), reasoning=reasoning_match.group(1))
            
            content_lower = response_content.lower()
            if any(word in content_lower for word in ['book', 'schedule', 'appointment', 'reschedule', 'cancel']):
                return SupervisorOutput(next="booking_node", reasoning="Detected booking-related request")
            elif any(word in content_lower for word in ['availability', 'available', 'doctor', 'specialization', 'faq']):
                return SupervisorOutput(next="information_node", reasoning="Detected information request")
            else:
                return SupervisorOutput(next="FINISH", reasoning="Unable to determine next action from response")
        except Exception as e:
            print(f"[❌ Parsing Error] {str(e)}")
            return SupervisorOutput(next="FINISH", reasoning="Error parsing supervisor response")
    
    def information_node(self, state: AgentState) -> Command[Literal["supervisor"]]:
        """
        Information node that handles doctor availability and FAQ queries.
        """
        try:
            system_prompt = information.system_prompt
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("placeholder", "{messages}")
            ])
            
            # Create agent with information tools
            agent = create_react_agent(
                model=self.information_llm,
                tools=[doctor_available, specialization_available],
                verbose=True,
                prompt=prompt
            )
            
            result = agent.invoke(state)
            print(f"[📋 Information Node] Result: {result}")
            
            agent_response = result["messages"][-1].content
            
            return Command(
                goto="supervisor",
                update={
                    "messages": state["messages"] + [
                        AIMessage(content=agent_response, name="information_node")
                    ]
                }
            )
            
        except Exception as e:
            print(f"[❌ Information Node Error] {str(e)}")
            error_message = "I apologize, but I encountered an error while retrieving information. Please try your request again."
            
            return Command(
                goto="supervisor",
                update={
                    "messages": state["messages"] + [
                        AIMessage(content=error_message, name="information_node")
                    ]
                }
            )
    
    def booking_node(self, state : AgentState) -> Command[Literal["supervisor"]]:
        user_id = state.get("id", "Unknown")
        original_query = state.get("query", "")
        
        system_prompt = booking.system_prompt.format(user_id=user_id, original_query=original_query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}")
        ])
        
        agent = create_react_agent(model=self.booking_llm, tools=[set_appointment, cancel_appointment, reschedule_appointment], verbose=True, prompt=prompt)
        result = agent.invoke(state)
        print("@@booking",result,"booking@@")
        
        return Command(goto="supervisor", update= {"messages" : state["messages"] + [AIMessage(content=result["messages"][-1].content, name="booking_node")]})
        
    def get_app(self):
        """
        Create and compile the state graph workflow.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("information_node", self.information_node)
        workflow.add_node("booking_node", self.booking_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        return workflow.compile()
        