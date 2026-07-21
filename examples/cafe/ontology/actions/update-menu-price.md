---
kind: action
id: update-menu-price
title: 메뉴 가격 변경
tier: T2
parameters:
  - name: item
    type: menu-item
    required: true
  - name: new-price
    type: number (KRW)
    required: true
---

## Preconditions
- An object with id = `item` exists, `type` is `menu-item`, and it is not `status: archived`.
- `new-price` is a number > 0.
- **User approval obtained for these exact parameter values** (T2 — the approval request states the item, current price, new price, and the consequence if wrong; approval binds to the recorded values and never carries over).

## Steps
1. Read the item's object file and note the current `props.price`.
2. Request approval: "change [[<item>]] price <old> → <new-price> KRW; this is customer-visible on the menu".
3. On approval: set `props.price` to `new-price`.
4. Append one Fact: `- 판매 가격이 <old>원에서 <new-price>원으로 변경되었다 (<date>, 승인: user)`.
5. Update the `updated` date.
6. Append one LOG line: `<date> [ACT:update-menu-price] item=<id>, new-price=<value> → done (approved: user, <date>)`.

## Effects
- The item's canonical price changes — **externally visible to customers** (why this is T2 even though the write itself is an internal file edit; see README "grade conservatively").

## On failure
- If interrupted after step 3, revert `props.price` to the old value and report. A price change without its Fact + LOG line is a schema violation.
