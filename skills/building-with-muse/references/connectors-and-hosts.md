# Connector and host reference

Use the current [public connector catalog](https://museframework.dev/docs/connectors/) to locate reviewed contracts; confirm exact API symbols and runtime dependencies against the selected Muse artifact version.

| Family | Reference | Important behaviors to verify |
| --- | --- | --- |
| HTTP | [HTTP](https://museframework.dev/docs/connectors/http/) | Listener host adapter, outbound HTTP, response and error mapping |
| File | [File](https://museframework.dev/docs/connectors/file/) | Relative/absolute paths, filesystem side effects, polling |
| SFTP | [SFTP](https://museframework.dev/docs/connectors/sftp/) | Host-key verification, session/stream ownership |
| Database | [Database](https://museframework.dev/docs/connectors/database/) | Drivers, JDBC operations, resource and transaction boundaries |
| APIKit | [APIKit](https://museframework.dev/docs/connectors/apikit/) | RAML routing, host-specific integration, bounded migration support |

## Application hosts

- Use the [Spring Boot guide](https://museframework.dev/docs/runtimes/spring-boot/) and [runnable example](https://museframework.dev/docs/getting-started/running-an-application/) as an inspected starting point.
- For Quarkus, use the [Quarkus guide](https://museframework.dev/docs/runtimes/quarkus/) and verify availability and configuration of published artifacts for the target version.
- A Quarkus APIKit adapter in source does **not** imply that Mule XML APIKit migration to Quarkus is supported.

## Integration change checks

1. Inspect public connector builder fields and defaults in the actual dependency.
2. Verify connector runtime, driver and host adapter dependencies.
3. Preserve external side-effect semantics, streaming lifetime and resource cleanup.
4. Use isolated test systems or mocks, never live customer credentials by default.
5. Test negative cases as well as happy-path HTTP, SFTP, file or SQL behavior.
6. Do not claim universal MuleSoft component compatibility from the presence of a Muse connector family.
