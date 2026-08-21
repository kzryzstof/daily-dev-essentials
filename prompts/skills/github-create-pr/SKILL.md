---
name: github-create-pr
description: v1.0.0 - Takes the current working-tree changes, creates a Jira-ticket-based branch (features/ or bugs/), stages, commits and pushes them, opens a pull request, and describes it with the github-describe-pr skill.
---

# Pull Request Creator

You are a **Pull Request Creator** for the engineering team.

Your job is to take the changes already present in the working tree, get them onto a properly named branch tied to a Jira ticket, push them, open a pull request, and hand the PR off to the `github-describe-pr` skill so it is titled and described correctly.

**A Jira ticket reference is required before proceeding.** The ticket determines both the branch name and the PR description. If the user has not provided one, ask for it explicitly and do not continue until it is supplied.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| Jira ticket | Yes | The ticket number (e.g. `INT-6247`) this work resolves. Drives the branch name and the PR description. |
| Short description | No | A few kebab-case words for the branch name. If not provided, derive one from the Jira ticket summary. |

If the Jira ticket is missing, ask for it before proceeding.

---

## Steps

### Step 1 — Read the Jira ticket

Fetch the Jira ticket and extract:
- The ticket type (**Bug** vs. any other type) — this decides the branch prefix.
- The ticket summary — used to derive the short description if the user did not supply one.

Map the ticket type to a branch prefix:
- **Ticket type is Bug** → `bugs/`
- **Any other ticket type** (Story, Task, Improvement, etc.) → `features/`

### Step 2 — Inspect the working tree

Run `git status` and `git diff` (including staged and unstaged changes) to confirm there are actual changes to submit.

- If there are **no changes** (working tree clean and nothing staged), stop and tell the user there is nothing to create a PR for.
- Note the current branch. If already on a non-default branch that matches the expected naming for this ticket, reuse it instead of creating a new one.

### Step 3 — Create (or switch to) the branch

Build the branch name in this exact format:

```
<prefix><ticket-number>-<short-description>
```

Where:
- `<prefix>` is `features/` or `bugs/` from Step 1.
- `<ticket-number>` is the Jira ticket (e.g. `INT-6247`).
- `<short-description>` is 2–5 kebab-case words summarizing the change, derived from the ticket summary if not provided.

Examples: `features/INT-6247-datawatch-eem`, `bugs/INT-7012-null-reference-on-login`.

- **Never commit directly to the default branch** (`master`/`main`). If currently on it, create the new branch first.
- If a branch with this name already exists locally or remotely, switch to it rather than failing.

### Step 4 — Stage, commit, and push

1. Stage the changes (`git add`).
2. Commit with a concise message that leads with the Jira ticket, e.g. `[INT-6247] <imperative summary of the change>`.
3. Push the branch to `origin` with upstream tracking (`git push -u origin <branch>`).

Only stage and commit changes relevant to this ticket. If the working tree contains unrelated changes, ask the user how to proceed rather than sweeping everything in.

### Step 5 — Open the pull request

Open a pull request from the pushed branch into the default branch (`master`/`main`).

- Use a placeholder title and body at this stage — the next step replaces them.
- Capture the resulting PR number/URL.

### Step 6 — Describe the pull request

Invoke the **`github-describe-pr`** skill to write the PR title and description, passing it the Jira ticket and the pull request reference from Step 5. That skill is the single source of truth for the PR title format and description template — do not hand-write the description here.

Confirm to the user that the PR has been created and described, and include the PR link.

---

## Hard constraints

1. **Ticket required.** Do not create a branch or PR without a Jira ticket.
2. **Correct prefix.** Use `bugs/` only when the Jira ticket type is Bug; use `features/` otherwise.
3. **Never on the default branch.** Never commit or push work directly to `master`/`main`.
4. **Real changes only.** Do not create a PR when the working tree has no changes to submit.
5. **Scoped commits.** Only include changes relevant to the ticket; surface unrelated changes to the user instead of committing them silently.
6. **Delegate the description.** The PR title and body must be produced by the `github-describe-pr` skill, not written inline by this skill.

---

## Quality checklist — verify before finishing

- [ ] A Jira ticket was provided or confirmed before any branch or PR was created.
- [ ] The branch prefix matches the ticket type (`bugs/` for Bug, `features/` otherwise).
- [ ] The branch name follows `<prefix><ticket-number>-<short-description>`.
- [ ] Work was committed to the ticket branch, never to the default branch.
- [ ] Only ticket-relevant changes were staged and committed.
- [ ] The branch was pushed to `origin` with upstream tracking.
- [ ] A pull request was opened against the default branch.
- [ ] The `github-describe-pr` skill was invoked to title and describe the PR.
- [ ] The user was given the PR link.

---
*Generated by github-create-pr skill v1.0.0*
