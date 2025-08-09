from prompts.router import system_prompt
from utils.llm import LLM_Model
from pydantic import BaseModel

class DecideOutput(BaseModel):
    next : str

def decide(query : str) -> str:
    llm = LLM_Model(0.1).get_model()
    query = f"system_prompt : {system_prompt} \n\n query : {query}"
    response = llm.invoke(query)
    content = response.content if hasattr(response, "content") else response
    
    try:
        output = DecideOutput.model_validate_json(str(content))
        if output.next == "Greeting":
            return "Hello, how can I help you with booking or checking availability for doctors?"
        elif output.next == "Out_of_context":
            return "Sorry, I can only assist with medical appointments and related information. How can I help you with that?"
        else:
            return "Medical"
    except Exception as e:
        print(f"[❌ Parsing error] {e}")
        return "Out_of_context"
    
         
         
    
    
    
    


