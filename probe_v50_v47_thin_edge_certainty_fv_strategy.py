"""v50 thin-edge certainty cap on top of v47.

Research-only. Tests whether the v47 surface is still overconfident when the
entry is expensive, has only a tiny fair-value edge, and there is enough time
left for a re-cross. This is represented as a probability cap, not a live bot
entry-rule change.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v45_latent_disagreement_switch_strategy as v45
import probe_v47_recross_hazard_fv_strategy as v47
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v50_v47_thin_edge_certainty_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v50_v47_thin_edge_certainty_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v50_v47_thin_edge_certainty_fv_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v50_v47_thin_edge_certainty_fv_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v50_v47_thin_edge_certainty_fv_selected_trades_latest.csv"

BASE_COL = "v47_recross_sigma1_v3cap68_p_yes_candidate"
BASE_MODEL = "v47_recross_sigma1_v3cap68"


def side_adjusted_p_yes(side: pd.Series, p_side: np.ndarray) -> pd.Series:
    return pd.Series(np.where(side.astype(str).eq("yes"), p_side, 1.0 - p_side), index=side.index).clip(
        v42.PROB_EPS,
        1.0 - v42.PROB_EPS,
    )


def cap_expensive_thin_edge(
    ops: pd.DataFrame,
    base_p: pd.Series,
    *,
    ask_min: float,
    edge_max: float,
    stc_min: float,
    cap: float,
) -> tuple[pd.Series, pd.Series]:
    selected_side = v45.selected_side_from_p(ops, base_p)
    yes_edge = 100.0 * base_p - ops["yes_ask_cents"]
    no_edge = 100.0 * (1.0 - base_p) - ops["no_ask_cents"]
    selected_ask = np.where(selected_side.eq("yes"), ops["yes_ask_cents"], ops["no_ask_cents"])
    selected_edge = np.where(selected_side.eq("yes"), yes_edge, no_edge)
    selected_p_side = np.where(selected_side.eq("yes"), base_p, 1.0 - base_p)
    hazard = (
        pd.Series(selected_ask, index=ops.index).ge(ask_min)
        & pd.Series(selected_edge, index=ops.index).le(edge_max)
        & ops["seconds_to_close"].between(stc_min, 600.0)
    ).fillna(False)
    adjusted_side = np.where(hazard, np.minimum(selected_p_side, cap), selected_p_side)
    return side_adjusted_p_yes(selected_side, adjusted_side), hazard


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v47.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    variants = [
        ("v50_thinedge_ask90_edge1_stc450_cap75", 90.0, 1.0, 450.0, 0.75),
        ("v50_thinedge_ask90_edge2_stc450_cap75", 90.0, 2.0, 450.0, 0.75),
        ("v50_thinedge_ask92_edge1_stc450_cap75", 92.0, 1.0, 450.0, 0.75),
        ("v50_thinedge_ask90_edge3_stc500_cap75", 90.0, 3.0, 500.0, 0.75),
    ]
    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    hazard_counts: dict[str, int] = {}
    for name, ask_min, edge_max, stc_min, cap in variants:
        values, hazard = cap_expensive_thin_edge(out, base_p, ask_min=ask_min, edge_max=edge_max, stc_min=stc_min, cap=cap)
        col = f"{name}_p_yes_candidate"
        out[col] = values
        candidate_cols.append(col)
        hazard_counts[name] = int(hazard.sum())
    metadata.update(
        {
            "base_model": BASE_MODEL,
            "thin_edge_hypothesis": "expensive selected ask plus <= small fair edge with 450-600s left is fragile certainty",
            "hazard_counts": hazard_counts,
        }
    )
    return out, candidate_cols, metadata


def selected_by_surface(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
    ].copy()
    source = robust if not robust.empty else eligible
    return source.sort_values(
        [
            "min_split_net_after_fees_1c_entry_dollars",
            "all_net_after_fees_1c_entry_dollars",
            "block10_positive",
        ],
        ascending=[False, False, False],
    ).head(40)


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
    robust = all_day[all_day["block10_positive"].ge(7)].copy() if not all_day.empty else all_day
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"])
    lines = [
        "# v50 Thin-Edge Certainty FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of v47.",
        "- Caps expensive tiny-edge certainty before close instead of treating it as reliable edge.",
        "- Live bot untouched.",
        "",
        "## Physics Notes",
        "",
        f"- Base model: `{metadata.get('base_model')}`",
        f"- Hypothesis: {metadata.get('thin_edge_hypothesis')}",
    ]
    for name, count in (metadata.get("hazard_counts") or {}).items():
        lines.append(f"- `{name}` hazard rows: {count}")
    lines += [
        "",
        "## Holdout Probability",
        "",
        "| candidate | Brier | logloss | side acc | mean p_yes |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} | {v42.pct(row['mean_p_yes'])} |"
        )
    lines += [
        "",
        "## Strategy Search",
        "",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive train/validation/holdout rows: {len(one_cent)}",
        f"- Fee+1c positive all-day rows: {len(all_day)}",
        f"- All-day rows with at least 7/10 positive chronological blocks: {len(robust)}",
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | {v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | {v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{v42.dollars(row['all_pnl_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v50 row cleared the all-day plus 7/10 block robustness gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust v50 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Treat this as research evidence requiring strict-forward validation, not a live-bot patch.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_positive_rows": int(len(all_day)),
                    "robust_rows": int(len(robust)),
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
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, candidate_cols, metadata = build_probability_candidates(ops)
    prob_records = v42.probability_metrics(ops, candidate_cols)
    summary, selected_trades = v42.build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_by_surface(summary)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v50 thin-edge certainty FV strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
