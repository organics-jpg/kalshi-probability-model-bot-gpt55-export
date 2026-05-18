"""False-conviction physics audit for the v28 target-coverage surface.

Research-only; no live bot changes or orders.

The current 75% coverage surface is losing mostly through direction-wrong
rows, especially medium raw-edge entries near the strike early in the market.
This probe tests that as an FV failure mode instead of a pure entry filter:
when boundary/recross geometry says the path can easily cross back, raw model
confidence may be too sharp even if the executable edge looks acceptable.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_false_conviction_physics_audit_latest.json"
OUT_MD = OUT_DIR / "v28_false_conviction_physics_audit_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def p_raw(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_eff"))


def ask(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("ask_prob"))
    if value is not None:
        return value
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_edge(row: dict[str, Any]) -> float | None:
    p = p_raw(row)
    a = ask(row)
    return None if p is None or a is None else p - a


def net_cents(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_gross_cents_after_entry_fee")) or 0.0)


def side_won(row: dict[str, Any]) -> bool | None:
    value = row.get("side_won")
    return value if isinstance(value, bool) else None


def forward_rows() -> tuple[list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    selected = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def is_mid_edge_boundary(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        edge is not None
        and 0.04 <= edge < 0.08
        and stc is not None
        and stc >= 720.0
        and abs_d is not None
        and abs_d <= 0.45
        and recross is not None
        and recross >= 0.55
    )


def is_cheap_near_turbulence(row: dict[str, Any]) -> bool:
    a = ask(row)
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        a is not None
        and a < 0.55
        and stc is not None
        and stc >= 720.0
        and abs_d is not None
        and abs_d <= 0.25
        and recross is not None
        and recross >= 0.75
    )


def is_early_no_decay(row: dict[str, Any]) -> bool:
    stc = as_float(row.get("seconds_to_close"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        str(row.get("side") or "").lower() == "no"
        and stc is not None
        and stc >= 660.0
        and abs_d is not None
        and abs_d <= 0.45
        and recross is not None
        and recross >= 0.55
    )


def is_false_conviction_zone(row: dict[str, Any]) -> bool:
    return is_mid_edge_boundary(row) or is_cheap_near_turbulence(row) or is_early_no_decay(row)


MASKS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "mid_edge_boundary_4_8pp": is_mid_edge_boundary,
    "cheap_near_boundary_turbulence": is_cheap_near_turbulence,
    "early_no_boundary_decay": is_early_no_decay,
    "composite_false_conviction_zone": is_false_conviction_zone,
}


def raw_probability(row: dict[str, Any]) -> float:
    p = p_raw(row)
    if p is None:
        raise ValueError("missing p")
    return clamp_prob(p)


def shrink_to_50(row: dict[str, Any], strength: float) -> float:
    p = raw_probability(row)
    return clamp_prob(0.5 + (1.0 - strength) * (p - 0.5))


def shrink_to_book(row: dict[str, Any], strength: float) -> float:
    p = raw_probability(row)
    a = ask(row)
    if a is None:
        return p
    return clamp_prob(p + strength * (a - p))


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw": raw_probability,
    "half_to_50": lambda row: shrink_to_50(row, 0.5),
    "full_to_50": lambda row: shrink_to_50(row, 1.0),
    "half_to_book": lambda row: shrink_to_book(row, 0.5),
    "full_to_book": lambda row: shrink_to_book(row, 1.0),
}


def score_probability(rows: list[dict[str, Any]], fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        won = side_won(row)
        if won is None:
            continue
        try:
            p = fn(row)
        except (TypeError, ValueError):
            continue
        outcome = 1.0 if won else 0.0
        scored.append((p, outcome))
    briers = [(p - outcome) ** 2 for p, outcome in scored]
    losses = [logloss(p, outcome) for p, outcome in scored]
    return {
        "scored": len(scored),
        "avg_p": sum(p for p, _ in scored) / len(scored) if scored else None,
        "win_rate": sum(outcome for _, outcome in scored) / len(scored) if scored else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
    }


def summarize_rows(name: str, rows: list[dict[str, Any]], denominator: int | None = None) -> dict[str, Any]:
    settled = [row for row in rows if side_won(row) is not None]
    wins = [row for row in settled if side_won(row) is True]
    losses = [row for row in settled if side_won(row) is False]
    net = sum(net_cents(row) for row in settled)
    return {
        "name": name,
        "entries": len(rows),
        "settled": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "coverage_pct": None if not denominator else len(rows) / denominator * 100.0,
        "win_rate": len(wins) / len(settled) if settled else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
    }


def adjusted_keep(row: dict[str, Any], adjusted_p: float) -> bool:
    a = ask(row)
    if a is None:
        return False
    return adjusted_p >= 0.60 or adjusted_p - a >= 0.04


def simulate_valve(rows: list[dict[str, Any]], denominator: int, mask: Callable[[dict[str, Any]], bool], overlay: str) -> dict[str, Any]:
    fn = OVERLAYS[overlay]
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for row in rows:
        if not mask(row):
            kept.append(row)
            continue
        try:
            p_adj = fn(row)
        except (TypeError, ValueError):
            kept.append(row)
            continue
        if adjusted_keep(row, p_adj):
            kept.append({**row, "false_conviction_adjusted_p": p_adj})
        else:
            removed.append({**row, "false_conviction_adjusted_p": p_adj})
    kept_summary = summarize_rows(f"{overlay}_kept", kept, denominator)
    removed_summary = summarize_rows(f"{overlay}_removed", removed)
    kept_summary["removed_entries"] = len(removed)
    kept_summary["removed_settled"] = removed_summary["settled"]
    kept_summary["removed_net_cents"] = removed_summary["net_cents"]
    kept_summary["delta_vs_current_net_cents"] = kept_summary["net_cents"] - sum(
        net_cents(row) for row in rows if side_won(row) is not None
    )
    return {
        "overlay": overlay,
        "kept": kept_summary,
        "removed": removed_summary,
        "removed_rows": [compact(row) for row in removed[:20]],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "won": row.get("side_won"),
        "net_cents": net_cents(row),
        "p_raw": p_raw(row),
        "p_adjusted": row.get("false_conviction_adjusted_p"),
        "ask": ask(row),
        "edge": raw_edge(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }


def probability_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = score_probability(rows, OVERLAYS["raw"])
    out = []
    for name, fn in OVERLAYS.items():
        score = score_probability(rows, fn)
        out.append({
            "overlay": name,
            **score,
            "brier_delta_vs_raw": None
            if raw.get("avg_brier") is None or score.get("avg_brier") is None
            else score["avg_brier"] - raw["avg_brier"],
            "logloss_delta_vs_raw": None
            if raw.get("avg_logloss") is None or score.get("avg_logloss") is None
            else score["avg_logloss"] - raw["avg_logloss"],
        })
    return sorted(out, key=lambda row: (float(row.get("avg_brier") or 999), float(row.get("avg_logloss") or 999)))


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    settled = [row for row in rows if side_won(row) is not None]
    mask_reports = []
    for name, fn in MASKS.items():
        masked = [row for row in rows if fn(row)]
        outside = [row for row in rows if not fn(row)]
        mask_reports.append({
            "mask": name,
            "inside": summarize_rows("inside", masked),
            "outside": summarize_rows("outside", outside),
            "inside_probability": probability_table(masked),
            "adjusted_valves": [simulate_valve(rows, denominator, fn, overlay) for overlay in OVERLAYS if overlay != "raw"],
        })
    return {
        "policy": POLICY,
        "forward_denominator": denominator,
        "current": summarize_rows("current", rows, denominator),
        "mask_reports": mask_reports,
        "worst_rows": [compact(row) for row in sorted(settled, key=net_cents)[:15]],
        "interpretation": interpretation(mask_reports),
    }


def interpretation(mask_reports: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    for report in mask_reports:
        inside = report.get("inside") or {}
        if int(inside.get("settled") or 0) >= 5 and float(inside.get("net_cents") or 0.0) < 0.0:
            notes.append(
                f"{report.get('mask')} is a repeated negative-expectancy pocket: "
                f"{inside.get('settled')} settled, W/L {inside.get('wins')}/{inside.get('losses')}, "
                f"net {inside.get('net_cents')}c."
            )
        best_valve = sorted(
            report.get("adjusted_valves") or [],
            key=lambda row: float(((row.get("kept") or {}).get("delta_vs_current_net_cents")) or -999999.0),
            reverse=True,
        )[0]
        kept = best_valve.get("kept") or {}
        notes.append(
            f"Best adjusted-FV valve for {report.get('mask')} is {best_valve.get('overlay')}: "
            f"coverage {kept.get('coverage_pct')}%, net {kept.get('net_cents')}c, "
            f"delta {kept.get('delta_vs_current_net_cents')}c."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> str:
    lines = [
        "# v28 False-Conviction Physics Audit",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
    ]
    current = report.get("current") or {}
    lines.extend([
        f"- Current entries/settled/coverage: `{current.get('entries')}/{current.get('settled')}/{fmt(current.get('coverage_pct'))}`",
        f"- Current W/L/net: `{current.get('wins')}/{current.get('losses')}/{fmt(current.get('net_cents'))}c`",
        "",
        "## Read",
        "",
    ])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for mask_report in report.get("mask_reports") or []:
        inside = mask_report.get("inside") or {}
        outside = mask_report.get("outside") or {}
        lines.extend([
            "",
            f"## {mask_report.get('mask')}",
            "",
            f"- Inside settled/W-L/net: `{inside.get('settled')}/{inside.get('wins')}-{inside.get('losses')}/{fmt(inside.get('net_cents'))}c`",
            f"- Outside settled/W-L/net: `{outside.get('settled')}/{outside.get('wins')}-{outside.get('losses')}/{fmt(outside.get('net_cents'))}c`",
            "",
            "### Probability Shrinkage Inside Mask",
            "",
            "| overlay | scored | avg p | win rate | brier d | logloss d |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in mask_report.get("inside_probability") or []:
            lines.append(
                f"| `{row.get('overlay')}` | {row.get('scored')} | {fmt(row.get('avg_p'))} | "
                f"{fmt(row.get('win_rate'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
                f"{fmt(row.get('logloss_delta_vs_raw'))} |"
            )
        lines.extend([
            "",
            "### Adjusted-FV Entry Impact",
            "",
            "| overlay | kept coverage | kept settled | kept net c | delta c | removed settled | removed net c |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ])
        for valve in mask_report.get("adjusted_valves") or []:
            kept = valve.get("kept") or {}
            removed = valve.get("removed") or {}
            lines.append(
                f"| `{valve.get('overlay')}` | {fmt(kept.get('coverage_pct'))} | {kept.get('settled')} | "
                f"{fmt(kept.get('net_cents'))} | {fmt(kept.get('delta_vs_current_net_cents'))} | "
                f"{removed.get('settled')} | {fmt(removed.get('net_cents'))} |"
            )
    lines.extend([
        "",
        "## Worst Rows",
        "",
        "| market | side | won | net c | raw p | adj p | ask | edge | stc | abs d | recross |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("worst_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('won')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('p_raw'))} | {fmt(row.get('p_adjusted'))} | {fmt(row.get('ask'))} | "
            f"{fmt(row.get('edge'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_md(report), encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
