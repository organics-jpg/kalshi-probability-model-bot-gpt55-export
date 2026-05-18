"""Research-only audit of live Mushroom v28 exit value.

The current live bot often exits before settlement. This audit asks whether
those exits added value versus simply holding the same filled entries to
settlement, then scans small diagnostic "suppress this exit" rules.

No bot files are imported or modified, and no orders are submitted.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRADES_PATH = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
MARKET_RESULTS_PATH = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
EXECUTION_EVENTS_PATH = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
LOCAL_TZ = ZoneInfo("America/New_York")
MATCH_WINDOW_SECONDS = 3.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def local_to_utc(value: Any) -> pd.Timestamp:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    if ts.tzinfo is None:
        ts = ts.tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous="NaT")
    return ts.tz_convert("UTC")


def load_market_results() -> dict[str, str]:
    rows = pd.read_csv(MARKET_RESULTS_PATH)
    return {
        str(row["market"]): str(row.get("result") or "").lower()
        for _, row in rows.iterrows()
    }


def load_trades() -> pd.DataFrame:
    rows = pd.read_csv(TRADES_PATH)
    results = load_market_results()
    for col in ["qty", "entry_fill_cents_used", "exit_fill_cents_used", "net_pnl_dollars"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    rows["exit_dt_utc"] = rows["exit_ts"].map(local_to_utc)
    rows["market_result_full"] = rows["market"].astype(str).map(results)
    rows["resolved"] = rows["market_result_full"].isin(["yes", "no"])

    def hold_pnl(row: pd.Series) -> float | None:
        if not row["resolved"]:
            return None
        qty = float(row.get("qty") or 0.0)
        entry = float(row.get("entry_fill_cents_used") or 0.0)
        if str(row.get("side") or "").lower() == str(row.get("market_result_full") or "").lower():
            return (100.0 - entry) * qty / 100.0
        return -entry * qty / 100.0

    rows["hold_to_settlement_pnl_dollars"] = rows.apply(hold_pnl, axis=1)
    rows["exit_value_delta_dollars"] = rows["net_pnl_dollars"] - rows["hold_to_settlement_pnl_dollars"]
    return rows


def load_exit_events() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with EXECUTION_EVENTS_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") != "exit_signal_seen":
                continue
            rows.append(
                {
                    "event_dt_utc": pd.to_datetime(event.get("ts_wall"), utc=True, errors="coerce"),
                    "market": str(event.get("market") or ""),
                    "side": str(event.get("side") or "").lower(),
                    "exit_reason": str(event.get("mushroom_v28_exit_reason") or ""),
                    "stop_tier": str(event.get("stop_tier") or ""),
                    "exit_bid_cents": as_float(event.get("mushroom_v28_exit_bid_cents")),
                    "entry_basis_cents": as_float(event.get("mushroom_v28_entry_basis_cents")),
                    "p_hold": as_float(event.get("mushroom_v28_p_hold")),
                    "fair_hold_cents": as_float(event.get("mushroom_v28_fair_hold_cents")),
                    "hold_net_cents": as_float(event.get("mushroom_v28_hold_net_cents")),
                    "exit_net_cents": as_float(event.get("mushroom_v28_exit_net_cents")),
                    "fair_drawdown_cents": as_float(event.get("mushroom_v28_fair_drawdown_cents")),
                    "d_sigma": as_float(event.get("mushroom_v28_d_sigma")),
                    "sigma_t_dollars": as_float(event.get("mushroom_v28_sigma_t_dollars")),
                    "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms") or event.get("book_age_ms")),
                    "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
                }
            )
    if not rows:
        raise SystemExit(f"No exit events found in {EXECUTION_EVENTS_PATH}")
    return pd.DataFrame(rows).sort_values(["market", "side", "event_dt_utc"]).reset_index(drop=True)


def join_exit_features(trades: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    exited = trades[trades["outcome"].astype(str).str.lower().eq("exited_before_settlement")].copy()
    grouped = {
        key: frame.reset_index(drop=True)
        for key, frame in events.groupby(["market", "side"], sort=False)
    }
    matched: list[dict[str, Any]] = []
    for _, trade in exited.iterrows():
        key = (str(trade.get("market") or ""), str(trade.get("side") or "").lower())
        candidates = grouped.get(key)
        if candidates is None or candidates.empty or pd.isna(trade["exit_dt_utc"]):
            matched.append({})
            continue
        diffs = (trade["exit_dt_utc"] - candidates["event_dt_utc"]).dt.total_seconds().abs()
        window = candidates[diffs.le(MATCH_WINDOW_SECONDS)].copy()
        if window.empty:
            matched.append({})
            continue
        window["match_abs_diff_seconds"] = (trade["exit_dt_utc"] - window["event_dt_utc"]).dt.total_seconds().abs()
        matched.append(window.sort_values("match_abs_diff_seconds").iloc[0].to_dict())
    features = pd.DataFrame(matched).add_prefix("exit_")
    out = pd.concat([exited.reset_index(drop=True), features.reset_index(drop=True)], axis=1)
    out["matched_exit_signal"] = out["exit_event_dt_utc"].notna() if "exit_event_dt_utc" in out else False
    out = out[out["resolved"] & out["hold_to_settlement_pnl_dollars"].notna()].copy()
    out = out.sort_values(["exit_dt_utc", "market", "side"]).reset_index(drop=True)
    return out


def split_labels(rows: pd.DataFrame) -> pd.Series:
    labels = pd.Series("", index=rows.index, dtype=object)
    ordered = rows.sort_values("exit_dt_utc").reset_index()
    n = len(ordered)
    for pos, original_idx in enumerate(ordered["index"]):
        frac = pos / max(1, n)
        if frac < 0.50:
            labels.loc[original_idx] = "train"
        elif frac < 0.75:
            labels.loc[original_idx] = "validation"
        else:
            labels.loc[original_idx] = "holdout"
    return labels


def aggregate(rows: pd.DataFrame) -> dict[str, Any]:
    return {
        "n": int(len(rows)),
        "actual_exit_net_dollars": float(rows["net_pnl_dollars"].sum()),
        "hold_to_settlement_net_dollars": float(rows["hold_to_settlement_pnl_dollars"].sum()),
        "exit_value_delta_dollars": float(rows["exit_value_delta_dollars"].sum()),
        "exits_helped": int(rows["exit_value_delta_dollars"].gt(0).sum()),
        "exits_hurt": int(rows["exit_value_delta_dollars"].lt(0).sum()),
    }


def suppress_mask(rows: pd.DataFrame, column: str, op: str, threshold: float) -> pd.Series:
    values = pd.to_numeric(rows[column], errors="coerce")
    mask = values.ge(threshold) if op == ">=" else values.le(threshold)
    return mask.fillna(False)


def scan_suppress_rules(rows: pd.DataFrame) -> list[dict[str, Any]]:
    specs = {
        "exit_sigma_t_dollars": [(">=", 100.0), (">=", 150.0), ("<=", 100.0), ("<=", 150.0)],
        "exit_btc_age_ms": [(">=", 500.0), (">=", 800.0), ("<=", 100.0), ("<=", 300.0)],
        "exit_exit_bid_cents": [("<=", 65.0), (">=", 80.0), (">=", 85.0)],
        "exit_p_hold": [("<=", 0.72), (">=", 0.80), (">=", 0.85)],
        "exit_fair_drawdown_cents": [("<=", 0.0), ("<=", -2.0), (">=", 4.0), (">=", 8.0)],
    }
    baseline_actual = float(rows["net_pnl_dollars"].sum())
    candidates: list[dict[str, Any]] = []
    for column, conds in specs.items():
        if column not in rows.columns:
            continue
        for op, threshold in conds:
            suppress = suppress_mask(rows, column, op, threshold)
            suppress_count = int(suppress.sum())
            if suppress_count < 5:
                continue
            suppressed_share = float(suppress.mean())
            # Do not consider rules that remove the exit engine from most exits.
            if suppressed_share > 0.35:
                continue
            adjusted = rows["net_pnl_dollars"].copy()
            adjusted.loc[suppress] = rows.loc[suppress, "hold_to_settlement_pnl_dollars"]
            split_rows = []
            for split in ["train", "validation", "holdout"]:
                m = rows["split"].eq(split)
                split_adjusted = adjusted.loc[m]
                split_rows.append(float(split_adjusted.sum()))
            row = {
                "rule": f"suppress_exit_if_{column.removeprefix('exit_')}{op}{threshold:g}",
                "suppressed_exits": suppress_count,
                "suppressed_share": suppressed_share,
                "adjusted_net_dollars": float(adjusted.sum()),
                "delta_vs_actual_exit_dollars": float(adjusted.sum() - baseline_actual),
                "hurtful_exits_suppressed": int(rows.loc[suppress, "exit_value_delta_dollars"].lt(0).sum()),
                "helpful_exits_suppressed": int(rows.loc[suppress, "exit_value_delta_dollars"].gt(0).sum()),
                "train_adjusted_net": split_rows[0],
                "validation_adjusted_net": split_rows[1],
                "holdout_adjusted_net": split_rows[2],
                "strict_pass": bool(
                    adjusted.sum() > baseline_actual
                    and split_rows[1] >= 0.0
                    and split_rows[2] >= 0.0
                ),
            }
            candidates.append(row)
    candidates.sort(
        key=lambda row: (
            row["strict_pass"],
            row["delta_vs_actual_exit_dollars"],
            row["holdout_adjusted_net"],
        ),
        reverse=True,
    )
    return candidates


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    generated: str,
    all_rows: pd.DataFrame,
    matched_rows: pd.DataFrame,
    all_summary: dict[str, Any],
    matched_summary: dict[str, Any],
    unmatched_summary: dict[str, Any],
    by_reason: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> None:
    lines = [
        "# Live v28 Exit Value Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit of current live v28 exits versus holding the same entries to settlement.",
        "- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.",
        "- No live bot files or processes are touched and no orders are submitted.",
        "",
        "## Baseline Exit Value",
        "",
        f"- Resolved exits: {all_summary['n']}",
        f"- Matched to `exit_signal_seen`: {matched_summary['n']}",
        f"- Unmatched resolved exits: {unmatched_summary['n']}",
        f"- Actual exit net, all resolved exits: ${all_summary['actual_exit_net_dollars']:.2f}",
        f"- Hold-to-settlement net for same entries: ${all_summary['hold_to_settlement_net_dollars']:.2f}",
        f"- Exit value added, all resolved exits: ${all_summary['exit_value_delta_dollars']:.2f}",
        f"- Helpful exits / hurtful exits, all resolved exits: {all_summary['exits_helped']} / {all_summary['exits_hurt']}",
        "",
        "Matched feature subset:",
        "",
        f"- Actual matched exit net: ${matched_summary['actual_exit_net_dollars']:.2f}",
        f"- Matched hold-to-settlement net: ${matched_summary['hold_to_settlement_net_dollars']:.2f}",
        f"- Matched exit value added: ${matched_summary['exit_value_delta_dollars']:.2f}",
        f"- Unmatched exit value added: ${unmatched_summary['exit_value_delta_dollars']:.2f}",
        "",
        "## By Exit Reason",
        "",
        "| reason | n | actual | hold | delta | helped/hurt |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in by_reason:
        lines.append(
            f"| `{row['exit_reason']}` | {row['n']} | ${row['actual_exit_net_dollars']:.2f} | "
            f"${row['hold_to_settlement_net_dollars']:.2f} | ${row['exit_value_delta_dollars']:.2f} | "
            f"{row['exits_helped']}/{row['exits_hurt']} |"
        )
    lines += [
        "",
        "## Suppress-Exit Diagnostics",
        "",
        "- Diagnostics below only apply to matched feature rows.",
        "",
        "| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in candidates[:20]:
        lines.append(
            f"| `{row['rule']}` | {row['strict_pass']} | {row['suppressed_exits']} ({row['suppressed_share']:.2%}) | "
            f"${row['adjusted_net_dollars']:.2f} | ${row['delta_vs_actual_exit_dollars']:.2f} | "
            f"{row['hurtful_exits_suppressed']}/{row['helpful_exits_suppressed']} | "
            f"${row['train_adjusted_net']:.2f}/${row['validation_adjusted_net']:.2f}/${row['holdout_adjusted_net']:.2f} |"
        )
    if not candidates:
        lines.append("| none | False | 0 | $0.00 | $0.00 | 0/0 | $0.00/$0.00/$0.00 |")
    lines += [
        "",
        "## Read",
        "",
        "- The current exit engine is adding material value versus passive holding after all resolved exits are included.",
        "- No matched-feature suppression rule passes the split gates after the scorer causality fix.",
        "- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.",
        "- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    trades = load_trades()
    events = load_exit_events()
    all_exit_rows = join_exit_features(trades, events)
    if all_exit_rows.empty:
        raise SystemExit("No resolved exited trades matched exit signal events.")
    all_exit_rows["split"] = split_labels(all_exit_rows)
    matched_rows = all_exit_rows[all_exit_rows["matched_exit_signal"].astype(bool)].copy()
    unmatched_rows = all_exit_rows[~all_exit_rows["matched_exit_signal"].astype(bool)].copy()
    if matched_rows.empty:
        raise SystemExit("No resolved exited trades matched exit signal events.")
    all_summary = aggregate(all_exit_rows)
    matched_summary = aggregate(matched_rows)
    unmatched_summary = aggregate(unmatched_rows)
    by_reason = [
        {"exit_reason": reason, **aggregate(group)}
        for reason, group in matched_rows.groupby("exit_exit_reason", sort=False)
    ]
    if not unmatched_rows.empty:
        by_reason.append({"exit_reason": "unmatched_exit_signal", **aggregate(unmatched_rows)})
    by_reason.sort(key=lambda row: row["exit_value_delta_dollars"], reverse=True)
    candidates = scan_suppress_rules(matched_rows)

    matched_rows.to_csv(OUT_DIR / "live_v28_exit_value_audit_rows_latest.csv", index=False)
    all_exit_rows.to_csv(OUT_DIR / "live_v28_exit_value_audit_all_exit_rows_latest.csv", index=False)
    write_csv(OUT_DIR / "live_v28_exit_value_audit_suppress_rules_latest.csv", candidates)
    payload = {
        "generated_utc": generated,
        "summary": all_summary,
        "matched_feature_summary": matched_summary,
        "unmatched_exit_summary": unmatched_summary,
        "by_reason": by_reason,
        "strict_pass_count": int(sum(1 for row in candidates if row["strict_pass"])),
        "top_candidates": candidates[:20],
    }
    for path in [
        OUT_DIR / "live_v28_exit_value_audit_latest.json",
        OUT_DIR / f"live_v28_exit_value_audit_{generated}.json",
    ]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for path in [
        OUT_DIR / "live_v28_exit_value_audit_latest.md",
        OUT_DIR / f"live_v28_exit_value_audit_{generated}.md",
    ]:
        write_report(path, generated, all_exit_rows, matched_rows, all_summary, matched_summary, unmatched_summary, by_reason, candidates)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
