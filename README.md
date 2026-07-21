# Ontology + Harness Template

A general-purpose base layer that structures domain knowledge into **semantic units a computer (LLM) can understand**, and defines the guardrails and runtime rules that let an AI agent **complete work autonomously without improvising** on top of it.

Template version: see `template-version` at the top of [SCHEMA.md](SCHEMA.md). Record it in your bootstrap log line (quick start step 6).

It synthesizes six proven designs. The first three are the core skeleton; the last three are layers adopted **behind guardrails** (see "3-layer architecture" below):

| Source | What was taken |
|---|---|
| Palantir Ontology | object types / properties / link types / **action types** — separation of knowledge (semantic layer) and behavior (kinetic layer) |
| Karpathy's LLM Wiki | raw sources immutable, wiki maintained by the LLM, conventions in a schema doc — the INGEST / QUERY / LINT operating loop |
| Claude system prompts (harness engineering) | permission tiers, autonomy boundaries, verification duties, failure behavior declared as explicit sections |
| garrytan/gbrain (memory layer) | hybrid search · gap analysis · candidate generation — but behind a **firewall**: operates only in `staging/` outside the canon; facts are promoted only through the INGEST gate (SCHEMA §9) |
| garrytan/gstack (org layer) | role division (virtual team) · sprint rhythm — but **only the role taxonomy, not the skill bodies**: role = `kind: role`, handoffs = tier-gated (SCHEMA §10) |
| Cerebras Knowledge Base ("How we built our knowledge base") | hybrid retrieval (lexical + fuzzy, RRF fusion) · distill-then-index · fact-level "bursting" · a uniform connector contract — but demoted to **locator duty**: search output is a pointer, never a source; connectors write only to `staging/` (SCHEMA §9.5, `bin/search.py`). Age-decay/recency-wins and answer-synthesis-as-fact were deliberately **not** taken (they conflict with the firewall) |

## Core design principles

**The cheapest model must still work.** So this template never relies on a model's "sense":

1. **Minimal judgment** — every point that needs judgment gets an explicit decision rule. There is no "handle appropriately".
2. **Forced checklists** — every procedure (operations/) is numbered steps that cannot be skipped.
3. **Forced output skeletons** — every file follows a frontmatter schema. No free-form output.
4. **Progressive disclosure** — never load everything per session. Only `INDEX.md` is always loaded; procedure docs are read only when doing that work. The smaller the model's context, the more this helps.
5. **Safety tiers (T0/T1/T2)** — every action has a tier; irreversible/externally-visible actions (T2) mechanically require human approval. The model gets no room to decide "this is probably fine".
6. **Every change in the log** — `LOG.md` is append-only. The single source for audits and debugging.

## Directory layout

```
ontology_v3/
├── README.md            ← this document (for humans; agents don't read it)
├── HARNESS.md           ← agent system prompt. Loaded whole every session
├── SCHEMA.md            ← ontology conventions (naming, IDs, frontmatter, links, extension contract)
├── ontology/            ← ❶ knowledge layer (canon = system of record)
│   ├── INDEX.md         ← full catalog. Loaded every session. One entry = one line
│   ├── LOG.md           ← append-only work log
│   ├── types/           ← object type definitions (the domain's "nouns")
│   ├── objects/         ← object instances (actual knowledge units)
│   ├── links/           ← link type definitions (the "grammar" of relations)
│   ├── actions/         ← action type definitions (the agent's "verbs" + guardrails)
│   └── roles/           ← ❸ org layer: role definitions (kind: role)
├── staging/             ← ❷ memory layer: gbrain-style candidate area (outside canon, raw-source grade)
│   ├── STAGING-LOG.md   ← generator activity log (append-only)
│   ├── candidates/      ← object candidates
│   ├── edges/           ← relation candidates
│   └── synthesis/       ← synthesized answers/opinions (status: opinion, not facts)
├── operations/
│   ├── INGEST.md        ← adding new information (= the staging→canon promotion gate)
│   ├── QUERY.md         ← answering questions
│   ├── ACT.md           ← executing actions (the heart of the harness)
│   ├── LINT.md          ← integrity checks (+ firewall checks 9–13)
│   └── ORCHESTRATE.md   ← multi-role sprint procedure (org layer)
├── bin/
│   ├── build_index.py         ← regenerates INDEX.md from frontmatter (parallel mode / big ontologies)
│   ├── search.py              ← hybrid retriever (locator only): BM25 + trigram fused by RRF, fact-level bursting, opt-in staging sweep
│   └── connector_skeleton.py  ← reference connector (SCHEMA §9.5): copy per channel, replace 2 functions
└── examples/cafe/       ← worked example domain (cafe operations). Start here
```

## Quick start — applying to a new domain

1. Open `examples/cafe/` and see what types/objects/links/actions/roles look like in practice (5 minutes).
2. Pick 3–7 **nouns** of your domain and define them in `ontology/types/` (copy `types/_TEMPLATE.type.md`).
3. Define 2–5 **relations** between those nouns in `ontology/links/`.
4. Define the **verbs** the agent may perform in `ontology/actions/`, each with a safety tier (T0/T1/T2). **This step IS the harness — grade conservatively.** Decision rule: observe-only → T0; changes only ontology-internal files and is reversible → T1; everything else — leaves the system, is seen by others, or touches money/contracts/deletion — → T2. In domains where mistakes are costly (medical, finance, legal), elevate even internal edits to T2 (e.g., editing a medication guideline; in the cafe example, `update-menu-price` is elevated the same way).
5. Fill the `{{ }}` placeholders in `HARNESS.md` (domain name, user, prohibitions, LINT cadence). `operations/LINT.md` also has `{{N}}` and two `{{period}}` placeholders.
6. **Bootstrap log** — append one `[SCHEMA]` line to `ontology/LOG.md` listing every definition created in steps 2–4, with `(user confirmed: <date>)` and the template version, e.g.
   `2026-06-01 [SCHEMA] bootstrap from ontology-template v2.1.0 — types: a, b; links: x; actions: y [T1]; role: z [max T1] (user confirmed: 2026-06-01)`
   Without this line, the first LINT will flag all your definitions as unauthorized (check 11).
7. Start each agent session with `HARNESS.md` + `ontology/INDEX.md` in the system prompt / first message. Done.
   - **Claude Code**: import both from the project's `CLAUDE.md` (e.g., `@HARNESS.md` and `@ontology/INDEX.md`), mark raw-source directories read-only via permissions, and require approval for tools that can produce T2 effects (send/delete/spend). The HARNESS approval flow is the behavioral layer on top of those hard gates.

## Using this as the base knowledge layer of any project

This template is meant to be copied into a project and customized. Two contracts keep that safe:

**What to extend vs. what to freeze** — see SCHEMA.md §11. In short: domain types/links/actions/roles, `x-` frontmatter keys, extra body sections, and new registered operations are extension points; tier semantics, LOG prefixes, append-only rules, the staging firewall, and the absolute rules are frozen (fork if you must change them).

**Where each kind of knowledge lives** — so different projects don't invent incompatible conventions:

| Kind of knowledge | Where it lives |
|---|---|
| **Entities** — things that exist: suppliers, services, incidents, documents | `types/` + `objects/` (Facts, props, Links) |
| **Adopted norms** — style guides, policies, principles the team has decided on (e.g., a technical writing guide) | Objects of a domain type such as `guideline`. Source = the adoption decision (`user:adopted YYYY-MM-DD`) or the source document. If the agent must also *obey* the norm while acting, additionally wire it into HARNESS prohibitions or action preconditions — retrieval and enforcement are separate concerns |
| **Procedures for the agent itself** — how to do a kind of work | `operations/*.md`, registered in HARNESS's work-type list (SCHEMA §11). Not objects |
| **Unconfirmed ideas, generator output, drafts** | `staging/` (candidates / synthesis) — never Facts |

**Upgrading**: a project records which `template-version` it copied (bootstrap log line). Upgrading = diff the template docs (HARNESS/SCHEMA/operations) against yours; your domain definitions and objects are data and are unaffected.

## Dual defense — back prompt rules with the environment

HARNESS.md rules are only the first line of defense. Where possible, make violations impossible at the **environment (permission) level** too:

- **Protect raw sources**: set the raw-source directory read-only at the OS level, or exclude it from the agent's write scope. Even if "never modify" is violated, modification is impossible.
- **Protect the audit trail**: version `ontology/` with git. Even if append-only is violated, the diff exposes and restores it.
- **Block T2**: where possible, gate T2-capable tools (send/delete/spend) at the tool/permission level as well (e.g., the agent runtime's permission settings). The HARNESS approval flow is the behavioral contract on top.
- **Domain prohibitions**: `{{absolute prohibitions}}` in HARNESS is policy. Anything detectable (e.g., a national-ID pattern) should also be added as a LINT check — dual coverage.

## What is "raw" and what is "wiki"

- **Raw sources**: meeting notes, documents, data dumps. Kept outside the ontology. The agent reads them and never modifies them.
- **Ontology (= wiki)**: everything under `ontology/`. The agent creates and updates it by procedure. Humans review and steer, but consistency upkeep (cross-links, index, contradiction detection) is the agent's job.

## 3-layer architecture — accumulated context becomes a company

This template is designed so that as context accumulates it grows into a "company" — **not an autonomously drifting one, but one under hard governance**. Three layers, each inside its own permission boundary:

- **❶ Knowledge layer `ontology/`** — the canon (system of record). The single source of "what is true". Deterministic, fully sourced; definition changes require human confirmation. **Untouchable by generators.**
- **❷ Memory layer `staging/`** — candidate area for gbrain-style search/synthesis/auto-wiring engines. Handles indexing, recall, and gap diagnosis of institutional memory. But it is graded a **"smarter raw source"** — candidates, not facts; the only path to canon is the INGEST promotion gate.
- **❸ Org layer `ontology/roles/`** — role definitions. A role = a permission bundle for a specialized agent under the same harness. Handoffs between roles are file-mediated and tier-gated.

### The firewall — why not merge them wholesale

gbrain and gstack stand on the **opposite bet about model capability** from this template. This template bets on "the cheapest model still works" (minimal judgment, determinism); gbrain bets on probabilistic retrieval and autonomous enrichment; gstack bets on "real judgment by capable models". Merging them wholesale silently destroys the safety guarantees. Instead, the template reuses its own raw-vs-wiki bulkhead to contain both:

- Generators (gbrain-style) write only to `staging/`. `ontology/` is read-only to them — enforce with OS permissions/git too where possible (dual defense).
- A candidate's sources must be **real sources**. Citing the generator itself ("found by vector search") is **provenance laundering** and blocks promotion (LINT check 9).
- Synthesized answers (`status: opinion`) are reference material for humans and are never promoted to objects (absolute rule 9).
- From gstack, only the **role taxonomy** is adopted — not judgment steps like "the CEO reviews and decides" with no criteria. Judgment outputs live in `staging/synthesis` as opinions; the only road to fact is INGEST with human confirmation.

### What "becomes a company" means — governance is already here

A company's reliability comes from **governance**, not from roles or memory. The four governance elements are structurally stronger here than in gstack — keep them, never trade them away:

| Corporate institution | Mechanism in this template |
|---|---|
| Audit trail | append-only `LOG.md` + git dual defense |
| Approval chain | T2 approval — valid once, for the exact parameter values; any change requires re-approval |
| Internal audit | periodic LINT (broken links, missing sources, firewall violations) |
| Charter / org changes | creating or changing type/action/**role** definitions requires human confirmation (absolute rules 6·10 — blocks agent privilege escalation) |

So the company *grows* as context accumulates, but the power to change the "book of facts" and the "charter" always sits behind a human gate.

### Adoption order (reverse or simultaneous adoption forbidden)

1. **Phase 1 — memory layer only**: create `staging/`, run generators as candidate generators. `ontology/` unchanged.
2. **Phase 2 — org layer (sequential)**: define `role`s; 2–3 roles run sequentially by a single integrated agent.
3. **Phase 3 — parallel sprints**: only after area partitioning + log sharding + derived INDEX + a single gatekeeper are in place.

Success/stop criteria per phase are pinned to machine-countable LINT metrics. Details: `operations/ORCHESTRATE.md`.

## FAQ

**Q. How many types should I create?**
Start small. Start with 3 and add a type only when LINT repeatedly reports "unclassifiable objects".

**Q. What if the model breaks the rules?**
Usually because HARNESS.md wasn't in context or got truncated. HARNESS.md is designed to stay short — put procedure detail in operations/, never in HARNESS.md.

**Q. What when INDEX.md gets big?**
The growth rule (SCHEMA §7.1) splits the Objects section into per-type sub-indexes at 200 entries; `bin/build_index.py` applies it automatically. INDEX.md stays small and always-loaded. For recall beyond title/summary scanning at that scale, `bin/search.py` provides hybrid search over the canon — pointer-only, wired into QUERY steps 1/4.

**Q. Can multiple agents work at the same time?**
LOG.md and INDEX.md become write-contended. If you need concurrency, follow Phase 3 (ORCHESTRATE): partition write scopes per role, shard logs, regenerate INDEX by build, and route all definition changes through a single gatekeeper.


##made by. wiz-magic
https://github.com/wiz-magic
