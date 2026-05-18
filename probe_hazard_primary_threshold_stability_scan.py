"""Block-stability scan for hazard-primary fallback thresholds.

The current hazard-primary fallback trial has good aggregate EV but weak
chronological block stability. This probe tests one physically motivated knob:
raise the first-passage hazard confidence floor before falling back to a
high-coverage fair-value prior.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is only a forward-test candidate because this scan
sees validation/holdout.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_hazard_fallback_frontier import FallbackSpec, fallback_selected, first_market_rows
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_physics_probability_blend_audit import add_blend_scores
from probe_profit_touch_hazard_frontier import HazardPolicy, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "hazard_primary_threshold_stability_scan_latest.md"
REPORT_JSON = OUT_DIR / "hazard_primary_threshold_stability_scan_latest.json"
SUMMARY_CSV = OUT_DIR / "hazard_primary_threshold_stability_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "hazard_primary_threshold_stability_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "hazard_primary_threshold_stability_slices_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.70


@dataclass(frozen=True)
class Candidate:
    name: str
    hazard_min_score: float
    fallback: FallbackSpec
    min_seconds_to_close: float

    @property
    def hazard_policy(self) -> HazardPolicy:
        return HazardPolicy(
            "hazard_discounted_mean_15",
            self.hazard_min_score,
            0.0,
            80.0,
            self.min_seconds_to_close,
            "touch_loss15<=0.80",
        )

    @property
    def fallback_policy(self) -> FallbackSpec:
        return FallbackSpec(
            self.fallback.name,
            self.fallback.chooser,
            self.fallback.min_score,
            self.fallback.ask_max,
            self.min_seconds_to_close,
            self.fallback.edge_floor_cents,
        )

    @property
    def label(self) -> str:
        return f"hazard>={self.hazard_min_score:g}; sec>={self.min_seconds_to_close:g}_else_{self.fallback_policy.label}"


FALLBACKS = [
    FallbackSpec("logit_thresh55_edge15", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0),
    FallbackSpec("score_min60", "score_min_book_rv15", 0.60, 95.0, 60.0, None),
]
HAZARD_FLOORS = [0.45, 0.50, 0.55, 0.60, 0.65]
MIN_SECONDS = [60.0, 600.0]
CANDIDATES = [
    Candidate(f"hazard{int(floor * 100):02d}_sec{int(min_sec)}_else_{fallback.name}", floor, fallback, min_sec)
    for floor in HAZARD_FLOORS
    for min_sec in MIN_SECONDS
    for fallback in FALLBACKS
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def hazard_selected(base: pd.DataFrame, side_rows: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen.copy()
    selected = chosen[touch_gate_mask(chosen, policy)].copy()
    selected["selector"] = f"hazard_primary_{policy.min_score:g}"
    return first_market_rows(enrich_selected(selected))


def combined_selected(base: pd.DataFrame, side_rows: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    primary = hazard_selected(base, side_rows, candidate.hazard_policy)
    fallback = fallback_selected(base, side_rows, candidate.fallback_policy)
    if primary.empty:
        return fallback
    primary_markets = set(primary["market"].astype(str))
    fallback = fallback[~fallback["market"].astype(str).isin(primary_markets)].copy()
    return (
        pd.concat([primary, fallback], ignore_index=True, sort=False)
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": candidate.name,
        "label": candidate.label,
        "hazard_min_score": candidate.hazard_min_score,
        "fallback": candidate.fallback.name,
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


def block_base(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    return out


def block_rows(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = block_base(base)
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate.name,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": coverage,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "median_ask": float(pd.to_numeric(part.get("ask_cents"), errors="coerce").median()) if n else None,
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
            }
        )
    return rows


def bucket(value: Any, cuts: list[float], labels: list[str]) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    for cut, label in zip(cuts, labels):
        if number <= cut:
            return label
    return labels[-1]


def slice_rows(dataset: str, candidate: Candidate, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    if selected.empty:
        return []
    frame = selected.copy()
    frame["entry_dt"] = pd.to_datetime(frame["entry_dt"], utc=True, errors="coerce")
    frame["entry_hour_utc"] = frame["entry_dt"].dt.hour.astype("Int64").astype(str)
    frame["ask_bucket"] = [
        bucket(value, [60, 70, 80, 95], ["ask<=60", "ask<=70", "ask<=80", "ask<=95", "ask>95"])
        for value in pd.to_numeric(frame["ask_cents"], errors="coerce")
    ]
    frame["time_bucket"] = [
        bucket(value, [300, 600, 900], ["sec<=300", "sec<=600", "sec<=900", "sec>900"])
        for value in pd.to_numeric(frame["seconds_to_close"], errors="coerce")
    ]
    frame["selector"] = frame.get("selector", "unknown").fillna("unknown").astype(str)
    out: List[Dict[str, Any]] = []
    for group_type, col in [
        ("selector", "selector"),
        ("split", "split"),
        ("side", "side"),
        ("hour", "entry_hour_utc"),
        ("ask", "ask_bucket"),
        ("time", "time_bucket"),
    ]:
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            wins = int(part["win"].astype(bool).sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            out.append(
                {
                    "dataset": dataset,
                    "candidate": candidate.name,
                    "group_type": group_type,
                    "group": str(group),
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n if n else None,
                    "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
                }
            )
    return out


def block_summary(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return blocks
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        positive = int(part["positive_net"].sum())
        both = int((part["positive_net"] & part["coverage_pass"]).sum())
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": positive / len(part) if len(part) else None,
                "positive_coverage_block_rate": both / len(part) if len(part) else None,
                "worst_block_net_pnl_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
            }
        )
    return pd.DataFrame(rows)


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame) -> None:
    block_summ = block_summary(blocks)
    supported_slices = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported_slices.sort_values("net_pnl_cents", ascending=True).head(16) if not supported_slices.empty else supported_slices

    combined_rows: List[Dict[str, Any]] = []
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        block_part = block_summ[block_summ["candidate"].eq(candidate)] if not block_summ.empty else block_summ
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        all_splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        combined_net = float(part["all_net_pnl_cents"].astype(float).sum()) if not part.empty else 0.0
        combined_rows.append(
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
    combined = pd.DataFrame(combined_rows).sort_values(
        ["robust", "min_positive_coverage_block_rate", "combined_net_pnl_cents"], ascending=[False, False, False]
    )

    lines = [
        "# Hazard Primary Threshold Stability Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether raising the hazard-primary confidence floor improves block stability while preserving market coverage through a fallback prior.",
        "- Any passing row is still only a forward-test candidate because this scan sees validation/holdout.",
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
        lines.append("- No hazard-primary threshold row clears the combined coverage, split, OOS, and block-stability gate.")
    lines.append("- Do not promote or lock a scanned row without fresh strict live registration.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = add_blend_scores(loader())
        base = market_base(side_rows)
        for candidate in CANDIDATES:
            selected = combined_selected(base, side_rows, candidate)
            selected.to_csv(OUT_DIR / f"hazard_primary_threshold_{candidate.name}_{dataset}_selected_latest.csv", index=False)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_out.extend(block_rows(dataset, candidate, base, selected))
            slice_out.extend(slice_rows(dataset, candidate, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)

    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"hazard_primary_threshold_stability_scan_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, summary, blocks, slices)
    (OUT_DIR / f"hazard_primary_threshold_stability_scan_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Hazard primary threshold stability scan complete")
    print(f"candidates={len(CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
