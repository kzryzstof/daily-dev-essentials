---
name: unit-test-guidelines
description: "v1.0.0 — Octelys C# unit-test formatting guidelines: naming convention, AAA structure, fluent-chain formatting, control flow formatting, mock/SUT setup placement, shared fixtures, (shared) assertion helpers, repetitive-access helpers, helper method placement, and the required coverage checklist."
---

# Unit Test Guidelines

This guide defines how a Octelys C# unit test class must be formatted and
structured. Apply every rule below to any test class you write or modify.

---

## Table of Contents

- [Test Naming](#test-naming)
- [Test Structure](#test-structure)
- [Fluent Chain Formatting](#fluent-chain-formatting)
- [Control Flow Formatting](#control-flow-formatting)
- [Setup Rules](#setup-rules)
- [Test Rules](#test-rules)
- [Assertion Helpers](#assertion-helpers)
- [Repetitive Access Helpers](#repetitive-access-helpers)
- [Helper Method Placement](#helper-method-placement)
- [Required Coverage](#required-coverage)

---

## Test Naming

Test method naming format: `MethodName_ScenarioInPresentTense_ExpectedResult`

| Part | Rule | Example |
|---|---|---|
| `MethodName` | The method under test | `ComposeAsync`, `Decompose` |
| `Scenario` | Present tense — describes the input state | `UserIsNull`, `CardIsValid`, `KeyIsNotComposite` |
| `ExpectedResult` | Past tense — describes the outcome | `PacsIdReturned`, `ArgumentExceptionThrown`, `InnerRangeExceptionThrown` |

---

## Test Structure

Use the AAA pattern. Include section comments on every test:

```csharp
//  Arrange.
//  Act.
//  Assert.
```

Omit the `//  Arrange.` comment when the section has no code.

---

## Fluent Chain Formatting

Break long fluent / method-chain statements so each call in the chain sits on its own line, with the leading `.` aligned one indent deeper than the receiver. This keeps the receiver, the call, and the argument visually distinct instead of buried in one wide line:

```csharp
getCache
    .ExecuteAsync<PacsBadgeConfiguration>("BadgeConfigurationCache")
    .Returns(new PacsBadgeConfiguration
    {
        PacsId = "BadgeConfigurationCache",
        Fields = new List<PacsBadgeConfigurationField>
        {
            new() { Name = OnGuardConstants.BadgeIdName,     Id = _expectedBadgeIdGuid },
            new() { Name = OnGuardConstants.BadgeTypeName,   Id = _expectedBadgeTypeName },
            new() { Name = OnGuardConstants.BadgeStatusName, Id = _expectedBadgeStatusName },
            new() { Name = OnGuardConstants.BadgeIssueCode,  Id = _expectedBadgeIssueCode }
        }
    });
```

Apply this whenever a statement chains two or more calls (e.g. `mock.Method(...).Returns(...)`, `Arg.Any<...>()` setups, builder chains) and the single-line form is long or hard to scan. Keep short, single-call statements on one line.

---

## Control Flow Formatting

1. Put a blank line **before** every control-flow statement (`if`, `for`, `foreach`, `while`, `switch`, `try`, …) when it follows another statement, so the control block stands apart from the lines above it.
2. Always wrap the body in braces — even a single-line body. Never use the brace-less one-line form.

So this:

```csharp
_pacsBadge.Fields.RemoveAll(f => f.Id == _expectedBadgeStatusName);
        if (status is not null)
            _pacsBadge.Fields.Add(new PacsBadgeConfigurationField { Id = _expectedBadgeStatusName, FieldType = PacsBadgeConfigurationField.Type.String, Value = status });
```

becomes:

```csharp
_pacsBadge.Fields.RemoveAll(f => f.Id == _expectedBadgeStatusName);

if (status is not null)
{
    _pacsBadge.Fields.Add(new PacsBadgeConfigurationField
    {
        Id = _expectedBadgeStatusName,
        FieldType = PacsBadgeConfigurationField.Type.String,
        Value = status
    });
}
```

---

## Setup Rules

1. Declare and configure all mocks in the test class constructor (xUnit) or `[SetUp]` method (NUnit).
2. Set default mock return values that cover the happy path in the constructor / `[SetUp]`.
3. Override mock behaviour in the `//  Arrange.` section only for edge cases and exceptions.
4. Promote the common request/input object (e.g. the faker-generated DTO under test) and its supporting fakes to private fields, and generate/wire them once in `[SetUp]`. Each test then mutates only the single property it exercises — no per-test `var x = Faker.Generate()` boilerplate.
5. When a mock can be configured with `Arg.Any<...>()` to return the happy-path object, do it once in `[SetUp]`. Edge-case tests override that same call (e.g. `.ReturnsNull()`) — NSubstitute's last-registered-wins rule makes the override take precedence.
6. Instantiate the class under test (the system under test) once in the test class constructor (xUnit) or `[SetUp]` method (NUnit), after the mocks are configured, and store it in a private field (e.g. `_sut`). Never new-up the system under test inside individual tests — the `//  Act.` section calls the method on the shared instance.

---

## Test Rules

1. Keep tests minimal — few or no `Arrange` lines, exactly one `Act` line, and one or more `Assert` lines.
2. Pass constants directly in the `Act` section; do not assign them to intermediate variables.
3. If a test requires multiple unrelated assertions, split it into separate tests.
4. **Never mix result assertions (`response.*`, callback content) with call-count assertions (`Received`, `DidNotReceive`) in the same test.** Separate the two concerns:
   - One test validates the *returned result* — `ExpectedResult` names the response shape (e.g. `FailedResultReturned`, `AllStepsSucceededReturned`).
   - A separate test validates *how many times a dependency was called* — `ExpectedResult` names the call count (e.g. `CorrectNumberOfImportCallsMade`, `NoImportCallsMade`, `BadgeImportCalledThreeTimes`).
5. Place reusable constants and request objects in the shared test project so they can be referenced across tests.
6. Prefer `.ReturnsNull()` over `.Returns((T?)null)` when mocking nullable return values (requires `using NSubstitute.ReturnsExtensions;`). Note: `.ReturnsNull()` does not resolve on every `Task<T?>` overload — fall back to `.Returns((T?)null)` if it fails to compile.
7. Cover null, empty, and whitespace inputs together in one parameterised test: `[TestCase(null)] [TestCase("")] [TestCase("   ")]` — matching `string.IsNullOrWhiteSpace` validation in the class under test.

---

## Repetitive Access Helpers

When the same hard-to-scan expression is repeated across tests — e.g. reaching into a collection to read or write one field:

```csharp
_pacsBadge.Fields.First(f => f.Id == _expectedBadgeStatusName).Value = status;
```

extract it behind an intention-revealing helper so each call site reads as one obvious line:

- **Used in a single test class** → add a `private` helper method in that class:

  ```csharp
  private static void SetField(PacsBadge badge, string name, string value)
      => badge.Fields.First(f => f.Id == name).Value = value;

  // call site
  SetField(_pacsBadge, _expectedBadgeStatusName, status);
  ```

- **Reused across multiple test files** → promote it to an extension method in a shared static class (`[ExcludeFromCodeCoverage]`), kept under an `Assertions/` or `Extensions/` folder in the test project, or in the shared test project when reused across DLAs:

  ```csharp
  [ExcludeFromCodeCoverage]
  public static class PacsBadgeExtensions
  {
      public static void SetField(this PacsBadge badge, string name, string value)
          => badge.Fields.First(f => f.Id == name).Value = value;
  }

  // call site
  _pacsBadge.SetField(_expectedBadgeStatusName, status);
  ```

Provide a matching reader (e.g. `GetField`) when tests also assert the value. Do not extract a helper for a one-off expression — only when the same shape repeats.

---

## Helper Method Placement

Place all `private` helper methods at the **bottom** of the test class, after every test method, grouped under a single `Helper methods` section comment:

```csharp
public class BadgeComposerTests
{
    // ...fields, constructor / [SetUp]...

    // ...test methods...

    //  Helper methods.

    private static void SetField(PacsBadge badge, string name, string value)
        => badge.Fields.First(f => f.Id == name).Value = value;

    private static PacsBadge BuildBadge(...) => ...;
}
```

Rules:

1. No `private` helper method may sit between or above the test methods — they all live below the last test.
2. Emit the `//  Helper methods.` comment exactly once, immediately before the first helper, only when the class has at least one private helper.
3. This applies to private helper methods only. Keep fields, the constructor / `[SetUp]`, and the system-under-test instantiation at the top of the class as usual.

---

## Required Coverage

Every test class must cover:

- **Happy path** — the expected successful execution
- **Edge cases** — boundary inputs, empty collections, minimum/maximum values
- **Exceptions** — every `throw` path in the class under test
- **Null/empty inputs** — null arguments, empty strings, missing required fields
- **Boundary conditions** — off-by-one values, max-length strings, zero counts
