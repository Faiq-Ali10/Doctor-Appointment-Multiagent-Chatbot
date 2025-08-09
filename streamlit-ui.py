import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

if API_URL is None:
    st.error("Environment variable 'API_URL' is not set.")
    st.stop()  

st.title("🩺 Doctor Appointment System")

# Instructions
st.markdown("""
### 📋 Instructions
- **General rule:** You must provide both **ID** and **Query**.
- **Check Availability:** Provide **Date**, **Doctor Name** or **Specialization**.
- **Book Appointment:** Provide **ID**, **Date**, **Time**, and **Doctor Name**.
- **Cancel Appointment:** Provide **ID**, **Date**, **Time**, and **Doctor Name**.
- **Reschedule Appointment:** Provide **ID**, **Old Date**, **Old Time**, **Old Doctor Name**, and **New Date**, **New Time**, **New Doctor Name**.
""")

# Display doctors info
try:
    doctors_response = requests.get(f"{API_URL}/doctors-information", verify=False)
    if doctors_response.status_code == 200:
        doctors_info = doctors_response.json()
        st.subheader("👨‍⚕️ Available Doctors")
        st.dataframe(doctors_info)
    else:
        st.error(f"Could not fetch doctor information. Status Code: {doctors_response.status_code}")
except Exception as e:
    st.error(f"Exception occurred while fetching doctors: {e}")

# Inputs
user_id = st.text_input("Enter your 7 digit ID number: (XXXXXXX)", "1234567")
query = st.text_area("Enter your query:", "Can you check if a general dentist is available on 5 August 2025?")

# Submit query when pressing Enter or clicking button
def submit_query():
    if user_id and query:
        try:
            response = requests.post(f"{API_URL}/doctor-appointment", json={"query": query, 'id': user_id}, verify=False)
            if response.status_code == 200:
                st.success("Response Received:")
                st.write(response.json()["message"])
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Exception occurred: {e}")
    else:
        st.warning("Please enter both ID and query.")

# Button to submit
if query and user_id and st.button("Submit Query"):
    submit_query()
