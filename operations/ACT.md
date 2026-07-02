# ACT — Executing actions (the heart of the harness)

Every "action" that is not an ontology update (INGEST) — operating external systems, sending messages, deleting files, deciding after computation — is performed only through this procedure.

**Prime rule: an action not defined in `ontology/actions/` does not exist.** If the user requests an undefined action, do not execute it — draft a new action type (SCHEMA.md §6 format) and show it. Propose T2 for the draft's tier when in doubt, and **the draft — including its tier — justifies no execution until the user confirms it in full** (HARNESS absolute rule 6). Once confirmed, save it to actions/, log a `[SCHEMA]` line, then execute via this procedure from step 1.

## Steps

1. **Identify the action** — Find the matching action in INDEX's Actions section and read the whole action file.

2. **Pin the parameters** — Fill every parameter in the action definition. A value may come from exactly two places: (a) the user said it directly, or (b) it is **uniquely** determined by the ontology's facts, `props`, or links — in that case note the supporting objects and cite them in the approval request/report. If there are two or more candidate values, or no source, do not execute — ask the user. Never fill by guessing.

3. **Check preconditions** — Verify the action's `## Preconditions` line by line. If any is false or unverifiable, do not execute; report which condition blocked and why.

4. **Tier gate**:
   - **T0**: proceed to step 5.
   - **T1**: proceed to step 5, but record the pre-change state so the report can include it.
   - **T2**: stop and request user approval in this format:
     ```
     [T2 approval request] <action-id>
     - What: <every parameter value, explicitly>
     - Why: <connection to the request; cite supporting objects for any ontology-derived parameter>
     - If it goes wrong: <the irreversible consequence>
     Execute?
     ```
     No execution without an explicit "yes". Silence, topic change, or a conditional reply is not approval. **Approval is valid for one execution with exactly the stated parameter values.** If any value changes after approval (whether the user changed it or a recomputation did), restart from step 4.

5. **Execute** — Perform the action's `## Steps` in order. Immediately before any state-changing command, confirm two things: (1) the parameter values about to be used are exactly the ones pinned in step 2 and (T2) approved, (2) the evidence actually supports this specific action. If anything unexpected appears mid-run (state differs from the precondition check, an error, a branch not in the definition), **stop immediately** and report to the user.

6. **Verify** — Confirm through an observable means that the changes in the action's `## Effects` actually happened. If you cannot verify, report "executed but unverified". Never report "it probably worked".

7. **LOG** — `<date> [ACT:<action-id>] <all pinned parameter values> → <verified result>` (T2: include `approved: user, <date>` — the approval binds to the recorded values).

8. **Report** — Conclusion first: what was executed and what the verification showed. On failure, include the failure output verbatim.

## On failure

- Follow the action's `## On failure`. If the failure is not covered there: roll back what is reversible; if irreversible, report the exact current state.
- If the same action fails twice for the same reason, stop trying.

## Self-check

- [ ] Was the executed action defined in actions/?
- [ ] If T2, was explicit approval received this turn?
- [ ] Were the effects verified — or the report explicit that they weren't?
- [ ] Was it logged?
