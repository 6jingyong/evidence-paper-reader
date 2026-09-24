# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- paper type: benchmark and human-evaluation paper

The most reusable contribution is the benchmark construction and the measured gap between automated ablation planning and the ablations authors actually performed. The current version reports 83 AuthorAblation instances and 350 ReviewerAblation instances, with the best system recovering only a limited fraction of author ablations. A small human baseline also shows that expert researchers outperform GPT-5.4 on the selected subset, which is useful evidence that the benchmark is not already saturated. The broad statement that one-step chain-of-thought planning is intrinsically superior to agentic planning should be kept narrower than the paper's rhetoric because GPT-5.4 is approximately tied across the two planner forms and model-specific results vary. The paper is mainly useful as a benchmark, evaluation design, and empirical result reference.

## 2. core claims

### claim 1
- content: AblationBench operationalizes ablation-planning quality using author-performed and reviewer-requested ablations collected from empirical AI papers.
- claim type: methodological
- conclusion strength: medium

### claim 2
- content: Current frontier language-model planners recover only a limited fraction of the ablations authors actually performed, with the best reported system reaching roughly 45 percent recall on AuthorAblation.
- claim type: performance
- conclusion strength: medium

### claim 3
- content: On the selected ten-paper human-baseline subset, ML PhD participants outperform GPT-5.4 at selecting useful ablations.
- claim type: performance
- conclusion strength: medium

### claim 4
- content: A single full-context chain-of-thought language-model call is generally a better ablation planner than a multi-step agentic planner.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: computational benchmark
- evidence provenance: paper-local
- evidence nodes: E1
- upstream claims: none
- evidence dependence: single-source
- source location: benchmark construction and dataset sections; AuthorAblation and ReviewerAblation dataset statistics in the current arXiv version
- support level: sufficient
- reason: The paper directly documents the paper selection, extraction pipeline, benchmark instances, and evaluation setup used to define the two benchmark tracks. This supports the bounded claim that the benchmark implements a reproducible evaluation target, not that it perfectly captures all scientifically valuable ablations.
- external dependency: none

### claim 2
- evidence type: computational benchmark
- evidence provenance: paper-local
- evidence nodes: E2 + E3
- upstream claims: C1
- evidence dependence: shared-source convergence
- source location: main planner-results table and results discussion in the current arXiv version
- support level: sufficient
- reason: The reported benchmark results directly show that even the best evaluated system matches only a minority of author ablations. This is a benchmark-specific performance result and does not require a stronger claim about general scientific reasoning ability.
- external dependency: none

### claim 3
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E4 + E5
- upstream claims: C1
- evidence dependence: partially independent convergence
- source location: human-baseline subsection; ten participants each evaluated one selected paper, with human F1@5 about 0.66 versus about 0.43 for GPT-5.4 on the same subset
- support level: sufficient
- reason: The paper directly reports the human evaluation and the matched model comparison. The evidence supports the stated result for this small selected subset but not a population-wide estimate of all expert researchers or all papers.
- external dependency: none

### claim 4
- evidence type: computational benchmark + author interpretation
- evidence provenance: paper-local
- evidence nodes: E2 + E3
- upstream claims: C1 + C2
- evidence dependence: shared-source convergence
- source location: planner comparison table and discussion comparing LM-Planner with Agent-Planner
- support level: partial
- reason: Several evaluated models favor the simpler planner and the aggregate discussion points in that direction, but GPT-5.4 is approximately tied across planner forms and model-specific results are not uniform. The evidence supports a bounded empirical tendency in this benchmark, not an intrinsic general advantage of one-step planning.
- external dependency: none

## 4. what is usable

### usable results
The model-by-model planner comparison, benchmark recall/F1 results, and matched human-baseline measurements are directly reusable as empirical reference points for automated scientific-ablation planning.

### usable methods or design
The split between AuthorAblation and ReviewerAblation, explicit matching criteria, judge aggregation, and matched human comparison are reusable evaluation-design ideas.

### usable materials or documentation
The paper documents benchmark composition, task construction, judge setup, prompts, and evaluation metrics in enough detail to inspect the benchmark logic, while this audit does not infer reproduction success.

## 5. what to downweight

### worth noticing but should be downweighted
The qualitative explanation for why simpler full-context prompting can outperform a longer agent trajectory is plausible but is less directly established than the benchmark score differences.

### should be treated cautiously or ignored
Any universal reading that chain-of-thought planning is superior to agentic planning independent of model, task, context length, or agent design should be ignored. The reported evidence is benchmark- and implementation-specific.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: medium
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The benchmark's ground truth is constructed from author and reviewer ablation choices, which are useful but not exhaustive definitions of scientific value. The human baseline is intentionally small and should not be generalized beyond the tested subset. Judge-model error and paper-selection effects remain potential limits even though the paper reports judge-validation checks. No structurally necessary external citation is required to judge the four core claims above because the decisive evidence is reported in the current paper.
