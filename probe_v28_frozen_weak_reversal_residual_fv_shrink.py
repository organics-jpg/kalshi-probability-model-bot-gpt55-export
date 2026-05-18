"""Frozen validator for weak-reversal residual FV shrink.

Research-only; no live bot changes or orders.

Freezes the discovery FV idea:
    For weak-reversal candidate rows where side=NO and raw edge is 5-8pp,
    shrink held-side probability halfway toward 50.
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
from probe_v28_coverage_repair_pool_diagnostic import POLICY
from probe_v28_weak_boundary_reversal_bakeoff import run_variant
from probe_v28_weak_reversal_residual_fv_shrink import metric_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FREEZE_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_freeze.json"
OUT_JSON = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_weak_reversal_residual_fv_shrink_latest.md"

VARIANT = "half_to_50"


def ensure_freeze() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if FREEZE_JSON.exists():
        return json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    payload = {
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "variant": VARIANT,
        "target_policy": POLICY,
        "weak_reversal": {
            "p_max": 0.60,
            "recross_floor": 0.75,
            "abs_d_max": 0.25,
            "max_delay": 240.0,
            "no_replacement_mode": "abstain",
        },
        "fv_adjustment": "if side=no and raw_edge_prob in [0.05,0.08), p=0.5+0.5*(p_raw-0.5)",
    }
    FREEZE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_surfaces(freeze: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, set[str]]:
    freeze_dt = parse_ts(freeze.get("freeze_ts_utc"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets), forward_markets


def build_report() -> dict[str, Any]:
    freeze = ensure_freeze()
    all_rows, target, denominator, forward_markets = build_surfaces(freeze)
    weak = run_variant(
        all_rows=all_rows,
        target=target,
        denominator=denominator,
        forward_markets=forward_markets,
        p_max=0.60,
        recross_floor=0.75,
        abs_d_max=0.25,
        max_delay=240.0,
        no_replacement_mode="abstain",
    )
    rows = weak.get("candidate_rows") or []
    raw_all = metric_rows(rows, "raw")
    variant_all = metric_rows(rows, VARIANT)
    raw_zone = metric_rows(rows, "raw", lambda row: str(row.get("side")) == "no")
    variant_zone = metric_rows(rows, VARIANT, lambda row: str(row.get("side")) == "no")
    blockers = []
    if variant_all.get("rows", 0) < 30:
        blockers.append("settled_lt_30")
    if variant_all.get("brier") is None or raw_all.get("brier") is None or float(variant_all["brier"]) >= float(raw_all["brier"]):
        blockers.append("brier_not_better")
    if variant_all.get("logloss") is None or raw_all.get("logloss") is None or float(variant_all["logloss"]) >= float(raw_all["logloss"]):
        blockers.append("logloss_not_better")
    return {
        "diagnostic": "frozen_weak_reversal_residual_fv_shrink",
        "freeze": freeze,
        "future_denominator": denominator,
        "weak_summary": weak.get("candidate_summary"),
        "raw_all": raw_all,
        "variant_all": variant_all,
        "raw_no_side": raw_zone,
        "variant_no_side": variant_zone,
        "brier_delta_vs_raw": none_delta(variant_all.get("brier"), raw_all.get("brier")),
        "logloss_delta_vs_raw": none_delta(variant_all.get("logloss"), raw_all.get("logloss")),
        "blockers": blockers,
        "ready_for_consideration": not blockers,
        "interpretation": interpretation(denominator, raw_all, variant_all, blockers),
    }


def none_delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def interpretation(
    denominator: int,
    raw_all: dict[str, Any],
    variant_all: dict[str, Any],
    blockers: list[str],
) -> list[str]:
    notes = [
        f"Frozen forward denominator is {denominator}; scored rows {variant_all.get('rows')}.",
        f"Raw Brier/logloss {raw_all.get('brier')}/{raw_all.get('logloss')}; variant {variant_all.get('brier')}/{variant_all.get('logloss')}.",
    ]
    if blockers:
        notes.append(f"Promotion blocked by: {', '.join(blockers)}.")
    notes.append("This validates calibration only; entry PnL is tracked by the separate residual repair validator.")
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
        "# v28 Frozen Weak-Reversal Residual FV Shrink",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Variant: `{(report.get('freeze') or {}).get('variant')}`",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
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
    for name, key in [
        ("raw_all", "raw_all"),
        ("variant_all", "variant_all"),
        ("raw_no_side", "raw_no_side"),
        ("variant_no_side", "variant_no_side"),
    ]:
        row = report.get(key) or {}
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
