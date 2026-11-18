import pytest
from fastapi.testclient import TestClient

from fraudfirstaid.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as test_client:
        yield test_client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "FraudFirstAid"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_resources(client):
    response = client.get("/api/resources")

    assert response.status_code == 200
    assert response.json()["financial_cyber_fraud_helpline"] == "1930"


@pytest.mark.parametrize(
    "incident_type",
    [
        "upi",
        "bank_transfer",
        "card",
        "phishing",
        "social_engineering",
        "identity_theft",
        "social_media",
        "other",
    ],
)
def test_all_guidance_types(client, incident_type):
    response = client.get(f"/api/guidance/{incident_type}")

    assert response.status_code == 200
    assert response.json()["incident_type"] == incident_type
    assert len(response.json()["steps"]) > 0


def test_invalid_guidance_type(client):
    response = client.get("/api/guidance/invalid")

    assert response.status_code == 422


def test_evidence_checklist(client):
    response = client.get("/api/evidence-checklist")

    assert response.status_code == 200
    assert len(response.json()["checklist"]) > 0


def test_create_incident(client):
    response = client.post(
        "/api/incidents",
        json={
            "incident_type": "upi",
            "description": "I noticed an unauthorized UPI transaction.",
            "amount_lost": 1500,
        },
    )

    assert response.status_code == 201
    assert response.json()["incident_type"] == "upi"
    assert response.json()["status"] == "new"


def test_create_incident_validation(client):
    response = client.post(
        "/api/incidents",
        json={
            "incident_type": "upi",
            "description": "short",
        },
    )

    assert response.status_code == 422


def test_create_incident_invalid_type(client):
    response = client.post(
        "/api/incidents",
        json={
            "incident_type": "unknown",
            "description": "This is a valid length description.",
        },
    )

    assert response.status_code == 422


def test_list_incidents(client):
    client.post(
        "/api/incidents",
        json={
            "incident_type": "phishing",
            "description": "I entered my details on a suspicious website.",
        },
    )

    response = client.get("/api/incidents")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_get_incident_not_found(client):
    response = client.get("/api/incidents/unknown-id")

    assert response.status_code == 404


def test_update_incident_status(client):
    created = client.post(
        "/api/incidents",
        json={
            "incident_type": "upi",
            "description": "An unauthorized UPI transaction occurred.",
        },
    )

    incident_id = created.json()["id"]

    updated = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={"status": "reported"},
    )

    assert updated.status_code == 200
    assert updated.json()["status"] == "reported"


def test_update_missing_incident(client):
    response = client.patch(
        "/api/incidents/unknown-id/status",
        json={"status": "reported"},
    )

    assert response.status_code == 404


def test_invalid_status(client):
    created = client.post(
        "/api/incidents",
        json={
            "incident_type": "upi",
            "description": "An unauthorized UPI transaction occurred.",
        },
    )

    incident_id = created.json()["id"]

    response = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={"status": "invalid"},
    )

    assert response.status_code == 422


def test_incident_statistics(client):
    response = client.post(
        "/api/incidents",
        json={
            "incident_type": "upi",
            "description": "An unauthorized UPI transaction occurred.",
        },
    )

    assert response.status_code == 201

    stats = client.get("/api/stats")

    assert stats.status_code == 200
    assert stats.json()["total_incidents"] == 1
    assert stats.json()["by_status"]["new"] == 1
