---
name: building-with-muse
description: Build, modify, debug, or test native Kotlin integrations with the Muse framework, typed DSL, supported connectors, and Spring Boot or Quarkus hosts. Use for Muse application development and review. For Mule 4 XML assessment or translation use the separate mulesoft-to-muse skill.
compatibility: Requires access to the target project's files. Executing builds requires JDK 21, Maven 3.9+, and resolvable compatible Muse artifacts.
---

# Build and maintain native Muse integrations

Muse is a typed Kotlin integration framework. Use the public DSL and reusable connectors; do not recreate transport infrastructure or the runtime. Kotlin compilation checks types, not registration, execution semantics or deployed behavior.

## Safety and evidence

- Inspect the project's `pom.xml`, selected Muse version, host, existing flows and tests before writing code. Never infer an installed release from GitHub `main`.
- Resolve unfamiliar public APIs using Kotlin LSP, the selected dependency, source and official documentation. Never fabricate a component, operation or contract.
- Respect declarative DSL, Engine API, engine runtime, connector API/runtime and host-adapter boundaries. When changing framework code, read the applicable repository `AGENTS.md`, `ARCHITECTURE.md` and accepted ADRs first.
- Preserve current behavior and external side effects unless explicitly asked to change them. Never expose credentials, customer payloads or secrets.
- Never edit or commit generated files in `target/`. Migrated application sources in `src/main/kotlin` are distinct from disposable `muse:generate` output.
- Do not silently migrate, deploy, publish, commit, merge or switch runtime hosts. Ask before irreversible operations.
- Distinguish inspected source, compilation, tests, runtime validation and deployment. None implies the next stage has passed.
- For Mule XML migration or compatibility assessment use the separate `mulesoft-to-muse` skill. Do not replace deterministic Babelfish translation with speculative LLM rewriting.

## 1. Discover the target application

1. Read Maven coordinates and dependency management. Identify installed Muse/connector versions and Spring Boot or Quarkus host configuration.
2. Identify registered flows, `MuseConfigProvider` and relevant runtime configuration. A Kotlin `flow(...)` declaration alone does not prove registration.
3. Inspect existing tests and record the expected payload, error, resource and external-side-effect contracts.
4. Load [architecture and version guidance](references/architecture-and-versions.md) if the host, module boundary or artifact compatibility is uncertain.

## 2. Discover the public DSL

1. Use Kotlin LSP and compilation with the actual classpath to inspect the correct builders and overloads when supported by the harness.
2. Load [flows and errors](references/flows-and-errors.md) and [connectors and hosts](references/connectors-and-hosts.md) only when relevant to the task.
3. Prefer changing a typed Muse component configuration to introducing a bespoke transport or framework abstraction.
4. Check bootstrapping and flow registration separately from Kotlin type checking. `flowRef(String)` can compile while naming a missing registered flow.
5. Handle streaming, error handlers and DataWeave according to documented contracts; do not assume all payloads are materialized or that DataWeave is absent.

## 3. Implement and verify

1. Make the smallest reviewable source change and preserve unrelated code.
2. Compile and run focused tests using the project's actual Maven profiles; see [verification and review](references/verification-and-review.md).
3. Fix failing assertions by diagnosing the code, not by changing expected results or hiding failures.
4. Where the task affects a connector, host, retry, error path or external system, run the appropriate isolated integration or packaged tests when available.
5. Inspect the final diff for resource leaks, credentials, unexpected side effects, regressions and generated files.

## 4. Return a verifiable report

State the application host and Muse version; list changed files; identify intended and externally observable behavior; report exact commands, passed/failed/skipped tests, failures, blockers and remaining review risks. Explicitly distinguish edited, compiled, tested, committed, merged, released and deployed.

## Read references on demand

- [Architecture, lifecycle, version selection](references/architecture-and-versions.md)
- [Flows, errors and expressions](references/flows-and-errors.md)
- [Connectors and hosts](references/connectors-and-hosts.md)
- [Verification and review](references/verification-and-review.md)

Use the [public technical documentation](https://museframework.dev/docs/) for current examples and contracts. The skill is not a replacement for the public reference.
