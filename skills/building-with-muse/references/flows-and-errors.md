# Flows, references, errors and expressions

## Example fragment

This example is a DSL **fragment**, not a complete running application. It reflects the [first flow guide](https://museframework.dev/docs/getting-started/first-flow/).

~~~kotlin
import dev.museframework.dsl.dsl.flow
import dev.museframework.dsl.dsl.setPayload

val flow = flow("set-payload-literal-flow") {
    setPayload {
        docName = "Set Payload"
        value = "new-payload-value"
    }
}
~~~

An externally triggered application also requires a source, registered flow and supported host.

## Domain constraints beyond Kotlin types

- Use Kotlin LSP to inspect the installed `flowRef` overloads and their public argument types.
- A `MuseFlow` reference and a name-based reference resolve differently.
- A type-correct `flowRef("payments")` does not prove that `payments` exists in the registered application.
- Existing Muse validation checks static name references during bootstrap, not necessarily at editor typing time.
- Flow and sub-flow error-handler scopes differ; verify the corresponding implementation and ADRs for the selected version.

Read [flows and events](https://museframework.dev/docs/concepts/flows-and-events/), [lifecycle](https://museframework.dev/docs/concepts/application-lifecycle/) and [error handling](https://museframework.dev/docs/concepts/error-handling/).

## Payloads and execution

- Preserve payload metadata, attributes, variables, correlation IDs and error contracts as required by the integration.
- Processors use `ProcessorResult` and declarative error handling; exceptions are not the normal result mechanism.
- Muse includes typed `DwExpression` and DataWeave integration. Do not substitute string interpolation for an arbitrary transformation.
- Streaming providers have lifecycle/resource ownership. Do not silently materialize or close them in a new scope.

Read [DataWeave](https://museframework.dev/docs/concepts/expressions-and-dataweave/) and [streaming](https://museframework.dev/docs/concepts/streaming/). Check success, failure and resource cleanup tests after modifications.
