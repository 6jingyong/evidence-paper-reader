# Real-paper evidence policy

Every real-paper test is a durable project evidence asset.

## Record first

Full paper audits must use the source-backed path under validation-runs/real-papers. A paper that only appears in a chat, temporary workspace, or untracked output does not count as repository evidence.

A named public source used only inside a benchmark may enter as benchmark-source evidence when its public source URL and benchmark judgment are preserved by the catalog builder. That is deliberately lower provenance than a full replay and must not be described as a completed paper audit.

The legacy fixture index exists only to preserve older work whose source/run metadata were not captured. Do not add new papers to the legacy path as a shortcut.

## One paper, many surfaces

Full replay, inventory stress, blind re-audit, model comparison, repeated stability, and future adversarial runs are test surfaces on one paper identity. They do not become multiple independent papers.

## Adoption claims

The generated EVIDENCE.md page is the source for factual project-adoption claims about tested papers. Source-backed papers can be traced to original sources and replay artifacts. Legacy fixtures demonstrate regression coverage but must not be described as if their missing source metadata had been reconstructed.

These assets demonstrate claim–evidence–reasoning auditing behavior. They must not be marketed as proof that the skill detects fraud, establishes misconduct, adjudicates scientific truth, or identifies dishonest authors. Even source-integrity cases support only the narrower statement that a documented provenance problem changes what evidence can safely carry a claim.

Protocol-ready blind cases are not completed blind-model results.

## Enforcement

The catalog builder discovers recorded rounds, named tiered benchmark sources, explicit benchmark-to-evidence mappings, legacy fixtures, blind benchmark membership, and durable blind runs. CI rejects stale catalogs, missing identities, duplicate counting through aliases, blind cases without recorded papers, missing legacy fixtures, or generated evidence pages that diverge from repository state.

Future paper-bearing benchmark formats must either reference an existing evidence identity or add their public sources to the catalog discovery/mapping contract. They must not create an untracked parallel paper list.
