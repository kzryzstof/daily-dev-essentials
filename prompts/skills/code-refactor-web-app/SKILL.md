---
name: code-refactor-web-app
description: v0.1.1 — Refactors an existing ASP.NET Core web application or Web API toward the layered project structure defined by the shared web-application conventions. Use when Codex needs to reorganize a .NET web solution, separate abstractions, application handlers, capability services, optional view models, and the presentation host, correct project-reference direction, or move misplaced controllers, endpoints, UI components, persistence, integrations, and composition code while preserving behavior and keeping builds and tests green.
---

# Refactor an ASP.NET Core Web Solution

Refactor an existing ASP.NET Core solution to conform to the shared web-application conventions
without changing its observable behavior.

## Reference — read before editing

Read `../references/code-web-app-conventions.md` completely before analyzing or editing. That path
is relative to this `SKILL.md` after installation with `prompts/scripts/update-skills.py`. In this
source repository, use `../../references/code-web-app-conventions.md`.

## Required context

Identify the solution or repository root. If it cannot be inferred from the current workspace or
the user's target, ask for it.

Treat the convention as a template:

- Derive `{RootNamespace}`, `{WebHost}`, and `{Capability}` from the repository.
- Do not rename projects merely to reproduce placeholder names.
- Treat `Services.{Capability}` as a repeatable pattern, not a prescribed project list.
- Treat view models, UI components, static assets, and Blazor-specific structure as optional.

## Scope

Apply the guideline to an existing solution. This includes:

- Project and folder responsibilities
- Project-reference direction
- Dependency-injection composition
- Placement of contracts, handlers, infrastructure, endpoints, and optional UI code
- Test-project alignment

Preserve:

- Public HTTP routes, verbs, status codes, request and response shapes
- Authentication and authorization behavior
- Configuration keys and binding behavior
- Serialization behavior
- Database and external-system behavior
- Hosted-service lifecycle and ordering
- UI routes, rendering modes, and user-visible behavior when a UI exists
- Public .NET APIs unless the user explicitly authorizes a breaking change

Do not perform unrelated style, naming, or algorithm refactors.

## Workflow

### 1. Inspect repository state

1. Check the working tree before editing.
2. Preserve all pre-existing user changes. Do not discard, overwrite, or reformat them.
3. Locate:
   - Solution files and project files
   - Central build and package-management files
   - Web host entry points
   - Test projects
   - Existing architecture documentation
4. Determine whether the host is:
   - Web API only
   - UI only
   - Combined API and UI
   - A web host serving a separately deployed client
5. Detect the actual UI framework, if any. Apply Blazor guidance only when Blazor is present.

### 2. Establish a green baseline

Run the repository's documented restore, build, and test commands. Prefer an existing solution-level command. When no command is documented:

```bash
dotnet build <solution>
dotnet test <solution> --no-build
```

Record:

- Commands executed
- Build result
- Test projects and pass counts
- Existing failures

If the solution does not build or relevant tests fail, do not start a broad structural refactor. Diagnose whether the failure predates the task. Continue only when the user explicitly accepts that baseline or when a narrowly scoped, clearly unrelated project can still be verified independently.

### 3. Inventory the architecture

Build an evidence-backed inventory from project files and source:

| Concern | Inspect |
|---|---|
| Contracts | Entities, value objects, interfaces, application requests/responses, configuration models |
| Application | Mediator handlers, use cases, validation, orchestration |
| Capabilities | Persistence, registries, imports/exports, external integrations, tooling, background work |
| Presentation | Controllers, minimal API endpoints, transport contracts, optional UI components and view models |
| Composition | `Program.cs`, hosting extensions, middleware, service registration |
| Tests | Project coverage, shared fixtures, references to implementation internals |

Inspect every `.csproj` project reference and produce the current dependency graph. Do not infer dependency direction from folder names alone.

### 4. Compare against the convention

Classify each finding:

- **Conforming** — leave it unchanged.
- **Misplaced code** — move it to an existing project or folder with the correct responsibility.
- **Invalid dependency** — remove or invert the reference through a contract.
- **Mixed capability** — split only when the concerns have genuinely distinct dependencies, configuration, ownership, or lifecycle.
- **Missing boundary** — introduce a project only when code already demonstrates a stable architectural responsibility.
- **Optional and absent** — do nothing. Do not create view-model, Blazor, AppHost, or capability projects speculatively.

Prefer the smallest change that restores a clear responsibility and valid dependency direction.

### 5. Plan dependency-safe phases

Order changes from inner contracts outward:

1. Establish or correct abstractions.
2. Move application requests and handlers.
3. Isolate each required `Services.{Capability}` implementation.
4. Correct optional view-model placement when a stateful UI uses that pattern.
5. Reduce the web host to presentation and composition concerns.
6. Align test projects and shared test helpers.
7. Remove obsolete references only after all callers have migrated.

For each phase, list:

- Files and projects affected
- Reference changes
- Namespace and accessibility changes
- DI registrations that must move
- Tests that prove behavior is preserved

Ask for confirmation before changing public APIs, HTTP contracts, persisted data formats, externally consumed project names, or deployment topology. Ordinary internal file moves and reference corrections do not require an extra gate.

### 6. Refactor incrementally

For every phase:

1. Move contracts before implementations that consume them.
2. Keep interfaces in `*.Abstractions` when they define cross-project boundaries.
3. Keep application handlers dependent on contracts, not concrete infrastructure.
4. Place each infrastructure implementation in the capability project that owns it.
5. Keep controllers, endpoints, and transport-specific models at the web-host boundary.
6. Keep `Program.cs` focused on configuration and composition.
7. Put each project's registrations in that project's `Hosting` extension when the repository uses this convention.
8. Update project references, namespaces, DI registrations, internals visibility, and tests in the same phase.
9. Build after the phase before continuing.

Do not introduce a generic `Integration` or `Registry` project solely because it appears as an example in the convention. Name capability projects for what they actually own.

### 7. Apply presentation rules conditionally

For Web APIs:

- Use `Controllers` for controller-based entry points or `Endpoints` for minimal/grouped APIs.
- Keep transport-specific request and response models at the host boundary.
- Map transport contracts to application requests.
- Keep HTTP concepts out of application and capability projects.

For applications with a hosted UI:

- Keep framework components thin.
- Use a separate view-model project only when the application has meaningful stateful presentation logic.
- Preserve UI routes, rendering mode, component behavior, and static-asset paths.

For Blazor specifically:

- Apply `Components/Pages`, `Components/Layout`, `Components/Dialogs`, and `Components/Shared` placement only when those concepts exist.
- Do not add Blazor packages, rendering modes, Radzen, `wwwroot`, or Razor components to API-only solutions.

### 8. Verify boundaries and behavior

After all phases:

1. Recompute the project-reference graph.
2. Confirm:
   - Application does not reference concrete capability implementations.
   - Capability projects do not reference the web host or optional view-model project.
   - Presentation code does not directly implement persistence or external integrations.
   - The web host remains the composition root.
3. Run a clean solution build.
4. Run the same tests recorded at baseline.
5. Run focused API, integration, or UI tests affected by moved boundaries.
6. Run formatting or analyzers only when already configured by the repository.

If a regression appears, isolate and correct the responsible phase. Do not declare success with a red build or newly failing tests.

## Report

Summarize:

- Host type detected
- Root namespace and capability projects identified
- Architectural gaps corrected
- Projects, files, and references moved or added
- DI and composition changes
- Conditional UI guidance applied or intentionally skipped
- Before/after dependency direction
- Baseline and final build/test results
- Remaining deviations, with reasons

Leave changes in the working tree for review. Do not commit unless the user explicitly asks.

## Hard constraints

1. Read and apply the shared convention before acting.
2. Preserve behavior and external contracts by default.
3. Do not force every example project into every solution.
4. Keep Blazor and all UI-specific guidance conditional.
5. Do not create empty architectural layers.
6. Do not hide dependency violations with service locators, reflection, or duplicated contracts.
7. Do not move implementation details into `Abstractions`.
8. Preserve pre-existing user changes.
9. Keep each phase buildable and testable.
10. Report verification evidence honestly.
