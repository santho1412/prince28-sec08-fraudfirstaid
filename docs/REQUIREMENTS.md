# FraudFirstAid – Requirements

## 1. Functional Requirements

FR-01: The system shall support at least 5 financial fraud categories.

FR-02: The system shall provide at least 3 immediate safety recommendations for each supported fraud category.

FR-03: The system shall provide at least 3 official reporting channels for financial cyber fraud in India.

FR-04: The system shall preserve and display at least 5 types of evidence users should retain after a fraud incident.

FR-05: The system shall provide searchable fraud guidance through REST API endpoints.

## 2. Non-Functional Requirements

NFR-01: The API shall respond to standard health-check requests within 1 second under normal local testing conditions.

NFR-02: The API shall return valid JSON responses for successful requests.

NFR-03: The API shall pass at least 10 automated tests.

NFR-04: The application shall use Python 3.12 and FastAPI.

NFR-05: The application shall never request or store banking passwords, OTPs, card PINs, or UPI PINs.

## 3. Security Requirements

- Never request banking passwords or OTPs.
- Never store card PINs or UPI PINs.
- Avoid collecting unnecessary personal information.
- Do not expose API secrets in source code.
- Clearly distinguish verified information from general guidance.

## 4. Constraints

- Python 3.12
- FastAPI backend
- uv package manager
- Windows 11 development environment
- GitHub version control
