"""v45 latent-hole disagreement switch FV strategy probe.

Research-only. Tests a stricter interpretation of the edge-hole latent state:
inside the latent state, the book is treated as the dominant measurement only
when the raw FV side and two-sided book side disagree. Otherwise it keeps the
v43 90% book/FV blend.

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
REPORT_MD = OUT_DIR / "v45_latent_disagreement_switch_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v45_latent_disagreement_switch_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v45_latent_disagreement_switch_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v45_latent_disagreement_switch_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v45_latent_disagreement_switch_selected_trades_latest.csv"


def latent_mask(ops: pd.DataFrame) -> tuple[pd.Series, dict[str, Any]]:
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
    return mask, {"latent_hole_markets": len(holes), "latent_hole_rows": int(mask.sum())}


def blend(raw: pd.Series, book: pd.Series, weight: float) -> pd.Series:
    return pd.Series(
        sigmoid((1.0 - weight) * logit(raw) + weight * logit(book)),
        index=raw.index,
    ).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)


def selected_side_from_p(ops: pd.DataFrame, p_yes: pd.Series) -> pd.Series:
    yes_edge = 100.0 * p_yes - ops["yes_ask_cents"]
    no_edge = 100.0 * (1.0 - p_yes) - ops["no_ask_cents"]
    return pd.Series(np.where(yes_edge.ge(no_edge), "yes", "no"), index=ops.index)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out = ops.copy()
    raw = out["v38_p_yes"].clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    book = out["book_mid_p_yes"].clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    active, metadata = latent_mask(out)

    raw_side = selected_side_from_p(out, raw)
    book_side = selected_side_from_p(out, book)
    disagree = active & raw_side.ne(book_side)

    blend90 = raw.copy()
    blend90.loc[active] = blend(raw.loc[active], book.loc[active], 0.90)

    switch = blend90.copy()
    switch.loc[disagree] = book.loc[disagree]

    raw_disagree_book = raw.copy()
    raw_disagree_book.loc[disagree] = book.loc[disagree]

    book_on_hole = raw.copy()
    book_on_hole.loc[active] = book.loc[active]

    out["v45_latent_disagree_book_else_blend90_p_yes_candidate"] = switch
    out["v45_latent_disagree_book_else_raw_p_yes_candidate"] = raw_disagree_book
    out["v45_latent_full_book_reference_p_yes_candidate"] = book_on_hole
    out["v45_latent_blend90_reference_p_yes_candidate"] = blend90

    metadata["latent_disagree_rows"] = int(disagree.sum())
    metadata["latent_disagree_markets"] = int(out.loc[disagree, "market"].astype(str).nunique())
    candidate_cols = [col for col in out.columns if col.endswith("_p_yes_candidate")]
    return out, candidate_cols, metadata


def selected_by_surface(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
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
        .head(3)
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
    robust = all_day[all_day["block10_positive"].ge(7)].copy() if not all_day.empty else all_day
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"])
    lines = [
        "# v45 Latent Disagreement Switch Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability probe on top of v38/v43 latent-hole logic.",
        "- Inside latent-hole state, switch fully to book only when raw FV and book selected sides disagree.",
        "- Entry/exit replay keeps the same 80% split-coverage, fee, and 1c haircut checks.",
        "- Live bot untouched.",
        "",
        "## Model Notes",
        "",
        f"- Latent-hole markets: {metadata.get('latent_hole_markets')}",
        f"- Latent-hole rows: {metadata.get('latent_hole_rows')}",
        f"- Raw/book disagreement rows inside latent state: {metadata.get('latent_disagree_rows')}",
        f"- Raw/book disagreement markets inside latent state: {metadata.get('latent_disagree_markets')}",
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
    for _, row in selected.head(35).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | {v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | {v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{v42.dollars(row['all_pnl_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v45 row cleared the all-day plus 7/10 block robustness gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust v45 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
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
    selected = selected_by_surface(summary)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v45 latent disagreement switch strategy complete")
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
