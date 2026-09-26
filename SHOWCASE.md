# Evidence Paper Reader — Showcase

Most paper readers summarize what a source says. **Evidence Paper Reader asks how far the disclosed evidence actually lets you say it.**

The examples below are not hand-written demos. Each one has a source-backed audit record in the repository with a structured ledger, claim-local evidence relations, reasoning edges, author-boundary metadata, routed checks, and a replayable final gate.

Current evidence base: **30 source-backed records**, **18 benchmark-only named sources**, **24 legacy regression fixtures**, **72 unique evidence identities**.

> The goal is not to "catch bad papers." The goal is to preserve the boundary between **what was measured**, **what was inferred**, and **what remains uncertain** — including when the authors already acknowledge that boundary themselves.

---

## 1. Deep Limit Order Book Forecasting — forecast score is not tradeability

**What the source directly supports**

Across 15 NASDAQ stocks, predictability varied strongly with microstructure, and some large-tick settings achieved strong F1/MCC results. The paper also introduced a complete-transaction metric (`pT`) and showed that conventional forecast scores could remain moderate or high while transaction-level correctness was very low.

**Missing bridge**

A model that predicts the next market-state label well is not automatically an actionable trading strategy. Live execution still depends on costs, queue position, slippage, latency, order placement, venue effects, and strategy rules.

**Authors acknowledge**

**Explicit.** The paper itself separates conventional forecast scores from transaction practicality, shows that high F1 can coexist with very low `pT`, and leaves realistic trading/execution use as a further problem.

**Reader takeaway**

The forecasting result is useful. The trading conclusion is a different endpoint.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-04/deep-lob-forecasting-2024/)

---

## 2. Echinacea for the common cold — favorable point estimates are not a demonstrated treatment effect

**What the source directly supports**

The blinded comparison reported a 28-point lower mean severity score and a 0.53-day shorter mean illness duration for echinacea versus placebo.

**Missing bridge**

Both confidence intervals included no benefit, and the prespecified blinded comparisons did not establish a substantive treatment effect.

**Authors acknowledge**

**Explicit.** The authors themselves conclude that illness duration and overall severity were not significantly reduced and describe only trends toward benefit.

**Reader takeaway**

The point estimates are real results. "This formulation substantively changes the course of the cold" is not established by those estimates.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-01/echinacea-2010/)

---

## 3. BESMILE-HF — feasibility is not clinical efficacy

**What the source directly supports**

In an 18-participant pilot, the intervention was feasible, adherence was good, no intervention-related adverse events were captured, and self-efficacy improved more than control at six weeks.

**Missing bridge**

The between-group exercise-capacity result was not statistically significant, its confidence interval included zero, and the pilot was not powered to establish clinical efficacy.

**Authors acknowledge**

**Explicit.** The authors describe the study as a small pilot, state that the exercise-capacity comparison was not definitive, and call for a larger trial with longer follow-up before clinical efficacy is concluded.

**Reader takeaway**

A pilot can support feasibility and a psychological outcome signal without supporting a clinical-benefit claim.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-03/besmile-hf-2021/)

---

## 4. Photochemical SEI for fast charging — strong result, broader mechanism

**What the source directly supports**

A graphite full cell using the photo-SEI reached 80% state of charge in 10.8 minutes at 2.6 mAh cm−2. The treated interface was more inorganic/LiF-rich and showed about tenfold lower interfacial ionic-transport resistance than the comparison.

**Missing bridge**

Those correlated changes do not uniquely isolate LiF-rich chemistry as the sole causal mechanism, and a successful laboratory treatment is not yet a demonstrated manufacturing route across other electrodes.

**Authors acknowledge**

**Partial.** The authors state that γ-ray processing is not directly adoptable in current LIB manufacturing and present applicability to other electrodes as future work. That acknowledges the transfer/manufacturing boundary, but not the full unique-mechanism concern.

**Reader takeaway**

The fast-charge result is strong. The mechanism and transfer claims need a wider evidentiary bridge.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-04/photochemical-sei-fast-charge-2021/)

---

## 5. Tropical alpine warming experiment — observed community change is not an observed shrub transition

**What the source directly supports**

The seven-year OTC experiment changed local microclimate, increased 2019 aboveground biomass, and altered community diversity/evenness. Overall species richness was not significantly reduced after accounting for sampling time.

**Missing bridge**

The experiment observed tussock and diversity changes. It did not observe a completed transition to a shrub-dominated ecosystem.

**Authors acknowledge**

**Explicit.** The authors present shrub dominance as a possible future step and explicitly call for further research on long-term growth-form transitions.

**Reader takeaway**

The projection may be plausible. It should remain a projection.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-04/microclimatic-warming-paramo-2021/)

---

## 6. BERT — broad benchmark success is not the whole construct of "language understanding"

**What the source directly supports**

BERT reported strong contemporaneous results across eleven NLP tasks, including GLUE, MultiNLI, SQuAD v1.1, and SQuAD v2.0.

**Missing bridge**

A diverse benchmark suite is still a finite set of operational tasks and metrics. Moving from benchmark breadth to the broader construct of "language understanding" is a proxy-to-construct inference.

**Authors acknowledge**

**Unclear in this audit.** The audit does not claim that the authors explicitly concede the same construct-validity boundary.

**Reader takeaway**

The benchmark evidence remains strong even when the broader construct claim is kept separate.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-04/bert-2019/)

---

## 7. QuantumFlow order-book imbalance — a technical blog can still contain usable evidence

**What the source directly supports**

Across five Binance perpetual markets, bid-heavy books were followed by higher prices more often than ask-heavy books. For BTC, the extreme-decile hit-rate spread was reported as 9.43 percentage points with a day-block bootstrap interval of 7.1 to 11.9 points.

The same article also reported only about 0.35 basis points of average gross return for the most bid-heavy BTC decile before fees.

**Missing bridge**

There is no need to downgrade the directional association merely because the source is a blog. But directional predictiveness still does not imply a profitable taker strategy.

**Authors acknowledge**

For the tradeability point, the source itself makes the negative boundary: gross return is too small relative to the cited taker-fee scale.

**Reader takeaway**

Prestige is not the audit target. A non-paper source can support a narrow claim well — and a negative conclusion can be fully supported too.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-03/order-book-imbalance-quantumflow-2026/)

---

## 8. Surgisphere hydroxychloroquine registry — visible statistics are not enough when the evidence substrate is no longer inspectable

**What the source presents**

The article reported a large multinational observational analysis with detailed tables and regression outputs.

**Why the normal claim audit stops**

The central dataset later became unavailable for independent audit, and the paper was retracted after documented concerns about data provenance and verifiability. Because every headline estimate depends on that substrate, visible tables alone do not reconstruct a trustworthy evidence chain.

**What this does *not* mean**

Evidence Paper Reader does **not** independently declare fabrication, misconduct, deception, or author intent. The narrower judgment is: the central evidence substrate cannot now carry the claimed estimates as an inspectable source-backed chain.

**Reader takeaway**

`non-auditable` is an evidence-usability state, not a misconduct verdict.

[Source-backed audit](validation-runs/real-papers/2026-09-26-round-02/surgisphere-hcq-2020/)

---

## What the output is trying to preserve

A good audit should let a reader distinguish:

1. **what the source directly shows**
2. **what logical bridge is needed to reach the broader claim**
3. **whether that bridge is supported, qualified, unsupported, or unclear**
4. **whether the authors themselves acknowledge the same boundary**
5. **what remains usable even when a broader claim is downweighted**

Author acknowledgment never repairs missing evidence. It changes the fairness of the explanation: if the authors already say "this still needs external validation," the audit should preserve that rather than presenting the limitation as an adversarial discovery.

## Verify the evidence base

- [Evidence registry](EVIDENCE.md)
- [Core skill](evidence-paper-reader/SKILL.md)
- [Core contract](evidence-paper-reader/references/core-contract.md)
- [Reasoning graph contract](evidence-paper-reader/references/reasoning-graph.md)
- [Evidence-relations contract](evidence-paper-reader/references/evidence-relations.md)
- [CI contract tests](.github/workflows/contract-tests.yml)
