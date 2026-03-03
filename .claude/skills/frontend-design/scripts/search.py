#!/usr/bin/env python3
"""
Aesthetic Eye Search Script
Fetches CSV data from GitHub and performs BM25 search.
Caches data locally with 24h TTL.
"""

import argparse
import csv
import io
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

from core import search_csv_data

# GitHub raw content base URL
GITHUB_BASE = "https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/src/ui-ux-pro-max"

# Cache settings
CACHE_DIR = Path(__file__).parent / "tmp"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Domain configurations: (csv_file, search_columns, output_columns)
# Column names match actual CSV headers from the remote repo
DOMAINS = {
    "styles": {
        "file": "data/styles.csv",
        "search": ["Style Category", "Keywords", "Best For", "Type", "AI Prompt Keywords"],
        "output": ["Style Category", "Type", "Keywords", "Primary Colors", "Secondary Colors", "Effects & Animation", "Best For", "Do Not Use For", "Performance", "Accessibility", "Mobile-Friendly", "Conversion-Focused", "Framework Compatibility", "AI Prompt Keywords", "CSS/Technical Keywords"],
    },
    "colors": {
        "file": "data/colors.csv",
        "search": ["Product Type", "Notes"],
        "output": ["Product Type", "Primary (Hex)", "Secondary (Hex)", "CTA (Hex)", "Background (Hex)", "Text (Hex)", "Border (Hex)", "Notes"],
    },
    "typography": {
        "file": "data/typography.csv",
        "search": ["Font Pairing Name", "Category", "Mood/Style Keywords", "Best For", "Heading Font", "Body Font"],
        "output": ["Font Pairing Name", "Category", "Heading Font", "Body Font", "Mood/Style Keywords", "Best For", "Google Fonts URL", "CSS Import", "Tailwind Config", "Notes"],
    },
    "charts": {
        "file": "data/charts.csv",
        "search": ["Data Type", "Keywords", "Best Chart Type", "Accessibility Notes"],
        "output": ["Data Type", "Keywords", "Best Chart Type", "Secondary Options", "Color Guidance", "Performance Impact", "Accessibility Notes", "Library Recommendation", "Interactive Level"],
    },
    "products": {
        "file": "data/products.csv",
        "search": ["Product Type", "Keywords", "Primary Style Recommendation", "Key Considerations"],
        "output": ["Product Type", "Keywords", "Primary Style Recommendation", "Secondary Styles", "Landing Page Pattern", "Dashboard Style (if applicable)", "Color Palette Focus", "Key Considerations"],
    },
    "landing": {
        "file": "data/landing.csv",
        "search": ["Pattern Name", "Keywords", "Conversion Optimization", "Section Order"],
        "output": ["Pattern Name", "Keywords", "Section Order", "Primary CTA Placement", "Color Strategy", "Recommended Effects", "Conversion Optimization"],
    },
    "ux": {
        "file": "data/ux-guidelines.csv",
        "search": ["Category", "Issue", "Description", "Platform"],
        "output": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"],
    },
    "icons": {
        "file": "data/icons.csv",
        "search": ["Category", "Icon Name", "Keywords", "Best For"],
        "output": ["Category", "Icon Name", "Keywords", "Library", "Import Code", "Usage", "Best For", "Style"],
    },
    "react-performance": {
        "file": "data/react-performance.csv",
        "search": ["Category", "Issue", "Keywords", "Description"],
        "output": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"],
    },
    "ui-reasoning": {
        "file": "data/ui-reasoning.csv",
        "search": ["UI_Category", "Recommended_Pattern", "Style_Priority"],
        "output": ["UI_Category", "Recommended_Pattern", "Style_Priority", "Color_Mood", "Typography_Mood", "Key_Effects", "Decision_Rules", "Anti_Patterns", "Severity"],
    },
    "web-interface": {
        "file": "data/web-interface.csv",
        "search": ["Category", "Issue", "Keywords", "Description"],
        "output": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"],
    },
}

# Stack files
STACKS = {
    "astro": "data/stacks/astro.csv",
    "flutter": "data/stacks/flutter.csv",
    "html-tailwind": "data/stacks/html-tailwind.csv",
    "jetpack-compose": "data/stacks/jetpack-compose.csv",
    "nextjs": "data/stacks/nextjs.csv",
    "nuxt-ui": "data/stacks/nuxt-ui.csv",
    "nuxtjs": "data/stacks/nuxtjs.csv",
    "react": "data/stacks/react.csv",
    "react-native": "data/stacks/react-native.csv",
    "shadcn": "data/stacks/shadcn.csv",
    "svelte": "data/stacks/svelte.csv",
    "swiftui": "data/stacks/swiftui.csv",
    "vue": "data/stacks/vue.csv",
}

# Keywords for auto-detecting domain
DOMAIN_KEYWORDS = {
    "styles": ["style", "design", "ui", "minimalism", "glassmorphism", "neumorphism", "brutalism", "dark mode", "flat", "aurora", "bento", "prompt", "css", "implementation", "variable", "checklist", "tailwind"],
    "colors": ["color", "palette", "hex", "#", "rgb"],
    "typography": ["font", "typography", "heading", "serif", "sans"],
    "charts": ["chart", "graph", "visualization", "trend", "bar", "pie", "scatter", "heatmap", "funnel"],
    "products": ["saas", "ecommerce", "e-commerce", "fintech", "healthcare", "gaming", "portfolio", "crypto", "dashboard"],
    "landing": ["landing", "page", "cta", "conversion", "hero", "testimonial", "pricing", "section"],
    "ux": ["ux", "usability", "accessibility", "wcag", "touch", "scroll", "animation", "keyboard", "navigation", "mobile"],
    "icons": ["icon", "icons", "lucide", "heroicons", "symbol", "glyph", "pictogram", "svg icon"],
    "react-performance": ["react", "next.js", "nextjs", "suspense", "memo", "usecallback", "useeffect", "rerender", "bundle", "waterfall", "barrel", "dynamic import", "rsc", "server component"],
    "ui-reasoning": ["ui reasoning", "decision", "anti-pattern", "style priority", "mood"],
    "web-interface": ["aria", "focus", "outline", "semantic", "virtualize", "autocomplete", "form", "input type", "preconnect"],
}


def get_cache_path(path: str) -> Path:
    """Get local cache path for a remote CSV file."""
    # Convert path like "data/styles.csv" to "data_styles.csv"
    safe_name = path.replace("/", "_")
    return CACHE_DIR / safe_name


def is_cache_valid(cache_path: Path) -> bool:
    """Check if cache file exists and is within TTL."""
    if not cache_path.exists():
        return False
    age = time.time() - cache_path.stat().st_mtime
    return age < CACHE_TTL_SECONDS


def cleanup_stale_cache():
    """Remove cache files older than TTL."""
    if not CACHE_DIR.exists():
        return
    now = time.time()
    for f in CACHE_DIR.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > CACHE_TTL_SECONDS:
            f.unlink()


def fetch_csv(path: str) -> list[dict]:
    """
    Fetch CSV from GitHub with local caching (24h TTL).

    Args:
        path: Relative path to CSV file

    Returns:
        List of dictionaries (one per row)
    """
    cache_path = get_cache_path(path)

    # Try cache first
    if is_cache_valid(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    # Fetch from remote
    url = f"{GITHUB_BASE}/{path}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')

            # Save to cache
            CACHE_DIR.mkdir(exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)

            reader = csv.DictReader(io.StringIO(content))
            return list(reader)
    except urllib.error.HTTPError as e:
        print(f"Error fetching {url}: HTTP {e.code}", file=sys.stderr)
        # Fall back to stale cache if available
        if cache_path.exists():
            print("Using stale cache.", file=sys.stderr)
            with open(cache_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        return []
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e.reason}", file=sys.stderr)
        # Fall back to stale cache if available
        if cache_path.exists():
            print("Using stale cache.", file=sys.stderr)
            with open(cache_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        return []


def detect_domain(query: str) -> str:
    """
    Auto-detect the best domain based on query keywords.

    Args:
        query: User search query

    Returns:
        Domain name (defaults to 'styles')
    """
    query_lower = query.lower()
    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[domain] = score

    if scores:
        return max(scores, key=scores.get)

    return "styles"  # Default


def format_results(results: list[dict], output_columns: list[str]) -> str:
    """
    Format search results for display.

    Args:
        results: List of search results with 'row' and 'score'
        output_columns: Columns to display

    Returns:
        Formatted string output
    """
    if not results:
        return "No results found."

    output = []
    for i, result in enumerate(results, 1):
        row = result['row']
        score = result['score']

        output.append(f"\n--- Result {i} (score: {score:.2f}) ---")
        for col in output_columns:
            if col in row and row[col]:
                value = row[col]
                # Truncate long values
                if len(value) > 300:
                    value = value[:297] + "..."
                output.append(f"{col}: {value}")

    return "\n".join(output)


def search(query: str, domain: Optional[str] = None, stack: Optional[str] = None,
           top_k: int = 5, json_output: bool = False) -> None:
    """
    Main search function.

    Args:
        query: Search query
        domain: Specific domain to search (auto-detected if None)
        stack: Stack-specific search (overrides domain)
        top_k: Number of results
        json_output: Output as JSON
    """
    if stack:
        # Stack-specific search
        if stack not in STACKS:
            print(f"Unknown stack: {stack}", file=sys.stderr)
            print(f"Available: {', '.join(STACKS.keys())}", file=sys.stderr)
            sys.exit(1)

        rows = fetch_csv(STACKS[stack])
        if not rows:
            print("Failed to fetch stack data.", file=sys.stderr)
            sys.exit(1)

        # Search all columns for stacks
        all_columns = list(rows[0].keys()) if rows else []
        results = search_csv_data(rows, query, all_columns, top_k)

        if json_output:
            print(json.dumps([r['row'] for r in results], indent=2))
        else:
            print(f"\nStack: {stack}")
            print(format_results(results, all_columns))

    else:
        # Domain search
        target_domain = domain or detect_domain(query)

        if target_domain not in DOMAINS:
            print(f"Unknown domain: {target_domain}", file=sys.stderr)
            print(f"Available: {', '.join(DOMAINS.keys())}", file=sys.stderr)
            sys.exit(1)

        config = DOMAINS[target_domain]
        rows = fetch_csv(config["file"])

        if not rows:
            print("Failed to fetch domain data.", file=sys.stderr)
            sys.exit(1)

        results = search_csv_data(rows, query, config["search"], top_k)

        if json_output:
            print(json.dumps([r['row'] for r in results], indent=2))
        else:
            print(f"\nDomain: {target_domain} (auto-detected)" if not domain else f"\nDomain: {target_domain}")
            print(format_results(results, config["output"]))


def main():
    parser = argparse.ArgumentParser(
        description="Search UI/UX design knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "glassmorphism dark mode"
  python3 search.py "healthcare" --domain colors
  python3 search.py "responsive" --stack html-tailwind
  python3 search.py "chart trend" --json
        """,
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(DOMAINS.keys()),
                        help="Specific domain to search")
    parser.add_argument("--stack", "-s", choices=list(STACKS.keys()),
                        help="Stack-specific search")
    parser.add_argument("--top", "-n", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()
    cleanup_stale_cache()
    search(args.query, args.domain, args.stack, args.top, args.json)


if __name__ == "__main__":
    main()
