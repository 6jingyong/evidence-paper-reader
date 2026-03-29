---
name: evidence-paper-reader
description: read evidence-driven research papers using a reader-side framework that separates claims, evidence types, support strength, usable value, and analysis pollution. use when a user wants to know what in a paper is actually trustworthy, what is only partially supported, what is methodologically reusable, or what should be downweighted. suitable for experimental natural science papers, benchmark or ablation-heavy method papers, simulation or computational papers, quantitative social science papers, and empirical social science papers with clear evidence chains such as surveys, interviews, archives, field notes, or content analysis. not for pure mathematics, highly clinical papers, or primarily normative or interpretive theory papers.
license: MIT
---

# Evidence Paper Reader

## Overview

Use this skill to read papers as a skeptical reader rather than as an editor or reviewer. The goal is to extract what can be relied on, identify what is only weakly supported, and prevent the author's narrative framing from being mistaken for evidence.

Default output language follows the user's input language. If the paper is in English, or uses field-specific terminology, do not force translation and do not add parenthetical translations unless the user explicitly asks.

## Workflow

1. Determine whether the paper is evidence-driven and within scope.
2. Identify the paper type and adjust attention accordingly.
3. Extract the core claims before judging them.
4. Assign an evidence type to each core claim.
5. Judge whether evidence strength matches conclusion strength.
6. Separate usable content from analysis that should be downweighted.
7. Produce the fixed reader-side output template.
8. If critical support comes from external cited work, surface the cited paper name and DOI when available so the user can follow up.

## Scope decision

Treat the paper as in scope only if it is primarily evidence-driven and has a traceable evidence chain.

Default in-scope categories:
- experimental natural science papers
- benchmark or ablation-heavy method papers
- simulation or computational papers
- quantitative social science papers
- empirical social science papers with clear evidence chains, including surveys, interviews, archives, field notes, and content analysis

Default out-of-scope categories:
- pure mathematics
- highly clinical papers
- papers centered on normative argument, pure theory exposition, or heavily interpretive analysis without a clear evidence chain

If the paper is partially in scope, continue but explicitly mark which parts can only receive weak judgment.

## Hard rules

- Do not score the paper.
- Do not simulate editorial peer review.
- Do not treat publication status as evidence strength.
- Do not infer missing logic on the author's behalf.
- Do not write vague praise or vague dismissal.
- Do not state that a result is false merely because support is insufficient.
- Do not claim reproducibility success or failure. Only judge whether reproducibility-relevant information appears sufficiently reported.
- Quote or locate sections, figures, tables, appendices, or cited works when available. If precise location is unavailable, do not fabricate it.

## Core judgment rules

### 1. Extract claims first
Do not begin with the abstract's framing. First isolate the main claims the paper wants the reader to accept.

Use these claim types:
- observational
- methodological
- mechanistic
- performance
- generality

### 2. Bind each claim to an evidence type
Every major claim must be tied to one or more evidence types. Use the controlled labels from `references/evidence-types.md`.

### 3. Judge support mismatch, not just amount of material
The central question is whether the evidence is strong enough for the level of conclusion being drawn.

### 4. Separate result from interpretation
Treat displayed results, reported statistics, demonstrated procedures, and documented materials separately from the author's explanation of what they mean.

### 5. Preserve uncertainty
When field knowledge, missing appendices, missing cited theory, or absent procedural detail blocks a judgment, say so directly.

## Paper-type emphasis

### Experimental, benchmark, or simulation papers
Prioritize:
- whether shown results actually support the stated mechanism or generality claim
- whether simulations are being used to overclaim real-world validity
- whether baselines or comparisons appear fair enough to sustain a performance claim
- whether the useful value lies mostly in results, methods, or setup rather than in interpretation

### Quantitative social science papers
Prioritize:
- whether inference scope matches the sample and design
- whether correlation is being stretched into causation
- whether robustness or sensitivity claims are doing real support work or only rhetorical work
- whether the paper's usable value lies more in the data/result layer than in the explanatory layer

### Empirical social science papers with interviews, archives, surveys, field notes, or content analysis
Prioritize:
- whether source material and interpretation are kept separate
- whether local material is being stretched into broad theory
- whether coding or material selection is being used as if it settled stronger claims than it can
- whether the real value lies in the material itself rather than in the imposed analytic frame

## Output template

Always use this exact section order.

# reader-side paper audit

## 1. reader conclusion
Write 3 to 6 sentences covering:
- what is most worth keeping from the paper
- what should be downweighted first
- whether the paper is mainly useful as result reference, method reference, inspiration, or low-priority material

## 2. core claims
List 3 to 5 core claims. For each claim include:
- content
- claim type
- conclusion strength: weak, medium, or strong

## 3. evidence and support
For each core claim include:
- evidence type
- support level: sufficient, partial, insufficient, or unclear
- main reason for that judgment

## 4. what is usable
Split into:
- usable results
- usable methods or design
- usable materials or documentation

Only include content that the paper itself actually demonstrates, reports, or documents.

## 5. what to downweight
Split into:
- worth noticing but should be downweighted
- should be treated cautiously or ignored

Use concrete reasons, not tone judgments.

## 6. value breakdown
Give one line each for:
- result value
- method value
- theory or insight value
- research design value
- material or documentation value

Use only: high, medium, low, or unclear.

## 7. uncertainty and follow-up
List the most important unresolved limits on judgment.
If a cited external paper appears structurally necessary to evaluate a core theory or mechanism claim, provide the cited work's title and DOI when available, and say that the user may want to read or upload it next.

## Writing discipline

- Prefer short declarative sentences.
- Use wording like: "usable content is limited to...", "the paper shows... but does not establish...", "the main overreach is...".
- Avoid wording like: "the paper is high quality", "the study is meaningful", "the analysis is deep", or other generic verdict language.

## References

Use these bundled references when needed:
- `references/evidence-types.md` for allowed evidence labels and how to apply them
- `references/pollution-patterns.md` for common overreach and contamination patterns
- `references/follow-up-boundaries.md` for how to discuss reproducibility limits, cited dependencies, and uncertainty without overclaiming
