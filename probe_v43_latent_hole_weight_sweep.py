"""v43 latent-hole posterior-weight sweep.

Research-only. Extends v42 by sweeping the posterior weight placed on the
two-sided book measurement after a raw-v38 edge-hole hidden-state trigger.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import logit, sigmoid


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v43_latent_hole_weight_sweep_latest.md"
REPORT_JSON = OUT_DIR / "v43_latent_hole_weight_sweep_latest.json"
SUMMARY_CSV = OUT_DIR / "v43_latent_hole_weight_sweep_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v43_latent_hole_weight_sweep_predictions_latest.csv"

WEIGHTS = [0.35, 0.50, 0.65, 0.80, 0.90, 1.00]


def latent_book_blend(ops: pd.DataFrame, weight: float) -> pd.Series:
    out = ops["v38_p_yes"].copy()
    holes = v42.first_hole_markets(
        ops,
        edge_floor=-2.0,
        p_floor=0.65,
        min_stc=60.0,
        max_stc=600.0,
        low=8.0,
        high=20.0,
    )
    for market, first_dt in holes.items():
        mask = ops["market"].astype(str).eq(market) & ops["entry_dt"].ge(first_dt)
        raw_l = logit(out.loc[mask])
        book_l = logit(ops.loc[mask, "book_mid_p_yes"])
        out.loc[mask] = sigmoid((1.0 - weight) * raw_l + weight * book_l)
    return out.clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def build_weight_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out = ops.copy()
    out["v38_raw_p_yes_candidate"] = out["v38_p_yes"]
    for weight in WEIGHTS:
        label = int(round(weight * 100))
        out[f"v43_latent_hole_bookblend{label}_p_yes_candidate"] = latent_book_blend(out, weight)
    return out, [c for c in out.columns if c.endswith("_p_yes_candidate")], {"weights": WEIGHTS}


def selected_by_family(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    eligible["family"] = eligible["model"].str.replace(r"_p_yes_candidate$", "", regex=True)
    return (
        eligible.sort_values(
            [
                "all_splits_1c_entry_positive",
                "positive_1c_days",
                "min_split_net_after_fees_1c_entry_dollars",
                "block10_positive",
                "all_net_after_fees_1c_entry_dollars",
            ],
            ascending=[False, False, False, False, False],
        )
        .groupby("model", as_index=False)
        .head(1)
        .sort_values(
            ["all_splits_1c_entry_positive", "positive_1c_days", "min_split_net_after_fees_1c_entry_dollars"],
            ascending=[False, False, False],
        )
    )


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    metadata: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    all_day = one_cent[one_cent["positive_1c_days"].eq(one_cent["total_days"])].copy() if not one_cent.empty else one_cent
    prob = pd.DataFrame(prob_records)
    holdout = prob[prob["split"].eq("holdout")].sort_values(["brier", "logloss"])
    lines = [
        "# v43 Latent-Hole Posterior Weight Sweep",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only sweep over book/FV posterior weights after latent edge-hole trigger.",
        "- Uses the same v42 80% split-coverage, fee, 1c haircut, day, and block checks.",
        "- Live bot untouched.",
        "",
        "## Search Result",
        "",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        f"- Rows after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive split rows: {len(one_cent)}",
        f"- Fee+1c positive all-day rows: {len(all_day)}",
        "",
        "## Holdout Probability",
        "",
        "| candidate | Brier | logloss | side acc | mean p_yes |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in holdout.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} | {v42.pct(row['mean_p_yes'])} |"
        )
    lines += [
        "",
        "## Best Row Per Surface",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | {v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if all_day.empty:
        lines.append("- No weighted latent-hole posterior is all-day positive after fees plus 1c entry.")
    else:
        best = all_day.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "block10_positive", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-day row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_positive_rows": int(len(all_day)),
                    "probability_records": prob_records,
                    "selected": selected.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = v42.load_rows()
    ops = v42.opportunity_table(rows)
    ops, candidate_cols, metadata = build_weight_candidates(ops)
    prob_records = v42.probability_metrics(ops, candidate_cols)
    summary, _ = v42.build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_by_family(summary)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v43 latent-hole weight sweep complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
