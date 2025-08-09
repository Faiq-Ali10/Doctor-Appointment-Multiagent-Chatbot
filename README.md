# Doctor Appointment Multiagent Chatbot

A multi-agent chatbot system designed for doctor appointment management.  
The system consists of three specialized agents: **Supervisor**, **Booking**, and **Information** to handle user queries effectively.

---

## Project Structure

```

DOCTOR_APPOINTMENT_Multiagent/
│
├── data/
│ └── data.csv # Doctors and specializations data
│
├── prompts/
│ ├── init.py
│ ├── booking.py # Booking agent prompts
│ ├── information.py # Information agent prompts
│ ├── router.py # Routing logic for agent selection
│ └── supervisor.py # Supervisor agent prompts
│
├── tests/
│ ├── init.py
│ ├── test_api.py # API endpoint tests
│ ├── conftest.py # Pytest fixtures
│
├── toolkit/
│ ├── init.py
│ ├── helper.py # Helper functions
│ └── tools.py # Tools used by agents
│
├── utils/
│ ├── init.py
│ ├── llm.py # LLM interaction logic
│ └── messages.py # Message helper functions
│
├── agent.py # Multi-agent orchestration logic
├── main.py # FastAPI backend application
├── routing_llm.py # LLM routing decisions
├── requirements.txt # Python dependencies
├── streamlit-ui.py # Streamlit frontend app
└── .gitignore # Git ignore rules

```

---

## Features

- Multi-agent system with three agents:
  - **Supervisor**: Oversees conversations and escalations
  - **Booking**: Handles appointment booking and scheduling
  - **Information**: Provides doctor and specialization details
- User inputs require a **7-digit integer ID** along with queries.
- Backend API built with **FastAPI**.
- Frontend UI built with **Streamlit** for easy interaction.
- Data stored in CSV (`data/data.csv`) for doctors and specializations.
- Tested via API endpoint tests using Pytest.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerization)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Faiq-Ali10/Doctor-Appointment-Multiagent-Chatbot
   cd doctor-appointment-multiagent

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3. Install dependencies:

```bash
pip install -r requirements.txt

3. Create a .env file and add your environment variables (e.g., API keys).

Backend
```bash
Running Locally
Backend
bash
Copy
Edit
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The backend API will be available at http://localhost:8000.

Frontend
bash
Copy
Edit
streamlit run streamlit-ui.py
The Streamlit UI will be available at http://localhost:8501.

Make sure your frontend is configured to send API requests to the correct backend URL.

Testing
Run tests with:

bash
Copy
Edit
pytest tests/
