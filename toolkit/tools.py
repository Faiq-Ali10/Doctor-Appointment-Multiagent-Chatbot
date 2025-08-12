from typing import Annotated
import numpy as np
from langchain.tools import tool
import pandas as pd
from toolkit.helper import get_doctors_names, get_specialization_names, convert_to_12

DOCTORS = get_doctors_names()
SPECIALIZATIONS = get_specialization_names()

@tool
def doctor_available(date : Annotated[str, "Date and time in DD-MM-YYYY format"], doctor : Annotated[str, f"Valid doctor name in database: {', '.join(DOCTORS)}"]):
    """
    Checking the database if we have availability for the specific doctor.
    The parameters should be mentioned by the user in the query
    """
    if doctor not in DOCTORS:
       return f"There is no Doctor : {doctor} registered!" 
   
    df = pd.read_csv("data/data.csv")
    
    availability = df[(df["date_slot"].apply(lambda d : d.split(" ")[0]) == date)&(df["doctor_name"] == doctor)&(df["is_available"] == True)]["date_slot"].to_list()
    available_time = [time.split(" ")[1] for time in availability]
    
    if len(available_time) == 0:
        return f"No Availability for Dr. {doctor} on {date}"
    
    return f"Availability for Dr. {doctor} on {date} are : {', '.join(available_time)}"

@tool
def specialization_available(date : Annotated[str, "Date and time in DD-MM-YYYY format"], specialization : Annotated[str, f"Valid doctor name in database: {', '.join(SPECIALIZATIONS)}"]):
    """
    Checking the database if we have availability for the specific specialization.
    The parameters should be mentioned by the user in the query
    """
    if specialization not in SPECIALIZATIONS:
       return f"There is no {specialization} doctors registered!" 
   
    df = pd.read_csv("data/data.csv")
    
    availability = df[(df["date_slot"].apply(lambda d : d.split(" ")[0]) == date)&(df["specialization"] == specialization)&(df["is_available"] == True)].groupby(["doctor_name", "specialization"])["date_slot"].apply(list).reset_index(name = "Available Slots")
    
    if len(availability) == 0:
        return f"No Availability for {specialization} on {date}"
    else:
        output = f"Availabilty on {date}:\n"
        for row in availability.values:
            output += row[0] + ". Available slots: \n" + ', \n'.join([convert_to_12(value.split(" ")[1])for value in row[2]])+'\n'
            
        return output
    
@tool
def set_appointment(date: Annotated[str, "Date and time in DD-MM-YYYY format"], id: Annotated[str, "Patient ID"], doctor : Annotated[str, f"Valid doctor name in database: {', '.join(DOCTORS)}"]):
    """
    Set appointment or slot with the doctor.
    The parameters MUST be mentioned by the user in the query.
    """
    f_id = float(id)
    if doctor not in DOCTORS:
       return f"There is no Doctor : {doctor} registered!" 
   
    df = pd.read_csv("data/data.csv")
    availability = df[(df["date_slot"] == date)&(df["doctor_name"] == doctor)&(df["is_available"] == True)]
    if len(availability) == 0:
        return f"No available appointments on {date} for Dr. {doctor}."
    elif len(availability) == 1:
        df.loc[(df["date_slot"] == date)&(df["doctor_name"] == doctor)&(df["is_available"] == True), ['is_available','patient_to_attend']] = [False, f_id] 
        df.to_csv(f'data/data.csv', index = False)

        return f"Successfully got appointment on {date} for Dr. {doctor}."
    
@tool
def cancel_appointment(date: Annotated[str, "Date and time in DD-MM-YYYY format"], id: Annotated[str, "Patient ID"], doctor : Annotated[str, f"Valid doctor name in database: {', '.join(DOCTORS)}"]):
    """
    Canceling an appointment.
    The parameters MUST be mentioned by the user in the query.
    """
    f_id = float(id)
    df = pd.read_csv("data/data.csv")
    availability = df[(df["date_slot"] == date)&(df["doctor_name"] == doctor)&(df["is_available"] == False)&(df["patient_to_attend"] == f_id)]
    if len(availability) == 0:
        return f"You don't have any appointment on {date}."
    elif len(availability) == 1:
        df.loc[(df["date_slot"] == date)&(df["is_available"] == False)&(df["doctor_name"] == doctor), ['is_available','patient_to_attend']] = [True, np.nan] 
        df.to_csv(f'data/data.csv', index = False)

        return f"Successfully cancelled appointment on {date}."
    
@tool
def reschedule_appointment(old_date: Annotated[str, "Date and time in DD-MM-YYYY format"], id: Annotated[str, "Patient ID"], new_date: Annotated[str, "Date and time in DD-MM-YYYY format"], old_doctor : Annotated[str, f"Valid doctor name in database: {', '.join(DOCTORS)}"], new_doctor : Annotated[str, f"Valid doctor name in database: {', '.join(DOCTORS)}"]):
    """
    Rescheduling an appointment.
    The parameters MUST be mentioned by the user in the query.
    """
    f_id = float(id)
    df = pd.read_csv("data/data.csv")
    availability = df[(df["date_slot"] == old_date)&(df["doctor_name"] == old_doctor)&(df["is_available"] == False)&(df["patient_to_attend"] == f_id)]
    if len(availability) == 0:
        return f"You don't have any appointment on {old_date}."
    elif len(availability) == 1:
        cancel = cancel_appointment.invoke({"date" : old_date, "id" : id, "doctor" : old_doctor})
        new = set_appointment.invoke({"date" : new_date, "id" : id, "doctor" : new_doctor})
        return f"{cancel}\n{new}"   
