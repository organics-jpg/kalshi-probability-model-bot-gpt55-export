"""Frozen watch for mid-band probability-reduce exit clipping.

Research-only; no live bot changes or orders.

The existing p_hold>=0.75 reduce-suppression repairs many clipped winners but
also has loss-control cost. The matched-unchanged loss audit found a narrower
lower-p_hold band where current probability-reduce exits clipped positions that
would have settled better. This watch freezes observable variants and scores
only rows after this probe's own birth timestamp for promotion evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_midband_reduce_rescue_watch_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sign(value: float) -> str:
    if value > 0:
        return "win"
    if value < 0:
        return "loss"
    return "flat"


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "source": str(SOURCE_JSON),
        "candidates": [
            "midband_p60_75_exit50_75_asklt80",
            "midband_p60_75_exit50_75_asklt80_fairddgte0",
            "midband_p60_75_exit50_70_asklt80",
            "midband_p65_75_exit50_75_asklt80",
        ],
        "research_only": True,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def probability_reduce(row: dict[str, Any]) -> bool:
    return str(row.get("exit_reason") or "") == "mushroom_v28_probability_reduce"


def between(value: Any, low: float, high: float) -> bool:
    number = as_float(value)
    return number is not None and low <= number < high


def rule_midband(row: dict[str, Any]) -> bool:
    return (
        probability_reduce(row)
        and between(row.get("p_hold"), 0.60, 0.75)
        and between(row.get("exit_cents"), 50.0, 76.0)
        and (as_float(row.get("entry_cents")) or 999.0) < 80.0
    )


def rule_midband_fairdd_nonnegative(row: dict[str, Any]) -> bool:
    return rule_midband(row) and (as_float(row.get("fair_drawdown_cents")) or -999999.0) >= 0.0


def rule_midband_exit70(row: dict[str, Any]) -> bool:
    return (
        probability_reduce(row)
        and between(row.get("p_hold"), 0.60, 0.75)
        and between(row.get("exit_cents"), 50.0, 71.0)
        and (as_float(row.get("entry_cents")) or 999.0) < 80.0
    )


def rule_midband_p65(row: dict[str, Any]) -> bool:
    return (
        probability_reduce(row)
        and between(row.get("p_hold"), 0.65, 0.75)
        and between(row.get("exit_cents"), 50.0, 76.0)
        and (as_float(row.get("entry_cents")) or 999.0) < 80.0
    )


RULES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "midband_p60_75_exit50_75_asklt80": rule_midband,
    "midband_p60_75_exit50_75_asklt80_fairddgte0": rule_midband_fairdd_nonnegative,
    "midband_p60_75_exit50_70_asklt80": rule_midband_exit70,
    "midband_p65_75_exit50_75_asklt80": rule_midband_p65,
}


PHYSICS = {
    "midband_p60_75_exit50_75_asklt80": (
        "Lower-p_hold probability-reduce exits at non-rich entry prices may be microstructure "
        "churn that clips near-boundary positions before settlement information resolves."
    ),
    "midband_p60_75_exit50_75_asklt80_fairddgte0": (
        "Requires non-negative fair drawdown at exit, avoiding states where the fair-value path "
        "already says the position is below its entry value."
    ),
    "midband_p60_75_exit50_70_asklt80": (
        "Uses the same confidence and entry-price band but limits the observed reduce mark to "
        "50-70c, where clipped-winner rows were concentrated."
    ),
    "midband_p65_75_exit50_75_asklt80": (
        "Conservative p_hold band just below the existing 0.75 rule, avoiding lower-confidence "
        "collapses."
    ),
}


def score_rows(candidate: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    rule = RULES[candidate]
    scored = []
    suppressed = []
    for row in rows:
        current = as_float(row.get("current_cents"))
        hold = as_float(row.get("hold_cents"))
        if current is None or hold is None:
            continue
        would_suppress = bool(rule(row))
        candidate_cents = hold if would_suppress else current
        delta = candidate_cents - current
        scored_row = {
            "market": row.get("market"),
            "side": row.get("side"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "current_cents": current,
            "candidate_cents": candidate_cents,
            "delta_cents": delta,
            "would_suppress": would_suppress,
            "p_hold": row.get("p_hold"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "fair_drawdown_cents": row.get("fair_drawdown_cents"),
            "result": row.get("result"),
        }
        scored.append(scored_row)
        if would_suppress:
            suppressed.append(scored_row)
    current_values = [as_float(row.get("current_cents")) or 0.0 for row in scored]
    candidate_values = [as_float(row.get("candidate_cents")) or 0.0 for row in scored]
    suppressed_delta = sum(as_float(row.get("delta_cents")) or 0.0 for row in suppressed)
    helpful = [row for row in suppressed if (as_float(row.get("delta_cents")) or 0.0) > 0.0]
    harmful = [row for row in suppressed if (as_float(row.get("delta_cents")) or 0.0) < 0.0]
    current_losses = sum(1 for value in current_values if value < 0.0)
    candidate_losses = sum(1 for value in candidate_values if value < 0.0)
    loss_control_cost = sum(as_float(row.get("delta_cents")) or 0.0 for row in harmful)
    full_loss_cushion = int(max(0.0, suppressed_delta) // 100.0)
    blockers = []
    if len(scored) < 30:
        blockers.append("settled_lt_30")
    if len(suppressed) < 30:
        blockers.append("suppressed_decisions_lt_30")
    if suppressed_delta <= 0.0:
        blockers.append("delta_not_positive")
    if loss_control_cost < 0.0:
        blockers.append("loss_control_cost_negative")
    if full_loss_cushion < 3:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "candidate": candidate,
        "physics": PHYSICS[candidate],
        "rows": len(scored),
        "suppressed": len(suppressed),
        "current_net_cents": sum(current_values),
        "candidate_net_cents": sum(candidate_values),
        "delta_vs_current_cents": sum(candidate_values) - sum(current_values),
        "current_wl": f"{sum(1 for value in current_values if value > 0.0)}/{current_losses}",
        "candidate_wl": f"{sum(1 for value in candidate_values if value > 0.0)}/{candidate_losses}",
        "loss_count_reduction": current_losses - candidate_losses,
        "helpful_suppressions": len(helpful),
        "harmful_suppressions": len(harmful),
        "loss_control_cost_cents": loss_control_cost,
        "full_loss_cushion": full_loss_cushion,
        "blockers": blockers,
        "top_helpful": sorted(helpful, key=lambda row: as_float(row.get("delta_cents")) or 0.0, reverse=True)[:8],
        "top_harmful": sorted(harmful, key=lambda row: as_float(row.get("delta_cents")) or 0.0)[:8],
    }


def build_report() -> dict[str, Any]:
    state = ensure_state()
    source = load_json(SOURCE_JSON)
    rows = source.get("rows") or []
    if not isinstance(rows, list):
        rows = []
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    post_rows = [
        row for row in rows
        if freeze_ts is not None
        and (parse_ts(row.get("entry_ts") or row.get("exit_ts")) or datetime.min.replace(tzinfo=timezone.utc)) >= freeze_ts
    ]
    diagnostic = [score_rows(candidate, rows) for candidate in RULES]
    post = [score_rows(candidate, post_rows) for candidate in RULES]
    diagnostic.sort(key=lambda row: (as_float(row.get("delta_vs_current_cents")) or -99999.0), reverse=True)
    post.sort(key=lambda row: (as_float(row.get("delta_vs_current_cents")) or -99999.0), reverse=True)
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "source_freeze": source.get("freeze") or {},
        "diagnostic_rows": len(rows),
        "post_birth_rows": len(post_rows),
        "diagnostic": diagnostic,
        "post_birth": post,
        "interpretation": [
            "Research-only frozen watch; no live exits are changed.",
            "Diagnostic rows explain the mechanism only. Promotion evidence must come from post-birth rows after this watch freeze.",
            "The variants test lower-p_hold probability-reduce clips while avoiding rich-entry/high-p_hold states that caused current suppression harm.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Exit Midband Reduce Rescue Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Diagnostic source rows: `{report.get('diagnostic_rows')}`",
        f"- Post-birth rows: `{report.get('post_birth_rows')}`",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    for section, rows in [("Diagnostic", report.get("diagnostic") or []), ("Post Birth", report.get("post_birth") or [])]:
        lines.extend([
            "",
            f"## {section}",
            "",
            "| candidate | rows | suppressed | current c | candidate c | delta c | W/L -> candidate | loss delta | helpful/harmful | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|",
        ])
        for row in rows:
            lines.append(
                f"| {row.get('candidate')} | {row.get('rows')} | {row.get('suppressed')} | "
                f"{fmt(row.get('current_net_cents'))} | {fmt(row.get('candidate_net_cents'))} | "
                f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('current_wl')} -> {row.get('candidate_wl')} | "
                f"{row.get('loss_count_reduction')} | {row.get('helpful_suppressions')}/{row.get('harmful_suppressions')} | "
                f"{row.get('full_loss_cushion')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    best_diag = (report.get("diagnostic") or [{}])[0]
    if best_diag.get("top_helpful"):
        lines.extend([
            "",
            "## Top Diagnostic Helpful Suppressions",
            "",
            "| market | side | current c | hold c | delta c | p_hold | entry | exit |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best_diag.get("top_helpful") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('current_cents'))} | "
                f"{fmt(row.get('candidate_cents'))} | {fmt(row.get('delta_cents'))} | "
                f"{fmt(row.get('p_hold'))} | {row.get('entry_cents')} | {row.get('exit_cents')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
