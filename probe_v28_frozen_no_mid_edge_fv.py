"""Frozen validator for broader NO mid-edge FV shrink.

Research-only; no live bot changes or orders.

Freezes the broader target-surface idea:
    If selected side is NO and raw edge is 5-8pp, shrink p_side to executable
    ask probability. This is a calibration overlay only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import apply_policy
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_coverage_repair_pool_diagnostic import POLICY, summarize
from probe_v28_no_mid_edge_fv_generalization import metric, no_mid_to_book, raw_transform


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FREEZE_JSON = OUT_DIR / "v28_frozen_no_mid_edge_fv_freeze.json"
OUT_JSON = OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_no_mid_edge_fv_latest.md"

VARIANT = "no_mid_to_book"


def ensure_freeze() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if FREEZE_JSON.exists():
        return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    payload = {
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "variant": VARIANT,
        "target_policy": POLICY,
        "fv_adjustment": "if side=no and raw_edge_prob in [0.05,0.08), p_side=ask_prob",
    }
    FREEZE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_rows(freeze: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze.get("freeze_ts_utc"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    _ = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return target, len(forward_markets)


def build_report() -> dict[str, Any]:
    freeze = ensure_freeze()
    target, denominator = build_rows(freeze)
    raw = metric(target, raw_transform)
    variant = metric(target, no_mid_to_book)
    blockers = []
    if variant.get("rows", 0) < 30:
        blockers.append("settled_lt_30")
    if variant.get("brier") is None or raw.get("brier") is None or float(variant["brier"]) >= float(raw["brier"]):
        blockers.append("brier_not_better")
    if variant.get("logloss") is None or raw.get("logloss") is None or float(variant["logloss"]) >= float(raw["logloss"]):
        blockers.append("logloss_not_better")
    return {
        "diagnostic": "frozen_no_mid_edge_fv",
        "freeze": freeze,
        "future_denominator": denominator,
        "target_summary": summarize(target, denominator),
        "raw": raw,
        "variant": variant,
        "brier_delta_vs_raw": delta(variant.get("brier"), raw.get("brier")),
        "logloss_delta_vs_raw": delta(variant.get("logloss"), raw.get("logloss")),
        "blockers": blockers,
        "ready_for_consideration": not blockers,
        "interpretation": interpretation(denominator, raw, variant, blockers),
    }


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def interpretation(denominator: int, raw: dict[str, Any], variant: dict[str, Any], blockers: list[str]) -> list[str]:
    notes = [
        f"Frozen forward denominator is {denominator}; scored rows {variant.get('rows')}.",
        f"Raw Brier/logloss {raw.get('brier')}/{raw.get('logloss')}; variant {variant.get('brier')}/{variant.get('logloss')}.",
    ]
    if blockers:
        notes.append(f"Promotion blocked by: {', '.join(blockers)}.")
    notes.append("This is a frozen calibration overlay, not live order logic.")
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
        "# v28 Frozen NO Mid-Edge FV",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Variant: `{(report.get('freeze') or {}).get('variant')}`",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Brier/logloss delta: `{report.get('brier_delta_vs_raw')}/{report.get('logloss_delta_vs_raw')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Metrics",
            "",
            "| slice | rows | avg p | win rate | Brier | logloss |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name in ["raw", "variant"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('rows')} | {fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
            f"{fmt(row.get('brier'))} | {fmt(row.get('logloss'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
