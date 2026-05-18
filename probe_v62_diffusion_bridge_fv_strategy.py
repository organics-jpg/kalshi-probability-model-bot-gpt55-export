"""v62 diffusion-bridge FV strategy probe.

Research-only. Tests whether near-strike probabilities should be blended with a
simple terminal diffusion prior: normalized distance-to-strike divided by
remaining-time volatility. The goal is a physics-side FV correction, not an
exit-only rule.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import logit, sigmoid


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v62_diffusion_bridge_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v62_diffusion_bridge_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v62_diffusion_bridge_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v62_diffusion_bridge_fv_selected_trades_latest.csv"

BASE_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
BASE_COL = f"{BASE_MODEL}_p_yes_candidate"

VARIANTS = [
    ("v62_diff_m050_t125_w25", 0.50, 1.25, 0.25),
    ("v62_diff_m050_t150_w25", 0.50, 1.50, 0.25),
    ("v62_diff_m050_t200_w25", 0.50, 2.00, 0.25),
    ("v62_diff_m075_t125_w25", 0.75, 1.25, 0.25),
    ("v62_diff_m075_t150_w25", 0.75, 1.50, 0.25),
    ("v62_diff_m075_t200_w25", 0.75, 2.00, 0.25),
    ("v62_diff_m100_t125_w25", 1.00, 1.25, 0.25),
    ("v62_diff_m100_t150_w25", 1.00, 1.50, 0.25),
    ("v62_diff_m100_t200_w25", 1.00, 2.00, 0.25),
    ("v62_diff_m075_t150_w50", 0.75, 1.50, 0.50),
    ("v62_diff_m100_t150_w50", 1.00, 1.50, 0.50),
    ("v62_diff_m100_t200_w50", 1.00, 2.00, 0.50),
]


def normal_cdf(values: np.ndarray) -> np.ndarray:
    erf = np.vectorize(math.erf)
    return 0.5 * (1.0 + erf(values / math.sqrt(2.0)))


def diffusion_probability(ops: pd.DataFrame, temperature: float) -> pd.Series:
    margin = pd.to_numeric(ops["margin_per_rv_sigma_15m"], errors="coerce").to_numpy(dtype=float)
    seconds = pd.to_numeric(ops["seconds_to_close"], errors="coerce").to_numpy(dtype=float)
    time_fraction = np.maximum(seconds, 30.0) / 900.0
    denom = temperature * np.sqrt(time_fraction)
    z = np.divide(margin, denom, out=np.zeros_like(margin, dtype=float), where=denom > 0.0)
    return pd.Series(normal_cdf(z), index=ops.index).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def blend_probability(base_p: pd.Series, diffusion_p: pd.Series, mask: pd.Series, weight: float) -> pd.Series:
    blended = sigmoid((1.0 - weight) * logit(base_p) + weight * logit(diffusion_p))
    return pd.Series(np.where(mask, blended, base_p), index=base_p.index).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v55.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    yes_axis_margin = pd.to_numeric(out["margin_per_rv_sigma_15m"], errors="coerce")
    in_entry_window = out["seconds_to_close"].between(0.0, 600.0)

    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    mask_counts: dict[str, int] = {}
    for name, margin_abs_max, temperature, weight in VARIANTS:
        diffusion_p = diffusion_probability(out, temperature)
        mask = (in_entry_window & yes_axis_margin.abs().le(margin_abs_max)).fillna(False)
        col = f"{name}_p_yes_candidate"
        out[col] = blend_probability(base_p, diffusion_p, mask, weight)
        candidate_cols.append(col)
        mask_counts[name] = int(mask.sum())

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": (
                "near strike, terminal probability should partially obey a diffusion bridge from current "
                "distance-to-strike and remaining-time volatility"
            ),
            "variants": [
                {
                    "name": name,
                    "yes_axis_abs_margin_max_sigma15": margin_abs_max,
                    "volatility_temperature": temperature,
                    "logit_blend_weight": weight,
                }
                for name, margin_abs_max, temperature, weight in VARIANTS
            ],
            "mask_counts": mask_counts,
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
        "# v62 Diffusion-Bridge FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of v55.",
        "- Blends near-strike probability with a distance/time diffusion prior.",
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
        lines.append("- No v62 row cleared the robustness gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best v62 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
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
    print("v62 diffusion-bridge FV strategy complete")
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
