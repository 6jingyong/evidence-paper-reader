---
name: evidence-paper-reader
description: read evidence-driven research papers using a reader-side framework that separates claims, evidence, support strength, usable value, and overreach. use when a user wants to know what in a paper is actually trustworthy, what is only partially supported, what is methodologically reusable, or what should be downweighted. supports experimental science, benchmark-heavy methods, quantitative social science, finance/econometrics, clinical and biomedical empirical papers, empirical aesthetics, and other papers with traceable evidence chains. not for pure mathematics, patient-specific clinical decision making, or primarily normative/interpretive theory without a traceable evidence chain.
license: MIT
---

# Evidence Paper Reader

## Goal

Treat the paper as one evidence-bearing source for a general claim–evidence–reasoning audit.

Identify what it claims, what the disclosed evidence supports, where reasoning adds extra reach, and what remains usable or uncertain.

Do not adjudicate ultimate scientific truth, investigate misconduct, infer author intent, score the paper, or simulate peer review.
Do not use publication status as evidence strength. Default output language follows the user.

## Load order

Always load:
1. `references/core-contract.md`
2. `references/evidence-viability.md`
3. `references/evidence-types.md` + `references/evidence-relations.md`
4. `references/reasoning-graph.md`
For output:
- when Python can run, load `references/audit-ledger-format.md` and complete through `scripts/audit_gate.py`
- use `scripts/render_audit.py` and `scripts/validate_audit.py` only as focused debugging tools
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

### Phase B — route and decide evidence handling
Use `suggest_modules.py` for lexical candidates, confirm each core claim with `semantic-router-card.md`, then merge with `merge_route.py`.

When Python can run, do not rely on memory to open routed references one by one. Build the active methodological context deterministically:

`python scripts/build_context.py --semantic-route semantic-route.json [--router-text paper.txt] [--lexical-route lexical-route.json] -o audit-context.md --manifest context-manifest.json --checks-template module-checks.json`

When lexical fallback matters, `paper.txt` is the plain source text used for lexical routing. A lexical-route JSON is only a cache and is accepted only when it matches deterministic recomputation from that text. Complete every generated module check with a status, at least one precise paper source location/material gap, and a reason; trap checks set `mitigation_checked=true` only after the false-positive guard pass, and an `unclear` routed check cannot coexist with `sufficient` support. Use the generated bundle for support judgment. If a claim changes or a new cue appears, rerun routing and rebuild the bundle.
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

### Phase C — evidence inventory and ledger
Follow the recomputed route's evidence-inventory decision. If inventory is not required, assign E-nodes directly. If it is required, load `evidence-inventory-format.md` and use `scripts/evidence_inventory.py` before support judgment.
Inventory path: locate R records → deduplicate repeated presentations with G keys → group shared evidence-generating bases with U keys → promote decision-critical results to E-nodes.
For each final E-node, record evidence type, provenance, upstream claims, evidence dependence, and the most precise source location available.
Use the same E-node whenever the same underlying result is reused; record ledger-v3 claim-local evidence relations, then build reasoning edges that explicitly connect E-nodes/upstream claims to each target claim.

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

### Phase E — validate and render
Prefer the fail-closed execution gate when scripts are available:
1. fill the audit ledger defined in `audit-ledger-format.md`
2. preserve the raw semantic-route JSON, generated `audit-context.md`, completed `module-checks.json`, and any router text needed for lexical fallback; lexical/merged route JSON may be kept only as verified caches
3. if the merged route requires evidence inventory, complete and validate the inventory
4. run `scripts/audit_gate.py audit.json --semantic-route semantic-route.json --context-bundle audit-context.md --module-checks module-checks.json [--router-text paper.txt] [--lexical-route lexical-route.json] [--route merged-route.json] [--inventory inventory.json] -o audit.md`

The gate recomputes routing, regenerates the expected context bundle byte-for-byte, requires exact per-claim routed-module execution records, rejects stale/tampered caches, then validates the ledger, inventory requirement, inventory↔ledger claim identity, evidence-node/dependence alignment, controlled evidence labels, and final rendered Markdown.

Do not bypass a failed gate by calling the renderer directly. Fix the failing stage or rerun routing when the workflow changed.

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
1. keep only `core-contract.md`, `evidence-viability.md`, `evidence-types.md`, and the active output interface (`audit-ledger-format.md` with the execution gate, otherwise `output-contract.md`) loaded initially
2. run the viability gate before claim extraction; do not force the full claim count for partially or non-auditable material
3. run lexical routing and semantic confirmation
4. generate the active context and module-check template with `scripts/build_context.py`; it recomputes the merge and includes every required base/routed reference
5. if the recomputed route requires inventory, build it now; then audit one claim at a time from the generated context and complete every routed module check
6. re-route if a later claim exposes a new methodological cue
7. preserve the semantic route, generated context bundle, completed module checks, any router text needed for lexical fallback, optional verified route caches, and any required evidence inventory
8. run `scripts/audit_gate.py` on those artifacts; only render after the gate passes

Flash path must not:
- reduce the required claim count for material classified `auditable`
- omit required output fields
- skip a routed module because it is inconvenient, including by bypassing the generated context bundle or substituting an unrouted methodology module
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
- `references/evidence-inventory-format.md`, `claim-evidence-links.md`, `claim-dependencies.md`, `reasoning-graph.md`
- `references/evidence-dependence.md`, `evidence-topology.md`, `follow-up-boundaries.md`, `pollution-patterns.md`

## Validation

When Python can run, `audit_gate.py` is the normal completion boundary:

`python scripts/audit_gate.py audit.json --semantic-route semantic-route.json --context-bundle audit-context.md --module-checks module-checks.json [--router-text paper.txt] [--lexical-route lexical-route.json] [--route merged-route.json] [--inventory inventory.json] -o audit.md`

Use `scripts/render_audit.py --check`, `scripts/evidence_inventory.py --check`, and `scripts/validate_audit.py` as focused debugging tools, not as substitutes for the combined gate.

The gate fails closed on mechanical cross-stage inconsistencies. It cannot decide whether a claim is ultimately true or whether misconduct occurred. Claim–evidence–reasoning judgment remains the model's job.
