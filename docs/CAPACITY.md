# Capacity plan: FraudFirstAid

Full corpus target: + 3 years of CERT-In, I4C and RBI advisories and 10 banks' fraud-reporting policies (2,000+ pages)

<!-- generated:start -->
## Measured on my start corpus (2026-11-24 06:09 UTC)

| What | Value |
|---|---|
| Files | 66 |
| Size on disk | 22.7 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 224 |
| Characters of text | 470,733 |
| Estimated tokens (characters / 4) | 117,683 |
| Tokens per page | 525 |
| PDFs with almost no text (scanned? OCR is Day 7) | 1 |
| Files not measured (zip, xlsx, unreadable) | 4 |

## Estimate for the full corpus (target: 2,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 8.9 |
| Tokens | measured tokens x scale | 1.05 M |
| Raw files | measured MB x scale | 203 MB |
| Chunks | tokens / 400 x 1.15 overlap | 3,018 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.18 = Rs 17 |
| Vector storage | chunks x 768 numbers x 4 bytes | 9 MB |
| Text in Postgres | characters x scale x 1.2 | 5 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. **Is embedding cost a problem?** No. The estimated one-time cost is approximately $0.18 (about Rs 17) for 2,000 pages.

2. **Do vectors and text fit in free Postgres?** The estimate is approximately 14 MB total: 9 MB for vectors and 5 MB for text. Confirm that the database dashboard quota exceeds this estimate.

3. **Which number is least certain?** The estimated 117,683 tokens. Characters divided by four is only a rough approximation. Measure using the actual tokenizer before production.

4. **What changes if the corpus grows 10 times?** At 20,000 pages, estimates become approximately 10.5 million tokens, 30,180 chunks and $1.81 (about Rs 172) for embeddings. Storage grows to approximately 93 MB for vectors and 51 MB for text, or 144 MB total.
