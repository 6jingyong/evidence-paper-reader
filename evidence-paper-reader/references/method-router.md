# Method router

Use this file to decide which optional references to load.

The router is deliberately conservative: a cue means "inspect this module", not "a flaw exists".

Always load:
- `core-contract.md`
- `output-contract.md`
- `evidence-types.md`

Load `domain-profiles.md` when the paper clearly belongs to one of its listed domains.

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

## Weak-model routing strategy

For a weaker model:
1. read the paper once for scope and 3-5 claims
2. create a minimal cue list
3. load only the modules matched by this router
4. audit claims one at a time
5. validate the final output with the Python validator

Do not keep all optional references in context unless the paper genuinely needs them.
