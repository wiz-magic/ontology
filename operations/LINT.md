# LINT — Integrity check

Mechanically checks the ontology's consistency. Run on cadence (every {{N}} INGESTs) or on user request.

## Checks (all, in order)

Files whose name starts with `_` (templates) are excluded from every check. Frontmatter keys prefixed `x-` are project extensions — ignore them (SCHEMA.md §11). `staging/` is not canon, so checks 1–8 do not apply to it (only firewall checks 9–13 do).

1. **Broken links** — every `[[link]]` in object files points to a file that exists.
2. **Orphan objects** — objects with no relations at all, only an INDEX summary. Archived objects are exempt. (Not an error — report only.)
3. **Index mismatch** — every file in `objects/ types/ links/ actions/ roles/` appears in INDEX.md (or its sub-indexes when split — SCHEMA.md §7.1), and every INDEX line points to a file that exists.
4. **Asymmetric relations** — A has `→ [[B]]` but B lacks `← [[A]]` (or vice versa).
5. **Schema violations** — missing required frontmatter fields; a `type:` referencing a nonexistent type; empty `sources`; undated `assumption:`/`needs-verification:` notes; a property the object's type marks `required: true` missing from `props` with no corresponding dated `needs-verification` note; a `props` key the type does not declare (`x-` keys exempt).
6. **Contradiction candidates** — conflicting facts within one object; `needs-verification(date):` notes older than 30 days.
7. **Stale objects** — `updated` older than {{period, recommended 90 days}}. Archived objects are exempt. (Report only.)
8. **Cardinality violations** — a link type with `cardinality` one-to-one or one-to-many where the "one" side carries two or more links. (Report only.)

### Firewall checks (memory & org layers)

9. **Provenance laundering** — objects in `ontology/objects/` whose `sources` point to a generator (`gbrain`, `vector search`, `embedding`, …) or to a `staging/` path. Canonical sources must be real sources. (Report only — a human decides to fix the source or demote the object.)
10. **Synthesis leakage** — files inside `ontology/objects/` with `status: opinion` or `kind: synthesis` (synthesis must never sit in the canon). (Report only.)
11. **Privilege escalation / unauthorized definitions** — definitions in `types/ links/ actions/ roles/` with no matching `[SCHEMA] … (user confirmed: …)` line in LOG (all 4 definition kinds require user confirmation — absolute rules 6·10). The bootstrap `[SCHEMA]` line (README quick start step 6) covers the initial set. (Report only.)
12. **Dream-cycle intrusion** — `[DREAM]` lines in `staging/STAGING-LOG.md` that do not report `(canonical changes 0)` (a signal the generator touched the canon). (Report only.)
13. **Staging hygiene** — candidates/edges still `status: candidate` more than {{period, recommended 30 days}} after `created` (stale); and `status: promoted` entries whose `promoted-to` object does not exist (broken receipt). (Report only.)

## Repair rules

- **Repair immediately (T1, without asking)**: of index mismatches (3), **only adding missing files to INDEX**; of asymmetric relations (4), **only adding the missing reverse line**. LINT's auto-repair is always additive/restorative, never deleting.
- **Report only (human decision required)**: broken links (1 — whether to create the object or drop the link is a domain call), orphans (2), broken INDEX lines (3 — never delete the line, absolute rule 7), schema violations (5), contradictions (6), staleness (7), cardinality (8), and **all firewall checks (9–13)**.
- `actions/` and `roles/` files are never auto-repaired — report any problem (action/role definition changes require user confirmation).
- During LINT, never add, delete, or edit Facts or props values. LINT touches structure only.

## Report format

```
[LINT result] 13 checks completed
- Repaired: <items and counts, or "none">
- Needs human decision: <list per check, or "none">
- Ontology size: objects N (archived N), types N, link types N, actions N, roles N | staging: open candidates N, synthesis N
```

Finally append to LOG.md: `<date> [LINT] N problems → repaired N / reported N`.
