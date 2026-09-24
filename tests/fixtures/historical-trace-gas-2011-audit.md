# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- paper type: controlled environmental field-method evaluation

The paper provides direct controlled-source evidence for the accuracy of VRPM and bLS emission-estimation methods under several source and sensor configurations. The strongest bLS single-source result, about 0.98 ± 0.24 relative accuracy, is useful but explicitly depends on filtering and sensor/source geometry; it should not be read as unconditional field accuracy. The study also contains important negative/configuration evidence: vertical point concentrations can perform poorly, VRPM loses data under unfavorable wind geometry, and adding more paths does not necessarily improve dual-source VRPM performance. The broad conclusion that bLS has significant potential for distributed agricultural systems is plausible but remains a generalization from synthetic sources and limited field conditions. The paper is mainly useful as a method-validation result reference.

## 2. core claims

### claim 1
- content: Under the tested single-source configuration, VRPM estimates have relative accuracy around 1.38 ± 0.28 when the combined valid dataset is used.
- claim type: performance
- conclusion strength: medium

### claim 2
- content: Under stringent filtering and the tested path-integrated configuration, bLS can estimate a single source with relative accuracy around 0.98 ± 0.24.
- claim type: performance
- conclusion strength: medium

### claim 3
- content: bLS is generally accurate and robust for measuring emissions from multi-distributed agricultural sources under ordinary deployment conditions.
- claim type: generality
- conclusion strength: strong

### claim 4
- content: Sensor geometry materially changes performance, with vertical point-concentration configurations performing poorly while multiple horizontal point sensors can approach useful accuracy.
- claim type: methodological
- conclusion strength: medium

## 3. evidence and support

### claim 1
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1
- evidence dependence: single-source
- source location: Results section 3.1.1, Figure 3, and Table 1
- support level: sufficient
- reason: The paper compares estimated emission with known synthetic-source emission and reports the combined relative-accuracy distribution. It also documents that one field date yielded only one valid dataset out of fifteen because of wind geometry.
- external dependency: none

### claim 2
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E2
- evidence dependence: single-source
- source location: bLS single-source results and Table 1
- support level: sufficient
- reason: The reported value directly reflects retained observations after atmospheric-stability and footprint criteria. The claim remains scoped to those filtered conditions rather than all attempted observations.
- external dependency: none

### claim 3
- evidence type: direct experiment + author interpretation
- evidence provenance: paper-local
- evidence nodes: E1 + E2 + E3
- evidence dependence: partially independent convergence
- source location: abstract and conclusion
- support level: partial
- reason: Controlled synthetic-source tests support practical potential, but accuracy depends on filtering, wind geometry, sensor placement, and a limited set of single/dual-source trials. Selection-conditioned evidence from valid or favorable configurations does not establish unconditional performance across agricultural deployments.
- external dependency: none

### claim 4
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E4 + E5
- evidence dependence: partially independent convergence
- source location: point-concentration and dual-source configuration results
- support level: sufficient
- reason: The study directly reports poor relative accuracy below 0.62 for a vertical point-concentration configuration and about 1.08 ± 0.44 for multiple horizontal point sensors, showing that configuration is decision-critical.
- external dependency: none

## 4. what is usable

### usable results
Known-source relative-accuracy measurements for VRPM and bLS across the tested configurations, including unsuccessful configurations and data-retention limitations, are directly reusable.

### usable methods or design
Using synthetic sources with known emission rates provides a strong field-method calibration/validation design because estimated emissions can be compared with controlled truth.

### usable materials or documentation
The paper reports source layouts, sensor configurations, filtering criteria, valid-dataset counts, and accuracy summaries in enough detail to expose when the best results apply.

## 5. what to downweight

### worth noticing but should be downweighted
The conclusion that bLS has strong agricultural potential is reasonable as a forward-looking interpretation, but the demonstrated operating envelope is narrower than real agricultural source/weather diversity.

### should be treated cautiously or ignored
Do not quote 0.98 ± 0.24 as an unconditional bLS field error rate. It is selection-conditioned on specified filtering and configuration, while other configurations in the same paper perform substantially worse.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: medium
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The key unresolved boundary is external validity across weather regimes, complex source geometries, and long operational deployments. Data filtering and geometry-specific validity are central to interpretation. No external cited work is required to identify this conditioning because the current paper reports the filters, attrition, and contrasting configurations directly.
