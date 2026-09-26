# Evidence Paper Reader

An open-source **Agent Skill** for **ChatGPT**, **Codex**, and other tools that support the open `SKILL.md` format.

This skill reads **evidence-driven research papers** from the **reader's** point of view. Instead of praising prose or imitating editorial peer review, it separates:

- evidence viability (`auditable`, `partially auditable`, or `non-auditable`)
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
- a separate evidence-viability gate that can stop evidence-shaped but non-auditable material before the model invents a full claim audit
- controlled evidence labels, including a distinct `computational benchmark` label for benchmark/ablation-heavy ML and software papers
- explicit source locations for support judgments
- explicit separation of paper-local evidence from imported citation support
- DOI handling that forbids guessing from memory
- evidence-topology checks for mechanical coupling, null-result interpretation, proxy/construct separation, selection-conditioned evidence, and scale transfer
- evidence-dependence checks that distinguish single-source evidence, shared-source corroboration, partial triangulation, and materially independent convergence
- stable evidence-node IDs that make cross-claim evidence reuse and claim stacking visible
- an optional R/G/U evidence-inventory layer for long papers that separates repeated source records, same-result identity, and shared evidence-generating units before promotion to E nodes
- explicit claim-to-claim dependencies that carry upstream uncertainty forward
- bounded methodological knowledge for figures/tables, statistical inference, measurement, and study design without embedding domain conclusions
- false-positive guards that require trap cues to survive a mitigation check before they can downweight a claim
- empirical finance, clinical/biomedical, and empirical-aesthetics coverage when the paper has a traceable evidence chain

## Layered architecture

The skill is intentionally split so execution can keep context focused without changing the audit standard.

### Layer 0 — thin orchestrator
`SKILL.md` contains only the stable workflow, mandatory boundaries, load order, and guarded Flash/Full execution paths.

It should stay small enough to read in full.

### Layer 1 — core contract
Every audit loads:
- `references/core-contract.md`
- `references/evidence-viability.md`
- `references/evidence-types.md`

For the output interface:
- with Python: load `references/audit-ledger-format.md`, fill JSON, then use `scripts/render_audit.py`
- without Python: load `references/output-contract.md` as the manual fallback

This keeps Markdown formatting out of the model's working context whenever the runtime can own it.

### Layer 2 — routing
`references/method-router.md` maps paper cues to optional modules.

When plain paper text is available and Python can run, `scripts/suggest_modules.py` provides a lexical first-pass route. Its output is advisory: a cue means "inspect this module", never "a flaw exists".

### Layer 3 — optional knowledge modules
Only load modules that matter to decision-critical claims or retrieval complexity:
- evidence inventory for long/structurally complex papers
- figures/tables
- statistics
- measurement
- study design
- topology
- dependence
- claim reuse/dependency
- external follow-up
- false-positive guards

`references/domain-profiles.md` adds domain-specific emphasis without changing the output format.

### Layer 4 — scripts and CI
`scripts/render_audit.py` owns canonical Markdown generation and `scripts/validate_audit.py` checks the mechanical output/graph contract.

The regression suite tests semantic boundaries with historical, adversarial, and anti-trigger real-paper fixtures.

The validator cannot replace scientific judgment; it removes bookkeeping and consistency work from the model.

### Flash path

Flash path is the staged-loading route. It keeps context small without reducing the work required.

1. Read `SKILL.md`.
2. Load `core-contract.md`, `evidence-viability.md`, `evidence-types.md`, and `audit-ledger-format.md` when the renderer is available.
3. Decide scope and evidence viability before claim extraction. Auditable material gets 3–5 claims; partially auditable material gets only the 1–5 reconstructable claims; non-auditable material does not manufacture claims.
4. Run or consult the router.
5. Load every matched module required by decision-critical claims.
6. Audit one claim at a time and re-route when new cues appear.
7. Fill the structured audit ledger and render it with `render_audit.py`.
8. Run the packaged `validate_audit.py`.

Flash path never permits fewer claims for material classified `auditable`, missing fields, skipped routed modules, weaker support standards, or abstract-only support judgments.

### Full path

Full path uses the same evidence and output contracts, but permits broader simultaneous module loading, a second cross-claim pass, and deeper dependency inspection.

Flash automatically escalates to Full when:
- three or more primary methodology modules are required
- a core claim structurally depends on an external cited work
- direct paper-local evidence materially conflicts across sections
- multiple studies/cohorts/datasets/sites/experiments require a non-trivial dependence map
- a decision-critical claim remains `unclear` after targeted checking
- the user requests a comprehensive/deep audit

The important distinction is execution strategy, not quality level: **Flash means less irrelevant context, not less work.**

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
│   │   ├── anti-trigger-difference-in-differences-2014-audit.md
│   │   ├── anti-trigger-lod-multiple-imputation-2011-audit.md
│   │   ├── anti-trigger-multisite-imaging-2023-audit.md
│   │   ├── anti-trigger-sprint-2015-audit.md
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
│   ├── viability-fixtures/
│   │   ├── synthetic-partially-auditable-tech-note-audit.md
│   │   ├── synthetic-promotional-brief-audit.md
│   │   └── synthetic-self-referential-framework-audit.md
│   ├── test_contract.py
│   ├── test_evidence_viability.py
│   └── validate_audit.py
└── evidence-paper-reader/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── scripts/
    │   ├── evidence_inventory.py
    │   ├── merge_route.py
    │   ├── render_audit.py
    │   ├── suggest_modules.py
    │   └── validate_audit.py
    └── references/
        ├── audit-ledger-format.md
        ├── claim-dependencies.md
        ├── claim-evidence-links.md
        ├── core-contract.md
        ├── domain-profiles.md
        ├── evidence-dependence.md
        ├── evidence-inventory-format.md
        ├── evidence-types.md
        ├── evidence-viability.md
        ├── evidence-topology.md
        ├── false-positive-guards.md
        ├── figure-and-table-traps.md
        ├── follow-up-boundaries.md
        ├── measurement-traps.md
        ├── method-router.md
        ├── semantic-router-card.md
        ├── output-contract.md
        ├── statistical-traps.md
        ├── study-design-traps.md
        └── pollution-patterns.md
```

### Evidence inventory for long papers

Long-paper reading adds a retrieval problem before the scientific judgment problem.

The optional inventory layer uses four identities:

- `R`: a locatable source record
- `G`: repeated presentations of the same underlying result
- `U`: the evidence-generating unit (participants, dataset, specimens, cohort, site, archive, etc.)
- `E`: the deduplicated evidence node used by the final audit

Example:

```text
abstract primary outcome   R1 ─┐
Table 2 same outcome       R2 ─┴─ G1 / U1 ─→ E1
secondary outcome          R3 ─── G2 / U1 ─→ E2
replication cohort         R4 ─── G3 / U2 ─→ E3
```

This prevents repeated presentation from becoming fake triangulation while preserving the distinction between different results from the same source unit and genuinely independent replication.

Every core claim in an inventory must either connect to promoted evidence or appear explicitly in `unresolved_claims`. Retrieval failure therefore stays visible instead of silently dropping a difficult claim.

Use:

```bash
python evidence-paper-reader/scripts/evidence_inventory.py --template > inventory.json
python evidence-paper-reader/scripts/evidence_inventory.py inventory.json --check
python evidence-paper-reader/scripts/evidence_inventory.py inventory.json --compact
python evidence-paper-reader/scripts/evidence_inventory.py inventory.json --audit-ledger audit.json
```

The last command can reject obvious contradictions such as an audit claiming `independent convergence` when the promoted E nodes share the same known U key.

### Scripted output renderer

When Python is available, the model does not need to manually reproduce Markdown headings or field ordering.

Create a starter ledger:

```bash
python evidence-paper-reader/scripts/render_audit.py --template > audit.json
```

Fill semantic fields in `audit.json`, then:

```bash
python evidence-paper-reader/scripts/render_audit.py audit.json --check
python evidence-paper-reader/scripts/render_audit.py audit.json -o audit.md
python evidence-paper-reader/scripts/validate_audit.py audit.md
```

The renderer owns claim numbering, seven-section layout, field ordering, evidence-node/upstream-claim joining, out-of-scope placeholders, and value-breakdown ordering. The model still owns claim extraction, evidence identity, dependence, support judgment, reasons, and uncertainty.

### Optional routing helper

For plain extracted paper text:

```bash
python evidence-paper-reader/scripts/suggest_modules.py paper.txt
python evidence-paper-reader/scripts/suggest_modules.py paper.txt --json
```

The helper searches for cheap lexical cues and proposes candidate references. It is not the final router. Core claims are confirmed with `semantic-router-card.md`, then `merge_route.py` combines semantic decisions with lexical candidates. A cue never declares a bias or flaw.

## Evidence base

Every real-paper test is treated as a durable repository evidence asset. See [EVIDENCE.md](EVIDENCE.md) for the generated, source-backed evidence catalog and the explicitly lower-provenance legacy regression set.

The catalog follows a provenance-graded record-first rule: full paper audits must leave source identity and replayable repository artifacts; named benchmark-only public sources are retained separately at lower evidence grade until promoted into a full replay. Multiple runs or benchmark surfaces on one source do not inflate the independent-source count. CI regenerates the expected catalog from repository state and fails if the published evidence page becomes stale.

The detailed policy is in `validation-runs/real-papers/EVIDENCE_POLICY.md`.

## Benchmarks

Six non-core benchmark suites live under `benchmarks/`:

- `tiered-source-40/`: 10 domains × 4 source/attention tiers; checks whether bounded evidence judgments can remain distinct from source prestige.
- `metadata-halo-12/`: paired anonymous A/B packets with identical scientific content and metadata hidden vs visible; designed for isolated-context causal testing of prestige/attention halo.
- `claim-selection-12/`: tests the pre-audit stage—core-claim recall, distractor selection, evidence-viability decisions, and especially silent narrowing of strong author claims into safer claims before support judgment.
- `router-adversarial-24/`: 12 semantic-only routing cases plus 12 lexical decoys; measures required-module recall, irrelevant keyword suppression, inventory routing, and lexical+semantic merge behavior.
- `stability-crossdomain-8/`: eight real-paper domains × five isolated repeats; separates repeated-run stability from reference correctness across viability, claim selection, routing, inventory choice, and support. It also includes a runner-neutral batch executor for one-packet-per-process fresh-context runs.
- `blind-real-paper-10/`: ten source-backed papers re-audited from answer-key-free source packets in fresh contexts; reviewer prompts cannot see stored ledgers or regression contracts, while a separate hidden scorer compares viability and bounded support judgments after the response exists.

The second benchmark must be run in fresh independent model contexts. The development conversation itself is contaminated by knowing the pair mapping and reference expectations, so repository setup is not reported as a model result.

## Contract tests

The repository includes a zero-dependency Python validator and a cross-domain real-paper regression suite. The fixtures are intentionally heterogeneous so the skill is tested against different evidence chains rather than a single model-paper style.

Run locally with:

```bash
python -m unittest discover -s tests -v
for audit in tests/fixtures/*-audit.md; do python evidence-paper-reader/scripts/validate_audit.py "$audit"; done
```

The tests verify, among other things, that:

- `SKILL.md` remains a thin orchestrator rather than absorbing the knowledge library
- structured ledger rendering produces canonical Markdown that passes the packaged validator
- mandatory versus optional references stay separated
- the advisory router suggests relevant modules without treating lexical cues as findings

- the seven output sections are present exactly once and in order
- `auditable` audits contain 3–5 claims, `partially auditable` audits contain only 1–5 reconstructable claims, and `non-auditable` audits do not manufacture claim blocks
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
- anti-trigger fixtures verify that correctly mitigated subgroup, interim-analysis, LOD, pre/post, and technical-repeat cues do not cause automatic downweighting
- evidence-viability fixtures distinguish auditable, partially auditable, and evidence-shaped non-auditable material
- claim-selection benchmark tests required-claim recall, forbidden selections, silent narrowing, viability accuracy, and claim-count discipline
- evidence-inventory tests prevent duplicate result promotion, cross-result E-node merges, repeated R promotion, invisible claim-retrieval gaps, and false independent convergence over shared U units
- router-adversarial tests require a perfect semantic route to recover keyword-hidden modules and suppress incidental lexical decoys without weakening conservative `unclear` behavior
- cross-domain stability tests verify 8 unique domains × 5 repeats, separate optional-claim omission from support error, and make single-run drift visible at the layer where it occurs

GitHub Actions runs the same checks on pushes and pull requests.

### Cross-domain repeated-run stability

One-shot correctness is not enough for a reusable skill. The `stability-crossdomain-8` benchmark repeats the same compact real-paper review five times in isolated contexts across eight domains:

- clinical cardiology
- materials science
- machine learning
- environmental modeling
- social science
- financial market microstructure
- ecology
- electrocatalysis

The scorer reports two different families of metrics:

- **stability**: pairwise agreement/Jaccard for viability, claim selection, routing, inventory choice, and support vectors
- **reference correctness**: viability accuracy, required-claim recall, forbidden-claim selection rate, required-module recall, unallowed-module rate, inventory accuracy, and support accuracy

This distinction matters because a model can be perfectly consistent and still be consistently wrong.

Generate the 40-job matrix with:

```bash
python benchmarks/stability-crossdomain-8/generate_runs.py
python benchmarks/stability-crossdomain-8/run_reviewer.py --command './review_one.sh {packet} {output}'
```

Then run each packet in a fresh context with the same model/configuration, save responses by packet ID, and score:

```bash
python benchmarks/stability-crossdomain-8/score_repeats.py responses/
```

The current development conversation knows the benchmark references, so it is not a valid isolated reviewer for those repeated runs.

### Evidence viability gate

Before claim extraction, the skill asks whether the source exposes a reconstructable evidence chain.

This is separate from topical scope. A source can be technically relevant and still be `non-auditable`.

Controlled states:

- `auditable`: central claims can be mapped to inspectable methods/results; run the normal 3–5 claim audit.
- `partially auditable`: only part of the central evidence chain is reconstructable; audit only the 1–5 claims that can actually be supported or bounded.
- `non-auditable`: the central evidence chain is not exposed; do not force a conventional claim audit.

Decision-critical flags include:

- critical method/result omission
- missing comparator
- selected-success-only presentation
- self-referential constructs
- circular validation
- demo-only evidence
- proprietary black boxes
- dominant external dependencies
- promotional evidence asymmetry
- documented source-integrity failure that blocks trust in the central evidence substrate

This is not a prestige filter. A blog, preprint, vendor white paper, or tiny pilot can be auditable. A polished or prestigious article can be non-auditable for a specific central claim.

The gate also separates unfamiliar terminology from circular terminology. A newly invented construct is acceptable when it is operationalized and tested against independent observations or predictions. It becomes a viability problem when the construct is defined by an author-created score and that same score is then used as the main proof that the construct exists.

Three synthetic regression fixtures protect the boundary:

- promotional technical brief with missing methods/comparator and selected demonstrations → `non-auditable`
- self-referential conceptual framework → `non-auditable`
- industrial note with a real logged performance result but proprietary mechanism → `partially auditable`

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

### Anti-trigger / false-positive regression wave

The fourth regression wave tests the opposite failure mode: methodological pattern matching that criticizes a paper even after the relevant risk has been handled.

| Fixture | Apparent trap cue | Mitigation that must receive credit |
| --- | --- | --- |
| `anti-trigger-sprint-2015-audit.md` | multiple subgroups and interim looks | prespecified interaction tests with Hommel adjustment; Lan-DeMets/O'Brien-Fleming group-sequential monitoring |
| `anti-trigger-lod-multiple-imputation-2011-audit.md` | many values below LOD | censoring-aware likelihood, multiple imputation, and 5,000-replicate simulation validation across censoring regimes |
| `anti-trigger-difference-in-differences-2014-audit.md` | pre/post intervention data | matched comparator and DiD analysis; authors explicitly refuse causal attribution when between-site change is null |
| `anti-trigger-multisite-imaging-2023-audit.md` | huge numbers of cells and technical repeats | explicit nested design and mixed-effects variance decomposition across lab/person/experiment/replicate/cell/time |

The target behavior is neither credulity nor reflexive criticism. A risk cue triggers a methodological check; a demonstrated mitigation earns credit; only residual uncertainty should affect the support judgment.

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
