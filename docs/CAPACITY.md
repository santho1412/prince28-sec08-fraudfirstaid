# Capacity plan: FraudFirstAid

Full corpus target: + 3 years of CERT-In, I4C and RBI advisories and 10 banks' fraud-reporting policies (2,000+ pages)

<!-- generated:start -->
## Measured on my start corpus (2026-11-23 16:54 UTC)

| What | Value |
|---|---|
| Files | 11 |
| Size on disk | 3.8 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 82 |
| Characters of text | 205,240 |
| Estimated tokens (characters / 4) | 51,310 |
| Tokens per page | 629 |
| PDFs with almost no text (scanned? OCR is Day 7) | 1 |
| Files not measured (zip, xlsx, unreadable) | 1 |

## Estimate for the full corpus (target: 2,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 24.5 |
| Tokens | measured tokens x scale | 1.26 M |
| Raw files | measured MB x scale | 93 MB |
| Chunks | tokens / 400 x 1.15 overlap | 3,617 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.22 = Rs 21 |
| Vector storage | chunks x 768 numbers x 4 bytes | 11 MB |
| Text in Postgres | characters x scale x 1.2 | 6 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. **Is embedding cost a problem?** No. The estimated one-time cost is only $0.22 (about ₹21) for 2,000 pages.
2. **Do vectors and text fit in free Postgres?** Yes, the estimate is 17 MB total (11 MB vectors + 6 MB text). Confirm that the database dashboard quota exceeds 17 MB.
3. **Which number is least certain?** The 51,310-token estimate. Characters / 4 is only a rough approximation; measure using the actual tokenizer before production.
4. **What changes if the corpus grows 10 times?** At 20,000 pages, estimates become 12.6 million tokens, 36,170 chunks and about $2.20 (₹209) for embeddings.
   Storage grows to approximately 110 MB for vectors and 60 MB for text (170 MB total).
