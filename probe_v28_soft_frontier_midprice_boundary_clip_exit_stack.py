"""Mid-price boundary size overlay crossed with the exit-clip separator.

Research-only; no live bot changes or orders.

This is the creative mix/match lane: use the broad mid-price boundary size
overlay for entries, then replay the observable clip separator on matched
exit-reduce rows. It tests whether the top broad-entry shape and the top
loss-churn exit separator are additive or just reusing the same historical luck.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDPRICE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
EXIT_REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_clip_exit_stack_state.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_clip_exit_stack_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_clip_exit_stack_latest.md"

EXIT_REASONS = {"mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"}
P_HOLD_FLOOR = 0.60
FAIR_DRAWDOWN_CEILING = 10.0
MIN_SETTLED = 30
MIN_JOINED_EXIT_ROWS = 30
TARGET_COVERAGE_MIN = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


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
        "candidate_family": "soft_frontier_midprice_boundary_clip_exit_stack",
        "entry_parent": "v28_soft_frontier_midprice_boundary_shrink",
        "exit_parent": "v28_exit_clip_separator_replay",
        "rule": (
            "Suppress probability-reduce/collapse-full exits only when p_hold>=0.60 and "
            "fair_drawdown_cents<=10; apply entry size weights to exit PnL."
        ),
        "strict_forward_note": (
            "Rows before this stack freeze are diagnostic only. Post-stack rows must satisfy "
            "sample, source, cushion, and loss-control gates before any live use."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


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


def is_at_or_after(ts_value: Any, freeze_ts: str) -> bool:
    ts = parse_ts(ts_value)
    freeze = parse_ts(freeze_ts)
    return bool(ts and freeze and ts >= freeze)


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    counts = source_counts(rows)
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def grouped_exit_rows() -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    payload = load_json(EXIT_REDUCE_JSON)
    for row in payload.get("rows") or []:
        if isinstance(row, dict):
            grouped[(market(row), side(row))].append(row)
    return grouped


def latest_exit(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not matches:
        return None
    return sorted(matches, key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))[-1]


def should_clip_suppress(row: dict[str, Any]) -> bool:
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    return (
        str(row.get("exit_reason") or "") in EXIT_REASONS
        and p_hold is not None
        and drawdown is not None
        and p_hold >= P_HOLD_FLOOR
        and drawdown <= FAIR_DRAWDOWN_CEILING
    )


def current_cents(row: dict[str, Any]) -> float:
    return float(row.get("current_cents") or 0.0)


def hold_cents(row: dict[str, Any]) -> float:
    return float(row.get("hold_cents") or row.get("candidate_cents") or 0.0)


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def evaluate_variant(
    lane: dict[str, Any],
    variant: dict[str, Any],
    exits: dict[tuple[str, str], list[dict[str, Any]]],
    stack_freeze_ts: str,
) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    rows = summary.get("rows") if isinstance(summary.get("rows"), list) else []
    joined: list[dict[str, Any]] = []
    unmatched = 0
    ambiguous = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        matches = exits.get((market(row), side(row))) or []
        entry_ts_set = {item.get("entry_ts") for item in matches if item.get("entry_ts")}
        if len(entry_ts_set) > 1:
            ambiguous += 1
        exit_row = latest_exit(matches)
        if exit_row is None:
            unmatched += 1
            continue
        weight = as_float(row.get("weight"))
        if weight is None:
            weight = 1.0
        current = current_cents(exit_row)
        clipped = should_clip_suppress(exit_row)
        candidate = hold_cents(exit_row) if clipped else current
        joined.append({
            "market": market(row),
            "side": side(row),
            "source": source(row),
            "weight": weight,
            "entry_weighted_net_cents": as_float(row.get("weighted_net_cents")) or 0.0,
            "exit_current_cents": current,
            "exit_candidate_cents": candidate,
            "weighted_exit_current_cents": weight * current,
            "weighted_exit_candidate_cents": weight * candidate,
            "weighted_exit_delta_cents": weight * (candidate - current),
            "entry_ts": exit_row.get("entry_ts"),
            "exit_ts": exit_row.get("exit_ts"),
            "exit_reason": exit_row.get("exit_reason"),
            "clip_suppressed": clipped,
            "p_hold": exit_row.get("p_hold"),
            "fair_drawdown_cents": exit_row.get("fair_drawdown_cents"),
            "midprice_boundary_band": bool(row.get("midprice_boundary_band")),
        })

    entry_rows = [row for row in rows if isinstance(row, dict)]
    entry_net = as_float(summary.get("net_cents")) or 0.0
    joined_current = sum(row["weighted_exit_current_cents"] for row in joined)
    joined_candidate = sum(row["weighted_exit_candidate_cents"] for row in joined)
    post_stack_joined = [
        row for row in joined
        if is_at_or_after(row.get("entry_ts") or row.get("exit_ts"), stack_freeze_ts)
    ]
    post_stack_candidate = sum(row["weighted_exit_candidate_cents"] for row in post_stack_joined)
    post_stack_current = sum(row["weighted_exit_current_cents"] for row in post_stack_joined)
    suppressed = [row for row in joined if row.get("clip_suppressed")]
    suppressed_losers = [row for row in suppressed if row["weighted_exit_candidate_cents"] < row["weighted_exit_current_cents"]]
    post_suppressed = [row for row in post_stack_joined if row.get("clip_suppressed")]
    share = reconstructed_share(entry_rows)
    settled = as_int(summary.get("settled"))
    coverage = as_float(summary.get("coverage_pct"))
    blockers: list[str] = []
    if not bool(lane.get("strict_forward")):
        blockers.append("entry_lane_not_strict_combo_forward")
    if settled < MIN_SETTLED:
        blockers.append("entry_settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("entry_coverage_too_low")
    if entry_net <= 0.0:
        blockers.append("entry_net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("entry_reconstructed_share_gt_35pct")
    if full_loss_cushion(entry_net) < MIN_FULL_LOSS_CUSHION:
        blockers.append("entry_full_loss_cushion_lt_3")
    if len(post_stack_joined) < MIN_JOINED_EXIT_ROWS:
        blockers.append("post_stack_joined_exit_rows_lt_30")
    if len(post_suppressed) < MIN_JOINED_EXIT_ROWS:
        blockers.append("post_stack_clip_decisions_lt_30")
    if post_stack_candidate <= 0.0:
        blockers.append("post_stack_weighted_exit_net_not_positive")
    if suppressed_losers:
        blockers.append("diagnostic_suppressed_losers_present")
    if full_loss_cushion(post_stack_candidate) < MIN_FULL_LOSS_CUSHION:
        blockers.append("post_stack_weighted_exit_full_loss_cushion_lt_3")
    return {
        "lane": lane.get("lane"),
        "strict_forward": bool(lane.get("strict_forward")),
        "stack_freeze_ts_utc": stack_freeze_ts,
        "policy": variant.get("candidate"),
        "candidate": f"{variant.get('candidate')}_clip_separator_weighted_exit_stack",
        "entry_summary": {key: value for key, value in summary.items() if key != "rows"},
        "source_counts": source_counts(entry_rows),
        "reconstructed_share": share,
        "joined_exit_rows": len(joined),
        "unmatched_entry_rows": unmatched,
        "ambiguous_join_rows": ambiguous,
        "clip_suppressed_rows": len(suppressed),
        "clip_suppressed_losers": len(suppressed_losers),
        "weighted_joined_exit_current_cents": joined_current,
        "weighted_joined_exit_candidate_cents": joined_candidate,
        "weighted_joined_exit_delta_cents": joined_candidate - joined_current,
        "weighted_joined_exit_full_loss_cushion": full_loss_cushion(joined_candidate),
        "post_stack_joined_exit_rows": len(post_stack_joined),
        "post_stack_clip_suppressed_rows": len(post_suppressed),
        "post_stack_weighted_exit_current_cents": post_stack_current,
        "post_stack_weighted_exit_candidate_cents": post_stack_candidate,
        "post_stack_weighted_exit_delta_cents": post_stack_candidate - post_stack_current,
        "post_stack_weighted_exit_full_loss_cushion": full_loss_cushion(post_stack_candidate),
        "joined_rows": joined,
        "post_stack_joined_rows": post_stack_joined,
        "blockers": blockers,
        "live_ready": not blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    stack_freeze_ts = str(state["freeze_ts_utc"])
    midprice = load_json(MIDPRICE_JSON)
    exits = grouped_exit_rows()
    variants: list[dict[str, Any]] = []
    for lane in midprice.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                variants.append(evaluate_variant(lane, variant, exits, stack_freeze_ts))
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_joined_exit_candidate_cents") or -999999.0),
            -float((row.get("entry_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "midprice_source_generated_at_utc": midprice.get("generated_at_utc"),
        "source": {
            "midprice": str(MIDPRICE_JSON),
            "exit_reduce": str(EXIT_REDUCE_JSON),
        },
        "rule": {
            "exit_reasons": sorted(EXIT_REASONS),
            "p_hold_floor": P_HOLD_FLOOR,
            "fair_drawdown_cents_ceiling": FAIR_DRAWDOWN_CEILING,
        },
        "variants": variants,
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in variants),
        "interpretation": interpretation(variants),
    }


def interpretation(variants: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a newly frozen mix/match overlap audit; it is not live-trading evidence.",
        "Entry weights are applied to exit PnL, and the exit rule is observable p_hold/fair-drawdown only.",
    ]
    if variants:
        best = variants[0]
        summary = best.get("entry_summary") or {}
        notes.append(
            f"Best overlap {best.get('candidate')} has entry settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, entry net {summary.get('net_cents')}c, "
            f"joined exit rows {best.get('joined_exit_rows')}, clip suppressions "
            f"{best.get('clip_suppressed_rows')}, weighted joined exit net "
            f"{best.get('weighted_joined_exit_candidate_cents')}c, delta "
            f"{best.get('weighted_joined_exit_delta_cents')}c, post-stack rows "
            f"{best.get('post_stack_joined_exit_rows')}, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Soft-Frontier Mid-Price Boundary + Clip Exit Stack",
        "",
        "Research-only frozen overlap audit. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Any live-ready variant: `{report.get('candidate_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Variants",
        "",
        "| rank | lane | policy | strict | entry settled | W/L | coverage | entry net | recon | joined exits | clip suppress | suppress losers | post joined | post suppress | weighted exit net | post-stack net | weighted delta | post-stack delta | blockers |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate((report.get("variants") or [])[:40], start=1):
        summary = row.get("entry_summary") or {}
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('policy')}` | {row.get('strict_forward')} | "
            f"{summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('joined_exit_rows')} | "
            f"{row.get('clip_suppressed_rows')} | {row.get('clip_suppressed_losers')} | "
            f"{row.get('post_stack_joined_exit_rows')} | {row.get('post_stack_clip_suppressed_rows')} | "
            f"{fmt(row.get('weighted_joined_exit_candidate_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_exit_candidate_cents'))} | "
            f"{fmt(row.get('weighted_joined_exit_delta_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_exit_delta_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
