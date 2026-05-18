"""Forward failure-mode registry for v28 entry-policy candidates.

This report intentionally does not search for the best threshold. It groups each
causal policy selection by predeclared physical tags so weak regimes remain
visible as forward evidence accumulates.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
IN_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_policy_failure_modes_latest.json"
OUT_MD = OUT_DIR / "v28_policy_failure_modes_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def physical_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    side = str(row.get("side") or "").lower()
    p_side = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_cents"))
    edge = as_float(row.get("edge_cents"))
    abs_d_sigma = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    seconds_to_close = as_float(row.get("seconds_to_close"))
    depth = as_float(row.get("eligible_depth"))

    if p_side is not None and abs(p_side - 0.50) <= 0.08:
        tags.append("near_coinflip_model")
    if p_side is not None and p_side < 0.45 and ask is not None and ask <= 40.0:
        tags.append("cheap_low_p_side")
    if side == "yes" and p_side is not None and p_side < 0.45:
        tags.append("cheap_yes_boundary_pull")
    if edge is not None and edge < 0.0:
        tags.append("negative_net_edge")
    if recross is not None and recross >= 0.75:
        tags.append("high_recross_hazard")
    if abs_d_sigma is not None and abs_d_sigma < 0.25:
        tags.append("near_strike_low_sigma_distance")
    if seconds_to_close is not None and seconds_to_close >= 720.0:
        tags.append("early_market_long_horizon")
    if seconds_to_close is not None and seconds_to_close <= 180.0:
        tags.append("late_market_short_horizon")
    if depth is not None and depth < 10.0:
        tags.append("thin_touch_depth")
    if p_side is not None and p_side >= 0.65:
        tags.append("high_confidence_side")
    return tags or ["untagged"]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("side_won") is not None]
    wins = sum(1 for row in resolved if row.get("side_won") is True)
    losses = sum(1 for row in resolved if row.get("side_won") is False)
    gross = sum(float(row.get("gross_cents") or 0.0) for row in resolved)
    return {
        "entries": len(rows),
        "resolved": len(resolved),
        "wins": wins,
        "losses": losses,
        "gross_cents": gross,
        "avg_gross_cents": (gross / len(resolved)) if resolved else None,
    }


def build_report() -> dict[str, Any]:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    by_policy: dict[str, list[dict[str, Any]]] = {}
    by_policy_tag: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in rows:
        policy = str(row.get("policy") or "")
        if not policy:
            continue
        by_policy.setdefault(policy, []).append(row)
        tag_map = by_policy_tag.setdefault(policy, {})
        for tag in physical_tags(row):
            tag_map.setdefault(tag, []).append(row)

    policy_summaries = {policy: summarize_rows(policy_rows) for policy, policy_rows in by_policy.items()}
    tag_summaries = {
        policy: {tag: summarize_rows(tag_rows) for tag, tag_rows in sorted(tag_map.items())}
        for policy, tag_map in sorted(by_policy_tag.items())
    }
    loss_rows = [
        row
        for row in rows
        if row.get("side_won") is False
    ]
    for row in loss_rows:
        row["physics_tags"] = ",".join(physical_tags(row))
    return {
        "source": str(IN_JSON),
        "policies": policy_summaries,
        "policy_tag_summaries": tag_summaries,
        "loss_rows": loss_rows,
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Policy Failure Modes",
        "",
        "- Scope: causal policy selections from the latest entry bakeoff.",
        "- Purpose: expose physical regimes that create losses or fragile wins without threshold hunting.",
        "",
        "## Loss Rows",
        "",
    ]
    if report["loss_rows"]:
        lines.append("| policy | market | side | p | ask | edge c | abs d sigma | recross | stc | gross c | tags |")
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for row in report["loss_rows"][-40:]:
            lines.append(
                "| {policy} | {market} | {side} | {p_side} | {ask_cents} | {edge_cents} | {abs_d_sigma} | {recross_hazard_score} | {seconds_to_close} | {gross_cents} | {physics_tags} |".format(
                    **row
                )
            )
    else:
        lines.append("No resolved loss rows yet.")
    lines.extend(["", "## Tag Summaries", ""])
    for policy, tag_map in report["policy_tag_summaries"].items():
        lines.extend([f"### {policy}", ""])
        lines.append("| tag | entries | resolved | wins | losses | gross c | avg gross c |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        ranked = sorted(
            tag_map.items(),
            key=lambda item: (-(item[1]["losses"]), item[1]["gross_cents"], item[0]),
        )
        for tag, summary in ranked:
            lines.append(
                f"| {tag} | {summary['entries']} | {summary['resolved']} | {summary['wins']} | {summary['losses']} | {summary['gross_cents']} | {summary['avg_gross_cents']} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
