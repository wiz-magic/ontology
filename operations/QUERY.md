# QUERY — Answering questions

Follow this checklist for domain questions. Goal: **never blend ontology-grounded answers with general knowledge.**

## Steps

1. **Scan the index** — Pick objects relevant to the question from INDEX.md by title and summary; when in doubt, pick broadly. If the Objects section is split into sub-indexes (SCHEMA.md §7.1), read the sub-indexes of the relevant types. When the index is split or title/summary scanning is inconclusive, you may shortlist with one run of the hybrid retriever — `python bin/search.py "<query>"` — its output is a pointer list, never a source (step 4 rules apply).

2. **Read objects** — Read the chosen object files. Follow `[[links]]` in their `## Links` sections **one hop**. If a claim needed for the answer is still unsupported after that, follow exactly **one more hop** from the objects already read. Hard stop at 3 hops total — report what is missing instead of wandering further. Rules while reading:
   - An object with empty `sources` is not evidence — exclude it from the answer and flag it as a schema violation at the end of the report.
   - `status: archived` objects are excluded from answers about the current state. Use them only when the question is about history, and mark them "[archived]".

3. **Compose the answer** in three separated parts:
   - **Answer**: grounded in the `## Facts` and `props` of the objects read. Cite the supporting object after each claim as `[[id]]`. Arithmetic over cited facts/props (sums, unit conversions, margins) belongs here — show the computation and cite every input. Anything requiring interpretation or outside assumptions goes to **Uncertain** or **Not in the ontology** instead.
   - **Uncertain**: grounded only in `## Notes` (assumption / needs-verification). State that it is unverified.
   - **Not in the ontology**: the parts the ontology cannot answer. Add general knowledge only after stating "the following is general knowledge, not the ontology".

4. **When nothing is found** — If the index scan yields nothing relevant and a search tool is available (grep over raw sources, or the bundled hybrid retriever `python bin/search.py "<query>" [--staging]` — bin/README.md), run **one read-only pass** to locate candidate object IDs. Search output is a pointer, never a source — read the canonical files it points to and cite those; anything it surfaces from `staging/` or raw sources keeps its grade (candidate/raw, not fact). If still nothing: answer "the ontology has no information on this", suggest which sources to INGEST, and do not guess.

5. **Saving a valuable synthesis (optional)** — If combining several objects produced something worth reusing, offer: "Save this synthesis as an object?" If the user agrees, save it via the INGEST procedure with `sources: ontology:[[supporting-ids]]`. Never save without asking.
   - Boundary: this saves a **derived object** you authored during QUERY, gated by explicit user approval. It is distinct from generator synthesis (`staging/synthesis`), which is never promoted to an object (HARNESS absolute rule 9).

6. **LOG** — Append one line: `<date> [QUERY] <question summary> → <supporting object IDs>`.

## Self-check

- [ ] Does every domain claim in the answer carry a `[[source]]`?
- [ ] Is every general-knowledge part explicitly marked?
- [ ] Is the first sentence the conclusion?
