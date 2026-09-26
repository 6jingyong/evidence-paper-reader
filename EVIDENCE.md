# Evidence base

This page is generated from repository artifacts. It records what the project has actually tested rather than a hand-maintained promotional count.

## Current coverage

- source-backed recorded papers: **10**
- legacy regression fixtures: **24**
- total evidence entries: **34**
- source-backed papers prepared for isolated blind re-audit: **10**

Source-backed entries have stable source identity plus replayable audit artifacts. Legacy fixtures are preserved regression evidence with incomplete historical source/run metadata and are not presented as equally reproducible.

## Source-backed papers

| Paper | Domain | Viability | Support vector | Test surfaces | Evidence path |
| --- | --- | --- | --- | --- | --- |
| Exploring digital image correlation technique for the analysis of the tensile properties of all-cellulose composites (2021) | materials-measurement | auditable | sufficient / sufficient / partial | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/acc-dic-2021 |
| Attention Is All You Need (2017) | machine-learning | auditable | sufficient / sufficient / partial | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/attention-is-all-you-need-2017 |
| Chocolate with High Cocoa Content as a Weight-Loss Accelerator (2015) | nutrition-p-hacking-promotional | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/chocolate-weight-loss-2015 |
| Echinacea for treating the common cold: a randomized controlled trial (2010) | clinical-medicine-negative-result | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/echinacea-2010 |
| Hydroxychloroquine and azithromycin as a treatment of COVID-19: results of an open-label non-randomized clinical trial (2020) | clinical-nonrandomized-proxy-endpoint | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/gautret-hcq-2020 |
| The experience of mathematical beauty and its neural correlates (2014) | neuroaesthetics | auditable | sufficient / partial / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/mathematical-beauty-2014 |
| Power Posing: Brief Nonverbal Displays Affect Neuroendocrine Levels and Risk Tolerance (2010) | social-psychology-small-n-multi-outcome | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/power-posing-2010 |
| A Randomized Trial of Intensive versus Standard Blood-Pressure Control (2015) | clinical-medicine | auditable | sufficient / sufficient / sufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/sprint-2015 |
| Hydroxychloroquine or chloroquine with or without a macrolide for treatment of COVID-19: a multinational registry analysis (2020) | registry-source-integrity | non-auditable | n/a | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/surgisphere-hcq-2020 |
| Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children (1998) | case-series-source-integrity | non-auditable | n/a | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/wakefield-mmr-1998 |

## Legacy regression evidence

These remain contract evidence, but their original source URL/model/run metadata were not reconstructed.

| Evidence ID | Fixture |
| --- | --- |
| legacy:ablationbench | tests/fixtures/ablationbench-audit.md |
| legacy:adversarial-care-coordination-before-after-2009 | tests/fixtures/adversarial-care-coordination-before-after-2009-audit.md |
| legacy:adversarial-collagen-dic-2021 | tests/fixtures/adversarial-collagen-dic-2021-audit.md |
| legacy:adversarial-organic-diet-biomarkers-2019 | tests/fixtures/adversarial-organic-diet-biomarkers-2019-audit.md |
| legacy:adversarial-subgroup-aneurysm-2008 | tests/fixtures/adversarial-subgroup-aneurysm-2008-audit.md |
| legacy:adversarial-train-test-leakage-2022 | tests/fixtures/adversarial-train-test-leakage-2022-audit.md |
| legacy:air-quality-cfd | tests/fixtures/air-quality-cfd-audit.md |
| legacy:anti-trigger-difference-in-differences-2014 | tests/fixtures/anti-trigger-difference-in-differences-2014-audit.md |
| legacy:anti-trigger-lod-multiple-imputation-2011 | tests/fixtures/anti-trigger-lod-multiple-imputation-2011-audit.md |
| legacy:anti-trigger-multisite-imaging-2023 | tests/fixtures/anti-trigger-multisite-imaging-2023-audit.md |
| legacy:anti-trigger-sprint-2015 | tests/fixtures/anti-trigger-sprint-2015-audit.md |
| legacy:hea-aluminum | tests/fixtures/hea-aluminum-audit.md |
| legacy:historical-akt-inos-2010 | tests/fixtures/historical-akt-inos-2010-audit.md |
| legacy:historical-bmd-gwas-replication-2010 | tests/fixtures/historical-bmd-gwas-replication-2010-audit.md |
| legacy:historical-brain-beauty-2011 | tests/fixtures/historical-brain-beauty-2011-audit.md |
| legacy:historical-echinacea-2010 | tests/fixtures/historical-echinacea-2010-audit.md |
| legacy:historical-liblinear-2008 | tests/fixtures/historical-liblinear-2008-audit.md |
| legacy:historical-nanoparticle-mmc-2010 | tests/fixtures/historical-nanoparticle-mmc-2010-audit.md |
| legacy:historical-order-book-2010 | tests/fixtures/historical-order-book-2010-audit.md |
| legacy:historical-trace-gas-2011 | tests/fixtures/historical-trace-gas-2011-audit.md |
| legacy:historical-tv-eating-2012 | tests/fixtures/historical-tv-eating-2012-audit.md |
| legacy:hyaluronic-hydrogel | tests/fixtures/hyaluronic-hydrogel-audit.md |
| legacy:resnet-smoke | tests/fixtures/resnet-smoke-audit.md |
| legacy:social-hyperconnection | tests/fixtures/social-hyperconnection-audit.md |

## Record-first policy

A paper mentioned or tested only in a development conversation does not count as project evidence. Future real-paper work must first create a source-backed validation-run record. Additional full replay, inventory, blind, model-comparison, or stability runs attach to the same paper identity rather than inflating the paper count.
