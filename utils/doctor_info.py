import pandas as pd

def fetch_doctors_info():
    try:
        df = pd.read_csv("data/data.csv", usecols=["specialization", "doctor_name"])
        unique_doctors = df.drop_duplicates().reset_index(drop=True)
        return unique_doctors.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": "Doctors information is not available "}