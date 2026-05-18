"""Mid-price boundary size overlay crossed with guarded exit candidates.

Research-only; no live bot changes or orders.

This probe tests whether the strongest broad-entry size overlay actually
overlaps the frozen guarded-exit evidence. It applies each entry row's size
weight to the matched exit-policy PnL so the stack is scored as a notional
overlay rather than as an unweighted row filter.
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
STATE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_state.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.md"

EXIT_SOURCES = {
    "book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "loss_guard_v1": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
}

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
        "candidate_family": "soft_frontier_midprice_boundary_exit_stack",
        "entry_parent": "v28_soft_frontier_midprice_boundary_shrink",
        "exit_parent": "frozen book-gap/loss-guard exit watches",
        "physics": (
            "Entry shrink handles near-boundary mid-price rows by reducing notional instead of cutting coverage. "
            "Guarded exits test whether remaining losses are exit-clipping errors rather than entry-selection errors."
        ),
        "strict_forward_note": (
            "This stack is frozen from its own timestamp. Current rows are overlap diagnostics unless they occur "
            "after this freeze with enough matched exit observations."
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


def exit_rows(source_path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    payload = load_json(source_path)
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        grouped[(market(row), side(row))].append(row)
    return grouped


def exit_freeze_ts(source_path: Path) -> str | None:
    payload = load_json(source_path)
    freeze = payload.get("freeze") if isinstance(payload.get("freeze"), dict) else {}
    return freeze.get("freeze_ts_utc")


def current_cents(row: dict[str, Any]) -> float:
    return float(row.get("current_cents") or row.get("current_net_cents") or 0.0)


def candidate_cents(row: dict[str, Any]) -> float:
    return float(row.get("candidate_cents") or row.get("candidate_net_cents") or 0.0)


def exit_reason(row: dict[str, Any]) -> str:
    return str(row.get("exit_reason") or "held_to_settlement_no_exit")


def is_at_or_after(ts_value: Any, freeze_ts: str) -> bool:
    ts = parse_ts(ts_value)
    freeze = parse_ts(freeze_ts)
    if ts is None or freeze is None:
        return False
    return ts >= freeze


def latest_exit(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not matches:
        return None
    return sorted(matches, key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))[-1]


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def evaluate_variant(
    lane: dict[str, Any],
    variant: dict[str, Any],
    exit_source: str,
    exits: dict[tuple[str, str], list[dict[str, Any]]],
    stack_freeze_ts: str,
    exit_source_freeze_ts: str | None,
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
        candidate = candidate_cents(exit_row)
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
            "exit_reason": exit_reason(exit_row),
            "suppressed": exit_row.get("suppressed"),
            "midprice_boundary_band": bool(row.get("midprice_boundary_band")),
        })

    entry_net = as_float(summary.get("net_cents")) or 0.0
    joined_current = sum(row["weighted_exit_current_cents"] for row in joined)
    joined_candidate = sum(row["weighted_exit_candidate_cents"] for row in joined)
    joined_delta = joined_candidate - joined_current
    post_stack_joined = [
        row for row in joined
        if is_at_or_after(row.get("entry_ts") or row.get("exit_ts"), stack_freeze_ts)
    ]
    post_stack_candidate = sum(row["weighted_exit_candidate_cents"] for row in post_stack_joined)
    post_stack_current = sum(row["weighted_exit_current_cents"] for row in post_stack_joined)
    post_stack_delta = post_stack_candidate - post_stack_current
    share = reconstructed_share([row for row in rows if isinstance(row, dict)])
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
    if post_stack_candidate <= 0.0:
        blockers.append("post_stack_weighted_exit_net_not_positive")
    if full_loss_cushion(post_stack_candidate) < MIN_FULL_LOSS_CUSHION:
        blockers.append("post_stack_weighted_exit_full_loss_cushion_lt_3")
    return {
        "lane": lane.get("lane"),
        "strict_forward": bool(lane.get("strict_forward")),
        "exit_source": exit_source,
        "exit_source_freeze_ts_utc": exit_source_freeze_ts,
        "stack_freeze_ts_utc": stack_freeze_ts,
        "policy": variant.get("candidate"),
        "candidate": f"{variant.get('candidate')}_{exit_source}_weighted_exit_stack",
        "entry_summary": {key: value for key, value in summary.items() if key != "rows"},
        "source_counts": source_counts([row for row in rows if isinstance(row, dict)]),
        "reconstructed_share": share,
        "joined_exit_rows": len(joined),
        "unmatched_entry_rows": unmatched,
        "ambiguous_join_rows": ambiguous,
        "weighted_joined_exit_current_cents": joined_current,
        "weighted_joined_exit_candidate_cents": joined_candidate,
        "weighted_joined_exit_delta_cents": joined_delta,
        "weighted_joined_exit_full_loss_cushion": full_loss_cushion(joined_candidate),
        "post_stack_joined_exit_rows": len(post_stack_joined),
        "post_stack_weighted_exit_current_cents": post_stack_current,
        "post_stack_weighted_exit_candidate_cents": post_stack_candidate,
        "post_stack_weighted_exit_delta_cents": post_stack_delta,
        "post_stack_weighted_exit_full_loss_cushion": full_loss_cushion(post_stack_candidate),
        "midprice_boundary_joined_rows": sum(1 for row in joined if row.get("midprice_boundary_band")),
        "joined_rows": joined,
        "post_stack_joined_rows": post_stack_joined,
        "blockers": blockers,
        "live_ready": not blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    stack_freeze_ts = str(state["freeze_ts_utc"])
    midprice = load_json(MIDPRICE_JSON)
    variants: list[dict[str, Any]] = []
    for exit_source, path in EXIT_SOURCES.items():
        exits = exit_rows(path)
        exit_ts = exit_freeze_ts(path)
        for lane in midprice.get("lanes") or []:
            if not isinstance(lane, dict):
                continue
            for variant in lane.get("variants") or []:
                if isinstance(variant, dict):
                    variants.append(evaluate_variant(lane, variant, exit_source, exits, stack_freeze_ts, exit_ts))
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
        "midprice_source_freeze_ts_utc": (midprice.get("state") or {}).get("freeze_ts_utc"),
        "exit_sources": {name: str(path) for name, path in EXIT_SOURCES.items()},
        "variants": variants,
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in variants),
        "interpretation": interpretation(variants),
    }


def interpretation(variants: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is an overlap/denominator audit for a newly frozen stack; it is not a live-trading promotion artifact.",
        "Entry weights are applied to exit PnL, so quarter-sized boundary rows contribute quarter-sized exit exposure.",
    ]
    if variants:
        best = variants[0]
        summary = best.get("entry_summary") or {}
        notes.append(
            f"Best overlap row {best.get('candidate')} has entry settled {summary.get('settled')}, "
            f"entry coverage {summary.get('coverage_pct')}%, entry net {summary.get('net_cents')}c, "
            f"joined exit rows {best.get('joined_exit_rows')}, weighted joined exit net "
            f"{best.get('weighted_joined_exit_candidate_cents')}c, delta "
            f"{best.get('weighted_joined_exit_delta_cents')}c, post-stack joined rows "
            f"{best.get('post_stack_joined_exit_rows')}, blockers {best.get('blockers')}."
        )
        strict = [row for row in variants if row.get("strict_forward")]
        if strict:
            top_strict = strict[0]
            strict_summary = top_strict.get("entry_summary") or {}
            notes.append(
                f"Best strict entry-lane overlap {top_strict.get('candidate')} has "
                f"{strict_summary.get('settled')} settled, {top_strict.get('joined_exit_rows')} diagnostic joined exits, "
                f"and {top_strict.get('post_stack_joined_exit_rows')} post-stack joined exits; "
                f"blockers {top_strict.get('blockers')}."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Soft-Frontier Mid-Price Boundary + Guarded Exit Stack",
        "",
        "Research-only frozen overlap audit. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack freeze UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Mid-price parent freeze UTC: `{report.get('midprice_source_freeze_ts_utc')}`",
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
        "| rank | lane | policy | exit | strict | entry settled | W/L | coverage | entry net | recon | joined exits | post-stack joined | weighted exit net | post-stack net | weighted delta | post-stack delta | blockers |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate((report.get("variants") or [])[:40], start=1):
        summary = row.get("entry_summary") or {}
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('policy')}` | `{row.get('exit_source')}` | "
            f"{row.get('strict_forward')} | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('joined_exit_rows')} | "
            f"{row.get('post_stack_joined_exit_rows')} | "
            f"{fmt(row.get('weighted_joined_exit_candidate_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_exit_candidate_cents'))} | "
            f"{fmt(row.get('weighted_joined_exit_delta_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_exit_delta_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
