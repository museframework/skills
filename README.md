# Muse Agent Skills

Agent Skills for the [Muse integration framework](https://github.com/museframework/muse).

## Available skills

- **[mulesoft-to-muse](skills/mulesoft-to-muse/SKILL.md)** — Guide migration from Mule 4 XML to Muse/Kotlin using the existing `muse:check` and `muse:migrate` Maven goals. Spring Boot is the default target; Quarkus is optional.

- **[building-with-muse](skills/building-with-muse/SKILL.md)** — Guide native Kotlin Muse flow development, modifications, debugging, verification, and review through existing typed APIs and supported connector hosts.

## Installation

Install with the [Skills CLI](https://skills.sh/):

```bash
npx skills add museframework/skills --skill mulesoft-to-muse
```

For native Kotlin Muse development use:

~~~bash
npx skills add museframework/skills --skill building-with-muse
~~~

Alternatively, copy `skills/mulesoft-to-muse/` or `skills/building-with-muse/` into the skills directory of an [Agent Skills-compatible agent](https://agentskills.io/specification). Keep `SKILL.md`, `references/`, and `scripts/` together.

Maven migration requires JDK 21, Maven 3.9+, and resolvable Muse artifacts. The optional read-only audit scripts require Python 3.9+.

## Validation

```bash
python3 -m unittest discover -s skills/mulesoft-to-muse/tests -v
python3 -m unittest discover -s skills/building-with-muse/tests -v
python3 -m compileall -q skills/mulesoft-to-muse/scripts
```

The migration skill guides the Maven plugin; it does not replace XML-to-Kotlin translation or guarantee full MuleSoft compatibility.
