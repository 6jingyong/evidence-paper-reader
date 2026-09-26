# Evidence relations

Ledger schema v3 makes the relation between each evidence node and each target claim explicit.

An evidence node is not globally "supporting" or "negative." The same E-node may support one claim, undermine a stronger claim, and be merely contextual for another. Relations therefore live inside each claim's support block.

## Relation shape

Each schema-v3 claim support block contains:

```json
"evidence_relations": [
  {
    "evidence_node": "E1",
    "relation": "supports",
    "reason": "The randomized primary-outcome contrast directly bears in the stated direction."
  },
  {
    "evidence_node": "E2",
    "relation": "undermines",
    "reason": "The same dataset shows a decision-critical adverse pattern that counts against the stronger benefit-only claim."
  }
]
```

Every evidence node declared in `evidence_nodes` must appear exactly once in `evidence_relations`, and no extra node may appear.

## Controlled relations

Use exactly one:

- `supports` — this evidence bears in favor of the claim or a necessary component of it
- `undermines` — this evidence bears against the claim or a necessary component/bridge
- `mixed` — the same evidence contains materially relevant features in both directions, or supports a narrower proposition while counting against the claim at its stated reach
- `contextual` — the evidence constrains interpretation, denominators, applicability, provenance, or scope without directly bearing for or against the target proposition

## Relation is not support level

Do not mechanically map relation labels to the final support judgment.

Examples:

- A claim can contain both `supports` and `undermines` evidence and still be sufficient if the total disclosed chain supports the claim at its stated scope.
- Evidence can `supports` a local observation while the reasoning edge that generalizes it is `unsupported`; the broader claim is still insufficient.
- A `contextual` attrition record may not dispute an analyzed-cohort percentage, but the same record may `undermines` a causal treatment-effect claim.
- A null-compatible estimate can be `mixed` for a strong efficacy claim: its point estimate may favor the intervention while its uncertainty does not establish the asserted effect.

The evidence relation answers **which way the evidence bears on this claim**. The reasoning graph answers **whether the logical bridge from the declared inputs reaches this claim**. The support level summarizes the whole audited chain.

## Claim-local identity

Relations are claim-local.

If E3 is an attrition record:
- C1: E3 may be `contextual` because it defines the analyzed denominator.
- C3: E3 may be `undermines` because selective attrition weakens the causal comparison.

Do not assign one global polarity to E3.

## Boundary

Evidence relations are compact, source-facing audit metadata. They do not encode author motive, scientific truth, or hidden chain-of-thought.

Use the most concrete source-facing reason possible. Avoid generic text such as "this is relevant evidence."
