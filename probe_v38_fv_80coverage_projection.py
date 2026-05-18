"""80%+ coverage P&L projection for pure FV probability candidates.

This probe is research-only. It does not score the live bot, modify the bot, or
submit orders.

The goal is to test whether the best FV surface candidate can support a broad
BTC 15m market policy. The projection is intentionally simple and auditable:

- use the minute-bucket replay rows;
- for each model and market-minute, pick the side with better model edge;
- enter once per market at the first minute where edge clears a threshold;
- hold to settlement;
- require train coverage of at least 80% of markets for ranked candidates.

Because FV is not an exit model, this is not a live-bot replacement backtest. It
is a consistent pressure test of whether a probability surface can carry broad
market coverage without immediately destroying P&L.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_minute_bucket_latest.csv"
REPORT_MD = OUT_DIR / "v38_fv_80coverage_projection_latest.md"
REPORT_JSON = OUT_DIR / "v38_fv_80coverage_projection_latest.json"
THRESHOLD_CSV = OUT_DIR / "v38_fv_80coverage_projection_thresholds_latest.csv"
PICK_CSV = OUT_DIR / "v38_fv_80coverage_projection_picks_latest.csv"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2_latest_score" / "summary.json"

MODELS = [
    "v28_live_surface",
    "v37_piecewise_dynamic_temp_antipersist3",
    "v38_long60_antipersist",
]
MIN_COVERAGE = 0.80
QTY = 2
THRESHOLDS = np.round(np.arange(-20.0, 20.0001, 0.25), 2)


def pct(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def load_rows() -> pd.DataFrame:
    usecols = {
        "opportunity_key",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "ask_cents",
        "split",
    }
    for model in MODELS:
        usecols.add(f"{model}_p_side")
        usecols.add(f"{model}_p_yes")
    rows = pd.read_csv(INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["ask_cents"] = pd.to_numeric(rows["ask_cents"], errors="coerce")
    if rows["win"].dtype == bool:
        rows["win_bool"] = rows["win"]
    else:
        rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    return rows.dropna(subset=["opportunity_key", "entry_dt", "market", "side", "ask_cents", "split"]).copy()


def best_side_by_opportunity(rows: pd.DataFrame, model: str) -> pd.DataFrame:
    work = rows[
        [
            "opportunity_key",
            "entry_dt",
            "market",
            "side",
            "outcome",
            "win_bool",
            "ask_cents",
            "split",
            f"{model}_p_side",
            f"{model}_p_yes",
        ]
    ].copy()
    work["model"] = model
    work["p_side"] = pd.to_numeric(work[f"{model}_p_side"], errors="coerce")
    work["p_yes"] = pd.to_numeric(work[f"{model}_p_yes"], errors="coerce")
    work["edge_cents"] = 100.0 * work["p_side"] - work["ask_cents"]
    work = work.dropna(subset=["p_side", "p_yes", "edge_cents"])
    work = work.sort_values(["opportunity_key", "edge_cents"], ascending=[True, False])
    return work.groupby("opportunity_key", as_index=False).head(1).sort_values(["market", "entry_dt"]).reset_index(drop=True)


def first_crossing(best: pd.DataFrame, threshold: float) -> pd.DataFrame:
    eligible = best[best["edge_cents"].ge(float(threshold))].copy()
    if eligible.empty:
        return eligible
    return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)


def market_universes(rows: pd.DataFrame) -> dict[str, set[str]]:
    out = {split: set(rows.loc[rows["split"].eq(split), "market"].astype(str).unique()) for split in ["train", "validation", "holdout"]}
    out["all"] = set(rows["market"].astype(str).unique())
    return out


def projection_metrics(picks: pd.DataFrame, universe: set[str]) -> dict[str, Any]:
    part = picks[picks["market"].astype(str).isin(universe)].copy()
    markets = int(len(universe))
    if markets == 0 or part.empty:
        return {
            "markets": markets,
            "trades": 0,
            "coverage": 0.0,
            "cost_dollars": 0.0,
            "pnl_dollars": 0.0,
            "roi": None,
            "wins": 0,
            "losses": 0,
            "avg_edge_cents": None,
            "avg_ask_cents": None,
        }
    ask = pd.to_numeric(part["ask_cents"], errors="coerce").to_numpy(dtype=float)
    wins = part["win_bool"].astype(bool).to_numpy()
    pnl_cents = np.where(wins, 100.0 - ask, -ask) * QTY
    cost_cents = ask * QTY
    cost = float(np.nansum(cost_cents) / 100.0)
    pnl = float(np.nansum(pnl_cents) / 100.0)
    return {
        "markets": markets,
        "trades": int(len(part)),
        "coverage": float(len(part) / markets),
        "cost_dollars": cost,
        "pnl_dollars": pnl,
        "roi": float(pnl / cost) if cost > 0 else None,
        "wins": int(wins.sum()),
        "losses": int((~wins).sum()),
        "avg_edge_cents": float(part["edge_cents"].mean()),
        "avg_ask_cents": float(part["ask_cents"].mean()),
    }


def flatten_record(model: str, threshold: float, metrics_by_split: dict[str, dict[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {"model": model, "threshold_cents": float(threshold)}
    for split, metrics in metrics_by_split.items():
        for key, value in metrics.items():
            record[f"{split}_{key}"] = value
    record["train_eligible_80"] = bool(metrics_by_split["train"]["coverage"] >= MIN_COVERAGE)
    record["all_splits_eligible_80"] = bool(all(metrics_by_split[s]["coverage"] >= MIN_COVERAGE for s in ["train", "validation", "holdout"]))
    record["all_splits_positive_pnl"] = bool(all(metrics_by_split[s]["pnl_dollars"] > 0 for s in ["train", "validation", "holdout"]))
    record["min_split_pnl_dollars"] = float(min(metrics_by_split[s]["pnl_dollars"] for s in ["train", "validation", "holdout"]))
    record["mean_split_roi"] = float(
        np.mean([metrics_by_split[s]["roi"] for s in ["train", "validation", "holdout"] if metrics_by_split[s]["roi"] is not None])
    )
    return record


def build() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows = load_rows()
    universes = market_universes(rows)
    threshold_records: list[dict[str, Any]] = []
    pick_frames: list[pd.DataFrame] = []
    for model in MODELS:
        best = best_side_by_opportunity(rows, model)
        for threshold in THRESHOLDS:
            picks = first_crossing(best, float(threshold))
            metrics = {split: projection_metrics(picks, universe) for split, universe in universes.items()}
            threshold_records.append(flatten_record(model, float(threshold), metrics))
        for threshold in [-1.75, -1.50, -1.25]:
            picks = first_crossing(best, float(threshold)).copy()
            picks["threshold_cents"] = float(threshold)
            pick_frames.append(picks)
    threshold_df = pd.DataFrame(threshold_records)
    picks_df = pd.concat(pick_frames, ignore_index=True, sort=False) if pick_frames else pd.DataFrame()
    metadata = {
        "input": str(INPUT),
        "models": MODELS,
        "min_coverage": MIN_COVERAGE,
        "qty": QTY,
        "markets": {split: len(universe) for split, universe in universes.items()},
    }
    return threshold_df, picks_df, metadata


def selected_rows(thresholds: pd.DataFrame) -> pd.DataFrame:
    selected: list[pd.Series] = []
    eligible = thresholds[thresholds["train_eligible_80"]].copy()
    for model in MODELS:
        part = eligible[eligible["model"].eq(model)].copy()
        if part.empty:
            continue
        selected.append(
            part.sort_values(["train_pnl_dollars", "train_roi", "all_coverage"], ascending=[False, False, False]).iloc[0]
        )
        stable = part[part["all_splits_eligible_80"] & part["all_splits_positive_pnl"]].copy()
        if not stable.empty:
            selected.append(
                stable.sort_values(["min_split_pnl_dollars", "all_pnl_dollars", "mean_split_roi"], ascending=[False, False, False]).iloc[0]
            )
    return pd.DataFrame(selected).drop_duplicates(["model", "threshold_cents"]).reset_index(drop=True)


def load_live_summary() -> dict[str, Any]:
    if not LIVE_SUMMARY.exists():
        return {}
    try:
        return json.loads(LIVE_SUMMARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_report(thresholds: pd.DataFrame, selected: pd.DataFrame, metadata: dict[str, Any]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    live = load_live_summary()
    lines = [
        "# v38 FV 80% Coverage Projection",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Pure FV probability projection, not live-bot scoring.",
        "- Uses first qualifying minute-bucket entry per market and holds to settlement.",
        "- Candidate ranking requires at least 80% train-market coverage.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Live Reference",
        "",
    ]
    if live:
        lines += [
            f"- Entries: {live.get('entries_total')}",
            f"- Open positions: {live.get('open_positions')}",
            f"- Net P&L: {dollars(live.get('net_pnl_total_dollars'))} on {dollars(live.get('gross_cost_basis_dollars'))} ({pct((live.get('net_pnl_total_percent') or 0) / 100.0)})",
            f"- Resolved/unresolved markets: {live.get('resolved_markets')} / {live.get('unresolved_markets')}",
            "",
        ]
    else:
        lines += ["- Latest live summary not found for comparison.", ""]
    lines += [
        "## Selected Thresholds",
        "",
        "| model | threshold | train cov | train P&L | train ROI | validation cov | validation P&L | validation ROI | holdout cov | holdout P&L | holdout ROI | all cov | all P&L | all ROI | stable 80+ positive? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in selected.iterrows():
        stable = bool(row["all_splits_eligible_80"] and row["all_splits_positive_pnl"])
        lines.append(
            f"| `{row['model']}` | {row['threshold_cents']:+.2f}c | "
            f"{pct(row['train_coverage'])} | {dollars(row['train_pnl_dollars'])} | {pct(row['train_roi'])} | "
            f"{pct(row['validation_coverage'])} | {dollars(row['validation_pnl_dollars'])} | {pct(row['validation_roi'])} | "
            f"{pct(row['holdout_coverage'])} | {dollars(row['holdout_pnl_dollars'])} | {pct(row['holdout_roi'])} | "
            f"{pct(row['all_coverage'])} | {dollars(row['all_pnl_dollars'])} | {pct(row['all_roi'])} | {stable} |"
        )
    v38 = selected[selected["model"].eq("v38_long60_antipersist")].copy()
    best_v38 = None if v38.empty else v38.sort_values(["all_splits_positive_pnl", "all_pnl_dollars"], ascending=[False, False]).iloc[0]
    lines += [
        "",
        "## Read",
        "",
    ]
    if best_v38 is not None:
        lines.append(
            f"- Best selected v38 row trades {pct(best_v38['all_coverage'])} of replay markets with "
            f"{dollars(best_v38['all_pnl_dollars'])} projected P&L on {dollars(best_v38['all_cost_dollars'])} "
            f"({pct(best_v38['all_roi'])})."
        )
    lines += [
        "- This projection is useful for broad-coverage pressure testing, but it is not a substitute for strict forward validation or an exit-aware strategy replay.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "selected": selected.to_dict("records"),
                    "live_summary": live,
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    thresholds, picks, metadata = build()
    selected = selected_rows(thresholds)
    thresholds.to_csv(THRESHOLD_CSV, index=False)
    picks.to_csv(PICK_CSV, index=False)
    write_report(thresholds, selected, metadata)
    print("v38 FV 80% coverage projection complete")
    print(f"threshold_rows={len(thresholds)} selected_rows={len(selected)} report={REPORT_MD}")
    if not selected.empty:
        best = selected[selected["model"].eq("v38_long60_antipersist")]
        if not best.empty:
            row = best.sort_values(["all_splits_positive_pnl", "all_pnl_dollars"], ascending=[False, False]).iloc[0]
            print(
                "best_v38 "
                f"threshold={row['threshold_cents']:+.2f}c "
                f"coverage={row['all_coverage']:.4f} "
                f"pnl={row['all_pnl_dollars']:.2f} "
                f"roi={row['all_roi']:.4f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
