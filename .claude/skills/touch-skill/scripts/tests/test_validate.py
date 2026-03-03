#!/usr/bin/env python3
"""Tests for quick_validate.py"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from quick_validate import (
    validate_skill,
    validate_line_counts,
    validate_description,
    validate_aggregate_budget,
    extract_description,
    AGGREGATE_SKILL_THRESHOLD,
    AGGREGATE_DESCRIPTION_BUDGET,
    MAX_DESCRIPTION_CHARS,
)


class TestValidateSkill(unittest.TestCase):
    """Test validate_skill function."""

    def setUp(self):
        """Create temp directory for test skills."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.test_dir)

    def create_skill(self, name, content):
        """Helper to create a test skill."""
        skill_dir = self.test_dir / name
        skill_dir.mkdir(parents=True)
        (skill_dir / 'SKILL.md').write_text(content)
        return skill_dir

    def test_valid_skill(self):
        """Test valid skill passes validation."""
        content = """---
name: test-skill
description: "A test skill. Use when testing validation."
---

# Test Skill

This is a test.
"""
        skill_dir = self.create_skill('test-skill', content)
        valid, errors, warnings = validate_skill(skill_dir)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_missing_skill_md(self):
        """Test missing SKILL.md fails."""
        skill_dir = self.test_dir / 'empty-skill'
        skill_dir.mkdir()
        valid, errors, _ = validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("SKILL.md not found", errors[0])

    def test_missing_frontmatter(self):
        """Test missing frontmatter fails."""
        content = "# No Frontmatter\n\nJust content."
        skill_dir = self.create_skill('no-frontmatter', content)
        valid, errors, _ = validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("frontmatter", errors[0].lower())

    def test_missing_name(self):
        """Test missing name field fails."""
        content = """---
description: "No name field"
---

# Test
"""
        skill_dir = self.create_skill('no-name', content)
        valid, errors, _ = validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertTrue(any("name" in e.lower() for e in errors))

    def test_invalid_name_uppercase(self):
        """Test uppercase name fails."""
        content = """---
name: TestSkill
description: "Has uppercase name"
---
"""
        skill_dir = self.create_skill('test', content)
        valid, errors, _ = validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertTrue(any("hyphen-case" in e.lower() for e in errors))

    def test_invalid_name_consecutive_hyphens(self):
        """Test consecutive hyphens in name fails."""
        content = """---
name: test--skill
description: "Has consecutive hyphens"
---
"""
        skill_dir = self.create_skill('test', content)
        valid, errors, _ = validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertTrue(any("consecutive" in e.lower() for e in errors))


class TestLineCounts(unittest.TestCase):
    """Test line count validation."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_skill_md_over_limit(self):
        """Test SKILL.md over 150 lines produces warning."""
        skill_dir = self.test_dir / 'long-skill'
        skill_dir.mkdir()
        # 4 frontmatter lines + 151 content lines = 155 total (exceeds 150)
        content = "---\nname: test\ndescription: test\n---\n" + "\n".join(["line"] * 151)
        (skill_dir / 'SKILL.md').write_text(content)
        _, warnings = validate_line_counts(skill_dir)
        self.assertTrue(any("SKILL.md" in w for w in warnings))

    def test_skill_md_under_limit_no_warning(self):
        """Test SKILL.md under 150 lines produces no warning."""
        skill_dir = self.test_dir / 'short-skill'
        skill_dir.mkdir()
        content = "---\nname: test\ndescription: test\n---\n" + "\n".join(["line"] * 50)
        (skill_dir / 'SKILL.md').write_text(content)
        _, warnings = validate_line_counts(skill_dir)
        self.assertFalse(any("SKILL.md" in w for w in warnings))

    def test_reference_over_limit(self):
        """Test reference file over 500 lines produces warning."""
        skill_dir = self.test_dir / 'long-ref'
        skill_dir.mkdir()
        refs_dir = skill_dir / 'references'
        refs_dir.mkdir()
        content = "\n".join(["line"] * 501)
        (refs_dir / 'long.md').write_text(content)
        _, warnings = validate_line_counts(skill_dir)
        self.assertTrue(any("references" in w for w in warnings))

    def test_reference_under_limit_no_warning(self):
        """Test reference file under 500 lines produces no warning."""
        skill_dir = self.test_dir / 'short-ref'
        skill_dir.mkdir()
        refs_dir = skill_dir / 'references'
        refs_dir.mkdir()
        content = "\n".join(["line"] * 300)
        (refs_dir / 'long.md').write_text(content)
        _, warnings = validate_line_counts(skill_dir)
        self.assertFalse(any("references" in w for w in warnings))


class TestDescriptionValidation(unittest.TestCase):
    """Test description quality validation."""

    def test_short_description_warning(self):
        """Test short description produces warning."""
        warnings = validate_description("Short")
        self.assertTrue(any("short" in w.lower() for w in warnings))

    def test_missing_trigger_warning(self):
        """Test missing trigger phrase produces warning."""
        warnings = validate_description("A skill that does something useful for users.")
        self.assertTrue(any("when to use" in w.lower() for w in warnings))

    def test_good_description_no_warning(self):
        """Test good description has no trigger warning."""
        warnings = validate_description("Use when you need to process PDFs and extract text.")
        self.assertFalse(any("when to use" in w.lower() for w in warnings))


class TestDescriptionMaxLength(unittest.TestCase):
    """Test per-skill description max length validation."""

    def test_description_over_max_warns(self):
        """Test description exceeding 600 chars produces warning."""
        long_desc = "Use this skill when " + "x" * 600
        warnings = validate_description(long_desc)
        self.assertTrue(any("max" in w.lower() and str(MAX_DESCRIPTION_CHARS) in w for w in warnings))

    def test_description_at_max_no_warning(self):
        """Test description exactly at 600 chars produces no max-length warning."""
        desc = "Use this skill when " + "x" * (MAX_DESCRIPTION_CHARS - 20)
        warnings = validate_description(desc)
        self.assertFalse(any("max" in w.lower() and str(MAX_DESCRIPTION_CHARS) in w for w in warnings))

    def test_description_under_max_no_warning(self):
        """Test description under 600 chars produces no max-length warning."""
        desc = "Use this skill when building something useful for users."
        warnings = validate_description(desc)
        self.assertFalse(any("max" in w.lower() and str(MAX_DESCRIPTION_CHARS) in w for w in warnings))


class TestAggregateBudget(unittest.TestCase):
    """Test aggregate description budget validation."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp()) / "skills"
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir.parent)

    def _make_skill(self, name, description):
        """Helper to create a minimal skill directory with a SKILL.md."""
        skill_dir = self.test_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f'---\nname: {name}\ndescription: "{description}"\n---\n'
        )
        return skill_dir

    def test_skipped_when_few_skills(self):
        """Test aggregate check is skipped with <= 15 skills."""
        for i in range(AGGREGATE_SKILL_THRESHOLD):
            self._make_skill(f"skill-{i}", "x" * 1100)
        target = self.test_dir / "skill-0"
        warnings = validate_aggregate_budget(target)
        self.assertEqual(warnings, [])

    def test_warns_when_budget_exceeded(self):
        """Test aggregate check warns when total exceeds 16,000 chars."""
        count = AGGREGATE_SKILL_THRESHOLD + 1
        per_skill = (AGGREGATE_DESCRIPTION_BUDGET // count) + 100
        for i in range(count):
            self._make_skill(f"skill-{i}", "x" * per_skill)
        target = self.test_dir / "skill-0"
        warnings = validate_aggregate_budget(target)
        self.assertTrue(any("budget" in w.lower() for w in warnings))

    def test_no_warning_when_under_budget(self):
        """Test aggregate check passes when total is under 16,000 chars."""
        count = AGGREGATE_SKILL_THRESHOLD + 1
        for i in range(count):
            self._make_skill(f"skill-{i}", "Use this skill when testing.")
        target = self.test_dir / "skill-0"
        warnings = validate_aggregate_budget(target)
        self.assertEqual(warnings, [])


class TestExtractDescription(unittest.TestCase):
    """Test extract_description helper."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extracts_description(self):
        """Test extraction from valid SKILL.md."""
        skill_md = self.test_dir / "SKILL.md"
        skill_md.write_text('---\nname: test\ndescription: "Hello world"\n---\n')
        self.assertEqual(extract_description(skill_md), "Hello world")

    def test_returns_none_for_missing_file(self):
        """Test returns None for nonexistent file."""
        self.assertIsNone(extract_description(self.test_dir / "missing.md"))

    def test_returns_none_for_no_frontmatter(self):
        """Test returns None for file without frontmatter."""
        skill_md = self.test_dir / "SKILL.md"
        skill_md.write_text("# No frontmatter here\n")
        self.assertIsNone(extract_description(skill_md))


if __name__ == '__main__':
    unittest.main()
