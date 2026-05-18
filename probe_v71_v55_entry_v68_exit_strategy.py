"""v71 v55 entry / v68 calibrated-logit exit strategy probe.

Research-only. v68 is the best probability-calibration surface found so far,
but direct v68 entry rows were not robust. This probe keeps the broad v55 entry
universe and tests whether v68 is useful as an exit-state surface, including
the v60 NO-side margin-gated exit family.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
import probe_v58_v55_exit_persistence_refine as v58
import probe_v68_regularized_physics_logit_fv_strategy as v68
import probe_v70_v55_entry_v66_margin_exit_strategy as v70
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v71_v55_entry_v68_exit_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v71_v55_entry_v68_exit_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v71_v55_entry_v68_exit_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v71_v55_entry_v68_exit_strategy_trades_latest.csv"

ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
ENTRY_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
ENTRY_COL = f"{ENTRY_MODEL}_p_yes_candidate"
EXIT_SURFACES = {
    "v55": (ENTRY_MODEL, ENTRY_COL),
    "v68_C1p0": ("v68_l2_C1p0", "v68_l2_C1p0_p_yes_candidate"),
    "v68_C0p5": ("v68_l2_C0p5", "v68_l2_C0p5_p_yes_candidate"),
    "v68_C0p2": ("v68_l2_C0p2", "v68_l2_C0p2_p_yes_candidate"),
    "v68_C0p1": ("v68_l2_C0p1", "v68_l2_C0p1_p_yes_candidate"),
    "v68_C0p05": ("v68_l2_C0p05", "v68_l2_C0p05_p_yes_candidate"),
}


def robust_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    return eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy()


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    robust = robust_rows(summary)
    source = robust if not robust.empty else summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    if source.empty:
        return source
    return source.sort_values(
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars", "block10_positive"],
        ascending=[False, False, False],
    ).head(40)


def summarize(
    model: str,
    exit_surface: str,
    policy: v58.PersistenceExitPolicy,
    trades: pd.DataFrame,
    universes: dict[str, set[str]],
) -> dict[str, Any]:
    record = base.flatten_metrics(model, ENTRY, base.ExitPolicy(policy.name), trades, universes)
    record["exit_surface"] = exit_surface
    record["exit_probability_floor"] = policy.probability_floor
    record["exit_min_hold_seconds"] = policy.min_hold_seconds
    record["exit_margin_ceiling_sigma15"] = policy.exit_margin_ceiling_sigma15
    record["exit_margin_gate_side"] = policy.margin_gate_side
    record["min_split_net_after_fees_1c_entry_dollars"] = float(
        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["all_splits_1c_entry_positive"] = v42.row_1c_positive(record)
    days = v42.day_metrics(trades)
    blocks = v42.block_metrics(trades, 10)
    record["positive_1c_days"] = days["positive_days"]
    record["total_days"] = days["total_days"]
    record["worst_1c_day_cents"] = days["worst_day_cents"]
    record["block10_positive"] = blocks["positive_blocks"]
    record["block10_worst_cents"] = blocks["worst_cents"]
    return record


def build() -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    rows = v47.load_rows()
    base_ops = v42.opportunity_table(rows)
    v55_ops, _, _ = v55.build_probability_candidates(base_ops.copy())
    v68_ops, v68_cols, _ = v68.build_probability_candidates(base_ops.copy())
    prob_records = v42.probability_metrics(v68_ops, v68_cols)
    universes = base.market_universes(rows)

    entry_frame = v42.frame_for_candidate(rows, v55_ops, ENTRY_COL)
    best = base.best_side_per_opportunity(entry_frame)
    entries = v42.choose_entries(best, ENTRY)
    if entries.empty:
        return pd.DataFrame(), pd.DataFrame(), prob_records

    records: list[dict[str, Any]] = []
    trades_by_key: dict[tuple[str, str], pd.DataFrame] = {}
    policies = v70.exit_policies()
    for exit_surface, (exit_model, exit_col) in EXIT_SURFACES.items():
        ops = v55_ops if exit_surface == "v55" else v68_ops
        if exit_col not in ops.columns:
            continue
        exit_frame = v42.frame_for_candidate(rows, ops, exit_col)
        paths = v58.quote_paths(exit_frame)
        for policy in policies:
            trades = v58.simulate(entries, paths, policy)
            if trades.empty:
                continue
            model = f"v55_entry__{exit_surface}_exit"
            records.append(summarize(model, exit_surface, policy, trades, universes))
            trades_by_key[(exit_surface, policy.name)] = trades.assign(candidate=model, exit_surface=exit_surface)

    summary = pd.DataFrame(records)
    selected = selected_rows(summary)
    selected_frames: list[pd.DataFrame] = []
    for _, row in selected.head(12).iterrows():
        frame = trades_by_key.get((str(row["exit_surface"]), str(row["exit_policy"])))
        if frame is not None:
            selected_frames.append(frame.assign(selected_rank=len(selected_frames) + 1))
    trades = pd.concat(selected_frames, ignore_index=True, sort=False) if selected_frames else pd.DataFrame()
    return summary, trades, prob_records


def write_report(summary: pd.DataFrame, selected: pd.DataFrame, prob_records: list[dict[str, Any]]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    robust = robust_rows(summary)
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"])
    lines = [
        "# v71 v55 Entry / v68 Exit Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only cross-surface exit test.",
        "- Entry universe is fixed to v55 `edge0_ask100_p0.65_stc0-600`.",
        "- Exit tests v68 calibrated-logit probabilities with the v60/v70 margin-gated policy family.",
        "- Live bot untouched.",
        "",
        "## Holdout Probability",
        "",
        "| candidate | Brier | logloss | side acc |",
        "|---|---:|---:|---:|",
    ]
    for _, row in holdout_prob.head(10).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} |"
        )
    lines += [
        "",
        "## Selected Rows",
        "",
        "| exit surface | exit policy | min cov | min 1c | all 1c | all fee | days | block10 | exits | trades |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"| `{row['exit_surface']}` | `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_exit_count'])} | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v71 row cleared the 80% coverage, split-positive, all-day, block-stability robustness screen.")
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
            f"- Best all-market robust v71 row is `{best_all['exit_surface']}` / `{best_all['exit_policy']}` "
            f"with all fee+1c {v42.dollars(best_all['all_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append(
            f"- Best min-split robust v71 row is `{best_min['exit_surface']}` / `{best_min['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best_min['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Compare to v60 all fee+1c $21.26 and v70 balanced all/min fee+1c $14.40/$2.17.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
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
    summary, trades, prob_records = build()
    selected = selected_rows(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not trades.empty:
        trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records)
    print("v71 v55 entry / v68 exit strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['exit_surface']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
