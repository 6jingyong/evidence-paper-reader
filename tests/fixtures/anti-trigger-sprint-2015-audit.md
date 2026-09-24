# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- paper type: randomized controlled clinical trial with prespecified subgroup and interim analyses

The trial directly supports lower rates of its primary cardiovascular composite outcome under intensive systolic-blood-pressure treatment in the enrolled high-risk population without diabetes, while also showing higher rates of several treatment-related adverse events. The presence of multiple prespecified subgroup analyses and repeated interim looks should not be treated as automatic p-hacking or optional stopping: subgroup heterogeneity was assessed with interaction tests using Hommel-adjusted p-values, and interim monitoring used a prespecified Lan-DeMets group-sequential design with O'Brien-Fleming-type boundaries. Those safeguards do not make every secondary result equally confirmatory, but they directly address the specific false-positive risks they were designed for. The paper is mainly useful as a strong intervention result and as an anti-trigger example for subgroup and sequential-analysis skepticism.

## 2. core claims

### claim 1
- content: Intensive systolic-blood-pressure treatment reduced the trial's primary composite cardiovascular outcome relative to standard treatment in the enrolled population.
- claim type: intervention
- conclusion strength: medium

### claim 2
- content: Intensive treatment reduced all-cause mortality relative to standard treatment during the trial follow-up.
- claim type: intervention
- conclusion strength: medium

### claim 3
- content: The trial found no convincing evidence that the primary treatment effect differed across its prespecified subgroups.
- claim type: observational
- conclusion strength: medium

### claim 4
- content: The trial's subgroup and early-stopping structure makes its primary treatment result intrinsically unreliable because of multiplicity and optional stopping.
- claim type: methodological
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: Results and primary outcome table; 1.65% per year versus 2.19% per year, hazard ratio 0.75 with 95% CI 0.64-0.89
- support level: sufficient
- reason: Random assignment and the prespecified primary time-to-event analysis directly support a lower primary-event rate under the intensive strategy in this population. The trial was stopped according to a planned sequential-monitoring framework rather than an unstructured favorable-data peek.
- external dependency: none

### claim 2
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E3 + E4
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: Results and mortality outcome table; all-cause mortality hazard ratio 0.73 with 95% CI 0.60-0.90
- support level: sufficient
- reason: The randomized comparison directly supports lower all-cause mortality during the observed follow-up. This remains a trial-population result rather than a universal blood-pressure target claim.
- external dependency: none

### claim 3
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E5 + E6 + E7
- upstream claims: C1
- evidence dependence: shared-source convergence
- source location: Statistical Analysis and subgroup results; prespecified subgroups assessed with likelihood-ratio interaction tests and Hommel-adjusted p-values
- support level: sufficient
- reason: The paper asks the correct heterogeneity question with interaction tests rather than inferring heterogeneity from separate subgroup significance. Multiplicity adjustment further addresses the family of prespecified subgroup tests. "No detected heterogeneity" is supported; exact equality of treatment effects is not claimed.
- external dependency: none

### claim 4
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E5 + E8
- upstream claims: C1 + C3
- evidence dependence: shared-source convergence
- source location: Statistical Analysis; Hommel-adjusted subgroup interactions and Lan-DeMets interim monitoring with O'Brien-Fleming-type spending
- support level: insufficient
- reason: Multiple subgroup analyses and interim looks are risk cues, but the trial explicitly used methods designed to control those error rates. Their presence alone therefore does not justify downgrading the primary randomized result as p-hacked or optionally stopped.
- external dependency: none

## 4. what is usable

### usable results
The primary composite outcome, mortality estimate, adverse-event profile, and prespecified interaction analyses are directly usable within the trial population.

### usable methods or design
Randomization, intention-to-treat analysis, multiplicity-adjusted subgroup interaction tests, and prespecified group-sequential monitoring are useful examples of explicit mitigation rather than reasons for automatic skepticism.

### usable materials or documentation
The paper reports group sizes, event rates, hazard ratios, confidence intervals, subgroup definitions, interim-monitoring framework, and important adverse events.

## 5. what to downweight

### worth noticing but should be downweighted
Secondary outcomes not protected by the same multiplicity structure should be interpreted according to their own prespecification and uncertainty rather than borrowing confirmatory status from the primary endpoint.

### should be treated cautiously or ignored
Do not label the study "p-hacked" merely because it contains several subgroup analyses or stopped early. Those specific risks were governed by explicit inferential procedures.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: medium
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The trial population excluded diabetes and several other groups, so treatment-target generalization remains bounded. Early stopping can change the amount of long-term information available even when the stopping rule is valid. The key anti-trigger lesson is narrower: prespecified interaction testing, multiplicity adjustment, and group-sequential monitoring should receive evidentiary credit rather than being treated as if the safeguards were absent.
