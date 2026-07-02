<!-- template-version: 2.1.0 -->

# SCHEMA — Ontology Conventions

This document defines the format of every file under `ontology/` and `staging/`. Do not create files in formats not defined here. If a format is ambiguous, re-read this document; if still ambiguous, copy the format of the nearest existing file.

## 1. IDs and naming

- Every ID is `lowercase-kebab-case`. Non-ASCII IDs (e.g., Korean) are allowed when the domain needs them.
- Filename = `<ID>.md`. IDs are unique within their directory.
- Files whose name starts with `_` (`_TEMPLATE.*`) are format samples, not ontology data. Never list them in INDEX; LINT skips them.
- Type IDs are singular nouns (`supplier`, `menu-item`). Action IDs start with a verb (`order-stock`, `update-price`).
- An ID never changes once created. If the name was wrong, fix `title` only.

## 2. Link syntax

- Reference other objects as `[[object-id]]`, in body and frontmatter alike.
- Direction is written in exactly two ways:
  - `- <link-type-id> → [[B]]` : this object is the link type's `from` (subject)
  - `- <link-type-id> ← [[A]]` : this object is the link type's `to` (target)
  - Which side applies is decided mechanically by matching the link type's `from:`/`to:` against this object's `type:`. Never invent a separate reverse link-type ID.
- A `[[link]]` to a nonexistent ID is forbidden. Create the target object first; if you can't, write plain text instead. (Unlike Karpathy's wiki, unresolved links are not allowed — cheap models mistake them for facts.)

## 3. Object type definition — `ontology/types/<type-id>.md`

```markdown
---
kind: type
id: <type-id>
title: <human-readable name>
description: <one line — what this type represents>
properties:
  - name: <property-name>
    required: true | false
    format: <free text | date (YYYY-MM-DD) | number | enumerated values>
---

## Membership criteria
How to decide whether something is / is not this type. Always state boundary cases.
(e.g., "Employees are NOT this type → use person")
```

## 4. Object instance — `ontology/objects/<object-id>.md`

```markdown
---
kind: object
id: <object-id>
type: <type-id>           # must exist in types/
title: <human-readable name>
updated: <YYYY-MM-DD>
status: active            # active | archived. Optional — absent means active.
props:                    # values for the properties the type declares (§4.1)
  <property-name>: <value>
sources:                  # where this object's facts come from. At least 1.
  - <raw source path>
  - "user:<what — e.g. direct input | adopted decision> YYYY-MM-DD"
  - "ontology:[[base-object-id]]"   # for derived objects built from other objects
---

## Facts
- One fact per line. No guesses or interpretation here.

## Links
- <link-type-id> → [[other-id]]   # when this object is from; use ← when it is to (§2)

## Notes
- Interpretation, uncertain info, open questions. Every line starts with
  `assumption(YYYY-MM-DD):` or `needs-verification(YYYY-MM-DD):`. The date in
  parentheses is the day the note was written and cannot be omitted
  (LINT measures neglect from it).
```

### 4.1 props vs Facts

- `props` hold values for the properties **declared by the object's type** — structured, filterable, machine-checkable.
- Every property the type marks `required: true` must be present in `props` with a non-empty value, **or** the object must carry a dated note `needs-verification(YYYY-MM-DD): <property> missing from source` (LINT check 5).
- A `props` key the type does not declare is a schema violation (keys prefixed `x-` are exempt — §11).
- Facts hold narrative statements. A value may appear in both, but `props` is canonical for declared properties; on conflict, fix whichever the source does not support.

### 4.2 Retirement and merging (never delete)

- When an entity ceases to exist in the domain (contract ended, product discontinued): do **not** delete the file. Set `status: archived`, add a Fact recording the end with its source, and keep all links. Update its INDEX line with the `[archived]` marker (§7).
- Duplicate objects: move any unique facts into the canonical object, then archive the duplicate with the Fact `Merged into [[canonical-id]] (YYYY-MM-DD)`.
- QUERY excludes archived objects from current-state answers (operations/QUERY.md). Deleting object files is not an ontology operation.

## 5. Link type definition — `ontology/links/<link-type-id>.md`

```markdown
---
kind: link-type
id: <link-type-id>         # verb phrase (e.g., supplies, reports-to)
title: <human-readable name>
from: <type-id>
to: <type-id>
cardinality: one-to-one | one-to-many | many-to-many
---

## Meaning
One line stating exactly what "A <link-type> B" means. Also state the reverse reading.
```

Links themselves are not separate files — record them in the `## Links` section of **both** object files (adding A→B means also adding the reverse line to B).

## 6. Action type definition — `ontology/actions/<action-id>.md`

```markdown
---
kind: action
id: <action-id>            # starts with a verb
title: <human-readable name>
tier: T0 | T1 | T2
parameters:
  - name: <parameter-name>
    type: <type-id or format>
    required: true | false
---

## Preconditions
Conditions that must all be true before execution. Write them mechanically checkable.
(e.g., "target object's type is supplier", "quantity > 0")

## Steps
1. Numbered steps. One action per step.

## Effects
What changes in the ontology / external world after execution. Include what to record in LOG.md.

## On failure
What to roll back and what to report.
```

## 7. INDEX.md format

One entry = one line. Sections are fixed per kind. When you create a file, add its line in the same turn (parallel mode excepted — §9.4: INDEX is rebuilt).

```markdown
# INDEX

## Types
- [<type-id>](types/<type-id>.md) — <description, verbatim>

## Objects
- [<object-id>](objects/<object-id>.md) (<type-id>) — <title> — <summary>
- [<object-id>](objects/<object-id>.md) (<type-id>) [archived] — <title> — <summary>

## Link Types
- [<link-type-id>](links/<link-type-id>.md) — <from> → <to>

## Actions
- [<action-id>](actions/<action-id>.md) [T0|T1|T2] — <title>

## Roles
- [<role-id>](roles/<role-id>.md) [max <T0|T1|T2>] — <description, verbatim>
```

- `<summary>` = the **first bullet of the object's `## Facts` section, verbatim**. `bin/build_index.py` uses the same rule, so manual and generated INDEX stay identical.
- INDEX.md lists **confirmed ontology data only**. Nothing under `staging/` ever appears here — INDEX is loaded as fact every session, and an unconfirmed candidate here would be mistaken for fact by cheap models (§9 firewall).

### 7.1 Growth rule (split by type)

INDEX.md is loaded every session, so it must stay small. When the Objects section exceeds **200 entries**:

- Move object lines into per-type sub-indexes `ontology/INDEX-objects-<type-id>.md` (same line format).
- The main Objects section becomes pointers: `- [<type-id>](INDEX-objects-<type-id>.md) — <N> objects`.
- Types / Link Types / Actions / Roles always stay in INDEX.md.
- Sub-indexes are read on demand (QUERY step 1); INDEX.md remains the always-loaded entry point.
- `bin/build_index.py` applies this rule automatically (`--split-threshold`, default 200).

## 8. LOG.md format

append-only. One line = one change. Only these six prefixes:

```
YYYY-MM-DD [INGEST] <what was read> → created: <IDs> / updated: <IDs> / receipts: <candidate: promoted|rejected>
YYYY-MM-DD [QUERY] <question summary> → <supporting object IDs>
YYYY-MM-DD [ACT:<action-id>] <all final parameter values> → <result> (T2: include "approved: user, <date>" — approval binds to the recorded values)
YYYY-MM-DD [LINT] <problems found> → <repaired / reported>
YYYY-MM-DD [SCHEMA] <type/link-type/action/role definitions added or changed> (user confirmed: <date>)
YYYY-MM-DD [HANDOFF] <from-role> → <to-role>: <artifact file paths or LOG references>
```

## 8.1 LOG sharding (parallel mode only)

With a single agent or sequential work (Phases 1–2), use only `LOG.md`.

In parallel mode (Phase 3), shard the log per role to avoid write contention:

- Each role agent appends only to its own shard `ontology/LOG-<role-id>.md` (also append-only).
- `[SCHEMA]` entries (type/link-type/action/role definition changes) are never sharded — only the single gatekeeper agent writes them, to `LOG.md` (the main shard) (operations/ORCHESTRATE.md).
- `[HANDOFF]` entries are written by the sending role, to its own shard.
- For audits, read all `LOG*.md` sorted by date/time. Never edit or reorder existing lines in any shard.

## 9. Memory layer — `staging/` (candidate area)

`staging/` is **outside** the canonical store `ontology/`. It holds output from gbrain-style search/synthesis/auto-wiring engines (or any candidate generator), at the grade of a **"smarter raw source"**.

Core rules (firewall):

- Generators write only to `staging/`. They **never** write to `ontology/` (also block via OS permissions / git where possible — dual defense).
- Nothing in `staging/` is a fact. Until promoted through INGEST (operations/INGEST.md), treat it exactly like a raw source — material for fact extraction, never citable as fact itself.
- Promotion is **one-way**: `staging/ → ontology/` only. Canonical objects never move back to staging.
- `staging/` is never listed in INDEX.md (§7).
- The canonical agent's **only** write inside `staging/` is the candidate status receipt during INGEST (§9.1 lifecycle fields). Everything else in staging is written by generators (or role agents whose write-scope includes staging).

Directory:

```
staging/
├── STAGING-LOG.md          ← generator activity log (append-only). §9.3
├── candidates/             ← object candidates (.candidate.md). §9.1
├── edges/                  ← relation candidates (.edge.md). §9.1
└── synthesis/              ← synthesized answers/opinions (.synthesis.md). §9.2
```

### 9.1 Object candidates / relation candidates

Object candidate — `staging/candidates/[<role-id>/]<candidate-id>.candidate.md`:

```markdown
---
kind: candidate
id: <candidate-id>
type: <type-id or "undecided">  # proposed type. "undecided" → a human classifies at INGEST step 3.
title: <human-readable name>
status: candidate               # candidate | promoted | rejected (lifecycle below)
confidence: <0.0–1.0>           # generator confidence. Reference only — never a promotion criterion.
created: <YYYY-MM-DD>
sources:                        # ≥1. Real sources only.
  - <raw source path or external URL>
---

## Proposed Facts
- One per line. Each must trace back to the real sources above.

## Notes
- Generator remarks. Not facts.
```

**Candidate lifecycle:** a candidate is created with `status: candidate`. At INGEST, the canonical agent records the outcome **on the candidate file** — this receipt is its only permitted staging write:

- promoted → set `status: promoted`, `promoted-to: <object-id>`, `resolved: <YYYY-MM-DD>`
- rejected → set `status: rejected`, `rejected-reason: <one line>`, `resolved: <YYYY-MM-DD>`

Only these fields may change after creation; Proposed Facts are never edited in place. LINT's staleness check (13) counts only `status: candidate`.

Relation candidate — `staging/edges/[<role-id>/]<edge-id>.edge.md`:

```markdown
---
kind: edge-candidate
id: <edge-id>
status: candidate               # candidate | promoted | rejected (same lifecycle as above)
confidence: <0.0–1.0>
created: <YYYY-MM-DD>
link-type: <link-type-id or "undecided">
from: <object-id or candidate-id>
to: <object-id or candidate-id>
sources:
  - <raw source path/URL>
---

## Evidence
- Which passage of which source this relation comes from.
```

**Provenance rule (most important):**

- A candidate's `sources` must contain **real sources only** (documents, URLs).
- **Forbidden** — citing the generator itself (`gbrain`, `vector search`, `embedding proximity`, `co-occurrence`) as a source. That is provenance laundering. Citing another candidate (`staging/*`) is also forbidden.
- A candidate whose `sources` are not real sources is not promotable — INGEST rejects it and LINT detects it.

### 9.2 Synthesis (opinions)

`staging/synthesis/<synthesis-id>.synthesis.md`:

```markdown
---
kind: synthesis
id: <synthesis-id>
status: opinion                 # never a fact. Never auto-promoted to an object.
created: <YYYY-MM-DD>
question: <the question this synthesis answers>
cites:                          # confirmed objects / raw sources the synthesis cites
  - "[[object-id]]"
  - <raw source path>
---

## Synthesized Answer
- Generator-composed prose. A reference answer for humans; asserts no new facts.

## Gaps
- What is still needed to confirm this answer (gap analysis).
```

Synthesis has a **blocked path to objecthood** — it never becomes an object via INGEST (HARNESS absolute rule 9). QUERY may consult it, but must label it "unconfirmed (opinion)" and keep it separate from fact citations (`[[object-id]]`).

### 9.3 STAGING-LOG.md

Audit trail of generator activity. append-only. One line = one run.

```
YYYY-MM-DD [GEN] <what was scanned> → candidates N / edges N / synthesis N
YYYY-MM-DD [DREAM] <enrichment kind: duplicate-marking | relevance scores | contradiction flags> → proposals N (canonical changes 0)
```

**Write authority:** written by whoever generates staging artifacts — an external generator, or a role agent whose `write-scope` includes staging. The canonical ontology agent reads this file but never appends to it; its candidate status receipts are logged in `LOG.md` under `[INGEST]`, not here. Dream cycles touch **staging only** and never modify the canonical store (a nonzero change count is a firewall violation — LINT check 12).

### 9.4 Derived INDEX (parallel mode)

In parallel mode (Phase 3), agents do not edit INDEX.md directly (write contention). Each agent only creates object files; INDEX.md (and any §7.1 sub-indexes) is **regenerated by build** from frontmatter (`bin/build_index.py`, reference implementation). The build output is the catalog. In single/sequential mode you may keep updating INDEX.md by hand, one line per change.

## 10. Org layer — roles (`kind: role`)

Define roles in `ontology/roles/<role-id>.md`. One role = a **bundle of permissions + procedures** for a specialized agent running under the same HARNESS.

```markdown
---
kind: role
id: <role-id>                   # noun (e.g., qa, designer, engineer)
title: <human-readable role name>
description: <one line — what this role is responsible for>
allowed-actions:                # whitelist of executable action IDs. Others are not executable in this role.
  - <action-id>
max-tier: T0 | T1 | T2          # highest reachable tier. Even whitelisted actions above this tier are not executable.
write-scope:                    # directories this role may write. Everything else is read-only.
  - <directory path>            # e.g., staging/candidates/qa/
---

## Responsibilities
- What this role does. One per line.

## Forbidden
- Especially: intruding on other roles' permissions; self-granting wider permissions.

## Handoffs
- receives ← <role-id>: what, in what form (staging artifact / LOG)
- hands → <role-id>: what, in what form
```

Rules:

- Creating or modifying a role definition requires **user confirmation**, same as types/actions (HARNESS absolute rule 6, `[SCHEMA]` log). This is the org-chart-change-needs-sign-off rule.
- No agent may **self-grant** roles, actions, or tiers to itself or another role, nor raise `max-tier` (privilege escalation ban). LINT detects "role/action definitions without a user-confirmation record".
- Handoffs are **file-mediated only** (staging artifacts + LOG), never message passing. Irreversible transitions (e.g., deploy) must be T2 actions requiring human approval. Procedure: operations/ORCHESTRATE.md.
- Bookkeeping is exempt from `write-scope`, which governs domain files only: (a) appending to the audit trail (`LOG.md` or the role's own shard) is **always permitted and required**; (b) in single/sequential mode, adding or updating the INDEX line of an object the role legitimately wrote inside its write-scope is likewise permitted (in parallel mode INDEX is rebuilt instead — §9.4).

## 11. Extension contract (per-project customization)

This template is a base layer. Projects customize it on top; these boundaries keep customizations compatible with the template's guarantees.

**Extension points (allowed):**

- Domain types / links / actions / roles — that is normal use, through the `[SCHEMA]` confirmation gate.
- Extra frontmatter keys prefixed `x-` (e.g., `x-team: growth`) — the builder and LINT ignore them.
- Extra body sections **after** the standard ones (e.g., after Facts/Links/Notes in objects).
- New operations: add `operations/<NAME>.md` **and** register it in HARNESS.md's work-type list. An unregistered procedure does not exist.
- Extra LINT checks, numbered 14+, appended to operations/LINT.md.
- Filling HARNESS `{{ }}` placeholders; adding domain prohibitions.

**Frozen core (fork the template if you must change these):**

- Tier semantics (T0/T1/T2) and the T2 approval contract.
- The six LOG prefixes and all append-only rules.
- The staging firewall: one-way INGEST promotion, the provenance rule, synthesis non-promotion.
- The absolute rules in HARNESS.md.

**Versioning:** this file carries `template-version` on its first line. Record that version in your bootstrap `[SCHEMA]` LOG line (README quick start), so a project can always be traced to the template revision it copied.
