"""Frozen validator for target-coverage boundary-temperature FV.

Research-only; no live bot changes or orders.

Freezes the diagnostic boundary-temperature idea so future rows can judge it
without re-selecting the best variant as new evidence arrives.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_boundary_temperature_fv import (
    boundary_temp_strong,
    raw_probability,
    score_variant,
)
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_boundary_temperature_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_boundary_temperature_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_boundary_temperature_fv_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
VARIANT = "boundary_temp_strong"
MIN_SETTLED = 30


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_policy": POLICY,
        "variant": VARIANT,
        "rule": "Apply conservative target-coverage probability, then shrink mid-confidence boundary/churn rows toward 50 by 0.50 * recross_heat.",
        "physics": "Near/mid-boundary high-recross rows are unresolved path states; probability should lose confidence continuously with recross heat rather than only through hard skips.",
        "source_artifact": "v28_target_coverage_boundary_temperature_fv_latest",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def future_rows(freeze_ts: str) -> tuple[list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    selected = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def chosen_variant(name: str) -> Callable[[dict[str, Any]], float]:
    if name == "boundary_temp_strong":
        return boundary_temp_strong
    raise ValueError(f"Unsupported frozen boundary-temperature variant: {name}")


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows, denominator = future_rows(str(state["freeze_ts_utc"]))
    raw = score_variant(rows, "raw_probability", raw_probability)
    variant = score_variant(rows, str(state["variant"]), chosen_variant(str(state["variant"])))
    brier_delta = delta(variant.get("brier_mean_delta"), raw.get("brier_mean_delta"))
    logloss_delta = delta(variant.get("logloss_mean_delta"), raw.get("logloss_mean_delta"))
    brier_p95 = (variant.get("brier_bootstrap") or {}).get("p95")
    logloss_p95 = (variant.get("logloss_bootstrap") or {}).get("p95")
    blockers = []
    if int(variant.get("rows") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if variant.get("brier_mean_delta") is None or float(variant.get("brier_mean_delta") or 0.0) >= 0.0:
        blockers.append("mean_brier_not_better")
    if brier_p95 is None or float(brier_p95) >= 0.0:
        blockers.append("brier_interval_not_strictly_negative")
    if variant.get("logloss_mean_delta") is None or float(variant.get("logloss_mean_delta") or 0.0) >= 0.0:
        blockers.append("mean_logloss_not_better")
    if logloss_p95 is None or float(logloss_p95) >= 0.0:
        blockers.append("logloss_interval_not_strictly_negative")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "entries": len(rows),
        "settled": variant.get("rows"),
        "raw": raw,
        "candidate": variant,
        "brier_delta_vs_raw": brier_delta,
        "logloss_delta_vs_raw": logloss_delta,
        "blockers": blockers,
        "ready_for_consideration": not blockers,
        "interpretation": [
            f"Frozen boundary-temperature FV has {len(rows)} future entries and {variant.get('rows')} settled/scored rows.",
            f"Candidate Brier/logloss mean deltas versus raw are {variant.get('brier_mean_delta')}/{variant.get('logloss_mean_delta')}.",
            "This is probability calibration only; it does not change entries, exits, or live order logic.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    candidate = report.get("candidate") or {}
    raw = report.get("raw") or {}
    lines = [
        "# v28 Frozen Boundary-Temperature FV",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Entry policy: `{freeze.get('entry_policy')}`",
        f"- Variant: `{freeze.get('variant')}`",
        f"- Future entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('future_denominator')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Brier/logloss delta vs raw: `{fmt(report.get('brier_delta_vs_raw'))}/{fmt(report.get('logloss_delta_vs_raw'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Metrics",
        "",
        "| slice | rows | adjusted | W/L | avg p | brier mean d | brier p95 | logloss mean d | logloss p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for name, row in [("raw", raw), ("candidate", candidate)]:
        lines.append(
            f"| {name} | {row.get('rows')} | {row.get('adjusted_rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('brier_mean_delta'))} | "
            f"{fmt((row.get('brier_bootstrap') or {}).get('p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt((row.get('logloss_bootstrap') or {}).get('p95'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
