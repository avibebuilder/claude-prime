#!/usr/bin/env python3
"""Tests for init_skill.py"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from init_skill import init_skill, title_case_skill_name, load_template


class TestTitleCase(unittest.TestCase):
    """Test title_case_skill_name function."""

    def test_single_word(self):
        """Test single word conversion."""
        self.assertEqual(title_case_skill_name("skill"), "Skill")

    def test_hyphenated(self):
        """Test hyphenated name conversion."""
        self.assertEqual(title_case_skill_name("my-new-skill"), "My New Skill")

    def test_with_numbers(self):
        """Test name with numbers."""
        self.assertEqual(title_case_skill_name("api-v2-helper"), "Api V2 Helper")


class TestInitSkill(unittest.TestCase):
    """Test init_skill function."""

    def setUp(self):
        """Create temp directory for test skills."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.test_dir)

    def test_creates_skill_directory(self):
        """Test skill directory is created."""
        result = init_skill("test-skill", self.test_dir)
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())

    def test_creates_skill_md(self):
        """Test SKILL.md is created."""
        result = init_skill("test-skill", self.test_dir)
        skill_md = result / "SKILL.md"
        self.assertTrue(skill_md.exists())

    def test_skill_md_has_frontmatter(self):
        """Test SKILL.md has valid frontmatter."""
        result = init_skill("test-skill", self.test_dir)
        content = (result / "SKILL.md").read_text()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: test-skill", content)
        self.assertIn("description:", content)

    def test_creates_scripts_directory(self):
        """Test scripts directory is created."""
        result = init_skill("test-skill", self.test_dir)
        scripts_dir = result / "scripts"
        self.assertTrue(scripts_dir.exists())

    def test_creates_example_script(self):
        """Test example script is created."""
        result = init_skill("test-skill", self.test_dir)
        example = result / "scripts" / "example.py"
        self.assertTrue(example.exists())

    def test_creates_references_directory(self):
        """Test references directory is created."""
        result = init_skill("test-skill", self.test_dir)
        refs_dir = result / "references"
        self.assertTrue(refs_dir.exists())

    def test_fails_on_existing_directory(self):
        """Test fails if skill directory already exists."""
        skill_dir = self.test_dir / "existing-skill"
        skill_dir.mkdir()
        result = init_skill("existing-skill", self.test_dir)
        self.assertIsNone(result)


class TestLoadTemplate(unittest.TestCase):
    """Test load_template function."""

    def test_fallback_when_missing(self):
        """Test fallback is used when template file missing."""
        fallback = "fallback content"
        result = load_template("nonexistent.md", fallback)
        self.assertEqual(result, fallback)


if __name__ == '__main__':
    unittest.main()
