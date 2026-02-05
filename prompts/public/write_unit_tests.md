# Unit Test Generation

Generate comprehensive unit tests for the provided class.

## Test Naming

Format: `MethodName_Scenario_ExpectedResult`

Example: `GetUser_IdIsValid_UserReturned`

## Test Structure

Use AAA pattern with section comments:
```csharp
//  Arrange.
//  Act.
//  Assert.
```

## Setup Rules

1. Define and configure all mocks in the test class constructor
2. Set default mock return values that cover happy path scenarios
3. Override mock behavior in Arrange section only for edge cases and exceptions

## Test Rules

1. Keep tests minimal: no or few Arrange lines, one Act line, one or more Assert lines
2. Use constants directly in Act section without intermediate variable assignments
3. Multiple assertions may indicate the test should be split
4. Place reusable constants (including request objects) in the shared project for reusability across tests

## Required Coverage

- Happy path
- Edge cases
- Exceptions
- Null/empty inputs
- Boundary conditions
