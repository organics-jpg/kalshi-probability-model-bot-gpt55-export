"""v72 v55 entry / hybrid v55-v66 exit strategy probe.

Research-only. Tests whether v70's robustness can be targeted to the NO-side
book-gap state while keeping v60's stronger v55-exit P&L elsewhere.

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
import probe_v70_v55_entry_v66_margin_exit_strategy as v70
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v72_v55_entry_hybrid_exit_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v72_v55_entry_hybrid_exit_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v72_v55_entry_hybrid_exit_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v72_v55_entry_hybrid_exit_strategy_trades_latest.csv"

ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
ENTRY_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
ENTRY_COL = f"{ENTRY_MODEL}_p_yes_candidate"
V66_MODEL = "v66_no_bookgap_g08_blend75"
V66_COL = f"{V66_MODEL}_p_yes_candidate"

SURFACE_MODES = [
    "all_v55",
    "all_v66",
    "yes_v55_no_v66",
    "yes_v66_no_v55",
    "no_gap05_v66_else_v55",
    "no_gap08_v66_else_v55",
    "no_gap10_v66_else_v55",
]


def choose_surface(entry: Any, mode: str) -> str:
    side = str(entry.side).lower()
    if mode == "all_v55":
        return "v55"
    if mode == "all_v66":
        return "v66"
    if mode == "yes_v55_no_v66":
        return "v55" if side == "yes" else "v66"
    if mode == "yes_v66_no_v55":
        return "v66" if side == "yes" else "v55"
    if mode.startswith("no_gap"):
        threshold_text = mode.split("_", 2)[1].replace("gap", "")
        threshold = float(threshold_text) / 100.0
        gap = getattr(entry, "v66_model_book_gap", None)
        try:
            gap_value = float(gap)
        except (TypeError, ValueError):
            gap_value = float("nan")
        if side == "no" and pd.notna(gap_value) and gap_value >= threshold:
            return "v66"
        return "v55"
    raise ValueError(f"unknown surface mode: {mode}")


def simulate_hybrid(
    entries: pd.DataFrame,
    paths_by_surface: dict[str, dict[tuple[str, str], v58.PhysicsQuotePath]],
    policy: v58.PersistenceExitPolicy,
    surface_mode: str,
) -> pd.DataFrame:
    trades: list[dict[str, Any]] = []
    for entry in entries.itertuples(index=False):
        surface = choose_surface(entry, surface_mode)
        path = paths_by_surface[surface].get((str(entry.market), str(entry.side)))
        if path is None:
            continue
        exit_info = v58.exit_for_entry(entry, path, policy)
        trade = {
            "model": f"v55_entry__{surface_mode}_exit",
            "market": entry.market,
            "split": entry.split,
            "entry_dt": entry.entry_dt,
            "side": entry.side,
            "outcome": entry.outcome,
            "win": bool(entry.win_bool),
            "entry_ask_cents": float(entry.ask_cents),
            "entry_bid_cents": float(entry.bid_cents) if pd.notna(entry.bid_cents) else float("nan"),
            "entry_p_side": float(entry.p_side),
            "entry_p_yes": float(entry.p_yes),
            "entry_edge_cents": float(entry.entry_edge_cents),
            "entry_seconds_to_close": float(entry.seconds_to_close),
            "entry_exit_surface": surface,
            "entry_v66_model_book_gap": float(getattr(entry, "v66_model_book_gap", float("nan"))),
            **exit_info,
        }
        trade["cost_cents"] = float(entry.ask_cents) * base.QTY
        trade["entry_fee_cents"] = base.estimate_kalshi_fee_cents(entry.ask_cents)
        trade["exit_fee_cents"] = (
            base.estimate_kalshi_fee_cents(trade["exit_bid_cents"])
            if not bool(trade["settled"]) and pd.notna(trade["exit_bid_cents"])
            else 0.0
        )
        trade["total_fee_cents"] = trade["entry_fee_cents"] + trade["exit_fee_cents"]
        trade["exit_policy"] = policy.name
        trades.append(trade)
    return pd.DataFrame(trades)


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
        ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars", "block10_positive"],
        ascending=[False, False, False],
    ).head(40)


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
    context_cols = ["opportunity_key", "v66_selected_side", "v66_model_book_gap", "v66_selected_book_p_side"]
    context = v66_ops[[col for col in context_cols if col in v66_ops.columns]].drop_duplicates("opportunity_key")
    entries = entries.merge(context, on="opportunity_key", how="left")

    paths_by_surface = {
        "v55": v58.quote_paths(v42.frame_for_candidate(rows, v55_ops, ENTRY_COL)),
        "v66": v58.quote_paths(v42.frame_for_candidate(rows, v66_ops, V66_COL)),
    }
    policies = v70.exit_policies()
    records: list[dict[str, Any]] = []
    trades_by_key: dict[tuple[str, str], pd.DataFrame] = {}
    for mode in SURFACE_MODES:
        for policy in policies:
            trades = simulate_hybrid(entries, paths_by_surface, policy, mode)
            if trades.empty:
                continue
            record = v70.summarize(f"v55_entry__{mode}_exit", mode, policy, trades, universes)
            record["exit_surface_mode"] = mode
            records.append(record)
            trades_by_key[(mode, policy.name)] = trades.assign(candidate=f"v55_entry__{mode}_exit", surface_mode=mode)

    summary = pd.DataFrame(records)
    selected = selected_rows(summary)
    selected_frames: list[pd.DataFrame] = []
    for _, row in selected.head(12).iterrows():
        frame = trades_by_key.get((str(row["exit_surface_mode"]), str(row["exit_policy"])))
        if frame is not None:
            selected_frames.append(frame.assign(selected_rank=len(selected_frames) + 1))
    trades = pd.concat(selected_frames, ignore_index=True, sort=False) if selected_frames else pd.DataFrame()
    return summary, trades


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    robust = robust_rows(summary)
    lines = [
        "# v72 v55 Entry / Hybrid Exit Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only hybrid exit-surface test.",
        "- Entry universe is fixed to v55 `edge0_ask100_p0.65_stc0-600`.",
        "- Tests whether v66 exits should apply only to NO-side book-gap states.",
        "- Live bot untouched.",
        "",
        "## Selected Rows",
        "",
        "| surface mode | exit policy | min cov | min 1c | all 1c | all fee | days | block10 | exits | trades |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"| `{row['exit_surface_mode']}` | `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_exit_count'])} | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No v72 row cleared the robustness screen.")
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
            f"- Best all-market robust v72 row is `{best_all['exit_surface_mode']}` / `{best_all['exit_policy']}` "
            f"with all fee+1c {v42.dollars(best_all['all_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append(
            f"- Best min-split robust v72 row is `{best_min['exit_surface_mode']}` / `{best_min['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best_min['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Compare to v60 all/min fee+1c $21.26/$0.87 and v70 balanced $14.40/$2.17.")
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
    print("v72 v55 entry / hybrid exit strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['exit_surface_mode']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
