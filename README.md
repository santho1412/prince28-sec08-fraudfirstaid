# Fraud First Aid

[![CI](https://github.com/santho1412/prince28-sec08-fraudfirstaid/actions/workflows/ci.yml/badge.svg)](https://github.com/santho1412/prince28-sec08-fraudfirstaid/actions/workflows/ci.yml)
[![Live API](https://img.shields.io/website?url=https%3A%2F%2Ffraudfirstaid-api.onrender.com%2Fhealth&label=live%20API)](https://fraudfirstaid-api.onrender.com/docs)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m804759926-69e852256f57023fb6940e33)](https://fraudfirstaid-api.onrender.com/health)

Fraud First Aid is an evidence-based cyber-fraud emergency response and reporting assistance platform designed to help victims of online financial fraud in India.

**Status:** Week 1 complete · live at https://fraudfirstaid-api.onrender.com

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

## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
```

This starts Postgres (with pgvector), Redis, runs the migrations and loads the sample data once, then starts the API.

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Liveness: [http://localhost:8000/health](http://localhost:8000/health)
- Readiness (checks the database): [http://localhost:8000/ready](http://localhost:8000/ready)

Stop with `Ctrl+C`, then `docker compose down`. Add `-v` to also delete the database volume.

## Develop and test

| Task | Mac / Linux | Windows |
|---|---|---|
| Run the API with reload | `make dev` | `uv run poe dev` |
| Unit tests (no network) | `make test` | `uv run poe test` |
| Integration tests (needs `docker compose up`) | `make test-integration` | `uv run poe test-integration` |
| Coverage report | `make cov` | `uv run poe cov` |
| Lint and format check | `make lint` | `uv run poe lint` |
