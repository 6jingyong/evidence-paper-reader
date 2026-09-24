# Semantic router card

Use this compact routing pass after core claims are extracted and after the lexical router has run.

Its job is only to decide which deeper references a decision-critical claim needs. It does not diagnose a flaw and it does not judge support.

Do not route from keywords alone. Ask whether the claim's evidence or inference materially depends on the issue.

## For each core claim

Return one decision for every route:

- `required` — this module is materially needed to judge the claim
- `not_required` — the cue is incidental or the claim does not materially depend on it
- `unclear` — available text is insufficient; preserve any lexical suggestion until checked

### figure-and-table-traps.md

Required when the claim materially depends on visual/tabular encoding, scale, normalization, aggregation, uncertainty bars, selected images, or values that must be reconstructed from a display.

Do not require it merely because the paper contains figures or tables.

### statistical-traps.md

Required when the claim materially depends on uncertainty, model estimates, multiplicity, selected findings, subgroup comparison, missing-data inference, repeated looks, or related statistical reasoning.

Do not require it merely because a statistical term appears in background text.

### measurement-traps.md

Required when validity of the measured quantity depends on an instrument, assay, threshold, scoring rule, preprocessing, segmentation, calibration, proxy, surrogate, coding scheme, or measurement context.

Do not require it merely because a standard instrument is named if no decision-critical measurement issue is present.

### study-design-traps.md

Required when the claim's causal/comparative/generalization reach depends on assignment, sampling, counterfactual choice, timing, attrition, clustering, repeated measures, intervention structure, or train/validation/test separation.

Do not require it for incidental uses of words such as cluster, test, control, or validation.

### evidence-topology.md

Required when support depends on selection/filtering, proxy-to-construct transfer, target reuse, mechanical predictor/outcome coupling, scale/domain transfer, or conflict between summary and direct evidence.

### evidence-dependence.md

Required when a claim combines multiple results and their independence/shared source matters.

### claim-evidence-links.md

Required when the same result is reused across multiple claims or when direct-support boundaries between one result and several stronger claims need to be exposed.

### claim-dependencies.md

Required when one claim is a premise for another and uncertainty can propagate downstream.

### follow-up-boundaries.md

Required when a decision-critical premise depends on an uninspected citation, missing supplement/appendix/data/code, proprietary source, or other unavailable external material.

### evidence inventory

Use the inventory path when retrieval/deduplication itself is a material burden: repeated presentations of the same result, multiple partially shared source units, evidence split across materials, or long text that would crowd out reasoning.

Do not use inventory merely because the paper is long.

## Output

Return JSON:

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
        "evidence-dependence.md": "unclear",
        "claim-evidence-links.md": "not_required",
        "claim-dependencies.md": "not_required",
        "follow-up-boundaries.md": "not_required"
      },
      "inventory": "not_required",
      "reason": "The claim is a comparative intervention estimate whose interpretation depends on assignment and uncertainty."
    }
  ]
}
```

Keep the reason concise.

## Merge rule

The merge script combines semantic decisions with lexical suggestions:

- semantic `required` adds a module
- semantic `not_required` removes an incidental lexical hit
- semantic `unclear` preserves a lexical hit if one exists
- if any trap module remains, `false-positive-guards.md` is added
- inventory uses the same rule: `required` on, `not_required` off, `unclear` preserves lexical recommendation

A semantic route changes context loading, not the support judgment.
