"""v63 late expensive-tail FV strategy probe.

Research-only. Tests whether very expensive, tiny-edge selected-side states
should have their FV probability capped even when they are not in the original
v50 thin-edge window. This targets the live-forward 97c NO / 1c edge failure
without adding an entry veto.

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
import probe_v55_book_anchor_recross_fv_strategy as v55
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v63_late_expensive_tail_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v63_late_expensive_tail_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v63_late_expensive_tail_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v63_late_expensive_tail_fv_selected_trades_latest.csv"

BASE_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
BASE_COL = f"{BASE_MODEL}_p_yes_candidate"

VARIANTS = [
    ("v63_tail_a94_e150_s120_cap85", 94.0, 1.50, 120.0, 0.85),
    ("v63_tail_a94_e200_s120_cap85", 94.0, 2.00, 120.0, 0.85),
    ("v63_tail_a94_e250_s120_cap85", 94.0, 2.50, 120.0, 0.85),
    ("v63_tail_a95_e150_s120_cap85", 95.0, 1.50, 120.0, 0.85),
    ("v63_tail_a95_e200_s120_cap85", 95.0, 2.00, 120.0, 0.85),
    ("v63_tail_a95_e250_s120_cap85", 95.0, 2.50, 120.0, 0.85),
    ("v63_tail_a96_e150_s120_cap85", 96.0, 1.50, 120.0, 0.85),
    ("v63_tail_a96_e200_s120_cap85", 96.0, 2.00, 120.0, 0.85),
    ("v63_tail_a96_e250_s120_cap85", 96.0, 2.50, 120.0, 0.85),
    ("v63_tail_a95_e200_s180_cap85", 95.0, 2.00, 180.0, 0.85),
    ("v63_tail_a95_e250_s180_cap85", 95.0, 2.50, 180.0, 0.85),
    ("v63_tail_a95_e200_s240_cap85", 95.0, 2.00, 240.0, 0.85),
    ("v63_tail_a95_e250_s240_cap85", 95.0, 2.50, 240.0, 0.85),
    ("v63_tail_a95_e200_s120_cap80", 95.0, 2.00, 120.0, 0.80),
    ("v63_tail_a95_e250_s120_cap80", 95.0, 2.50, 120.0, 0.80),
    ("v63_tail_a96_e200_s120_cap80", 96.0, 2.00, 120.0, 0.80),
    ("v63_tail_a96_e250_s120_cap80", 96.0, 2.50, 120.0, 0.80),
]


def side_adjusted_p_yes(side: pd.Series, p_side: np.ndarray | pd.Series) -> pd.Series:
    values = np.where(side.astype(str).eq("yes"), p_side, 1.0 - p_side)
    return pd.Series(values, index=side.index).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def selected_features(ops: pd.DataFrame, p_yes: pd.Series) -> pd.DataFrame:
    yes_edge = 100.0 * p_yes - ops["yes_ask_cents"]
    no_edge = 100.0 * (1.0 - p_yes) - ops["no_ask_cents"]
    selected_yes = yes_edge.ge(no_edge)
    out = pd.DataFrame(index=ops.index)
    out["selected_side"] = np.where(selected_yes, "yes", "no")
    out["selected_ask"] = np.where(selected_yes, ops["yes_ask_cents"], ops["no_ask_cents"])
    out["selected_edge"] = np.where(selected_yes, yes_edge, no_edge)
    out["selected_p_side"] = np.where(selected_yes, p_yes, 1.0 - p_yes)
    return out


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v55.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    features = selected_features(out, base_p)
    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]

    hazard_counts: dict[str, int] = {}
    for name, ask_min, edge_max, stc_min, cap in VARIANTS:
        hazard = (
            pd.to_numeric(features["selected_ask"], errors="coerce").ge(ask_min)
            & pd.to_numeric(features["selected_edge"], errors="coerce").le(edge_max)
            & out["seconds_to_close"].between(stc_min, 600.0)
        ).fillna(False)
        adjusted_side = np.where(hazard, np.minimum(features["selected_p_side"].to_numpy(dtype=float), cap), features["selected_p_side"])
        col = f"{name}_p_yes_candidate"
        out[col] = side_adjusted_p_yes(features["selected_side"], adjusted_side)
        candidate_cols.append(col)
        hazard_counts[name] = int(hazard.sum())

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": "expensive selected-side contracts with tiny FV edge are fragile certainty states",
            "variants": [
                {
                    "name": name,
                    "selected_ask_min_cents": ask_min,
                    "selected_edge_max_cents": edge_max,
                    "min_seconds_to_close": stc_min,
                    "selected_p_side_cap": cap,
                }
                for name, ask_min, edge_max, stc_min, cap in VARIANTS
            ],
            "hazard_counts": hazard_counts,
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
        "# v63 Late Expensive-Tail FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of v55.",
        "- Caps fragile high-ask tiny-edge selected-side probabilities.",
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
        "| candidate | Brier | logloss | side acc | mean p_yes |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.head(20).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} | {v42.pct(row['mean_p_yes'])} |"
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
        lines.append("- No v63 row cleared the robustness gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best v63 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Treat this as a probability-surface candidate requiring strict-forward validation before promotion.")
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
    print("v63 late expensive-tail FV strategy complete")
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
