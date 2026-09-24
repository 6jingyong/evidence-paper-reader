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

Always load:
1. `references/core-contract.md`
2. `references/evidence-viability.md`
3. `references/evidence-types.md`

For output:
- when Python can run, load `references/audit-ledger-format.md` and use `scripts/render_audit.py`
- otherwise load `references/output-contract.md` and render manually

Then route optional references using:
- `references/method-router.md`
- optionally `scripts/suggest_modules.py` when plain paper text is available and scripts can run

Load `references/domain-profiles.md` only when a listed domain clearly applies.

Do not load every optional reference by default.

## Minimal workflow

### Phase A — scope, viability, and claims
1. Inventory what is actually available: main text, figures/tables, supplement/appendix, references, data/code links.
2. Decide topical scope: `in scope`, `partially in scope`, or `out of scope`.
3. Run `evidence-viability.md`: `auditable`, `partially auditable`, or `non-auditable`.
4. Record any controlled viability flags.
5. If auditable, extract 3–5 core claims. If partially auditable, extract only the 1–5 claims whose evidence chain can actually be reconstructed. If non-auditable, do not manufacture claims.
6. Put prerequisite claims before downstream mechanism/causality/generality claims.

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
Prefer the structured renderer when available:
1. fill the audit ledger defined in `audit-ledger-format.md`
2. run `scripts/render_audit.py`
3. run `scripts/validate_audit.py` on the rendered Markdown

If scripts cannot run, use `output-contract.md` exactly.

For out-of-scope or non-auditable material, keep the seven-section skeleton and use `not applicable` for sections 2 and 3 where appropriate.

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

## Flash path

Flash path is a staged-loading strategy for keeping context focused. It does not lower the audit standard.

In Flash path:
1. keep only `core-contract.md`, `evidence-viability.md`, `evidence-types.md`, and the active output interface (`audit-ledger-format.md` with renderer, otherwise `output-contract.md`) loaded initially
2. run the viability gate before claim extraction; do not force the full claim count for partially or non-auditable material
3. run or consult the router
4. load every optional module that a decision-critical claim actually requires
5. audit one claim at a time
6. re-route if a later claim exposes a new methodological cue
7. render the complete audit with `scripts/render_audit.py` when available
8. run `scripts/validate_audit.py` on the finished audit when a Python runtime is available

Flash path must not:
- reduce the required claim count for material classified `auditable`
- omit required output fields
- skip a routed module because it is inconvenient
- lower the evidence/support standard
- skip false-positive guards after a trap module is triggered
- stop after abstract-only reading when a decision-critical result/method section is available

Automatically switch to Full path when any of these occurs:
- three or more primary methodological modules are needed
- a core claim depends structurally on an external cited work
- direct results conflict materially across abstract/results/figures/tables/conclusion
- multiple studies, cohorts, datasets, sites, or experiments require a non-trivial dependence map
- a decision-critical claim remains `unclear` after its targeted module check
- the user asks for a comprehensive/deep audit

If the paper is long, prioritize:
- abstract/conclusion for claim extraction
- results + decision-critical figures/tables for evidence
- methods needed to interpret those claims
- cited work only when structurally necessary

Flash means less irrelevant context, not less work.

## Full path

Full path keeps the same output contract but allows broader simultaneous module loading, second-pass cross-claim checks, and deeper external-dependency inspection. Use it whenever Flash escalation criteria are met.

## Optional deep references

Use these only when the compact contract is not enough:
- `references/claim-evidence-links.md`
- `references/claim-dependencies.md`
- `references/evidence-dependence.md`
- `references/evidence-topology.md`
- `references/follow-up-boundaries.md`
- `references/pollution-patterns.md`

## Validation

The renderer and validator own the mechanical output contract:
`python scripts/render_audit.py audit.json -o audit.md`
`python scripts/validate_audit.py audit.md`

It verifies fields, controlled values, claim numbering, evidence-node syntax, convergence-node count, provenance/dependency rules, and conservative uncertainty propagation.

The validator cannot decide whether a scientific interpretation is true. Semantic judgment remains the model's job.
