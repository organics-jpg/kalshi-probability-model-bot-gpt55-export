"""Frozen watch for a relaxed geometry guard on probability_reduce exits.

Research-only; no live bot changes or orders.

The base p_hold>=0.75 probability_reduce suppression has strong forward delta
but two costly loss-control failures. The side-geometry guard removes those
diagnostically, but in its own forward window it rejected one positive NO-side
base opportunity. This watch freezes the smallest observed relaxation:

- suppress when the side-geometry sign agrees, or
- for NO-side only, allow sign-disagree suppression when the current exit is
  already a deep realized loss (current_cents <= -20).

Diagnostic rows are mechanism evidence only. Promotion requires rows after this
watch's own freeze timestamp.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.md"

P_HOLD_FLOOR = 0.75
NO_DEEP_CURRENT_LOSS_CENTS = -20.0
MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "candidate": "side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075",
        "freeze_ts_utc": utc_now_iso(),
        "p_hold_floor": P_HOLD_FLOOR,
        "no_deep_current_loss_cents": NO_DEEP_CURRENT_LOSS_CENTS,
        "rule": (
            "Suppress mushroom_v28_probability_reduce when p_hold >= 0.75 and "
            "fair_drawdown sign agrees with the held side; additionally, for NO "
            "side only, allow sign-disagree suppression if current_cents <= -20."
        ),
        "physics": (
            "Side-consistent fair-drawdown is the main guard. The NO-side deep-loss "
            "exception treats a probability_reduce exit that is already a large "
            "realized loss as less useful loss control when p_hold remains high."
        ),
        "research_only": True,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def suppress_relaxed(row: dict[str, Any]) -> bool:
    if suppress_side_geometry(row):
        return True
    if not suppress_base(row):
        return False
    side = str(row.get("side") or "").lower()
    drawdown = as_float(row.get("fair_drawdown_cents"))
    current = as_float(row.get("current_cents"))
    return (
        side == "no"
        and drawdown is not None
        and drawdown > 0.0
        and current is not None
        and current <= NO_DEEP_CURRENT_LOSS_CENTS
    )


POLICIES = [
    ("base_suppress_reduce_p_hold_ge_075", suppress_base),
    ("side_geometry_suppress_reduce_p_hold_ge_075", suppress_side_geometry),
    ("side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075", suppress_relaxed),
]


def load_source_rows() -> list[dict[str, Any]]:
    payload = load_json(SOURCE_JSON)
    return [row for row in payload.get("rows") or [] if isinstance(row, dict)]


def rows_after(rows: list[dict[str, Any]], freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    out = []
    for row in rows:
        entry_dt = parse_ts(row.get("entry_ts"))
        if freeze_dt is not None and (entry_dt is None or entry_dt <= freeze_dt):
            continue
        out.append(row)
    return out


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
            "entry_ts": row.get("entry_ts"),
            "side": row.get("side"),
            "result": row.get("result"),
            "exit_reason": row.get("exit_reason"),
            "exit_cents": row.get("exit_cents"),
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
    delta = candidate_net - current_net
    return {
        "policy": policy,
        "rows": len(scored),
        "settled": len(scored),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": delta,
        "candidate_wins": sum(1 for row in scored if row["candidate_cents"] > 0),
        "candidate_losses": sum(1 for row in scored if row["candidate_cents"] <= 0),
        "suppressed": len(suppressed_rows),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "winner_recovery_cents": sum(row["delta_cents"] for row in suppressed_winners),
        "loss_control_cost_cents": sum(row["delta_cents"] for row in suppressed_losers),
        "full_loss_cushion_estimate": int(max(0.0, delta) // 100.0),
        "suppressed_rows": suppressed_rows,
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    if int(as_float(summary.get("settled")) or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if int(as_float(summary.get("suppressed")) or 0) < MIN_SUPPRESSED:
        out.append("suppressed_decisions_lt_30")
    if (as_float(summary.get("delta_vs_current_cents")) or 0.0) <= 0.0:
        out.append("delta_not_positive")
    if int(as_float(summary.get("suppressed_losers")) or 0) > 0:
        out.append("suppressed_losers_present")
    if int(as_float(summary.get("full_loss_cushion_estimate")) or 0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def best_policy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    policies = [score_policy(rows, name, fn) for name, fn in POLICIES]
    policies.sort(key=lambda row: as_float(row.get("delta_vs_current_cents")) or -999999.0, reverse=True)
    return {
        "policies": policies,
        "best": policies[0] if policies else {},
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows = load_source_rows()
    diagnostic = best_policy(all_rows)
    strict_rows = rows_after(all_rows, str(state["freeze_ts_utc"]))
    strict = best_policy(strict_rows)
    strict_summary = next(
        (
            row for row in strict["policies"]
            if row.get("policy") == state.get("candidate")
        ),
        strict["best"],
    )
    report = {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Frozen-forward watch for the relaxed side-geometry probability_reduce suppression guard.",
        "source": str(SOURCE_JSON),
        "freeze": state,
        "diagnostic": diagnostic,
        "strict_post_freeze": strict,
        "summary": {key: value for key, value in strict_summary.items() if key != "suppressed_rows"},
        "blockers": blockers(strict_summary),
        "candidate_live_ready": False,
    }
    report["interpretation"] = [
        "Research-only frozen watch; no live logic changes or orders.",
        (
            f"Diagnostic best is {diagnostic['best'].get('policy')} with "
            f"{diagnostic['best'].get('delta_vs_current_cents')}c delta and "
            f"{diagnostic['best'].get('suppressed_winners')}/{diagnostic['best'].get('suppressed_losers')} suppressed W/L."
        ),
        (
            f"Strict post-freeze candidate has {strict_summary.get('settled')} settled rows, "
            f"{strict_summary.get('suppressed')} suppressed decisions, "
            f"{strict_summary.get('delta_vs_current_cents')}c delta, blockers {report['blockers']}."
        ),
    ]
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_policy_table(lines: list[str], policies: list[dict[str, Any]]) -> None:
    lines.extend([
        "| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | recovery c | loss cost c | cushion |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for policy in policies:
        lines.append(
            f"| `{policy.get('policy')}` | {policy.get('settled')} | "
            f"{fmt(policy.get('candidate_net_cents'))} | {fmt(policy.get('delta_vs_current_cents'))} | "
            f"{policy.get('candidate_wins')}/{policy.get('candidate_losses')} | "
            f"{policy.get('suppressed')} | {policy.get('suppressed_winners')}/{policy.get('suppressed_losers')} | "
            f"{fmt(policy.get('winner_recovery_cents'))} | {fmt(policy.get('loss_control_cost_cents'))} | "
            f"{policy.get('full_loss_cushion_estimate')} |"
        )


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    summary = report.get("summary") or {}
    lines = [
        "# v28 Frozen Exit Reduce Geometry Relaxed Watch",
        "",
        "Research-only; frozen watch, no live logic changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Strict settled/suppressed/delta: `{summary.get('settled')}/{summary.get('suppressed')}/{fmt(summary.get('delta_vs_current_cents'))}c`",
        f"- Strict blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(["", "## Diagnostic Comparison", ""])
    write_policy_table(lines, (report.get("diagnostic") or {}).get("policies") or [])
    lines.extend(["", "## Strict Post-Freeze Comparison", ""])
    write_policy_table(lines, (report.get("strict_post_freeze") or {}).get("policies") or [])
    best = (report.get("diagnostic") or {}).get("best") or {}
    lines.extend([
        "",
        "## Diagnostic Best Suppressed Rows",
        "",
        "| market | side | result | exit | p_hold | drawdown | current c | hold c | delta c | won |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in best.get("suppressed_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('result')}` | "
            f"{fmt(row.get('exit_cents'))} | {fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('delta_cents'))} | {row.get('side_won')} |"
        )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
