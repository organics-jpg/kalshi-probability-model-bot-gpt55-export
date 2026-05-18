"""Temporal side-flip diagnostic for book versus Brownian/score policies.

Research-only: no orders are submitted and no bot files or live processes are
modified.

The recent strict evidence suggests the problem is not only side selection but
timing. This probe asks whether a later Brownian/score decision adds useful
information after an earlier book-margin decision, or whether the later side
flip is often a worse entry.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents
from probe_frontier_candidate_v2_diagnostic import select_policy
from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct


REPORT_MD = OUT_DIR / "temporal_side_flip_diagnostic_latest.md"
REPORT_JSON = OUT_DIR / "temporal_side_flip_diagnostic_latest.json"
REPORT_CSV = OUT_DIR / "temporal_side_flip_diagnostic_latest.csv"

ANCHORS = ["book_margin", "book_margin_early", "book_margin_gap015"]
REFERENCES = ["frontier_v2", "score_min60"]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def selected_for_dataset(side_rows: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    base = market_base(side_rows)
    names = sorted(set(ANCHORS + REFERENCES))
    return {name: select_policy(side_rows, base, name) for name in names}


def paired_rows(dataset: str, anchor_name: str, reference_name: str, anchor: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    cols = ["market", "split", "side", "ask_cents", "win", "net_pnl_cents", "entry_dt", "seconds_to_close"]
    pair = anchor[cols].merge(reference[cols], on=["market", "split"], suffixes=("_anchor", "_reference"))
    if pair.empty:
        return pair
    pair["dataset"] = dataset
    pair["anchor"] = anchor_name
    pair["reference"] = reference_name
    pair["entry_dt_anchor"] = pd.to_datetime(pair["entry_dt_anchor"], utc=True, errors="coerce")
    pair["entry_dt_reference"] = pd.to_datetime(pair["entry_dt_reference"], utc=True, errors="coerce")
    pair["reference_minus_anchor_seconds"] = (
        pair["entry_dt_reference"] - pair["entry_dt_anchor"]
    ).dt.total_seconds()
    pair["side_disagree"] = pair["side_anchor"].astype(str) != pair["side_reference"].astype(str)
    pair["anchor_minus_reference_cents"] = (
        pd.to_numeric(pair["net_pnl_cents_anchor"], errors="coerce")
        - pd.to_numeric(pair["net_pnl_cents_reference"], errors="coerce")
    )
    pair["anchor_win_bool"] = pair["win_anchor"].astype(bool)
    pair["reference_win_bool"] = pair["win_reference"].astype(bool)
    return pair


def bucket_name(part: pd.DataFrame) -> pd.Series:
    dt = pd.to_numeric(part["reference_minus_anchor_seconds"], errors="coerce")
    earlier = dt.gt(1e-6)
    later = dt.lt(-1e-6)
    disagree = part["side_disagree"].astype(bool)
    out = pd.Series("same_time_same_side", index=part.index, dtype="object")
    out[~disagree & earlier] = "anchor_earlier_same_side"
    out[disagree & earlier] = "anchor_earlier_side_flip"
    out[~disagree & later] = "anchor_later_same_side"
    out[disagree & later] = "anchor_later_side_flip"
    out[disagree & ~(earlier | later)] = "same_time_side_flip"
    return out


def summarize_pair(pair: pd.DataFrame) -> List[Dict[str, Any]]:
    if pair.empty:
        return []
    pair = pair.copy()
    pair["bucket"] = bucket_name(pair)
    rows: List[Dict[str, Any]] = []
    buckets = ["all_pairs", "anchor_earlier_same_side", "anchor_earlier_side_flip", "anchor_later_same_side", "anchor_later_side_flip"]
    for bucket in buckets:
        part = pair if bucket == "all_pairs" else pair[pair["bucket"].eq(bucket)]
        n = int(len(part))
        rows.append(
            {
                "dataset": str(pair["dataset"].iloc[0]),
                "anchor": str(pair["anchor"].iloc[0]),
                "reference": str(pair["reference"].iloc[0]),
                "bucket": bucket,
                "pairs": n,
                "anchor_wins": int(part["anchor_win_bool"].sum()) if n else 0,
                "reference_wins": int(part["reference_win_bool"].sum()) if n else 0,
                "anchor_accuracy": float(part["anchor_win_bool"].mean()) if n else None,
                "reference_accuracy": float(part["reference_win_bool"].mean()) if n else None,
                "anchor_net_pnl_cents": float(pd.to_numeric(part["net_pnl_cents_anchor"], errors="coerce").sum()) if n else 0.0,
                "reference_net_pnl_cents": float(pd.to_numeric(part["net_pnl_cents_reference"], errors="coerce").sum()) if n else 0.0,
                "anchor_minus_reference_cents": float(part["anchor_minus_reference_cents"].sum()) if n else 0.0,
                "mean_anchor_minus_reference_cents": float(part["anchor_minus_reference_cents"].mean()) if n else None,
                "median_reference_minus_anchor_seconds": float(pd.to_numeric(part["reference_minus_anchor_seconds"], errors="coerce").median()) if n else None,
            }
        )
    return rows


def run_dataset(dataset: str, side_rows: pd.DataFrame) -> List[Dict[str, Any]]:
    selected = selected_for_dataset(side_rows)
    rows: List[Dict[str, Any]] = []
    for anchor in ANCHORS:
        for reference in REFERENCES:
            pair = paired_rows(dataset, anchor, reference, selected[anchor], selected[reference])
            rows.extend(summarize_pair(pair))
    return rows


def write_report(generated: str, rows: pd.DataFrame) -> None:
    lines = [
        "# Temporal Side-Flip Diagnostic",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Compares first selected book-style rows with first selected Brownian/score rows in the same market.",
        "- Positive `anchor-reference` means the book-style row beat the later/other policy row.",
        "",
        "## Focus Buckets",
        "",
        "| dataset | anchor | reference | bucket | pairs | anchor acc/net | ref acc/net | anchor-ref | median ref-anchor sec |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    focus = rows[rows["bucket"].isin(["all_pairs", "anchor_earlier_side_flip", "anchor_earlier_same_side"])].copy()
    focus = focus.sort_values(["dataset", "anchor", "reference", "bucket"])
    for _, row in focus.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['anchor']}` | `{row['reference']}` | {row['bucket']} | "
            f"{int(row['pairs'])} | {pct(row['anchor_accuracy'])}/{fmt_cents(row['anchor_net_pnl_cents'])} | "
            f"{pct(row['reference_accuracy'])}/{fmt_cents(row['reference_net_pnl_cents'])} | "
            f"{fmt_cents(row['anchor_minus_reference_cents'])} | "
            f"{row['median_reference_minus_anchor_seconds']:.1f} |"
        )
    lines += ["", "## Read", ""]
    current_flips = focus[
        focus["dataset"].eq("current")
        & focus["bucket"].eq("anchor_earlier_side_flip")
        & focus["pairs"].gt(0)
    ].copy()
    if current_flips.empty:
        lines.append("- No current anchor-earlier side-flip bucket was available.")
    else:
        best = current_flips.sort_values("anchor_minus_reference_cents", ascending=False).iloc[0]
        lines.append(
            f"- Strongest current early-book side-flip bucket: `{best['anchor']}` vs `{best['reference']}` "
            f"at {fmt_cents(best['anchor_minus_reference_cents'])} over {int(best['pairs'])} paired markets."
        )
    lines.append("- This is diagnostic timing evidence only; any rule change still needs strict forward registration.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows = run_dataset("current", load_side_rows()) + run_dataset("v21", load_v21_side_rows())
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Temporal side-flip diagnostic complete")
    print(f"rows={len(df)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
