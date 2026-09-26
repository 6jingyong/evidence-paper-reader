# Evidence topology

Use this reference when the evidence labels themselves look correct but the way evidence is connected to the claim may inflate support.

The question is not only "what evidence type is this?" but also "what structural relationship exists between the evidence, variable construction, analysis population, and conclusion?"

## 1. Mechanical coupling

A predictor or explanatory variable may partly contain the outcome, a direct outcome-changing event, or another mechanically linked quantity.

Check:
- Does the predictor definition include events that directly change the outcome?
- Are exposure and outcome computed from overlapping ingredients?
- Would a strong relationship remain if the mechanically linked component were removed?
- Does the paper perform such a decoupled robustness test?

Interpretation:
- A mechanically coupled model may still be useful for prediction or description.
- Raw fit statistics should not be read as fully independent explanatory or causal evidence.
- If a decoupled specification remains strong, report that separately; it is stronger evidence than the coupled fit.

## 2. Validation independence

Calibration, tuning, model selection, prompt selection, threshold choice, or judge optimization can reuse the same target later presented as validation.

Check:
- Was the reported evaluation target used during fitting or selection?
- Is there a genuinely held-out target, instrument, dataset, annotator, station, or time period?
- Is post-fit agreement being narrated as external accuracy?

Interpretation:
- Agreement with the fitting target supports successful fitting.
- Independent accuracy/generalization requires evidence that was not used to optimize the method.

## 3. Selection-conditioned evidence

Reported evidence may apply only after filtering, attrition, complete-case restriction, validity thresholds, favorable configuration choice, or selection of an optimum.

Check:
- What was the starting denominator and what remained?
- Why were observations/configurations excluded?
- Is the reported result an average over all attempts or only valid/retained cases?
- Are "best", "up to", or "optimal" results being generalized to ordinary operation?

Interpretation:
- Keep the claim scoped to the retained subset or condition.
- Selection is not automatically a flaw; physically or methodologically justified filters can be necessary.
- The error is silently changing the target population/configuration after selection.

## 4. Null-result boundary

A non-significant difference is not the same as evidence of equivalence or absence of a meaningful effect.

Check:
- What effect sizes remain inside the confidence or credible interval?
- Was the study designed for equivalence or non-inferiority?
- Is there a pre-specified meaningful-effect margin?
- Was precision or power adequate for the stronger "no meaningful effect" claim?

Interpretation:
- "No statistically detected difference" can be supported when the test is non-significant.
- "No effect", "equivalent", "safe", or "clinically irrelevant" requires tighter evidence.

## 5. Proxy-to-construct boundary

Papers often operationalize an abstract construct with a rating, biomarker, neural signal, benchmark, survey scale, coded category, or surrogate endpoint.

Check:
- What exactly was measured?
- What broader construct does the paper say the measure represents?
- Is the operationalization validated for the scope being claimed?
- Could other dimensions of the construct vary independently of the proxy?

Interpretation:
- Strong evidence about a proxy supports a claim about that proxy.
- It does not automatically establish that the proxy is identical to or exhaustive of the broader construct.

## 6. Internal consistency

The same claim may be restated differently across abstract, results, tables/figures, discussion, and conclusion.

Check:
- Do numerical trends match summary language?
- Do phase/category labels stay consistent?
- Does the conclusion add mechanism or causality absent from the results?
- Does the sample denominator drift across sections?

Interpretation:
- Prefer the most direct, precisely located paper-local evidence for the bounded result.
- Surface the contradiction instead of silently choosing the favorable version.

## 7. Imported mechanism or theory

A paper may directly establish a result but obtain its mechanism, interpretation, baseline fact, or theoretical bridge from prior literature.

Check:
- Would the current-paper claim still stand if the cited mechanism were unknown?
- Which link is demonstrated locally and which is imported?
- Is the cited work available to inspect?

Interpretation:
- Use evidence provenance 'mixed' or 'external citation' where appropriate.
- Do not convert cited support into paper-local evidence.

## 8. Scale and domain transfer

Evidence may move across levels: cell to organism, synthetic source to field deployment, benchmark to real task, selected assets to markets, two art modalities to aesthetics in general.

Check:
- What is the demonstrated population, scale, modality, environment, or regime?
- What changes when the claim moves to the broader target?
- Is there direct transfer evidence or only analogy/interpretation?

Interpretation:
- A local result can be strong while the transfer claim remains partial or insufficient.
- Do not lower confidence in the local result merely because generalization is weak; separate the two claims.

## Usage rule

Do not attach topology labels mechanically. First state the concrete structural problem in plain language, then use the corresponding pollution-pattern label if it helps keep the audit concise.
