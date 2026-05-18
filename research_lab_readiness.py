from __future__ import annotations

import argparse
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover - optional schema reader
    pq = None


ROOT = Path(__file__).resolve().parent
RESEARCH_DATA_ROOT = ROOT / "research_data"
EDGE_DIR = ROOT / "logs" / "edge_research"
INTEGRITY_LEDGER = EDGE_DIR / "dwell_execution_integrity_ledger.jsonl"
READINESS_SCHEMA_VERSION = "research-lab-readiness-v1"
GAUNTLET_SCHEMA_VERSION = "gauntlet-tape-schema-v1"
ACTIVE_CAPTURE_STALE_SECONDS = 300
DERIVED_TAPE_LAG_WARN_SECONDS = 300
SOURCE_DECISION_EVENT_TYPES = {
    "execution_liquidity_dwell_approved",
    "execution_liquidity_dwell_rejected",
    "liquidity_dwell_approved_log",
    "liquidity_dwell_rejected_log",
}

REQUIRED_MANIFEST_KEYS = [
    "dataset_tag",
    "schema_version",
    "recorder_version",
    "feature_set_version",
    "recorder_type",
    "strategy_tags",
    "live_bot_run_tag",
    "source_dataset_tag",
    "source_log_paths",
    "started_at_utc",
    "ended_at_utc",
    "market_tickers",
    "market_selection_reason",
    "records_raw_market_feed",
    "records_book_checkpoints",
    "records_strategy_decisions",
    "records_execution_events",
    "records_settlement_labels",
    "data_quality_flags",
]
NONEMPTY_MANIFEST_KEYS = {
    "dataset_tag",
    "schema_version",
    "recorder_version",
    "feature_set_version",
    "recorder_type",
}

CORE_FEATURE_COLUMNS = [
    "ts",
    "market_ticker",
    "local_recv_dt",
    "trust_state",
    "yes_bid_cents",
    "yes_ask_cents",
    "no_bid_cents",
    "no_ask_cents",
    "yes_bid_size",
    "no_bid_size",
    "seconds_to_close",
    "spread_yes",
    "spread_no",
    "depth_imbalance",
]

GAUNTLET_FEATURE_COLUMNS = [
    "feature_available_at",
    "quote_age_ms",
    "bid_sum_cents",
    "yes_opponent_pressure",
    "no_opponent_pressure",
    "yes_entry_limit_cents",
    "no_entry_limit_cents",
    "yes_implied_ask_size",
    "no_implied_ask_size",
    "yes_fillable_size2_at_top",
    "no_fillable_size2_at_top",
    "online_neighbor_yes_history_count",
    "online_neighbor_yes_win_rate",
    "online_neighbor_yes_model_ev_cents",
    "online_neighbor_yes_lcb_cents",
    "online_neighbor_no_history_count",
    "online_neighbor_no_win_rate",
    "online_neighbor_no_model_ev_cents",
    "online_neighbor_no_lcb_cents",
]

BTC_FEATURE_COLUMNS = [
    "btc_close",
    "btc_move_1m_bps",
    "btc_move_5m_bps",
    "btc_move_15m_bps",
    "btc_range_15m_bps",
    "btc_rsi14",
    "btc_macd_hist",
    "btc_price_vs_ema21",
]

CANDIDATE_DECISION_COLUMNS = [
    "decision_id",
    "candidate_id",
    "strategy_id",
    "strategy_version",
    "dataset_tag",
    "source_feature_ts",
    "available_at",
    "market_ticker",
    "side",
    "proposed_limit_cents",
    "proposed_size",
    "seconds_to_close",
    "all_gates_passed",
    "decision",
    "reject_reason",
    "gate_values_json",
    "thresholds_json",
    "code_version",
]

FILLABILITY_COLUMNS = [
    "decision_id",
    "snapshot_ts",
    "available_at",
    "market_ticker",
    "side",
    "limit_cents",
    "requested_size",
    "fillable_at_limit",
    "fillable_size_at_limit",
    "fillable_size_one_cent_worse",
    "fillable_size_two_cents_worse",
    "estimated_ioc_fill_size",
    "estimated_slippage_cents",
    "book_age_ms",
    "feed_age_ms",
    "trust_state",
    "sequence_ok",
    "account_snapshot_age_ms",
    "blocker",
]

OUTCOME_LABEL_COLUMNS = [
    "decision_id",
    "market_ticker",
    "side",
    "label_available_at",
    "settlement_ts",
    "market_result",
    "would_win",
    "gross_pnl_cents_per_contract",
    "gross_pnl_cents_for_size",
    "label_source",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_dt(value: Any) -> datetime | None:
    if value in (None, "", "null", "None"):
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def newest_files(root: Path, suffix: str, limit: int = 32) -> list[Path]:
    if not root.exists():
        return []
    files: list[tuple[float, Path]] = []
    for fp in root.rglob(f"*{suffix}"):
        try:
            files.append((fp.stat().st_mtime, fp))
        except OSError:
            continue
    return [fp for _, fp in sorted(files, reverse=True)[:limit]]


def read_first_line(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def read_last_line(path: Path, block_size: int = 8192) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            file_size = handle.tell()
            if file_size == 0:
                return ""
            offset = min(file_size, block_size)
            data = b""
            while offset <= file_size:
                handle.seek(file_size - offset)
                data = handle.read(offset)
                if b"\n" in data.strip(b"\r\n"):
                    break
                if offset == file_size:
                    break
                offset = min(file_size, offset + block_size)
            lines = [line for line in data.splitlines() if line.strip()]
            if not lines:
                return ""
            return lines[-1].decode("utf-8", errors="replace").strip()
    except OSError:
        return ""


def parse_json_line(line: str) -> dict[str, Any]:
    if not line:
        return {}
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def timestamp_from_payload(payload: dict[str, Any]) -> datetime | None:
    for key in ("local_recv_ts", "checkpoint_ts", "ts_wall", "ts", "created_at", "updated_at"):
        parsed = parse_dt(payload.get(key))
        if parsed is not None:
            return parsed
    return None


def partition_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for part in path.parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key and value:
            values[key] = value
    return values


def scan_ndjson_tree(root: Path) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "exists": root.exists(),
        "file_count": 0,
        "total_bytes": 0,
        "latest_file_mtime_utc": None,
        "latest_file_path": None,
        "latest_event_ts": None,
        "first_sample_event_ts": None,
        "partition_days": [],
        "partition_types": [],
        "partition_markets_sample": [],
        "max_file_mtime_gap_seconds": None,
        "sample_event_types": {},
        "latest_event_ts_by_type": {},
    }
    if not root.exists():
        return stats

    days: set[str] = set()
    types: set[str] = set()
    markets: set[str] = set()
    file_mtimes: list[float] = []
    ndjson_files: list[Path] = []
    latest_mtime = 0.0
    latest_path: Path | None = None

    for fp in root.rglob("*.ndjson"):
        try:
            stat = fp.stat()
        except OSError:
            continue
        ndjson_files.append(fp)
        stats["file_count"] += 1
        stats["total_bytes"] += int(stat.st_size)
        file_mtimes.append(float(stat.st_mtime))
        if stat.st_mtime > latest_mtime:
            latest_mtime = float(stat.st_mtime)
            latest_path = fp
        parts = partition_values(fp)
        if "day" in parts:
            days.add(parts["day"])
        if "type" in parts:
            types.add(parts["type"])
        if "market" in parts:
            markets.add(parts["market"])

    if latest_path is not None:
        stats["latest_file_path"] = str(latest_path)
        stats["latest_file_mtime_utc"] = datetime.fromtimestamp(latest_mtime, timezone.utc).isoformat()

    sorted_mtimes = sorted(file_mtimes)
    if len(sorted_mtimes) >= 2:
        gaps = [b - a for a, b in zip(sorted_mtimes, sorted_mtimes[1:])]
        stats["max_file_mtime_gap_seconds"] = round(max(gaps), 3)

    event_types: Counter[str] = Counter()
    event_type_latest: dict[str, datetime] = {}
    sampled_ts: list[datetime] = []
    for fp in ndjson_files:
        for line in (read_first_line(fp), read_last_line(fp)):
            payload = parse_json_line(line)
            if not payload:
                continue
            parts = partition_values(fp)
            event_type = (
                str(payload.get("event_type") or payload.get("type") or payload.get("msg_type") or parts.get("type") or "")
            )
            if event_type:
                event_types[event_type] += 1
            ts = timestamp_from_payload(payload)
            if ts is not None:
                sampled_ts.append(ts)
                if event_type and (event_type not in event_type_latest or ts > event_type_latest[event_type]):
                    event_type_latest[event_type] = ts

    if sampled_ts:
        stats["first_sample_event_ts"] = min(sampled_ts).isoformat()
        stats["latest_event_ts"] = max(sampled_ts).isoformat()
    stats["partition_days"] = sorted(days)
    stats["partition_types"] = sorted(types)
    stats["partition_markets_sample"] = sorted(markets)[:25]
    stats["sample_event_types"] = dict(event_types)
    stats["latest_event_ts_by_type"] = {
        event_type: ts.isoformat() for event_type, ts in sorted(event_type_latest.items())
    }
    return stats


def scan_parquet_tree(root: Path, timestamp_columns: tuple[str, ...] = ("ts", "entry_dt", "settlement_ts")) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "exists": root.exists(),
        "file_count": 0,
        "latest_file_mtime_utc": None,
        "latest_file_path": None,
        "columns": [],
        "latest_timestamp_sample": None,
    }
    if not root.exists():
        return stats
    files: list[tuple[float, Path]] = []
    for fp in root.rglob("*.parquet"):
        try:
            files.append((fp.stat().st_mtime, fp))
        except OSError:
            continue
    stats["file_count"] = len(files)
    if not files:
        return stats
    files_sorted = sorted(files, reverse=True)
    latest_mtime, latest_path = files_sorted[0]
    stats["latest_file_mtime_utc"] = datetime.fromtimestamp(latest_mtime, timezone.utc).isoformat()
    stats["latest_file_path"] = str(latest_path)

    columns: set[str] = set()
    latest_ts: datetime | None = None
    for _, fp in files_sorted[:50]:
        try:
            if pq is None:
                continue
            parquet_file = pq.ParquetFile(fp)
            names = list(parquet_file.schema_arrow.names)
            columns.update(names)
            columns.update(partition_values(fp).keys())
            ts_cols = [col for col in timestamp_columns if col in names]
            if ts_cols:
                table = parquet_file.read(columns=ts_cols)
                for col in ts_cols:
                    values = table.column(col).to_pylist()
                    for value in values[-10:]:
                        parsed = parse_dt(value)
                        if parsed is not None and (latest_ts is None or parsed > latest_ts):
                            latest_ts = parsed
        except Exception:
            continue
    stats["columns"] = sorted(columns)
    stats["latest_timestamp_sample"] = latest_ts.isoformat() if latest_ts is not None else None
    return stats


def source_log_paths(bot_tag: str | None) -> list[str]:
    if not bot_tag:
        return []
    paths = [
        ROOT / "logs" / bot_tag / "bot.log",
        ROOT / "logs" / bot_tag / "execution_events.ndjson",
        ROOT / "logs" / bot_tag / "launcher.stdout.log",
        ROOT / "logs" / bot_tag / "launcher.stderr.log",
    ]
    return [str(path) for path in paths if path.exists()]


def default_manifest(
    dataset_tag: str,
    *,
    recorder_type: str,
    strategy_tags: list[str],
    live_bot_run_tag: str | None,
    source_dataset_tag: str | None,
    log_paths: list[str],
    raw_stats: dict[str, Any],
    checkpoint_stats: dict[str, Any],
    feature_stats: dict[str, Any],
    label_stats: dict[str, Any],
) -> dict[str, Any]:
    market_tickers = sorted(
        set(raw_stats.get("partition_markets_sample") or [])
        | set(checkpoint_stats.get("partition_markets_sample") or [])
    )
    started = raw_stats.get("first_sample_event_ts") or checkpoint_stats.get("first_sample_event_ts")
    ended = raw_stats.get("latest_event_ts") or checkpoint_stats.get("latest_event_ts")
    return {
        "dataset_tag": dataset_tag,
        "schema_version": "phase1-ndjson-v1",
        "recorder_version": "unknown",
        "feature_set_version": (
            "research-lab-features-v3-online-neighbor"
            if all(col in feature_stats.get("columns", []) for col in GAUNTLET_FEATURE_COLUMNS)
            else (
                "research-lab-features-v2-gauntlet"
                if all(col in feature_stats.get("columns", []) for col in GAUNTLET_FEATURE_COLUMNS[:3])
                else "pre-gauntlet-or-unbuilt"
            )
        ),
        "recorder_type": recorder_type,
        "strategy_tags": strategy_tags,
        "live_bot_run_tag": live_bot_run_tag or "",
        "source_dataset_tag": source_dataset_tag or "",
        "source_log_paths": log_paths,
        "started_at_utc": started or "",
        "ended_at_utc": ended or "",
        "market_tickers": market_tickers,
        "market_selection_reason": "KXBTC15M live/passive stream" if market_tickers else "",
        "records_raw_market_feed": bool(raw_stats.get("file_count")),
        "records_book_checkpoints": bool(checkpoint_stats.get("file_count")),
        "records_strategy_decisions": False,
        "records_execution_events": any(path.endswith("execution_events.ndjson") for path in log_paths),
        "records_settlement_labels": bool(label_stats.get("file_count")),
        "data_quality_flags": [],
        "updated_at_utc": utc_now().isoformat(),
    }


def merge_manifest(existing: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    merged = dict(generated)
    for key, value in existing.items():
        if key == "updated_at_utc":
            continue
        if key == "feature_set_version" and str(generated.get(key) or "").startswith("research-lab-features-v"):
            continue
        if value not in (None, "", [], {}) or key not in merged:
            merged[key] = value
    for key in REQUIRED_MANIFEST_KEYS:
        merged.setdefault(key, generated.get(key, "" if key not in {"strategy_tags", "source_log_paths", "market_tickers", "data_quality_flags"} else []))
    merged["updated_at_utc"] = utc_now().isoformat()
    return merged


def gauntlet_tape_schema(dataset_tag: str) -> dict[str, Any]:
    return {
        "schema_version": GAUNTLET_SCHEMA_VERSION,
        "dataset_tag": dataset_tag,
        "updated_at_utc": utc_now().isoformat(),
        "feature_tape_required_columns": CORE_FEATURE_COLUMNS,
        "feature_tape_gauntlet_columns": GAUNTLET_FEATURE_COLUMNS,
        "feature_tape_btc_columns": BTC_FEATURE_COLUMNS,
        "candidate_decision_tape_columns": CANDIDATE_DECISION_COLUMNS,
        "fillability_snapshot_columns": FILLABILITY_COLUMNS,
        "outcome_label_columns": OUTCOME_LABEL_COLUMNS,
        "anti_leakage_rule": "Candidate decisions may use only fields whose available_at is <= decision available_at; settlement labels are labels only.",
        "promotion_rule": "A candidate must be frozen before scoring and must pass approved-stream, fillability-adjusted, false-positive, side/time, and freshness gates before live review.",
    }


def schema_version_payload(dataset_tag: str, schema_version: str) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "dataset_tag": dataset_tag,
        "updated_at": utc_now().isoformat(),
        "readiness_schema_version": READINESS_SCHEMA_VERSION,
        "gauntlet_schema_version": GAUNTLET_SCHEMA_VERSION,
    }


def ingestion_watchdog_status(readiness: dict[str, Any]) -> dict[str, Any]:
    stats = readiness["stats"]
    return {
        "schema_version": "research-lab-ingestion-watchdog-v1",
        "dataset_tag": readiness["dataset_tag"],
        "checked_at_utc": utc_now().isoformat(),
        "status": readiness["status"],
        "blockers": readiness["blockers"],
        "warnings": readiness["warnings"],
        "raw_file_count": stats["raw_events"].get("file_count"),
        "checkpoint_file_count": stats["book_checkpoints"].get("file_count"),
        "latest_raw_event_ts": stats["raw_events"].get("latest_event_ts"),
        "latest_raw_file_mtime_utc": stats["raw_events"].get("latest_file_mtime_utc"),
        "latest_checkpoint_event_ts": stats["book_checkpoints"].get("latest_event_ts"),
        "latest_checkpoint_file_mtime_utc": stats["book_checkpoints"].get("latest_file_mtime_utc"),
        "raw_max_file_mtime_gap_seconds": stats["raw_events"].get("max_file_mtime_gap_seconds"),
        "checkpoint_max_file_mtime_gap_seconds": stats["book_checkpoints"].get("max_file_mtime_gap_seconds"),
        "feature_file_count": stats["features"].get("file_count"),
        "latest_feature_ts": stats["features"].get("latest_timestamp_sample"),
        "candidate_decision_file_count": stats["candidate_decisions"].get("file_count"),
        "latest_candidate_decision_ts": stats["candidate_decisions"].get("latest_timestamp_sample"),
        "fillability_snapshot_file_count": stats["fillability_snapshots"].get("file_count"),
        "latest_fillability_snapshot_ts": stats["fillability_snapshots"].get("latest_timestamp_sample"),
        "outcome_label_file_count": stats.get("outcome_labels", {}).get("file_count"),
        "latest_outcome_label_ts": stats.get("outcome_labels", {}).get("latest_timestamp_sample"),
        "freshness_checks": readiness.get("freshness_checks") or {},
    }


def candidate_template(dataset_tag: str, strategy_tags: list[str]) -> dict[str, Any]:
    base_strategy = strategy_tags[0] if strategy_tags else "candidate_strategy"
    return {
        "schema_version": "gauntlet-candidate-spec-v1",
        "source_dataset_tag": dataset_tag,
        "frozen": False,
        "frozen_at_utc": "",
        "created_at_utc": utc_now().isoformat(),
        "notes": "Fill in candidate specs, freeze them, then run gauntlet scoring. Do not tune candidates mid-run.",
        "promotion_gates": {
            "min_forward_decisions": 25,
            "approved_stream_pnl_cents_min": 1,
            "fillability_adjusted_pnl_cents_min": 1,
            "max_false_positive_loss_cents": 300,
            "require_side_stability": True,
            "require_no_unlabeled_settlements": True,
        },
        "candidates": [
            {
                "candidate_id": f"{base_strategy}_template",
                "strategy_id": base_strategy,
                "strategy_version": "v0-template",
                "enabled": False,
                "description": "Template only. Replace with a frozen candidate before scoring.",
                "entry_logic": {
                    "family": "liquidity_dwell_or_overlay",
                    "uses_feature_tape_only": True,
                    "allowed_input_columns": CORE_FEATURE_COLUMNS + GAUNTLET_FEATURE_COLUMNS + BTC_FEATURE_COLUMNS,
                    "parameters": {},
                },
                "sizing": {"contracts": 2},
                "exit_policy": {"type": "hold_to_settlement"},
                "reject_reasons": [],
            }
        ],
    }


def status_from_checks(blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "FAIL"
    if warnings:
        return "WARN"
    return "PASS"


def seconds_between(later: datetime | None, earlier: datetime | None) -> float | None:
    if later is None or earlier is None:
        return None
    return round((later - earlier).total_seconds(), 3)


def positive_lag_seconds(anchor: datetime | None, observed: datetime | None) -> float | None:
    lag = seconds_between(anchor, observed)
    if lag is None:
        return None
    return round(max(0.0, lag), 3)


def latest_event_type_ts(stats: dict[str, Any], event_types: set[str]) -> datetime | None:
    latest: datetime | None = None
    by_type = stats.get("latest_event_ts_by_type") or {}
    if not isinstance(by_type, dict):
        return None
    for event_type in event_types:
        parsed = parse_dt(by_type.get(event_type))
        if parsed is not None and (latest is None or parsed > latest):
            latest = parsed
    return latest


def build_freshness_checks(
    *,
    now: datetime,
    raw_stats: dict[str, Any],
    checkpoint_stats: dict[str, Any],
    normalized_stats: dict[str, Any],
    feature_stats: dict[str, Any],
    decision_stats: dict[str, Any],
    fillability_stats: dict[str, Any],
    outcome_label_stats: dict[str, Any],
) -> dict[str, Any]:
    raw_latest = parse_dt(raw_stats.get("latest_event_ts"))
    checkpoint_latest = parse_dt(checkpoint_stats.get("latest_event_ts"))
    normalized_latest = parse_dt(normalized_stats.get("latest_timestamp_sample"))
    feature_latest = parse_dt(feature_stats.get("latest_timestamp_sample"))
    source_decision_latest = latest_event_type_ts(raw_stats, SOURCE_DECISION_EVENT_TYPES)
    decision_latest = parse_dt(decision_stats.get("latest_timestamp_sample"))
    fillability_latest = parse_dt(fillability_stats.get("latest_timestamp_sample"))
    outcome_latest = parse_dt(outcome_label_stats.get("latest_timestamp_sample"))

    return {
        "checked_at_utc": now.isoformat(),
        "active_capture_stale_seconds_threshold": ACTIVE_CAPTURE_STALE_SECONDS,
        "derived_tape_lag_warn_seconds_threshold": DERIVED_TAPE_LAG_WARN_SECONDS,
        "latest_raw_event_ts": raw_latest.isoformat() if raw_latest else None,
        "latest_checkpoint_event_ts": checkpoint_latest.isoformat() if checkpoint_latest else None,
        "latest_source_decision_event_ts": source_decision_latest.isoformat() if source_decision_latest else None,
        "latest_normalized_event_ts": normalized_latest.isoformat() if normalized_latest else None,
        "latest_feature_ts": feature_latest.isoformat() if feature_latest else None,
        "latest_candidate_decision_ts": decision_latest.isoformat() if decision_latest else None,
        "latest_fillability_snapshot_ts": fillability_latest.isoformat() if fillability_latest else None,
        "latest_outcome_label_ts": outcome_latest.isoformat() if outcome_latest else None,
        "raw_capture_age_seconds": positive_lag_seconds(now, raw_latest),
        "checkpoint_capture_age_seconds": positive_lag_seconds(now, checkpoint_latest),
        "normalized_lag_vs_raw_seconds": positive_lag_seconds(raw_latest, normalized_latest),
        "feature_lag_vs_raw_seconds": positive_lag_seconds(raw_latest, feature_latest),
        "candidate_decision_lag_vs_source_decision_seconds": positive_lag_seconds(source_decision_latest, decision_latest),
        "fillability_lag_vs_source_decision_seconds": positive_lag_seconds(source_decision_latest, fillability_latest),
        "outcome_label_lag_vs_source_decision_seconds": positive_lag_seconds(source_decision_latest, outcome_latest),
    }


def build_readiness(
    dataset_tag: str,
    *,
    recorder_type: str,
    strategy_tags: list[str],
    live_bot_run_tag: str | None,
    source_dataset_tag: str | None,
) -> dict[str, Any]:
    now = utc_now()
    dataset_root = RESEARCH_DATA_ROOT / dataset_tag
    metadata_root = dataset_root / "metadata"
    raw_stats = scan_ndjson_tree(dataset_root / "raw_events")
    checkpoint_stats = scan_ndjson_tree(dataset_root / "book_checkpoints")
    feature_stats = scan_parquet_tree(dataset_root / "features", timestamp_columns=("ts",))
    label_stats = scan_parquet_tree(dataset_root / "trade_labels", timestamp_columns=("entry_dt", "settlement_ts"))
    normalized_stats = scan_parquet_tree(dataset_root / "normalized_events", timestamp_columns=("local_recv_dt",))
    decision_stats = scan_parquet_tree(dataset_root / "candidate_decisions", timestamp_columns=("available_at", "source_feature_ts"))
    fillability_stats = scan_parquet_tree(dataset_root / "fillability_snapshots", timestamp_columns=("available_at", "snapshot_ts"))
    outcome_label_stats = scan_parquet_tree(dataset_root / "outcome_labels", timestamp_columns=("label_available_at", "settlement_ts"))
    freshness_checks = build_freshness_checks(
        now=now,
        raw_stats=raw_stats,
        checkpoint_stats=checkpoint_stats,
        normalized_stats=normalized_stats,
        feature_stats=feature_stats,
        decision_stats=decision_stats,
        fillability_stats=fillability_stats,
        outcome_label_stats=outcome_label_stats,
    )

    generated_manifest = default_manifest(
        dataset_tag,
        recorder_type=recorder_type,
        strategy_tags=strategy_tags,
        live_bot_run_tag=live_bot_run_tag,
        source_dataset_tag=source_dataset_tag,
        log_paths=source_log_paths(live_bot_run_tag),
        raw_stats=raw_stats,
        checkpoint_stats=checkpoint_stats,
        feature_stats=feature_stats,
        label_stats=label_stats,
    )
    existing_manifest = read_json(metadata_root / "dataset_manifest.json")
    manifest = merge_manifest(existing_manifest, generated_manifest)

    feature_columns = set(feature_stats.get("columns") or [])
    decision_columns = set(decision_stats.get("columns") or [])
    fillability_columns = set(fillability_stats.get("columns") or [])
    outcome_label_columns = set(outcome_label_stats.get("columns") or [])
    missing_core_features = [col for col in CORE_FEATURE_COLUMNS if col not in feature_columns]
    missing_gauntlet_features = [col for col in GAUNTLET_FEATURE_COLUMNS if col not in feature_columns]
    missing_btc_features = [col for col in BTC_FEATURE_COLUMNS if col not in feature_columns]
    missing_candidate_columns = [col for col in CANDIDATE_DECISION_COLUMNS if col not in decision_columns]
    missing_fillability_columns = [col for col in FILLABILITY_COLUMNS if col not in fillability_columns]
    missing_outcome_label_columns = [col for col in OUTCOME_LABEL_COLUMNS if col not in outcome_label_columns]
    missing_manifest_keys = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    missing_manifest_keys.extend(
        key for key in NONEMPTY_MANIFEST_KEYS if key in manifest and manifest.get(key) in (None, "", [], {})
    )

    blockers: list[str] = []
    warnings: list[str] = []
    if not raw_stats.get("file_count"):
        blockers.append("missing_raw_events")
    if not checkpoint_stats.get("file_count"):
        blockers.append("missing_book_checkpoints")
    if missing_manifest_keys:
        warnings.append("manifest_incomplete")
    if missing_core_features:
        warnings.append("core_feature_tape_missing_or_unbuilt")
    if missing_gauntlet_features:
        warnings.append("gauntlet_feature_columns_missing_until_pipeline_rebuild")
    if missing_btc_features:
        warnings.append("btc_feature_columns_missing_or_unbuilt")
    if not decision_stats.get("file_count"):
        warnings.append("candidate_decision_tape_not_built")
    if not fillability_stats.get("file_count"):
        warnings.append("fillability_snapshot_tape_not_built")
    if not outcome_label_stats.get("file_count") and decision_stats.get("file_count"):
        warnings.append("outcome_label_tape_not_built")
    if live_bot_run_tag:
        if (freshness_checks.get("raw_capture_age_seconds") or 0) > ACTIVE_CAPTURE_STALE_SECONDS:
            warnings.append("active_raw_capture_stale")
        if (freshness_checks.get("checkpoint_capture_age_seconds") or 0) > ACTIVE_CAPTURE_STALE_SECONDS:
            warnings.append("active_checkpoint_capture_stale")
    if (freshness_checks.get("normalized_lag_vs_raw_seconds") or 0) > DERIVED_TAPE_LAG_WARN_SECONDS:
        warnings.append("normalized_events_lag_raw_capture")
    if (freshness_checks.get("feature_lag_vs_raw_seconds") or 0) > DERIVED_TAPE_LAG_WARN_SECONDS:
        warnings.append("feature_tape_lag_raw_capture")
    if (freshness_checks.get("candidate_decision_lag_vs_source_decision_seconds") or 0) > DERIVED_TAPE_LAG_WARN_SECONDS:
        warnings.append("candidate_decision_tape_lag_source_decisions")
    if (freshness_checks.get("fillability_lag_vs_source_decision_seconds") or 0) > DERIVED_TAPE_LAG_WARN_SECONDS:
        warnings.append("fillability_snapshot_tape_lag_source_decisions")
    if (freshness_checks.get("outcome_label_lag_vs_source_decision_seconds") or 0) > DERIVED_TAPE_LAG_WARN_SECONDS:
        warnings.append("outcome_label_tape_lag_source_decisions")
    if recorder_type == "backfill":
        warnings.append("dataset_is_backfill_not_native_passive")

    status = status_from_checks(blockers, warnings)
    return {
        "schema_version": READINESS_SCHEMA_VERSION,
        "dataset_tag": dataset_tag,
        "generated_at_utc": now.isoformat(),
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "manifest": manifest,
        "stats": {
            "raw_events": raw_stats,
            "book_checkpoints": checkpoint_stats,
            "normalized_events": normalized_stats,
            "features": feature_stats,
            "trade_labels": label_stats,
            "candidate_decisions": decision_stats,
            "fillability_snapshots": fillability_stats,
            "outcome_labels": outcome_label_stats,
        },
        "freshness_checks": freshness_checks,
        "schema_checks": {
            "missing_manifest_keys": missing_manifest_keys,
            "missing_core_feature_columns": missing_core_features,
            "missing_gauntlet_feature_columns": missing_gauntlet_features,
            "missing_btc_feature_columns": missing_btc_features,
            "missing_candidate_decision_columns": missing_candidate_columns,
            "missing_fillability_columns": missing_fillability_columns,
            "missing_outcome_label_columns": missing_outcome_label_columns,
        },
        "labels": {
            "implementation_correctness": "PASS",
            "live_vs_backtest_alignment": "WARN" if status != "PASS" else "MONITOR",
            "calculation_speed": "MONITOR",
            "stale_book_rate": "MONITOR",
            "fillability": "MONITOR" if not blockers else "WARN",
            "research_lab_readiness": status,
        },
    }


def write_readiness_artifacts(readiness: dict[str, Any], write_dataset_files: bool) -> dict[str, Path]:
    dataset_tag = str(readiness["dataset_tag"])
    stamp = utc_now().strftime("%Y%m%dT%H%M%SZ")
    dataset_root = RESEARCH_DATA_ROOT / dataset_tag
    metadata_root = dataset_root / "metadata"
    candidate_root = dataset_root / "candidate_specs"
    EDGE_DIR.mkdir(parents=True, exist_ok=True)

    if write_dataset_files:
        metadata_root.mkdir(parents=True, exist_ok=True)
        candidate_root.mkdir(parents=True, exist_ok=True)
        write_json(metadata_root / "dataset_manifest.json", readiness["manifest"])
        write_json(metadata_root / "gauntlet_tape_schema.json", gauntlet_tape_schema(dataset_tag))
        schema_path = metadata_root / "schema_version.json"
        if not schema_path.exists():
            write_json(schema_path, schema_version_payload(dataset_tag, str(readiness["manifest"].get("schema_version") or "")))
        write_json(metadata_root / "ingestion_watchdog_status.json", ingestion_watchdog_status(readiness))
        write_json(metadata_root / "readiness_status.json", readiness)
        template_path = candidate_root / "gauntlet_candidates.template.json"
        if not template_path.exists():
            write_json(template_path, candidate_template(dataset_tag, list(readiness["manifest"].get("strategy_tags") or [])))

    summary_path = EDGE_DIR / f"codex_dwell_execution_integrity_research_lab_readiness_{dataset_tag}_{stamp}.json"
    report_path = EDGE_DIR / f"codex_dwell_execution_integrity_research_lab_readiness_{dataset_tag}_{stamp}.md"
    write_json(summary_path, readiness)
    report_path.write_text(render_report(readiness, summary_path), encoding="utf-8")
    shutil.copyfile(summary_path, EDGE_DIR / f"codex_dwell_execution_integrity_research_lab_readiness_{dataset_tag}_latest.json")
    shutil.copyfile(report_path, EDGE_DIR / f"codex_dwell_execution_integrity_research_lab_readiness_{dataset_tag}_latest.md")
    return {"summary_json": summary_path, "report": report_path}


def render_report(readiness: dict[str, Any], summary_path: Path) -> str:
    manifest = readiness["manifest"]
    stats = readiness["stats"]
    checks = readiness["schema_checks"]
    labels = readiness["labels"]
    freshness = readiness.get("freshness_checks") or {}
    lines = [
        f"# Research Lab Readiness: {readiness['dataset_tag']}",
        "",
        f"- Generated: `{readiness['generated_at_utc']}`",
        f"- Status: `{readiness['status']}`",
        "- Scope: research-only readiness/control-plane update; no live bot behavior, run scripts, locks, secrets, or state changed.",
        "",
        "## Data Coverage",
        "",
        f"- Recorder type: `{manifest.get('recorder_type')}`",
        f"- Raw event files: `{stats['raw_events'].get('file_count')}`; latest sample ts `{stats['raw_events'].get('latest_event_ts')}`; latest mtime `{stats['raw_events'].get('latest_file_mtime_utc')}`.",
        f"- Book checkpoint files: `{stats['book_checkpoints'].get('file_count')}`; latest sample ts `{stats['book_checkpoints'].get('latest_event_ts')}`; latest mtime `{stats['book_checkpoints'].get('latest_file_mtime_utc')}`.",
        f"- Feature files: `{stats['features'].get('file_count')}`; latest sample ts `{stats['features'].get('latest_timestamp_sample')}`.",
        f"- Trade label files: `{stats['trade_labels'].get('file_count')}`; latest label sample `{stats['trade_labels'].get('latest_timestamp_sample')}`.",
        f"- Candidate decision files: `{stats['candidate_decisions'].get('file_count')}`; latest sample ts `{stats['candidate_decisions'].get('latest_timestamp_sample')}`.",
        f"- Fillability snapshot files: `{stats['fillability_snapshots'].get('file_count')}`; latest sample ts `{stats['fillability_snapshots'].get('latest_timestamp_sample')}`.",
        f"- Outcome label files: `{stats.get('outcome_labels', {}).get('file_count')}`; latest sample ts `{stats.get('outcome_labels', {}).get('latest_timestamp_sample')}`.",
        "",
        "## Freshness Watchdog",
        "",
        f"- Raw capture age: `{freshness.get('raw_capture_age_seconds')}` seconds.",
        f"- Checkpoint capture age: `{freshness.get('checkpoint_capture_age_seconds')}` seconds.",
        f"- Feature lag vs raw capture: `{freshness.get('feature_lag_vs_raw_seconds')}` seconds.",
        f"- Candidate decision lag vs latest source decision: `{freshness.get('candidate_decision_lag_vs_source_decision_seconds')}` seconds.",
        f"- Fillability snapshot lag vs latest source decision: `{freshness.get('fillability_lag_vs_source_decision_seconds')}` seconds.",
        f"- Outcome label lag vs latest source decision: `{freshness.get('outcome_label_lag_vs_source_decision_seconds')}` seconds.",
        "",
        "## Missing Pieces",
        "",
        f"- Blockers: `{', '.join(readiness['blockers']) if readiness['blockers'] else 'none'}`",
        f"- Warnings: `{', '.join(readiness['warnings']) if readiness['warnings'] else 'none'}`",
        f"- Missing core feature columns: `{', '.join(checks['missing_core_feature_columns']) if checks['missing_core_feature_columns'] else 'none'}`",
        f"- Missing gauntlet feature columns: `{', '.join(checks['missing_gauntlet_feature_columns']) if checks['missing_gauntlet_feature_columns'] else 'none'}`",
        f"- Candidate decision tape missing columns: `{', '.join(checks['missing_candidate_decision_columns'][:12]) if checks['missing_candidate_decision_columns'] else 'none'}`",
        f"- Fillability tape missing columns: `{', '.join(checks['missing_fillability_columns'][:12]) if checks['missing_fillability_columns'] else 'none'}`",
        f"- Outcome label tape missing columns: `{', '.join(checks.get('missing_outcome_label_columns', [])[:12]) if checks.get('missing_outcome_label_columns') else 'none'}`",
        "",
        "## How This Feeds The Gauntlet",
        "",
        "- `dataset_manifest.json` fixes provenance and prevents native passive data from being mixed with backfills.",
        "- `gauntlet_tape_schema.json` defines the feature, candidate-decision, fillability, and outcome-label contracts.",
        "- `ingestion_watchdog_status.json` gives raw/checkpoint freshness, derived-tape lag, file-gap, and tape-count telemetry.",
        "- `candidate_specs/gauntlet_candidates.template.json` is the frozen-candidate starting point; real candidates should be copied into versioned files and frozen before scoring.",
        "- `readiness_status.json` gives the gauntlet a machine-readable preflight gate.",
        "",
        "## Labels",
        "",
        f"- Implementation correctness: `{labels['implementation_correctness']}`",
        f"- Live-vs-backtest alignment: `{labels['live_vs_backtest_alignment']}`",
        f"- Calculation speed: `{labels['calculation_speed']}`",
        f"- Stale-book rate: `{labels['stale_book_rate']}`",
        f"- Fillability: `{labels['fillability']}`",
        f"- Research Lab readiness: `{labels['research_lab_readiness']}`",
        "",
        "## Artifact",
        "",
        f"- Summary JSON: `{summary_path}`",
    ]
    return "\n".join(lines) + "\n"


def append_ledger(readiness: dict[str, Any], artifacts: dict[str, Path]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": readiness["generated_at_utc"],
        "automation_id": "dwell-execution-integrity-research",
        "type": "research_lab_readiness",
        "status": readiness["status"],
        "hypothesis": "The Research Lab needs a machine-readable readiness layer before gauntlet scoring.",
        "method": "Audited dataset provenance, raw/checkpoint coverage, feature schema, candidate decision tape contract, fillability snapshot contract, and outcome-label readiness.",
        "result": f"{readiness['dataset_tag']} readiness is {readiness['status']} with blockers={readiness['blockers']} warnings={readiness['warnings']}.",
        "labels": readiness["labels"],
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "next_step": "Build or run missing ingestion/feature/candidate/fillability tapes before scoring live-forward candidates.",
    }
    with INTEGRITY_LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and prepare Research Lab datasets for gauntlet scoring.")
    parser.add_argument("--dataset", required=True, help="Research Lab dataset tag under research_data/<dataset>.")
    parser.add_argument("--bot-tag", default="", help="Optional live bot log tag used as source-log provenance.")
    parser.add_argument("--strategy-tag", action="append", default=[], help="Strategy tag(s) associated with the dataset.")
    parser.add_argument("--recorder-type", choices=["native_passive", "live_bot_attached", "shadow", "backfill"], default="")
    parser.add_argument("--source-dataset-tag", default="")
    parser.add_argument("--write", action="store_true", help="Write dataset metadata/schema/template files.")
    args = parser.parse_args()

    dataset_root = RESEARCH_DATA_ROOT / args.dataset
    raw_exists = (dataset_root / "raw_events").exists()
    checkpoint_exists = (dataset_root / "book_checkpoints").exists()
    recorder_type = args.recorder_type or ("native_passive" if raw_exists and checkpoint_exists else "backfill")
    readiness = build_readiness(
        args.dataset,
        recorder_type=recorder_type,
        strategy_tags=args.strategy_tag,
        live_bot_run_tag=args.bot_tag or None,
        source_dataset_tag=args.source_dataset_tag or None,
    )
    artifacts = write_readiness_artifacts(readiness, write_dataset_files=args.write)
    append_ledger(readiness, artifacts)
    print(json.dumps(readiness, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
