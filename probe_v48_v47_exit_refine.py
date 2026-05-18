"""v48 exit refinement around the v47 re-cross hazard FV candidate.

Research-only. Tests whether the v47 probability surface wants a different
exit trigger than the inherited v45 prob54 rule while preserving 80% coverage.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v48_v47_exit_refine_latest.md"
REPORT_JSON = OUT_DIR / "v48_v47_exit_refine_latest.json"
SUMMARY_CSV = OUT_DIR / "v48_v47_exit_refine_summary_latest.csv"
MODEL = "v47_recross_sigma1_v3cap68"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)


def exit_policies() -> list[base.ExitPolicy]:
    policies: list[base.ExitPolicy] = []
    for prob in [None, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.62]:
        policies.append(base.ExitPolicy("hold" if prob is None else f"prob{int(prob * 100)}", probability_floor=prob))
    for take in [3, 5, 8, 10, 12, 15, 20]:
        policies.append(base.ExitPolicy(f"take{take}", take_profit_cents=float(take)))
        for prob in [0.52, 0.54, 0.56, 0.58, 0.60]:
            policies.append(
                base.ExitPolicy(f"take{take}_or_prob{int(prob * 100)}", take_profit_cents=float(take), probability_floor=prob)
            )
    for fair in [-2, 0, 1, 2, 3, 5]:
        policies.append(base.ExitPolicy(f"fair{fair}", fair_edge_ceiling_cents=float(fair)))
        for prob in [0.52, 0.54, 0.56]:
            policies.append(
                base.ExitPolicy(f"fair{fair}_or_prob{int(prob * 100)}", fair_edge_ceiling_cents=float(fair), probability_floor=prob)
            )
    for stop in [25, 30, 35, 40, 45, 50, 55, 60]:
        policies.append(base.ExitPolicy(f"stop{stop}", stop_bid_cents=float(stop)))
        for prob in [0.52, 0.54, 0.56]:
            policies.append(base.ExitPolicy(f"stop{stop}_or_prob{int(prob * 100)}", stop_bid_cents=float(stop), probability_floor=prob))
    for hold_seconds in [15, 30, 45, 60, 90, 120]:
        for prob in [0.52, 0.54, 0.56, 0.58]:
            policies.append(
                base.ExitPolicy(
                    f"hold{hold_seconds}_prob{int(prob * 100)}",
                    probability_floor=prob,
                    min_hold_seconds=float(hold_seconds),
                )
            )
    return policies


def fee_1c(trades: pd.DataFrame) -> pd.Series:
    return trades["pnl_cents"] - trades["total_fee_cents"] - base.QTY


def block_metrics(trades: pd.DataFrame, fee: pd.Series) -> dict[str, Any]:
    ordered = trades.assign(fee_1c_cents=fee).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    values = [
        float(ordered.iloc[idx]["fee_1c_cents"].sum() / 100.0)
        for idx in np.array_split(np.arange(len(ordered)), 10)
        if len(idx)
    ]
    return {
        "block10_positive": int(sum(value > 0 for value in values)),
        "block10_worst_dollars": float(min(values)) if values else None,
    }


def build() -> pd.DataFrame:
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, _, _ = v47.build_probability_candidates(ops)
    frame = v42.frame_for_candidate(rows, ops, f"{MODEL}_p_yes_candidate")
    best = base.best_side_per_opportunity(frame)
    paths = base.quote_paths(frame)
    universes = base.market_universes(rows)
    entries = v42.choose_entries(best, ENTRY)
    records: list[dict[str, Any]] = []
    for policy in exit_policies():
        trades = base.simulate(entries, paths, policy)
        if trades.empty:
            continue
        fee = fee_1c(trades)
        split_values: dict[str, float] = {}
        coverages: dict[str, float] = {}
        for split, universe in universes.items():
            mask = trades["market"].astype(str).isin(universe)
            split_values[split] = float(fee[mask].sum() / 100.0)
            coverages[split] = float(mask.sum() / len(universe)) if universe else 0.0
        day_values = fee.groupby(pd.to_datetime(trades["entry_dt"], utc=True).dt.strftime("%Y-%m-%d")).sum() / 100.0
        record = {
            "model": MODEL,
            "entry_policy": ENTRY.name,
            "exit_policy": policy.name,
            "trades": int(len(trades)),
            "min_split_coverage": float(min(coverages.values())),
            "all_net_after_fees_1c_entry_dollars": float(fee.sum() / 100.0),
            "min_split_net_after_fees_1c_entry_dollars": float(min(split_values.values())),
            "train_net_after_fees_1c_entry_dollars": split_values.get("train"),
            "validation_net_after_fees_1c_entry_dollars": split_values.get("validation"),
            "holdout_net_after_fees_1c_entry_dollars": split_values.get("holdout"),
            "positive_1c_days": int((day_values > 0).sum()),
            "total_days": int(len(day_values)),
            "worst_1c_day_dollars": float(day_values.min()) if len(day_values) else None,
            "settled_count": int(trades["settled"].sum()),
            "exit_count": int((~trades["settled"]).sum()),
            "losses": int((~trades["win"]).sum()),
        }
        record.update(block_metrics(trades, fee))
        records.append(record)
    return pd.DataFrame(records)


def write_report(summary: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(0.80)].copy() if not summary.empty else summary
    robust = eligible[
        eligible["min_split_net_after_fees_1c_entry_dollars"].gt(0.0)
        & eligible["positive_1c_days"].eq(eligible["total_days"])
    ].copy() if not eligible.empty else eligible
    selected = robust.sort_values(
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
        ascending=[False, False],
    ) if not robust.empty else eligible.sort_values(
        ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars"],
        ascending=[False, False],
    )
    lines = [
        "# v48 v47 Exit Refinement",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only exit sweep around `v47_recross_sigma1_v3cap68`.",
        "- Entry is fixed at `edge0_ask100_p0.65_stc0-600`; only exit behavior changes.",
        "- Live bot untouched.",
        "",
        "## Search Result",
        "",
        f"- Exit policies evaluated: {len(summary)}",
        f"- 80%+ coverage policies: {len(eligible)}",
        f"- Split-positive and all-day-positive policies: {len(robust)}",
        "",
        "## Selected Rows",
        "",
        "| exit | min cov | min 1c | all 1c | train | validation | holdout | days | block10 | settled | exits |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(25).iterrows():
        lines.append(
            f"| `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['train_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['validation_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['holdout_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['settled_count'])} | {int(row['exit_count'])} |"
        )
    lines += ["", "## Read", ""]
    if not selected.empty:
        best = selected.iloc[0]
        lines.append(
            f"- Best robust exit is `{best['exit_policy']}` with min split fee+1c "
            f"{v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} and all-market fee+1c "
            f"{v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- The exit improvement is small; the main gain remains the v47 probability transform.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "summary_rows": int(len(summary)),
                    "eligible_80_rows": int(len(eligible)),
                    "robust_rows": int(len(robust)),
                    "selected": selected.head(25).to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary = build()
    summary.to_csv(SUMMARY_CSV, index=False)
    write_report(summary)
    print("v48 v47 exit refinement complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not summary.empty:
        best = summary[
            summary["min_split_coverage"].ge(0.80)
            & summary["min_split_net_after_fees_1c_entry_dollars"].gt(0.0)
            & summary["positive_1c_days"].eq(summary["total_days"])
        ].sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        )
        if not best.empty:
            row = best.iloc[0]
            print(
                f"best={row['exit_policy']} min_1c={float(row['min_split_net_after_fees_1c_entry_dollars']):.2f} "
                f"all_1c={float(row['all_net_after_fees_1c_entry_dollars']):.2f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
