---
name: setup-review
description: Phase 0 — Set up a paper review. Creates a review branch, parses the manuscript, extracts symbols, and installs issue spotters.
argument-hint: [commit-sha]
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Phase 0: Setup Review

**Input**: `$ARGUMENTS` — optionally a commit SHA to pin the review to.

You are running inside the paper's own git repo. The review will happen on a branch in this repo.

## Step 1: Create review branch and pin commit

1. Record the current HEAD SHA as `paper_commit` (or use the provided SHA if given).
2. Get the repo URL from `git remote get-url origin` (use "local" if no remote).
3. Create and switch to a new branch:
   ```bash
   git checkout -b review-$(date +%Y%m%d-%H%M%S)
   ```

## Step 2: Explore the repo

Explore the repo to understand its structure:
- What's in it? Just a manuscript, or also code/data/figures?
- Where is the manuscript? (look for `paper/`, `manuscript.md`, `main.tex`, `*.tex`, `*.md`, `*.docx`, `*.pdf`)
- What format is the manuscript?
- Is there analysis code? What language?
- Are there data files?

For arXiv URLs (if the user provides one containing `arxiv.org`):
- Extract the arXiv ID
- Check if an HTML version exists at `https://arxiv.org/html/{id}`
- Prefer the HTML version over PDF for better parsing quality

Create `.review/config.json`:
```json
{
  "paper_repo": "<url-or-local>",
  "paper_commit": "<sha>",
  "manuscript_path": "<path-to-main-file>",
  "manuscript_format": "tex|md|html|docx|pdf",
  "has_code": true|false,
  "has_data": true|false,
  "code_paths": ["code/", ...],
  "data_paths": ["data/", ...],
  "models": ["claude-sonnet-4-6", "gpt-4o", "gemini-2.5-pro"],
  "reviewed_at": "<ISO timestamp>"
}
```

## Step 3: Parse manuscript

Run the parse_document.py script to convert the manuscript to one-sentence-per-line markdown.

Look for the roboree scripts path in the system prompt (it will say "roboree scripts are at: <path>"). Use that path:

```bash
python <r2-scripts-path>/parse_document.py \
  --input <manuscript-path> \
  --output-dir .review/parsed/ \
  --symbol-table .review/symbol_table.json
```

The script handles:
- LaTeX: native section splitting (preserves raw LaTeX, no pandoc)
- HTML/docx/PDF: markdown conversion
- Sentence splitting (one sentence per line, preserving math blocks)
- Symbol table extraction (via edsl, or regex fallback)

## Step 4: Create review structure

```bash
mkdir -p .review/chunks .review/holistic
```

Verify that `.review/issue_spotters/` was created by the `r2` CLI launcher. If not, check the system prompt for the issue spotters path and copy them manually.

List the available issue spotters and tell the user they can customize them before running `/broad-sweep`:
```bash
ls .review/issue_spotters/
```

Create a `.gitignore` that excludes `.env`:
```bash
echo ".env" > .gitignore
```

## Step 5: Write overview.json

Write `.review/overview.json` summarizing what was found:
```json
{
  "manuscript_format": "<format>",
  "sections_parsed": <N>,
  "symbols_extracted": <N>,
  "has_code": true|false,
  "has_data": true|false,
  "issue_spotters": ["<list of spotter names>"]
}
```

## Step 6: Commit

```bash
git add -A
git commit -m "review: setup for <repo>@<sha>"
```

Report what was found: manuscript format, whether code/data exist, number of sections parsed, number of symbols extracted, and the list of issue spotters available.
