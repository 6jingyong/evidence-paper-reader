# Output contract

This is the manual rendering fallback and the canonical Markdown reference. When Python is available, prefer `scripts/render_audit.py` with `references/audit-ledger-format.md` so the model does not spend context or attention on formatting.

Use this exact top-level section order.

# reader-side paper audit

## 1. reader conclusion
Start with:
- `scope status: in scope | partially in scope | out of scope`
- `evidence viability: auditable | partially auditable | non-auditable`
- `viability flags: none | <one or more controlled flags from evidence-viability.md>`
- `paper type: ...`

Then write 3 to 6 sentences covering:
- what is most worth keeping
- what should be downweighted first
- whether the paper is mainly useful as result reference, method reference, inspiration, or low-priority material

## 2. core claims

For `auditable` material, list 3 to 5 sequential claims. For `partially auditable` material, list only the 1 to 5 claims whose evidence chain can actually be reconstructed.

### claim 1
- content: ...
- claim type: observational | methodological | mechanistic | performance | generality | intervention
- conclusion strength: weak | medium | strong

Repeat sequentially.

For an out-of-scope or `non-auditable` source, use:
`not applicable — <reason>`

## 3. evidence and support

Use the same claim numbers as section 2.

### claim 1
- evidence type: <one or more controlled labels from evidence-types.md>
- evidence provenance: paper-local | external citation | mixed
- evidence nodes: E1 | E1 + E2 | ...
- upstream claims: none | C1 | C1 + C2 | ...
- evidence dependence: single-source | shared-source convergence | partially independent convergence | independent convergence | unclear
- source location: <section/figure/table/appendix/page or location unavailable>
- support level: sufficient | partial | insufficient | unclear
- reason: ...
- external dependency: none | <cited work title; DOI only if verified/available; why it matters>

For an out-of-scope or `non-auditable` source, use:
`not applicable — <reason>`

## 4. what is usable

Use these exact subheadings:

### usable results

### usable methods or design

### usable materials or documentation

Only include content demonstrated, reported, or documented by the paper.

## 5. what to downweight

Use these exact subheadings:

### worth noticing but should be downweighted

### should be treated cautiously or ignored

Use concrete reasons.

Do not add adequately handled methodological risks merely to show that they were noticed.

## 6. value breakdown

Give exactly one line each:
- result value: high | medium | low | unclear
- method value: high | medium | low | unclear
- theory or insight value: high | medium | low | unclear
- research design value: high | medium | low | unclear
- material or documentation value: high | medium | low | unclear

## 7. uncertainty and follow-up

List the most important unresolved limits.

If a cited external paper is structurally necessary:
1. name it
2. include DOI only if present in inspected material or verified through an authoritative lookup
3. explain why it matters
4. suggest reading/uploading it next

If no structurally necessary external dependency exists, say so.

## Writing discipline

Prefer short declarative sentences.

Useful patterns:
- `the paper shows ... but does not establish ...`
- `usable content is limited to ...`
- `the main overreach is ...`

Avoid generic verdicts such as:
- `high-quality paper`
- `deep analysis`
- `meaningful study`

Do not score the paper.
Do not simulate editorial peer review.
