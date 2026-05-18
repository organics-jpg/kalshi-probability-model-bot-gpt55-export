"""Failure-physics audit for the book_p80 forward-lock candidate.

The cross-dataset frontier surfaced a high-confidence book policy that keeps
>=80% recurring BTC 15m markets, but its edge is thin because it buys expensive
contracts. This probe explains the selected wins/losses physically instead of
searching a new overlay.

Research-only: no orders are submitted and no live bot files or processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi
from probe_market_interval_80coverage import (
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


REPORT_MD = OUT_DIR / "book_p80_failure_physics_audit_latest.md"
REPORT_JSON = OUT_DIR / "book_p80_failure_physics_audit_latest.json"
DETAIL_CSV = OUT_DIR / "book_p80_failure_physics_selected_latest.csv"
CONDITION_CSV = OUT_DIR / "book_p80_failure_physics_conditions_latest.csv"
BLOCK_CSV = OUT_DIR / "book_p80_failure_physics_blocks_latest.csv"

BOOK_P80 = Policy("book_p_side", 0.80, 95.0, 120.0, "none")
BLOCK_SIZE = 20

FEATURES = [
    "ask_cents",
    "seconds_to_close",
    "book_p_side",
    "book_margin_cents",
    "spread_cents",
    "margin_dollars",
    "margin_per_rv_sigma_15m",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "score_min_book_rv15",
    "score_mean_book_rv15",
    "signed_move_3m",
    "signed_move_5m",
    "signed_move_15m",
    "signed_move_30m",
    "adverse_move_15m",
    "adverse_move_30m",
    "rv_sigma_t_15m",
    "rv_sigma_t_30m",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_series(values: pd.Series) -> pd.Series:
    if values.dtype == bool:
        return values
    text = values.astype(str).str.strip().str.lower()
    return text.isin(["true", "1", "yes"])


def selected_for_dataset(name: str, side_rows: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    base = market_base(side_rows)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BOOK_P80.chooser)
    selected = enrich_selected(select_markets_from_chosen(chosen, BOOK_P80))
    selected["dataset"] = name
    selected["win"] = bool_series(selected["win"]) if "win" in selected.columns else False
    selected["entry_dt"] = pd.to_datetime(selected["entry_dt"], utc=True, errors="coerce")
    selected["close_dt"] = pd.to_datetime(selected["close_dt"], utc=True, errors="coerce")
    return base.assign(dataset=name), selected


def summarize_selection(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    n = int(len(selected))
    wins = int(selected["win"].sum()) if n else 0
    total = int(len(base))
    acc = wins / n if n else None
    be = float(selected["fee_aware_break_even_p"].mean()) if n else None
    net = float(selected["net_pnl_cents"].sum()) if n else 0.0
    cost = float(selected["entry_cost_cents"].sum()) if n else 0.0
    return {
        "base_markets": total,
        "selected_markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": acc,
        "coverage": n / total if total else None,
        "fee_aware_break_even_accuracy": be,
        "accuracy_minus_break_even": (acc - be) if acc is not None and be is not None else None,
        "net_pnl_cents": net,
        "net_roi_on_cost": net / cost if cost else None,
        "median_ask": float(selected["ask_cents"].median()) if n else None,
        "mean_ask": float(selected["ask_cents"].mean()) if n else None,
        "p75_ask": float(selected["ask_cents"].quantile(0.75)) if n else None,
        "median_seconds_to_close": float(selected["seconds_to_close"].median()) if n else None,
    }


def feature_separations(selected: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    wins = selected[selected["win"]]
    losses = selected[~selected["win"]]
    for feature in FEATURES:
        if feature not in selected.columns:
            continue
        win_values = pd.to_numeric(wins[feature], errors="coerce")
        loss_values = pd.to_numeric(losses[feature], errors="coerce")
        if win_values.notna().sum() < 5 or loss_values.notna().sum() < 5:
            continue
        win_median = float(win_values.median())
        loss_median = float(loss_values.median())
        rows.append(
            {
                "feature": feature,
                "win_median": win_median,
                "loss_median": loss_median,
                "loss_minus_win": loss_median - win_median,
            }
        )
    return sorted(rows, key=lambda row: abs(float(row["loss_minus_win"])), reverse=True)


def rule_masks(selected: pd.DataFrame) -> Dict[str, pd.Series]:
    def num(col: str) -> pd.Series:
        return pd.to_numeric(selected.get(col, pd.Series(index=selected.index, dtype=float)), errors="coerce")

    return {
        "ask>=85": num("ask_cents").ge(85.0),
        "ask>=90": num("ask_cents").ge(90.0),
        "seconds_to_close>=600": num("seconds_to_close").ge(600.0),
        "margin_dollars<=25": num("margin_dollars").le(25.0),
        "margin_rv15<=0.50": num("margin_per_rv_sigma_15m").le(0.50),
        "brownian15<0.55": num("brownian_p_rv_15m").lt(0.55),
        "score_min<0.65": num("score_min_book_rv15").lt(0.65),
        "signed_move_15m<=-100": num("signed_move_15m").le(-100.0),
        "signed_move_30m<=-250": num("signed_move_30m").le(-250.0),
        "adverse15>=100": num("adverse_move_15m").ge(100.0),
        "adverse30>=250": num("adverse_move_30m").ge(250.0),
    }


def condition_rows(dataset: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    total_n = int(len(selected))
    total_net = float(selected["net_pnl_cents"].sum()) if total_n else 0.0
    for rule, mask in rule_masks(selected).items():
        mask = mask.fillna(False)
        for label, part in [("inside", selected[mask]), ("outside", selected[~mask])]:
            n = int(len(part))
            wins = int(part["win"].sum()) if n else 0
            cost = float(part["entry_cost_cents"].sum()) if n else 0.0
            net = float(part["net_pnl_cents"].sum()) if n else 0.0
            out.append(
                {
                    "dataset": dataset,
                    "rule": rule,
                    "side": label,
                    "markets": n,
                    "retention": n / total_n if total_n else None,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_roi_on_cost": net / cost if cost else None,
                    "delta_vs_total_net_cents": net - total_net,
                }
            )
    return out


def block_rows(dataset: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    ordered = selected.sort_values(["close_dt", "entry_dt", "market"]).reset_index(drop=True)
    if ordered.empty:
        return rows
    for block_idx, start in enumerate(range(0, len(ordered), BLOCK_SIZE), start=1):
        part = ordered.iloc[start : start + BLOCK_SIZE]
        n = int(len(part))
        wins = int(part["win"].sum())
        rows.append(
            {
                "dataset": dataset,
                "block": block_idx,
                "markets": n,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": float(part["net_pnl_cents"].sum()) if n else 0.0,
                "first_close_dt": part["close_dt"].min().isoformat() if n else None,
                "last_close_dt": part["close_dt"].max().isoformat() if n else None,
            }
        )
    return rows


def worst_losses(selected: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    cols = [
        "dataset",
        "market",
        "close_dt",
        "side",
        "ask_cents",
        "net_pnl_cents",
        "book_p_side",
        "brownian_p_rv_15m",
        "score_min_book_rv15",
        "margin_dollars",
        "margin_per_rv_sigma_15m",
        "signed_move_15m",
        "signed_move_30m",
        "seconds_to_close",
    ]
    available = [col for col in cols if col in selected.columns]
    losses = selected[~selected["win"]].copy()
    if losses.empty:
        return losses.reindex(columns=available)
    return losses.sort_values(["net_pnl_cents", "ask_cents"], ascending=[True, False]).head(n).reindex(columns=available)


def write_report(
    generated: str,
    summaries: Dict[str, Dict[str, Any]],
    separations: Dict[str, List[Dict[str, Any]]],
    conditions: pd.DataFrame,
    blocks: pd.DataFrame,
    worst: pd.DataFrame,
) -> None:
    lines = [
        "# Book P80 Failure Physics Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Explains the `book_p80_profit_frontier` forward-lock hypothesis rather than promoting it.",
        "- Policy: `book_p_side>=0.80; ask<=95; sec_to_close>=120`.",
        "",
        "## Summary",
        "",
        "| dataset | selected/base | wins/losses | acc | break-even | acc-BE | coverage | net P&L | ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset, row in summaries.items():
        lines.append(
            f"| {dataset} | {row['selected_markets']}/{row['base_markets']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['accuracy'])} | "
            f"{pct(row['fee_aware_break_even_accuracy'])} | {pct(row['accuracy_minus_break_even'])} | "
            f"{pct(row['coverage'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} |"
        )

    lines += ["", "## Largest Win/Loss Separations", ""]
    for dataset, rows in separations.items():
        lines += [
            f"### {dataset}",
            "",
            "| feature | win median | loss median | loss-win |",
            "|---|---:|---:|---:|",
        ]
        for row in rows[:10]:
            lines.append(
                f"| `{row['feature']}` | {row['win_median']:.3f} | "
                f"{row['loss_median']:.3f} | {row['loss_minus_win']:.3f} |"
            )
        lines.append("")

    condition_view = conditions[
        (conditions["side"] == "inside")
        & conditions["markets"].ge(10)
    ].sort_values(["dataset", "net_pnl_cents"])
    lines += [
        "## Weak-State Conditions",
        "",
        "| dataset | condition | markets | retention | wins/losses | acc | net P&L | ROI |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in condition_view.head(18).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['rule']}` | {int(row['markets'])} | {pct(row['retention'])} | "
            f"{int(row['wins'])}/{int(row['losses'])} | {pct(row['accuracy'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} | {fmt_roi(row['net_roi_on_cost'])} |"
        )

    block_summary = blocks.groupby("dataset").agg(
        blocks=("block", "count"),
        positive_blocks=("net_pnl_cents", lambda values: int((values > 0).sum())),
        worst_block=("net_pnl_cents", "min"),
        median_block=("net_pnl_cents", "median"),
    ).reset_index()
    lines += [
        "",
        "## Block Stability",
        "",
        "| dataset | blocks | positive blocks | positive rate | worst block | median block |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in block_summary.iterrows():
        positive_rate = float(row["positive_blocks"]) / float(row["blocks"]) if row["blocks"] else None
        lines.append(
            f"| {row['dataset']} | {int(row['blocks'])} | {int(row['positive_blocks'])} | "
            f"{pct(positive_rate)} | {fmt_cents(row['worst_block'])} | {fmt_cents(row['median_block'])} |"
        )

    lines += [
        "",
        "## Worst Losses",
        "",
        "| dataset | market | side | ask | net | book p | brownian15 | score min | margin | signed15 | signed30 | sec |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst.iterrows():
        lines.append(
            f"| {row.get('dataset')} | `{row.get('market')}` | {row.get('side')} | "
            f"{fmt_cents(row.get('ask_cents'))} | {fmt_cents(row.get('net_pnl_cents'))} | "
            f"{float(row.get('book_p_side')):.3f} | {float(row.get('brownian_p_rv_15m')):.3f} | "
            f"{float(row.get('score_min_book_rv15')):.3f} | {float(row.get('margin_dollars')):.2f} | "
            f"{float(row.get('signed_move_15m')):.2f} | {float(row.get('signed_move_30m')):.2f} | "
            f"{float(row.get('seconds_to_close')):.1f} |"
        )

    lines += [
        "",
        "## Read",
        "",
        "- The `book_p80` edge is real historically but thin: current accuracy only clears fee-aware break-even by about half a percentage point.",
        "- The model buys high-priced contracts, so individual losses are large and cannot be repaired with a small number of extra wins.",
        "- Any blocker discovered here is diagnostic only. The forward lock must accumulate pre-resolution rows after its effective boundary before it can count.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_selected = selected_for_dataset("current", load_side_rows())
    v21_base, v21_selected = selected_for_dataset("v21", load_v21_side_rows())
    selected = pd.concat([current_selected, v21_selected], ignore_index=True, sort=False)
    base_by = {"current": current_base, "v21": v21_base}
    selected_by = {"current": current_selected, "v21": v21_selected}

    summaries = {name: summarize_selection(base_by[name], selected_by[name]) for name in selected_by}
    separations = {name: feature_separations(selected_by[name]) for name in selected_by}
    condition_df = pd.DataFrame([row for name, frame in selected_by.items() for row in condition_rows(name, frame)])
    block_df = pd.DataFrame([row for name, frame in selected_by.items() for row in block_rows(name, frame)])
    worst_df = worst_losses(selected)

    DETAIL_CSV.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(DETAIL_CSV, index=False)
    condition_df.to_csv(CONDITION_CSV, index=False)
    block_df.to_csv(BLOCK_CSV, index=False)
    write_report(generated, summaries, separations, condition_df, block_df, worst_df)
    payload = {
        "generated_utc": generated,
        "policy": BOOK_P80.label,
        "summaries": summaries,
        "top_separations": {name: rows[:10] for name, rows in separations.items()},
        "reports": {
            "md": str(REPORT_MD),
            "selected_csv": str(DETAIL_CSV),
            "condition_csv": str(CONDITION_CSV),
            "block_csv": str(BLOCK_CSV),
        },
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"book_p80_failure_physics_audit_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (OUT_DIR / f"book_p80_failure_physics_audit_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Book p80 failure physics audit complete")
    print(f"current={summaries['current']['wins']}/{summaries['current']['losses']} {fmt_cents(summaries['current']['net_pnl_cents'])}")
    print(f"v21={summaries['v21']['wins']}/{summaries['v21']['losses']} {fmt_cents(summaries['v21']['net_pnl_cents'])}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
