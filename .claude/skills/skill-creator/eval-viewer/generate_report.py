#!/usr/bin/env python3
"""Generate a self-contained HTML report visualizing the skill optimization journey.

Reads workspace iteration data, benchmark results, and optional description
optimization results, then injects everything into report.html as a single
static file.

Usage:
    python generate_report.py <workspace-path>
    python generate_report.py <workspace-path> --run-loop-results results.json
    python generate_report.py <workspace-path> --output /tmp/my-report.html

No dependencies beyond the Python stdlib are required.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def detect_skill_name(workspace: Path) -> str:
    """Auto-detect skill name from workspace directory name or evals.json."""
    # Try evals.json first
    evals_path = workspace / "evals.json"
    if evals_path.exists():
        try:
            data = json.loads(evals_path.read_text())
            name = data.get("skill_name", "")
            if name:
                return name
        except (json.JSONDecodeError, OSError):
            pass

    # Fall back to directory name
    name = workspace.name
    for suffix in ("-workspace", "_workspace", "-ws"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name


def read_skill_changes(iteration_dir: Path) -> list[str]:
    """Read skill_changes.json from an iteration directory."""
    path = iteration_dir / "skill_changes.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        return data.get("skill_changes", [])
    except (json.JSONDecodeError, OSError):
        return []


def find_iteration_dirs(workspace: Path) -> list[Path]:
    """Find iteration-N directories sorted by number."""
    dirs = []
    for child in workspace.iterdir():
        if child.is_dir() and child.name.startswith("iteration-"):
            try:
                num = int(child.name.split("-", 1)[1])
                dirs.append((num, child))
            except ValueError:
                continue
    dirs.sort(key=lambda t: t[0])
    return [d for _, d in dirs]


def read_benchmark(iteration_dir: Path) -> dict | None:
    """Read benchmark.json from an iteration directory."""
    path = iteration_dir / "benchmark.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def read_judge_output(iteration_dir: Path) -> dict | None:
    """Read judge-output.json from an iteration directory."""
    path = iteration_dir / "judge-output.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def read_grading(grading_path: Path) -> dict | None:
    """Read a grading.json file."""
    if not grading_path.exists():
        return None
    try:
        return json.loads(grading_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def read_eval_metadata(eval_dir: Path) -> dict | None:
    """Read eval_metadata.json from an eval directory."""
    path = eval_dir / "eval_metadata.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def collect_eval_expectations(iteration_dir: Path) -> dict:
    """Collect expectation results per eval from grading.json files.

    Returns: {eval_name: {config_name: [{text, passed, evidence}]}}
    """
    result: dict[str, dict[str, list[dict]]] = {}

    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir() or not eval_dir.name.startswith("eval-"):
            # Also accept named eval directories (anything that has config subdirs)
            if not eval_dir.is_dir():
                continue
            # Check if this dir has with_skill/without_skill subdirs
            has_configs = any(
                (eval_dir / c).is_dir()
                for c in ("with_skill", "without_skill", "new_skill", "old_skill")
            )
            if not has_configs:
                continue

        eval_name = eval_dir.name

        # Try to get a better name from eval_metadata
        metadata = read_eval_metadata(eval_dir)
        if metadata and metadata.get("eval_name"):
            eval_name = metadata["eval_name"]

        result[eval_name] = {}

        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            # Look for run dirs or direct grading.json
            grading_path = config_dir / "grading.json"
            if grading_path.exists():
                grading = read_grading(grading_path)
                if grading:
                    result[eval_name][config_dir.name] = grading.get(
                        "expectations", []
                    )
                continue

            # Check run-N subdirectories
            for run_dir in sorted(config_dir.glob("run-*")):
                grading = read_grading(run_dir / "grading.json")
                if grading:
                    # Use first run's expectations as representative
                    result[eval_name][config_dir.name] = grading.get(
                        "expectations", []
                    )
                    break

    return result


def read_evals_json(workspace: Path) -> dict[str, str]:
    """Read evals.json and return {eval_name_or_id: prompt}."""
    path = workspace / "evals.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        prompts = {}
        for ev in data.get("evals", []):
            prompt = ev.get("prompt", "")
            for key in filter(None, [ev.get("eval_name"), ev.get("name"), str(ev.get("id", "")) or None]):
                prompts[key] = prompt
        return prompts
    except (json.JSONDecodeError, OSError):
        return {}


def read_run_loop_results(path: Path) -> dict | None:
    """Read run_loop.py output JSON."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def extract_failures(iteration_dirs: list[Path]) -> list[dict]:
    """Extract failed expectations from the last iteration, grouped by eval."""
    if not iteration_dirs:
        return []

    last_dir = iteration_dirs[-1]
    groups: dict[str, list[dict]] = {}
    group_order: list[str] = []

    for eval_dir in sorted(last_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        has_configs = any(
            (eval_dir / c).is_dir()
            for c in ("with_skill", "without_skill", "new_skill", "old_skill")
        )
        if not has_configs:
            continue

        metadata = read_eval_metadata(eval_dir)
        eval_name = (metadata or {}).get("eval_name") or eval_dir.name

        grading = None
        for config_name in ("with_skill", "new_skill"):
            config_dir = eval_dir / config_name
            if config_dir.is_dir():
                grading = read_grading(config_dir / "grading.json")
                if grading:
                    break

        if not grading:
            continue

        failures = []
        for exp in grading.get("expectations", []):
            passed = exp.get("passed")
            if passed is False or passed is None:
                evidence = exp.get("evidence", "") or ""
                failures.append({
                    "text": exp.get("text", ""),
                    "evidence": evidence,
                    "neutral": passed is None,
                })

        if failures:
            if eval_name not in groups:
                groups[eval_name] = []
                group_order.append(eval_name)
            groups[eval_name].extend(failures)

    return [{"eval_name": name, "failures": groups[name]} for name in group_order]


def build_improvement_story(iterations: list[dict]) -> list[dict]:
    """Build a plain-text progression summary per iteration."""
    story = []
    for idx, it in enumerate(iterations):
        pass_rate = it.get("pass_rate")
        skill_changes = it.get("skill_changes") or []

        if skill_changes:
            parts = []
            for c in skill_changes[:3]:
                if isinstance(c, str):
                    parts.append(c)
                elif isinstance(c, dict):
                    parts.append(c.get("description") or c.get("change") or str(c))
            summary = ", ".join(parts)
        elif idx > 0:
            prev_rate = iterations[idx - 1].get("pass_rate")
            if pass_rate is not None and prev_rate is not None:
                delta = (pass_rate - prev_rate) * 100
                sign = "+" if delta >= 0 else ""
                summary = f"improved {sign}{delta:.0f}%"
            else:
                summary = ""
        else:
            summary = ""

        story.append({
            "iteration": it.get("iteration", idx + 1),
            "pass_rate": pass_rate,
            "summary": summary,
        })

    return story


def build_report_data(
    workspace: Path,
    skill_name: str,
    run_loop_path: Path | None = None,
) -> dict:
    """Collect all data from the workspace into the report data structure."""

    iteration_dirs = find_iteration_dirs(workspace)
    eval_prompts = read_evals_json(workspace)

    # Supplement eval_prompts from eval_metadata.json files in iteration dirs.
    # evals.json only has numeric ids, but eval_metadata.json has eval_name + prompt.
    for iter_dir in iteration_dirs:
        for eval_dir in iter_dir.iterdir():
            if not eval_dir.is_dir():
                continue
            metadata = read_eval_metadata(eval_dir)
            if not metadata:
                continue
            name = metadata.get("eval_name") or metadata.get("name")
            prompt = metadata.get("prompt", "")
            if name and prompt and name not in eval_prompts:
                eval_prompts[name] = prompt

    # Read judge-output.json from workspace root (legacy fallback)
    judge_data = None
    judge_path = workspace / "judge-output.json"
    if judge_path.exists():
        try:
            judge_data = json.loads(judge_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    iterations = []

    for idx, iter_dir in enumerate(iteration_dirs):
        iter_num = idx + 1
        try:
            iter_num = int(iter_dir.name.split("-", 1)[1])
        except ValueError:
            pass

        benchmark = read_benchmark(iter_dir)
        judge = read_judge_output(iter_dir)
        skill_changes = read_skill_changes(iter_dir)
        eval_expectations = collect_eval_expectations(iter_dir)

        per_eval: dict = {}
        for eval_name, configs in eval_expectations.items():
            per_eval[eval_name] = {"expectations": []}
            for config_name in ("with_skill", "new_skill"):
                if config_name in configs:
                    per_eval[eval_name]["expectations"] = configs[config_name]
                    break
            else:
                for _config_name, expectations_list in configs.items():
                    per_eval[eval_name]["expectations"] = expectations_list
                    break

        # Extract per-eval metrics from benchmark
        if benchmark:
            bm_per_eval = benchmark.get("run_summary", {}).get("per_eval", {})
            for ename, eval_stats in bm_per_eval.items():
                if ename not in per_eval:
                    per_eval[ename] = {"expectations": []}
                pe = per_eval[ename]
                for cfg in ("with_skill", "new_skill"):
                    if cfg in eval_stats:
                        pr = eval_stats[cfg].get("pass_rate", {})
                        pe["pass_rate"] = pr.get("mean") if isinstance(pr, dict) else pr
                        break
                pe["delta"] = eval_stats.get("delta")
                pe["winner"] = eval_stats.get("winner")

            if not bm_per_eval:
                for run in benchmark.get("runs", []):
                    ename = run.get("eval_name", "")
                    if not ename:
                        continue
                    result = run.get("result", {})
                    if ename not in per_eval:
                        per_eval[ename] = {"expectations": []}
                    per_eval[ename]["pass_rate"] = result.get("pass_rate")

            for ename, pe in per_eval.items():
                if pe.get("pass_rate") is None and pe.get("expectations"):
                    scored = [a for a in pe["expectations"] if a.get("passed") is not None]
                    total = len(scored)
                    passed = sum(1 for a in scored if a.get("passed") is True)
                    pe["pass_rate"] = passed / total if total > 0 else None

        pass_rate = None
        if benchmark and benchmark.get("run_summary"):
            rs = benchmark["run_summary"]
            for config in ("with_skill", "new_skill"):
                if config in rs:
                    pass_rate = rs[config].get("pass_rate", {}).get("mean")
                    break

        iterations.append(
            {
                "iteration": iter_num,
                "quality_score": judge.get("quality_score") if judge else None,
                "pass_rate": pass_rate,
                "recommendation": judge.get("decision") if judge else None,
                "notes": judge.get("reasoning") if judge else None,
                "reason": judge.get("risk_of_continuing") if judge else None,
                "skill_changes": skill_changes,
                "per_eval": per_eval,
                "benchmark": benchmark.get("run_summary") if benchmark else None,
                "judge": judge,
            }
        )

    # Description optimization data
    rl_data = None
    desc_opt = None
    if run_loop_path:
        rl_data = read_run_loop_results(run_loop_path)
        if rl_data:
            history_entries = []
            for h in rl_data.get("history", []):
                history_entries.append(
                    {
                        "iteration": h.get("iteration"),
                        "description": h.get("description", ""),
                        "train_passed": h.get("train_passed", h.get("passed", 0)),
                        "train_total": h.get("train_total", h.get("total", 0)),
                        "test_passed": h.get("test_passed"),
                        "test_total": h.get("test_total"),
                    }
                )
            desc_opt = {
                "original_description": rl_data.get("original_description", ""),
                "best_description": rl_data.get("best_description", ""),
                "best_score": rl_data.get("best_score", ""),
                "iterations_run": rl_data.get("iterations_run", 0),
                "history": history_entries,
            }

    # Extract model from first iteration's benchmark metadata
    model = None
    for iter_dir in iteration_dirs:
        bm = read_benchmark(iter_dir)
        if bm and bm.get("metadata", {}).get("executor_model"):
            model = bm["metadata"]["executor_model"]
            break

    return {
        "skill_name": skill_name,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": model,
        "iterations": iterations,
        "description_optimization": desc_opt,
        "eval_prompts": eval_prompts,
        "failures": extract_failures(iteration_dirs),
        "improvement_story": build_improvement_story(iterations),
        "judge": judge_data,
    }


def generate_html(report_data: dict) -> str:
    """Inject report data into the HTML template and return the complete page."""
    template_path = Path(__file__).parent / "report.html"
    template = template_path.read_text()

    data_json = json.dumps(report_data)
    return template.replace(
        "/*__REPORT_DATA__*/", f"const REPORT_DATA = {data_json};"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a self-contained HTML report for the skill optimization journey"
    )
    parser.add_argument(
        "workspace", type=Path, help="Path to the workspace directory"
    )
    parser.add_argument(
        "--run-loop-results",
        type=Path,
        default=None,
        help="Path to run_loop.py output JSON for description optimization data",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output path (defaults to <workspace>/report.html)",
    )
    parser.add_argument(
        "--skill-name",
        "-n",
        type=str,
        default=None,
        help="Skill name (auto-detected from workspace if not provided)",
    )
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Error: {workspace} is not a directory", file=sys.stderr)
        sys.exit(1)

    skill_name = args.skill_name or detect_skill_name(workspace)
    output_path = args.output or (workspace / "report.html")

    run_loop_path = args.run_loop_results.resolve() if args.run_loop_results else None

    report_data = build_report_data(workspace, skill_name, run_loop_path)

    html = generate_html(report_data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"\n  Report written to: {output_path}\n")


if __name__ == "__main__":
    main()
