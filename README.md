# Evidence Paper Reader

An open-source **Agent Skill** for **ChatGPT**, **Codex**, and other tools that support the open `SKILL.md` format.

This skill reads **evidence-driven research papers** from the **reader's** point of view. Instead of praising prose or imitating editorial peer review, it separates:

- core claims
- evidence types
- support strength
- usable results, methods, and materials
- analysis that should be downweighted
- uncertainty and follow-up dependencies

It is designed for users who want to know **what in a paper is actually trustworthy** and **what is mostly narrative overreach**.

## What this skill is for

Use this skill when you want to audit a paper such as:

- experimental natural science papers
- benchmark or ablation-heavy method papers
- simulation or computational papers
- quantitative social science papers
- empirical social science papers with clear evidence chains, including surveys, interviews, archives, field notes, and content analysis

It is **not** intended as a paper scoring tool or a peer-review simulator.

## What the skill outputs

The skill produces a fixed **reader-side paper audit** that emphasizes:

1. reader conclusion
2. core claims
3. evidence and support
4. what is usable
5. what to downweight
6. value breakdown
7. uncertainty and follow-up

Each major claim is tied to a controlled evidence type, evidence provenance (`paper-local`, `external citation`, or `mixed`), evidence dependence, a traceable source location, and a bounded support judgment. This prevents an external citation from silently becoming evidence demonstrated by the current paper.

## Evidence contract

The current contract is intentionally stricter than a prose-only prompt:

- fixed top-level output sections and field names
- explicit scope status: `in scope`, `partially in scope`, or `out of scope`
- controlled evidence labels, including a distinct `computational benchmark` label for benchmark/ablation-heavy ML and software papers
- explicit source locations for support judgments
- explicit separation of paper-local evidence from imported citation support
- DOI handling that forbids guessing from memory
- evidence-topology checks for mechanical coupling, null-result interpretation, proxy/construct separation, selection-conditioned evidence, and scale transfer
- evidence-dependence checks that distinguish single-source evidence, shared-source corroboration, partial triangulation, and materially independent convergence
- stable evidence-node IDs that make cross-claim evidence reuse and claim stacking visible
- explicit claim-to-claim dependencies that carry upstream uncertainty forward
- bounded methodological knowledge for figures/tables, statistical inference, measurement, and study design without embedding domain conclusions
- empirical finance, clinical/biomedical, and empirical-aesthetics coverage when the paper has a traceable evidence chain

## Repository layout

```text
.
├── .github/
│   └── workflows/
│       └── contract-tests.yml
├── LICENSE
├── README.md
├── tests/
│   ├── fixtures/
│   │   ├── ablationbench-audit.md
│   │   ├── adversarial-care-coordination-before-after-2009-audit.md
│   │   ├── adversarial-collagen-dic-2021-audit.md
│   │   ├── adversarial-organic-diet-biomarkers-2019-audit.md
│   │   ├── adversarial-subgroup-aneurysm-2008-audit.md
│   │   ├── adversarial-train-test-leakage-2022-audit.md
│   │   ├── historical-akt-inos-2010-audit.md
│   │   ├── historical-brain-beauty-2011-audit.md
│   │   ├── historical-bmd-gwas-replication-2010-audit.md
│   │   ├── historical-echinacea-2010-audit.md
│   │   ├── historical-liblinear-2008-audit.md
│   │   ├── historical-nanoparticle-mmc-2010-audit.md
│   │   ├── historical-order-book-2010-audit.md
│   │   ├── historical-trace-gas-2011-audit.md
│   │   ├── historical-tv-eating-2012-audit.md
│   │   ├── air-quality-cfd-audit.md
│   │   ├── hea-aluminum-audit.md
│   │   ├── hyaluronic-hydrogel-audit.md
│   │   ├── resnet-smoke-audit.md
│   │   └── social-hyperconnection-audit.md
│   ├── test_contract.py
│   └── validate_audit.py
└── evidence-paper-reader/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── references/
        ├── claim-dependencies.md
        ├── claim-evidence-links.md
        ├── evidence-dependence.md
        ├── evidence-types.md
        ├── evidence-topology.md
        ├── figure-and-table-traps.md
        ├── follow-up-boundaries.md
        ├── measurement-traps.md
        ├── statistical-traps.md
        ├── study-design-traps.md
        └── pollution-patterns.md
```

## Contract tests

The repository includes a zero-dependency Python validator and a cross-domain real-paper regression suite. The fixtures are intentionally heterogeneous so the skill is tested against different evidence chains rather than a single model-paper style.

Run locally with:

```bash
python -m unittest discover -s tests -v
for audit in tests/fixtures/*-audit.md; do python tests/validate_audit.py "$audit"; done
```

The tests verify, among other things, that:

- the seven output sections are present exactly once and in order
- in-scope audits contain 3-5 sequential core claims
- claim/support fields use controlled values
- unknown evidence labels are rejected
- `literature citation` cannot be labeled `paper-local`
- `external citation` or `mixed` provenance requires a named external dependency
- every real-paper regression fixture satisfies the contract
- cross-section consistency and validation-independence rules remain present
- historical regression rules for mechanical coupling, null results, proxy reification, and selection-conditioned evidence remain present
- intervention claims and administrative/transactional evidence stay valid controlled labels
- every support block carries a controlled evidence-dependence class
- real fixtures preserve examples of shared-source, partially independent, and independent convergence
- every support block carries machine-checkable evidence-node IDs
- convergence labels require at least two evidence nodes
- claim-stacking regressions preserve evidence reuse instead of renaming the same result
- every support block declares upstream claim dependencies
- forward/self dependencies are rejected and uncertainty cannot disappear without new evidence
- figure/table interpretation traps remain present as bounded methodological knowledge
- statistical, measurement, and study-design trap references remain modular and explicitly bounded from domain-fact priors
- adversarial fixtures trigger subgroup-interaction, detection-limit, regression-to-the-mean, benchmark-leakage, and technical-repeat checks without adding new output fields

GitHub Actions runs the same checks on pushes and pull requests.

### Claim dependencies and uncertainty propagation

Claims can depend on earlier claims as premises. Each support block therefore declares `upstream claims: none` or earlier IDs such as `C1 + C2`. Claims are ordered as a DAG: later claims may depend on earlier ones, never the reverse.

The validator implements a conservative propagation rule. If a downstream claim adds no evidence nodes beyond its required upstream claims, and any required upstream claim is not `sufficient`, the downstream claim cannot become `sufficient` merely by restatement. New direct evidence can still change the judgment.

### Bounded methodological world knowledge

The skill intentionally avoids embedding field conclusions such as expected material properties, treatment efficacy, or market behavior. It does include portable reading knowledge that changes how evidence should be interpreted.

`figure-and-table-traps.md` covers decision-critical visual and tabular interpretation.

`statistical-traps.md` covers effect size versus significance, multiplicity and selection, optional stopping, regression to the mean, subgroup interactions, covariate adjustment, model-form assumptions, dependence, missing data, Bayesian interpretation, and robustness.

`measurement-traps.md` covers reliability versus validity, calibration/drift, detection limits, ceiling/floor effects, batch effects, assay specificity, measurement error, composite measures, surrogate endpoints, image-derived quantities, sensor context, coding reliability, and preprocessing.

`study-design-traps.md` covers the unit of assignment, randomization/blinding, uncontrolled pre/post designs, historical controls, attrition/survivorship, case-control sampling, immortal time, crossover/clustered designs, quasi-experimental identification, mediation, benchmark leakage, and temporal leakage.

These are not automatic flaw labels. The reader routes only the modules relevant to a core claim and states what the design or measurement does and does not justify. Domain facts remain external to the skill unless the user separately asks for literature context.

### Claim-evidence links and evidence reuse

Every support block now lists stable local evidence-node IDs such as `E1` or `E1 + E2`. The same result keeps the same ID when it is reused across claims. This exposes a common failure mode: one result is directly valid for a narrow claim, then reused for a stronger mechanism or generality claim without any new direct evidence.

The 2011 brain-beauty fixture is a regression example: the same mOFC/self-rating evidence nodes are reused across the observational cross-modal result, the broader "faculty of beauty" interpretation, and the even broader generalization to other sources of beauty. The nodes stay fixed while support moves from sufficient to partial or insufficient. Reuse is allowed; duplicated evidentiary weight is not.

### Evidence dependence and triangulation

The audit does not count every figure, endpoint, assay, or model as a separate confirmation. Each core claim now receives one dependence class:

- `single-source`
- `shared-source convergence`
- `partially independent convergence`
- `independent convergence`
- `unclear`

For example, two outcomes from the same randomized cohort are shared-source convergence, while the CATSPERB BMD association in the 2010 GWAS fixture receives independent-convergence status only because the supporting signal appears in a separately sampled replication cohort. Different evidence types do not automatically imply independence.

### Adversarial methodology regression wave

A third regression wave selects papers that can look convincing under surface reading but require the correct methodological module to avoid overclaiming.

| Fixture | Domain | Trigger | Main adversarial boundary |
| --- | --- | --- | --- |
| `adversarial-subgroup-aneurysm-2008-audit.md` | medicine / RCT subgroup | statistics | significance within separate subgroups is not a treatment-by-subgroup interaction |
| `adversarial-organic-diet-biomarkers-2019-audit.md` | environmental health / intervention | measurement + statistics + design | LOD handling, 58-parameter multiplicity control, cluster/crossover structure, and co-intervention confounding |
| `adversarial-care-coordination-before-after-2009-audit.md` | health services | study design + statistics | large pre/post savings can reflect regression to the mean without a concurrent counterfactual |
| `adversarial-train-test-leakage-2022-audit.md` | information retrieval | ML study design | semantic train-test overlap can inflate metrics or change rankings, but effect size depends on contamination fraction |
| `adversarial-collagen-dic-2021-audit.md` | microscopy / measurement | measurement + dependence | repeated imaging/processing improves precision but does not turn five fibrils into many independent specimens |

The point of these fixtures is trigger correctness. They should activate only the methodological knowledge relevant to the claim and should not turn the audit into a generic checklist.

### Current real-paper regression matrix

| Fixture | Domain | Paper | Main stress case |
| --- | --- | --- | --- |
| `resnet-smoke-audit.md` | information science / ML | *Deep Residual Learning for Image Recognition* | benchmark evidence, mechanism vs performance, generality |
| `ablationbench-audit.md` | information science / AI-for-science | *AblationBench: Evaluating Automated Planning of Ablations in Empirical AI Research* | benchmark construction, human baseline, model-specific generalization |
| `hyaluronic-hydrogel-audit.md` | biomaterials / cell biology | *Hydrogels with Ultrasound-Treated Hyaluronic Acid Regulate CD44-Mediated Angiogenic Potential of Human Vascular Endothelial Cells In Vitro* | paper-local intervention evidence vs imported signaling mechanism |
| `hea-aluminum-audit.md` | materials science | *Effect of Al Content on Microstructure and Mechanical Properties of CoCrFeNiMn High-Entropy Alloy* | abstract/conclusion vs reported values; phase/mechanism overreach |
| `air-quality-cfd-audit.md` | environment / air quality | *Integrating Cost-Effective Measurements and CFD Modeling for Accurate Air Quality Assessment* | calibration target reused for evaluation; validation independence |
| `social-hyperconnection-audit.md` | social survey | *How Screen Time and Social Media Hyperconnection Have Harmed Adolescents’ Relational and Psychological Well-Being since the COVID-19 Pandemic* | repeated cross-sectional association vs causal wording |

### Historical regression wave: papers from 2008-2012

The second regression wave deliberately samples papers around 2010, when reporting conventions, online supplements, preregistration norms, and field-specific validation practices differed from current papers.

| Fixture | Year | Domain | Paper | Main stress case |
| --- | ---: | --- | --- | --- |
| `historical-liblinear-2008-audit.md` | 2008 | information science | *LIBLINEAR: A Library for Large Linear Classification* | short paper delegates broad benchmark/theory claims to companion citations |
| `historical-akt-inos-2010-audit.md` | 2010 | biochemistry | *Akt-Mediated Signaling...Suppresses Hepatocyte iNOS...* | partial pathway reversal vs complete-mechanism wording |
| `historical-nanoparticle-mmc-2010-audit.md` | 2010 | materials | *Improved Mechanical and Tribological Properties of Metal-Matrix Composites...* | best/optimal formulations vs unfavorable concentrations; selection-conditioned evidence |
| `historical-trace-gas-2011-audit.md` | 2011 | environment | *Measuring Trace Gas Emission from Multi-Distributed Sources...* | filtered valid observations and configuration-dependent accuracy |
| `historical-tv-eating-2012-audit.md` | 2012 (2009-10 data) | social survey | *Associations of Television Viewing With Eating Behaviors...* | association, effect modification, and non-causal mediation language |
| `historical-order-book-2010-audit.md` | 2010 | finance | *The Price Impact of Order Book Events* | predictor/outcome mechanical coupling and one-regime generalization |
| `historical-echinacea-2010-audit.md` | 2010 | medicine | *Echinacea for Treating the Common Cold: A Randomized Trial* | non-significance vs equivalence/no meaningful effect |
| `historical-brain-beauty-2011-audit.md` | 2011 | empirical aesthetics | *Toward A Brain-Based Theory of Beauty* | measured rating/neural correlate vs broader construct and universality |
| `historical-bmd-gwas-replication-2010-audit.md` | 2010 | medical genetics | *Genome-Wide Association Study of Bone Mineral Density in Premenopausal European-American Women and Replication in African-American Women* | discovery cohort vs materially independent replication cohort |

These fixtures are not gold-standard peer reviews. They are contract regressions: each preserves a specific evidence-chain failure mode that the skill should continue to notice as its instructions evolve.

## Install

### ChatGPT
Upload or install the `evidence-paper-reader` skill folder in a ChatGPT environment that supports Skills.

### Codex
Copy `evidence-paper-reader/` into your Codex skills directory.

### Other tools that support the open SKILL.md / Agent Skills format
Use the same folder directly if the tool supports this format.

## Why this repo is marketplace-friendly

- public GitHub-ready skill folder
- uses the open `SKILL.md` standard
- contains a single focused skill
- includes a license
- includes a README with clear scope and install instructions
- includes contract tests that keep output and evidence semantics stable as the skill evolves

This makes the repository easy to share directly on GitHub and suitable for discovery by GitHub-based skill indexes such as **Skill Marketplace**.

## Suggested GitHub repository metadata

Suggested repository name:
- `evidence-paper-reader`

Suggested repository description:
- `Reader-side paper audit skill for evidence, support strength, usable results, and overreach in research papers.`

Suggested GitHub topics:
- `agent-skill`
- `skill-md`
- `chatgpt`
- `codex`
- `research`
- `paper-reading`
- `literature-review`
- `science`
- `social-science`
- `open-source`

## License

MIT
