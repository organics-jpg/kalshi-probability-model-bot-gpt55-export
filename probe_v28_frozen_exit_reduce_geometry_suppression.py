"""Frozen-forward monitor for geometry-aware probability_reduce suppression.

Research-only; no live bot changes or orders.

Freeze the side-geometry p_hold >= 0.75 rule from
probe_v28_exit_reduce_geometry_suppression.py and score only rows whose entry
timestamp occurs after this script's first run.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_geometry_suppression_latest.md"

P_HOLD_FLOOR = 0.75


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def freeze_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "candidate": "side_geometry_suppress_reduce_p_hold_ge_075",
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "p_hold_floor": P_HOLD_FLOOR,
        "rule": "Suppress mushroom_v28_probability_reduce only when p_hold >= 0.75 and fair_drawdown sign agrees with held side: YES drawdown >= 0, NO drawdown <= 0.",
        "physics": "A high held-side probability is not enough; the local fair-value movement should agree that the thesis has not truly broken.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def side_won(row: dict[str, Any]) -> bool | None:
    side = str(row.get("side") or "").lower()
    result = str(row.get("result") or "").lower()
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def suppress_candidate(row: dict[str, Any]) -> bool:
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


def suppress_base(row: dict[str, Any]) -> bool:
    if str(row.get("exit_reason") or "") != "mushroom_v28_probability_reduce":
        return False
    if (as_float(row.get("p_hold")) or 0.0) < P_HOLD_FLOOR:
        return False
    return True


def score_policy(rows: list[dict[str, Any]], policy: str, suppress_fn: Any) -> dict[str, Any]:
    scored = []
    for row in rows:
        current = as_float(row.get("current_cents"))
        hold = as_float(row.get("hold_cents"))
        if current is None or hold is None:
            continue
        suppressed = bool(suppress_fn(row))
        candidate = hold if suppressed else current
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
            "suppressed": suppressed,
            "side_won": side_won(row),
        })
    suppressed_rows = [row for row in scored if row["suppressed"]]
    suppressed_winners = [row for row in suppressed_rows if row["side_won"] is True]
    suppressed_losers = [row for row in suppressed_rows if row["side_won"] is False]
    current_net = sum(row["current_cents"] for row in scored)
    candidate_net = sum(row["candidate_cents"] for row in scored)
    return {
        "policy": policy,
        "rows": len(scored),
        "settled": len(scored),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "candidate_wins": sum(1 for row in scored if row["candidate_cents"] > 0),
        "candidate_losses": sum(1 for row in scored if row["candidate_cents"] <= 0),
        "suppressed": len(suppressed_rows),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "winner_recovery_cents": sum(row["delta_cents"] for row in suppressed_winners),
        "loss_control_cost_cents": sum(row["delta_cents"] for row in suppressed_losers),
        "suppressed_rows": suppressed_rows,
    }


def build_report() -> dict[str, Any]:
    state = freeze_state()
    source = load_json(SOURCE_JSON)
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    rows = []
    for row in source.get("rows") or []:
        if not isinstance(row, dict):
            continue
        entry_ts = parse_ts(row.get("entry_ts"))
        if freeze_ts is not None and (entry_ts is None or entry_ts <= freeze_ts):
            continue
        current = as_float(row.get("current_cents"))
        hold = as_float(row.get("hold_cents"))
        if current is None or hold is None:
            continue
        suppressed = suppress_candidate(row)
        candidate = hold if suppressed else current
        enriched = {
            "market": row.get("market"),
            "entry_ts": row.get("entry_ts"),
            "side": row.get("side"),
            "result": row.get("result"),
            "exit_reason": row.get("exit_reason"),
            "p_hold": row.get("p_hold"),
            "fair_drawdown_cents": row.get("fair_drawdown_cents"),
            "current_cents": current,
            "hold_cents": hold,
            "candidate_cents": candidate,
            "delta_cents": candidate - current,
            "suppressed": suppressed,
            "side_won": side_won(row),
        }
        rows.append(enriched)
    counterfactual = [
        score_policy(rows, "base_suppress_reduce_p_hold_ge_075", suppress_base),
        score_policy(rows, "side_geometry_suppress_reduce_p_hold_ge_075", suppress_candidate),
    ]
    geometry_policy = counterfactual[1]
    summary = {
        key: value
        for key, value in geometry_policy.items()
        if key != "suppressed_rows"
    }
    blockers = []
    if summary["settled"] < 30:
        blockers.append("settled_lt_30")
    if summary["delta_vs_current_cents"] <= 0:
        blockers.append("delta_not_positive")
    if summary["suppressed_losers"] > 0:
        blockers.append("suppressed_losers_present")
    return {
        "purpose": "Frozen-forward monitor for geometry-aware probability_reduce suppression.",
        "freeze": state,
        "source": str(SOURCE_JSON),
        "summary": summary,
        "counterfactual_policies": counterfactual,
        "blockers": blockers,
        "candidate_live_ready": not blockers,
        "interpretation": [
            f"Frozen geometry suppression has {summary['settled']} settled rows after freeze.",
            f"Delta versus current v28 exits is {summary['delta_vs_current_cents']}c.",
            f"Suppressed exits: {summary['suppressed']}; winners {summary['suppressed_winners']}, losers {summary['suppressed_losers']}.",
            "Base p_hold suppression is included as a post-geometry-freeze counterfactual; geometry is not validated until it fires and beats that baseline on forward rows.",
        ],
        "rows": rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Exit Reduce Geometry Suppression",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future rows/settled: `{summary.get('rows')}/{summary.get('settled')}`",
        f"- Current/candidate gross: `{fmt(summary.get('current_net_cents'))}c/{fmt(summary.get('candidate_net_cents'))}c`",
        f"- Delta vs current: `{fmt(summary.get('delta_vs_current_cents'))}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Post-Freeze Counterfactual Policies",
        "",
        "| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | winner recovery c | loss cost c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for policy in report.get("counterfactual_policies") or []:
        lines.append(
            f"| `{policy.get('policy')}` | {policy.get('settled')} | "
            f"{fmt(policy.get('candidate_net_cents'))} | {fmt(policy.get('delta_vs_current_cents'))} | "
            f"{policy.get('candidate_wins')}/{policy.get('candidate_losses')} | "
            f"{policy.get('suppressed')} | {policy.get('suppressed_winners')}/{policy.get('suppressed_losers')} | "
            f"{fmt(policy.get('winner_recovery_cents'))} | {fmt(policy.get('loss_control_cost_cents'))} |"
        )
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | result | p_hold | drawdown | current c | hold c | candidate c | delta c | suppressed |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('result')}` | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('candidate_cents'))} | {fmt(row.get('delta_cents'))} | "
            f"{row.get('suppressed')} |"
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
