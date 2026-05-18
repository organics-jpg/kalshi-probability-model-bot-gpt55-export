from __future__ import annotations

import csv
import hashlib
import json
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ou_mispricing_strategy_lab as lab


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
DOCS_DIR = ROOT / "docs" / "research"


VARIANTS: dict[str, dict[str, Any]] = {
    "default": {
        "entry_z_min": 4.0,
        "min_raw_edge_cents": 1.5,
        "min_sim_ev_cents": 1.0,
        "max_loss_prob": 0.58,
        "max_spread_cents": 6.0,
    },
    "strict": {
        "entry_z_min": 6.0,
        "min_raw_edge_cents": 3.0,
        "min_sim_ev_cents": 2.0,
        "max_loss_prob": 0.52,
        "max_spread_cents": 4.0,
    },
    "very_strict": {
        "entry_z_min": 8.0,
        "min_raw_edge_cents": 4.0,
        "min_sim_ev_cents": 3.0,
        "max_loss_prob": 0.48,
        "max_spread_cents": 3.0,
    },
}


BASE_SETTINGS: dict[str, Any] = {
    "z_lookback": 400,
    "min_ou_points": 120,
    "min_seconds_to_close": 45.0,
    "max_seconds_to_close": 600.0,
    "sample_seconds": 5.0,
    "pt_values": "3,5,8,12,18,25",
    "sl_values": "4,8,12,20,35,55",
    "hold_values": "30,60,120,240,480",
    "sim_paths": 2000,
    "seed": 14081159,
    "allow_reentry": False,
    "vol_lookback_seconds": 1800.0,
    "min_vol_points": 20,
    "fallback_sigma_per_sqrt_s": 5.0,
    "native_max_spot_age_seconds": 30.0,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_event_files() -> tuple[list[Path], list[dict[str, Any]]]:
    candidates = []
    for root_name in ("logs", "trial_archives"):
        root = ROOT / root_name
        if root.exists():
            candidates.extend(root.rglob("execution_events.ndjson"))
    rows: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    selected: list[Path] = []
    for path in sorted({p.resolve() for p in candidates}, key=lambda p: str(p).lower()):
        size = path.stat().st_size
        file_hash = sha256_file(path)
        duplicate = file_hash in seen_hashes
        if not duplicate:
            seen_hashes.add(file_hash)
            selected.append(path)
        rows.append(
            {
                "path": str(path),
                "bytes": size,
                "mb": round(size / (1024 * 1024), 3),
                "last_write": path.stat().st_mtime,
                "sha256": file_hash,
                "selected": not duplicate,
                "duplicate_by_hash": duplicate,
            }
        )
    return selected, rows


def combine_market_results() -> tuple[Path, dict[str, lab.MarketResult], dict[str, Any]]:
    candidates = []
    for root_name in ("stats", "trial_archives"):
        root = ROOT / root_name
        if root.exists():
            candidates.extend(root.rglob("market_results.csv"))

    by_market: dict[str, dict[str, str]] = {}
    source_counts = Counter()
    conflicts: list[dict[str, str]] = []
    for path in sorted({p.resolve() for p in candidates}, key=lambda p: str(p).lower()):
        try:
            with path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    market = str(row.get("market") or "").strip()
                    result = str(row.get("result") or row.get("market_result") or "").strip().lower()
                    if not market or market.lower() == "none" or result not in {"yes", "no"}:
                        continue
                    normalized = {
                        "market": market,
                        "result": result,
                        "status": str(row.get("status") or ""),
                        "settlement_ts": str(row.get("settlement_ts") or ""),
                        "close_time": str(row.get("close_time") or ""),
                        "watch_close_time": str(row.get("watch_close_time") or ""),
                        "source": str(path),
                    }
                    prior = by_market.get(market)
                    if prior is not None and prior.get("result") != result:
                        conflicts.append(
                            {
                                "market": market,
                                "prior_result": prior.get("result", ""),
                                "new_result": result,
                                "prior_source": prior.get("source", ""),
                                "new_source": str(path),
                            }
                        )
                        continue
                    by_market[market] = normalized
                    source_counts[str(path)] += 1
        except OSError:
            continue

    out_path = REPORT_DIR / "ou_mispricing_all_market_results_combined.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["market", "result", "status", "settlement_ts", "close_time", "watch_close_time", "source"]
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(by_market.values(), key=lambda r: r["market"]):
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    loaded = lab.load_market_results(out_path)
    meta = {
        "source_files": len(set(str(p.resolve()) for p in candidates)),
        "combined_rows": len(by_market),
        "conflict_count": len(conflicts),
        "conflicts_sample": conflicts[:20],
        "top_sources": source_counts.most_common(20),
    }
    return out_path, loaded, meta


def discover_native_files(kind: str) -> list[Path]:
    root = ROOT / "research_data"
    if not root.exists():
        return []
    return sorted(
        [
            path.resolve()
            for path in root.rglob("*.ndjson")
            if "raw_events" in path.parts and f"type={kind}" in path.parts
        ],
        key=lambda path: str(path).lower(),
    )


def discover_spot_tick_files() -> list[Path]:
    root = ROOT / "logs" / "particle_research" / "real_shadow"
    if not root.exists():
        return []
    return sorted(
        {path.resolve() for path in root.rglob("independent_spot_ticks.ndjson")},
        key=lambda path: str(path).lower(),
    )


def load_spot_series(paths: list[Path]) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    rows: list[tuple[float, float]] = []
    source_counts = Counter()
    skipped = Counter()
    for path in paths:
        for _, raw in lab.read_json_lines(path):
            ts = lab.parse_ts(
                raw.get("exchange_ts_utc")
                or raw.get("local_recv_ts_utc")
                or raw.get("exchange_ts")
                or raw.get("local_recv_ts")
                or raw.get("ts_wall")
            )
            price = (
                lab.as_float(raw.get("price"))
                or lab.as_float(raw.get("btc_price"))
                or lab.as_float(raw.get("spot_price"))
                or lab.as_float(raw.get("underlying_price"))
            )
            if ts is None or price is None:
                skipped["missing_ts_or_price"] += 1
                continue
            rows.append((ts.timestamp(), price))
            source_counts[str(path)] += 1
    rows.sort(key=lambda item: item[0])
    return rows, {
        "spot_tick_files": len(paths),
        "spot_tick_rows": len(rows),
        "spot_tick_skips": dict(skipped),
        "top_spot_sources": source_counts.most_common(20),
    }


def spot_at_or_before(
    spot_series: list[tuple[float, float]],
    ts_float: float,
    *,
    max_age_seconds: float,
) -> tuple[float, float] | None:
    if not spot_series:
        return None
    idx = bisect_right(spot_series, (ts_float, float("inf"))) - 1
    if idx < 0:
        return None
    spot_ts, price = spot_series[idx]
    if ts_float - spot_ts > max_age_seconds:
        return None
    return spot_ts, price


def load_native_watch_markets(paths: list[Path]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    source_counts = Counter()
    skipped = Counter()
    conflicts = Counter()
    for path in paths:
        for _, raw in lab.read_json_lines(path):
            payload = lab.extract_payload(raw)
            market = str(payload.get("market") or payload.get("market_ticker") or "").strip()
            strike = lab.as_float(payload.get("strike") or payload.get("mushroom_v28_strike"))
            close_ts = lab.parse_ts(payload.get("close_time") or payload.get("watch_close_time"))
            if not market or strike is None or close_ts is None:
                skipped["missing_market_strike_or_close"] += 1
                continue
            prior = out.get(market)
            if prior is not None:
                if abs(float(prior["strike"]) - strike) > 1e-6:
                    conflicts["strike"] += 1
                if prior["close_ts"] != close_ts:
                    conflicts["close_ts"] += 1
            out[market] = {"strike": float(strike), "close_ts": close_ts}
            source_counts[str(path)] += 1
    return out, {
        "watch_market_files": len(paths),
        "watch_market_rows": sum(source_counts.values()),
        "watch_market_markets": len(out),
        "watch_market_skips": dict(skipped),
        "watch_market_conflicts": dict(conflicts),
        "top_watch_sources": source_counts.most_common(20),
    }


def native_ticker_snapshot(
    raw: dict[str, Any],
    watch_by_market: dict[str, dict[str, Any]],
    spot_series: list[tuple[float, float]],
    *,
    max_spot_age_seconds: float,
) -> tuple[lab.Snapshot | None, str]:
    payload = lab.extract_payload(raw)
    market = str(payload.get("market") or payload.get("market_ticker") or "").strip()
    if not market:
        return None, "missing_market"
    watch = watch_by_market.get(market)
    if watch is None:
        return None, "missing_watch_market"
    ts = lab.parse_ts(payload.get("ts_wall") or payload.get("local_recv_ts") or payload.get("time") or payload.get("exchange_ts"))
    if ts is None:
        return None, "missing_ts"
    close_ts = watch["close_ts"]
    seconds_to_close = max(0.0, (close_ts - ts).total_seconds())
    if seconds_to_close <= 0:
        return None, "after_close"
    spot = spot_at_or_before(
        spot_series,
        ts.timestamp(),
        max_age_seconds=max_spot_age_seconds,
    )
    if spot is None:
        return None, "missing_fresh_spot"

    yes_ask = lab.first_cents(payload, ("derived_yes_ask", "yes_ask", "yes_ask_cents"))
    no_ask = lab.first_cents(payload, ("derived_no_ask", "no_ask", "no_ask_cents"))
    yes_bid = lab.first_cents(payload, ("yes_bid", "yes_bid_cents"))
    no_bid = lab.first_cents(payload, ("no_bid", "no_bid_cents"))
    if yes_bid is None and no_ask is not None:
        yes_bid = max(0.0, min(99.0, 100.0 - float(no_ask)))
    if no_bid is None and yes_ask is not None:
        no_bid = max(0.0, min(99.0, 100.0 - float(yes_ask)))
    if any(value is None for value in (yes_ask, yes_bid, no_ask, no_bid)):
        return None, "missing_book"

    return lab.Snapshot(
        ts=ts,
        market=market,
        strike=float(watch["strike"]),
        btc_price=float(spot[1]),
        close_ts=close_ts,
        seconds_to_close=seconds_to_close,
        yes_ask=float(yes_ask),
        yes_bid=float(yes_bid),
        no_ask=float(no_ask),
        no_bid=float(no_bid),
    ), "ok"


def load_native_snapshots() -> tuple[list[lab.Snapshot], dict[str, Any]]:
    watch_paths = discover_native_files("watch_market")
    ticker_paths = discover_native_files("ticker")
    spot_paths = discover_spot_tick_files()
    spot_series, spot_meta = load_spot_series(spot_paths)
    watch_by_market, watch_meta = load_native_watch_markets(watch_paths)

    rows: list[lab.Snapshot] = []
    source_counts = Counter()
    skipped = Counter()
    max_spot_age_seconds = float(BASE_SETTINGS["native_max_spot_age_seconds"])
    for path in ticker_paths:
        for _, raw in lab.read_json_lines(path):
            snap, reason = native_ticker_snapshot(
                raw,
                watch_by_market,
                spot_series,
                max_spot_age_seconds=max_spot_age_seconds,
            )
            if snap is None:
                skipped[reason] += 1
                continue
            rows.append(snap)
            source_counts[str(path)] += 1
    rows.sort(key=lambda row: (row.ts, row.market))
    meta = {
        **spot_meta,
        **watch_meta,
        "native_ticker_files": len(ticker_paths),
        "native_ticker_rows_used": len(rows),
        "native_ticker_skips": dict(skipped),
        "native_max_spot_age_seconds": max_spot_age_seconds,
        "native_markets": len({row.market for row in rows}),
        "top_native_ticker_sources": source_counts.most_common(20),
    }
    return rows, meta


def dedupe_snapshots(rows: list[lab.Snapshot]) -> tuple[list[lab.Snapshot], int]:
    seen: set[tuple[Any, ...]] = set()
    out: list[lab.Snapshot] = []
    for row in rows:
        key = (
            row.ts,
            row.market,
            round(row.strike, 6),
            round(row.btc_price, 2),
            row.close_ts,
            round(row.yes_ask, 4),
            round(row.yes_bid, 4),
            round(row.no_ask, 4),
            round(row.no_bid, 4),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    out.sort(key=lambda row: (row.ts, row.market))
    return out, len(rows) - len(out)


def summarize_trades(trades: list[dict[str, Any]]) -> dict[str, Any]:
    day: Counter[str] = Counter()
    day_pnl: Counter[str] = Counter()
    side: Counter[str] = Counter()
    side_pnl: Counter[str] = Counter()
    reason: Counter[str] = Counter()
    reason_pnl: Counter[str] = Counter()
    for trade in trades:
        pnl = float(trade.get("net_pnl_dollars") or 0.0)
        day_key = str(trade.get("entry_ts") or "")[:10]
        side_key = str(trade.get("side") or "")
        reason_key = str(trade.get("exit_reason") or "")
        day[day_key] += 1
        day_pnl[day_key] += pnl
        side[side_key] += 1
        side_pnl[side_key] += pnl
        reason[reason_key] += 1
        reason_pnl[reason_key] += pnl
    return {
        "by_day": [
            {"day": key, "trades": day[key], "pnl": round(float(day_pnl[key]), 4)}
            for key in sorted(day)
        ],
        "by_side": [
            {"side": key, "trades": side[key], "pnl": round(float(side_pnl[key]), 4)}
            for key in sorted(side)
        ],
        "by_exit_reason": [
            {"exit_reason": key, "trades": reason[key], "pnl": round(float(reason_pnl[key]), 4)}
            for key in sorted(reason)
        ],
    }


def run_variant(
    name: str,
    settings: dict[str, Any],
    snapshots: list[lab.Snapshot],
    market_results: dict[str, lab.MarketResult],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    merged = {**BASE_SETTINGS, **settings}
    report = lab.run_backtest(
        snapshots,
        market_results,
        z_lookback=int(merged["z_lookback"]),
        min_ou_points=int(merged["min_ou_points"]),
        entry_z_min=float(merged["entry_z_min"]),
        min_raw_edge_cents=float(merged["min_raw_edge_cents"]),
        min_sim_ev_cents=float(merged["min_sim_ev_cents"]),
        max_loss_prob=float(merged["max_loss_prob"]),
        max_spread_cents=float(merged["max_spread_cents"]),
        min_seconds_to_close=float(merged["min_seconds_to_close"]),
        max_seconds_to_close=float(merged["max_seconds_to_close"]),
        sample_seconds=float(merged["sample_seconds"]),
        pt_values=lab.parse_float_list(str(merged["pt_values"])),
        sl_values=lab.parse_float_list(str(merged["sl_values"])),
        hold_values=lab.parse_float_list(str(merged["hold_values"])),
        sim_paths=int(merged["sim_paths"]),
        one_entry_per_market=not bool(merged["allow_reentry"]),
        seed=int(merged["seed"]),
    )
    payload = {
        "generated_utc": utc_now_iso(),
        "variant": name,
        "inputs": inputs,
        "settings": merged,
        **report,
    }
    payload["diagnostics"] = summarize_trades(payload.get("trades") or [])
    lab.write_backtest_outputs(
        payload,
        json_path=REPORT_DIR / f"ou_mispricing_all_market_data_{name}.json",
        md_path=DOCS_DIR / f"OU_MISPRICING_ALL_MARKET_DATA_{name.upper()}.md",
        trades_csv_path=REPORT_DIR / f"ou_mispricing_all_market_data_trades_{name}.csv",
    )
    return payload


def render_verdict(summary: dict[str, Any]) -> str:
    native_meta = summary["inputs"].get("native_meta") or {}
    lines = [
        "# OU Mispricing All-Market-Data Backtest",
        "",
        f"Generated: {summary['generated_utc']}",
        "",
        "Research-only. No live bot logic, state, processes, or orders were changed.",
        "",
        "## Inputs",
        "",
        f"- Selected unique event tapes: {summary['inputs']['selected_event_files']}",
        f"- Duplicate event tapes skipped by exact hash: {summary['inputs']['duplicate_event_files']}",
        f"- Combined market result labels: {summary['inputs']['combined_market_result_rows']}",
        f"- Native spot tick files joined: {native_meta.get('spot_tick_files', 0)}",
        f"- Native spot ticks parsed: {native_meta.get('spot_tick_rows', 0)}",
        f"- Native watch-market files parsed: {native_meta.get('watch_market_files', 0)}",
        f"- Native ticker files parsed: {native_meta.get('native_ticker_files', 0)}",
        f"- Native max prior-spot age: {native_meta.get('native_max_spot_age_seconds', 0.0)} seconds",
        f"- Execution-event snapshots extracted: {summary['inputs']['execution_snapshot_count']}",
        f"- Native passive snapshots joined from research_data: {summary['inputs']['native_snapshot_count']}",
        f"- Exact duplicate snapshots skipped: {summary['inputs']['duplicate_snapshot_count']}",
        f"- Raw snapshots after merge: {summary['inputs']['raw_snapshot_count']}",
        f"- Fair-value snapshots: {summary['inputs']['fair_snapshot_count']}",
        f"- Downsampled snapshots: {summary['inputs']['sampled_snapshot_count']}",
        f"- Markets in sampled snapshots: {summary['inputs']['sampled_markets']}",
        "",
        "## Variant Results",
        "",
        "| Variant | Trades | Net PnL | Win rate | Avg/trade | Markets | Sim decisions |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["variants"]:
        lines.append(
            f"| {row['variant']} | {row['trade_count']} | ${row['net_pnl_dollars']:.2f} | "
            f"{row['win_rate']:.2%} | {row['mean_trade_pnl_dollars'] * 100:.2f}c | "
            f"{row['markets']} | {row['sim_decisions_scored']} |"
        )
    lines.extend(
        [
            "",
            "## Shape Of The PnL",
            "",
            "| Variant | NO trades / PnL | YES trades / PnL |",
            "|---|---:|---:|",
        ]
    )
    for row in summary["variants"]:
        by_side = {item["side"]: item for item in row.get("diagnostics", {}).get("by_side", [])}
        no_row = by_side.get("no", {"trades": 0, "pnl": 0.0})
        yes_row = by_side.get("yes", {"trades": 0, "pnl": 0.0})
        lines.append(
            f"| {row['variant']} | {no_row['trades']} / ${float(no_row['pnl']):.2f} | "
            f"{yes_row['trades']} / ${float(yes_row['pnl']):.2f} |"
        )
    lines.extend(
        [
            "",
            "| Variant | Take-profit | Max-hold | Settlement-after-tape | Stop-loss | Last-bid mark |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summary["variants"]:
        by_reason = {
            item["exit_reason"]: item
            for item in row.get("diagnostics", {}).get("by_exit_reason", [])
        }

        def fmt_reason(name: str) -> str:
            item = by_reason.get(name, {"trades": 0, "pnl": 0.0})
            return f"{item['trades']} / ${float(item['pnl']):.2f}"

        lines.append(
            f"| {row['variant']} | {fmt_reason('take_profit')} | {fmt_reason('max_hold')} | "
            f"{fmt_reason('settlement_after_tape')} | {fmt_reason('stop_loss')} | "
            f"{fmt_reason('last_bid_after_tape')} |"
        )
    very_strict = next((row for row in summary["variants"] if row["variant"] == "very_strict"), None)
    if very_strict is not None:
        day_rows = very_strict.get("diagnostics", {}).get("by_day", [])
        positive_days = sum(1 for row in day_rows if float(row.get("pnl") or 0.0) > 0.0)
        losing_days = [
            f"{row['day']} (${float(row.get('pnl') or 0.0):.2f})"
            for row in day_rows
            if float(row.get("pnl") or 0.0) <= 0.0
        ]
        lines.extend(
            [
                "",
                f"Very-strict daily PnL was positive on {positive_days} of {len(day_rows)} observed dates.",
                "Non-positive dates: " + (", ".join(losing_days) if losing_days else "none") + ".",
                "",
                "## Verdict",
                "",
                "The broader backtest is still net positive after the estimated Kalshi-style entry/exit fee model used by the lab.",
                "The best broad result is `very_strict`: "
                f"{very_strict['trade_count']} one-entry-per-market trades, "
                f"${very_strict['net_pnl_dollars']:.2f} net PnL, and "
                f"{very_strict['mean_trade_pnl_dollars'] * 100:.2f}c average net PnL per trade.",
                "",
                "This is stronger than the narrower execution-event-only run because it adds native passive market data, but it is not clean enough to treat as deployment-ready. Profit is concentrated in NO-side entries and take-profit exits; held-to-time and stop exits are negative. The next test should focus on whether the take-profit behavior survives in forward shadow, and whether max-hold/settlement exits should be filtered or killed earlier.",
            ]
        )
    lines.extend(["", "## Notes", ""])
    lines.extend(summary["notes"])
    return "\n".join(lines) + "\n"


def main() -> None:
    event_paths, event_manifest = discover_event_files()
    combined_results_path, market_results, label_meta = combine_market_results()

    execution_raw = lab.load_snapshots(event_paths, market_results)
    native_raw, native_meta = load_native_snapshots()
    raw, duplicate_snapshot_count = dedupe_snapshots(execution_raw + native_raw)
    enriched = lab.add_fair_values(
        raw,
        vol_lookback_seconds=float(BASE_SETTINGS["vol_lookback_seconds"]),
        min_vol_points=int(BASE_SETTINGS["min_vol_points"]),
        fallback_sigma_per_sqrt_s=float(BASE_SETTINGS["fallback_sigma_per_sqrt_s"]),
    )
    sampled = lab.downsample_snapshots(enriched, sample_seconds=float(BASE_SETTINGS["sample_seconds"]))
    inputs = {
        "event_paths": [str(path) for path in event_paths],
        "event_file_count": len(event_paths),
        "event_manifest": event_manifest,
        "selected_event_files": len(event_paths),
        "duplicate_event_files": sum(1 for row in event_manifest if row["duplicate_by_hash"]),
        "combined_market_results_csv": str(combined_results_path),
        "combined_market_result_rows": len(market_results),
        "label_meta": label_meta,
        "execution_snapshot_count": len(execution_raw),
        "native_snapshot_count": len(native_raw),
        "native_meta": native_meta,
        "duplicate_snapshot_count": duplicate_snapshot_count,
        "raw_snapshot_count": len(raw),
        "fair_snapshot_count": len(enriched),
        "sampled_snapshot_count": len(sampled),
        "sampled_markets": len({row.market for row in sampled}),
    }

    variant_payloads = []
    for name, settings in VARIANTS.items():
        variant_payloads.append(run_variant(name, settings, sampled, market_results, inputs))

    summary = {
        "generated_utc": utc_now_iso(),
        "inputs": inputs,
        "variants": [
            {
                "variant": payload["variant"],
                "trade_count": payload["summary"]["trade_count"],
                "net_pnl_dollars": payload["summary"]["net_pnl_dollars"],
                "win_rate": payload["summary"]["win_rate"],
                "mean_trade_pnl_dollars": payload["summary"]["mean_trade_pnl_dollars"],
                "markets": payload["summary"]["markets"],
                "sim_decisions_scored": payload["summary"]["sim_decisions_scored"],
                "rejects": payload["summary"].get("rejects", {}),
                "exit_reasons": payload["summary"].get("exit_reasons", {}),
                "diagnostics": payload.get("diagnostics", {}),
            }
            for payload in variant_payloads
        ],
        "notes": [
            "This broad run pools locally recorded execution-event tapes plus native passive research_data ticker shards joined to prior independent BTC spot ticks.",
            "Native passive joins use only spot ticks at or before the Kalshi quote timestamp, capped by native_max_spot_age_seconds.",
            "Each variant still uses one-entry-per-market de-duplication.",
            "Exact duplicate execution_events.ndjson files are skipped by SHA-256, but overlapping non-identical logs may still add richer quote history for the same market.",
            "The result is broader retrospective evidence, not forward proof. A fresh pre-registered shadow is still required before live use.",
        ],
    }
    out_json = REPORT_DIR / "ou_mispricing_all_market_data_summary.json"
    out_md = DOCS_DIR / "OU_MISPRICING_ALL_MARKET_DATA_VERDICT.md"
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_verdict(summary), encoding="utf-8")
    print(json.dumps({"summary_json": str(out_json), "summary_md": str(out_md), "variants": summary["variants"]}, indent=2))


if __name__ == "__main__":
    main()
