from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

IncidentType = Literal[
    "upi",
    "bank_transfer",
    "card",
    "phishing",
    "social_engineering",
    "identity_theft",
    "social_media",
    "other",
]

IncidentStatus = Literal[
    "new",
    "reported",
    "in_progress",
    "resolved",
    "closed",
]


class IncidentCreate(BaseModel):
    incident_type: IncidentType
    description: str = Field(min_length=10, max_length=2000)
    amount_lost: float | None = Field(default=None, ge=0)
    occurred_at: datetime | None = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


GUIDANCE = {
    "upi": [
        "Contact your bank or payment app using its official support channel.",
        "Ask the provider to secure the affected account or payment method.",
        "For financial cyber fraud, call India's 1930 helpline promptly.",
        "Submit a complaint at the National Cyber Crime Reporting Portal.",
    ],
    "bank_transfer": [
        "Contact your bank immediately using its official phone number or app.",
        "Ask the bank to report and review the unauthorised transaction.",
        "For financial cyber fraud, call India's 1930 helpline promptly.",
        "Submit a complaint at the National Cyber Crime Reporting Portal.",
    ],
    "card": [
        "Contact your card issuer using its official support channel.",
        "Ask the issuer to block or secure the affected card.",
        "Review recent transactions with your bank.",
        "Report the incident through 1930 and the official cybercrime portal.",
    ],
    "phishing": [
        "Do not open further links or attachments from the suspicious message.",
        "If you entered a password, change it using the genuine service website.",
        "Secure your email account and enable multi-factor authentication.",
        "Contact your bank if you shared financial information.",
        "Report the incident through the official cybercrime portal.",
    ],
    "social_engineering": [
        "Stop communicating with the suspected scammer.",
        "Do not share OTPs, passwords, PINs, or remote-access permissions.",
        "Contact your bank immediately if you shared financial information.",
        "For financial cyber fraud, call 1930 promptly.",
        "Submit a complaint through the official cybercrime portal.",
    ],
    "identity_theft": [
        "Secure your email and other important accounts.",
        "Change compromised passwords from a trusted device.",
        "Enable multi-factor authentication where available.",
        "Contact affected service providers through official channels.",
        "Report the incident through the official cybercrime portal.",
    ],
    "social_media": [
        "Secure your social media account and change its password.",
        "Enable multi-factor authentication.",
        "Save relevant messages, profile links, and timestamps as evidence.",
        "Report the account or content to the platform.",
        "Report suspected cybercrime through the official cybercrime portal.",
    ],
    "other": [
        "Stop interacting with the suspected scammer.",
        "Secure any accounts or payment methods that may be affected.",
        "Preserve relevant messages and transaction records.",
        "Report suspected cybercrime through the official cybercrime portal.",
    ],
}


EVIDENCE_CHECKLIST = [
    "Transaction reference number or UTR, if applicable",
    "Transaction date, time, and amount",
    "Bank or payment app notification",
    "Screenshots of relevant messages and conversations",
    "Website URLs, phone numbers, email addresses, or profile links",
    "Bank or cybercrime complaint acknowledgement number",
]


def create_app(database_path: str | Path | None = None) -> FastAPI:
    if database_path is None:
        db_file = Path(__file__).resolve().parents[2] / "data" / "incidents.db"
    else:
        db_file = Path(database_path)

    db_file.parent.mkdir(parents=True, exist_ok=True)

    def connect() -> sqlite3.Connection:
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_database() -> None:
        with closing(connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    incident_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount_lost REAL,
                    occurred_at TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    initialize_database()

    app = FastAPI(
        title="FraudFirstAid",
        description=(
            "Cyber fraud emergency response and reporting guidance for India. "
            "This tool provides guidance and does not file official complaints."
        ),
        version="1.0.0",
    )

    @app.get("/")
    def root():
        return {
            "name": "FraudFirstAid",
            "message": "Cyber fraud assistance API is running.",
            "docs": "/docs",
        }

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.get("/api/resources")
    def resources():
        return {
            "country": "India",
            "financial_cyber_fraud_helpline": "1930",
            "cybercrime_reporting_portal": "https://cybercrime.gov.in/",
            "emergency_police_helpline": "112",
            "notice": (
                "Use official channels. FraudFirstAid does not submit "
                "complaints to government agencies or banks."
            ),
        }

    @app.get("/api/guidance/{incident_type}")
    def get_guidance(incident_type: IncidentType):
        return {
            "incident_type": incident_type,
            "steps": GUIDANCE[incident_type],
            "important": (
                "Never share your OTP, PIN, password, CVV, or banking login details with anyone."
            ),
        }

    @app.get("/api/evidence-checklist")
    def evidence_checklist():
        return {
            "checklist": EVIDENCE_CHECKLIST,
            "privacy_warning": (
                "Do not upload or share passwords, OTPs, PINs, CVVs, or complete card details."
            ),
        }

    @app.post("/api/incidents", status_code=201)
    def create_incident(payload: IncidentCreate):
        incident_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        occurred_at = payload.occurred_at.isoformat() if payload.occurred_at is not None else None

        with closing(connect()) as connection:
            connection.execute(
                """
                INSERT INTO incidents (
                    id, incident_type, description, amount_lost,
                    occurred_at, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    payload.incident_type,
                    payload.description,
                    payload.amount_lost,
                    occurred_at,
                    "new",
                    now,
                    now,
                ),
            )
            connection.commit()

        return {
            "id": incident_id,
            "incident_type": payload.incident_type,
            "description": payload.description,
            "amount_lost": payload.amount_lost,
            "occurred_at": occurred_at,
            "status": "new",
            "created_at": now,
            "updated_at": now,
        }

    @app.get("/api/incidents")
    def list_incidents(
        limit: int = Query(default=50, ge=1, le=100),
    ):
        with closing(connect()) as connection:
            rows = connection.execute(
                """
                SELECT * FROM incidents
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return {"count": len(rows), "incidents": [dict(row) for row in rows]}

    @app.get("/api/incidents/{incident_id}")
    def get_incident(incident_id: str):
        with closing(connect()) as connection:
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?",
                (incident_id,),
            ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        return dict(row)

    @app.patch("/api/incidents/{incident_id}/status")
    def update_incident_status(
        incident_id: str,
        payload: IncidentStatusUpdate,
    ):
        now = datetime.now(UTC).isoformat()

        with closing(connect()) as connection:
            cursor = connection.execute(
                """
                UPDATE incidents
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (payload.status, now, incident_id),
            )
            connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found",
                )

            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?",
                (incident_id,),
            ).fetchone()

        return dict(row)

    @app.get("/api/stats")
    def incident_stats():
        with closing(connect()) as connection:
            total = connection.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]

            statuses = connection.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM incidents
                GROUP BY status
                """
            ).fetchall()

        return {
            "total_incidents": total,
            "by_status": {row["status"]: row["count"] for row in statuses},
        }

    return app


app = create_app()
