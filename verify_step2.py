from pathlib import Path

docs = Path("docs")

required_files = {
    "PROJECT_CARD.md": [
        "FraudFirstAid",
        "Problem Statement",
        "Proposed Solution",
        "Technology Stack",
    ],
    "DISCOVERY_QUESTIONS.md": [
        "Discovery Questions",
        "online financial fraud",
    ],
    "REQUIREMENTS.md": [
        "Functional Requirements",
        "Non-Functional Requirements",
        "Security Requirements",
        "Constraints",
    ],
}

all_passed = True

for filename, required_content in required_files.items():
    file_path = docs / filename

    print(f"\nChecking {filename}...")

    if not file_path.is_file():
        print("FAILED: File missing")
        all_passed = False
        continue

    content = file_path.read_text(encoding="utf-8")

    for item in required_content:
        if item.lower() in content.lower():
            print(f"PASS: {item}")
        else:
            print(f"FAIL: {item}")
            all_passed = False

# Verify ten discovery questions
questions_file = docs / "DISCOVERY_QUESTIONS.md"

if questions_file.exists():
    lines = questions_file.read_text(encoding="utf-8").splitlines()
    questions = [
        line for line in lines if line.strip() and line.strip()[0].isdigit() and ". " in line
    ]

    print(f"\nDiscovery questions: {len(questions)}/10")

    if len(questions) != 10:
        all_passed = False

print("\nSTEP 2 DOCUMENTATION:", "PASSED" if all_passed else "NEEDS FIXING")
