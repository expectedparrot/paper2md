---
name: draft-responses
description: Draft author responses for each confirmed issue. Writes response.json next to each issue (append-only).
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Draft Author Responses

Run from the repo root. Requires severity-voted issues from Phase 4. The paper source is in this same repo.

## Find issues to respond to

Scan for directories that have `issue.json`, `investigation.json` (confirmed), and `votes.json` but do NOT yet have `response.json`. Use `.review/dedup.json` to process only canonical issues. Skip issues whose `votes.json` has `"consensus": "not_an_issue"`.

## For each confirmed issue

Read `issue.json`, `investigation.json`, and `votes.json`. Then, with full access to the repo, draft response options from the author's perspective:

### 1. Can the reviewer be wrong?
- Re-read the flagged text and surrounding context
- Check if the reviewer misunderstood the argument or missed context
- If wrong, draft a rebuttal with specific references

### 2. Is there a quick fix?
- A sentence or two added to the manuscript
- A clarifying footnote or table note
- Correcting a factual inaccuracy

### 3. Is there a substantive fix?
- Additional analysis or robustness check
- A missing methodological detail
- A new paragraph addressing a legitimate gap

### 4. Should the author acknowledge without fixing?
- Add to limitations section
- Note as future work

## Output

Write `response.json` next to the other files in the issue directory:

```json
{
  "recommended_action": "fix|rebut|acknowledge",
  "response_draft": "<draft text the author could use>",
  "manuscript_changes": [
    {"file": "<path>", "line": <N>, "description": "<what to change>"}
  ],
  "created_at": "<ISO timestamp>"
}
```

For fixes, be specific — describe the actual text change. For rebuttals, write a response-letter paragraph. For acknowledgments, draft a sentence for the limitations section.

Do NOT modify `issue.json`, `investigation.json`, or `votes.json`.

## After completion

```bash
git add -A
git commit -m "review: draft responses — <N> fix, <N> rebut, <N> acknowledge"
```

Report: for each issue, the recommended action and a one-line summary.
