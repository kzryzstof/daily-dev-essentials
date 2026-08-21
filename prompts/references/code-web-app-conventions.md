# Web Application Project Structure

## Project Overview

This solution is an ASP.NET Core web host. It may expose a Web API, serve a user interface, or do both. It follows a layered, clean-architecture-inspired design that separates domain contracts, application use cases, infrastructure services, and presentation concerns.

The web project is the composition root. It registers every implementation with dependency injection and exposes the application's entry points, such as controllers, minimal API endpoints, or optional UI components. Presentation code does not access databases or external systems directly.

## Solution Structure

The placeholders used below are:

- `{RootNamespace}`: the namespace shared by all projects, for example `{Company}.{ProductName}`
- `{WebHost}`: the name of the application host, for example `WebApi`, `WebApp`, or `Workbench`
- `{Capability}`: one independently implemented infrastructure concern, for example `Persistence`, `Registry`, `Import`, `Integration`, or `Tooling`

```text
{Solution}/
├── src/
│   ├── {RootNamespace}.Abstractions/
│   │   ├── Configuration/
│   │   ├── Diagnostics/                       # Shared LoggerMessageExtensions
│   │   ├── Entities/
│   │   ├── Exceptions/
│   │   ├── Infrastructure/
│   │   ├── Requests/
│   │   ├── Responses/
│   │   ├── Services/                          # I{Capability}Service contracts
│   │   └── ViewModels/                        # Optional: UI-facing interfaces
│   │
│   ├── {RootNamespace}.Application/
│   │   ├── Features/
│   │   ├── Services/
│   │   ├── Validations/
│   │   └── Hosting/
│   │
│   ├── {RootNamespace}.Services.{Capability}/
│   │   ├── {Capability}Service.cs              # Public root implementation
│   │   ├── Abstractions/
│   │   ├── Background/                         # BackgroundService implementations
│   │   ├── Clients/
│   │   ├── Events/
│   │   ├── Extensions/
│   │   ├── Processing/
│   │   ├── Synchronization/
│   │   └── Hosting/
│   │
│   ├── {RootNamespace}.ViewModels/             # Optional: applications with a stateful UI
│   │   ├── Entities/
│   │   ├── Pages/
│   │   ├── Services/
│   │   └── Hosting/
│   │
│   ├── {RootNamespace}.{WebHost}/
│   │   ├── Controllers/                        # For controller-based APIs
│   │   ├── Endpoints/                          # For minimal or grouped APIs
│   │   ├── Contracts/                          # Host-specific HTTP contracts, when needed
│   │   ├── Components/                         # Optional: Blazor UI
│   │   │   ├── Dialogs/
│   │   │   ├── Layout/
│   │   │   ├── Pages/
│   │   │   └── Shared/
│   │   ├── wwwroot/                            # Optional: UI or static assets
│   │   ├── Program.cs
│   │   └── appsettings.json
│   │
│   └── {RootNamespace}.AppHost/                # Optional: .NET Aspire orchestration
│
├── test/
│   ├── {RootNamespace}.Abstractions.UnitTests/
│   ├── {RootNamespace}.Application.UnitTests/
│   ├── {RootNamespace}.Services.{Capability}.UnitTests/
│   ├── {RootNamespace}.ViewModels.UnitTests/   # When ViewModels exists
│   └── {RootNamespace}.Tests.Shared/
│
├── Directory.Build.props
├── Directory.Packages.props
└── {Solution}.slnx
```

The `{RootNamespace}.Services.{Capability}` entry represents a repeatable pattern, not one literal project. Add only the capability projects the application needs. For example, a solution may contain:

```text
{Company}.{ProductName}.Services.Persistence/
{Company}.{ProductName}.Services.Registry/
{Company}.{ProductName}.Services.Import/
{Company}.{ProductName}.Services.Tooling/
```

The internal folders shown for a capability project are illustrative. A registry capability may contain `Registries/` and `Hosting/Background/`, while a persistence capability may contain `Clients/`, `Queries/`, and connection factories.

Organize internal implementations by responsibility or lifecycle, using names
such as `Background`, `Events`, `Processing`, and `Synchronization`. Avoid
generic or redundant folders such as `Services`, `Internal`, or a folder that
repeats the capability project's name.

Every `Services.{Capability}` project has one public capability boundary:

1. Define `I{Capability}Service` under `{RootNamespace}.Abstractions/Services`.
2. Place the public `{Capability}Service` implementation at the root of the capability project.
3. Make `{Capability}Service` implement `I{Capability}Service`.
4. Keep supporting clients, stores, hosted services, handlers, and workflow helpers internal.
5. Register the interface and implementation through the capability project's public `Hosting` extension.

For example, `{RootNamespace}.Services.Persistence` exposes
`PersistenceService : IPersistenceService`. Its database clients, queries,
serializers, and stores remain internal.

## Project Responsibilities

### `*.Abstractions`

Defines the contracts shared by the solution:

- Domain entities and value objects
- Application request and response types
- Transport-neutral application response statuses and payloads
- Shared source-generated logging extensions under `Diagnostics`
- Service and infrastructure interfaces
- View-model interfaces when the solution includes a view-model layer
- Configuration models
- Domain-level exceptions

This project contains no database, HTTP, container, or UI implementation details. All other projects may reference it.

### `*.Application`

Implements the application's use cases:

- Mediator request handlers
- Business workflows and orchestration
- Validation sequences
- Domain-facing generators and application services

Organize handlers by feature or business capability. This project references `Abstractions` and works against interfaces rather than concrete infrastructure implementations.

### `*.Services.{Capability}`

This is the repeatable infrastructure-project pattern. Each project implements one cohesive capability behind contracts defined in `Abstractions`. Create a separate capability project when the concern has distinct dependencies, configuration, ownership, or lifecycle behavior.

The supported public surface of each capability consists of:

- `I{Capability}Service` in `Abstractions/Services`
- The public `{Capability}Service` implementation at the capability-project root
- The public dependency-injection extension under `Hosting`

All other capability classes should be internal unless another assembly
genuinely requires a public type. Consumers, including other capability
projects, depend on `I{Capability}Service`, not the concrete implementation or
its helpers.

When the root `{Capability}Service` coordinates multiple supporting classes,
define internal interfaces for those collaborators under the capability
project's `Abstractions` folder. Inject the internal interfaces into the root
service and register their concrete implementations in the capability's
`Hosting` extension. The root service must not construct stores, clients,
locks, or similar collaborators itself. These internal interfaces are
implementation seams inside one capability and do not belong in the
solution-wide `*.Abstractions` project.

Common examples include:

| Capability | Example responsibility |
|---|---|
| `Persistence` | Database clients, connection factories, queries, commands, serialization, and stored-model mapping |
| `Registry` | In-memory snapshots, status registries, polling, timers, and hosted refresh services |
| `Import` or `Export` | Mapping and workflows for a specific data pipeline |
| `Integration` | Vendor APIs, message brokers, file stores, object stores, or other external systems |
| `Tooling` | Optional development and diagnostic integrations, such as local sidecars |

These names are examples, not a prescribed list. Prefer a capability-specific name that explains what the project owns. Implementation details must not leak into the application, view-model, or UI projects.

Place classes that inherit `BackgroundService` under the capability's
`Background` folder. Name each class after the work it performs and use the
`BackgroundService` suffix, for example `PollingBackgroundService` or
`SocketConnectionBackgroundService`.

### `*.ViewModels`

This is an optional project for applications with a stateful user interface. A Web API with no hosted front end normally does not need it.

When present, it contains presentation state and UI behavior:

- Page view models
- Entity view models
- Selection, filtering, loading, and error state
- Commands that dispatch application requests through the mediator
- Property-change notifications used by the UI

View models may coordinate application requests and service state. They must not execute SQL or depend on a specific UI framework's component types.

### `*.{WebHost}`

The ASP.NET Core web project is the composition root and presentation host:

- Registers application and infrastructure services, plus view-model services when present
- Configures middleware, routing, authentication, authorization, and serialization
- Exposes controllers or minimal API endpoints when the host serves an HTTP API
- Optionally configures interactive rendering and hosts UI components
- Optionally serves CSS, JavaScript, images, and other static assets

Keep `Program.cs` limited to configuration and application composition. Place service-registration logic in a public `Hosting` extension within the project that owns the implementation.

### Configuration and options

Define shared configuration models under `Abstractions/Configuration`. Each
capability's public `Hosting` extension accepts `IConfiguration`, binds the
capability's named configuration section with `AddOptions<T>` or
`Configure<T>`, and registers its services. Capability services consume
`IOptions<T>` (or `IOptionsMonitor<T>` when runtime reloads are required);
`Program.cs` must not manually construct configuration objects or pass concrete
settings into service constructors.

Keep configuration-section names aligned with their configuration-model names
unless an existing external configuration contract requires a legacy name.
Place each setting on the configuration model for the capability that owns and
consumes the behavior; do not keep persistence, retry, caching, or storage
settings on an unrelated integration's configuration merely because that
integration supplies some of the persisted data.
Apply normalization with `PostConfigure`, express invalid settings with options
validation, and use `ValidateOnStart` when invalid configuration should prevent
the application from starting.

### `*.AppHost`

An optional .NET Aspire project may orchestrate databases, containers, emulators, and supporting services for local development. It is operational infrastructure, not a dependency of the domain or application layers.

### Test projects

Create one focused `{ProductionProject}.UnitTests` project for every production
project, including projects that do not have tests yet, so new tests have an
unambiguous home. Each test class must use the same relative folder structure
as the production class it tests, and its namespace must reflect that test
folder.
Each unit-test project references the production project it tests; it must not
reference sibling capability implementations merely to construct a dependency.
Use fakes for cross-capability service contracts instead. Put reusable builders,
fakes, fixtures, constants, and assertion helpers in `*.Tests.Shared` when they
are genuinely shared by multiple test projects.

For dependency-injected constructors and primary constructors, place
`ILogger<T>` first whenever the class injects a logger. List the remaining
dependencies after it.

## Dependency Rules

```text
Controllers / API endpoints ───────────────▶ Application ─────────▶ Abstractions
Optional UI components ─▶ optional ViewModels ──────────┘

Services.{Capability A} ──────────────────────────────────────────▶ Abstractions
Services.{Capability B} ──────────────────────────────────────────▶ Abstractions
Services.{Capability C} ──────────────────────────────────────────▶ Abstractions

Web host ─▶ composes Application, capability services, and optional ViewModels
```

- `Abstractions` is the common contract layer.
- `Application` references only `Abstractions` and required shared domain libraries.
- Each `Services.{Capability}` project references `Abstractions` and implements its `I{Capability}Service` contract.
- Capability projects consume sibling capabilities through their service interfaces and must not reference sibling implementation projects.
- When present, `ViewModels` references `Abstractions`, communicates through application requests and service contracts, and remains independent of the UI framework.
- The web host may reference every project because it is the composition root.
- Infrastructure projects should not reference the web host or view-model project.
- Keep capability implementation details internal. Only the root `{Capability}Service` and its `Hosting` extension are public by default.

The presentation shape does not change the inner layers. A Web API, a server-rendered application, and a combined API/UI host can all use the same application and infrastructure projects. A separately deployed browser or native client communicates with the Web API over HTTP; a server-side UI may dispatch application requests in process.

## Request Flow

A typical Web API request follows this path:

1. A controller or endpoint receives and validates the HTTP request.
2. The endpoint maps the HTTP contract to an application request.
3. The request is sent through the mediator.
4. An application handler coordinates the required service contracts and catches exceptions raised by them.
5. Infrastructure implementations read or update external state.
6. The handler returns a transport-neutral application response describing the outcome.
7. The endpoint maps that response to the appropriate HTTP response.

### Application response handling

Define a shared `ApplicationResponse<T>` contract under `Abstractions/Responses` with these outcome statuses:

- `Ok` for a completed operation with a result.
- `Accepted` for an operation accepted for asynchronous or deferred completion.
- `NotFound` when the requested application resource does not exist.
- `InternalServiceError` when a dependency or unexpected application failure prevents completion.

Application handlers must catch exceptions from service contracts, log each caught exception, and return `InternalServiceError` instead of allowing infrastructure exceptions to cross the mediator boundary. Define source-generated `[LoggerMessage]` extension methods in the shared public `Abstractions/Diagnostics/LoggerMessageExtensions` partial static class, with stable event IDs, levels, and message templates. The layer that catches an exception owns that log entry; controllers must not log the same exception again. Expected outcomes should use `Ok`, `Accepted`, or `NotFound` as appropriate. The web host is solely responsible for mapping application response statuses to HTTP results such as `Ok`, `Accepted`, `NotFound`, or a `500` problem response. Keep ASP.NET Core result types and HTTP status codes out of `Abstractions` and `Application`.

When the host also serves an interactive UI, a typical UI operation follows this path:

1. A page or component receives a user interaction.
2. The component delegates state and behavior to a view model when that pattern is used.
3. The component or view model dispatches an application request.
4. The application and infrastructure layers perform the operation.
5. The presentation state is updated and the UI framework re-renders the affected view.

## Placement Guidelines

- Put controller-based HTTP entry points in `Controllers`.
- Put minimal or grouped HTTP entry points in `Endpoints`.
- Put `BackgroundService` implementations in the owning capability's
  `Background` folder and name them after their responsibility with the
  `BackgroundService` suffix.
- Organize supporting capability implementations by responsibility or
  lifecycle rather than under generic or redundant folders.
- Keep HTTP request and response models at the host boundary when they are transport-specific.
- When using Blazor, put routable screens in `Components/Pages`.
- When using Blazor, put application-wide chrome in `Components/Layout`, modal workflows in `Components/Dialogs`, and reusable elements in `Components/Shared`.
- Keep UI components thin; move substantial workflow and state-management logic into view models or application handlers.
- Place request contracts under `Abstractions/Requests`, grouped by feature.
- Place shared application response contracts under `Abstractions/Responses`.
- Place request handlers under the matching feature in `Application`; handlers log caught service exceptions and return an application response rather than leaking exceptions to presentation.
- Define shared source-generated logging methods in the public `Abstractions/Diagnostics/LoggerMessageExtensions` partial static class, and call those strongly typed extensions from handlers instead of inline `LogError` message templates.
- Define every capability's `I{Capability}Service` contract under `Abstractions/Services`.
- Put the public `{Capability}Service` implementation at the root of its `Services.{Capability}` project.
- Make supporting capability classes and their interfaces internal; inject
  those interfaces into the root capability service. Consume other
  capabilities through their public service interfaces.
- Keep database clients, SQL, containers, and vendor SDK types inside the appropriate `Services.{Capability}` project.
- Register each project's services through its own `Hosting` extension.
- Pass `IConfiguration` from the composition root to each capability's
  `Hosting` extension, bind named sections there, and inject `IOptions<T>` into
  capability services.
- Use `Directory.Packages.props` for centralized NuGet package versions and `Directory.Build.props` for shared build settings.

## Implementation Readability

- Keep orchestration methods at one level of abstraction. Extract retry,
  exception-handling, cleanup, and other lower-level mechanics into
  intention-revealing private methods.
- Use blank lines to separate distinct operations, such as logging, awaiting
  work, and returning, when the separation makes the control flow easier to
  scan. In particular, leave a blank line before a control-flow statement such
  as `if`, `for`, `foreach`, or `while` when it follows a declaration, awaited
  operation, or other executable statement in the same block.
- Do not pass information as a separate parameter when another argument
  already carries it. Keep explicit contextual parameters when the source
  object may legitimately omit that information.

## Typical Libraries and Frameworks

- C# and .NET
- ASP.NET Core
- ASP.NET Core controllers or minimal APIs for HTTP endpoints
- Optionally, Blazor or another UI framework when the host serves a front end
- Optionally, a component library such as Radzen Blazor
- Mediator for requests and application handlers
- PostgreSQL or another persistence provider behind service contracts
- .NET hosted services for periodic background work
- .NET Aspire for optional local orchestration
- xUnit, a mocking library, and fluent assertions for tests

These technologies reflect the reference architecture and may be substituted when the solution has different requirements.

## UI Guidelines

These guidelines apply only when the web host serves a user interface:

- Use a modern, clean, responsive design.
- Keep pages focused on one user workflow.
- Provide explicit loading, empty, success, and error states.
- Build repeated interaction patterns as shared components.
- Keep business decisions out of UI markup and code-behind files.
