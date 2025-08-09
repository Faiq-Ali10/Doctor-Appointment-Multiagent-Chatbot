import pandas as pd

def get_doctors_names():
    df = pd.read_csv("data/data.csv")
    return tuple(df["doctor_name"].unique())

def get_specialization_names():
    df = pd.read_csv("data/data.csv")
    return tuple(df["specialization"].unique())

def convert_to_12(time : str):
    hours, minutes = map(int, time.split(":"))
    period = "am" if hours < 12 else "pm"
    hours = hours % 12 or 12
    return f"{hours}:{minutes} {period}"