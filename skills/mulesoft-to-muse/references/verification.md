# Verification matrix and reporting contract

A migration is **not complete** merely because `muse:check` or `muse:migrate` reported success.

## Required evidence

| Stage | Acceptance evidence | Failure condition |
| --- | --- | --- |
| Input snapshot | Source commit/revision or hashes of XML, RAML, external `.dwl`, properties and important resources | Source inputs changed without consent |
| Maven setup | Correct published plugin + provider artifacts resolved from intended repository | Plugin realm missing mapper provider |
| Static check | Strict check scanned expected XML files and has no blocking unmapped components | Zero XML silently skipped, or missing mappings |
| Translation | Every input XML accounted for in generated Kotlin inventory; no skipped translations | `Skipped generation`, collision/overwriting, missing classes |
| POM reconciliation | Runtime-specific compatible dependency graph; app-level dependencies and nonsecret settings reviewed | Old/mixed versions, missing connector/driver, untracked exclusions |
| Compilation/testing | Maven compile/test results and reports recorded for generated project | Compilation fails or tests not executed but claimed as passing |
| Runtime | Correct startup, flow/source registration, and appropriate host operation | No listener/flow or wrong host |
| Behavioral comparison | Paired positive/negative and edge-case requests/events, media and errors, binary payloads, side effects | Unexplained behavior drift |
| Cutover readiness | Explicit ops, security, observability, secrets, transactions, licensing, performance and rollback review | Unmeasured assumptions stated as certified |

Scripts `inspect_project.py` and `verify_migration.py` perform **read-only structural audits**. They cannot prove Mule semantic parity or Maven resolution. Review their warnings and revalidate with real Maven/runtime evidence.

## Suggested sanitized report template

```markdown
# Mule-to-Muse migration evidence

- Original project/revision:
- Target working copy:
- Muse plugin/artifact version (published/provenance):
- Runtime: spring-boot | quarkus
- Mapper providers and versions:
- Commands and exit codes:
- Strict check scanned N XML files / supported count / unresolved count:
- Kotlin generated inventory / skipped files:
- POM backup, dependency diff and effective POM review:
- Maven compile / tests / packaging (passed, failed, skipped):
- Runtime and paired behavioral cases (passed, failed, unverified):
- Remaining risks and owners:
- Overall state: assessed | generated | compiled | started | behaviorally verified
```

## Historic bounded example (not universal certification)

The [website tutorial](https://github.com/museframework/muse-website/blob/main/src/pages/guides/mulesoft-to-muse.md) uses the published Muse **0.2.0** Spring Boot example and preserves five original XML/RAML/properties files byte-for-byte. The AgentWorklog validation from 2026-11-13 independently observed strict mapping of 21 components and seven HTTP checks across Maven, executable JAR and arm64 Docker. Separate paired Mule EE / Muse research reported nine application-level HTTP scenarios matching with carefully documented normalization/limitations. These measurements do not validate arbitrary XML, Quarkus migration, future versions, production licensing, streaming or performance.
