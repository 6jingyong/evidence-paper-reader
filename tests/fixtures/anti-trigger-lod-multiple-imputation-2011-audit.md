# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- evidence viability: auditable
- viability flags: none
- paper type: censored-data statistical method paper with simulation and environmental-health application

The paper should not be downweighted merely because many laboratory measurements fall below the limit of detection. It explicitly treats those observations as left-censored rather than exact zeros or exact LOD/2 values, builds a bivariate likelihood that includes censoring and missingness, and evaluates the resulting estimators over 5,000 simulated samples across multiple censoring levels, correlations, and sample sizes. The simulations also expose the method's limits: bias increases for small samples with heavy censoring, so the correct conclusion is not that multiple imputation solves every non-detect problem. The paper is mainly useful as a methodological reference and as an anti-trigger example showing that non-detects are a modeling problem rather than automatic evidence failure.

## 2. core claims

### claim 1
- content: Simple constant substitution for values below the LOD can materially distort parameter and association estimates in the tested bivariate setting.
- claim type: methodological
- conclusion strength: medium

### claim 2
- content: The proposed likelihood-based multiple-imputation approach produces useful estimates for left-censored bivariate measurements across the tested simulation settings, especially with larger samples or less extreme censoring.
- claim type: performance
- conclusion strength: medium

### claim 3
- content: The presence of substantial non-detection in the pesticide application makes the biomarker analysis intrinsically invalid.
- claim type: methodological
- conclusion strength: strong

### claim 4
- content: The proposed method can be assumed unbiased for arbitrary distributions, tiny samples, and arbitrarily high censoring.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: numerical simulation + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: partially independent convergence
- source location: Simulation study and PACE3 application; comparisons of multiple imputation, LOD/2, LOD substitution, and excluding nondetects
- support level: sufficient
- reason: Simulations and the empirical application show materially different estimates under simple substitution and exclusion rules. This directly supports the bounded claim that ad hoc handling can distort results.
- external dependency: none

### claim 2
- evidence type: numerical simulation + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E3 + E4 + E5
- upstream claims: C1
- evidence dependence: partially independent convergence
- source location: Simulation study; n=50 and n=200, varying correlation and censoring proportions, 5,000 replicates per scenario
- support level: sufficient
- reason: The method is evaluated against known simulation truth across a structured range of conditions. It performs well in many tested settings while visibly degrading at small n and heavy censoring, so the support is strongest for the bounded performance claim rather than universality.
- external dependency: none

### claim 3
- evidence type: statistical analysis
- evidence provenance: paper-local
- evidence nodes: E4 + E6
- upstream claims: C2
- evidence dependence: shared-source convergence
- source location: Methods and Data Analysis; censored likelihood, multiple imputation, and explicit propagation of imputation uncertainty
- support level: insufficient
- reason: Non-detects create left-censoring, but the paper models that censoring explicitly rather than pretending the measurements are known constants. The methodological risk remains conditional on distributional assumptions and sample size; the mere presence of nondetects is not grounds to declare the analysis invalid.
- external dependency: none

### claim 4
- evidence type: numerical simulation + author interpretation
- evidence provenance: paper-local
- evidence nodes: E3 + E5 + E7
- upstream claims: C2
- evidence dependence: partially independent convergence
- source location: Simulation results and Discussion; increased bias at n=50 with 50%-70% censoring and discussion of alternative distributions
- support level: insufficient
- reason: The paper itself shows larger bias under small-sample/high-censoring conditions and notes that the assumed distribution may be inappropriate in settings with structural zeros or other shapes. Those limitations directly contradict an unrestricted-validity claim.
- external dependency: none

## 4. what is usable

### usable results
The simulation bias patterns and comparison of MI with ad hoc substitution/exclusion methods are directly usable for evaluating non-detect handling.

### usable methods or design
Using a censoring-aware likelihood, generating multiple plausible values, combining inference across imputations, and validating against simulated truth are strong methodological choices.

### usable materials or documentation
The paper states sample sizes, censoring fractions, correlation settings, number of simulation replicates, distributional assumptions, and the empirical pesticide application.

## 5. what to downweight

### worth noticing but should be downweighted
The real-data association remains conditional on the assumed model for the latent concentration distribution and other observational-study limitations.

### should be treated cautiously or ignored
Do not penalize the analysis simply because values are below LOD. The relevant question is whether censoring and its uncertainty were modeled appropriately.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: high
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
Distribution-based imputation inherits its distributional assumptions, and the simulations show weaker performance with small samples and extreme censoring. The paper explicitly discusses cases such as structural zeros where a different mixture model may be needed. The anti-trigger lesson is that LOD is not an automatic failure label when the analysis models censoring and validates the method.
