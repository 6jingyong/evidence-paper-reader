# Carrier-neutral claim–evidence–reasoning core

This is the carrier-neutral semantic layer underneath Evidence Paper Reader.

A **source** is any inspectable artifact that makes claims and exposes some basis for them: a research paper, technical whitepaper, vendor datasheet, benchmark page, industry report, policy brief, case study, incident postmortem, engineering blog, backtest note, experiment memo, or another evidence-bearing artifact.

The core does not assume that the source is scientific, peer reviewed, academic, or even prose-first.

## Core objects

### Source

Record enough identity to know what artifact is being audited and what material was actually available.

Carrier adapters decide how to express source identity and locations.

### Claim

A source-facing proposition that the source reports, argues, interprets, recommends, or concludes.

Do not replace the source claim with the auditor's criticism before judging support.

### Evidence node

A stable local unit of inspected evidence used by one or more claims.

The same underlying evidence keeps the same E-node identity when reused.

### Evidence relation

For each target claim, every declared E-node has one claim-local relation:

- `supports`
- `undermines`
- `mixed`
- `contextual`

The relation is local to the claim, not a permanent property of the evidence.

### Reasoning edge

An R-edge records the inspectable logical bridge from evidence/upstream claims to a target claim:

- inputs
- inference type
- reasoning status
- added reach
- material assumptions

It is an audit artifact, not hidden chain-of-thought.

### Support judgment

Use:

- `sufficient`
- `partial`
- `insufficient`
- `unclear`

Support summarizes the whole disclosed chain at the claim's stated scope. It is not a vote count over positive/negative evidence labels.

## Carrier-neutral invariants

1. Scope and evidence viability are decided before forcing a claim count.
2. Claims remain source-facing.
3. Every E-node is stable across reuse.
4. In schema v3, every claim-local E-node has exactly one evidence relation.
5. In schema v2+, every auditable claim has at least one reasoning edge.
6. Reasoning edges exactly close over the claim's declared evidence and upstream-claim inputs.
7. Upstream claim dependencies point only backward.
8. Uncertainty cannot disappear downstream without new evidence.
9. Repeated presentation of one underlying result does not create independent confirmation.
10. A local measurement/result is not silently upgraded to a broader construct, causal claim, deployment claim, or universal generalization.
11. Missing information yields `unclear` or a bounded claim, not invented evidence.
12. Source status, branding, prestige, confidence, citation count, or visual polish do not substitute for evidence.
13. The audit does not decide ultimate truth, culpability, author intent, or editorial acceptance.

## Adapter obligations

A carrier adapter must define:

- how source identity is recorded
- how source-local versus external evidence provenance is represented
- how source locations are cited
- any carrier-specific claim types or methodological modules
- how the carrier-neutral audit IR is rendered for users

Adapters may add stricter rules but must not weaken the core invariants.

## Paper adapter

Evidence Paper Reader is currently the first strict adapter.

Its present IR uses:

- `paper_type` as the source-type field
- `paper-local` as the source-local provenance label
- section/figure/table/appendix/page locations
- paper-oriented methodological routing modules
- the seven-section reader-side paper audit renderer

Those names are adapter details. The logical objects—claims, E-nodes, claim-local evidence relations, R-edges, dependencies, and support—are carrier neutral.

## Boundary

Carrier neutrality does not mean every source is auditable.

A marketing page with no inspectable basis can be non-auditable. A vendor datasheet may support a narrow measured specification but not field lifetime. A policy brief may expose a descriptive trend but not identify its cause. A technical blog may contain a reproducible benchmark that supports a local performance claim.

The core asks the same question in each case: **what does this source's disclosed evidence actually carry, and where does the reasoning add unsupported reach?**
