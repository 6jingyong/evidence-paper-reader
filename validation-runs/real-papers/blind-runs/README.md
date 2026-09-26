# Durable blind-review runs

This directory is the permanent home for completed isolated blind re-audits.

A local benchmark response directory is not project evidence until it is copied here with enough provenance to review how it was produced.

Each completed run uses:

- run.json — reviewer/model/runtime identity, source git head, case list, and explicit isolation declaration
- responses/<case_id>.json — one fresh-context response per paper
- score.json — hidden-scorer output for exactly those responses

Required isolation declaration:

- fresh_context_per_case: true
- repository_answer_keys_accessible: false
- method: a concrete description of how isolation was achieved

A completed run may cover all ten cases or a declared subset. Every case must already be a source-backed paper in validation-runs/real-papers and a member of blind-real-paper-10.

Do not commit a run generated from the same contaminated development context that authored or inspected the answer key.

Multiple reviewer runs are preserved side by side. They are additional test surfaces on the same paper identities, not additional independent papers.
