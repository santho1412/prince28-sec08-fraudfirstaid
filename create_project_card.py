from pathlib import Path

project_card = """# FraudFirstAid – Project Card

## Project Name
FraudFirstAid

## Project Description
FraudFirstAid is an AI-powered fraud assistance platform that helps
people respond to online financial scams.

It provides immediate safety guidance, official reporting procedures,
reporting deadlines, and financial safety information.

## Problem Statement
People who experience online financial fraud often do not know what
to do immediately, where to report the incident, or how to protect
their financial accounts.

## Proposed Solution
A Python-based application that provides structured fraud-response
guidance based on the type of scam reported by the user.

## Target Users
- College students
- Parents
- Online banking users
- Cyber-safety volunteers

## Main Features
1. Fraud type identification
2. Immediate action recommendations
3. Official complaint reporting guidance
4. Bank contact and account safety guidance
5. Evidence preservation checklist
6. Reporting deadline information
7. Fraud prevention education

## Technology Stack
- Python 3.12
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- Ruff
- uv

## Project Scope
The first version will provide structured guidance and verified
reporting information. It will not access bank accounts or
automatically reverse financial transactions.

## Expected Outcome
A functional Python application that guides users through the
initial response to online financial fraud.
"""

# Create docs folder
docs = Path("docs")
docs.mkdir(exist_ok=True)

# Create project card
file_path = docs / "PROJECT_CARD.md"
file_path.write_text(project_card, encoding="utf-8")

print("PROJECT CARD CREATED SUCCESSFULLY!")
print(f"File location: {file_path.resolve()}")
