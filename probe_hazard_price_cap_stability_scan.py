"""Causal stability scan for hazard/fallback price caps.

Recent strict failures were expensive entries. This probe tests whether a
simple fee-aware cost prior, implemented as stricter ask caps on the hazard
primary and fallback selector, improves robustness while preserving 75-80%+
recurring-market coverage. Arbitration remains timestamp-causal.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows can only become fresh forward-test locks.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

import probe_hazard_primary_threshold_stability_scan as threshold_scan
from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_hazard_fallback_causal_frontier import first_causal_rows
from probe_hazard_fallback_frontier import FallbackSpec, fallback_selected
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, choose_decision_sides, clean_json, load_side_rows, market_base, pct
from probe_physics_probability_blend_audit import add_blend_scores
from probe_profit_touch_hazard_frontier import HazardPolicy, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "hazard_price_cap_stability_scan_latest.md"
REPORT_JSON = OUT_DIR / "hazard_price_cap_stability_scan_latest.json"
SUMMARY_CSV = OUT_DIR / "hazard_price_cap_stability_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "hazard_price_cap_stability_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "hazard_price_cap_stability_slices_latest.csv"

POSITIVE_BLOCK_RATE_FLOOR = 0.70
MIN_SLICE_MARKETS = 12


@dataclass(frozen=True)
class Candidate:
    name: str
    hazard_ask_max: float
    fallback: FallbackSpec

    @property
    def hazard_policy(self) -> HazardPolicy:
        return HazardPolicy(
            "hazard_discounted_mean_15",
            0.45,
            0.0,
            self.hazard_ask_max,
            60.0,
            "touch_loss15<=0.80",
        )

    @property
    def label(self) -> str:
        return f"hazard_ask<={self.hazard_ask_max:g}_else_{self.fallback.name}_ask<={self.fallback.ask_max:g}"


def make_fallbacks() -> List[FallbackSpec]:
    specs: List[FallbackSpec] = []
    for ask_max in [70.0, 75.0, 80.0, 95.0]:
        specs.append(FallbackSpec(f"score60_ask{int(ask_max)}", "score_min_book_rv15", 0.60, ask_max, 60.0, None))
        specs.append(
            FallbackSpec(
                f"logit55_edge15_ask{int(ask_max)}",
                "blend_logit_book_rv_hazard_mean",
                0.55,
                ask_max,
                60.0,
                -15.0,
            )
        )
    return specs


CANDIDATES = [
    Candidate(f"hazard_ask{int(hazard_ask)}_else_{fallback.name}", hazard_ask, fallback)
    for hazard_ask in [65.0, 70.0, 75.0, 80.0]
    for fallback in make_fallbacks()
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def hazard_selected(base: pd.DataFrame, side_rows: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, candidate.hazard_policy.chooser)
    if chosen.empty:
        return chosen.copy()
    selected = chosen[touch_gate_mask(chosen, candidate.hazard_policy)].copy()
    selected["selector"] = f"hazard_primary_ask{int(candidate.hazard_ask_max)}"
    if selected.empty:
        return selected
    return (
        enrich_selected(selected)
        .sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def combined_selected(base: pd.DataFrame, side_rows: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    primary = hazard_selected(base, side_rows, candidate)
    fallback = fallback_selected(base, side_rows, candidate.fallback)
    return first_causal_rows(primary, fallback)


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": candidate.name,
        "label": candidate.label,
        "hazard_ask_max": candidate.hazard_ask_max,
        "fallback": candidate.fallback.name,
        "fallback_ask_max": candidate.fallback.ask_max,
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )
    row["all_splits_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["oos_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["validation", "holdout"]
    )
    return row


def combined_table(summary: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    block_summ = threshold_scan.block_summary(blocks)
    rows: List[Dict[str, Any]] = []
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        block_part = block_summ[block_summ["candidate"].eq(candidate)] if not block_summ.empty else block_summ
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        all_splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        combined_net = float(part["all_net_pnl_cents"].astype(float).sum()) if not part.empty else 0.0
        rows.append(
            {
                "candidate": candidate,
                "combined_net_pnl_cents": combined_net,
                "coverage_ok": coverage_ok,
                "all_splits_ok": all_splits_ok,
                "oos_ok": oos_ok,
                "min_positive_coverage_block_rate": min_block_rate,
                "robust": coverage_ok and all_splits_ok and oos_ok and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["robust", "min_positive_coverage_block_rate", "combined_net_pnl_cents"],
        ascending=[False, False, False],
    )


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame) -> None:
    combined = combined_table(summary, blocks)
    supported = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported.sort_values("net_pnl_cents", ascending=True).head(18) if not supported.empty else supported
    lines = [
        "# Hazard Price-Cap Stability Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests stricter hazard and fallback ask caps under timestamp-causal arbitration.",
        "- Any passing row must still be forward-locked before use.",
        "",
        "## Combined Read",
        "",
        "| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |",
        "|---|---:|---|---|---|---:|---|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {fmt_cents(row['combined_net_pnl_cents'])} | "
            f"{bool(row['coverage_ok'])} | {bool(row['all_splits_ok'])} | {bool(row['oos_ok'])} | "
            f"{pct(row['min_positive_coverage_block_rate'])} | {bool(row['robust'])} |"
        )

    lines += [
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {bool(row['coverage_pass'])} | "
            f"{bool(row['all_splits_positive'])} |"
        )

    lines += [
        "",
        "## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
        "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    if worst_slices.empty:
        lines.append("| none | none | none | 0 | 0/0 | 0.0c | 0.0c | NA |")
    else:
        for _, row in worst_slices.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['group_type']}=`{row['group']}` | "
                f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
                f"{fmt_cents(row['median_ask'])} |"
            )
    lines += ["", "## Read", ""]
    if combined["robust"].any():
        best = combined[combined["robust"]].iloc[0]
        lines.append(f"- Best robust diagnostic row: `{best['candidate']}`.")
    else:
        lines.append("- No hazard/fallback price-cap row clears coverage, split, OOS, and block-stability gates.")
    lines.append("- Do not promote or lock a scanned row without fresh strict live registration.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary_rows: List[Dict[str, Any]] = []
    block_rows: List[Dict[str, Any]] = []
    slice_rows: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = add_blend_scores(loader())
        base = market_base(side_rows)
        for candidate in CANDIDATES:
            selected = combined_selected(base, side_rows, candidate)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_rows.extend(threshold_scan.block_rows(dataset, candidate, base, selected))
            slice_rows.extend(threshold_scan.slice_rows(dataset, candidate, selected))
    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_rows)
    slices = pd.DataFrame(slice_rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    combined = combined_table(summary, blocks)
    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "combined": clean_json_local(combined.to_dict(orient="records")),
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"hazard_price_cap_stability_scan_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, summary, blocks, slices)
    (OUT_DIR / f"hazard_price_cap_stability_scan_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Hazard price-cap stability scan complete")
    print(f"candidates={len(CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
