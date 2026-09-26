# Evidence inventory format

Use this intermediate representation when the paper is long, evidence is repeated across sections, or several claims depend on overlapping experiments/datasets.

It is internal working state. Do not print the inventory in the normal seven-section audit unless the user asks for it.

## Why R, G, U, and E are different

Use four identities:

- `R1, R2...` — **source records**: concrete appearances or evidence-bearing statements located in the available material
- `G1, G2...` — **result identity**: records that describe the same underlying result share one G key
- `U1, U2...` — **evidence-generating unit**: results generated from the same participants, specimens, dataset, experiment, cohort, site, archive, or other materially shared source share one U key
- `E1, E2...` — **audit evidence nodes**: deduplicated results promoted into the final claim-evidence graph

These identities solve different problems.

Example:

- abstract sentence reporting the primary RCT outcome → R1 / G1 / U1
- Table 2 reporting the same primary outcome → R2 / G1 / U1
- secondary outcome from the same participants → R3 / G2 / U1
- independent replication cohort → R4 / G3 / U2

Promotion should then be:

- E1 ← R1 + R2
- E2 ← R3
- E3 ← R4

E1 and E2 are distinct results but remain shared-source because both depend on U1.
E3 can contribute materially independent evidence because it comes from U2.

## Core JSON shape

```json
{
  "evidence_viability": "auditable",
  "claims": [
    {"claim_id": "C1", "content": "The intervention reduced the primary outcome."},
    {"claim_id": "C2", "content": "The effect generalizes beyond the enrolled population."}
  ],
  "materials": [
    {
      "material_id": "M1",
      "kind": "main text",
      "availability": "available",
      "location": "full article",
      "notes": "Results and Methods available."
    },
    {
      "material_id": "M2",
      "kind": "supplement",
      "availability": "missing",
      "location": "supplement link",
      "notes": "Not provided in the current context."
    }
  ],
  "records": [
    {
      "record_id": "R1",
      "claim_refs": ["C1"],
      "material_id": "M1",
      "record_role": "direct result",
      "provenance": "paper-local",
      "location": "Results; Table 2",
      "summary": "Primary outcome was lower in the intervention group.",
      "sample_or_unit": "randomized participants in the primary analysis",
      "comparison_or_baseline": "intervention versus control",
      "result_detail": "effect estimate and uncertainty reported in Table 2",
      "result_key": "G1",
      "unit_key": "U1",
      "availability": "complete",
      "selection_or_filtering": "none reported for the primary analysis"
    }
  ],
  "promotions": [
    {
      "evidence_node": "E1",
      "record_ids": ["R1"],
      "reason": "Primary paper-local outcome result."
    }
  ],
  "unresolved_claims": [
    {
      "claim_id": "C2",
      "reason": "No paper-local or inspected external evidence directly tests transfer beyond the enrolled population."
    }
  ]
}
```

## Controlled values

### Material kind

Use one of:

- `main text`
- `figure`
- `table`
- `supplement`
- `appendix`
- `data or code`
- `external reference`
- `other`

### Material availability

Use one of:

- `available`
- `partial`
- `missing`

### Record role

Use one of:

- `direct result`
- `method detail`
- `derived result`
- `robustness result`
- `limitation`
- `author interpretation`
- `external evidence`

### Provenance

Use one of:

- `paper-local`
- `external citation`

### Record availability

Use one of:

- `complete`
- `partial`

## Source-record rule

A record is a locatable evidence-bearing object, not a paragraph summary of the whole paper.

Good records:

- one effect estimate in Table 2
- one benchmark comparison in Figure 4
- one perturbation result in a mechanism experiment
- one sample-selection rule that changes the effective population
- one external citation used as a decisive mechanistic premise

Bad records:

- "the paper has many experiments"
- "the authors discuss several mechanisms"
- an entire Results section collapsed into one R record

Keep records narrow enough that a reviewer can point back to the exact location.

## Result identity: G keys

Use the same G key when two records are merely different presentations of the same underlying result.

Common duplicate presentations:

- abstract statement + results prose + figure of the same endpoint
- a value stated in text and repeated in a table
- a figure panel and a supplementary table reporting the same fitted estimate
- conclusion restating the same measured comparison

Do not assign a new G key merely because the paper repeats a result.

Use different G keys for genuinely different results, even if they share the same source unit.

## Evidence-generating unit: U keys

U keys encode material dependence, not visual location.

Share one U key when records come from the same dominant data/source-generating basis, for example:

- same randomized participants
- same survey wave
- same specimens or biological preparation
- same benchmark dataset/split
- same market dataset/period
- same field site/deployment
- same archive or administrative records
- same simulation run family when no independent input basis exists

Use a different U key only when the source-generating basis is materially independent.

If independence cannot be established, use `unknown` rather than inventing a new U key.

Technical repeats do not create new U keys by themselves.

## Promotion: R to E

Promotion deduplicates source records into the evidence graph used by the final audit.

Rules:

1. Every promoted E node must reference at least one R record.
2. All R records grouped into one E node must share the same G key.
3. One R record cannot belong to two E nodes.
4. One G key cannot be promoted into multiple E nodes.
5. Records can remain unpromoted when they are background, redundant, or not decision-critical.
6. Different G keys should remain different E nodes even when they share a U key.
7. Reusing one E node across several claims happens later in the audit ledger; do not duplicate the E node here.

This makes duplication mechanically visible before support judgment.

## Claim coverage

Every decision-critical core claim must have at least one of:

- a promoted paper-local evidence node
- a promoted external evidence node
- an entry in `unresolved_claims` stating why no reconstructable evidence candidate was found

Do not create an E node merely to avoid an empty claim.

`unresolved_claims` is not a support judgment. It preserves a visible retrieval gap for the later audit, where the claim may receive `insufficient` or `unclear`.

## Missing materials

Inventory unavailable material explicitly.

Examples:

- supplement referenced but not available
- figure image missing from extracted text
- external paper cited but not inspected
- proprietary benchmark or dataset inaccessible
- appendix omitted from the supplied copy

Missing material is not evidence.

Its value is to explain why a claim may remain unclear or partially auditable.

## Long-paper workflow

For long or structurally complex papers:

1. make the material inventory
2. extract/confirm core claims
3. scan decision-critical sections and create R records
4. deduplicate repeated appearances with G keys
5. group shared source-generating bases with U keys
6. promote decision-critical G groups to E nodes
7. use the compact E-node map for support judgment

Do not keep the entire paper text in active context once the decision-critical records have been captured and their locations are preserved.

## Short-paper workflow

For a short paper with a few obvious, non-repeated results, direct E-node assignment remains acceptable.

Do not create inventory bureaucracy when it does not reduce ambiguity or context load.

## Responsibility boundary

The script can validate IDs, deduplication, references, and some dependence contradictions.

The model still decides:

- whether two appearances are truly the same result
- whether two results share an evidence-generating unit
- which records are decision-critical
- whether a missing material blocks a claim
- which promoted E nodes support each claim

The inventory is a memory aid and consistency layer, not an automatic scientific reader.
