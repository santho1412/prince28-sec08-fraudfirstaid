
# Fraud First Aid – Project Requirements

## 1. Functional Requirements

### FR-01: Fraud Incident Registration
The system must allow users to select a fraud category and enter the incident date, time and transaction details.

### FR-02: Emergency Action Guidance
The system must generate the next five recommended emergency actions based on the reported fraud scenario.

### FR-03: Reporting Assistance
The system must provide the appropriate reporting channels, including the 1930 helpline, National Cyber Crime Reporting Portal and bank contact routes.

### FR-04: RBI Liability Guidance
The system must explain applicable customer-liability rules based on transaction type, customer responsibility and bank notification timeline, with official source citations.

### FR-05: Evidence and Complaint Tracking
The system must provide an evidence checklist and allow users to track their complaint reference and reporting progress without storing sensitive banking information.

## 2. Non-Functional Requirements

### NFR-01: Response Time
The API must return normal guidance responses within 2 seconds for at least 95% of requests under a test load of 50 concurrent users.

### NFR-02: Data Privacy
The system must not store real bank account numbers, card numbers, passwords, OTPs or unnecessary personal information.

### NFR-03: Reliability
The system must pass at least 95% of its automated functional test cases before release.

### NFR-04: Usability
A first-time user must be able to locate the emergency action checklist within 3 clicks.

### NFR-05: Maintainability
The project must use Python type hints, Ruff formatting and linting, automated pytest tests, and documented API endpoints.

---

## 3. Acceptance Criteria

- All 5 functional requirements must be implemented and tested.
- All 5 non-functional requirements must have measurable verification methods.
- Regulatory guidance must cite official sources.
- Test scenarios must use synthetic data.
- No sensitive victim banking information must be exposed or unnecessarily retained.
