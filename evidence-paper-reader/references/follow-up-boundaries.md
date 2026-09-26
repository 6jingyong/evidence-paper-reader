# Follow-up boundaries

## Reproducibility boundary
This skill does not decide whether a result will replicate or reproduce successfully.
It may judge only whether reproducibility-relevant information appears adequately reported for a reader to assess or attempt follow-up work.

Use formulations such as:
- "reproducibility-relevant detail appears limited because ..."
- "the paper reports enough procedural detail to inspect the setup, but not enough to infer likely reproduction success"
- "the paper's support may still depend on unavailable implementation, appendix, data, or preprocessing detail"

Avoid formulations such as:
- "this result cannot be reproduced"
- "this paper is reproducible"
- "the experiments will fail on replication"

## Evidence provenance boundary
Every core-claim support judgment should identify one provenance state:
- `paper-local`: the current paper directly reports or documents the supporting result/material
- `external citation`: the current paper delegates the relevant support to prior work
- `mixed`: the current paper contributes some direct support but a material part of the claim still depends on cited work

A bibliography entry, related-work summary, or author statement about prior literature does not become paper-local evidence merely because it appears in the current PDF.

If the current paper reports what another work found, you may accurately describe that attribution, but do not treat the cited finding as independently checked until the cited work itself is available.

## Citation dependency boundary
Sometimes a paper's mechanism, theory, baseline fact, measurement validity, or framing depends critically on one or more prior works.
When that dependency appears structurally important:
1. Name the cited work.
2. Provide the DOI if it is present in inspected material.
3. If the DOI is absent and authoritative metadata lookup is available, it may be looked up; identify it as a metadata lookup rather than as information extracted from the paper.
4. State briefly why the dependency matters for evaluating the current paper.
5. Invite the user to read or upload that work next.

Do not guess a DOI from memory.
Do not pretend to know the cited paper's contents unless they are actually available.
Do not flood section 7 with every citation; surface only dependencies that can materially change a core support judgment.

## Uncertainty boundary
When judgment is blocked, say what blocks it. Common blockers:
- appendix not provided
- missing figure, table, or supplement
- domain-specific theory not available in the prompt or document
- unclear sample construction
- unreported preprocessing or parameter settings
- cited mechanism delegated to prior work
- source location cannot be recovered from the available representation
