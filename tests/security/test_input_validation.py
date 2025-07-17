from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_user_missing_email():
    response = client.post("/user", json={"name": "No Email"})
    assert response.status_code == 422


def test_create_user_empty_name():
    response = client.post("/user", json={"email": "test@example.com", "name": ""})
    assert response.status_code == 422


def test_create_user_sql_injection_like_input():
    malicious_email = "'; DROP TABLE users; --"
    response = client.post("/user", json={"email": malicious_email, "name": "Hacker"})
    # Should fail validation or be handled safely
    assert response.status_code in (200, 201, 422)
    # Depending on your schema, 422 if email validation is strict
