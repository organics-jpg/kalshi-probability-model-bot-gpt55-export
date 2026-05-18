"""v57 cross-surface entry/exit strategy probe.

Research-only. Tests whether a more calibrated but less profitable probability
surface should be used for exits while entries remain on the higher-PnL FV
surfaces. This separates "where to enter" from "when the probability thesis has
decayed."

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
import probe_v53_weak_recross_thin_edge_combo_fv_strategy as v53
import probe_v55_book_anchor_recross_fv_strategy as v55
import probe_v56_book_edge_recross_fv_strategy as v56
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v57_cross_surface_exit_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v57_cross_surface_exit_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v57_cross_surface_exit_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v57_cross_surface_exit_strategy_trades_latest.csv"

V50 = "v50_thinedge_ask90_edge1_stc450_cap75"
V53 = "v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75"
V55 = "v55_bookanchor_m10_v20_g05_book_plus2"
V56_CAL_1 = "v56_bedge1_m11_v15_g05_book_else_plus2"
V56_CAL_2 = "v56_bedge0_m11_v15_g05_book_else_plus2"
V56_CAL_3 = "v56_bedge1_m10_v15_g04_book_else_plus2"

ENTRY_MODELS = [V50, V53, V55]
EXIT_MODELS = [V50, V53, V55, V56_CAL_1, V56_CAL_2, V56_CAL_3]
ENTRY_POLICIES = [
    base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0),
    base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 60.0),
]
EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob52", probability_floor=0.52),
    base.ExitPolicy("prob54", probability_floor=0.54),
    base.ExitPolicy("prob56", probability_floor=0.56),
    base.ExitPolicy("hold15_prob52", probability_floor=0.52, min_hold_seconds=15.0),
    base.ExitPolicy("hold15_prob54", probability_floor=0.54, min_hold_seconds=15.0),
]


def candidate_col(model: str) -> str:
    return f"{model}_p_yes_candidate"


def build_all_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    out = ops.copy()
    sources: dict[str, pd.DataFrame] = {}
    source_meta: dict[str, Any] = {}
    for label, builder in [
        ("v55", v55.build_probability_candidates),
        ("v53", v53.build_probability_candidates),
        ("v56", v56.build_probability_candidates),
    ]:
        built, _, metadata = builder(ops)
        sources[label] = built
        source_meta[label] = metadata

    needed = {candidate_col(model) for model in set(ENTRY_MODELS + EXIT_MODELS)}
    missing: list[str] = []
    for col in needed:
        for built in sources.values():
            if col in built.columns:
                out[col] = built[col]
                break
        else:
            missing.append(col)
    if missing:
        raise SystemExit(f"Missing candidate columns: {missing}")
    return out, {"source_metadata": source_meta, "entry_models": ENTRY_MODELS, "exit_models": EXIT_MODELS}


def summarize_trade_row(
    entry_model: str,
    entry_policy: base.EntryPolicy,
    exit_model: str,
    exit_policy: base.ExitPolicy,
    trades: pd.DataFrame,
    universes: dict[str, set[str]],
) -> dict[str, Any]:
    model_name = f"{entry_model}__exit_{exit_model}"
    record = base.flatten_metrics(model_name, entry_policy, exit_policy, trades, universes)
    record["entry_model"] = entry_model
    record["exit_model"] = exit_model
    record["cross_model"] = model_name
    record["exit_policy"] = exit_policy.name
    record["min_split_net_after_fees_1c_entry_dollars"] = float(
        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["all_splits_1c_entry_positive"] = v42.row_1c_positive(record)
    days = v42.day_metrics(trades)
    record["positive_1c_days"] = days["positive_days"]
    record["total_days"] = days["total_days"]
    record["worst_1c_day_cents"] = days["worst_day_cents"]
    block10 = v42.block_metrics(trades, 10)
    record["block10_positive"] = block10["positive_blocks"]
    record["block10_worst_cents"] = block10["worst_cents"]
    return record


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
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
    ).head(50)


def run_search(rows: pd.DataFrame, ops: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    universes = base.market_universes(rows)
    frame_cache: dict[str, pd.DataFrame] = {}
    best_cache: dict[str, pd.DataFrame] = {}
    path_cache: dict[str, dict[tuple[str, str], base.QuotePath]] = {}
    for model in set(ENTRY_MODELS + EXIT_MODELS):
        frame = v42.frame_for_candidate(rows, ops, candidate_col(model))
        frame["model"] = model
        frame_cache[model] = frame
        best_cache[model] = base.best_side_per_opportunity(frame)
        path_cache[model] = base.quote_paths(frame)

    records: list[dict[str, Any]] = []
    selected_trade_frames: list[pd.DataFrame] = []
    for entry_model in ENTRY_MODELS:
        for entry_policy in ENTRY_POLICIES:
            entries = v42.choose_entries(best_cache[entry_model], entry_policy)
            if entries.empty:
                continue
            min_coverage = min(
                len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                for split in ["train", "validation", "holdout"]
            )
            if min_coverage < v42.MIN_SPLIT_COVERAGE:
                continue
            for exit_model in EXIT_MODELS:
                for exit_policy in EXIT_POLICIES:
                    trades = base.simulate(entries, path_cache[exit_model], exit_policy)
                    if trades.empty:
                        continue
                    trades["model"] = f"{entry_model}__exit_{exit_model}"
                    trades["entry_model"] = entry_model
                    trades["exit_model"] = exit_model
                    record = summarize_trade_row(entry_model, entry_policy, exit_model, exit_policy, trades, universes)
                    record["min_split_coverage"] = min_coverage
                    records.append(record)

    summary = pd.DataFrame(records)
    selected = selected_rows(summary)
    if not selected.empty:
        for _, row in selected.head(12).iterrows():
            entry_policy = base.EntryPolicy(
                float(row["entry_edge_floor_cents"]),
                float(row["entry_ask_cap_cents"]),
                float(row["entry_min_p_side"]),
                float(row["entry_max_seconds_to_close"]),
                float(row["entry_min_seconds_to_close"]),
            )
            exit_policy = next(policy for policy in EXIT_POLICIES if policy.name == row["exit_policy"])
            entries = v42.choose_entries(best_cache[str(row["entry_model"])], entry_policy)
            trades = base.simulate(entries, path_cache[str(row["exit_model"])], exit_policy)
            trades["model"] = row["cross_model"]
            trades["entry_model"] = row["entry_model"]
            trades["exit_model"] = row["exit_model"]
            trades["entry_policy"] = row["entry_policy"]
            trades["exit_policy"] = row["exit_policy"]
            selected_trade_frames.append(trades)
    selected_trades = pd.concat(selected_trade_frames, ignore_index=True, sort=False) if selected_trade_frames else pd.DataFrame()
    return summary, selected_trades


def write_report(summary: pd.DataFrame, selected: pd.DataFrame, metadata: dict[str, Any]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy() if not eligible.empty else eligible
    lines = [
        "# v57 Cross-Surface Exit Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only entry/exit decoupling test.",
        "- Entry surfaces are high-PnL v50/v53/v55; exit surfaces include calibrated v56 variants.",
        "- Live bot untouched.",
        "",
        "## Search",
        "",
        f"- Rows evaluated: {len(summary)}",
        f"- Robust rows: {len(robust)}",
        "",
        "## Selected Rows",
        "",
        "| entry model | exit model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['entry_model']}` | `{row['exit_model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No cross-surface row cleared the robustness gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best row uses `{best['entry_model']}` for entry and `{best['exit_model']}` for exit with "
            f"`{best['exit_policy']}`: all-market fee+1c {v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}, "
            f"min split fee+1c {v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Strict-forward validation is required before promotion.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "summary_rows": int(len(summary)),
                    "robust_rows": int(len(robust)),
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
    ops, metadata = build_all_candidates(ops)
    summary, selected_trades = run_search(rows, ops)
    selected = selected_rows(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, metadata)
    print("v57 cross-surface exit strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best_entry={best['entry_model']} best_exit={best['exit_model']} {best['entry_policy']} "
            f"{best['exit_policy']} min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
