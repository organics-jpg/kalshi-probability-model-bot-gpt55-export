"""Diagnostic for what raw p52 removes from raw p50.

Raw p52 is currently the best broad discovery challenger. This report makes the
mechanism explicit: which markets raw p50 takes that raw p52 skips, whether the
skips are low-margin noise, and whether that tradeoff survives basic temporal
and physics-tag views.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_delta_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_delta_diagnostic_latest.md"

KEEP_POLICY = "v28_raw_p52_edge0"
BASE_POLICY = "v28_raw_p50_edge0"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    if value is not None:
        return value
    return as_float(row.get("gross_cents"))


def bucket_row(row: dict[str, Any]) -> dict[str, bool]:
    ask = as_float(row.get("ask_prob"))
    edge = as_float(row.get("raw_edge_prob") or row.get("eff_edge_prob"))
    depth = as_float(row.get("eligible_depth"))
    recross = as_float(row.get("recross_hazard_score"))
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return {
        "expensive_ask_ge_75": ask is not None and ask >= 0.75,
        "low_edge_lt_5pp": edge is not None and edge < 0.05,
        "edge_5_10pp": edge is not None and 0.05 <= edge < 0.10,
        "thin_touch_depth": depth is not None and depth < 25.0,
        "crowded_touch_depth": depth is not None and depth > 1300.0,
        "high_recross": recross is not None and recross >= 0.25,
        "near_strike": abs_d is not None and abs_d <= 0.35,
        "long_horizon": stc is not None and stc >= 600.0,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    resolved = [row for row in rows if net(row) is not None]
    total_net = sum(float(net(row) or 0.0) for row in resolved)
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    return {
        "count": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents_after_fee": total_net,
        "avg_net_cents_after_fee": total_net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
    }


def summarize_tags(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for tag in [
        "expensive_ask_ge_75",
        "low_edge_lt_5pp",
        "edge_5_10pp",
        "thin_touch_depth",
        "crowded_touch_depth",
        "high_recross",
        "near_strike",
        "long_horizon",
    ]:
        bucket = [row for row in rows if (row.get("tags") or {}).get(tag)]
        out.append({"tag": tag, **summarize(bucket)})
    return out


def build_report() -> dict[str, Any]:
    payload = build_raw_physics_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    by_policy_market = {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {BASE_POLICY, KEEP_POLICY}
    }
    base_markets = sorted({market for policy, market in by_policy_market if policy == BASE_POLICY and market})
    kept: list[dict[str, Any]] = []
    kept_candidate_rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    for market in base_markets:
        base = by_policy_market.get((BASE_POLICY, market))
        keep = by_policy_market.get((KEEP_POLICY, market))
        if not base:
            continue
        row = {**base, "tags": bucket_row(base), "kept_by_p52": keep is not None}
        if keep is None:
            skipped.append(row)
        else:
            kept.append(row)
            kept_candidate_rows.append({**keep, "tags": bucket_row(keep), "base_row": base})
            if keep.get("side") != base.get("side") or keep.get("ts_wall") != base.get("ts_wall"):
                base_net = net(base)
                p52_net = net(keep)
                changed.append({
                    **row,
                    "p52_row": keep,
                    "base_net_cents": base_net,
                    "p52_net_cents": p52_net,
                    "p52_minus_base_net_cents": (
                        None if base_net is None or p52_net is None else float(p52_net) - float(base_net)
                    ),
                    "base_won": base.get("side_won"),
                    "p52_won": keep.get("side_won"),
                })
    return {
        "base_policy": BASE_POLICY,
        "keep_policy": KEEP_POLICY,
        "summary": {
            "base": summarize(kept + skipped),
            "base_rows_kept_by_p52": summarize(kept),
            "actual_p52_rows": summarize(kept_candidate_rows),
            "skipped_by_p52": summarize(skipped),
            "changed_selection_count": len(changed),
            "changed_selection_net_delta_cents": sum(
                float(row.get("p52_minus_base_net_cents") or 0.0)
                for row in changed
                if row.get("p52_minus_base_net_cents") is not None
            ),
        },
        "skipped_tag_summary": summarize_tags(skipped),
        "base_kept_tag_summary": summarize_tags(kept),
        "actual_p52_tag_summary": summarize_tags(kept_candidate_rows),
        "skipped_rows": skipped,
        "changed_rows": changed,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Raw p52 Delta Diagnostic",
        "",
        f"- Base policy: `{report['base_policy']}`",
        f"- Candidate policy: `{report['keep_policy']}`",
        "",
        "## Summary",
        "",
        "| bucket | count | settled | W/L | net c | avg c | brier |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in report["summary"].items():
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| {name} | {row['count']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['net_cents_after_fee'])} | {fmt(row['avg_net_cents_after_fee'])} | {fmt(row['avg_brier'])} |"
        )
    lines.append(f"- Changed p52 selections among kept markets: `{report['summary']['changed_selection_count']}`")
    lines.append(f"- Changed-selection net delta: `{fmt(report['summary']['changed_selection_net_delta_cents'])}c`")
    lines.extend([
        "",
        "## Skipped Tag Summary",
        "",
        "| tag | count | settled | W/L | net c | avg c | brier |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["skipped_tag_summary"]:
        if not row["count"]:
            continue
        lines.append(
            f"| {row['tag']} | {row['count']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['net_cents_after_fee'])} | {fmt(row['avg_net_cents_after_fee'])} | {fmt(row['avg_brier'])} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | side | source | p | ask | edge | depth | recross | stc | won | net c | tags |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report["skipped_rows"]:
        tags = ",".join(key for key, value in (row.get("tags") or {}).items() if value)
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {fmt(row.get('p_eff'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('eff_edge_prob'))} | {fmt(row.get('eligible_depth'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{row.get('side_won')} | {fmt(net(row))} | {tags} |"
        )
    lines.extend([
        "",
        "## Changed Selections",
        "",
        "| market | base side | p52 side | base p | p52 p | base ask | p52 ask | base net | p52 net | delta | base won | p52 won |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report["changed_rows"]:
        p52 = row.get("p52_row") or {}
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {p52.get('side')} | "
            f"{fmt(row.get('p_eff'))} | {fmt(p52.get('p_eff'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(p52.get('ask_prob'))} | "
            f"{fmt(row.get('base_net_cents'))} | {fmt(row.get('p52_net_cents'))} | "
            f"{fmt(row.get('p52_minus_base_net_cents'))} | {row.get('base_won')} | {row.get('p52_won')} |"
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
