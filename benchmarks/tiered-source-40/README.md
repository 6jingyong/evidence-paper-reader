# Tiered Source 40 Benchmark

This benchmark stress-tests whether Evidence Paper Reader follows the evidence chain rather than source prestige.

## Design

The domain sample is reproducible:

- random seed: `20260924`
- 10 domains selected from a broader cross-domain pool
- 4 source tiers per domain
- 40 cases total

Selected domains:

1. battery materials
2. climate science
3. ecology
4. clinical cardiology
5. human-computer interaction
6. sensor engineering
7. financial market microstructure
8. education
9. catalysis
10. natural language processing

The four source tiers are:

- `flagship_high_attention`: flagship venue and/or clearly high-attention/high-citation source
- `ordinary_a`
- `ordinary_b`
- `low_attention_nontraditional`: low-attention, pilot, preprint, Matters Arising, or technical/community source

The tiers are metadata, **not quality priors**.

Because HCI/NLP are conference-centered and fields have incompatible quartile systems, `flagship_high_attention` is deliberately broader than a literal JCR-Q1 label.

Domains were randomly selected. Papers were stratified/purposively selected inside each domain to satisfy the four-tier design and public-access needs; they were not uniformly sampled from all papers in the field.

## What v1 measures

This is a first-pass source-level screening benchmark, not forty full systematic reviews.

For every source it records:

- scope status
- modules that should trigger
- support for a narrow/direct claim
- support for a broader headline/mechanism/generality claim
- the main evidence boundary

The point is to test whether a low-prestige source can still receive strong support for a well-demonstrated local result, and whether a flagship paper still gets downweighted when its claim reach exceeds its evidence.

## Aggregate result

| Tier | n | Narrow claim | Broad claim | Scope |
| --- | ---: | --- | --- | --- |
| flagship / high attention | 10 | 10 sufficient | 10 partial | 10 in scope |
| ordinary A | 10 | 10 sufficient | 10 partial | 10 in scope |
| ordinary B | 10 | 10 sufficient | 10 partial | 10 in scope |
| low attention / nontraditional | 10 | 5 sufficient, 5 partial | 4 partial, 5 insufficient, 1 unclear | 7 in scope, 3 partially in scope |

Three immediate checks:

- **No flagship halo in the broad-claim column:** 10/10 flagship cases are still downweighted from a narrow direct result to a broader claim.
- **No automatic low-attention penalty:** 5/10 low-attention/nontraditional cases still receive `sufficient` for their bounded direct claim.
- **Low-attention failures are structural:** the weakest broad claims are mostly synthesis-with-external-dependency, tiny-pilot efficacy, real-user generalization from benchmark data, critique dependent on another paper, or community guidance without a single local evidence chain.

This is exactly the intended behavior: source prestige may affect what evidence is available or how much prior scrutiny a work received, but it is not itself an evidence label.

## Ten four-way comparisons

| Domain | Flagship / high attention | Ordinary A | Ordinary B | Low attention / nontraditional |
| --- | --- | --- | --- | --- |
| battery materials | *Ultrahigh power and energy density in partially ordered lithium-ion cathode materials* | *Layered-rocksalt intergrown cathode...* | *Photochemically driven solid electrolyte interphase...* | ChemRxiv: *Dry Electrode Architecture Design...* |
| climate science | *Assessing the observed impact of anthropogenic climate change* | *Anthropogenic climate change has driven over 5 million km2...* | *Attribution of 2020 hurricane season extreme rainfall...* | EarthArXiv: *Surface Infrared Forcing as a Primary Driver...* |
| ecology | *Accelerated modern human-induced species losses...* | *Microclimatic Warming Leads to a Decrease...* | *Impact of round goby on native invertebrate communities...* | *Ecoacoustics as a novel tool...: Results of a pilot study* |
| clinical cardiology | SPRINT | narrative AMI psychoeducation RCT | web-platform hypertension cluster RCT | 18-person BESMILE-HF pilot RCT |
| HCI | *Why Johnny Can't Encrypt* | model-based RL adaptive UI | interface landmarks/spatial memory | arXiv adaptive UI generation/RL |
| sensor engineering | BEACO2N field calibration | SO2/NO2 coastal train/test calibration | low-cost piezoelectric rain sensor | arXiv temporal deep-learning calibration |
| financial microstructure | *The Price Impact of Order Book Events* | queue imbalance one-tick prediction | *Deep Limit Order Book Forecasting* | QuantumFlow order-book-imbalance blog |
| education | Krueger / Project STAR | flipped-learning RCT | preregistered encouragement field experiment | 26-student virtual-learning randomized study |
| catalysis | scalable Cu -> C2+ catalyst | iodide-mediated Cu restructuring | NO oxidation/storage experiment + simulation | Nature Communications Matters Arising with 3 citations |
| NLP | BERT | benchmark-dataset discrimination | StructEval | Hugging Face evaluation blog |

See `cases.json` for exact titles, URLs, tier rationale, scope, trigger modules, and evidence-boundary judgments.

## Illustrative prestige reversals

### Technical blog can beat a strong paper on one narrow question

The QuantumFlow order-book article is not peer reviewed, but it reports a concrete five-market test, non-overlapping hourly observations, a day-level block bootstrap, and explicitly distinguishes directional predictability from trading profitability.

Its bounded directional claim is therefore marked `sufficient`, while the trading-strategy claim is `insufficient`.

The source type is not what determines either judgment.

### Top journal can still be structurally dependent

`Pitfalls in identifying active catalyst species` appears in Nature Communications but is a Matters Arising response to another article.

Its critique may be useful, but strong conclusions about the original active species structurally depend on inspecting the target article and the characterization chain. It is therefore only `partially in scope` in this isolated-source benchmark.

### Pilot study can support feasibility but not efficacy

BESMILE-HF has only 18 participants.

That is enough to make adherence/feasibility observations real and directly inspectable. It is not enough to turn preliminary physiological differences into a stable clinical efficacy claim.

### Preprint status does not force partial support

The dry-electrode ChemRxiv paper and the 2026 air-sensor calibration preprint both contain concrete experimental/evaluation chains. Their narrow tested performance claims can receive `sufficient` in a first-pass audit while broader deployment/generalization claims remain `partial`.

## Important limitation: this is not yet a causal test of prestige bias

The v1 screening pass was not metadata-blinded. Venue/source identity was visible during curation and review.

Therefore the aggregate result can show that the current framework *permits* prestige-independent judgments, but it cannot prove that a model's judgment is unaffected by prestige cues.

A stricter A/B experiment would use matched content packets:

- A: paper content with venue/authors/citation counts hidden
- B: same content with metadata visible
- compare claim selection, support levels, requested follow-up, and language severity

That protocol should be used before making a causal claim about journal-halo bias.

## Files

- `cases.json`: 40 selected sources and first-pass judgments
- `summarize.py`: zero-dependency manifest validator and aggregator

Run:

```bash
python benchmarks/tiered-source-40/summarize.py
python benchmarks/tiered-source-40/summarize.py --json
```
