---
kind: type
id: equipment
title: 설비
description: A machine the cafe owns or operates
properties:
  - name: model
    required: true
    format: free text
  - name: purchased
    required: false
    format: date (YYYY-MM-DD)
---

## Membership criteria
- Machines used in operations (grinder, espresso machine, refrigerator) are this type.
- Consumables (filters, cleaning agents) are NOT this type.
- Rented machines ARE this type — record the rental terms as a Fact.
