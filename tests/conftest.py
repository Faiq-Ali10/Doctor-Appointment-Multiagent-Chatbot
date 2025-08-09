import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def test_client():
    """FastAPI TestClient for testing API endpoints."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def valid_payload():
    return {
        "query": "Check availability of Dr. John Doe on 2025-08-05",
        "id": 1234567
    }

@pytest.fixture
def invalid_id_short():
    return {
        "query": "Book appointment",
        "id": 12345
    }

@pytest.fixture
def invalid_id_long():
    return {
        "query": "Book appointment",
        "id": 123456789
    }

@pytest.fixture
def invalid_id_string():
    return {
        "query": "Check info",
        "id": "1234567"
    }

@pytest.fixture
def missing_id():
    return {
        "query": "Check availability"
    }

@pytest.fixture
def non_medical_query():
    return {
        "query": "Hello, how are you?",
        "id": 1234567
    }
