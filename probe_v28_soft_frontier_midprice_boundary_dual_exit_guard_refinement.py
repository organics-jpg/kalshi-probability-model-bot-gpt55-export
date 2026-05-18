"""Guard refinements for the mid-price boundary dual-exit stack.

Research-only; no live bot changes or orders.

The first dual stack found a strong book-gap/clip union but one diagnostic
suppressed loser. This probe tests observable guard variants that might remove
that failure mode without using settlement outcome:
- do not suppress rows already downweighted by the mid-price boundary overlay
- require stronger p_hold for probability_reduce suppressions
- combine both guards
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
BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
STATE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_state.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.md"

EXIT_REASONS = {"mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"}
P_HOLD_FLOOR = 0.60
FAIR_DRAWDOWN_CEILING = 10.0
MIN_SETTLED = 30
MIN_JOINED = 30
TARGET_COVERAGE_MIN = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

GUARDS = {
    "or_base": {"reduce_p_hold_floor": 0.60, "allow_midprice_boundary_suppress": True},
    "or_no_midprice_boundary_suppress": {"reduce_p_hold_floor": 0.60, "allow_midprice_boundary_suppress": False},
    "or_reduce_p_hold80": {"reduce_p_hold_floor": 0.80, "allow_midprice_boundary_suppress": True},
    "or_reduce_p_hold80_no_midprice_boundary": {"reduce_p_hold_floor": 0.80, "allow_midprice_boundary_suppress": False},
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
        "candidate_family": "soft_frontier_midprice_boundary_dual_exit_guard_refinement",
        "parent": "v28_soft_frontier_midprice_boundary_dual_exit_stack",
        "strict_forward_note": "Guard variants are frozen from this timestamp; diagnostic rows are mechanism evidence only.",
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


def grouped_rows(path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    payload = load_json(path)
    for row in payload.get("rows") or []:
        if isinstance(row, dict):
            grouped[(market(row), side(row))].append(row)
    return grouped


def latest(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not matches:
        return None
    return sorted(matches, key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))[-1]


def current(row: dict[str, Any] | None) -> float:
    return float((row or {}).get("current_cents") or 0.0)


def hold(row: dict[str, Any] | None) -> float:
    return float((row or {}).get("hold_cents") or (row or {}).get("candidate_cents") or 0.0)


def p_hold(row: dict[str, Any] | None) -> float | None:
    return as_float((row or {}).get("p_hold"))


def exit_reason(row: dict[str, Any] | None) -> str:
    return str((row or {}).get("exit_reason") or "")


def book_gap_signal(row: dict[str, Any] | None) -> bool:
    return bool(row and row.get("suppressed"))


def clip_signal(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    drawdown = as_float(row.get("fair_drawdown_cents"))
    p = p_hold(row)
    return (
        exit_reason(row) in EXIT_REASONS
        and p is not None
        and drawdown is not None
        and p >= P_HOLD_FLOOR
        and drawdown <= FAIR_DRAWDOWN_CEILING
    )


def guarded_suppress(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any], guard: dict[str, Any]) -> bool:
    base = reduce or book
    suppress = book_gap_signal(book) or clip_signal(base)
    if not suppress:
        return False
    if not guard["allow_midprice_boundary_suppress"] and bool(entry.get("midprice_boundary_band")):
        return False
    if exit_reason(base) == "mushroom_v28_probability_reduce":
        p = p_hold(base)
        if p is None or p < float(guard["reduce_p_hold_floor"]):
            return False
    return True


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def evaluate_variant(
    lane: dict[str, Any],
    variant: dict[str, Any],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    guard_name: str,
    guard: dict[str, Any],
    freeze_ts: str,
) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    entry_rows = [row for row in (summary.get("rows") or []) if isinstance(row, dict)]
    joined: list[dict[str, Any]] = []
    for row in entry_rows:
        key = (market(row), side(row))
        book = latest(book_rows.get(key) or [])
        reduce = latest(reduce_rows.get(key) or [])
        base = reduce or book
        if base is None:
            continue
        weight = as_float(row.get("weight"))
        if weight is None:
            weight = 1.0
        suppress = guarded_suppress(book, reduce, row, guard)
        base_current = current(base)
        candidate = hold(base) if suppress else base_current
        joined.append({
            "market": market(row),
            "side": side(row),
            "source": source(row),
            "entry_ts": base.get("entry_ts"),
            "exit_ts": base.get("exit_ts"),
            "exit_reason": exit_reason(base),
            "midprice_boundary_band": bool(row.get("midprice_boundary_band")),
            "p_hold": p_hold(base),
            "fair_drawdown_cents": as_float(base.get("fair_drawdown_cents")),
            "book_gap_signal": book_gap_signal(book),
            "clip_signal": clip_signal(base),
            "suppressed": suppress,
            "weight": weight,
            "weighted_current_cents": weight * base_current,
            "weighted_candidate_cents": weight * candidate,
            "weighted_delta_cents": weight * (candidate - base_current),
        })
    current_net = sum(row["weighted_current_cents"] for row in joined)
    candidate_net = sum(row["weighted_candidate_cents"] for row in joined)
    post_rows = [row for row in joined if is_at_or_after(row.get("entry_ts") or row.get("exit_ts"), freeze_ts)]
    post_candidate = sum(row["weighted_candidate_cents"] for row in post_rows)
    suppressed = [row for row in joined if row.get("suppressed")]
    suppressed_losers = [row for row in suppressed if row["weighted_candidate_cents"] < row["weighted_current_cents"]]
    post_suppressed = [row for row in post_rows if row.get("suppressed")]
    share = reconstructed_share(entry_rows)
    entry_net = as_float(summary.get("net_cents")) or 0.0
    coverage = as_float(summary.get("coverage_pct"))
    blockers: list[str] = []
    if not bool(lane.get("strict_forward")):
        blockers.append("entry_lane_not_strict_combo_forward")
    if as_int(summary.get("settled")) < MIN_SETTLED:
        blockers.append("entry_settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("entry_coverage_too_low")
    if entry_net <= 0:
        blockers.append("entry_net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("entry_reconstructed_share_gt_35pct")
    if full_loss_cushion(entry_net) < MIN_FULL_LOSS_CUSHION:
        blockers.append("entry_full_loss_cushion_lt_3")
    if len(post_rows) < MIN_JOINED:
        blockers.append("post_stack_joined_exit_rows_lt_30")
    if len(post_suppressed) < MIN_JOINED:
        blockers.append("post_stack_suppressed_decisions_lt_30")
    if post_candidate <= 0:
        blockers.append("post_stack_weighted_exit_net_not_positive")
    if suppressed_losers:
        blockers.append("diagnostic_suppressed_losers_present")
    if full_loss_cushion(post_candidate) < MIN_FULL_LOSS_CUSHION:
        blockers.append("post_stack_weighted_exit_full_loss_cushion_lt_3")
    return {
        "lane": lane.get("lane"),
        "strict_forward": bool(lane.get("strict_forward")),
        "guard": guard_name,
        "policy": f"{variant.get('candidate')}_{guard_name}",
        "entry_summary": {key: value for key, value in summary.items() if key != "rows"},
        "source_counts": source_counts(entry_rows),
        "reconstructed_share": share,
        "joined_exit_rows": len(joined),
        "suppressed_rows": len(suppressed),
        "suppressed_losers": len(suppressed_losers),
        "weighted_current_cents": current_net,
        "weighted_candidate_cents": candidate_net,
        "weighted_delta_cents": candidate_net - current_net,
        "post_stack_joined_rows": len(post_rows),
        "post_stack_suppressed_rows": len(post_suppressed),
        "post_stack_weighted_candidate_cents": post_candidate,
        "blockers": blockers,
        "live_ready": not blockers,
        "joined_rows": joined,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    midprice = load_json(MIDPRICE_JSON)
    book = grouped_rows(BOOK_GAP_JSON)
    reduce = grouped_rows(REDUCE_JSON)
    variants: list[dict[str, Any]] = []
    for lane in midprice.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            for guard_name, guard in GUARDS.items():
                variants.append(evaluate_variant(lane, variant, book, reduce, guard_name, guard, freeze_ts))
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            int(row.get("suppressed_losers") or 0),
            -float(row.get("weighted_candidate_cents") or -999999),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "guards": GUARDS,
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in variants),
        "variants": variants,
        "interpretation": interpretation(variants),
    }


def interpretation(variants: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This freezes observable guard refinements for the broad dual-exit stack.",
        "Rows before the guard freeze are diagnostic only; no live-readiness can come from them.",
    ]
    if variants:
        best = variants[0]
        summary = best.get("entry_summary") or {}
        notes.append(
            f"Best guard {best.get('policy')} has entry settled {summary.get('settled')}, coverage "
            f"{summary.get('coverage_pct')}%, joined {best.get('joined_exit_rows')}, suppressions "
            f"{best.get('suppressed_rows')}, suppressed losers {best.get('suppressed_losers')}, net "
            f"{best.get('weighted_candidate_cents')}c, delta {best.get('weighted_delta_cents')}c, blockers "
            f"{best.get('blockers')}."
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
        "# v28 Soft-Frontier Mid-Price Boundary Dual-Exit Guard Refinement",
        "",
        "Research-only frozen guard audit. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Guard freeze UTC: `{freeze.get('freeze_ts_utc')}`",
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
        "| rank | lane | policy | guard | strict | entry settled | W/L | coverage | recon | joined | suppress | suppress losers | post joined | post suppress | weighted net | weighted delta | blockers |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate((report.get("variants") or [])[:60], start=1):
        summary = row.get("entry_summary") or {}
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('policy')}` | `{row.get('guard')}` | "
            f"{row.get('strict_forward')} | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('joined_exit_rows')} | {row.get('suppressed_rows')} | {row.get('suppressed_losers')} | "
            f"{row.get('post_stack_joined_rows')} | {row.get('post_stack_suppressed_rows')} | "
            f"{fmt(row.get('weighted_candidate_cents'))} | {fmt(row.get('weighted_delta_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
