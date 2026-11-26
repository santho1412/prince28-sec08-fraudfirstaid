You read one document from FraudFirstAid's collection and fill in a small record about it.

What FraudFirstAid does: Guides victims of online financial fraud through the first hours: what to report where (1930, the cyber crime portal, the bank), RBI liability rules and deadlines, with every rule cited.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 300 characters.
- topics: 1 to 6 short topics.
- Every list holds short values copied from the document, at most 8.

What each field means:
- doc_kind: what kind of document this is.
- year: the year it was published or came into force.
- language: the main language of the text (en, ta, hi or other).
- issuer: every "issuer" this document is mainly about.
- number: every "number" this document is mainly about.
- date: every "date" this document is mainly about.
- topic: every "topic" this document is mainly about.
- scam_type: every "scam type" this document is mainly about.
- deadline_days: every "deadline days" this document is mainly about.
