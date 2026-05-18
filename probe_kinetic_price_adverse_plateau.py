"""Plateau diagnostic for kinetic price/adverse guards.

The price/adverse guard is the cleanest current kinetic challenger, but a
single threshold pair can still be a scar. This probe scans the local surface
around ask caps and adverse 15-minute motion caps to see whether nearby
physically similar guards preserve EV across both captures.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_kinetic_guard_physics_sanity import GuardSpec, guard_mask
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_profit_kinetic_touch_fresh_validation import KINETIC_TOUCH_LOCK_PATH
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "kinetic_price_adverse_plateau_latest.md"
REPORT_JSON = OUT_DIR / "kinetic_price_adverse_plateau_latest.json"
REPORT_CSV = OUT_DIR / "kinetic_price_adverse_plateau_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def finite(value: Any, default: float = -999999.0) -> float:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return default
    if not np.isfinite(val):
        return default
    return val


def select_with_spec(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy, spec: GuardSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    eligible = chosen[touch_gate_mask(chosen, policy) & guard_mask(chosen, spec)].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return enrich_selected(selected)


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    out = split_metric(base, selected, split)
    out["coverage_pass"] = finite(out.get("coverage"), 0.0) >= MARKET_COVERAGE_FLOOR
    out["positive_net"] = finite(out.get("net_pnl_cents"), 0.0) > 0.0
    return out


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def all_split_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(finite(metrics[split].get("net_pnl_cents"), 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def all_split_coverage(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(finite(metrics[split].get("coverage"), 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])


def min_oos_roi(*metric_sets: Dict[str, Dict[str, Any]]) -> float:
    values: List[float] = []
    for metrics in metric_sets:
        values.extend(
            [
                finite(metrics["validation"].get("net_roi_on_cost")),
                finite(metrics["holdout"].get("net_roi_on_cost")),
            ]
        )
    return min(values) if values else -999999.0


def make_specs() -> List[GuardSpec]:
    specs: List[GuardSpec] = [GuardSpec("base")]
    ask_caps: List[Optional[float]] = [65.0, 70.0, 75.0, 80.0, 85.0, 90.0, None]
    adverse_caps: List[Optional[float]] = [50.0, 75.0, 100.0, 125.0, 150.0, None]
    for adverse in adverse_caps:
        for ask in ask_caps:
            specs.append(GuardSpec("adverse_ask_plateau", max_adverse15=adverse, max_ask=ask))
            specs.append(GuardSpec("kinetic57_adverse_ask_plateau", min_kinetic=0.57, max_adverse15=adverse, max_ask=ask))

    seen: set[str] = set()
    out: List[GuardSpec] = []
    for spec in specs:
        if spec.label in seen:
            continue
        seen.add(spec.label)
        out.append(spec)
    return out


def flatten(
    spec: GuardSpec,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    base_current: Dict[str, Any],
    base_v21: Dict[str, Any],
) -> Dict[str, Any]:
    current_all = current_metrics["all"]
    v21_all = v21_metrics["all"]
    row: Dict[str, Any] = {
        "family": spec.family,
        "guard": spec.label,
        "max_adverse15": spec.max_adverse15,
        "max_ask": spec.max_ask,
        "min_kinetic": spec.min_kinetic,
        "current_coverage_pass": all_split_coverage(current_metrics),
        "v21_coverage_pass": all_split_coverage(v21_metrics),
        "current_all_split_positive": all_split_positive(current_metrics),
        "v21_all_split_positive": all_split_positive(v21_metrics),
        "min_oos_roi": min_oos_roi(current_metrics, v21_metrics),
        "current_delta_vs_base_cents": finite(current_all.get("net_pnl_cents")) - finite(base_current.get("net_pnl_cents")),
        "v21_delta_vs_base_cents": finite(v21_all.get("net_pnl_cents")) - finite(base_v21.get("net_pnl_cents")),
        "combined_delta_vs_base_cents": (
            finite(current_all.get("net_pnl_cents"))
            + finite(v21_all.get("net_pnl_cents"))
            - finite(base_current.get("net_pnl_cents"))
            - finite(base_v21.get("net_pnl_cents"))
        ),
    }
    row["both_coverage_pass"] = row["current_coverage_pass"] and row["v21_coverage_pass"]
    row["both_all_split_positive"] = row["current_all_split_positive"] and row["v21_all_split_positive"]
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def plateau_neighbors(rows: pd.DataFrame, target: Tuple[float, float]) -> pd.DataFrame:
    adverse_order = [50.0, 75.0, 100.0, 125.0, 150.0]
    ask_order = [65.0, 70.0, 75.0, 80.0, 85.0, 90.0]
    target_adv, target_ask = target
    adv_i = adverse_order.index(target_adv)
    ask_i = ask_order.index(target_ask)
    allowed_adv = set(adverse_order[max(0, adv_i - 1) : min(len(adverse_order), adv_i + 2)])
    allowed_ask = set(ask_order[max(0, ask_i - 1) : min(len(ask_order), ask_i + 2)])
    mask = (
        rows["family"].eq("adverse_ask_plateau")
        & rows["max_adverse15"].isin(allowed_adv)
        & rows["max_ask"].isin(allowed_ask)
    )
    return rows[mask].copy()


def write_report(generated: str, lock: Dict[str, Any], rows: pd.DataFrame) -> None:
    filtered = rows[rows["both_coverage_pass"]].copy()
    stable = filtered[filtered["both_all_split_positive"]].copy()
    stable = stable.sort_values(
        ["combined_delta_vs_base_cents", "min_oos_roi", "current_all_net_pnl_cents"],
        ascending=[False, False, False],
    )
    top = stable.head(15)
    neighbors = plateau_neighbors(rows, (100.0, 70.0))
    neighbor_good = neighbors[
        neighbors["both_coverage_pass"]
        & neighbors["both_all_split_positive"]
        & rows.loc[neighbors.index, "current_delta_vs_base_cents"].gt(0)
        & rows.loc[neighbors.index, "v21_delta_vs_base_cents"].gt(0)
    ]

    lines: List[str] = [
        "# Kinetic Price/Adverse Plateau Diagnostic",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Scans nearby ask and adverse-motion caps around the kinetic price/adverse guard.",
        "- Any threshold change must receive a separate future lock before it counts as fresh evidence.",
        "",
        "## Data",
        "",
        f"- Policy: `{lock['policy']['label']}`",
        f"- Kinetic lock close time: `{lock.get('lock_close_dt')}`",
        f"- Guards scanned: {len(rows)}",
        f"- Both-dataset 80%-coverage guards: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset 80%-coverage all-split-positive guards: {int(stable.shape[0])}",
        f"- Local 3x3 neighbors around `adverse15<=100 AND ask<=70`: {len(neighbors)}",
        f"- Neighbors with positive current and v21 delta versus unguarded kinetic: {len(neighbor_good)}/{len(neighbors)}",
        "",
        "## Top Plateau Rows",
        "",
        "| rank | guard | family | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | min OOS ROI |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['guard']}` | `{row['family']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_cents(row['current_delta_vs_base_cents'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_cents(row['v21_delta_vs_base_cents'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )

    lines += [
        "",
        "## Local Neighbor Read",
        "",
        "| guard | current delta | v21 delta | current cov | v21 cov | all-split-positive |",
        "|---|---:|---:|---:|---:|---|",
    ]
    neighbor_rows = neighbors.sort_values(["max_adverse15", "max_ask"])
    for _, row in neighbor_rows.iterrows():
        all_pos = bool(row["both_all_split_positive"])
        lines.append(
            f"| `{row['guard']}` | {fmt_cents(row['current_delta_vs_base_cents'])} | "
            f"{fmt_cents(row['v21_delta_vs_base_cents'])} | {pct(row['current_all_coverage'])} | "
            f"{pct(row['v21_all_coverage'])} | {all_pos} |"
        )

    lines += [
        "",
        "## Read",
        "",
    ]
    if len(neighbor_good) >= max(1, len(neighbors) // 2):
        lines.append("- The price/adverse guard sits on a broader positive plateau, not an isolated single-cell spike.")
    else:
        lines.append("- The local price/adverse neighborhood is mixed; treat the exact guard as fragile until fresh evidence grows.")
    lines.append("- Post-outcome plateau diagnostics are useful for physics, but they are not promotion evidence.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "lock": clean_json_local(lock),
                "guards": clean_json_local(rows.to_dict(orient="records")),
                "neighbor_good_count": int(len(neighbor_good)),
                "neighbor_count": int(len(neighbors)),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    rows.to_csv(REPORT_CSV, index=False)


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])

    current_side = add_touch_hazard_scores(load_side_rows())
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)

    base_spec = GuardSpec("base")
    base_current_sel = select_with_spec(current_side, current_base, policy, base_spec)
    base_v21_sel = select_with_spec(v21_side, v21_base, policy, base_spec)
    base_current = metric(current_base, base_current_sel, "all")
    base_v21 = metric(v21_base, base_v21_sel, "all")

    records: List[Dict[str, Any]] = []
    for spec in make_specs():
        current_sel = select_with_spec(current_side, current_base, policy, spec)
        v21_sel = select_with_spec(v21_side, v21_base, policy, spec)
        records.append(
            flatten(
                spec,
                metrics_for(current_base, current_sel),
                metrics_for(v21_base, v21_sel),
                base_current,
                base_v21,
            )
        )

    rows = pd.DataFrame(records)
    write_report(generated, lock, rows)
    print("Kinetic price/adverse plateau diagnostic complete")
    print(f"guards={len(rows)} both_coverage={int(rows['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
