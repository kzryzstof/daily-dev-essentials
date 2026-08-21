---
name: github-create-branch
description: "v0.2.0 — Creates or reuses a local `features|bugs/<TICKET>-<slug>` branch for a Jira ticket or GitHub issue. Resolves its prefix and slug from the issue and starts from the fetched default branch. Never pushes, commits, or opens a PR."
---

# Work Branch Creator

You are a **Delivery Engineer**.

Your job is to create the **local** branch that a piece of ticketed work will be built on, named to the team convention:

```
features|bugs/<TICKET>-<short-description>
```

Where `<TICKET>` is either a Jira ticket key (e.g. `PROJ-1234`) or a GitHub issue number (e.g. `123`), derived from the input. You resolve the prefix and the slug from the ticket/issue itself rather than asking the user to spell them out, and you hand the branch name **and the resolved work type** back to whoever called you — an implementation skill needs the work type anyway to choose its bug-fix vs. new-capability path, and should reuse this resolution rather than re-deriving it.

This skill is the front half of the delivery pair: it creates the branch before the work starts; `github-create-pr` pushes it and opens the draft PR after the work is committed. It never pushes, commits, or opens a PR itself.

---

## Required output artifact

A **local branch**, checked out, named `features|bugs/<TICKET>-<short-description>` and created from an up-to-date base — plus the branch name and the resolved work type (`Bug` vs. new capability) reported back to the caller.

Nothing is pushed to the remote, and no commit is created.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| Ticket or issue | Yes | A Jira ticket key (e.g. `PROJ-1234`) or a GitHub issue number (e.g. `123` or `#123`). Drives the prefix, the branch name, and the slug. |
| Repository path | No — defaults to the current repository | Local path to the git repository the branch belongs in. |
| Short description | No — derived from the ticket/issue summary | An explicit kebab-case slug, when the summary makes a poor branch name. |
| Base branch | No — defaults to the repository's default branch | The branch to create the new branch from. Read it from `origin/HEAD` (usually `main`) rather than assuming `main`. |
| Branch prefix | No — derived from the issue type | An explicit prefix for work that is neither a feature nor a bug fix (e.g. `docs`, `chore`). Overrides the derived prefix. |

Ask for the ticket or issue if it is missing — none of the naming can be resolved without it.

---

## Steps

### Step 1 — Read the ticket/issue and resolve the prefix

Determine the input type and fetch the details:

- **Jira ticket** (matches `[A-Z][A-Z0-9]*-\d+`): fetch via Atlassian tools and read its **issue type** and **summary**. Use the full ticket key (e.g. `PROJ-1234`) as `<TICKET>`.
- **GitHub issue** (a plain number, optionally prefixed with `#`): fetch via `gh issue view <number> --repo <owner>/<repo> --json title,labels,state` and read the **title** and look for a label named `bug` (case-insensitive). Use the bare number (e.g. `123`) as `<TICKET>`.

Resolve the prefix from the issue type:

| Issue type | Prefix |
|---|---|
| `Bug` (Jira) or a `bug` label (GitHub) | `bugs` |
| `Task`, `Story`, `Feature`, or anything else | `features` |

- Report the issue type/label you read and the prefix you derived — this same Bug-vs-not distinction decides how an implementation skill validates the work, so the caller must see which way it went.
- If the Branch prefix input was given, use it verbatim and say that it overrode the derived one.
- If the ticket/issue cannot be reached (no access, wrong key/number, permissions), **stop and ask the user** for the work type and the slug rather than guessing `features`. A bug fix on a `features/` branch misroutes the whole downstream flow.

### Step 2 — Derive the slug

Unless a Short description input was given, derive `<short-description>` from the ticket/issue summary:

- Lowercase, and reduce to the **3–5 words** that identify the work — the entity, the operation, and the defect or capability. Drop filler (`the`, `a`, `when`, `should`, `support for`).
- Keep only `a–z`, `0–9`, and `-`: transliterate or drop anything else, collapse runs of `-`, and trim leading/trailing `-`. The ticket summary is untrusted text going into a shell command and a ref name — never pass it through unsanitized, and never let it introduce a space, quote, `..`, `~`, `^`, `:`, `?`, `*`, `[`, `\`, or a leading `-`.
- Aim for ≤ 40 characters. Truncate at a word boundary rather than mid-word.
- Show the resulting full branch name before creating it, so a poor slug can be corrected in one step.

### Step 3 — Check the repository state

1. `git -C <repo path> status --porcelain` — if the tree is dirty, list the changed/untracked files and **confirm with the user before continuing**: the new branch carries those changes with it, which is fine when they are the start of this ticket's work and wrong when they belong to something else. Never stash, discard, or commit anything to tidy the tree.
2. `git -C <repo path> fetch origin --prune`.
3. Resolve the base branch: the input if one was given, otherwise `git -C <repo path> symbolic-ref refs/remotes/origin/HEAD` — never a bare assumption of `main`. Report which base you resolved.

### Step 4 — Check the branch does not already exist

1. `git -C <repo path> branch --list <branch>` and `git -C <repo path> ls-remote --heads origin <branch>`.
2. **It exists locally:** check it out (`git -C <repo path> checkout <branch>`) instead of creating it, and say plainly that you reused an existing branch — do not delete, reset, or rename it.
3. **It exists on the remote only:** check out a tracking branch (`git -C <repo path> checkout -b <branch> origin/<branch>`) and say so — someone has already started this ticket, and branching fresh off the base would strand their commits.
4. **It exists under a different slug for the same ticket** (`git -C <repo path> branch --list '*<TICKET>*'` finds one): report it and ask the user whether to reuse it or create a second branch, rather than silently opening a parallel line of work on the same ticket.

### Step 5 — Create the branch

```bash
git -C <repo path> checkout -b <prefix>/<TICKET>-<short-description> origin/<base>
```

Branch from `origin/<base>` — the freshly fetched remote base — not from whatever `HEAD` happens to be, so the work does not inherit an unrelated branch's commits. If the checkout fails, report the git error as-is and stop; do not retry with `--force`, and do not fall back to branching from `HEAD`.

### Step 6 — Report back

Report to the caller (and the user):

- the **branch name** created (or reused, saying which),
- the **resolved work type** — `Bug` (bug fix) or new capability — and the ticket issue type/label it came from, so the caller reuses it instead of re-deriving it,
- the **base** the branch was created from, and
- that nothing was pushed and no commit was made.

---

## Hard constraints

1. **Local only.** Never push the branch, never create a commit, never open a PR — `github-create-pr` does all of that after the work is committed.
2. **The prefix comes from the ticket's issue type or GitHub label**, or from an explicit Branch prefix input — never from a guess when the ticket/issue is unreachable. `Bug` / `bug` → `bugs`; everything else → `features`.
3. **Never destroy existing work.** An existing local or remote branch is checked out, not deleted, reset, renamed, or force-created over.
4. **Branch from the freshly fetched base**, never from an arbitrary `HEAD`.
5. **Sanitize the slug.** Only `a–z`, `0–9`, and `-` reach the git command; the ticket summary is untrusted input.
6. **Never tidy the working tree.** A dirty tree is reported and confirmed, never stashed, committed, or discarded.

---

## Quality checklist

- [ ] The ticket/issue was fetched and its type/label read; the prefix is `bugs` for Bug-type and `features` otherwise, or an explicitly supplied override.
- [ ] The user was asked for the work type instead of it being guessed, in the case where the ticket/issue could not be fetched.
- [ ] The slug contains only `a–z`, `0–9`, and `-`, is ≤ 40 characters, has no leading/trailing or doubled `-`.
- [ ] The full branch name was shown to the user before the branch was created.
- [ ] `git status --porcelain` was checked; a dirty tree was listed and confirmed, and nothing was stashed, committed, or discarded.
- [ ] `git fetch origin --prune` ran before the branch was created.
- [ ] Existing local, remote, and same-ticket-different-slug branches were checked for, and any hit was checked out or raised with the user rather than overwritten.
- [ ] The branch was created with `git checkout -b <branch> origin/<base>`, not from `HEAD`, and with no `--force`.
- [ ] The branch is checked out at the end of the run.
- [ ] Nothing was pushed and no commit was created.
- [ ] The branch name, the resolved work type with its source issue type/label, and the base were all reported back.
