# Method router

Use this file to decide which optional references to load.

The lexical router produces candidates, not final routes. A cue means "consider this module", not "a flaw exists".

Always load:
- `core-contract.md`
- `evidence-viability.md`
- `evidence-types.md`

Output interface:
- if Python can run: load `audit-ledger-format.md`, build routed context with `scripts/build_context.py`, and complete through `scripts/audit_gate.py`
- use `scripts/render_audit.py` / `scripts/validate_audit.py` only for focused debugging
- otherwise: load `output-contract.md`

Load `domain-profiles.md` when the paper clearly belongs to one of its listed domains.

## Evidence inventory trigger

Use `evidence-inventory-format.md` + `scripts/evidence_inventory.py` when retrieval/deduplication itself is becoming a reasoning burden, especially when:
- the same result is repeated across abstract/results/figures/tables/supplement
- multiple cohorts, datasets, sites, experiments, or replications share some but not all source units
- decision-critical evidence is split across main text and supplement/appendix
- several claims reuse overlapping data or experiments
- the paper is long enough that keeping all result text active would crowd out the audit contract

Do not trigger the inventory path merely because the article has many pages. It should reduce ambiguity or active-context load.


## Semantic confirmation pass

After core claims are available:
1. run or inspect the lexical candidate router
2. apply `semantic-router-card.md` to each decision-critical claim, preserving exact `claim_text`
3. use `scripts/build_context.py` to recompute the merge and materialize the routed references; when lexical fallback matters, pass the same plain source text used for lexical routing via `--router-text`; cached lexical JSON never substitutes for source text

Semantic `required` can add a module missed by keywords.
Semantic `not_required` can remove an incidental lexical hit.
Semantic `unclear` preserves a lexical hit until checked.

This claim-level pass is mandatory when optional routing matters. It is intentionally much smaller than loading every methodology reference.

## Route table

### Figures and tables
Load `figure-and-table-traps.md` when a core claim materially depends on:
- a figure
- a table
- a heatmap
- microscopy or imaging panels
- a cumulative curve
- a dual-axis or transformed-axis plot
- visual comparison of selected examples

Common cues:
`figure`, `table`, `heatmap`, `error bar`, `SEM`, `SD`, `CI`, `log scale`, `normalized`, `z-score`, `representative image`

### Statistical inference
Load `statistical-traps.md` when a core claim materially depends on:
- p-values or confidence/credible intervals
- regression or model coefficients
- multiple outcomes/features/comparisons
- subgroup claims
- repeated interim looks
- missing-data modeling
- robustness/specification analysis
- Bayesian inference

Common cues:
`p=`, `p <`, `confidence interval`, `credible interval`, `regression`, `odds ratio`, `hazard ratio`, `subgroup`, `interaction`, `multiple comparison`, `FDR`, `Bonferroni`, `imputation`

### Measurement and instruments
Load `measurement-traps.md` when a core claim materially depends on:
- an assay
- a sensor
- calibration
- a rating/score
- imaging-derived quantity
- LOD/LOQ
- a surrogate or biomarker
- batch correction
- preprocessing-defined measurement

Common cues:
`assay`, `sensor`, `calibration`, `LOD`, `LOQ`, `below detection`, `biomarker`, `surrogate`, `batch`, `segmentation`, `intensity`, `score`, `rating`

### Study design and identification
Load `study-design-traps.md` when a core claim materially depends on:
- randomization or intervention assignment
- before/after comparison
- historical or concurrent controls
- attrition/censoring
- clustered assignment
- repeated measures
- quasi-experimental identification
- train/validation/test splits
- prediction timing

Common cues:
`randomized`, `controlled`, `before-after`, `pre-post`, `difference-in-differences`, `matched control`, `cluster`, `site`, `attrition`, `crossover`, `instrumental variable`, `regression discontinuity`, `train`, `validation`, `test set`, `leakage`

### Evidence topology
Load `evidence-topology.md` when a core claim involves:
- mechanically related predictor/outcome construction
- selected or filtered analysis subsets
- proxy-to-construct transfer
- calibration target reused as validation
- cross-scale or cross-domain transfer
- internal conflict between summary and direct result

Common cues:
`filtered`, `valid cases`, `complete case`, `best configuration`, `proxy`, `surrogate`, `calibration`, `generalize`, `real-world`

### Evidence dependence
Load `evidence-dependence.md` when:
- a claim uses multiple evidence nodes
- replication is claimed
- several outcomes/assays/models agree
- technical and biological/subject/site replication must be separated

### Claim-evidence reuse
Load `claim-evidence-links.md` when:
- the same evidence node appears under multiple claims
- one result is used to support performance + mechanism + generality
- a claim has many evidence nodes and direct-support boundaries are unclear

### Claim dependencies
Load `claim-dependencies.md` when:
- one claim logically depends on another
- mechanism/causality/generality is built on earlier results
- uncertainty may be propagating through an inference chain

### External dependencies
Load `follow-up-boundaries.md` when:
- a core claim structurally depends on a cited paper
- DOI resolution matters
- missing supplement/data/code blocks judgment

## Mandatory anti-trigger pass

Whenever any optional trap module is loaded, also apply `false-positive-guards.md`.

Do not report a trap cue as a flaw until the mitigation check is complete.

## Flash routing strategy

Flash path is a context-loading strategy, not a reduced-quality mode.

1. read the paper once for scope and evidence viability; extract claims only after the viability gate
2. generate lexical route candidates
3. confirm routes claim-by-claim with `semantic-router-card.md`, preserving exact claim text
4. run `scripts/build_context.py` to deterministically merge routing and materialize the active reference bundle; if any semantic decision is `unclear`, provide the plain router text so lexical routing is recomputed rather than trusted from cache
5. audit claims one at a time using that bundle
6. re-run routing and rebuild the bundle if a later claim changes or exposes a new cue
7. keep false-positive guards in the generated context whenever a trap module is retained
8. complete through `scripts/audit_gate.py` with the raw semantic route and any lexical route needed for deterministic recomputation

Flash path does not permit fewer claims, missing fields, skipped routed modules, abstract-only support judgments, or weaker evidence standards.

## Escalate to Full path

Switch from Flash to Full path when any of these applies:
- three or more primary methodological modules are needed among figure/table, statistics, measurement, study design, and topology
- a core claim structurally depends on an external cited work
- direct results materially conflict across sections or displayed evidence
- multiple studies, cohorts, datasets, sites, or experiments require a non-trivial dependence map
- a decision-critical claim remains `unclear` after its targeted module check
- the user requests a comprehensive/deep audit

Full path may load more modules simultaneously and run a second cross-claim pass, but it uses the same evidence and output contracts.

Do not keep all optional references in context unless the paper genuinely needs them.
