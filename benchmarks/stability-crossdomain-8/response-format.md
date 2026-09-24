# Cross-domain stability benchmark response

Return JSON only.

```json
{
  "case_id": "ST01",
  "evidence_viability": "auditable",
  "selected_claim_ids": ["K1", "K2", "K5"],
  "modules": ["study-design-traps.md", "statistical-traps.md"],
  "use_evidence_inventory": false,
  "support": [
    {"claim_id": "K1", "support_level": "sufficient"},
    {"claim_id": "K2", "support_level": "sufficient"},
    {"claim_id": "K5", "support_level": "sufficient"}
  ],
  "note": "..."
}
```

Rules:

- Use the Evidence Paper Reader skill.
- Select the claims that should enter the audit; do not silently narrow strong source claims into safer replacements.
- List only modules that are materially required after lexical + semantic routing.
- Use evidence inventory only when retrieval/deduplication materially benefits from it.
- Give a support level for every selected claim and no unselected claim.
- Controlled support: `sufficient`, `partial`, `insufficient`, `unclear`.
- Keep `note` concise.
