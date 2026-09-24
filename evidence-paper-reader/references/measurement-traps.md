# Measurement and instrument traps

Use this reference when a core claim depends materially on a measured variable, assay, sensor, score, rating, image-derived quantity, instrument, or surrogate endpoint.

The central question is not only whether a value was measured precisely, but whether the measurement actually represents the quantity the claim is about.

## Reliability versus validity

A measure can be highly repeatable yet measure the wrong construct.

Separate:
- repeatability or precision
- calibration accuracy
- construct validity
- external validity of the measurement in the target setting

Low noise does not rescue a systematically biased or conceptually mismatched measure.

## Calibration and drift

Check:
- calibration reference
- calibration range
- whether the target samples lie inside that range
- pre/post calibration
- drift over time
- recalibration frequency
- whether calibration and validation use independent targets

A good calibration curve does not by itself establish accuracy in new matrices, instruments, operators, or environments.

## Limit of detection and quantification

Values near or below LOD/LOQ can be censored, substituted, truncated, or highly uncertain.

Check:
- how non-detects are handled
- whether "zero" means truly absent or merely below detection
- whether group differences depend on values near the detection limit

Replacing all non-detects with zero, LOD/2, or another constant can change distributions and model estimates.

## Saturation, ceiling, and floor effects

An instrument or scale can lose sensitivity near its upper or lower range.

Consequences include:
- compressed group differences
- artificial plateaus
- apparent thresholding
- inability to distinguish strong responders or weak signals

A null difference near a measurement ceiling or floor is not strong evidence of biological or behavioral equivalence.

## Resolution and false precision

Reported decimal places should not imply more information than instrument resolution, calibration, sampling, or model uncertainty supports.

Distinguish display precision from measurement precision.

## Batch, lot, and operator effects

Measurements can shift across:
- reagent lots
- sequencing or assay batches
- instruments
- laboratories
- operators
- imaging sessions
- manufacturing batches
- software/preprocessing versions

Check whether batch is confounded with condition or group.

Normalization can reduce batch differences without proving they are fully removed.

## Specificity and cross-reactivity

An assay signal can respond to multiple analytes, structures, classes, labels, or image features.

Ask whether the measured signal is specific enough for the claimed target.

A biomarker or staining signal should not be treated as a unique mechanism marker unless specificity is supported.

## Measurement error

### Non-differential error
Random error in a predictor often attenuates simple associations, but not universally under complex models.

### Differential error
If measurement quality differs by group, condition, outcome, or exposure, bias can go in less predictable directions.

Do not assume measurement error always makes an effect smaller.

## Derived and composite measures

Composite indices, scores, embeddings, normalized ratios, and derived variables may combine several assumptions.

Check:
- component definitions
- weighting
- missing-component handling
- whether one component dominates the index
- whether the composite is being interpreted as a natural physical or psychological quantity

A composite can be useful operationally without being an intrinsic construct.

## Surrogate endpoints

A surrogate or proxy can respond to an intervention even when the patient-, system-, or user-relevant outcome does not.

Keep:
- biomarker
- intermediate process variable
- surrogate endpoint
- final outcome
separate in the claim chain.

## Image-derived measurements

For segmentation, microscopy, imaging, remote sensing, or computer vision measurements, inspect:
- thresholding/segmentation rule
- field or region selection
- scale calibration
- preprocessing
- whether acquisition settings are comparable
- whether multiple crops from one source are treated as independent

A larger number of image patches does not necessarily increase the number of independent biological or physical samples.

## Sensor and environmental context

Sensor response can depend on:
- temperature
- humidity
- flow
- pressure
- matrix composition
- interference
- placement
- warm-up or response time

A calibration established under one context may not transfer unchanged to another.

## Inter-rater and coding measurements

For ratings, labels, coding, or qualitative classification:
- identify who generated the labels
- whether raters were blinded to relevant conditions
- whether agreement was assessed
- whether disagreements were resolved by a rule or by discussion
- whether the same coder developed and applied the codebook

High inter-rater agreement supports consistency, not necessarily validity of the category system.

## Preprocessing dependence

Background subtraction, baseline correction, smoothing, normalization, filtering, imputation, and feature extraction can materially define the measurement.

Ask whether the result is robust to reasonable preprocessing alternatives when the preprocessing choice is decision-critical.

## Usage rule

Use measurement knowledge to bound what the observed value can establish. Do not replace paper-local calibration or validation evidence with generic expectations about how an instrument "usually" behaves.
