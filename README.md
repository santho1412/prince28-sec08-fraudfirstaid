
# Fraud First Aid

Fraud First Aid is an evidence-based cyber-fraud emergency response and reporting assistance platform designed to help victims of online financial fraud in India.

**Status:** Day 1 foundation — Python project setup, quality gates and FastAPI skeleton. Live URL planned from Day 5.

## Who it's for

A volunteer at a Tambaram college cyber-safety cell who helps students and parents respond to online financial fraud, including UPI scams, OTP theft and fake-job scams.

## The problem

People who experience online financial fraud often do not know what to do immediately after losing money. Some victims report the incident late, while others contact the wrong organisation and lose valuable time. The reporting process involves multiple channels, including the 1930 helpline, the National Cyber Crime Reporting Portal and the victim's bank. Understanding bank liability rules and reporting deadlines is also difficult. Fraud First Aid aims to make these steps easier through clear, evidence-based guidance.

## Data sources

- RBI customer-liability circular (6 July 2017) and subsequent applicable directions.
- RBI Integrated Ombudsman Scheme 2021.
- National Cyber Crime Reporting Portal guides and FAQs.
- CERT-In and I4C scam advisories.
- Sanchar Saathi guidance.
- Banks' fraud-reporting policies.

Useful links:

- https://cybercrime.gov.in/
- https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=11040
- https://cms.rbi.org.in/
- https://sancharsaathi.gov.in/
- https://www.cert-in.org.in/

**Data privacy:** Use public government documents and synthetic test data. Never store real victim names, account numbers or card numbers.

## Hardest problem (my interview story)

The most challenging part is determining whether a transaction was authorised or unauthorised. A payment that a victim personally sends to a scammer can have different liability treatment from an unauthorised debit caused by stolen credentials. The applicable RBI rules depend on the circumstances, customer fault and the time taken to notify the bank. Working-day calculations must also account for bank holidays. Every liability explanation must be supported by the applicable current RBI direction.

## Signature feature

**Golden-hour checklist:** Users enter what happened and when. The application generates the next five recommended actions, reporting destinations, relevant deadlines and applicable liability guidance.

## Target metric

- 100% accuracy across 30 liability and deadline timeline tests.
- At least 95% correct reporting routes across 40 scam scenarios.

## Run it locally

```bash
uv sync
```

Windows:

```cmd
copy .env.example .env
```

Start the API:

```bash
uv run uvicorn fraudfirstaid.api.main:create_app --factory --reload
```

Open:

http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```
