"""Forward loss attribution for the target-coverage v28 surface.

Research-only; no live bot changes or orders.

The target-coverage FV overlay is closest to the user's required 75-80% market
participation. This report explains its forward P&L failures by physical tags
without treating any tag as an optimized rule.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_loss_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_loss_attribution_latest.md"


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


def tags(row: dict[str, Any]) -> list[str]:
    p = as_float(row.get("p_raw"))
    ask = as_float(row.get("ask_prob"))
    edge = as_float(row.get("raw_edge_prob"))
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    side = str(row.get("side") or "").lower()
    out = ["all"]
    if p is not None:
        if p < 0.58:
            out.append("weak_raw_p_lt_58")
        if 0.58 <= p < 0.65:
            out.append("mid_raw_p_58_65")
        if p >= 0.65:
            out.append("high_raw_p_ge_65")
    if ask is not None:
        if ask < 0.55:
            out.append("cheap_ask_lt_55")
        if ask >= 0.70:
            out.append("expensive_ask_ge_70")
    if edge is not None:
        if edge < 0.03:
            out.append("thin_edge_lt_3pp")
        if edge >= 0.10:
            out.append("large_edge_ge_10pp")
    if stc is not None:
        if stc >= 720:
            out.append("early_stc_ge_720")
        if stc <= 180:
            out.append("late_stc_lte_180")
    if abs_d is not None:
        if abs_d <= 0.25:
            out.append("near_strike_absd_lte_025")
        if abs_d >= 0.75:
            out.append("far_from_strike_absd_gte_075")
    if recross is not None:
        if recross >= 0.75:
            out.append("high_recross_ge_075")
        if recross >= 0.90:
            out.append("extreme_recross_ge_090")
    if side in {"yes", "no"}:
        out.append(f"{side}_side")
    reason = str(row.get("coverage_valve_reason") or "")
    if reason:
        out.append(f"reason_{reason}")
    if p is not None and abs_d is not None and recross is not None and p < 0.60 and abs_d <= 0.25 and recross >= 0.75:
        out.append("weak_boundary_turbulence")
    if ask is not None and edge is not None and ask >= 0.70 and edge < 0.05:
        out.append("paid_high_price_thin_edge")
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    gross = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "rows": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents": gross,
        "avg_net_cents": gross / len(settled) if settled else None,
    }


def build_report() -> dict[str, Any]:
    payload = load_json(SOURCE_JSON)
    rows = payload.get("forward_rows") if isinstance(payload.get("forward_rows"), list) else []
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    enriched = []
    for row in rows:
        row_tags = tags(row)
        enriched_row = {**row, "physics_tags": row_tags}
        enriched.append(enriched_row)
        for tag in row_tags:
            by_tag[tag].append(enriched_row)
    tag_rows = [{"tag": tag, **summarize(tagged)} for tag, tagged in by_tag.items()]
    tag_rows.sort(key=lambda item: (float(item.get("net_cents") or 0.0), -int(item.get("settled") or 0), item["tag"]))
    losses = [row for row in enriched if row.get("side_won") is False]
    losses.sort(key=lambda row: float(row.get("net_gross_cents_after_entry_fee") or 0.0))
    return {
        "source": str(SOURCE_JSON),
        "policy": payload.get("policy"),
        "forward_denominator": payload.get("forward_denominator"),
        "forward_summary": (payload.get("forward") or [{}])[0],
        "tag_summaries": tag_rows,
        "loss_rows": losses,
        "interpretation": interpretation(tag_rows, losses),
    }


def interpretation(tag_rows: list[dict[str, Any]], losses: list[dict[str, Any]]) -> list[str]:
    worst = [row for row in tag_rows if row.get("tag") != "all" and int(row.get("settled") or 0) >= 3][:5]
    notes = [
        f"Target-coverage forward loss rows: {len(losses)}.",
        "Worst repeated physical tags are diagnostic only; new rules must be frozen before scoring.",
    ]
    for row in worst:
        notes.append(
            f"{row['tag']}: settled {row['settled']}, W/L {row['wins']}/{row['losses']}, net {row['net_cents']}c."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Target-Coverage Loss Attribution",
        "",
        "Forward-only physical attribution for the current target-coverage surface.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Tag Summaries",
        "",
        "| tag | rows | settled | W/L | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("tag_summaries") or []:
        if int(row.get("settled") or 0) == 0:
            continue
        lines.append(
            f"| {row.get('tag')} | {row.get('rows')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Loss Rows",
        "",
        "| market | side | p | ask | edge | stc | abs d | recross | net c | reason | tags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("loss_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('net_gross_cents_after_entry_fee'))} | "
            f"{row.get('coverage_valve_reason')} | {', '.join(row.get('physics_tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
