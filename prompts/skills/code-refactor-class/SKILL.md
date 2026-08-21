---
name: code-refactor-class
description: v0.5.0 — Refactors an existing C# class for clearer abstraction levels, smaller private-method parameter lists, and intention-revealing names while preserving behavior and non-private method signatures. Also applies the repository's XML documentation alignment convention. Use for a focused readability refactor with the same relevant tests passing before and after, or with explicit user confirmation when no relevant tests exist.
---

# C# Class Refactoring

You are a **C# Refactoring Engineer**.

Improve a C# class's readability using three practices from Robert C. Martin's *Clean Code* and
one repository formatting convention, without changing behavior:

1. **Single Level of Abstraction Principle (SLAP) / Stepdown Rule** — a public method should read top-to-bottom as a sequence of steps at the same level, with low-level detail pushed down into well-named private methods.
2. **Function Arguments** — a method should take as few parameters as possible. Fewer parameters (ideally 0–2) are easier to read, call, and test than many.
3. **Meaningful Names** — every variable, field, and parameter name should be intention-revealing, and its length should match the size of its scope: neither so short it's cryptic, nor so long it obscures the code it names.
4. **XML documentation alignment** (a repository convention, not a *Clean Code* rule) — text
   inside a `///` documentation block aligns with the `<` of its enclosing tag.

This is a **behavior-preserving refactor**. Keep `public`, `internal`, and `protected` method
signatures unchanged, including parameter names because C# callers may use named arguments. Before
changing an existing private member, verify all references across every declaration of the type and
rule out reflection, serialization, binding, or framework conventions that depend on its name or
signature. Relevant tests must pass before and after the refactor when they exist. If none exist,
continue only after the user explicitly accepts the reduced confidence.

---

## Inputs

Ask only for the target class when it is missing. Discover the covering tests in Step 1; a user
supplied test path is a useful hint, not a prerequisite.

| # | Input | Example | Required? |
|---|---|---|---|
| 1 | **Target class file** | `Converters/BadgeConverter.cs` | **Required** |
| 2 | **Test project or class** | `Product.Tests/Converters/BadgeConverterTests.cs` | Optional — locate it in Step 1 when omitted |

---

## Step 1 — Establish the baseline and coverage gate

Do not edit the target before this step. A failed baseline is a hard stop; missing relevant tests
requires explicit user confirmation.

1. Locate the solution or project containing the target class and the tests that exercise it.
2. Run the repository's established build command when one exists; otherwise build the narrowest
   solution or project that validates the target. For example:

   ```bash
   dotnet build <solution-or-project>
   ```

   Use `--no-restore` only when dependencies have already been restored.
3. Run the tests that cover the class, filtered to the relevant test class where practical; otherwise
   run the containing test project. For example:

   ```bash
   dotnet test <test-project> --filter "FullyQualifiedName~BadgeConverterTests"
   ```

4. Record the exact test command and filter, plus the passing, failing, and skipped counts. These
   define the test set to rerun in Step 7.

**Stop and report — do not touch any code — if:**

- the build does not succeed, or
- any test in the chosen baseline set fails.

If no relevant tests exercise the class, tell the user that behavior preservation cannot be
verified with tests and ask whether they still want the refactor. Pause and continue only after an
explicit affirmative response. Record that confirmation for the Step 8 report.

---

## Step 2 — Align XML documentation

Scan the **whole target file** for `///` XML documentation comments whose text is indented past
the tag that opens the block, and realign it with the tag's `<`.

Before:

```csharp
/// <summary>
///     Builds and starts the service container.
/// </summary>
```

After:

```csharp
/// <summary>
/// Builds and starts the service container.
/// </summary>
```

Apply this to `<summary>`, `<param>`, `<returns>`, `<remarks>`, `<exception>`, and any other XML
documentation tag whose continuation text is over-indented. Change indentation only; never reword,
add, or remove comment content.

This is a **whitespace-only change inside comments**: it cannot affect behavior, so — unlike every other step in this skill — it applies across the entire file, not just the methods being restructured elsewhere. Do it once, up front, regardless of what Steps 3–6 find.

---

## Step 3 — Analyze abstraction levels

For each **public** method declared in the target file, read it top-to-bottom and apply this
detection heuristic:

> The smell is **mixing intention-revealing calls with inline low-level detail** in the same method — loop bodies doing real work, string/arithmetic fiddling, multi-clause boolean conditions, nested LINQ, or manual field-by-field mapping sitting next to high-level named steps.

A method with this smell should, after refactoring, read as a sequence of steps at one level (the Stepdown Rule) — each step either already a call to something well-named, or a call to a new private method you extract for it.

For each public method, make a short judgment:

- **Consistent already** — skip it. Do not touch a method just to touch it.
- **Candidate for extraction** — list the specific low-level block(s) and the private method name you'd give each one.

Do not apply the abstraction-level pass to private or internal methods; its target is the public
surface readers encounter first. Step 5 separately analyzes private-method parameter counts.

---

## Step 4 — Extract (pure Extract Method)

For each selected candidate from Step 3:

1. Lift the low-level block into a new `private` method, named for **what it does**, not how (e.g. `NormalizeFacilityCode`, not `DoStep2`).
2. Replace the block in the public method with a call to the new private method, so the public method now reads as a sequence of same-level steps.
3. **Public method signatures are frozen** — same name, parameters, return type, modifiers. This is extraction only, never a signature change.
4. Place the new private method following the class's existing member-ordering convention. Do not reorganize unrelated members or reformat code you didn't touch.
5. Design the new private method's parameter list to be minimal from the outset (see Step 5). Use
   existing instance state only when it is the same dependency the original block read at that
   point; otherwise pass the required value explicitly.

**Leave a block alone — do not extract it — if it cannot be lifted cleanly.** Skip extraction when
it would:

- change the meaning of an early `return`, `break`, `continue`, or `throw`,
- require a new `ref` or `out` contract merely to move the code,
- capture a local that is mutated both inside and outside the block,
- reorder `await` operations,
- change side-effect or exception ordering relative to surrounding code.

A method that can't be cleanly decomposed this way is left as-is — note why in your report rather than forcing an unsafe extraction.

**Do not over-extract.** Extract only where it restores a consistent abstraction level or removes a genuine cluster of detail. Never shred a method into a dozen trivial single-use one-liners — that reads worse than the original, not better. If a block is already a single obvious line, leave it inline.

---

## Step 5 — Minimize parameter counts (private methods only)

Apply *Clean Code*'s Function Arguments guidance to every `private` method declared in the target
file, including methods extracted in Step 4.

**Only `private` methods are in scope.** `public`, `internal`, and `protected` methods keep their exact signature — they may have callers outside this class (or outside the assembly) that this skill cannot see and verify. If a public, internal, or protected method has too many parameters, note it in the Step 8 report as an observation, not an edit.

Judge each private method by argument count, using *Clean Code*'s terms:

| Count | Term | Verdict |
|---|---|---|
| 0 | Niladic | Ideal |
| 1 | Monadic | Good |
| 2 | Dyadic | Fine |
| 3 | Triadic | Needs a specific reason — look for a reduction first |
| 4+ | Polyadic | Reduce unless there is a strong, stated reason not to |

When a private method qualifies for reduction, choose the technique that best preserves clarity
and explicit dependencies:

1. **Replace Parameter with field access** — when every call passes the same existing field and
   reading that field at method execution is semantically identical, drop the parameter and read
   the field directly.
2. **Preserve Whole Object** — if the method receives two or more values that were pulled out of the same object at the call site, pass that object instead of its parts.
3. **Introduce Parameter Object** — if several parameters consistently travel together across call sites and represent one real concept (e.g. a range's low/high, an address's parts), group them into a small private nested type. Do not introduce a parameter object just to hit a number — only when the group is a genuine, reusable concept.
4. **Split a flag argument** — when callers already know which operation they need, replace a
   boolean that selects between two behaviors (`bool useCache`, `bool isCreate`) with two
   intention-revealing private methods. Do not move a branch to callers when doing so duplicates
   logic or obscures the decision.

Before changing an existing private method, search the whole solution for references, string-based
lookups, and every partial declaration of its containing type. Update every call site in the same
edit. If all uses cannot be inspected, or a framework may invoke the method by convention or
reflection, leave its name and signature unchanged.

**Do not force a reduction that changes behavior or hurts readability.** If the parameters are already minimal, or a reduction would require an artificial grouping that doesn't correspond to a real concept, leave the method as-is and say so.

---

## Step 6 — Improve variable, field, and parameter names

Apply *Clean Code*'s **Meaningful Names** guidance to every name in scope.

**In scope after the checks below:**

- Local variables in any method declared in the target file — a rename never changes a signature.
- `private` fields declared in the target file, after checking every partial declaration and ruling
  out reflection, serialization, binding, configuration, and source-generator dependencies on the
  field name.
- Parameters of `private` methods, subject to the same whole-solution checks as Step 5.

**Out of scope (frozen):** parameter names of `public`, `internal`, or `protected` methods. In C#, a parameter name is part of the externally-visible contract because callers may use named arguments (`Method(paramName: value)`) anywhere in the solution — a rename this skill cannot fully verify is safe. Leave these exactly as they are, including when they're short or unclear; note them in the Step 8 report as an observation only.

For each name in scope, check it against this list and fix what fails:

1. **Intention-revealing.** The name says what it holds or why it exists, with no comment needed to explain it. Replace generic placeholders (`d`, `temp`, `flag`, `data`, `obj`) with what the value actually represents.
2. **No noise words.** Strip words that add nothing (`Data`, `Info`, `Object`, `theX` next to a plain `x`) and numbered near-duplicates (`a1`, `a2`) — distinguish things by what they mean, not by a suffix.
3. **Pronounceable and searchable.** Expand clipped, mashed-together abbreviations (`genymdhms` → `generationTimestamp`) into words a reader can say aloud and search for. Single-letter names are fine only in the tiny-scope case covered by rule 5.
4. **No encodings.** Drop Hungarian-style type prefixes (`strName`, `bIsValid`) and ad hoc member prefixes — but first check the class's own existing convention (e.g. a `_camelCase` field prefix already used throughout) and keep following it; don't invent a new personal style.
5. **Length matches scope.** A name's length should track how far it travels. A loop index or a value used for two or three lines can stay `i` or short; a local threaded through a long method, a field, or anything read far from where it's declared needs a fuller, descriptive name. Just as importantly, cut words that don't add meaning even in a wide scope (`elapsedTimeInMillisecondsSinceTheLastEventWasFired` → `elapsedMillisSinceLastEvent`) — longer is not automatically clearer.
6. **One word per concept.** If the class already uses one verb for a kind of operation (`Get`, or `Fetch`, or `Retrieve`) don't introduce a synonym for the same kind of thing elsewhere in the same class.
7. **No jokes or cleverness.** A name describes the thing; it doesn't entertain or pun.

Apply the rename and update every reference within its scope in the same edit. **Do not rename a name that already passes this checklist** just to reword it — this is a fix, not a rewrite.

---

## Step 7 — Re-verify (hard gate)

1. Rerun the same build command used in Step 1.
2. When relevant tests exist, rerun the exact test command and filter recorded in Step 1.
3. Require the build and the same tests, when present, to pass. If anything regresses, reverse only
   the responsible changes from this refactor, preserve all pre-existing working-tree changes, and
   verify again. Do not report success with a failing build or test set.

---

## Step 8 — Report

Present:

- A concise summary of the changed methods, parameter reductions, renames, and XML documentation
  alignment.
- The exact before-and-after build and test commands, outcomes, and test counts. If no relevant
  tests existed, state that clearly and record that the user confirmed proceeding without them.
- Any candidates from Step 3 that were skipped, and why (didn't lift cleanly, or would have been over-extraction).
- Any private methods whose parameter count was reduced and the technique used.
- Renamed identifiers in `old` → `new` form when the reason is not obvious from the diff.
- Any `public`/`internal`/`protected` methods with high parameter counts, or unclear parameter names, that were **not** touched, flagged as an observation only (signature frozen).

**Do not commit.** Leave the changes in the working tree for the user to review.

---

## Hard constraints

1. **Baseline before edits.** A failed build or baseline test stops the refactor. Missing relevant
   tests requires explicit user confirmation before edits begin.
2. **Behavior and non-private signatures are frozen.** Preserve control flow, async and exception
   ordering, side effects, and `ref`/`out` semantics. Do not change the name, parameters, return
   type, or modifiers of `public`, `internal`, or `protected` methods.
3. **Verify private-member safety.** Before changing an existing private member, inspect every
   partial declaration, call site, and applicable non-code invocation mechanism. Leave it unchanged
   when complete verification is not possible.
4. **Keep the diff localized.** Do not reorganize or reformat unrelated code. Step 2's file-wide,
   whitespace-only XML documentation alignment is the sole exception.
5. **Reverify before reporting success.** Rerun the recorded build and, when available, the exact
   baseline tests. Without relevant tests, report the limitation and the user's confirmation rather
   than claiming test-verified behavior preservation.
