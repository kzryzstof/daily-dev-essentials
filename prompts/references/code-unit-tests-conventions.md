# Unit Test Conventions

This guide defines the default formatting and structure for C# unit tests. Apply it when writing or
modifying tests, while preserving explicit repository instructions and framework requirements.

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
| `Scenario` | Present tense — describes the input state | `UserIsNull`, `ItemIsValid`, `KeyIsNotComposite` |
| `ExpectedResult` | Past tense — describes the outcome | `ProfileReturned`, `ArgumentExceptionThrown`, `ServiceExceptionThrown` |

---

## Test Structure

Use the Arrange–Act–Assert (AAA) pattern. Include section comments on every test:

```csharp
//  Arrange.
//  Act.
//  Assert.
```

Omit `//  Arrange.` when the section has no code. Treat Act as one logical operation; a multiline
invocation or an exception-capturing delegate may occupy more than one physical line.

---

## Fluent Chain Formatting

Break a long fluent or method-chain statement so each call sits on its own line, with the leading
`.` aligned one indentation level deeper than the receiver. This keeps the receiver, calls, and
arguments visually distinct:

```csharp
configurationStore
    .GetAsync<UserConfiguration>("DefaultConfiguration")
    .Returns(new UserConfiguration
    {
        Id = "DefaultConfiguration",
        Fields = new List<ConfigurationField>
        {
            new() { Name = ConfigurationFields.UserId, Id = _expectedUserId },
            new() { Name = ConfigurationFields.Status, Id = _expectedStatusId }
        }
    });
```

Apply this when a chain contains two or more calls and its single-line form is long or hard to scan.
Keep short, readable chains on one line.

---

## Control Flow Formatting

1. Put a blank line **before** every control-flow statement (`if`, `for`, `foreach`, `while`, `switch`, `try`, …) when it follows another statement, so the control block stands apart from the lines above it.
2. Always wrap the body in braces — even a single-line body. Never use the brace-less one-line form.

So this:

```csharp
_profile.Fields.RemoveAll(field => field.Id == _expectedStatusId);
if (status is not null)
    _profile.Fields.Add(new ProfileField { Id = _expectedStatusId, Value = status });
```

becomes:

```csharp
_profile.Fields.RemoveAll(field => field.Id == _expectedStatusId);

if (status is not null)
{
    _profile.Fields.Add(new ProfileField
    {
        Id = _expectedStatusId,
        Value = status
    });
}
```

---

## Setup Rules

1. Put dependencies and setup shared by most tests in the framework's per-test lifecycle hook, such
   as the test constructor in xUnit or a `[SetUp]` method in NUnit. Keep behavior specific to one
   scenario in that test's Arrange section.
2. Configure only the happy-path defaults that most tests require. Avoid broad mock defaults that
   allow an interaction to succeed without the test arranging or asserting the relevant behavior.
3. Recreate mutable requests, fakes, and the system under test for every test case. xUnit creates a
   test-class instance per test; NUnit setup must initialize fresh state on every run.
4. Promote a common request or input to a private field when most tests use it and each scenario
   changes only the property it exercises. Keep one-off inputs local to their test.
5. Construct the system under test in shared setup when its constructor is not under test and
   scenario-specific arrangements do not affect construction. Construct it in the individual test
   when the constructor behavior or pre-construction setup is the subject of that scenario.
6. Follow the mocking library's actual precedence and null-return APIs. For NSubstitute, later
   matching configurations normally take precedence; verify overload resolution rather than
   assuming an override applies.

---

## Test Rules

1. Keep each test focused on one behavior, with only the arrangement needed to expose it and one
   logical Act operation.
2. Pass a literal or constant directly when its meaning is obvious. Use a named local when the name
   communicates scenario intent that the raw value cannot.
3. If a test requires multiple unrelated assertions, split it into separate tests.
4. Prefer separate tests for result assertions and dependency-interaction assertions when they
   represent distinct behaviors:
   - One test validates the *returned result* — `ExpectedResult` names the response shape (e.g.
     `FailedResultReturned`, `SuccessfulResultReturned`).
   - Another validates *how often a dependency was called* — `ExpectedResult` names the interaction
     (e.g. `CorrectNumberOfCallsMade`, `NoCallsMade`, `SaveCalledThreeTimes`).
   Combine them only when the result and interaction together define one indivisible observable
   outcome; keep the assertions tightly related.
5. Promote constants, builders, and request objects to a shared test project only after multiple
   test projects genuinely reuse them. Prefer the narrowest useful scope.
6. When using NSubstitute with `NSubstitute.ReturnsExtensions`, prefer `.ReturnsNull()` when it
   resolves for the return type. Use an explicit typed null when the extension is unavailable or
   overload resolution fails.
7. When the production behavior treats null, empty, and whitespace identically, cover them with one
   parameterized test using the current framework's syntax, such as NUnit `[TestCase]` attributes or
   xUnit `[Theory]` with `[InlineData]`.

---

## Assertion Helpers

Extract an assertion helper when several tests repeat the same multi-step assertion or when a
domain-specific name makes the expected outcome clearer. Keep a helper private when one class uses
it; promote it to the shared test project only when multiple test classes genuinely reuse it.

An assertion helper must preserve diagnostic quality. Include the values needed to explain a
failure, and do not hide unrelated assertions behind one broad helper. Prefer the assertion
library's native equivalence or collection assertions when they already express the intent clearly.

---

## Repetitive Access Helpers

When the same hard-to-scan expression is repeated across tests — e.g. reaching into a collection to read or write one field:

```csharp
_profile.Fields.First(field => field.Id == _expectedStatusId).Value = status;
```

extract it behind an intention-revealing helper so each call site reads as one obvious line:

- **Used in a single test class** → add a `private` helper method in that class:

  ```csharp
  private static void SetField(UserProfile profile, string id, string value)
      => profile.Fields.First(field => field.Id == id).Value = value;

  // call site
  SetField(_profile, _expectedStatusId, status);
  ```

- **Reused across multiple test files** → promote it to an extension method in a static class under
  an `Assertions/` or `Extensions/` folder in the test project. Move it to a shared test project
  only when multiple test projects reuse it:

  ```csharp
  public static class UserProfileExtensions
  {
      public static void SetField(this UserProfile profile, string id, string value)
          => profile.Fields.First(field => field.Id == id).Value = value;
  }

  // call site
  _profile.SetField(_expectedStatusId, status);
  ```

Provide a matching reader (e.g. `GetField`) only when repeated assertions also need it. Do not add a
helper for a one-off expression.

---

## Helper Method Placement

Place private helper methods at the **bottom** of the test class, after every test method:

```csharp
public class ProfileComposerTests
{
    // ...fields, constructor / [SetUp]...

    // ...test methods...

    private static void SetField(UserProfile profile, string id, string value)
        => profile.Fields.First(field => field.Id == id).Value = value;

    private static UserProfile BuildProfile(...) => ...;
}
```

This placement keeps test cases together and avoids a section-banner comment that merely narrates
the member group. Keep fields and shared setup at the top of the class, following the repository's
member-ordering rules when they differ.

---

## Required Coverage

Cover each applicable observable behavior in the class under test. Do not add a category merely to
satisfy this list when the production contract has no corresponding behavior:

- **Happy path** — the expected successful execution
- **Invalid inputs** — null, empty, or malformed values when the public contract handles them
- **Boundaries** — minimum, maximum, zero, empty collections, and off-by-one values when relevant
- **Failure outcomes** — documented exceptions, error results, or dependency failures visible to
  the caller

Test observable contracts rather than mirroring every implementation branch or private `throw`.
