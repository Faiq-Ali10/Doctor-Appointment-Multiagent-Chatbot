import json
from utils.llm import LLM_Model
from prompts.qa import system_prompt as qa_system_prompt
from utils.doctor_info import fetch_doctors_info

def medical_answer(question: str) -> str:
    doctor_data = fetch_doctors_info()

    doctor_data_str = json.dumps(doctor_data)
    
    # Format the imported system prompt with the fetched data
    formatted_prompt = qa_system_prompt.format(doctor_data=doctor_data_str)

    # Merge formatted system prompt and user question
    prompt = f"{formatted_prompt}\n\nQuestion: {question}"

    # Get LLM response
    qa_llm = LLM_Model(0.3).get_model()
    llm_response = qa_llm.invoke(prompt)
    
    # Extract content safely:
    if hasattr(llm_response, "content"):
        return str(llm_response.content)  # usually an AIMessage
    elif isinstance(llm_response, str):
        return llm_response
    else:
        # fallback: try to convert to string
        return str(llm_response)
