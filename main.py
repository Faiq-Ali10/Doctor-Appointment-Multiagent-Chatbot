import os
from typing import cast
from urllib import robotparser
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel,  field_validator
from agent import DoctorAppointmentAgent, AgentState
from langchain_core.messages import HumanMessage
from utils.messages import get_consolidated_response
import pandas as pd
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from routing_llm import decide

load_dotenv()
os.environ["LANGSMITH_TRACING"] = str(os.getenv("LANGSMITH_TRACING"))
os.environ["LANGSMITH_ENDPOINT"] = str(os.getenv("LANGSMITH_ENDPOINT"))
os.environ["LANGCHAIN_API_KEY"] = str(os.getenv("LANGCHAIN_API_KEY"))
os.environ["LANGSMITH_PROJECT"] = str(os.getenv("LANGSMITH_PROJECT"))
os.environ["GROQ_API_KEY"] = str(os.getenv("GROQ_API_KEY"))
os.environ["API_URL"] = str(os.getenv("API_URL"))

app = FastAPI()

agent = DoctorAppointmentAgent(0.1, 0.2, 0.1).get_app()

class UserInput(BaseModel):
    query : str
    id : int
    
    @field_validator("id")
    def validate_id_length(cls, v):
        if len(str(v)) != 7:
            raise ValueError("ID must be exactly 7 digits long.")
        return v

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        msg = errors[0].get("msg", "Invalid request")
        return JSONResponse(status_code=400, content=msg)
    return JSONResponse(status_code=400, content={"error": "Error 400: Could not process the request."})

@app.post("/doctor-appointment")
async def execute(data: UserInput) -> dict:
    router = decide(data.query)
    if router == "Medical":
        try:
            query = {
                "messages": [HumanMessage(content=data.query)], 
                "next": "supervisor",
                "reasoning": "",
                "id": data.id,
                "query": data.query  
            }
            
            response = agent.invoke(cast(AgentState, query), config={"recursion_limit": 20})
            
            # Get consolidated response
            final_message = get_consolidated_response(response.get("messages", []))
            
            return {"message": final_message}
            
        except Exception as e:
            print(f"[❌ FastAPI Error] {str(e)}")
            return {"message": "I apologize, but I encountered an error. Please try again."}
    else:
        return {"message": router}
    
@app.get("/doctors-information")
async def get_doctors():
    try:
        df = pd.read_csv("data/data.csv", usecols=["specialization", "doctor_name"])
        unique_doctors = df.drop_duplicates().reset_index(drop=True)
        return unique_doctors.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Doctors information is not available "}