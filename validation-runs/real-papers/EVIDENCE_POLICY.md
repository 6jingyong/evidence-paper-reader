# Real-paper evidence policy

Every real-paper test is a durable project evidence asset.

## Record first

New paper tests must use the source-backed path under validation-runs/real-papers. A paper that only appears in a chat, temporary workspace, or untracked output does not count as repository evidence.

The legacy fixture index exists only to preserve older work whose source/run metadata were not captured. Do not add new papers to the legacy path as a shortcut.

## One paper, many surfaces

Full replay, inventory stress, blind re-audit, model comparison, repeated stability, and future adversarial runs are test surfaces on one paper identity. They do not become multiple independent papers.

## Adoption claims

The generated EVIDENCE.md page is the source for factual project-adoption claims about tested papers. Source-backed papers can be traced to original sources and replay artifacts. Legacy fixtures demonstrate regression coverage but must not be described as if their missing source metadata had been reconstructed.

Protocol-ready blind cases are not completed blind-model results.

## Enforcement

The catalog builder discovers recorded rounds, legacy fixtures, and blind benchmark membership. CI rejects stale catalogs, missing source-backed identities, blind cases without recorded papers, missing legacy fixtures, or generated evidence pages that diverge from repository state.

Future paper-bearing benchmark formats should reference source-backed recorded case IDs rather than creating parallel paper identities.
