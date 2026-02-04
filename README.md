# Misc

A collection of miscellaneous code snippets, utilities, configurations, and prompts.

## Repository Structure

### `azure/`
Azure-related utilities and helpers.

- **`function_apps/`** - Helper classes for Azure Functions, including `HostHelper.cs` which provides utilities to build `IHost` instances for dependency injection in Azure Functions, particularly useful for integration testing with mock services.

### `csharp/`
C# code snippets and utilities.

- **`tests/`** - Testing utilities, including `ObjectExtension.cs` which provides a Moq extension method `OrEquivalent()` that uses FluentAssertions for object comparison in mock verifications.

### `ide/`
IDE configuration files.

- **`rider.file-format`** - JetBrains Rider file layout/member reordering patterns configuration (XML format) for consistent code organization.

### `prompts/`
AI/LLM prompt templates.

- **`work/`** - Work-related prompts, including `nunit_add_setname.md` which provides a template for naming NUnit `TestCaseData` with `SetName()` following a consistent naming convention.
