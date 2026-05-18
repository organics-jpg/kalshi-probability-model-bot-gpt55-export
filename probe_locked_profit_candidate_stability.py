"""Stability audit for the locked BTC 15m profit-frontier candidate.

The profit frontier found broad EV-positive rules whose hit rate is far below
95%. This audit asks whether the locked rule is stable enough to keep testing:
does profit survive across datasets, splits, sides, price/time/vol regimes, and
simple unseen-loss stress?

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import LOCK_PATH, policy_from_record


BOOTSTRAP_SAMPLES = 10_000
RNG_SEED = 20260502


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


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(side_rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str = "all") -> Dict[str, Any]:
    out = split_metric(base, selected, split)
    out["wilson_minus_break_even"] = (
        (out["wilson95_lower"] or 0.0) - (out["fee_aware_break_even_accuracy"] or 1.0)
    )
    out["coverage_pass"] = (out["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    out["positive_net"] = (out["net_pnl_cents"] or 0.0) > 0.0
    return out


def group_metric(selected: pd.DataFrame, group_col: str) -> List[Dict[str, Any]]:
    if selected.empty or group_col not in selected.columns:
        return []
    rows: List[Dict[str, Any]] = []
    for name, part in selected.groupby(group_col, dropna=False, sort=False, observed=True):
        n = int(len(part))
        wins = int(part["win"].sum()) if n else 0
        cost = float(part["entry_cost_cents"].sum()) if n else 0.0
        net = float(part["net_pnl_cents"].sum()) if n else 0.0
        break_even = float(part["fee_aware_break_even_p"].mean()) if n else None
        acc = wins / n if n else None
        rows.append(
            {
                "group": str(name),
                "markets": n,
                "wins": wins,
                "losses": n - wins,
                "accuracy": acc,
                "break_even": break_even,
                "accuracy_minus_break_even": (acc - break_even) if acc is not None and break_even is not None else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "median_ask": float(part["ask_cents"].median()) if n else None,
                "median_seconds_to_close": float(part["seconds_to_close"].median()) if n else None,
            }
        )
    rows.sort(key=lambda row: (row["net_pnl_cents"], row["markets"]))
    return rows


def add_regime_bins(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    for col in [
        "ask_cents",
        "seconds_to_close",
        "rv_sigma_t_15m",
        "margin_per_rv_sigma_15m",
        "brownian_p_rv_15m",
        "adverse_move_15m",
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
    out = out.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    if len(out) >= 5:
        out["time_block"] = pd.qcut(np.arange(len(out)), q=5, labels=["block1", "block2", "block3", "block4", "block5"])
    else:
        out["time_block"] = "all"
    return out


def bootstrap_edge(values: Iterable[float]) -> Dict[str, Any]:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    n = int(len(arr))
    if n <= 0:
        return {"n": 0, "mean_cents": None, "p05_mean_cents": None, "p95_mean_cents": None, "prob_mean_le_zero": None}
    rng = np.random.default_rng(RNG_SEED + n)
    sample_idx = rng.integers(0, n, size=(BOOTSTRAP_SAMPLES, n))
    means = arr[sample_idx].mean(axis=1)
    return {
        "n": n,
        "mean_cents": float(arr.mean()),
        "sd_cents": float(arr.std(ddof=1)) if n > 1 else 0.0,
        "p05_mean_cents": float(np.quantile(means, 0.05)),
        "p95_mean_cents": float(np.quantile(means, 0.95)),
        "prob_mean_le_zero": float((means <= 0.0).mean()),
    }


def min_n_for_wilson_edge(observed_accuracy: Optional[float], break_even: Optional[float]) -> Optional[int]:
    if observed_accuracy is None or break_even is None:
        return None
    if observed_accuracy <= break_even:
        return None
    for n in range(1, 5001):
        wins = int(math.floor(observed_accuracy * n))
        if wins / n < observed_accuracy - (1.0 / n):
            wins += 1
        if wins > n:
            wins = n
        if wilson_lower(wins, n) is not None and wilson_lower(wins, n) >= break_even:
            return n
    return None


def unseen_loss_stress(selected: pd.DataFrame) -> Dict[str, Any]:
    if selected.empty:
        return {}
    net = float(selected["net_pnl_cents"].sum())
    loss_rows = selected[~selected["win"]].copy()
    if loss_rows.empty:
        typical_loss = -float(selected["entry_cost_cents"].median())
        worst_loss = -float(selected["entry_cost_cents"].max())
    else:
        typical_loss = float(loss_rows["net_pnl_cents"].median())
        worst_loss = float(loss_rows["net_pnl_cents"].min())
    typical_needed = math.floor(net / abs(typical_loss)) + 1 if net > 0 and typical_loss < 0 else 0
    worst_needed = math.floor(net / abs(worst_loss)) + 1 if net > 0 and worst_loss < 0 else 0
    return {
        "net_pnl_cents": net,
        "typical_loss_cents": typical_loss,
        "worst_loss_cents": worst_loss,
        "typical_extra_losses_to_zero": int(typical_needed),
        "worst_extra_losses_to_zero": int(worst_needed),
    }


def evaluate_dataset(name: str, side_rows: pd.DataFrame, lock: Dict[str, Any]) -> Dict[str, Any]:
    base = market_base(side_rows)
    policy = policy_from_record(lock["policy"])
    selected = add_regime_bins(select_for_policy(side_rows, base, policy))
    by_split = {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}
    by_group = {
        group_col: group_metric(selected, group_col)
        for group_col in ["split", "side", "ask_bin", "seconds_bin", "rv15_bin", "margin_rv15_bin", "brownian_bin", "adverse15_bin", "time_block"]
    }
    boot = bootstrap_edge(selected["net_pnl_cents"])
    all_metric = by_split["all"]
    required_n = min_n_for_wilson_edge(all_metric["accuracy"], all_metric["fee_aware_break_even_accuracy"])
    return {
        "name": name,
        "base_markets": int(len(base)),
        "selected_markets": int(len(selected)),
        "policy": lock["policy"],
        "by_split": by_split,
        "by_group": by_group,
        "bootstrap": boot,
        "unseen_loss_stress": unseen_loss_stress(selected),
        "selected": selected,
        "wilson_edge_min_n_at_observed_accuracy": required_n,
    }


def current_fresh_eval(current_eval: Dict[str, Any], lock: Dict[str, Any]) -> Dict[str, Any]:
    selected = current_eval["selected"]
    side_rows = load_side_rows()
    base = market_base(side_rows)
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
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
        "wilson_edge_min_n_at_observed_accuracy": min_n_for_wilson_edge(
            fresh_metric["accuracy"], fresh_metric["fee_aware_break_even_accuracy"]
        ),
    }


def table_lines_for_groups(rows: List[Dict[str, Any]], limit: int = 10) -> List[str]:
    lines = [
        "| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows[:limit]:
        lines.append(
            f"| `{row['group']}` | {row['markets']} | {row['wins']}/{row['losses']} | "
            f"{pct(row['accuracy'])} | {pct(row['break_even'])} | "
            f"{pct(row['accuracy_minus_break_even'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} |"
        )
    return lines


def write_report(path: Path, generated: str, lock: Dict[str, Any], current: Dict[str, Any], v21: Dict[str, Any], fresh: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Locked Profit Candidate Stability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests the locked profit candidate without retuning it after later refreshed markets.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "- Selection uses only pre-entry fields in the lock: Brownian RV15 probability, ask, seconds-to-close, 15m adverse move, and RV-normalized margin.",
        "",
        "## Locked Policy",
        "",
        f"- Label: `{lock['policy']['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Lock file: `{LOCK_PATH}`",
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
                f"{fmt_num(row['wilson_minus_break_even'], 3)} | {pct(row['coverage'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_roi(row['net_roi_on_cost'])} |"
            )
    lines += [
        "",
        "## Fresh After Lock",
        "",
    ]
    fm = fresh["metric"]
    lines.append(
        f"- Fresh current markets: {int(fm['markets'])}/{int(fm['base_markets'])}; "
        f"wins/losses {int(fm['wins'])}/{int(fm['losses'])}; net {fmt_cents(fm['net_pnl_cents'])}; "
        f"ROI {fmt_roi(fm['net_roi_on_cost'])}; Wilson edge {fmt_num(fm['wilson_minus_break_even'], 3)}."
    )
    lines.append(
        f"- Fresh extra typical losses to wipe current fresh P&L: "
        f"{fresh['unseen_loss_stress'].get('typical_extra_losses_to_zero', 'NA')}."
    )
    lines.append("")
    lines += [
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
            f"{fmt_num(boot['prob_mean_le_zero'], 3)} | "
            f"{stress.get('typical_extra_losses_to_zero')} | {stress.get('worst_extra_losses_to_zero')} | "
            f"{dataset['wilson_edge_min_n_at_observed_accuracy'] or 'NA'} |"
        )
    lines.append("")
    for dataset in [current, v21]:
        lines += [f"## Weakest Regime Slices: {dataset['name'].title()}", ""]
        weak_rows: List[Dict[str, Any]] = []
        for key in ["split", "side", "ask_bin", "seconds_bin", "rv15_bin", "margin_rv15_bin", "brownian_bin", "adverse15_bin", "time_block"]:
            for row in dataset["by_group"].get(key, []):
                tagged = dict(row)
                tagged["group"] = f"{key}={row['group']}"
                weak_rows.append(tagged)
        weak_rows.sort(key=lambda row: (row["net_pnl_cents"], row["markets"]))
        lines += table_lines_for_groups(weak_rows, limit=12)
        lines.append("")
    lines += ["## Read", ""]
    current_all = current["by_split"]["all"]
    v21_all = v21["by_split"]["all"]
    if (current_all["net_pnl_cents"] or 0) > 0 and (v21_all["net_pnl_cents"] or 0) > 0:
        lines.append("- The locked candidate remains net-positive on both full datasets after the latest refresh.")
    if (current["by_split"]["train"]["net_pnl_cents"] or 0) <= 0:
        lines.append("- Current train split is negative, so the edge is not uniformly stable inside the current capture.")
    if (fresh["metric"]["markets"] or 0) < 30:
        lines.append("- Fresh post-lock sample is too small for promotion-quality EV evidence.")
    lines.append("- Keep the lock unchanged and let fresh evidence accumulate; retuning to the refreshed top row would contaminate forward validation.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    if not LOCK_PATH.exists():
        raise SystemExit(f"Missing profit lock: {LOCK_PATH}")
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    current = evaluate_dataset("current", load_side_rows(), lock)
    v21 = evaluate_dataset("v21", load_v21_side_rows(), lock)
    fresh = current_fresh_eval(current, lock)
    current_selected = current.pop("selected")
    v21_selected = v21.pop("selected")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_latest = OUT_DIR / "locked_profit_candidate_stability_latest.md"
    md_stamp = OUT_DIR / f"locked_profit_candidate_stability_{generated}.md"
    json_latest = OUT_DIR / "locked_profit_candidate_stability_latest.json"
    json_stamp = OUT_DIR / f"locked_profit_candidate_stability_{generated}.json"
    current_csv = OUT_DIR / "locked_profit_candidate_current_selected_latest.csv"
    v21_csv = OUT_DIR / "locked_profit_candidate_v21_selected_latest.csv"
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
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Locked profit candidate stability audit complete")
    print(f"current_net={current['by_split']['all']['net_pnl_cents']} v21_net={v21['by_split']['all']['net_pnl_cents']}")
    print(f"fresh_markets={fresh['metric']['markets']} fresh_net={fresh['metric']['net_pnl_cents']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
