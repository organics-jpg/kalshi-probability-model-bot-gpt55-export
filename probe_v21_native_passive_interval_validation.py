"""Validate locked interval physics candidates on native passive websocket data.

This is an independent live-websocket validation pass using the
research_data/live_mushroom_v21_size2 recorder. It does not discover new
thresholds. It only evaluates already-frozen pure-physics interval candidates on
the passive ticker stream, with outcomes inferred from cached Coinbase BTC 1m
closes versus the recorded market strike.

No orders are submitted and no live bot code or state is touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_interval_pure_physics_ablation import (
    PhysicsPolicy,
    add_pure_physics_scores,
    choose_decision_sides,
    select_markets,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    clean_json,
    market_base,
    pct,
)
from probe_physics_priors_boundary_models import COINBASE_BTC_CACHE, asof_values, load_coinbase_candles
from probe_live_heartbeat_physics_priors import attach_physics, safe_mid


DATASET_DIR = Path("research_data/live_mushroom_v21_size2")
WATCH_DIR = DATASET_DIR / "raw_events" / "type=watch_market"
TICKER_DIR = DATASET_DIR / "raw_events" / "type=ticker"
LOCK_PATH = OUT_DIR / "locked_interval_pure_physics.json"
SINGLE_LOCK_PATH = OUT_DIR / "locked_pure_physics_interval.json"


def iter_json_lines(paths: Iterable[Path]) -> Iterable[Dict[str, Any]]:
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                row["_source_file"] = str(path)
                row["_source_line"] = line_no
                yield row


def numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(out):
        return None
    return out


def payload(row: Dict[str, Any]) -> Dict[str, Any]:
    value = row.get("payload_json")
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def load_watch_markets() -> Dict[str, Dict[str, Any]]:
    markets: Dict[str, Dict[str, Any]] = {}
    paths = sorted(WATCH_DIR.rglob("*.ndjson"))
    for row in iter_json_lines(paths):
        data = payload(row)
        market = str(data.get("market_ticker") or row.get("market_ticker") or "")
        if not market:
            continue
        close_dt = pd.to_datetime(data.get("close_time"), utc=True, errors="coerce")
        strike = numeric(data.get("strike"))
        if pd.isna(close_dt) or strike is None:
            continue
        existing = markets.get(market)
        candidate = {
            "market": market,
            "close_time": close_dt.isoformat(),
            "strike": float(strike),
            "status": data.get("status"),
            "first_watch_ts": row.get("ts_wall") or row.get("local_recv_ts"),
            "source_file": row.get("_source_file"),
        }
        if existing is None:
            markets[market] = candidate
        else:
            # Prefer the earliest active record, but keep a deterministic strike/close.
            old_ts = pd.to_datetime(existing.get("first_watch_ts"), utc=True, errors="coerce")
            new_ts = pd.to_datetime(candidate.get("first_watch_ts"), utc=True, errors="coerce")
            if pd.isna(old_ts) or (not pd.isna(new_ts) and new_ts < old_ts):
                markets[market] = candidate
    return markets


def load_candles_for_times(times: pd.Series) -> pd.DataFrame:
    entries = pd.DataFrame({"entry_dt": pd.to_datetime(times, utc=True, errors="coerce").dropna()})
    candles = load_coinbase_candles(entries, fetch_missing=False)
    if candles.empty and COINBASE_BTC_CACHE.exists():
        candles = pd.read_parquet(COINBASE_BTC_CACHE)
        candles["close_dt"] = pd.to_datetime(candles["close_dt"], utc=True, errors="coerce")
    return candles


def infer_outcomes(markets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    if not markets:
        return {}
    market_frame = pd.DataFrame(markets.values())
    market_frame["close_dt"] = pd.to_datetime(market_frame["close_time"], utc=True, errors="coerce")
    candles = load_candles_for_times(market_frame["close_dt"])
    if candles.empty:
        return {}
    market_frame["btc_close_at_expiry"] = asof_values(candles, market_frame["close_dt"], "close", 180.0)
    out: Dict[str, Dict[str, Any]] = {}
    for row in market_frame.dropna(subset=["close_dt", "strike", "btc_close_at_expiry"]).itertuples(index=False):
        close_dt = getattr(row, "close_dt")
        # Do not label markets that have not reached the available candle horizon.
        if pd.isna(close_dt):
            continue
        btc_close = float(getattr(row, "btc_close_at_expiry"))
        strike = float(getattr(row, "strike"))
        out[str(getattr(row, "market"))] = {
            "outcome": "yes" if btc_close > strike else "no",
            "method": "coinbase_close_vs_recorded_strike",
            "source": str(COINBASE_BTC_CACHE),
            "btc_close_at_expiry": btc_close,
            "strike": strike,
        }
    return out


def quote_rows_for_ticker(markets: Dict[str, Dict[str, Any]], outcomes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    paths = sorted(TICKER_DIR.rglob("*.ndjson"))
    rows: List[Dict[str, Any]] = []
    seen: set[tuple[str, pd.Timestamp]] = set()
    source_line_no = 0
    for raw in iter_json_lines(paths):
        source_line_no += 1
        data = payload(raw)
        market = str(data.get("market_ticker") or raw.get("market_ticker") or "")
        market_info = markets.get(market)
        if not market_info or market not in outcomes:
            continue
        entry_dt = pd.to_datetime(raw.get("ts_wall") or raw.get("local_recv_ts") or data.get("time"), utc=True, errors="coerce")
        close_dt = pd.to_datetime(market_info.get("close_time"), utc=True, errors="coerce")
        strike = numeric(market_info.get("strike"))
        if pd.isna(entry_dt) or pd.isna(close_dt) or strike is None:
            continue
        seconds_to_close = (close_dt - entry_dt).total_seconds()
        if seconds_to_close <= 0:
            continue
        entry_minute = entry_dt.floor("min")
        key = (market, entry_minute)
        if key in seen:
            continue

        yes_bid = numeric(data.get("yes_bid"))
        yes_ask = numeric(data.get("yes_ask"))
        no_bid = numeric(data.get("no_bid"))
        no_ask = numeric(data.get("no_ask"))
        yes_mid = safe_mid(int(yes_bid) if yes_bid is not None else None, int(yes_ask) if yes_ask is not None else None)
        no_mid = safe_mid(int(no_bid) if no_bid is not None else None, int(no_ask) if no_ask is not None else None)
        if yes_mid is None or no_mid is None:
            continue
        seen.add(key)
        outcome = outcomes[market]["outcome"]
        quote_by_side = {
            "yes": {"bid": yes_bid, "ask": yes_ask, "mid": yes_mid, "other_mid": no_mid},
            "no": {"bid": no_bid, "ask": no_ask, "mid": no_mid, "other_mid": yes_mid},
        }
        for side, quote in quote_by_side.items():
            if quote["bid"] is None or quote["ask"] is None:
                continue
            rows.append(
                {
                    "dataset": "v21_native_passive_ticker_minute",
                    "decision_key": f"{market}|{entry_minute.isoformat()}",
                    "entry_key": f"{market}|{entry_minute.isoformat()}|{side}",
                    "entry_dt": entry_dt,
                    "entry_minute": entry_minute,
                    "market": market,
                    "side": side,
                    "outcome": outcome,
                    "outcome_available": True,
                    "win": side == outcome,
                    "qty": 1,
                    "ask_cents": float(quote["ask"]),
                    "bid_cents": float(quote["bid"]),
                    "book_mid_cents": float(quote["mid"]),
                    "book_p_side": float(quote["mid"]) / 100.0,
                    "book_other_mid_cents": float(quote["other_mid"]),
                    "book_margin_cents": float(quote["mid"] - quote["other_mid"]),
                    "spread_cents": float(quote["ask"] - quote["bid"]),
                    "spot": np.nan,
                    "strike": float(strike),
                    "seconds_to_close": float(seconds_to_close),
                    "v28_sigma_t_dollars": np.nan,
                    "source_line_no": source_line_no,
                    "trust_state": raw.get("trust_state"),
                    "outcome_method": outcomes[market]["method"],
                    "outcome_source": outcomes[market]["source"],
                    "close_dt": close_dt,
                }
            )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["entry_dt", "decision_key", "side"]).reset_index(drop=True)


def load_locked_policies() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    if LOCK_PATH.exists():
        try:
            data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            for item in data.get("candidates", []):
                policy = item.get("policy") or {}
                candidates.append(
                    {
                        "name": str(item.get("name")),
                        "source_lock": str(LOCK_PATH),
                        "policy": PhysicsPolicy(
                            chooser=str(policy["chooser"]),
                            min_score=float(policy["min_score"]),
                            ask_max=float(policy["ask_max"]),
                            min_seconds_to_close=float(policy["min_seconds_to_close"]),
                            gate=str(policy.get("gate") or "none"),
                        ),
                    }
                )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            pass
    if SINGLE_LOCK_PATH.exists():
        try:
            data = json.loads(SINGLE_LOCK_PATH.read_text(encoding="utf-8"))
            policy = (data.get("candidate") or {}).get("policy") or {}
            name = str((data.get("candidate") or {}).get("name") or "single_locked_pure_physics")
            label = str(policy.get("label") or "")
            if not any(item["name"] == name or item["policy"].label == label for item in candidates):
                candidates.append(
                    {
                        "name": name,
                        "source_lock": str(SINGLE_LOCK_PATH),
                        "policy": PhysicsPolicy(
                            chooser=str(policy["chooser"]),
                            min_score=float(policy["min_score"]),
                            ask_max=float(policy["ask_max"]),
                            min_seconds_to_close=float(policy["min_seconds_to_close"]),
                            gate=str(policy.get("gate") or "none"),
                        ),
                    }
                )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            pass
    return candidates


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
    }


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"]
    )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def write_report(path: Path, generated: str, diagnostics: Dict[str, Any], summaries: List[Dict[str, Any]]) -> None:
    lines: List[str] = [
        "# V21 Native Passive Interval Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Source dataset: `research_data/live_mushroom_v21_size2` native passive ticker websocket stream.",
        "- Outcomes are inferred from cached Coinbase BTC 1m close at market expiry versus recorded strike.",
        "- Candidate policies are loaded from existing locked pure-physics interval locks; no threshold search is performed.",
        "",
        "## Data",
        "",
        f"- Watch markets parsed: {diagnostics['watch_markets']}",
        f"- Markets with inferred outcomes: {diagnostics['outcome_markets']}",
        f"- Minute decision rows before physics: {diagnostics['raw_side_rows']}",
        f"- Minute decision rows after candle physics: {diagnostics['physics_side_rows']}",
        f"- Resolved interval denominator: {diagnostics['resolved_intervals']}",
        "",
        "## Locked Candidate Validation",
        "",
        "| candidate | target | Wilson | all acc | all cov | all Wilson low | holdout acc | holdout cov | median ask | ask=100 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        all_m = summary["metrics"]["all"]
        holdout = summary["metrics"]["holdout"]
        lines.append(
            f"| `{summary['name']}` | {summary['target_pass']} | {summary['wilson_pass']} | "
            f"{pct(all_m['accuracy'])} | {pct(all_m['coverage'])} | {pct(all_m['wilson95_lower'])} | "
            f"{pct(holdout['accuracy'])} | {pct(holdout['coverage'])} | {fmt(all_m['median_ask'])} | {all_m['ask_eq_100']} |"
        )
    lines += ["", "## Read", ""]
    if any(summary["wilson_pass"] for summary in summaries):
        lines.append("At least one locked candidate passes the 95% / 80% interval target with Wilson-robust split evidence on this independent live websocket dataset.")
    elif any(summary["target_pass"] for summary in summaries):
        lines.append("At least one locked candidate passes the literal split target on this independent live websocket dataset, but not the Wilson-robust proof.")
    else:
        lines.append("No locked pure-physics candidate clears the 95% / 80% split target on this independent live websocket dataset.")
    if any((summary["metrics"]["all"]["median_ask"] or 0.0) >= 95.0 for summary in summaries):
        lines.append("The high-price degeneracy warning remains visible on at least one candidate.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    markets = load_watch_markets()
    outcomes = infer_outcomes(markets)
    raw = quote_rows_for_ticker(markets, outcomes)
    physics, candle_info = attach_physics(raw, fetch_btc_candles=False)
    physics = add_pure_physics_scores(physics)
    base = market_base(physics)
    physics = physics.merge(base[["market", "split"]], on="market", how="inner")

    summaries: List[Dict[str, Any]] = []
    selected_frames: List[pd.DataFrame] = []
    for item in load_locked_policies():
        policy = item["policy"]
        chosen = choose_decision_sides(physics, policy.chooser)
        selected = select_markets({policy.chooser: chosen}, policy).copy()
        selected["candidate"] = item["name"]
        selected["source_lock"] = item["source_lock"]
        selected_frames.append(selected)
        metrics = {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}
        summaries.append(
            {
                "name": item["name"],
                "source_lock": item["source_lock"],
                "policy": {
                    "label": policy.label,
                    "chooser": policy.chooser,
                    "min_score": policy.min_score,
                    "ask_max": policy.ask_max,
                    "min_seconds_to_close": policy.min_seconds_to_close,
                    "gate": policy.gate,
                },
                "metrics": metrics,
                "target_pass": target_pass(metrics),
                "wilson_pass": wilson_pass(metrics),
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    diagnostics = {
        "watch_markets": int(len(markets)),
        "outcome_markets": int(len(outcomes)),
        "raw_side_rows": int(len(raw)),
        "physics_side_rows": int(len(physics)),
        "resolved_intervals": int(len(base)),
        "candle_info": candle_info,
    }
    md_latest = OUT_DIR / "v21_native_passive_interval_validation_latest.md"
    md_stamp = OUT_DIR / f"v21_native_passive_interval_validation_{generated}.md"
    json_latest = OUT_DIR / "v21_native_passive_interval_validation_latest.json"
    json_stamp = OUT_DIR / f"v21_native_passive_interval_validation_{generated}.json"
    selected_latest = OUT_DIR / "v21_native_passive_interval_validation_selected_latest.csv"
    selected_stamp = OUT_DIR / f"v21_native_passive_interval_validation_selected_{generated}.csv"
    ledger_latest = OUT_DIR / "v21_native_passive_interval_validation_ledger_latest.csv"
    ledger_stamp = OUT_DIR / f"v21_native_passive_interval_validation_ledger_{generated}.csv"

    selected.to_csv(selected_latest, index=False)
    selected.to_csv(selected_stamp, index=False)
    physics.to_csv(ledger_latest, index=False)
    physics.to_csv(ledger_stamp, index=False)
    write_report(md_latest, generated, diagnostics, summaries)
    write_report(md_stamp, generated, diagnostics, summaries)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "summaries": summaries}
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("V21 native passive interval validation complete")
    print(f"watch_markets={len(markets)} outcome_markets={len(outcomes)} intervals={len(base)}")
    print(f"raw_side_rows={len(raw)} physics_side_rows={len(physics)} candidates={len(summaries)}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
