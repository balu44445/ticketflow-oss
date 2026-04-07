from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ticketflow.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_laptop_request_workflow():
    create_response = client.post(
        "/requests",
        json={
            "requester_name": "Bala",
            "requester_email": "bala@example.com",
            "request_type": "laptop",
            "business_justification": "Need a laptop for onboarding work",
        },
    )
    assert create_response.status_code == 201
    request_id = create_response.json()["id"]

    manager_response = client.post(
        f"/requests/{request_id}/manager-review",
        json={"approved": True, "actor": "Manager One"},
    )
    assert manager_response.status_code == 200
    body = manager_response.json()
    assert body["status"] == "fulfillment_in_progress"
    assert len(body["tasks"]) == 1

    task_id = body["tasks"][0]["id"]
    complete_response = client.post(
        f"/requests/{request_id}/tasks/{task_id}/complete",
        params={"actor": "Agent One"},
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "closed"


def test_vpn_request_requires_security_approval():
    create_response = client.post(
        "/requests",
        json={
            "requester_name": "Bala",
            "requester_email": "bala@example.com",
            "request_type": "vpn",
            "business_justification": "Need secure remote access",
        },
    )
    request_id = create_response.json()["id"]

    manager_response = client.post(
        f"/requests/{request_id}/manager-review",
        json={"approved": True, "actor": "Manager One"},
    )
    assert manager_response.status_code == 200
    assert manager_response.json()["status"] == "pending_security"

    security_response = client.post(
        f"/requests/{request_id}/security-review",
        json={"approved": True, "actor": "Security One"},
    )
    assert security_response.status_code == 200
    assert security_response.json()["status"] == "fulfillment_in_progress"
