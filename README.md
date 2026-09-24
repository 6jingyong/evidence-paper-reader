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
│   │   └── resnet-smoke-audit.md
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

The repository includes a zero-dependency Python validator and regression tests. The smoke fixture is a reader-side audit of **Deep Residual Learning for Image Recognition** (He et al., 2015/2016), chosen because it exercises benchmark evidence, method claims, mechanistic interpretation, generality overreach, and source-location tracking.

Run locally with:

```bash
python -m unittest discover -s tests -v
python tests/validate_audit.py tests/fixtures/resnet-smoke-audit.md
```

The tests verify, among other things, that:

- the seven output sections are present exactly once and in order
- in-scope audits contain 3-5 sequential core claims
- claim/support fields use controlled values
- unknown evidence labels are rejected
- `literature citation` cannot be labeled `paper-local`
- `external citation` or `mixed` provenance requires a named external dependency
- the real-paper smoke fixture satisfies the contract

GitHub Actions runs the same checks on pushes and pull requests.

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
