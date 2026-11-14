---
name: mulesoft-to-muse
description: Assess or migrate an existing MuleSoft Mule 4 Maven application to Muse using deterministic muse:check and muse:migrate goals. Guide mapper-provider and runtime dependency steering, default to Spring Boot, optionally target Quarkus, reconcile generated Maven files, and verify functional behavior. Use when users request Mule XML compatibility assessment, Mule-to-Kotlin migration, or a Spring Boot/Quarkus Muse target.
compatibility: Requires access to project files. Maven execution requires JDK 21, Maven 3.9+, and resolvable Muse artifacts; optional audit scripts require Python 3.9+.
---

# Migrate MuleSoft 4 to Muse

Treat **the Maven plugin and Babelfish as the deterministic translator**. Your role is to select and configure dependencies, run the tools, assess gaps, restore application-specific integration, and verify behavior. Muse translates supported Mule XML **to Kotlin source**; it does not interpret the Mule XML at runtime. No full MuleSoft-compatibility promise is implied.

## Non-negotiable safety rules

- Preserve the original Mule application. Work in a separate copy/worktree; record the source revision and a manifest of original Mule XML, RAML, properties and external DataWeave files. Do not change these inputs without explicit approval.
- Never run `muse:migrate` on the only copy: it can rename `pom.xml` to `pom.xml.mulesoft`, replace `pom.xml`, and write/overwrite `src/main/kotlin` and runtime resources. Its backup is not a transactional rollback, and repeated runs can overwrite the migrated POM without refreshing the backup.
- Never silently switch runtimes, change behavior, invent missing connector implementations, remove integration/security requirements, copy secrets into reports, or deploy. Ask before any irreversible operation or production cutover.
- Check the actual Muse Maven plugin/version availability and source contracts. Do not automatically use the source reactor's current Maven version when only an older version is published. Do not equate successful component mapping or compilation with functional parity.
- Distinguish unsupported XML, missing mapper-provider dependency, target-host limitation, generated-POM defect, environment problem, and behavioral failure. An unsupported component is not a license to hallucinate a Kotlin equivalent.

## 1. Inventory the original project

1. Identify the Maven project root(s), modules, `pom.xml`, Java/Mule runtime versions, packaging, project coordinates, any Mule-specific Maven extension, XML under `src/main/mule`, RAML/OAS, properties, `src/main/resources`, `.dwl` references, test suites, and external dependencies/side effects.
2. Determine what baseline tests, requests, events, fixtures, credentials and external services are available. Never record raw secrets. Capture original behavior where practical.
3. Run the **read-only** audit script on the migration workspace:

   ```bash
   python3 /path/to/skill/scripts/inspect_project.py /path/to/workspace --json
   ```

   Its namespace/provider suggestions are advisory. Read [dependency-steering](references/dependency-steering.md) for provider scoping and [maven-plugin](references/maven-plugin.md) for actual goal properties.
4. Verify this is a supported **Mule 4 XML** path, not an assumed Mule 3 or custom-extension conversion.

## 2. Prepare an isolated Maven workspace

- Keep pristine original inputs in a separate directory and make a second working copy. Prefer a clean Git branch/worktree if the project is versioned, or a clearly labeled directory copy. Verify the baseline manifest before running a write goal.
- Choose an **existing released** Muse version and use compatible versions consistently for the Maven plugin, mapper providers, BOM and runtime dependencies; check resolver output rather than inferring published availability from source POMs.
- Make the temporary Maven POM executable by the Muse plugin. Preserve `groupId`, `artifactId`, and version as necessary; remove or isolate incompatible Mule packaging/build extensions only in the working copy. Configure `dev.museframework.maven:muse-maven-plugin` in `<build><plugins>`; add optional mapper-provider artifacts under **that plugin's** `<dependencies>`. Core mapper provider is already bundled.
- Select **Spring Boot by default**; select Quarkus only if requested. Prefer explicit `-Dmuse.runtime=spring-boot` / `-Dmuse.runtime=quarkus` during migration to avoid accidental host detection from transitive dependencies. Auto-detection consults the application's compile/runtime dependencies, **not** plugin mapper dependencies. See [runtime-selection](references/runtime-selection.md).

## 3. Run strict deterministic assessment (mandatory gate)

From the prepared working project:

```bash
mvn muse:check -Dmuse.lenient=false
```

If the Mule XML lives elsewhere, pass `-Dmuse.sourceDirectory=/absolute/path/to/src/main/mule`. **Do not** treat `BUILD SUCCESS` as a valid check when the goal says `Source directory does not exist` or `No XML files found`. Inspect the number of XML files scanned and component counts. Read missing-provider diagnostics and inspect plugin dependencies before declaring an XML element unsupported.

If strict check fails: stop automatic migration. Classify each missing mapping; add a legitimate, released provider in plugin dependencies where available, rerun the check, or report a genuinely unsupported feature and obtain agreement for an explicit manual implementation. Never hide missing mappings by using `muse.lenient=true` as a success criterion.

## 4. Run deterministic migration

Only after the strict gate passes and the migration copy is safe:

```bash
# Default, explicit for reproducibility
mvn muse:migrate -Dmuse.runtime=spring-boot

# Alternative ONLY when user chose Quarkus and preflight supports it
mvn muse:migrate -Dmuse.runtime=quarkus
```

Optional settings: `-Dmuse.packageName=...`, `-Dmuse.sourceDirectory=...`, `-Dmuse.nativeBuild=true`. The migration goal itself translates with `lenient=true`, so **do not rely solely on its exit status**. Check each original XML file produced a corresponding flow configuration and inspect warnings such as `Skipped generation`.

For Quarkus with APIKit XML, the currently inspected `QuarkusRuntimeStrategy` explicitly rejects migration even though a Quarkus APIKit adapter exists. Do not bypass this validation, remove APIKit, or claim support from adapter presence; present the blocker and alternatives. Confirm current behavior against the chosen plugin version. See [runtime-selection](references/runtime-selection.md).

## 5. Reconcile the generated project before compiling

`muse:migrate` generates `src/main/kotlin` flow sources and an application POM. The POM generator is **not** a complete migration of arbitrary application dependencies, security and deployment settings. Inspect `pom.xml.mulesoft` and compare all functional and build requirements with the new POM:

- Ensure all Muse versions are mutually compatible and available. The inspected framework source at `v0.2.1` hardcodes **0.1.0** in Spring/Quarkus POM generators; treat that as a known source-level caveat, not a trustworthy target version. Verify against the actual goal artifact you ran.
- Restore required connector runtime libraries, drivers, API contracts, nonsecret properties, resource loading, external integrations, logging, deployment and tests. **Mapper dependencies belong in the plugin classpath for future translation; runtime connectors belong in the project classpath.** The generated POM might not retain the Muse plugin at all because `muse:migrate` produces checked-in Kotlin sources (unlike `muse:generate`).
- Inspect the generated Kotlin, application entry point/configuration, resources, README and original POM backup. Generated files from `muse:migrate` are **project source under `src/main/kotlin`**, different from disposable `muse:generate` output under `target/generated-sources/muse`; do not edit `target/` or conflate both workflows.
- Preserve original resource bytes unless explicitly approved to change; avoid unnecessary re-running of `muse:migrate` after manual edits.

Run read-only output verification after migration:

```bash
python3 /path/to/skill/scripts/verify_migration.py \
  /path/to/pristine-original /path/to/migrated-copy --runtime spring-boot --json
```

The script checks structural invariants and source preservation; it does not replace Maven compilation or behavior testing. See [verification](references/verification.md).

## 6. Build, run, and compare

After POM reconciliation, compile/package and run through the chosen host's build plugin. The generated `muse:migrate` POM may not support the `muse:run` goal because it need not retain the Muse Maven plugin. Consult [runtime-selection](references/runtime-selection.md) and inspect effective Maven goals before choosing invocation.

Compare real outputs, statuses, error cases, binary payloads, headers/media types, side effects, scheduling, transaction boundaries and external interactions against the original application. Track each gap with an explicit **pass/fail/unverified** result, evidence and follow-up. Read [verification](references/verification.md).

## Deliverable

Produce: original source revision and manifest; selected Muse version and runtime; mapper/project dependency matrix; exact commands and exit results; strict check coverage and warnings; generated-file inventory; POM reconciliation; test matrix and evidence; remaining blockers; and an explicit statement of **assessed**, **generated**, **compiled**, **started**, or **behaviorally verified** (do not overclaim).

## References on demand

- [Maven goal semantics and parameters](references/maven-plugin.md)
- [Mapper and runtime dependency steering](references/dependency-steering.md)
- [Spring Boot vs Quarkus](references/runtime-selection.md)
- [Workflow troubleshooting and safe reruns](references/migration-workflow.md)
- [Verification contract and reporting](references/verification.md)
