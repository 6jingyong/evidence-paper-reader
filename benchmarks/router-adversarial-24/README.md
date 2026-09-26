# Router Adversarial 24

This benchmark tests whether Evidence Paper Reader loads the right methodological modules for the actual inference rather than for surface keywords.

## Two halves

### 12 semantic-positive cases

The relevant issue is described without the router's canonical vocabulary.

Examples:

- many outcomes, only threshold-crossing results discussed → statistics
- instrument cannot resolve small values and records them as zero → measurement
- extreme prior utilization followed by lower subsequent utilization → design + statistics
- only top day-1 formulations advanced to long cycling → topology
- hundreds of image fields nested inside five animals → dependence + statistics
- truncated visual scale → figure/table
- causal threshold assignment without naming the quasi-experimental design → design + statistics
- author-created index interpreted as trust → measurement + topology
- one result repeated across abstract/results/display/supplement → inventory + claim-evidence reuse

These cases measure semantic recall beyond regex.

### 12 lexical-decoy cases

A canonical cue appears but is irrelevant to the core claim.

Examples:

- "proxy server" is networking, not proxy-to-construct evidence
- "cluster of servers" is not clustered assignment
- "Bayes et al." is an author name
- "regression test suite" is software testing
- a supplement containing biographies does not create a decision-critical external dependency
- a participant-flow figure does not require visual analysis when the audited result is fully stated elsewhere

These cases measure whether the semantic pass can remove incidental lexical hits.

## Architecture under test

```text
plain paper text
    │
    ├─ suggest_modules.py
    │      cheap lexical candidate generation
    │
core claims
    │
    └─ semantic-router-card.md
           claim-level required / not_required / unclear
                 │
                 ▼
           merge_route.py
                 │
                 ▼
           modules + inventory path
```

Merge semantics:

- semantic required adds
- semantic not_required suppresses incidental lexical hits
- semantic unclear preserves lexical hits
- false-positive guards are added after trap-module routing
- inventory uses the same required/not_required/unclear rule

## Metrics

- required-module recall
- forbidden-module trigger rate
- inventory-path accuracy
- exact-case route rate

The benchmark reports the lexical baseline, but CI does not require the lexical baseline to stay bad. If regex improves, the score should improve.

The contract test instead requires that a correct semantic route plus the merge script reaches the reference route exactly.

## Run

Lexical baseline plus perfect semantic reference:

```bash
python benchmarks/router-adversarial-24/score.py
```

After collecting real semantic-router model responses:

```bash
python benchmarks/router-adversarial-24/score.py --semantic-responses responses/
```

Use fresh responses if comparing model versions.

This benchmark evaluates routing only. A routed module is a request to inspect a methodological issue, not a declaration that the paper is flawed.
