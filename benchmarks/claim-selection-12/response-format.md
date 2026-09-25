# Claim-selection benchmark response format

Use JSON only.

```json
{
  "case_id": "<packet case id>",
  "evidence_viability": "<controlled value>",
  "selected_claim_ids": ["<candidate id>", "..."],
  "reason": "<concise selection rationale>"
}
```

Rules:

- Preserve the article's actual claim strength. Do not silently replace a strong causal/mechanistic/general claim with a safer association claim merely because the safer claim is better supported.
- The purpose of claim selection is to decide what should be audited, not what should ultimately be accepted.
- Select source-facing claims: propositions the source itself reports, argues, interprets, or concludes.
- Do not select auditor diagnostics, design criticisms, or method-description filler merely to fill the claim quota.
- Do not select a claim that the source packet does not actually make.
- `auditable`: choose 3–5 core claims when available.
- `partially auditable`: choose only 1–5 reconstructable or explicitly unresolved central claims.
- `non-auditable`: return an empty `selected_claim_ids` list.
- `evidence_viability` must be one of `auditable`, `partially auditable`, or `non-auditable`.
