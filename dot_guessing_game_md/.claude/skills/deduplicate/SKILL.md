---
name: deduplicate
description: Phase 3 — Deduplicate confirmed issues by writing a dedup.json mapping file. No files are moved or modified.
user-invocable: true
allowed-tools: Read, Write, Glob, Grep
---

# Phase 3: Deduplication

Run from the repo root. Requires investigated issues from Phase 2.

## Process

1. Scan for all directories that have both `issue.json` and `investigation.json` with `"verdict": "confirmed"` (or `"uncertain"`).

2. For each confirmed issue, read `issue.json` (title, quoted_text, description, spotter) and `investigation.json` (location, category).

3. Cluster by:
   - **Location proximity**: issues referencing lines within +/-10 lines of each other in the same file
   - **Topic similarity**: issues about the same symbol, equation, or claim
   - **Same spotter on overlapping chunks**: the same spotter firing on adjacent chunks likely found the same issue

4. For each cluster, pick a **canonical** representative (the one with the best evidence or most specific location).

## Output

Write a single file: `.review/dedup.json`

```json
{
  "clusters": [
    {
      "canonical": "chunks/intro-00-a3f2bc/undefined_symbols",
      "members": [
        "chunks/intro-00-a3f2bc/undefined_symbols",
        "chunks/intro-01-b7c1de/undefined_symbols"
      ],
      "reason": "Same issue: undefined kappa, overlapping chunks"
    },
    {
      "canonical": "holistic/missing-robustness",
      "members": ["holistic/missing-robustness"],
      "reason": "Singleton"
    }
  ],
  "cross_references": {
    "chunks/model-00-c4d5/methodology_errors": ["chunks/results-00-e6f7/overclaiming"]
  }
}
```

**Important**: Paths in `dedup.json` are relative to `.review/`. The `canonical` path is used by downstream phases to identify which issues to process.

Do NOT modify or move any `issue.json` or `investigation.json` files. The dedup mapping is a separate overlay.

## After completion

```bash
git add -A
git commit -m "review: deduplication — <N> canonical issues from <M> total confirmed"
```

Report: how many canonical issues remain, how many were merged, how many have cross-references.
