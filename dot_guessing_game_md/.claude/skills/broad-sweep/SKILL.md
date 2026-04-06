---
name: broad-sweep
description: Phase 1 — Run the chunks x issue_spotters cross-product to find candidate issues. Uses edsl for parallel LLM review.
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Phase 1: Broad Sweep

Run from the repo root. Requires `.review/config.json`, `.review/parsed/`, `.review/symbol_table.json`, and `.review/issue_spotters/` from Phase 0.

## How it works

The broad sweep runs a cross-product of **chunks x issue_spotters**:

- **Chunks**: The parsed manuscript is split into overlapping ~800-word windows
- **Issue spotters**: Named markdown files in `.review/issue_spotters/` describing what to look for

Each (chunk, spotter) pair is one scenario in the edsl survey. The result is either:
- `issue.json` — the spotter found something in that chunk
- `no_issue.json` — the spotter checked and found nothing

## Execute the broad sweep

Look for the roboree scripts path in the system prompt (it will say "roboree scripts are at: <path>"). Use that path:

```bash
python <r2-scripts-path>/broad_sweep.py \
  --parsed-dir .review/parsed/ \
  --symbol-table .review/symbol_table.json \
  --spotters-dir .review/issue_spotters/ \
  --output-dir .review/chunks/ \
  --config .review/config.json
```

## Output structure

```
.review/chunks/
  <chunk-id>/
    chunk.md                        # The chunk text
    mathematical_errors/
      issue.json   OR  no_issue.json
    undefined_symbols/
      issue.json   OR  no_issue.json
    logical_gaps/
      no_issue.json
    ...
```

Each `issue.json` contains:
```json
{
  "title": "<issue title>",
  "spotter": "<spotter_name>",
  "quoted_text": "<relevant quote>",
  "description": "<what's wrong>",
  "source_section": "<section file>",
  "chunk_index": 0,
  "created_at": "<ISO timestamp>"
}
```

## Resumability

The script checks for existing output files before running. If interrupted, re-running it will skip already-processed (chunk, spotter) pairs.

## After completion

Commit:
```bash
git add -A
git commit -m "review: broad sweep — <N> issues from <total> (chunk x spotter) pairs"
```

Report: number of issue spotters, number of chunks, total matrix size, and how many issues were found.
