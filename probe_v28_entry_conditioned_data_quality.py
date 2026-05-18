"""Data-quality and causality audit for v28 entry-conditioned FV work.

This verifies that the fixed raw-p50 entry slice used by the calibrated FV
diagnostics is sane: one selected row per market, pre-close observations, no
missing prices/probabilities, and no obvious timestamp/settlement leakage.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_entry_conditioned_data_quality_latest.json"
OUT_MD = OUT_DIR / "v28_entry_conditioned_data_quality_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def market_close_guess(market: str) -> datetime | None:
    # Kalshi BTC 15m tickers in this workspace look like
    # KXBTC15M-26MAY051945-45. The middle chunk is YYMONDDHHMM.
    try:
        parts = market.split("-")
        date_part = parts[1]
        yy = int(date_part[:2])
        mon_text = date_part[2:5].upper()
        day = int(date_part[5:7])
        hh = int(date_part[7:9])
        mm = int(date_part[9:11])
    except (IndexError, ValueError):
        return None
    months = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }
    month = months.get(mon_text)
    if month is None:
        return None
    # The ticker close time is local ET. Current session is May, so DST is UTC-4.
    return datetime(2000 + yy, month, day, hh, mm, tzinfo=timezone(timedelta(hours=-4))).astimezone(timezone.utc)


def row_issue_flags(row: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    market = str(row.get("market") or "")
    ts = parse_ts(row.get("ts_wall"))
    close = market_close_guess(market)
    stc = as_float(row.get("seconds_to_close"))
    ask = as_float(row.get("ask_prob"))
    p = as_float(row.get("p_side"))
    raw_edge = as_float(row.get("raw_edge_prob"))
    if ts is None:
        flags.append("missing_or_bad_ts")
    if close is None:
        flags.append("missing_close_guess")
    if ts is not None and close is not None and ts >= close:
        flags.append("ts_not_before_close")
    if stc is not None and stc < 0:
        flags.append("negative_seconds_to_close")
    if ask is None or not (0.01 <= ask <= 0.90):
        flags.append("bad_ask_prob")
    if p is None or not (0.0 < p < 1.0):
        flags.append("bad_raw_probability")
    if raw_edge is None:
        flags.append("missing_raw_edge")
    if row.get("source") not in {"approved_entry", "rejected_actionable"}:
        flags.append("unknown_source")
    if row.get("source") == "rejected_actionable" and row.get("reason") in {None, ""}:
        flags.append("missing_reject_reason")
    return flags


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    markets = [str(row.get("market") or "") for row in picked]
    duplicate_markets = sorted({market for market in markets if markets.count(market) > 1})
    row_checks = []
    for row in picked:
        market = str(row.get("market") or "")
        ts = parse_ts(row.get("ts_wall"))
        close = market_close_guess(market)
        flags = row_issue_flags(row)
        raw_p = as_float(row.get("p_side"))
        plus05 = None if raw_p is None else OVERLAYS["entry_conditioned_plus05_probability"](row)
        row_checks.append({
            "market": market,
            "ts_wall": row.get("ts_wall"),
            "close_guess_utc": close.isoformat() if close else None,
            "seconds_before_close_from_ticker": None if ts is None or close is None else (close - ts).total_seconds(),
            "seconds_to_close_field": row.get("seconds_to_close"),
            "source": row.get("source"),
            "reason": row.get("reason"),
            "side": row.get("side"),
            "p_raw": row.get("p_side"),
            "p_plus05": plus05,
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "flags": flags,
        })
    all_flags = [flag for row in row_checks for flag in row["flags"]]
    return {
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "selected_entries": len(picked),
        "unique_markets": len(set(markets)),
        "duplicate_markets": duplicate_markets,
        "approved_entries": sum(1 for row in picked if row.get("source") == "approved_entry"),
        "shadow_rejected_actionable": sum(1 for row in picked if row.get("source") == "rejected_actionable"),
        "settled_entries": sum(1 for row in picked if row.get("side_won") is not None),
        "rows_with_flags": sum(1 for row in row_checks if row["flags"]),
        "flag_counts": {flag: all_flags.count(flag) for flag in sorted(set(all_flags))},
        "row_checks": row_checks,
        "data_quality_pass": not duplicate_markets and not all_flags,
        "note": "Ticker close parsing is an audit cross-check; seconds_to_close remains the model's native timing field.",
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Entry-Conditioned Data Quality",
        "",
        "Causality and data-quality audit for the raw-p50 fixed entry slice used by calibrated FV diagnostics.",
        "",
        f"- Selected entries: `{report['selected_entries']}`",
        f"- Unique markets: `{report['unique_markets']}`",
        f"- Approved/shadow rows: `{report['approved_entries']}/{report['shadow_rejected_actionable']}`",
        f"- Settled entries: `{report['settled_entries']}`",
        f"- Data-quality pass: `{report['data_quality_pass']}`",
        f"- Duplicate markets: `{report['duplicate_markets']}`",
        f"- Flag counts: `{report['flag_counts']}`",
        "",
        "| market | source | side | p raw | p +5 | ask | stc field | stc ticker | won | net c | flags |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in report["row_checks"]:
        lines.append(
            f"| {row['market']} | {row['source']} | {row['side']} | {fmt(row['p_raw'])} | "
            f"{fmt(row['p_plus05'])} | {fmt(row['ask_prob'])} | {fmt(row['seconds_to_close_field'])} | "
            f"{fmt(row['seconds_before_close_from_ticker'])} | {row['side_won']} | "
            f"{fmt(row['net_gross_cents_after_entry_fee'])} | {', '.join(row['flags']) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
