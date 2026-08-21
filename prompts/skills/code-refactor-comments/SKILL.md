---
name: code-refactor-comments
description: v0.3.0 — Audits and refactors comments in C# files using the shared comment conventions. Use to remove narration, preserve non-obvious intent, correct XML documentation, consolidate duplicated invariants, or replace commentary with clearer code while preserving behavior.
---

# C# Comment Refactorer

Act as a C# maintenance engineer. Make every in-scope comment earn its place while
preserving behavior and keeping the diff local to the requested files.

The comments convention is authoritative. Do not turn its examples or this procedure into a
second rule set.

## References — read before editing

| Reference | Path | When to read it |
|---|---|---|
| **Code Comments Conventions** | `../references/code-comments-conventions.md` | Always; read completely before classifying any comment |
| **Code Unit Test Conventions** | `../references/code-unit-tests-conventions.md` | For test code; read the Test Structure and Test Naming sections before touching structural or `[TestCase]` comments |

Paths are relative to this `SKILL.md` after installation by
`prompts/scripts/update-skills.py`. In this source repository, resolve shared references as
`../../references/<file>`.

## Inputs and scope

Accept one or more C# files, a class, a directory, or the C# files in the current diff. Prefer the
user's explicit paths. If no paths are given and the current work clearly identifies changed C#
files, scope the pass to those files; otherwise ask for the target.

Also locate the solution/project and the narrowest tests covering the target when available. Do
not expand a file request into a repository-wide cleanup.

Exclude generated outputs (`bin/`, `obj/`, `*.g.cs`, generated clients, migrations, and files with
an auto-generated header) unless the user explicitly includes them.

## Protected text

Do not delete or rewrite:

- copyright, license, or attribution headers;
- auto-generated markers;
- analyzer, formatter, coverage, or compiler suppression directives;
- comments consumed by documentation or code-generation tooling;
- intentionally preserved dispatcher `case` lines sanctioned by the project conventions;
- test `//  Arrange.`, `//  Act.`, and `//  Assert.` markers;
- meaningful trailing `[TestCase]` notes.

Classify protected text separately from prose comments. If its purpose is unclear, leave it in
place and report it instead of guessing.

## Procedure

### 1. Establish the working state

1. Read the applicable references before editing.
2. Inspect the target files, their project context, and existing uncommitted changes. Preserve
   unrelated user work.
3. Locate the narrowest build and test commands that cover the target. Record whether a green
   baseline is available.

Run the baseline before any executable-code refactoring. A failing or missing baseline does not
prevent comment-only edits, but it forbids renames, extracted variables/constants/methods, and
other executable-code changes. State that limitation explicitly.

### 2. Classify every in-scope comment

Classify each `//`, `/* ... */`, and `///` block as exactly one of:

- **Keep** — contains an irreducible fact allowed by the comments convention.
- **Tighten** — earns its place but includes narration, duplication, or unnecessary prose.
- **Delete** — recoverable from the code, stale, a banner/byline/change log, or commented-out
  code.
- **Consolidate** — repeats an invariant whose authoritative home is elsewhere in the file.
- **Replace with code** — a clearer name, explanatory variable, named constant, or extracted
  method can carry the meaning.
- **Protected** — required legal, generated, compiler, analyzer, documentation, or test-tool text.

Judge the comment against the code at its exact site. Do not keep it merely because it is accurate.
Do not delete a non-recoverable constraint merely because its wording is poor.

### 3. Apply the smallest sufficient change

Apply classifications in this order:

1. Delete comments that add no information.
2. Choose one authoritative home for each repeated invariant; keep the mechanism there and only
   irreducible branch-specific consequences at sibling sites.
3. Tighten retained comments to the non-recoverable **why**, consequence, constraint, deliberate
   absence, third-party quirk, or external source of truth.
4. Prefer a local rename, explanatory variable, named constant, or method extraction when that
   makes the comment unnecessary and the green-baseline gate permits executable changes.
5. Apply XML documentation scope and formatting from the comments convention. Keep required public
   API documentation in shared libraries and external-source `<remarks>` links; remove boilerplate
   that merely restates an internal signature.
6. Re-read each retained or changed comment against the final code and apply the reference's review
   checklist.

Never invent a ticket ID, external URL, rationale, or consequence. Search the local code, tests, and
git history when they can establish the fact. If required evidence remains unavailable, preserve
valuable intent and report the missing source rather than fabricating one.

### 4. Preserve behavior

For comment-only edits:

- Do not change executable tokens while cleaning comments.
- Run the containing project build when available, because XML documentation and analyzers can
  still make comment edits compile-significant.

For code-assisted edits:

- Require a green pre-edit build and the narrowest relevant passing test set.
- Keep public, protected, and internal signatures unchanged, including parameter names.
- Preserve evaluation, exception, side-effect, and async ordering.
- Re-run the same build and test set after editing.
- Revert only the refactoring that caused a regression; do not weaken or skip verification.

If verification cannot run because dependencies or infrastructure are unavailable, report the
exact command and failure. Do not claim the refactor is verified.

### 5. Keep the diff focused

Do not reformat unrelated code, reorganize members, add new documentation for completeness, or
rewrite comments that already satisfy the convention. Do not alter behavior while pursuing a
cleaner explanation.

## Output

Edit the requested files in place. Report briefly:

- files changed;
- comments deleted, tightened, consolidated, retained for a non-obvious reason, or replaced with
  code;
- any protected or evidence-dependent comments left untouched;
- baseline and final build/test commands and results;
- any unverified limitation.

Do not commit.
