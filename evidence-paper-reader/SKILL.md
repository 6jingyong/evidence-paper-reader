---
name: evidence-paper-reader
description: read evidence-driven research papers using a reader-side framework that separates claims, evidence, support strength, usable value, and overreach. use when a user wants to know what in a paper is actually trustworthy, what is only partially supported, what is methodologically reusable, or what should be downweighted. supports experimental science, benchmark-heavy methods, quantitative social science, finance/econometrics, clinical and biomedical empirical papers, empirical aesthetics, and other papers with traceable evidence chains. not for pure mathematics, patient-specific clinical decision making, or primarily normative/interpretive theory without a traceable evidence chain.
license: MIT
---

# Evidence Paper Reader

## Goal

Read the paper as a skeptical reader, not as an editor.

Extract what the paper actually demonstrates, separate it from interpretation, and keep uncertainty visible.

Do not score the paper.
Do not simulate peer review.
Do not use publication status as evidence strength.

Default output language follows the user.

## Load order

Always load these three references:
1. `references/core-contract.md`
2. `references/output-contract.md`
3. `references/evidence-types.md`

Then route optional references using:
- `references/method-router.md`
- optionally `scripts/suggest_modules.py` when plain paper text is available and scripts can run

Load `references/domain-profiles.md` only when a listed domain clearly applies.

Do not load every optional reference by default.

## Minimal workflow

### Phase A — scope and claims
1. Inventory what is actually available: main text, figures/tables, supplement/appendix, references, data/code links.
2. Decide scope: `in scope`, `partially in scope`, or `out of scope`.
3. For in-scope papers, extract 3–5 core claims before judging them.
4. Put prerequisite claims before downstream mechanism/causality/generality claims.

### Phase B — evidence ledger
For each claim:
1. assign stable evidence-node IDs such as `E1`, `E2`
2. record evidence type using `evidence-types.md`
3. record provenance: paper-local / external citation / mixed
4. record upstream claim IDs
5. record evidence dependence
6. record the most precise source location available

Use the same E-node whenever the same underlying result is reused.

### Phase C — route only needed checks
Use `method-router.md` or the advisory router script.

Typical optional modules:
- figures/tables → `figure-and-table-traps.md`
- statistical inference → `statistical-traps.md`
- measurement/instruments → `measurement-traps.md`
- assignment/sampling/causal identification → `study-design-traps.md`
- mechanical coupling/proxy/selection/transfer → `evidence-topology.md`
- multiple evidence units/replication → `evidence-dependence.md`
- evidence reused across claims → `claim-evidence-links.md`
- claim-to-claim inference chain → `claim-dependencies.md`
- external citation or missing-material dependency → `follow-up-boundaries.md`

Whenever a trap module is used, also apply:
- `false-positive-guards.md`

A cue triggers inspection, not automatic criticism.

### Phase D — support judgment
For each claim, choose exactly one:
- sufficient
- partial
- insufficient
- unclear

Judge the claim as written.

Do not silently narrow it first.
Do not let upstream uncertainty disappear without new evidence.
Do not treat repeated analyses of the same source as independent replication.
Do not let abstract/conclusion prose override more direct paper-local results.

### Phase E — render
Use `output-contract.md` exactly.

For out-of-scope papers, keep the seven-section skeleton and use `not applicable` where appropriate.

## Mandatory boundaries

A literature citation is not paper-local evidence.

Do not claim knowledge of an external paper unless it was inspected.
Do not guess DOIs from memory.

A non-significant result is not automatically:
- no effect
- equivalence
- safety
- practical irrelevance

Methodological world knowledge may interpret evidence, but must not replace it with expected domain values, normal ranges, treatment effects, material properties, market behavior, or field consensus.

For medical papers, audit design and evidence only; do not convert the audit into patient-specific treatment advice or an independent standard-of-care recommendation.

## Weak-model mode

When context or model capability is limited:

1. keep only `core-contract.md`, `output-contract.md`, and `evidence-types.md` loaded initially
2. extract claims first
3. run or consult the router
4. load at most the modules that match decision-critical claims
5. audit one claim at a time
6. run `tests/validate_audit.py` on the finished audit when a Python runtime is available

If the paper is long, prioritize:
- abstract/conclusion for claim extraction
- results + decision-critical figures/tables for evidence
- methods needed to interpret those claims
- cited work only when structurally necessary

Do not spend context on irrelevant sections merely to be exhaustive.

## Optional deep references

Use these only when the compact contract is not enough:
- `references/claim-evidence-links.md`
- `references/claim-dependencies.md`
- `references/evidence-dependence.md`
- `references/evidence-topology.md`
- `references/follow-up-boundaries.md`
- `references/pollution-patterns.md`

## Validation

The zero-dependency validator checks the mechanical contract:
`python tests/validate_audit.py <audit.md>`

It verifies fields, controlled values, claim numbering, evidence-node syntax, convergence-node count, provenance/dependency rules, and conservative uncertainty propagation.

The validator cannot decide whether a scientific interpretation is true. Semantic judgment remains the model's job.
