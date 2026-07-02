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
