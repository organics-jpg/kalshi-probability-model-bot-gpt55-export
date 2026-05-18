"""Raw-conviction override diagnostic for v28/RMT forgetting candidates.

The first frozen-forward miss exposed a specific physics question: if raw v28
sees a large executable edge early, should a later book/RMT anchor be allowed to
flip the side? This report measures that path without promoting any rule.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_rmt_forgetting_entry_bakeoff import build_report as build_entry_bakeoff_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_conviction_override_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_raw_conviction_override_diagnostic_latest.md"

RAW_POLICY = "v28_raw_p50_edge0"
COMPARISON_POLICIES = [
    "first_side_raw_later_book_p60_edge0",
    "rmt_repetition_forget_p60_edge0",
    "book_ask_prior_p60_edge0",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def edge_bucket(edge: float | None) -> str:
    if edge is None:
        return "missing_edge"
    if edge >= 0.20:
        return "raw_edge_ge_20pp"
    if edge >= 0.10:
        return "raw_edge_10_20pp"
    if edge >= 0.05:
        return "raw_edge_5_10pp"
    if edge >= 0.00:
        return "raw_edge_0_5pp"
    return "raw_edge_negative"


def stc_bucket(seconds_to_close: float | None) -> str:
    if seconds_to_close is None:
        return "stc_missing"
    if seconds_to_close <= 120:
        return "stc_0_120"
    if seconds_to_close <= 300:
        return "stc_120_300"
    if seconds_to_close <= 600:
        return "stc_300_600"
    return "stc_gt_600"


def gross_after_fee(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    if value is not None:
        return value
    return as_float(row.get("gross_cents"))


def summarize_bucket(rows: list[dict[str, Any]], bucket_name: str) -> dict[str, Any]:
    settled = [row for row in rows if row.get("raw_side_won") is not None]
    raw_net = sum(float(row.get("raw_net_cents") or 0.0) for row in settled)
    alt_net = sum(float(row.get("alt_net_cents") or 0.0) for row in settled if row.get("alt_net_cents") is not None)
    alt_settled = [row for row in settled if row.get("alt_side_won") is not None]
    return {
        "bucket": bucket_name,
        "count": len(rows),
        "settled": len(settled),
        "raw_wins": sum(1 for row in settled if row.get("raw_side_won") is True),
        "raw_losses": sum(1 for row in settled if row.get("raw_side_won") is False),
        "raw_net_cents": raw_net,
        "raw_avg_net_cents": raw_net / len(settled) if settled else None,
        "alt_settled": len(alt_settled),
        "alt_wins": sum(1 for row in alt_settled if row.get("alt_side_won") is True),
        "alt_losses": sum(1 for row in alt_settled if row.get("alt_side_won") is False),
        "alt_net_cents": alt_net,
        "alt_avg_net_cents": alt_net / len(alt_settled) if alt_settled else None,
        "alt_minus_raw_cents": alt_net - raw_net if alt_settled else None,
    }


def build_report() -> dict[str, Any]:
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    by_policy_market = {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {RAW_POLICY, *COMPARISON_POLICIES}
    }
    markets = sorted({market for policy, market in by_policy_market if policy == RAW_POLICY and market})
    comparisons: list[dict[str, Any]] = []
    for market in markets:
        raw = by_policy_market.get((RAW_POLICY, market))
        if not raw:
            continue
        raw_edge = as_float(raw.get("eff_edge_prob"))
        raw_stc = as_float(raw.get("seconds_to_close"))
        for alt_policy in COMPARISON_POLICIES:
            alt = by_policy_market.get((alt_policy, market))
            same_side = bool(alt and alt.get("side") == raw.get("side"))
            status = "alt_missed"
            if alt:
                status = "same_side" if same_side else "side_flip"
            comparisons.append({
                "market": market,
                "alt_policy": alt_policy,
                "status": status,
                "raw_side": raw.get("side"),
                "alt_side": alt.get("side") if alt else None,
                "raw_edge": raw_edge,
                "raw_edge_bucket": edge_bucket(raw_edge),
                "raw_stc": raw_stc,
                "raw_stc_bucket": stc_bucket(raw_stc),
                "raw_p_eff": raw.get("p_eff"),
                "raw_ask": raw.get("ask_prob"),
                "raw_source": raw.get("source"),
                "raw_spectral_tag": raw.get("spectral_tag"),
                "raw_recross_hazard": raw.get("h6_recross_hazard_high"),
                "raw_abs_d_sigma": raw.get("abs_d_sigma"),
                "alt_edge": alt.get("eff_edge_prob") if alt else None,
                "alt_p_eff": alt.get("p_eff") if alt else None,
                "alt_ask": alt.get("ask_prob") if alt else None,
                "alt_source": alt.get("source") if alt else None,
                "alt_delay_seconds": (
                    None
                    if not alt or not raw.get("ts_wall") or not alt.get("ts_wall")
                    else None
                ),
                "raw_side_won": raw.get("side_won"),
                "alt_side_won": alt.get("side_won") if alt else None,
                "raw_net_cents": gross_after_fee(raw),
                "alt_net_cents": gross_after_fee(alt) if alt else None,
            })
    return {
        "raw_policy": RAW_POLICY,
        "comparison_policies": COMPARISON_POLICIES,
        "summary": summarize(comparisons),
        "rows": comparisons,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_alt_status: list[dict[str, Any]] = []
    by_raw_edge_bucket: list[dict[str, Any]] = []
    by_status_edge: list[dict[str, Any]] = []
    by_stc: list[dict[str, Any]] = []
    by_recross: list[dict[str, Any]] = []
    for alt_policy in COMPARISON_POLICIES:
        policy_rows = [row for row in rows if row.get("alt_policy") == alt_policy]
        for status in ["same_side", "side_flip", "alt_missed"]:
            by_alt_status.append(summarize_bucket(
                [row for row in policy_rows if row.get("status") == status],
                f"{alt_policy}:{status}",
            ))
        for bucket in ["raw_edge_ge_20pp", "raw_edge_10_20pp", "raw_edge_5_10pp", "raw_edge_0_5pp", "raw_edge_negative"]:
            by_raw_edge_bucket.append(summarize_bucket(
                [row for row in policy_rows if row.get("raw_edge_bucket") == bucket],
                f"{alt_policy}:{bucket}",
            ))
        for status in ["same_side", "side_flip"]:
            for bucket in ["raw_edge_ge_20pp", "raw_edge_10_20pp", "raw_edge_5_10pp", "raw_edge_0_5pp"]:
                by_status_edge.append(summarize_bucket(
                    [
                        row for row in policy_rows
                        if row.get("status") == status and row.get("raw_edge_bucket") == bucket
                    ],
                    f"{alt_policy}:{status}:{bucket}",
                ))
        for bucket in ["stc_0_120", "stc_120_300", "stc_300_600", "stc_gt_600"]:
            by_stc.append(summarize_bucket(
                [row for row in policy_rows if row.get("raw_stc_bucket") == bucket],
                f"{alt_policy}:{bucket}",
            ))
        for flag in [True, False]:
            by_recross.append(summarize_bucket(
                [row for row in policy_rows if row.get("raw_recross_hazard") is flag],
                f"{alt_policy}:recross_high_{flag}",
            ))
    return {
        "by_alt_status": by_alt_status,
        "by_raw_edge_bucket": by_raw_edge_bucket,
        "by_status_edge": by_status_edge,
        "by_stc": by_stc,
        "by_recross": by_recross,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def add_table(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "",
        f"## {title}",
        "",
        "| bucket | count | settled | raw W/L | raw net c | raw avg c | alt settled | alt W/L | alt net c | alt - raw c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        if not row.get("count"):
            continue
        lines.append(
            f"| {row['bucket']} | {row['count']} | {row['settled']} | {row['raw_wins']}/{row['raw_losses']} | "
            f"{fmt(row['raw_net_cents'])} | {fmt(row['raw_avg_net_cents'])} | {row['alt_settled']} | "
            f"{row['alt_wins']}/{row['alt_losses']} | {fmt(row['alt_net_cents'])} | {fmt(row['alt_minus_raw_cents'])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Raw-Conviction Override Diagnostic",
        "",
        "Shadow-only diagnostic. It tests whether strong raw v28 executable edge should override later book/RMT side flips.",
        "",
        f"- Raw policy: `{report['raw_policy']}`",
        f"- Comparison policies: `{', '.join(report['comparison_policies'])}`",
    ]
    add_table(lines, "By Later Policy Status", summary["by_alt_status"])
    add_table(lines, "By Raw Edge Bucket", summary["by_raw_edge_bucket"])
    add_table(lines, "By Status And Raw Edge", summary["by_status_edge"])
    add_table(lines, "By Seconds To Close", summary["by_stc"])
    add_table(lines, "By Recross Hazard", summary["by_recross"])
    lines.extend([
        "",
        "## Recent Comparisons",
        "",
        "| market | alt policy | status | raw side | alt side | raw edge | raw stc | recross | raw won | alt won | raw net | alt net |",
        "|---|---|---|---|---|---:|---:|---|---|---|---:|---:|",
    ])
    for row in report["rows"][-45:]:
        lines.append(
            f"| {row.get('market')} | {row.get('alt_policy')} | {row.get('status')} | {row.get('raw_side')} | "
            f"{row.get('alt_side')} | {fmt(row.get('raw_edge'))} | {fmt(row.get('raw_stc'))} | "
            f"{row.get('raw_recross_hazard')} | {row.get('raw_side_won')} | {row.get('alt_side_won')} | "
            f"{fmt(row.get('raw_net_cents'))} | {fmt(row.get('alt_net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
