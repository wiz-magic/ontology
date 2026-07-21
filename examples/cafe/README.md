# examples/cafe — worked example domain

A small, fully populated instance of the template: operations of a fictional cafe ("도란카페"). Use it to see what each file kind looks like in practice, and as a sandbox for the bundled tools. `SCHEMA.md` and `operations/` are **shared from the template root** — only `HARNESS.md` here is instance-specific (placeholders filled).

## 5-minute tour (read in this order)

1. `ontology/types/` — 3 nouns: `supplier`, `menu-item`, `equipment`. Note the membership boundary cases each one states.
2. `ontology/objects/` — 7 instances. Two demonstrate rules on purpose:
   - [[seoul-dairy]] — a `required` prop (`contact`) missing from the source → covered by a dated `needs-verification` note (SCHEMA §4.1).
   - [[daehan-beans]] — `status: archived` with the contract-end Fact; never deleted (SCHEMA §4.2).
3. `ontology/links/` — `supplies`, `maintains`. Every relation is written on **both** object files (SCHEMA §2).
4. `ontology/actions/` — one per tier: `lookup-supplier` [T0], `log-equipment-issue` [T1], `update-menu-price` [T2] (customer-visible price change → human approval, even though the write itself is a file edit).
5. `ontology/roles/procurement.md` — a permission bundle: 2 allowed actions, max T1, staging-scoped writes.
6. `ontology/LOG.md` — the bootstrap `[SCHEMA]` line and the `[INGEST]` lines that created everything above. `ontology/INDEX.md` is derived from frontmatter.
7. `staging/` — 2 open candidates emitted by the connector skeleton from `raw/inbox/`, plus one synthesis (`status: opinion`) that QUERY may consult but never cite as fact.

## Try the tools (run from the template root)

```
python bin/build_index.py --check --root examples/cafe     # INDEX is derived & current
python bin/search.py "우유 납품" --root examples/cafe        # hybrid search over the canon
python bin/search.py "그라인더 소음" --staging --root examples/cafe   # + open candidates (grade-labeled)
python bin/connector_skeleton.py --source examples/cafe/raw/inbox --root examples/cafe --connector-id inbox
# ^ idempotent: re-running emits 0 new candidates (reproducible IDs — SCHEMA §9.5 rule 6)
```

## Exercise — walk the promotion gate once

Run INGEST (`operations/INGEST.md`) on `staging/candidates/inbox-slack-grinder-noise.candidate.md`:

- Its `sources` point at `raw/inbox/slack-grinder-noise.md` — a **real source**, so it is promotable (the §9.1 provenance rule).
- Extract the facts from the raw file (not from the candidate's prose), update [[grinder-mazzer]], write the `status: promoted` receipt on the candidate, refresh INDEX, and append the `[INGEST]` LOG line.
- Counter-example to reason about: why can `staging/synthesis/latte-cost-review.synthesis.md` never be promoted, no matter how good it is? (HARNESS absolute rule 9.)
