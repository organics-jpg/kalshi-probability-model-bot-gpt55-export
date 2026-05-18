"""Robustness audit for the v28 source-aware FV overlay.

Research-only; no live bot changes or orders.

The source-aware overlay is promising only if its calibration improvement is
not carried by one lucky market or one evidence source. This audit recomputes
the overlay after removing each market and on each source slice.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_source_aware_fv_overlay_validator import (
    OVERLAY_FNS,
    build_rows,
    enrich,
    score_overlay,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_source_aware_fv_robustness_audit_latest.json"
OUT_MD = OUT_DIR / "v28_source_aware_fv_robustness_audit_latest.md"

EXPECTED_OVERLAY = "source_aware_approved_book_target_logit125_p60_only"
MIN_LOMO_SETTLED = 25


def settled_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("side_won") is not None]


def score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return enrich([score_overlay(rows, name, fn) for name, fn in OVERLAY_FNS.items()])


def get_overlay(scored: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return next((row for row in scored if row.get("overlay") == name), {})


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def leave_one_market_out(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    markets = sorted({str(row.get("market")) for row in rows if row.get("market")})
    out = []
    for market in markets:
        kept = [row for row in rows if str(row.get("market")) != market]
        scored = score_rows(kept)
        expected = get_overlay(scored, EXPECTED_OVERLAY)
        best = scored[0] if scored else {}
        brier_delta = as_float(expected.get("brier_delta_vs_raw"))
        logloss_delta = as_float(expected.get("logloss_delta_vs_raw"))
        out.append({
            "removed_market": market,
            "kept_settled": expected.get("settled"),
            "best_overlay": best.get("overlay"),
            "expected_rank": 1 + next((idx for idx, row in enumerate(scored) if row.get("overlay") == EXPECTED_OVERLAY), -1),
            "expected_brier_delta_vs_raw": brier_delta,
            "expected_logloss_delta_vs_raw": logloss_delta,
            "passes": (
                int(expected.get("settled") or 0) >= MIN_LOMO_SETTLED
                and brier_delta is not None
                and brier_delta < 0.0
                and logloss_delta is not None
                and logloss_delta < 0.0
            ),
        })
    return out


def source_slices(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = sorted({str(row.get("source") or "unknown") for row in rows})
    out = []
    for source in sources:
        source_rows = [row for row in rows if str(row.get("source") or "unknown") == source]
        scored = score_rows(source_rows)
        expected = get_overlay(scored, EXPECTED_OVERLAY)
        best = scored[0] if scored else {}
        out.append({
            "source": source,
            "settled": expected.get("settled"),
            "best_overlay": best.get("overlay"),
            "expected_rank": 1 + next((idx for idx, row in enumerate(scored) if row.get("overlay") == EXPECTED_OVERLAY), -1),
            "expected_brier_delta_vs_raw": expected.get("brier_delta_vs_raw"),
            "expected_logloss_delta_vs_raw": expected.get("logloss_delta_vs_raw"),
            "best_brier_delta_vs_raw": best.get("brier_delta_vs_raw"),
            "best_logloss_delta_vs_raw": best.get("logloss_delta_vs_raw"),
        })
    return out


def contribution_by_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full = get_overlay(score_rows(rows), EXPECTED_OVERLAY)
    full_delta = as_float(full.get("brier_delta_vs_raw")) or 0.0
    records = []
    for item in leave_one_market_out(rows):
        after = as_float(item.get("expected_brier_delta_vs_raw"))
        if after is None:
            continue
        # More positive contribution means removing the market weakens the gain.
        records.append({
            "market": item["removed_market"],
            "brier_delta_contribution": after - full_delta,
            "kept_brier_delta_vs_raw": after,
        })
    records.sort(key=lambda row: abs(float(row["brier_delta_contribution"])), reverse=True)
    return records


def build_report() -> dict[str, Any]:
    rows = settled_rows(build_rows())
    scored = score_rows(rows)
    expected = get_overlay(scored, EXPECTED_OVERLAY)
    lomo = leave_one_market_out(rows)
    slices = source_slices(rows)
    contributions = contribution_by_market(rows)
    fail_lomo = [row for row in lomo if not row.get("passes")]
    dominant = contributions[0] if contributions else {}
    dominant_abs = abs(float(dominant.get("brier_delta_contribution") or 0.0))
    full_abs = abs(float(expected.get("brier_delta_vs_raw") or 0.0))
    dominant_share = dominant_abs / full_abs if full_abs else None
    blockers = []
    if fail_lomo:
        blockers.append("leave_one_market_failure")
    if dominant_share is not None and dominant_share > 0.50:
        blockers.append("single_market_contribution_gt_50pct")
    return {
        "overlay": EXPECTED_OVERLAY,
        "settled": expected.get("settled"),
        "full_brier_delta_vs_raw": expected.get("brier_delta_vs_raw"),
        "full_logloss_delta_vs_raw": expected.get("logloss_delta_vs_raw"),
        "leave_one_market_failures": len(fail_lomo),
        "dominant_market_brier_delta_share": dominant_share,
        "blockers": blockers,
        "leave_one_market": lomo,
        "source_slices": slices,
        "top_market_contributions": contributions[:10],
        "interpretation": current_read(expected, fail_lomo, dominant_share, slices),
    }


def current_read(
    expected: dict[str, Any],
    fail_lomo: list[dict[str, Any]],
    dominant_share: float | None,
    slices: list[dict[str, Any]],
) -> list[str]:
    notes = [
        f"Full source-aware overlay Brier/logloss deltas are {expected.get('brier_delta_vs_raw')}/{expected.get('logloss_delta_vs_raw')}.",
        f"Leave-one-market failures: {len(fail_lomo)}.",
    ]
    if dominant_share is not None:
        notes.append(f"Largest single-market absolute Brier-delta contribution share is {dominant_share:.2%}.")
    for row in slices:
        notes.append(
            f"Source slice {row.get('source')} best overlay is {row.get('best_overlay')} with expected source-aware rank {row.get('expected_rank')}."
        )
    return notes


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
        "# v28 Source-Aware FV Robustness Audit",
        "",
        "Research-only perturbation audit for the source-aware FV overlay.",
        "",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Settled: `{report.get('settled')}`",
        f"- Full Brier/logloss delta vs raw: `{fmt(report.get('full_brier_delta_vs_raw'))}/{fmt(report.get('full_logloss_delta_vs_raw'))}`",
        f"- Leave-one-market failures: `{report.get('leave_one_market_failures')}`",
        f"- Dominant market Brier-delta share: `{fmt(report.get('dominant_market_brier_delta_share'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Source Slices",
        "",
        "| source | settled | best overlay | source-aware rank | d brier | d logloss |",
        "|---|---:|---|---:|---:|---:|",
    ])
    for row in report.get("source_slices") or []:
        lines.append(
            f"| {row.get('source')} | {row.get('settled')} | `{row.get('best_overlay')}` | "
            f"{row.get('expected_rank')} | {fmt(row.get('expected_brier_delta_vs_raw'))} | "
            f"{fmt(row.get('expected_logloss_delta_vs_raw'))} |"
        )
    lines.extend([
        "",
        "## Top Market Contributions",
        "",
        "| market | contribution | kept d brier |",
        "|---|---:|---:|",
    ])
    for row in report.get("top_market_contributions") or []:
        lines.append(
            f"| `{row.get('market')}` | {fmt(row.get('brier_delta_contribution'))} | {fmt(row.get('kept_brier_delta_vs_raw'))} |"
        )
    lines.extend([
        "",
        "## Leave-One-Market",
        "",
        "| removed market | kept settled | best overlay | source-aware rank | d brier | d logloss | pass |",
        "|---|---:|---|---:|---:|---:|---:|",
    ])
    for row in report.get("leave_one_market") or []:
        lines.append(
            f"| `{row.get('removed_market')}` | {row.get('kept_settled')} | `{row.get('best_overlay')}` | "
            f"{row.get('expected_rank')} | {fmt(row.get('expected_brier_delta_vs_raw'))} | "
            f"{fmt(row.get('expected_logloss_delta_vs_raw'))} | {row.get('passes')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
