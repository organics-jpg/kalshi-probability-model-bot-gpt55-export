"""Confirmation-path diagnostic for raw p52 vs raw p50.

Raw p52 sometimes selects a later row than raw p50 in the same market. This
report explains that wait: whether it flips side, pays more for confirmation,
or improves probability/geometry enough to justify the delay. Shadow-only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_confirmation_path_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_confirmation_path_latest.md"
BASE_POLICY = "v28_raw_p50_edge0"
CONFIRM_POLICY = "v28_raw_p52_edge0"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def net(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    if value is not None:
        return value
    return as_float(row.get("gross_cents"))


def brier(row: dict[str, Any]) -> float | None:
    if row.get("side_won") is None or row.get("p_eff") is None:
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return (float(row["p_eff"]) - outcome) ** 2


def delay_seconds(base: dict[str, Any], confirm: dict[str, Any]) -> float | None:
    base_ts = parse_ts(base.get("ts_wall"))
    confirm_ts = parse_ts(confirm.get("ts_wall"))
    if base_ts is None or confirm_ts is None:
        return None
    return (confirm_ts - base_ts).total_seconds()


def classify_path(base: dict[str, Any], confirm: dict[str, Any]) -> str:
    if confirm.get("side") != base.get("side"):
        return "side_flip_confirmation"
    base_ask = as_float(base.get("ask_prob"))
    confirm_ask = as_float(confirm.get("ask_prob"))
    base_p = as_float(base.get("p_eff"))
    confirm_p = as_float(confirm.get("p_eff"))
    if base_ask is not None and confirm_ask is not None and confirm_ask > base_ask + 0.02:
        if base_p is not None and confirm_p is not None and confirm_p > base_p + 0.02:
            return "pay_up_for_probability_confirmation"
        return "pay_up_without_probability_confirmation"
    if base_p is not None and confirm_p is not None and confirm_p > base_p + 0.02:
        return "probability_confirmation_same_price"
    return "minor_wait"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("base_net_cents") is not None and row.get("confirm_net_cents") is not None]
    delta = sum(float(row.get("confirm_minus_base_net_cents") or 0.0) for row in resolved)
    base_net = sum(float(row.get("base_net_cents") or 0.0) for row in resolved)
    confirm_net = sum(float(row.get("confirm_net_cents") or 0.0) for row in resolved)
    return {
        "count": len(rows),
        "resolved": len(resolved),
        "base_wins": sum(1 for row in resolved if row.get("base_won") is True),
        "confirm_wins": sum(1 for row in resolved if row.get("confirm_won") is True),
        "base_net_cents": base_net,
        "confirm_net_cents": confirm_net,
        "confirm_minus_base_net_cents": delta,
        "avg_delay_seconds": (
            sum(float(row["delay_seconds"]) for row in rows if row.get("delay_seconds") is not None)
            / max(1, sum(1 for row in rows if row.get("delay_seconds") is not None))
            if rows else None
        ),
        "avg_base_brier": avg(row.get("base_brier") for row in resolved),
        "avg_confirm_brier": avg(row.get("confirm_brier") for row in resolved),
    }


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def build_report() -> dict[str, Any]:
    payload = build_raw_physics_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    by_policy_market = {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {BASE_POLICY, CONFIRM_POLICY}
    }
    paths: list[dict[str, Any]] = []
    for _, market in sorted(k for k in by_policy_market if k[0] == BASE_POLICY):
        base = by_policy_market.get((BASE_POLICY, market))
        confirm = by_policy_market.get((CONFIRM_POLICY, market))
        if not base or not confirm:
            continue
        changed = base.get("ts_wall") != confirm.get("ts_wall") or base.get("side") != confirm.get("side")
        if not changed:
            continue
        base_p = as_float(base.get("p_eff"))
        confirm_p = as_float(confirm.get("p_eff"))
        base_ask = as_float(base.get("ask_prob"))
        confirm_ask = as_float(confirm.get("ask_prob"))
        base_net = net(base)
        confirm_net = net(confirm)
        paths.append({
            "market": market,
            "path_type": classify_path(base, confirm),
            "base_side": base.get("side"),
            "confirm_side": confirm.get("side"),
            "delay_seconds": delay_seconds(base, confirm),
            "base_ts": base.get("ts_wall"),
            "confirm_ts": confirm.get("ts_wall"),
            "base_p": base_p,
            "confirm_p": confirm_p,
            "delta_p": None if base_p is None or confirm_p is None else confirm_p - base_p,
            "base_ask": base_ask,
            "confirm_ask": confirm_ask,
            "delta_ask": None if base_ask is None or confirm_ask is None else confirm_ask - base_ask,
            "base_edge": as_float(base.get("eff_edge_prob")),
            "confirm_edge": as_float(confirm.get("eff_edge_prob")),
            "base_won": base.get("side_won"),
            "confirm_won": confirm.get("side_won"),
            "base_net_cents": base_net,
            "confirm_net_cents": confirm_net,
            "confirm_minus_base_net_cents": (
                None if base_net is None or confirm_net is None else float(confirm_net) - float(base_net)
            ),
            "base_brier": brier(base),
            "confirm_brier": brier(confirm),
            "base_recross": base.get("recross_hazard_score"),
            "confirm_recross": confirm.get("recross_hazard_score"),
            "base_abs_d_sigma": base.get("abs_d_sigma"),
            "confirm_abs_d_sigma": confirm.get("abs_d_sigma"),
        })
    by_type: list[dict[str, Any]] = []
    for path_type in sorted({row["path_type"] for row in paths}):
        by_type.append({"path_type": path_type, **summarize([row for row in paths if row["path_type"] == path_type])})
    return {
        "base_policy": BASE_POLICY,
        "confirm_policy": CONFIRM_POLICY,
        "summary": summarize(paths),
        "by_path_type": by_type,
        "rows": paths,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    s = report["summary"]
    lines = [
        "# v28 Raw p52 Confirmation Path",
        "",
        f"- Base policy: `{report['base_policy']}`",
        f"- Confirmation policy: `{report['confirm_policy']}`",
        "",
        "## Summary",
        "",
        f"- Changed paths: `{s['count']}`",
        f"- Resolved changed paths: `{s['resolved']}`",
        f"- Base W/net: `{s['base_wins']}/{s['base_net_cents']}c`",
        f"- Confirm W/net: `{s['confirm_wins']}/{s['confirm_net_cents']}c`",
        f"- Confirm minus base: `{fmt(s['confirm_minus_base_net_cents'])}c`",
        f"- Avg delay seconds: `{fmt(s['avg_delay_seconds'])}`",
        f"- Avg Brier base/confirm: `{fmt(s['avg_base_brier'])}/{fmt(s['avg_confirm_brier'])}`",
        "",
        "## By Path Type",
        "",
        "| path type | count | resolved | base W | confirm W | base net | confirm net | delta | avg delay | brier base/confirm |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["by_path_type"]:
        lines.append(
            f"| {row['path_type']} | {row['count']} | {row['resolved']} | {row['base_wins']} | {row['confirm_wins']} | "
            f"{fmt(row['base_net_cents'])} | {fmt(row['confirm_net_cents'])} | {fmt(row['confirm_minus_base_net_cents'])} | "
            f"{fmt(row['avg_delay_seconds'])} | {fmt(row['avg_base_brier'])}/{fmt(row['avg_confirm_brier'])} |"
        )
    lines.extend([
        "",
        "## Changed Rows",
        "",
        "| market | type | base side | confirm side | delay | base p | confirm p | base ask | confirm ask | base net | confirm net | delta | base won | confirm won |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report["rows"]:
        lines.append(
            f"| {row['market']} | {row['path_type']} | {row['base_side']} | {row['confirm_side']} | "
            f"{fmt(row['delay_seconds'])} | {fmt(row['base_p'])} | {fmt(row['confirm_p'])} | "
            f"{fmt(row['base_ask'])} | {fmt(row['confirm_ask'])} | {fmt(row['base_net_cents'])} | "
            f"{fmt(row['confirm_net_cents'])} | {fmt(row['confirm_minus_base_net_cents'])} | "
            f"{row['base_won']} | {row['confirm_won']} |"
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
