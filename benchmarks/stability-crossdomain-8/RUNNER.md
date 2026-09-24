# Cross-Domain Stability 8 — isolated runner

The benchmark itself does not assume a particular model API.

`run_reviewer.py` starts **one external reviewer process per packet**. Before launch it also materializes a per-packet prompt file. The reviewer process receives one packet, one prompt, and must create exactly one JSON response.

Supported command placeholders:

- `{packet}` — raw packet path
- `{prompt}` — self-contained prompt path
- `{output}` — response JSON path
- `{packet_id}`
- `{case_id}`
- `{repeat}`

The same values are also exported as:

- `EPR_PACKET_ID`
- `EPR_CASE_ID`
- `EPR_REPEAT`
- `EPR_PACKET_PATH`
- `EPR_PROMPT_PATH`
- `EPR_OUTPUT_PATH`

The prompt contains the packet plus the public response contract. It does **not** contain reference expectations or scorer output. Use `--include-skill` when the external reviewer does not already have the benchmark skill installed in its fresh execution context.

## Isolation rule

The runner never sends two packets to the same reviewer process.

The external command is responsible for creating a genuinely fresh model context. A command that keeps conversational/model state between invocations is not a valid stability experiment.

Run with the same:

- model
- skill version
- system/developer instructions
- reasoning/effort setting
- response format
- temperature/sampling policy

across all repeats.

## Example adapter contract

A wrapper called `review_one.sh` might receive:

```bash
review_one.sh "{prompt}" "{output}"
```

and internally launch your preferred model runner in a fresh process.

The wrapper must write JSON matching `response-format.md` to the requested output path.

Then:

```bash
python benchmarks/stability-crossdomain-8/generate_runs.py
python benchmarks/stability-crossdomain-8/run_reviewer.py \
  --command './review_one.sh {prompt} {output}' \
  --status-file runs/status.json
python benchmarks/stability-crossdomain-8/score_repeats.py runs/responses/
```

For a reviewer that needs the skill text in the prompt:

```bash
python benchmarks/stability-crossdomain-8/run_reviewer.py \
  --include-skill \
  --command './review_one.sh {prompt} {output}'
```

## Single-packet smoke test

Before committing to 40 runs, use:

```bash
python benchmarks/stability-crossdomain-8/generate_runs.py
python benchmarks/stability-crossdomain-8/run_reviewer.py \
  --limit 1 \
  --command './review_one.sh {prompt} {output}' \
  --status-file runs/smoke-status.json
```

Inspect the generated prompt and response. Once one packet passes end-to-end, remove `--limit 1` and run the full 40-job matrix.

## Resume

A valid existing response can be retained:

```bash
python benchmarks/stability-crossdomain-8/run_reviewer.py \
  --command './review_one.sh {prompt} {output}' \
  --resume
```

Malformed/incomplete existing JSON is deleted and rerun.

## Dry run

Inspect the exact jobs without launching a model:

```bash
python benchmarks/stability-crossdomain-8/run_reviewer.py \
  --command './review_one.sh {prompt} {output}' \
  --limit 3 \
  --dry-run
```

## Why this remains runner-neutral

Work, Codex, ChatGPT-hosted tools, local model servers, and other agent systems expose different ways to open fresh contexts.

The benchmark should measure the reviewer, not hard-code one vendor integration.

The only required interface is:

```text
one fresh process
+ one prompt
+ one JSON response
```

The packet path remains available separately for wrappers that prefer direct file access.

The repository therefore supplies the experiment protocol and scorer while the surrounding platform supplies context isolation.
