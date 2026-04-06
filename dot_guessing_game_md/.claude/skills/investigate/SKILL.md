---
name: investigate
description: Phase 2 — Investigate candidate issues. Writes investigation.json next to each issue.json with evidence and a confirm/reject verdict.
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Phase 2: Investigation

Run from the repo root. The paper source is in this same repo.

Read `.review/config.json` to find the paper commit SHA and manuscript path.

## Find candidate issues

Scan for all `issue.json` files that do NOT yet have an `investigation.json` next to them:

```
.review/chunks/<chunk-id>/<spotter>/issue.json    (from broad sweep)
.review/holistic/<slug>/issue.json                 (from holistic review)
```

Skip any directory that already has `investigation.json` (already investigated).

## For each candidate issue

Use the `investigate-issue` sub-agent or investigate directly.

### Manuscript investigation
- Grep for the key terms, symbols, and equation references mentioned in the issue
- Read related sections to check if the issue is addressed elsewhere (appendix, later section, footnote)
- Check cross-references and citations

### Code investigation (if `.review/config.json` shows `has_code: true`)
- Read analysis scripts to verify claimed results
- Check parameter values in code vs. manuscript
- Run scripts if possible to reproduce numbers

### Data investigation (if `.review/config.json` shows `has_data: true`)
- Verify sample sizes match claims
- Check that referenced data files exist

### Write the verdict

Write `investigation.json` **next to** the `issue.json` (in the same directory). Never move or modify `issue.json`.

**Confirmed**:
```json
{
  "verdict": "confirmed",
  "location": {"file": "<path>", "lines": [<start>, <end>]},
  "category": "<category>",
  "evidence": [
    {"searched_for": "<terms>", "scope": "<where>", "found": "<what>"}
  ],
  "suggested_fix": "<actionable suggestion>",
  "models_flagged": ["<model>"],
  "investigated_at": "<ISO timestamp>"
}
```

**Rejected**:
```json
{
  "verdict": "rejected",
  "rejection_reason": "<concrete explanation with line numbers or code locations>",
  "investigated_at": "<ISO timestamp>"
}
```

**Uncertain**:
```json
{
  "verdict": "uncertain",
  "notes": "<what was checked, why it's unclear>",
  "investigated_at": "<ISO timestamp>"
}
```

## After completion

```bash
git add -A
git commit -m "review: investigation — <C> confirmed, <R> rejected, <U> uncertain"
```

Report: number confirmed, number rejected, brief summary of the most significant confirmed issues.
