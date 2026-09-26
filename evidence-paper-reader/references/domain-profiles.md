# Domain profiles

Load only the profile that matches the paper.

These profiles change emphasis, not the output format.

## Experimental natural science / materials / biochemistry

Prioritize:
- independent specimen or biological-unit count
- technical versus biological replication
- measurement/calibration chain
- phase/structure assignment versus direct evidence
- mechanism claims versus observed property changes
- selected/optimal conditions versus ordinary operation
- scale transfer from specimen/cell to broader system

## Machine learning / software / benchmark papers

Use `computational benchmark` for dataset/task evaluations and ablations.

Prioritize:
- train/validation/test separation
- test-set or benchmark leakage
- fair baselines
- ablation interpretation
- model/seed/configuration selection
- benchmark versus real-task generalization
- whether the same judge/target guided optimization and evaluation

Do not relabel a benchmark as `numerical simulation` unless it actually simulates a target system or phenomenon.

## Finance / econometrics / market microstructure

Prioritize:
- mechanical coupling between predictor and price/return/volume/accounting outcomes
- contemporaneous association versus causal language
- one-regime / one-period / selected-asset generalization
- transaction-record construction
- time alignment and leakage
- clustered/time-series dependence

## Clinical / biomedical empirical research

Prioritize:
- randomization, control, blinding, attrition
- primary versus secondary/subgroup outcomes
- effect sizes and intervals, not p-values alone
- non-significance versus equivalence
- per-protocol/complete-case versus randomized population
- biomarker/surrogate versus patient-relevant outcome
- adverse events and treatment tradeoffs

Do not convert the audit into patient-specific treatment advice.

## Quantitative social science / surveys

Prioritize:
- sampling frame and population reach
- cross-sectional association versus causality
- repeated cross-sections versus longitudinal inference
- missing-data and weighting assumptions
- subgroup/interaction interpretation
- survey scale versus broader construct

## Interviews / archives / field notes / content analysis

Prioritize:
- source material versus interpretation
- material selection
- coding procedure and rater dependence
- local case material versus general theory
- whether the main value lies in documentation rather than explanation

## Empirical aesthetics / human-subject arts research

Prioritize:
- operationalization of beauty/preference/meaning/style/creativity
- rating/neural/behavioral proxy versus broader construct
- stimulus-set and cultural generalization
- prior-defined regions/categories/coding
- limited modality-to-universal-aesthetics transfer

## Environmental / sensor / field studies

Prioritize:
- calibration and validation independence
- environmental context transfer
- filtering/valid-data retention
- sensor placement and response conditions
- field-period/site generalization
- model fit versus independent ground truth
