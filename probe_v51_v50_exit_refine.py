"""v51 exit refinement around the v50 thin-edge certainty FV candidate."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v48_v47_exit_refine as v48
import probe_v50_v47_thin_edge_certainty_fv_strategy as v50
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v51_v50_exit_refine_latest.md"
REPORT_JSON = OUT_DIR / "v51_v50_exit_refine_latest.json"
SUMMARY_CSV = OUT_DIR / "v51_v50_exit_refine_summary_latest.csv"
MODEL = "v50_thinedge_ask90_edge1_stc450_cap75"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)


def build() -> pd.DataFrame:
    rows = v50.v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, _, _ = v50.build_probability_candidates(ops)
    frame = v42.frame_for_candidate(rows, ops, f"{MODEL}_p_yes_candidate")
    best = base.best_side_per_opportunity(frame)
    paths = base.quote_paths(frame)
    universes = base.market_universes(rows)
    entries = v42.choose_entries(best, ENTRY)
    records: list[dict] = []
    for policy in v48.exit_policies():
        trades = base.simulate(entries, paths, policy)
        if trades.empty:
            continue
        fee = v48.fee_1c(trades)
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
        record.update(v48.block_metrics(trades, fee))
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
        "# v51 v50 Exit Refinement",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only exit sweep around `v50_thinedge_ask90_edge1_stc450_cap75`.",
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
    lines.append("- The exit improvement remains smaller than the v50 FV improvement.")
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
    print("v51 v50 exit refinement complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    robust = summary[
        summary["min_split_coverage"].ge(0.80)
        & summary["min_split_net_after_fees_1c_entry_dollars"].gt(0.0)
        & summary["positive_1c_days"].eq(summary["total_days"])
    ].sort_values(
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
        ascending=[False, False],
    )
    if not robust.empty:
        row = robust.iloc[0]
        print(
            f"best={row['exit_policy']} min_1c={float(row['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(row['all_net_after_fees_1c_entry_dollars']):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
