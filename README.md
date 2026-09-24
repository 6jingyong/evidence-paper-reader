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

Each major claim is tied to a controlled evidence type, evidence provenance (`paper-local`, `external citation`, or `mixed`), a traceable source location, and a bounded support judgment. This prevents an external citation from silently becoming evidence demonstrated by the current paper.

## Evidence contract

The current contract is intentionally stricter than a prose-only prompt:

- fixed top-level output sections and field names
- explicit scope status: `in scope`, `partially in scope`, or `out of scope`
- controlled evidence labels, including a distinct `computational benchmark` label for benchmark/ablation-heavy ML and software papers
- explicit source locations for support judgments
- explicit separation of paper-local evidence from imported citation support
- DOI handling that forbids guessing from memory

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
        ├── evidence-types.md
        ├── follow-up-boundaries.md
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

GitHub Actions runs the same checks on pushes and pull requests.

### Current real-paper regression matrix

| Fixture | Domain | Paper | Main stress case |
| --- | --- | --- | --- |
| `resnet-smoke-audit.md` | information science / ML | *Deep Residual Learning for Image Recognition* | benchmark evidence, mechanism vs performance, generality |
| `ablationbench-audit.md` | information science / AI-for-science | *AblationBench: Evaluating Automated Planning of Ablations in Empirical AI Research* | benchmark construction, human baseline, model-specific generalization |
| `hyaluronic-hydrogel-audit.md` | biomaterials / cell biology | *Hydrogels with Ultrasound-Treated Hyaluronic Acid Regulate CD44-Mediated Angiogenic Potential of Human Vascular Endothelial Cells In Vitro* | paper-local intervention evidence vs imported signaling mechanism |
| `hea-aluminum-audit.md` | materials science | *Effect of Al Content on Microstructure and Mechanical Properties of CoCrFeNiMn High-Entropy Alloy* | abstract/conclusion vs reported values; phase/mechanism overreach |
| `air-quality-cfd-audit.md` | environment / air quality | *Integrating Cost-Effective Measurements and CFD Modeling for Accurate Air Quality Assessment* | calibration target reused for evaluation; validation independence |
| `social-hyperconnection-audit.md` | social survey | *How Screen Time and Social Media Hyperconnection Have Harmed Adolescents’ Relational and Psychological Well-Being since the COVID-19 Pandemic* | repeated cross-sectional association vs causal wording |

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
