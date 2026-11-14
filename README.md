# Muse Agent Skills

Reusable, implementation-aware guidance for working with [Muse](https://github.com/museframework/muse).

## Available skills

| Skill | Purpose |
| --- | --- |
| [mulesoft-to-muse](mulesoft-to-muse/SKILL.md) | Assess and migrate Mule 4 XML applications into Muse/Kotlin projects using the deterministic Muse Maven plugin, with Spring Boot as the default target or Quarkus when explicitly selected. |

Skills follow the [Agent Skills specification](https://agentskills.io/specification). They do not package Muse binaries or replace `muse:check` or `muse:migrate`.

## Usage

Install the `mulesoft-to-muse` skill directory with an Agent Skills-compatible host, then request an assessment or migration of a Mule 4 Maven project. The agent should read `SKILL.md` and the linked references, operate on an isolated copy/worktree, and request approval before replacing an existing project or performing deployment.

Prerequisites for the Maven workflow: JDK 21, Maven 3.9+, a Muse plugin version available to the target environment, and the relevant Babelfish providers. The bundled Python inspection/verification scripts use Python 3.9+ and the standard library only.

## Local validation

```bash
python3 -m unittest discover -s mulesoft-to-muse/tests -v
python3 -m compileall -q mulesoft-to-muse/scripts
```

This repository is separate from the Muse framework; migration semantics and Maven goal parameters are owned by the [framework implementation](https://github.com/museframework/muse/tree/main/muse-maven-plugin).
