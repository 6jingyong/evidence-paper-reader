# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- evidence viability: auditable
- viability flags: none
- paper type: multisite hierarchical reproducibility and imaging-method study

The study contains very large numbers of cells, time points, and technical replicates, but it should not be accused of pseudo-replication merely because the raw row count is large. The experimental design explicitly nests technical replicates inside independent experiments, persons, and laboratories, and the analysis uses a linear mixed-effects model to estimate variance components at those levels. This structure reveals rather than hides dependence: laboratory-to-laboratory variability is the largest technical component, while technical-repeat variability is smaller. Batch-effect correction then improves separation of perturbation effects across laboratories, but that correction should not be generalized into a claim that all imaging studies become reproducible after normalization. The paper is mainly useful as a measurement/dependence reference and as an anti-trigger example of technical repeats handled at their proper hierarchical level.

## 2. core claims

### claim 1
- content: In the tested 2D live-cell migration system, laboratory-to-laboratory differences contribute more technical variability than person, experiment, or technical-replicate levels.
- claim type: observational
- conclusion strength: medium

### claim 2
- content: The large number of cells and technical repeats can be treated as independent laboratory-level replications when estimating reproducibility.
- claim type: methodological
- conclusion strength: strong

### claim 3
- content: The hierarchical mixed-effects analysis appropriately separates variance contributions across laboratory, person, experiment, technical replicate, cell, and time levels for the stated variance-component question.
- claim type: methodological
- conclusion strength: medium

### claim 4
- content: Batch-effect removal universally solves cross-laboratory reproducibility for high-content imaging.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2 + E3
- upstream claims: none
- evidence dependence: partially independent convergence
- source location: Figure 1 design, Variability sources, and Figure 3; three independent laboratories, three persons per laboratory, three independent experiments per person, and nested technical replicates
- support level: sufficient
- reason: The multilevel design deliberately samples multiple laboratories and lower-level sources, and the mixed model estimates variance at each level. The reported hierarchy therefore concerns the measured systems rather than an artifact of counting every cell as an independent laboratory.
- external dependency: none

### claim 2
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E4
- upstream claims: C1
- evidence dependence: shared-source convergence
- source location: Study design and mixed-effects model specification
- support level: insufficient
- reason: Cells, time points, and technical replicates are explicitly nested inside experiments, persons, and laboratories. The paper does not use their large count to manufacture independent laboratory replication; it models dependence across levels.
- external dependency: none

### claim 3
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E3 + E4
- upstream claims: none
- evidence dependence: partially independent convergence
- source location: Variability sources and Materials/Methods; nested random-intercept linear mixed-effects model
- support level: sufficient
- reason: The model architecture matches the hierarchical data-generating structure relevant to the variance-component claim. Technical repeats remain useful observations for estimating within-level variability without being relabeled as independent sites.
- external dependency: none

### claim 4
- evidence type: direct experiment + statistical analysis + author interpretation
- evidence provenance: paper-local
- evidence nodes: E5 + E6
- upstream claims: C1 + C3
- evidence dependence: partially independent convergence
- source location: Batch effect removal results and Discussion
- support level: partial
- reason: Correction improves perturbation separation across the tested laboratories and datasets, but the effect is demonstrated within specific 2D/3D migration systems, shared protocols, and modeling choices. It does not establish a universal correction recipe for all image-based biology.
- external dependency: none

## 4. what is usable

### usable results
Variance-component estimates, laboratory/person/experiment/replicate comparisons, and perturbation results before and after batch correction are directly usable for the tested imaging systems.

### usable methods or design
The explicit nested design and mixed-effects variance decomposition are strong examples of using technical repeats without confusing them with independent laboratories.

### usable materials or documentation
The study reports laboratories, operators, independent experiments, technical replicates, approximate cell counts, acquisition intervals, common protocols, processing pipeline, and shared raw/code resources.

## 5. what to downweight

### worth noticing but should be downweighted
Batch-effect removal improves the tested cross-site perturbation analysis, but its effectiveness remains system- and model-dependent.

### should be treated cautiously or ignored
Do not flag pseudo-replication merely because thousands of cell-time observations exist. The inferential structure explicitly models those observations as nested rather than as thousands of independent sites.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: high
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The study deliberately standardizes cell lines, key reagents, and parts of the analysis pipeline, so broader inter-laboratory heterogeneity may be larger in less coordinated settings. The anti-trigger lesson is specific: repeated lower-level observations are legitimate when the hierarchy is preserved in design and analysis; technical replication is not itself evidence of pseudo-replication.
