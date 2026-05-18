"""Bake off FV bridge exit-stack variants including collapse suppression.

Research-only; no live bot changes or orders.

The reduce-geometry stack recovered several clipped winners. Residual
attribution points to probability_collapse_full as the next branch to test.
This diagnostic keeps the FV bridge fixed and compares exit-stack variants.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import probe_v28_fv_bridge_exit_geometry_stack as stack


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_fv_bridge_exit_combo_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_fv_bridge_exit_combo_bakeoff_latest.md"

P_HOLD_FLOOR = 0.75


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reduce_geometry(exit_row: dict[str, Any]) -> bool:
    return stack.suppress_geometry(exit_row)


def collapse_drawdown_lte(limit: float) -> Callable[[dict[str, Any]], bool]:
    def _rule(exit_row: dict[str, Any]) -> bool:
        if str(exit_row.get("exit_reason") or "") != "mushroom_v28_probability_collapse_full":
            return False
        drawdown = as_float(exit_row.get("fair_drawdown_cents"))
        return drawdown is not None and drawdown <= limit

    return _rule


def collapse_drawdown_lte_and_p_hold(limit: float, p_floor: float) -> Callable[[dict[str, Any]], bool]:
    def _rule(exit_row: dict[str, Any]) -> bool:
        if not collapse_drawdown_lte(limit)(exit_row):
            return False
        return (as_float(exit_row.get("p_hold")) or 0.0) >= p_floor

    return _rule


POLICIES: list[tuple[str, list[Callable[[dict[str, Any]], bool]]]] = [
    ("current_exit_policy", []),
    ("reduce_geometry_only", [reduce_geometry]),
    ("reduce_geometry_plus_collapse_drawdown_lte_8", [reduce_geometry, collapse_drawdown_lte(8.0)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_10", [reduce_geometry, collapse_drawdown_lte(10.0)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_12", [reduce_geometry, collapse_drawdown_lte(12.0)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_15", [reduce_geometry, collapse_drawdown_lte(15.0)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_18", [reduce_geometry, collapse_drawdown_lte(18.0)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055", [reduce_geometry, collapse_drawdown_lte_and_p_hold(15.0, 0.55)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060", [reduce_geometry, collapse_drawdown_lte_and_p_hold(15.0, 0.60)]),
    ("reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060", [reduce_geometry, collapse_drawdown_lte_and_p_hold(18.0, 0.60)]),
]


def suppress_by_policy(exit_row: dict[str, Any], rules: list[Callable[[dict[str, Any]], bool]]) -> bool:
    return any(rule(exit_row) for rule in rules)


def score_scenario(
    scenario: dict[str, Any],
    exit_index: dict[tuple[str, str], list[dict[str, Any]]],
    policy_name: str,
    rules: list[Callable[[dict[str, Any]], bool]],
) -> dict[str, Any]:
    used: set[int] = set()
    scored_rows = []
    rows = scenario.get("rows")
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        current = as_float(row.get("net_cents"))
        hold = stack.hold_net_cents(row)
        if current is None or hold is None:
            continue
        match = stack.match_exit_row(row, exit_index, used)
        candidate = current
        delta = 0.0
        suppressed = False
        branch = "no_matched_exit"
        if match is not None:
            branch = str(match.get("exit_reason") or "no_exit_reason")
            match_current = as_float(match.get("current_cents"))
            match_hold = as_float(match.get("hold_cents"))
            if match_current is not None and match_hold is not None and suppress_by_policy(match, rules):
                suppressed = True
                delta = match_hold - match_current
                candidate = current + delta
        scored_rows.append({
            "market": row.get("market"),
            "source": row.get("source"),
            "side": row.get("side"),
            "side_won": row.get("side_won"),
            "ask_prob": row.get("ask_prob"),
            "realized_net_cents": current,
            "hold_net_cents": hold,
            "candidate_net_cents": candidate,
            "candidate_delta_cents": delta,
            "matched_exit": match is not None,
            "matched_exit_reason": branch,
            "suppressed": suppressed,
        })
    directional_wins = sum(1 for row in scored_rows if row.get("side_won") is True)
    directional_losses = sum(1 for row in scored_rows if row.get("side_won") is False)
    realized = sum(row["realized_net_cents"] for row in scored_rows)
    candidate = sum(row["candidate_net_cents"] for row in scored_rows)
    hold = sum(row["hold_net_cents"] for row in scored_rows)
    return {
        "policy": policy_name,
        "scenario": scenario.get("scenario"),
        "entries": scenario.get("entries"),
        "settled": len(scored_rows),
        "coverage_pct": scenario.get("coverage_pct"),
        "directional_wins": directional_wins,
        "directional_losses": directional_losses,
        "realized_net_cents": realized,
        "candidate_net_cents": candidate,
        "hold_to_settlement_net_cents": hold,
        "delta_vs_realized_cents": candidate - realized,
        "candidate_vs_hold_cents": candidate - hold,
        "matched_rows": sum(1 for row in scored_rows if row.get("matched_exit")),
        "suppressed_rows": sum(1 for row in scored_rows if row.get("suppressed")),
        "negative_candidate_winners": sum(
            1 for row in scored_rows
            if row.get("side_won") is True and (as_float(row.get("candidate_net_cents")) or 0.0) < 0.0
        ),
        "rows": scored_rows,
    }


def build_report() -> dict[str, Any]:
    bridge_payload = stack.load_json(stack.BRIDGE_SOURCE_JSON)
    exit_payload = stack.load_json(stack.EXIT_ROWS_JSON)
    exit_index = stack.indexed_exit_rows(exit_payload)
    windows = []
    for window in stack.bridge_windows(bridge_payload):
        scenario_reports = []
        for scenario in window.get("scenarios") or []:
            if not isinstance(scenario, dict):
                continue
            policies = [score_scenario(scenario, exit_index, name, rules) for name, rules in POLICIES]
            policies.sort(
                key=lambda row: (
                    as_float(row.get("candidate_net_cents")) or -999999.0,
                    -(as_float(row.get("negative_candidate_winners")) or 999999.0),
                ),
                reverse=True,
            )
            scenario_reports.append({
                "scenario": scenario.get("scenario"),
                "policies": policies,
            })
        windows.append({
            "window": window.get("window"),
            "freeze_ts_utc": window.get("freeze_ts_utc"),
            "future_denominator": window.get("future_denominator"),
            "scenarios": scenario_reports,
        })
    approved_diag = next(
        (
            scenario for window in windows
            if window.get("window") == "diagnostic_existing_false_conviction_freeze"
            for scenario in window.get("scenarios", [])
            if scenario.get("scenario") == "lead_approved_only"
        ),
        {},
    )
    best = (approved_diag.get("policies") or [{}])[0]
    return {
        "purpose": "Diagnostic bakeoff for FV bridge exit-stack policies after residual collapse attribution.",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "FV bridge row selection stays fixed",
            "diagnostic only; any winner must be frozen forward before promotion",
        ],
        "interpretation": [
            f"Approved-only diagnostic best policy is {best.get('policy')} with candidate net {best.get('candidate_net_cents')}c.",
            "Collapse suppress rules here use available matched exit fields; the older sigma-aware rule remains a separate hypothesis.",
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
        "# v28 FV Bridge Exit Combo Bakeoff",
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
            lines.append("| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |")
            lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
            for idx, policy in enumerate(scenario.get("policies") or [], start=1):
                lines.append(
                    f"| {idx} | `{policy.get('policy')}` | {policy.get('settled')} | "
                    f"{fmt(policy.get('coverage_pct'))} | {policy.get('directional_wins')}/{policy.get('directional_losses')} | "
                    f"{fmt(policy.get('candidate_net_cents'))} | {fmt(policy.get('delta_vs_realized_cents'))} | "
                    f"{fmt(policy.get('hold_to_settlement_net_cents'))} | {policy.get('matched_rows')} | "
                    f"{policy.get('suppressed_rows')} | {policy.get('negative_candidate_winners')} |"
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
