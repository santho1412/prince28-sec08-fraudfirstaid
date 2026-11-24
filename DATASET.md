# Dataset: FraudFirstAid

Guides victims of online financial fraud through the first hours: what to report where (1930, the cyber crime portal, the bank), RBI liability rules and deadlines, with every rule cited.

- **Start target:** RBI liability circular + Ombudsman scheme + portal FAQs + 50 advisories
- **Full target:** + 3 years of CERT-In, I4C and RBI advisories and 10 banks' fraud-reporting policies (2,000+ pages)
- **Collected by:** `scripts/fetch.py` as `examate-student-bot` (https://github.com/santho1412/prince28-sec08-fraudfirstaid): robots.txt respected, at most 4 requests at once, 0.5 s between requests to one site.

## Where the documents come from

- https://cybercrime.gov.in/
- https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=11040
- https://cms.rbi.org.in/
- https://sancharsaathi.gov.in/
- https://www.cert-in.org.in/

## Terms I follow

Public government documents. Never store real victim names, account numbers or card numbers.

- Every answer links to the original document.
- No personal data is collected.

<!-- generated:start -->
## Sources (generated 2026-11-24 06:09 UTC by scripts/dataset_report.py)

| Source | Licence / terms | Files | MB | Pages* | How | Fetched | Example URL |
|---|---|---|---|---|---|---|---|
| certin | Official CERT-In publication; reuse permission not yet verified | 33 | 4.5 | 83 | http | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2025-0019&pageid=PUBVLNOTES02 |
| i4c | Official government publication; reuse permission not yet verified | 25 | 17.1 | 75 | http+manual | 2026-11-24 | https://cybercrime.gov.in/pdf/Advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| rbi | Official RBI publication; reuse permission not yet verified | 8 | 1.1 | 66 | http+manual | 2026-11-24 | https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63011 |

**Total:** 66 files, 22.7 MB, 224 pages. Not downloaded: 0 blocked by robots.txt, 1 failed.

*Pages = PDF pages, plus one page per 3,000 characters of text or HTML.

## Files (first 66 of 66)

The complete list, with a sha256 fingerprint of every file, is `data/manifest.jsonl`.

| # | Title / file | Source | Pages | Fetched | URL |
|---|---|---|---|---|---|
| 1 | CERT-In Directions 2022 | certin | 8 | 2026-11-23 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf |
| 2 | CERT-In Directions FAQs | certin | 28 | 2026-11-23 | https://www.cert-in.org.in/PDF/FAQs_on_CyberSecurityDirections_May2022.pdf |
| 3 | CERT-In Advisory CIAD-2024-0062 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0062 |
| 4 | CERT-In Advisory CIAD-2025-0050 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0050 |
| 5 | CERT-In Advisory CIAD-2025-0048 | certin | 2 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0048 |
| 6 | CERT-In Advisory CIAD-2024-0057 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0057 |
| 7 | CERT-In Advisory CIAD-2025-0052 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0052 |
| 8 | CERT-In Advisory CIAD-2025-0045 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0045 |
| 9 | CERT-In Advisory CIAD-2024-0054 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0054 |
| 10 | CERT-In Advisory CIAD-2025-0047 | certin | 2 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0047 |
| 11 | CERT-In Advisory CIAD-2025-0046 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0046 |
| 12 | CERT-In Advisory CIAD-2025-0054 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0054 |
| 13 | CERT-In Advisory CIAD-2024-0058 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0058 |
| 14 | Cybersecurity Advisory CIAD-2025-0019 | certin | 2 | 2026-11-23 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2025-0019&pageid=PUBVLNOTES02 |
| 15 | CERT-In Advisory CIAD-2025-0044 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0044 |
| 16 | CERT-In Advisory CIAD-2024-0055 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0055 |
| 17 | CERT-In Advisory CIAD-2024-0060 | certin | 3 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0060 |
| 18 | CERT-In Advisory CIAD-2025-0043 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0043 |
| 19 | CERT-In Advisory CIAD-2024-0050 | certin | 4 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0050 |
| 20 | CERT-In Advisory CIAD-2024-0056 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0056 |
| 21 | CERT-In Advisory CIAD-2024-0051 | certin | 3 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0051 |
| 22 | CERT-In Advisory CIAD-2024-0049 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0049 |
| 23 | CERT-In Advisory CIAD-2025-0049 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0049 |
| 24 | CERT-In Advisory CIAD-2024-0059 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0059 |
| 25 | CERT-In Advisory CIAD-2024-0053 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0053 |
| 26 | CERT-In Advisory CIAD-2025-0053 | certin | 2 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0053 |
| 27 | CERT-In Advisory CIAD-2024-0063 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0063 |
| 28 | CERT-In Advisory CIAD-2025-0041 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0041 |
| 29 | CERT-In Advisory CIAD-2024-0052 | certin | 2 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0052 |
| 30 | CERT-In Advisory CIAD-2024-0061 | certin | 2 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2024-0061 |
| 31 | CERT-In Advisory CIAD-2025-0042 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0042 |
| 32 | CERT-In Advisory CIAD-2025-0055 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0055 |
| 33 | CERT-In Advisory CIAD-2025-0051 | certin | 1 | 2026-11-24 | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES02&VLCODE=CIAD-2025-0051 |
| 34 | Advisory_on_digital | i4c | 2 | 2026-11-23 | https://cybercrime.gov.in/#Advisory_on_digital.pdf |
| 35 | National_Cyber_Crime_Portal_FAQ | i4c |  | 2026-11-24 | https://cybercrime.gov.in/advisory#National_Cyber_Crime_Portal_FAQ.html |
| 36 | National_Cyber_Crime_Portal_FAQ | i4c | 3 | 2026-11-24 | https://cybercrime.gov.in/faq#National_Cyber_Crime_Portal_FAQ.pdf |
| 37 | Advisory on - title needs verification | i4c | 1 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Advisory%20on.pdf |
| 38 | Digital Arrest Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Advisory%20on%20digital.pdf |
| 39 | Advisory regarding fake - title needs verification | i4c | 1 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Advisory%20regarding%20fake.pdf |
| 40 | Fake Stock Market Investment Website App Advisory | i4c |  | 2026-11-24 | https://cybercrime.gov.in/pdf/Advisories/ADVISORY%20TAU-ADV-001%20%2822.04.2024%29.pdf |
| 41 | Digital Arrest Advisory | i4c |  | 2026-11-23 | https://cybercrime.gov.in/pdf/Advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| 42 | Banking Trojans Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Banking%20Trojans.pdf |
| 43 | Business Email Compromise Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20committing%20Business.pdf |
| 44 | Cybercriminals Defrauding Citizens Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20defrauding%20citizens.pdf |
| 45 | Eavesdropping Attacks Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20perpetrating%20Eavesdropping.pdf |
| 46 | Mobile Device Settings Tampering Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20Tampering%20with.pdf |
| 47 | Caller ID Spoofing Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20using%20Caller.pdf |
| 48 | Fake Customer Care Numbers Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20using%20Fake%20Customer.pdf |
| 49 | Fake Social Media Verification Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20using%20fake%20Social%20Media.pdf |
| 50 | Malicious Browser Extensions Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Cybercriminals%20using%20malicious.pdf |
| 51 | Fake Unpaid Electricity Bill SMS Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Fake%20SMSs%20related%20to%20unpaid.pdf |
| 52 | Fake Job Offer SMS Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Fraudsters%20sending%20Fake.pdf |
| 53 | Army Personnel Identity Fraud Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Fraudsters%20using%20Army%20personnel.pdf |
| 54 | Fraudsters Using Heat Signatures | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Fraudsters%20using%20heat.pdf |
| 55 | Malicious Executable Files Advisory | i4c | 2 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Malicious%20Executable%20Files.pdf |
| 56 | Misuse of Matrimonial Platforms Advisory | i4c | 1 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Misuse%20of%20Matrimonial.pdf |
| 57 | Monthly Underground Banking Report | i4c | 33 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/Monthly%20Underground%20Banking%20Report.pdf |
| 58 | WhatsApp Web Account Advisory | i4c | 4 | 2026-11-24 | https://cybercrime.gov.in/assets/learning-corner/advisory/pdf/WhatsApp%20Web%20Account.pdf |
| 59 | Integrated_Ombudsman_Scheme_2026 | rbi | 24 | 2026-11-24 | https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62052#Integrated_Ombudsman_Scheme_2026.pdf |
| 60 | 2026 Customer Protection Amendment | rbi | 3 | 2026-11-23 | https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63011 |
| 61 | Integrated Ombudsman Scheme 2026 | rbi | 2 | 2026-11-23 | https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62052 |
| 62 | Fraud Prevention Master Directions | rbi | 15 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12702 |
| 63 | Payments Banks Amendment Directions 2026 | rbi | 10 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13545 |
| 64 | Authentication Mechanisms for Digital Payments | rbi | 5 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12898 |
| 65 | Customer Protection and Limited Liability Circular | rbi | 7 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11040 |
| 66 | Reserve Bank Integrated Ombudsman Scheme 2026 PDF - verify URL | rbi |  | 2026-11-24 | https://rbidocs.rbi.org.in/rdocs/content/pdfs/SCHEME16012026_A.pdf |
<!-- generated:end -->

## Known gaps

- Start target reached: RBI liability circular, Ombudsman scheme, portal FAQ and 50 unique advisories are collected.
- Current corpus: 66 files, 22.7 MB and 224 pages.
- Full target not reached: three years of CERT-In, I4C and RBI advisories and 10 banks' fraud-reporting policies remain to be collected.
- One I4C download is HTML saved with a `.pdf` extension; it is not a valid PDF and must not be treated as a usable advisory.
- One PDF has almost no extractable text and may need OCR.
- Some files are duplicates or alternate copies of the same document.
- Reuse permission is not yet verified for collected government documents. Confirm terms before using or redistributing their contents.

### Duplicate audit

- SHA-256 audit found 1 duplicate group across 3 different URLs.
- This represents 2 extra downloads.
- All 3 files contain the same HTML fallback page, not the requested PDF/FAQ content.
- These are invalid duplicate downloads, not genuine duplicate publications.
