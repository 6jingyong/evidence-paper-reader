# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- evidence viability: auditable
- viability flags: none
- paper type: uncontrolled before-after health-services evaluation

The paper documents a substantial decline in hospital use after enrollment in an integrated care-coordination service and converts those changes into large estimated savings. Those observed pre/post differences are real administrative-record findings, but causal attribution to the service is much weaker because there is no concurrent control group and clients are selected from an unusually high-utilization population. Regression to the mean, changing health status, secular trends, and selection can therefore generate part of the apparent reduction even if the service has no causal effect. The paper itself acknowledges the lack of a control group, which is an important limitation, but its strong cost-effectiveness conclusion still exceeds what the before-after design uniquely identifies. The paper is mainly useful as an adversarial design example showing how a large, economically impressive effect can remain causally uncertain.

## 2. core claims

### claim 1
- content: Hospital bed-days and A&E attendances were lower after clients entered the care-coordination service than in the preceding observation period.
- claim type: observational
- conclusion strength: medium

### claim 2
- content: The care-coordination service prevented approximately 14 to 29 hospital bed-days per client per year and several A&E attendances.
- claim type: intervention
- conclusion strength: strong

### claim 3
- content: The service is highly cost-effective because the observed reduction in utilization was caused by the intervention.
- claim type: intervention
- conclusion strength: strong

### claim 4
- content: Corroborating information is sufficient to remove the main causal uncertainty created by the absence of a control group.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: administrative or transactional record + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: Abstract and evaluation results; hospital stays and A&E use tracked before and after entry into the service
- support level: sufficient
- reason: The administrative utilization records directly support a within-client decline after enrollment. This descriptive result does not require a causal counterfactual.
- external dependency: none

### claim 2
- evidence type: administrative or transactional record + statistical analysis + author interpretation
- evidence provenance: paper-local
- evidence nodes: E1 + E2 + E3
- upstream claims: C1
- evidence dependence: shared-source convergence
- source location: Abstract and Conclusions; reported 14-29 saved bed-days per client per year and fewer A&E attendances
- support level: partial
- reason: The numerical savings calculation is built from observed pre/post utilization, but the word "prevented" is causal. High-utilization clients can naturally move toward lower utilization on repeat observation, and no concurrent control estimates what would have happened without the program.
- external dependency: none

### claim 3
- evidence type: administrative or transactional record + statistical analysis + author interpretation
- evidence provenance: paper-local
- evidence nodes: E1 + E2 + E3 + E4
- upstream claims: C1 + C2
- evidence dependence: shared-source convergence
- source location: Conclusions and cost-effectiveness calculations
- support level: partial
- reason: The accounting can show that the program would be cost-effective if the utilization reduction were caused by the service. The design cannot uniquely identify that causal counterfactual, so cost-effectiveness conditional on attribution is stronger than demonstrated causal savings.
- external dependency: none

### claim 4
- evidence type: author interpretation + literature citation
- evidence provenance: mixed
- evidence nodes: E5 + E6
- upstream claims: C2 + C3
- evidence dependence: unclear
- source location: Abstract statement that corroborating independent evidence supports the conclusions
- support level: unclear
- reason: The available paper reports corroborating evidence, but without reconstructing those external comparisons as independent counterfactual evidence, they cannot simply erase regression-to-the-mean and secular-trend concerns from the primary before-after design.
- external dependency: corroborating evidence cited by the paper; each source would need separate inspection to determine whether it supplies an independent counterfactual

## 4. what is usable

### usable results
The observed utilization trajectory, client-level administrative records, reported falls/QoL outcomes, and cost thresholds are useful descriptive inputs.

### usable methods or design
Tracking the same clients before and after service entry is useful for operational monitoring and hypothesis generation.

### usable materials or documentation
The paper exposes enough of its cost assumptions and admits the absence of a control group, making the causal boundary inspectable.

## 5. what to downweight

### worth noticing but should be downweighted
The estimated magnitude of utilization decline is operationally interesting and may justify a better-controlled evaluation.

### should be treated cautiously or ignored
Do not equate pre/post decline with admissions "prevented" by the program. Regression to the mean is especially plausible when enrollment selects people after unusually high recent utilization.

## 6. value breakdown
- result value: medium
- method value: medium
- theory or insight value: low
- research design value: low
- material or documentation value: high

## 7. uncertainty and follow-up
The dominant uncertainty is counterfactual: what would these high-risk clients' utilization have been over the same period without the service? A matched concurrent control, difference-in-differences design, interrupted time series with adequate pre-period data, or another credible counterfactual could materially change the support level for the causal and cost-effectiveness claims.
