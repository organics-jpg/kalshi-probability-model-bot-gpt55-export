"""v58 exit-persistence refinement for the v55 book-anchor FV surface.

Research-only. The most useful current failure mode is a v55/v57 false exit:
the model cut a winning near-boundary NO after one short-lived probability
collapse. This probe keeps v55 entry probability unchanged and tests whether
exit probability must persist for multiple websocket samples or elapsed seconds
before it is treated as thesis decay.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v58_v55_exit_persistence_refine_latest.md"
REPORT_JSON = OUT_DIR / "v58_v55_exit_persistence_refine_latest.json"
SUMMARY_CSV = OUT_DIR / "v58_v55_exit_persistence_refine_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v58_v55_exit_persistence_refine_selected_trades_latest.csv"

MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
MODEL_COL = f"{MODEL}_p_yes_candidate"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)


@dataclass(frozen=True)
class PersistenceExitPolicy:
    name: str
    probability_floor: float | None = None
    min_hold_seconds: float = 0.0
    confirm_count: int = 1
    dwell_seconds: float = 0.0
    recover_probability: float | None = None
    take_profit_cents: float | None = None
    near_margin_abs_sigma15: float | None = None
    near_velocity_abs_3m: float | None = None
    exit_margin_ceiling_sigma15: float | None = None
    exit_held_margin_ceiling_sigma15: float | None = None
    margin_gate_side: str | None = None


@dataclass(frozen=True)
class PhysicsQuotePath:
    entry_ns: np.ndarray
    entry_dt: list[pd.Timestamp]
    bid_cents: np.ndarray
    p_side: np.ndarray
    seconds_to_close: np.ndarray
    held_margin_sigma15: np.ndarray
    held_velocity_3m: np.ndarray
    side_margin_sigma15: np.ndarray
    side_velocity_3m: np.ndarray


def exit_policies() -> list[PersistenceExitPolicy]:
    policies: list[PersistenceExitPolicy] = [PersistenceExitPolicy("hold")]
    for prob in [0.50, 0.52, 0.54, 0.56, 0.58]:
        prob_name = int(prob * 100)
        policies.append(PersistenceExitPolicy(f"prob{prob_name}", probability_floor=prob))
        for hold in [15, 30, 45, 60, 90, 120, 180]:
            policies.append(
                PersistenceExitPolicy(
                    f"hold{hold}_prob{prob_name}",
                    probability_floor=prob,
                    min_hold_seconds=float(hold),
                )
            )
        for confirm in [2, 3]:
            for hold in [0, 15, 30, 60, 90]:
                prefix = "" if hold == 0 else f"hold{hold}_"
                policies.append(
                    PersistenceExitPolicy(
                        f"{prefix}prob{prob_name}_confirm{confirm}",
                        probability_floor=prob,
                        min_hold_seconds=float(hold),
                        confirm_count=confirm,
                    )
                )
        for dwell in [30, 45, 60, 90, 120]:
            for hold in [0, 15, 30, 60]:
                prefix = "" if hold == 0 else f"hold{hold}_"
                policies.append(
                    PersistenceExitPolicy(
                        f"{prefix}prob{prob_name}_dwell{dwell}",
                        probability_floor=prob,
                        min_hold_seconds=float(hold),
                        dwell_seconds=float(dwell),
                    )
                )
        for recover_delta in [0.02, 0.04]:
            recover = min(prob + recover_delta, 0.99)
            for dwell in [30, 60, 90]:
                policies.append(
                    PersistenceExitPolicy(
                        f"prob{prob_name}_dwell{dwell}_recover{int(recover * 100)}",
                        probability_floor=prob,
                        dwell_seconds=float(dwell),
                        recover_probability=recover,
                    )
                )
        for margin in [0.50, 0.75, 1.00, 1.25, 1.50]:
            margin_name = int(margin * 100)
            policies.append(
                PersistenceExitPolicy(
                    f"prob{prob_name}_near{margin_name}_confirm2",
                    probability_floor=prob,
                    confirm_count=2,
                    near_margin_abs_sigma15=margin,
                )
            )
            policies.append(
                PersistenceExitPolicy(
                    f"prob{prob_name}_near{margin_name}_dwell30",
                    probability_floor=prob,
                    dwell_seconds=30.0,
                    near_margin_abs_sigma15=margin,
                )
            )
            for velocity in [0.15, 0.25, 0.50]:
                velocity_name = int(velocity * 100)
                policies.append(
                    PersistenceExitPolicy(
                        f"prob{prob_name}_near{margin_name}_v{velocity_name}_confirm2",
                        probability_floor=prob,
                        confirm_count=2,
                        near_margin_abs_sigma15=margin,
                        near_velocity_abs_3m=velocity,
                    )
                )
        for ceiling in [-0.25, 0.0, 0.10, 0.25, 0.50]:
            ceiling_name = str(ceiling).replace("-", "m").replace(".", "p")
            policies.append(
                PersistenceExitPolicy(
                    f"prob{prob_name}_marginlte{ceiling_name}",
                    probability_floor=prob,
                    exit_margin_ceiling_sigma15=ceiling,
                )
            )
            policies.append(
                PersistenceExitPolicy(
                    f"hold15_prob{prob_name}_marginlte{ceiling_name}",
                    probability_floor=prob,
                    min_hold_seconds=15.0,
                    exit_margin_ceiling_sigma15=ceiling,
                )
            )
            policies.append(
                PersistenceExitPolicy(
                    f"prob{prob_name}_heldmarginlte{ceiling_name}",
                    probability_floor=prob,
                    exit_held_margin_ceiling_sigma15=ceiling,
                )
            )
            for side in ["no", "yes"]:
                policies.append(
                    PersistenceExitPolicy(
                        f"hold15_prob{prob_name}_{side}side_marginlte{ceiling_name}",
                        probability_floor=prob,
                        min_hold_seconds=15.0,
                        exit_margin_ceiling_sigma15=ceiling,
                        margin_gate_side=side,
                    )
                )
                policies.append(
                    PersistenceExitPolicy(
                        f"prob{prob_name}_{side}side_marginlte{ceiling_name}",
                        probability_floor=prob,
                        exit_margin_ceiling_sigma15=ceiling,
                        margin_gate_side=side,
                    )
                )
            policies.append(
                PersistenceExitPolicy(
                    f"hold15_prob{prob_name}_heldmarginlte{ceiling_name}",
                    probability_floor=prob,
                    min_hold_seconds=15.0,
                    exit_held_margin_ceiling_sigma15=ceiling,
                )
            )

    for take in [8, 10, 12, 15]:
        policies.append(PersistenceExitPolicy(f"take{take}", take_profit_cents=float(take)))
        for prob in [0.52, 0.54, 0.56]:
            prob_name = int(prob * 100)
            policies.append(
                PersistenceExitPolicy(
                    f"take{take}_or_prob{prob_name}",
                    probability_floor=prob,
                    take_profit_cents=float(take),
                )
            )
            policies.append(
                PersistenceExitPolicy(
                    f"take{take}_or_prob{prob_name}_confirm2",
                    probability_floor=prob,
                    confirm_count=2,
                    take_profit_cents=float(take),
                )
            )
            policies.append(
                PersistenceExitPolicy(
                    f"take{take}_or_prob{prob_name}_dwell30",
                    probability_floor=prob,
                    dwell_seconds=30.0,
                    take_profit_cents=float(take),
                )
            )
    return policies


def quote_paths(frame: pd.DataFrame) -> dict[tuple[str, str], PhysicsQuotePath]:
    paths: dict[tuple[str, str], PhysicsQuotePath] = {}
    enriched = frame.copy()
    sign = np.where(enriched["side"].astype(str).eq("yes"), 1.0, -1.0)
    enriched["held_margin_sigma15"] = pd.to_numeric(enriched.get("margin_per_rv_sigma_15m"), errors="coerce")
    enriched["held_velocity_3m"] = pd.to_numeric(enriched.get("signed_velocity_dps_3m"), errors="coerce")
    enriched["side_margin_sigma15"] = sign * enriched["held_margin_sigma15"]
    enriched["side_velocity_3m"] = sign * enriched["held_velocity_3m"]
    for key, group in enriched.sort_values(["market", "side", "entry_dt"]).groupby(["market", "side"]):
        clean = group[
            pd.to_numeric(group["bid_cents"], errors="coerce").notna()
            & group["bid_cents"].ge(1.0)
            & pd.to_numeric(group["p_side"], errors="coerce").notna()
        ].copy()
        if clean.empty:
            continue
        paths[(str(key[0]), str(key[1]))] = PhysicsQuotePath(
            entry_ns=clean["entry_dt"].astype("int64").to_numpy(dtype=np.int64),
            entry_dt=list(clean["entry_dt"]),
            bid_cents=clean["bid_cents"].to_numpy(dtype=float),
            p_side=clean["p_side"].to_numpy(dtype=float),
            seconds_to_close=clean["seconds_to_close"].to_numpy(dtype=float),
            held_margin_sigma15=clean["held_margin_sigma15"].to_numpy(dtype=float),
            held_velocity_3m=clean["held_velocity_3m"].to_numpy(dtype=float),
            side_margin_sigma15=clean["side_margin_sigma15"].to_numpy(dtype=float),
            side_velocity_3m=clean["side_velocity_3m"].to_numpy(dtype=float),
        )
    return paths


def conditional_persistence_applies(path: PhysicsQuotePath, idx: int, policy: PersistenceExitPolicy) -> bool:
    if policy.near_margin_abs_sigma15 is None and policy.near_velocity_abs_3m is None:
        return True
    if policy.near_margin_abs_sigma15 is not None:
        margin = float(path.side_margin_sigma15[idx])
        if not np.isfinite(margin) or abs(margin) > policy.near_margin_abs_sigma15:
            return False
    if policy.near_velocity_abs_3m is not None:
        velocity = float(path.side_velocity_3m[idx])
        if not np.isfinite(velocity) or abs(velocity) > policy.near_velocity_abs_3m:
            return False
    return True


def exit_for_entry(entry: Any, path: PhysicsQuotePath, policy: PersistenceExitPolicy) -> dict[str, Any]:
    entry_dt = pd.Timestamp(entry.entry_dt)
    entry_ask = float(entry.ask_cents)
    entry_ns = entry_dt.value
    if policy.min_hold_seconds > 0:
        min_exit_ns = entry_ns + int(policy.min_hold_seconds * 1_000_000_000)
        start_idx = int(np.searchsorted(path.entry_ns, min_exit_ns, side="left"))
    else:
        start_idx = int(np.searchsorted(path.entry_ns, entry_ns, side="right"))

    low_run = 0
    low_start_ns: int | None = None
    recover = policy.recover_probability if policy.recover_probability is not None else policy.probability_floor
    for idx in range(start_idx, len(path.entry_ns)):
        bid = float(path.bid_cents[idx])
        p_side = float(path.p_side[idx])
        triggers: list[str] = []

        if policy.take_profit_cents is not None and bid >= entry_ask + policy.take_profit_cents:
            triggers.append("take_profit")

        if policy.probability_floor is not None:
            if p_side <= policy.probability_floor:
                side_gate_applies = policy.margin_gate_side is None or str(entry.side).lower() == policy.margin_gate_side
                margin_allowed = (
                    not side_gate_applies
                    or (
                    policy.exit_margin_ceiling_sigma15 is None
                    or float(path.side_margin_sigma15[idx]) <= policy.exit_margin_ceiling_sigma15
                    )
                ) and (
                    not side_gate_applies
                    or (
                    policy.exit_held_margin_ceiling_sigma15 is None
                    or float(path.held_margin_sigma15[idx]) <= policy.exit_held_margin_ceiling_sigma15
                    )
                )
                if margin_allowed:
                    low_run += 1
                    if low_start_ns is None:
                        low_start_ns = int(path.entry_ns[idx])
                    dwell_elapsed = (int(path.entry_ns[idx]) - low_start_ns) / 1_000_000_000.0
                    conditional = conditional_persistence_applies(path, idx, policy)
                    required_count = max(1, policy.confirm_count) if conditional else 1
                    required_dwell = policy.dwell_seconds if conditional else 0.0
                    count_ok = low_run >= required_count
                    dwell_ok = required_dwell <= 0.0 or dwell_elapsed >= required_dwell
                    if count_ok and dwell_ok:
                        triggers.append("probability_reduce")
                else:
                    low_run = 0
                    low_start_ns = None
            elif recover is None or p_side >= recover:
                low_run = 0
                low_start_ns = None

        if triggers:
            exit_fair_edge_to_bid = 100.0 * p_side - bid
            return {
                "exit_type": "+".join(triggers),
                "exit_dt": path.entry_dt[idx],
                "exit_seconds_to_close": float(path.seconds_to_close[idx]),
                "exit_bid_cents": bid,
                "exit_p_side": p_side,
                "exit_fair_edge_to_bid_cents": exit_fair_edge_to_bid,
                "exit_confirm_count": int(low_run),
                "exit_dwell_seconds": (
                    float((int(path.entry_ns[idx]) - low_start_ns) / 1_000_000_000.0) if low_start_ns is not None else 0.0
                ),
                "exit_held_margin_sigma15": float(path.held_margin_sigma15[idx]),
                "exit_held_velocity_3m": float(path.held_velocity_3m[idx]),
                "exit_side_margin_sigma15": float(path.side_margin_sigma15[idx]),
                "exit_side_velocity_3m": float(path.side_velocity_3m[idx]),
                "pnl_cents": (bid - entry_ask) * base.QTY,
                "settled": False,
            }

    win = bool(entry.win_bool)
    settlement_value = 100.0 if win else 0.0
    return {
        "exit_type": "settlement_win" if win else "settlement_loss",
        "exit_dt": pd.NaT,
        "exit_seconds_to_close": np.nan,
        "exit_bid_cents": np.nan,
        "exit_p_side": np.nan,
        "exit_fair_edge_to_bid_cents": np.nan,
        "exit_confirm_count": 0,
        "exit_dwell_seconds": np.nan,
        "exit_held_margin_sigma15": np.nan,
        "exit_held_velocity_3m": np.nan,
        "exit_side_margin_sigma15": np.nan,
        "exit_side_velocity_3m": np.nan,
        "pnl_cents": (settlement_value - entry_ask) * base.QTY,
        "settled": True,
    }


def simulate(entries: pd.DataFrame, paths: dict[tuple[str, str], PhysicsQuotePath], policy: PersistenceExitPolicy) -> pd.DataFrame:
    trades: list[dict[str, Any]] = []
    for entry in entries.itertuples(index=False):
        path = paths.get((str(entry.market), str(entry.side)))
        if path is None:
            continue
        exit_info = exit_for_entry(entry, path, policy)
        trade = {
            "model": entry.model,
            "market": entry.market,
            "split": entry.split,
            "entry_dt": entry.entry_dt,
            "side": entry.side,
            "outcome": entry.outcome,
            "win": bool(entry.win_bool),
            "entry_ask_cents": float(entry.ask_cents),
            "entry_bid_cents": float(entry.bid_cents) if pd.notna(entry.bid_cents) else np.nan,
            "entry_p_side": float(entry.p_side),
            "entry_p_yes": float(entry.p_yes),
            "entry_edge_cents": float(entry.entry_edge_cents),
            "entry_seconds_to_close": float(entry.seconds_to_close),
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


def summarize_policy(
    policy: PersistenceExitPolicy,
    trades: pd.DataFrame,
    universes: dict[str, set[str]],
) -> dict[str, Any]:
    record = base.flatten_metrics(MODEL, ENTRY, base.ExitPolicy(policy.name), trades, universes)
    record["probability_floor"] = policy.probability_floor
    record["min_hold_seconds"] = policy.min_hold_seconds
    record["confirm_count"] = policy.confirm_count
    record["dwell_seconds"] = policy.dwell_seconds
    record["recover_probability"] = policy.recover_probability
    record["take_profit_cents"] = policy.take_profit_cents
    record["near_margin_abs_sigma15"] = policy.near_margin_abs_sigma15
    record["near_velocity_abs_3m"] = policy.near_velocity_abs_3m
    record["exit_margin_ceiling_sigma15"] = policy.exit_margin_ceiling_sigma15
    record["exit_held_margin_ceiling_sigma15"] = policy.exit_held_margin_ceiling_sigma15
    record["margin_gate_side"] = policy.margin_gate_side
    record["min_split_net_after_fees_1c_entry_dollars"] = float(
        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["all_splits_1c_entry_positive"] = v42.row_1c_positive(record)
    days = v42.day_metrics(trades)
    record["positive_1c_days"] = days["positive_days"]
    record["total_days"] = days["total_days"]
    record["worst_1c_day_cents"] = days["worst_day_cents"]
    blocks = v42.block_metrics(trades, 10)
    record["block10_positive"] = blocks["positive_blocks"]
    record["block10_worst_cents"] = blocks["worst_cents"]
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
        [
            "all_net_after_fees_1c_entry_dollars",
            "min_split_net_after_fees_1c_entry_dollars",
            "block10_positive",
        ],
        ascending=[False, False, False],
    ).head(50)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, _, _ = v55.build_probability_candidates(ops)
    frame = v42.frame_for_candidate(rows, ops, MODEL_COL)
    best = base.best_side_per_opportunity(frame)
    paths = quote_paths(frame)
    universes = base.market_universes(rows)
    entries = v42.choose_entries(best, ENTRY)

    records: list[dict[str, Any]] = []
    trade_frames: dict[str, pd.DataFrame] = {}
    for policy in exit_policies():
        trades = simulate(entries, paths, policy)
        if trades.empty:
            continue
        records.append(summarize_policy(policy, trades, universes))
        if policy.name in {"prob54", "prob52", "hold15_prob52", "hold60_prob52", "prob52_confirm2", "prob52_dwell30"}:
            trade_frames[policy.name] = trades

    summary = pd.DataFrame(records)
    selected = selected_rows(summary)
    selected_frames: list[pd.DataFrame] = []
    policy_by_name = {policy.name: policy for policy in exit_policies()}
    for _, row in selected.head(12).iterrows():
        name = str(row["exit_policy"])
        trades = trade_frames.get(name)
        if trades is None:
            trades = simulate(entries, paths, policy_by_name[name])
        selected_frames.append(trades.assign(selected_rank=len(selected_frames) + 1))
    selected_trades = pd.concat(selected_frames, ignore_index=True, sort=False) if selected_frames else pd.DataFrame()
    return summary, selected_trades


def baseline_rows(summary: pd.DataFrame) -> pd.DataFrame:
    names = ["prob54", "prob52", "hold15_prob52", "hold60_prob52", "prob52_confirm2", "prob52_dwell30"]
    return summary[summary["exit_policy"].isin(names)].copy()


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy() if not eligible.empty else eligible
    baselines = baseline_rows(summary).sort_values("all_net_after_fees_1c_entry_dollars", ascending=False)
    lines = [
        "# v58 v55 Exit Persistence Refinement",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only exit persistence sweep around `v55_bookanchor_m10_v20_g05_book_plus2`.",
        "- Entry is fixed at `edge0_ask100_p0.65_stc0-600`; FV probability surface is unchanged.",
        "- Tests whether probability-collapse exits need confirmation/dwell before acting.",
        "- `marginlte*` rows are asymmetric YES-axis margin gates; `heldmarginlte*` rows are symmetric held-side margin gates.",
        "- Live bot untouched.",
        "",
        "## Search",
        "",
        f"- Exit policies evaluated: {len(summary)}",
        f"- 80%+ coverage policies: {len(eligible)}",
        f"- Robust policies: {len(robust)}",
        "",
        "## Baselines",
        "",
        "| exit | min cov | min 1c | all 1c | all fee | days | block10 | trades | exits | settled |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in baselines.iterrows():
        lines.append(
            f"| `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} | "
            f"{int(row['all_exit_count'])} | {int(row['all_settled_count'])} |"
        )
    lines += [
        "",
        "## Selected Rows",
        "",
        "| exit | min cov | min 1c | all 1c | all fee | days | block10 | trades | exits | settled |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} | "
            f"{int(row['all_exit_count'])} | {int(row['all_settled_count'])} |"
        )

    lines += ["", "## Read", ""]
    if selected.empty:
        lines.append("- No eligible v58 row was found.")
    else:
        best = selected.iloc[0]
        base_prob54 = summary[summary["exit_policy"].eq("prob54")].iloc[0]
        base_hold15 = summary[summary["exit_policy"].eq("hold15_prob52")].iloc[0]
        lines.append(
            f"- Best v58 row is `{best['exit_policy']}` with all-market fee+1c "
            f"{v42.dollars(best['all_net_after_fees_1c_entry_dollars'])} and min-split fee+1c "
            f"{v42.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
        if "marginlte" in str(best["exit_policy"]) and "heldmarginlte" not in str(best["exit_policy"]):
            lines.append(
                "- This best row is an asymmetric YES-axis market-structure gate, not a symmetric held-side physics law."
            )
        lines.append(
            f"- Delta vs v55 `prob54`: all fee+1c "
            f"{v42.dollars(float(best['all_net_after_fees_1c_entry_dollars']) - float(base_prob54['all_net_after_fees_1c_entry_dollars']))}; "
            f"delta vs v57-style `hold15_prob52`: "
            f"{v42.dollars(float(best['all_net_after_fees_1c_entry_dollars']) - float(base_hold15['all_net_after_fees_1c_entry_dollars']))}."
        )
        lines.append("- Strict-forward shadow validation is still required before promotion.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "summary_rows": int(len(summary)),
                    "eligible_80_rows": int(len(eligible)),
                    "robust_rows": int(len(robust)),
                    "baselines": baselines.to_dict("records"),
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
    summary, selected_trades = build()
    selected = selected_rows(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected)
    print("v58 v55 exit persistence refinement complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['exit_policy']} min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_fee={float(best['all_net_after_fees_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
