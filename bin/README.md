# bin/ — Auxiliary tools

## build_index.py

Reference implementation that **derives and regenerates** `ontology/INDEX.md` from file frontmatter. Prevents write contention when multiple agents would otherwise edit INDEX.md in parallel mode (SCHEMA.md §9.4, ORCHESTRATE parallel procedure), and applies the growth rule that splits big Objects sections into per-type sub-indexes (SCHEMA.md §7.1).

```
python bin/build_index.py                      # rewrite INDEX.md
python bin/build_index.py --check              # verify only; exit 1 on mismatch (CI hook)
python bin/build_index.py --root PATH          # operate on another copy (e.g. examples/cafe)
python bin/build_index.py --split-threshold N  # split Objects by type above N entries (default 200)
```

- Stdlib only (no external dependencies). Python 3.
- It parses only the frontmatter subset this template uses — a **reference implementation** you may adapt per domain. The core contract: "in parallel mode, INDEX.md is deterministically regenerated from the canonical files; humans and agents do not hand-edit it".
- In single/sequential mode (Phases 1–2) you may skip it and keep updating INDEX.md by hand, one line per change (summary = first Facts bullet, so hand-written and generated output stay identical).

## search.py

Hybrid retriever over the canon (and, opt-in, open staging entries). **Locator only** — output is a pointer list; a pointer is never a source (HARNESS; QUERY steps 1/4; INGEST step 3). Because the tool is deterministic and LLM-free, it doubles as the retrieval primitive for any agent runtime (call it via shell, or wrap it as an MCP tool).

```
python bin/search.py "<query>"              # search ontology/ (canon)
python bin/search.py "<query>" --staging    # + open candidates/edges + synthesis (grade-labeled)
python bin/search.py "<query>" --top 15     # number of results (default 10)
python bin/search.py "<query>" --root PATH  # operate on another copy (e.g. examples/cafe)
```

Design (stdlib only; scans at query time — no index files, so it is never stale):

- **Distill-then-index** — it indexes the ontology's already-normalized units (objects/definitions), not raw sources. Retrieval quality comes from the normalization the template already enforces; raw sources stay grep territory.
- **Two granularities ("bursting")** — whole files AND individual `## Facts` / `## Proposed Facts` bullets, each bullet prefixed with its parent's title/type, so a single fact inside a big object is findable on its own.
- **Two retrievers fused by Reciprocal Rank Fusion** (RRF, k=60) — word-level BM25 (exact tokens win: IDs, error strings, flags) + character-trigram TF-IDF cosine (fuzzy/partial match, Korean morphology, typos). Consensus across retrievers beats a single strong vote.
- **Per-file cap** — fact-level and file-level hits of the same file merge into one result line (best-matching snippet shown), keeping the top-N diverse.
- **No age decay, no recency-wins** — freshness and contradiction handling belong to INGEST/LINT, never to a ranker. Staging hits are labeled with their grade + created date instead; promoted/rejected candidates are excluded (promoted content lives in the canon). Archived objects are labeled `[object archived]`.
- **Embedding hook** — a real vector retriever can be added as a third ranking fused by the same RRF; the interface is `rank(query) -> [(doc_index, score)]`.

## connector_skeleton.py

Reference connector (SCHEMA.md §9.5) — **copy one per channel** and replace its two channel-specific functions: `extract_units()` (what "one coherent unit" is in your channel) and `distill()` (normalize a unit into a searchable title + Proposed Facts; the built-in heading/bullet extractor is a placeholder good enough for structured notes only).

```
python bin/connector_skeleton.py --source PATH          # scan a source folder
    [--root PATH] [--connector-id NAME] [--date YYYY-MM-DD] [--dry-run]
```

The skeleton keeps the §9.5 contract guarantees regardless of customization: writes only `staging/candidates/` + `STAGING-LOG.md` `[GEN]` lines (rule 1); `sources` = the real source path, never the connector (rule 3); one candidate per unit (rule 4); never edits an existing candidate whatever its status (rule 5); reproducible IDs so re-runs skip instead of duplicating (rule 6). Every run — including a run that emits nothing — appends one `[GEN]` audit line.

Try it on the worked example: `python bin/connector_skeleton.py --source examples/cafe/raw/inbox --root examples/cafe --connector-id inbox` (idempotent — the emitted candidates are already committed).
