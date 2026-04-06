---
name: review-paper
description: Run a full paper review pipeline (append-only). Builds a .review/ tree where each phase writes new files, never modifying existing ones.
argument-hint: [commit-sha]
user-invocable: true
---

# Full Paper Review Pipeline

You are running the complete paper review pipeline on the current repo's paper.

**Input**: `$ARGUMENTS` — optionally a commit SHA to pin the review to.

The review happens on a new branch in this repo. All review artifacts live in `.review/` as an append-only file tree — each phase writes new files, never modifying existing ones.

Execute each phase in order. After each phase, commit with the prescribed commit message. If any phase fails, stop and report the error clearly.

## Phase 0: Setup

Run `/setup-review $ARGUMENTS`

Creates a review branch, parses the manuscript, extracts the symbol table, and installs issue spotters into `.review/issue_spotters/`.

## Phase 1a: Broad Sweep

Run `/broad-sweep`

Runs the (chunks x issue_spotters) cross-product as an edsl survey. Each pair produces `issue.json` or `no_issue.json` in `.review/chunks/<chunk-id>/<spotter>/`.

## Phase 1b: Holistic Review

Run `/holistic-review`

Reads the full paper, writes a referee report, and creates `issue.json` files in `.review/holistic/<slug>/`.

## Phase 2: Investigation

Run `/investigate`

For each `issue.json` that lacks an `investigation.json`, investigates using full repo access and writes `investigation.json` with a confirm/reject/uncertain verdict.

## Phase 3: Deduplication

Run `/deduplicate`

Writes `.review/dedup.json` mapping confirmed issues to canonical representatives. No files are moved or modified.

## Phase 4: Severity Voting

Run `/vote-severity`

Writes `votes.json` next to each confirmed canonical issue, plus `.review/severity.json` summary.

## Phase 5: Draft Responses

Run `/draft-responses`

Writes `response.json` next to each confirmed canonical issue with recommended action and draft text.

## Phase 6: Publish

Run `/publish-review`

Walks the tree and generates `REVIEW.md`. Optionally creates GitHub Issues.

## After completion

Report to the user:
- Total issues found (by severity)
- Review branch name
- Link to REVIEW.md
- The append-only tree can be inspected with `find .review/ -name "*.json" | head -50`
