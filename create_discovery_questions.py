
from pathlib import Path

questions = [
    "What types of online financial fraud should the application support?",
    "Who are the primary users of FraudFirstAid?",
    "What immediate actions should a victim take after discovering fraud?",
    "How can users identify the type of financial scam they experienced?",
    "Which official authorities should users contact to report fraud?",
    "What information and evidence should users preserve?",
    "How should users receive bank account and payment safety guidance?",
    "How can the application provide accurate reporting deadlines?",
    "Should the application support multiple languages in future versions?",
    "How can we ensure that the information provided is reliable, secure, and regularly updated?"
]

# Create docs directory
docs = Path("docs")
docs.mkdir(exist_ok=True)

# Generate Markdown content
content = "# FraudFirstAid – Discovery Questions\n\n"

for number, question in enumerate(questions, start=1):
    content += f"{number}. {question}\n\n"

# Save file
file_path = docs / "DISCOVERY_QUESTIONS.md"
file_path.write_text(content, encoding="utf-8")

print("SUCCESS: Discovery questions created!")
print(f"Location: {file_path.resolve()}")
print(f"Total questions: {len(questions)}")
