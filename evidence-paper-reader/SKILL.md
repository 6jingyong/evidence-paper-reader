---
name: evidence-paper-reader
description: read evidence-driven research papers using a reader-side framework that separates claims, evidence types, support strength, usable value, and analysis pollution. use when a user wants to know what in a paper is actually trustworthy, what is only partially supported, what is methodologically reusable, or what should be downweighted. suitable for experimental natural science papers, benchmark or ablation-heavy method papers, simulation or computational papers, quantitative finance and econometrics, clinical and biomedical empirical papers with traceable evidence chains, quantitative social science papers, empirical aesthetics or human-subject arts research, and empirical social science papers with clear evidence chains such as surveys, interviews, archives, field notes, or content analysis. not for pure mathematics, patient-specific clinical decision making, or primarily normative or interpretive theory papers without a traceable evidence chain.
license: MIT
---

# Evidence Paper Reader

## Overview

Use this skill to read papers as a skeptical reader rather than as an editor or reviewer. The goal is to extract what can be relied on, identify what is only weakly supported, and prevent the author's narrative framing from being mistaken for evidence.

Default output language follows the user's input language. If the paper is in English, or uses field-specific terminology, do not force translation and do not add parenthetical translations unless the user explicitly asks.

## Workflow

1. Inventory the material actually available: main text, figures/tables, appendices or supplements, references, data/code links, and any missing pieces.
2. Make a scope decision before substantive judgment and record one status: `in scope`, `partially in scope`, or `out of scope`.
3. Identify the paper type and adjust attention accordingly.
4. Extract the core claims before judging them.
5. Bind each core claim to controlled evidence labels, evidence provenance, and a source location.
6. Judge whether evidence strength matches conclusion strength.
7. Run a cross-section consistency scan: compare abstract, results, displayed figures/tables, discussion, and conclusion for the same quantitative trend, phase assignment, sample description, or causal statement.
8. Check validation independence: ask whether the evaluation reuses a calibration target, tuning set, judge, proxy, or other signal that was already used to optimize the reported method.
9. Check evidence topology: look for mechanical coupling between predictor and outcome, selected/filtered analysis subsets, and operational proxies that are being treated as the broader construct itself.
10. For null or negative findings, inspect uncertainty bounds before accepting claims of no effect, equivalence, safety, or practical irrelevance.
11. Separate usable content from analysis that should be downweighted.
12. Resolve citation dependencies: distinguish support shown in the current paper from support delegated to cited work.
13. Produce the fixed reader-side output template.

## Scope decision

Treat the paper as in scope only if it is primarily evidence-driven and has a traceable evidence chain.

Use exactly one scope status:
- `in scope`: the central claims can be audited from evidence reported or directly documented by the paper
- `partially in scope`: some central claims have traceable evidence, while other major parts are normative, interpretive, theoretical, clinical, or blocked by missing material
- `out of scope`: the paper's central contribution cannot be meaningfully audited with this evidence-chain framework

Default in-scope categories:
- experimental natural science papers
- benchmark or ablation-heavy method papers
- simulation or computational papers
- quantitative social science papers
- quantitative finance, econometrics, and market-microstructure papers with traceable empirical records
- clinical trials, diagnostic studies, and observational medical papers when the task is evidence-chain auditing rather than patient-specific treatment advice
- empirical aesthetics, neuroaesthetics, reception studies, and other arts/humanities papers when their central claims rely on traceable empirical evidence
- empirical social science papers with clear evidence chains, including surveys, interviews, archives, field notes, and content analysis

Default out-of-scope categories:
- pure mathematics
- patient-specific clinical decision or treatment-recommendation tasks that require applying evidence to an individual rather than auditing a paper
- clinical guideline or standard-of-care judgments that depend on a wider evidence base than the paper under inspection
- papers centered on normative argument, pure theory exposition, or heavily interpretive analysis without a clear evidence chain

If the paper is partially in scope, continue but explicitly mark which claims or sections can only receive weak judgment.

If the paper is out of scope, preserve the seven-section output skeleton so downstream use remains predictable, but do not force 3 to 5 artificial claims. In sections 2 through 6, use `not applicable` where the framework would create false precision, and explain the scope blocker in section 1 and section 7.

## Hard rules

- Do not score the paper.
- Do not simulate editorial peer review.
- Do not treat publication status as evidence strength.
- Do not infer missing logic on the author's behalf.
- Do not write vague praise or vague dismissal.
- Do not state that a result is false merely because support is insufficient.
- Do not claim reproducibility success or failure. Only judge whether reproducibility-relevant information appears sufficiently reported.
- Use only the evidence labels defined in `references/evidence-types.md` unless the user explicitly requests a looser reading.
- Every support judgment must identify evidence provenance as `paper-local`, `external citation`, or `mixed`.
- A literature citation is not paper-local evidence. Do not upgrade a current-paper support judgment merely because the paper cites prior work.
- Every evidence item must include a traceable source location when available: section, figure, table, appendix/supplement, or page. If no precise location is available, write `location unavailable`; never fabricate one.
- Do not claim to know the contents of a cited work unless that work is actually available to inspect.
- Do not guess DOIs from memory.
- When the abstract, conclusion, discussion, and displayed results conflict, expose the conflict. Do not silently reconcile incompatible numbers, trends, phase labels, sample descriptions, or causal statements.
- Do not let summary prose override more direct paper-local evidence such as reported measurements, tables, figures, or explicitly documented procedures.
- Do not treat agreement with a calibration or tuning target as independent validation of real-world accuracy or generalization when that same target helped fit the method.
- If a predictor, exposure, score, or explanatory variable mechanically contains or is defined by events that also change the outcome, state the coupling and do not interpret the raw association or R-squared as independent explanatory strength.
- Do not translate `not statistically significant` into `no effect`, `equivalent`, `safe`, or `clinically irrelevant`. Inspect confidence/credible intervals, power or precision, and any pre-specified equivalence or non-inferiority margin.
- Keep an operational proxy separate from the broader construct it represents. A rating, biomarker, neural correlate, benchmark score, or survey scale can support claims about that measure without automatically establishing the full construct.
- When evidence is filtered, complete-case, thresholded, configuration-selected, or reported at an optimal setting, keep the claim scoped to the retained subset or condition unless the paper separately supports broader operation.
- For medical papers, audit the reported design, outcomes, uncertainty, and causal reach; do not turn the paper audit into patient-specific medical advice or a standard-of-care recommendation.

## Core judgment rules

### 1. Extract claims first
Do not begin with the abstract's framing. First isolate the main claims the paper wants the reader to accept.

Use these claim types:
- observational
- methodological
- mechanistic
- performance
- generality
- intervention

`conclusion strength` describes the reach of the paper's claim, not confidence in your judgment:
- `weak`: local/descriptive claim with limited extrapolation
- `medium`: comparative, explanatory, or bounded generalization claim
- `strong`: broad causal, mechanistic, or generality claim that reaches well beyond the immediate observation

### 2. Bind each claim to an evidence type
Every major claim must be tied to one or more evidence types. Use the controlled labels from `references/evidence-types.md`.

For each evidence item, also record:
- evidence provenance: `paper-local`, `external citation`, or `mixed`
- source location: the most precise available section/figure/table/appendix/page locator

### 3. Judge support mismatch, not just amount of material
The central question is whether the evidence is strong enough for the level of conclusion being drawn.

A support level applies to the claim as written, not to a narrower claim you silently substitute:
- `sufficient`: the shown evidence supports the claim at approximately the stated scope
- `partial`: a narrower or qualified version is supported, but the stated claim reaches farther
- `insufficient`: the available evidence does not establish the stated claim
- `unclear`: available material is too incomplete or ambiguous to judge

### 4. Separate result from interpretation
Treat displayed results, reported statistics, demonstrated procedures, and documented materials separately from the author's explanation of what they mean.

### 5. Preserve uncertainty
When field knowledge, missing appendices, missing cited theory, or absent procedural detail blocks a judgment, say so directly.

### 6. Keep external dependencies external
If a core claim relies structurally on a cited work, name that dependency in the claim's support entry. The current paper may accurately report the cited result, but until the cited work is inspected, that imported support remains an external dependency rather than verified paper-local evidence. Follow `references/follow-up-boundaries.md`.

### 7. Check internal consistency before finalizing
For each core claim, compare the strongest direct evidence with every place the paper restates that claim, especially the abstract and conclusion. If one section says a quantity rises continuously while the reported values do not, or if the conclusion names a phase/mechanism not directly established in the results, report the contradiction explicitly. Prefer the most direct, precisely located paper-local evidence for the bounded result; lower support for the broader narrative claim rather than choosing whichever wording is more favorable.

### 8. Check whether validation is independent
Distinguish `fit to target` from `validated against an independent target`. If a model, sensor, calibration, scoring rule, or agent is optimized against a target and then evaluated mainly by agreement with that same target, the result can support successful fitting but cannot by itself establish external accuracy or generalization. Look for independent held-out measurements, stations, datasets, annotators, or other genuinely separate validation evidence before upgrading the broader claim.

### 9. Check evidence topology and construction
Ask whether the variables and analysis population are independent enough for the claimed interpretation.
- If predictor and outcome share mechanically coupled components, report what part of the fit may be structural and look for a decoupled robustness analysis.
- If results are calculated after filtering, attrition, complete-case restriction, validity thresholds, or selection of an optimal configuration, record that conditioning and do not silently generalize to excluded cases.
- If the paper operationalizes an abstract construct through a proxy, distinguish `evidence about the proxy` from `evidence about the construct`. Strong measurement of a proxy does not by itself prove that the proxy exhausts the construct.

### 10. Interpret null results through effect bounds
A non-significant test answers a different question from equivalence or absence of a meaningful effect. For intervention, clinical, policy, or performance claims, inspect the confidence/credible interval and any declared meaningful-effect threshold. If the interval still contains effects that would matter under the paper's own framing, support a claim such as `no statistically detected difference`, but downweight a stronger `no meaningful effect` conclusion.

## Paper-type emphasis

### Experimental, benchmark, or simulation papers
Prioritize:
- whether shown results actually support the stated mechanism or generality claim
- whether simulations are being used to overclaim real-world validity
- whether baselines or comparisons appear fair enough to sustain a performance claim
- whether calibration/tuning and validation are genuinely independent when accuracy or generalization is claimed
- whether the abstract/conclusion accurately restate the displayed quantitative and phase/structure results
- whether the useful value lies mostly in results, methods, or setup rather than in interpretation

For machine-learning, software, or algorithm papers, use `computational benchmark` for dataset/task evaluations and ablations. Do not relabel benchmark results as `numerical simulation` unless the computation is actually simulating a target system or phenomenon.

### Finance, econometrics, and market-microstructure papers
Prioritize:
- whether explanatory variables are mechanically coupled to price, return, volume, accounting, or other outcome definitions
- whether contemporaneous regression language such as `drives`, `impact`, or `explains` exceeds the temporal and identification structure
- whether robustness survives a construction that removes mechanically outcome-changing components
- whether evidence from one market regime, month, asset universe, or liquidity condition is generalized too broadly

### Clinical and biomedical empirical papers
Prioritize:
- randomization, control condition, blinding, attrition, outcome specification, and whether analyses match the pre-specified comparison when reported
- effect sizes and uncertainty intervals, not p-values alone
- whether a non-significant finding is being upgraded to equivalence or no clinically meaningful effect
- whether subgroup, per-protocol, or complete-case findings are being generalized to the full trial population
- whether mechanistic biomarkers are being treated as substitutes for patient-relevant outcomes

This skill can audit the evidence chain of a clinical paper. It must not convert that audit into patient-specific treatment advice or an independent standard-of-care verdict.

### Empirical aesthetics and human-subject arts research
Prioritize:
- how abstract constructs such as beauty, preference, meaning, style, creativity, or aesthetic value are operationalized
- whether self-ratings, neural signals, behavioral tasks, or coded judgments are being treated as the construct itself
- whether limited stimulus sets, cultures, modalities, or participant samples are generalized into universal aesthetic claims
- whether prior-defined regions, categories, or coding schemes materially constrain what the analysis can discover

### Quantitative social science papers
Prioritize:
- whether inference scope matches the sample and design
- whether correlation is being stretched into causation, especially when titles or conclusions use verbs such as `caused`, `harmed`, or `improved` for cross-sectional or otherwise non-causal designs
- whether robustness or sensitivity claims are doing real support work or only rhetorical work
- whether the paper's usable value lies more in the data/result layer than in the explanatory layer

### Empirical social science papers with interviews, archives, surveys, field notes, or content analysis
Prioritize:
- whether source material and interpretation are kept separate
- whether local material is being stretched into broad theory
- whether coding or material selection is being used as if it settled stronger claims than it can
- whether the real value lies in the material itself rather than in the imposed analytic frame

## Output template

Always use this exact section order and field names. Do not insert extra top-level sections.

# reader-side paper audit

## 1. reader conclusion
Start with:
- `scope status: in scope | partially in scope | out of scope`
- `paper type: ...`

Then write 3 to 6 sentences covering:
- what is most worth keeping from the paper
- what should be downweighted first
- whether the paper is mainly useful as result reference, method reference, inspiration, or low-priority material

## 2. core claims
For `in scope` and `partially in scope` papers, list 3 to 5 core claims using this structure:

### claim 1
- content: ...
- claim type: observational | methodological | mechanistic | performance | generality | intervention
- conclusion strength: weak | medium | strong

Repeat sequentially as needed. For an `out of scope` paper, use `not applicable — <reason>` instead of inventing claims.

## 3. evidence and support
For every claim in section 2, use the same claim number and this structure:

### claim 1
- evidence type: <one or more controlled labels from references/evidence-types.md>
- evidence provenance: paper-local | external citation | mixed
- source location: <section/figure/table/appendix/page or location unavailable>
- support level: sufficient | partial | insufficient | unclear
- reason: ...
- external dependency: none | <cited work title; DOI if verified/available; why it matters>

If multiple evidence items support one claim, keep them within the same claim block and make their locations explicit. For an `out of scope` paper, use `not applicable — <reason>`.

## 4. what is usable
Use these exact subheadings:

### usable results

### usable methods or design

### usable materials or documentation

Only include content that the paper itself actually demonstrates, reports, or documents. If the paper is out of scope, use `not applicable` where appropriate.

## 5. what to downweight
Use these exact subheadings:

### worth noticing but should be downweighted

### should be treated cautiously or ignored

Use concrete reasons, not tone judgments. If the paper is out of scope, use `not applicable` where appropriate.

## 6. value breakdown
Give exactly one line each:
- result value: high | medium | low | unclear
- method value: high | medium | low | unclear
- theory or insight value: high | medium | low | unclear
- research design value: high | medium | low | unclear
- material or documentation value: high | medium | low | unclear

For an out-of-scope paper, `unclear` is usually preferable to invented low/high judgments.

## 7. uncertainty and follow-up
List the most important unresolved limits on judgment, including missing appendices/supplements/data/code when they matter.

If a cited external paper appears structurally necessary to evaluate a core theory or mechanism claim:
1. provide the cited work's title
2. provide its DOI only when present in the inspected material or verified through an authoritative metadata lookup
3. state why the dependency matters
4. say that the user may want to read or upload it next

If no structurally necessary external dependency was found, say so rather than manufacturing one.

## Writing discipline

- Prefer short declarative sentences.
- Use wording like: "usable content is limited to...", "the paper shows... but does not establish...", "the main overreach is...".
- Avoid wording like: "the paper is high quality", "the study is meaningful", "the analysis is deep", or other generic verdict language.

## References

Use these bundled references when needed:
- `references/evidence-types.md` for allowed evidence labels and how to apply them
- `references/pollution-patterns.md` for common overreach and contamination patterns
- `references/follow-up-boundaries.md` for reproducibility limits, evidence provenance, cited dependencies, and DOI handling
