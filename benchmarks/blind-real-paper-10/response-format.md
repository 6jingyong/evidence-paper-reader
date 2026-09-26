Return exactly one JSON object with these fields:

```json
{
  "case_id": "case id from the packet",
  "evidence_viability": "auditable | partially auditable | non-auditable",
  "viability_flags": ["controlled viability flags, or empty"],
  "claims": [
    {
      "content": "source-facing claim in your own wording",
      "claim_type": "observational | methodological | mechanistic | performance | generality | intervention",
      "conclusion_strength": "weak | medium | strong",
      "support_level": "sufficient | partial | insufficient | unclear",
      "source_location": "precise source location",
      "reason": "why the disclosed evidence reaches this support level"
    }
  ],
  "modules": ["routed reference module filenames"],
  "use_evidence_inventory": false,
  "reader_conclusion": "brief overall evidence judgment"
}
```

Rules:

- If `evidence_viability` is `auditable`, return 3–5 claims.
- If it is `partially auditable`, return 1–5 reconstructable claims.
- If it is `non-auditable`, return an empty `claims` list.
- Do not invent stored claim IDs.
- Do not use repository answer keys, prior audit ledgers, scorer files, or regression contracts.
- Judge the public source material itself.
