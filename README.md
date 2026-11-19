# FraudFirstAid

## About

FraudFirstAid is a Python-based financial fraud assistance platform that helps people respond to online financial scams.

It provides immediate safety guidance, official reporting procedures, evidence preservation guidance, and financial safety information.

## Problem Statement

People experiencing online financial fraud often do not know what immediate actions to take or where to report incidents. FraudFirstAid aims to make reliable guidance easier to access.

## Target Users

- College students
- Parents
- Online banking users
- Cyber-safety volunteers

## Features

1. Fraud category identification
2. Immediate safety recommendations
3. Official fraud reporting guidance
4. Bank and payment safety information
5. Evidence preservation guidance
6. Reporting information
7. Fraud prevention recommendations

## Data Sources

The project uses official information and guidance from:

- Reserve Bank of India (RBI)
- National Cyber Crime Reporting Portal
- Indian Computer Emergency Response Team (CERT-In)
- Department of Telecommunications – Sanchar Saathi

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic
- Uvicorn
- uv
- Pytest
- Ruff

## Project Structure

```text
FraudFirstAid/
    docs/
    src/
        fraudfirstaid/
    tests/
    data/
    pyproject.toml
    uv.lock
    README.md
```

## Installation

```bash
uv sync
```

## Run Application

```bash
uv run uvicorn fraudfirstaid.api.main:app --reload
```

## API Documentation

After starting the server, visit:

http://127.0.0.1:8000/docs

## Hardest Problem

One of the most challenging parts of this project is designing reliable API error handling and ensuring that fraud guidance comes from trustworthy sources. Maintaining consistent data structures and validating API responses are also important challenges.

## Target Metric

- At least 5 supported fraud categories.
- At least 20 fraud guidance and reference records.
- At least 10 automated API tests passing.
- Health-check response within 1 second under normal local testing conditions.

## Security

- Never request banking passwords or OTPs.
- Never store card PINs or UPI PINs.
- Avoid collecting unnecessary personal information.
- Protect sensitive user information.

## Project Status

FastAPI foundation, sample fraud records, API error handling, and automated tests implemented.

## License

To be decided.
