#!/usr/bin/env python3
"""
Tests for frontend-design remote search.
Validates that remote CSV structure hasn't changed.
"""

import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from search import fetch_csv, DOMAINS, STACKS, GITHUB_BASE, CACHE_DIR, get_cache_path, is_cache_valid
from core import BM25, search_csv_data


class TestRemoteAccess(unittest.TestCase):
    """Test that remote CSVs are accessible."""

    def test_github_base_url_valid(self):
        """Verify base URL format."""
        self.assertIn("raw.githubusercontent.com", GITHUB_BASE)
        self.assertIn("ui-ux-pro-max", GITHUB_BASE)
        self.assertIn("src/ui-ux-pro-max", GITHUB_BASE)

    def test_fetch_styles_csv(self):
        """Test styles.csv is accessible and has data."""
        rows = fetch_csv("data/styles.csv")
        self.assertGreater(len(rows), 0, "styles.csv should have rows")

    def test_fetch_colors_csv(self):
        """Test colors.csv is accessible."""
        rows = fetch_csv("data/colors.csv")
        self.assertGreater(len(rows), 0, "colors.csv should have rows")

    def test_fetch_typography_csv(self):
        """Test typography.csv is accessible."""
        rows = fetch_csv("data/typography.csv")
        self.assertGreater(len(rows), 0, "typography.csv should have rows")

    def test_fetch_icons_csv(self):
        """Test icons.csv is accessible."""
        rows = fetch_csv("data/icons.csv")
        self.assertGreater(len(rows), 0, "icons.csv should have rows")

    def test_fetch_react_performance_csv(self):
        """Test react-performance.csv is accessible."""
        rows = fetch_csv("data/react-performance.csv")
        self.assertGreater(len(rows), 0, "react-performance.csv should have rows")

    def test_fetch_ui_reasoning_csv(self):
        """Test ui-reasoning.csv is accessible."""
        rows = fetch_csv("data/ui-reasoning.csv")
        self.assertGreater(len(rows), 0, "ui-reasoning.csv should have rows")

    def test_fetch_web_interface_csv(self):
        """Test web-interface.csv is accessible."""
        rows = fetch_csv("data/web-interface.csv")
        self.assertGreater(len(rows), 0, "web-interface.csv should have rows")


class TestCSVSchema(unittest.TestCase):
    """Test that expected columns exist in remote CSVs."""

    def test_styles_has_expected_columns(self):
        """Verify styles.csv has key columns we depend on."""
        rows = fetch_csv("data/styles.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["Style Category", "Keywords", "Type"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")

    def test_colors_has_expected_columns(self):
        """Verify colors.csv has key columns."""
        rows = fetch_csv("data/colors.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["Product Type", "Primary (Hex)", "Border (Hex)"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")

    def test_typography_has_expected_columns(self):
        """Verify typography.csv has key columns."""
        rows = fetch_csv("data/typography.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["Heading Font", "Body Font", "Category"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")

    def test_icons_has_expected_columns(self):
        """Verify icons.csv has key columns."""
        rows = fetch_csv("data/icons.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["Category", "Icon Name", "Library", "Import Code"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")

    def test_ux_has_expected_columns(self):
        """Verify ux-guidelines.csv has updated columns."""
        rows = fetch_csv("data/ux-guidelines.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["Category", "Issue", "Platform", "Severity"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")

    def test_ui_reasoning_has_expected_columns(self):
        """Verify ui-reasoning.csv has key columns."""
        rows = fetch_csv("data/ui-reasoning.csv")
        self.assertGreater(len(rows), 0)

        first_row = rows[0]
        expected = ["UI_Category", "Recommended_Pattern", "Severity"]
        for col in expected:
            self.assertIn(col, first_row.keys(), f"Missing column: {col}")


class TestBM25Algorithm(unittest.TestCase):
    """Test BM25 search algorithm."""

    def test_bm25_basic_search(self):
        """Test BM25 returns ranked results."""
        bm25 = BM25()
        docs = [
            "glassmorphism dark mode transparent",
            "brutalism bold typography",
            "minimalism clean simple",
        ]
        bm25.fit(docs)

        results = bm25.score("glassmorphism dark", top_k=3)
        self.assertGreater(len(results), 0)
        # First result should be the glassmorphism doc
        self.assertEqual(results[0][0], 0)

    def test_bm25_no_match(self):
        """Test BM25 handles no matches gracefully."""
        bm25 = BM25()
        bm25.fit(["hello world", "foo bar"])

        results = bm25.score("xyznotfound", top_k=3)
        self.assertEqual(len(results), 0)

    def test_bm25_empty_corpus(self):
        """Test BM25 handles empty corpus."""
        bm25 = BM25()
        bm25.fit([])

        results = bm25.score("test", top_k=3)
        self.assertEqual(len(results), 0)


class TestSearchIntegration(unittest.TestCase):
    """Integration tests for full search flow."""

    def test_search_glassmorphism_returns_results(self):
        """Test searching for glassmorphism returns relevant results."""
        rows = fetch_csv("data/styles.csv")
        all_columns = list(rows[0].keys())

        results = search_csv_data(rows, "glassmorphism", all_columns, top_k=3)
        self.assertGreater(len(results), 0)

        top_result = results[0]['row']
        found = any('glassmorphism' in str(v).lower() for v in top_result.values())
        self.assertTrue(found, "Top result should contain 'glassmorphism'")

    def test_search_healthcare_colors(self):
        """Test searching for healthcare in colors domain."""
        rows = fetch_csv("data/colors.csv")
        all_columns = list(rows[0].keys())

        results = search_csv_data(rows, "healthcare", all_columns, top_k=3)
        self.assertGreater(len(results), 0)

    def test_search_icons(self):
        """Test searching for navigation icons."""
        rows = fetch_csv("data/icons.csv")
        all_columns = list(rows[0].keys())

        results = search_csv_data(rows, "navigation menu", all_columns, top_k=3)
        self.assertGreater(len(results), 0)


class TestDomainConfig(unittest.TestCase):
    """Test domain configuration matches remote structure."""

    def test_all_domain_files_exist(self):
        """Verify all configured domain files are accessible."""
        for domain, config in DOMAINS.items():
            rows = fetch_csv(config["file"])
            self.assertGreater(len(rows), 0, f"Domain {domain} file not accessible")

    def test_all_stack_files_exist(self):
        """Verify all configured stack files are accessible."""
        for stack, path in STACKS.items():
            rows = fetch_csv(path)
            self.assertGreater(len(rows), 0, f"Stack {stack} file not accessible")

    def test_no_prompts_domain(self):
        """Verify prompts domain has been removed."""
        self.assertNotIn("prompts", DOMAINS)


class TestCaching(unittest.TestCase):
    """Test caching functionality."""

    def test_cache_path_generation(self):
        """Test cache path is generated correctly."""
        path = get_cache_path("data/styles.csv")
        self.assertEqual(path.name, "data_styles.csv")
        self.assertEqual(path.parent, CACHE_DIR)

    def test_cache_created_after_fetch(self):
        """Test that cache file is created after fetching."""
        rows = fetch_csv("data/styles.csv")
        self.assertGreater(len(rows), 0)

        cache_path = get_cache_path("data/styles.csv")
        self.assertTrue(cache_path.exists(), "Cache file should exist after fetch")

    def test_cache_validity(self):
        """Test cache validity check works."""
        fetch_csv("data/styles.csv")

        cache_path = get_cache_path("data/styles.csv")
        self.assertTrue(is_cache_valid(cache_path))

    def test_cache_dir_in_gitignore(self):
        """Verify tmp/ is in .gitignore."""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            self.assertIn("tmp/", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
