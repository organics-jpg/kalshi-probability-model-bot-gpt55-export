"""Book-margin time-window stability scan.

The strict forward failures show a plausible physical failure mode: book-side
confidence early in a 15-minute interval can be stale because there is still
substantial first-passage time for BTC to cross the strike. This diagnostic
tests causal time windows for the locked book-margin policy by waiting until
`seconds_to_close` is below a fixed ceiling while preserving high market
coverage.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is only a forward-test candidate because the scan sees
validation/holdout outcomes.
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
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)


REPORT_MD = OUT_DIR / "book_margin_time_window_stability_scan_latest.md"
REPORT_JSON = OUT_DIR / "book_margin_time_window_stability_scan_latest.json"
SUMMARY_CSV = OUT_DIR / "book_margin_time_window_stability_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "book_margin_time_window_stability_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "book_margin_time_window_stability_slices_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.75


@dataclass(frozen=True)
class Candidate:
    name: str
    min_seconds_to_close: float
    max_seconds_to_close: float | None

    @property
    def policy(self) -> Policy:
        return Policy(
            chooser="book_p_side",
            min_score=0.60,
            ask_max=95.0,
            min_seconds_to_close=self.min_seconds_to_close,
            gate="margin_rv15>=0",
        )

    @property
    def label(self) -> str:
        max_text = "none" if self.max_seconds_to_close is None else f"{self.max_seconds_to_close:g}"
        return f"{self.policy.label}; sec_to_close<={max_text}"


CANDIDATES = [
    Candidate("book_margin_locked", 120.0, None),
    Candidate("book_margin_wait480_locked", 480.0, None),
    Candidate("book_margin_max780", 120.0, 780.0),
    Candidate("book_margin_window360_780", 360.0, 780.0),
    Candidate("book_margin_window480_780", 480.0, 780.0),
    Candidate("book_margin_window540_780", 540.0, 780.0),
    Candidate("book_margin_window600_780", 600.0, 780.0),
    Candidate("book_margin_window480_720", 480.0, 720.0),
    Candidate("book_margin_window540_720", 540.0, 720.0),
    Candidate("book_margin_window600_720", 600.0, 720.0),
    Candidate("book_margin_window480_660", 480.0, 660.0),
    Candidate("book_margin_window540_660", 540.0, 660.0),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def select_candidate(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, candidate.policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    mask = gate_mask(chosen, candidate.policy)
    if candidate.max_seconds_to_close is not None:
        mask &= pd.to_numeric(chosen["seconds_to_close"], errors="coerce").le(candidate.max_seconds_to_close)
    eligible = chosen[mask.fillna(False)].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["candidate"] = candidate.name
    selected["candidate_label"] = candidate.label
    return enrich_selected(selected)


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": candidate.name,
        "label": candidate.label,
        "min_seconds_to_close": candidate.min_seconds_to_close,
        "max_seconds_to_close": candidate.max_seconds_to_close,
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


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
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
                "candidate": candidate,
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
                "median_seconds_to_close": float(pd.to_numeric(part.get("seconds_to_close"), errors="coerce").median()) if n else None,
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


def slice_rows(dataset: str, candidate: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
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
        bucket(value, [600, 720, 780, 840], ["sec<=600", "sec<=720", "sec<=780", "sec<=840", "sec>840"])
        for value in pd.to_numeric(frame["seconds_to_close"], errors="coerce")
    ]
    frame["score_bucket"] = [
        bucket(value, [0.60, 0.65, 0.70, 0.80], ["p<=0.60", "p<=0.65", "p<=0.70", "p<=0.80", "p>0.80"])
        for value in pd.to_numeric(frame["book_p_side"], errors="coerce")
    ]
    out: List[Dict[str, Any]] = []
    for group_type, col in [
        ("split", "split"),
        ("side", "side"),
        ("hour", "entry_hour_utc"),
        ("ask", "ask_bucket"),
        ("time", "time_bucket"),
        ("score", "score_bucket"),
    ]:
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            wins = int(part["win"].astype(bool).sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            out.append(
                {
                    "dataset": dataset,
                    "candidate": candidate,
                    "group_type": group_type,
                    "group": str(group),
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n if n else None,
                    "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
                    "median_seconds_to_close": float(pd.to_numeric(part["seconds_to_close"], errors="coerce").median()) if n else None,
                }
            )
    return out


def block_summary(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return blocks
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        both = int((part["positive_net"] & part["coverage_pass"]).sum())
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_coverage_blocks": both,
                "positive_coverage_block_rate": both / len(part) if len(part) else 0.0,
                "worst_block_net_pnl_cents": float(part["net_pnl_cents"].min()) if not part.empty else 0.0,
            }
        )
    return pd.DataFrame(rows)


def combined_table(summary: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    block_summ = block_summary(blocks)
    rows: List[Dict[str, Any]] = []
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        block_part = block_summ[block_summ["candidate"].eq(candidate)] if not block_summ.empty else block_summ
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        combined_net = float(part["all_net_pnl_cents"].astype(float).sum()) if not part.empty else 0.0
        rows.append(
            {
                "candidate": candidate,
                "combined_net_pnl_cents": combined_net,
                "coverage_ok": coverage_ok,
                "all_splits_ok": splits_ok,
                "oos_ok": oos_ok,
                "min_positive_coverage_block_rate": min_block_rate,
                "robust": coverage_ok and splits_ok and oos_ok and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["robust", "min_positive_coverage_block_rate", "combined_net_pnl_cents"],
        ascending=[False, False, False],
    )


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame) -> None:
    combined = combined_table(summary, blocks)
    supported_slices = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported_slices.sort_values("net_pnl_cents", ascending=True).head(18) if not supported_slices.empty else supported_slices

    lines = [
        "# Book-Margin Time-Window Stability Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests causal time windows for the locked book-margin policy.",
        "- Motivation: early entries have more first-passage time for BTC to cross the strike.",
        "- Any passing row is only a forward-test candidate because this scan sees validation/holdout.",
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
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median sec | coverage pass | all splits positive |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {fmt_cents(row['all_median_seconds_to_close'])} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} |"
        )

    lines += [
        "",
        "## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
        "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median sec |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    if worst_slices.empty:
        lines.append("| none | none | none | 0 | 0/0 | 0.0c | 0.0c | NA | NA |")
    else:
        for _, row in worst_slices.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['group_type']}=`{row['group']}` | "
                f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
                f"{fmt_cents(row['median_ask'])} | {fmt_cents(row['median_seconds_to_close'])} |"
            )

    lines += ["", "## Read", ""]
    if combined["robust"].any():
        best = combined[combined["robust"]].iloc[0]
        lines.append(f"- Best robust diagnostic row: `{best['candidate']}`.")
        lines.append("- It is not promotion evidence; it would need fresh strict pre-resolution registration.")
    else:
        lines.append("- No book-margin time-window row clears the combined coverage, split, OOS, and block-stability gate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = loader()
        base = market_base(side_rows)
        for candidate in CANDIDATES:
            selected = select_candidate(side_rows, base, candidate)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_out.extend(block_rows(dataset, candidate.name, base, selected))
            slice_out.extend(slice_rows(dataset, candidate.name, selected))

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
        "combined": clean_json_local(combined_table(summary, blocks).to_dict(orient="records")),
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"book_margin_time_window_stability_scan_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, summary, blocks, slices)
    (OUT_DIR / f"book_margin_time_window_stability_scan_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Book-margin time-window stability scan complete")
    print(f"candidates={len(CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
