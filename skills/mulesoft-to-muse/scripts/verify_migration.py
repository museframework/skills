#!/usr/bin/env python3
"""Read-only structural verification of a muse:migrate output directory.

Checks preserved original inputs and expected runtime artifacts. Maven and
functional tests are still required; this script makes no parity claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from inspect_project import audit, config_class_name, local_name, child, value

PRESERVED_SUFFIXES = {".xml", ".raml", ".yaml", ".yml", ".properties", ".dwl", ".json", ".wsdl", ".xsd"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compare(original: Path, migrated: Path, runtime: str) -> dict:
    original = original.resolve()
    migrated = migrated.resolve()
    result: dict = {
        "original": str(original), "migrated": str(migrated), "runtime": runtime,
        "preserved_source_files": [], "generated_config_files": [],
        "warnings": [], "errors": [], "status": "fail",
    }
    if original == migrated:
        result["errors"].append("Original and migrated paths are identical: independent snapshot required")
        return result
    if not original.is_dir() or not migrated.is_dir():
        result["errors"].append("Original and migrated directories must both exist")
        return result
    inventory = audit(original)
    if inventory["errors"]:
        result["errors"].extend(f"Original inventory: {msg}" for msg in inventory["errors"])
    if "Potential generated Kotlin class collision" in " ".join(inventory["warnings"]):
        result["errors"].append("Original XML filenames may collide on generated class names")
    for src in sorted(original.rglob("*")):
        if not src.is_file() or src.suffix.lower() not in PRESERVED_SUFFIXES:
            continue
        rel = src.relative_to(original)
        if not (rel.parts[:3] == ("src", "main", "mule") or rel.parts[:3] == ("src", "main", "resources")):
            continue
        dest = migrated / rel
        if not dest.exists():
            result["errors"].append(f"Original input missing in migrated copy: {rel}")
        elif sha256(src) != sha256(dest):
            result["errors"].append(f"Original input modified: {rel}")
        else:
            result["preserved_source_files"].append(rel.as_posix())

    backup = migrated / "pom.xml.mulesoft"
    if not backup.is_file():
        result["errors"].append("Missing pom.xml.mulesoft backup")
    pom = migrated / "pom.xml"
    if not pom.is_file():
        result["errors"].append("Missing generated pom.xml")
    else:
        try:
            root = ET.parse(pom).getroot()
            xml_deps = child(root, "dependencies")
            dep_names = {value(dep, "artifactId") for dep in xml_deps if local_name(dep.tag) == "dependency"} if xml_deps is not None else set()
            host_dep = {"spring-boot": "muse-spring-boot", "quarkus": "muse-quarkus"}[runtime]
            if host_dep not in dep_names:
                result["errors"].append(f"Expected target host dependency absent in generated POM: {host_dep}")
            if value(root, "packaging", "jar") == "mule-application":
                result["errors"].append("Migrated project still uses mule-application packaging")
            # The current POM generators use 0.1.0; these are warnings because
            # the selected plugin might differ and repair is deliberately manual.
            versions = [value(dep, "version") for dep in xml_deps if local_name(dep.tag) == "dependency"] if xml_deps is not None else []
            if "0.1.0" in versions or "0.1.0" in pom.read_text(encoding="utf-8"):
                result["warnings"].append("Generated POM contains Muse 0.1.0 references; verify release compatibility before compiling")
        except ET.ParseError as exc:
            result["errors"].append(f"Generated POM is invalid XML: {exc}")

    src_kotlin = migrated / "src/main/kotlin"
    generated = list(src_kotlin.rglob("*.kt")) if src_kotlin.is_dir() else []
    names = {path.name for path in generated}
    for xml_rel in inventory["xml_files"]:
        expected = config_class_name(Path(xml_rel))
        if expected not in names:
            result["errors"].append(f"Missing Kotlin config for {xml_rel}: {expected}")
        else:
            result["generated_config_files"].append(expected)
    if not generated:
        result["errors"].append("No Kotlin source generated under src/main/kotlin")
    if runtime == "spring-boot":
        if not any(name.endswith("Application.kt") for name in names):
            result["errors"].append("Missing Spring Boot *Application.kt entry point")
        if not (migrated / "src/main/resources/application-muse.properties").is_file():
            result["errors"].append("Missing Spring application-muse.properties")
    else:
        if not (migrated / "src/main/resources/application.properties").is_file():
            result["errors"].append("Missing Quarkus application.properties")
        if "apikit" in inventory["families"]:
            result["errors"].append("Quarkus+APIKit Mule XML migration is unsupported by inspected migration strategy")
        if any(name.endswith("Application.kt") for name in names):
            result["warnings"].append("Unexpected *Application.kt for Quarkus; inspect host-specific bootstrap")
    result["generated_config_files"] = sorted(set(result["generated_config_files"]))
    result["status"] = "pass" if not result["errors"] else "fail"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Immutable original Mule project")
    parser.add_argument("migrated", type=Path, help="Post-migrate Muse project")
    parser.add_argument("--runtime", choices=["spring-boot", "quarkus"], default="spring-boot")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = compare(args.original, args.migrated, args.runtime)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Structural result: {result['status']} ({args.runtime})")
        print(f"Preserved: {len(result['preserved_source_files'])} files; flow configs: {len(result['generated_config_files'])}")
        for key in ("warnings", "errors"):
            for message in result[key]:
                print(f"{key[:-1].upper()}: {message}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
