# Evidence base

This page is generated from repository artifacts. It records what the project has actually tested rather than a hand-maintained promotional count.

## Current coverage

- source-backed recorded papers: **10**
- benchmark-only named sources: **38**
- legacy regression fixtures: **24**
- total unique evidence entries: **72**
- tiered-source benchmark cases mapped to durable identities: **40**
- source-backed papers prepared for isolated blind re-audit: **10**

Source-backed entries have stable source identity plus replayable audit artifacts. Benchmark-source entries have explicit public source metadata and benchmark judgments but not a full replay. Legacy fixtures preserve older regression work whose original source/run metadata were not reconstructed.

## Source-backed papers

| Paper | Domain | Viability | Support vector | Test surfaces | Evidence path |
| --- | --- | --- | --- | --- | --- |
| Exploring digital image correlation technique for the analysis of the tensile properties of all-cellulose composites (2021) | materials-measurement | auditable | sufficient / sufficient / partial | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/acc-dic-2021 |
| Attention Is All You Need (2017) | machine-learning | auditable | sufficient / sufficient / partial | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/attention-is-all-you-need-2017 |
| Chocolate with High Cocoa Content as a Weight-Loss Accelerator (2015) | nutrition-p-hacking-promotional | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/chocolate-weight-loss-2015 |
| Echinacea for treating the common cold: a randomized controlled trial (2010) | clinical-medicine-negative-result | auditable | sufficient / sufficient / insufficient | full-replay, claim-selection-12, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/echinacea-2010 |
| Hydroxychloroquine and azithromycin as a treatment of COVID-19: results of an open-label non-randomized clinical trial (2020) | clinical-nonrandomized-proxy-endpoint | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/gautret-hcq-2020 |
| The experience of mathematical beauty and its neural correlates (2014) | neuroaesthetics | auditable | sufficient / partial / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/mathematical-beauty-2014 |
| Power Posing: Brief Nonverbal Displays Affect Neuroendocrine Levels and Risk Tolerance (2010) | social-psychology-small-n-multi-outcome | auditable | sufficient / sufficient / insufficient | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/power-posing-2010 |
| A Randomized Trial of Intensive versus Standard Blood-Pressure Control (2015) | clinical-medicine | auditable | sufficient / sufficient / sufficient | full-replay, tiered-source-40, metadata-halo-12, stability-crossdomain-8, claim-selection-12, blind-re-audit | validation-runs/real-papers/2026-09-26-round-01/sprint-2015 |
| Hydroxychloroquine or chloroquine with or without a macrolide for treatment of COVID-19: a multinational registry analysis (2020) | registry-source-integrity | non-auditable | n/a | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/surgisphere-hcq-2020 |
| Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children (1998) | case-series-source-integrity | non-auditable | n/a | full-replay, blind-re-audit | validation-runs/real-papers/2026-09-26-round-02/wakefield-mmr-1998 |

## Benchmark-only named sources

These public sources were used in benchmark cases and are preserved as evidence of tested source diversity. They are not counted as full replay audits until promoted into a recorded round.

| Source | Domain | Tier | Narrow / broad support | Test surfaces |
| --- | --- | --- | --- | --- |
| Ultrahigh power and energy density in partially ordered lithium-ion cathode materials (2020) | battery materials | flagship_high_attention | sufficient / partial | tiered-source-40, metadata-halo-12 |
| Dry Electrode Architecture Design for Pushing Energy Density Limits at Cell Level (2025) | battery materials | low_attention_nontraditional | sufficient / partial | tiered-source-40, metadata-halo-12 |
| Layered-rocksalt intergrown cathode for high-capacity zero-strain battery operation (2021) | battery materials | ordinary_a | sufficient / partial | tiered-source-40 |
| Photochemically driven solid electrolyte interphase for extremely fast-charging lithium-ion batteries (2021) | battery materials | ordinary_b | sufficient / partial | tiered-source-40 |
| Feasibility and Preliminary Effects of the BESMILE-HF Program on Chronic Heart Failure Patients: A Pilot Randomized Controlled Trial (2021) | clinical cardiology | low_attention_nontraditional | sufficient / insufficient | tiered-source-40, metadata-halo-12 |
| Effects of a Narrative-Based Psychoeducational Intervention to Prepare Patients for Responding to Acute Myocardial Infarction: A Randomized Clinical Trial (2022) | clinical cardiology | ordinary_a | sufficient / partial | tiered-source-40 |
| Effect of a Multicomponent Intervention Delivered on a Web-Based Platform on Hypertension Control: A Cluster Randomized Clinical Trial (2022) | clinical cardiology | ordinary_b | sufficient / partial | tiered-source-40 |
| A scalable method for preparing Cu electrocatalysts that convert CO2 into C2+ products (2020) | catalysis | flagship_high_attention | sufficient / partial | tiered-source-40, metadata-halo-12, stability-crossdomain-8 |
| Pitfalls in identifying active catalyst species (2020) | catalysis | low_attention_nontraditional | partial / insufficient | tiered-source-40, metadata-halo-12 |
| Iodide-mediated Cu catalyst restructuring during CO2 electroreduction (2022) | catalysis | ordinary_a | sufficient / partial | tiered-source-40 |
| Experimental and numerical investigation of NO oxidation on Pt/Al2O3- and NOx storage on Pt/BaO/Al2O3-catalysts (2022) | catalysis | ordinary_b | sufficient / partial | tiered-source-40 |
| Assessing the observed impact of anthropogenic climate change (2016) | climate science | flagship_high_attention | sufficient / partial | tiered-source-40 |
| Surface Infrared Forcing as a Primary Driver of Contemporary Global Warming: A Synthesis of Biophysical, Spectral, and Land-Use Evidence (2026) | climate science | low_attention_nontraditional | partial / insufficient | tiered-source-40 |
| Anthropogenic climate change has driven over 5 million km2 of drylands towards desertification (2020) | climate science | ordinary_a | sufficient / partial | tiered-source-40 |
| Attribution of 2020 hurricane season extreme rainfall to human-induced climate change (2022) | climate science | ordinary_b | sufficient / partial | tiered-source-40 |
| Accelerated modern human-induced species losses: Entering the sixth mass extinction (2015) | ecology | flagship_high_attention | sufficient / partial | tiered-source-40 |
| Ecoacoustics as a novel tool for assessing pond restoration success: Results of a pilot study (2021) | ecology | low_attention_nontraditional | partial / partial | tiered-source-40 |
| Microclimatic Warming Leads to a Decrease in Species and Growth Form Diversity: Insights From a Tropical Alpine Grassland (2021) | ecology | ordinary_a | sufficient / partial | tiered-source-40 |
| Impact of round goby on native invertebrate communities - An experimental field study (2021) | ecology | ordinary_b | sufficient / partial | tiered-source-40, stability-crossdomain-8 |
| Experimental Estimates of Education Production Functions (1999) | education | flagship_high_attention | sufficient / partial | tiered-source-40 |
| Learning How to Order Imaging Tests and Make Subsequent Clinical Decisions: a Randomized Study of the Effectiveness of a Virtual Learning Environment for Medical Students (2021) | education | low_attention_nontraditional | sufficient / partial | tiered-source-40 |
| Flipped learning enhances non-technical skill performance in simulation-based education: a randomised controlled trial (2021) | education | ordinary_a | sufficient / partial | tiered-source-40 |
| Not just words! Effects of a light-touch randomized encouragement intervention on students' exam grades, self-efficacy, motivation, and test anxiety (2021) | education | ordinary_b | sufficient / partial | tiered-source-40 |
| Does a stacked bid side actually mean support? (2026) | financial market microstructure | low_attention_nontraditional | sufficient / insufficient | tiered-source-40, metadata-halo-12 |
| Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book (2016) | financial market microstructure | ordinary_a | sufficient / partial | tiered-source-40 |
| Deep Limit Order Book Forecasting (2024) | financial market microstructure | ordinary_b | sufficient / partial | tiered-source-40 |
| Why Johnny Can't Encrypt: A Usability Evaluation of PGP 5.0 (1999) | human-computer interaction | flagship_high_attention | sufficient / partial | tiered-source-40 |
| Adaptive User Interface Generation Through Reinforcement Learning: A Data-Driven Approach to Personalization and Optimization (2024) | human-computer interaction | low_attention_nontraditional | partial / insufficient | tiered-source-40 |
| Adapting User Interfaces with Model-based Reinforcement Learning (2021) | human-computer interaction | ordinary_a | sufficient / partial | tiered-source-40 |
| The Image of the Interface: How People Use Landmarks to Develop Spatial Memory of Commands in Graphical Interfaces (2021) | human-computer interaction | ordinary_b | sufficient / partial | tiered-source-40 |
| BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (2019) | natural language processing | flagship_high_attention | sufficient / partial | tiered-source-40, metadata-halo-12 |
| Let's talk about LLM evaluation (2024) | natural language processing | low_attention_nontraditional | partial / unclear | tiered-source-40, metadata-halo-12 |
| Are All the Datasets in Benchmark Necessary? A Pilot Study of Dataset Evaluation for Text Classification (2022) | natural language processing | ordinary_a | sufficient / partial | tiered-source-40 |
| StructEval: Deepen and Broaden Large Language Model Assessment via Structured Evaluation (2024) | natural language processing | ordinary_b | sufficient / partial | tiered-source-40 |
| The BErkeley Atmospheric CO2 Observation Network: field calibration and evaluation of low-cost air quality sensors (2018) | sensor engineering | flagship_high_attention | sufficient / partial | tiered-source-40, metadata-halo-12 |
| A temporal deep learning framework for calibration of low-cost air quality sensors (2026) | sensor engineering | low_attention_nontraditional | sufficient / partial | tiered-source-40, metadata-halo-12 |
| Calibration of SO2 and NO2 Electrochemical Sensors via a Training and Testing Method in an Industrial Coastal Environment (2022) | sensor engineering | ordinary_a | sufficient / partial | tiered-source-40 |
| Development and Calibration of a Low-Cost, Piezoelectric Rainfall Sensor through Machine Learning (2022) | sensor engineering | ordinary_b | sufficient / partial | tiered-source-40 |

## Legacy regression evidence

These remain contract evidence, but their original source URL/model/run metadata were not reconstructed.

| Evidence ID | Fixture | Test surfaces |
| --- | --- | --- |
| legacy:ablationbench | tests/fixtures/ablationbench-audit.md | legacy-regression |
| legacy:adversarial-care-coordination-before-after-2009 | tests/fixtures/adversarial-care-coordination-before-after-2009-audit.md | legacy-regression, claim-selection-12 |
| legacy:adversarial-collagen-dic-2021 | tests/fixtures/adversarial-collagen-dic-2021-audit.md | legacy-regression |
| legacy:adversarial-organic-diet-biomarkers-2019 | tests/fixtures/adversarial-organic-diet-biomarkers-2019-audit.md | legacy-regression |
| legacy:adversarial-subgroup-aneurysm-2008 | tests/fixtures/adversarial-subgroup-aneurysm-2008-audit.md | legacy-regression |
| legacy:adversarial-train-test-leakage-2022 | tests/fixtures/adversarial-train-test-leakage-2022-audit.md | legacy-regression |
| legacy:air-quality-cfd | tests/fixtures/air-quality-cfd-audit.md | legacy-regression, stability-crossdomain-8, claim-selection-12 |
| legacy:anti-trigger-difference-in-differences-2014 | tests/fixtures/anti-trigger-difference-in-differences-2014-audit.md | legacy-regression |
| legacy:anti-trigger-lod-multiple-imputation-2011 | tests/fixtures/anti-trigger-lod-multiple-imputation-2011-audit.md | legacy-regression |
| legacy:anti-trigger-multisite-imaging-2023 | tests/fixtures/anti-trigger-multisite-imaging-2023-audit.md | legacy-regression |
| legacy:anti-trigger-sprint-2015 | tests/fixtures/anti-trigger-sprint-2015-audit.md | legacy-regression |
| legacy:hea-aluminum | tests/fixtures/hea-aluminum-audit.md | legacy-regression, stability-crossdomain-8, claim-selection-12 |
| legacy:historical-akt-inos-2010 | tests/fixtures/historical-akt-inos-2010-audit.md | legacy-regression |
| legacy:historical-bmd-gwas-replication-2010 | tests/fixtures/historical-bmd-gwas-replication-2010-audit.md | legacy-regression, claim-selection-12 |
| legacy:historical-brain-beauty-2011 | tests/fixtures/historical-brain-beauty-2011-audit.md | legacy-regression, claim-selection-12 |
| legacy:historical-echinacea-2010 | tests/fixtures/historical-echinacea-2010-audit.md | legacy-regression |
| legacy:historical-liblinear-2008 | tests/fixtures/historical-liblinear-2008-audit.md | legacy-regression |
| legacy:historical-nanoparticle-mmc-2010 | tests/fixtures/historical-nanoparticle-mmc-2010-audit.md | legacy-regression |
| legacy:historical-order-book-2010 | tests/fixtures/historical-order-book-2010-audit.md | legacy-regression, tiered-source-40, metadata-halo-12, stability-crossdomain-8 |
| legacy:historical-trace-gas-2011 | tests/fixtures/historical-trace-gas-2011-audit.md | legacy-regression |
| legacy:historical-tv-eating-2012 | tests/fixtures/historical-tv-eating-2012-audit.md | legacy-regression |
| legacy:hyaluronic-hydrogel | tests/fixtures/hyaluronic-hydrogel-audit.md | legacy-regression |
| legacy:resnet-smoke | tests/fixtures/resnet-smoke-audit.md | legacy-regression, stability-crossdomain-8, claim-selection-12 |
| legacy:social-hyperconnection | tests/fixtures/social-hyperconnection-audit.md | legacy-regression, stability-crossdomain-8, claim-selection-12 |

## Record-first policy

A paper or public source tested only in a development conversation does not count as project evidence. Full paper audits must become source-backed validation-run records. Named benchmark sources are retained at their actual evidence grade, and additional replay, blind, model-comparison, or stability runs attach to the same identity rather than inflating coverage.
