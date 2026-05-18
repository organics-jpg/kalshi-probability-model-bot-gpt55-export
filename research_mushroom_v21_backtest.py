from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from btc_mushroom_forecaster_v22 import MushroomConfig, MushroomForecaster


ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT / "research_data"
EDGE_DIR = ROOT / "logs" / "edge_research"
SCRIPT_VERSION = "mushroom-v21-research-backtest-v1"
UTC = timezone.utc

DEFAULT_SOURCE_CANDIDATE_ID = "pnl_max_p05_q065_logged_live_reference_v1"
DEFAULT_DATASET = "live_liquidity_dwell_size2"
DEFAULT_POSITION_SIZE = 2
DEFAULT_MIN_P_SIDE = 0.80
DEFAULT_STRICT_P_SIDE = 0.85
DEFAULT_MIN_EDGE_CENTS = 2.0
DEFAULT_SLIPPAGE_CENTS = 1.0
DEFAULT_MAX_QUOTE_AGE_MS = 1000.0


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def parse_dt(value: Any) -> datetime | None:
    if value in (None, "", "None", "null"):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def safe_float(value: Any) -> float | None:
    if value in (None, "", "None", "null", "nan"):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def safe_int(value: Any) -> int | None:
    out = safe_float(value)
    if out is None:
        return None
    return int(round(out))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_parquet_tree(root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not root.exists():
        return pd.DataFrame()
    for fp in sorted(root.rglob("*.parquet")):
        try:
            frame = pd.read_parquet(fp)
        except Exception:
            continue
        if frame.empty:
            continue
        market_from_path = ""
        for part in fp.parts:
            if part.startswith("market_ticker="):
                market_from_path = part.split("=", 1)[1]
                break
        if market_from_path:
            if "market_ticker" not in frame.columns:
                frame["market_ticker"] = market_from_path
            else:
                frame["market_ticker"] = frame["market_ticker"].fillna(market_from_path)
                frame.loc[frame["market_ticker"].astype(str) == "", "market_ticker"] = market_from_path
        candidate_from_path = ""
        for part in fp.parts:
            if part.startswith("candidate_id="):
                candidate_from_path = part.split("=", 1)[1]
                break
        if candidate_from_path and "candidate_id" not in frame.columns:
            frame["candidate_id"] = candidate_from_path
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_source_decisions(dataset_root: Path, source_candidate_id: str) -> pd.DataFrame:
    root = dataset_root / "candidate_decisions" / f"candidate_id={source_candidate_id}"
    decisions = load_parquet_tree(root)
    if decisions.empty:
        all_decisions = load_parquet_tree(dataset_root / "candidate_decisions")
        if all_decisions.empty or "candidate_id" not in all_decisions.columns:
            return pd.DataFrame()
        decisions = all_decisions[all_decisions["candidate_id"].astype(str) == source_candidate_id].copy()
    if decisions.empty:
        return decisions
    for col in ("source_feature_ts", "available_at"):
        if col in decisions.columns:
            decisions[col] = pd.to_datetime(decisions[col], utc=True, errors="coerce")
    decisions = decisions.sort_values(["available_at", "market_ticker", "side"], na_position="last").reset_index(drop=True)
    return decisions


def load_features(dataset_root: Path) -> dict[str, pd.DataFrame]:
    features = load_parquet_tree(dataset_root / "features")
    if features.empty:
        return {}
    for col in ("feature_available_at", "ts", "local_recv_dt"):
        if col in features.columns:
            features[col] = pd.to_datetime(features[col], utc=True, errors="coerce")
    if "feature_available_at" not in features.columns:
        features["feature_available_at"] = features.get("ts")
    features = features[features["market_ticker"].notna() & features["feature_available_at"].notna()].copy()
    by_market: dict[str, pd.DataFrame] = {}
    for market, grp in features.groupby(features["market_ticker"].astype(str)):
        by_market[market] = grp.sort_values("feature_available_at").reset_index(drop=True)
    return by_market


def load_candles(dataset_root: Path) -> pd.DataFrame:
    candles = load_parquet_tree(dataset_root / "btc_spot_candles")
    if candles.empty:
        return candles
    for col in ("open_dt", "close_dt"):
        if col in candles.columns:
            candles[col] = pd.to_datetime(candles[col], utc=True, errors="coerce")
    candles = candles[candles["close_dt"].notna()].copy()
    candles = candles.drop_duplicates(subset=["close_dt"], keep="last")
    return candles.sort_values("close_dt").reset_index(drop=True)


def find_feature(features_by_market: dict[str, pd.DataFrame], market: str, ts: datetime) -> dict[str, Any] | None:
    frame = features_by_market.get(market)
    if frame is None or frame.empty:
        return None
    ts_pd = pd.Timestamp(ts)
    idx = frame["feature_available_at"].searchsorted(ts_pd, side="right") - 1
    if idx < 0:
        return None
    row = frame.iloc[int(idx)].to_dict()
    return row


def fetch_market_metadata(ticker: str, session: requests.Session, *, timeout: float = 10.0) -> dict[str, Any]:
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    market = payload.get("market")
    return market if isinstance(market, dict) else {}


def build_market_metadata(
    dataset_root: Path,
    tickers: list[str],
    *,
    refresh: bool,
    write: bool,
) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    cache_path = dataset_root / "metadata" / "mushroom_v21_market_metadata_cache.json"
    cache = read_json(cache_path)
    markets = cache.get("markets") if isinstance(cache.get("markets"), dict) else {}
    out: dict[str, dict[str, Any]] = {str(k): v for k, v in markets.items() if isinstance(v, dict)}
    issues: Counter[str] = Counter()
    missing = [ticker for ticker in tickers if refresh or ticker not in out]
    if missing:
        session = requests.Session()
        for idx, ticker in enumerate(missing, start=1):
            try:
                market = fetch_market_metadata(ticker, session)
            except Exception:
                issues["metadata_fetch_failed"] += 1
                continue
            if not market:
                issues["metadata_empty"] += 1
                continue
            out[ticker] = market
            if idx % 25 == 0:
                time.sleep(0.2)
    for ticker in tickers:
        market = out.get(ticker) or {}
        if safe_float(market.get("floor_strike")) is None:
            issues["missing_strike"] += 1
        if str(market.get("result") or "").lower() not in {"yes", "no"}:
            issues["missing_result"] += 1
    if write:
        payload = {
            "schema_version": "mushroom-v21-market-metadata-cache-v1",
            "updated_at_utc": utc_now().isoformat(),
            "source": "Kalshi public trade-api markets endpoint",
            "markets": out,
        }
        write_json(cache_path, payload)
    return out, issues


def estimated_order_fee_cents(price_cents: int, count: int) -> int:
    bounded_price = max(1, min(99, int(price_cents)))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def update_forecaster_to(
    forecaster: MushroomForecaster,
    candles: pd.DataFrame,
    candle_idx: int,
    ts: datetime,
) -> int:
    while candle_idx < len(candles):
        row = candles.iloc[candle_idx]
        close_dt = row.get("close_dt")
        if pd.isna(close_dt) or pd.Timestamp(close_dt).to_pydatetime() > ts:
            break
        forecaster.update_bar(
            ts=pd.Timestamp(row["close_dt"]).to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume") or 0.0),
        )
        candle_idx += 1
    return candle_idx


def classify_bucket(seconds_to_close: float | None) -> str:
    if seconds_to_close is None:
        return "unknown"
    if seconds_to_close < 30:
        return "0_30s"
    if seconds_to_close < 60:
        return "30_60s"
    if seconds_to_close < 120:
        return "60_120s"
    if seconds_to_close < 240:
        return "120_240s"
    if seconds_to_close < 480:
        return "240_480s"
    return "480s_plus"


def score_rows(rows: list[dict[str, Any]], *, gate_name: str) -> dict[str, Any]:
    approved = [row for row in rows if row.get(gate_name)]
    labeled = [row for row in approved if row.get("would_win") is not None]
    winners = [row for row in labeled if row.get("would_win") is True]
    losers = [row for row in labeled if row.get("would_win") is False]
    gross = sum(float(row.get("gross_pnl_cents_for_size") or 0.0) for row in labeled)
    net = sum(float(row.get("net_pnl_cents_for_size") or 0.0) for row in labeled)
    conservative = sum(float(row.get("conservative_pnl_cents_for_size") or 0.0) for row in labeled)
    side_counts = Counter(str(row.get("side") or "") for row in labeled)
    side_pnl: defaultdict[str, float] = defaultdict(float)
    bucket_pnl: defaultdict[str, float] = defaultdict(float)
    for row in labeled:
        side_pnl[str(row.get("side") or "")] += float(row.get("conservative_pnl_cents_for_size") or 0.0)
        bucket_pnl[classify_bucket(safe_float(row.get("seconds_to_close")))] += float(row.get("conservative_pnl_cents_for_size") or 0.0)
    return {
        "approved": len(approved),
        "labeled_approved": len(labeled),
        "winners": len(winners),
        "losers": len(losers),
        "win_rate": round(len(winners) / len(labeled), 6) if labeled else None,
        "gross_pnl_cents": round(gross, 4),
        "net_pnl_cents": round(net, 4),
        "conservative_pnl_cents": round(conservative, 4),
        "avg_edge_cents": round(sum(float(row["v21_edge_cents"]) for row in approved) / len(approved), 6) if approved else None,
        "avg_p_side": round(sum(float(row["v21_p_side"]) for row in approved) / len(approved), 6) if approved else None,
        "side_counts": dict(side_counts),
        "side_conservative_pnl_cents": {key: round(value, 4) for key, value in sorted(side_pnl.items())},
        "time_to_close_conservative_pnl_cents": {key: round(value, 4) for key, value in sorted(bucket_pnl.items())},
    }


def probability_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [row for row in rows if row.get("would_win") is not None and row.get("v21_p_side") is not None]
    if not labeled:
        return {"n": 0}
    brier = 0.0
    log_loss = 0.0
    abs_error = 0.0
    for row in labeled:
        p = min(1.0 - 1e-9, max(1e-9, float(row["v21_p_side"])))
        y = 1.0 if row["would_win"] else 0.0
        brier += (p - y) ** 2
        log_loss += -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))
        abs_error += abs(p - y)
    return {
        "n": len(labeled),
        "brier": round(brier / len(labeled), 8),
        "log_loss": round(log_loss / len(labeled), 8),
        "mean_abs_error": round(abs_error / len(labeled), 8),
        "base_win_rate": round(sum(1 for row in labeled if row["would_win"]) / len(labeled), 6),
        "avg_p_side": round(sum(float(row["v21_p_side"]) for row in labeled) / len(labeled), 6),
    }


def render_report(summary: dict[str, Any], rows: list[dict[str, Any]], artifacts: dict[str, Path]) -> str:
    broad = summary["broad_gate"]
    strict = summary["strict_gate"]
    metrics = summary["probability_metrics"]
    issues = summary["unscored_reasons"]
    metadata_issues = summary["metadata_issues"]
    top_rows = sorted(
        [row for row in rows if row.get("broad_would_enter")],
        key=lambda row: float(row.get("v21_edge_cents") or 0.0),
        reverse=True,
    )[:12]
    lines = [
        f"# Mushroom v21 Research Lab Backtest: {summary['dataset_tag']}",
        "",
        f"- Generated: `{summary['generated_at_utc']}`",
        "- Scope: research-only backtest. No live bot code, configs, state, orders, or processes were changed.",
        f"- Model: `v0.21 static field` from `btc_mushroom_forecaster_v22.py` component `p_static_boundary_field` before v0.22 transport.",
        f"- Source decision tape: `{summary['source_candidate_id']}` gauntlet decision points.",
        f"- Source decisions: `{summary['source_decision_count']}`; scored rows: `{summary['scored_rows']}`.",
        f"- Dataset recorder type: `{summary['recorder_type']}`; data flags: `{summary['data_quality_flags']}`.",
        f"- Strike/result source: Kalshi public market metadata cached at `{summary['market_metadata_cache']}`.",
        "",
        "## Gate Results",
        "",
        "| Gate | Approved | Win rate | Gross PnL | Net PnL | Conservative PnL | Avg edge | Avg p(side) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| broad p>={summary['min_p_side']}, edge>={summary['min_edge_cents']}c | "
            f"{broad['approved']} | {broad['win_rate']} | {broad['gross_pnl_cents']}c | "
            f"{broad['net_pnl_cents']}c | {broad['conservative_pnl_cents']}c | "
            f"{broad['avg_edge_cents']}c | {broad['avg_p_side']} |"
        ),
        (
            f"| strict p>={summary['strict_p_side']}, edge>={summary['min_edge_cents']}c | "
            f"{strict['approved']} | {strict['win_rate']} | {strict['gross_pnl_cents']}c | "
            f"{strict['net_pnl_cents']}c | {strict['conservative_pnl_cents']}c | "
            f"{strict['avg_edge_cents']}c | {strict['avg_p_side']} |"
        ),
        "",
        "Conservative PnL subtracts entry fee plus the configured slippage budget from hold-to-settlement payoff.",
        "",
        "## Probability Quality",
        "",
        f"- Labeled scored rows: `{metrics.get('n', 0)}`",
        f"- Brier: `{metrics.get('brier')}`; log loss: `{metrics.get('log_loss')}`; mean abs error: `{metrics.get('mean_abs_error')}`.",
        f"- Base side win rate: `{metrics.get('base_win_rate')}`; average v21 p(side): `{metrics.get('avg_p_side')}`.",
        "",
        "## Caveats",
        "",
        f"- Unscored reasons: `{issues}`.",
        f"- Market metadata issues: `{metadata_issues}`.",
        f"- Quote freshness gate: `quote_age_ms <= {summary['max_quote_age_ms']}`.",
        "- The active dataset is log-derived top-of-book backfill, so depth/fillability confidence is weaker than native passive capture.",
        "- BTC spot candles are Binance 1m candles from the Research Lab feature set; Kalshi settlement uses CF Benchmarks RTI.",
        "",
        "## Strongest Broad Entries",
        "",
        "| Time | Market | Side | Ask | Result | p(side) | Edge | Conservative PnL |",
        "|---|---|---|---:|---|---:|---:|---:|",
    ]
    for row in top_rows:
        lines.append(
            f"| `{row.get('available_at')}` | `{row.get('market_ticker')}` | `{row.get('side')}` | "
            f"{row.get('ask_cents')} | `{row.get('market_result')}` | {row.get('v21_p_side')} | "
            f"{row.get('v21_edge_cents')}c | {row.get('conservative_pnl_cents_for_size')}c |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary JSON: `{artifacts['summary_json']}`",
            f"- Decision CSV: `{artifacts['decisions_csv']}`",
            f"- Latest Markdown: `{artifacts['latest_report']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fields = sorted({key for row in rows for key in row.keys()})
    else:
        fields = []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_backtest(args: argparse.Namespace) -> dict[str, Any]:
    dataset_root = RESEARCH_ROOT / args.dataset
    if not dataset_root.exists():
        raise SystemExit(f"Missing Research Lab dataset: {dataset_root}")
    manifest = read_json(dataset_root / "metadata" / "dataset_manifest.json")
    decisions = load_source_decisions(dataset_root, args.source_candidate_id)
    if decisions.empty:
        raise SystemExit(
            f"No source candidate decisions found for {args.source_candidate_id}. "
            "Run research_gauntlet.py for the dataset first."
        )
    features_by_market = load_features(dataset_root)
    candles = load_candles(dataset_root)
    if not features_by_market:
        raise SystemExit(f"Missing feature tape under {dataset_root / 'features'}")
    if candles.empty:
        raise SystemExit(f"Missing BTC spot candles under {dataset_root / 'btc_spot_candles'}")

    markets = sorted(set(str(value) for value in decisions["market_ticker"].dropna().unique()))
    market_metadata, metadata_issues = build_market_metadata(
        dataset_root,
        markets,
        refresh=bool(args.refresh_market_cache),
        write=bool(args.write),
    )

    cfg = MushroomConfig(
        transport_recent_weight=0.0,
        transport_long_weight=0.0,
        transport_temperature=1.0,
    )
    forecaster = MushroomForecaster(cfg)
    candle_idx = 0
    rows: list[dict[str, Any]] = []
    unscored: Counter[str] = Counter()

    for _, decision in decisions.iterrows():
        market = str(decision.get("market_ticker") or "")
        side = str(decision.get("side") or "").lower()
        decision_ts = parse_dt(decision.get("source_feature_ts")) or parse_dt(decision.get("available_at"))
        if not market or side not in {"yes", "no"} or decision_ts is None:
            unscored["bad_source_decision"] += 1
            continue
        candle_idx = update_forecaster_to(forecaster, candles, candle_idx, decision_ts)
        if len(forecaster.history) < cfg.min_history_points:
            unscored["model_warming"] += 1
            continue
        feature = find_feature(features_by_market, market, decision_ts)
        if feature is None:
            unscored["missing_feature"] += 1
            continue
        seconds_to_close = safe_float(feature.get("seconds_to_close") if feature.get("seconds_to_close") is not None else decision.get("seconds_to_close"))
        if seconds_to_close is None or seconds_to_close <= 0:
            unscored["closed_or_missing_horizon"] += 1
            continue
        quote_age_ms = safe_float(feature.get("quote_age_ms"))
        if quote_age_ms is not None and quote_age_ms > float(args.max_quote_age_ms):
            unscored["stale_quote"] += 1
            continue
        market_info = market_metadata.get(market) or {}
        strike = safe_float(market_info.get("floor_strike"))
        result = str(market_info.get("result") or "").lower()
        if strike is None:
            unscored["missing_strike"] += 1
            continue
        if result not in {"yes", "no"}:
            unscored["missing_result"] += 1
            continue
        ask_col = f"{side}_entry_limit_cents"
        ask_cents = safe_int(feature.get(ask_col))
        if ask_cents is None:
            ask_cents = safe_int(decision.get("proposed_limit_cents"))
        if ask_cents is None or ask_cents <= 0 or ask_cents >= 100:
            unscored["missing_or_bad_ask"] += 1
            continue
        yes_bid = safe_float(feature.get("yes_bid_cents"))
        yes_ask = safe_float(feature.get("yes_ask_cents"))
        market_p_yes = None
        if yes_bid is not None and yes_ask is not None:
            market_p_yes = max(0.001, min(0.999, (yes_bid + yes_ask) / 200.0))
        try:
            pred = forecaster.predict_physical(
                side="yes",
                strike=float(strike),
                horizon_seconds=float(seconds_to_close),
                market_p_yes=market_p_yes,
            )
        except Exception as exc:
            unscored[f"prediction_error:{type(exc).__name__}"] += 1
            continue
        p_yes_static = float(pred.components["p_static_boundary_field"])
        p_side = p_yes_static if side == "yes" else 1.0 - p_yes_static
        fair_cents = 100.0 * p_side
        fee_per_contract = estimated_order_fee_cents(ask_cents, int(args.position_size)) / float(args.position_size)
        edge_cents = fair_cents - float(ask_cents) - fee_per_contract - float(args.slippage_cents)
        would_win = result == side
        gross_per_contract = 100.0 - ask_cents if would_win else -float(ask_cents)
        net_per_contract = gross_per_contract - fee_per_contract
        conservative_per_contract = net_per_contract - float(args.slippage_cents)
        row = {
            "decision_id": str(decision.get("decision_id") or ""),
            "dataset_tag": args.dataset,
            "market_ticker": market,
            "available_at": decision_ts.isoformat(),
            "side": side,
            "market_result": result,
            "would_win": would_win,
            "strike": round(float(strike), 4),
            "ask_cents": ask_cents,
            "fee_cents_per_contract": round(fee_per_contract, 6),
            "slippage_budget_cents": float(args.slippage_cents),
            "seconds_to_close": round(float(seconds_to_close), 6),
            "time_to_close_bucket": classify_bucket(seconds_to_close),
            "quote_age_ms": round(float(quote_age_ms), 6) if quote_age_ms is not None else None,
            "btc_close": round(float(pred.components["spot"]), 6),
            "v21_p_yes": round(p_yes_static, 8),
            "v21_p_side": round(p_side, 8),
            "v21_fair_cents": round(fair_cents, 6),
            "v21_edge_cents": round(edge_cents, 6),
            "v21_d_sigma": round(float(pred.components["d_sigma"]), 8),
            "v21_abs_d_sigma": round(float(pred.components["abs_d_sigma"]), 8),
            "v21_p_anchor": round(float(pred.components["p_anchor"]), 8),
            "v21_arrow": round(float(pred.components["arrow"]), 8),
            "v21_static_gate": round(float(pred.components["static_gate"]), 8),
            "gross_pnl_cents_for_size": round(gross_per_contract * int(args.position_size), 6),
            "net_pnl_cents_for_size": round(net_per_contract * int(args.position_size), 6),
            "conservative_pnl_cents_for_size": round(conservative_per_contract * int(args.position_size), 6),
            "broad_would_enter": bool(p_side >= float(args.min_p_side) and edge_cents >= float(args.min_edge_cents)),
            "strict_would_enter": bool(p_side >= float(args.strict_p_side) and edge_cents >= float(args.min_edge_cents)),
            "source_candidate_decision": str(decision.get("decision") or ""),
            "source_candidate_reject_reason": str(decision.get("reject_reason") or ""),
        }
        rows.append(row)

    generated_at = utc_now()
    stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    summary = {
        "schema_version": "mushroom-v21-research-backtest-summary-v1",
        "script_version": SCRIPT_VERSION,
        "dataset_tag": args.dataset,
        "generated_at_utc": generated_at.isoformat(),
        "source_candidate_id": args.source_candidate_id,
        "source_decision_count": int(len(decisions)),
        "scored_rows": len(rows),
        "unscored_reasons": dict(unscored),
        "metadata_issues": dict(metadata_issues),
        "recorder_type": str(manifest.get("recorder_type") or "unknown"),
        "data_quality_flags": manifest.get("data_quality_flags") or [],
        "market_metadata_cache": str(dataset_root / "metadata" / "mushroom_v21_market_metadata_cache.json"),
        "model": {
            "name": "btc_mushroom_v21_static_field",
            "definition": "p_static_boundary_field from btc_mushroom_forecaster_v22 before v0.22 transport correction",
            "min_history_points": cfg.min_history_points,
            "transport_recent_weight": cfg.transport_recent_weight,
            "transport_long_weight": cfg.transport_long_weight,
            "transport_temperature": cfg.transport_temperature,
        },
        "position_size": int(args.position_size),
        "min_p_side": float(args.min_p_side),
        "strict_p_side": float(args.strict_p_side),
        "min_edge_cents": float(args.min_edge_cents),
        "slippage_cents": float(args.slippage_cents),
        "max_quote_age_ms": float(args.max_quote_age_ms),
        "probability_metrics": probability_metrics(rows),
        "broad_gate": score_rows(rows, gate_name="broad_would_enter"),
        "strict_gate": score_rows(rows, gate_name="strict_would_enter"),
    }
    summary["new_edge_status"] = (
        "PASS_candidate_positive_conservative_pnl"
        if summary["broad_gate"]["approved"] and float(summary["broad_gate"]["conservative_pnl_cents"]) > 0
        else "FAIL_no_positive_broad_gate"
    )

    artifacts = {
        "summary_json": EDGE_DIR / f"codex_mushroom_v21_backtest_{args.dataset}_{stamp}.json",
        "report": EDGE_DIR / f"codex_mushroom_v21_backtest_{args.dataset}_{stamp}.md",
        "decisions_csv": EDGE_DIR / f"codex_mushroom_v21_backtest_decisions_{args.dataset}_{stamp}.csv",
        "latest_summary": EDGE_DIR / f"codex_mushroom_v21_backtest_{args.dataset}_latest.json",
        "latest_report": EDGE_DIR / f"codex_mushroom_v21_backtest_{args.dataset}_latest.md",
        "latest_decisions_csv": EDGE_DIR / f"codex_mushroom_v21_backtest_decisions_{args.dataset}_latest.csv",
    }
    if args.write:
        write_json(artifacts["summary_json"], summary)
        write_csv(artifacts["decisions_csv"], rows)
        artifacts["report"].write_text(render_report(summary, rows, artifacts), encoding="utf-8")
        shutil.copyfile(artifacts["summary_json"], artifacts["latest_summary"])
        shutil.copyfile(artifacts["report"], artifacts["latest_report"])
        shutil.copyfile(artifacts["decisions_csv"], artifacts["latest_decisions_csv"])
    summary["artifacts"] = {key: str(value) for key, value in artifacts.items()}
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest Mushroom v21 static field on Research Lab gauntlet decision points.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--source-candidate-id", default=DEFAULT_SOURCE_CANDIDATE_ID)
    parser.add_argument("--position-size", type=int, default=DEFAULT_POSITION_SIZE)
    parser.add_argument("--min-p-side", type=float, default=DEFAULT_MIN_P_SIDE)
    parser.add_argument("--strict-p-side", type=float, default=DEFAULT_STRICT_P_SIDE)
    parser.add_argument("--min-edge-cents", type=float, default=DEFAULT_MIN_EDGE_CENTS)
    parser.add_argument("--slippage-cents", type=float, default=DEFAULT_SLIPPAGE_CENTS)
    parser.add_argument("--max-quote-age-ms", type=float, default=DEFAULT_MAX_QUOTE_AGE_MS)
    parser.add_argument("--refresh-market-cache", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    summary = run_backtest(args)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
