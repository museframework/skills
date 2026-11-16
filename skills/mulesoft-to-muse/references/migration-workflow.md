# Safe migration workflow, reruns, and diagnostic taxonomy

## Recommended isolated layout

```text
migration-evaluation/
  original/         # immutable source checkout or pristine copy
  work-spring-boot/ # mutable copy; select one host per copy
  work-quarkus/     # separate mutable copy only if requested
  reports/          # sanitized manifests, commands, logs, test comparisons
```

Record exact commit/branch or a SHA-256 file manifest before any edits. Do not store private credentials, proprietary customer XML or log payloads in a public skills repository or issue.

## Preflight to Maven

- `inspect_project.py` (read-only) inventories Mule XML, likely mapper families, plugin/project dependencies, runtime markers and hazards such as missing source folder.
- Review Mule `pom.xml` packaging. A source `mule-application` packaging often depends on Mule-only Maven extensions; prepare a **temporary** Muse-compatible POM in the working copy, retaining coordinates and original source inputs.
- Configure plugin and providers. Verify published coordinates by resolving the plugin and dependencies on a normal or intentionally isolated Maven repository; do not assume network success.
- Run `mvn muse:check -Dmuse.lenient=false`; capture the output and verify scanned file count. If no XML was scanned, classify as failed preflight regardless of Maven exit code.
- Record provider set; add missing providers to the **plugin dependency list** only when there is a known implementation and published artifact, then recheck.
- If mappings are missing even with correct providers, make a manual remediation plan and stop migration until approved.

## Migration execution

- Snapshot the original file tree and POM; run only in the mutable host-specific copy.
- Call `muse:migrate -Dmuse.runtime=<host>` once per chosen workspace.
- Capture POM backup, modified/new files and compiler warnings; inspect translator's `Skipped generation` diagnostics because migration uses permissive translation.
- Do not run Maven phases that unexpectedly re-invoke `migrate` on every build. If `migrate` was bound to `validate` in a fixture or prepared POM, remove that binding from the final POM to avoid destructive reruns.
- Inspect generated `pom.xml` and correct it according to the current release. Restore necessary runtime dependencies and resources, verify classpath and compile.

## Diagnostics decision table

| Observation | Likely class | Action |
| --- | --- | --- |
| No XML directory or zero XML scanned | Input/setup | Correct source path; do not claim pass |
| Missing mapping, provider absent in plugin | Dependency steering | Add correct mapper provider under `<plugin><dependencies>`, re-run strict check |
| Mapping absent despite correct provider | Translation coverage | Stop, report supported/unsupported and manual work |
| Ambiguous Spring/Quarkus auto-detection | Host selection | Use explicit `muse.runtime` or remove erroneous runtime deps in working copy |
| Quarkus + APIKit fatal | Host-specific limitation | Stop Quarkus automatic path; propose Spring or scoped future feature |
| `pom.xml.mulesoft` exists and POM changed | Normal write side effect | Compare full diff, preserve original snapshot |
| Generated sources fewer than original XML files | Possible skipped translation/collision | Inspect log, file paths, classname collisions; treat as failure pending explanation |
| Generated POM resolves old Muse version | POM generator mismatch | Reconcile to a published coherent dependency set before build |
| Missing runtime connector/driver | Runtime dependency gap | Restore explicit required application dependencies, not plugin mapper artifacts |
| Build succeeds but endpoint/side effect differs | Behavioral gap | Record paired evidence; do not claim parity |

## Example acceptance sequence (not a one-size-fits-all script)

```bash
# In the prepared working copy of a Mule application
python3 /path/to/skill/scripts/inspect_project.py . --json
mvn muse:check -Dmuse.lenient=false
mvn muse:migrate -Dmuse.runtime=spring-boot
python3 /path/to/skill/scripts/verify_migration.py ../original . --runtime spring-boot --json
# Review/fix POM and app integration; then:
mvn clean compile
mvn test
```

After reconciliation, choose the host's actual startup/packaging plugin configuration. The checked-in `muse:migrate` Kotlin output differs from the `muse:generate` source-at-build-time workflow described in the published tutorial.
