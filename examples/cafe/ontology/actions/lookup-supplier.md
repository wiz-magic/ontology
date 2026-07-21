---
kind: action
id: lookup-supplier
title: 공급처 조회
tier: T0
parameters:
  - name: item
    type: menu-item
    required: true
---

## Preconditions
- An object with id = `item` exists in `objects/` and its `type` is `menu-item`.
- The object is not `status: archived` (for archived items, answer via QUERY with the [archived] marker instead).

## Steps
1. Read the item's object file.
2. Follow every `supplies ←` link in its `## Links` section.
3. Read each linked supplier and collect `contact`, `payment-terms`, and delivery-related Facts.
4. Report: item → suppliers, each with contact and terms, citing `[[id]]` per claim.

## Effects
- No ontology change. Append one LOG line: `<date> [ACT:lookup-supplier] item=<id> → reported N suppliers`.

## On failure
- Item not found / wrong type → report which precondition failed. Nothing to roll back.
