# Claim dependencies and uncertainty propagation

Use this reference when one paper claim is used as a premise for another claim.

The purpose is to prevent a weak or uncertain upstream inference from becoming certain merely because it is restated later in the paper.

## Upstream-claim field

Every in-scope support block uses:

- `upstream claims: none`

or, when the claim logically depends on earlier claims:

- `upstream claims: C1`
- `upstream claims: C1 + C2`

Claims should be numbered in a topological order: an upstream reference may only point to an earlier claim number.

## Direct evidence versus derived inference

A downstream claim can have:
- reused evidence nodes from upstream claims
- new direct evidence nodes
- both

The key distinction is whether the added claim reach is independently tested.

Examples:
- C1: treatment changes biomarker
- C2: biomarker mediates clinical effect

If C2 only reuses C1's evidence, C2 inherits C1's uncertainty and also adds a new mechanistic inference. It cannot become better supported than C1 by repetition alone.

If C2 adds a separate mediation experiment or intervention that directly tests the mechanism, the new evidence can change the support judgment.

## Uncertainty propagation

Use these rules:

1. A downstream claim does not automatically inherit a support label; judge the claim itself.
2. However, an upstream uncertainty cannot disappear without new evidence.
3. If a downstream claim reuses only evidence nodes already attached to its upstream claims and at least one required upstream claim is not `sufficient`, the downstream claim cannot be `sufficient`.
4. If the downstream claim adds genuinely new direct evidence, reassess it on the combined evidence rather than mechanically inheriting the weaker label.
5. If an upstream claim is `insufficient` or `unclear` and the downstream inference requires that claim to be true, state the dependency explicitly.

## Inference-chain laundering

A common failure pattern is:

- C1 receives partial support
- C2 treats C1 as established and adds interpretation
- C3 treats C2 as established and generalizes further
- the conclusion states C3 without carrying forward the earlier uncertainty

This is **inference-chain laundering**.

Keep the upstream links visible so uncertainty is not reset at every paragraph or section.

## Branching and convergence

Several downstream claims may depend on one upstream result. This does not create independent support.

Likewise, a downstream claim may depend on two earlier claims. If those earlier claims share the same evidence nodes or source, the downstream claim should not be described as independent convergence merely because two claim labels are listed.

## Contradictory upstream claims

If an upstream claim is contradicted by another paper-local result, preserve the contradiction. Do not choose one branch silently and continue the inference chain.

## Validator-oriented syntax

Use exactly:
- `upstream claims: none`
- or `upstream claims: C1 + C2`

References must point only to earlier claim numbers and must not repeat the same claim.

## Usage rule

Claim dependencies are logical dependencies, not citation counts. Add an upstream claim only when the downstream claim actually requires that earlier claim as a premise.
