import os
import pytest

os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DB"] = "namma_tn_test"
os.environ["ADMIN_EMAIL"] = "admin@namma.tn"
os.environ["ADMIN_PASSWORD"] = "admin123"

from app import create_app
from app.config import Config


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def register_user(client, payload):
    return client.post("/api/auth/register", json=payload)


def login_user(client, payload):
    return client.post("/api/auth/login", json=payload)


def test_root_endpoint_returns_app_status(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert "service" in body


def test_default_admin_credentials_exist():
    assert Config.ADMIN_EMAIL == "admin@namma.tn"
    assert Config.ADMIN_PASSWORD == "admin123"


def test_citizen_registration_and_login(client):
    payload = {
        "name": "Test Citizen",
        "email": "citizen@example.com",
        "phone": "9876543210",
        "password": "secret123",
    }
    reg = register_user(client, payload)
    assert reg.status_code == 201
    body = reg.get_json()
    assert "token" in body
    assert body["user"]["role"] == "citizen"

    login = login_user(client, {"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    assert login.get_json()["user"]["email"] == payload["email"]


def test_ai_analysis_handles_tamil_tanglish_and_english(client):
    for message in [
        "enga street la 3 days ah water varala",
        "Thiruvaiyaru main road la periya pothole irukku",
        "Water is not supplied to our area for 3 days",
    ]:
        response = client.post("/api/ai/analyze", json={"message": message})
        assert response.status_code == 200
        data = response.get_json()
        assert data["category"] in {"water", "road", "drainage", "waste", "streetlight", "flooding", "other"}
        assert data["severity"] in {"low", "medium", "high"}
        assert data["needs_location"] is True


def test_empty_message_is_rejected_and_duplicate_registration_is_blocked(client):
    response = client.post("/api/ai/analyze", json={"message": ""})
    assert response.status_code == 400

    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "phone": "9876543210",
        "password": "secret123",
    }
    first = register_user(client, payload)
    second = register_user(client, payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_citizen_can_create_and_track_complaint_without_photo(client):
    user = register_user(client, {
        "name": "Complaint Owner",
        "email": "owner@example.com",
        "phone": "9876543210",
        "password": "secret123",
    }).get_json()
    token = user["token"]

    analysis = client.post("/api/ai/analyze", json={"message": "Road is damaged near the market"}).get_json()
    complaint = client.post(
        "/api/complaints",
        json={
            "message": "Road is damaged near the market",
            "category": analysis["category"],
            "severity": analysis["severity"],
            "district": "Thanjavur",
            "area": "Thiruvaiyaru",
            "duration": "3 days",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert complaint.status_code == 201
    complaint_body = complaint.get_json()
    assert complaint_body["status"] == "Submitted"
    assert complaint_body["complaint_id"].startswith("TN-")

    my_list = client.get("/api/complaints/my", headers={"Authorization": f"Bearer {token}"})
    assert my_list.status_code == 200
    assert len(my_list.get_json()) >= 1

    tracked = client.get(f"/api/complaints/{complaint_body['complaint_id']}")
    assert tracked.status_code == 200
    assert tracked.get_json()["area"] == "Thiruvaiyaru"


def test_proof_image_validation_and_status_transitions(client):
    user = register_user(client, {
        "name": "Photo User",
        "email": "photo@example.com",
        "phone": "9876543210",
        "password": "secret123",
    }).get_json()
    token = user["token"]

    analysis = client.post("/api/ai/analyze", json={"message": "Street light not working"}).get_json()
    complaint = client.post(
        "/api/complaints",
        json={
            "message": "Street light not working",
            "category": analysis["category"],
            "severity": analysis["severity"],
            "district": "Thanjavur",
            "area": "Tanjore",
            "proof_image": "data:image/png;base64,abcd1234",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert complaint.status_code == 201
    complaint_id = complaint.get_json()["complaint_id"]

    invalid = client.post(
        "/api/complaints",
        json={
            "message": "Bad image",
            "category": "waste",
            "severity": "medium",
            "district": "Thanjavur",
            "area": "Tanjore",
            "proof_image": "not-a-data-url",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert invalid.status_code == 400

    admin_login = login_user(client, {"email": "admin@namma.tn", "password": "admin123"})
    admin_token = admin_login.get_json()["token"]

    status_update = client.patch(
        f"/api/complaints/{complaint_id}",
        json={"status": "In Progress"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status_update.status_code == 200
    assert status_update.get_json()["status"] == "In Progress"

    bad_status = client.patch(
        f"/api/complaints/{complaint_id}",
        json={"status": "Deleted"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert bad_status.status_code == 400


def test_citizen_without_complaints_and_invalid_access(client):
    user = register_user(client, {
        "name": "No Complaint User",
        "email": "empty@example.com",
        "phone": "9876543210",
        "password": "secret123",
    }).get_json()
    token = user["token"]

    my_list = client.get("/api/complaints/my", headers={"Authorization": f"Bearer {token}"})
    assert my_list.status_code == 200
    assert my_list.get_json() == []

    admin_forbidden = client.get("/api/complaints", headers={"Authorization": f"Bearer {token}"})
    assert admin_forbidden.status_code == 403


def test_invalid_auth_and_missing_complaint_id(client):
    bad_token = client.get("/api/auth/me", headers={"Authorization": "Bearer bad-token"})
    assert bad_token.status_code == 401

    missing = client.get("/api/complaints/TN-NOPE-000000-AAAA")
    assert missing.status_code == 404

    malformed_request = client.post(
        "/api/complaints",
        json={
            "message": "Only message",
            "category": "road",
            "severity": "high",
            "district": "",
            "area": "",
        },
        headers={"Authorization": "Bearer bad-token"},
    )
    assert malformed_request.status_code == 401

