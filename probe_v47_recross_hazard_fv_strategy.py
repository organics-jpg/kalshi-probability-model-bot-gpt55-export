"""v47 re-cross hazard FV strategy probe.

Research-only. Tests whether v45 is overconfident when the selected side has a
fresh favorable burst but the price has not moved far enough from the strike.
That state is treated as re-cross hazard: the selected-side probability is
capped or shrunk instead of allowing the model to extrapolate continuation.

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
import probe_v45_latent_disagreement_switch_strategy as v45
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v47_recross_hazard_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v47_recross_hazard_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v47_recross_hazard_fv_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v47_recross_hazard_fv_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v47_recross_hazard_fv_selected_trades_latest.csv"

BASE_COL = "v45_latent_disagree_book_else_blend90_p_yes_candidate"
BASE_MODEL = "v45_latent_disagree_book_else_blend90"
PHYSICS_COLS = [
    "margin_per_rv_sigma_15m",
    "signed_velocity_dps_1m",
    "signed_velocity_dps_3m",
]


def load_rows() -> pd.DataFrame:
    usecols = {
        "opportunity_key",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "seconds_to_close",
        "split",
        f"{v42.MODEL}_p_yes",
        *PHYSICS_COLS,
    }
    rows = pd.read_csv(v42.INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in [
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "seconds_to_close",
        f"{v42.MODEL}_p_yes",
        *PHYSICS_COLS,
    ]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    return rows.dropna(
        subset=[
            "opportunity_key",
            "entry_dt",
            "market",
            "side",
            "ask_cents",
            "seconds_to_close",
            "split",
        ]
    ).sort_values(["market", "entry_dt", "side"]).reset_index(drop=True)


def side_adjusted_p_yes(side: pd.Series, p_side: np.ndarray) -> pd.Series:
    p = np.where(side.astype(str).eq("yes"), p_side, 1.0 - p_side)
    return pd.Series(p, index=side.index).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def recross_features(ops: pd.DataFrame, base_p: pd.Series) -> pd.DataFrame:
    selected_side = v45.selected_side_from_p(ops, base_p)
    sign = np.where(selected_side.astype(str).eq("yes"), 1.0, -1.0)
    out = pd.DataFrame(index=ops.index)
    out["selected_side"] = selected_side
    out["selected_p_side"] = np.where(selected_side.eq("yes"), base_p, 1.0 - base_p)
    out["side_margin_sigma15"] = sign * pd.to_numeric(ops["margin_per_rv_sigma_15m"], errors="coerce")
    out["side_velocity_1m"] = sign * pd.to_numeric(ops["signed_velocity_dps_1m"], errors="coerce")
    out["side_velocity_3m"] = sign * pd.to_numeric(ops["signed_velocity_dps_3m"], errors="coerce")
    return out


def cap_selected_side(
    base_p: pd.Series,
    features: pd.DataFrame,
    hazard: pd.Series,
    *,
    cap: float,
) -> pd.Series:
    p_side = features["selected_p_side"].to_numpy(dtype=float)
    adjusted = np.where(hazard.to_numpy(dtype=bool), np.minimum(p_side, cap), p_side)
    return side_adjusted_p_yes(features["selected_side"], adjusted)


def shrink_selected_side(
    base_p: pd.Series,
    features: pd.DataFrame,
    hazard: pd.Series,
    *,
    factor: float,
) -> pd.Series:
    p_side = features["selected_p_side"].to_numpy(dtype=float)
    adjusted = np.where(hazard.to_numpy(dtype=bool), 0.5 + (p_side - 0.5) * factor, p_side)
    return side_adjusted_p_yes(features["selected_side"], adjusted)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v45.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    features = recross_features(out, base_p)
    in_entry_window = out["seconds_to_close"].between(0.0, 600.0)

    hazard_sigma1_v3 = (
        in_entry_window
        & features["side_margin_sigma15"].le(1.0)
        & features["side_velocity_3m"].ge(0.50)
    )
    hazard_sigma075_v3 = (
        in_entry_window
        & features["side_margin_sigma15"].le(0.75)
        & features["side_velocity_3m"].ge(0.50)
    )
    hazard_v1_2 = in_entry_window & features["side_velocity_1m"].ge(2.0)

    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    out["v47_recross_sigma1_v3cap68_p_yes_candidate"] = cap_selected_side(
        base_p,
        features,
        hazard_sigma1_v3,
        cap=0.68,
    )
    out["v47_recross_sigma1_v3cap72_p_yes_candidate"] = cap_selected_side(
        base_p,
        features,
        hazard_sigma1_v3,
        cap=0.72,
    )
    out["v47_recross_sigma075_v3cap75_p_yes_candidate"] = cap_selected_side(
        base_p,
        features,
        hazard_sigma075_v3,
        cap=0.75,
    )
    out["v47_recross_v1_2_shrink80_p_yes_candidate"] = shrink_selected_side(
        base_p,
        features,
        hazard_v1_2,
        factor=0.80,
    )

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "recross_definition": "selected side within 1.0 RV sigma and 3m selected-side velocity >= 0.50 dps",
            "hazard_sigma1_v3_rows": int(hazard_sigma1_v3.sum()),
            "hazard_sigma075_v3_rows": int(hazard_sigma075_v3.sum()),
            "hazard_v1_2_rows": int(hazard_v1_2.sum()),
        }
    )
    candidate_cols = [
        f"{BASE_MODEL}_p_yes_candidate",
        "v47_recross_sigma1_v3cap68_p_yes_candidate",
        "v47_recross_sigma1_v3cap72_p_yes_candidate",
        "v47_recross_sigma075_v3cap75_p_yes_candidate",
        "v47_recross_v1_2_shrink80_p_yes_candidate",
    ]
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
        "# v47 Re-cross Hazard FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability transform on top of the v45 lead.",
        "- Tests whether fresh favorable bursts near the strike should cap selected-side probability.",
        "- Entry/exit replay keeps the same 80% split-coverage, fee, and 1c haircut checks.",
        "- Live bot untouched.",
        "",
        "## Physics Notes",
        "",
        f"- Base model: `{metadata.get('base_model')}`",
        f"- Main hazard: {metadata.get('recross_definition')}",
        f"- Main hazard rows: {metadata.get('hazard_sigma1_v3_rows')}",
        f"- Tighter margin hazard rows: {metadata.get('hazard_sigma075_v3_rows')}",
        f"- One-minute burst hazard rows: {metadata.get('hazard_v1_2_rows')}",
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
        lines.append("- No v47 row cleared the all-day plus 7/10 block robustness gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust v47 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Treat this as a candidate requiring strict-forward validation, not a live-bot patch.")

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
    rows = load_rows()
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
    print("v47 re-cross hazard FV strategy complete")
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
