import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root GET / endpoint returns 200 OK and serves Web UI."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_ask_empty_question_validation():
    """Verify empty question returns 422 validation error."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
    assert "Question cannot be empty" in response.text


def test_ask_missing_question_field():
    """Verify missing question field returns 422 validation error."""
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_valid_question():
    """Verify valid question returns 200 with answer and citations."""
    response = client.post(
        "/ask",
        json={"question": "What is the first round of Zoho selection process?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    assert "citations" in data
    assert isinstance(data["citations"], list)
