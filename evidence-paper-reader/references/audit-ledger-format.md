# Audit ledger format

Use this structured JSON ledger when `scripts/render_audit.py` is available.

The ledger is an intermediate representation. It contains semantic judgments but no Markdown layout decisions.

## Core shape

```json
{
  "scope_status": "in scope",
  "evidence_viability": "auditable",
  "viability_flags": [],
  "paper_type": "randomized controlled trial",
  "reader_conclusion": "The paper directly supports ...",
  "claims": [
    {
      "content": "The intervention reduced the primary outcome.",
      "claim_type": "intervention",
      "conclusion_strength": "medium",
      "support": {
        "evidence_type": ["direct experiment", "statistical analysis"],
        "evidence_provenance": "paper-local",
        "evidence_nodes": ["E1", "E2"],
        "upstream_claims": [],
        "evidence_dependence": "shared-source convergence",
        "source_location": "Results; Table 2",
        "support_level": "sufficient",
        "reason": "Random assignment and the primary comparison directly support the bounded claim.",
        "external_dependency": "none"
      }
    }
  ],
  "usable": {
    "results": "The primary outcome estimate is usable.",
    "methods_or_design": "The randomized comparison is reusable as a design reference.",
    "materials_or_documentation": "The paper reports group sizes and confidence intervals."
  },
  "downweight": {
    "worth_noticing": "Secondary outcomes remain exploratory.",
    "cautious_or_ignore": "Do not generalize beyond the enrolled population without additional evidence."
  },
  "value_breakdown": {
    "result": "high",
    "method": "high",
    "theory_or_insight": "medium",
    "research_design": "high",
    "material_or_documentation": "high"
  },
  "uncertainty_and_follow_up": "Long-term outcomes remain uncertain."
}
```

`auditable` ledgers require 3–5 claims. `partially auditable` ledgers require 1–5 reconstructable claims. `non-auditable` ledgers use an empty claims list.

The renderer assigns claim numbers from list order. Do not put claim numbers in claim content.

## Structured fields

Use arrays for:
- `viability_flags`
- `evidence_type`
- `evidence_nodes`
- `upstream_claims`

Examples:
- `"evidence_nodes": ["E1", "E2"]`
- `"upstream_claims": [1, 2]`

The renderer converts these to:
- `E1 + E2`
- `C1 + C2`

This removes formatting bookkeeping from the model.

## Non-auditable or out-of-scope ledger

For `non-auditable` or `out of scope`:
- use an empty `claims` list
- provide `not_applicable_reason`
- for `non-auditable`, provide at least one controlled `viability_flags` value
- keep `usable`, `downweight`, `value_breakdown`, and `uncertainty_and_follow_up`
- use `unclear` value levels when a value category cannot be meaningfully judged

The renderer generates the required `not applicable` placeholders in sections 2 and 3.

## Renderer commands

Create a starter ledger:

```bash
python evidence-paper-reader/scripts/render_audit.py --template > audit.json
```

For a focused ledger check:

```bash
python evidence-paper-reader/scripts/render_audit.py audit.json --check
```

For normal completion, use the combined execution gate with the merged route and, when required, the evidence inventory:

```bash
python evidence-paper-reader/scripts/audit_gate.py audit.json \
  --route merged-route.json \
  --inventory inventory.json \
  -o audit.md
```

Omit `--inventory` only when the merged route says `use_evidence_inventory: false`.

The combined gate also validates the canonical rendered Markdown. Direct renderer/validator calls remain useful for debugging individual stages.

## Responsibility boundary

The renderer handles:
- section order
- headings
- claim numbering
- field order
- evidence-node formatting
- upstream-claim formatting
- out-of-scope/non-auditable placeholders
- evidence-viability and viability-flag formatting
- value-breakdown ordering

The model still handles:
- what the claims are
- what evidence supports them
- evidence-node identity
- evidence dependence
- upstream logical dependence
- support level
- reasons and uncertainty

Rendering is mechanical. Scientific judgment is not.

Cross-stage consistency is also mechanical where possible. `audit_gate.py` therefore rejects:
- a claim audit with no merged route
- a route-required inventory that was skipped
- an inventory supplied against a route that says not to use one
- claim text/order drifting between an inventory and the final ledger
- evidence nodes or independence claims that conflict with the inventory
- malformed route guard/path bookkeeping
- controlled evidence labels that fail the final Markdown contract

When one of these fails, repair or rerun the relevant stage instead of bypassing the gate.
