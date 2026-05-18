"""No-trade-impact live v28 physics shadow validator.

This script is research-only. It reads the live v28 execution/bot logs,
applies a fixed physics-prior shadow rule to every filled entry order, and
writes a separate ledger/report under logs/edge_research.

It does not import, modify, signal, or stop the live bot.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from probe_live_v28_fv_accuracy_volume import (
    BOT_LOG,
    EXECUTION_LOG,
    OUT_DIR,
    as_float,
    as_int,
    first_present,
    iter_json_lines,
    parse_bot_log,
)
from probe_live_9070_v28_replay import fetch_coinbase_btc_1m
from probe_physics_priors_boundary_models import (
    COINBASE_BTC_CACHE,
    add_candle_physics,
    load_coinbase_candles,
)


FIXED_RULE = {
    "rule_id": "adverse15_gt10_v28_cushion_0p5",
    "label": "ask<=100; block 15m adverse>10 unless v28 cushion>0.5",
    "ask_max": 100.0,
    "adverse_feature": "adverse_move_15m",
    "adverse_min": 10.0,
    "cushion_feature": "margin_per_v28_sigma",
    "cushion_min": 0.5,
}
LOCK_PATH = OUT_DIR / "live_v28_physics_shadow_lock.json"
MIN_FRESH_TRADES = 75
MIN_FRESH_CONTRACTS = 150
MIN_TARGET_ACCURACY = 0.95
MIN_RETENTION = 0.75


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, tuple):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def iso_ts(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).isoformat()


def closed_market_outcomes_only(
    markets: Dict[str, Dict[str, Any]],
    outcomes: Dict[str, Dict[str, Any]],
    now: Optional[pd.Timestamp] = None,
) -> Dict[str, Dict[str, Any]]:
    """Keep inferred quote outcomes only after the market close time has passed."""
    now_ts = now if now is not None else pd.Timestamp.now(tz="UTC")
    filtered: Dict[str, Dict[str, Any]] = {}
    for market, outcome in outcomes.items():
        close_time = markets.get(market, {}).get("close_time")
        close_ts = pd.to_datetime(close_time, utc=True, errors="coerce")
        if pd.isna(close_ts) or close_ts <= now_ts:
            filtered[market] = outcome
    return filtered


def grouped_live_entry_fills(path: Path) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, int]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    diagnostics = {
        "raw_entry_fill_events": 0,
        "deduped_entry_orders": 0,
        "skipped_bad_side": 0,
        "skipped_zero_qty": 0,
    }
    for event in iter_json_lines(path):
        if event.get("event_type") not in {"fill_full", "fill_partial"}:
            continue
        client_order_id = str(event.get("client_order_id") or "")
        if not client_order_id.startswith("btc15m-entry"):
            continue
        fill_count = as_int(event.get("fill_count")) or 0
        cumulative = as_int(event.get("cumulative_fill_count")) or 0
        if max(fill_count, cumulative) <= 0:
            diagnostics["skipped_zero_qty"] += 1
            continue
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        if side not in {"yes", "no"}:
            diagnostics["skipped_bad_side"] += 1
            continue
        diagnostics["raw_entry_fill_events"] += 1
        key = str(event.get("order_id") or client_order_id)
        grouped.setdefault(key, []).append(event)
    diagnostics["deduped_entry_orders"] = len(grouped)
    return grouped, diagnostics


def live_entries_dataframe(grouped: Dict[str, List[Dict[str, Any]]], outcomes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for key, events in grouped.items():
        events = sorted(events, key=lambda row: int(row.get("_line_no") or 0))
        source = max(events, key=lambda row: len([name for name in row if str(name).startswith("mushroom")]))
        cumulative_counts = [as_int(row.get("cumulative_fill_count")) for row in events]
        cumulative_counts = [value for value in cumulative_counts if value is not None]
        if cumulative_counts:
            qty = max(cumulative_counts)
        elif len(events) > 1:
            qty = sum(as_int(row.get("fill_count")) or 0 for row in events)
        else:
            qty = as_int(events[-1].get("fill_count")) or 0
        if qty <= 0:
            continue

        market = str(source.get("market") or "")
        side = str(source.get("side") or source.get("mushroom_v28_side") or "").lower()
        ask = as_float(
            first_present(
                source,
                "mushroom_v28_ask_cents",
                "actual_fill_price_cents",
                "trigger_price_cents",
                "top_of_book_limit_cents",
                "cap_price_cents",
            )
        )
        outcome = outcomes.get(market, {}).get("outcome")
        entry_dt = pd.to_datetime(source.get("ts_wall"), utc=True, errors="coerce")
        rows.append(
            {
                "dataset": "current_v28_live_shadow",
                "entry_key": key,
                "entry_dt": entry_dt,
                "market": market,
                "side": side,
                "outcome": outcome,
                "outcome_available": outcome in {"yes", "no"},
                "win": bool(side == outcome) if outcome in {"yes", "no"} else None,
                "qty": int(qty),
                "ask_cents": ask,
                "spot": as_float(source.get("mushroom_v28_btc_price")),
                "strike": as_float(source.get("mushroom_v28_strike")),
                "seconds_to_close": as_float(source.get("mushroom_v28_seconds_to_close")),
                "v28_sigma_t_dollars": as_float(source.get("mushroom_v28_sigma_t_dollars")),
                "v28_p_side": as_float(source.get("mushroom_v28_p_side")),
                "v28_edge_cents": as_float(source.get("mushroom_v28_edge_cents")),
                "source_line_no": source.get("_line_no"),
                "outcome_method": outcomes.get(market, {}).get("method"),
                "outcome_source": outcomes.get(market, {}).get("source"),
            }
        )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.sort_values("entry_dt").reset_index(drop=True)


def shadow_physics_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Build physics fields while preserving unresolved rows."""
    if raw.empty:
        return raw
    out = raw.copy()
    out = out.dropna(subset=["entry_dt", "side", "qty", "spot", "strike", "seconds_to_close"])
    out = out[out["side"].isin(["yes", "no"])].copy()
    out = out[out["qty"] > 0].copy()
    out = out[out["seconds_to_close"] > 0].copy()
    out["side_sign"] = np.where(out["side"] == "yes", 1.0, -1.0)
    out["margin_dollars"] = out["side_sign"] * (out["spot"] - out["strike"])
    out["margin_per_sqrt_sec"] = out["margin_dollars"] / np.sqrt(out["seconds_to_close"])
    out["margin_per_v28_sigma"] = out["margin_dollars"] / out["v28_sigma_t_dollars"]
    z = np.asarray(out["margin_per_v28_sigma"], dtype=float)
    out["brownian_p_v28_sigma"] = 0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2.0)))
    return out.sort_values(["entry_dt", "market", "side"]).reset_index(drop=True)


def create_lock(raw: pd.DataFrame) -> Dict[str, Any]:
    line_no = pd.to_numeric(raw.get("source_line_no"), errors="coerce")
    max_line = int(line_no.max()) if line_no.notna().any() else None
    max_entry_dt = raw["entry_dt"].max() if "entry_dt" in raw.columns and not raw.empty else None
    lock = {
        "lock_id": "live_v28_physics_shadow_lock_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rule_id": FIXED_RULE["rule_id"],
        "rule_label": FIXED_RULE["label"],
        "execution_log": str(EXECUTION_LOG),
        "bot_log": str(BOT_LOG),
        "initial_max_source_line_no": max_line,
        "initial_max_entry_dt": iso_ts(max_entry_dt),
        "purpose": "Out-of-sample boundary for fresh current-v28 physics shadow validation.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


def load_or_create_lock(raw: pd.DataFrame) -> Dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return create_lock(raw)


def mark_fresh_after_lock(df: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    out = df.copy()
    max_line = lock.get("initial_max_source_line_no")
    line_no = pd.to_numeric(out.get("source_line_no"), errors="coerce")
    fresh_by_line = pd.Series(False, index=out.index)
    if max_line is not None and line_no.notna().any():
        fresh_by_line = line_no > int(max_line)
    lock_dt = pd.to_datetime(lock.get("created_utc"), utc=True, errors="coerce")
    fresh_by_time = pd.Series(False, index=out.index)
    if not pd.isna(lock_dt):
        fresh_by_time = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce") > lock_dt
    out["shadow_lock_id"] = lock.get("lock_id")
    out["shadow_lock_created_utc"] = lock.get("created_utc")
    out["fresh_after_lock"] = (fresh_by_line | fresh_by_time).fillna(False)
    return out


def ensure_candles_for_entries(entries: pd.DataFrame, fetch_missing: bool) -> pd.DataFrame:
    if entries.empty:
        return pd.DataFrame()
    candles = load_coinbase_candles(entries, fetch_missing=False)
    if not fetch_missing:
        return candles
    start = entries["entry_dt"].min() - pd.Timedelta(hours=2)
    end = entries["entry_dt"].max() + pd.Timedelta(minutes=5)
    need_fetch = True
    if not candles.empty:
        covered_start = candles["close_dt"].min()
        covered_end = candles["close_dt"].max()
        need_fetch = bool(pd.isna(covered_start) or pd.isna(covered_end) or covered_start > start or covered_end < end)
    if need_fetch:
        fetched = fetch_coinbase_btc_1m(start, end)
        frames = [candles] if not candles.empty else []
        if not fetched.empty:
            frames.append(fetched)
        if frames:
            cache_df = pd.concat(frames, ignore_index=True)
            cache_df["close_dt"] = pd.to_datetime(cache_df["close_dt"], utc=True, errors="coerce")
            cache_df = cache_df.dropna(subset=["close_dt", "open", "high", "low", "close"])
            cache_df = cache_df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
            cache_df.to_parquet(COINBASE_BTC_CACHE, index=False)
            return load_coinbase_candles(entries, fetch_missing=False)
    return candles


def apply_fixed_shadow_rule(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    required = [
        "ask_cents",
        FIXED_RULE["adverse_feature"],
        FIXED_RULE["cushion_feature"],
    ]
    missing_mask = pd.Series(False, index=out.index)
    missing_parts: List[List[str]] = [[] for _ in range(len(out))]
    for feature in required:
        is_missing = out[feature].isna() if feature in out.columns else pd.Series(True, index=out.index)
        missing_mask |= is_missing
        for pos, missing in enumerate(is_missing.to_numpy()):
            if missing:
                missing_parts[pos].append(feature)

    base_ok = out["ask_cents"].notna() & (out["ask_cents"] <= float(FIXED_RULE["ask_max"]))
    adverse = out[FIXED_RULE["adverse_feature"]].fillna(np.inf)
    cushion = out[FIXED_RULE["cushion_feature"]].fillna(-np.inf)
    blocked = (adverse >= float(FIXED_RULE["adverse_min"])) & (cushion <= float(FIXED_RULE["cushion_min"]))
    selected = base_ok & ~blocked & ~missing_mask
    out["shadow_rule_id"] = FIXED_RULE["rule_id"]
    out["shadow_rule_label"] = FIXED_RULE["label"]
    out["shadow_evaluable"] = ~missing_mask
    out["shadow_selected"] = selected
    out["shadow_blocked"] = blocked & ~missing_mask
    out["shadow_reason"] = np.where(
        missing_mask,
        ["missing:" + ",".join(parts) for parts in missing_parts],
        np.where(~base_ok, "ask_above_cap", np.where(blocked, "adverse_drift_without_cushion", "selected")),
    )
    return out


def metrics(df: pd.DataFrame, selected_only: bool) -> Dict[str, Any]:
    resolved = df[df["outcome_available"]].copy()
    if selected_only:
        resolved = resolved[resolved["shadow_selected"]]
    trades = int(len(resolved))
    contracts = int(resolved["qty"].sum()) if not resolved.empty else 0
    wins = resolved[resolved["win"] == True]  # noqa: E712
    trade_wins = int(len(wins))
    contract_wins = int(wins["qty"].sum()) if not wins.empty else 0
    baseline = df[df["outcome_available"]].copy()
    baseline_trades = int(len(baseline))
    baseline_contracts = int(baseline["qty"].sum()) if not baseline.empty else 0
    return {
        "trades": trades,
        "contracts": contracts,
        "trade_wins": trade_wins,
        "contract_wins": contract_wins,
        "trade_accuracy": trade_wins / trades if trades else None,
        "contract_accuracy": contract_wins / contracts if contracts else None,
        "trade_retention": trades / baseline_trades if baseline_trades else None,
        "contract_retention": contracts / baseline_contracts if baseline_contracts else None,
        "baseline_resolved_trades": baseline_trades,
        "baseline_resolved_contracts": baseline_contracts,
    }


def split_metrics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    resolved = df[df["outcome_available"]].copy().sort_values("entry_dt").reset_index(drop=True)
    n = len(resolved)
    train_end = int(math.floor(n * 0.60))
    val_end = int(math.floor(n * 0.80))
    split_names = {
        "train": resolved.iloc[:train_end],
        "validation": resolved.iloc[train_end:val_end],
        "holdout": resolved.iloc[val_end:],
        "all": resolved,
    }
    return {
        name: {
            "baseline": metrics(part, selected_only=False),
            "shadow": metrics(part, selected_only=True),
        }
        for name, part in split_names.items()
    }


def fresh_summary(df: pd.DataFrame) -> Dict[str, Any]:
    fresh = df[df["fresh_after_lock"]].copy() if "fresh_after_lock" in df.columns else df.iloc[0:0].copy()
    base = metrics(fresh, selected_only=False)
    shadow = metrics(fresh, selected_only=True)
    sample_ready = shadow["trades"] >= MIN_FRESH_TRADES and shadow["contracts"] >= MIN_FRESH_CONTRACTS
    accuracy_gate = bool(
        (shadow["trade_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
        and (shadow["contract_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
    )
    retention_gate = bool(
        (shadow["trade_retention"] or 0.0) >= MIN_RETENTION
        and (shadow["contract_retention"] or 0.0) >= MIN_RETENTION
    )
    passes_gate = bool(
        sample_ready
        and accuracy_gate
        and retention_gate
    )
    return {
        "rows": int(len(fresh)),
        "resolved_rows": int(fresh["outcome_available"].sum()) if not fresh.empty else 0,
        "unresolved_rows": int((~fresh["outcome_available"]).sum()) if not fresh.empty else 0,
        "evaluable_rows": int(fresh["shadow_evaluable"].sum()) if not fresh.empty else 0,
        "selected_rows": int(fresh["shadow_selected"].sum()) if not fresh.empty else 0,
        "baseline": base,
        "shadow": shadow,
        "sample_ready": sample_ready,
        "passes_gate": passes_gate,
        "accuracy_gate": accuracy_gate,
        "retention_gate": retention_gate,
        "selected_trade_shortfall": max(0, MIN_FRESH_TRADES - int(shadow["trades"])),
        "selected_contract_shortfall": max(0, MIN_FRESH_CONTRACTS - int(shadow["contracts"])),
        "min_fresh_trades": MIN_FRESH_TRADES,
        "min_fresh_contracts": MIN_FRESH_CONTRACTS,
    }


def write_ledger(df: pd.DataFrame, path: Path) -> None:
    fields = [
        "entry_dt",
        "market",
        "side",
        "outcome",
        "outcome_available",
        "win",
        "qty",
        "ask_cents",
        "spot",
        "strike",
        "seconds_to_close",
        "margin_dollars",
        "margin_per_v28_sigma",
        "signed_move_15m",
        "adverse_move_15m",
        "v28_p_side",
        "v28_edge_cents",
        "shadow_rule_id",
        "shadow_selected",
        "shadow_blocked",
        "shadow_reason",
        "entry_key",
        "source_line_no",
        "shadow_lock_id",
        "fresh_after_lock",
        "outcome_method",
    ]
    present = [field for field in fields if field in df.columns]
    df[present].to_csv(path, index=False)


def write_report(path: Path, generated: str, df: pd.DataFrame, summary: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Live v28 Physics Shadow Validator")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Rule")
    lines.append("")
    lines.append(f"- `{FIXED_RULE['label']}`")
    lines.append("- Research-only shadow rule; no orders are submitted.")
    lines.append(f"- Lock file: `{LOCK_PATH}`")
    if summary.get("lock"):
        lock = summary["lock"]
        lines.append(f"- Fresh evidence starts after source line `{lock.get('initial_max_source_line_no')}` / `{lock.get('created_utc')}`.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Total shadow rows: {len(df)}")
    lines.append(f"- Resolved rows: {int(df['outcome_available'].sum()) if not df.empty else 0}")
    lines.append(f"- Unresolved rows: {int((~df['outcome_available']).sum()) if not df.empty else 0}")
    lines.append(f"- Evaluable rows: {int(df['shadow_evaluable'].sum()) if not df.empty else 0}")
    lines.append(f"- Selected rows: {int(df['shadow_selected'].sum()) if not df.empty else 0}")
    lines.append("")
    fresh = summary["fresh_after_lock"]
    lines.append("## Fresh After Lock")
    lines.append("")
    lines.append(f"- Fresh rows: {fresh['rows']}")
    lines.append(f"- Fresh resolved rows: {fresh['resolved_rows']}")
    lines.append(f"- Fresh unresolved rows: {fresh['unresolved_rows']}")
    lines.append(f"- Fresh selected rows: {fresh['selected_rows']}")
    lines.append(f"- Fresh sample ready: {fresh['sample_ready']}")
    lines.append(f"- Fresh accuracy gate: {fresh['accuracy_gate']}")
    lines.append(f"- Fresh retention gate: {fresh['retention_gate']}")
    lines.append(
        f"- Fresh selected sample shortfall: {fresh['selected_trade_shortfall']} trades / "
        f"{fresh['selected_contract_shortfall']} contracts"
    )
    lines.append("")
    lines.append("| fresh set | baseline contracts | baseline acc | shadow contracts | shadow acc | shadow retention |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    fresh_base = fresh["baseline"]
    fresh_shadow = fresh["shadow"]
    lines.append(
        f"| after lock | {fresh_base['contract_wins']}/{fresh_base['contracts']} | {pct(fresh_base['contract_accuracy'])} | "
        f"{fresh_shadow['contract_wins']}/{fresh_shadow['contracts']} | {pct(fresh_shadow['contract_accuracy'])} | {pct(fresh_shadow['contract_retention'])} |"
    )
    lines.append("")
    lines.append("## Resolved Accuracy")
    lines.append("")
    lines.append("| split | baseline contracts | baseline acc | shadow contracts | shadow acc | shadow retention |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for split in ["all", "train", "validation", "holdout"]:
        base = summary["splits"][split]["baseline"]
        shadow = summary["splits"][split]["shadow"]
        lines.append(
            f"| {split} | {base['contract_wins']}/{base['contracts']} | {pct(base['contract_accuracy'])} | "
            f"{shadow['contract_wins']}/{shadow['contracts']} | {pct(shadow['contract_accuracy'])} | {pct(shadow['contract_retention'])} |"
        )
    lines.append("")
    lines.append("## Completion Read")
    lines.append("")
    all_shadow = summary["splits"]["all"]["shadow"]
    holdout_shadow = summary["splits"]["holdout"]["shadow"]
    if (
        (all_shadow["contract_accuracy"] or 0.0) >= 0.95
        and (all_shadow["contract_retention"] or 0.0) >= 0.75
        and (holdout_shadow["contract_accuracy"] or 0.0) >= 0.95
        and (holdout_shadow["contract_retention"] or 0.0) >= 0.75
    ):
        lines.append("The shadow rule currently satisfies the observed accuracy/retention gate on resolved live v28 fills.")
    else:
        lines.append("The shadow rule does not currently satisfy the observed accuracy/retention gate on resolved live v28 fills.")
    if fresh["passes_gate"]:
        lines.append("The fresh-after-lock sample satisfies the configured accuracy/retention/sample gates.")
    else:
        lines.append("The fresh-after-lock sample does not yet satisfy the configured accuracy/retention/sample gates.")
    lines.append("")
    lines.append("The current v28 resolved holdout is still the limiting evidence source; fresh fills are needed before promotion.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    grouped, diagnostics = grouped_live_entry_fills(EXECUTION_LOG)
    raw = live_entries_dataframe(grouped, outcomes)
    if raw.empty:
        raise SystemExit("No live v28 entry fills found.")

    candles = ensure_candles_for_entries(raw, fetch_missing=bool(args.fetch_btc_candles))
    lock = load_or_create_lock(raw)
    features = shadow_physics_features(raw)
    features = add_candle_physics(features, candles)
    shadow = apply_fixed_shadow_rule(features)
    shadow = mark_fresh_after_lock(shadow, lock)
    summary = {
        "rule": FIXED_RULE,
        "lock": lock,
        "diagnostics": diagnostics,
        "splits": split_metrics(shadow),
        "fresh_after_lock": fresh_summary(shadow),
        "total_rows": int(len(shadow)),
        "resolved_rows": int(shadow["outcome_available"].sum()),
        "unresolved_rows": int((~shadow["outcome_available"]).sum()),
        "evaluable_rows": int(shadow["shadow_evaluable"].sum()),
        "selected_rows": int(shadow["shadow_selected"].sum()),
    }

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    json_latest = OUT_DIR / "live_v28_physics_shadow_latest.json"
    json_stamp = OUT_DIR / f"live_v28_physics_shadow_{generated}.json"
    md_latest = OUT_DIR / "live_v28_physics_shadow_latest.md"
    md_stamp = OUT_DIR / f"live_v28_physics_shadow_{generated}.md"
    csv_latest = OUT_DIR / "live_v28_physics_shadow_latest.csv"
    csv_stamp = OUT_DIR / f"live_v28_physics_shadow_{generated}.csv"
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")
    write_ledger(shadow, csv_latest)
    write_ledger(shadow, csv_stamp)
    write_report(md_latest, generated, shadow, summary)
    write_report(md_stamp, generated, shadow, summary)

    all_shadow = summary["splits"]["all"]["shadow"]
    print("Live v28 physics shadow validation complete")
    print(f"rows={summary['total_rows']} resolved={summary['resolved_rows']} unresolved={summary['unresolved_rows']}")
    print(f"selected={summary['selected_rows']} evaluable={summary['evaluable_rows']}")
    print(
        "fresh_after_lock="
        f"{summary['fresh_after_lock']['selected_rows']} selected / "
        f"{summary['fresh_after_lock']['resolved_rows']} resolved rows "
        f"sample_ready={summary['fresh_after_lock']['sample_ready']}"
    )
    print(
        "shadow_all="
        f"{all_shadow['contract_wins']}/{all_shadow['contracts']} contracts "
        f"acc={all_shadow['contract_accuracy']} retention={all_shadow['contract_retention']}"
    )
    print(f"report={md_latest}")
    print(f"ledger={csv_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
