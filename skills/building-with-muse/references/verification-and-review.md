# Verification and review

## Test ownership

- `*Test`: unit and component tests.
- `*IT`: module integration tests.
- `*E2ETest`: packaged or process-level acceptance.
- Maven Invoker: Maven plugin composition and generated-project verification.

Read [Test Muse flows](https://museframework.dev/docs/guides/test-flows/), [verification guide](https://github.com/museframework/muse/blob/main/docs/development/verification.md), and the appropriate repository `AGENTS.md`. The Maven lifecycle and test profiles vary by module and consumer.

## Conditional Maven examples

Only run these commands when the current application POM supports them:

~~~sh
mvn -B -ntp -Dkotlin.daemon.enabled=false test
mvn -B -ntp -Dkotlin.daemon.enabled=false verify
~~~

The second command does not prove integration tests were selected; inspect Surefire/Failsafe reports, profile configuration, pass/fail/skip counts and produced artifacts.

In the framework's standalone Spring Boot example directory, the published test profile uses:

~~~sh
mvn -B -ntp -Dkotlin.daemon.enabled=false -Pe2e verify
~~~

Check actual dependencies and do not assume a passing source-level test exists on the agent's host.

## Human review surface

Record what changed to external HTTP/file/SFTP/database side effects; flow registration and error paths; retries/timeouts; security and secret handling; lifecycle and streaming resources; host adapters; tests and remaining unverified cases. Diff line count is not a safety guarantee.

## Final report

Include `Host / Muse version`, `Files changed`, `Commands executed`, `Tests passed/failed/skipped`, `Observed outputs and side effects`, `Known limitations`, and `Reviewer attention`. Say "not run" for checks not executed. Do not equate compilation with runtime behavior or merge/deployment.
