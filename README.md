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

## Repository layout

```text
.
├── LICENSE
├── README.md
└── evidence-paper-reader/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── references/
        ├── evidence-types.md
        ├── follow-up-boundaries.md
        └── pollution-patterns.md
```

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
