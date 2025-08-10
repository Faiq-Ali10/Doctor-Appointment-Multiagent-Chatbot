from prompts.router import system_prompt
from utils.llm import LLM_Model
from pydantic import BaseModel
from qa_llm import medical_answer

class DecideOutput(BaseModel):
    next : str

def decide(original_query : str) -> str:
    llm = LLM_Model(0.1).get_model()
    query = f"system_prompt : {system_prompt} \n\n query : {original_query}"
    response = llm.invoke(query)
    content = response.content if hasattr(response, "content") else response
    
    try:
        output = DecideOutput.model_validate_json(str(content))
        print(output.next)
        if output.next == "__Greeting__":
            return "Hello, how can I help you with booking or checking availability for doctors?"
        elif output.next == "__Out_of_context__":
            return "Sorry, I can only assist with medical appointments and related information. How can I help you with that?"
        elif output.next == "__Agent__":
            return "__Agent__"
        else:
            return medical_answer(original_query)
    except Exception as e:
        print(f"[❌ Parsing error] {e}")
        return "Out_of_context"
    
         
         
    
    
    
    


