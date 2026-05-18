"""EV breakeven attribution for v28 candidate surfaces.

Research-only; no live bot changes or orders.

Purpose:
    Probability accuracy is not enough when contract payoff is asymmetric.
    A favorite can win often and still lose money if its win rate is below
    executable ask plus fees. This probe separates directional error from
    price/friction error for the current broad candidate families.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report
from probe_v28_shadow_entry_policy_bakeoff import build_report as build_entry_policy_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_ev_breakeven_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_ev_breakeven_attribution_latest.md"

POLICIES = [
    "v28_raw_p52_edge0",
    "v28_raw_p50_edge0",
    "book_plus_05_no_cheap_yes_boundary",
    "book_plus_03_cheap_convex",
    "p50_book_plus_05_edge_nonnegative",
    "baseline_v28_approved",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        ask = as_float(row.get("ask"))
    if ask is None:
        return None
    return ask if ask <= 1.0 else ask / 100.0


def net_cents(row: dict[str, Any]) -> float | None:
    for key in ["net_gross_cents_after_entry_fee", "gross_cents", "gross_c"]:
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def p_eff(row: dict[str, Any]) -> float | None:
    for key in ["p_eff", "p", "p_raw"]:
        value = as_float(row.get(key))
        if value is not None:
            return value if value <= 1.0 else value / 100.0
    return None


def side_won(row: dict[str, Any]) -> bool | None:
    value = row.get("side_won")
    if value is None:
        result = row.get("result")
        side = row.get("side")
        if result is None or side is None:
            return None
        return str(result).lower() == str(side).lower()
    return bool(value)


def ask_bucket(ask: float | None) -> str:
    if ask is None:
        return "ask_unknown"
    if ask < 0.45:
        return "ask_lt45"
    if ask < 0.55:
        return "ask45_55"
    if ask < 0.65:
        return "ask55_65"
    if ask < 0.75:
        return "ask65_75"
    if ask < 0.85:
        return "ask75_85"
    return "ask_ge85"


def edge_bucket(row: dict[str, Any]) -> str:
    ask = ask_prob(row)
    p = p_eff(row)
    if ask is None or p is None:
        return "edge_unknown"
    edge = p - ask
    if edge < 0.02:
        return "edge_lt2pp"
    if edge < 0.04:
        return "edge2_4pp"
    if edge < 0.08:
        return "edge4_8pp"
    return "edge_ge8pp"


def physics_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    ask = ask_prob(row)
    p = p_eff(row)
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    stc = as_float(row.get("seconds_to_close")) or as_float(row.get("stc")) or 0.0
    if ask is not None and ask < 0.55:
        tags.append("cheap_ask")
    if ask is not None and ask >= 0.75:
        tags.append("expensive_ask")
    if p is not None and p < 0.60:
        tags.append("weak_probability")
    if abs_d <= 0.25:
        tags.append("near_boundary")
    if recross >= 0.80:
        tags.append("high_recross")
    if stc >= 720.0:
        tags.append("early_long_horizon")
    if edge_bucket(row) in {"edge_lt2pp", "edge2_4pp"}:
        tags.append("thin_edge")
    return tags or ["untagged"]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if side_won(row) is not None and net_cents(row) is not None]
    wins = sum(1 for row in settled if side_won(row) is True)
    losses = sum(1 for row in settled if side_won(row) is False)
    net = sum(float(net_cents(row) or 0.0) for row in settled)
    avg_ask = avg(ask_prob(row) for row in settled)
    avg_p = avg(p_eff(row) for row in settled)
    win_rate = wins / len(settled) if settled else None
    # Approximate breakeven probability before maker/taker details. Fees are
    # already included in net where available, so this is the price geometry.
    breakeven_gap = None
    if win_rate is not None and avg_ask is not None:
        breakeven_gap = win_rate - avg_ask
    direction_wrong_net = sum(float(net_cents(row) or 0.0) for row in settled if side_won(row) is False)
    side_won_net = sum(float(net_cents(row) or 0.0) for row in settled if side_won(row) is True)
    side_won_negative = [row for row in settled if side_won(row) is True and float(net_cents(row) or 0.0) < 0.0]
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_p": avg_p,
        "avg_ask": avg_ask,
        "win_rate_minus_avg_ask": breakeven_gap,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "direction_wrong_net_cents": direction_wrong_net,
        "side_won_net_cents": side_won_net,
        "side_won_negative_count": len(side_won_negative),
        "side_won_negative_net_cents": sum(float(net_cents(row) or 0.0) for row in side_won_negative),
    }


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def grouped(rows: list[dict[str, Any]], key_fn: Any) -> list[dict[str, Any]]:
    by_key: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_key.setdefault(key_fn(row), []).append(row)
    out = []
    for key, group in by_key.items():
        out.append({"bucket": key, **summarize_rows(group)})
    return sorted(out, key=lambda item: float(item.get("net_cents") or 0.0))


def tag_grouped(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_tag: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in physics_tags(row):
            by_tag.setdefault(tag, []).append(row)
    out = []
    for tag, group in by_tag.items():
        out.append({"tag": tag, **summarize_rows(group)})
    return sorted(out, key=lambda item: float(item.get("net_cents") or 0.0))


def all_policy_rows() -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    raw_report = build_raw_physics_report()
    for row in raw_report.get("rows") or []:
        policy = str(row.get("policy") or "")
        if policy in POLICIES:
            out.setdefault(policy, []).append(row)
    entry_report = build_entry_policy_report()
    for row in entry_report.get("rows") or []:
        policy = str(row.get("policy") or "")
        if policy in POLICIES:
            out.setdefault(policy, []).append(row)
    return out


def build_report() -> dict[str, Any]:
    policy_rows = all_policy_rows()
    policies = []
    details = {}
    for policy in POLICIES:
        rows = policy_rows.get(policy, [])
        summary = {"policy": policy, **summarize_rows(rows)}
        policies.append(summary)
        details[policy] = {
            "ask_buckets": grouped(rows, lambda row: ask_bucket(ask_prob(row))),
            "edge_buckets": grouped(rows, edge_bucket),
            "physics_tags": tag_grouped(rows),
        }
    return {
        "policies": sorted(policies, key=lambda item: float(item.get("net_cents") or -10**9), reverse=True),
        "details": details,
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 EV Breakeven Attribution",
        "",
        "Separates side-probability accuracy from executable price geometry.",
        "",
        "## Policy Summary",
        "",
        "| policy | entries | settled | W/L | win rate | avg p | avg ask | win-ask | net c | wrong-side c | won-side c | won-side neg |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("policies") or []:
        lines.append(
            f"| {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('avg_p'))} | {fmt(row.get('avg_ask'))} | "
            f"{fmt(row.get('win_rate_minus_avg_ask'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('direction_wrong_net_cents'))} | {fmt(row.get('side_won_net_cents'))} | "
            f"{row.get('side_won_negative_count')} / {fmt(row.get('side_won_negative_net_cents'))} |"
        )
    for policy in [row.get("policy") for row in report.get("policies") or []]:
        detail = (report.get("details") or {}).get(policy, {})
        lines.extend(["", f"## {policy}", "", "### Worst Physics Tags", "", "| tag | settled | W/L | avg ask | win-ask | net c | wrong-side c |", "|---|---:|---:|---:|---:|---:|---:|"])
        for row in (detail.get("physics_tags") or [])[:10]:
            lines.append(
                f"| {row.get('tag')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('avg_ask'))} | {fmt(row.get('win_rate_minus_avg_ask'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('direction_wrong_net_cents'))} |"
            )
        lines.extend(["", "### Ask Buckets", "", "| bucket | settled | W/L | avg ask | win-ask | net c |", "|---|---:|---:|---:|---:|---:|"])
        for row in detail.get("ask_buckets") or []:
            lines.append(
                f"| {row.get('bucket')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('avg_ask'))} | {fmt(row.get('win_rate_minus_avg_ask'))} | {fmt(row.get('net_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
