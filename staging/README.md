# staging/ — Memory layer (candidate area)

This directory is **outside** the canonical store `ontology/`. It holds output from gbrain-style search/synthesis/auto-wiring engines (or any candidate generator), at the grade of a **"smarter raw source"**.

Full conventions: `SCHEMA.md` §9. The core:

- Generators write only here. They never write to `ontology/`.
- Nothing here is a fact — it is a candidate. Becoming canon requires the promotion gate in `operations/INGEST.md`.
- A candidate's sources must be **real sources** — citing the generator itself ("found by vector search") is provenance laundering and blocks promotion.
- Synthesis (`synthesis/`, `status: opinion`) is reference material for humans and is never promoted to an object (fact).
- Candidate lifecycle: `candidate → promoted | rejected`. The canonical agent records the outcome on the candidate file at INGEST (its only write here); LINT tracks stale open candidates.
- **Connectors** — continuous feeds (chat threads, code repos, team databases) are ordinary generators bound by one uniform contract: distill each source unit and emit these same candidate/edge/synthesis file kinds, real sources only. Full contract: `SCHEMA.md` §9.5; reference implementation: `bin/connector_skeleton.py` (copy one per channel).
- Open candidates and synthesis are searchable alongside the canon via `python bin/search.py "<query>" --staging` — results are grade-labeled pointers, never facts.

```
staging/
├── STAGING-LOG.md   ← generator activity log (append-only)
├── candidates/      ← object candidates (.candidate.md)
├── edges/           ← relation candidates (.edge.md)
└── synthesis/       ← synthesized answers/opinions (.synthesis.md)
```
