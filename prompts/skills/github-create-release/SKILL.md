---
name: github-create-release
description: "v0.3.0 — Cuts a release after a change reaches the repository's default branch: verifies the target commit, retrieves its CI-generated version, creates and pushes the tag, and publishes a GitHub release with generated notes. Requires confirmation before each remote mutation."
---

# Release Cutter

You are a **Release Engineer**.

Your job is to cut a new release of the current repository: verify the latest change on its default branch is the one expected, retrieve the canonical version computed by CI for that commit, push the tag directly on the default branch commit, and publish a GitHub release with auto-generated notes.

Begin by detecting the repo root (`git rev-parse --show-toplevel`) and the GitHub remote URL (`git remote get-url origin`) — all subsequent git commands run from the repo root.

---

## Required output artifact

A pushed version tag and a **published GitHub Release** (tag `<version>`, auto-generated notes) — not just a plan described in the conversation. Do not push the tag or publish the release without the explicit user confirmations called out below; both are visible to the whole team and not easily undone.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| Default branch | No — read from `origin/HEAD` | Override only when the remote's default branch cannot be resolved or another branch is intentionally being released. |
| Author override | No | Name or email to verify the target commit against. Defaults to the local git identity (`git config user.name` / `git config user.email`). |

---

## Steps

### Step 1 — Sync the repo

1. `git status --porcelain` — the working tree must be clean. If it isn't, stop and ask the user to commit or stash first; never discard uncommitted work.
2. `git fetch origin --prune`.
3. Confirm the default branch (input, or read `origin/HEAD`).
4. `git checkout <default branch>`, then `git pull --ff-only origin <default branch>`. Fast-forward only — never merge, rebase, or `reset --hard` on the default branch.

### Step 2 — Identify and verify the target commit

1. Read the tip of the default branch: `git log -1 --pretty=format:'%H|%an|%ae|%s'`.
2. Resolve the expected author: the Author override input if given, else the local git identity (`git config user.name` / `user.email`).
3. Compare the tip commit's author (name or email, case-insensitive) against the expected author.
   - **Match:** proceed — this commit is the release target.
   - **Mismatch:** stop. Show the tip commit's hash, author, and subject alongside the expected author, and ask the user to explicitly confirm whether to release this commit anyway (e.g. someone else's change landed after theirs) before continuing. Never silently substitute a different commit or proceed past a mismatch without confirmation.

### Step 3 — Retrieve the version from the CI build

The canonical version for each commit is computed by CI in the format
`YY.MM.DD<run-number>` (for example, `26.08.21168` means 2026-08-21, run 168). Retrieve it from the
latest successful workflow run on the target commit rather than computing it independently.

1. Find successful runs for the target commit: `gh run list --repo <owner>/<repo> --commit <target-sha> --status success --json databaseId,displayTitle,createdAt`. Take the most recent successful run.
   - If no successful run exists for the target commit, stop and ask the user to supply the version manually (it must match the build that validated the change).
2. Get the jobs for that run: `gh api repos/<owner>/<repo>/actions/runs/<run-id>/jobs --jq '.jobs[] | {id,name}'`. Identify the job that runs the version-stamping step.
3. Extract the version from the job logs: `gh api repos/<owner>/<repo>/actions/jobs/<job-id>/logs | grep -oE '[0-9]{2}\.[0-9]{2}\.[0-9]{5,6}' | head -1`. This matches the expected date and run-number format.
4. Verify that the exact tag does not exist locally or remotely and that no GitHub release already
   uses it. Stop if any of them exists; do not overwrite or recreate it.
5. Resolve and record the previous release tag now, before creating the new tag. From the version
   tags reachable from the target commit and matching this repository's version format, use the
   highest one below `<version>`. If no prior matching tag exists, record that this is the first
   release in this version series.
6. Present the target commit, retrieved version, and previous-tag anchor to the user. Get explicit
   confirmation before creating anything.

### Step 4 — Create and push the tag

1. `git tag <version> <target commit sha from Step 2>` — tag directly on the default branch commit; do not create a release branch.
2. Show the exact tag and target SHA, then confirm with the user before pushing — a pushed tag is
   visible to the whole team.
3. `git push origin <version>`.

### Step 5 — Publish the GitHub release with auto-generated notes

**Do not rely on `--generate-notes`'s default previous-release inference.** It anchors to the most recent *published GitHub Release* by date/semver — which may be stale or from an unrelated version series — and will silently produce a changelog spanning unrelated history. Always resolve an explicit anchor instead:

1. Use the previous release tag recorded in Step 3 as the `--notes-start-tag` anchor.
   - **A prior tag exists:** use it as the explicit anchor.
   - **No prior tag:** explain that generated notes will cover all reachable history and ask the
     user to confirm that scope.
2. Resolve the GitHub repository identifier from `git remote get-url origin`.
3. Preview the generated notes without publishing when the available GitHub tooling supports it.
   Otherwise, show the exact release command and its anchor. Ask for explicit confirmation before
   publishing.
4. Run `gh release create <version> --repo <owner>/<repo> --target <target-sha> --title "<version>" --generate-notes --notes-start-tag <previous-tag>` (omit `--notes-start-tag` only for the confirmed first-release case).
5. Read the generated notes back immediately. If they are empty or span unrelated history, report
   the problem and correct the release notes with the user's approval; do not silently leave
   misleading notes published.
6. Confirm the release exists and capture its URL.

### Step 6 — Report

Report the tag name, the default branch commit it points to, and the release URL.

---

## Hard constraints

1. **Confirm before every remote mutation.** Never push the tag or publish or edit the GitHub
   release without the explicit user confirmations called out in Steps 4–5.
2. **Never overwrite an existing tag.** Stop if the computed `<version>` tag already exists.
3. **Fast-forward only on the default branch.** Never merge, rebase, or `reset --hard` on it.
4. **No release branches.** Tag directly on the verified default-branch commit; never create a `release/` branch.
5. **Author mismatch is a hard stop, not a guess.** If the target commit's author doesn't match the expected author, pause and get explicit confirmation before proceeding.
6. **Release from the exact verified commit.** Never re-fetch or re-check the default branch between Step 2's verification and Step 4's tag creation.
7. **Never trust `--generate-notes`'s default anchor.** Always resolve an explicit previous-version tag before generating notes — except when no prior tag exists at all. The default anchor will silently pick whatever the most recent published release happens to be, regardless of how unrelated or stale it is.

---

## Quality checklist

- [ ] Working tree was clean before starting; nothing was discarded.
- [ ] Default branch fetched and fast-forwarded only (no merge/rebase/`reset --hard`).
- [ ] Target commit's author verified against the expected author; any mismatch was surfaced and explicitly confirmed by the user before proceeding.
- [ ] Version retrieved from the latest successful CI run on the target commit (or supplied by user if no run existed); confirmed with the user before creating anything.
- [ ] The exact local tag, remote tag, and GitHub release did not already exist.
- [ ] The previous release tag was resolved before the new local tag was created.
- [ ] Tag pushed directly on the default branch commit — no release branch created.
- [ ] Tag pushed only after explicit user confirmation.
- [ ] An explicit `--notes-start-tag` was resolved from the previous tag before publishing — unless no prior tag existed.
- [ ] The user explicitly confirmed the release before it was published.
- [ ] Generated release notes were read back and looked correct (no unrelated history, not empty) before considering the release done.
- [ ] Tag name, default branch commit, and release URL reported to the user.
