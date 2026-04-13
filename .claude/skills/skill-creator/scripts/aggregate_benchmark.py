#!/usr/bin/env python3
"""
Aggregate individual run results into benchmark summary statistics.

Reads grading.json files from run directories and produces:
- run_summary with mean, stddev, min, max for each metric
- delta between with_skill and without_skill configurations

Usage:
    python aggregate_benchmark.py <benchmark_dir>

Example:
    python aggregate_benchmark.py benchmarks/2026-01-15T10-30-00/

The script supports two directory layouts:

    Workspace layout (from skill-creator iterations):
    <benchmark_dir>/
    └── eval-N/
        ├── with_skill/
        │   ├── run-1/grading.json
        │   └── run-2/grading.json
        └── without_skill/
            ├── run-1/grading.json
            └── run-2/grading.json

    Legacy layout (with runs/ subdirectory):
    <benchmark_dir>/
    └── runs/
        └── eval-N/
            ├── with_skill/
            │   └── run-1/grading.json
            └── without_skill/
                └── run-1/grading.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def calculate_stats(values: list[float]) -> dict:
    """Calculate mean, stddev, min, max, n for a list of values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0, "n": 0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "n": n
    }


def _load_declared_eval_ids(benchmark_dir: Path) -> set | None:
    """
    Load declared eval IDs from evals.json, if available.

    Looks for evals.json in benchmark_dir (workspace layout iteration dirs have
    evals.json one level up) and its parent. Returns a set of declared IDs, or
    None if evals.json cannot be found (caller should skip filtering).
    """
    for candidate in (benchmark_dir.parent / "evals.json", benchmark_dir / "evals.json"):
        if candidate.exists():
            try:
                with open(candidate) as f:
                    data = json.load(f)
                return {e["id"] for e in data.get("evals", []) if "id" in e}
            except (json.JSONDecodeError, OSError):
                return None
    return None


def load_run_results(benchmark_dir: Path) -> dict:
    """
    Load all run results from a benchmark directory.

    Returns dict keyed by config name (e.g. "with_skill"/"without_skill",
    or "new_skill"/"old_skill"), each containing a list of run results.
    """
    # Support both layouts: eval dirs directly under benchmark_dir, or under runs/
    runs_dir = benchmark_dir / "runs"
    if runs_dir.exists():
        search_dir = runs_dir
    else:
        search_dir = benchmark_dir

    _KNOWN_CONFIGS = {"with_skill", "without_skill", "new_skill", "old_skill"}
    _SKIP_DIRS = {"runs", "outputs", "inputs", "skill-snapshot", ".git"}
    results: dict[str, list] = {}

    # Cross-reference against evals.json to ignore stray inner-run artifacts
    declared_ids = _load_declared_eval_ids(benchmark_dir)

    # Discover eval dirs: any subdirectory containing config dirs with run-* subdirs
    # or config dirs with grading.json directly
    eval_dirs = []
    for child in sorted(search_dir.iterdir()):
        if not child.is_dir() or child.name in _SKIP_DIRS:
            continue
        # Check if this dir has config subdirs with run-* dirs or direct grading.json
        has_runs = any(
            list(config_dir.glob("run-*")) or (config_dir / "grading.json").exists()
            for config_dir in child.iterdir()
            if config_dir.is_dir()
        )
        if not has_runs:
            continue
        # If evals.json is available, only include dirs whose eval_id is declared
        if declared_ids is not None:
            metadata_path = child / "eval_metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path) as mf:
                        meta = json.load(mf)
                    if meta.get("eval_id") not in declared_ids:
                        print(f"Skipping {child.name}: eval_id {meta.get('eval_id')!r} not in evals.json",
                              file=sys.stderr)
                        continue
                except (json.JSONDecodeError, OSError):
                    pass  # Can't validate — include it
        eval_dirs.append(child)

    if not eval_dirs:
        print(f"No eval directories found in {search_dir}", file=sys.stderr)
        return {}

    for eval_idx, eval_dir in enumerate(eval_dirs):
        metadata_path = eval_dir / "eval_metadata.json"
        eval_name = None
        if metadata_path.exists():
            try:
                with open(metadata_path) as mf:
                    eval_meta = json.load(mf)
                    eval_id = eval_meta.get("eval_id", eval_idx)
                    eval_name = eval_meta.get("eval_name")
            except (json.JSONDecodeError, OSError):
                eval_id = eval_idx
        else:
            try:
                eval_id = int(eval_dir.name.split("-")[1])
            except ValueError:
                eval_id = eval_idx

        # Discover config directories dynamically rather than hardcoding names
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            # Skip non-config directories (inputs, outputs, etc.)
            run_dirs = list(config_dir.glob("run-*"))
            direct_grading = config_dir / "grading.json"
            if not run_dirs and not direct_grading.exists():
                continue
            config = config_dir.name
            if config not in _KNOWN_CONFIGS:
                print(f"Warning: unexpected config name '{config}' in {eval_dir}. "
                      f"Expected one of: {', '.join(sorted(_KNOWN_CONFIGS))}. "
                      f"Viewer may not display results correctly.", file=sys.stderr)
            if config not in results:
                results[config] = []

            # If grading.json exists directly in config dir and no run-* dirs,
            # treat it as a single run
            if direct_grading.exists() and not run_dirs:
                grading_files = [(1, direct_grading)]
            else:
                grading_files = []
                for run_dir in sorted(run_dirs):
                    run_number = int(run_dir.name.split("-")[1])
                    grading_file = run_dir / "grading.json"
                    if not grading_file.exists():
                        print(f"Warning: grading.json not found in {run_dir}", file=sys.stderr)
                        continue
                    grading_files.append((run_number, grading_file))

            for run_number, grading_file in grading_files:
                try:
                    with open(grading_file) as f:
                        grading = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in {grading_file}: {e}", file=sys.stderr)
                    continue

                # Extract metrics
                result = {
                    "eval_id": eval_id,
                    "eval_name": eval_name,
                    "run_number": run_number,
                    "pass_rate": grading.get("summary", {}).get("pass_rate", 0.0),
                    "passed": grading.get("summary", {}).get("passed", 0),
                    "failed": grading.get("summary", {}).get("failed", 0),
                    "total": grading.get("summary", {}).get("total", 0),
                }

                # Extract timing — grading.json for duration, timing.json for tokens
                timing = grading.get("timing", {})
                result["time_seconds"] = timing.get("total_duration_seconds", 0.0)
                result["tokens"] = None
                timing_file = grading_file.parent / "timing.json"
                if timing_file.exists():
                    try:
                        with open(timing_file) as tf:
                            timing_data = json.load(tf)
                        if result["time_seconds"] == 0.0:
                            result["time_seconds"] = timing_data.get("total_duration_seconds", 0.0)
                        result["tokens"] = timing_data.get("total_tokens")
                    except json.JSONDecodeError:
                        pass

                # Extract metrics if available
                metrics = grading.get("execution_metrics") or {}
                result["tool_calls"] = metrics.get("total_tool_calls", 0)
                result["errors"] = metrics.get("errors_encountered", 0)

                # Extract expectations — filter out malformed entries
                raw_expectations = grading.get("expectations", [])
                valid_expectations = []
                for exp in raw_expectations:
                    if "text" not in exp or "passed" not in exp:
                        print(f"Warning: expectation in {grading_file} missing required fields "
                              f"(text, passed): {exp}", file=sys.stderr)
                        continue
                    valid_expectations.append(exp)
                result["expectations"] = valid_expectations

                # Extract claims and eval feedback from grader
                result["claims"] = grading.get("claims", [])
                result["eval_feedback"] = grading.get("eval_feedback")

                # Extract notes from user_notes_summary
                notes_summary = grading.get("user_notes_summary", {})
                notes = []
                notes.extend(notes_summary.get("uncertainties", []))
                notes.extend(notes_summary.get("needs_review", []))
                notes.extend(notes_summary.get("workarounds", []))
                result["notes"] = notes

                results[config].append(result)

    return results


def aggregate_results(results: dict) -> dict:
    """
    Aggregate run results into summary statistics.

    Returns run_summary with stats for each configuration and delta.
    """
    run_summary = {}
    configs = list(results.keys())

    for config in configs:
        runs = results.get(config, [])

        if not runs:
            run_summary[config] = {
                "pass_rate": calculate_stats([]),
                "time_seconds": calculate_stats([]),
                "tokens": None
            }
            continue

        pass_rates = [r["pass_rate"] for r in runs]
        times = [r["time_seconds"] for r in runs]
        tokens = [r["tokens"] for r in runs if r.get("tokens") is not None]

        run_summary[config] = {
            "pass_rate": calculate_stats(pass_rates),
            "time_seconds": calculate_stats(times),
            "tokens": calculate_stats(tokens) if tokens else None
        }

    # Calculate per-eval breakdown
    # Group runs by eval_name/eval_id, then by config
    eval_runs: dict[str, dict[str, list]] = {}
    for config in results:
        for r in results[config]:
            ename = r.get("eval_name") or f"eval-{r.get('eval_id', '?')}"
            if ename not in eval_runs:
                eval_runs[ename] = {}
            if config not in eval_runs[ename]:
                eval_runs[ename][config] = []
            eval_runs[ename][config].append(r)

    per_eval_summary: dict[str, dict] = {}
    for ename, config_runs in eval_runs.items():
        entry: dict = {}
        for config, runs_list in config_runs.items():
            pass_rates = [r["pass_rate"] for r in runs_list]
            entry[config] = {
                "pass_rate": calculate_stats(pass_rates),
                "passed": sum(r["passed"] for r in runs_list),
                "failed": sum(r["failed"] for r in runs_list),
                "total": sum(r["total"] for r in runs_list),
            }
        # Compute delta and winner if two configs
        config_names = list(entry.keys())
        if len(config_names) >= 2:
            a_rate = entry[config_names[0]].get("pass_rate", {}).get("mean", 0)
            b_rate = entry[config_names[1]].get("pass_rate", {}).get("mean", 0)
            entry["delta"] = round(a_rate - b_rate, 4)
            entry["winner"] = config_names[0] if a_rate >= b_rate else config_names[1]
        per_eval_summary[ename] = entry

    run_summary["per_eval"] = per_eval_summary

    # Calculate delta between the first two configs (if two exist)
    if len(configs) >= 2:
        primary = run_summary.get(configs[0], {})
        baseline = run_summary.get(configs[1], {})

        delta_pass_rate = primary.get("pass_rate", {}).get("mean", 0) - baseline.get("pass_rate", {}).get("mean", 0)
        delta_time = primary.get("time_seconds", {}).get("mean", 0) - baseline.get("time_seconds", {}).get("mean", 0)

        primary_tokens = primary.get("tokens")
        baseline_tokens = baseline.get("tokens")
        if primary_tokens and baseline_tokens:
            delta_tokens = primary_tokens.get("mean", 0) - baseline_tokens.get("mean", 0)
            delta_tokens_str = f"{delta_tokens:+.0f}"
        else:
            delta_tokens_str = "N/A"

        run_summary["delta"] = {
            "pass_rate": f"{delta_pass_rate:+.2f}",
            "time_seconds": f"{delta_time:+.1f}",
            "tokens": delta_tokens_str
        }
    else:
        run_summary["delta"] = None

    return run_summary


def generate_benchmark(benchmark_dir: Path, skill_name: str = "", skill_path: str = "") -> dict:
    """
    Generate complete benchmark.json from run results.
    """
    results = load_run_results(benchmark_dir)
    run_summary = aggregate_results(results)

    # Build runs array for benchmark.json
    runs = []
    for config in results:
        for result in results[config]:
            run_entry = {
                "eval_id": result["eval_id"],
                "configuration": config,
                "run_number": result["run_number"],
                "result": {
                    "pass_rate": result["pass_rate"],
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "total": result["total"],
                    "time_seconds": result["time_seconds"],
                    "tokens": result.get("tokens"),
                    "tool_calls": result.get("tool_calls", 0),
                    "errors": result.get("errors", 0)
                },
                "expectations": result["expectations"],
                "notes": result["notes"],
                "claims": result.get("claims", []),
            }
            if result.get("eval_name"):
                run_entry["eval_name"] = result["eval_name"]
            if result.get("eval_feedback"):
                run_entry["eval_feedback"] = result["eval_feedback"]
            runs.append(run_entry)

    # Determine eval IDs from results
    eval_ids = sorted(set(
        r["eval_id"]
        for config in results.values()
        for r in config
    ))

    benchmark = {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "skill_path": skill_path or "<path/to/skill>",
            "executor_model": "<model-name>",
            "analyzer_model": "<model-name>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": eval_ids,
            "runs_per_configuration": 3
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": []  # To be filled by analyzer
    }

    return benchmark


def generate_markdown(benchmark: dict) -> str:
    """Generate human-readable benchmark.md from benchmark data."""
    metadata = benchmark["metadata"]
    run_summary = benchmark["run_summary"]

    # Determine config names (excluding "delta")
    configs = [k for k in run_summary if k not in ("delta", "per_eval")]
    has_comparison = len(configs) >= 2
    config_a = configs[0] if len(configs) >= 1 else "config_a"
    label_a = config_a.replace("_", " ").title()

    def _fmt_tokens(stats, total_runs):
        if not stats:
            return "N/A"
        n = stats.get("n", 0)
        base = f"{stats['mean']:.0f} ± {stats['stddev']:.0f}"
        if n < total_runs:
            return f"{base} ({n}/{total_runs} runs)"
        return base

    lines = [
        f"# Skill Benchmark: {metadata['skill_name']}",
        "",
        f"**Model**: {metadata['executor_model']}",
        f"**Date**: {metadata['timestamp']}",
        f"**Evals**: {', '.join(map(str, metadata['evals_run']))} ({metadata['runs_per_configuration']} runs each per configuration)",
        "",
        "## Summary",
        "",
    ]

    a_summary = run_summary.get(config_a, {})
    a_pr = a_summary.get("pass_rate", {})
    a_time = a_summary.get("time_seconds", {})
    a_tokens = a_summary.get("tokens")
    a_total_runs = a_pr.get("n", 0)

    if has_comparison:
        config_b = configs[1]
        label_b = config_b.replace("_", " ").title()
        b_summary = run_summary.get(config_b, {})
        b_pr = b_summary.get("pass_rate", {})
        b_time = b_summary.get("time_seconds", {})
        b_tokens = b_summary.get("tokens")
        b_total_runs = b_pr.get("n", 0)
        delta = run_summary.get("delta", {}) or {}

        lines.append(f"| Metric | {label_a} | {label_b} | Delta |")
        lines.append("|--------|------------|---------------|-------|")
        lines.append(f"| Pass Rate | {a_pr.get('mean', 0)*100:.0f}% ± {a_pr.get('stddev', 0)*100:.0f}% | {b_pr.get('mean', 0)*100:.0f}% ± {b_pr.get('stddev', 0)*100:.0f}% | {delta.get('pass_rate', '—')} |")
        lines.append(f"| Time | {a_time.get('mean', 0):.1f}s ± {a_time.get('stddev', 0):.1f}s | {b_time.get('mean', 0):.1f}s ± {b_time.get('stddev', 0):.1f}s | {delta.get('time_seconds', '—')}s |")
        lines.append(f"| Tokens | {_fmt_tokens(a_tokens, a_total_runs)} | {_fmt_tokens(b_tokens, b_total_runs)} | {delta.get('tokens', '—')} |")
    else:
        lines.append(f"| Metric | {label_a} |")
        lines.append("|--------|------------|")
        lines.append(f"| Pass Rate | {a_pr.get('mean', 0)*100:.0f}% ± {a_pr.get('stddev', 0)*100:.0f}% |")
        lines.append(f"| Time | {a_time.get('mean', 0):.1f}s ± {a_time.get('stddev', 0):.1f}s |")
        lines.append(f"| Tokens | {_fmt_tokens(a_tokens, a_total_runs)} |")

    # Notes section
    if benchmark.get("notes"):
        lines.extend([
            "",
            "## Notes",
            ""
        ])
        for note in benchmark["notes"]:
            lines.append(f"- {note}")

    # Eval feedback section (from grader critique of assertions)
    all_feedback = []
    for run in benchmark.get("runs", []):
        ef = run.get("eval_feedback")
        if ef:
            eval_label = run.get("eval_name", f"eval {run.get('eval_id', '?')}")
            config_label = run.get("configuration", "?")
            all_feedback.append((eval_label, config_label, ef))

    if all_feedback:
        lines.extend(["", "## Eval Feedback", ""])
        for eval_label, config_label, ef in all_feedback:
            lines.append(f"### {eval_label} ({config_label})")
            if ef.get("overall"):
                lines.append(f"**Overall**: {ef['overall']}")
            for suggestion in ef.get("suggestions", []):
                assertion = suggestion.get("assertion", "")
                reason = suggestion.get("reason", "")
                if assertion:
                    lines.append(f"- **{assertion}**: {reason}")
                else:
                    lines.append(f"- {reason}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate benchmark run results into summary statistics"
    )
    parser.add_argument(
        "benchmark_dir",
        type=Path,
        help="Path to the benchmark directory"
    )
    parser.add_argument(
        "--skill-name",
        default="",
        help="Name of the skill being benchmarked"
    )
    parser.add_argument(
        "--skill-path",
        default="",
        help="Path to the skill being benchmarked"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output path for benchmark.json (default: <benchmark_dir>/benchmark.json)"
    )

    args = parser.parse_args()

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}", file=sys.stderr)
        sys.exit(1)

    # Generate benchmark
    benchmark = generate_benchmark(args.benchmark_dir, args.skill_name, args.skill_path)

    # Determine output paths
    output_json = args.output or (args.benchmark_dir / "benchmark.json")
    output_md = output_json.with_suffix(".md")

    # Write benchmark.json
    with open(output_json, "w") as f:
        json.dump(benchmark, f, indent=2)
    print(f"Generated: {output_json}")

    # Write benchmark.md
    markdown = generate_markdown(benchmark)
    with open(output_md, "w") as f:
        f.write(markdown)
    print(f"Generated: {output_md}")

    # Print summary
    run_summary = benchmark["run_summary"]
    configs = [k for k in run_summary if k not in ("delta", "per_eval")]
    delta = run_summary.get("delta", {})

    print(f"\nSummary:")
    for config in configs:
        pr = run_summary[config]["pass_rate"]["mean"]
        label = config.replace("_", " ").title()
        print(f"  {label}: {pr*100:.1f}% pass rate")
    delta = run_summary.get("delta")
    if delta:
        print(f"  Delta:         {delta.get('pass_rate', '—')}")


if __name__ == "__main__":
    main()
