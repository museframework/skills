# Maven plugin semantics (source-informed)

Reference implementation inspected: `museframework/muse` on `main`/`develop`, 2026-11-14. **Recheck the exact version in use**, since this document is not generated from a published plugin descriptor.

| Goal | Implementation | Reads | Mutates | Caveat |
| --- | --- | --- | --- | --- |
| `muse:check` | `MuseCheckMojo.kt` | XML under `muse.sourceDirectory`, plugin mapper realm | No project source mutation | Missing directory or XML logs and returns successfully; strict checking controlled by `muse.lenient` (default `false`) |
| `muse:migrate` | `MuseMigrateMojo.kt` | XML, project artifacts, project coordinates, plugin mapper realm | Replaces POM, creates Kotlin sources + runtime resources | Calls translator with `lenient=true`; skipped files can be warnings, so strict preflight and postflight inventory are compulsory |
| `muse:generate` | `MuseGenerateMojo.kt` | XML, plugin realm | `target/generated-sources/muse` | Different XML-first iterative workflow; generated output is disposable |
| `muse:run` | `MuseRunMojo.kt` | Host runtime + generated application | Starts application | Requires plugin wiring; delegates to host-specific plugin |

## Documented and source parameters

| Property | Goal | Meaning |
| --- | --- | --- |
| `muse.sourceDirectory` | check, migrate | XML source folder; default `${project.basedir}/src/main/mule` |
| `muse.lenient` | check | Default `false` strict error behavior |
| `muse.check.skip` | check | Explicit skip; never use for an acceptance gate |
| `muse.runtime` | migrate | `spring-boot` or `quarkus`; explicit configuration wins over dependency detection |
| `muse.packageName` | migrate | Generated Kotlin package; default derived from group ID |
| `muse.nativeBuild` | migrate | Default `false`; affects generated runtime declarations / POM native configuration |
| `muse.skip` | migrate | Explicit skip; never use for acceptance |

**Do not imply `-Dmuse.lenient=false` makes `muse:migrate` strict.** It only configures `muse:check`; the inspected migration implementation passes `lenient=true` directly to the translator.

## Important write semantics

The migrate goal:

1. Parses all `.xml` files recursively under source directory.
2. Resolves runtime and selects a `RuntimeStrategy`.
3. Checks mapping coverage and logs diagnostics.
4. Translates each XML file; in lenient mode, a file with unsupported elements can produce warnings and no generated flow config.
5. Calls `validateMigration` (e.g. blocks Quarkus+APIKit).
6. Renames a preexisting POM to `pom.xml.mulesoft` **only if that backup is absent**; then writes the runtime's POM to `pom.xml`.
7. Writes Kotlin translation results and bootstrap/resources under `src/main`, potentially overwriting existing paths; creates `.gitignore` only when absent.

The flow files have names derived from the source XML filename (camel-cased + `Config.kt`), but independent XML files may collide on derived name. Audit collisions and inventories instead of assuming one-to-one files are safe to overwrite.

`muse:migrate` currently has no separate destination output path or dry-run flag. A copy/worktree boundary is therefore necessary. A successful Maven exit does not ensure the original POM has been fully preserved; only the single POM backup is automatic.

## Goal names in Maven

The shorthand `mvn muse:check` requires normal Maven plugin resolution, typically a POM declaration of `dev.museframework.maven:muse-maven-plugin`. When shorthand resolution fails, invoke the exact published coordinates:

```bash
mvn dev.museframework.maven:muse-maven-plugin:<verified-version>:check -Dmuse.lenient=false
mvn dev.museframework.maven:muse-maven-plugin:<verified-version>:migrate -Dmuse.runtime=spring-boot
```

Substitute a **verified** version, not a source-branch assumption.

## Authoritative source links

- [Checker Mojo](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-maven-plugin/src/main/kotlin/dev/museframework/plugin/maven/mojo/MuseCheckMojo.kt)
- [Migration Mojo](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-maven-plugin/src/main/kotlin/dev/museframework/plugin/maven/mojo/MuseMigrateMojo.kt)
- [Runtime resolver](https://github.com/museframework/muse/blob/main/muse-maven-plugin/muse-plugin-core/src/main/kotlin/dev/museframework/plugin/core/runtime/RuntimeResolver.kt)
- [Maven plugin guide](https://github.com/museframework/muse/blob/main/docs/maven-plugin.md) — some narrative and sample versions predate the newer validated tutorial; prefer implementation/release evidence where inconsistent
