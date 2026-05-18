"""Causal blocker overlays for the kinetic touch-profit candidate.

The first forward kinetic signal lost, and the stability audit found weak
high-adverse / high-ask slices. This diagnostic scans simple pre-entry blocker
overlays on top of the frozen kinetic rule while preserving broad recurring
market coverage. Any attractive overlay must get a separate future lock before
it can count as fresh evidence.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
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
from probe_profit_lock_time_boundary import effective_lock_dt


@dataclass(frozen=True)
class Overlay:
    label: str
    clauses: tuple[str, ...]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def clause_mask(rows: pd.DataFrame, clause: str) -> pd.Series:
    true = pd.Series(True, index=rows.index)
    if clause == "none":
        return true
    specs = {
        "ask<=80": rows["ask_cents"].le(80.0),
        "ask<=75": rows["ask_cents"].le(75.0),
        "ask<=70": rows["ask_cents"].le(70.0),
        "book>=0.55": rows["book_p_side"].ge(0.55),
        "book>=0.60": rows["book_p_side"].ge(0.60),
        "brownian15>=0.58": rows["brownian_p_rv_15m"].ge(0.58),
        "brownian15>=0.60": rows["brownian_p_rv_15m"].ge(0.60),
        "kinetic>=0.57": rows["kinetic_touch_score_15"].ge(0.57),
        "kinetic>=0.60": rows["kinetic_touch_score_15"].ge(0.60),
        "adverse15<=20": rows["adverse_move_15m"].le(20.0),
        "adverse15<=50": rows["adverse_move_15m"].le(50.0),
        "adverse15<=100": rows["adverse_move_15m"].le(100.0),
        "touch_loss15<=0.85": rows["touch_loss_rv_15m"].le(0.85),
        "touch_loss15<=0.80": rows["touch_loss_rv_15m"].le(0.80),
        "touch_loss15>=0.50": rows["touch_loss_rv_15m"].ge(0.50),
        "margin15>=0.25": rows["margin_per_rv_sigma_15m"].ge(0.25),
        "margin15>=0.00": rows["margin_per_rv_sigma_15m"].ge(0.00),
        "spread<=2": rows["spread_cents"].le(2.0),
    }
    if clause not in specs:
        raise ValueError(f"unknown clause: {clause}")
    return specs[clause].fillna(False)


def overlay_mask(rows: pd.DataFrame, overlay: Overlay) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    for clause in overlay.clauses:
        mask &= clause_mask(rows, clause)
    return mask.fillna(False)


def make_overlays() -> List[Overlay]:
    singles = [
        "none",
        "ask<=80",
        "ask<=75",
        "ask<=70",
        "book>=0.55",
        "book>=0.60",
        "brownian15>=0.58",
        "brownian15>=0.60",
        "kinetic>=0.57",
        "kinetic>=0.60",
        "adverse15<=20",
        "adverse15<=50",
        "adverse15<=100",
        "touch_loss15<=0.85",
        "touch_loss15<=0.80",
        "touch_loss15>=0.50",
        "margin15>=0.25",
        "margin15>=0.00",
        "spread<=2",
    ]
    combos = [
        ("adverse15<=20", "ask<=80"),
        ("adverse15<=20", "book>=0.55"),
        ("adverse15<=20", "brownian15>=0.58"),
        ("adverse15<=20", "touch_loss15<=0.85"),
        ("adverse15<=50", "ask<=80"),
        ("adverse15<=50", "book>=0.55"),
        ("adverse15<=50", "brownian15>=0.58"),
        ("adverse15<=50", "touch_loss15<=0.85"),
        ("ask<=80", "book>=0.55"),
        ("ask<=80", "brownian15>=0.58"),
        ("ask<=80", "touch_loss15<=0.85"),
        ("book>=0.55", "brownian15>=0.58"),
        ("book>=0.55", "touch_loss15<=0.85"),
        ("kinetic>=0.57", "adverse15<=50"),
        ("kinetic>=0.57", "ask<=80"),
        ("margin15>=0.00", "adverse15<=50"),
        ("margin15>=0.25", "ask<=80"),
    ]
    overlays = [Overlay(clause, (clause,)) for clause in singles]
    overlays.extend(Overlay(" AND ".join(combo), combo) for combo in combos)
    return overlays


def select_with_overlay(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy, overlay: Overlay) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    eligible = chosen[touch_gate_mask(chosen, policy) & overlay_mask(chosen, overlay)].copy()
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


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str = "all") -> Dict[str, Any]:
    out = split_metric(base, selected, split)
    out["coverage_pass"] = (out["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    out["positive_net"] = (out["net_pnl_cents"] or 0.0) > 0.0
    return out


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])


def all_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def min_oos_roi(current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> float:
    values = [
        current["validation"]["net_roi_on_cost"] or -1.0,
        current["holdout"]["net_roi_on_cost"] or -1.0,
        v21["validation"]["net_roi_on_cost"] or -1.0,
        v21["holdout"]["net_roi_on_cost"] or -1.0,
    ]
    return float(min(values))


def flatten(overlay: Overlay, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]], fresh_metric: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "overlay": overlay.label,
        "clauses": " AND ".join(overlay.clauses),
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "current_all_positive": all_positive(current_metrics),
        "v21_all_positive": all_positive(v21_metrics),
        "fresh_net_pnl_cents": fresh_metric.get("net_pnl_cents"),
        "fresh_markets": fresh_metric.get("markets"),
        "fresh_base_markets": fresh_metric.get("base_markets"),
        "fresh_coverage": fresh_metric.get("coverage"),
        "min_oos_roi": min_oos_roi(current_metrics, v21_metrics),
    }
    row["both_coverage_pass"] = row["current_coverage_pass"] and row["v21_coverage_pass"]
    row["both_positive_all_splits"] = row["current_all_positive"] and row["v21_all_positive"]
    row["combined_all_net_pnl_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) + (
        v21_metrics["all"]["net_pnl_cents"] or 0.0
    )
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_coverage_pass"]),
        int(row["both_positive_all_splits"]),
        row["min_oos_roi"],
        row["combined_all_net_pnl_cents"],
        row["current_all_net_pnl_cents"] or -999999.0,
        row["v21_all_net_pnl_cents"] or -999999.0,
    )


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    if not KINETIC_TOUCH_LOCK_PATH.exists():
        raise SystemExit(f"Missing kinetic touch lock: {KINETIC_TOUCH_LOCK_PATH}")
    lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])
    overlays = make_overlays()

    current_side = add_touch_hazard_scores(load_side_rows())
    current_base = market_base(current_side)
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    v21_base = market_base(v21_side)

    lock_close_dt = effective_lock_dt(lock)
    fresh_base = current_base[pd.to_datetime(current_base["close_dt"], utc=True, errors="coerce").gt(lock_close_dt)].copy()
    fresh_side = current_side[
        pd.to_datetime(current_side["entry_dt"], utc=True, errors="coerce").gt(lock_close_dt)
        & current_side["market"].isin(set(fresh_base["market"]))
    ].copy()

    rows: List[Dict[str, Any]] = []
    for overlay in overlays:
        current_selected = select_with_overlay(current_side, current_base, policy, overlay)
        v21_selected = select_with_overlay(v21_side, v21_base, policy, overlay)
        fresh_selected = (
            select_with_overlay(fresh_side, fresh_base, policy, overlay)
            if not fresh_base.empty
            else current_selected.iloc[0:0].copy()
        )
        current_metrics = metrics_for(current_base, current_selected)
        v21_metrics = metrics_for(v21_base, v21_selected)
        fresh_metric = metric(fresh_base, fresh_selected, "all")
        rows.append(flatten(overlay, current_metrics, v21_metrics, fresh_metric))

    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "fresh_base_intervals": int(len(fresh_base)),
        "overlays": int(len(overlays)),
        "lock_close_dt": lock.get("lock_close_dt"),
        "policy": lock["policy"],
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    coverage = results[results["both_coverage_pass"]]
    positive = coverage[coverage["both_positive_all_splits"]]
    lines: List[str] = [
        "# Kinetic-Touch Blocker Overlay Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Scans simple causal overlays on top of the frozen kinetic-touch rule.",
        "- Any useful overlay must receive a separate future lock before it counts as fresh validation.",
        "",
        "## Data",
        "",
        f"- Policy: `{diagnostics['policy']['label']}`",
        f"- Lock close time: `{diagnostics['lock_close_dt']}`",
        f"- Current intervals: {diagnostics['current_intervals']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}",
        f"- Fresh base intervals after kinetic lock: {diagnostics['fresh_base_intervals']}",
        f"- Overlays scanned: {diagnostics['overlays']}",
        f"- Both-dataset 80%-coverage overlays: {len(coverage)}",
        f"- Both-dataset 80%-coverage all-split-positive overlays: {len(positive)}",
        "",
        "## Top Coverage-Preserving Overlays",
        "",
        "| rank | overlay | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | fresh net | min OOS ROI |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(coverage.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['overlay']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_cents(row['fresh_net_pnl_cents'])} | {fmt_roi(row['min_oos_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if positive.empty:
        lines.append("- No kinetic overlay preserved 80% coverage on both datasets while staying positive on every split.")
    else:
        best = positive.iloc[0].to_dict()
        lines.append(f"- Best all-split-positive coverage-preserving overlay: `{best['overlay']}`.")
        lines.append(
            f"- It has current {fmt_cents(best['current_all_net_pnl_cents'])} / {fmt_roi(best['current_all_net_roi_on_cost'])}, "
            f"v21 {fmt_cents(best['v21_all_net_pnl_cents'])} / {fmt_roi(best['v21_all_net_roi_on_cost'])}, "
            f"and fresh diagnostic net {fmt_cents(best['fresh_net_pnl_cents'])}."
        )
    lines.append("- This scan is post-outcome diagnostics only; do not merge an overlay into existing fresh evidence.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "kinetic_touch_blocker_overlays_latest.csv"
    csv_stamp = OUT_DIR / f"kinetic_touch_blocker_overlays_{generated}.csv"
    md_latest = OUT_DIR / "kinetic_touch_blocker_overlays_latest.md"
    md_stamp = OUT_DIR / f"kinetic_touch_blocker_overlays_{generated}.md"
    json_latest = OUT_DIR / "kinetic_touch_blocker_overlays_latest.json"
    json_stamp = OUT_DIR / f"kinetic_touch_blocker_overlays_{generated}.json"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_coverage_count": int(results["both_coverage_pass"].sum()),
        "both_positive_all_splits_count": int((results["both_coverage_pass"] & results["both_positive_all_splits"]).sum()),
        "top_rows": results.head(25).to_dict("records"),
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Kinetic-touch blocker overlay scan complete")
    print(f"overlays={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"both_positive_all_splits={int((results['both_coverage_pass'] & results['both_positive_all_splits']).sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
