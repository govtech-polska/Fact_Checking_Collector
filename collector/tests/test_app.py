from starlette.testclient import TestClient

from collector.app import app

client = TestClient(app)


def test_missing_data_create_chatbot_verification_request():
    expected_missing_fields = ["email", "question", "source"]
    missing_field_error = "field required"

    data = {}
    response = client.post("/chatbot-verification-request", json=data)

    assert response.status_code == 422
    response_body = response.json()

    for step, error in enumerate(response_body["detail"]):
        assert expected_missing_fields[step] in error["loc"]
        assert error["msg"] == missing_field_error


def test_successful_create_chatbot_verification_request():
    data = {
        "email": "test@test.com",
        "question": "test question",
        "source": "http://test.com",
    }

    response = client.post("/chatbot-verification-request", json=data)

    assert response.status_code == 201

    response_body = response.json()
    assert "id" in response_body
    assert data["email"] == response_body["reporter_email"]
    assert data["question"] == response_body["question"]
    assert data["source"] == response_body["source"]
