"""Portable Agent Skills metadata and local reference checks (stdlib only)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_name_and_description(self):
        contents = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(contents.startswith("---\n"))
        metadata = contents.split("---\n", 2)[1]
        fields = dict(line.split(":", 1) for line in metadata.splitlines() if ":" in line)
        name = fields["name"].strip()
        description = fields["description"].strip()
        self.assertEqual(name, ROOT.name)
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertTrue(0 < len(description) <= 1024)
        self.assertIn("Mule", description)

    def test_references_exist(self):
        contents = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        refs = re.findall(r"\]\((references/[^)]+\.md)\)", contents)
        self.assertGreaterEqual(len(set(refs)), 5)
        for ref in refs:
            with self.subTest(reference=ref):
                self.assertTrue((ROOT / ref).is_file())

    def test_read_only_script_paths_exist(self):
        for script in ("inspect_project.py", "verify_migration.py"):
            with self.subTest(script=script):
                self.assertTrue((ROOT / "scripts" / script).is_file())


if __name__ == "__main__":
    unittest.main()
