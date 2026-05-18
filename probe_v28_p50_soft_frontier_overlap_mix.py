"""Overlap/mix probe for p50 book-edge and soft-frontier midprice lanes.

Research-only; no live bot changes or orders.

This asks whether the broad p50/book-edge family is complementary to the
current soft-frontier/midprice family. The useful portfolio is not a bigger
green row; it is a union where non-overlap rows add independent PnL without
reopening source-quality or full-loss-cushion failure modes.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOFT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
P50_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_p50_soft_frontier_overlap_mix_latest.json"
OUT_MD = OUT_DIR / "v28_p50_soft_frontier_overlap_mix_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35


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


def amount(row: dict[str, Any]) -> float:
    for key in ("weighted_net_cents", "net_cents", "gross_cents", "raw_net_cents"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return 0.0


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def won(row: dict[str, Any]) -> bool:
    return amount(row) > 0


def lost(row: dict[str, Any]) -> bool:
    return amount(row) < 0


def clean(row: dict[str, Any]) -> bool:
    return str(row.get("source") or "") == "approved_entry"


def p50_row(row: dict[str, Any], policy: str, weight_fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    clone = dict(row)
    clone["policy"] = policy
    clone["weighted_net_cents"] = (as_float(row.get("gross_cents")) or 0.0) * weight_fn(row)
    clone["weight"] = weight_fn(row)
    return clone


def p50_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in payload.get("rows") or [] if isinstance(row, dict) and market(row)]
    denominator = int(as_float(payload.get("future_denominator_markets")) or len(rows))
    variants: list[tuple[str, Callable[[dict[str, Any]], bool], Callable[[dict[str, Any]], float]]] = [
        ("p50_full_size", lambda _row: True, lambda _row: 1.0),
        ("p50_quarter_no_side", lambda _row: True, lambda row: 0.25 if row.get("side") == "no" else 1.0),
        ("p50_yes_only", lambda row: row.get("side") == "yes", lambda _row: 1.0),
        ("p50_yes_or_no_low_recross", lambda row: row.get("side") == "yes" or (as_float(row.get("recross_hazard_score")) or 0.0) < 0.60, lambda _row: 1.0),
        ("p50_yes_or_no_strong_distance", lambda row: row.get("side") == "yes" or (as_float(row.get("abs_d_sigma")) or 0.0) >= 0.65, lambda _row: 1.0),
    ]
    out = []
    for policy, keep, weight in variants:
        kept = [p50_row(row, policy, weight) for row in rows if keep(row)]
        out.append({
            "source": "p50_book_edge",
            "lane": "frozen_parent_diagnostic",
            "policy": policy,
            "denominator": denominator,
            "rows": kept,
            "summary": summarize(kept, denominator),
        })
    return out


def soft_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    wanted = {
        ("diagnostic_entry", "diagnostic_entry_quarter_midprice_boundary"),
        ("diagnostic_bridge", "diagnostic_bridge_quarter_midprice_boundary"),
        ("post_feature_freeze_entry", "post_feature_freeze_entry_quarter_midprice_boundary"),
        ("post_feature_freeze_bridge", "post_feature_freeze_bridge_quarter_midprice_boundary"),
    }
    out = []
    for lane in payload.get("lanes") or []:
        lane_name = str(lane.get("lane") or "")
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for variant in lane.get("variants") or []:
            policy = str(variant.get("candidate") or "")
            if (lane_name, policy) not in wanted:
                continue
            summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
            rows = []
            for row in summary.get("rows") or []:
                if not isinstance(row, dict) or not market(row):
                    continue
                clone = dict(row)
                clone["weighted_net_cents"] = as_float(clone.get("weighted_net_cents")) or as_float(clone.get("net_cents")) or 0.0
                rows.append(clone)
            out.append({
                "source": "soft_frontier_midprice",
                "lane": lane_name,
                "policy": policy,
                "denominator": denominator,
                "rows": rows,
                "summary": summarize(rows, denominator),
            })
    return out


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    total = sum(amount(row) for row in rows)
    entries = len(rows)
    return {
        "entries": entries,
        "settled": entries,
        "wins": sum(1 for row in rows if won(row)),
        "losses": sum(1 for row in rows if lost(row)),
        "net_cents": total,
        "coverage_pct": (entries / denominator * 100.0) if denominator else 0.0,
        "reconstructed_share": 1.0 - (sum(1 for row in rows if clean(row)) / entries) if entries else None,
        "full_loss_cushion": math.floor(total / 100.0) if total > 0 else 0,
        "worst_loss_cents": min((amount(row) for row in rows), default=0.0),
    }


def blockers(summary: dict[str, Any], diagnostic: bool) -> list[str]:
    out = []
    if diagnostic:
        out.append("diagnostic_or_parent_mix_needs_own_freeze")
    if int(summary.get("settled") or 0) < 30:
        out.append("settled_lt_30")
    coverage = as_float(summary.get("coverage_pct"))
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        out.append("coverage_too_low")
    elif coverage > TARGET_COVERAGE_MAX:
        out.append("coverage_too_high")
    if (as_float(summary.get("net_cents")) or 0.0) <= 0:
        out.append("net_not_positive")
    recon = as_float(summary.get("reconstructed_share"))
    if recon is None or recon > MAX_RECON_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(summary.get("full_loss_cushion") or 0) < 3:
        out.append("full_loss_cushion_lt_3")
    out.append("live_ready_false")
    return out


def union_primary_first(primary: dict[str, Any], add_on: dict[str, Any]) -> dict[str, Any]:
    primary_rows = {market(row): row for row in primary.get("rows") or []}
    add_rows = {market(row): row for row in add_on.get("rows") or []}
    nonoverlap = [row for key, row in add_rows.items() if key not in primary_rows]
    shared_keys = set(primary_rows) & set(add_rows)
    union_rows = list(primary_rows.values()) + nonoverlap
    denominator = max(int(primary.get("denominator") or 0), int(add_on.get("denominator") or 0), len(union_rows))
    summary = summarize(union_rows, denominator)
    primary_summary = primary.get("summary") or summarize(list(primary_rows.values()), denominator)
    add_summary = summarize(nonoverlap, denominator)
    shared_agree = 0
    shared_disagree = 0
    for key in shared_keys:
        p_row = primary_rows[key]
        a_row = add_rows[key]
        if str(p_row.get("side") or "") == str(a_row.get("side") or ""):
            shared_agree += 1
        else:
            shared_disagree += 1
    diagnostic = str(primary.get("lane") or "").startswith("diagnostic") or str(add_on.get("lane") or "").startswith("frozen_parent")
    return {
        "primary": f"{primary.get('source')}:{primary.get('lane')}:{primary.get('policy')}",
        "add_on": f"{add_on.get('source')}:{add_on.get('lane')}:{add_on.get('policy')}",
        **summary,
        "primary_net_cents": primary_summary.get("net_cents"),
        "add_on_nonoverlap_entries": len(nonoverlap),
        "add_on_nonoverlap_net_cents": add_summary.get("net_cents"),
        "shared_markets": len(shared_keys),
        "shared_side_agree": shared_agree,
        "shared_side_disagree": shared_disagree,
        "blockers": blockers(summary, diagnostic=diagnostic),
        "live_ready": False,
    }


def build_report() -> dict[str, Any]:
    soft = soft_lanes(load_json(SOFT_JSON))
    p50 = p50_lanes(load_json(P50_JSON))
    portfolios = []
    for primary in soft:
        for add_on in p50:
            portfolios.append(union_primary_first(primary, add_on))
    for primary in p50:
        for add_on in soft:
            portfolios.append(union_primary_first(primary, add_on))
    portfolios.sort(key=lambda row: as_float(row.get("net_cents")) or -999999.0, reverse=True)
    best_target = next(
        (
            row for row in portfolios
            if TARGET_COVERAGE_MIN <= (as_float(row.get("coverage_pct")) or 0.0) <= TARGET_COVERAGE_MAX
            and (as_float(row.get("net_cents")) or 0.0) > 0
        ),
        {},
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "soft_frontier_midprice": str(SOFT_JSON),
            "p50_book_edge": str(P50_JSON),
        },
        "lane_counts": {"soft_lanes": len(soft), "p50_lanes": len(p50), "portfolios": len(portfolios)},
        "soft_lanes": [compact_lane(row) for row in soft],
        "p50_lanes": [compact_lane(row) for row in p50],
        "portfolios": portfolios,
        "best_positive_target_coverage": best_target,
        "candidate_live_ready": False,
        "interpretation": [
            "This is diagnostic overlap research only; any dual child needs its own frozen forward birth.",
            "The key metric is add-on non-overlap PnL, because shared-market overlap does not create independent market coverage.",
            "A useful dual strategy should add positive non-overlap rows while keeping 75-90% coverage, <=35% reconstructed share, and cushion >=3.",
        ],
    }


def compact_lane(lane: dict[str, Any]) -> dict[str, Any]:
    summary = lane.get("summary") or {}
    return {
        "source": lane.get("source"),
        "lane": lane.get("lane"),
        "policy": lane.get("policy"),
        "entries": summary.get("entries"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "net_cents": summary.get("net_cents"),
        "coverage_pct": summary.get("coverage_pct"),
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
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
    lines = [
        "# v28 p50 + Soft-Frontier Overlap Mix",
        "",
        "Research-only p50/book-edge versus soft-frontier/midprice overlap test. No live orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Lane counts: `{report.get('lane_counts')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")

    best = report.get("best_positive_target_coverage") or {}
    lines.extend([
        "",
        "## Best Positive Target-Coverage Mix",
        "",
        f"- Primary: `{best.get('primary')}`",
        f"- Add-on: `{best.get('add_on')}`",
        f"- Entries/W-L/net/coverage/recon/cushion: `{best.get('entries')}/{best.get('wins')}-{best.get('losses')}/{fmt(best.get('net_cents'))}c/{fmt(best.get('coverage_pct'))}%/{fmt(best.get('reconstructed_share'))}/{best.get('full_loss_cushion')}`",
        f"- Add-on non-overlap entries/net: `{best.get('add_on_nonoverlap_entries')}/{fmt(best.get('add_on_nonoverlap_net_cents'))}c`",
        f"- Shared markets/side agree/disagree: `{best.get('shared_markets')}/{best.get('shared_side_agree')}/{best.get('shared_side_disagree')}`",
        f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        "",
        "## Top Portfolio Mixes",
        "",
        "| rank | primary | add-on | entries | W/L | net | coverage | recon | cushion | add-on nonoverlap | shared agree/disagree | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for rank, row in enumerate((report.get("portfolios") or [])[:25], 1):
        lines.append(
            f"| {rank} | `{row.get('primary')}` | `{row.get('add_on')}` | {row.get('entries')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | {fmt(row.get('coverage_pct'))}% | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} | "
            f"{row.get('add_on_nonoverlap_entries')}/{fmt(row.get('add_on_nonoverlap_net_cents'))} | "
            f"{row.get('shared_side_agree')}/{row.get('shared_side_disagree')} | "
            f"`{', '.join(row.get('blockers') or []) or 'none'}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
