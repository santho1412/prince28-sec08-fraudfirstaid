
from pathlib import Path

requirements = """# FraudFirstAid – Requirements

## 1. Functional Requirements

FR-01: The system shall accept fraud-related user information.

FR-02: The system shall identify the reported fraud category
using structured rules.

FR-03: The system shall provide immediate safety recommendations.

FR-04: The system shall provide official fraud reporting guidance.

FR-05: The system shall provide evidence preservation guidance.

FR-06: The system shall provide bank and payment safety information.

FR-07: The system shall display relevant reporting information.

FR-08: The system shall provide fraud prevention recommendations.

## 2. Non-Functional Requirements

NFR-01: The application shall be developed using Python.

NFR-02: The API shall use FastAPI.

NFR-03: The application shall validate incoming user information.

NFR-04: The API shall return structured JSON responses.

NFR-05: The application shall protect sensitive user information.

NFR-06: The application shall provide understandable guidance.

NFR-07: The application shall be maintainable and testable.

NFR-08: The application shall use verified information sources.

## 3. Security Requirements

- Never request banking passwords or OTPs.
- Never store card PINs or UPI PINs.
- Avoid collecting unnecessary personal information.
- Do not expose API secrets in source code.
- Do not promise recovery of lost money.
- Clearly distinguish verified information from general guidance.

## 4. Constraints

- Python 3.12
- FastAPI backend
- uv package manager
- Windows 11 development environment
- GitHub version control
"""

# Create docs folder if it does not exist
docs_folder = Path("docs")
docs_folder.mkdir(exist_ok=True)

# Write requirements file
file_path = docs_folder / "REQUIREMENTS.md"
file_path.write_text(requirements, encoding="utf-8")

print("SUCCESS: REQUIREMENTS.md created!")
print(f"Location: {file_path.resolve()}")
print("Functional requirements: 8")
print("Non-functional requirements: 8")
print("Security requirements: 6")
