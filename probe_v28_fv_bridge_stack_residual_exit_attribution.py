"""Residual exit attribution after FV bridge + reduce-geometry stack.

Research-only; no live bot changes or orders.

The geometry reduce rule recovers some clipped winners. This probe asks what
still remains: which exit branches leave directionally-correct FV bridge rows
negative even after the stack adjustment?
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_fv_bridge_exit_geometry_stack_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_bridge_stack_residual_exit_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_fv_bridge_stack_residual_exit_attribution_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def bucket_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "branch": None,
        "rows": 0,
        "directional_winners": 0,
        "negative_realized_winners": 0,
        "negative_stack_winners": 0,
        "realized_net_cents": 0.0,
        "stack_net_cents": 0.0,
        "hold_net_cents": 0.0,
        "stack_delta_cents": 0.0,
        "examples": [],
    })
    for row in rows:
        if not isinstance(row, dict):
            continue
        branch = str(row.get("matched_exit_reason") or "no_matched_exit")
        bucket = buckets[branch]
        bucket["branch"] = branch
        bucket["rows"] += 1
        realized = as_float(row.get("realized_net_cents")) or 0.0
        stack_net = as_float(row.get("stack_net_cents")) or 0.0
        hold = as_float(row.get("hold_net_cents")) or 0.0
        delta = as_float(row.get("stack_delta_cents")) or 0.0
        bucket["realized_net_cents"] += realized
        bucket["stack_net_cents"] += stack_net
        bucket["hold_net_cents"] += hold
        bucket["stack_delta_cents"] += delta
        if row.get("side_won") is True:
            bucket["directional_winners"] += 1
            if realized < 0:
                bucket["negative_realized_winners"] += 1
            if stack_net < 0:
                bucket["negative_stack_winners"] += 1
        if row.get("side_won") is True and stack_net < 0 and len(bucket["examples"]) < 6:
            bucket["examples"].append({
                "market": row.get("market"),
                "source": row.get("source"),
                "side": row.get("side"),
                "ask_prob": row.get("ask_prob"),
                "realized_net_cents": realized,
                "stack_net_cents": stack_net,
                "hold_net_cents": hold,
                "matched_seconds": row.get("matched_seconds"),
            })
    out = list(buckets.values())
    out.sort(
        key=lambda bucket: (
            bucket["negative_stack_winners"],
            -bucket["stack_net_cents"],
            bucket["rows"],
        ),
        reverse=True,
    )
    return out


def scenario_rows(report: dict[str, Any], window_name: str, scenario_name: str) -> list[dict[str, Any]]:
    for window in report.get("windows") or []:
        if not isinstance(window, dict) or window.get("window") != window_name:
            continue
        for scenario in window.get("scenarios") or []:
            if isinstance(scenario, dict) and scenario.get("scenario") == scenario_name:
                rows = scenario.get("rows")
                return rows if isinstance(rows, list) else []
    return []


def build_report() -> dict[str, Any]:
    stack_report = load_json(STACK_JSON)
    windows = []
    for window in stack_report.get("windows") or []:
        if not isinstance(window, dict):
            continue
        scenarios = []
        for scenario in window.get("scenarios") or []:
            if not isinstance(scenario, dict):
                continue
            rows = scenario.get("rows")
            if not isinstance(rows, list):
                rows = []
            scenarios.append({
                "scenario": scenario.get("scenario"),
                "settled": scenario.get("settled"),
                "coverage_pct": scenario.get("coverage_pct"),
                "stack_net_cents": scenario.get("stack_net_cents"),
                "negative_stack_winners": scenario.get("negative_stack_winners"),
                "branch_buckets": bucket_rows(rows),
            })
        windows.append({
            "window": window.get("window"),
            "freeze_ts_utc": window.get("freeze_ts_utc"),
            "scenarios": scenarios,
        })
    approved_diag_rows = scenario_rows(stack_report, "diagnostic_existing_false_conviction_freeze", "lead_approved_only")
    approved_buckets = bucket_rows(approved_diag_rows)
    top_residual = approved_buckets[0] if approved_buckets else {}
    return {
        "purpose": "Attribution of remaining negative directionally-correct winners after FV bridge + reduce-geometry stack.",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "diagnostic attribution only unless rows are post-freeze",
            "preserve approved-only/reconstructed split",
        ],
        "source": str(STACK_JSON),
        "interpretation": [
            f"Approved-only diagnostic residual top branch is {top_residual.get('branch')} with "
            f"{top_residual.get('negative_stack_winners')} negative stack winners.",
            "Branches with negative directionally-correct winners are candidates for further exit physics, not live patches.",
        ],
        "windows": windows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 FV Bridge Stack Residual Exit Attribution",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(["", f"## {window.get('window')}", ""])
        for scenario in window.get("scenarios") or []:
            lines.extend(["", f"### {scenario.get('scenario')}", ""])
            lines.append("| branch | rows | directional winners | negative winners current/stack | realized c | stack c | hold c | stack delta c |")
            lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
            for bucket in scenario.get("branch_buckets") or []:
                lines.append(
                    f"| `{bucket.get('branch')}` | {bucket.get('rows')} | {bucket.get('directional_winners')} | "
                    f"{bucket.get('negative_realized_winners')}/{bucket.get('negative_stack_winners')} | "
                    f"{fmt(bucket.get('realized_net_cents'))} | {fmt(bucket.get('stack_net_cents'))} | "
                    f"{fmt(bucket.get('hold_net_cents'))} | {fmt(bucket.get('stack_delta_cents'))} |"
                )
            lines.extend(["", "Residual Negative Winner Examples:", ""])
            lines.append("| branch | market | source | side | ask | realized c | stack c | hold c |")
            lines.append("|---|---|---|---|---:|---:|---:|---:|")
            for bucket in scenario.get("branch_buckets") or []:
                for row in bucket.get("examples") or []:
                    lines.append(
                        f"| `{bucket.get('branch')}` | `{row.get('market')}` | `{row.get('source')}` | "
                        f"`{row.get('side')}` | {fmt(row.get('ask_prob'))} | "
                        f"{fmt(row.get('realized_net_cents'))} | {fmt(row.get('stack_net_cents'))} | "
                        f"{fmt(row.get('hold_net_cents'))} |"
                    )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
