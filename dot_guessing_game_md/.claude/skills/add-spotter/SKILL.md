---
name: add-spotter
description: Add a custom issue spotter for the paper review. Describe what to look for and this will create the spotter file.
argument-hint: <description of what to look for>
user-invocable: true
allowed-tools: Read, Write, Glob
---

# Add Issue Spotter

**Input**: `$ARGUMENTS` — a description of what the spotter should look for (e.g., "p-hacking", "selection bias", "missing confidence intervals").

## Instructions

1. Read the user's description from `$ARGUMENTS`.

2. Derive a short slug name from the description (e.g., "p-hacking" becomes `p_hacking`, "selection bias" becomes `selection_bias`). Use lowercase with underscores, no spaces.

3. Check if `.review/issue_spotters/` exists. If not, create it.

4. Check if a spotter with this name already exists. If so, tell the user and ask if they want to overwrite.

5. Write a new spotter file to `.review/issue_spotters/<slug>.md` following this format:

```markdown
# <Title>

Look for <concise description of what to check for>.

Pay special attention to:
- <specific thing to look for>
- <specific thing to look for>
- <specific thing to look for>
- <specific thing to look for>
- <specific thing to look for>
```

The spotter should be:
- **Specific**: Give concrete examples of what counts as a finding
- **Actionable**: Each bullet should be something a reviewer can check
- **Scoped**: Focus on one category of issue, not everything at once

6. List the current spotters in `.review/issue_spotters/` so the user can see what's active.

7. Tell the user the spotter will be used in the next `/broad-sweep` run.
