---
kind: edge-candidate
id: my-edge
status: candidate               # candidate | promoted | rejected — receipt fields below are set at INGEST
# promoted-to: recorded on both object files   # set on promotion
# rejected-reason: one line     # set on rejection
# resolved: YYYY-MM-DD          # set on promotion/rejection
confidence: 0.7
created: 2026-01-01
link-type: undecided
from: object-id-or-candidate-id
to: object-id-or-candidate-id
sources:
  - "raw/source-file-path"
---

## Evidence
- Which passage of which source this relation comes from, one line.
