---
kind: link-type
id: maintains
title: 유지보수한다
from: supplier
to: equipment
cardinality: one-to-many
---

## Meaning
"A maintains B" = supplier A holds the maintenance/service contract for equipment B. Reverse reading: B is maintained by A. One supplier can maintain many machines; each machine has at most one maintainer (one-to-many).
