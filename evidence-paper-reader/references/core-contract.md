# Core audit contract

This is the compact semantic contract that should be loaded for every paper-side audit.

The goal is to keep different model configurations aligned on the same evidence graph without requiring every methodological reference to stay in context.

## 0. Audit target: claim → evidence → reasoning

This contract audits logical reach, not scientific authority.

For each important claim, ask what the source actually says, what evidence is available, what that evidence directly supports, and which additional inferential steps are needed to reach the stated conclusion.

Do not turn the audit into:
- a verdict on ultimate scientific truth
- a fraud, fabrication, falsification, or misconduct investigation
- an inference about author honesty, intent, or competence
- a venue/prestige-based quality score
- a simulated editorial or peer-review recommendation

Documented corrections, retractions, provenance failures, or external disputes may be used only as evidence about whether a claim-evidence chain remains inspectable or usable. Record the documented fact and its consequence for the chain; do not infer blame.

## 1. Scope first

Use exactly one scope status:
- `in scope`
- `partially in scope`
- `out of scope`

An in-scope paper has a traceable evidence chain that can be inspected from the available paper material.

Do not force claims for an out-of-scope paper. Preserve the seven-section output skeleton and use `not applicable` where needed.

## 2. Evidence viability before claims

After topical scope, assign one evidence-viability label using `evidence-viability.md`:

- `auditable`
- `partially auditable`
- `non-auditable`

Also record controlled viability flags.

Viability asks whether the evidence chain is exposed enough to audit. It is not a venue, prestige, novelty, or excitement judgment.

- `auditable`: extract 3–5 core claims.
- `partially auditable`: extract only 1–5 claims whose chain can actually be reconstructed.
- `non-auditable`: do not manufacture claims; sections 2 and 3 may be not applicable.

## 3. Claims

For auditable or partially auditable material, extract claims before judging them.

Allowed claim types:
- `observational`
- `methodological`
- `mechanistic`
- `performance`
- `generality`
- `intervention`

Conclusion strength describes the reach of the claim:
- `weak`: local/descriptive
- `medium`: comparative, explanatory, or bounded generalization
- `strong`: broad causal, mechanistic, or generality reach

Do not silently narrow a claim before judging support.

Core claims must be source-facing: propositions the paper itself reports, argues, interprets, or concludes. Do not use auditor diagnostics, design criticisms, or evidence-quality descriptions merely to fill the claim count. Statements such as "the validation is not independent" or "the evidence is cross-sectional" belong in support reasoning/downweighting unless the paper itself makes that proposition a central claim. A methodological claim may be selected when the paper itself claims a method, design property, or validation result.

## 4. Evidence nodes

Assign stable local IDs:
- `E1`
- `E2`
- `E3`

Use the same ID whenever the same result, experiment, analysis, or imported evidence item is reused across claims.

Do not create a new ID merely because the same result appears in another figure, section, or claim.

Evidence-node count is not evidence independence.

For long or structurally complex papers, E nodes may be built through the optional `evidence-inventory-format.md` R/G/U intermediate layer. That layer is internal bookkeeping; the final audit still uses E nodes.

## 5. Claim dependencies

Claims are ordered topologically.

Each support block uses:
- `upstream claims: none`
- or earlier claims such as `C1` or `C1 + C2`

A claim may not depend on itself or on a later claim.

Uncertainty does not reset downstream. If a downstream claim adds no new evidence nodes beyond required upstream claims, it cannot become `sufficient` when a required upstream claim is not sufficient.

### Claim-local evidence relations

Ledger schema v3 requires every declared evidence node to have exactly one claim-local relation from `evidence-relations.md`:

- `supports`
- `undermines`
- `mixed`
- `contextual`

The relation is not a global property of the E-node. The same result may support one claim, undermine a stronger claim, and merely contextualize another.

Do not infer the final support level mechanically from these labels. Evidence relation and reasoning status are separate dimensions.

## 6. Reasoning edges

Ledger schema v2 makes the logical bridge from evidence/upstream claims to each target claim explicit.

Every auditable claim must be reached by one or more `R` edges. Together those edges must account for exactly the evidence nodes and upstream claims declared in the claim's support block.

Use `reasoning-graph.md` for the controlled inference types and edge statuses.

The graph is a compact auditable artifact, not private chain-of-thought. Record only the premises, inference type, added reach, material assumptions, and whether that bridge is direct, supported, qualified, unsupported, or unclear.

A support judgment and its reasoning edges must agree: `sufficient` cannot hide a qualified or unsupported bridge; `insufficient` must expose where the stated reach is unsupported.

## 7. Evidence provenance

Use exactly one:
- `paper-local`
- `external citation`
- `mixed`

A citation is not paper-local evidence.

Do not claim knowledge of a cited work unless it was inspected.
Do not guess DOIs from memory.

## 8. Evidence dependence

Use exactly one:
- `single-source`
- `shared-source convergence`
- `partially independent convergence`
- `independent convergence`
- `unclear`

Any convergence label requires at least two evidence nodes.

Technical repeats, multiple outcomes from the same participants, multiple models on the same dataset, repeated random seeds, or several figures from one experiment do not automatically create independent replication.

## 9. Support level

Use exactly one:
- `sufficient`
- `partial`
- `insufficient`
- `unclear`

Interpretation:
- `sufficient`: shown evidence supports the claim at approximately the stated scope
- `partial`: a narrower or qualified version is supported
- `insufficient`: available evidence does not establish the stated claim
- `unclear`: available material is too incomplete or ambiguous to judge

Do not treat publication status, author confidence, figure complexity, or citation count as support strength.

## 10. Direct evidence wins over narrative summary

Compare abstract, results, figures/tables, discussion, and conclusion.

When they conflict:
- preserve the conflict
- prefer the most direct and precisely located paper-local result for the bounded claim
- do not let summary prose overwrite measured values, tables, figures, or documented procedures

## 11. Reuse and inference reach

Evidence reuse is allowed.

The same E node can support:
- a narrow result directly
- a mechanism only partially
- a generality claim weakly or not at all

Do not clone evidentiary weight across claims.

Ask:
- What does this evidence directly establish?
- What extra reach is added by the claim?
- Is there new direct evidence for that extra reach?

## 12. Uncertainty and null results

Do not translate `not statistically significant` into:
- no effect
- equivalence
- safety
- clinical irrelevance

Inspect effect size, uncertainty interval, and any equivalence/non-inferiority margin.

If material needed for judgment is missing, say `unclear` rather than filling the gap.

## 13. Methodological risk is not a verdict

A risk cue starts a check.

Before downweighting:
1. identify the exact failure mode
2. verify that the paper actually uses the vulnerable inference
3. check whether the paper directly mitigates the risk
4. credit effective mitigation
5. report only residual risk

If a potential issue is adequately handled and leaves no decision-relevant residual concern, it does not need to appear in the final downweight section.

## 14. Domain knowledge boundary

Use bundled methodological knowledge to interpret evidence.

Do not inject expected domain values, normal ranges, treatment effects, material properties, market behavior, or field consensus as substitutes for inspected evidence.

If external scientific context is needed, treat that as a separate literature-search task.

## 15. Medical boundary

A clinical paper may be audited for design, outcomes, uncertainty, and causal reach.

Do not turn a paper audit into patient-specific advice or an independent standard-of-care recommendation.
