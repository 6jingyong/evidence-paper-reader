# Study design traps

Use this reference when the strength of a core claim depends on how observations, interventions, groups, time periods, datasets, or benchmark splits were assigned or selected.

The goal is to identify what the design can identify, not to demand randomized trials for every question.

## Unit of assignment versus unit of analysis

The inferential unit should match the unit that was independently assigned or sampled.

Common mismatches:
- treatment assigned by school but analysis treats students as independent
- one specimen generates many fields/images
- one patient generates many lesions or time points
- one document generates many segments
- one source task generates many benchmark items

More rows do not create more independent assignments.

## Randomization, concealment, and blinding

For randomized studies distinguish:
- sequence generation
- allocation concealment
- participant blinding
- operator/assessor blinding
- analysis masking when relevant

Random assignment reduces confounding; blinding addresses different biases. One does not imply the other.

## Before-after without a concurrent control

Change after an intervention can reflect:
- secular trend
- regression to the mean
- seasonality
- learning
- maturation
- instrumentation drift
- unrelated co-interventions

A controlled or interrupted design may strengthen attribution, but a simple pre/post change is not by itself causal proof.

## Historical controls

A current intervention group compared with an earlier cohort can differ for reasons other than the intervention:
- case mix
- measurement practice
- background treatment
- technology
- selection
- time trend

Historical controls can be informative but are not exchangeable by default.

## Attrition and informative censoring

Loss to follow-up or excluded observations can bias estimates when dropout relates to treatment, exposure, prognosis, outcome, or measurement success.

Check:
- starting n
- analyzed n
- reasons for loss/exclusion
- whether attrition differs across groups
- whether analysis assumes censoring is non-informative

## Survivorship and selection bias

Conditioning on cases that remain observable can distort conclusions.

Examples:
- only successful firms
- only surviving devices
- only patients reaching follow-up
- only valid sensor periods
- only papers or datasets with complete records

The observed population may not represent the population that entered the process.

## Case-control sampling

Case-control designs can estimate exposure-outcome association efficiently, but raw case fractions are design-controlled rather than population risk.

Odds ratios may be appropriate; direct risk or prevalence statements require additional information.

## Immortal-time and time-alignment bias

If membership in an exposed group requires surviving event-free long enough to receive or qualify for the exposure, the pre-exposure "immortal" time can bias comparisons.

More generally, align:
- time zero
- eligibility
- exposure assignment
- start of follow-up
- outcome risk window

Misaligned clocks can create artificial treatment advantages or disadvantages.

## Crossover and repeated-period designs

Check:
- washout
- carryover
- period effects
- treatment order
- whether repeated measurements are analyzed as paired/dependent

A crossover design is not automatically self-controlling if carryover remains plausible.

## Clustered and multi-site designs

Site, class, laboratory, hospital, batch, market, or geographic cluster can introduce shared environment and treatment implementation.

Check whether:
- assignment occurred at cluster level
- analysis accounts for cluster dependence
- one unusual site drives the result
- site and treatment are confounded

## Difference-in-differences and interrupted time series

For difference-in-differences, the key identifying assumption concerns the counterfactual trend, not merely the existence of pre/post data.

Look for:
- pre-trend evidence
- anticipatory effects
- concurrent shocks
- composition changes

For interrupted time series, distinguish an immediate level/slope change from background autocorrelation and pre-existing trend.

## Regression discontinuity

Check:
- whether treatment assignment truly changes at the cutoff
- manipulation or sorting around the threshold
- bandwidth sensitivity
- continuity of relevant covariates
- local nature of the estimand

A local discontinuity does not automatically generalize far from the threshold.

## Instrumental-variable and natural-experiment designs

An instrument must do more than correlate with exposure.

The causal interpretation depends on assumptions such as:
- relevance
- exclusion of direct pathways to outcome
- appropriate independence/exogeneity
- interpretation of the affected population

Do not certify these assumptions from statistical strength alone.

## Mediation design

Mechanistic mediation requires temporal and causal structure stronger than showing:
- exposure associates with mediator
- mediator associates with outcome

Adjustment-based mediation can fail under unmeasured mediator-outcome confounding or when mediator and outcome timing are unclear.

## Benchmark and ML design

Check:
- train/validation/test separation
- hyperparameter or prompt tuning on the test set
- leakage through preprocessing, duplicates, near-duplicates, metadata, or benchmark construction
- repeated seed/configuration selection
- benchmark contamination from training data when relevant and evidenced
- whether the evaluation distribution matches the generality claim

A held-out split is only independent if information from it did not materially guide model or method selection.

## Temporal leakage

Predictors must be available at the stated prediction time.

Future information, post-outcome variables, revised records, or target-derived features can inflate predictive performance without supporting deployable forecasting.

## Ecological and individual-level inference

Group-level associations do not automatically establish individual-level relationships, and individual-level effects do not automatically aggregate to group/system behavior.

Keep the inferential level aligned with the data-generating unit.

## Usage rule

Evaluate the design relative to the claim actually made. An observational design can strongly support description and prediction while remaining weak for a causal claim. Do not downgrade useful local results merely because a stronger design would be needed for a broader conclusion.
