"""Exit-overlay audit for the near-gate feature-gate size-shrink branch.

Research-only; no live bot changes or orders.

This mixes the best current post-feature-freeze entry branch with the exit
mechanisms that dominate the high-PnL diagnostic candidates. The question is
whether book-gap / reduce / clip exit suppression improves the near-gate branch
without changing live bot logic or using settlement labels for selection.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    as_float,
    load_or_create_state,
    market,
    net,
    source,
)
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_exit_overlay_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_size_shrink_exit_overlay_latest.md"

POLICY = "repair_low_absd_quarter_else_half"
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_JOINED_EXIT_ROWS = 30
MIN_SUPPRESSED_ROWS = 30
MIN_FULL_LOSS_CUSHION = 3

EXIT_REASONS = {"mushroom_v28_probability_reduce", "mushroom_v28_probability_collapse_full"}


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


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def grouped_exit_rows(path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    payload = load_json(path)
    for row in payload.get("rows") or []:
        if isinstance(row, dict) and market(row) and side(row):
            grouped[(market(row), side(row))].append(row)
    return grouped


def latest(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    floor = datetime.min.replace(tzinfo=timezone.utc)
    return sorted(rows, key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or floor)[-1]


def current_cents(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    return as_float(row.get("current_cents"))


def hold_cents(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    return as_float(row.get("hold_cents") if row.get("hold_cents") is not None else row.get("candidate_cents"))


def p_hold(row: dict[str, Any] | None) -> float | None:
    return as_float((row or {}).get("p_hold"))


def fair_drawdown(row: dict[str, Any] | None) -> float | None:
    return as_float((row or {}).get("fair_drawdown_cents"))


def exit_reason(row: dict[str, Any] | None) -> str:
    return str((row or {}).get("exit_reason") or "")


def suppress_book_gap(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return bool(book and book.get("suppressed"))


def suppress_reduce_p75(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return bool(reduce and reduce.get("suppressed"))


def suppress_clip_p60_drawdown10(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    base = reduce or book
    p = p_hold(base)
    drawdown = fair_drawdown(base)
    return (
        exit_reason(base) in EXIT_REASONS
        and p is not None
        and drawdown is not None
        and p >= 0.60
        and drawdown <= 10.0
    )


def suppress_book_or_reduce(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return suppress_book_gap(book, reduce, entry) or suppress_reduce_p75(book, reduce, entry)


def suppress_book_or_clip(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return suppress_book_gap(book, reduce, entry) or suppress_clip_p60_drawdown10(book, reduce, entry)


def suppress_book_reduce_or_clip(book: dict[str, Any] | None, reduce: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return (
        suppress_book_gap(book, reduce, entry)
        or suppress_reduce_p75(book, reduce, entry)
        or suppress_clip_p60_drawdown10(book, reduce, entry)
    )


SUPPRESSORS: dict[str, Callable[[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any]], bool]] = {
    "base_current_exit_control": lambda book, reduce, entry: False,
    "book_gap_only": suppress_book_gap,
    "reduce_p75_only": suppress_reduce_p75,
    "clip_p60_drawdown10_only": suppress_clip_p60_drawdown10,
    "book_gap_or_reduce_p75": suppress_book_or_reduce,
    "book_gap_or_clip_p60_drawdown10": suppress_book_or_clip,
    "book_gap_or_reduce_p75_or_clip": suppress_book_reduce_or_clip,
}


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    counts = source_counts(rows)
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def build_entry_rows(freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> tuple[list[dict[str, Any]], set[tuple[str, str]], int]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    anchor_rows = selected(rows, ANCHOR_RULE)
    repair_rows = selected(rows, REPAIR_RULE)
    return repair_rows, {row_key(row) for row in anchor_rows}, int(denominator_raw or 0)


def evaluate_variant(
    lane: str,
    entries: list[dict[str, Any]],
    anchor_keys: set[tuple[str, str]],
    denominator: int,
    suppressor_name: str,
    suppressor: Callable[[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any]], bool],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
) -> dict[str, Any]:
    evaluated = []
    for entry in entries:
        key = (market(entry), side(entry))
        book = latest(book_rows.get(key) or [])
        reduce = latest(reduce_rows.get(key) or [])
        base = reduce or book
        weight = repair_weight(POLICY, entry, anchor_keys)
        entry_hold = net(entry)
        cur = current_cents(base)
        hold = hold_cents(base)
        joined = cur is not None and hold is not None
        base_current = cur if joined else entry_hold
        suppress = bool(joined and suppressor(book, reduce, entry))
        candidate = hold if suppress and hold is not None else base_current
        evaluated.append({
            "market": market(entry),
            "side": side(entry),
            "source": source(entry),
            "weight": weight,
            "joined_exit": joined,
            "suppressed": suppress,
            "entry_hold_cents": entry_hold,
            "baseline_current_cents": base_current,
            "candidate_cents": candidate,
            "weighted_entry_hold_cents": weight * entry_hold,
            "weighted_baseline_current_cents": weight * base_current,
            "weighted_candidate_cents": weight * candidate,
            "weighted_delta_vs_current_cents": weight * (candidate - base_current),
            "weighted_delta_vs_entry_hold_cents": weight * (candidate - entry_hold),
            "exit_reason": exit_reason(base),
            "p_hold": p_hold(base),
            "fair_drawdown_cents": fair_drawdown(base),
            "book_gap_signal": bool(book and book.get("suppressed")),
            "reduce_signal": bool(reduce and reduce.get("suppressed")),
            "clip_signal": suppress_clip_p60_drawdown10(book, reduce, entry),
        })
    settled = [row for row in evaluated if row["candidate_cents"] is not None]
    candidate_net = sum(row["weighted_candidate_cents"] for row in settled)
    current_net = sum(row["weighted_baseline_current_cents"] for row in settled)
    entry_hold_net = sum(row["weighted_entry_hold_cents"] for row in settled)
    suppressed = [row for row in evaluated if row["suppressed"]]
    share = reconstructed_share(entries)
    coverage = 100.0 * len(entries) / denominator if denominator else 0.0
    blockers = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if share is not None and share > MAX_RECON_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if sum(1 for row in evaluated if row["joined_exit"]) < MIN_JOINED_EXIT_ROWS:
        blockers.append("joined_exit_rows_lt_30")
    if suppressor_name != "base_current_exit_control" and len(suppressed) < MIN_SUPPRESSED_ROWS:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_net <= 0:
        blockers.append("weighted_candidate_net_not_positive")
    if int(max(0.0, candidate_net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("weighted_full_loss_cushion_lt_3")
    return {
        "lane": lane,
        "policy": f"{POLICY}_{suppressor_name}",
        "entries": len(entries),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row["weighted_candidate_cents"] > 0),
        "losses": sum(1 for row in settled if row["weighted_candidate_cents"] < 0),
        "coverage_pct": coverage,
        "weighted_candidate_net_cents": candidate_net,
        "weighted_current_exit_net_cents": current_net,
        "weighted_entry_hold_net_cents": entry_hold_net,
        "delta_vs_current_exit_cents": candidate_net - current_net,
        "delta_vs_entry_hold_cents": candidate_net - entry_hold_net,
        "row_reconstructed_share": share,
        "source_counts": source_counts(entries),
        "joined_exit_rows": sum(1 for row in evaluated if row["joined_exit"]),
        "suppressed_rows": len(suppressed),
        "suppressed_delta_cents": sum(row["weighted_delta_vs_current_cents"] for row in suppressed),
        "suppressed_loss_control_cost_cents": sum(
            row["weighted_delta_vs_current_cents"] for row in suppressed if row["weighted_delta_vs_current_cents"] < 0
        ),
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "live_ready": not blockers,
        "worst_rows": sorted(evaluated, key=lambda row: row["weighted_candidate_cents"])[:8],
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> dict[str, Any]:
    entries, anchor_keys, denominator = build_entry_rows(freeze_ts, surfaces_fn)
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    variants = [
        evaluate_variant(label, entries, anchor_keys, denominator, name, suppressor, book_rows, reduce_rows)
        for name, suppressor in SUPPRESSORS.items()
    ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_candidate_net_cents") or -999999.0),
            -float(row.get("delta_vs_current_exit_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "future_denominator": denominator,
        "entry_policy": POLICY,
        "entries": len(entries),
        "anchor_weighted_rows": sum(1 for row in entries if row_key(row) in anchor_keys),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Mix near-gate feature-gate size shrink entries with high-PnL diagnostic exit suppressors.",
        "lanes": [
            evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
            evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Exit overlays are diagnostic/research-only; no live bot logic was changed.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        notes.append(
            f"{lane.get('lane')}: best overlay {best.get('policy')} has "
            f"W/L {best.get('wins')}/{best.get('losses')}, candidate net {best.get('weighted_candidate_net_cents')}c, "
            f"delta vs current exits {best.get('delta_vs_current_exit_cents')}c, "
            f"suppressed {best.get('suppressed_rows')}, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Size-Shrink Exit Overlay Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Entry policy: `{lane.get('entry_policy')}`",
            f"- Entries/denominator: `{lane.get('entries')}/{lane.get('future_denominator')}`",
            "",
            "| overlay | W/L | candidate net | current-exit net | entry-hold net | delta current | delta entry | joined | suppressed | source | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("variants") or []:
            lines.append(
                f"| {row.get('policy')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('weighted_candidate_net_cents'))} | {fmt(row.get('weighted_current_exit_net_cents'))} | "
                f"{fmt(row.get('weighted_entry_hold_net_cents'))} | {fmt(row.get('delta_vs_current_exit_cents'))} | "
                f"{fmt(row.get('delta_vs_entry_hold_cents'))} | {row.get('joined_exit_rows')} | {row.get('suppressed_rows')} | "
                f"{fmt(row.get('row_reconstructed_share'))} | {row.get('full_loss_cushion')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
