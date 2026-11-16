"""No Maven/network needed: unit checks for read-only audit invariants."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from inspect_project import audit
from verify_migration import compare

POM = """<project xmlns='http://maven.apache.org/POM/4.0.0'>
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.example</groupId><artifactId>hello-app</artifactId><version>1.0</version>
  <packaging>jar</packaging>
  <build><plugins><plugin><groupId>dev.museframework.maven</groupId>
    <artifactId>muse-maven-plugin</artifactId><version>0.2.1</version>
    <dependencies><dependency><groupId>dev.museframework</groupId>
      <artifactId>muse-http-babelfish-mappers</artifactId><version>0.2.1</version>
    </dependency></dependencies>
  </plugin></plugins></build>
  <dependencies><dependency><groupId>dev.museframework.connectors</groupId>
    <artifactId>muse-spring-boot</artifactId><version>0.2.1</version>
  </dependency></dependencies>
</project>"""
SIMPLE_MULE = """<?xml version='1.0'?>
<mule xmlns='http://www.mulesoft.org/schema/mule/core'
      xmlns:http='http://www.mulesoft.org/schema/mule/http'>
  <flow name='hello'><http:listener path='/hello'/></flow>
</mule>"""


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.original = self.root / "original"
        self.migrated = self.root / "migrated"
        self.original.mkdir()
        self.make_original()

    def make_original(self):
        (self.original / "pom.xml").write_text(POM, encoding="utf-8")
        src = self.original / "src/main/mule"
        src.mkdir(parents=True)
        (src / "simple-flow.xml").write_text(SIMPLE_MULE, encoding="utf-8")
        resources = self.original / "src/main/resources"
        resources.mkdir(parents=True)
        (resources / "config.yaml").write_text("greeting: 'hi'", encoding="utf-8")

    def make_migrated(self, runtime="spring-boot"):
        shutil.copytree(self.original, self.migrated)
        (self.migrated / "pom.xml.mulesoft").write_text(POM, encoding="utf-8")
        host = "muse-spring-boot" if runtime == "spring-boot" else "muse-quarkus"
        (self.migrated / "pom.xml").write_text(POM.replace("muse-spring-boot", host), encoding="utf-8")
        kt = self.migrated / "src/main/kotlin/org/example"
        kt.mkdir(parents=True)
        (kt / "SimpleFlowConfig.kt").write_text("package org.example", encoding="utf-8")
        resources = self.migrated / "src/main/resources"
        if runtime == "spring-boot":
            (kt / "HelloAppApplication.kt").write_text("fun main() {}", encoding="utf-8")
            (resources / "application-muse.properties").write_text("muse.application.name=Hello", encoding="utf-8")
        else:
            (resources / "application.properties").write_text("quarkus.application.name=Hello", encoding="utf-8")

    def test_inspection_detects_http_provider_and_spring_runtime(self):
        report = audit(self.original)
        self.assertFalse(report["errors"])
        self.assertEqual(report["families"], ["core", "http"])
        self.assertEqual(report["missing_plugin_providers"], [])
        self.assertEqual(report["runtime_selection"], "spring-boot")

    def test_inspection_flags_missing_provider(self):
        pom = self.original / "pom.xml"
        pom.write_text(POM.replace("muse-http-babelfish-mappers", "other-provider"), encoding="utf-8")
        self.assertIn("muse-http-babelfish-mappers", audit(self.original)["missing_plugin_providers"])

    def test_missing_source_directory_is_error_not_success(self):
        shutil.rmtree(self.original / "src/main/mule")
        self.assertTrue(audit(self.original)["errors"])

    def test_collision_warning(self):
        src = self.original / "src/main/mule"
        (src / "simple_flow.xml").write_text(SIMPLE_MULE, encoding="utf-8")
        self.assertTrue(any("collision" in msg for msg in audit(self.original)["warnings"]))

    def test_structural_spring_success(self):
        self.make_migrated()
        result = compare(self.original, self.migrated, "spring-boot")
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(len(result["preserved_source_files"]), 2)

    def test_changed_mule_input_is_failure(self):
        self.make_migrated()
        (self.migrated / "src/main/mule/simple-flow.xml").write_text("<changed/>", encoding="utf-8")
        self.assertIn("Original input modified", str(compare(self.original, self.migrated, "spring-boot")["errors"]))

    def test_missing_config_is_failure(self):
        self.make_migrated()
        (self.migrated / "src/main/kotlin/org/example/SimpleFlowConfig.kt").unlink()
        self.assertIn("Missing Kotlin config", str(compare(self.original, self.migrated, "spring-boot")["errors"]))

    def test_ee_namespace_recognized(self):
        src = self.original / "src/main/mule/simple-flow.xml"
        src.write_text(SIMPLE_MULE.replace("</flow>", "<ee:transform xmlns:ee='http://www.mulesoft.org/schema/mule/ee/core'/></flow>"), encoding="utf-8")
        self.assertIn("ee", audit(self.original)["families"])

    def test_unknown_namespace_reported(self):
        src = self.original / "src/main/mule/simple-flow.xml"
        src.write_text(SIMPLE_MULE.replace("</flow>", "<custom:op xmlns:custom='https://example.org/mule/custom'/></flow>"), encoding="utf-8")
        self.assertIn("https://example.org/mule/custom", audit(self.original)["unrecognized_namespaces"])

    def test_quarkus_structural_success(self):
        self.make_migrated(runtime="quarkus")
        result = compare(self.original, self.migrated, "quarkus")
        self.assertEqual(result["status"], "pass", result["errors"])

    def test_quarkus_apikit_is_rejected(self):
        src = self.original / "src/main/mule/simple-flow.xml"
        src.write_text(SIMPLE_MULE.replace("<flow ", "<flow ").replace("</flow>", "<apikit:router xmlns:apikit='http://www.mulesoft.org/schema/mule/apikit'/></flow>"), encoding="utf-8")
        self.make_migrated(runtime="quarkus")
        self.assertIn("Quarkus+APIKit", str(compare(self.original, self.migrated, "quarkus")["errors"]))

    def test_same_original_and_target_is_rejected(self):
        self.assertEqual(compare(self.original, self.original, "spring-boot")["status"], "fail")


if __name__ == "__main__":
    unittest.main()
