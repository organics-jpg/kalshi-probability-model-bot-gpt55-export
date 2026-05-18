"""Soft-frontier mid-price entry plus delayed-recheck exit diagnostic.

Research-only; no live bot changes or orders.

The current top rows combine broad soft-frontier/mid-price entries with exit
suppression, but the high-exit-bid feature-gate audit showed that blind hold
suppression can require surviving large adverse marks. This probe asks whether
the same delayed-recheck survival rule composes with the broad mid-price entry
family.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats
from probe_v28_feature_gate_exit_bid_path_risk import parse_utc, to_eastern_naive


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDPRICE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_exit_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_exit_latest.md"

TARGET_COVERAGE_MIN = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_JOINED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3

VARIANTS = [
    {"name": "delay60_bid_ge60_drop_lte10", "delay_seconds": 60, "bid_floor": 60, "max_drop": 10},
    {"name": "delay60_bid_ge65_drop_lte10", "delay_seconds": 60, "bid_floor": 65, "max_drop": 10},
    {"name": "delay60_bid_ge70_drop_lte10", "delay_seconds": 60, "bid_floor": 70, "max_drop": 10},
    {"name": "delay120_bid_ge60_drop_lte10", "delay_seconds": 120, "bid_floor": 60, "max_drop": 10},
]


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def maybe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def group_exit_rows(path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in load_json(path).get("rows") or []:
        if isinstance(row, dict):
            grouped[(market(row), side(row))].append(row)
    for key in grouped:
        grouped[key].sort(key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
    return grouped


def latest(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[-1] if rows else None


def choose_exit_row(
    entry: dict[str, Any],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    source_name: str,
) -> dict[str, Any] | None:
    key = (market(entry), side(entry))
    book = latest(book_rows.get(key) or [])
    reduce = latest(reduce_rows.get(key) or [])
    if source_name == "book_gap":
        return book
    if source_name == "reduce":
        return reduce
    candidates = [row for row in [book, reduce] if row is not None]
    candidates.sort(key=lambda row: parse_ts(row.get("exit_ts") or row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
    return candidates[-1] if candidates else None


def path_points(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    exit_ts = to_eastern_naive(parse_utc(row.get("exit_ts")))
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market(row)))
    points = [
        {**hb, "held_bid": held_bid(hb, side(row))}
        for hb in heartbeats
        if hb["market"] == market(row)
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    points.sort(key=lambda item: item["ts"])
    return points


def delayed_recheck_pass(exit_row: dict[str, Any], points: list[dict[str, Any]], variant: dict[str, Any]) -> dict[str, Any]:
    exit_ts = to_eastern_naive(parse_utc(exit_row.get("exit_ts")))
    if exit_ts is None or not points:
        return {
            "suppressed": False,
            "exit_bid": None,
            "recheck_bid": None,
            "min_window_bid": None,
            "window_drop_cents": None,
            "recheck_missing": True,
        }
    exit_bid = fnum(points[0].get("held_bid"), None)
    recheck_ts = exit_ts + timedelta(seconds=int(variant["delay_seconds"]))
    recheck = next((point for point in points if point["ts"] >= recheck_ts), None)
    window = [point for point in points if point["ts"] <= recheck_ts]
    recheck_bid = None if recheck is None else fnum(recheck.get("held_bid"), None)
    min_window_bid = min([fnum(point.get("held_bid")) for point in window], default=None)
    drop = None if min_window_bid is None or exit_bid is None else exit_bid - min_window_bid
    suppress = (
        recheck_bid is not None
        and recheck_bid >= float(variant["bid_floor"])
        and drop is not None
        and drop <= float(variant["max_drop"])
    )
    return {
        "suppressed": suppress,
        "exit_bid": exit_bid,
        "recheck_bid": recheck_bid,
        "min_window_bid": min_window_bid,
        "window_drop_cents": drop,
        "recheck_missing": recheck is None,
    }


def evaluate(
    lane: dict[str, Any],
    entry_variant: dict[str, Any],
    exit_source: str,
    recheck_variant: dict[str, Any],
    book_rows: dict[tuple[str, str], list[dict[str, Any]]],
    reduce_rows: dict[tuple[str, str], list[dict[str, Any]]],
    heartbeats: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = entry_variant.get("summary") if isinstance(entry_variant.get("summary"), dict) else {}
    entry_rows = [row for row in summary.get("rows") or [] if isinstance(row, dict)]
    joined: list[dict[str, Any]] = []
    for entry in entry_rows:
        exit_row = choose_exit_row(entry, book_rows, reduce_rows, exit_source)
        if exit_row is None:
            continue
        weight = maybe_float(entry.get("weight"))
        if weight is None:
            weight = 1.0
        points = path_points(exit_row, heartbeats)
        recheck = delayed_recheck_pass(exit_row, points, recheck_variant)
        current = fnum(exit_row.get("current_cents"))
        hold = fnum(exit_row.get("hold_cents") or exit_row.get("candidate_cents"))
        candidate = hold if recheck["suppressed"] else current
        joined.append(
            {
                "market": market(entry),
                "side": side(entry),
                "source": source(entry),
                "entry_weight": weight,
                "exit_source": exit_source,
                "exit_ts": exit_row.get("exit_ts"),
                "exit_reason": exit_row.get("exit_reason"),
                "p_hold": exit_row.get("p_hold"),
                "fair_drawdown_cents": exit_row.get("fair_drawdown_cents"),
                "current_cents": current,
                "hold_cents": hold,
                "candidate_cents": candidate,
                "delta_cents": candidate - current,
                "weighted_current_cents": weight * current,
                "weighted_candidate_cents": weight * candidate,
                "weighted_delta_cents": weight * (candidate - current),
                **recheck,
            }
        )
    net = sum(row["weighted_candidate_cents"] for row in joined)
    current_net = sum(row["weighted_current_cents"] for row in joined)
    suppressed = [row for row in joined if row.get("suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("weighted_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("weighted_delta_cents")) < 0]
    share = reconstructed_share(entry_rows)
    coverage = maybe_float(summary.get("coverage_pct"))
    entry_net = fnum(summary.get("net_cents"))
    blockers: list[str] = []
    if not bool(lane.get("strict_forward")):
        blockers.append("entry_lane_not_strict_forward")
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("entry_settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("entry_coverage_too_low")
    if entry_net <= 0:
        blockers.append("entry_net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("entry_reconstructed_share_gt_35pct")
    if len(joined) < MIN_JOINED:
        blockers.append("joined_exit_rows_lt_30")
    if len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if net <= 0:
        blockers.append("weighted_exit_net_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
    if full_loss_cushion(net) < MIN_FULL_LOSS_CUSHION:
        blockers.append("weighted_full_loss_cushion_lt_3")
    blockers.append("diagnostic_exit_composition")
    return {
        "lane": lane.get("lane"),
        "strict_forward": bool(lane.get("strict_forward")),
        "entry_policy": entry_variant.get("candidate"),
        "exit_source": exit_source,
        "recheck_policy": recheck_variant["name"],
        "policy": f"{entry_variant.get('candidate')}_{exit_source}_{recheck_variant['name']}",
        "entry_summary": {key: value for key, value in summary.items() if key != "rows"},
        "reconstructed_share": share,
        "source_counts": source_counts(entry_rows),
        "joined_exit_rows": len(joined),
        "suppressed_rows": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "weighted_current_cents": current_net,
        "weighted_candidate_cents": net,
        "weighted_delta_cents": net - current_net,
        "full_loss_cushion_estimate": full_loss_cushion(net),
        "blockers": blockers,
        "live_ready": False,
        "rows": joined,
    }


def build_report() -> dict[str, Any]:
    midprice = load_json(MIDPRICE_JSON)
    book_rows = group_exit_rows(BOOK_GAP_JSON)
    reduce_rows = group_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    rows: list[dict[str, Any]] = []
    for lane in midprice.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        for entry_variant in lane.get("variants") or []:
            if not isinstance(entry_variant, dict):
                continue
            for exit_source in ["latest", "reduce", "book_gap"]:
                for recheck_variant in VARIANTS:
                    rows.append(evaluate(lane, entry_variant, exit_source, recheck_variant, book_rows, reduce_rows, heartbeats))
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            int(row.get("harmful_suppressed") or 0),
            -float(row.get("weighted_candidate_cents") or -999999),
        )
    )
    best = rows[0] if rows else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "midprice": str(MIDPRICE_JSON),
            "book_gap": str(BOOK_GAP_JSON),
            "reduce": str(REDUCE_JSON),
        },
        "variants": rows,
        "interpretation": [
            "Research-only diagnostic composition; no live bot changes or orders.",
            (
                f"Best row {best.get('policy')} has joined {best.get('joined_exit_rows')}, "
                f"suppressed {best.get('suppressed_rows')}, harmful {best.get('harmful_suppressed')}, "
                f"net {best.get('weighted_candidate_cents')}c, blockers {best.get('blockers')}."
            ) if best else "No rows scored.",
            "This is not strict promotion evidence; it tests whether delayed recheck composes with the broad entry family.",
        ],
        "candidate_live_ready": False,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Mid-Price Delayed-Recheck Exit Diagnostic",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Any live-ready variant: `{report.get('candidate_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Top Variants",
            "",
            "| rank | lane | entry | exit source | recheck | strict | settled | W/L | coverage | recon | joined | suppressed | H/H | weighted net | delta | cushion | blockers |",
            "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate((report.get("variants") or [])[:80], start=1):
        summary = row.get("entry_summary") or {}
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('entry_policy')}` | `{row.get('exit_source')}` | "
            f"`{row.get('recheck_policy')}` | {row.get('strict_forward')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('joined_exit_rows')} | {row.get('suppressed_rows')} | "
            f"{row.get('helpful_suppressed')}/{row.get('harmful_suppressed')} | "
            f"{fmt(row.get('weighted_candidate_cents'))} | {fmt(row.get('weighted_delta_cents'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
