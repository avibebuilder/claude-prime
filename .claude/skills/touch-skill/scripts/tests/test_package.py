#!/usr/bin/env python3
"""Tests for package_skill.py"""

import unittest
import tempfile
import shutil
import zipfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from package_skill import package_skill


class TestPackageSkill(unittest.TestCase):
    """Test package_skill function."""

    def setUp(self):
        """Create temp directory and valid test skill."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.output_dir = Path(tempfile.mkdtemp())

        # Create a valid skill
        self.skill_dir = self.test_dir / "test-skill"
        self.skill_dir.mkdir()
        skill_content = """---
name: test-skill
description: "A test skill. Use when testing packaging."
---

# Test Skill

This is a test skill for packaging.
"""
        (self.skill_dir / "SKILL.md").write_text(skill_content)

        # Add a script
        scripts_dir = self.skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "example.py").write_text("print('hello')")

    def tearDown(self):
        """Clean up temp directories."""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)

    def test_creates_zip_file(self):
        """Test zip file is created."""
        result = package_skill(self.skill_dir, self.output_dir)
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        self.assertEqual(result.suffix, ".zip")

    def test_zip_contains_skill_md(self):
        """Test zip contains SKILL.md."""
        result = package_skill(self.skill_dir, self.output_dir)
        with zipfile.ZipFile(result, 'r') as zf:
            names = zf.namelist()
            self.assertTrue(any("SKILL.md" in n for n in names))

    def test_zip_contains_scripts(self):
        """Test zip contains scripts directory."""
        result = package_skill(self.skill_dir, self.output_dir)
        with zipfile.ZipFile(result, 'r') as zf:
            names = zf.namelist()
            self.assertTrue(any("scripts" in n for n in names))

    def test_fails_on_missing_skill(self):
        """Test fails if skill directory doesn't exist."""
        result = package_skill(self.test_dir / "nonexistent", self.output_dir)
        self.assertIsNone(result)

    def test_fails_on_invalid_skill(self):
        """Test fails if skill validation fails."""
        # Create invalid skill (no frontmatter)
        invalid_dir = self.test_dir / "invalid-skill"
        invalid_dir.mkdir()
        (invalid_dir / "SKILL.md").write_text("No frontmatter here")
        result = package_skill(invalid_dir, self.output_dir)
        self.assertIsNone(result)

    def test_uses_current_dir_as_default_output(self):
        """Test uses current directory if no output specified."""
        import os
        original_cwd = os.getcwd()
        os.chdir(self.output_dir)
        try:
            result = package_skill(self.skill_dir)
            self.assertIsNotNone(result)
            self.assertEqual(result.parent, self.output_dir)
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
