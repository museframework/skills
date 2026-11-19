import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
REPO = SKILL.parents[2]
README = REPO / "README.md"


class SkillContractTest(unittest.TestCase):
    def test_metadata(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---\n", 2)[1]
        self.assertIn("name: building-with-muse", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertIn("compatibility:", frontmatter)
        self.assertIn("mulesoft-to-muse", text)
        self.assertIn("Kotlin LSP", text)

    def test_references_resolve(self):
        body = SKILL.read_text(encoding="utf-8")
        paths = re.findall(r"\]\((references/[^)]+\.md)\)", body)
        self.assertGreaterEqual(len(paths), 4)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((SKILL.parent / path).is_file())

    def test_skill_catalog(self):
        self.assertTrue((REPO / "skills/mulesoft-to-muse/SKILL.md").exists())
        self.assertIn("skills/building-with-muse/SKILL.md", README.read_text(encoding="utf-8"))

    def test_no_future_docs_routes_advertised(self):
        for path in (SKILL, *(SKILL.parent / "references").glob("*.md")):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("museframework.dev/llms.txt", content)
            self.assertNotIn("museframework.dev/docs/ai-skills/building-with-muse", content)

    def test_generated_sources_and_verification_guardrails(self):
        body = SKILL.read_text(encoding="utf-8")
        self.assertIn("Never edit or commit generated files", body)
        self.assertIn("registered", body)
        self.assertIn("passed/failed/skipped", body)


if __name__ == "__main__":
    unittest.main()
