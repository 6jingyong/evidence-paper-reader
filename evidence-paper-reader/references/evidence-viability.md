# Evidence viability gate

Run this gate before full claim extraction.

It answers a different question from topical scope:

- **scope**: is this the kind of material Evidence Paper Reader should examine?
- **evidence viability**: does the material expose enough of its evidence chain to be meaningfully audited?

A source can be in scope but non-auditable.

## Controlled labels

Use exactly one:

- `auditable`
- `partially auditable`
- `non-auditable`

### auditable

The central claims can be traced to inspectable methods, observations, measurements, records, derivations, or other evidence.

Missing detail may limit support, but it does not prevent reconstruction of the main evidence chain.

### partially auditable

At least one important claim has a traceable evidence chain, but one or more central claims are blocked by missing methods, missing results, opaque constructs, proprietary dependencies, or inaccessible external evidence.

Audit only what can actually be reconstructed.

Do not invent enough claims merely to reach a quota.

### non-auditable

The central claims cannot be mapped to an inspectable evidence chain from the available material.

Typical cases are evidence-shaped rhetoric: product claims, demonstrations, named frameworks, or technical stories are presented, but the information needed to test the central inference is absent.

For a non-auditable source, do not manufacture a 3–5 claim audit. Sections 2 and 3 may be marked not applicable while sections 4–7 explain what, if anything, remains useful.

## Controlled viability flags

Use `none` only when no decision-critical viability problem exists.

Otherwise use one or more of:

- `critical-method-omission`
- `critical-result-omission`
- `missing-comparator`
- `selective-success-only`
- `self-referential-construct`
- `circular-validation`
- `demo-only`
- `proprietary-black-box`
- `external-dependency-dominant`
- `promotional-asymmetry`
- `source-integrity-failure`

These flags describe evidence structure, not author motive.

## Minimum reconstruction test

For the main claim, ask:

1. What was actually done, observed, measured, derived, or collected?
2. On what units, samples, participants, systems, records, or cases?
3. What quantity or outcome changed?
4. Relative to what baseline, comparator, prior state, or prediction when the claim is comparative?
5. Where is the decision-critical result shown?
6. Can the central construct be operationalized independently of the conclusion?
7. Can a skeptical reader distinguish success cases from selection, cherry-picking, or demonstration-only presentation?
8. Which decisive premises are paper-local and which are external or proprietary?

A source need not answer every question perfectly to be auditable. The gate turns negative only when missing information blocks the central inference.

## Evidence-shaped but non-auditable patterns

### Critical method omission

The article reports a result but omits information needed to know what produced it.

Examples:
- no sample definition
- no test conditions
- no data-generation procedure
- no meaningful description of preprocessing
- no way to distinguish independent observations from repeats

Do not require every reproducibility detail. The omission must matter to the central claim.

### Critical result omission

The article states success without exposing the result needed to judge it.

Examples:
- "improved dramatically" without a value, comparison, or distribution
- screenshots without the underlying measured quantity
- a conclusion that refers to a test whose output is not shown

### Missing comparator

A comparative claim such as "faster", "more accurate", "safer", "higher efficiency", or "better" is made without a meaningful baseline or comparator.

Absence of a comparator is not fatal to a purely descriptive claim.

### Selective-success-only presentation

Only favorable demonstrations, best runs, selected customers, selected images, or successful cases are shown while the selection rule and failure rate are unavailable.

This differs from ordinary small-n evidence: the problem is that the denominator or selection process cannot be reconstructed.

### Self-referential construct

A new term is introduced and its evidence is defined in terms of the same term or an author-created proxy without an independent anchor.

Example structure:

`X-ness = high X-score`

`the system has high X-score`

`therefore the system exhibits X-ness`

This establishes the operational score by definition, not the broader construct.

New terminology is not a problem by itself. A new construct can be auditable when its operationalization is explicit and connected to independent observations or predictions.

### Circular validation

The target used to define, tune, label, or select the method is reused as the decisive validation target, and no independent criterion is supplied.

This overlaps with non-independent validation but becomes a viability problem when there is no separable test left to audit.

### Demo-only evidence

A demonstration proves that something can occur in one shown instance but is narrated as if it establishes frequency, reliability, comparative performance, or generality.

A demo can still support a narrow existence claim.

### Proprietary black box

A decisive input, metric, labeling process, benchmark, or analysis is proprietary or unavailable, so the central claim cannot be reconstructed.

Commercial or proprietary work is not automatically non-auditable. Judge only the blocked part.

### External-dependency dominant

The source's central conclusion is mostly a retelling or synthesis of claims from external sources that are not inspected, with little independent paper-local evidence.

This can still have documentation or conceptual value.

### Source integrity failure

The central evidence depends on records, datasets, measurements, or provenance that can no longer be treated as a trustworthy inspectable substrate because a documented integrity failure blocks verification.

Examples include a retracted paper whose authors or journal state that the underlying data cannot be independently verified, fabricated or materially misdescribed source records, or an unavailable dataset whose provenance is the reason for retraction.

Do not set this flag merely because a paper is controversial, contradicted, corrected, or retracted for a reason that does not undermine the evidence chain. Record the documented integrity problem and its source. When the integrity failure reaches the central evidence substrate, `non-auditable` is appropriate even if the prose, tables, and statistical outputs remain fully visible.

### Promotional asymmetry

The source has a one-sided evidence structure characteristic of promotion:
- benefits are quantified but costs/failures are omitted
- only favorable cases are shown
- comparisons use unnamed or weak baselines
- product-specific terminology substitutes for operational definitions
- calls to adopt/buy/use the system carry more weight than the disclosed evidence

Do not infer advertising intent from tone, company authorship, or brand names alone. Use this flag only for the evidence asymmetry.

## "Meaningless" versus low-value

Do not use `non-auditable` merely because:
- the effect is small
- the sample is small
- the result is negative
- the paper is poorly written
- the venue is weak
- the source is a blog or preprint
- the terminology is unfamiliar
- the work is incremental

A small or boring study can still be perfectly auditable.

The gate is about whether the evidence chain can be reconstructed, not whether the result is exciting.

## Output consequence

- `auditable`: extract 3–5 core claims.
- `partially auditable`: extract 1–5 claims that are actually reconstructable; explicitly leave blocked central claims unresolved.
- `non-auditable`: do not force claim extraction. Mark sections 2 and 3 not applicable and explain the blocking viability flags.

The value breakdown can still preserve useful documentation, methods descriptions, terminology, or inspiration even when result evidence is non-auditable.
