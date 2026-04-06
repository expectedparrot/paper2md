---
name: publish-review
description: Phase 6 — Generate the REVIEW.md report by walking the append-only review tree. Optionally create GitHub Issues.
argument-hint: [--no-github-issues]
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Phase 6: Publish Review

Run from the repo root. Requires the completed review tree in `.review/`.

## Step 1: Generate REVIEW.md and REVIEW.html

Look for the roboree scripts path in the system prompt (it will say "roboree scripts are at: <path>"). Use that path:

```bash
python <r2-scripts-path>/build_report.py \
  --review-dir .review/ \
  --config .review/config.json \
  --output REVIEW.md
```

Then generate the styled HTML report:

```bash
python <r2-scripts-path>/build_html_report.py \
  --review-dir .review/ \
  --config .review/config.json \
  --output REVIEW.html
```

Both scripts walk the append-only tree:
- Find all confirmed, canonical issues (via `dedup.json`)
- Read `issue.json` + `investigation.json` + `votes.json` + `response.json` for each
- Generate a structured report grouped by severity

The HTML version is self-contained (no external dependencies) with collapsible issue cards, severity badges, agreement bars, and model vote details. It prints well too.

## Step 2: Create GitHub Issues (unless --no-github-issues)

Check if `$ARGUMENTS` contains `--no-github-issues`. If not, create issues on the repo.

Read `paper_repo` from `.review/config.json`. For each confirmed canonical issue with severity != not_an_issue:

```bash
gh issue create --repo <paper_repo> \
  --title "<severity>: <title>" \
  --body "<issue description with evidence>" \
  --label "<severity>,<spotter>"
```

All links should be pinned to the `paper_commit` SHA from config.

**Important**: Ask the user for confirmation before creating GitHub Issues.

## Step 3: Final commit

```bash
git add -A
git commit -m "review: complete"
```

Report: link to REVIEW.md, number of GitHub Issues created (if any).
