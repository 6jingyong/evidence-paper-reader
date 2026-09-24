# Evidence dependence and triangulation

Use this reference after identifying evidence type, provenance, and topology.

The purpose is to prevent evidence counting from being mistaken for evidence independence. Five figures can still represent one underlying evidence unit; two different methods can still share the same sample; two genuinely separate cohorts can provide stronger convergence than many re-analyses of one dataset.

## Evidence unit

An **evidence unit** is one materially distinct data-generating or source-generating basis for a claim.

Examples:
- one randomized cohort
- one independently collected survey wave
- one experimental preparation or biological system
- one benchmark dataset/task family
- one market dataset and period
- one field deployment
- one archival collection
- one independently acquired replication dataset

A figure, table, statistical model, transformed endpoint, or re-analysis is not automatically a new evidence unit.

## Controlled dependence classes

Use exactly one of these labels for each core claim.

### single-source
The claim is supported mainly by one evidence unit or one analytic chain.

Examples:
- one RCT cohort with one primary comparison
- one benchmark result on one dataset
- one material characterization series from one specimen set

### shared-source convergence
Multiple readouts, analyses, outcomes, figures, or modalities point in the same direction, but they share the same underlying sample, participants, specimen set, raw dataset, intervention, or other dominant source of error.

Examples:
- severity and duration outcomes from the same randomized patients
- several regression specifications on the same survey wave
- two fMRI contrasts from the same participants
- hardness, strength, and phase measurements from the same alloy batches

Interpretation:
- This is corroboration, but not independent replication.
- Do not multiply confidence simply because several correlated endpoints agree.

### partially independent convergence
The claim is supported by evidence units that differ in an important way but still share material upstream dependencies.

Examples:
- the same biological system tested with pharmacologic and genetic perturbations
- the same method tested on separate benchmark datasets
- separate monitoring stations during the same field period
- multiple assets or subperiods drawn from one market regime
- human and model judgments on the same selected benchmark items

Interpretation:
- Stronger than repeated analyses of one source.
- Still vulnerable to shared design, sampling, preprocessing, environment, or construct assumptions.

### independent convergence
Two or more materially independent evidence units support the same claim with substantially separate sampling or error structures.

Typical requirements:
- independently recruited cohorts or independently collected datasets
- separate experimental replications or sites rather than technical repeats
- no shared calibration target or selection criterion that mechanically enforces agreement
- the claim is actually tested in each unit rather than inferred by analogy

Interpretation:
- Independent convergence can materially strengthen support.
- Do not use this label merely because evidence types differ.

### unclear
The paper does not report enough information to determine whether apparently multiple supports are independent.

Use this rather than guessing.

## Dependence graph

When a claim has multiple supports, reason as a small graph:

- **nodes**: candidate evidence units
- **edges**: shared participants, specimens, raw data, field conditions, preprocessing, labels, calibration targets, judges, inclusion filters, intervention batches, code paths, or citation sources

The denser and more consequential the shared edges, the less independent the apparent convergence.

You do not need to print the graph unless useful. The output field should summarize it with one controlled dependence label and a short explanation in the reason.

## Replication versus technical repetition

Do not call these independent replication:
- repeated measurements on the same specimen
- multiple technical assay wells from the same biological preparation
- multiple outcomes from the same participants
- many bootstrap samples from one dataset
- repeated random seeds on the same benchmark split
- multiple regression specifications on the same records
- several figures derived from the same underlying experiment

They can improve precision or robustness but do not create a new independent evidence unit.

## Triangulation

Different evidence types can provide useful triangulation when their failure modes differ.

Examples:
- intervention + observational measurement
- structural characterization + mechanical property test
- survey + administrative record
- benchmark + independent human evaluation

However, different evidence types are not automatically independent. If they share the same subjects, specimens, data-generation process, or target construction, classify the dependence accordingly.

## Support-strength rule

Do not compute support level from a count of evidence items.

Instead ask:
1. How direct is each evidence unit for the claim?
2. How independent are their main failure modes?
3. Do they actually converge on the same claim?
4. Does one evidence unit carry most of the support while the others are derivative?
5. Would the claim materially weaken if the dominant evidence unit failed?

Independent convergence can justify stronger support than one source alone, but a large number of shared-source analyses should not be treated as equivalent to independent replication.

## External citations

Multiple citations are not multiple verified evidence units unless their contents are actually inspected.

A literature review paragraph that cites five papers remains external-citation provenance. Do not infer independence, replication quality, or convergence from citation count alone.

## Usage rule

Use dependence labels descriptively, not as scores. They explain why apparently abundant evidence should or should not increase confidence; they do not replace the claim-specific support judgment.
