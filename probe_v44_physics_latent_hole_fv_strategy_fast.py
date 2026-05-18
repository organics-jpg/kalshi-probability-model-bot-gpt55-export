"""Fast v44 physics plus latent-hole FV strategy probe.

Research-only. Reuses the cached v41 probability predictions and tests a small
set of physics/book posterior surfaces with the v43 latent-hole book blend.

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
V41_PREDICTIONS = OUT_DIR / "v41_physics_path_posterior_strategy_predictions_latest.csv"
REPORT_MD = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_latest.md"
REPORT_JSON = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_latest.json"
SUMMARY_CSV = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_selected_trades_latest.csv"

PROB_EPS = 1e-6

SOURCE_SURFACES = {
    "v41_v38_bookres_l210": "v41_v38_physics_book_residual_l210_p_yes_candidate",
    "v41_v38_bookres_l230": "v41_v38_physics_book_residual_l230_p_yes_candidate",
    "v41_v39_bookres_l210": "v41_v39_physics_book_residual_l210_p_yes_candidate",
    "v41_v39_bookres_l230": "v41_v39_physics_book_residual_l230_p_yes_candidate",
    "v41_v39_core_l210": "v41_v39_physics_core_l210_p_yes_candidate",
    "v41_v39_path_l230": "v41_v39_physics_path_l230_p_yes_candidate",
}
HOLE_BLEND_WEIGHTS = [0.80, 0.90, 1.00]


def load_v41_predictions() -> pd.DataFrame:
    usecols = ["opportunity_key", *SOURCE_SURFACES.values()]
    return pd.read_csv(V41_PREDICTIONS, usecols=lambda col: col in usecols, low_memory=False)


def logit_blend(left: pd.Series, right: pd.Series, weight_right: float) -> pd.Series:
    return pd.Series(
        sigmoid((1.0 - weight_right) * logit(left) + weight_right * logit(right)),
        index=left.index,
    ).clip(PROB_EPS, 1.0 - PROB_EPS)


def latent_hole_mask(ops: pd.DataFrame) -> tuple[pd.Series, dict[str, Any]]:
    holes = v42.first_hole_markets(
        ops,
        edge_floor=-2.0,
        p_floor=0.65,
        min_stc=60.0,
        max_stc=600.0,
        low=8.0,
        high=20.0,
    )
    mask = pd.Series(False, index=ops.index)
    for market, first_dt in holes.items():
        mask |= ops["market"].astype(str).eq(str(market)) & ops["entry_dt"].ge(pd.Timestamp(first_dt))
    return mask, {
        "latent_hole_markets": len(holes),
        "latent_hole_rows": int(mask.sum()),
        "trigger": "first raw-v38 selected edge in (8c,20c], p_side>=0.65, stc 60-600",
    }


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out = ops.merge(load_v41_predictions(), on="opportunity_key", how="left")
    latent_mask, metadata = latent_hole_mask(out)
    raw = out["v38_p_yes"].clip(PROB_EPS, 1.0 - PROB_EPS)
    book = out["book_mid_p_yes"].clip(PROB_EPS, 1.0 - PROB_EPS)

    candidate_cols: list[str] = []
    v43_ref = raw.copy()
    v43_ref.loc[latent_mask] = logit_blend(raw.loc[latent_mask], book.loc[latent_mask], 0.90)
    out["v44_v38_holeblend90_reference_p_yes_candidate"] = v43_ref.clip(PROB_EPS, 1.0 - PROB_EPS)
    candidate_cols.append("v44_v38_holeblend90_reference_p_yes_candidate")

    for short_name, source_col in SOURCE_SURFACES.items():
        if source_col not in out.columns:
            continue
        source = pd.to_numeric(out[source_col], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
        copy_col = f"v44_source_{short_name}_p_yes_candidate"
        out[copy_col] = source
        candidate_cols.append(copy_col)

        switch_col = f"v44_{short_name}_outside_source_inside_v43hole90_p_yes_candidate"
        out[switch_col] = source.copy()
        out.loc[latent_mask, switch_col] = v43_ref.loc[latent_mask]
        candidate_cols.append(switch_col)

        for weight in HOLE_BLEND_WEIGHTS:
            label = int(round(weight * 100))
            col = f"v44_{short_name}_holeblend{label}_p_yes_candidate"
            out[col] = source.copy()
            out.loc[latent_mask, col] = logit_blend(source.loc[latent_mask], book.loc[latent_mask], weight)
            candidate_cols.append(col)

    metadata["candidate_count"] = len(candidate_cols)
    metadata["source_surfaces"] = list(SOURCE_SURFACES)
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
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"]).head(18)

    lines = [
        "# v44 Fast Physics Latent-Hole FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only targeted test using cached v41 physics/book probability predictions.",
        "- Tests whether the v43 latent-hole book blend improves those FV surfaces without hard entry vetoes.",
        "- Uses the v42 entry/exit replay with at least 80% chronological split coverage.",
        "- Live bot untouched.",
        "",
        "## Model Notes",
        "",
        f"- Latent-hole markets: {metadata.get('latent_hole_markets')}",
        f"- Latent-hole opportunity rows: {metadata.get('latent_hole_rows')}",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        "",
        "## Holdout Probability",
        "",
        "| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {int(row['rows'])} | {float(row['brier']):.5f} | "
            f"{float(row['logloss']):.5f} | {v42.pct(row['side_accuracy'])} | "
            f"{v42.pct(row['mean_p_yes'])} | {v42.pct(row['yes_rate'])} |"
        )

    lines += [
        "",
        "## Strategy Search",
        "",
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
    for _, row in selected.head(40).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | {v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | {v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{v42.dollars(row['all_pnl_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )

    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v44 fast row cleared the all-day plus 7/10 block robustness gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust v44 fast row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    if not one_cent.empty:
        best_split = one_cent.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "positive_1c_days", "block10_positive"],
            ascending=[False, False, False],
        ).iloc[0]
        lines.append(
            f"- Best split-positive v44 fast row is `{best_split['model']}` / `{best_split['entry_policy']}` / "
            f"`{best_split['exit_policy']}` with min split fee+1c {v42.dollars(best_split['min_split_net_after_fees_1c_entry_dollars'])}."
        )

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
    rows = v42.load_rows()
    ops = v42.opportunity_table(rows)
    ops, candidate_cols, metadata = build_probability_candidates(ops)
    prob_records = v42.probability_metrics(ops, candidate_cols)
    summary, selected_trades = v42.build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = v42.selected_rows(summary) if not summary.empty else summary
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v44 fast physics latent-hole FV strategy complete")
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
