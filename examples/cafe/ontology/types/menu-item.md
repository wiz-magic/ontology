---
kind: type
id: menu-item
title: 메뉴 항목
description: An item currently or previously sold on the cafe menu
properties:
  - name: price
    required: true
    format: number (KRW)
  - name: category
    required: false
    format: coffee | non-coffee | dessert
---

## Membership criteria
- Items that appear on the customer-facing menu are this type.
- Ingredients (beans, milk, syrup) are NOT this type — they appear as Facts and `supplies` links.
- Discontinued items stay as this type with `status: archived` (SCHEMA.md §4.2) — never delete them.
