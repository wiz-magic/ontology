# INGEST — Adding new information to the ontology

Whenever a new source (document, memo, user statement) updates the ontology, run this checklist top to bottom. Do not skip steps.

## Steps

1. **Check the source** — Read the whole source. If it is a file, note its path. If it is a user statement, prepare `user:direct input <today>` as the source.
   - **Promoting staging candidates**: use this same procedure. The candidate itself is NOT a source — the real sources are what its `sources` list points to. If a candidate's `sources` contain no real source (only the generator itself — gbrain, vector search — or another candidate), **do not promote** (provenance laundering). Reject it in step 7 and report it as "insufficient provenance" in step 9.

2. **Extract facts** — Pull the domain facts out of the source into a scratch list, one per line:
   - Only what the source states. Never supplement from your general knowledge.
   - A statement that requires interpretation is not a fact — classify it as an `assumption:` item.
   - **Discard generator prose.** When promoting, synthesized prose (from `staging/synthesis` or a candidate's Notes) is not evidence. Only what is directly written in the candidate's real sources counts.

3. **Match types** — Decide which object each fact belongs to:
   - Fact about an existing object → mark that file for update. (At scale, you may locate the existing object / check for duplicates with one `bin/search.py` run — pointer only; confirm by reading the file before updating.)
   - Fact about a new entity → find the matching type in INDEX's Types section; read its membership criteria to confirm.
   - **No matching type → do not create the object.** Report the fact as "unclassifiable" and, if warranted, propose a new type to the user.

4. **Create/update objects** — Follow SCHEMA.md §4 (same skeleton as the directory's `_TEMPLATE` file):
   - New object: copy the skeleton and fill it. Put the step-1 sources into `sources`.
   - **Fill `props`**: for every property the object's type declares, set its value in `props` if the source provides it. If a `required` property cannot be filled from the source, **do not guess** — add `needs-verification(<today>): <property> missing from source` to Notes and include it in the step-9 report.
   - **Update vs contradiction**: a newer source superseding an older value with a different effective time (a price change, a new contact) is an **update**, not a contradiction — append it as a new dated Fact; set `props` to the new value only if it is in effect as of today, otherwise leave `props` and let the dated Fact carry the future change. The contradiction rule below applies only when sources disagree about the **same point in time**.
   - Contradiction: if a new fact **contradicts** an existing one about the same point in time, adopt neither. Keep the existing line, add `needs-verification(<today>): <sourceA> says X but <sourceB> says Y` to Notes, and report it. The user decides which is true.
   - **Retirement**: if the source establishes that an entity has ceased (contract ended, product discontinued), do not delete — set `status: archived` and add a Fact recording the end with its source (SCHEMA.md §4.2).
   - Update the `updated` date.
   - Never create `kind: type | link-type | action | role` files in this step (HARNESS absolute rule 6 — user confirmation required).

5. **Update links** — When a fact reveals a relation between two objects:
   - Find the matching link type in INDEX's Link Types. If none fits, do not link — report an "unclassifiable relation".
   - Add the relation to the `## Links` section of **both** object files. Direction per SCHEMA.md §2: `→ [[other]]` on the `from` object, `← [[other]]` on the `to` object.
   - Edge-candidate promotion (`staging/edges`): both `from`/`to` must already be **canonical objects**. If one is still a candidate, promote it first; if you can't, do not promote the edge — report "endpoint not promoted" (unresolved links forbidden, SCHEMA.md §2).

6. **Update INDEX** — Add one line per new object (Objects section, or the type's sub-index if split — SCHEMA.md §7.1). Refresh lines whose summary (first Facts bullet) or `[archived]` marker changed. Parallel mode: skip — INDEX is rebuilt at integration (SCHEMA.md §9.4).

7. **Candidate receipts** (staging promotion only) — On each processed candidate file set the outcome: `status: promoted` + `promoted-to: <object-id>` + `resolved: <today>`, or `status: rejected` + `rejected-reason: <one line>` + `resolved: <today>`. This status receipt is the only write you may perform inside `staging/` (SCHEMA.md §9.1).

8. **LOG** — Append one line to LOG.md: `<date> [INGEST] <source> → created: <IDs> / updated: <IDs> / receipts: <candidate-id: promoted|rejected, …>`.

9. **Report** — Report to the user: objects created/updated, unclassifiable items, contradictions found, rejected candidates. If a category is empty, say "none" explicitly.

## Self-check (verify all before reporting)

- [ ] Does every new object have ≥1 source, and every required prop either filled or covered by a dated `needs-verification` note?
- [ ] Does every added `[[link]]` point to a file that actually exists?
- [ ] Is every relation written on both objects?
- [ ] Are INDEX.md and LOG.md updated (or the parallel-mode exception noted)?
- [ ] (Promotion) Does every adopted fact trace back to the candidate's **real sources** — not the candidate or the generator? Are receipts written on the candidate files?
