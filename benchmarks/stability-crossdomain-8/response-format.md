# Cross-domain stability benchmark response

Return JSON only.

Use this schema:

```json
{
  "case_id": "<packet case id>",
  "evidence_viability": "<controlled value>",
  "selected_claim_ids": ["<candidate id>", "..."],
  "modules": ["<module filename>", "..."],
  "use_evidence_inventory": false,
  "support": [
    {"claim_id": "<selected candidate id>", "support_level": "<controlled value>"}
  ],
  "note": "<optional concise note>"
}
```

Rules:

- Use the Evidence Paper Reader skill.
- `case_id` must match the packet.
- `evidence_viability` must be one of: `auditable`, `partially auditable`, `non-auditable`.
- For `auditable`, select 3–5 candidate claims; for `partially auditable`, select 1–5; for `non-auditable`, select none.
- Select claims that should enter the audit; do not silently narrow strong source claims into safer replacements.
- List only modules materially required after lexical + semantic routing.
- Use evidence inventory only when retrieval/deduplication materially benefits from it.
- Give exactly one support entry for every selected claim and no unselected claim.
- Controlled support: `sufficient`, `partial`, `insufficient`, `unclear`.
- Keep `note` concise.
- Do not use or infer private answer keys, reference blocks, or scorer output.
