"""v52 weak re-cross hazard FV strategy probe.

Research-only. Tests whether v47's re-cross hazard is too strict: the current
strict-forward losses show selected-side cushion under 1 RV sigma with only
moderate favorable velocity, below the v47 0.50 dps threshold.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v45_latent_disagreement_switch_strategy as v45
import probe_v47_recross_hazard_fv_strategy as v47
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v52_weak_recross_hazard_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v52_weak_recross_hazard_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v52_weak_recross_hazard_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v52_weak_recross_hazard_fv_selected_trades_latest.csv"

BASE_COL = "v45_latent_disagree_book_else_blend90_p_yes_candidate"
BASE_MODEL = "v45_latent_disagree_book_else_blend90"


VARIANTS = [
    ("v52_weakrecross_sigma1_v3p10_cap68", 1.00, 0.10, 0.68),
    ("v52_weakrecross_sigma1_v3p15_cap68", 1.00, 0.15, 0.68),
    ("v52_weakrecross_sigma1_v3p20_cap68", 1.00, 0.20, 0.68),
    ("v52_weakrecross_sigma1_v3p25_cap68", 1.00, 0.25, 0.68),
    ("v52_weakrecross_sigma1_v3p15_cap72", 1.00, 0.15, 0.72),
    ("v52_weakrecross_sigma1_v3p15_cap75", 1.00, 0.15, 0.75),
    ("v52_weakrecross_sigma08_v3p15_cap68", 0.80, 0.15, 0.68),
    ("v52_weakrecross_sigma12_v3p15_cap68", 1.20, 0.15, 0.68),
]


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v45.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    features = v47.recross_features(out, base_p)
    in_entry_window = out["seconds_to_close"].between(0.0, 600.0)

    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    hazard_counts: dict[str, int] = {}
    for name, max_margin_sigma, min_velocity_3m, cap in VARIANTS:
        hazard = (
            in_entry_window
            & features["side_margin_sigma15"].le(max_margin_sigma)
            & features["side_velocity_3m"].ge(min_velocity_3m)
        ).fillna(False)
        out[f"{name}_p_yes_candidate"] = v47.cap_selected_side(base_p, features, hazard, cap=cap)
        candidate_cols.append(f"{name}_p_yes_candidate")
        hazard_counts[name] = int(hazard.sum())

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": "v47 re-cross hazard threshold is too strict; moderate favorable velocity near strike is also fragile.",
            "variants": [
                {"name": name, "max_margin_sigma15": margin, "min_velocity_3m": velocity, "cap": cap}
                for name, margin, velocity, cap in VARIANTS
            ],
            "hazard_counts": hazard_counts,
        }
    )
    return out, candidate_cols, metadata


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
        "# v52 Weak Re-cross Hazard FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of v45.",
        "- Sweeps weaker near-strike re-cross caps than v47.",
        "- Live bot untouched.",
        "",
        "## Physics Notes",
        "",
        f"- Base model: `{metadata.get('base_model')}`",
        f"- Hypothesis: {metadata.get('hypothesis')}",
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
        lines.append("- No weak re-cross row cleared the all-day plus 7/10 block robustness gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Treat this as a hypothesis screen; strict-forward validation is still required.")

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
    selected = v47.selected_by_surface(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v52 weak re-cross hazard FV strategy complete")
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
