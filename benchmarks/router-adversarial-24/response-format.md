# Router adversarial benchmark response

Use the compact semantic router card.

Return JSON only:

```json
{
  "claims": [
    {
      "claim_id": "C1",
      "routes": {
        "figure-and-table-traps.md": "not_required",
        "statistical-traps.md": "required",
        "measurement-traps.md": "not_required",
        "study-design-traps.md": "required",
        "evidence-topology.md": "not_required",
        "evidence-dependence.md": "not_required",
        "claim-evidence-links.md": "not_required",
        "claim-dependencies.md": "not_required",
        "follow-up-boundaries.md": "not_required"
      },
      "inventory": "not_required",
      "reason": "..."
    }
  ]
}
```

Evaluate only the supplied C1 claim and evidence text.

A module is `required` only when it materially helps judge that claim. Keyword presence alone is insufficient.
