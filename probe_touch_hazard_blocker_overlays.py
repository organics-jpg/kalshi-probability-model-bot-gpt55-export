"""Causal blocker overlays for the locked touch-hazard EV candidate.

The touch-hazard lock is the current best EV candidate, but fresh evidence is
tiny and noisy. This probe tests simple causal overlays on top of the frozen
touch-hazard policy without changing the lock. Each overlay is evaluated on the
current heartbeat ledger, independent v21 ledger, and post-lock current sample.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
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
from probe_profit_touch_hazard_fresh_validation import TOUCH_LOCK_PATH, policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask


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


def fmt_num(value: Optional[float], digits: int = 2) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def clause_mask(rows: pd.DataFrame, clause: str) -> pd.Series:
    true = pd.Series(True, index=rows.index)
    if clause == "none":
        return true
    specs = {
        "ask>=45": rows["ask_cents"].ge(45.0),
        "ask>=50": rows["ask_cents"].ge(50.0),
        "ask>=55": rows["ask_cents"].ge(55.0),
        "ask<=60": rows["ask_cents"].le(60.0),
        "ask<=70": rows["ask_cents"].le(70.0),
        "book>=0.50": rows["book_p_side"].ge(0.50),
        "book>=0.55": rows["book_p_side"].ge(0.55),
        "book>=0.60": rows["book_p_side"].ge(0.60),
        "score>=0.43": rows["book_touch_blend_15"].ge(0.43),
        "score>=0.45": rows["book_touch_blend_15"].ge(0.45),
        "score>=0.47": rows["book_touch_blend_15"].ge(0.47),
        "drift5<=0.95": rows["drift_p_5m_rv_15m"].le(0.95),
        "drift5>=0.35": rows["drift_p_5m_rv_15m"].ge(0.35),
        "adverse15<=150": rows["adverse_move_15m"].le(150.0),
        "touch_loss15<=0.95": rows["touch_loss_rv_15m"].le(0.95),
        "touch_loss15>=0.80": rows["touch_loss_rv_15m"].ge(0.80),
        "margin15>=-0.10": rows["margin_per_rv_sigma_15m"].ge(-0.10),
        "margin15<=0.25": rows["margin_per_rv_sigma_15m"].le(0.25),
        "brownian15>=0.48": rows["brownian_p_rv_15m"].ge(0.48),
        "brownian15<=0.58": rows["brownian_p_rv_15m"].le(0.58),
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
        "ask>=45",
        "ask>=50",
        "ask>=55",
        "ask<=60",
        "ask<=70",
        "book>=0.50",
        "book>=0.55",
        "book>=0.60",
        "score>=0.43",
        "score>=0.45",
        "score>=0.47",
        "drift5<=0.95",
        "drift5>=0.35",
        "adverse15<=150",
        "touch_loss15<=0.95",
        "touch_loss15>=0.80",
        "margin15>=-0.10",
        "margin15<=0.25",
        "brownian15>=0.48",
        "brownian15<=0.58",
    ]
    combos = [
        ("ask>=50", "book>=0.50"),
        ("ask>=50", "score>=0.43"),
        ("ask>=50", "drift5<=0.95"),
        ("ask>=50", "touch_loss15>=0.80"),
        ("ask>=50", "brownian15<=0.58"),
        ("book>=0.50", "score>=0.43"),
        ("book>=0.50", "drift5<=0.95"),
        ("book>=0.50", "touch_loss15>=0.80"),
        ("score>=0.43", "touch_loss15>=0.80"),
        ("score>=0.45", "ask>=50"),
        ("score>=0.45", "book>=0.50"),
        ("ask>=50", "ask<=70"),
        ("ask>=50", "ask<=60"),
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


def positive_all(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def positive_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(overlay: Overlay, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]], fresh_metric: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "overlay": overlay.label,
        "clauses": " AND ".join(overlay.clauses),
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "current_positive_all_splits": positive_all(current_metrics),
        "v21_positive_all_splits": positive_all(v21_metrics),
        "current_positive_oos": positive_oos(current_metrics),
        "v21_positive_oos": positive_oos(v21_metrics),
        "fresh_markets": fresh_metric["markets"],
        "fresh_base_markets": fresh_metric["base_markets"],
        "fresh_wins": fresh_metric["wins"],
        "fresh_losses": fresh_metric["losses"],
        "fresh_net_pnl_cents": fresh_metric["net_pnl_cents"],
        "fresh_coverage": fresh_metric["coverage"],
    }
    row["both_coverage_pass"] = row["current_coverage_pass"] and row["v21_coverage_pass"]
    row["both_positive_all_splits"] = row["current_positive_all_splits"] and row["v21_positive_all_splits"]
    row["both_positive_oos"] = row["current_positive_oos"] and row["v21_positive_oos"]
    row["combined_all_net_pnl_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) + (
        v21_metrics["all"]["net_pnl_cents"] or 0.0
    )
    row["min_oos_roi"] = min(
        min(current_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
        min(v21_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
    )
    row["max_median_ask"] = max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0)
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, met in metrics.items():
            for key, value in met.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_coverage_pass"]),
        int(row["both_positive_oos"]),
        int(row["both_positive_all_splits"]),
        row["fresh_net_pnl_cents"] or -10_000.0,
        row["min_oos_roi"],
        row["combined_all_net_pnl_cents"],
        -(row["max_median_ask"] or 100.0),
    )


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    if not TOUCH_LOCK_PATH.exists():
        raise SystemExit(f"Missing touch-hazard lock: {TOUCH_LOCK_PATH}")
    lock = json.loads(TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])
    overlays = make_overlays()
    current_side = add_touch_hazard_scores(load_side_rows())
    current_base = market_base(current_side)
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    v21_base = market_base(v21_side)
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
    fresh_base = current_base[pd.to_datetime(current_base["close_dt"], utc=True, errors="coerce") > lock_close_dt].copy()
    fresh_side = current_side[
        pd.to_datetime(current_side["entry_dt"], utc=True, errors="coerce").gt(lock_close_dt)
        & current_side["market"].isin(set(fresh_base["market"]))
    ].copy()
    rows: List[Dict[str, Any]] = []
    for overlay in overlays:
        current_selected = select_with_overlay(current_side, current_base, policy, overlay)
        v21_selected = select_with_overlay(v21_side, v21_base, policy, overlay)
        fresh_selected = select_with_overlay(fresh_side, fresh_base, policy, overlay)
        rows.append(
            flatten(
                overlay,
                metrics_for(current_base, current_selected),
                metrics_for(v21_base, v21_selected),
                metric(fresh_base, fresh_selected, "all"),
            )
        )
    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "policy": lock["policy"],
        "lock_close_dt": lock.get("lock_close_dt"),
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "fresh_base_markets": int(len(fresh_base)),
        "overlays": int(len(overlays)),
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path: Path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    both_cov = results[results["both_coverage_pass"]]
    both_all = both_cov[both_cov["both_positive_all_splits"]]
    lines = [
        "# Touch-Hazard Blocker Overlay Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- The frozen touch-hazard lock is not changed; overlays are diagnostics/challengers only.",
        "- Ranking requires 80% recurring-market coverage on current and v21 before rewarding fresh and OOS profit.",
        "",
        "## Data",
        "",
        f"- Policy: `{diagnostics['policy']['label']}`",
        f"- Lock close time: `{diagnostics['lock_close_dt']}`",
        f"- Current intervals: {diagnostics['current_intervals']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}",
        f"- Fresh post-lock base markets: {diagnostics['fresh_base_markets']}",
        f"- Overlays scanned: {diagnostics['overlays']}",
        f"- Both-dataset 80%-coverage overlays: {len(both_cov)}",
        f"- Both-dataset 80%-coverage overlays positive on all splits: {len(both_all)}",
        "",
        "## Top Coverage-Preserving Overlays",
        "",
        "| rank | overlay | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | fresh | min OOS ROI | median ask |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(both_cov.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['overlay']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{int(row['fresh_wins'])}/{int(row['fresh_losses'])}, {fmt_cents(row['fresh_net_pnl_cents'])}, {pct(row['fresh_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} | {fmt_cents(row['max_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if both_cov.empty:
        lines.append("- No overlay preserved 80% coverage on both datasets.")
    else:
        best = both_cov.iloc[0].to_dict()
        lines.append(f"- Best coverage-preserving overlay: `{best['overlay']}`.")
        lines.append(
            f"- Fresh post-lock result for that overlay: {int(best['fresh_wins'])}/{int(best['fresh_losses'])}, "
            f"{fmt_cents(best['fresh_net_pnl_cents'])}, {pct(best['fresh_coverage'])} coverage."
        )
        lines.append(
            f"- Current/V21 all-ledger net: {fmt_cents(best['current_all_net_pnl_cents'])} / "
            f"{fmt_cents(best['v21_all_net_pnl_cents'])}."
        )
    if both_all.empty:
        lines.append("- No coverage-preserving overlay was positive on every train/validation/holdout split across both datasets.")
    else:
        lines.append(f"- {len(both_all)} coverage-preserving overlays were positive on all splits across both datasets.")
    lines.append("- This is not a promotion lock; it is an attribution scan for the next frozen challenger.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    csv_latest = OUT_DIR / "touch_hazard_blocker_overlays_latest.csv"
    csv_stamp = OUT_DIR / f"touch_hazard_blocker_overlays_{generated}.csv"
    md_latest = OUT_DIR / "touch_hazard_blocker_overlays_latest.md"
    md_stamp = OUT_DIR / f"touch_hazard_blocker_overlays_{generated}.md"
    json_latest = OUT_DIR / "touch_hazard_blocker_overlays_latest.json"
    json_stamp = OUT_DIR / f"touch_hazard_blocker_overlays_{generated}.json"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_coverage_count": int(results["both_coverage_pass"].sum()),
        "both_coverage_positive_all_count": int((results["both_coverage_pass"] & results["both_positive_all_splits"]).sum()),
        "top_rows": results.head(25).to_dict("records"),
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Touch-hazard blocker overlay scan complete")
    print(f"overlays={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
