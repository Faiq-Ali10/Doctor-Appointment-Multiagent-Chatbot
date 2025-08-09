def test_post_doctor_appointment_valid(test_client, valid_payload):
    response = test_client.post("/doctor-appointment", json=valid_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "message" in json_data

def test_post_doctor_appointment_id_too_short(test_client, invalid_id_short):
    response = test_client.post("/doctor-appointment", json=invalid_id_short)
    assert response.status_code == 400
    assert "ID must be exactly 7 digits long." in response.text

def test_post_doctor_appointment_id_too_long(test_client, invalid_id_long):
    response = test_client.post("/doctor-appointment", json=invalid_id_long)
    assert response.status_code == 400
    assert "ID must be exactly 7 digits long." in response.text

def test_post_doctor_appointment_id_as_string(test_client):
    payload = {
        "query": "Check info",
        "id": "not_an_integer"
    }
    response = test_client.post("/doctor-appointment", json=payload)
    assert response.status_code == 400

def test_post_doctor_appointment_missing_id(test_client, missing_id):
    response = test_client.post("/doctor-appointment", json=missing_id)
    assert response.status_code == 400 
    assert "Field required" in response.text or "field required" in response.text.lower()

def test_post_doctor_appointment_non_medical_query(test_client, non_medical_query):
    response = test_client.post("/doctor-appointment", json=non_medical_query)
    assert response.status_code == 200
    json_data = response.json()
    assert "message" in json_data

def test_get_doctors_information_success(test_client):
    response = test_client.get("/doctors-information")
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    if json_data:
        first = json_data[0]
        assert "specialization" in first
        assert "doctor_name" in first

def test_get_doctors_information_file_not_found(test_client, monkeypatch):
    import pandas as pd

    def fake_read_csv(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    response = test_client.get("/doctors-information")
    assert response.status_code == 200
    assert response.json() == {"error": "Doctors information is not available "}

def test_post_doctor_appointment_agent_exception(test_client, valid_payload, monkeypatch):
    from main import agent

    def raise_exc(*args, **kwargs):
        raise Exception("Forced error")

    monkeypatch.setattr(agent, "invoke", raise_exc)
    response = test_client.post("/doctor-appointment", json=valid_payload)
    assert response.status_code == 200
    assert "I apologize" in response.json()["message"]

def test_validation_exception_handler_custom_message(test_client):
    bad_payload = {"query": "Test", "id": 1}
    response = test_client.post("/doctor-appointment", json=bad_payload)
    assert response.status_code == 400
    assert "ID must be exactly 7 digits long." in response.text
