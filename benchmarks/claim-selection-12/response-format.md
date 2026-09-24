# Claim-selection benchmark response format

Use JSON only.

```json
{
  "case_id": "CS01",
  "evidence_viability": "auditable",
  "selected_claim_ids": ["K1", "K2", "K5"],
  "reason": "..."
}
```

Rules:

- Preserve the article's actual claim strength. Do not silently replace a strong causal/mechanistic/general claim with a safer association claim merely because the safer claim is better supported.
- The purpose of claim selection is to decide what should be audited, not what should ultimately be accepted.
- Do not select method-description details merely to fill the claim quota.
- Do not select a claim that the source packet does not actually make.
- `auditable`: choose 3–5 core claims when available.
- `partially auditable`: choose only 1–5 reconstructable or explicitly unresolved central claims.
- `non-auditable`: return an empty `selected_claim_ids` list.
