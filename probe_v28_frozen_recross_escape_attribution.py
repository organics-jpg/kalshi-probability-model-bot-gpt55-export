"""Forward-only attribution for the p52 recross-escape challenger.

Research-only. This does not change live bot logic or place orders.

The recross/RMT/forgetting work is only useful if it localizes a physical
state. This report breaks the frozen challenger into predeclared buckets so a
small aggregate P&L win cannot hide a bad regime.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_recross_escape_probability_calibration import TRANSFORMS, logloss


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_RECROSS_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_recross_escape_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_recross_escape_attribution_latest.md"
POLICY = "p52_recross_escape_opp240_oppedge5_keep"
BASE_POLICY = "v28_raw_p52_edge0_base"


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


def rows_for_policy(payload: dict[str, Any], policy: str) -> list[dict[str, Any]]:
    for item in payload.get("summary") or []:
        if item.get("policy") == policy:
            rows = item.get("selected_forward_rows")
            return rows if isinstance(rows, list) else []
    return []


def settled(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("side_won") is not None]


def row_net(row: dict[str, Any]) -> float:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    return value if value is not None else 0.0


def row_bucket_tags(row: dict[str, Any]) -> list[str]:
    tags = ["all"]
    mode = str(row.get("mode") or "unknown")
    tags.append(f"mode:{mode}")

    source = str(row.get("source") or "unknown")
    tags.append(f"source:{source}")

    stc = as_float(row.get("seconds_to_close"))
    if stc is None:
        tags.append("stc:unknown")
    elif stc <= 120.0:
        tags.append("stc:late_lte120")
    elif stc <= 360.0:
        tags.append("stc:mid_120_360")
    else:
        tags.append("stc:early_gt360")

    p_eff = as_float(row.get("p_eff"))
    if p_eff is None:
        tags.append("p:unknown")
    elif p_eff < 0.60:
        tags.append("p:weak_52_60")
    elif p_eff < 0.70:
        tags.append("p:solid_60_70")
    else:
        tags.append("p:strong_ge70")

    edge = as_float(row.get("eff_edge_prob"))
    if edge is None:
        tags.append("edge:unknown")
    elif edge < 0.02:
        tags.append("edge:thin_lt2pp")
    elif edge < 0.05:
        tags.append("edge:modest_2_5pp")
    else:
        tags.append("edge:wide_ge5pp")

    ask = as_float(row.get("ask_prob"))
    if ask is None:
        tags.append("ask:unknown")
    elif ask <= 0.55:
        tags.append("ask:cheap_lte55")
    elif ask <= 0.70:
        tags.append("ask:mid_55_70")
    else:
        tags.append("ask:expensive_gt70")

    return tags


def summarize_rows(rows: list[dict[str, Any]], probability_name: str = "raw_probability") -> dict[str, Any]:
    done = settled(rows)
    fn = TRANSFORMS[probability_name]
    probs = [fn(row) for row in done]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in done]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    return {
        "entries": len(rows),
        "settled": len(done),
        "wins": sum(1 for row in done if row.get("side_won") is True),
        "losses": sum(1 for row in done if row.get("side_won") is False),
        "net_cents": sum(row_net(row) for row in done),
        "avg_p": sum(probs) / len(probs) if probs else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
    }


def tagged_breakdown(rows: list[dict[str, Any]], probability_name: str) -> list[dict[str, Any]]:
    by_tag: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in row_bucket_tags(row):
            by_tag.setdefault(tag, []).append(row)
    breakdown = [
        {"tag": tag, **summarize_rows(tag_rows, probability_name)}
        for tag, tag_rows in sorted(by_tag.items())
    ]
    breakdown.sort(key=lambda item: (str(item["tag"] != "all"), str(item["tag"])))
    return breakdown


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def add_probability_deltas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = summarize_rows(rows, "raw_probability")
    compared: list[dict[str, Any]] = []
    for name in ("raw_probability", "plus03_probability", "plus05_probability", "conservative_mode_probability"):
        item = summarize_rows(rows, name)
        item["probability"] = name
        item["brier_delta_vs_raw"] = delta(item.get("avg_brier"), raw.get("avg_brier"))
        item["logloss_delta_vs_raw"] = delta(item.get("avg_logloss"), raw.get("avg_logloss"))
        compared.append(item)
    return compared


def build_report() -> dict[str, Any]:
    payload = load_json(FROZEN_RECROSS_JSON)
    challenger_rows = rows_for_policy(payload, POLICY)
    base_rows = rows_for_policy(payload, BASE_POLICY)
    return {
        "source_freeze_ts": payload.get("freeze_ts"),
        "source_forward_market_denominator": payload.get("forward_market_denominator"),
        "policy": POLICY,
        "base_policy": BASE_POLICY,
        "challenger": summarize_rows(challenger_rows, "raw_probability"),
        "baseline": summarize_rows(base_rows, "raw_probability"),
        "probability_overlays": add_probability_deltas(challenger_rows),
        "tagged_raw_probability": tagged_breakdown(challenger_rows, "raw_probability"),
        "tagged_plus05_probability": tagged_breakdown(challenger_rows, "plus05_probability"),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Recross-Escape Attribution",
        "",
        "Forward-only attribution for the recross-escape challenger. Rows before the freeze do not count.",
        "",
        f"- Source freeze timestamp UTC: `{report.get('source_freeze_ts')}`",
        f"- Source forward denominator: `{report.get('source_forward_market_denominator')}`",
        f"- Policy: `{report.get('policy')}`",
        "",
        "## Policy Comparison",
        "",
        "| policy | entries | settled | W/L | net c | avg p | brier | logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, key in ((report.get("base_policy"), "baseline"), (report.get("policy"), "challenger")):
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('avg_logloss'))} |"
        )

    lines.extend([
        "",
        "## Probability Overlays On Challenger Rows",
        "",
        "| probability | entries | settled | W/L | avg p | brier | brier d | logloss | logloss d |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("probability_overlays") or []:
        lines.append(
            f"| {row.get('probability')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} |"
        )

    lines.extend([
        "",
        "## Raw Probability By Physical Tag",
        "",
        "| tag | entries | settled | W/L | net c | avg p | brier | logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("tagged_raw_probability") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('avg_logloss'))} |"
        )

    lines.extend([
        "",
        "## Plus05 Probability By Physical Tag",
        "",
        "| tag | entries | settled | W/L | net c | avg p | brier | logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("tagged_plus05_probability") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('avg_logloss'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
