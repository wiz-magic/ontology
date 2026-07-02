---
kind: candidate
id: my-candidate
type: undecided                 # proposed type; "undecided" → a human classifies at INGEST step 3
title: Candidate name
status: candidate               # candidate | promoted | rejected — receipt fields below are set at INGEST
# promoted-to: object-id        # set on promotion
# rejected-reason: one line     # set on rejection
# resolved: YYYY-MM-DD          # set on promotion/rejection
confidence: 0.7                 # generator confidence. Reference only — never a promotion criterion.
created: 2026-01-01
sources:                        # ≥1, real sources only
  - "raw/source-file-path"
---

## Proposed Facts
- One per line. Each must trace back to the real sources above.
- The generator itself (gbrain, vector search) is not a source — no provenance laundering (SCHEMA.md §9.1).

## Notes
- Generator remarks. Not facts.
