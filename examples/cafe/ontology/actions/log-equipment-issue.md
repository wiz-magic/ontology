---
kind: action
id: log-equipment-issue
title: 설비 이슈 기록
tier: T1
parameters:
  - name: equipment
    type: equipment
    required: true
  - name: issue
    type: free text
    required: true
---

## Preconditions
- An object with id = `equipment` exists in `objects/` and its `type` is `equipment`.
- `issue` is a non-empty observation (what happened, when noticed). Interpretation of the cause belongs in Notes as `assumption:`, not in the issue text.

## Steps
1. Read the equipment's object file.
2. Append one Fact: `- <date> 이슈 보고: <issue>` (source: `user:direct input <date>` added to `sources` if not already present).
3. Update the `updated` date.
4. Append one LOG line: `<date> [ACT:log-equipment-issue] equipment=<id>, issue=<issue> → Fact appended`.

## Effects
- The equipment object gains one dated Fact. Reversible (T1) — the file change can be reverted via git.

## On failure
- If the file write fails partway, restore the file from git and report. Never leave a Fact without its source.
