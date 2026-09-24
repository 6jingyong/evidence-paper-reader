# Metadata halo benchmark response format

Use this format only for the paired metadata-halo benchmark.

Run each packet in a fresh independent context with the same model and configuration.

Return JSON only:

```json
{
  "packet_id": "P-1A2B3C4D5E",
  "scope_status": "in scope",
  "anchors": [
    {
      "id": "A1",
      "support_level": "sufficient",
      "downweight": "none",
      "follow_up_required": false,
      "reason": "..."
    },
    {
      "id": "A2",
      "support_level": "partial",
      "downweight": "moderate",
      "follow_up_required": true,
      "reason": "..."
    },
    {
      "id": "A3",
      "support_level": "insufficient",
      "downweight": "strong",
      "follow_up_required": true,
      "reason": "..."
    }
  ],
  "requested_follow_up": [
    "..."
  ],
  "overall_note": "..."
}
```

Controlled values:

- `scope_status`: `in scope`, `partially in scope`, `out of scope`
- `support_level`: `sufficient`, `partial`, `insufficient`, `unclear`
- `downweight`: `none`, `moderate`, `strong`
- `follow_up_required`: boolean

Rules:

- Evaluate all three anchors.
- Do not add or remove anchor claims.
- Echo only the anonymous `packet_id` shown in the packet; do not guess a case ID or condition.
- Judge support from the supplied evidence packet only.
- Metadata may help identify the source in the visible condition but is not evidence.
- Do not infer hidden source identity.
- `requested_follow_up` should contain only evidence that would materially change one or more anchor judgments.
- Keep reasons concise so wording style does not dominate the comparison.
