---
kind: role
id: my-role
title: Role Name
description: One line — what this role is responsible for
allowed-actions:
  - action-id
max-tier: T1
write-scope:
  - staging/candidates/my-role/
---

## Responsibilities
- What this role does. One per line.

## Forbidden
- Intruding on other roles' permissions; self-granting wider permissions.

## Handoffs
- receives ← role-id: what, in what form (staging artifact / LOG)
- hands → role-id: what, in what form
