# Statistical interpretation traps

Use this reference only when a core claim materially depends on statistical inference, model specification, subgroup analysis, or repeated testing.

The goal is not to reject a result because a statistical method is imperfect. The goal is to identify when the reported inferential quantity does not support the strength or scope of the claim.

## Effect size before significance

A p-value does not measure effect size, practical importance, replication probability, or the probability that a hypothesis is true.

Check:
- effect estimate
- uncertainty interval
- scale and units
- whether the effect is large enough to matter under the paper's own framing
- whether the interval includes materially different interpretations

A tiny effect can be statistically precise. A potentially important effect can be statistically uncertain.

## Multiple testing and selection

### Multiplicity
When many outcomes, subgroups, features, time points, models, or contrasts are tested, nominal significance can arise by chance.

Check:
- how many tests were plausible candidates
- whether the displayed tests were pre-specified or selected after inspection
- whether multiplicity control is reported when the paper makes discovery or selection claims
- whether the headline result is one among many similar comparisons

Do not assume absence of a correction is automatically fatal. Match the concern to the claim: exploratory screening and confirmatory inference have different evidentiary demands.

### Winner's curse
Effects selected because they are the largest or most significant are often upward-biased estimates of the underlying effect.

Treat selected discovery estimates differently from independently replicated estimates.

### Researcher/model degrees of freedom
Several reasonable preprocessing, covariate, exclusion, transformation, or model choices can produce a wide result space.

Robustness across nearby specifications is more informative when the alternatives were not selected solely because they preserved the desired conclusion.

## Optional stopping and repeated looks

Repeatedly inspecting accumulating data and stopping when a threshold is crossed changes nominal error rates unless the design accounts for sequential testing.

Look for:
- interim analyses
- early stopping
- repeated peeking
- adaptive sample-size changes
- repeated benchmark runs until a favorable seed appears

Do not infer optional stopping merely from an unusual sample size; require evidence from the reported workflow.

## Regression to the mean

Groups selected for extreme baseline values tend to move toward the average on repeat measurement even without an intervention.

This matters for:
- before/after designs
- high-risk or extreme-score recruitment
- defect/failure investigations
- top/bottom performer follow-up

A pre/post improvement in an extreme selected group is not automatically an intervention effect.

## Subgroup and interaction traps

### Significant in one group, not significant in another
This does not by itself prove that the groups differ.

Prefer a direct interaction or heterogeneity test when the claim is about a difference between subgroup effects.

### Post-hoc subgroup
A subgroup defined after seeing the data can generate hypotheses but usually provides weaker confirmatory evidence unless independently replicated.

### Small subgroup instability
Large-looking subgroup effects can be driven by few events or observations. Inspect n and uncertainty.

## Covariate adjustment traps

### Overadjustment
Adjusting for a mediator or descendant of the exposure can remove part of the effect the paper intends to estimate.

### Collider conditioning
Conditioning on a variable caused by two other variables can induce an association that was not present before conditioning.

### Inconsistent model targets
Two adjusted models with different covariate sets can estimate different quantities. Do not treat coefficient changes as purely "more accurate" without considering what estimand changed.

Do not diagnose a collider or mediator from variable names alone. The causal structure must be plausible and relevant to the claim.

## Model-form traps

### Nonlinearity hidden by a linear summary
A single slope can obscure thresholds, saturation, U-shapes, or regime changes.

### Extrapolation
Model predictions outside the observed support are not directly validated by in-range fit.

### Separation and sparse events
Logistic or related models can become unstable when outcomes are rare or predictors nearly separate groups.

### Ratio and denominator instability
Ratios can become volatile when denominators are small, noisy, or close to zero.

### Transform and back-transform
Means or differences on log, logit, standardized, or other transformed scales do not always translate directly into arithmetic-scale interpretations.

## Dependence and standard errors

Observations can be statistically dependent because of:
- repeated measures
- families
- schools or hospitals
- geographic clusters
- time series
- multiple samples from one specimen
- multiple patches/crops from one image
- many prompts/items generated from one source

Check whether uncertainty estimation reflects the actual independent unit.

A large row count is not the same as a large number of independent units.

## Missing data

Complete-case analysis is not automatically unbiased.

Ask:
- how much data are missing
- whether missingness differs by group or outcome
- whether the analysis population changes across models
- what assumptions the imputation or weighting method requires

Do not infer the missingness mechanism from absence alone.

## Bayesian results

For posterior claims, inspect:
- prior choice when it materially affects the result
- posterior interval, not only posterior mean
- whether Bayes factors or posterior probabilities are interpreted on the scale actually computed
- sensitivity to reasonable priors when the data are weak

Do not translate Bayesian intervals mechanically into frequentist confidence statements or vice versa.

## Robustness versus duplication

Ten nearby model specifications using the same dataset do not create ten independent confirmations.

Robustness analysis can show that a result is not fragile to specific modeling choices; evidence independence remains governed by the underlying data source.

## Usage rule

Apply only the statistical traps that can materially change a core support judgment. State the concrete inferential mismatch rather than labeling a method "bad" in the abstract.
