"""Mid-price boundary size overlay crossed with book-gap and clip exits.

Research-only; no live bot changes or orders.

This probe compares observable exit-combination policies on the same broad
mid-price boundary entry rows:
- book_gap_only: existing frozen soft book-gap rule
- clip_only: fair-drawdown/p_hold clip separator
- book_gap_or_clip: suppress if either observable repair fires
- book_gap_and_clip: suppress only when both repairs agree
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
STATE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_state.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_stack_latest.md"

EXIT_REASONS = {"mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"}
P_HOLD_FLOOR = 0.60
FAIR_DRAWDOWN_CEILING = 10.0
TARGET_COVERAGE_MIN = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_JOINED = 30
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
        "candidate_family": "soft_frontier_midprice_boundary_dual_exit_stack",
        "entry_parent": "v28_soft_frontier_midprice_boundary_shrink",
        "exit_parents": ["v28_frozen_exit_book_gap_suppression", "v28_exit_clip_separator_replay"],
        "strict_forward_note": "Diagnostic overlap rows are not promotion evidence; post-freeze rows must fill first.",
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
    if not row:
        return 0.0
    return float(row.get("current_cents") or 0.0)


def hold(row: dict[str, Any] | None) -> float:
    if not row:
        return 0.0
    return float(row.get("hold_cents") or row.get("candidate_cents") or 0.0)


def book_gap_signal(row: dict[str, Any] | None) -> bool:
    return bool(row and row.get("suppressed"))


def clip_signal(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    p_hold = as_float(row.get("p_hold"))
    drawdown = as_float(row.get("fair_drawdown_cents"))
    return (
        str(row.get("exit_reason") or "") in EXIT_REASONS
        and p_hold is not None
        and drawdown is not None
        and p_hold >= P_HOLD_FLOOR
        and drawdown <= FAIR_DRAWDOWN_CEILING
    )


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def policy_suppresses(policy: str, book_signal: bool, clip: bool) -> bool:
    if policy == "book_gap_only":
        return book_signal
    if policy == "clip_only":
        return clip
    if policy == "book_gap_or_clip":
        return book_signal or clip
    if policy == "book_gap_and_clip":
        return book_signal and clip
    raise ValueError(policy)


def evaluate_variant(
    lane: dict[str, Any],
    variant: dict[str, Any],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    policy: str,
    freeze_ts: str,
) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    entry_rows = [row for row in (summary.get("rows") or []) if isinstance(row, dict)]
    joined: list[dict[str, Any]] = []
    unmatched = 0
    for row in entry_rows:
        key = (market(row), side(row))
        book = latest(book_rows.get(key) or [])
        reduce = latest(reduce_rows.get(key) or [])
        base = reduce or book
        if base is None:
            unmatched += 1
            continue
        weight = as_float(row.get("weight"))
        if weight is None:
            weight = 1.0
        book_sig = book_gap_signal(book)
        clip_sig = clip_signal(reduce or book)
        suppress = policy_suppresses(policy, book_sig, clip_sig)
        candidate = hold(base) if suppress else current(base)
        base_current = current(base)
        joined.append({
            "market": market(row),
            "side": side(row),
            "source": source(row),
            "weight": weight,
            "entry_ts": base.get("entry_ts"),
            "exit_ts": base.get("exit_ts"),
            "exit_reason": base.get("exit_reason"),
            "book_gap_signal": book_sig,
            "clip_signal": clip_sig,
            "suppressed": suppress,
            "weighted_current_cents": weight * base_current,
            "weighted_candidate_cents": weight * candidate,
            "weighted_delta_cents": weight * (candidate - base_current),
            "candidate_cents": candidate,
            "current_cents": base_current,
        })

    entry_net = as_float(summary.get("net_cents")) or 0.0
    candidate_net = sum(row["weighted_candidate_cents"] for row in joined)
    current_net = sum(row["weighted_current_cents"] for row in joined)
    post_rows = [row for row in joined if is_at_or_after(row.get("entry_ts") or row.get("exit_ts"), freeze_ts)]
    post_candidate = sum(row["weighted_candidate_cents"] for row in post_rows)
    suppressed = [row for row in joined if row.get("suppressed")]
    suppressed_losers = [row for row in suppressed if row["weighted_candidate_cents"] < row["weighted_current_cents"]]
    post_suppressed = [row for row in post_rows if row.get("suppressed")]
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
        "policy": f"{variant.get('candidate')}_{policy}",
        "exit_policy": policy,
        "entry_summary": {key: value for key, value in summary.items() if key != "rows"},
        "source_counts": source_counts(entry_rows),
        "reconstructed_share": share,
        "joined_exit_rows": len(joined),
        "unmatched_entry_rows": unmatched,
        "suppressed_rows": len(suppressed),
        "suppressed_losers": len(suppressed_losers),
        "weighted_current_cents": current_net,
        "weighted_candidate_cents": candidate_net,
        "weighted_delta_cents": candidate_net - current_net,
        "post_stack_joined_rows": len(post_rows),
        "post_stack_suppressed_rows": len(post_suppressed),
        "post_stack_weighted_candidate_cents": post_candidate,
        "blockers": blockers,
        "joined_rows": joined,
        "live_ready": not blockers,
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
            for policy in ("book_gap_only", "clip_only", "book_gap_or_clip", "book_gap_and_clip"):
                variants.append(evaluate_variant(lane, variant, book, reduce, policy, freeze_ts))
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_candidate_cents") or -999999),
            -float((row.get("entry_summary") or {}).get("net_cents") or -999999),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in variants),
        "sources": {"midprice": str(MIDPRICE_JSON), "book_gap": str(BOOK_GAP_JSON), "reduce": str(REDUCE_JSON)},
        "variants": variants,
        "interpretation": interpretation(variants),
    }


def interpretation(variants: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a newly frozen diagnostic overlap; post-freeze rows are required before promotion.",
        "The policies are observable and do not use settlement outcome to choose the exit.",
    ]
    if variants:
        best = variants[0]
        summary = best.get("entry_summary") or {}
        notes.append(
            f"Best policy {best.get('policy')} has entry settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, W/L {summary.get('wins')}/{summary.get('losses')}, "
            f"joined rows {best.get('joined_exit_rows')}, suppressions {best.get('suppressed_rows')}, "
            f"suppressed losers {best.get('suppressed_losers')}, weighted net {best.get('weighted_candidate_cents')}c, "
            f"delta {best.get('weighted_delta_cents')}c, post rows {best.get('post_stack_joined_rows')}, "
            f"blockers {best.get('blockers')}."
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
        "# v28 Soft-Frontier Mid-Price Boundary + Dual Exit Stack",
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
        "| rank | lane | policy | exit policy | strict | entry settled | W/L | coverage | recon | joined | suppress | suppress losers | post joined | post suppress | weighted net | weighted delta | post net | blockers |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate((report.get("variants") or [])[:60], start=1):
        summary = row.get("entry_summary") or {}
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('policy')}` | `{row.get('exit_policy')}` | "
            f"{row.get('strict_forward')} | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('joined_exit_rows')} | {row.get('suppressed_rows')} | {row.get('suppressed_losers')} | "
            f"{row.get('post_stack_joined_rows')} | {row.get('post_stack_suppressed_rows')} | "
            f"{fmt(row.get('weighted_candidate_cents'))} | {fmt(row.get('weighted_delta_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_candidate_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
