# False-positive guards

Use this reference to prevent methodological trap detection from becoming automatic criticism.

A trap cue is a question to investigate, not a verdict.

## Core rule

Do not downgrade a claim merely because a familiar risk feature is present.

First ask:
1. What failure mode could the feature create?
2. Did the paper actually rely on the vulnerable inference?
3. Did the design or analysis explicitly mitigate that failure mode?
4. Does the mitigation address the relevant error source?
5. What residual uncertainty remains after mitigation?

Credit effective mitigation. Do not pretend that a risk remains unaddressed when the paper directly addresses it.

## Common anti-triggers

### Multiple subgroups are not automatically p-hacking
Do not penalize subgroup analysis merely because several subgroups are shown.

Look for:
- prespecification
- a direct treatment-by-subgroup interaction test
- multiplicity adjustment when confirmatory subgroup claims are made
- bounded language when subgroup analyses are exploratory

A non-significant interaction can support "no detected heterogeneity" without proving exact equality of treatment effects.

### Interim analyses are not automatically optional stopping
Repeated looks can be valid when governed by a prespecified group-sequential design, alpha-spending rule, or stopping boundary.

Check the actual stopping rule before invoking optional stopping.

### Non-detects are not automatically unusable data
LOD/LOQ creates censoring and uncertainty, not automatic invalidity.

Appropriate methods can include:
- censored likelihoods
- Tobit-type models
- interval/censoring models
- multiple imputation that propagates uncertainty
- justified binary detectability analyses

Judge the assumptions and validation of the method rather than penalizing the mere presence of non-detects.

### Technical repeats are not automatically pseudo-replication
Technical repeats are legitimate for estimating within-unit precision and technical variability.

The problem occurs only when they are treated as independent biological/physical units for a claim that requires independent specimens, participants, experiments, sites, or cohorts.

Hierarchical or mixed-effects models can explicitly preserve the nested structure.

### Before-after is not automatically uncontrolled
A study with pre/post data may still have a credible counterfactual through:
- a concurrent comparator
- difference-in-differences
- comparative interrupted time series
- synthetic control
- randomized timing or rollout

Inspect identification assumptions such as parallel trends, common shocks, or comparator suitability. Do not collapse all pre/post studies into simple uncontrolled before-after designs.

### Observational is not synonymous with weak
Observational records can strongly support description, prediction, incidence, prevalence, association, or bounded quasi-experimental claims.

Downgrade only the causal or generality reach that the design cannot identify.

### A truncated or log axis is not automatically misleading
A non-zero baseline can be appropriate when zero is not meaningful. A log scale can be the correct representation for multiplicative processes or wide dynamic ranges.

The question is whether the axis supports the comparison the prose asks the reader to make.

### Adjustment is not automatically overadjustment
Covariate adjustment can improve precision or address confounding. Overadjustment/collider concerns require a plausible causal structure, not suspicion based only on the number of covariates.

### Batch correction is not automatically data manipulation
When batch effects are measured and the correction procedure is explicit, correction can improve cross-batch comparability.

Check whether the biological/experimental effect is identifiable separately from batch and whether correction is validated. Do not infer impropriety from normalization itself.

## Residual-risk rule

A mitigation rarely proves that every possible bias is absent.

Use language such as:
- "this addresses the specific multiplicity concern"
- "the nested model preserves the unit structure"
- "the comparator removes the simple before-after attribution, subject to the stated DiD assumptions"
- "the censored-data model is preferable to substitution under its distributional assumptions"

Do not jump from "mitigation exists" to "study is bias-free."

## Silence rule

If a potential trap is adequately handled and leaves no decision-relevant residual issue, it does not need to appear in the final downweight section.

The skill should surface methodological issues that change interpretation, not reward itself for noticing every possible hazard.

## Usage rule

Methodological skepticism is asymmetric only toward unsupported claims, not toward complexity itself. Prefer a precise statement of residual risk over a generic warning label.
