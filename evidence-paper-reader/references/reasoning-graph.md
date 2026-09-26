# Reasoning graph

The reasoning graph makes the **claim → evidence → reasoning** layer explicit in structured ledgers.

It is not a chain-of-thought transcript. It records only the inspectable logical bridge needed to audit whether the listed inputs can carry the target claim.

## Edge shape

Ledger schema v2 uses a top-level `reasoning_edges` list.

Each edge has:

- `edge_id`: sequential `R1`, `R2`, ...
- `target_claim`: the 1-based claim number the edge reaches
- `evidence_nodes`: E-nodes used by this edge
- `upstream_claims`: earlier claims used as premises
- `inference_type`: controlled logical bridge
- `reasoning_status`: how well the bridge reaches the target claim
- `added_reach`: what the inference adds beyond the direct inputs, or `none`
- `assumptions`: explicit assumptions needed for the bridge

At least one of `evidence_nodes` or `upstream_claims` must be non-empty.

## Controlled inference types

Use exactly one:

- `direct-result` — the claim is essentially a bounded restatement of an inspected result
- `comparison` — the claim depends on comparing groups, systems, conditions, baselines, or methods
- `statistical-inference` — the claim requires an inferential/statistical bridge beyond reporting the observed quantity
- `causal` — the claim attributes an effect to an intervention/exposure
- `mechanistic` — the claim identifies a mechanism or explanatory pathway
- `generalization` — the claim extends beyond directly tested populations, tasks, settings, times, or materials
- `proxy-to-construct` — the claim moves from an operational measure/proxy to a broader construct
- `aggregation` — the claim combines several local results into a higher-level conclusion
- `external-import` — the edge structurally depends on inspected external evidence

Choose the bridge that contributes the main extra inferential reach. A claim can have multiple edges when distinct bridges matter.

## Reasoning status

Use exactly one:

- `direct` — no material inferential reach is added; `added_reach` must be `none`
- `supported` — there is a real inferential bridge, and the disclosed evidence supports it at the claim's stated scope
- `qualified` — the bridge supports only a narrower or qualified version of the target claim
- `unsupported` — the disclosed inputs do not establish the stated bridge
- `unclear` — the available material is insufficient to decide whether the bridge holds

This status is about the edge, not the truth of the world.

## Closure rules

For ledger schema v2:

1. Every auditable/partially-auditable claim must have at least one reasoning edge.
2. Edge IDs are sequential from `R1`.
3. Every edge targets one existing claim.
4. Edge evidence inputs must come from that claim's declared `evidence_nodes`.
5. Edge upstream inputs must come from that claim's declared `upstream_claims` and refer only to earlier claims.
6. The union of all edges reaching one claim must cover **exactly** that claim's evidence nodes and upstream claims.
7. A `sufficient` claim may contain only `direct` or `supported` edges.
8. A `partial` claim must expose at least one `qualified`, `unsupported`, or `unclear` edge.
9. An `insufficient` claim must expose at least one `unsupported` edge.
10. An `unclear` claim must expose at least one `unclear` edge.

These rules prevent the reasoning graph from becoming a decorative summary disconnected from support judgment.

## Added reach

`added_reach` should name the actual logical move.

Good examples:

- `none`
- `Extends the measured WMT benchmark result to a broader cross-task generality claim.`
- `Moves from short-term PCR negativity to clinical treatment efficacy.`
- `Treats medial orbitofrontal BOLD activity as evidence for a broader abstract beauty construct.`
- `Extends the within-machine measurement comparison to literature-wide method comparability.`

Avoid generic filler such as:

- `the evidence supports the claim`
- `some inference is needed`
- `generalization may be limited`

## Assumptions

Record assumptions that are necessary for the edge but not directly established by its listed inputs.

Examples:

- the operational endpoint is a valid proxy for the broader construct
- treatment groups are exchangeable after the stated design/adjustment
- benchmark differences transfer to the deployment setting
- cited external evidence is applicable to the current population

Do not list universal background assumptions merely to fill the field. Use an empty list when no material additional assumption is needed.

## Boundary

This graph is a compact audit artifact, not hidden model reasoning.

It should be understandable and reviewable by a reader from the cited evidence and claim text. Do not store private chain-of-thought, speculative author motives, or uninspectable mental steps.
