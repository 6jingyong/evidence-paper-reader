# Durable source-to-audit runs

This directory stores completed source-to-audit benchmark evidence.

A completed run must preserve:

- `run.json` — reviewer/model/runtime, source git head, case IDs, and isolation declaration
- `source-inputs/<case_id>.json` — canonical source identity, acquisition/normalization method, exact review-material SHA-256 and byte count
- `responses/<case_id>.json` — fresh ledger-v2 reviewer response
- `score.json` — hidden scorer output for exactly those responses

The normalized source text/PDF itself is **not** committed here by default. The durable record proves which bytes were reviewed through their cryptographic fingerprint without redistributing source material whose license may not permit repository inclusion.

Required isolation:

- fresh_context_per_case: true
- repository_answer_keys_accessible: false
- method: concrete description of how the reviewer was isolated

A run can cover a declared subset, but every case must already belong to source-to-audit-10 and have a source-backed paper identity.
