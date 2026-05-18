"""Source/failure drilldown for the frozen p50 book-edge entry lane.

Research-only; no live bot changes or orders.

This reads the already-frozen `p50_book_plus_05_edge_nonnegative` future
validator and asks why it is profitable but non-promotable. Source labels are
used only for audit attribution. Candidate repairs below use observable row
features such as side, boundary distance, recross hazard, edge thickness,
freshness, depth, and clock.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_p50_book_edge_source_failure_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_p50_book_edge_source_failure_drilldown_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_SOURCE_SHARE = 0.35


Row = dict[str, Any]
Predicate = Callable[[Row], bool]
WeightFn = Callable[[Row], float]


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


def settled(row: Row) -> bool:
    return row.get("side_won") is not None and as_float(row.get("gross_cents")) is not None


def won(row: Row) -> bool:
    return row.get("side_won") is True


def lost(row: Row) -> bool:
    return row.get("side_won") is False


def val(row: Row, key: str, default: float = 0.0) -> float:
    parsed = as_float(row.get(key))
    return default if parsed is None else parsed


def stat_rows(rows: list[Row], denominator: int, weight_fn: WeightFn | None = None) -> dict[str, Any]:
    weight_fn = weight_fn or (lambda _row: 1.0)
    settled_rows = [row for row in rows if settled(row)]
    weights = [max(0.0, float(weight_fn(row))) for row in settled_rows]
    weighted_gross = sum(val(row, "gross_cents") * weight for row, weight in zip(settled_rows, weights))
    approved = [row for row in rows if row.get("source") == "approved_entry"]
    rejected = [row for row in rows if row.get("source") == "rejected_actionable"]
    approved_weight = sum(max(0.0, float(weight_fn(row))) for row in rows if row.get("source") == "approved_entry")
    rejected_weight = sum(max(0.0, float(weight_fn(row))) for row in rows if row.get("source") == "rejected_actionable")
    total_weight = approved_weight + rejected_weight
    markets = {row.get("market") for row in rows if row.get("market")}
    coverage = (len(markets) / denominator * 100.0) if denominator else 0.0
    return {
        "entries": len(rows),
        "effective_entries": sum(max(0.0, float(weight_fn(row))) for row in rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if won(row)),
        "losses": sum(1 for row in settled_rows if lost(row)),
        "gross_cents": weighted_gross,
        "avg_gross_cents": weighted_gross / sum(weights) if sum(weights) else None,
        "coverage_pct": coverage,
        "approved_entry_count": len(approved),
        "rejected_actionable_count": len(rejected),
        "rejected_actionable_share": len(rejected) / len(rows) if rows else None,
        "weighted_rejected_actionable_share": rejected_weight / total_weight if total_weight else None,
        "full_loss_cushion": math.floor(weighted_gross / 100.0) if weighted_gross > 0 else 0,
    }


def source_splits(rows: list[Row], denominator: int) -> list[dict[str, Any]]:
    splits = []
    for source in sorted({str(row.get("source") or "unknown") for row in rows}):
        source_rows = [row for row in rows if str(row.get("source") or "unknown") == source]
        splits.append({"source": source, **stat_rows(source_rows, denominator)})
    return sorted(splits, key=lambda row: as_float(row.get("gross_cents")) or 0.0, reverse=True)


def bucket_splits(rows: list[Row], denominator: int) -> list[dict[str, Any]]:
    buckets: list[tuple[str, Predicate]] = [
        ("side_yes", lambda row: row.get("side") == "yes"),
        ("side_no", lambda row: row.get("side") == "no"),
        ("abs_d_lt_025", lambda row: val(row, "abs_d_sigma") < 0.25),
        ("abs_d_025_050", lambda row: 0.25 <= val(row, "abs_d_sigma") < 0.50),
        ("abs_d_050_065", lambda row: 0.50 <= val(row, "abs_d_sigma") < 0.65),
        ("abs_d_gte_065", lambda row: val(row, "abs_d_sigma") >= 0.65),
        ("recross_gte_060", lambda row: val(row, "recross_hazard_score") >= 0.60),
        ("recross_gte_075", lambda row: val(row, "recross_hazard_score") >= 0.75),
        ("edge_lt_3", lambda row: val(row, "edge_cents") < 3.0),
        ("edge_gte_3", lambda row: val(row, "edge_cents") >= 3.0),
        ("raw_edge_lt_5", lambda row: val(row, "raw_edge_cents") < 5.0),
        ("book_age_gt_1000ms", lambda row: val(row, "book_age_ms") > 1000.0),
        ("btc_age_gt_1000ms", lambda row: val(row, "btc_age_ms") > 1000.0),
        ("depth_lt_200", lambda row: val(row, "eligible_depth") < 200.0),
        ("late_lt_240s", lambda row: val(row, "seconds_to_close") < 240.0),
        ("early_gt_720s", lambda row: val(row, "seconds_to_close") > 720.0),
        ("no_side_recross_gte_060", lambda row: row.get("side") == "no" and val(row, "recross_hazard_score") >= 0.60),
        ("no_side_abs_d_lt_065", lambda row: row.get("side") == "no" and val(row, "abs_d_sigma") < 0.65),
        ("yes_side_abs_d_gte_065", lambda row: row.get("side") == "yes" and val(row, "abs_d_sigma") >= 0.65),
    ]
    out = []
    for name, pred in buckets:
        bucket_rows = [row for row in rows if pred(row)]
        if bucket_rows:
            out.append({"bucket": name, **stat_rows(bucket_rows, denominator)})
    return sorted(out, key=lambda row: as_float(row.get("gross_cents")) or 0.0, reverse=True)


def loss_tags(row: Row) -> list[str]:
    tags = []
    if row.get("source") != "approved_entry":
        tags.append("source_quality_error")
    if row.get("side") == "no":
        tags.append("no_side_error")
    if val(row, "abs_d_sigma") < 0.25:
        tags.append("near_strike_boundary")
    elif val(row, "abs_d_sigma") < 0.65:
        tags.append("weak_boundary_distance")
    if val(row, "recross_hazard_score") >= 0.75:
        tags.append("extreme_recross_hazard")
    elif val(row, "recross_hazard_score") >= 0.60:
        tags.append("high_recross_hazard")
    if val(row, "edge_cents") < 3.0:
        tags.append("thin_fee_edge")
    if val(row, "raw_edge_cents") < 5.0:
        tags.append("thin_raw_edge")
    if val(row, "book_age_ms") > 1000.0 or val(row, "btc_age_ms") > 1000.0:
        tags.append("stale_source_age")
    if val(row, "eligible_depth") < 200.0:
        tags.append("low_depth")
    if val(row, "seconds_to_close") < 240.0:
        tags.append("late_clock")
    if val(row, "seconds_to_close") > 720.0:
        tags.append("early_clock")
    return tags or ["unclassified_loss"]


def loss_attribution(rows: list[Row]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not lost(row):
            continue
        gross = val(row, "gross_cents")
        for tag in loss_tags(row):
            item = counts.setdefault(tag, {"tag": tag, "loss_count": 0, "loss_gross_cents": 0.0})
            item["loss_count"] += 1
            item["loss_gross_cents"] += gross
    return sorted(counts.values(), key=lambda item: (item["loss_count"], -item["loss_gross_cents"]), reverse=True)


def apply_filter(rows: list[Row], keep: Predicate) -> list[Row]:
    return [row for row in rows if keep(row)]


def blocker_list(stats: dict[str, Any], use_weighted_share: bool = False) -> list[str]:
    blockers = []
    if int(stats.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    coverage = as_float(stats.get("coverage_pct"))
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    elif coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if (as_float(stats.get("gross_cents")) or 0.0) <= 0:
        blockers.append("gross_not_positive")
    share_key = "weighted_rejected_actionable_share" if use_weighted_share else "rejected_actionable_share"
    share = as_float(stats.get(share_key))
    if share is None or share > MAX_SOURCE_SHARE:
        blockers.append("rejected_actionable_share_gt_35pct")
    if int(stats.get("full_loss_cushion") or 0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    return blockers


def variant_rows(rows: list[Row], denominator: int) -> list[dict[str, Any]]:
    variants: list[tuple[str, str, Predicate, WeightFn | None, bool]] = [
        ("base", "current frozen p50 book-edge lane", lambda _row: True, None, False),
        ("yes_only", "take only YES-side book-edge rows", lambda row: row.get("side") == "yes", None, False),
        ("no_only", "take only NO-side book-edge rows", lambda row: row.get("side") == "no", None, False),
        ("drop_no_side", "drop all NO-side rows", lambda row: row.get("side") != "no", None, False),
        ("drop_abs_d_lt_050", "drop weak boundary distance abs_d_sigma < 0.50", lambda row: val(row, "abs_d_sigma") >= 0.50, None, False),
        ("drop_abs_d_lt_065", "drop weak boundary distance abs_d_sigma < 0.65", lambda row: val(row, "abs_d_sigma") >= 0.65, None, False),
        ("drop_recross_gte_060", "drop high recross hazard >= 0.60", lambda row: val(row, "recross_hazard_score") < 0.60, None, False),
        ("drop_recross_gte_075", "drop extreme recross hazard >= 0.75", lambda row: val(row, "recross_hazard_score") < 0.75, None, False),
        ("drop_recross60_absd65", "drop rows that combine recross >= 0.60 with abs_d_sigma < 0.65", lambda row: not (val(row, "recross_hazard_score") >= 0.60 and val(row, "abs_d_sigma") < 0.65), None, False),
        ("drop_edge_lt_3", "drop fee-aware edge < 3c", lambda row: val(row, "edge_cents") >= 3.0, None, False),
        ("drop_raw_edge_lt_5", "drop raw edge < 5c", lambda row: val(row, "raw_edge_cents") >= 5.0, None, False),
        ("drop_depth_lt_200", "drop shallow eligible depth < 200", lambda row: val(row, "eligible_depth") >= 200.0, None, False),
        ("drop_early_gt_720", "drop very early rows with >720s to close", lambda row: val(row, "seconds_to_close") <= 720.0, None, False),
        ("yes_or_absd_gte_065", "allow YES rows, require strong distance for NO rows", lambda row: row.get("side") == "yes" or val(row, "abs_d_sigma") >= 0.65, None, False),
        ("yes_or_no_recross_lt_060", "allow YES rows, require low recross for NO rows", lambda row: row.get("side") == "yes" or val(row, "recross_hazard_score") < 0.60, None, False),
        ("yes_or_no_absd065_recross060", "allow YES rows, require NO rows to be strong-distance and low-recross", lambda row: row.get("side") == "yes" or (val(row, "abs_d_sigma") >= 0.65 and val(row, "recross_hazard_score") < 0.60), None, False),
        ("drop_no_weak_or_high_recross", "drop NO rows with weak distance or high recross", lambda row: row.get("side") != "no" or (val(row, "abs_d_sigma") >= 0.65 and val(row, "recross_hazard_score") < 0.60), None, False),
        ("half_no_side", "half-size NO rows, full-size YES rows", lambda _row: True, lambda row: 0.5 if row.get("side") == "no" else 1.0, True),
        ("quarter_no_side", "quarter-size NO rows, full-size YES rows", lambda _row: True, lambda row: 0.25 if row.get("side") == "no" else 1.0, True),
        ("half_weak_or_recross", "half-size weak-distance or high-recross rows", lambda _row: True, lambda row: 0.5 if (val(row, "abs_d_sigma") < 0.65 or val(row, "recross_hazard_score") >= 0.60) else 1.0, True),
        ("quarter_weak_or_recross", "quarter-size weak-distance or high-recross rows", lambda _row: True, lambda row: 0.25 if (val(row, "abs_d_sigma") < 0.65 or val(row, "recross_hazard_score") >= 0.60) else 1.0, True),
        ("half_no_weak_or_recross", "half-size NO rows only when weak-distance or high-recross", lambda _row: True, lambda row: 0.5 if (row.get("side") == "no" and (val(row, "abs_d_sigma") < 0.65 or val(row, "recross_hazard_score") >= 0.60)) else 1.0, True),
        ("quarter_no_weak_or_recross", "quarter-size NO rows only when weak-distance or high-recross", lambda _row: True, lambda row: 0.25 if (row.get("side") == "no" and (val(row, "abs_d_sigma") < 0.65 or val(row, "recross_hazard_score") >= 0.60)) else 1.0, True),
    ]
    out = []
    for name, description, keep, weight_fn, weighted_share_gate in variants:
        kept = apply_filter(rows, keep)
        stats = stat_rows(kept, denominator, weight_fn)
        out.append({
            "variant": name,
            "description": description,
            **stats,
            "blockers": blocker_list(stats, use_weighted_share=weighted_share_gate),
            "gate_live_ready": False,
            "live_ready_reason": "diagnostic_repair_only_not_pre_registered",
        })
    return sorted(out, key=lambda row: as_float(row.get("gross_cents")) or 0.0, reverse=True)


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    denominator = int(source.get("future_denominator_markets") or 0)
    variants = variant_rows(rows, denominator)
    best_target = next(
        (
            row for row in variants
            if TARGET_COVERAGE_MIN <= (as_float(row.get("coverage_pct")) or 0.0) <= TARGET_COVERAGE_MAX
            and (as_float(row.get("gross_cents")) or 0.0) > 0
        ),
        {},
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(SOURCE_JSON),
        "candidate": "p50_book_plus_05_edge_nonnegative",
        "freeze": source.get("freeze"),
        "future_denominator_markets": denominator,
        "source_summary": source.get("summary"),
        "source_blockers": source.get("blockers"),
        "source_splits": source_splits(rows, denominator),
        "bucket_splits": bucket_splits(rows, denominator),
        "loss_attribution": loss_attribution(rows),
        "variants": variants,
        "best_positive_target_coverage_variant": best_target,
        "candidate_live_ready": False,
        "interpretation": [
            "The broad p50 book-edge lane is profitable but remains source-blocked; source labels are audit-only and cannot be used as a live rule.",
            "Approved rows are very clean but too sparse; the rejected-actionable slice still contributes positive PnL while carrying most of the full-loss risk.",
            "The strongest observable failure clue is side asymmetry: YES rows are strongly positive while NO rows are net negative in this sample.",
            "All variants here are diagnostic repairs. Any live-testable child needs its own frozen forward birth and the controlled live-test gate.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("source_summary") or {}
    lines = [
        "# v28 p50 Book-Edge Source Failure Drilldown",
        "",
        "Research-only drilldown of the frozen p50 book-edge entry lane. No live orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Future denominator markets: `{report.get('future_denominator_markets')}`",
        f"- Base entries/settled/W-L: `{summary.get('entries')}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}`",
        f"- Base gross/coverage/source share: `{fmt(summary.get('gross_cents'))}c/{fmt(summary.get('coverage_pct'))}%/{fmt(summary.get('simulated_share'))}`",
        f"- Base blockers: `{', '.join(report.get('source_blockers') or []) or 'none'}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")

    lines.extend(["", "## Source Splits", "", "| Source | Entries | W-L | Gross c | Coverage % | Rejected share |", "|---|---:|---:|---:|---:|---:|"])
    for row in report.get("source_splits") or []:
        lines.append(
            f"| `{row.get('source')}` | {row.get('entries')} | {row.get('wins')}-{row.get('losses')} | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('coverage_pct'))} | {fmt(row.get('rejected_actionable_share'))} |"
        )

    lines.extend(["", "## Top Observable Buckets", "", "| Bucket | Entries | W-L | Gross c | Coverage % |", "|---|---:|---:|---:|---:|"])
    for row in (report.get("bucket_splits") or [])[:16]:
        lines.append(
            f"| `{row.get('bucket')}` | {row.get('entries')} | {row.get('wins')}-{row.get('losses')} | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('coverage_pct'))} |"
        )

    lines.extend(["", "## Loss Tags", "", "| Tag | Losses | Loss gross c |", "|---|---:|---:|"])
    for row in report.get("loss_attribution") or []:
        lines.append(f"| `{row.get('tag')}` | {row.get('loss_count')} | {fmt(row.get('loss_gross_cents'))} |")

    lines.extend(["", "## Variant Bakeoff", "", "| Variant | Entries | W-L | Gross c | Coverage % | Rejected share | Cushion | Blockers |", "|---|---:|---:|---:|---:|---:|---:|---|"])
    for row in report.get("variants") or []:
        share = row.get("weighted_rejected_actionable_share") if row.get("variant", "").startswith(("half_", "quarter_")) else row.get("rejected_actionable_share")
        lines.append(
            f"| `{row.get('variant')}` | {row.get('entries')} | {row.get('wins')}-{row.get('losses')} | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('coverage_pct'))} | {fmt(share)} | "
            f"{row.get('full_loss_cushion')} | `{', '.join(row.get('blockers') or []) or 'none'}` |"
        )

    best = report.get("best_positive_target_coverage_variant") or {}
    lines.extend([
        "",
        "## Best Positive Target-Coverage Variant",
        "",
        f"- Variant: `{best.get('variant')}`",
        f"- Entries/settled/W-L: `{best.get('entries')}/{best.get('settled')}/{best.get('wins')}-{best.get('losses')}`",
        f"- Gross/coverage/rejected share/cushion: `{fmt(best.get('gross_cents'))}c/{fmt(best.get('coverage_pct'))}%/{fmt(best.get('rejected_actionable_share'))}/{best.get('full_loss_cushion')}`",
        f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
