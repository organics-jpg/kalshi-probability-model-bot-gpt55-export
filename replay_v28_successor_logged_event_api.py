"""Replay the v28 FV API on logged-event rows with cached BTC bars.

Research-only. This reconstructs the v28 engine state from the local Coinbase
1m bar cache and evaluates the logged-event causal rows. It never touches live
bot state, orders, thresholds, secrets, or processes.

The replay is useful for validating the v28 API surface and component columns,
but it is not promotion evidence: the BTC state is reconstructed from a cache
and the labels remain posthoc diagnostic labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

import pandas as pd

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config
from replay_v28_successor_baselines import as_float, rel_path, sha256_file


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

LOGGED_ROWS_CSV = OUT_DIR / "causal_rows_logged_events_latest.csv"
BTC_1M_CACHE = EDGE_DIR / "coinbase_btc_usd_1m_cache.parquet"

API_REPLAY_CSV = OUT_DIR / "v28_logged_event_api_replay_latest.csv"
API_REPLAY_JSON = OUT_DIR / "v28_logged_event_api_replay_latest.json"
API_REPLAY_SUMMARY_JSON = EDGE_DIR / "v28_successor_logged_event_api_replay_latest.json"
API_REPLAY_SUMMARY_MD = EDGE_DIR / "v28_successor_logged_event_api_replay_latest.md"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
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


def iso_z(value: Any) -> str | None:
    parsed = parse_ts(value)
    if parsed is None:
        return None
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_csv_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
            if limit_rows is not None and len(rows) >= limit_rows:
                break
    return rows


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_btc_bars(path: Path = BTC_1M_CACHE) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    columns = ["open_dt", "close_dt", "open", "high", "low", "close", "volume"]
    frame = pd.read_parquet(path, columns=columns)
    frame = frame.dropna(subset=["open_dt", "close_dt", "open", "high", "low", "close"])
    frame = frame.sort_values("close_dt").reset_index(drop=True)
    return frame


def component_scalar(components: dict[str, Any], key: str, index: int = 0) -> float | None:
    value = components.get(key)
    if value is None:
        return None
    try:
        if hasattr(value, "__len__") and not isinstance(value, (str, bytes)):
            return float(value[index])
        return float(value)
    except (TypeError, ValueError, IndexError):
        return None


def finite_delta(a: Any, b: Any) -> float | None:
    left = as_float(a)
    right = as_float(b)
    if left is None or right is None:
        return None
    return left - right


def summarize_deltas(values: list[float]) -> dict[str, float | None]:
    clean = sorted(value for value in values if math.isfinite(value))
    if not clean:
        return {"count": 0, "mean_abs": None, "median_abs": None, "p95_abs": None, "max_abs": None}
    abs_values = sorted(abs(value) for value in clean)
    p95_index = min(len(abs_values) - 1, int(math.ceil(0.95 * len(abs_values)) - 1))
    return {
        "count": len(clean),
        "mean_abs": sum(abs_values) / len(abs_values),
        "median_abs": median(abs_values),
        "p95_abs": abs_values[p95_index],
        "max_abs": abs_values[-1],
    }


def feed_bars_until(engine: FastMushroomFVEngineV28, bars: pd.DataFrame, next_bar_idx: int, decision_ts: datetime) -> tuple[int, int]:
    fed = 0
    total = len(bars)
    while next_bar_idx < total:
        row = bars.iloc[next_bar_idx]
        close_dt = row["close_dt"]
        close_ts = close_dt.to_pydatetime() if hasattr(close_dt, "to_pydatetime") else close_dt
        if close_ts.tzinfo is None:
            close_ts = close_ts.replace(tzinfo=timezone.utc)
        close_ts = close_ts.astimezone(timezone.utc)
        if close_ts > decision_ts:
            break
        engine.update_bar(
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0) or 0.0),
            ts=close_ts,
        )
        next_bar_idx += 1
        fed += 1
    return next_bar_idx, fed


def bar_index_at_or_before(bars: pd.DataFrame, decision_ts: datetime) -> int:
    if bars.empty:
        return 0
    close_values = bars["close_dt"]
    target = pd.Timestamp(decision_ts)
    return int(close_values.searchsorted(target, side="right"))


def warmup_engine_from_first_row(
    engine: FastMushroomFVEngineV28,
    bars: pd.DataFrame,
    sortable_rows: list[tuple[datetime, dict[str, Any]]],
) -> tuple[int, int, int]:
    if bars.empty or not sortable_rows:
        return 0, 0, 0
    first_decision_ts, first_row = sortable_rows[0]
    if first_decision_ts.year == datetime.max.year:
        return 0, 0, 0
    end_idx = bar_index_at_or_before(bars, first_decision_ts)
    logged_history = as_float(first_row.get("history_bars"))
    if logged_history is None or logged_history <= 0:
        warmup_bars = int(FastMushroomV28Config().min_bars)
    else:
        warmup_bars = int(max(FastMushroomV28Config().min_bars, min(logged_history, end_idx)))
    start_idx = max(0, end_idx - warmup_bars)
    fed = 0
    for idx in range(start_idx, end_idx):
        row = bars.iloc[idx]
        close_dt = row["close_dt"]
        close_ts = close_dt.to_pydatetime() if hasattr(close_dt, "to_pydatetime") else close_dt
        if close_ts.tzinfo is None:
            close_ts = close_ts.replace(tzinfo=timezone.utc)
        close_ts = close_ts.astimezone(timezone.utc)
        engine.update_bar(
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0) or 0.0),
            ts=close_ts,
        )
        fed += 1
    return end_idx, fed, start_idx


def cache_latest_bar_before(bars: pd.DataFrame, bar_idx: int) -> dict[str, Any]:
    if bars.empty or bar_idx <= 0:
        return {"close_dt": None, "close": None}
    row = bars.iloc[bar_idx - 1]
    close_dt = row["close_dt"]
    return {
        "close_dt": iso_z(close_dt.to_pydatetime() if hasattr(close_dt, "to_pydatetime") else close_dt),
        "close": float(row["close"]),
    }


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = read_csv_rows(LOGGED_ROWS_CSV, limit_rows=limit_rows)
    bars = load_btc_bars()
    engine = FastMushroomFVEngineV28(FastMushroomV28Config())
    outputs: list[dict[str, Any]] = []

    sortable_rows = []
    for row in rows:
        decision_ts = parse_ts(row.get("decision_ts_utc"))
        sortable_rows.append((decision_ts or datetime.max.replace(tzinfo=timezone.utc), row))
    sortable_rows = sorted(sortable_rows, key=lambda item: (item[0], str(item[1].get("row_id") or "")))
    next_bar_idx, total_bars_fed, warmup_start_idx = warmup_engine_from_first_row(engine, bars, sortable_rows)
    warmup_end_idx = next_bar_idx

    for decision_ts, row in sortable_rows:
        if decision_ts.year == datetime.max.year:
            outputs.append(blocked_row(row, "missing_or_unparseable_decision_ts", next_bar_idx, bars))
            continue
        if bars.empty:
            outputs.append(blocked_row(row, "missing_btc_1m_cache", next_bar_idx, bars))
            continue
        next_bar_idx, fed = feed_bars_until(engine, bars, next_bar_idx, decision_ts)
        total_bars_fed += fed
        latest_bar = cache_latest_bar_before(bars, next_bar_idx)
        strike = as_float(row.get("strike"))
        seconds_to_close = as_float(row.get("seconds_to_close"))
        if strike is None:
            outputs.append(blocked_row(row, "missing_strike", next_bar_idx, bars, latest_bar))
            continue
        if seconds_to_close is None or seconds_to_close <= 0.0:
            outputs.append(blocked_row(row, "missing_or_nonpositive_seconds_to_close", next_bar_idx, bars, latest_bar))
            continue
        if not engine.ready():
            outputs.append(blocked_row(row, "v28_engine_not_ready_after_predecision_bars", next_bar_idx, bars, latest_bar))
            continue

        logged_btc = as_float(row.get("btc_price"))
        if logged_btc is not None:
            engine.last_live_price = float(logged_btc)
            engine.last_live_ts = decision_ts

        try:
            prediction = engine.predict_many(strikes=[strike], horizon_seconds=seconds_to_close)
        except Exception as exc:  # pragma: no cover - defensive artifact row
            outputs.append(blocked_row(row, f"v28_api_error:{type(exc).__name__}", next_bar_idx, bars, latest_bar))
            continue

        components = prediction.components
        replay_p_yes = float(prediction.p_yes[0])
        replay_fair_yes = float(prediction.fair_yes_cents[0])
        replay_fair_no = float(prediction.fair_no_cents[0])
        replay_sigma = float(prediction.sigma_t_dollars)
        replay_d_sigma = float(prediction.d_sigma[0])
        cache_gap_seconds = None
        if latest_bar["close_dt"] is not None:
            latest_ts = parse_ts(latest_bar["close_dt"])
            if latest_ts is not None:
                cache_gap_seconds = max(0.0, (decision_ts - latest_ts).total_seconds())
        out = {
            "row_id": row.get("row_id"),
            "market_ticker": row.get("market_ticker"),
            "decision_ts_utc": row.get("decision_ts_utc"),
            "market_close_ts_utc": row.get("market_close_ts_utc"),
            "source_type": row.get("source_type"),
            "source_quality_tier": row.get("source_quality_tier"),
            "side": row.get("side"),
            "strike": strike,
            "seconds_to_close": seconds_to_close,
            "replay_status": "replayed_v28_api_from_predecision_btc_cache",
            "allowed_for_forward_promotion": False,
            "promotion_exclusion_reason": "reconstructed_btc_cache_and_posthoc_labels_not_frozen_forward_evidence",
            "btc_cache_bars_loaded_before_decision": next_bar_idx,
            "btc_cache_latest_close_ts_utc": latest_bar["close_dt"],
            "btc_cache_latest_close": latest_bar["close"],
            "btc_cache_gap_to_decision_seconds": cache_gap_seconds,
            "logged_btc_price": logged_btc,
            "replay_spot": float(prediction.spot),
            "replay_minus_logged_btc_price": finite_delta(float(prediction.spot), logged_btc),
            "logged_v28_p_yes": as_float(row.get("v28_p_yes")),
            "replay_v28_p_yes": replay_p_yes,
            "replay_minus_logged_v28_p_yes": finite_delta(replay_p_yes, row.get("v28_p_yes")),
            "logged_v28_fair_yes_cents": as_float(row.get("v28_fair_yes_cents")),
            "replay_v28_fair_yes_cents": replay_fair_yes,
            "replay_minus_logged_fair_yes_cents": finite_delta(replay_fair_yes, row.get("v28_fair_yes_cents")),
            "replay_v28_fair_no_cents": replay_fair_no,
            "logged_sigma_t_dollars": as_float(row.get("sigma_t_dollars")),
            "replay_sigma_t_dollars": replay_sigma,
            "replay_minus_logged_sigma_t_dollars": finite_delta(replay_sigma, row.get("sigma_t_dollars")),
            "logged_d_sigma": as_float(row.get("d_sigma")),
            "replay_d_sigma": replay_d_sigma,
            "replay_minus_logged_d_sigma": finite_delta(replay_d_sigma, row.get("d_sigma")),
            "replay_p_anchor": component_scalar(components, "p_anchor"),
            "replay_p_static_boundary_field": component_scalar(components, "p_static_boundary_field"),
            "replay_p_recent_transport": component_scalar(components, "p_recent_transport"),
            "replay_p_long_transport": component_scalar(components, "p_long_transport"),
            "replay_edge_gate": component_scalar(components, "edge_gate"),
            "replay_static_gate": component_scalar(components, "static_gate"),
            "replay_arrow": component_scalar(components, "arrow"),
            "replay_volshock": component_scalar(components, "volshock"),
            "replay_transport_recent_n": component_scalar(components, "transport_recent_n"),
            "replay_transport_long_n": component_scalar(components, "transport_long_n"),
            "replay_learned_horizon_minutes": component_scalar(components, "learned_horizon_minutes"),
            "replay_effective_horizon_minutes": component_scalar(components, "effective_horizon_minutes"),
        }
        outputs.append(out)

    replayed = [row for row in outputs if row.get("replay_status") == "replayed_v28_api_from_predecision_btc_cache"]
    p_deltas = [float(row["replay_minus_logged_v28_p_yes"]) for row in replayed if as_float(row.get("replay_minus_logged_v28_p_yes")) is not None]
    fair_deltas = [float(row["replay_minus_logged_fair_yes_cents"]) for row in replayed if as_float(row.get("replay_minus_logged_fair_yes_cents")) is not None]
    spot_deltas = [float(row["replay_minus_logged_btc_price"]) for row in replayed if as_float(row.get("replay_minus_logged_btc_price")) is not None]
    component_fields = [
        "replay_p_anchor",
        "replay_p_static_boundary_field",
        "replay_p_recent_transport",
        "replay_p_long_transport",
        "replay_arrow",
        "replay_transport_recent_n",
        "replay_transport_long_n",
    ]
    if not bars.empty:
        cache_start = iso_z(bars.iloc[0]["open_dt"].to_pydatetime() if hasattr(bars.iloc[0]["open_dt"], "to_pydatetime") else bars.iloc[0]["open_dt"])
        cache_end = iso_z(bars.iloc[-1]["close_dt"].to_pydatetime() if hasattr(bars.iloc[-1]["close_dt"], "to_pydatetime") else bars.iloc[-1]["close_dt"])
    else:
        cache_start = None
        cache_end = None
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "replay_verdict": (
            "research_reconstructed_v28_api_replay_available_not_promotion"
            if replayed
            else "blocked_no_replayable_rows"
        ),
        "row_count": len(outputs),
        "replayed_rows": len(replayed),
        "blocked_rows": len(outputs) - len(replayed),
        "market_count": len({str(row.get("market_ticker") or "") for row in outputs if row.get("market_ticker")}),
        "component_coverage": {
            field: sum(1 for row in replayed if as_float(row.get(field)) is not None)
            for field in component_fields
        },
        "delta_summary": {
            "p_yes": summarize_deltas(p_deltas),
            "fair_yes_cents": summarize_deltas(fair_deltas),
            "spot_dollars": summarize_deltas(spot_deltas),
        },
        "blocked_reason_counts": count_blocked_reasons(outputs),
        "inputs": {
            "logged_rows_csv": rel_path(LOGGED_ROWS_CSV),
            "logged_rows_hash": sha256_file(LOGGED_ROWS_CSV),
            "btc_1m_cache": rel_path(BTC_1M_CACHE),
            "btc_1m_cache_hash": sha256_file(BTC_1M_CACHE),
            "btc_cache_rows": int(len(bars)),
            "btc_cache_start_utc": cache_start,
            "btc_cache_end_utc": cache_end,
            "bars_fed_to_engine": total_bars_fed,
            "warmup_start_bar_index": warmup_start_idx,
            "warmup_end_bar_index": warmup_end_idx,
        },
        "promotion_status": {
            "allowed_for_forward_promotion": False,
            "reason": "research replay uses reconstructed BTC cache and posthoc labels; it is not a frozen pre-settlement candidate registry",
        },
        "outputs": {
            "csv": rel_path(API_REPLAY_CSV),
            "json": rel_path(API_REPLAY_JSON),
            "summary_json": rel_path(API_REPLAY_SUMMARY_JSON),
            "summary_md": rel_path(API_REPLAY_SUMMARY_MD),
        },
    }
    return outputs, summary


def blocked_row(
    row: dict[str, Any],
    reason: str,
    bar_idx: int,
    bars: pd.DataFrame,
    latest_bar: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest_bar = latest_bar or cache_latest_bar_before(bars, bar_idx)
    return {
        "row_id": row.get("row_id"),
        "market_ticker": row.get("market_ticker"),
        "decision_ts_utc": row.get("decision_ts_utc"),
        "market_close_ts_utc": row.get("market_close_ts_utc"),
        "source_type": row.get("source_type"),
        "source_quality_tier": row.get("source_quality_tier"),
        "side": row.get("side"),
        "strike": as_float(row.get("strike")),
        "seconds_to_close": as_float(row.get("seconds_to_close")),
        "replay_status": "blocked",
        "blocked_reason": reason,
        "allowed_for_forward_promotion": False,
        "promotion_exclusion_reason": "not_replayable_or_not_frozen_forward_evidence",
        "btc_cache_bars_loaded_before_decision": bar_idx,
        "btc_cache_latest_close_ts_utc": latest_bar.get("close_dt"),
        "btc_cache_latest_close": latest_bar.get("close"),
        "logged_v28_p_yes": as_float(row.get("v28_p_yes")),
        "logged_v28_fair_yes_cents": as_float(row.get("v28_fair_yes_cents")),
    }


def count_blocked_reasons(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if row.get("replay_status") == "blocked":
            reason = str(row.get("blocked_reason") or "unknown")
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Logged-Event API Replay",
        "",
        "Research-only reconstructed replay. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Replay verdict: `{summary['replay_verdict']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Replayed rows: `{summary['replayed_rows']}`",
        f"- Blocked rows: `{summary['blocked_rows']}`",
        f"- Markets: `{summary['market_count']}`",
        f"- BTC cache: `{summary['inputs']['btc_cache_start_utc']}` to `{summary['inputs']['btc_cache_end_utc']}` rows=`{summary['inputs']['btc_cache_rows']}`",
        f"- Bars fed to v28 engine: `{summary['inputs']['bars_fed_to_engine']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed_for_forward_promotion']}`",
        "",
        "## Delta Summary",
        "",
        "| quantity | count | mean abs | median abs | p95 abs | max abs |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, values in summary["delta_summary"].items():
        lines.append(
            f"| `{name}` | {values['count']} | {fmt(values['mean_abs'])} | {fmt(values['median_abs'])} | {fmt(values['p95_abs'])} | {fmt(values['max_abs'])} |"
        )
    lines.extend(
        [
            "",
            "## Component Coverage",
            "",
            "| component | rows |",
            "|---|---:|",
        ]
    )
    for field, count in summary["component_coverage"].items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(
        [
            "",
            "## Blocked Reasons",
            "",
            "| reason | rows |",
            "|---|---:|",
        ]
    )
    for reason, count in summary["blocked_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is the first true v28 API call path in the successor pipeline.",
            "- It proves the replay harness can regenerate v28 component columns from predecision BTC bars and logged market geometry.",
            "- It is not exact live-state replay because the original tick stream and serialized live engine transport state were not captured with each decision.",
            "- It is not promotion evidence because labels are still posthoc diagnostic labels and no frozen forward candidate predictions are registered.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "NA"
    return f"{parsed:.8f}"


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, API_REPLAY_CSV)
    API_REPLAY_JSON.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    API_REPLAY_SUMMARY_JSON.write_text(json.dumps({"summary": summary, "sample_rows": rows[:50]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(rows, summary, API_REPLAY_SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write replay artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional row limit for quick checks.")
    args = parser.parse_args()
    rows, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "replay_verdict": summary["replay_verdict"],
                "row_count": summary["row_count"],
                "replayed_rows": summary["replayed_rows"],
                "blocked_rows": summary["blocked_rows"],
                "p_yes_delta": summary["delta_summary"]["p_yes"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
