"""Geometry-aware probability_reduce suppression candidate.

Research-only; no live bot changes or orders.

The frozen p_hold >= 0.75 reduce-suppression candidate recovers many clipped
winners but keeps a few costly losers. This tests whether the fair-drawdown sign
can act as a side-aware physics gate before suppressing the exit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_geometry_suppression_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_geometry_suppression_latest.md"

P_HOLD_FLOOR = 0.75


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_source() -> dict[str, Any]:
    if not SOURCE_JSON.exists():
        return {}
    try:
        payload = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def side_won(row: dict[str, Any]) -> bool | None:
    side = str(row.get("side") or "").lower()
    result = str(row.get("result") or "").lower()
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def suppress_base(row: dict[str, Any]) -> bool:
    return (
        str(row.get("exit_reason") or "") == "mushroom_v28_probability_reduce"
        and (as_float(row.get("p_hold")) or 0.0) >= P_HOLD_FLOOR
    )


def suppress_side_geometry(row: dict[str, Any]) -> bool:
    if not suppress_base(row):
        return False
    side = str(row.get("side") or "").lower()
    drawdown = as_float(row.get("fair_drawdown_cents"))
    if drawdown is None:
        return False
    if side == "yes":
        return drawdown >= 0.0
    if side == "no":
        return drawdown <= 0.0
    return False


def suppress_yes_only_geometry(row: dict[str, Any]) -> bool:
    return suppress_side_geometry(row) and str(row.get("side") or "").lower() == "yes"


def suppress_no_only_geometry(row: dict[str, Any]) -> bool:
    return suppress_side_geometry(row) and str(row.get("side") or "").lower() == "no"


POLICIES = [
    ("current_v28", lambda row: False),
    ("base_suppress_reduce_p_hold_ge_075", suppress_base),
    ("side_geometry_suppress_reduce_p_hold_ge_075", suppress_side_geometry),
    ("yes_only_geometry_suppress_reduce_p_hold_ge_075", suppress_yes_only_geometry),
    ("no_only_geometry_suppress_reduce_p_hold_ge_075", suppress_no_only_geometry),
]


def score_policy(rows: list[dict[str, Any]], name: str, fn: Any) -> dict[str, Any]:
    scored = []
    for row in rows:
        current = as_float(row.get("current_cents"))
        hold = as_float(row.get("hold_cents"))
        if current is None or hold is None:
            continue
        suppress = bool(fn(row))
        candidate = hold if suppress else current
        won = side_won(row)
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "exit_reason": row.get("exit_reason"),
            "p_hold": row.get("p_hold"),
            "fair_drawdown_cents": row.get("fair_drawdown_cents"),
            "current_cents": current,
            "hold_cents": hold,
            "candidate_cents": candidate,
            "delta_cents": candidate - current,
            "suppressed": suppress,
            "side_won": won,
        })
    suppressed = [row for row in scored if row["suppressed"]]
    suppressed_winners = [row for row in suppressed if row["side_won"] is True]
    suppressed_losers = [row for row in suppressed if row["side_won"] is False]
    current_net = sum(row["current_cents"] for row in scored)
    candidate_net = sum(row["candidate_cents"] for row in scored)
    return {
        "policy": name,
        "settled": len(scored),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "candidate_wins": sum(1 for row in scored if row["candidate_cents"] > 0),
        "candidate_losses": sum(1 for row in scored if row["candidate_cents"] <= 0),
        "suppressed": len(suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "winner_recovery_cents": sum(row["delta_cents"] for row in suppressed_winners),
        "loss_control_cost_cents": sum(row["delta_cents"] for row in suppressed_losers),
        "suppressed_rows": suppressed,
    }


def build_report() -> dict[str, Any]:
    payload = load_source()
    rows = [row for row in payload.get("rows") or [] if isinstance(row, dict)]
    policies = [score_policy(rows, name, fn) for name, fn in POLICIES]
    policies.sort(key=lambda row: as_float(row.get("delta_vs_current_cents")) or -999999.0, reverse=True)
    best = policies[0] if policies else {}
    interpretation = [
        f"Best policy is {best.get('policy')} with delta {best.get('delta_vs_current_cents')}c on {best.get('settled')} settled rows.",
        "Geometry gate tests whether suppressing probability_reduce should require side-consistent fair-drawdown sign.",
        "This is diagnostic only; promotion would require frozen forward validation and source-quality checks.",
    ]
    return {
        "purpose": "Test geometry-aware probability_reduce suppression against the frozen reduce-suppression rows.",
        "source": str(SOURCE_JSON),
        "requirements": [
            "research-only, no live bot changes, no orders",
            "do not pick by old PnL without future freeze",
            "compare against current v28 and base p_hold suppression",
        ],
        "p_hold_floor": P_HOLD_FLOOR,
        "interpretation": interpretation,
        "policies": policies,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Reduce Geometry Suppression",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Policies",
        "",
        "| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | winner recovery c | loss cost c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for policy in report.get("policies") or []:
        lines.append(
            f"| `{policy.get('policy')}` | {policy.get('settled')} | "
            f"{fmt(policy.get('candidate_net_cents'))} | {fmt(policy.get('delta_vs_current_cents'))} | "
            f"{policy.get('candidate_wins')}/{policy.get('candidate_losses')} | "
            f"{policy.get('suppressed')} | {policy.get('suppressed_winners')}/{policy.get('suppressed_losers')} | "
            f"{fmt(policy.get('winner_recovery_cents'))} | {fmt(policy.get('loss_control_cost_cents'))} |"
        )
    lines.extend(["", "## Suppressed Rows By Best Policy", ""])
    best = (report.get("policies") or [{}])[0]
    lines.append("| market | side | result | p_hold | drawdown | current c | hold c | delta c |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    for row in best.get("suppressed_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('result')}` | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('delta_cents'))} |"
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
