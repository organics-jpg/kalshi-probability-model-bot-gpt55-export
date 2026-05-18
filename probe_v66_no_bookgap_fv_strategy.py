"""v66 NO-side book-gap FV strategy probe.

Research-only. Tests a causal probability-surface adjustment discovered after
v65: v57 losses cluster in NO entries where the model is far richer than the
order book, while comparable YES-side model/book gaps are historically positive.

The transform shrinks only selected NO-side probabilities back toward the book
when model-minus-book disagreement is large. It is an FV adjustment, not a live
bot patch and not an explicit trade veto.
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
REPORT_MD = OUT_DIR / "v66_no_bookgap_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v66_no_bookgap_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v66_no_bookgap_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v66_no_bookgap_fv_selected_trades_latest.csv"
DIAGNOSTIC_CSV = OUT_DIR / "v66_no_bookgap_entry_diagnostics_latest.csv"

BASE_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
BASE_COL = f"{BASE_MODEL}_p_yes_candidate"

# Small, interpretable set from the cheap v66 screen. The first entries favor
# all-market PnL; the blend rows favor min-split robustness.
VARIANTS = [
    ("v66_no_bookgap_g05_bookplus00", 0.05, "book_plus", 0.00),
    ("v66_no_bookgap_g08_bookplus04", 0.08, "book_plus", 0.04),
    ("v66_no_bookgap_g05_bookplus04", 0.05, "book_plus", 0.04),
    ("v66_no_bookgap_g08_blend50", 0.08, "blend", 0.50),
    ("v66_no_bookgap_g08_blend75", 0.08, "blend", 0.75),
    ("v66_no_bookgap_g05_blend50", 0.05, "blend", 0.50),
]


def selected_context(ops: pd.DataFrame, base_p: pd.Series) -> pd.DataFrame:
    features = v47.recross_features(ops, base_p)
    book_p_yes = pd.to_numeric(ops["book_mid_p_yes"], errors="coerce").clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    selected_side = features["selected_side"].astype(str)
    selected_book = pd.Series(np.where(selected_side.eq("yes"), book_p_yes, 1.0 - book_p_yes), index=ops.index)
    out = features.copy()
    out["book_p_yes"] = book_p_yes
    out["selected_book_p_side"] = selected_book
    out["model_book_gap"] = out["selected_p_side"].astype(float) - selected_book.astype(float)
    return out


def adjust_side_probability(
    selected_p: pd.Series,
    selected_book: pd.Series,
    mask: pd.Series,
    mode: str,
    value: float,
) -> np.ndarray:
    if mode == "book_plus":
        target = np.minimum(selected_p, selected_book + value)
    elif mode == "blend":
        target = (1.0 - value) * selected_p + value * selected_book
    else:
        raise ValueError(f"unknown v66 mode: {mode}")
    return np.where(mask.to_numpy(dtype=bool), target, selected_p)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v55.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    ctx = selected_context(out, base_p)
    selected_side = ctx["selected_side"].astype(str)
    selected_p = ctx["selected_p_side"].astype(float)
    selected_book = ctx["selected_book_p_side"].astype(float)
    no_side = selected_side.eq("no")
    in_entry_window = out["seconds_to_close"].between(0.0, 600.0)
    gap = ctx["model_book_gap"].astype(float)

    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    variant_records: list[dict[str, Any]] = []
    for name, gap_threshold, mode, value in VARIANTS:
        mask = (in_entry_window & no_side & gap.ge(gap_threshold)).fillna(False)
        adjusted = adjust_side_probability(selected_p, selected_book, mask, mode, value)
        col = f"{name}_p_yes_candidate"
        out[col] = v47.side_adjusted_p_yes(selected_side, adjusted)
        candidate_cols.append(col)
        variant_records.append(
            {
                "name": name,
                "gap_threshold": gap_threshold,
                "mode": mode,
                "value": value,
                "adjusted_rows": int(mask.sum()),
            }
        )

    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": (
                "NO-side model/book disagreement is more fragile than YES-side disagreement; "
                "large NO-side selected probability gaps should be shrunk toward the book"
            ),
            "variants": variant_records,
        }
    )
    out = pd.concat(
        [
            out,
            ctx[
                [
                    "selected_side",
                    "selected_p_side",
                    "selected_book_p_side",
                    "model_book_gap",
                    "side_margin_sigma15",
                    "side_velocity_1m",
                    "side_velocity_3m",
                ]
            ].add_prefix("v66_"),
        ],
        axis=1,
    )
    return out, candidate_cols, metadata


def diagnostic_records(rows: pd.DataFrame, ops: pd.DataFrame) -> pd.DataFrame:
    import probe_v39_entry_exit_strategy_projection as base

    col = f"{BASE_MODEL}_p_yes_candidate"
    frame = v42.frame_for_candidate(rows, ops, col)
    best = base.best_side_per_opportunity(frame)
    entries = v42.choose_entries(best, base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0))
    paths = base.quote_paths(frame)
    trades = base.simulate(entries, paths, base.ExitPolicy("hold15_prob52", probability_floor=0.52, min_hold_seconds=15.0))
    trades["fee_1c_entry_cents"] = trades["pnl_cents"] - trades["total_fee_cents"] - base.QTY
    ctx_cols = [
        "opportunity_key",
        "entry_dt",
        "market",
        "v66_selected_side",
        "v66_selected_p_side",
        "v66_selected_book_p_side",
        "v66_model_book_gap",
        "v66_side_margin_sigma15",
        "v66_side_velocity_1m",
        "v66_side_velocity_3m",
    ]
    context = ops[[col for col in ctx_cols if col in ops.columns]].copy()
    merged = trades.merge(context, on=["market", "entry_dt"], how="left")
    records = []
    for label, mask in [
        ("all_v57_style", pd.Series(True, index=merged.index)),
        ("YES_gap_ge_05", merged["side"].astype(str).eq("yes") & merged["v66_model_book_gap"].ge(0.05)),
        ("NO_gap_ge_05", merged["side"].astype(str).eq("no") & merged["v66_model_book_gap"].ge(0.05)),
        ("NO_gap_ge_08", merged["side"].astype(str).eq("no") & merged["v66_model_book_gap"].ge(0.08)),
        ("NO_gap_ge_05_ask_lt_90", merged["side"].astype(str).eq("no") & merged["v66_model_book_gap"].ge(0.05) & merged["entry_ask_cents"].lt(90.0)),
        ("NO_gap_ge_05_ask_ge_90", merged["side"].astype(str).eq("no") & merged["v66_model_book_gap"].ge(0.05) & merged["entry_ask_cents"].ge(90.0)),
    ]:
        part = merged[mask.fillna(False)].copy()
        if part.empty:
            records.append({"slice": label, "trades": 0, "fee_1c_entry_dollars": 0.0})
            continue
        records.append(
            {
                "slice": label,
                "trades": int(len(part)),
                "fee_1c_entry_dollars": float(part["fee_1c_entry_cents"].sum() / 100.0),
                "avg_fee_1c_entry_cents": float(part["fee_1c_entry_cents"].mean()),
                "wins": int(part["win"].astype(bool).sum()),
                "losses": int((~part["win"].astype(bool)).sum()),
                "exits": int((~part["settled"].astype(bool)).sum()),
                "avg_ask": float(part["entry_ask_cents"].mean()),
                "avg_edge": float(part["entry_edge_cents"].mean()),
                "avg_p_side": float(part["entry_p_side"].mean()),
                "avg_model_book_gap": float(part["v66_model_book_gap"].mean()),
            }
        )
    return pd.DataFrame(records)


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
    diagnostics: pd.DataFrame,
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
        "# v66 NO-Side Book-Gap FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV transform on top of v55.",
        "- Shrinks large selected NO-side model/book gaps toward the book.",
        "- Live bot untouched.",
        "",
        "## Entry Diagnostic",
        "",
        "| slice | trades | fee+1c | avg c | wins | losses | exits | avg ask | avg edge | avg p | avg gap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in diagnostics.iterrows():
        lines.append(
            f"| `{row['slice']}` | {int(row['trades'])} | {v42.dollars(row['fee_1c_entry_dollars'])} | "
            f"{'' if pd.isna(row.get('avg_fee_1c_entry_cents')) else f'{float(row['avg_fee_1c_entry_cents']):.1f}'} | "
            f"{int(row.get('wins', 0))} | {int(row.get('losses', 0))} | {int(row.get('exits', 0))} | "
            f"{'' if pd.isna(row.get('avg_ask')) else f'{float(row['avg_ask']):.1f}'} | "
            f"{'' if pd.isna(row.get('avg_edge')) else f'{float(row['avg_edge']):.2f}'} | "
            f"{'' if pd.isna(row.get('avg_p_side')) else f'{float(row['avg_p_side']):.3f}'} | "
            f"{'' if pd.isna(row.get('avg_model_book_gap')) else f'{float(row['avg_model_book_gap']):.3f}'} |"
        )
    lines += [
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
        lines.append("- No v66 row cleared the robustness gate.")
    else:
        best_all = robust.sort_values(
            ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        best_min = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-market v66 row is `{best_all['model']}` with all fee+1c "
            f"{v42.dollars(best_all['all_net_after_fees_1c_entry_dollars'])} and min split "
            f"{v42.dollars(best_all['min_split_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append(
            f"- Best min-split v66 row is `{best_min['model']}` with min split fee+1c "
            f"{v42.dollars(best_min['min_split_net_after_fees_1c_entry_dollars'])} and all fee+1c "
            f"{v42.dollars(best_min['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Current read: useful robustness lens, not a PnL upgrade over v57/v60.")
    lines.append("- Strict-forward validation would be required before any promotion.")
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
                    "diagnostics": diagnostics.to_dict("records"),
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
    diagnostics = diagnostic_records(rows, ops)
    summary, selected_trades = v42.build_strategy(rows, ops, candidate_cols)
    selected = selected_by_surface(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    diagnostics.to_csv(DIAGNOSTIC_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, diagnostics, metadata, candidate_cols)
    print("v66 NO-side book-gap FV strategy complete")
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
