from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_live_pnl_policy_lab import estimated_taker_fee_cents


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SUMMARY_CSV = OUT_DIR / "threshold_touch_broad_execution_log_backtest_latest.csv"
TRADES_CSV = OUT_DIR / "threshold_touch_broad_execution_log_trades_latest.csv"
SUMMARY_JSON = OUT_DIR / "threshold_touch_broad_execution_log_backtest_latest.json"
SUMMARY_MD = OUT_DIR / "threshold_touch_broad_execution_log_backtest_latest.md"

SUCCESSOR_LABELS = ROOT / "research_particle" / "v28_successor" / "sidecar_bundle_batch_settlement_labels_latest.csv"
SUCCESSOR_LABELED_ROWS = ROOT / "research_particle" / "v28_successor" / "live_pnl_labeled_decisions_latest.csv"

THRESHOLDS = [80.0, 90.0]
ENTRY_MODES = ["strict_cross", "include_left_censored"]
EXIT_GATES = ["hold", "v28_fair_lt_60", "v28_fair_lt_70", "v28_fair_lt_75", "v28_fair_lt_80", "v28_fair_lt_85"]
EPS = 1e-9


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def as_float(value: Any, default: float = math.nan) -> float:
    try:
        if value is None or value == "":
            return default
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def finite(value: float) -> bool:
    return math.isfinite(value) and not math.isnan(value)


def fee(price_cents: float) -> int:
    return estimated_taker_fee_cents(price_cents, count=1)


def fmt(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6f}"
    return str(value)


def add_label(
    labels: dict[str, dict[str, Any]],
    *,
    market: Any,
    result: Any,
    close_time: Any = "",
    settlement_ts: Any = "",
    source: str,
) -> None:
    ticker = str(market or "").strip()
    side = str(result or "").strip().lower()
    if not ticker or ticker.lower() == "nan" or side not in {"yes", "no"}:
        return
    existing = labels.get(ticker)
    close_dt = parse_ts(close_time)
    settlement_dt = parse_ts(settlement_ts)
    if existing is not None:
        if existing["settlement_side"] != side:
            existing.setdefault("label_conflicts", set()).update({existing["settlement_side"], side})
            return
        if close_dt is not None and existing.get("market_close_dt") is None:
            existing["market_close_dt"] = close_dt
        if settlement_dt is not None and existing.get("settlement_dt") is None:
            existing["settlement_dt"] = settlement_dt
        existing["label_sources"].add(source)
        return
    labels[ticker] = {
        "market_ticker": ticker,
        "settlement_side": side,
        "market_close_dt": close_dt,
        "settlement_dt": settlement_dt,
        "label_sources": {source},
    }


def load_labels() -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    if SUCCESSOR_LABELS.exists():
        with SUCCESSOR_LABELS.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                add_label(
                    labels,
                    market=row.get("market_ticker"),
                    result=row.get("binary_result") or ("yes" if str(row.get("y_yes_win")) == "1" else "no" if str(row.get("y_yes_win")) == "0" else ""),
                    settlement_ts=row.get("settlement_ts_utc"),
                    source="v28_successor_settlement_labels",
                )
    if SUCCESSOR_LABELED_ROWS.exists():
        with SUCCESSOR_LABELED_ROWS.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                side = row.get("settlement_side") or ("yes" if str(row.get("y_yes_win")) == "1" else "no" if str(row.get("y_yes_win")) == "0" else "")
                add_label(
                    labels,
                    market=row.get("market_ticker"),
                    result=side,
                    close_time=row.get("market_close_ts_utc"),
                    settlement_ts=row.get("settlement_ts_utc"),
                    source="v28_successor_labeled_decisions",
                )
    for path in ROOT.glob("**/market_results.csv"):
        if "\\.git\\" in str(path):
            continue
        try:
            with path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    add_label(
                        labels,
                        market=row.get("market"),
                        result=row.get("result"),
                        close_time=row.get("close_time"),
                        settlement_ts=row.get("settlement_ts"),
                        source=str(path.relative_to(ROOT)),
                    )
        except OSError:
            continue
    for path in ROOT.glob("**/market_result_cache.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for market, row in data.items():
            if not isinstance(row, dict):
                continue
            add_label(
                labels,
                market=row.get("market") or market,
                result=row.get("result"),
                close_time=row.get("close_time"),
                settlement_ts=row.get("settlement_ts"),
                source=str(path.relative_to(ROOT)),
            )
    return labels


def parse_depth(value: Any) -> float:
    return as_float(value, 0.0)


def event_ts(obj: dict[str, Any]) -> datetime | None:
    for key in ("decision_ts_utc", "ts_wall", "ts", "timestamp", "event_ts", "local_recv_ts"):
        ts = parse_ts(obj.get(key))
        if ts is not None:
            return ts
    return None


def market_from_event(obj: dict[str, Any]) -> str:
    return str(obj.get("market") or obj.get("market_ticker") or obj.get("ticker") or "").strip()


def close_from_event(ts: datetime | None, obj: dict[str, Any]) -> datetime | None:
    explicit = parse_ts(obj.get("market_close_ts_utc") or obj.get("market_close_time") or obj.get("close_time"))
    if explicit is not None:
        return explicit
    seconds = as_float(obj.get("mushroom_v28_seconds_to_close") or obj.get("mushroom_seconds_to_close"))
    if ts is not None and finite(seconds):
        return ts + timedelta(seconds=seconds)
    return None


def side_observation(
    *,
    obj: dict[str, Any],
    path: Path,
    line_no: int,
    ts: datetime,
    market: str,
    side: str,
    ask: float,
    depth: float,
    fair: float,
    close_dt: datetime | None,
) -> dict[str, Any] | None:
    if side not in {"yes", "no"} or not finite(ask) or ask <= 0.0 or ask >= 100.0:
        return None
    return {
        "market_ticker": market,
        "ts": ts,
        "side": side,
        "ask_cents": ask,
        "bid_cents": math.nan,
        "eligible_depth": depth,
        "v28_fair_side_cents": fair,
        "event_type": obj.get("event_type") or "",
        "market_close_dt_from_event": close_dt,
        "source_file": str(path.relative_to(ROOT)),
        "source_line": line_no,
    }


def observations_from_event(obj: dict[str, Any], path: Path, line_no: int) -> list[dict[str, Any]]:
    ts = event_ts(obj)
    market = market_from_event(obj)
    if ts is None or not market:
        return []
    close_dt = close_from_event(ts, obj)
    out: list[dict[str, Any]] = []

    yes_ask = as_float(obj.get("derived_yes_ask") or obj.get("yes_ask_cents") or obj.get("yes_ask"))
    no_ask = as_float(obj.get("derived_no_ask") or obj.get("no_ask_cents") or obj.get("no_ask"))
    if finite(yes_ask):
        out.append(
            side_observation(
                obj=obj,
                path=path,
                line_no=line_no,
                ts=ts,
                market=market,
                side="yes",
                ask=yes_ask,
                depth=parse_depth(obj.get("mushroom_yes_eligible_depth") or obj.get("yes_ask_size") or obj.get("yes_ask_size_fp")),
                fair=as_float(obj.get("mushroom_yes_fair_cents") or obj.get("mushroom_v28_fair_yes_cents")),
                close_dt=close_dt,
            )
        )
    if finite(no_ask):
        out.append(
            side_observation(
                obj=obj,
                path=path,
                line_no=line_no,
                ts=ts,
                market=market,
                side="no",
                ask=no_ask,
                depth=parse_depth(obj.get("mushroom_no_eligible_depth") or obj.get("no_ask_size") or obj.get("no_ask_size_fp")),
                fair=as_float(obj.get("mushroom_no_fair_cents") or obj.get("mushroom_v28_fair_no_cents")),
                close_dt=close_dt,
            )
        )

    row_side = str(obj.get("mushroom_v28_side") or obj.get("mushroom_side") or obj.get("side") or "").strip().lower()
    row_ask = as_float(obj.get("mushroom_v28_ask_cents") or obj.get("mushroom_ask_cents") or obj.get("ask_cents") or obj.get("cap_price_cents"))
    if row_side in {"yes", "no"} and finite(row_ask):
        out.append(
            side_observation(
                obj=obj,
                path=path,
                line_no=line_no,
                ts=ts,
                market=market,
                side=row_side,
                ask=row_ask,
                depth=parse_depth(obj.get("mushroom_v28_eligible_depth") or obj.get("mushroom_eligible_depth") or obj.get("eligible_depth")),
                fair=as_float(
                    obj.get("mushroom_v28_phi_memory_adjusted_fair_side_cents")
                    or obj.get("mushroom_v28_fair_side_cents")
                    or obj.get("mushroom_fair_cents")
                ),
                close_dt=close_dt,
            )
        )

    return [row for row in out if row is not None]


def load_execution_log_observations(labels: dict[str, dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    obs_index: dict[tuple[str, str, str, float], dict[str, Any]] = {}
    files = list(ROOT.glob("logs/**/execution_events.ndjson")) + list(ROOT.glob("trial_archives/**/execution_events.ndjson"))
    event_count = 0
    obs_count = 0
    market_count_before_label = set()
    files_used = 0
    for path in files:
        local_used = False
        try:
            with path.open(encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event_count += 1
                    for obs in observations_from_event(obj, path, line_no):
                        market_count_before_label.add(obs["market_ticker"])
                        if obs["market_ticker"] not in labels:
                            continue
                        key = (obs["market_ticker"], iso_z(obs["ts"]), obs["side"], round(obs["ask_cents"], 4))
                        if key in obs_index:
                            existing = obs_index[key]
                            if obs["eligible_depth"] > existing["eligible_depth"]:
                                existing["eligible_depth"] = obs["eligible_depth"]
                                existing["event_type"] = obs["event_type"]
                                existing["source_file"] = obs["source_file"]
                                existing["source_line"] = obs["source_line"]
                            if not finite(existing["v28_fair_side_cents"]) and finite(obs["v28_fair_side_cents"]):
                                existing["v28_fair_side_cents"] = obs["v28_fair_side_cents"]
                            continue
                        obs_index[key] = obs
                        by_market[obs["market_ticker"]].append(obs)
                        obs_count += 1
                        local_used = True
                        if labels[obs["market_ticker"]].get("market_close_dt") is None and obs["market_close_dt_from_event"] is not None:
                            labels[obs["market_ticker"]]["market_close_dt"] = obs["market_close_dt_from_event"]
        except OSError:
            continue
        if local_used:
            files_used += 1

    # Fill same-timestamp bid from the opposite side's ask when both sides are logged.
    for events in by_market.values():
        opposite_ask: dict[tuple[str, str], float] = {}
        for event in events:
            key = (iso_z(event["ts"]), "no" if event["side"] == "yes" else "yes")
            opposite_ask[(iso_z(event["ts"]), event["side"])] = event["ask_cents"]
            if key in opposite_ask:
                event["bid_cents"] = 100.0 - opposite_ask[key]
        for event in events:
            if finite(event["bid_cents"]):
                continue
            key = (iso_z(event["ts"]), "no" if event["side"] == "yes" else "yes")
            if key in opposite_ask:
                event["bid_cents"] = 100.0 - opposite_ask[key]
        events.sort(key=lambda item: (item["ts"], item["side"], item["ask_cents"]))

    coverage = {
        "execution_log_files_seen": len(files),
        "execution_log_files_used": files_used,
        "execution_events_seen": event_count,
        "side_observations_joined_to_labels": obs_count,
        "markets_seen_before_label_join": len(market_count_before_label),
        "markets_with_joined_log_observations": len(by_market),
    }
    return by_market, coverage


def find_entry(events: list[dict[str, Any]], threshold: float, entry_mode: str, close_dt: datetime | None) -> dict[str, Any] | None:
    seen_below = {"yes": False, "no": False}
    for event in events:
        if close_dt is not None and event["ts"] >= close_dt:
            continue
        side = event["side"]
        ask = event["ask_cents"]
        if ask < threshold:
            seen_below[side] = True
            continue
        if ask < threshold:
            continue
        left_censored = not seen_below[side]
        if entry_mode == "strict_cross" and left_censored:
            continue
        if event["eligible_depth"] <= 0.0:
            # Some older rows have missing depth, but zero-depth rows are not
            # useful as fillability evidence.
            continue
        entry = dict(event)
        entry["entry_left_censored"] = left_censored
        return entry
    return None


def exit_trigger(event: dict[str, Any], gate: str) -> tuple[bool, str]:
    if gate == "hold":
        return False, ""
    fair = event["v28_fair_side_cents"]
    if not finite(fair):
        return False, ""
    limit = float(gate.rsplit("_", 1)[-1])
    if fair < limit:
        return True, f"v28_fair_side_cents={fair:.3f}<{limit:.0f}"
    return False, ""


def find_exit(events: list[dict[str, Any]], entry: dict[str, Any], gate: str, close_dt: datetime | None) -> tuple[dict[str, Any] | None, str]:
    if gate == "hold":
        return None, ""
    for event in events:
        if event["side"] != entry["side"]:
            continue
        if event["ts"] <= entry["ts"]:
            continue
        if close_dt is not None and event["ts"] >= close_dt:
            continue
        hit, reason = exit_trigger(event, gate)
        if not hit:
            continue
        if not finite(event["bid_cents"]):
            continue
        return event, reason
    return None, ""


def trade_pnl(side: str, settlement_side: str, entry_price: float, exit_event: dict[str, Any] | None) -> tuple[float, str, float, int]:
    entry_fee = fee(entry_price)
    if exit_event is not None:
        exit_price = max(0.0, min(100.0, float(exit_event["bid_cents"])))
        exit_fee = fee(exit_price) if exit_price > EPS else 0
        return exit_price - entry_price - entry_fee - exit_fee, "early_exit", exit_price, exit_fee
    if side == settlement_side:
        return 100.0 - entry_price - entry_fee, "settlement_win", 100.0, 0
    return -entry_price - entry_fee, "settlement_loss", 0.0, 0


def summarize(trades: list[dict[str, Any]]) -> dict[str, Any]:
    pnl = [float(t["net_pnl_cents"]) for t in trades]
    if not pnl:
        return {}
    running = peak = max_dd = 0.0
    for value in pnl:
        running += value
        peak = max(peak, running)
        max_dd = max(max_dd, peak - running)
    avg = sum(pnl) / len(pnl)
    if len(pnl) > 1:
        variance = sum((value - avg) ** 2 for value in pnl) / (len(pnl) - 1)
        stderr = math.sqrt(variance / len(pnl))
    else:
        stderr = 0.0
    return {
        "entries": len(trades),
        "wins_if_held": sum(1 for t in trades if t["entry_side"] == t["settlement_side"]),
        "losses_if_held": sum(1 for t in trades if t["entry_side"] != t["settlement_side"]),
        "win_rate_if_held": sum(1 for t in trades if t["entry_side"] == t["settlement_side"]) / len(trades),
        "early_exits": sum(1 for t in trades if t["outcome"] == "early_exit"),
        "early_exited_winners": sum(1 for t in trades if t["outcome"] == "early_exit" and t["entry_side"] == t["settlement_side"]),
        "early_exited_losers": sum(1 for t in trades if t["outcome"] == "early_exit" and t["entry_side"] != t["settlement_side"]),
        "left_censored_entries": sum(1 for t in trades if t["entry_left_censored"]),
        "net_pnl_cents": sum(pnl),
        "avg_pnl_cents": avg,
        "median_pnl_cents": sorted(pnl)[len(pnl) // 2],
        "max_drawdown_cents": max_dd,
        "lcb_avg_pnl_cents": avg - 1.96 * stderr,
    }


def run() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = load_labels()
    by_market, coverage = load_execution_log_observations(labels)
    coverage.update(
        {
            "labels_loaded": len(labels),
            "labels_with_close_time": sum(1 for row in labels.values() if row.get("market_close_dt") is not None),
        }
    )

    summary_rows: list[dict[str, Any]] = []
    all_trades: list[dict[str, Any]] = []
    for threshold in THRESHOLDS:
        for entry_mode in ENTRY_MODES:
            entries: dict[str, dict[str, Any]] = {}
            for market, events in by_market.items():
                close_dt = labels[market].get("market_close_dt")
                if close_dt is None:
                    continue
                entry = find_entry(events, threshold, entry_mode, close_dt)
                if entry is not None:
                    entries[market] = entry
            for gate in EXIT_GATES:
                trades: list[dict[str, Any]] = []
                for market, entry in entries.items():
                    label = labels[market]
                    close_dt = label.get("market_close_dt")
                    exit_event, exit_reason = find_exit(by_market[market], entry, gate, close_dt)
                    pnl, outcome, exit_price, exit_fee = trade_pnl(entry["side"], label["settlement_side"], threshold, exit_event)
                    trade = {
                        "threshold": threshold,
                        "entry_mode": entry_mode,
                        "exit_gate": gate,
                        "market_ticker": market,
                        "entry_side": entry["side"],
                        "settlement_side": label["settlement_side"],
                        "entry_ts_utc": iso_z(entry["ts"]),
                        "market_close_ts_utc": iso_z(close_dt),
                        "entry_seconds_to_close": (close_dt - entry["ts"]).total_seconds() if close_dt is not None else math.nan,
                        "entry_price_cents": threshold,
                        "entry_observed_ask_cents": entry["ask_cents"],
                        "entry_observed_bid_cents": entry["bid_cents"],
                        "entry_observed_depth": entry["eligible_depth"],
                        "entry_v28_fair_side_cents": entry["v28_fair_side_cents"],
                        "entry_left_censored": entry["entry_left_censored"],
                        "entry_fee_cents": fee(threshold),
                        "outcome": outcome,
                        "exit_ts_utc": iso_z(exit_event["ts"]) if exit_event is not None else "",
                        "exit_price_cents": exit_price,
                        "exit_fee_cents": exit_fee,
                        "exit_reason": exit_reason,
                        "net_pnl_cents": pnl,
                        "label_sources": ";".join(sorted(str(s) for s in label["label_sources"])),
                        "entry_event_type": entry["event_type"],
                        "entry_source_file": entry["source_file"],
                        "entry_source_line": entry["source_line"],
                    }
                    trades.append(trade)
                    all_trades.append(trade)
                summary = summarize(trades)
                if summary:
                    summary.update(
                        {
                            "source_tier": "broad_execution_log_derived",
                            "threshold": threshold,
                            "entry_mode": entry_mode,
                            "exit_gate": gate,
                            "markets_with_joined_log_observations": len(by_market),
                            "markets_with_threshold_touch": len(entries),
                        }
                    )
                    summary_rows.append(summary)
    return summary_rows, all_trades, coverage


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fmt(value) for key, value in row.items()})


def write_report(summary_rows: list[dict[str, Any]], coverage: dict[str, Any]) -> None:
    key_rows = [
        row
        for row in summary_rows
        if row["entry_mode"] == "include_left_censored" and row["exit_gate"] in {"hold", "v28_fair_lt_70", "v28_fair_lt_75", "v28_fair_lt_80"}
    ]
    top_rows = sorted(summary_rows, key=lambda row: (row["net_pnl_cents"], row["entries"]), reverse=True)[:20]
    lines = [
        "# Broad Execution-Log Threshold Touch Backtest",
        "",
        "Research-only. This is log-derived historical replay, not live trading and not continuous exchange replay.",
        "",
        f"- Labels loaded: {coverage['labels_loaded']}",
        f"- Labels with close time: {coverage['labels_with_close_time']}",
        f"- Execution log files seen: {coverage['execution_log_files_seen']}",
        f"- Execution log files used: {coverage['execution_log_files_used']}",
        f"- Execution events scanned: {coverage['execution_events_seen']}",
        f"- Side observations joined to labels: {coverage['side_observations_joined_to_labels']}",
        f"- Markets seen before label join: {coverage['markets_seen_before_label_join']}",
        f"- Markets with joined log observations: {coverage['markets_with_joined_log_observations']}",
        "",
        "## Key Include-Left-Censored Rows",
        "| threshold | gate | entries | wins if held | losses if held | exits | exited winners | exited losers | net c | avg c | LCB c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in key_rows:
        lines.append(
            "| {threshold:.0f} | {exit_gate} | {entries} | {wins_if_held} | {losses_if_held} | {early_exits} | "
            "{early_exited_winners} | {early_exited_losers} | {net_pnl_cents:.1f} | {avg_pnl_cents:.2f} | "
            "{lcb_avg_pnl_cents:.2f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Top Configurations",
            "| threshold | mode | gate | entries | wins if held | losses if held | exits | left censored | net c | avg c | LCB c |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in top_rows:
        lines.append(
            "| {threshold:.0f} | {entry_mode} | {exit_gate} | {entries} | {wins_if_held} | {losses_if_held} | {early_exits} | "
            "{left_censored_entries} | {net_pnl_cents:.1f} | {avg_pnl_cents:.2f} | {lcb_avg_pnl_cents:.2f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Correctness Notes",
            "- This tier uses historical bot execution observations, so it is much broader than native raw ticker replay but lower confidence for fillability.",
            "- Entries are still first threshold touches by market, not FV-filtered approvals.",
            "- Exit PnL is only scored when a later log row has both a v28 fair trigger and an inferable same-side bid.",
            "- Treat this as a hypothesis generator; the native replay and future frozen live-forward rows remain the cleaner evidence tiers.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows, trades, coverage = run()
    write_csv(SUMMARY_CSV, summary_rows)
    write_csv(TRADES_CSV, trades)
    SUMMARY_JSON.write_text(json.dumps({"coverage": coverage, "summary": summary_rows}, indent=2, default=str), encoding="utf-8")
    write_report(summary_rows, coverage)
    print(f"labels_loaded={coverage['labels_loaded']}")
    print(f"execution_events={coverage['execution_events_seen']}")
    print(f"markets_with_joined_log_observations={coverage['markets_with_joined_log_observations']}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {TRADES_CSV}")
    print(f"wrote {SUMMARY_MD}")
    print("KEY")
    for row in summary_rows:
        if row["entry_mode"] != "include_left_censored":
            continue
        if row["exit_gate"] not in {"hold", "v28_fair_lt_70", "v28_fair_lt_80"}:
            continue
        print(
            row["threshold"],
            row["exit_gate"],
            "entries",
            row["entries"],
            "wins_if_held",
            row["wins_if_held"],
            "losses_if_held",
            row["losses_if_held"],
            "exits",
            row["early_exits"],
            "net",
            round(row["net_pnl_cents"], 1),
            "avg",
            round(row["avg_pnl_cents"], 2),
            "lcb",
            round(row["lcb_avg_pnl_cents"], 2),
        )


if __name__ == "__main__":
    main()
