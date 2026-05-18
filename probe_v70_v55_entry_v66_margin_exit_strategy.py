"""v70 v55 entry / v66 margin-exit strategy probe.

Research-only. Tests whether the profitable v60 margin-gated exit family is
more stable when the exit probability comes from the better-calibrated v66
balanced FV surface while entries stay on the broad v55 universe.

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
import probe_v66_no_bookgap_fv_strategy as v66
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v70_v55_entry_v66_margin_exit_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v70_v55_entry_v66_margin_exit_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v70_v55_entry_v66_margin_exit_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v70_v55_entry_v66_margin_exit_strategy_trades_latest.csv"

ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
ENTRY_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
ENTRY_COL = f"{ENTRY_MODEL}_p_yes_candidate"
EXIT_SURFACES = {
    "v55": ("v55_bookanchor_m10_v20_g05_book_plus2", "v55_bookanchor_m10_v20_g05_book_plus2_p_yes_candidate"),
    "v66_bal": ("v66_no_bookgap_g08_blend75", "v66_no_bookgap_g08_blend75_p_yes_candidate"),
}
PROB_FLOORS = [0.50, 0.52, 0.54, 0.56]
MARGIN_CEILINGS = [-0.25, 0.0, 0.25, 0.50]
GATE_SIDES: list[str | None] = [None, "no", "yes"]


def policy_name(prob: float, side: str | None, ceiling: float | None) -> str:
    prob_name = int(round(prob * 100))
    if ceiling is None:
        return f"hold15_prob{prob_name}"
    ceiling_name = str(ceiling).replace("-", "m").replace(".", "p")
    if side is None:
        return f"hold15_prob{prob_name}_marginlte{ceiling_name}"
    return f"hold15_prob{prob_name}_{side}side_marginlte{ceiling_name}"


def exit_policies() -> list[v58.PersistenceExitPolicy]:
    policies: list[v58.PersistenceExitPolicy] = []
    for prob in PROB_FLOORS:
        policies.append(
            v58.PersistenceExitPolicy(
                policy_name(prob, None, None),
                probability_floor=prob,
                min_hold_seconds=15.0,
            )
        )
        for ceiling in MARGIN_CEILINGS:
            for side in GATE_SIDES:
                policies.append(
                    v58.PersistenceExitPolicy(
                        policy_name(prob, side, ceiling),
                        probability_floor=prob,
                        min_hold_seconds=15.0,
                        exit_margin_ceiling_sigma15=ceiling,
                        margin_gate_side=side,
                    )
                )
    return policies


def min_entry_1c(record: dict[str, Any]) -> float:
    return float(min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"]))


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
    record["min_split_net_after_fees_1c_entry_dollars"] = min_entry_1c(record)
    record["all_splits_1c_entry_positive"] = v42.row_1c_positive(record)
    days = v42.day_metrics(trades)
    blocks = v42.block_metrics(trades, 10)
    record["positive_1c_days"] = days["positive_days"]
    record["total_days"] = days["total_days"]
    record["worst_1c_day_cents"] = days["worst_day_cents"]
    record["block10_positive"] = blocks["positive_blocks"]
    record["block10_worst_cents"] = blocks["worst_cents"]
    return record


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
    ).head(30)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = v47.load_rows()
    base_ops = v42.opportunity_table(rows)
    v55_ops, _, _ = v55.build_probability_candidates(base_ops.copy())
    v66_ops, _, _ = v66.build_probability_candidates(base_ops.copy())
    universes = base.market_universes(rows)

    entry_frame = v42.frame_for_candidate(rows, v55_ops, ENTRY_COL)
    best = base.best_side_per_opportunity(entry_frame)
    entries = v42.choose_entries(best, ENTRY)
    if entries.empty:
        return pd.DataFrame(), pd.DataFrame()

    surface_ops = {"v55": v55_ops, "v66_bal": v66_ops}
    records: list[dict[str, Any]] = []
    trades_by_key: dict[tuple[str, str], pd.DataFrame] = {}
    policies = exit_policies()
    for exit_surface, (exit_model, exit_col) in EXIT_SURFACES.items():
        exit_frame = v42.frame_for_candidate(rows, surface_ops[exit_surface], exit_col)
        paths = v58.quote_paths(exit_frame)
        for policy in policies:
            trades = v58.simulate(entries, paths, policy)
            if trades.empty:
                continue
            model = f"v55_entry__{exit_surface}_margin_exit"
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
    return summary, trades


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    robust = robust_rows(summary)
    lines = [
        "# v70 v55 Entry / v66 Margin Exit Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only cross-surface exit test.",
        "- Entry universe is fixed to v55 `edge0_ask100_p0.65_stc0-600`.",
        "- Exit tests the v60 margin-gated policy family on v55 and v66 balanced probability paths.",
        "- Live bot untouched.",
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
        lines.append("- No v70 row cleared the 80% coverage, split-positive, all-day, block-stability robustness screen.")
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
            f"- Best all-market robust v70 row is `{best_all['exit_surface']}` / `{best_all['exit_policy']}` "
            f"with all fee+1c {v42.dollars(best_all['all_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append(
            f"- Best min-split robust v70 row is `{best_min['exit_surface']}` / `{best_min['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best_min['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Compare to v60 all fee+1c $21.26 and v69 min split fee+1c $2.17 before promotion.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
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
    summary, trades = build()
    selected = selected_rows(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not trades.empty:
        trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected)
    print("v70 v55 entry / v66 margin exit strategy complete")
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
