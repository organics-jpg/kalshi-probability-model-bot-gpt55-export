"""v65 audit: exit-floor scan plus path-instability diagnostics.

Research-only. This tests whether the v55/v57 probability-collapse exit should
be changed after fresh forward losses, and whether adverse path motion exposes a
clean, non-overfit physical regime.

No live bot files, order paths, or processes are touched.
"""
from __future__ import annotations

import json
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
REPORT_MD = OUT_DIR / "v65_exit_floor_path_instability_audit_latest.md"
REPORT_JSON = OUT_DIR / "v65_exit_floor_path_instability_audit_latest.json"
FLOOR_CSV = OUT_DIR / "v65_exit_floor_scan_latest.csv"
PATH_CSV = OUT_DIR / "v65_path_instability_trades_latest.csv"
SLICE_CSV = OUT_DIR / "v65_path_instability_slices_latest.csv"

MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
MODEL_COL = f"{MODEL}_p_yes_candidate"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
BASELINE_FLOOR = 0.52
WINDOWS_SECONDS = [30.0, 60.0, 120.0, 240.0]


def fee_1c_entry_cents(rows: pd.DataFrame) -> pd.Series:
    return (
        pd.to_numeric(rows["pnl_cents"], errors="coerce").fillna(0.0)
        - pd.to_numeric(rows["total_fee_cents"], errors="coerce").fillna(0.0)
        - base.QTY
    )


def settlement_fee_1c_entry_cents(rows: pd.DataFrame) -> pd.Series:
    ask = pd.to_numeric(rows["entry_ask_cents"], errors="coerce").fillna(0.0)
    win = rows["win"].astype(bool)
    settlement_value = np.where(win, 100.0, 0.0)
    entry_fee = pd.to_numeric(rows["entry_fee_cents"], errors="coerce").fillna(0.0)
    return (settlement_value - ask) * base.QTY - entry_fee - base.QTY


def build_base_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str], base.QuotePath], dict[str, set[str]]]:
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, _, _ = v55.build_probability_candidates(ops)
    frame = v42.frame_for_candidate(rows, ops, MODEL_COL)
    best = base.best_side_per_opportunity(frame)
    entries = v42.choose_entries(best, ENTRY)
    paths = base.quote_paths(frame)
    universes = base.market_universes(rows)
    return rows, entries, paths, universes


def exit_floor_scan(
    entries: pd.DataFrame, paths: dict[tuple[str, str], base.QuotePath], universes: dict[str, set[str]]
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for floor in [0.40, 0.45, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.62, 0.65, 0.70, 0.75, 0.80]:
        policy = base.ExitPolicy(
            f"hold15_prob{int(round(floor * 100)):02d}",
            probability_floor=floor,
            min_hold_seconds=15.0,
        )
        trades = base.simulate(entries, paths, policy)
        record = base.flatten_metrics(MODEL, ENTRY, policy, trades, universes)
        record["exit_probability_floor"] = floor
        record["all_fee_1c_entry_dollars"] = record["all_net_after_fees_1c_entry_dollars"]
        record["all_fee_1c_roundtrip_dollars"] = record["all_net_after_fees_1c_roundtrip_dollars"]
        record["min_fee_1c_entry_dollars"] = min(
            record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"]
        )
        record["min_fee_1c_roundtrip_dollars"] = min(
            record[f"{split}_net_after_fees_1c_roundtrip_dollars"] for split in ["train", "validation", "holdout"]
        )
        records.append(record)
    return pd.DataFrame(records)


def first_elapsed(elapsed: np.ndarray, mask: np.ndarray) -> float:
    hits = np.flatnonzero(mask)
    if len(hits) == 0:
        return float("nan")
    return float(elapsed[int(hits[0])])


def path_metrics_for_trade(row: Any, path: base.QuotePath) -> dict[str, Any]:
    entry_dt = pd.Timestamp(row.entry_dt)
    entry_ns = entry_dt.value
    start_idx = int(np.searchsorted(path.entry_ns, entry_ns, side="left"))
    if start_idx >= len(path.entry_ns):
        return {"path_points": 0}

    elapsed = (path.entry_ns[start_idx:] - entry_ns).astype(float) / 1_000_000_000.0
    bid = path.bid_cents[start_idx:].astype(float)
    p_side = path.p_side[start_idx:].astype(float)
    stc = path.seconds_to_close[start_idx:].astype(float)
    valid = elapsed >= 0.0
    elapsed = elapsed[valid]
    bid = bid[valid]
    p_side = p_side[valid]
    stc = stc[valid]
    if len(bid) == 0:
        return {"path_points": 0}

    entry_ask = float(row.entry_ask_cents)
    entry_p = float(row.entry_p_side)
    out: dict[str, Any] = {
        "path_points": int(len(bid)),
        "min_bid_after_entry": float(np.nanmin(bid)),
        "max_bid_after_entry": float(np.nanmax(bid)),
        "min_p_side_after_entry": float(np.nanmin(p_side)),
        "max_p_side_after_entry": float(np.nanmax(p_side)),
        "bid_drawdown_cents": float(entry_ask - np.nanmin(bid)),
        "bid_runup_cents": float(np.nanmax(bid) - entry_ask),
        "p_side_drawdown": float(entry_p - np.nanmin(p_side)),
        "p_side_runup": float(np.nanmax(p_side) - entry_p),
        "first_prob52_elapsed_sec": first_elapsed(elapsed, p_side <= 0.52),
        "first_prob56_elapsed_sec": first_elapsed(elapsed, p_side <= 0.56),
        "first_bid_drop20_elapsed_sec": first_elapsed(elapsed, bid <= entry_ask - 20.0),
        "first_bid_drop40_elapsed_sec": first_elapsed(elapsed, bid <= entry_ask - 40.0),
        "last_path_seconds_to_close": float(stc[-1]),
    }

    for window in WINDOWS_SECONDS:
        mask = elapsed <= window
        label = int(window)
        if not bool(mask.any()):
            out[f"w{label}_min_bid"] = float("nan")
            out[f"w{label}_min_p_side"] = float("nan")
            out[f"w{label}_bid_drawdown_cents"] = float("nan")
            out[f"w{label}_p_side_drawdown"] = float("nan")
            continue
        out[f"w{label}_min_bid"] = float(np.nanmin(bid[mask]))
        out[f"w{label}_min_p_side"] = float(np.nanmin(p_side[mask]))
        out[f"w{label}_bid_drawdown_cents"] = float(entry_ask - np.nanmin(bid[mask]))
        out[f"w{label}_p_side_drawdown"] = float(entry_p - np.nanmin(p_side[mask]))
    return out


def baseline_trades_with_paths(entries: pd.DataFrame, paths: dict[tuple[str, str], base.QuotePath]) -> pd.DataFrame:
    policy = base.ExitPolicy("hold15_prob52", probability_floor=BASELINE_FLOOR, min_hold_seconds=15.0)
    trades = base.simulate(entries, paths, policy)
    if trades.empty:
        return trades
    metrics: list[dict[str, Any]] = []
    for row in trades.itertuples(index=False):
        path = paths.get((str(row.market), str(row.side)))
        if path is None:
            metrics.append({"path_points": 0})
        else:
            metrics.append(path_metrics_for_trade(row, path))
    out = pd.concat([trades.reset_index(drop=True), pd.DataFrame(metrics)], axis=1)
    out["fee_1c_entry_cents"] = fee_1c_entry_cents(out)
    out["settlement_fee_1c_entry_cents"] = settlement_fee_1c_entry_cents(out)
    out["exit_over_hold_cents"] = out["fee_1c_entry_cents"] - out["settlement_fee_1c_entry_cents"]
    return out


def summarize_slice(rows: pd.DataFrame, label: str) -> dict[str, Any]:
    if rows.empty:
        return {
            "slice": label,
            "trades": 0,
            "fee_1c_entry_dollars": 0.0,
            "settlement_fee_1c_entry_dollars": 0.0,
            "exit_over_hold_dollars": 0.0,
            "exits": 0,
            "wins": 0,
            "losses": 0,
            "avg_bid_drawdown": None,
            "avg_p_drawdown": None,
        }
    return {
        "slice": label,
        "trades": int(len(rows)),
        "fee_1c_entry_dollars": float(rows["fee_1c_entry_cents"].sum() / 100.0),
        "settlement_fee_1c_entry_dollars": float(rows["settlement_fee_1c_entry_cents"].sum() / 100.0),
        "exit_over_hold_dollars": float(rows["exit_over_hold_cents"].sum() / 100.0),
        "exits": int((~rows["settled"].astype(bool)).sum()),
        "wins": int(rows["win"].astype(bool).sum()),
        "losses": int((~rows["win"].astype(bool)).sum()),
        "avg_bid_drawdown": float(pd.to_numeric(rows["bid_drawdown_cents"], errors="coerce").mean()),
        "avg_p_drawdown": float(pd.to_numeric(rows["p_side_drawdown"], errors="coerce").mean()),
        "avg_w120_bid_drawdown": float(pd.to_numeric(rows["w120_bid_drawdown_cents"], errors="coerce").mean()),
        "avg_w120_p_drawdown": float(pd.to_numeric(rows["w120_p_side_drawdown"], errors="coerce").mean()),
    }


def path_slices(trades: pd.DataFrame) -> pd.DataFrame:
    side = trades["side"].astype(str)
    ask = pd.to_numeric(trades["entry_ask_cents"], errors="coerce")
    edge = pd.to_numeric(trades["entry_edge_cents"], errors="coerce")
    p_side = pd.to_numeric(trades["entry_p_side"], errors="coerce")
    stc = pd.to_numeric(trades["entry_seconds_to_close"], errors="coerce")
    w120_pdrop = pd.to_numeric(trades["w120_p_side_drawdown"], errors="coerce")
    w120_bdrop = pd.to_numeric(trades["w120_bid_drawdown_cents"], errors="coerce")
    full_pdrop = pd.to_numeric(trades["p_side_drawdown"], errors="coerce")
    full_bdrop = pd.to_numeric(trades["bid_drawdown_cents"], errors="coerce")
    masks = [
        ("all_v57_style", pd.Series(True, index=trades.index)),
        ("YES_entries", side.eq("yes")),
        ("NO_entries", side.eq("no")),
        ("exited_by_prob52", ~trades["settled"].astype(bool)),
        ("settlement_would_lose", ~trades["win"].astype(bool)),
        ("w120_pdrop_ge_20pp", w120_pdrop.ge(0.20)),
        ("w120_pdrop_ge_35pp", w120_pdrop.ge(0.35)),
        ("w120_bid_drop_ge_20c", w120_bdrop.ge(20.0)),
        ("w120_bid_drop_ge_40c", w120_bdrop.ge(40.0)),
        ("full_pdrop_ge_35pp", full_pdrop.ge(0.35)),
        ("full_bid_drop_ge_40c", full_bdrop.ge(40.0)),
        (
            "NO_tail_highask_tinyedge",
            side.eq("no") & ask.ge(95.0) & edge.le(2.0) & p_side.ge(0.95) & stc.between(120.0, 450.0),
        ),
        (
            "NO_tail_highask_tinyedge_w120_pdrop20",
            side.eq("no")
            & ask.ge(95.0)
            & edge.le(2.0)
            & p_side.ge(0.95)
            & stc.between(120.0, 450.0)
            & w120_pdrop.ge(0.20),
        ),
    ]
    return pd.DataFrame([summarize_slice(trades[mask].copy(), label) for label, mask in masks])


def dollars(value: Any) -> str:
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "NA"


def number(value: Any, decimals: int = 2) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return ""
    if not np.isfinite(val):
        return ""
    return f"{val:.{decimals}f}"


def write_report(floors: pd.DataFrame, trades: pd.DataFrame, slices: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    best_all = floors.sort_values(["all_fee_1c_entry_dollars", "min_fee_1c_entry_dollars"], ascending=[False, False]).iloc[0]
    best_min = floors.sort_values(["min_fee_1c_entry_dollars", "all_fee_1c_entry_dollars"], ascending=[False, False]).iloc[0]
    prob52 = floors[floors["exit_probability_floor"].eq(BASELINE_FLOOR)].iloc[0]
    lines = [
        "# v65 Exit-Floor Path-Instability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit for the v55 FV / v57 hold15 probability-collapse exit.",
        "- Tests exit floors without changing entry coverage, then slices adverse path motion.",
        "- Live bot untouched.",
        "",
        "## Exit-Floor Scan",
        "",
        "| floor | all fee+1c entry | all fee+1c roundtrip | min split fee+1c entry | min split fee+1c roundtrip | exits | trades | min cov |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in floors.sort_values("exit_probability_floor").iterrows():
        lines.append(
            f"| {float(row['exit_probability_floor']):.2f} | "
            f"{dollars(row['all_fee_1c_entry_dollars'])} | "
            f"{dollars(row['all_fee_1c_roundtrip_dollars'])} | "
            f"{dollars(row['min_fee_1c_entry_dollars'])} | "
            f"{dollars(row['min_fee_1c_roundtrip_dollars'])} | "
            f"{int(row['all_exit_count'])} | {int(row['all_trades'])} | "
            f"{100.0 * float(row['min_split_coverage']):.2f}% |"
        )
    lines += [
        "",
        "## Path Slices",
        "",
        "| slice | trades | fee+1c entry | hold-to-settle fee+1c | exit over hold | exits | wins | losses | avg full bid dd | avg full p dd | avg 120s bid dd | avg 120s p dd |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in slices.iterrows():
        lines.append(
            f"| `{row['slice']}` | {int(row['trades'])} | "
            f"{dollars(row['fee_1c_entry_dollars'])} | "
            f"{dollars(row['settlement_fee_1c_entry_dollars'])} | "
            f"{dollars(row['exit_over_hold_dollars'])} | "
            f"{int(row['exits'])} | {int(row['wins'])} | {int(row['losses'])} | "
            f"{number(row['avg_bid_drawdown'], 1)} | {number(row['avg_p_drawdown'], 3)} | "
            f"{number(row['avg_w120_bid_drawdown'], 1)} | {number(row['avg_w120_p_drawdown'], 3)} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best all-market exit floor is `{float(best_all['exit_probability_floor']):.2f}` with "
        f"{dollars(best_all['all_fee_1c_entry_dollars'])} all fee+1c entry P&L.",
        f"- Best min-split exit floor is `{float(best_min['exit_probability_floor']):.2f}` with "
        f"{dollars(best_min['min_fee_1c_entry_dollars'])} min-split fee+1c entry P&L.",
        f"- Baseline v57 floor `0.52` remains {dollars(prob52['all_fee_1c_entry_dollars'])} all-market and "
        f"{dollars(prob52['min_fee_1c_entry_dollars'])} min-split fee+1c entry P&L.",
    ]
    if float(best_all["exit_probability_floor"]) == BASELINE_FLOOR:
        lines.append("- The scan does not justify changing the simple v57 probability floor on retrospective data.")
    else:
        lines.append("- The scan found a different all-market floor, but it still needs strict-forward validation.")
    lines.append(
        "- Path-instability slices are diagnostic only: they explain where losses happen, but any rule based on them must keep 75-80% coverage and pass strict-forward validation."
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "model": MODEL,
                    "entry_policy": ENTRY.name,
                    "baseline_floor": BASELINE_FLOOR,
                    "best_all_floor": float(best_all["exit_probability_floor"]),
                    "best_min_floor": float(best_min["exit_probability_floor"]),
                    "floor_scan": json.loads(floors.to_json(orient="records", date_format="iso")),
                    "path_slices": json.loads(slices.to_json(orient="records", date_format="iso")),
                    "trades": int(len(trades)),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    _, entries, paths, universes = build_base_frames()
    floors = exit_floor_scan(entries, paths, universes)
    trades = baseline_trades_with_paths(entries, paths)
    slices = path_slices(trades)
    floors.to_csv(FLOOR_CSV, index=False)
    trades.to_csv(PATH_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    write_report(floors, trades, slices)
    print("v65 exit-floor path-instability audit complete")
    print(f"report={REPORT_MD}")
    print(f"best_all_floor={floors.sort_values('all_fee_1c_entry_dollars', ascending=False).iloc[0]['exit_probability_floor']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
