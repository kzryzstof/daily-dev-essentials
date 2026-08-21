---
name: code-refactor-tests
description: v1.7.0 — Writes or refactors C# unit tests using the shared test conventions. Use for naming, AAA structure, setup, assertions, helpers, formatting, or an explicitly requested coverage review.
---

# C# Unit Test Refactorer

Write or refactor C# unit tests while preserving their intent and keeping the diff focused on the
requested test class and any directly required test helpers.

The shared test conventions are authoritative. Do not duplicate them in this skill or turn their
examples into additional rules.

## Reference — read before editing

Read `../references/code-unit-tests-conventions.md` completely before editing. That path is relative
to this `SKILL.md` after installation with `prompts/scripts/update-skills.py`. In this source
repository, use `../../references/code-unit-tests-conventions.md`.

## Inputs and scope

Accept an existing test file, a class under test, or explicit paths to both. If the user names only
the production class, locate its existing tests and containing test project. If neither the target
nor a discoverable current change identifies the intended class, ask for the target.

Inspect the class under test before changing assertions or coverage. Preserve every existing test
case unless the user explicitly asks to consolidate or remove tests. If a test contradicts the
current production contract, report the evidence and ask before removing it.

Match the requested mode:

- **Refactor or format:** preserve the existing behavioral coverage and assertion strength. Report
  coverage gaps, but do not add unrelated cases unless the user asks.
- **Write or extend:** add cases for the requested behavior and its applicable boundaries.
- **Review:** inspect and report findings without editing unless the user also requests changes.

Do not turn a single-class request into a test-suite-wide cleanup.

## Procedure

1. Read the convention and inspect the class under test, test framework, mocking and assertion
   libraries, nearby tests, repository instructions, and existing uncommitted changes.
2. Run the narrowest relevant test command before editing when the project can be executed. If the
   baseline fails, distinguish pre-existing failures from the requested work. Restrict changes to
   formatting or a user-requested test correction until a green baseline is available, and do not
   claim behavior was preserved.
3. Refactor the target to follow the convention for naming, AAA sections, setup, fluent chains,
   control flow, assertions, shared data, and helper placement.
4. When coverage work is in scope, compare the tests with the class under test and add cases only
   for applicable observable behavior. Do not invent requirements or create meaningless boundary
   tests merely to fill a checklist.
5. Keep test intent unchanged. Do not weaken assertions, replace precise assertions with broader
   ones, skip tests, or modify production behavior merely to make the tests pass.
6. Run the repository's formatter when it applies, then build the containing test project and rerun
   the same test command and filter used for the baseline.

If the shared convention conflicts with the project's compiler, test framework, or explicit
repository-wide instructions, follow the project and report the conflict rather than forcing code
that does not compile or execute.

## Output

Edit the requested files in place unless the user explicitly asks for an inline example. Report:

- files changed and any helpers added or reused;
- material structural or coverage changes;
- baseline and final build/test commands and results; and
- any verification limitation or unresolved convention conflict.

Do not commit.
