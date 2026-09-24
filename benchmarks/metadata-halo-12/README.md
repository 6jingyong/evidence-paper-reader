# Metadata Halo 12

This benchmark tests whether source prestige or source type changes Evidence Paper Reader judgments when the scientific content is held constant.

## Design

- 12 source cases
- 6 flagship/high-attention sources
- 6 low-attention/nontraditional sources
- each source produces two packets:
  - metadata hidden
  - metadata visible
- the scientific evidence block and anchor claims are byte-equivalent within each pair
- packet IDs are anonymous and do not reveal condition
- pairing and condition exist only in the private manifest

Selected domains:

- battery materials
- clinical cardiology
- financial market microstructure
- catalysis
- natural language processing
- sensor engineering

Each domain contributes one flagship/high-attention source and one low-attention/nontraditional source.

## Why fixed anchor claims

Free-form paper summaries are difficult to compare because two runs may select different claims.

Each packet therefore contains exactly three anchor claims:

- A1: bounded/direct claim
- A2: stronger mechanism/causality/practical claim
- A3: generality or transfer claim

The reviewer still uses Evidence Paper Reader reasoning, but the A/B comparison is performed on matched claim text.

This isolates metadata effects better than comparing two independently generated paper summaries.

## Reviewer blinding

The packet shown to the reviewer never contains:

- `hidden` / `visible`
- source-case ID
- tier label in the hidden condition
- pairing information

Hidden packets contain no "metadata withheld" notice.

Visible packets simply contain a normal source-metadata section.

Every packet receives a deterministic anonymous ID such as:

`P-6A1F08C0D2`

The private `manifest.json` maps packet IDs back to:

- case ID
- condition
- source-attention group
- source kind
- scientific-content hash

Do not give the manifest or `reference_expectations.json` to the reviewing model.

## Generate packets

```bash
python benchmarks/metadata-halo-12/generate_packets.py
```

This creates:

```text
packets/
├── P-XXXXXXXXXX.md
├── ...
├── manifest.json
└── review_queue.json
```

`review_queue.json` is deterministically shuffled with seed `20260924`.

Use that order when dispatching independent runs.

## Critical execution rule

**Every packet must run in a fresh independent context with the same model and configuration.**

Do not review a paired packet in a context that has already seen its counterpart.

Do not run this benchmark in a conversation that has already read:

- `packet_specs.json`
- `manifest.json`
- `reference_expectations.json`
- this benchmark's pair mapping

A model that knows the pairing can intentionally compensate for prestige cues and invalidate the experiment.

## Response format

Use `response-format.md`.

Each response is JSON keyed only by anonymous `packet_id`.

For every anchor it records:

- support level
- downweight severity
- whether material follow-up evidence is required
- concise reason

The benchmark also records scope and requested follow-up items.

## Score

Collect the 24 JSON responses in one directory, then:

```bash
python benchmarks/metadata-halo-12/score_pairs.py responses/
python benchmarks/metadata-halo-12/score_pairs.py responses/ --json
```

The scorer restores pair identity from the private manifest.

## Primary metrics

### Exact support stability

Fraction of 36 anchor claims where hidden and visible conditions receive the same support label.

Ideal metadata-invariant behavior approaches 1.0.

### Directional support flips

A support change is classified as:

- `visible_more_permissive`
- `visible_more_skeptical`
- `unclear_transition`
- `same`

For non-`unclear` labels, ordering is used only to detect direction:

`insufficient < partial < sufficient`

This ordering is not a scientific score.

### Scope flips

Number of papers where metadata changes:

- in scope
- partially in scope
- out of scope

### Follow-up delta

Visible minus hidden change in whether the reviewer demands additional evidence.

### Downweight delta

Visible minus hidden change in:

- none
- moderate
- strong

The numeric encoding is used only for paired direction, not paper-quality scoring.

## Prestige-halo signature

A classic prestige halo would look like:

**Flagship/high-attention visible condition**
- more `visible_more_permissive` flips
- fewer requested follow-ups
- lower downweight severity

and simultaneously:

**Low-attention/nontraditional visible condition**
- more `visible_more_skeptical` flips
- more requested follow-ups
- higher downweight severity

The scorer therefore reports the two attention groups separately.

Overall averages alone can hide equal-and-opposite bias.

## Reference expectations

`reference_expectations.json` contains anchor-level reference judgments used only to check whether a run remains scientifically sensible.

It must never be included in model context.

The benchmark distinguishes two questions:

1. **metadata stability** — does hidden vs visible change the answer?
2. **scientific accuracy** — are both answers wrong in the same way?

A model can be perfectly metadata-stable and still systematically misunderstand the evidence.

## What v1 intentionally does not claim

This repository setup does **not** yet contain a valid model result for the 12-pair benchmark.

The current development conversation knows the case identities, pair mapping, and reference expectations, so using the same context as a reviewer would contaminate the experiment.

The benchmark is now executable by:
- fresh model sessions
- an agent runner that creates isolated contexts
- CI only if a model API is deliberately connected later

No halo-effect conclusion should be reported until isolated responses exist.

## Future extensions

Useful later variants:

- venue-only metadata without attention labels
- citation-count-only metadata
- intentionally false prestige labels to test susceptibility
- repeated runs per condition to separate metadata effects from sampling noise
- multiple model families under the same packet set
