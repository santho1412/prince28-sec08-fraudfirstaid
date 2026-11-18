from fastapi.testclient import TestClient

from fraudfirstaid.main import create_app


def test_home_and_health(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/health").json()["status"] == "healthy"


def test_create_and_read_incident(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as client:
        response = client.post(
            "/api/incidents",
            json={
                "incident_type": "upi",
                "description": "I noticed an unauthorised UPI transaction.",
                "amount_lost": 1500,
            },
        )

        assert response.status_code == 201
        incident_id = response.json()["id"]

        detail = client.get(f"/api/incidents/{incident_id}")
        assert detail.status_code == 200
        assert detail.json()["incident_type"] == "upi"


def test_invalid_incident_is_rejected(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as client:
        response = client.post(
            "/api/incidents",
            json={
                "incident_type": "upi",
                "description": "short",
            },
        )

        assert response.status_code == 422


def test_guidance_and_resources(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as client:
        guidance = client.get("/api/guidance/upi")
        resources = client.get("/api/resources")
        checklist = client.get("/api/evidence-checklist")

        assert guidance.status_code == 200
        assert len(guidance.json()["steps"]) > 0
        assert resources.json()["financial_cyber_fraud_helpline"] == "1930"
        assert len(checklist.json()["checklist"]) > 0


def test_update_incident_status(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as client:
        created = client.post(
            "/api/incidents",
            json={
                "incident_type": "phishing",
                "description": "I entered my details on a suspicious website.",
            },
        )

        incident_id = created.json()["id"]

        updated = client.patch(
            f"/api/incidents/{incident_id}/status",
            json={"status": "reported"},
        )

        assert updated.status_code == 200
        assert updated.json()["status"] == "reported"
