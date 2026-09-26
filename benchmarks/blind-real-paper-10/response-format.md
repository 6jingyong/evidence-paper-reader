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
      "evidence_nodes": ["E1"],
      "evidence_relations": [
        {
          "evidence_node": "E1",
          "relation": "supports | undermines | mixed | contextual",
          "reason": "how this evidence bears on this claim"
        }
      ],
      "upstream_claims": [],
      "support_level": "sufficient | partial | insufficient | unclear",
      "source_location": "precise source location",
      "reason": "why the disclosed evidence reaches this support level"
    }
  ],
  "reasoning_edges": [
    {
      "edge_id": "R1",
      "target_claim": 1,
      "evidence_nodes": ["E1"],
      "upstream_claims": [],
      "inference_type": "direct-result | comparison | statistical-inference | causal | mechanistic | generalization | proxy-to-construct | aggregation | external-import",
      "reasoning_status": "direct | supported | qualified | unsupported | unclear",
      "added_reach": "none or the extra logical reach beyond the direct inputs",
      "assumptions": ["material assumptions, or empty"]
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
- If it is `non-auditable`, return an empty `claims` list and an empty `reasoning_edges` list.
- Number claims by list order only; do not put stored or guessed claim IDs in the claim text.
- Evidence nodes use `E1`, `E2`, ... and upstream claims use earlier 1-based claim numbers.
- Every claim must assign each declared E-node exactly one claim-local evidence relation: `supports`, `undermines`, `mixed`, or `contextual`. Do not infer final support mechanically from the relation label.
- Every auditable claim must be reached by at least one reasoning edge.
- For each claim, the union of its reasoning-edge evidence/upstream inputs must exactly match the claim's declared `evidence_nodes` and `upstream_claims`.
- `sufficient` may use only `direct`/`supported` edges; `partial` must expose a qualified/unsupported/unclear bridge; `insufficient` must expose an unsupported bridge; `unclear` must expose an unclear bridge.
- `direct` edges must use `added_reach: "none"`.
- This is a compact audit graph, not private chain-of-thought. Record inspectable premises, logical bridge, added reach, and material assumptions only.
- Do not use repository answer keys, prior audit ledgers, scorer files, or regression contracts.
- Judge the public source material itself.
