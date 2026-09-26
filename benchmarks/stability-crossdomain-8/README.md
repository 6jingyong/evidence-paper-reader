# Cross-Domain Stability 8

This benchmark measures repeated-run stability, not just one-shot correctness.

## Papers and domains

Eight real-paper cases are selected to stress different parts of the skill:

1. clinical cardiology — SPRINT
2. materials science — Al-content high-entropy alloy
3. machine learning — ResNet
4. environmental modeling — air-quality measurement + CFD
5. social science — adolescent screen/social-media survey
6. financial market microstructure — order-book-event price impact
7. ecology — round-goby field experiment
8. electrocatalysis — scalable Cu catalyst for C2+ CO2 reduction

Each case is reviewed **5 times in isolated fresh contexts**, giving 40 runs.

## Why fixed compact packets

The goal is to measure execution stability rather than retrieval noise from websites/PDF parsers.

Each packet therefore contains:

- source identity
- compact paper-local evidence facts
- five candidate claims

The reviewer must still decide:

- evidence viability
- which claims belong in the audit
- which methodology modules are required
- whether the compact packet incorrectly triggers evidence inventory
- support level for every selected claim

## Stability versus correctness

These are deliberately separate.

A model can be:

- stable and correct
- stable and wrong
- unstable but correct on average
- unstable and wrong

### Stability metrics

Per case and then averaged across cases:

- viability pairwise exact agreement
- claim-selection pairwise Jaccard
- routing pairwise Jaccard
- inventory pairwise exact agreement (negative-control diagnostic only)
- support-vector pairwise exact agreement

For support, omission is treated as `not_selected`, so unstable claim selection propagates into the support-stability metric rather than disappearing.

### Reference metrics

- viability accuracy
- required-claim recall
- forbidden-claim selection rate
- required-module recall
- unallowed-module rate
- inventory over-trigger rate (all compact packets are intentionally negative controls)
- support accuracy

Reference expectations are internal benchmark metadata and must not be shown to the reviewing model.

## Generate the 40-job run matrix

```bash
python benchmarks/stability-crossdomain-8/generate_runs.py
```

This creates 40 anonymous packet files and a deterministically shuffled `run_matrix.json`.

Every packet must be run in a fresh context with the same model, effort/configuration, skill version, and response format.

## Score

Store each response as `<packet_id>.json`, then run:

```bash
python benchmarks/stability-crossdomain-8/score_repeats.py responses/
python benchmarks/stability-crossdomain-8/score_repeats.py responses/ --json
```

The most useful output is not a single score. It is the layer profile:

```text
viability      1.00
claim selection 0.88
routing         0.73
support         0.81
```

That profile tells us where to improve the skill.

## Execution isolation

Do not run repeated reviews inside a conversation that has already seen:

- the reference block in `case_specs.json`
- earlier responses for the same case
- scorer output for the same model/configuration

The current development conversation knows the references and therefore cannot provide a valid repeated-run result.

A Work/Codex/agent runner that launches isolated sessions is the intended execution environment.

## Interpretation

If viability is stable but claim selection drifts, improve the claim-selection stage.

If claim selection is stable but routing drifts, tighten semantic-router instructions or module boundaries.

Inventory is intentionally not included in the aggregate stability layers because these compact packets do not provide positive inventory coverage. Positive inventory routing is tested separately by the adversarial router benchmark (for example RA10) and the inventory fixtures.

If routing is stable but support drifts, the evidence contracts/support semantics need stronger anchors.

If support is stable but systematically wrong, more methodological knowledge or better evidence packets are needed.

If only one domain is unstable, prefer a targeted domain/profile fix over expanding global prompts.
