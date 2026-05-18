"""v53 weak re-cross plus thin-edge certainty FV combo.

Research-only. Combines the best v52 weak re-cross cap with the v50 expensive
thin-edge certainty cap. The goal is to see whether the current forward-loss
stress signal can be covered without giving back too much retrospective PnL.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v50_v47_thin_edge_certainty_fv_strategy as v50
import probe_v52_weak_recross_hazard_fv_strategy as v52
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_selected_trades_latest.csv"

BASES = [
    "v52_weakrecross_sigma08_v3p15_cap68",
    "v52_weakrecross_sigma1_v3p15_cap75",
    "v52_weakrecross_sigma1_v3p15_cap72",
]

THIN_VARIANTS = [
    ("thin_ask90_edge1_stc450_cap75", 90.0, 1.0, 450.0, 0.75),
    ("thin_ask90_edge2_stc450_cap75", 90.0, 2.0, 450.0, 0.75),
    ("thin_ask90_edge1_stc450_cap72", 90.0, 1.0, 450.0, 0.72),
    ("thin_ask92_edge1_stc450_cap75", 92.0, 1.0, 450.0, 0.75),
]


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v52.build_probability_candidates(ops)
    candidate_cols: list[str] = []
    hazard_counts: dict[str, int] = {}
    for base in BASES:
        base_col = f"{base}_p_yes_candidate"
        base_p = out[base_col].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
        for suffix, ask_min, edge_max, stc_min, cap in THIN_VARIANTS:
            values, hazard = v50.cap_expensive_thin_edge(
                out,
                base_p,
                ask_min=ask_min,
                edge_max=edge_max,
                stc_min=stc_min,
                cap=cap,
            )
            name = f"v53_{base}_{suffix}"
            col = f"{name}_p_yes_candidate"
            out[col] = values
            candidate_cols.append(col)
            hazard_counts[name] = int(hazard.sum())
    metadata.update(
        {
            "base_models": BASES,
            "thin_variants": [
                {"name": name, "ask_min": ask, "edge_max": edge, "stc_min": stc, "cap": cap}
                for name, ask, edge, stc, cap in THIN_VARIANTS
            ],
            "hazard_counts": hazard_counts,
            "hypothesis": "combine weaker near-strike re-cross caution with v50 expensive tiny-edge certainty cap",
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
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars", "block10_positive"],
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
        "# v53 Weak Re-cross + Thin-Edge Combo FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform.",
        "- Combines v52 weak re-cross caution with v50 expensive tiny-edge certainty cap.",
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
        lines.append("- No v53 row cleared the robustness gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best v53 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append("- This improves worst-split PnL versus v50 but gives back some all-market PnL.")
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
    print("v53 weak re-cross plus thin-edge combo FV strategy complete")
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
