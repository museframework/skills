# Muse Agent Skills

Agent Skills for the [Muse integration framework](https://github.com/museframework/muse).

## Available skills

- **[mulesoft-to-muse](mulesoft-to-muse/SKILL.md)** — Guide migration from Mule 4 XML to Muse/Kotlin using the existing `muse:check` and `muse:migrate` Maven goals. Spring Boot is the default target; Quarkus is optional.

## Installation

Copy `mulesoft-to-muse/` into the skills directory of an [Agent Skills-compatible agent](https://agentskills.io/specification). Keep `SKILL.md`, `references/`, and `scripts/` together.

Maven migration requires JDK 21, Maven 3.9+, and resolvable Muse artifacts. The optional read-only audit scripts require Python 3.9+.

## Validation

```bash
python3 -m unittest discover -s mulesoft-to-muse/tests -v
python3 -m compileall -q mulesoft-to-muse/scripts
```

The skill guides the Maven plugin; it does not replace XML-to-Kotlin translation or guarantee full MuleSoft compatibility.
