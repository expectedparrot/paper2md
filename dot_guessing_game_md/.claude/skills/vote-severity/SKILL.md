---
name: vote-severity
description: Phase 4 — Run multi-model severity voting on confirmed issues. Writes votes.json next to each issue (append-only).
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Phase 4: Multi-Model Severity Voting

Run from the repo root. Requires investigated and deduplicated issues from Phases 2-3.

## Execute severity voting

Look for the roboree scripts path in the system prompt (it will say "roboree scripts are at: <path>"). Use that path:

```bash
python <r2-scripts-path>/vote_severity.py \
  --review-dir .review/ \
  --config .review/config.json
```

The script:
1. Finds all confirmed, canonical issues (using `dedup.json` if present)
2. Skips issues that already have `votes.json` (resumable)
3. Runs an edsl cross-product: issues x models (from config)
4. Writes `votes.json` next to each `issue.json`
5. Writes a top-level `.review/severity.json` summary

## Output

**Per-issue** — `votes.json` written next to `issue.json`:
```json
{
  "votes": [
    {"model": "claude-sonnet-4-6", "severity": "major", "reasoning": "..."},
    {"model": "gpt-4o", "severity": "major", "reasoning": "..."},
    {"model": "gemini-2.5-pro", "severity": "moderate", "reasoning": "..."}
  ],
  "consensus": "major",
  "agreement": 0.67,
  "voted_at": "<ISO timestamp>"
}
```

**Top-level** — `.review/severity.json`:
```json
{
  "issues": {
    "chunks/model-00-a3f2/undefined_symbols": {"severity": "major", "agreement": 0.67}
  },
  "summary": {"major": 3, "moderate": 5, "minor": 2},
  "voted_not_an_issue": ["chunks/intro-00-b7c1/logical_gaps"],
  "created_at": "<ISO timestamp>"
}
```

Issues voted `not_an_issue` are NOT moved or deleted — they simply have a `votes.json` with `"consensus": "not_an_issue"` and are listed in the `voted_not_an_issue` array.

## After completion

```bash
git add -A
git commit -m "review: severity voting — <M> major, <Mo> moderate, <Mi> minor"
```

Report: breakdown by severity, any issues rejected as not_an_issue.
