"""Research-only staged interval policy scan.

The raw interval pass covers 80%+ of recurring BTC 15m markets at high realized
accuracy, but it is dominated by late/high-price states. This probe tests a
causal staged policy: at each heartbeat, try an economical physics/book gate
first; if it does not pass at that heartbeat, try a stricter fallback gate. The
first eligible heartbeat in each market is the selected trade.

The unit of volume is still recurring market intervals. This script reads only
research ledgers and writes under logs/edge_research; it does not import or
modify the live bot.
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

from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


def wilson_lower_bound(wins: int, total: int, z: float = 1.96) -> Optional[float]:
    if total <= 0:
        return None
    phat = wins / total
    denom = 1.0 + z * z / total
    centre = phat + z * z / (2.0 * total)
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total)
    return (centre - margin) / denom


@dataclass(frozen=True)
class StageSpec:
    name: str
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float = 0.0
    max_seconds_to_close: Optional[float] = None
    gate: str = "none"

    @property
    def label(self) -> str:
        parts = [
            self.name,
            f"choose={self.chooser}",
            f"{self.chooser}>={self.min_score:g}",
            f"ask<={self.ask_max:g}",
            f"sec>={self.min_seconds_to_close:g}",
        ]
        if self.max_seconds_to_close is not None:
            parts.append(f"sec<={self.max_seconds_to_close:g}")
        if self.gate != "none":
            parts.append(self.gate)
        return "; ".join(parts)


def gate_mask(df: pd.DataFrame, stage: StageSpec) -> pd.Series:
    mask = (
        df[stage.chooser].ge(stage.min_score)
        & df["ask_cents"].le(stage.ask_max)
        & df["seconds_to_close"].ge(stage.min_seconds_to_close)
    )
    if stage.max_seconds_to_close is not None:
        mask &= df["seconds_to_close"].le(stage.max_seconds_to_close)
    if stage.gate == "none":
        return mask.fillna(False)
    if stage.gate == "adverse15<=10_or_margin_rv15>=0.5":
        mask &= df["adverse_move_15m"].le(10) | df["margin_per_rv_sigma_15m"].ge(0.5)
    elif stage.gate == "brownian15>=0.55_and_brownian30>=0.55":
        mask &= df["brownian_p_rv_15m"].ge(0.55) & df["brownian_p_rv_30m"].ge(0.55)
    elif stage.gate == "spread<=4":
        mask &= df["spread_cents"].le(4)
    elif stage.gate == "margin_rv15>=0":
        mask &= df["margin_per_rv_sigma_15m"].ge(0)
    elif stage.gate == "book_rv_gap<=0.20":
        mask &= df["abs_book_rv15_gap"].le(0.20)
    else:
        raise ValueError(f"unknown gate: {stage.gate}")
    return mask.fillna(False)


def choose_decision_sides(side_rows: pd.DataFrame, chooser: str) -> pd.DataFrame:
    usable = side_rows[side_rows[chooser].notna()].copy()
    if usable.empty:
        return usable
    chosen = (
        usable.sort_values(["decision_key", chooser, "book_p_side"], ascending=[True, False, False])
        .groupby("decision_key", as_index=False, sort=False)
        .first()
    )
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def make_stage1_specs() -> List[StageSpec]:
    specs: List[StageSpec] = []
    for chooser in ["book_p_side", "score_mean_book_rv15", "score_min_book_rv15"]:
        for threshold in [0.80, 0.85, 0.90]:
            for ask_max in [90.0, 95.0]:
                for min_sec in [60.0, 120.0]:
                    for gate in ["none", "adverse15<=10_or_margin_rv15>=0.5"]:
                        specs.append(StageSpec("economical", chooser, threshold, ask_max, min_sec, None, gate))
    return specs


def make_fallback_specs() -> List[StageSpec]:
    specs: List[StageSpec] = []
    for chooser in ["book_p_side", "score_min_book_rv15"]:
        for threshold in [0.90, 0.95]:
            for ask_max in [98.0, 100.0]:
                for max_sec in [300.0, None]:
                    specs.append(StageSpec("fallback", chooser, threshold, ask_max, 0.0, max_sec, "none"))
    return specs


def eligible_rows(chosen_cache: Dict[str, pd.DataFrame], stage: StageSpec, stage_rank: int) -> pd.DataFrame:
    chosen = chosen_cache.get(stage.chooser)
    if chosen is None or chosen.empty:
        return pd.DataFrame()
    rows = chosen[gate_mask(chosen, stage)].copy()
    if rows.empty:
        return rows
    rows["stage_rank"] = stage_rank
    rows["stage_name"] = stage.name
    rows["stage_label"] = stage.label
    return rows


def select_staged(
    chosen_cache: Dict[str, pd.DataFrame],
    stage1: StageSpec,
    fallback: StageSpec,
) -> pd.DataFrame:
    first_rows = eligible_rows(chosen_cache, stage1, 1)
    fallback_rows = eligible_rows(chosen_cache, fallback, 2)
    if first_rows.empty and fallback_rows.empty:
        return pd.DataFrame()
    combined = pd.concat([first_rows, fallback_rows], ignore_index=True)
    selected = (
        combined.sort_values(["market", "entry_dt", "stage_rank"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return selected


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    stake = float(selected_part["ask_cents"].sum()) if rows else 0.0
    pnl = float(((100.0 - selected_part["ask_cents"]) * selected_part["win"] - selected_part["ask_cents"] * (~selected_part["win"])).sum()) if rows else 0.0
    return {
        "markets": rows,
        "wins": wins,
        "losses": rows - wins,
        "base_markets": int(len(base_part)),
        "accuracy": wins / rows if rows else None,
        "coverage": rows / len(base_part) if len(base_part) else None,
        "wilson_low": wilson_lower_bound(wins, rows),
        "median_ask": float(selected_part["ask_cents"].median()) if rows else None,
        "p75_ask": float(selected_part["ask_cents"].quantile(0.75)) if rows else None,
        "ask_ge_95": int((selected_part["ask_cents"] >= 95).sum()) if rows else 0,
        "ask_eq_100": int((selected_part["ask_cents"] >= 100).sum()) if rows else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if rows else None,
        "gross_pnl_cents": pnl,
        "stake_cents": stake,
        "gross_roi": pnl / stake if stake else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    for split in ["all", "train", "validation", "holdout"]:
        if (metrics[split]["coverage"] or 0.0) < MARKET_COVERAGE_FLOOR:
            return False
        if (metrics[split]["accuracy"] or 0.0) < TARGET_ACCURACY:
            return False
    return metrics["all"]["markets"] >= MIN_SELECTED_MARKETS and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS


def less_degenerate_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    all_m = metrics["all"]
    return (
        target_pass(metrics)
        and (all_m["median_ask"] or 100.0) <= 94.0
        and (all_m["ask_eq_100"] or 0) == 0
        and (all_m["wilson_low"] or 0.0) >= TARGET_ACCURACY
    )


def flatten(stage1: StageSpec, fallback: StageSpec, selected: pd.DataFrame, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "stage1": stage1.label,
        "fallback": fallback.label,
        "target_pass": target_pass(metrics),
        "less_degenerate_pass": less_degenerate_pass(metrics),
        "stage1_markets": int((selected["stage_name"] == "economical").sum()) if not selected.empty else 0,
        "fallback_markets": int((selected["stage_name"] == "fallback").sum()) if not selected.empty else 0,
    }
    row["min_test_accuracy"] = min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0)
    row["min_test_coverage"] = min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["less_degenerate_pass"]),
        int(row["target_pass"]),
        row["min_test_accuracy"],
        row["all_wilson_low"] or 0.0,
        -(row["all_median_ask"] or 100.0),
        -(row["all_ask_eq_100"] or 999),
        row["all_gross_roi"] or -999,
        row["min_test_coverage"],
    )


def scan(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    stage1_specs = make_stage1_specs()
    fallback_specs = make_fallback_specs()
    all_specs = stage1_specs + fallback_specs
    chosen_cache = {chooser: choose_decision_sides(side_rows, chooser) for chooser in sorted({spec.chooser for spec in all_specs})}
    eligible_cache = {
        spec.label: eligible_rows(chosen_cache, spec, 1 if spec.name == "economical" else 2)
        for spec in all_specs
    }
    rows: List[Dict[str, Any]] = []
    for stage1 in stage1_specs:
        for fallback in fallback_specs:
            first_rows = eligible_cache.get(stage1.label, pd.DataFrame())
            fallback_rows = eligible_cache.get(fallback.label, pd.DataFrame())
            if first_rows.empty and fallback_rows.empty:
                selected = pd.DataFrame()
            else:
                selected = (
                    pd.concat([first_rows, fallback_rows], ignore_index=True)
                    .sort_values(["market", "entry_dt", "stage_rank"])
                    .groupby("market", as_index=False, sort=False)
                    .first()
                    .sort_values(["entry_dt", "market"])
                    .reset_index(drop=True)
                )
            metrics = metrics_for(base, selected)
            rows.append(flatten(stage1, fallback, selected, metrics))
    rows.sort(key=rank_key, reverse=True)
    return pd.DataFrame(rows)


def write_report(path: Path, generated: str, base: pd.DataFrame, results: pd.DataFrame) -> None:
    lines: List[str] = []
    lines.append("# Staged BTC 15m Interval Policy Scan")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only scan; no orders are submitted and no bot files are modified.")
    lines.append("- Unit of volume is the recurring BTC 15-minute market ticker.")
    lines.append("- Staging is causal: at each heartbeat, economical gate is checked first, then fallback gate; first eligible heartbeat per market is selected.")
    lines.append("- Goal is to preserve >=80% market coverage and >=95% accuracy while reducing high-price/late-entry degeneracy.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Resolved intervals: {len(base)}")
    for split in ["train", "validation", "holdout"]:
        lines.append(f"- {split.title()} intervals: {int((base['split'] == split).sum())}")
    lines.append(f"- Staged candidates scanned: {len(results)}")
    lines.append(f"- Raw target-pass candidates: {int(results['target_pass'].sum())}")
    lines.append(f"- Less-degenerate target-pass candidates: {int(results['less_degenerate_pass'].sum())}")
    lines.append("")

    def table(title: str, frame: pd.DataFrame) -> None:
        lines.append(title)
        lines.append("")
        if frame.empty:
            lines.append("No rows.")
            lines.append("")
            return
        lines.append("| rank | stage1 markets | fallback markets | all acc | all cov | Wilson low | val acc | holdout acc | median ask | ask=100 | ROI | target | less-degen |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
        for idx, row in enumerate(frame.head(15).to_dict("records"), start=1):
            lines.append(
                f"| {idx} | {int(row['stage1_markets'])} | {int(row['fallback_markets'])} | "
                f"{pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | {pct(row['all_wilson_low'])} | "
                f"{pct(row['validation_accuracy'])} | {pct(row['holdout_accuracy'])} | "
                f"{row['all_median_ask']:.1f} | {int(row['all_ask_eq_100'])} | {pct(row['all_gross_roi'])} | "
                f"{row['target_pass']} | {row['less_degenerate_pass']} |"
            )
        lines.append("")
        best = frame.head(1).to_dict("records")[0]
        lines.append("Best row policy detail:")
        lines.append("")
        lines.append(f"- Stage 1: `{best['stage1']}`")
        lines.append(f"- Fallback: `{best['fallback']}`")
        lines.append("")

    table("## Target-Passing Staged Candidates", results[results["target_pass"]])
    table("## Best Less-Degenerate Candidates", results[results["less_degenerate_pass"]])
    table("## Best Overall Candidates", results)

    lines.append("## Conclusion")
    lines.append("")
    if int(results["less_degenerate_pass"].sum()) > 0:
        lines.append("A staged policy cleared the full target with lower degeneracy flags. It still needs fresh locked interval validation before promotion.")
    elif int(results["target_pass"].sum()) > 0:
        lines.append("Staging can preserve raw 95% / 80% interval performance, but no staged candidate removed the high-price/sample-size degeneracy.")
    else:
        lines.append("No staged interval policy cleared 95% accuracy while covering 80% of recurring markets.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    side_rows = load_side_rows()
    base = market_base(side_rows)
    results = scan(base, side_rows)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    csv_latest = OUT_DIR / "staged_interval_policy_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"staged_interval_policy_candidates_{generated}.csv"
    md_latest = OUT_DIR / "staged_interval_policy_latest.md"
    md_stamp = OUT_DIR / f"staged_interval_policy_{generated}.md"
    json_latest = OUT_DIR / "staged_interval_policy_latest.json"
    json_stamp = OUT_DIR / f"staged_interval_policy_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, base, results)
    write_report(md_stamp, generated, base, results)

    summary = {
        "generated_utc": generated,
        "resolved_intervals": int(len(base)),
        "candidate_count": int(len(results)),
        "target_pass_count": int(results["target_pass"].sum()),
        "less_degenerate_pass_count": int(results["less_degenerate_pass"].sum()),
        "top_target": results[results["target_pass"]].head(10).to_dict("records"),
        "top_overall": results.head(10).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Staged interval policy scan complete")
    print(
        f"resolved_intervals={len(base)} candidates={len(results)} "
        f"target_pass={int(results['target_pass'].sum())} "
        f"less_degenerate_pass={int(results['less_degenerate_pass'].sum())}"
    )
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
