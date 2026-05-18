"""80%-coverage audit for v38 edge-hole candidates.

Research-only. Uses saved retrospective candidate trades and candidate summary
records; no live bot code, process, or order path is touched.

The earlier best row, block_market_first_edge_8_20, has the best P&L but misses
the user's stricter 80% market-coverage requirement on one split. This audit
selects only candidates with min train/validation/holdout coverage >= 80%.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SUMMARY_JSON = OUT_DIR / "v38_edge_hole_veto_candidate_latest.json"
TRADES_CSV = OUT_DIR / "v38_edge_hole_veto_candidate_trades_latest.csv"
REPORT_MD = OUT_DIR / "v38_edge_hole80_candidate_audit_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole80_candidate_audit_latest.json"

COVERAGE_FLOOR = 0.80
REFERENCE = "block_market_first_edge_8_20"


def dollars(value: Any) -> str:
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "NA"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def pct(value: Any) -> str:
    try:
        return f"{100.0 * float(value):.2f}%"
    except (TypeError, ValueError):
        return "NA"


def load_records() -> pd.DataFrame:
    payload = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    records = pd.DataFrame(payload.get("records") or [])
    if records.empty:
        raise SystemExit(f"No records found in {SUMMARY_JSON}")
    for col in [
        "min_split_coverage",
        "min_split_net_after_fees_dollars",
        "min_split_net_after_fees_1c_entry_dollars",
        "all_net_after_fees_dollars",
        "all_net_after_fees_1c_entry_dollars",
        "all_pnl_dollars",
        "all_trades",
    ]:
        records[col] = pd.to_numeric(records.get(col), errors="coerce")
    return records


def load_trades() -> pd.DataFrame:
    rows = pd.read_csv(TRADES_CSV, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["entry_day_utc"] = rows["entry_dt"].dt.strftime("%Y-%m-%d")
    for col in ["pnl_cents", "total_fee_cents", "cost_cents"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce").fillna(0.0)
    rows["fee_net_cents"] = rows["pnl_cents"] - rows["total_fee_cents"]
    rows["fee_net_1c_entry_cents"] = rows["fee_net_cents"] - base.QTY
    return rows


def day_table(trades: pd.DataFrame, candidates: set[str]) -> pd.DataFrame:
    rows = trades[trades["candidate"].isin(candidates)].copy()
    return (
        rows.groupby(["candidate", "entry_day_utc"], as_index=False)
        .agg(
            trades=("market", "count"),
            gross_cents=("pnl_cents", "sum"),
            fee_net_cents=("fee_net_cents", "sum"),
            fee_net_1c_entry_cents=("fee_net_1c_entry_cents", "sum"),
            exits=("settled", lambda s: int((~s.astype(bool)).sum())),
        )
        .sort_values(["candidate", "entry_day_utc"])
    )


def day_stability(table: pd.DataFrame) -> pd.DataFrame:
    if table.empty:
        return table
    return (
        table.groupby("candidate", as_index=False)
        .agg(
            total_days=("entry_day_utc", "nunique"),
            positive_1c_days=("fee_net_1c_entry_cents", lambda s: int((s > 0).sum())),
            worst_1c_day_cents=("fee_net_1c_entry_cents", "min"),
            total_1c_cents=("fee_net_1c_entry_cents", "sum"),
        )
        .sort_values(["positive_1c_days", "worst_1c_day_cents", "total_1c_cents"], ascending=[False, False, False])
    )


def lodo(table: pd.DataFrame, candidates: set[str]) -> list[dict[str, Any]]:
    rows = table[table["candidate"].isin(candidates)].copy()
    days = sorted(rows["entry_day_utc"].dropna().astype(str).unique())
    out: list[dict[str, Any]] = []
    for holdout_day in days:
        train = rows[~rows["entry_day_utc"].eq(holdout_day)].copy()
        hold = rows[rows["entry_day_utc"].eq(holdout_day)].copy()
        train_rank = (
            train.groupby("candidate", as_index=False)
            .agg(
                train_days=("entry_day_utc", "nunique"),
                train_min_day_1c=("fee_net_1c_entry_cents", "min"),
                train_total_1c=("fee_net_1c_entry_cents", "sum"),
                train_positive_days=("fee_net_1c_entry_cents", lambda s: int((s > 0).sum())),
            )
            .sort_values(["train_min_day_1c", "train_total_1c"], ascending=[False, False])
        )
        if train_rank.empty:
            continue
        selected = train_rank.iloc[0]
        selected_hold = hold[hold["candidate"].eq(selected["candidate"])]
        out.append(
            {
                "holdout_day": holdout_day,
                "selected_candidate": str(selected["candidate"]),
                "selected_train_min_day_1c": float(selected["train_min_day_1c"]),
                "selected_train_total_1c": float(selected["train_total_1c"]),
                "selected_holdout_1c": float(selected_hold["fee_net_1c_entry_cents"].sum())
                if not selected_hold.empty
                else 0.0,
            }
        )
    return out


def build() -> dict[str, Any]:
    records = load_records()
    trades = load_trades()
    compliant = records[
        records["candidate"].astype(str).str.startswith("block_market_first")
        & records["min_split_coverage"].ge(COVERAGE_FLOOR)
        & records["all_splits_1c_entry_positive"].astype(bool)
    ].copy()
    compliant = compliant.sort_values(
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
        ascending=[False, False],
    )
    if compliant.empty:
        raise SystemExit("No edge-hole block-first candidate clears the 80% + fee+1c gate.")
    candidates = set(compliant["candidate"].astype(str))
    candidates.add(REFERENCE)
    by_day = day_table(trades, candidates)
    stability = day_stability(by_day)
    lodo_rows = lodo(by_day, set(compliant["candidate"].astype(str)))
    best = compliant.iloc[0].to_dict()
    reference = records[records["candidate"].eq(REFERENCE)].head(1)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "coverage_floor": COVERAGE_FLOOR,
        "best_80_candidate": best,
        "reference_candidate": reference.iloc[0].to_dict() if not reference.empty else None,
        "compliant_candidates": compliant.to_dict("records"),
        "day_stability": stability.to_dict("records"),
        "by_day": by_day.to_dict("records"),
        "lodo": lodo_rows,
    }


def write_report(payload: dict[str, Any]) -> None:
    best = payload["best_80_candidate"]
    reference = payload.get("reference_candidate") or {}
    lodo_rows = payload["lodo"]
    selected_positive = sum(1 for row in lodo_rows if row["selected_holdout_1c"] > 0)
    lines = [
        "# v38 Edge-Hole 80% Candidate Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Scope",
        "",
        "- Research-only audit of saved v38 edge-hole trades.",
        "- Enforces at least 80% coverage in train, validation, and holdout.",
        "- Uses fees plus a 1c entry haircut as the robustness metric.",
        "",
        "## Best 80% Candidate",
        "",
        f"- Candidate: `{best['candidate']}`",
        f"- Min split coverage: {pct(best['min_split_coverage'])}",
        f"- All fee+1c entry P&L: {dollars(best['all_net_after_fees_1c_entry_dollars'])}",
        f"- Min split fee+1c entry P&L: {dollars(best['min_split_net_after_fees_1c_entry_dollars'])}",
        f"- All gross P&L: {dollars(best['all_pnl_dollars'])}",
        f"- Trades: {int(best['all_trades'])}",
        "",
        "## Reference Noncompliant Row",
        "",
        f"- `{REFERENCE}` min split coverage: {pct(reference.get('min_split_coverage'))}",
        f"- `{REFERENCE}` all fee+1c entry P&L: {dollars(reference.get('all_net_after_fees_1c_entry_dollars'))}",
        "",
        "## Compliant Rows",
        "",
        "| candidate | min cov | min 1c | all 1c | all fee | gross | trades |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["compliant_candidates"]:
        lines.append(
            f"| `{row['candidate']}` | {pct(row['min_split_coverage'])} | "
            f"{dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_dollars'])} | {dollars(row['all_pnl_dollars'])} | "
            f"{int(row['all_trades'])} |"
        )
    lines += [
        "",
        "## Day Stability",
        "",
        "| candidate | positive days | worst 1c day | total 1c |",
        "|---|---:|---:|---:|",
    ]
    for row in payload["day_stability"]:
        lines.append(
            f"| `{row['candidate']}` | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{dollars_cents(row['worst_1c_day_cents'])} | {dollars_cents(row['total_1c_cents'])} |"
        )
    lines += [
        "",
        "## LODO Among 80% Candidates",
        "",
        "| holdout day | selected candidate | train min day | train total | holdout 1c |",
        "|---|---|---:|---:|---:|",
    ]
    for row in lodo_rows:
        lines.append(
            f"| `{row['holdout_day']}` | `{row['selected_candidate']}` | "
            f"{dollars_cents(row['selected_train_min_day_1c'])} | "
            f"{dollars_cents(row['selected_train_total_1c'])} | "
            f"{dollars_cents(row['selected_holdout_1c'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best compliant replacement for `{REFERENCE}` is `{best['candidate']}`.",
        f"- LODO-selected 80% candidate is positive on held-out day {selected_positive}/{len(lodo_rows)}.",
        "- This keeps the edge-hole physics family, but shifts the live-shadow candidate to obey the 80% coverage constraint.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    write_report(payload)
    best = payload["best_80_candidate"]
    print("v38 edge-hole 80% candidate audit complete")
    print(f"report={REPORT_MD}")
    print(
        f"best={best['candidate']} min_cov={float(best['min_split_coverage']):.4f} "
        f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
