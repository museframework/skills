# Architecture, lifecycle and version selection

## Find authoritative contracts

Read the consumer application's `pom.xml` and effective dependency management first. Identify the Muse BOM, connector API/runtime artifacts, Maven plugins and host adapter. A website example is not proof that a different installed version exposes the same API. Read the matching source or source JAR before using unfamiliar symbols.

- [Framework source](https://github.com/museframework/muse)
- [Architecture](https://github.com/museframework/muse/blob/main/ARCHITECTURE.md)
- [Framework AGENTS.md](https://github.com/museframework/muse/blob/main/AGENTS.md)
- [Public architecture documentation](https://museframework.dev/docs/concepts/architecture/)

## Ownership boundaries

| Layer | Owns |
| --- | --- |
| `muse-dsl` | Kotlin declarative builders, models and flow-reference validation |
| `muse-engine-api` | Public event, processor, result, streaming and SPI contracts |
| `muse-engine` | Lifecycle, bootstrap, pipeline resolution and runtime execution |
| Connector `*-api` | Typed operations, configurations and public source models |
| Connector runtime | Transport implementation, component registration, resource ownership |
| Spring/Quarkus adapter | Application-host and transport integration |
| Babelfish providers | Supported Mule XML-to-Kotlin source translation |

Connector runtime implementations must not depend on the engine implementation. Follow accepted ADRs, tests and local module rules for code-level work.

## Lifecycle

Muse uses Bootstrap → Init → Start. Bootstrap validates supported static references against registered flows, Init resolves sources and processors, Start activates external resources. Finding a `flow` call in source does not establish that the host registers it.

## Version checks

1. Resolve the artifact/version actually used by the consumer project.
2. Check the applicable source, test and documentation revision.
3. If the release is unavailable or uncertain, disclose the gap instead of inventing a method or claiming support.
4. Do not change dependency versions or switch runtime hosts without explicit authorization.
