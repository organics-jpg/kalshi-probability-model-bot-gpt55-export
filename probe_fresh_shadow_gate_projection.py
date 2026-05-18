"""Project the remaining fresh-shadow evidence needed to satisfy the live gate.

This is a research-only helper. It reads the latest live v28 physics shadow
JSON and computes what future post-lock evidence would be required to satisfy:

- 95% selected trade and contract accuracy,
- 75% and 80% selected-volume retention,
- the configured fresh selected sample floors.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from probe_live_v28_fv_accuracy_volume import OUT_DIR


SHADOW_JSON = OUT_DIR / "live_v28_physics_shadow_latest.json"
REPORT_LATEST = OUT_DIR / "fresh_shadow_gate_projection_latest.md"
JSON_LATEST = OUT_DIR / "fresh_shadow_gate_projection_latest.json"
TARGET_ACCURACY = 0.95
RETENTION_FLOORS = [0.75, 0.80]


def pct(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def max_losses_for_accuracy(selected: int, wins: int, target: float) -> Dict[str, int]:
    required_wins = math.ceil(target * selected)
    losses_allowed_total = max(0, selected - required_wins)
    current_losses = selected - wins
    return {
        "selected": selected,
        "wins": wins,
        "required_wins": required_wins,
        "losses_allowed_total": losses_allowed_total,
        "additional_losses_allowed": max(0, losses_allowed_total - current_losses),
    }


def projection_for_unit(fresh: Dict[str, Any], unit: str, retention: float) -> Dict[str, Any]:
    shadow = fresh["shadow"]
    baseline = fresh["baseline"]
    min_selected = int(fresh[f"min_fresh_{unit}"])
    current_selected = int(shadow[unit])
    current_selected_wins = int(shadow[f"{unit[:-1]}_wins"])
    current_baseline = int(baseline[unit])

    additional_selected_needed = max(0, min_selected - current_selected)
    selected_at_floor = current_selected + additional_selected_needed
    wins_at_floor = current_selected_wins + additional_selected_needed
    accuracy = max_losses_for_accuracy(selected_at_floor, wins_at_floor, TARGET_ACCURACY)

    max_total_at_floor = math.floor(selected_at_floor / retention)
    max_future_total = max(0, max_total_at_floor - current_baseline)
    max_future_blocked = max(0, max_future_total - additional_selected_needed)

    return {
        "unit": unit,
        "retention_floor": retention,
        "current_baseline": current_baseline,
        "current_selected": current_selected,
        "current_selected_wins": current_selected_wins,
        "min_selected": min_selected,
        "additional_selected_needed": additional_selected_needed,
        "selected_at_floor": selected_at_floor,
        "max_total_at_floor": max_total_at_floor,
        "max_future_total_at_floor": max_future_total,
        "max_future_blocked_at_floor": max_future_blocked,
        "additional_selected_losses_allowed_at_floor": accuracy["additional_losses_allowed"],
        "required_selected_wins_at_floor": accuracy["required_wins"],
    }


def build_projection(shadow: Dict[str, Any]) -> Dict[str, Any]:
    fresh = shadow["fresh_after_lock"]
    rows: List[Dict[str, Any]] = []
    for retention in RETENTION_FLOORS:
        for unit in ["trades", "contracts"]:
            rows.append(projection_for_unit(fresh, unit, retention))
    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ"),
        "source": str(SHADOW_JSON),
        "rule": shadow.get("rule"),
        "lock": shadow.get("lock"),
        "fresh_after_lock": fresh,
        "target_accuracy": TARGET_ACCURACY,
        "retention_floors": RETENTION_FLOORS,
        "projections": rows,
    }


def write_report(payload: Dict[str, Any], path: Path) -> None:
    fresh = payload["fresh_after_lock"]
    shadow = fresh["shadow"]
    baseline = fresh["baseline"]
    lines: List[str] = []
    lines.append("# Fresh Shadow Gate Projection")
    lines.append("")
    lines.append(f"Generated UTC: `{payload['generated_utc']}`")
    lines.append("")
    lines.append("## Current Fresh State")
    lines.append("")
    lines.append(f"- Rule: `{payload['rule']['label']}`")
    lines.append(f"- Fresh baseline: {baseline['contract_wins']}/{baseline['contracts']} contracts = {pct(baseline['contract_accuracy'])}")
    lines.append(f"- Fresh selected: {shadow['contract_wins']}/{shadow['contracts']} contracts = {pct(shadow['contract_accuracy'])}")
    lines.append(f"- Fresh selected retention: {pct(shadow['contract_retention'])}")
    lines.append(f"- Sample ready: {fresh['sample_ready']}")
    lines.append(f"- Accuracy gate: {fresh['accuracy_gate']}")
    lines.append(f"- Retention gate: {fresh['retention_gate']}")
    lines.append("")
    lines.append("## Minimum Future Evidence At Sample Floor")
    lines.append("")
    lines.append("| retention floor | unit | current selected | minimum selected | add selected needed | max future blocked | selected losses allowed |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|")
    for row in payload["projections"]:
        lines.append(
            f"| {pct(row['retention_floor'])} | {row['unit']} | {row['current_selected']} | "
            f"{row['min_selected']} | {row['additional_selected_needed']} | "
            f"{row['max_future_blocked_at_floor']} | {row['additional_selected_losses_allowed_at_floor']} |"
        )
    lines.append("")
    lines.append("## Readout")
    lines.append("")
    by_floor_unit = {
        (float(row["retention_floor"]), str(row["unit"])): row
        for row in payload["projections"]
    }
    r75_trades = by_floor_unit[(0.75, "trades")]
    r75_contracts = by_floor_unit[(0.75, "contracts")]
    r80_trades = by_floor_unit[(0.80, "trades")]
    r80_contracts = by_floor_unit[(0.80, "contracts")]
    lines.append(
        f"At the 75% retention floor, the shadow needs at least "
        f"{r75_trades['additional_selected_needed']} more selected trades and "
        f"{r75_contracts['additional_selected_needed']} more selected contracts. "
        f"At that sample floor it can block at most "
        f"{r75_trades['max_future_blocked_at_floor']} future baseline trades / "
        f"{r75_contracts['max_future_blocked_at_floor']} future baseline contracts "
        "while staying at 75% retention."
    )
    lines.append(
        f"At the 80% retention floor, it can block at most "
        f"{r80_trades['max_future_blocked_at_floor']} future baseline trades / "
        f"{r80_contracts['max_future_blocked_at_floor']} future baseline contracts "
        "at the same minimum selected sample."
    )
    lines.append(
        "Accuracy is not the current blocker on the tiny fresh sample; volume retention and sample size are."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    shadow = json.loads(SHADOW_JSON.read_text(encoding="utf-8"))
    payload = build_projection(shadow)
    JSON_LATEST.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamped_json = OUT_DIR / f"fresh_shadow_gate_projection_{payload['generated_utc']}.json"
    stamped_md = OUT_DIR / f"fresh_shadow_gate_projection_{payload['generated_utc']}.md"
    stamped_json.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    write_report(payload, REPORT_LATEST)
    write_report(payload, stamped_md)
    print("Fresh shadow gate projection complete")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
