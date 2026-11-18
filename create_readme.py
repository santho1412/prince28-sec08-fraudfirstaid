
from pathlib import Path

readme = """# FraudFirstAid

## About

FraudFirstAid is a Python-based financial fraud assistance
platform that helps people respond to online financial scams.

It provides immediate safety guidance, official reporting
procedures, evidence preservation guidance, and financial
safety information.

## Problem Statement

People experiencing online financial fraud often do not know
what immediate actions to take or where to report incidents.

## Features

1. Fraud category identification
2. Immediate safety recommendations
3. Official fraud reporting guidance
4. Bank and payment safety information
5. Evidence preservation guidance
6. Reporting information
7. Fraud prevention recommendations

## Target Users

- College students
- Parents
- Online banking users
- Cyber-safety volunteers

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

Install dependencies:

```bash
uv sync
```

## Run Application

```bash
uv run uvicorn fraudfirstaid.main:app --reload
```

Note: The API command will work after the FastAPI application
entry point is implemented.

## API Documentation

After starting the server, visit:

http://127.0.0.1:8000/docs

## Security

- Never request banking passwords or OTPs.
- Never store card PINs or UPI PINs.
- Use verified official reporting information.
- Protect sensitive user information.

## Project Status

Foundation and requirements documentation.

## License

To be decided.
"""

Path("README.md").write_text(readme, encoding="utf-8")

print("README.md created successfully!")
print("Location:", Path("README.md").resolve())
