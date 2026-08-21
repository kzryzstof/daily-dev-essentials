---
name: code-upgrade-dotnet
description: v0.2.0-alpha — Upgrades a CPM-enabled SDK-style .NET solution to a user-specified .NET version, sets LangVersion to latest, updates compatible stable NuGet packages and CI/container runtime pins, resolves upgrade-related compatibility issues, and verifies restore, build, and tests. Use for a coordinated .NET runtime and dependency upgrade; migrate solutions to Central Package Management separately first.
---

# Upgrade a .NET Solution

Upgrade the target framework, language version, owned direct packages, and build environments as one coherent change. Preserve application behavior and repository boundaries while resolving compatibility work required by the requested version.

## Required input gate

Require the target .NET major/minor version, such as `10.0`, before inspecting or editing the repository. If the user did not provide it, ask exactly one concise question and wait:

> What .NET version should this solution target (for example, `10.0`)?

Do not infer “latest.” Normalize the answer into the target framework (`net10.0`), CI SDK band (`10.0.x`), and container tag (`10.0`) only after confirming the release exists. Default package policy to the newest stable compatible version; include prerelease packages only when the user explicitly requests them.

## 1. Establish scope and baseline

1. Read repository instructions and inspect `git status`. Preserve unrelated user changes.
2. Identify the root solution, all owned projects, submodules, nested build/package boundaries, and the applicable `Directory.Build.props`, `Directory.Packages.props`, effective NuGet configuration hierarchy, `global.json`, lock files, workload manifests, Dockerfiles, and pipeline YAML.
3. Keep submodule-owned and independent nested solutions outside the mutation boundary. Still inspect included projects and shared configuration inheritance so the root upgrade does not change excluded code accidentally.
4. Require Central Package Management for the selected root. If no applicable `Directory.Packages.props` enables `ManagePackageVersionsCentrally`, stop and recommend `code-enable-cpm`; do not combine CPM adoption with the runtime upgrade.
5. Inventory effective target frameworks, language versions, SDK/runtime pins, runtime identifiers, workloads, every owned `PackageVersion`, intentional conditions, package-source mappings, and direct `PackageReference` exceptions such as `VersionOverride`.
6. Record the resolved direct package graph and run the repository's normal restore, build, and tests before editing. Report baseline failures and continue only when upgrade failures can be distinguished from them.

Confirm the requested .NET release, support status, required SDK/IDE versions, and every intervening major version's breaking changes using current official Microsoft documentation. Do not rely on memory for release or support information.

## 2. Update target framework, language version, and SDK pins

Update the applicable `TargetFramework` or `TargetFrameworks` in `Directory.Build.props`. Preserve platform suffixes, for example `net8.0-windows` to `net10.0-windows`. For multi-targeted projects, replace only the modern .NET targets selected for upgrade; preserve `.NET Framework` and `netstandard` targets unless the user includes them.

Evaluate root property inheritance across every descendant project before editing. If excluded submodule or independent projects would inherit the root settings, scope the applicable `PropertyGroup` to owned projects with a stable, explicit repository-relative condition. Do not edit excluded projects to counteract leaked `TargetFramework` or `LangVersion` values. Verify effective evaluated properties for both owned and excluded projects after the change.

Set this shared property in `Directory.Build.props`:

```xml
<LangVersion>latest</LangVersion>
```

Replace any existing shared numeric, preview, or other `LangVersion` value with `latest`. Remove redundant `LangVersion` overrides from owned project files when they are intended to follow the shared setting. Preserve an override only when a project has a documented compatibility constraint, and report it as an exception. Verify the selected stable SDK accepts the effective language version; do not use `preview` unless explicitly requested.

Inspect owned project files for target-framework values that intentionally override the root. Update those that represent the same application/test target; retain project-specific targets only with a documented compatibility reason. Update related explicit properties only when they pin the old runtime, including `RuntimeFrameworkVersion`, targeting-pack versions, test-host runtime settings, and generated-output paths containing the old TFM.

When `global.json` exists, update it to a real stable SDK compatible with the requested runtime and preserve intentional `rollForward`, `allowPrerelease`, workload, and MSBuild SDK settings. When it is absent, do not create one unless repository conventions or the user explicitly require an SDK pin; CI and container version updates remain mandatory. Run `dotnet workload restore` when the solution uses workloads; do not install or remove unrelated workloads.

## 3. Resolve the newest compatible package versions

Authenticate to the effective configured sources without writing credentials to tracked files. Respect the complete NuGet configuration hierarchy and any source mappings; do not create a repository `NuGet.config` merely for this upgrade. Treat an inaccessible private feed as a blocker for packages mapped to it; never guess a private package's newest version.

After retargeting, query current feed metadata rather than hard-coding versions. Prefer machine-readable CLI output when supported:

```bash
dotnet package list --project <solution> --outdated --format json
```

Use `dotnet list <solution> package --outdated --format json` with SDKs that predate the noun-first form. Check `--help` rather than assuming syntax. Use exact package searches against the configured sources when the outdated report cannot evaluate a centrally pinned package.

For every effective `PackageVersion` in the selected CPM boundary:

- Select the highest stable version that restores for every project/framework using that entry, including new major versions.
- Preserve project-, framework-, and configuration-specific conditions. When consumers need different latest compatible versions, retain separate conditioned entries rather than forcing one version.
- Update intentionally pinned transitive packages already present in `Directory.Packages.props`, but do not add versions for unpinned transitive dependencies.
- Preserve all `PackageReference` metadata and intentional `VersionOverride` items. Verify and report overrides separately instead of silently centralizing them.
- Do not downgrade an existing prerelease to an older stable version. Move to a newer stable release when available; otherwise retain it and report the prerelease exception unless the user authorized prerelease updates.
- Replace deprecated packages only when an official successor is clear and the replacement is necessary for the requested runtime; report this as a package substitution, not a version bump.

Capture an explicit old → new version table before editing. Update `Directory.Packages.props` without reordering unrelated entries. Refresh tracked `packages.lock.json` files using the repository's lock-file policy.

## 4. Update build and runtime pipelines

Search all tracked YAML, Dockerfiles, scripts, deployment manifests, and reusable-workflow inputs for the old SDK, runtime, TFM, language version, and solution output paths.

Update, as applicable:

- GitHub Actions `setup-dotnet` versions and matrices.
- Azure Pipelines `UseDotNet` tasks or equivalent SDK installers.
- Docker SDK, ASP.NET runtime, and runtime-deps `FROM` tags while preserving image flavor, OS, and architecture suffixes.
- Build arguments, environment variables, cache keys, artifact paths, test settings, coverage paths, and publish paths containing the old TFM.
- Hosting/runtime declarations that determine which .NET runtime executes the deployed application.

Keep SDK and runtime stages on the requested major/minor version. Do not update unrelated action versions, base operating systems, service images, triggers, permissions, or deployment tooling merely because newer versions exist.

Audit the final stage's `USER` declaration whenever its resolved runtime tag is a chiseled variant (for example `-noble-chiseled`, `-noble-chiseled-extra`) — these images ship a predefined non-root `app` user. If that stage has no explicit `USER` line yet, add one immediately before `ENTRYPOINT`/`CMD`, matching the convention already established by other repos' chiseled Dockerfiles:

```dockerfile
# Switch to a non-root user to appease Wiz but solve no actual problem.
# The .NET chiseled images ship with a predefined non-root user named "app".
USER app
```

This applies whether the image was already chiseled before the upgrade or only becomes chiseled as part of it — treat it as a standing property of the resolved tag, not something triggered only by a tag change. Do not add a `USER` line when the resolved base image is not chiseled (no predefined `app` user exists) or when the final stage already declares one, and never invent a new user or UID.

Follow referenced reusable workflows or external pipeline templates far enough to identify runtime pins. Update them only when they are repository-owned and in scope; otherwise report the external pin and the coordination required.

## 5. Restore, compile, and address compatibility

1. Restore the full solution with the target SDK and `--force-evaluate` when supported.
2. Build with the repository's normal configuration and warnings visible.
3. Run all normal unit, integration, and end-to-end tests that are practical in the repository's established workflow.
4. Fix source, configuration, analyzer, serialization, hosting, and test changes directly caused by the runtime, `LangVersion=latest`, or package upgrades. Consult official breaking-change documentation for the target and every skipped major version before choosing a workaround.
5. Prefer adapting code to supported APIs over suppressing warnings, disabling analyzers, pinning old packages, or adding compatibility switches. Use a lower package version only when the newest release is demonstrably incompatible with the requested target, and select the newest compatible stable version with evidence.
6. Re-run restore, build, and affected tests after each compatibility fix until the complete validation set is green.

Do not claim the upgrade is complete while compilation or tests fail. If an external service, credential, platform, workload, or incompatible vendor package blocks validation, exhaust safe local checks and report the exact blocker and last passing stage.

## 6. Final audit

1. Search for stale references to the old TFM, SDK/runtime major, container tag, numeric/preview `LangVersion`, and output path. Classify intentional historical text and excluded submodule pins rather than editing them.
2. Run the outdated-package query again. Every remaining owned direct/central package must be current, intentionally prerelease/pinned, or documented as the newest compatible version.
3. Review `dotnet package list --vulnerable` and `--deprecated` separately; these switches cannot be combined with `--outdated`.
4. Inspect the final diff for accidental source changes, lost package metadata, credential leakage, unrelated pipeline churn, and altered submodules.
5. Report the requested .NET version, effective `LangVersion`, SDK/runtime pins changed, complete package old → new table, compatibility changes, pipeline/container files changed, remaining exceptions, and before/after validation results.

## Constraints

- Never begin mutation without the user-specified target .NET version.
- Always set the shared `LangVersion` to `latest`; never substitute `preview` without explicit instruction.
- Never interpret “most recent packages” as permission to adopt prerelease versions.
- Never guess package versions or claim currency without querying the configured feeds during the run.
- Never edit excluded submodules or nested independent build roots.
- Never hide upgrade failures by suppressing warnings, skipping tests, or retaining an old dependency without reporting it.
- Never store NuGet credentials or tokens in tracked files, command output, or reports.
