from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_openapi_documentation():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "Hospital Appointment Booking System" in response.json()["info"]["title"]