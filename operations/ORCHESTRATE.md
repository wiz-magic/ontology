# ORCHESTRATE — Running work across multiple roles (org layer)

Follow this document when one piece of work passes through several roles (`ontology/roles/`). It reduces a gstack-style "sprint" to a composition of the 4 kinds of work (INGEST/QUERY/ACT/LINT).

This document **does not replace** INGEST/QUERY/ACT/LINT — it only sequences them. Every step still runs its procedure file's checklist verbatim.

## Sprint stage ↔ the 4 kinds of work

| Sprint stage | Ontology work | Notes |
|---|---|---|
| think / plan | QUERY (+ INGEST if a plan object is created) | Read the existing ontology and plan. T0–T1. |
| build | ACT | Action execution, tier-gated. |
| ship | ACT (T2) | External effect. **Human approval required.** |
| reflect | INGEST + LINT | Newly confirmed facts → INGEST. The retrospective itself is a synthesis (`staging/synthesis`, `status: opinion`) — not fact, so never a canonical object. Then run LINT. |

Outputs of judgment-heavy role steps (design critique, prioritization) go **always to `staging/synthesis` with `status: opinion`**. The only road from there to canonical fact is the INGEST human-confirmation gate — judgment never contaminates the deterministic record.

## Role handoff procedure

1. **Identify the role** — Confirm which role you are acting as; read its `roles/<role-id>.md`.
2. **Check permissions** — Verify this work is inside the role's `allowed-actions` and does not exceed `max-tier`. If it falls outside, do not execute — propose a handoff to a role that has the permission. Never widen your own permissions (HARNESS absolute rule 10).
3. **Do the work** — Follow the matching procedure file. Write only inside the role's `write-scope` (bookkeeping — log appends and INDEX lines for objects written in scope — is always allowed, SCHEMA.md §10).
4. **Leave the handoff artifact** — Leave what the next role will read **as files** (staging artifacts or LOG lines), never as message passing.
5. **Log the handoff** — The sending role appends `[HANDOFF] <from-role> → <to-role>: <artifact paths>` (SCHEMA.md §8; in parallel mode, to its own shard).
6. **Transition gate** — Irreversible transitions (ship etc.) are T2 actions. Follow ACT.md step 4's T2 approval.
7. **Log everything** — Every piece of work goes to LOG (in parallel mode, the role's own shard `LOG-<role-id>.md`).

## Parallel sprints (Phase 3)

Before running multiple role agents concurrently, ALL of the following must be in place. Enabling parallelism without them corrupts the audit trail through LOG/INDEX contention (the exact failure README warns about).

Prerequisites:

- **Area partitioning** — non-overlapping `write-scope` per role (e.g., `staging/candidates/<role-id>/`). Namespace object IDs per role so two roles never write the same object file concurrently.
- **Log sharding** — each role appends only to `ontology/LOG-<role-id>.md` (SCHEMA.md §8.1).
- **Derived INDEX** — agents never edit INDEX.md directly. They only create object files; the integration step regenerates INDEX with `bin/build_index.py` (SCHEMA.md §9.4).
- **Single gatekeeper** — creating/modifying type/link-type/action/role definitions (shared resources) is done by one gatekeeper agent only, logged as `[SCHEMA]` in `LOG.md` (the main shard). No other role changes definitions.

Integration step (at sprint end, performed by a single integration agent):

1. Review and promote every role's `staging/` output through the INGEST gate (filter provenance laundering and synthesized prose).
2. Regenerate INDEX.md with `bin/build_index.py`.
3. Run LINT once (especially firewall checks 9–13).
4. If conflicts/orphans/contradictions are trending up, lower the parallelism and report to the user.

## Adoption order (reverse or simultaneous adoption forbidden)

Judge each phase's stop criteria by machine-counted LINT metrics. There is no "probably fine".

- **Phase 1 (memory layer only)**: create `staging/`; generators produce candidates only. `ontology/` unchanged.
  - Success: the INGEST gate controls promotion; no inaccurate candidate leaks into objects (LINT 1·5·9·10 = 0).
  - Stop: candidates are provenance-laundered (check 9), or generators auto-write into `ontology/INDEX`/`LOG`.
- **Phase 2 (org layer, sequential)**: `role` definitions + 2–3 roles orchestrated sequentially by a single integrated agent.
  - Success: all handoffs file-mediated + irreversible transitions pass T2 human approval; 0 LOG contention.
  - Stop: a role exceeds its permissions — privilege escalation / unauthorized definitions (check 11), or an action outside `allowed-actions`/`max-tier` (blocked at handoff step 2, not by LINT) — or concurrent-write conflicts.
- **Phase 3 (parallel sprints)**: limited concurrency after area partitioning.
  - Success: N roles in parallel without contention + INDEX/LOG integrity maintained through integration.
  - Stop: conflicts/orphans/contradictions trending up → roll back to the previous phase.
