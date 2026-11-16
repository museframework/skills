# Dependency steering: two realms, two concerns

**Do not merge the plugin mapper classpath with the application's runtime classpath.** This is the crucial control point for deterministic Muse migration.

## 1. Plugin realm: mapper discovery for check/migrate

`TranslatorRegistry` discovers `BabelfishMapperProvider`s with `ServiceLoader` using the classloader that loaded the plugin core. `MuseCheckMojo` and `MuseMigrateMojo` use this registry. The `core` provider is bundled transitively by the plugin; optional provider artifacts belong under the Maven **plugin** dependencies.

Example for a Mule application containing HTTP and APIKit (replace `RELEASE_VERSION` with a verified published version):

```xml
<build>
  <plugins>
    <plugin>
      <groupId>dev.museframework.maven</groupId>
      <artifactId>muse-maven-plugin</artifactId>
      <version>RELEASE_VERSION</version>
      <configuration><runtime>spring-boot</runtime></configuration>
      <dependencies>
        <dependency>
          <groupId>dev.museframework</groupId>
          <artifactId>muse-http-babelfish-mappers</artifactId>
          <version>RELEASE_VERSION</version>
        </dependency>
        <dependency>
          <groupId>dev.museframework</groupId>
          <artifactId>muse-apikit-babelfish-mappers</artifactId>
          <version>RELEASE_VERSION</version>
        </dependency>
      </dependencies>
    </plugin>
  </plugins>
</build>
```

Known optional mapper providers in the inspected codebase (all under group `dev.museframework`):

| Mule family | Plugin dependency artifactId |
| --- | --- |
| HTTP listener/request | `muse-http-babelfish-mappers` |
| APIKit | `muse-apikit-babelfish-mappers` |
| Database | `muse-db-babelfish-mappers` |
| File | `muse-file-babelfish-mappers` |
| SFTP | `muse-sftp-babelfish-mappers` |
| Core/EE common | Core mapper bundled by plugin |

This is **a candidate provider inventory**, not a universal guarantee of coverage. Each specific XML operation/attribute must be checked by the installed provider and release. Custom Mule connectors are not automatically supported.

If a checker reports missing mappings, first audit that the relevant provider is declared under `<plugin><dependencies>` and successfully resolved; adding the artifact only in project dependencies cannot fix ServiceLoader discovery within the plugin realm. When mapper registration is present but a specific component is still unsupported, keep it as a coverage gap.

## 2. Application realm: runtime detection and execution

The runtime resolver sees *project* Maven artifacts with `compile` or `runtime` scope, excluding `test` and `provided`. It recognizes Spring Boot and Quarkus marker artifact IDs. With no explicit runtime and no markers, **`muse:migrate`** selects Spring Boot as a fallback. If both are detected, auto-detection is ambiguous and fails.

Known application runtime host dependencies:

- Spring Boot host: `dev.museframework.connectors:muse-spring-boot`.
- HTTP on Spring: `dev.museframework.connectors:muse-http-connector-spring`.
- APIKit on Spring: `dev.museframework.connectors:muse-apikit-connector-spring`.
- Quarkus host: `dev.museframework.connectors:muse-quarkus`.
- HTTP on Quarkus: `dev.museframework.connectors:muse-http-connector-quarkus`.

Application runtime dependencies and connector families may require additional modules (File, SFTP, DB, drivers, RAML resources, etc.). Verify each actual connector contract and transitive classpath. Source namespace discovery determines the generated POM's limited host dependencies, but does **not** automatically migrate every original project dependency.

Explicit `muse.runtime` is preferable for deterministic result selection:

```bash
mvn muse:migrate -Dmuse.runtime=spring-boot
mvn muse:migrate -Dmuse.runtime=quarkus
```

You can steer via project dependencies instead, but confirm Maven's actual resolved artifacts, including transitive dependencies, before relying on auto-detection. Distinguish **the runtime that shapes emitted code/POM** from **the mapper providers available for translation**.

## 3. Generated POM follow-up

The inspected Spring/Quarkus `*PomXmlGenerator` implementations hardcode Muse **0.1.0** even when the Maven reactor is at 0.2.1. Inspect and correct the generated POM using a mutually compatible, resolvable **real** release. The POM generators also cannot infer custom repositories/credentials, non-Muse APIs, drivers, tests, and organizational deployment conventions.

The Spring generator includes an outdated MuleSoft releases repository stanza; inspect whether it remains necessary and whether it conflicts with the requirement for a clean Muse project. Avoid copying credentials or blindly preserving every source dependency.

After `muse:migrate`, the generator may not include the Muse Maven plugin in the **generated** POM, since it has emitted source into `src/main/kotlin`. To continue XML-first generation instead, use the documented `muse:generate` workflow and an intentionally configured plugin. Do not assume `muse:run` is available in the migrated project.

## Source contracts

- [TranslatorRegistry](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-plugin-core/src/main/kotlin/dev/museframework/plugin/core/translation/TranslatorRegistry.kt)
- [Dependency-based runtime detection](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-plugin-core/src/main/kotlin/dev/museframework/plugin/core/runtime/RuntimeDetector.kt)
- [ADR-019 provider-owned testing](https://github.com/museframework/muse/blob/main/docs/adr/ADR-019-babelfish-provider-owned-testing.md)
- [Verified Spring Boot POM example at v0.2.0](https://github.com/museframework/muse/blob/v0.2.0/examples/mule-test-backend/pom.xml) — `generate` workflow example, not `migrate` output
