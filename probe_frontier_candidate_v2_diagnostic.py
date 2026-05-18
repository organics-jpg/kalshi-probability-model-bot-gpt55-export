"""Diagnostic comparison of refreshed frontier candidates versus v2.

The refreshed broad frontier moved away from pure Brownian v2 toward book-side
and book/Brownian consensus candidates. This probe compares those candidates
against v2 on the same current and v21 interval ledgers, including paired
side-disagreement deltas.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_market_interval_80coverage import (
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH


LOCKS = {
    "frontier_v2": FRONTIER_V2_LOCK_PATH,
    "book_margin": OUT_DIR / "profit_frontier_book_margin_lock.json",
    "book_margin_early": OUT_DIR / "profit_frontier_book_margin_early_lock.json",
    "book_margin_gap015": OUT_DIR / "profit_frontier_book_margin_gap015_lock.json",
    "score_min60": OUT_DIR / "profit_frontier_score_min60_lock.json",
    "score_min60_gap020": OUT_DIR / "profit_frontier_score_min60_gap020_lock.json",
}

REPORT_MD = OUT_DIR / "frontier_candidate_v2_diagnostic_latest.md"
REPORT_JSON = OUT_DIR / "frontier_candidate_v2_diagnostic_latest.json"
POLICY_CSV = OUT_DIR / "frontier_candidate_v2_diagnostic_policy_latest.csv"
PAIR_CSV = OUT_DIR / "frontier_candidate_v2_diagnostic_pair_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_lock(name: str) -> Dict[str, Any]:
    path = LOCKS[name]
    return json.loads(path.read_text(encoding="utf-8"))


def load_lock_policy(name: str) -> Any:
    lock = load_lock(name)
    return policy_from_record(lock["policy"])


def simple_condition_mask(rows: pd.DataFrame, condition: Dict[str, Any]) -> pd.Series:
    values = pd.to_numeric(rows.get(condition["feature"]), errors="coerce")
    threshold = float(condition["threshold"])
    if condition["op"] == "<=":
        return values.le(threshold).fillna(False)
    if condition["op"] == ">=":
        return values.ge(threshold).fillna(False)
    raise ValueError(f"unknown condition op: {condition['op']}")


def select_policy(side_rows: pd.DataFrame, base: pd.DataFrame, name: str) -> pd.DataFrame:
    lock = load_lock(name)
    policy = load_lock_policy(name)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    selected = enrich_selected(select_markets_from_chosen(chosen, policy))
    veto = lock.get("veto")
    if veto and not selected.empty:
        selected = selected[simple_condition_mask(selected, veto)].copy()
    selected["policy_name"] = name
    selected["policy_label"] = policy.label
    return selected


def flatten_metrics(dataset: str, name: str, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"dataset": dataset, "policy": name}
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    return row


def pair_summary(dataset: str, candidate: str, candidate_rows: pd.DataFrame, v2_rows: pd.DataFrame) -> List[Dict[str, Any]]:
    cols = ["market", "split", "side", "ask_cents", "win", "net_pnl_cents", "entry_dt"]
    pair = candidate_rows[cols].merge(v2_rows[cols], on=["market", "split"], suffixes=("_candidate", "_v2"))
    if pair.empty:
        return []
    pair["side_disagree"] = pair["side_candidate"].astype(str) != pair["side_v2"].astype(str)
    pair["candidate_minus_v2_cents"] = (
        pd.to_numeric(pair["net_pnl_cents_candidate"], errors="coerce")
        - pd.to_numeric(pair["net_pnl_cents_v2"], errors="coerce")
    )
    pair["candidate_win_bool"] = pair["win_candidate"].astype(bool)
    pair["v2_win_bool"] = pair["win_v2"].astype(bool)

    rows: List[Dict[str, Any]] = []
    for split in ["all", "train", "validation", "holdout"]:
        split_part = pair if split == "all" else pair[pair["split"].eq(split)]
        for bucket, part in [
            ("all_pairs", split_part),
            ("same_side", split_part[~split_part["side_disagree"]]),
            ("disagree", split_part[split_part["side_disagree"]]),
        ]:
            n = int(len(part))
            rows.append(
                {
                    "dataset": dataset,
                    "candidate": candidate,
                    "split": split,
                    "bucket": bucket,
                    "paired_markets": n,
                    "candidate_wins": int(part["candidate_win_bool"].sum()) if n else 0,
                    "v2_wins": int(part["v2_win_bool"].sum()) if n else 0,
                    "candidate_accuracy": float(part["candidate_win_bool"].mean()) if n else None,
                    "v2_accuracy": float(part["v2_win_bool"].mean()) if n else None,
                    "candidate_net_pnl_cents": float(pd.to_numeric(part["net_pnl_cents_candidate"], errors="coerce").sum()) if n else 0.0,
                    "v2_net_pnl_cents": float(pd.to_numeric(part["net_pnl_cents_v2"], errors="coerce").sum()) if n else 0.0,
                    "candidate_minus_v2_cents": float(part["candidate_minus_v2_cents"].sum()) if n else 0.0,
                    "mean_candidate_minus_v2_cents": float(part["candidate_minus_v2_cents"].mean()) if n else None,
                }
            )
    return rows


def run_dataset(dataset: str, side_rows: pd.DataFrame) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    base = market_base(side_rows)
    selected = {name: select_policy(side_rows, base, name) for name in LOCKS}
    policy_rows = [
        flatten_metrics(dataset, name, metrics_for(base, frame))
        for name, frame in selected.items()
    ]
    pair_rows: List[Dict[str, Any]] = []
    for candidate in ["book_margin", "book_margin_early", "book_margin_gap015", "score_min60", "score_min60_gap020"]:
        pair_rows.extend(pair_summary(dataset, candidate, selected[candidate], selected["frontier_v2"]))
    return policy_rows, pair_rows


def write_report(generated: str, policy_rows: pd.DataFrame, pair_rows: pd.DataFrame) -> None:
    lines = [
        "# Frontier Candidate vs V2 Diagnostic",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Compares refreshed book/score forward candidates against the older Brownian v2 lock.",
        "- Uses the current two-sided heartbeat ledger and the independent v21 ledger.",
        "",
        "## Policy Metrics",
        "",
        "| dataset | policy | all net/ROI | all acc/cov | holdout net/acc/cov | median ask |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in policy_rows.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['policy']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])}/{pct(row['holdout_accuracy'])}/{pct(row['holdout_coverage'])} | "
            f"{fmt_cents(row['all_median_ask'])} |"
        )

    lines += [
        "",
        "## Paired Deltas Versus V2",
        "",
        "| dataset | candidate | bucket | pairs | candidate acc/net | v2 acc/net | candidate-v2 | mean delta |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    focus = pair_rows[(pair_rows["split"].eq("all")) & (pair_rows["bucket"].isin(["all_pairs", "same_side", "disagree"]))]
    for _, row in focus.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | {row['bucket']} | {int(row['paired_markets'])} | "
            f"{pct(row['candidate_accuracy'])}/{fmt_cents(row['candidate_net_pnl_cents'])} | "
            f"{pct(row['v2_accuracy'])}/{fmt_cents(row['v2_net_pnl_cents'])} | "
            f"{fmt_cents(row['candidate_minus_v2_cents'])} | {fmt_cents(row['mean_candidate_minus_v2_cents'])} |"
        )

    lines += ["", "## Read", ""]
    for candidate in ["book_margin", "book_margin_early", "book_margin_gap015", "score_min60", "score_min60_gap020"]:
        cur = pair_rows[
            pair_rows["dataset"].eq("current")
            & pair_rows["candidate"].eq(candidate)
            & pair_rows["split"].eq("all")
            & pair_rows["bucket"].eq("all_pairs")
        ]
        v21 = pair_rows[
            pair_rows["dataset"].eq("v21")
            & pair_rows["candidate"].eq(candidate)
            & pair_rows["split"].eq("all")
            & pair_rows["bucket"].eq("all_pairs")
        ]
        if cur.empty or v21.empty:
            continue
        cur_delta = float(cur.iloc[0]["candidate_minus_v2_cents"])
        v21_delta = float(v21.iloc[0]["candidate_minus_v2_cents"])
        lines.append(
            f"- `{candidate}` paired delta current/v21: {fmt_cents(cur_delta)}/{fmt_cents(v21_delta)} versus v2."
        )
    lines.append("- A candidate that fixes current v2 failures but gives back too much v21 edge is a forward-test candidate, not a replacement.")
    lines.append("- Promotion still requires strict pre-resolution live sample size and >=80% recurring-market coverage.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_policy, current_pair = run_dataset("current", load_side_rows())
    v21_policy, v21_pair = run_dataset("v21", load_v21_side_rows())
    policy_df = pd.DataFrame(current_policy + v21_policy)
    pair_df = pd.DataFrame(current_pair + v21_pair)
    policy_df.to_csv(POLICY_CSV, index=False)
    pair_df.to_csv(PAIR_CSV, index=False)
    payload = {
        "generated_utc": generated,
        "policy_rows": clean_json_local(policy_df.to_dict(orient="records")),
        "pair_rows": clean_json_local(pair_df.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(generated, policy_df, pair_df)
    print("Frontier candidate vs v2 diagnostic complete")
    print(f"policies={len(policy_df)} pair_rows={len(pair_df)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
