---
kind: type
id: supplier
title: 공급업체
description: External company that supplies goods or services to the cafe
properties:
  - name: contact
    required: true
    format: free text
  - name: payment-terms
    required: false
    format: free text
---

## Membership criteria
- External companies with an active or past supply/service contract are this type.
- Internal staff are NOT this type (propose a `person` type if needed).
- One-off vendors (a single purchase, no ongoing contract) are NOT this type — record the purchase as a Fact on the related object instead.
