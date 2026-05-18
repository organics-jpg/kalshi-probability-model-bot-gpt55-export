"""v56 book-edge-gated re-cross FV strategy probe.

Research-only. Tests a stricter version of the v55 boundary-condition idea:
near strike, if the book mid does not itself clear the selected ask, the model's
extra edge is treated as extrapolation risk and anchored to the book. Otherwise
the softer v55 book+2 anchor is allowed.

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
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v50_v47_thin_edge_certainty_fv_strategy as v50
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v56_book_edge_recross_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v56_book_edge_recross_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v56_book_edge_recross_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v56_book_edge_recross_fv_selected_trades_latest.csv"

BASE_COL = "v50_thinedge_ask90_edge1_stc450_cap75_p_yes_candidate"
BASE_MODEL = "v50_thinedge_ask90_edge1_stc450_cap75"

VARIANTS = [
    ("v56_bedge0_m10_v15_g05_book_else_plus2", 1.0, 0.15, 0.05, 0.0),
    ("v56_bedge1_m10_v15_g05_book_else_plus2", 1.0, 0.15, 0.05, 1.0),
    ("v56_bedge2_m10_v15_g05_book_else_plus2", 1.0, 0.15, 0.05, 2.0),
    ("v56_bedge0_m10_v20_g05_book_else_plus2", 1.0, 0.20, 0.05, 0.0),
    ("v56_bedge1_m10_v20_g05_book_else_plus2", 1.0, 0.20, 0.05, 1.0),
    ("v56_bedge0_m11_v15_g05_book_else_plus2", 1.1, 0.15, 0.05, 0.0),
    ("v56_bedge1_m11_v15_g05_book_else_plus2", 1.1, 0.15, 0.05, 1.0),
    ("v56_bedge0_m10_v15_g04_book_else_plus2", 1.0, 0.15, 0.04, 0.0),
    ("v56_bedge1_m10_v15_g04_book_else_plus2", 1.0, 0.15, 0.04, 1.0),
]


def side_adjusted_p_yes(side: pd.Series, p_side: np.ndarray | pd.Series) -> pd.Series:
    values = np.where(side.astype(str).eq("yes"), p_side, 1.0 - p_side)
    return pd.Series(values, index=side.index).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v50.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    features = v47.recross_features(out, base_p)
    selected_side = features["selected_side"].astype(str)
    selected_p = features["selected_p_side"].astype(float)

    book_p_yes = out["book_mid_p_yes"].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    selected_book = pd.Series(np.where(selected_side.eq("yes"), book_p_yes, 1.0 - book_p_yes), index=out.index)
    selected_ask = pd.Series(
        np.where(selected_side.eq("yes"), out["yes_ask_cents"], out["no_ask_cents"]),
        index=out.index,
    ).astype(float)
    model_book_gap = selected_p - selected_book
    book_edge_cents = 100.0 * selected_book - selected_ask
    in_entry_window = out["seconds_to_close"].between(0.0, 600.0)

    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    hazard_counts: dict[str, int] = {}
    book_gate_counts: dict[str, int] = {}
    for name, margin_max, velocity_min, gap_min, book_edge_max in VARIANTS:
        hazard = (
            in_entry_window
            & features["side_margin_sigma15"].le(margin_max)
            & features["side_velocity_3m"].ge(velocity_min)
            & model_book_gap.ge(gap_min)
        ).fillna(False)
        book_gate = (hazard & book_edge_cents.le(book_edge_max)).fillna(False)
        soft_anchor = (hazard & ~book_gate).fillna(False)
        adjusted_side = np.where(book_gate, selected_book, selected_p)
        adjusted_side = np.where(soft_anchor, np.minimum(adjusted_side, selected_book + 0.02), adjusted_side)
        col = f"{name}_p_yes_candidate"
        out[col] = side_adjusted_p_yes(selected_side, adjusted_side)
        candidate_cols.append(col)
        hazard_counts[name] = int(hazard.sum())
        book_gate_counts[name] = int(book_gate.sum())

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": "near-strike FV edge unsupported by book edge is extrapolation risk",
            "variants": [
                {
                    "name": name,
                    "max_margin_sigma15": margin,
                    "min_velocity_3m": velocity,
                    "min_model_minus_book": gap,
                    "book_edge_max_cents": book_edge,
                }
                for name, margin, velocity, gap, book_edge in VARIANTS
            ],
            "hazard_counts": hazard_counts,
            "book_gate_counts": book_gate_counts,
        }
    )
    return out, candidate_cols, metadata


def selected_by_surface(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy()
    source = robust if not robust.empty else eligible
    return source.sort_values(
        ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars", "block10_positive"],
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
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy() if not eligible.empty else eligible
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"])

    lines = [
        "# v56 Book-Edge Re-cross FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of v50.",
        "- Tests whether unsupported near-strike model/book edge should be anchored fully to book.",
        "- Live bot untouched.",
        "",
        "## Search",
        "",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Robust rows: {len(robust)}",
        "",
        "## Holdout Probability",
        "",
        "| candidate | Brier | logloss | side acc |",
        "|---|---:|---:|---:|",
    ]
    for _, row in holdout_prob.head(20).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} |"
        )
    lines += [
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v56 row cleared the robustness gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best v56 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Strict-forward validation is required before promotion.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
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
    selected = selected_by_surface(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v56 book-edge re-cross FV strategy complete")
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
