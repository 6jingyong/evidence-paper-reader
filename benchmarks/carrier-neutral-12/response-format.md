Return exactly one JSON object:

```json
{
  "case_id": "CN01",
  "evidence_viability": "auditable | partially auditable | non-auditable",
  "viability_flags": [],
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
          "reason": "how the evidence bears on this claim"
        }
      ],
      "upstream_claims": [],
      "support_level": "sufficient | partial | insufficient | unclear",
      "source_location": "location in the supplied source text",
      "reason": "why the disclosed chain reaches this support level"
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
      "added_reach": "none or the extra logical reach beyond direct inputs",
      "assumptions": []
    }
  ],
  "reader_conclusion": "brief overall claim–evidence–reasoning judgment"
}
```

Rules:

- Preserve the source-facing claims rather than replacing them with critique.
- If auditable, return the important explicit claims in source order. These synthetic cases normally contain three numbered claims.
- If non-auditable, return an empty `claims` list and empty `reasoning_edges`.
- Every declared E-node gets exactly one claim-local evidence relation.
- Every auditable claim has at least one reasoning edge.
- The union of reasoning-edge evidence/upstream inputs for a claim exactly matches that claim's declared inputs.
- `sufficient` may use only `direct` / `supported` edges.
- `partial` exposes at least one `qualified`, `unsupported`, or `unclear` bridge.
- `insufficient` exposes at least one `unsupported` bridge.
- `unclear` exposes at least one `unclear` bridge.
- `direct` uses `added_reach: "none"`.
- Do not infer author intent, culpability, scientific truth, or prestige-based quality.
- Return inspectable audit metadata, not private chain-of-thought.
