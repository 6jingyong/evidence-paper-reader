# Claim-evidence links and evidence reuse

Use this reference after claims, evidence types, topology, and dependence have been identified.

The purpose is to make the claim-evidence graph visible without turning the output into a formal graph language.

## Evidence nodes

Assign local evidence-node IDs inside each paper audit:

- `E1`
- `E2`
- `E3`
- and so on

An evidence node is a specific paper-local result, analysis, experiment, documented material, or imported evidence item that can be pointed to in the paper.

Examples:
- a matched benchmark comparison in Figure 4
- one randomized primary-outcome comparison
- one receptor-blocking experiment
- one independent replication-cohort result
- one regression table over a defined dataset
- one cited external mechanism paper when that citation is part of the claim support

Evidence nodes are not assumed to be independent. Independence is handled separately by `evidence dependence`.

## Evidence inventory bridge

For long or structurally complex papers, use `evidence-inventory-format.md` before assigning final E nodes.

The identities are intentionally different:

- R = a locatable source record
- G = same underlying result across repeated presentations
- U = shared evidence-generating unit
- E = deduplicated audit evidence node

A result repeated in abstract, prose, figure, and table may create several R records but should keep one G key and normally promote to one E node.

Distinct results from the same participants/dataset/specimens should use different G keys but the same U key. They may become different E nodes while remaining shared-source evidence.

Independent replication should use a different U key only when the source-generating basis is materially independent.

The inventory script can catch duplicate promotion and some false-independence claims, but it cannot decide semantic identity by itself.

## Stable identity rule

Use the same evidence-node ID whenever the same underlying result is reused across claims.

Do not create E1, E7, and E12 for the same Figure 4 merely because it appears under three different claims. Renaming the same evidence does not create new support.

If two results come from the same source but are genuinely distinct readouts or analyses, they may receive different node IDs while still being classified as `shared-source convergence`.

## Claim-evidence graph

Think of:
- claim nodes: C1, C2, C3...
- evidence nodes: E1, E2, E3...
- links: which evidence nodes are used to support which claims

The output does not need to print C labels separately because claim numbers already provide them. It does need to list `evidence nodes` in every support block.

## Evidence reuse

Reusing evidence is often legitimate.

One result can simultaneously support:
- a narrow observational claim directly
- a methodological claim partially
- a mechanistic claim indirectly
- a generality claim weakly or not at all

The error is not reuse itself. The error is cloning the evidentiary weight of one result across progressively stronger claims.

## Direct-support boundary

For every reused evidence node, ask:

1. What is the narrowest claim this result directly establishes?
2. Which additional claims require interpretation, mechanism, transfer, or extrapolation?
3. Does a stronger claim have any additional direct evidence node?
4. If the dominant node were removed, how many claims would collapse?

A performance result does not automatically establish mechanism.
A mechanism result in one system does not automatically establish generality.
A correlation does not become causal because the same table is discussed in several sections.

## Claim stacking

A common structure is:

- E1 directly supports C1
- E1 is reused to support C2
- E1 is reused again to support C3
- C2 and C3 are broader than C1 but no new direct evidence appears

This is **claim stacking** or **evidence double-spending**.

When this occurs:
- keep E1's identity stable across claims
- do not count E1 again as new corroboration
- judge each claim at its own strength
- lower support for claims whose added reach is not backed by additional direct evidence

## Multi-node claims

A claim may use more than one evidence node:

`E1 + E2 + E3`

This can represent:
- triangulation
- replication
- a mechanism chain
- a result plus an external citation
- a robustness analysis

Do not infer stronger support from node count alone. Use `evidence dependence` to determine whether the nodes are shared-source, partially independent, independently convergent, or unclear.

## External evidence nodes

A cited work may be represented as an evidence node only when it actually contributes to the current claim's support.

Its provenance remains `external citation` or `mixed`.
The node ID does not make it paper-local.
If the cited work has not been inspected, do not infer its internal evidence quality or independence from other cited works.

## Contradictory nodes

If one evidence node conflicts with another or with the paper's summary claim, keep both visible rather than selecting the favorable one.

The support reason should explain the conflict and the support level should reflect it.

## Validator-oriented syntax

Use this field in every in-scope support block:

`- evidence nodes: E1`

or:

`- evidence nodes: E1 + E2`

Use uppercase E followed by a positive integer.
Reuse the same ID across claims when the same evidence is being reused.

## Usage rule

Evidence-node IDs are local bookkeeping, not scores. Their value is that they expose evidence reuse, make claim stacking auditable, and prevent one result from silently becoming several independent confirmations.
