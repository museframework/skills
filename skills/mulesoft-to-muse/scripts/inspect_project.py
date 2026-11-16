#!/usr/bin/env python3
"""Read-only audit of a Mule 4 Maven project before Muse migration.

This script makes *suggestions*, not a Muse compatibility determination. Only
muse:check with the actual plugin/providers can determine mapper coverage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MAPPER_ARTIFACTS = {
    "http": "muse-http-babelfish-mappers",
    "apikit": "muse-apikit-babelfish-mappers",
    "db": "muse-db-babelfish-mappers",
    "file": "muse-file-babelfish-mappers",
    "sftp": "muse-sftp-babelfish-mappers",
}

RUNTIME_MARKERS = (
    ("muse-spring-boot", "spring-boot"),
    ("spring-boot-autoconfigure", "spring-boot"),
    ("spring-boot", "spring-boot"),
    ("muse-quarkus", "quarkus"),
    ("quarkus-core", "quarkus"),
    ("quarkus-arc", "quarkus"),
    ("muse-ktor", "ktor"),
    ("ktor-server-core", "ktor"),
    ("ktor-server", "ktor"),
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(parent: ET.Element | None, name: str) -> ET.Element | None:
    return next((x for x in parent if local_name(x.tag) == name), None) if parent is not None else None


def children(parent: ET.Element | None, name: str) -> list[ET.Element]:
    return [x for x in parent if local_name(x.tag) == name] if parent is not None else []


def value(parent: ET.Element | None, name: str, default: str = "") -> str:
    element = child(parent, name)
    return (element.text or "").strip() if element is not None else default


def mule_family(xml_namespace_uri: str) -> str | None:
    # Mule namespaces follow /schema/mule/<family>.  Keep this advisory: not all
    # third-party namespaces follow that pattern or have a Muse implementation.
    match = re.search(r"/schema/mule/([a-zA-Z0-9-]+)(?:/core)?$", xml_namespace_uri)
    if not match:
        return None
    name = match.group(1)
    return "core" if name == "core" else name


def config_class_name(path: Path) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[-_ ]", path.stem)) + "Config.kt"


def dependencies(pom: ET.Element | None) -> list[dict[str, str]]:
    return [
        {
            "group_id": value(dep, "groupId"),
            "artifact_id": value(dep, "artifactId"),
            "version": value(dep, "version"),
            "scope": value(dep, "scope", "compile"),
        }
        for dep in children(pom, "dependency")
    ]


def audit(root: Path, source_directory: Path | None = None) -> dict:
    root = root.resolve()
    source = (source_directory or root / "src/main/mule").resolve()
    result: dict = {
        "project": str(root), "source_directory": str(source), "xml_files": [],
        "families": [], "unrecognized_namespaces": [], "required_plugin_providers": [], "declared_plugin_providers": [],
        "missing_plugin_providers": [], "application_dependencies": [],
        "detected_runtimes": [], "runtime_selection": "spring-boot (migrate fallback)",
        "warnings": [], "errors": [],
    }
    if not root.is_dir():
        result["errors"].append(f"Project root does not exist: {root}")
        return result

    pom_path = root / "pom.xml"
    if pom_path.exists():
        try:
            document = ET.parse(pom_path).getroot()
        except ET.ParseError as exc:
            result["errors"].append(f"Invalid pom.xml: {exc}")
            document = None
        if document is not None:
            result["packaging"] = value(document, "packaging", "jar")
            result["coordinates"] = {
                "group_id": value(document, "groupId") or value(child(document, "parent"), "groupId"),
                "artifact_id": value(document, "artifactId"),
                "version": value(document, "version") or value(child(document, "parent"), "version"),
            }
            result["application_dependencies"] = dependencies(child(document, "dependencies"))
            plugins = children(child(child(document, "build"), "plugins"), "plugin")
            muse_plugins = [p for p in plugins if value(p, "artifactId") == "muse-maven-plugin"]
            if not muse_plugins:
                result["warnings"].append("Muse plugin not declared under build/plugins; configure it in the working copy")
            else:
                if len(muse_plugins) > 1:
                    result["warnings"].append("Multiple Muse Maven plugin declarations under build/plugins")
                provider_deps = [d for p in muse_plugins for d in dependencies(child(p, "dependencies"))]
                result["declared_plugin_providers"] = sorted({d["artifact_id"] for d in provider_deps})
                result["muse_plugin_versions"] = sorted({value(p, "version") for p in muse_plugins})
                result["explicit_runtime"] = [value(child(p, "configuration"), "runtime") for p in muse_plugins]
            detected = {
                runtime
                for dep in result["application_dependencies"]
                if dep["scope"].lower() in ("compile", "runtime")
                for marker, runtime in RUNTIME_MARKERS
                if marker in dep["artifact_id"]
            }
            result["detected_runtimes"] = sorted(detected)
            if len(detected) > 1:
                result["runtime_selection"] = "ambiguous without explicit muse.runtime"
                result["warnings"].append("Multiple runtime markers in direct project dependencies; resolved transitives may add more")
            elif detected:
                result["runtime_selection"] = next(iter(detected))
            if result["packaging"] == "mule-application":
                result["warnings"].append("Source has Mule packaging; prepare a Muse-compatible temporary POM in a working copy")
    else:
        result["errors"].append("Missing pom.xml")

    if not source.is_dir():
        result["errors"].append("Mule XML source directory absent; muse:check would skip it")
        return result

    families: set[str] = set()
    unknown_namespaces: set[str] = set()
    seen_names: dict[str, str] = {}
    for xml_file in sorted(source.rglob("*")):
        if not xml_file.is_file() or xml_file.suffix.lower() != ".xml":
            continue
        rel = xml_file.relative_to(source).as_posix()
        result["xml_files"].append(rel)
        generated_name = config_class_name(xml_file)
        if generated_name in seen_names:
            result["warnings"].append(
                f"Potential generated Kotlin class collision: {seen_names[generated_name]} and {rel} -> {generated_name}"
            )
        seen_names[generated_name] = rel
        try:
            doc = ET.parse(xml_file)
        except ET.ParseError as exc:
            result["errors"].append(f"Invalid XML {rel}: {exc}")
            continue
        for element in doc.iter():
            if element.tag.startswith("{"):
                namespace = element.tag[1:].split("}", 1)[0]
                family = mule_family(namespace)
                if family:
                    families.add(family)
                elif namespace not in ("http://www.w3.org/2001/XMLSchema",):
                    unknown_namespaces.add(namespace)
    if not result["xml_files"]:
        result["errors"].append("No Mule XML files found; muse:check would return without scanning")
    result["families"] = sorted(families)
    result["unrecognized_namespaces"] = sorted(unknown_namespaces)
    if unknown_namespaces:
        result["warnings"].append("Unrecognized XML namespaces require manual mapper/extension assessment")
    result["required_plugin_providers"] = sorted({MAPPER_ARTIFACTS[f] for f in families if f in MAPPER_ARTIFACTS})
    result["missing_plugin_providers"] = sorted(set(result["required_plugin_providers"]) - set(result["declared_plugin_providers"]))
    if result["missing_plugin_providers"]:
        result["warnings"].append("Suggested mapper providers missing from Muse plugin dependencies (not proof of mapping failure)")
    if "apikit" in families:
        result["warnings"].append("Quarkus migration of Mule APIKit XML is blocked by inspected QuarkusRuntimeStrategy")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Mule/Muse project root to audit (read-only)")
    parser.add_argument("--source-directory", type=Path, help="Override XML source directory")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report")
    args = parser.parse_args()
    result = audit(args.project, args.source_directory)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Project: {result['project']}")
        print(f"XML files: {len(result['xml_files'])} | families: {', '.join(result['families'])}")
        print(f"Runtime: {result['runtime_selection']}")
        print(f"Suggested plugin providers: {', '.join(result['required_plugin_providers'])}")
        for key in ("warnings", "errors"):
            for message in result[key]:
                print(f"{key[:-1].upper()}: {message}")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
