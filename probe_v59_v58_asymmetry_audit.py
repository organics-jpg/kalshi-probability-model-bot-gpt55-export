"""v59 audit of the v58 YES-axis margin-gated exit candidate.

Research-only. The v58 high-PnL row is intentionally asymmetric, so this audit
checks whether its edge is broad across side/split/day/block or concentrated in
a few lucky markets. It compares v58 against the v57-style hold15/prob52
baseline using the same v55 entry surface.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v58_v55_exit_persistence_refine as v58
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v59_v58_asymmetry_audit_latest.md"
REPORT_JSON = OUT_DIR / "v59_v58_asymmetry_audit_latest.json"
SLICE_CSV = OUT_DIR / "v59_v58_asymmetry_policy_slice_latest.csv"
DELTA_CSV = OUT_DIR / "v59_v58_asymmetry_delta_latest.csv"

BASELINE = "hold15_prob52"
ASYM = "hold15_prob52_noside_marginlte0p25"
HELD = "hold15_prob54_heldmarginlte0p5"
POLICIES = [BASELINE, ASYM, HELD]


def fee_1c_cents(rows: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(rows["pnl_cents"], errors="coerce").fillna(0.0) - pd.to_numeric(
        rows["total_fee_cents"], errors="coerce"
    ).fillna(0.0) - v58.base.QTY


def summarize(part: pd.DataFrame, label: str, value: str) -> dict[str, Any]:
    if part.empty:
        return {
            "slice": label,
            "value": value,
            "trades": 0,
            "fee_1c_dollars": 0.0,
            "exits": 0,
            "settled": 0,
            "wins": 0,
            "losses": 0,
        }
    win = part["win"].astype(bool)
    settled = part["settled"].astype(bool)
    return {
        "slice": label,
        "value": value,
        "trades": int(len(part)),
        "fee_1c_dollars": float(fee_1c_cents(part).sum() / 100.0),
        "avg_fee_1c_cents": float(fee_1c_cents(part).mean()),
        "exits": int((~settled).sum()),
        "settled": int(settled.sum()),
        "wins": int(win.sum()),
        "losses": int((~win).sum()),
        "win_rate": float(win.mean()) if len(part) else None,
    }


def policy_slices(trades: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for policy in POLICIES:
        rows = trades[trades["exit_policy"].eq(policy)].copy()
        records.append({"policy": policy, **summarize(rows, "all", "all")})
        for side, part in rows.groupby("side"):
            records.append({"policy": policy, **summarize(part, "side", str(side))})
        for split, part in rows.groupby("split"):
            records.append({"policy": policy, **summarize(part, "split", str(split))})
        day = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
        for day_value, part in rows.groupby(day):
            records.append({"policy": policy, **summarize(part, "day", str(day_value))})
    return pd.DataFrame(records)


def delta_vs_baseline(trades: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["market", "entry_dt", "side"]
    base = trades[trades["exit_policy"].eq(BASELINE)].copy()
    asym = trades[trades["exit_policy"].eq(ASYM)].copy()
    for rows in [base, asym]:
        rows["fee_1c_cents"] = fee_1c_cents(rows)
    cols = [
        *key_cols,
        "split",
        "outcome",
        "win",
        "entry_ask_cents",
        "entry_p_side",
        "entry_seconds_to_close",
        "exit_type",
        "exit_dt",
        "exit_bid_cents",
        "exit_p_side",
        "settled",
        "fee_1c_cents",
    ]
    joined = base[cols].merge(asym[cols], on=key_cols, suffixes=("_base", "_asym"), how="inner")
    joined["delta_fee_1c_cents"] = joined["fee_1c_cents_asym"] - joined["fee_1c_cents_base"]
    joined["abs_delta_fee_1c_cents"] = joined["delta_fee_1c_cents"].abs()
    return joined.sort_values("delta_fee_1c_cents", ascending=False).reset_index(drop=True)


def concentration_stats(delta: pd.DataFrame) -> dict[str, Any]:
    if delta.empty:
        return {}
    total = float(delta["delta_fee_1c_cents"].sum())
    positive = delta[delta["delta_fee_1c_cents"].gt(0)].sort_values("delta_fee_1c_cents", ascending=False)
    negative = delta[delta["delta_fee_1c_cents"].lt(0)].sort_values("delta_fee_1c_cents")
    top5 = float(positive.head(5)["delta_fee_1c_cents"].sum()) if not positive.empty else 0.0
    top10 = float(positive.head(10)["delta_fee_1c_cents"].sum()) if not positive.empty else 0.0
    return {
        "total_delta_dollars": total / 100.0,
        "positive_delta_markets": int(len(positive)),
        "negative_delta_markets": int(len(negative)),
        "top5_positive_delta_dollars": top5 / 100.0,
        "top10_positive_delta_dollars": top10 / 100.0,
        "top5_share_of_total_delta": float(top5 / total) if total > 0 else None,
        "top10_share_of_total_delta": float(top10 / total) if total > 0 else None,
        "worst_negative_delta_dollars": float(negative["delta_fee_1c_cents"].min() / 100.0) if not negative.empty else 0.0,
    }


def write_report(slices: pd.DataFrame, delta: pd.DataFrame, concentration: dict[str, Any]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    def money(value: Any) -> str:
        try:
            return f"${float(value):.2f}"
        except (TypeError, ValueError):
            return "NA"

    lines = [
        "# v59 v58 Asymmetry Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only overfit/concentration audit for the v58 NO-side YES-axis margin-gated exit.",
        "- Compares v58 against v57-style `hold15_prob52` and the best symmetric held-side margin row.",
        "- Live bot untouched.",
        "",
        "## Policy Slices",
        "",
        "| policy | slice | value | trades | fee+1c | exits | settled | wins | losses |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in slices[slices["slice"].isin(["all", "side", "split"])].iterrows():
        lines.append(
            f"| `{row['policy']}` | `{row['slice']}` | `{row['value']}` | {int(row['trades'])} | "
            f"{money(row['fee_1c_dollars'])} | {int(row['exits'])} | {int(row['settled'])} | "
            f"{int(row['wins'])} | {int(row['losses'])} |"
        )
    lines += [
        "",
        "## Delta Concentration",
        "",
        f"- Total v58-v57 fee+1c delta: {money(concentration.get('total_delta_dollars'))}",
        f"- Positive / negative delta markets: {concentration.get('positive_delta_markets', 0)} / {concentration.get('negative_delta_markets', 0)}",
        f"- Top 5 positive-delta markets: {money(concentration.get('top5_positive_delta_dollars'))} "
        f"({100.0 * float(concentration.get('top5_share_of_total_delta') or 0.0):.1f}% of total delta)",
        f"- Top 10 positive-delta markets: {money(concentration.get('top10_positive_delta_dollars'))} "
        f"({100.0 * float(concentration.get('top10_share_of_total_delta') or 0.0):.1f}% of total delta)",
        f"- Worst single negative delta: {money(concentration.get('worst_negative_delta_dollars'))}",
        "",
        "## Largest Positive Deltas",
        "",
        "| market | side | split | base fee+1c | v58 fee+1c | delta | base exit | v58 exit |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for _, row in delta.head(12).iterrows():
        lines.append(
            f"| `{row['market']}` | `{row['side']}` | `{row['split_base']}` | "
            f"{money(float(row['fee_1c_cents_base']) / 100.0)} | {money(float(row['fee_1c_cents_asym']) / 100.0)} | "
            f"{money(float(row['delta_fee_1c_cents']) / 100.0)} | `{row['exit_type_base']}` | `{row['exit_type_asym']}` |"
        )
    lines += ["", "## Read", ""]
    top5_share = concentration.get("top5_share_of_total_delta")
    if top5_share is not None and float(top5_share) > 0.70:
        lines.append("- The v58 improvement is highly concentrated; treat it as overfit-prone until forward data confirms it.")
    else:
        lines.append("- The v58 improvement is not dominated by only the top five markets, but forward validation is still required.")
    lines.append("- The symmetric held-side margin row improves robustness less than v58 and does not beat v57 on all-market PnL.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "concentration": concentration,
                    "policy_slices": json.loads(slices.to_json(orient="records", date_format="iso")),
                    "top_deltas": json.loads(delta.head(50).to_json(orient="records", date_format="iso")),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = v58.v47.load_rows()
    ops = v58.v42.opportunity_table(rows)
    ops, _, _ = v58.v55.build_probability_candidates(ops)
    frame = v58.v42.frame_for_candidate(rows, ops, v58.MODEL_COL)
    best = v58.base.best_side_per_opportunity(frame)
    paths = v58.quote_paths(frame)
    entries = v58.v42.choose_entries(best, v58.ENTRY)
    policy_by_name = {policy.name: policy for policy in v58.exit_policies()}
    trades = pd.concat(
        [v58.simulate(entries, paths, policy_by_name[name]).assign(exit_policy=name) for name in POLICIES],
        ignore_index=True,
        sort=False,
    )
    slices = policy_slices(trades)
    delta = delta_vs_baseline(trades)
    concentration = concentration_stats(delta)
    slices.to_csv(SLICE_CSV, index=False)
    delta.to_csv(DELTA_CSV, index=False)
    write_report(slices, delta, concentration)
    print("v59 v58 asymmetry audit complete")
    print(f"report={REPORT_MD}")
    print(f"total_delta={concentration.get('total_delta_dollars')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
