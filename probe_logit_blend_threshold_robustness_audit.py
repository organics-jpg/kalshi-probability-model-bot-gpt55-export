"""Robustness audit for logit-blend threshold candidates.

The threshold frontier can find attractive aggregate rows after seeing
validation/holdout. This audit keeps those rows diagnostic by stress-testing
the exact selector across current and v21 ledgers with splits, chronological
blocks, and market slices.

Research-only: no orders are submitted and no bot files or live processes are
modified.
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
from probe_logit_blend_threshold_frontier import ASK_MAX, CHOOSER, MIN_SECONDS_TO_CLOSE, first_market_rows
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


REPORT_MD = OUT_DIR / "logit_blend_threshold_robustness_audit_latest.md"
REPORT_JSON = OUT_DIR / "logit_blend_threshold_robustness_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "logit_blend_threshold_robustness_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "logit_blend_threshold_robustness_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "logit_blend_threshold_robustness_slices_latest.csv"
HISTORY_CSV = OUT_DIR / "logit_blend_threshold_robustness_history_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.70


@dataclass(frozen=True)
class Candidate:
    name: str
    min_score: float
    edge_floor_cents: float
    min_seconds_to_close: float = MIN_SECONDS_TO_CLOSE

    @property
    def label(self) -> str:
        return (
            f"{CHOOSER}>={self.min_score:.2f}; fair_edge>={self.edge_floor_cents:g}c; "
            f"ask<={ASK_MAX:g}; sec>={self.min_seconds_to_close:g}"
        )


CANDIDATES = [
    Candidate("logit55_edge15_locked", 0.55, -15.0),
    Candidate("logit65_edge10_strict", 0.65, -10.0),
    Candidate("logit55_edge10_control", 0.55, -10.0),
    Candidate("logit60_edge10_control", 0.60, -10.0),
    Candidate("logit60_edge15_control", 0.60, -15.0),
    Candidate("logit55_edge15_sec600", 0.55, -15.0, 600.0),
    Candidate("logit55_edge10_sec600", 0.55, -10.0, 600.0),
    Candidate("logit60_edge15_sec600", 0.60, -15.0, 600.0),
    Candidate("logit65_edge10_sec600", 0.65, -10.0, 600.0),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def selected_for(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, CHOOSER)
    if chosen.empty:
        return enrich_selected(chosen.copy())
    chosen = enrich_selected(chosen)
    scores = pd.to_numeric(chosen[CHOOSER], errors="coerce")
    chosen["fair_edge_cents"] = 100.0 * scores - pd.to_numeric(chosen["entry_cost_cents"], errors="coerce")
    eligible = chosen[
        scores.ge(candidate.min_score)
        & pd.to_numeric(chosen["fair_edge_cents"], errors="coerce").ge(candidate.edge_floor_cents)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(candidate.min_seconds_to_close)
    ].copy()
    return first_market_rows(eligible)


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": candidate.name,
        "label": candidate.label,
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
    out: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        out.append(
            {
                "dataset": dataset,
                "candidate": candidate.name,
                "block_index": int(block_index),
                "block_start_close_dt": pd.to_datetime(block["close_dt"].min(), utc=True, errors="coerce"),
                "block_end_close_dt": pd.to_datetime(block["close_dt"].max(), utc=True, errors="coerce"),
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
    return out


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
    frame["score_bucket"] = [
        bucket(value, [0.60, 0.70, 0.80, 0.90], ["p<=0.60", "p<=0.70", "p<=0.80", "p<=0.90", "p>0.90"])
        for value in pd.to_numeric(frame[CHOOSER], errors="coerce")
    ]
    frame["edge_bucket"] = [
        bucket(value, [-10, -5, 0, 5], ["edge<=-10", "edge<=-5", "edge<=0", "edge<=5", "edge>5"])
        for value in pd.to_numeric(frame["fair_edge_cents"], errors="coerce")
    ]
    out: List[Dict[str, Any]] = []
    for group_type, col in [
        ("split", "split"),
        ("side", "side"),
        ("hour", "entry_hour_utc"),
        ("ask", "ask_bucket"),
        ("time", "time_bucket"),
        ("score", "score_bucket"),
        ("edge", "edge_bucket"),
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


def history_rows() -> List[Dict[str, Any]]:
    labels = {candidate.name: candidate.label for candidate in CANDIDATES}
    rows: List[Dict[str, Any]] = []
    for path in sorted(OUT_DIR.glob("logit_blend_threshold_frontier_*.csv")):
        try:
            frame = pd.read_csv(path)
        except Exception:
            continue
        for name, label in labels.items():
            part = frame[frame["label"].eq(label)]
            if part.empty:
                continue
            row = part.iloc[0]
            rows.append(
                {
                    "file": path.name,
                    "candidate": name,
                    "combined_all_net_pnl_cents": row.get("combined_all_net_pnl_cents"),
                    "current_all_net_pnl_cents": row.get("current_all_net_pnl_cents"),
                    "current_validation_net_pnl_cents": row.get("current_validation_net_pnl_cents"),
                    "current_holdout_net_pnl_cents": row.get("current_holdout_net_pnl_cents"),
                    "v21_all_net_pnl_cents": row.get("v21_all_net_pnl_cents"),
                    "v21_train_net_pnl_cents": row.get("v21_train_net_pnl_cents"),
                    "v21_validation_net_pnl_cents": row.get("v21_validation_net_pnl_cents"),
                    "v21_holdout_net_pnl_cents": row.get("v21_holdout_net_pnl_cents"),
                }
            )
    return rows


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


def write_report(
    generated: str,
    summary: pd.DataFrame,
    blocks: pd.DataFrame,
    slices: pd.DataFrame,
    history: pd.DataFrame,
) -> None:
    block_summ = block_summary(blocks)
    supported_slices = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported_slices.sort_values("net_pnl_cents", ascending=True).head(18) if not supported_slices.empty else supported_slices

    lines = [
        "# Logit Blend Threshold Robustness Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Replays thresholded logit book/RV/hazard selectors on current and v21 ledgers.",
        "- This can reject or prioritize forward collection; promotion still requires strict registered live evidence.",
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {bool(row['coverage_pass'])} | "
            f"{bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )

    lines += [
        "",
        "## Block Summary",
        "",
        "| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in block_summ.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | {int(row['blocks'])} | "
            f"{pct(row['positive_block_rate'])} | {pct(row['positive_coverage_block_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} |"
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

    lines += [
        "",
        "## History",
        "",
        "| file | candidate | combined all | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if history.empty:
        lines.append("| none | none | 0.0c | 0.0c | 0.0c | 0.0c | 0.0c | 0.0c | 0.0c | 0.0c |")
    else:
        for _, row in history[history["candidate"].eq("logit55_edge15_locked")].tail(8).iterrows():
            lines.append(
                f"| `{row['file']}` | `{row['candidate']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
                f"{fmt_cents(row['current_all_net_pnl_cents'])} | {fmt_cents(row['current_validation_net_pnl_cents'])} | "
                f"{fmt_cents(row['current_holdout_net_pnl_cents'])} | {fmt_cents(row['v21_all_net_pnl_cents'])} | "
                f"{fmt_cents(row['v21_train_net_pnl_cents'])} | {fmt_cents(row['v21_validation_net_pnl_cents'])} | "
                f"{fmt_cents(row['v21_holdout_net_pnl_cents'])} |"
            )

    lines += ["", "## Read", ""]
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        block_part = block_summ[block_summ["candidate"].eq(candidate)] if not block_summ.empty else block_summ
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        all_splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        robust = coverage_ok and all_splits_ok and oos_ok and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR
        lines.append(
            f"- `{candidate}` coverage/all-splits/OOS/min positive+coverage block rate/robust: "
            f"{coverage_ok}/{all_splits_ok}/{oos_ok}/{pct(min_block_rate)}/{robust}."
        )
    lines.append("- Robust offline diagnostics still do not replace strict live pre-registration evidence.")
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
            selected = selected_for(side_rows, base, candidate)
            selected.to_csv(OUT_DIR / f"logit_blend_threshold_{candidate.name}_{dataset}_selected_latest.csv", index=False)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_out.extend(block_rows(dataset, candidate, base, selected))
            slice_out.extend(slice_rows(dataset, candidate, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    history = pd.DataFrame(history_rows())

    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    history.to_csv(HISTORY_CSV, index=False)

    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
        "history": clean_json_local(history.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"logit_blend_threshold_robustness_audit_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, summary, blocks, slices, history)
    (OUT_DIR / f"logit_blend_threshold_robustness_audit_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Logit blend threshold robustness audit complete")
    print(f"candidates={len(CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
