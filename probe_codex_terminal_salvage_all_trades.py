from __future__ import annotations

import argparse
import gzip
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from probe_codex_terminal_path_edges import seconds_to_close, sim_terminal_window_salvage
from probe_stop_touch_confirmation import (
    EDGE_DIR,
    ET,
    HEARTBEAT_RE,
    UTC,
    estimated_order_fee_cents,
    exit_pnl,
    first_present,
    parse_float,
    parse_log_ts,
    summarize_rows,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_PARAMS = {
    "held_ask_max": 45,
    "final_window_seconds": 60,
    "min_remaining_seconds": 15,
}


def discover_datasets() -> list[str]:
    datasets: list[str] = []
    for trades_path in sorted((ROOT / "stats").glob("*/trades.csv")):
        dataset = trades_path.parent.name
        if not (trades_path.parent / "market_results.csv").exists():
            continue
        if not (ROOT / "logs" / dataset).exists():
            continue
        datasets.append(dataset)
    return datasets


def candidate_log_files(dataset: str) -> list[Path]:
    log_dir = ROOT / "logs" / dataset
    if not log_dir.exists():
        return []
    return sorted([path for path in log_dir.glob("bot.log*") if path.is_file()])


def cache_path(dataset: str) -> Path:
    if dataset == "live_90_70":
        existing = EDGE_DIR / "live_90_70_cross_book_cases.json.gz"
        if existing.exists():
            return existing
    return EDGE_DIR / f"{dataset}_all_trade_cross_book_cases.json.gz"


def read_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def write_cache(path: Path, payload: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)


def coerce_float(value: Any, default: float = 0.0) -> float:
    parsed = parse_float(value)
    return float(default if parsed is None or math.isnan(parsed) else parsed)


def load_trades_with_final_results(dataset: str) -> pd.DataFrame:
    trades_path = ROOT / "stats" / dataset / "trades.csv"
    results_path = ROOT / "stats" / dataset / "market_results.csv"
    trades = pd.read_csv(trades_path)
    market_results = pd.read_csv(results_path)
    if "market" not in trades.columns or "side" not in trades.columns:
        return pd.DataFrame()
    if "market" in market_results.columns:
        final_cols = [col for col in ("market", "result", "market_result", "settlement_ts", "close_time") if col in market_results.columns]
        final = market_results[final_cols].copy()
        rename: dict[str, str] = {}
        if "result" in final.columns:
            rename["result"] = "final_result"
        elif "market_result" in final.columns:
            rename["market_result"] = "final_result"
        if "settlement_ts" in final.columns:
            rename["settlement_ts"] = "final_settlement_ts"
        elif "close_time" in final.columns:
            rename["close_time"] = "final_settlement_ts"
        final = final.rename(columns=rename)
        final = final.drop_duplicates(subset=["market"], keep="last")
        trades = trades.merge(final, on="market", how="left")
    trades = trades[pd.notna(trades.get("entry_fill_cents_used"))].copy()
    if trades.empty:
        return trades
    trades["side_l"] = trades["side"].astype(str).str.lower()
    trades["final_result_l"] = trades.apply(
        lambda row: str(
            first_present(row.get("result"), row.get("market_result"), row.get("final_result")) or ""
        ).lower(),
        axis=1,
    )
    trades = trades[trades["side_l"].isin(["yes", "no"]) & trades["final_result_l"].isin(["yes", "no"])].copy()
    trades["settlement_win_final"] = trades["side_l"] == trades["final_result_l"]
    trades["entry_local"] = pd.to_datetime(trades["entry_ts"], errors="coerce")
    if getattr(trades["entry_local"].dt, "tz", None) is None:
        trades["entry_local"] = trades["entry_local"].dt.tz_localize(ET, ambiguous="NaT", nonexistent="NaT")
    trades["entry_utc"] = trades["entry_local"].dt.tz_convert("UTC")
    settlement_text = trades.apply(
        lambda row: first_present(row.get("settlement_ts"), row.get("final_settlement_ts")),
        axis=1,
    )
    trades["settlement_utc"] = pd.to_datetime(settlement_text, errors="coerce", utc=True)
    for col in ("entry_fee_cents", "exit_fee_cents"):
        if col not in trades.columns:
            trades[col] = 0.0
    if "net_pnl_dollars" not in trades.columns:
        trades["net_pnl_dollars"] = pd.NA
    if "gross_pnl_dollars" not in trades.columns:
        trades["gross_pnl_dollars"] = pd.NA
    trades["actual_net_pnl_for_replay"] = trades.apply(
        lambda row: coerce_float(first_present(row.get("net_pnl_dollars"), row.get("gross_pnl_dollars")), 0.0),
        axis=1,
    )
    return trades


def raw_trade_count(dataset: str) -> int:
    trades_path = ROOT / "stats" / dataset / "trades.csv"
    return int(len(pd.read_csv(trades_path))) if trades_path.exists() else 0


def hold_pnl_from_trade(row: pd.Series, settlement_win: bool) -> float:
    qty = int(row["qty"])
    entry = float(row["entry_fill_cents_used"])
    fee = coerce_float(row.get("entry_fee_cents"), 0.0)
    if settlement_win:
        return round((qty * (100 - entry) - fee) / 100.0, 4)
    return round(-(qty * entry + fee) / 100.0, 4)


def build_cases(dataset: str) -> dict[str, Any]:
    raw_trades_total = raw_trade_count(dataset)
    trades = load_trades_with_final_results(dataset)
    markets = set(trades["market"].astype(str)) if not trades.empty else set()
    heartbeat_series: dict[str, list[tuple[datetime, float | None, float | None, float | None, float | None]]] = {
        market: [] for market in markets
    }
    scanned_lines = 0
    matched_lines = 0
    started = time.time()
    for log_path in candidate_log_files(dataset):
        with log_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                scanned_lines += 1
                if "Heartbeat | watch=" not in line:
                    continue
                match = HEARTBEAT_RE.search(line)
                if not match:
                    continue
                market = match.group("market")
                if market not in heartbeat_series:
                    continue
                yes_bid = parse_float(match.group("yes_bid"))
                yes_ask = parse_float(match.group("yes_ask"))
                no_bid = parse_float(match.group("no_bid"))
                no_ask = parse_float(match.group("no_ask"))
                if yes_bid is None and no_bid is None:
                    continue
                heartbeat_series[market].append((parse_log_ts(match.group("ts")), yes_bid, yes_ask, no_bid, no_ask))
                matched_lines += 1

    cases: list[dict[str, Any]] = []
    for _, row in trades.iterrows():
        market = str(row["market"])
        entry_utc = row["entry_utc"]
        if pd.isna(entry_utc):
            continue
        settlement_utc = row["settlement_utc"]
        end_utc = (
            settlement_utc + pd.Timedelta(seconds=60)
            if not pd.isna(settlement_utc)
            else entry_utc + pd.Timedelta(minutes=16)
        )
        side = str(row["side_l"])
        path: list[dict[str, float]] = []
        for ts, yes_bid, yes_ask, no_bid, no_ask in heartbeat_series.get(market, []):
            if ts < entry_utc or ts > end_utc:
                continue
            own_bid = yes_bid if side == "yes" else no_bid
            opp_bid = no_bid if side == "yes" else yes_bid
            own_ask = yes_ask if side == "yes" else no_ask
            opp_ask = no_ask if side == "yes" else yes_ask
            if own_bid is None:
                continue
            elapsed = round((ts - entry_utc.to_pydatetime()).total_seconds(), 3)
            if elapsed < 0:
                continue
            point = {
                "elapsed": float(elapsed),
                "own_bid": float(own_bid),
                "opp_bid": float(opp_bid) if opp_bid is not None else math.nan,
                "own_ask": float(own_ask) if own_ask is not None else math.nan,
                "opp_ask": float(opp_ask) if opp_ask is not None else math.nan,
                "yes_bid": float(yes_bid) if yes_bid is not None else math.nan,
                "no_bid": float(no_bid) if no_bid is not None else math.nan,
            }
            point["bid_sum"] = point["own_bid"] + point["opp_bid"] if not math.isnan(point["opp_bid"]) else math.nan
            point["held_ask"] = 100.0 - point["opp_bid"] if math.isnan(point["own_ask"]) and not math.isnan(point["opp_bid"]) else point["own_ask"]
            path.append(point)
        if not path:
            continue
        settlement_win = bool(row["settlement_win_final"])
        cases.append(
            {
                "dataset": dataset,
                "market": market,
                "side": side,
                "entry_ts": entry_utc.to_pydatetime().isoformat(),
                "entry_day_et": entry_utc.to_pydatetime().astimezone(ET).strftime("%Y-%m-%d"),
                "entry": float(row["entry_fill_cents_used"]),
                "entry_trigger_cents": coerce_float(row.get("entry_trigger_cents"), float(row["entry_fill_cents_used"])),
                "qty": int(row["qty"]),
                "entry_fee_cents": coerce_float(row.get("entry_fee_cents"), 0.0),
                "actual_net_pnl": float(row["actual_net_pnl_for_replay"]),
                "actual_exit": bool(pd.notna(row.get("exit_ts")) and str(row.get("exit_ts")).strip()),
                "actual_exit_bid": parse_float(row.get("exit_fill_cents_used")),
                "final_result": str(row["final_result_l"]),
                "settlement_win": settlement_win,
                "hold_pnl": hold_pnl_from_trade(row, settlement_win),
                "path": path,
                "min_bid": min(float(point["own_bid"]) for point in path),
                "max_drawdown": max(0.0, float(row["entry_fill_cents_used"]) - min(float(point["own_bid"]) for point in path)),
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": dataset,
        "raw_trades_total": raw_trades_total,
        "trades_total": int(len(trades)),
        "cases": cases,
        "source_logs": [str(path) for path in candidate_log_files(dataset)],
        "scan_stats": {
            "scanned_lines": scanned_lines,
            "matched_heartbeat_lines": matched_lines,
            "elapsed_seconds": round(time.time() - started, 3),
        },
    }


def load_dataset_cases(dataset: str, *, refresh_cache: bool) -> dict[str, Any]:
    path = cache_path(dataset)
    if path.exists() and not refresh_cache:
        payload = read_cache(path)
        payload.setdefault("dataset", dataset)
        payload.setdefault("cache_path", str(path))
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
        if "trades_total" not in payload:
            trades_path = ROOT / "stats" / dataset / "trades.csv"
            payload["trades_total"] = int(len(pd.read_csv(trades_path))) if trades_path.exists() else len(payload.get("cases", []))
        payload.setdefault("raw_trades_total", raw_trade_count(dataset))
        return payload
    payload = build_cases(dataset)
    payload["cache_path"] = str(path)
    write_cache(path, payload)
    return payload


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    exit_bid = meta.get("exit_bid")
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "entry_day_et": case["entry_day_et"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "exit" if meta.get("exit") else "hold",
        "exit_bid": float(exit_bid) if exit_bid is not None else None,
    }


def sim_actual(case: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    return float(case["actual_net_pnl"]), {
        "exit": bool(case.get("actual_exit")),
        "exit_bid": case.get("actual_exit_bid"),
    }


def sim_no_stop(case: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    return float(case["hold_pnl"]), {"exit": False}


def sim_fixed_stop(case: dict[str, Any], stop: float) -> tuple[float, dict[str, Any]]:
    for point in case["path"]:
        held_ask = float(point.get("held_ask", math.nan))
        if not math.isnan(held_ask) and held_ask <= stop:
            bid = float(point["own_bid"])
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "held_ask": held_ask,
                "exit_elapsed": float(point["elapsed"]),
            }
    return float(case["hold_pnl"]), {"exit": False}


def summarize_label(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_rows(label, rows)
    summary["datasets"] = sorted({row["dataset"] for row in rows})
    return summary


def summarize_by_dataset(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for dataset in sorted({row["dataset"] for row in rows}):
        output[dataset] = summarize_label(label, [row for row in rows if row["dataset"] == dataset])
    return output


def run_terminal(cases: list[dict[str, Any]], params: dict[str, Any], label: str) -> dict[str, Any]:
    rows = [row_for(case, *sim_terminal_window_salvage(case, params), label) for case in cases]
    return {
        "label": label,
        "params": params,
        "summary": summarize_label(label, rows),
        "by_dataset": summarize_by_dataset(label, rows),
    }


def run_baseline(cases: list[dict[str, Any]], label: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        if label == "actual":
            pnl, meta = sim_actual(case)
        elif label == "no_stop":
            pnl, meta = sim_no_stop(case)
        elif label == "held_ask_stop_70":
            pnl, meta = sim_fixed_stop(case, 70)
        else:
            raise ValueError(label)
        rows.append(row_for(case, pnl, meta, label))
    return {
        "label": label,
        "summary": summarize_label(label, rows),
        "by_dataset": summarize_by_dataset(label, rows),
    }


def run_sensitivity(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for held_ask_max in (35, 40, 45, 50, 55):
        for final_window_seconds in (45, 60, 75, 90):
            for min_remaining_seconds in (5, 10, 15, 20):
                if min_remaining_seconds >= final_window_seconds:
                    continue
                params = {
                    "held_ask_max": held_ask_max,
                    "final_window_seconds": final_window_seconds,
                    "min_remaining_seconds": min_remaining_seconds,
                }
                result = run_terminal(
                    cases,
                    params,
                    f"terminal_h{held_ask_max}_w{final_window_seconds}_m{min_remaining_seconds}",
                )
                rows.append(result)
    return sorted(rows, key=lambda item: item["summary"]["sim_pnl"], reverse=True)


def walk_forward_fixed(cases: list[dict[str, Any]], params: dict[str, Any]) -> dict[str, Any]:
    ordered = sorted(cases, key=lambda case: case["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    return {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split]["entry_ts"] if holdout else None,
        "train": run_terminal(train, params, "terminal_fixed_train")["summary"],
        "holdout": run_terminal(holdout, params, "terminal_fixed_holdout")["summary"],
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    fixed = payload["terminal_fixed"]["summary"]
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Terminal Salvage All-Trade Validation",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Raw local trades discovered: `{payload['raw_trade_count_total']}`",
        f"- Final-labeled trades considered: `{payload['trade_count_total']}`",
        f"- Quote-path-covered cases: `{payload['case_count']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Fixed strategy params: `{json.dumps(payload['terminal_fixed']['params'], sort_keys=True)}`",
        "",
        "## Aggregate",
        "",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 baseline PnL: `${stop70['sim_pnl']}`",
        f"- Terminal salvage PnL: `${fixed['sim_pnl']}`",
        f"- Delta vs actual: `${fixed['sim_pnl'] - actual['sim_pnl']:.2f}`",
        f"- Delta vs no-stop: `${fixed['sim_pnl'] - no_stop['sim_pnl']:.2f}`",
        f"- Exits / false exits / missed true losers: `{fixed['exits']} / {fixed['false_exit_settlement_winners']} / {fixed['missed_true_losers']}`",
        f"- False-exit rate / missed-true-loser rate: `{fixed['false_exit_rate']} / {fixed['missed_true_loser_rate']}`",
        "",
        "## By Dataset",
        "",
        "| Dataset | Cases | Actual | No-stop | Terminal | Delta vs no-stop | Exits | False | Missed losers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset in payload["datasets"]:
        terminal = payload["terminal_fixed"]["by_dataset"][dataset]
        actual_ds = payload["baselines"]["actual"]["by_dataset"][dataset]
        no_stop_ds = payload["baselines"]["no_stop"]["by_dataset"][dataset]
        lines.append(
            f"| `{dataset}` | {terminal['n']} | {actual_ds['sim_pnl']} | {no_stop_ds['sim_pnl']} | "
            f"{terminal['sim_pnl']} | {terminal['sim_pnl'] - no_stop_ds['sim_pnl']:.2f} | "
            f"{terminal['exits']} | {terminal['false_exit_settlement_winners']} | {terminal['missed_true_losers']} |"
        )
    walk = payload["walk_forward_fixed"]
    lines.extend(
        [
            "",
            "## Fixed Walk-Forward",
            "",
            f"- Split entry: `{walk['split_entry_ts']}`",
            f"- Train PnL / delta vs no-stop: `${walk['train']['sim_pnl']}` / `${walk['train']['delta_vs_no_stop']}`",
            f"- Holdout PnL / delta vs no-stop: `${walk['holdout']['sim_pnl']}` / `${walk['holdout']['delta_vs_no_stop']}`",
            "",
            "## Nearby Sensitivity",
            "",
            "| Rank | Params | PnL | Delta vs no-stop | Exits | False | Missed losers |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for idx, item in enumerate(payload["sensitivity_top"][:10], start=1):
        summary = item["summary"]
        lines.append(
            f"| {idx} | `{json.dumps(item['params'], sort_keys=True)}` | {summary['sim_pnl']} | "
            f"{summary['delta_vs_no_stop']} | {summary['exits']} | "
            f"{summary['false_exit_settlement_winners']} | {summary['missed_true_losers']} |"
        )
    lines.extend(
        [
            "",
            "## Audit Notes",
            "",
            "- `seconds_to_close` comes from the market ticker close time plus the live heartbeat timestamp.",
            "- Settlement labels are merged from each dataset's `market_results.csv`.",
            "- Exit PnL uses actual trade size, recorded entry cents, recorded entry fee when present, and the same estimated Kalshi exit fee helper as the prior research probe.",
            "- This is research-only and does not modify live logic, configs, run scripts, or bot processes.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate terminal-window salvage on every local trade with quote-path coverage.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    dataset_payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    all_cases: list[dict[str, Any]] = []
    for payload in dataset_payloads:
        all_cases.extend(payload.get("cases", []))
    all_cases = sorted(all_cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))

    baselines = {
        "actual": run_baseline(all_cases, "actual"),
        "no_stop": run_baseline(all_cases, "no_stop"),
        "held_ask_stop_70": run_baseline(all_cases, "held_ask_stop_70"),
    }
    terminal_fixed = run_terminal(all_cases, dict(DEFAULT_PARAMS), "terminal_window_salvage_fixed")
    sensitivity = run_sensitivity(all_cases)
    generated_at = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_terminal_salvage_all_trades_{stamp}.json"
    md_path = EDGE_DIR / f"codex_terminal_salvage_all_trades_{stamp}.md"
    latest_json = EDGE_DIR / "codex_terminal_salvage_all_trades_latest.json"
    latest_md = EDGE_DIR / "codex_terminal_salvage_all_trades_latest.md"
    payload = {
        "generated_at": generated_at,
        "datasets": sorted({case["dataset"] for case in all_cases}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": item.get("dataset"),
                "raw_trades_total": item.get("raw_trades_total"),
                "trades_total": item.get("trades_total"),
                "case_count": len(item.get("cases", [])),
                "cache_path": item.get("cache_path"),
                "source_logs": item.get("source_logs"),
                "scan_stats": item.get("scan_stats"),
            }
            for item in dataset_payloads
        ],
        "raw_trade_count_total": int(sum(int(item.get("raw_trades_total") or 0) for item in dataset_payloads)),
        "trade_count_total": int(sum(int(item.get("trades_total") or 0) for item in dataset_payloads)),
        "case_count": len(all_cases),
        "baselines": baselines,
        "terminal_fixed": terminal_fixed,
        "walk_forward_fixed": walk_forward_fixed(all_cases, dict(DEFAULT_PARAMS)),
        "sensitivity_top": sensitivity[:25],
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "live_logic_changed": False,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")
    write_markdown(md_path, payload)
    write_markdown(latest_md, payload)

    fixed = terminal_fixed["summary"]
    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(
        f"Cases={len(all_cases)} labeled_trades={payload['trade_count_total']} "
        f"raw_trades={payload['raw_trade_count_total']} datasets={','.join(payload['datasets'])}"
    )
    print(
        f"terminal_fixed sim={fixed['sim_pnl']} delta_actual={fixed['sim_pnl'] - baselines['actual']['summary']['sim_pnl']:.2f} "
        f"delta_no_stop={fixed['sim_pnl'] - baselines['no_stop']['summary']['sim_pnl']:.2f} "
        f"exits={fixed['exits']} false={fixed['false_exit_settlement_winners']} missed={fixed['missed_true_losers']}"
    )
    for dataset in payload["datasets"]:
        terminal = terminal_fixed["by_dataset"][dataset]
        no_stop = baselines["no_stop"]["by_dataset"][dataset]
        print(
            f"{dataset}: n={terminal['n']} terminal={terminal['sim_pnl']} "
            f"no_stop={no_stop['sim_pnl']} delta_no_stop={terminal['sim_pnl'] - no_stop['sim_pnl']:.2f} "
            f"false={terminal['false_exit_settlement_winners']} missed={terminal['missed_true_losers']}"
        )


if __name__ == "__main__":
    main()
