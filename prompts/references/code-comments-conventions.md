# Code Comments Conventions

This guide defines when a C# comment earns its place, and what to do instead when
it does not. Apply every rule below to any code you write or modify.

---

## Table of Contents

- [The Test](#the-test)
- [Comments That Earn Their Place](#comments-that-earn-their-place)
- [Comments To Delete](#comments-to-delete)
- [Invariant vs. Incident](#invariant-vs-incident)
- [One Home Per Invariant](#one-home-per-invariant)
- [Prefer Code Over Commentary](#prefer-code-over-commentary)
- [XML Doc Comments](#xml-doc-comments)
- [Formatting](#formatting)
- [Review Checklist](#review-checklist)

---

## The Test

Before writing or keeping any comment, ask:

> **Can a reader recover this fact from the code at this site?**

- **Yes** → delete the comment. If the fact is hard to recover, fix the name or extract a method;
  do not narrate.
- **No** → keep it, and write only the part that is not recoverable.

A comment is not free. It is not compiled, not tested, and not refactored, so it rots silently
while the code around it changes. Every comment you keep is a maintenance liability you are
claiming is worth paying for. Comments that restate the code cost the same and buy nothing.

Comments explain **why**, a non-obvious constraint, or a consequence that the code cannot show. If
a comment merely narrates the statement below it, delete it.

---

## Comments That Earn Their Place

| Category | What it captures | Example |
|---|---|---|
| **Cross-component consequence** | An effect that lives in another class, component, or pipeline stage and is invisible at this call site | *"Removing the local record makes the downstream export report the object as deleted."* |
| **Intent / decision** | Why this approach was chosen over the obvious alternative, with the ticket ID | *"Keep the stored value so the reconciliation pass does not restore it on every interval (PROJ-1234)."* |
| **Irreversibility / consequence warning** | What breaks if someone relaxes this later | *"The downstream service cannot reverse a deletion, so remove only the version that was evaluated."* |
| **Deliberate absence** | Why something a sibling branch does **not** happen here | *"Do not enqueue a retry because this outcome is a permanent rejection."* |
| **Conservative limit rationale** | The reason for a self-imposed limit that the external system does not enforce | *"The API accepts any length; this cap protects the downstream write."* |
| **External source of truth** | A `<remarks>` doc comment with the source URL on enums mirroring an external API | `<remarks>See https://api.example.com/docs/card-status</remarks>` |
| **Third-party quirk** | Undocumented or counter-intuitive third-party behaviour a reader would otherwise "fix" | *"The API returns 200 with an empty body when the user is unknown."* |
| **Warning** | Non-obvious cost or constraint: not thread-safe, long-running, ordering-dependent | *"Callers must preserve input order because the server assigns sequence numbers by position."* |
| **`TODO` / ticket ref** | Deferred work, always with the ticket ID | `//  TODO {TICKET}: …` |

Every one of these shares a property: **the fact does not exist anywhere in the code at that
site**. That is the whole justification.

A ticket ID, a third-party format name, or a requirement number is a citation, not an explanation. It
earns a place only when it is attached to a sentence that itself states the constraint, the
alternative rejected, or the consequence — never as a substitute for that sentence. *"PROJ-1234:
matches the specification's sample output"* names a source but never says why the behaviour matters
at this site. Delete the citation and, if no other clause earns its place under the table above,
delete the whole comment.

---

## Comments To Delete

| Smell | Why | Instead |
|---|---|---|
| **Restates the code** | `//  The profile was removed` above `if (result.Outcome == Outcome.ProfileRemoved)` | Delete. The enum member already says it. |
| **Restates a method name** | `//  Conditional on the version read above` above `RemoveIfUnchangedAsync(pacsId, entry.Version)` | Delete. |
| **Repeats an invariant stated elsewhere** | Four copies rot independently | See [One Home Per Invariant](#one-home-per-invariant) |
| **Second-hand reporting** | `//  (the reconciler logs the detail)` — describes another class's behaviour, breaks when that class changes | Delete. |
| **Section banners** | `//////// Helpers ////////`, closing-brace comments | Delete. Extract a method if the file needs signposting. |
| **Change log / byline** | `//  Added by …`, `//  Changed 2026-08-11` | Delete. Git owns history. |
| **Commented-out code** | Nobody who follows you dares delete it | Delete. Git owns it. |
| **Mandated boilerplate** | `/// <summary>Gets the name.</summary>` on an obvious member | Delete. See [XML Doc Comments](#xml-doc-comments). |
| **Essay** | A paragraph where a clause works | Cut to the irreducible fact. |
| **Cites a source, not a reason** | `//  PROJ-1234: matches the specification's sample output` names where a value came from, not why it matters here | Delete the citation. Keep only the actual constraint or consequence; if none exists, delete the whole comment. |
| **Narrates a bug that no longer exists** | `//  A plain MERGE lets two concurrent writers both take the INSERT branch and throw 23505...` above code that contains no `MERGE` anywhere — see [Invariant vs. Incident](#invariant-vs-incident) | Move the incident narrative to the commit message / PR description. Keep only the durable invariant, if one survives. |

### Test code

Two exemptions, both governed by
[`code-unit-tests-conventions.md`](code-unit-tests-conventions.md) — this file does not override
them:

- **The `//  Arrange.` / `//  Act.` / `//  Assert.` section comments are required** on every test.
  They are structural markers, not narration, and the "restates the code" rule does not apply.
- **A trailing note on a `[TestCase]` row** naming what that case exercises
  (`//  case-insensitive`, `//  empty username`) is a keeper: the intent behind a literal is not
  recoverable from the literal.

Everything else in this file applies to test code unchanged.

---

## Invariant vs. Incident

A fix comment tends to arrive with two kinds of content tangled together: a durable fact about
the code that now exists, and the story of the bug that led here — the symptom, the evidence that
pinned it down, why the old approach failed. Only the first belongs in the file.

**The split:** would this sentence still make sense to someone who has never seen the diff and is
reading only the merged file? A durable invariant passes — it describes a property of the code in
front of the reader (see [Comments That Earn Their Place](#comments-that-earn-their-place),
especially *Intent/decision*, which is allowed to name "the obvious alternative" a reader would
otherwise reach for). An incident narrative fails — understanding it depends on knowing what the
code used to do, which is exactly the part that disappears when the old code is deleted. That
narrative is not lost, it just has two better homes: the **commit message**, for whoever reads git
history later, and a short **inline PR comment on the changed lines**, for whoever is reviewing
the diff right now. Both are read *with* the diff and do not rot when the file changes again later
— unlike the file itself, they are never mistaken for a fact about the code as it stands today.

```csharp
//  ❌ Incident narrative. There is no MERGE left to contrast against, so this describes the old
//  failure rather than a durable fact about the SQL below.
protected override string Sql => """INSERT INTO export_queue (...) ... ON CONFLICT (...) DO UPDATE ...""";

//  ✅ Concurrent callers write the same key, so this must remain one atomic INSERT ... ON
//  CONFLICT statement rather than a SELECT followed by a write (PROJ-1234).
protected override string Sql => """INSERT INTO export_queue (...) ... ON CONFLICT (...) DO UPDATE ...""";
```

The commit message and a short inline PR comment at the fix site are where the incident narrative
goes instead — not discarded, relocated. State the symptom, the evidence that pinned the cause,
and why the chosen fix closes it; the ticket ID ties it back for anyone who needs the full story
later. This file only governs what stays out of the code.

---

## One Home Per Invariant

When one mechanism governs several branches, **state it once, at the place that establishes it.**
Each branch then states only its own consequence — never the mechanism again.

Duplicating an invariant across branches is the single most common way comment blocks rot: the
next person edits one copy and silently leaves the others lying.

```csharp
//  ✅ The invariant's home — stated once, where the version is read.
//  The downstream service cannot reverse a deletion, so every removal below must target the
//  version that was evaluated.
CacheEntry? entry = await _cache.GetAsync(id);

// …

//  ✅ Branch-specific consequence only — no restatement of the guard mechanism.
//  Another operation may have restored this entry in the meantime, in which case it must survive.
bool removed = await _cache.RemoveIfUnchangedAsync(id, entry.Version);

//  ❌ Restates the mechanism the block above already owns.
//  The version guard prevents a concurrent operation from restoring an entry during removal.
```

---

## Prefer Code Over Commentary

Reach for these before writing a comment:

1. **Rename.** A `Check*` method, a constant, or a local with an intention-revealing name removes
   most explanatory comments outright.
2. **Extract a method.** A comment introducing a block of a long method is a method waiting to be
   named. This also keeps the caller at a single level of abstraction (see the
   `code-refactor-class` skill).
3. **Introduce an explanatory variable.** `bool isPermanentCollision = …` beats a comment saying
   the condition means a permanent collision.
4. **Name the constant.** `ProfileConstants.MaximumNameLength` beats `//  50 is the max`.

A long comment block on a single call site is usually a signal that the enclosing method is doing
too much at mixed altitude, not that the site needs prose.

---

## XML Doc Comments

- **Public API surface** of a shared library: document it.
- **Internal implementation classes** (components, converters, clients, workers): document only what the
  signature does not already say. Do not add `<summary>` blocks that restate the method name.
- **Enums mirroring an external API**: keep a `<remarks>` with the source URL.
- Never let a `<param>`/`<returns>` outlive the parameter it describes. If you change a signature,
  update or delete the doc in the same edit.

---

## Formatting

- **Three logical lines maximum for prose comments.** State the irreducible fact and stop. A
  comment that needs a fourth line is usually explaining more than one thing — split it or reach
  for [Prefer Code Over Commentary](#prefer-code-over-commentary). Legal text, generated/tooling
  directives, and required XML documentation keep the structure their consumers require.
- Two spaces after `//`: `//  Like this.` — matches the `//  Arrange.` convention in
  [`code-unit-tests-conventions.md`](code-unit-tests-conventions.md).
- Sentence case, full sentences, terminating period.
- Wrap at the file's prevailing width (~100 chars); do not run to the editor's right edge.
- Blank comment line (`//`) to separate paragraphs inside one block — but a block needing
  paragraphs is a prompt to re-read [Prefer Code Over Commentary](#prefer-code-over-commentary).
- Reference code sites as `ClassName.cs:42` or `ClassName.MethodAsync`, never as "the method
  above/below" — relative directions break on the next edit.

---

## Review Checklist

Before opening the PR, for every comment added or touched:

- [ ] It states something **not recoverable** from the code at that site.
- [ ] It explains **why**, a non-obvious constraint, or a consequence that the code cannot show.
- [ ] It is **3 lines or fewer**.
- [ ] The invariant it describes is stated **exactly once** in the file; sibling branches carry
      only their own consequence.
- [ ] For a bug fix: it would still make sense to a reader who never saw the diff. If it doesn't,
      move that part to the commit message / PR description — see
      [Invariant vs. Incident](#invariant-vs-incident).
- [ ] No rename, extracted method, or explanatory variable would have removed the need for it.
- [ ] It names no other class's internal behaviour that could change without this file changing.
- [ ] Ticket IDs are present on decision and `TODO` comments.
- [ ] It is still true of the code as finally written — re-read it after the last edit.
- [ ] No commented-out code, banner, byline, or change-log entry was introduced.
