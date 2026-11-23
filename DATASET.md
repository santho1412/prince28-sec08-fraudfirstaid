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
## Sources (generated 2026-11-23 16:54 UTC by scripts/dataset_report.py)

| Source | Licence / terms | Files | MB | Pages* | How | Fetched | Example URL |
|---|---|---|---|---|---|---|---|
| certin | Official CERT-In publication; reuse permission not yet verified | 3 | 2.1 | 38 | http | 2026-11-23 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2025-0019&pageid=PUBVLNOTES02 |
| i4c | Official government publication; reuse permission not yet verified | 2 | 0.9 | 2 | http+manual | 2026-11-23 | https://cybercrime.gov.in/pdf/Advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| rbi | Official RBI publication; reuse permission not yet verified | 6 | 0.8 | 42 | http | 2026-11-23 | https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63011 |

**Total:** 11 files, 3.8 MB, 82 pages. Not downloaded: 0 blocked by robots.txt, 0 failed.

*Pages = PDF pages, plus one page per 3,000 characters of text or HTML.

## Files (first 11 of 11)

The complete list, with a sha256 fingerprint of every file, is `data/manifest.jsonl`.

| # | Title / file | Source | Pages | Fetched | URL |
|---|---|---|---|---|---|
| 1 | CERT-In Directions 2022 | certin | 8 | 2026-11-23 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf |
| 2 | CERT-In Directions FAQs | certin | 28 | 2026-11-23 | https://www.cert-in.org.in/PDF/FAQs_on_CyberSecurityDirections_May2022.pdf |
| 3 | Cybersecurity Advisory CIAD-2025-0019 | certin | 2 | 2026-11-23 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2025-0019&pageid=PUBVLNOTES02 |
| 4 | Advisory_on_digital | i4c | 2 | 2026-11-23 | https://cybercrime.gov.in/#Advisory_on_digital.pdf |
| 5 | Digital Arrest Advisory | i4c |  | 2026-11-23 | https://cybercrime.gov.in/pdf/Advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| 6 | 2026 Customer Protection Amendment | rbi | 3 | 2026-11-23 | https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63011 |
| 7 | Integrated Ombudsman Scheme 2026 | rbi | 2 | 2026-11-23 | https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62052 |
| 8 | Fraud Prevention Master Directions | rbi | 15 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12702 |
| 9 | Payments Banks Amendment Directions 2026 | rbi | 10 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13545 |
| 10 | Authentication Mechanisms for Digital Payments | rbi | 5 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12898 |
| 11 | Customer Protection and Limited Liability Circular | rbi | 7 | 2026-11-23 | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11040 |
<!-- generated:end -->

## Known gaps

- The start target is incomplete: only 11 files and 82 pages are collected; 50 advisories and portal FAQs are still missing.
- The full target is not reached: 10 banks' fraud-reporting policies and three years of CERT-In, I4C and RBI advisories remain to be collected.
- One I4C download is HTML saved with a `.pdf` extension; it is not a valid PDF.
- One PDF has almost no extractable text and may need OCR.
- Reuse permission is not yet verified for the collected government documents. Confirm terms before using or redistributing their contents.
