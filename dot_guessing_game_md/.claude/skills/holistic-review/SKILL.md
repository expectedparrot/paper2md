---
name: holistic-review
description: One-shot holistic referee review of the full paper. Issues are written to .review/holistic/ as append-only issue.json files.
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, WebFetch
---

# Holistic Referee Review

Run from the repo root. Requires `.review/config.json` and `.review/parsed/` from Phase 0. Can run before, after, or concurrently with the broad sweep.

## Step 1: Read the full paper

Read all parsed sections in order to build a complete picture of the paper. If a PDF is available in the repo, read that too for figures and tables.

## Step 2: Write a referee report

Write a structured referee report to `.review/holistic_report.md` in the voice of a knowledgeable, constructive journal referee. The report should cover:

### Summary (1 paragraph)
Summarize what the paper does, its main contribution, and key findings.

### Overall assessment
- **Importance**: Is this an important question? Does the paper make a meaningful contribution?
- **Novelty**: What is genuinely new vs. incremental?
- **Positioning**: Is the paper well-positioned relative to the literature? Are key references missing?

### Major concerns
Issues that would need to be addressed before publication.

### Minor concerns
Issues that improve the paper but don't block publication.

### Questions for the authors
Specific questions a referee would ask.

## Step 3: Parse issues from the report

Extract each concern (major and minor) from the holistic report and create issue directories in `.review/holistic/`:

```
.review/holistic/
  <issue-slug>/
    issue.json
```

Each `issue.json`:
```json
{
  "title": "<issue title>",
  "spotter": "holistic",
  "source_section": "<most relevant section file>",
  "quoted_text": "<most relevant quote from the manuscript>",
  "description": "<description from the referee report>",
  "holistic_severity": "major|minor",
  "created_at": "<ISO timestamp>"
}
```

Use descriptive slugs for directory names (e.g., `single-llm-dependence`, `missing-robustness-checks`).

## Step 4: Commit

```bash
git add -A
git commit -m "review: holistic review — <N> issues (<M> major, <Mi> minor)"
```

Report: the full referee report summary, number of issues extracted.
