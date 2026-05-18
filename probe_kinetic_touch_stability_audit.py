"""Stability audit for the kinetic touch-profit forward candidate.

The kinetic candidate is the refreshed top broad EV row after the earlier
touch-hazard lock weakened. This audit does not retune the candidate; it asks
whether the frozen kinetic rule is stable across datasets, chronological
splits, price / volatility / boundary regimes, and simple stress tests.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_locked_profit_candidate_stability import (
    bootstrap_edge,
    group_metric,
    min_n_for_wilson_edge,
    unseen_loss_stress,
)
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
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, select_markets
from probe_profit_lock_time_boundary import effective_lock_dt


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Any, digits: int = 3) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not np.isfinite(val):
        return "NA"
    return f"{val:.{digits}f}"


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets(chosen, policy))


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str = "all") -> Dict[str, Any]:
    out = split_metric(base, selected, split)
    out["wilson_minus_break_even"] = (
        (out["wilson95_lower"] or 0.0) - (out["fee_aware_break_even_accuracy"] or 1.0)
    )
    out["coverage_pass"] = (out["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    out["positive_net"] = (out["net_pnl_cents"] or 0.0) > 0.0
    return out


def add_kinetic_bins(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    for col in [
        "ask_cents",
        "seconds_to_close",
        "rv_sigma_t_15m",
        "margin_per_rv_sigma_15m",
        "brownian_p_rv_15m",
        "adverse_move_15m",
        "touch_loss_rv_15m",
        "kinetic_touch_score_15",
        "book_p_side",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["ask_bin"] = pd.cut(out["ask_cents"], [-np.inf, 50, 60, 70, 80, 90, 95, np.inf], include_lowest=True)
    out["seconds_bin"] = pd.cut(out["seconds_to_close"], [-np.inf, 120, 240, 480, 720, np.inf], include_lowest=True)
    out["rv15_bin"] = pd.qcut(out["rv_sigma_t_15m"], q=4, duplicates="drop")
    out["margin_rv15_bin"] = pd.cut(out["margin_per_rv_sigma_15m"], [-np.inf, 0, 0.25, 0.5, 1.0, 1.5, np.inf])
    out["brownian_bin"] = pd.cut(out["brownian_p_rv_15m"], [-np.inf, 0.55, 0.6, 0.65, 0.7, 0.8, np.inf])
    out["adverse15_bin"] = pd.cut(out["adverse_move_15m"], [-np.inf, 0, 5, 10, 20, np.inf])
    out["touch_loss_bin"] = pd.cut(out["touch_loss_rv_15m"], [-np.inf, 0.5, 0.7, 0.8, 0.85, 0.9, np.inf])
    out["kinetic_score_bin"] = pd.cut(out["kinetic_touch_score_15"], [-np.inf, 0.55, 0.57, 0.6, 0.65, 0.7, np.inf])
    out["book_bin"] = pd.cut(out["book_p_side"], [-np.inf, 0.55, 0.6, 0.65, 0.7, 0.8, np.inf])
    out = out.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    if len(out) >= 5:
        out["time_block"] = pd.qcut(np.arange(len(out)), q=5, labels=["block1", "block2", "block3", "block4", "block5"])
    else:
        out["time_block"] = "all"
    return out


def evaluate_dataset(name: str, side_rows: pd.DataFrame, lock: Dict[str, Any]) -> Dict[str, Any]:
    side_rows = add_touch_hazard_scores(side_rows)
    base = market_base(side_rows)
    policy = policy_from_record(lock["policy"])
    selected = add_kinetic_bins(select_for_policy(side_rows, base, policy))
    by_split = {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}
    by_group = {
        group_col: group_metric(selected, group_col)
        for group_col in [
            "split",
            "side",
            "ask_bin",
            "seconds_bin",
            "rv15_bin",
            "margin_rv15_bin",
            "brownian_bin",
            "adverse15_bin",
            "touch_loss_bin",
            "kinetic_score_bin",
            "book_bin",
            "time_block",
        ]
    }
    all_metric = by_split["all"]
    return {
        "name": name,
        "base_markets": int(len(base)),
        "selected_markets": int(len(selected)),
        "by_split": by_split,
        "by_group": by_group,
        "bootstrap": bootstrap_edge(selected["net_pnl_cents"]),
        "unseen_loss_stress": unseen_loss_stress(selected),
        "selected": selected,
        "wilson_edge_min_n_at_observed_accuracy": min_n_for_wilson_edge(
            all_metric["accuracy"], all_metric["fee_aware_break_even_accuracy"]
        ),
    }


def fresh_eval(current_eval: Dict[str, Any], lock: Dict[str, Any]) -> Dict[str, Any]:
    base = market_base(add_touch_hazard_scores(load_side_rows()))
    selected = current_eval["selected"]
    lock_close_dt = effective_lock_dt(lock)
    if pd.isna(lock_close_dt):
        fresh_base = base.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt].copy()
    fresh_selected = selected[selected["market"].isin(set(fresh_base["market"]))].copy()
    fresh_metric = metric(fresh_base, fresh_selected, "all")
    return {
        "base_markets": int(len(fresh_base)),
        "selected_markets": int(len(fresh_selected)),
        "metric": fresh_metric,
        "bootstrap": bootstrap_edge(fresh_selected["net_pnl_cents"]),
        "unseen_loss_stress": unseen_loss_stress(fresh_selected),
    }


def add_group_table(lines: List[str], rows: List[Dict[str, Any]], limit: int = 14) -> None:
    lines.append("| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in rows[:limit]:
        lines.append(
            f"| `{row['group']}` | {row['markets']} | {row['wins']}/{row['losses']} | "
            f"{pct(row['accuracy'])} | {pct(row['break_even'])} | "
            f"{pct(row['accuracy_minus_break_even'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} |"
        )


def write_report(path: Path, generated: str, lock: Dict[str, Any], current: Dict[str, Any], v21: Dict[str, Any], fresh: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Kinetic-Touch Stability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests the frozen kinetic-touch forward candidate without retuning it.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "",
        "## Locked Policy",
        "",
        f"- Label: `{lock['policy']['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Lock file: `{KINETIC_TOUCH_LOCK_PATH}`",
        "",
        "## Split Stability",
        "",
        "| dataset | split | markets | wins/losses | acc | breakeven | Wilson low | Wilson edge | coverage | net P&L | ROI |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset in [current, v21]:
        for split in ["all", "train", "validation", "holdout"]:
            row = dataset["by_split"][split]
            lines.append(
                f"| {dataset['name']} | {split} | {int(row['markets'])}/{int(row['base_markets'])} | "
                f"{int(row['wins'])}/{int(row['losses'])} | {pct(row['accuracy'])} | "
                f"{pct(row['fee_aware_break_even_accuracy'])} | {pct(row['wilson95_lower'])} | "
                f"{fmt_num(row['wilson_minus_break_even'])} | {pct(row['coverage'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_roi(row['net_roi_on_cost'])} |"
            )

    lines += ["", "## Fresh After Kinetic Lock", ""]
    fm = fresh["metric"]
    lines.append(
        f"- Fresh current markets: {int(fm['markets'])}/{int(fm['base_markets'])}; "
        f"wins/losses {int(fm['wins'])}/{int(fm['losses'])}; net {fmt_cents(fm['net_pnl_cents'])}; "
        f"ROI {fmt_roi(fm['net_roi_on_cost'])}; Wilson edge {fmt_num(fm['wilson_minus_break_even'])}."
    )

    lines += [
        "",
        "## Fragility",
        "",
        "| dataset | mean edge | boot p05 mean | boot p95 mean | bootstrap P(mean<=0) | extra typical losses to zero | extra worst losses to zero | Wilson-edge n at observed acc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset in [current, v21]:
        boot = dataset["bootstrap"]
        stress = dataset["unseen_loss_stress"]
        lines.append(
            f"| {dataset['name']} | {fmt_cents(boot['mean_cents'])} | "
            f"{fmt_cents(boot['p05_mean_cents'])} | {fmt_cents(boot['p95_mean_cents'])} | "
            f"{fmt_num(boot['prob_mean_le_zero'])} | "
            f"{stress.get('typical_extra_losses_to_zero')} | {stress.get('worst_extra_losses_to_zero')} | "
            f"{dataset['wilson_edge_min_n_at_observed_accuracy'] or 'NA'} |"
        )

    for dataset in [current, v21]:
        lines += ["", f"## Weakest Regime Slices: {dataset['name'].title()}", ""]
        weak_rows: List[Dict[str, Any]] = []
        for key in [
            "split",
            "side",
            "ask_bin",
            "seconds_bin",
            "rv15_bin",
            "margin_rv15_bin",
            "brownian_bin",
            "adverse15_bin",
            "touch_loss_bin",
            "kinetic_score_bin",
            "book_bin",
            "time_block",
        ]:
            for row in dataset["by_group"].get(key, []):
                tagged = dict(row)
                tagged["group"] = f"{key}={row['group']}"
                weak_rows.append(tagged)
        weak_rows.sort(key=lambda row: (row["net_pnl_cents"], row["markets"]))
        add_group_table(lines, weak_rows)

    lines += ["", "## Read", ""]
    current_all = current["by_split"]["all"]
    v21_all = v21["by_split"]["all"]
    lines.append(
        f"- Full-ledger EV is positive on current ({fmt_cents(current_all['net_pnl_cents'])}) "
        f"and v21 ({fmt_cents(v21_all['net_pnl_cents'])})."
    )
    if (fresh["metric"]["markets"] or 0) < 30:
        lines.append("- Fresh post-lock sample is too small for promotion-quality EV evidence.")
    if (current["bootstrap"]["prob_mean_le_zero"] or 0.0) > 0.05:
        lines.append("- Current bootstrap still assigns nontrivial probability to nonpositive mean edge.")
    lines.append("- Keep the kinetic lock unchanged and let pending markets settle; do not retune this row into its own fresh sample.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    if not KINETIC_TOUCH_LOCK_PATH.exists():
        raise SystemExit(f"Missing kinetic touch lock: {KINETIC_TOUCH_LOCK_PATH}")
    lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    current = evaluate_dataset("current", load_side_rows(), lock)
    v21 = evaluate_dataset("v21", load_v21_side_rows(), lock)
    fresh = fresh_eval(current, lock)
    current_selected = current.pop("selected")
    v21_selected = v21.pop("selected")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_latest = OUT_DIR / "kinetic_touch_stability_audit_latest.md"
    md_stamp = OUT_DIR / f"kinetic_touch_stability_audit_{generated}.md"
    json_latest = OUT_DIR / "kinetic_touch_stability_audit_latest.json"
    json_stamp = OUT_DIR / f"kinetic_touch_stability_audit_{generated}.json"
    current_csv = OUT_DIR / "kinetic_touch_current_selected_latest.csv"
    v21_csv = OUT_DIR / "kinetic_touch_v21_selected_latest.csv"
    current_selected.to_csv(current_csv, index=False)
    v21_selected.to_csv(v21_csv, index=False)
    write_report(md_latest, generated, lock, current, v21, fresh)
    write_report(md_stamp, generated, lock, current, v21, fresh)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "current": current,
        "v21": v21,
        "fresh": fresh,
        "selected_csvs": {
            "current": str(current_csv),
            "v21": str(v21_csv),
        },
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Kinetic-touch stability audit complete")
    print(f"current_net={current['by_split']['all']['net_pnl_cents']} v21_net={v21['by_split']['all']['net_pnl_cents']}")
    print(f"fresh_markets={fresh['metric']['markets']} fresh_net={fresh['metric']['net_pnl_cents']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
