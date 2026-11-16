# Target runtimes: Spring Boot default, Quarkus opt-in

**Source inspection date:** 2026-11-14. Recheck the chosen plugin artifact's behavior before asserting support.

## Runtime resolution

`RuntimeResolver.resolve(explicitConfig, projectArtifacts)`:

1. Explicit `<configuration><runtime>...</runtime></configuration>` or `-Dmuse.runtime=...` wins.
2. Otherwise detects markers among resolved compile/runtime artifacts (`muse-spring-boot`, `spring-boot`, `muse-quarkus`, `quarkus-core`, etc.).
3. Ambiguity fails. With no detection it returns `None`; `MuseMigrateMojo` converts `None` to Spring Boot, not a no-host project.

For a repeatable migration, use explicit `-Dmuse.runtime` and record it in the report.

## Spring Boot

- `muse:migrate` generates Spring-specific Muse configuration Kotlin, a Spring application entry point, `application-muse.properties`, and a Spring-based Maven POM.
- Reflection-backed `MuseConfigComponent` is used for normal generation; the native build mode uses an explicit `MuseConfigProvider` contract.
- For host-execution workflows with an appropriately configured POM: `spring-boot:run`. Build/repackage must be checked in the actual generated POM; do not claim `mvn package` yields an executable Boot JAR until the Boot packaging goal has been configured and verified.
- Spring Boot target is the **default** and is the only host covered by the published website MuleSoft migration tutorial's real parity evidence (Muse 0.2.0 vs Mule EE 4.11.0 for a bounded sample).

## Quarkus

- `muse:migrate -Dmuse.runtime=quarkus` generates Quarkus-flavored CDI configuration Kotlin, `application.properties`, and a Quarkus Maven POM with Quarkus host extension and HTTP extension when applicable.
- The dedicated Quarkus Maven plugin handles build and dev start (`quarkus:dev`); the image path is host-specific and not equivalent to Spring Boot Buildpacks. The Quarkus migration fixture uses `-Dmuse.nativeBuild=true` to generate an explicit `MuseConfigProvider` and native profile.
- **Blocking known limitation:** the inspected `QuarkusRuntimeStrategy.migrationCompatibilityErrors()` returns a fatal error for the `apikit` XML namespace. Do not work around by dropping APIKit or ignoring the error. The presence of a handwritten APIKit Quarkus adapter and related tests does not remove this migration-specific gate.
- Quarkus artifact publication/resolution and actual migrated-project compilation/startup must be verified in the consumer environment. A Maven Invoker fixture asserting POM/CDI output is not a production proof of behavioral parity.

| Concern | Spring Boot | Quarkus |
| --- | --- | --- |
| Default for `muse:migrate` | Yes | No |
| Explicit steering | `spring-boot` | `quarkus` |
| Host dependency | `muse-spring-boot` | `muse-quarkus` |
| HTTP adapter | `muse-http-connector-spring` | `muse-http-connector-quarkus` |
| APIKit Mule XML migration | Demonstrated for bounded Spring example | Explicitly blocked by inspected migration strategy |
| Runtime bootstrap file | `*Application.kt` and Muse properties | CDI config and `application.properties` |
| Dev command after POM reconciliation | `spring-boot:run` | `quarkus:dev` |

Do not automatically infer Quarkus migration compatibility from mapper coverage: `muse:check` operates independently of the host runtime.

## Authoritative pointers

- [SpringBootRuntimeStrategy](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-plugin-core/src/main/kotlin/dev/museframework/plugin/core/runtime/spring/SpringBootRuntimeStrategy.kt)
- [QuarkusRuntimeStrategy](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-plugin-core/src/main/kotlin/dev/museframework/plugin/core/runtime/quarkus/QuarkusRuntimeStrategy.kt)
- [Quarkus Maven Invoker fixture](https://github.com/museframework/muse/tree/main/muse-maven-plugin/muse-plugin-it/src/it/migrate-quarkus)
- [Verified website MuleSoft migration tutorial](https://github.com/museframework/muse-website/blob/main/src/pages/guides/mulesoft-to-muse.md)
