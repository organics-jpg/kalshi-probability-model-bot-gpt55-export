"""Frozen watch for value-over-hold-only book-gap exit suppression.

Research-only; no live bot changes or orders.

The broad book-gap exit candidate is the top current PnL lane, but its
suppressed loss-control cost comes from probability_reduce rows. This freezes a
cleaner physical variant: only suppress value-over-hold exits when the held
side still has enough book/fair-value support. Probability-reduce exits remain
treated as a stronger state-warning class unless future evidence says
otherwise.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.md"

MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3

VARIANTS = {
    "value_only_gap15_or_p75": {
        "exit_reasons": {"mushroom_v28_exit_value_over_hold"},
        "gap_floor": 0.15,
        "p_hold_floor": 0.75,
    },
    "value_only_gap15_or_p79": {
        "exit_reasons": {"mushroom_v28_exit_value_over_hold"},
        "gap_floor": 0.15,
        "p_hold_floor": 0.79,
    },
    "value_only_gap15_only": {
        "exit_reasons": {"mushroom_v28_exit_value_over_hold"},
        "gap_floor": 0.15,
        "p_hold_floor": None,
    },
    "both_soft_reasons_gap15_or_p79": {
        "exit_reasons": {"mushroom_v28_exit_value_over_hold", "mushroom_v28_probability_reduce"},
        "gap_floor": 0.15,
        "p_hold_floor": 0.79,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "value_only_gap15_or_p75",
        "candidate_family": "exit_book_gap_value_only",
        "rule": (
            "Suppress only mushroom_v28_exit_value_over_hold when "
            "hold_book_gap >= 0.15 or p_hold >= 0.75; keep probability_reduce "
            "and probability_collapse_full exits unchanged."
        ),
        "physics": (
            "Value-over-hold exits can be spread/turbulence clipping while "
            "probability_reduce exits are a stronger state-warning class. The "
            "variant tries to keep winner recovery without inheriting the two "
            "observed catastrophic reduce-hold losses."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
        "source_artifact": str(SOURCE_JSON),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts") or row.get("entry_ts"))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cents(row: dict[str, Any], field: str) -> float:
    return float(as_float(row.get(field)) or 0.0)


def rows_after(rows: list[dict[str, Any]], freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    out = []
    for row in rows:
        ts = row_ts(row)
        if freeze_dt is not None and ts is not None and ts < freeze_dt:
            continue
        out.append(row)
    return out


def should_suppress(row: dict[str, Any], variant: dict[str, Any]) -> bool:
    if row.get("exit_reason") not in variant["exit_reasons"]:
        return False
    gap = as_float(row.get("hold_book_gap"))
    p_hold = as_float(row.get("p_hold"))
    gap_floor = as_float(variant.get("gap_floor"))
    p_floor = as_float(variant.get("p_hold_floor"))
    gap_pass = gap_floor is not None and gap is not None and gap >= gap_floor
    p_pass = p_floor is not None and p_hold is not None and p_hold >= p_floor
    return gap_pass or p_pass


def score_rows(rows: list[dict[str, Any]], variant_name: str, variant: dict[str, Any]) -> dict[str, Any]:
    scored = []
    for source_row in rows:
        row = dict(source_row)
        suppress = should_suppress(row, variant)
        candidate = cents(row, "hold_cents") if suppress else cents(row, "current_cents")
        current = cents(row, "current_cents")
        row["value_only_candidate_cents"] = candidate
        row["value_only_delta_cents"] = candidate - current
        row["value_only_suppressed"] = suppress
        scored.append(row)

    candidate_vals = [float(row["value_only_candidate_cents"]) for row in scored]
    current_vals = [cents(row, "current_cents") for row in scored]
    suppressed = [row for row in scored if row.get("value_only_suppressed")]
    suppressed_winners = [
        row for row in suppressed
        if str(row.get("side") or "").lower() == str(row.get("result") or "").lower()
    ]
    suppressed_losers = [row for row in suppressed if row not in suppressed_winners]
    recovery = sum(float(row["value_only_delta_cents"]) for row in suppressed_winners)
    loss_cost = sum(float(row["value_only_delta_cents"]) for row in suppressed_losers)
    net = sum(candidate_vals)
    summary = {
        "variant": variant_name,
        "rows": len(scored),
        "settled": len(candidate_vals),
        "current_gross_cents": sum(current_vals),
        "candidate_gross_cents": net,
        "delta_vs_current_cents": net - sum(current_vals),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "suppressed_exits": len(suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "winner_clip_recovered_cents": recovery,
        "loss_control_cost_cents": loss_cost,
        "full_loss_cushion_estimate": int(net // 100.0) if net > 0.0 else 0,
    }
    blockers = []
    if int(summary["settled"]) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if float(summary["delta_vs_current_cents"]) <= 0.0:
        blockers.append("delta_not_positive")
    if float(summary["candidate_gross_cents"]) <= 0.0:
        blockers.append("net_not_positive")
    if int(summary["suppressed_losers"]) > 0:
        blockers.append("suppressed_losers_present")
    if float(summary["loss_control_cost_cents"]) < 0.0:
        blockers.append("suppressed_loss_control_cost_negative")
    if int(summary["full_loss_cushion_estimate"]) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "variant": variant_name,
        "rule": {
            "exit_reasons": sorted(variant["exit_reasons"]),
            "gap_floor": variant.get("gap_floor"),
            "p_hold_floor": variant.get("p_hold_floor"),
        },
        "summary": summary,
        "rows": scored,
        "blockers": blockers,
        "live_ready": not blockers,
    }


def evaluate_lane(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    variants = [score_rows(rows, name, variant) for name, variant in VARIANTS.items()]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("candidate_gross_cents") or -999999.0),
        )
    )
    return {"lane": label, "variants": variants}


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    source = load_json(SOURCE_JSON)
    source_rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    source_freeze_ts = str((source.get("freeze") or {}).get("freeze_ts_utc") or state["freeze_ts_utc"])
    diagnostic = evaluate_lane("diagnostic_from_book_gap_freeze", rows_after(source_rows, source_freeze_ts))
    post_birth = evaluate_lane("post_value_only_birth", rows_after(source_rows, str(state["freeze_ts_utc"])))
    primary = next(
        (
            row for row in post_birth["variants"]
            if row.get("variant") == state.get("candidate")
        ),
        post_birth["variants"][0] if post_birth["variants"] else {},
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "source_freeze_ts_utc": source_freeze_ts,
        "lanes": [diagnostic, post_birth],
        "summary": primary.get("summary") or {},
        "blockers": primary.get("blockers") or [],
        "candidate_live_ready": bool(primary.get("live_ready")),
        "interpretation": interpretation([diagnostic, post_birth]),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a frozen watch; diagnostic rows motivate the freeze but do not promote it.",
        "Probability-reduce exits stay unchanged in the primary value-only rule.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('variant')} settled {summary.get('settled')}, "
            f"net {summary.get('candidate_gross_cents')}c, delta {summary.get('delta_vs_current_cents')}c, "
            f"suppressed W/L {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')}, "
            f"loss cost {summary.get('loss_control_cost_cents')}c, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Exit Book-Gap Value-Only",
        "",
        "Research-only frozen forward watch. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Any live-ready primary: `{report.get('candidate_live_ready')}`",
        f"- Primary blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            "| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | suppressed W/L | recovery c | loss cost c | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("summary") or {}
            lines.append(
                f"| {idx} | `{row.get('variant')}` | {summary.get('settled')} | "
                f"{summary.get('candidate_wins')}/{summary.get('candidate_losses')} | "
                f"{fmt(summary.get('current_gross_cents'))} | {fmt(summary.get('candidate_gross_cents'))} | "
                f"{fmt(summary.get('delta_vs_current_cents'))} | {summary.get('suppressed_exits')} | "
                f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                f"{fmt(summary.get('winner_clip_recovered_cents'))} | {fmt(summary.get('loss_control_cost_cents'))} | "
                f"{summary.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
