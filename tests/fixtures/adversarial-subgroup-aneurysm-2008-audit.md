# reader-side paper audit

## 1. reader conclusion
- scope status: partially in scope
- evidence viability: auditable
- viability flags: none
- paper type: randomized-trial subgroup analysis

The randomized parent trial supports a bounded comparison of coiling versus clipping in elderly patients, but the subgroup-specific treatment-choice conclusion is much weaker than the headline wording suggests. The paper reports a non-significant overall difference in independent survival among 278 elderly participants, then reports significant treatment differences inside small aneurysm-location subgroups. Separate significance within subgroups does not by itself establish that treatment effects differ between subgroups; the relevant inferential question is an interaction or heterogeneity comparison. Because the available inspected material does not establish such an interaction analysis for the headline location-specific conclusion, that conclusion should be downweighted. The paper is mainly useful as a subgroup-analysis stress case rather than as stand-alone evidence for location-specific treatment selection.

## 2. core claims

### claim 1
- content: Among the 278 ISAT participants aged 65 years or older, independent survival at one year did not differ significantly overall between endovascular coiling and neurosurgical clipping.
- claim type: intervention
- conclusion strength: medium

### claim 2
- content: In the internal-carotid/posterior-communicating subgroup, coiling produced better one-year independent survival than clipping.
- claim type: intervention
- conclusion strength: medium

### claim 3
- content: In the middle-cerebral-artery subgroup, clipping produced better one-year independent survival than coiling.
- claim type: intervention
- conclusion strength: medium

### claim 4
- content: Aneurysm location identifies elderly patients who should preferentially receive coiling versus clipping.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: abstract Methods and Results; 83/138 coiling versus 78/140 clipping independent at one year, reported as non-significant
- support level: sufficient
- reason: The randomized elderly subgroup directly supports the bounded statement that the overall one-year independence comparison was not statistically significant. This does not imply equivalence between treatments.
- external dependency: none

### claim 2
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E3 + E4
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: abstract Results; internal-carotid/posterior-communicating subgroup, 36/50 coiling versus 26/50 clipping independent at one year, P<0.05
- support level: sufficient
- reason: The subgroup-specific comparison supports a local association between assigned treatment and outcome inside this small subgroup. It does not by itself establish that this subgroup responds differently from other aneurysm-location groups.
- external dependency: none

### claim 3
- evidence type: direct experiment + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E5 + E6
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: abstract Results; middle-cerebral-artery subgroup, 10/22 coiling versus 13/15 clipping independent at one year, P<0.05
- support level: sufficient
- reason: The subgroup-specific comparison supports a local result for the observed MCA subgroup. The small cell counts make the estimate imprecise, and separate subgroup significance is not the same statistical question as treatment-by-location interaction.
- external dependency: none

### claim 4
- evidence type: direct experiment + statistical analysis + literature citation
- evidence provenance: mixed
- evidence nodes: E3 + E4 + E5 + E6 + E7
- upstream claims: C2 + C3
- evidence dependence: shared-source convergence
- source location: abstract Conclusion plus methodological critique of this exact subgroup analysis
- support level: partial
- reason: The location-specific treatment recommendation is built from significant within-location comparisons. A later methodological analysis of this exact example points out that the inferential question is whether treatment effects differ across complementary subgroups, not whether one subgroup reaches P<0.05 and another does not. The available evidence therefore supports the observed subgroup results more strongly than the general treatment-selection rule.
- external dependency: The Problem of Subgroup Analyses: An Example from a Trial on Ruptured Intracranial Aneurysms; used to evaluate the interaction-test issue in this exact analysis

## 4. what is usable

### usable results
The randomized elderly-subgroup outcome counts, overall non-significant comparison, subgroup-specific outcome counts, and epilepsy-frequency result are usable as reported trial observations.

### usable methods or design
The underlying random assignment remains valuable for treatment comparisons within the enrolled elderly population.

### usable materials or documentation
The abstract provides treatment-group denominators and one-year independence counts for the overall elderly subgroup and two aneurysm-location subgroups.

## 5. what to downweight

### worth noticing but should be downweighted
The significant location-specific comparisons are hypothesis-generating evidence that aneurysm location may modify treatment effect.

### should be treated cautiously or ignored
Do not infer treatment-effect heterogeneity merely because treatment is significant in one location-defined subgroup and different or non-significant elsewhere. A direct interaction/heterogeneity test and replication are needed for the stronger location-specific treatment rule.

## 6. value breakdown
- result value: medium
- method value: medium
- theory or insight value: low
- research design value: medium
- material or documentation value: medium

## 7. uncertainty and follow-up
The available inspected original material is strongest at the abstract level, so details of all prespecified subgroup analyses and any interaction modeling are not fully available here. The later methodological paper explicitly analyzes this trial as a subgroup-inference example. The key unresolved question for the strong treatment-by-location conclusion is whether an appropriate interaction analysis was prespecified, performed, and independently corroborated.
