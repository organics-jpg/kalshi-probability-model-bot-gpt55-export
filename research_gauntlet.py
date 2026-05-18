from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT / "research_data"
EDGE_DIR = ROOT / "logs" / "edge_research"
GAUNTLET_LEDGER = EDGE_DIR / "research_lab_gauntlet_ledger.jsonl"
SCRIPT_VERSION = "research-gauntlet-v5"
SPEC_VERSION = "gauntlet-candidate-spec-v1"
TAPE_VERSION = "gauntlet-tapes-v1"
UTC = timezone.utc

MONTH_ABBR_TO_NUM = {
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

CANDIDATE_COLUMNS = [
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

OUTCOME_COLUMNS = [
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

TOP_HISTORICAL_CANDIDATES: list[dict[str, Any]] = [
    {
        "candidate_id": "btc_spot_ev_score_scaled_sizer_78bf3a16_fixed_size_v1",
        "strategy_id": "btc_spot_ev_score_scaled_sizer_78bf3a16",
        "strategy_version": "fixed_size_research_lab_proxy_v1",
        "enabled": True,
        "description": (
            "Top historical score-scaled BTC spot EV candidate, scored here as a fixed "
            "2-contract admission proxy because live dwell sizing is fixed."
        ),
        "entry_logic": {
            "family": "btc_spot_ev_fixed",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:btc_spot_synthetic_ev_candidate_refinement_20260424T191301Z",
            "historical_summary": {
                "baseline_n": 991,
                "entries": 101,
                "entry_win_rate": 0.9307,
                "sim_pnl_cents": 209.85,
                "total_contracts": 1687,
            },
            "parameters": {
                "delay_seconds": 120,
                "intercept": 1.5,
                "location_weight": 1.0,
                "macd_weight": 0.0,
                "max_entry_ask": 88,
                "max_opp_pressure": 0.3,
                "max_spread": 4,
                "min_bid_sum": 0,
                "min_ev_cents": 2.0,
                "min_roi": 0.0,
                "move_scale": 0.25,
                "pressure_penalty": 0.5,
                "range_penalty": 0.0,
                "rsi_weight": 0.0,
                "side_polarity": 1,
                "spread_penalty": 0.03,
                "w_1m": 0.0,
                "w_5m": 1.0,
                "w_15m": 0.0,
                "limit_source": "feature_entry_limit",
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
    {
        "candidate_id": "online_neighbor_lcb_sizer_settlement_stress_5aecbb41_blocked_v1",
        "strategy_id": "online_neighbor_lcb_sizer_settlement_stress_5aecbb41",
        "strategy_version": "research_lab_online_neighbor_features_v1",
        "enabled": True,
        "description": (
            "Top historical online-neighbor LCB sizer scored against Research Lab "
            "online-neighbor features generated from prior closed markets only."
        ),
        "entry_logic": {
            "family": "online_neighbor_lcb",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:conformal_neighbor_stress_validation_20260424T200940Z",
            "historical_summary": {
                "baseline_n": 991,
                "entries": 43,
                "entry_win_rate": 1.0,
                "sim_pnl_cents": 141.42,
                "total_contracts": 842,
            },
            "parameters": {
                "delay_seconds": 120,
                "k": 25,
                "lcb_z": 0.5,
                "max_contracts": 20,
                "max_entry_ask": 90,
                "max_multiplier": 2.0,
                "max_opp_pressure": 0.3,
                "max_spread": 4,
                "min_history": 80,
                "min_lcb_cents": 0.0,
                "min_model_ev_cents": 2.0,
                "min_neighbor_win_rate": 0.78,
                "pool_min_ev_cents": -2.0,
                "required_features": [
                    "online_neighbor_{side}_lcb_cents",
                    "online_neighbor_{side}_win_rate",
                    "online_neighbor_{side}_history_count",
                    "online_neighbor_{side}_model_ev_cents",
                ],
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
    {
        "candidate_id": "btc_spot_ev_fixed_candidate_stress_8709cfd0_live_forward_v1",
        "strategy_id": "btc_spot_ev_fixed_candidate_stress_8709cfd0",
        "strategy_version": "research_lab_feature_tape_v1",
        "enabled": True,
        "description": "Fixed BTC spot EV candidate stress winner scored on Research Lab BTC feature tape.",
        "entry_logic": {
            "family": "btc_spot_ev_fixed",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:btc_spot_synthetic_ev_candidate_refinement_20260424T191113Z",
            "historical_summary": {
                "baseline_n": 924,
                "entries": 101,
                "entry_win_rate": 0.9307,
                "sim_pnl_cents": 104.12,
                "total_contracts": 842,
            },
            "parameters": {
                "delay_seconds": 120,
                "intercept": 1.5,
                "location_weight": 1.0,
                "macd_weight": 0.0,
                "max_entry_ask": 88,
                "max_opp_pressure": 0.3,
                "max_spread": 4,
                "min_bid_sum": 0,
                "min_ev_cents": 2.0,
                "move_scale": 0.25,
                "pressure_penalty": 0.5,
                "range_penalty": 0.0,
                "rsi_weight": 0.0,
                "side_polarity": 1,
                "spread_penalty": 0.03,
                "w_1m": 0.0,
                "w_5m": 1.0,
                "w_15m": 0.0,
                "limit_source": "feature_entry_limit",
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
    {
        "candidate_id": "btc_momentum_concordance_admission_fc12daa9_live_forward_v1",
        "strategy_id": "btc_momentum_concordance_admission_fc12daa9",
        "strategy_version": "research_lab_feature_tape_v1",
        "enabled": True,
        "description": "BTC momentum concordance admission candidate scored on Research Lab BTC feature tape.",
        "entry_logic": {
            "family": "btc_momentum_concordance",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:codex_entry_cross_asset_likelihood_research_20260424T181047Z",
            "historical_summary": {
                "baseline_n": 129,
                "entries": 112,
                "entry_win_rate": 0.9018,
                "sim_pnl_cents": 105.12,
                "total_contracts": 1103,
            },
            "parameters": {
                "delay_seconds": 0,
                "macd_weight": 0.1,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.5,
                "max_spread": 4,
                "min_bid_sum": 0,
                "min_score": -1.0,
                "pressure_penalty": 0.5,
                "range_penalty": 0.25,
                "rsi_weight": 0.25,
                "spread_penalty": 0.03,
                "w_1m": 0.0,
                "w_5m": 0.5,
                "w_15m": 1.0,
                "limit_source": "feature_entry_limit",
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
    {
        "candidate_id": "btc_spot_ev_roi_volatility_refinement_232123ec_live_forward_v1",
        "strategy_id": "btc_spot_ev_roi_volatility_refinement_232123ec",
        "strategy_version": "research_lab_feature_tape_v1",
        "enabled": True,
        "description": "BTC spot EV candidate with ROI and volatility gates scored on Research Lab BTC feature tape.",
        "entry_logic": {
            "family": "btc_spot_ev_roi_volatility",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:btc_spot_synthetic_ev_candidate_refinement_20260424T191301Z",
            "historical_summary": {
                "baseline_n": 924,
                "entries": 107,
                "entry_win_rate": 0.9065,
                "sim_pnl_cents": 99.41,
                "total_contracts": 946,
            },
            "parameters": {
                "delay_seconds": 120,
                "intercept": 1.5,
                "location_weight": 1.0,
                "macd_weight": 0.0,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.3,
                "max_range_15m_bps": 75.0,
                "max_spread": 4,
                "min_bid_sum": 0,
                "min_ev_cents": 2.0,
                "min_roi": 0.0,
                "move_scale": 0.25,
                "pressure_penalty": 0.5,
                "range_penalty": 0.0,
                "rsi_weight": 0.0,
                "side_polarity": 1,
                "spread_penalty": 0.03,
                "w_1m": 0.0,
                "w_5m": 1.0,
                "w_15m": 0.0,
                "limit_source": "feature_entry_limit",
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
    {
        "candidate_id": "online_neighbor_lcb_admission_settlement_stress_a9214293_blocked_v1",
        "strategy_id": "online_neighbor_lcb_admission_settlement_stress_a9214293",
        "strategy_version": "research_lab_online_neighbor_features_v1",
        "enabled": True,
        "description": (
            "Top historical online-neighbor LCB admission rule scored against "
            "Research Lab online-neighbor features generated from prior closed "
            "markets only."
        ),
        "entry_logic": {
            "family": "online_neighbor_lcb",
            "uses_feature_tape_only": True,
            "provenance": "edge_idea_ledger:conformal_neighbor_stress_validation_20260424T200940Z",
            "historical_summary": {
                "baseline_n": 991,
                "entries": 43,
                "entry_win_rate": 1.0,
                "sim_pnl_cents": 73.94,
                "total_contracts": 441,
            },
            "parameters": {
                "delay_seconds": 120,
                "k": 25,
                "lcb_z": 0.5,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.3,
                "max_spread": 4,
                "min_history": 80,
                "min_lcb_cents": 0.0,
                "min_model_ev_cents": 2.0,
                "min_neighbor_win_rate": 0.78,
                "pool_min_ev_cents": -2.0,
                "required_features": [
                    "online_neighbor_{side}_lcb_cents",
                    "online_neighbor_{side}_win_rate",
                    "online_neighbor_{side}_history_count",
                    "online_neighbor_{side}_model_ev_cents",
                ],
            },
        },
        "sizing": {"contracts": 2},
        "exit_policy": {"type": "hold_to_settlement"},
    },
]


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


def parse_float(value: Any) -> float | None:
    if value in (None, "", "None", "null", "nan"):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def parse_int(value: Any) -> int | None:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(round(parsed))


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def parse_market_close_from_ticker(market: str) -> datetime | None:
    parts = str(market or "").split("-")
    if len(parts) != 3 or len(parts[1]) != 11:
        return None
    stamp = parts[1]
    try:
        year = 2000 + int(stamp[:2])
        month = MONTH_ABBR_TO_NUM.get(stamp[2:5].upper())
        day = int(stamp[5:7])
        hour = int(stamp[7:9])
        minute = int(stamp[9:11])
    except Exception:
        return None
    if month is None:
        return None
    # Kalshi BTC15M ticker timestamps are Eastern local wall-clock.
    from zoneinfo import ZoneInfo

    return datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("America/New_York")).astimezone(UTC)


def stable_id(*parts: Any) -> str:
    text = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:24]


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


def iter_ndjson(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for fp in sorted(root.rglob("*.ndjson")):
        with fp.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    payload["_file_path"] = str(fp)
                    rows.append(payload)
    return rows


def event_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload_json")
    return payload if isinstance(payload, dict) else {}


def load_feature_rows(dataset_root: Path) -> dict[str, list[dict[str, Any]]]:
    feature_root = dataset_root / "features"
    if not feature_root.exists():
        return {}
    frames: list[pd.DataFrame] = []
    for fp in sorted(feature_root.rglob("*.parquet")):
        try:
            frame = pd.read_parquet(fp)
        except Exception:
            continue
        if not frame.empty:
            market_from_path = ""
            for part in fp.parts:
                if part.startswith("market_ticker="):
                    market_from_path = part.split("=", 1)[1]
                    break
            if "market_ticker" not in frame.columns:
                frame["market_ticker"] = market_from_path
            elif market_from_path:
                frame["market_ticker"] = frame["market_ticker"].fillna(market_from_path)
                frame.loc[frame["market_ticker"].astype(str) == "", "market_ticker"] = market_from_path
            frames.append(frame)
    if not frames:
        return {}

    combined = pd.concat(frames, ignore_index=True)
    if "market_ticker" not in combined.columns:
        combined["market_ticker"] = ""
    for col in ("feature_available_at", "ts", "local_recv_dt"):
        if col in combined.columns:
            combined[col] = pd.to_datetime(combined[col], utc=True, errors="coerce")

    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in combined.to_dict("records"):
        market = str(row.get("market_ticker") or "")
        if not market:
            continue
        feature_ts = parse_dt(row.get("feature_available_at")) or parse_dt(row.get("ts")) or parse_dt(row.get("local_recv_dt"))
        if feature_ts is None:
            continue
        row["_feature_ts"] = feature_ts
        by_market[market].append(row)
    for rows in by_market.values():
        rows.sort(key=lambda item: item.get("_feature_ts") or datetime.min.replace(tzinfo=UTC))
    return dict(by_market)


def find_feature(
    features_by_market: dict[str, list[dict[str, Any]]],
    market: str,
    event_ts: datetime | None,
    *,
    max_age_seconds: int = 180,
) -> dict[str, Any] | None:
    if event_ts is None:
        return None
    rows = features_by_market.get(market) or []
    for row in reversed(rows):
        feature_ts = row.get("_feature_ts")
        if feature_ts is None or feature_ts > event_ts:
            continue
        if (event_ts - feature_ts).total_seconds() <= max_age_seconds:
            return row
        return None
    return None


def load_lab(dataset_tag: str) -> dict[str, Any]:
    dataset_root = RESEARCH_ROOT / dataset_tag
    rows = iter_ndjson(dataset_root / "raw_events")
    features_by_market = load_feature_rows(dataset_root)
    heartbeats: dict[str, list[dict[str, Any]]] = defaultdict(list)
    closes: dict[str, datetime] = {}
    execution_events: list[dict[str, Any]] = []
    latest_raw_ts: datetime | None = None

    for row in rows:
        payload = event_payload(row)
        raw_type = str(row.get("event_type") or "")
        ts = parse_dt(row.get("local_recv_ts") or row.get("ts_wall"))
        if ts is not None and (latest_raw_ts is None or ts > latest_raw_ts):
            latest_raw_ts = ts
        if raw_type == "heartbeat":
            market = str(row.get("market_ticker") or payload.get("market_ticker") or "")
            if not market:
                continue
            heartbeats[market].append(
                {
                    "ts": ts,
                    "yes_bid": parse_int(payload.get("yes_bid")),
                    "yes_ask": parse_int(payload.get("yes_ask")),
                    "no_bid": parse_int(payload.get("no_bid")),
                    "no_ask": parse_int(payload.get("no_ask")),
                    "trust_state": row.get("trust_state"),
                }
            )
            continue
        if raw_type == "watch_market":
            market = str(row.get("market_ticker") or payload.get("market_ticker") or "")
            close_dt = parse_dt(payload.get("close_time")) or parse_market_close_from_ticker(market)
            if market and close_dt is not None:
                closes[market] = close_dt
            continue
        if raw_type.startswith("execution_"):
            event = dict(payload)
            event.setdefault("event_type", str(payload.get("event_type") or raw_type.replace("execution_", "", 1)))
            event.setdefault("market", row.get("market_ticker"))
            event.setdefault("ts_wall", row.get("local_recv_ts") or row.get("ts_wall"))
            event["_raw_type"] = raw_type
            event["_raw_file_path"] = row.get("_file_path")
            execution_events.append(event)

    for market_rows in heartbeats.values():
        market_rows.sort(key=lambda item: item.get("ts") or datetime.min.replace(tzinfo=UTC))
    execution_events.sort(key=lambda event: parse_dt(event.get("ts_wall")) or datetime.min.replace(tzinfo=UTC))
    return {
        "rows": rows,
        "heartbeats": heartbeats,
        "closes": closes,
        "execution_events": execution_events,
        "features_by_market": features_by_market,
        "latest_raw_ts": latest_raw_ts,
    }


def infer_outcome(
    market: str,
    closes: dict[str, datetime],
    heartbeats: dict[str, list[dict[str, Any]]],
    *,
    now: datetime,
) -> tuple[str | None, datetime | None, str]:
    close_dt = closes.get(market) or parse_market_close_from_ticker(market)
    if close_dt is not None and now < close_dt + timedelta(seconds=20):
        return None, None, "market_not_past_close_buffer"
    rows = [row for row in heartbeats.get(market, []) if row.get("ts") is not None]
    if close_dt is not None:
        rows = [row for row in rows if row["ts"] <= close_dt + timedelta(seconds=20)]
    rows = [row for row in rows if row.get("yes_bid") is not None and row.get("no_bid") is not None]
    if not rows:
        return None, None, "missing_heartbeat_outcome"

    extremes: list[tuple[dict[str, Any], str]] = []
    for row in rows:
        yes_bid = int(row["yes_bid"])
        no_bid = int(row["no_bid"])
        if yes_bid >= 95 and no_bid <= 5:
            extremes.append((row, "yes"))
        elif no_bid >= 95 and yes_bid <= 5:
            extremes.append((row, "no"))
    if extremes:
        row, side = extremes[-1]
        return side, row.get("ts"), "lab_heartbeat_extreme"

    row = rows[-1]
    side = "yes" if int(row["yes_bid"]) > int(row["no_bid"]) else "no"
    return side, row.get("ts"), "lab_heartbeat_last_before_close"


def default_candidate_spec(dataset_tag: str) -> dict[str, Any]:
    created = utc_now().isoformat()
    return {
        "schema_version": SPEC_VERSION,
        "source_dataset_tag": dataset_tag,
        "created_at_utc": created,
        "frozen": True,
        "frozen_at_utc": created,
        "spec_id": "live_liquidity_dwell_reference_plus_top_historical_v2",
        "notes": (
            "Frozen research-only gauntlet spec. Candidates are scored on logged live dwell "
            "decision points from the Research Lab backfill; this is forward plumbing evidence, "
            "not a native passive replay or live behavior change. The top historical "
            "candidates are added directly to this frozen spec without a separate importer "
            "or registry."
        ),
        "promotion_gates": {
            "min_forward_decisions": 25,
            "approved_stream_pnl_cents_min": 1,
            "fillability_adjusted_pnl_cents_min": 1,
            "max_false_positive_loss_cents": 300,
            "require_side_stability": True,
            "require_no_unlabeled_settlements": True,
        },
        "top_historical_candidate_ids": [candidate["candidate_id"] for candidate in TOP_HISTORICAL_CANDIDATES],
        "candidates": [
            {
                "candidate_id": "pnl_max_p05_q065_logged_live_reference_v1",
                "strategy_id": "liquidity_dwell_p05_q065_hold",
                "strategy_version": "p05_q065_hold_logged_v1",
                "enabled": True,
                "description": "Live reference dwell gates scored from logged Research Lab decision points.",
                "entry_logic": {
                    "family": "logged_live_liquidity_dwell",
                    "uses_feature_tape_only": False,
                    "provenance": "log_derived_research_lab_decision_points",
                    "parameters": {
                        "delay_seconds": 120,
                        "max_entry_ask": 90,
                        "max_opp_pressure": 0.5,
                        "min_quality_share": 0.65,
                        "min_quality_seconds": 10,
                    },
                },
                "sizing": {"contracts": 2},
                "exit_policy": {"type": "hold_to_settlement"},
            },
            {
                "candidate_id": "locked_conservative_p03_q075_logged_shadow_v1",
                "strategy_id": "locked_conservative_p03_q075",
                "strategy_version": "logged_shadow_v1",
                "enabled": True,
                "description": "Historical conservative dwell comparator scored on available logged gates.",
                "entry_logic": {
                    "family": "available_gate_shadow",
                    "uses_feature_tape_only": False,
                    "provenance": "log_derived_research_lab_decision_points",
                    "parameters": {
                        "delay_seconds": 120,
                        "max_entry_ask": 90,
                        "max_opp_pressure": 0.3,
                        "min_quality_share": 0.75,
                        "min_quality_seconds": 10,
                    },
                },
                "sizing": {"contracts": 2},
                "exit_policy": {"type": "hold_to_settlement"},
            },
            {
                "candidate_id": "robust_pressure_persistence_ask88_available_fields_v1",
                "strategy_id": "robust_pressure_persistence_ask88",
                "strategy_version": "available_fields_shadow_v1",
                "enabled": True,
                "description": "Ask<=88 pressure comparator; pressure-path persistence is explicitly unavailable in this backfill.",
                "entry_logic": {
                    "family": "available_gate_shadow",
                    "uses_feature_tape_only": False,
                    "provenance": "log_derived_research_lab_decision_points",
                    "parameters": {
                        "delay_seconds": 120,
                        "max_entry_ask": 88,
                        "max_opp_pressure": 0.5,
                        "min_quality_share": 0.65,
                        "min_quality_seconds": 10,
                        "missing_gate": "pressure_path_persistence",
                    },
                },
                "sizing": {"contracts": 2},
                "exit_policy": {"type": "hold_to_settlement"},
            },
        ] + copy.deepcopy(TOP_HISTORICAL_CANDIDATES),
    }


def ensure_top_historical_candidates(spec: dict[str, Any]) -> bool:
    candidates = spec.setdefault("candidates", [])
    if not isinstance(candidates, list):
        spec["candidates"] = []
        candidates = spec["candidates"]
    existing_ids = {str(candidate.get("candidate_id") or "") for candidate in candidates if isinstance(candidate, dict)}
    changed = False
    by_default_id = {candidate["candidate_id"]: candidate for candidate in TOP_HISTORICAL_CANDIDATES}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_id = str(candidate.get("candidate_id") or "")
        default_candidate = by_default_id.get(candidate_id)
        if default_candidate is None:
            continue
        existing_family = str(((candidate.get("entry_logic") or {}).get("family")) or "")
        default_family = str(((default_candidate.get("entry_logic") or {}).get("family")) or "")
        if existing_family == "blocked_missing_feature" and default_family == "online_neighbor_lcb":
            candidate["strategy_version"] = default_candidate.get("strategy_version")
            candidate["description"] = default_candidate.get("description")
            candidate["entry_logic"] = copy.deepcopy(default_candidate.get("entry_logic") or {})
            changed = True
    for candidate in TOP_HISTORICAL_CANDIDATES:
        if candidate["candidate_id"] in existing_ids:
            continue
        candidates.append(copy.deepcopy(candidate))
        existing_ids.add(candidate["candidate_id"])
        changed = True
    if changed:
        spec["spec_id"] = "live_liquidity_dwell_reference_plus_top_historical_v2"
        spec["notes"] = (
            str(spec.get("notes") or "").rstrip()
            + " Top historical candidates were added directly to the frozen gauntlet spec; "
            "no candidate importer or registry was created."
        ).strip()
    spec["top_historical_candidate_ids"] = [candidate["candidate_id"] for candidate in TOP_HISTORICAL_CANDIDATES]
    return changed


def load_or_create_spec(dataset_tag: str, *, write: bool, spec_path: Path | None = None) -> tuple[dict[str, Any], Path]:
    dataset_root = RESEARCH_ROOT / dataset_tag
    target = spec_path or dataset_root / "candidate_specs" / "gauntlet_candidates.v1.json"
    if target.exists():
        spec = read_json(target)
    else:
        spec = default_candidate_spec(dataset_tag)
        if write:
            write_json(target, spec)
            latest = dataset_root / "candidate_specs" / "gauntlet_candidates.latest.json"
            shutil.copyfile(target, latest)
    changed = ensure_top_historical_candidates(spec)
    if write and changed:
        write_json(target, spec)
        latest = dataset_root / "candidate_specs" / "gauntlet_candidates.latest.json"
        shutil.copyfile(target, latest)
    return spec, target


def event_limit(event: dict[str, Any]) -> int | None:
    for key in ("actual_fill_price_cents", "top_of_book_limit_cents", "cap_price_cents", "entry_limit", "trigger_price_cents"):
        value = parse_int(event.get(key))
        if value is not None:
            return value
    return None


def feature_number(feature: dict[str, Any] | None, key: str) -> float | None:
    if feature is None:
        return None
    return parse_float(feature.get(key))


def side_feature_number(feature: dict[str, Any] | None, side: str, suffix: str) -> float | None:
    if side not in {"yes", "no"}:
        return None
    value = feature_number(feature, f"online_neighbor_{side}_{suffix}")
    if value is not None:
        return value
    return feature_number(feature, f"online_neighbor_{suffix}")


def side_sign(side: str) -> int:
    if side == "yes":
        return 1
    if side == "no":
        return -1
    return 0


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def entry_logic(candidate: dict[str, Any]) -> dict[str, Any]:
    logic = candidate.get("entry_logic")
    return logic if isinstance(logic, dict) else {}


def entry_params(candidate: dict[str, Any]) -> dict[str, Any]:
    params = entry_logic(candidate).get("parameters")
    return params if isinstance(params, dict) else {}


def candidate_uses_feature_limit(candidate: dict[str, Any]) -> bool:
    logic = entry_logic(candidate)
    params = entry_params(candidate)
    return bool(logic.get("uses_feature_tape_only")) or str(params.get("limit_source") or "") == "feature_entry_limit"


def candidate_limit(candidate: dict[str, Any], event: dict[str, Any], feature: dict[str, Any] | None, side: str) -> int | None:
    if candidate_uses_feature_limit(candidate):
        value = feature_number(feature, f"{side}_entry_limit_cents")
        if value is not None:
            return int(round(value))
    return event_limit(event)


def candidate_pressure(event: dict[str, Any], feature: dict[str, Any] | None, side: str) -> float | None:
    value = parse_float(event.get("pressure"))
    if value is not None:
        return value
    return feature_number(feature, f"{side}_opponent_pressure")


def candidate_spread(event: dict[str, Any], feature: dict[str, Any] | None, side: str) -> float | None:
    value = parse_float(event.get("spread"))
    if value is not None:
        return value
    return feature_number(feature, f"spread_{side}")


def candidate_bid_sum(event: dict[str, Any], feature: dict[str, Any] | None) -> float | None:
    value = parse_float(event.get("bid_sum"))
    if value is not None:
        return value
    return feature_number(feature, "bid_sum_cents")


def missing_feature_keys(feature: dict[str, Any] | None, keys: list[str]) -> list[str]:
    missing: list[str] = []
    for key in keys:
        if feature is None or feature.get(key) in (None, "", "None", "null") or parse_float(feature.get(key)) is None:
            missing.append(key)
    return missing


def gate_json_value(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.to_pydatetime().astimezone(UTC).isoformat()
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat() if value.tzinfo else value.replace(tzinfo=UTC).isoformat()
    parsed = parse_float(value)
    if parsed is not None and isinstance(value, float):
        return parsed
    return value


def gate_values(
    event: dict[str, Any],
    feature: dict[str, Any] | None = None,
    side: str = "",
    limit: int | None = None,
) -> dict[str, Any]:
    keys = [
        "pressure",
        "spread",
        "quality_share",
        "quality_seconds",
        "book_age_ms",
        "feed_age_ms",
        "bid_sum",
        "eligible_depth",
        "executable_window_ms",
        "sequence_ok",
        "snapshot_ready",
        "last_seq",
        "last_resync_ts",
    ]
    values = {key: gate_json_value(event.get(key)) for key in keys if event.get(key) not in (None, "")}
    if limit is not None:
        values["candidate_limit_cents"] = limit
    if feature is not None:
        feature_keys = [
            "feature_available_at",
            "quote_age_ms",
            "bid_sum_cents",
            f"{side}_entry_limit_cents",
            f"{side}_opponent_pressure",
            f"spread_{side}",
            f"{side}_range_60s",
            f"{side}_move_60s",
            "btc_move_1m_bps",
            "btc_move_5m_bps",
            "btc_move_15m_bps",
            "btc_range_15m_bps",
            "btc_distance_to_15m_high_bps",
            "btc_distance_to_15m_low_bps",
            "btc_rsi14",
            "btc_macd_hist",
            f"online_neighbor_{side}_history_count",
            f"online_neighbor_{side}_win_rate",
            f"online_neighbor_{side}_model_ev_cents",
            f"online_neighbor_{side}_lcb_cents",
        ]
        for key in feature_keys:
            value = feature.get(key)
            if value not in (None, "", "None", "null"):
                converted = gate_json_value(value)
                if converted is not None:
                    values[key] = converted
    return values


def apply_quote_gates(
    *,
    params: dict[str, Any],
    limit: int | None,
    pressure: float | None,
    spread: float | None,
    quality_share: float | None,
    quality_seconds: float | None,
    bid_sum: float | None,
) -> list[str]:
    blockers: list[str] = []
    max_entry = parse_float(params.get("max_entry_ask"))
    max_pressure = parse_float(params.get("max_opp_pressure"))
    max_spread = parse_float(params.get("max_spread"))
    min_quality_share = parse_float(params.get("min_quality_share"))
    min_quality_seconds = parse_float(params.get("min_quality_seconds"))
    min_bid_sum = parse_float(params.get("min_bid_sum"))
    if max_entry is not None and (limit is None or limit > max_entry):
        blockers.append("ask" if limit is not None else "missing_limit")
    if pressure is not None and max_pressure is not None and pressure > max_pressure:
        blockers.append("pressure")
    if spread is not None and max_spread is not None and spread > max_spread:
        blockers.append("spread")
    if min_bid_sum is not None and bid_sum is not None and bid_sum < min_bid_sum:
        blockers.append("bid_sum")
    if quality_share is not None and min_quality_share is not None and quality_share < min_quality_share:
        blockers.append("quality_share")
    if quality_seconds is not None and min_quality_seconds is not None and quality_seconds < min_quality_seconds:
        blockers.append("quality_seconds")
    return blockers


def btc_ev_decision(
    *,
    params: dict[str, Any],
    side: str,
    limit: int | None,
    pressure: float | None,
    spread: float | None,
    feature: dict[str, Any] | None,
) -> tuple[bool, str]:
    required = ["btc_range_15m_bps", "btc_distance_to_15m_high_bps", "btc_distance_to_15m_low_bps"]
    if parse_float(params.get("w_1m")) not in (None, 0.0):
        required.append("btc_move_1m_bps")
    if parse_float(params.get("w_5m")) not in (None, 0.0):
        required.append("btc_move_5m_bps")
    if parse_float(params.get("w_15m")) not in (None, 0.0):
        required.append("btc_move_15m_bps")
    missing = missing_feature_keys(feature, required)
    if limit is None:
        missing.append("candidate_limit_cents")
    if pressure is None:
        missing.append(f"{side}_opponent_pressure")
    if spread is None:
        missing.append(f"spread_{side}")
    if missing:
        return False, "candidate_missing_feature:" + ",".join(sorted(set(missing)))

    sign = side_sign(side) * int(parse_int(params.get("side_polarity")) or 1)
    if sign == 0:
        return False, "candidate_gate_failed:side"
    range_15m = max(abs(feature_number(feature, "btc_range_15m_bps") or 0.0), 1.0)
    dist_high = feature_number(feature, "btc_distance_to_15m_high_bps") or 0.0
    dist_low = feature_number(feature, "btc_distance_to_15m_low_bps") or 0.0
    move_1m = feature_number(feature, "btc_move_1m_bps") or 0.0
    move_5m = feature_number(feature, "btc_move_5m_bps") or 0.0
    move_15m = feature_number(feature, "btc_move_15m_bps") or 0.0

    momentum = (
        (parse_float(params.get("w_1m")) or 0.0) * move_1m
        + (parse_float(params.get("w_5m")) or 0.0) * move_5m
        + (parse_float(params.get("w_15m")) or 0.0) * move_15m
    )
    location = (dist_low - dist_high) / range_15m
    score = (
        (parse_float(params.get("intercept")) or 0.0)
        + (parse_float(params.get("move_scale")) or 0.0) * sign * momentum / math.sqrt(range_15m)
        + (parse_float(params.get("location_weight")) or 0.0) * sign * location
        - (parse_float(params.get("pressure_penalty")) or 0.0) * float(pressure or 0.0)
        - (parse_float(params.get("spread_penalty")) or 0.0) * float(spread or 0.0)
        - (parse_float(params.get("range_penalty")) or 0.0) * range_15m / 100.0
    )
    q = sigmoid(score)
    ev_cents = 100.0 * q - float(limit or 0.0)
    roi = ev_cents / max(float(limit or 1.0), 1.0)
    blockers: list[str] = []
    min_ev = parse_float(params.get("min_ev_cents"))
    min_roi = parse_float(params.get("min_roi"))
    max_range = parse_float(params.get("max_range_15m_bps"))
    if min_ev is not None and ev_cents < min_ev:
        blockers.append("ev")
    if min_roi is not None and roi < min_roi:
        blockers.append("roi")
    if max_range is not None and range_15m > max_range:
        blockers.append("btc_range")
    if blockers:
        return False, "candidate_gate_failed:" + ",".join(blockers)
    return True, ""


def btc_momentum_decision(
    *,
    params: dict[str, Any],
    side: str,
    pressure: float | None,
    spread: float | None,
    feature: dict[str, Any] | None,
) -> tuple[bool, str]:
    required = ["btc_range_15m_bps", "btc_move_1m_bps", "btc_move_5m_bps", "btc_move_15m_bps"]
    if parse_float(params.get("rsi_weight")) not in (None, 0.0):
        required.append("btc_rsi14")
    if parse_float(params.get("macd_weight")) not in (None, 0.0):
        required.append("btc_macd_hist")
    missing = missing_feature_keys(feature, required)
    if pressure is None:
        missing.append(f"{side}_opponent_pressure")
    if spread is None:
        missing.append(f"spread_{side}")
    if missing:
        return False, "candidate_missing_feature:" + ",".join(sorted(set(missing)))

    sign = side_sign(side)
    if sign == 0:
        return False, "candidate_gate_failed:side"
    range_15m = max(abs(feature_number(feature, "btc_range_15m_bps") or 0.0), 1.0)
    move_score = (
        (parse_float(params.get("w_1m")) or 0.0) * (feature_number(feature, "btc_move_1m_bps") or 0.0)
        + (parse_float(params.get("w_5m")) or 0.0) * (feature_number(feature, "btc_move_5m_bps") or 0.0)
        + (parse_float(params.get("w_15m")) or 0.0) * (feature_number(feature, "btc_move_15m_bps") or 0.0)
    )
    rsi14 = feature_number(feature, "btc_rsi14") or 50.0
    macd_hist = feature_number(feature, "btc_macd_hist") or 0.0
    score = (
        sign * move_score / math.sqrt(range_15m)
        + (parse_float(params.get("rsi_weight")) or 0.0) * sign * (rsi14 - 50.0) / 20.0
        + (parse_float(params.get("macd_weight")) or 0.0) * sign * macd_hist / 20.0
        - (parse_float(params.get("pressure_penalty")) or 0.0) * float(pressure or 0.0)
        - (parse_float(params.get("spread_penalty")) or 0.0) * float(spread or 0.0)
        - (parse_float(params.get("range_penalty")) or 0.0) * range_15m / 100.0
    )
    min_score = parse_float(params.get("min_score"))
    if min_score is not None and score < min_score:
        return False, "candidate_gate_failed:momentum_score"
    return True, ""


def online_neighbor_decision(
    *,
    params: dict[str, Any],
    side: str,
    feature: dict[str, Any] | None,
) -> tuple[bool, str]:
    required = [
        f"online_neighbor_{side}_history_count",
        f"online_neighbor_{side}_win_rate",
        f"online_neighbor_{side}_model_ev_cents",
        f"online_neighbor_{side}_lcb_cents",
    ]
    missing = missing_feature_keys(feature, required)
    if missing:
        return False, "candidate_missing_feature:" + ",".join(sorted(set(missing)))

    history_count = side_feature_number(feature, side, "history_count") or 0.0
    win_rate = side_feature_number(feature, side, "win_rate")
    model_ev = side_feature_number(feature, side, "model_ev_cents")
    lcb = side_feature_number(feature, side, "lcb_cents")
    blockers: list[str] = []
    min_history = parse_float(params.get("min_history"))
    min_win_rate = parse_float(params.get("min_neighbor_win_rate"))
    min_model_ev = parse_float(params.get("min_model_ev_cents"))
    min_lcb = parse_float(params.get("min_lcb_cents"))
    if min_history is not None and history_count < min_history:
        blockers.append("online_neighbor_history_count")
    if min_win_rate is not None and (win_rate is None or win_rate < min_win_rate):
        blockers.append("online_neighbor_win_rate")
    if min_model_ev is not None and (model_ev is None or model_ev < min_model_ev):
        blockers.append("online_neighbor_model_ev")
    if min_lcb is not None and (lcb is None or lcb < min_lcb):
        blockers.append("online_neighbor_lcb")
    if blockers:
        return False, "candidate_gate_failed:" + ",".join(blockers)
    return True, ""


def evaluate_candidate(
    candidate: dict[str, Any],
    event: dict[str, Any],
    feature: dict[str, Any] | None = None,
) -> tuple[bool, str, str]:
    event_type = str(event.get("event_type") or "")
    reason = str(event.get("decision_reason") or "")
    family = str(entry_logic(candidate).get("family") or "")
    params = entry_params(candidate)
    side = str(event.get("side") or "").lower()
    limit = candidate_limit(candidate, event, feature, side)

    if event_type not in {"liquidity_dwell_approved", "liquidity_dwell_rejected"}:
        return False, "observe", event_type
    if family == "logged_live_liquidity_dwell" and event_type == "liquidity_dwell_rejected":
        return False, "reject", reason or "logged_live_reject"
    if family == "logged_live_liquidity_dwell":
        return True, "approve", ""

    if family == "blocked_missing_feature":
        required = [str(item) for item in params.get("required_features", []) if str(item)]
        return False, "reject", "candidate_missing_feature:" + ",".join(required or ["unspecified"])

    pressure = candidate_pressure(event, feature, side)
    spread = candidate_spread(event, feature, side)
    quality_share = parse_float(event.get("quality_share"))
    quality_seconds = parse_float(event.get("quality_seconds"))
    bid_sum = candidate_bid_sum(event, feature)
    blockers = apply_quote_gates(
        params=params,
        limit=limit,
        pressure=pressure,
        spread=spread,
        quality_share=quality_share,
        quality_seconds=quality_seconds,
        bid_sum=bid_sum,
    )
    if blockers:
        return False, "reject", "candidate_gate_failed:" + ",".join(blockers)
    if family in {"btc_spot_ev_fixed", "btc_spot_ev_roi_volatility"}:
        passed, reject_reason = btc_ev_decision(
            params=params,
            side=side,
            limit=limit,
            pressure=pressure,
            spread=spread,
            feature=feature,
        )
        return (True, "approve", "") if passed else (False, "reject", reject_reason)
    if family == "btc_momentum_concordance":
        passed, reject_reason = btc_momentum_decision(
            params=params,
            side=side,
            pressure=pressure,
            spread=spread,
            feature=feature,
        )
        return (True, "approve", "") if passed else (False, "reject", reject_reason)
    if family == "online_neighbor_lcb":
        passed, reject_reason = online_neighbor_decision(
            params=params,
            side=side,
            feature=feature,
        )
        return (True, "approve", "") if passed else (False, "reject", reject_reason)
    return True, "approve", ""


def followup_events(execution_events: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    out: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in execution_events:
        key = (str(event.get("market") or ""), str(event.get("side") or ""))
        if key[0] and key[1]:
            out[key].append(event)
    for rows in out.values():
        rows.sort(key=lambda event: parse_dt(event.get("ts_wall")) or datetime.min.replace(tzinfo=UTC))
    return out


def find_followup(approval_event: dict[str, Any], by_market_side: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any] | None:
    market = str(approval_event.get("market") or "")
    side = str(approval_event.get("side") or "")
    ts = parse_dt(approval_event.get("ts_wall"))
    if not market or not side or ts is None:
        return None
    rows = by_market_side.get((market, side), [])
    candidates: list[dict[str, Any]] = []
    for row in rows:
        row_ts = parse_dt(row.get("ts_wall"))
        if row_ts is None or row_ts < ts or row_ts > ts + timedelta(seconds=10):
            continue
        if row.get("event_type") in {"execution_deferred", "order_submit_success", "fill_full"}:
            candidates.append(row)
    return candidates[0] if candidates else None


def parse_depth(value: Any) -> float | None:
    parsed = parse_float(value)
    return parsed


def classify_blocker(
    *,
    decision: str,
    reject_reason: str,
    event: dict[str, Any],
    followup: dict[str, Any] | None,
    requested_size: int,
) -> tuple[str, float, float, float, float, bool, float | None]:
    limit_depth = parse_depth(event.get("executable_depth_at_limit")) or parse_depth(event.get("eligible_depth")) or 0.0
    one_worse = parse_depth(event.get("executable_depth_one_cent_lower")) or 0.0
    two_worse = parse_depth(event.get("executable_depth_two_cents_lower")) or 0.0
    slippage: float | None = None
    if limit_depth >= requested_size:
        slippage = 0.0
    elif one_worse >= requested_size:
        slippage = 1.0
    elif two_worse >= requested_size:
        slippage = 2.0

    if decision != "approve":
        return f"reject:{reject_reason or 'unknown'}", limit_depth, one_worse, two_worse, 0.0, False, slippage

    if followup is not None and followup.get("event_type") == "execution_deferred":
        result = str(followup.get("result") or "execution_deferred")
        if result == "insufficient_balance":
            result = "account_insufficient_balance"
        return result, limit_depth, one_worse, two_worse, 0.0, False, slippage

    if followup is not None and followup.get("event_type") == "order_submit_success":
        fill_count = parse_float(followup.get("fill_count")) or 0.0
        if fill_count <= 0.0:
            return "ioc_zero_fill", limit_depth, one_worse, two_worse, 0.0, False, slippage
        return "none", limit_depth, one_worse, two_worse, min(float(requested_size), fill_count), True, 0.0

    if followup is not None and followup.get("event_type") == "fill_full":
        fill_count = parse_float(followup.get("fill_count")) or float(requested_size)
        return "none", limit_depth, one_worse, two_worse, min(float(requested_size), fill_count), True, 0.0

    book_age = parse_float(event.get("book_age_ms"))
    max_book_age = parse_float(event.get("max_book_age_ms")) or 250.0
    if book_age is not None and book_age > max_book_age:
        return "stale_book_age", limit_depth, one_worse, two_worse, 0.0, False, slippage
    if limit_depth <= 0.0:
        return "depth_unavailable_backfill", limit_depth, one_worse, two_worse, 0.0, False, slippage
    if limit_depth < requested_size:
        return "insufficient_depth", limit_depth, one_worse, two_worse, 0.0, False, slippage
    return "none", limit_depth, one_worse, two_worse, float(requested_size), True, 0.0


def gross_pnl(side: str, outcome: str | None, limit: int | None, size: int) -> tuple[int | None, int | None]:
    if outcome is None or limit is None or side not in {"yes", "no"}:
        return None, None
    per_contract = 100 - limit if side == outcome else -limit
    return per_contract, per_contract * size


def time_to_close_bucket(seconds_to_close: Any) -> str:
    seconds = parse_float(seconds_to_close)
    if seconds is None:
        return "unknown"
    if seconds < 0:
        return "post_close"
    if seconds < 30:
        return "0_30s"
    if seconds < 60:
        return "30_60s"
    if seconds < 120:
        return "60_120s"
    if seconds < 240:
        return "120_240s"
    if seconds < 480:
        return "240_480s"
    return "480s_plus"


def build_tapes(dataset_tag: str, spec: dict[str, Any], lab: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    candidates = [candidate for candidate in spec.get("candidates", []) if candidate.get("enabled")]
    candidate_rows: list[dict[str, Any]] = []
    fillability_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    anti_leakage_violations: list[dict[str, Any]] = []
    followups = followup_events(lab["execution_events"])

    decision_events = [
        event
        for event in lab["execution_events"]
        if event.get("event_type") in {"liquidity_dwell_approved", "liquidity_dwell_rejected"}
    ]
    decision_event_counts = Counter(str(event.get("event_type") or "unknown") for event in decision_events)
    latest_decision_event: dict[str, Any] | None = None
    latest_decision_ts: datetime | None = None
    for event in decision_events:
        event_ts = parse_dt(event.get("ts_wall"))
        if event_ts is not None and (latest_decision_ts is None or event_ts > latest_decision_ts):
            latest_decision_ts = event_ts
            latest_decision_event = event
    for source_index, event in enumerate(decision_events, start=1):
        event_ts = parse_dt(event.get("ts_wall"))
        market = str(event.get("market") or "")
        side = str(event.get("side") or "").lower()
        feature = find_feature(lab.get("features_by_market") or {}, market, event_ts)
        close_dt = lab["closes"].get(market) or parse_market_close_from_ticker(market)
        seconds_to_close = (close_dt - event_ts).total_seconds() if close_dt and event_ts else None
        outcome, label_ts, label_source = infer_outcome(market, lab["closes"], lab["heartbeats"], now=now)
        leakage_label = bool(event_ts and label_ts and label_ts <= event_ts)
        for candidate in candidates:
            passed, decision, reject_reason = evaluate_candidate(candidate, event, feature)
            size = parse_int(((candidate.get("sizing") or {}).get("contracts"))) or parse_int(event.get("position_size")) or 2
            limit = candidate_limit(candidate, event, feature, side)
            decision_id = stable_id(dataset_tag, candidate["candidate_id"], source_index, market, side, event.get("ts_wall"))
            gate_json = json.dumps(gate_values(event, feature, side, limit), sort_keys=True, separators=(",", ":"))
            thresholds = entry_params(candidate)
            threshold_json = json.dumps(thresholds, sort_keys=True, separators=(",", ":"))
            feature_ts = feature.get("_feature_ts") if feature else None
            source_ts = feature_ts.isoformat() if feature_ts else (event_ts.isoformat() if event_ts else None)
            available_at = event_ts.isoformat() if event_ts else None
            candidate_rows.append(
                {
                    "decision_id": decision_id,
                    "candidate_id": candidate["candidate_id"],
                    "strategy_id": candidate.get("strategy_id", ""),
                    "strategy_version": candidate.get("strategy_version", ""),
                    "dataset_tag": dataset_tag,
                    "source_feature_ts": source_ts,
                    "available_at": available_at,
                    "market_ticker": market,
                    "side": side,
                    "proposed_limit_cents": limit,
                    "proposed_size": size,
                    "seconds_to_close": seconds_to_close,
                    "all_gates_passed": bool(passed),
                    "decision": decision,
                    "reject_reason": reject_reason,
                    "gate_values_json": gate_json,
                    "thresholds_json": threshold_json,
                    "code_version": SCRIPT_VERSION,
                }
            )

            followup = find_followup(event, followups) if passed else None
            blocker, depth0, depth1, depth2, estimated_fill, fillable, slippage = classify_blocker(
                decision=decision,
                reject_reason=reject_reason,
                event=event,
                followup=followup,
                requested_size=size,
            )
            fillability_rows.append(
                {
                    "decision_id": decision_id,
                    "snapshot_ts": source_ts,
                    "available_at": available_at,
                    "market_ticker": market,
                    "side": side,
                    "limit_cents": limit,
                    "requested_size": size,
                    "fillable_at_limit": fillable,
                    "fillable_size_at_limit": depth0,
                    "fillable_size_one_cent_worse": depth1,
                    "fillable_size_two_cents_worse": depth2,
                    "estimated_ioc_fill_size": estimated_fill,
                    "estimated_slippage_cents": slippage,
                    "book_age_ms": parse_float(event.get("book_age_ms")),
                    "feed_age_ms": parse_float(event.get("feed_age_ms")),
                    "trust_state": event.get("trust_state"),
                    "sequence_ok": parse_bool(event.get("sequence_ok")),
                    "account_snapshot_age_ms": parse_float(event.get("account_age_ms") or (followup or {}).get("account_age_ms")),
                    "blocker": blocker,
                }
            )

            scored_outcome = outcome
            scored_label_ts = label_ts
            scored_label_source = label_source
            if leakage_label:
                anti_leakage_violations.append(
                    {
                        "decision_id": decision_id,
                        "market_ticker": market,
                        "side": side,
                        "decision_ts": event_ts.isoformat() if event_ts else None,
                        "label_available_at": label_ts.isoformat() if label_ts else None,
                        "label_source": label_source,
                        "action": "outcome_label_quarantined",
                    }
                )
                scored_outcome = None
                scored_label_ts = None
                scored_label_source = f"anti_leakage_quarantined:{label_source}"
            pnl_per_contract, pnl_for_size = gross_pnl(side, scored_outcome, limit, size)
            outcome_rows.append(
                {
                    "decision_id": decision_id,
                    "market_ticker": market,
                    "side": side,
                    "label_available_at": scored_label_ts.isoformat() if scored_label_ts else None,
                    "settlement_ts": close_dt.isoformat() if close_dt else None,
                    "market_result": scored_outcome,
                    "would_win": bool(scored_outcome == side) if scored_outcome else None,
                    "gross_pnl_cents_per_contract": pnl_per_contract,
                    "gross_pnl_cents_for_size": pnl_for_size,
                    "label_source": scored_label_source,
                }
            )

    return {
        "candidate_rows": candidate_rows,
        "fillability_rows": fillability_rows,
        "outcome_rows": outcome_rows,
        "anti_leakage_violations": anti_leakage_violations,
        "candidate_count": len(candidates),
        "source_decision_event_count": len(decision_events),
        "source_decision_event_counts": dict(decision_event_counts),
        "latest_source_decision_ts": latest_decision_ts.isoformat() if latest_decision_ts else None,
        "latest_source_decision_market": str((latest_decision_event or {}).get("market") or ""),
        "latest_source_decision_type": str((latest_decision_event or {}).get("event_type") or ""),
    }


def ensure_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = None
    return out[columns + [col for col in out.columns if col not in columns]]


def write_partitioned_parquet(df: pd.DataFrame, root: Path, partition_cols: list[str], stem: str) -> int:
    if df.empty:
        return 0
    count = 0
    working = df.copy()
    for col in partition_cols:
        if col not in working.columns:
            working[col] = "unknown"
        working[col] = working[col].astype(object).where(pd.notna(working[col]), "unknown")
        working[col] = working[col].replace({"": "unknown", "None": "unknown", "NaT": "unknown", "nan": "unknown"})
    for key, group in working.groupby(partition_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        target = root
        for col, value in zip(partition_cols, key):
            target = target / f"{col}={value}"
        target.mkdir(parents=True, exist_ok=True)
        table = pa.Table.from_pandas(group.drop(columns=partition_cols, errors="ignore").reset_index(drop=True), preserve_index=False)
        pq.write_table(table, target / f"{stem}.parquet", compression="snappy")
        count += 1
    return count


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def max_timestamp_from_frame(frame: pd.DataFrame, columns: tuple[str, ...]) -> datetime | None:
    latest: datetime | None = None
    if frame.empty:
        return latest
    for column in columns:
        if column not in frame.columns:
            continue
        series = pd.to_datetime(frame[column], utc=True, errors="coerce").dropna()
        if series.empty:
            continue
        parsed = series.max().to_pydatetime()
        if latest is None or parsed > latest:
            latest = parsed
    return latest


def positive_lag_seconds(later: datetime | None, earlier: datetime | None) -> float | None:
    if later is None or earlier is None:
        return None
    return round(max(0.0, (later - earlier).total_seconds()), 3)


def dataframe_counter(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame.columns:
        return {}
    series = frame[column].fillna("missing").astype(str)
    return {str(key): int(value) for key, value in series.value_counts(dropna=False).sort_index().items()}


def finite_float_summary(values: pd.Series) -> dict[str, float | int | None]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {
        "count": int(len(numeric)),
        "min": round(float(numeric.min()), 3),
        "median": round(float(numeric.median()), 3),
        "max": round(float(numeric.max()), 3),
    }


def capture_quality_summary(
    *,
    lab: dict[str, Any],
    manifest: dict[str, Any],
    tapes: dict[str, Any],
    checked_at: datetime,
) -> dict[str, Any]:
    latest_raw = lab.get("latest_raw_ts")
    latest_source = parse_dt(tapes.get("latest_source_decision_ts"))
    raw_age = positive_lag_seconds(checked_at, latest_raw)
    source_decision_age = positive_lag_seconds(checked_at, latest_source)
    recorder_type = str(manifest.get("recorder_type") or "unknown")
    has_capture = bool(lab.get("rows")) and bool(lab.get("heartbeats")) and bool(lab.get("execution_events"))
    issues: list[str] = []
    if not has_capture:
        issues.append("missing_lab_capture")
    if raw_age is None:
        issues.append("latest_raw_event_unknown")
    elif raw_age > 300:
        issues.append("raw_capture_stale_gt_300s")
    if recorder_type == "backfill":
        issues.append("dataset_is_backfill_not_native_passive")
    if not latest_source:
        issues.append("no_source_decision_events")

    if not has_capture:
        status = "FAIL_missing_capture"
    elif raw_age is not None and raw_age > 300:
        status = "FAIL_capture_stale"
    elif recorder_type == "backfill":
        status = "WARN_backfill_current"
    else:
        status = "PASS_native_or_attached_current"

    return {
        "status": status,
        "issues": issues,
        "checked_at_utc": checked_at.isoformat(),
        "recorder_type": recorder_type,
        "recorder_version": manifest.get("recorder_version") or "",
        "data_quality_flags": list(manifest.get("data_quality_flags") or []),
        "latest_raw_event_ts": latest_raw.isoformat() if latest_raw else None,
        "raw_capture_age_seconds": raw_age,
        "latest_source_decision_ts": latest_source.isoformat() if latest_source else None,
        "source_decision_age_seconds": source_decision_age,
        "raw_event_rows_loaded": int(len(lab.get("rows") or [])),
        "heartbeat_market_count": int(len(lab.get("heartbeats") or {})),
        "execution_event_count": int(len(lab.get("execution_events") or [])),
        "source_decision_event_counts": tapes.get("source_decision_event_counts") or {},
    }


def fillability_quality_summary(fillability_df: pd.DataFrame) -> dict[str, Any]:
    if fillability_df.empty:
        return {
            "status": "FAIL_no_fillability_rows",
            "rows": 0,
            "blocker_counts": {},
            "depth_quality_flags": ["no_fillability_rows"],
        }
    blocker_counts = dataframe_counter(fillability_df, "blocker")
    rows = int(len(fillability_df))
    depth_unavailable = int((fillability_df.get("blocker", pd.Series(dtype=object)).astype(str) == "depth_unavailable_backfill").sum())
    stale_like = int(fillability_df.get("blocker", pd.Series(dtype=object)).astype(str).str.contains("stale", na=False).sum())
    account_missing = int(pd.to_numeric(fillability_df.get("account_snapshot_age_ms"), errors="coerce").isna().sum())
    book_age_missing = int(pd.to_numeric(fillability_df.get("book_age_ms"), errors="coerce").isna().sum())
    feed_age_missing = int(pd.to_numeric(fillability_df.get("feed_age_ms"), errors="coerce").isna().sum())
    full_fill_rows = int((pd.to_numeric(fillability_df.get("estimated_ioc_fill_size"), errors="coerce") >= pd.to_numeric(fillability_df.get("requested_size"), errors="coerce")).sum())
    sequence_values = fillability_df.get("sequence_ok")
    sequence_unknown = int(sequence_values.isna().sum()) if sequence_values is not None else rows
    depth_quality_flags: list[str] = []
    if depth_unavailable:
        depth_quality_flags.append("depth_unavailable_backfill_present")
    if book_age_missing:
        depth_quality_flags.append("book_age_missing_present")
    if feed_age_missing:
        depth_quality_flags.append("feed_age_missing_present")
    if account_missing:
        depth_quality_flags.append("account_age_missing_present")
    if sequence_unknown:
        depth_quality_flags.append("sequence_health_unknown_present")
    return {
        "status": "MONITOR_backfill_depth_limits" if depth_quality_flags else "PASS",
        "rows": rows,
        "blocker_counts": blocker_counts,
        "depth_unavailable_backfill_rows": depth_unavailable,
        "stale_blocker_rows": stale_like,
        "estimated_full_fill_rows": full_fill_rows,
        "book_age_missing_rows": book_age_missing,
        "feed_age_missing_rows": feed_age_missing,
        "account_snapshot_age_missing_rows": account_missing,
        "sequence_ok_unknown_rows": sequence_unknown,
        "book_age_ms_summary": finite_float_summary(fillability_df.get("book_age_ms", pd.Series(dtype=float))),
        "feed_age_ms_summary": finite_float_summary(fillability_df.get("feed_age_ms", pd.Series(dtype=float))),
        "depth_quality_flags": depth_quality_flags,
    }


def label_quality_summary(
    outcome_df: pd.DataFrame,
    anti_leakage_violations: list[dict[str, Any]],
) -> dict[str, Any]:
    if outcome_df.empty:
        return {
            "status": "FAIL_no_outcome_rows",
            "rows": 0,
            "label_source_counts": {},
            "unlabeled_rows": 0,
            "anti_leakage_quarantine_count": len(anti_leakage_violations),
        }
    unlabeled_rows = int(outcome_df["market_result"].isna().sum()) if "market_result" in outcome_df.columns else int(len(outcome_df))
    label_source_counts = dataframe_counter(outcome_df, "label_source")
    quarantine_by_source = Counter(str(row.get("label_source") or "unknown") for row in anti_leakage_violations)
    quarantine_by_market = Counter(str(row.get("market_ticker") or "unknown") for row in anti_leakage_violations)
    status = "WARN_labels_quarantined" if anti_leakage_violations else ("MONITOR_unlabeled_outcomes_present" if unlabeled_rows else "PASS")
    return {
        "status": status,
        "rows": int(len(outcome_df)),
        "label_source_counts": label_source_counts,
        "unlabeled_rows": unlabeled_rows,
        "anti_leakage_quarantine_count": int(len(anti_leakage_violations)),
        "anti_leakage_quarantine_by_source": dict(quarantine_by_source),
        "anti_leakage_quarantine_by_market": dict(quarantine_by_market),
    }


def tape_freshness_audit(
    *,
    tapes: dict[str, Any],
    candidate_df: pd.DataFrame,
    fillability_df: pd.DataFrame,
    outcome_df: pd.DataFrame,
) -> dict[str, Any]:
    source_latest = parse_dt(tapes.get("latest_source_decision_ts"))
    candidate_latest = max_timestamp_from_frame(candidate_df, ("available_at", "source_feature_ts"))
    fillability_latest = max_timestamp_from_frame(fillability_df, ("available_at", "snapshot_ts"))
    outcome_latest = max_timestamp_from_frame(outcome_df, ("label_available_at", "settlement_ts"))
    unlabeled_outcomes = int(outcome_df["market_result"].isna().sum()) if not outcome_df.empty else 0

    candidate_lag = positive_lag_seconds(source_latest, candidate_latest)
    fillability_lag = positive_lag_seconds(source_latest, fillability_latest)
    outcome_lag = positive_lag_seconds(source_latest, outcome_latest)
    issues: list[str] = []
    if candidate_lag is None:
        issues.append("candidate_decision_tape_missing")
    elif candidate_lag > 0:
        issues.append("candidate_decision_tape_lags_source")
    if fillability_lag is None:
        issues.append("fillability_snapshot_tape_missing")
    elif fillability_lag > 0:
        issues.append("fillability_snapshot_tape_lags_source")
    if unlabeled_outcomes:
        issues.append("unlabeled_or_unsettled_outcomes_present")

    return {
        "status": "PASS" if not issues else "MONITOR",
        "issues": issues,
        "latest_source_decision_ts": source_latest.isoformat() if source_latest else None,
        "latest_source_decision_market": tapes.get("latest_source_decision_market") or "",
        "latest_source_decision_type": tapes.get("latest_source_decision_type") or "",
        "source_decision_event_counts": tapes.get("source_decision_event_counts") or {},
        "latest_candidate_decision_ts": candidate_latest.isoformat() if candidate_latest else None,
        "latest_fillability_snapshot_ts": fillability_latest.isoformat() if fillability_latest else None,
        "latest_outcome_label_ts": outcome_latest.isoformat() if outcome_latest else None,
        "candidate_decision_lag_vs_source_seconds": candidate_lag,
        "fillability_lag_vs_source_seconds": fillability_lag,
        "outcome_label_lag_vs_source_seconds": outcome_lag,
        "unlabeled_outcome_count": unlabeled_outcomes,
    }


def tape_integrity_audit(
    *,
    candidate_rows: list[dict[str, Any]],
    fillability_rows: list[dict[str, Any]],
    outcome_rows: list[dict[str, Any]],
    candidate_count: int,
    source_decision_event_count: int,
) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    decision_ids = [str(row.get("decision_id") or "") for row in candidate_rows]
    fillability_ids = [str(row.get("decision_id") or "") for row in fillability_rows]
    outcome_ids = [str(row.get("decision_id") or "") for row in outcome_rows]
    decision_id_counts = Counter(decision_ids)
    candidate_by_id = {str(row.get("decision_id") or ""): row for row in candidate_rows}

    def add_violation(kind: str, decision_id: str | None = None, **details: Any) -> None:
        if len(violations) >= 50:
            return
        payload = {"kind": kind}
        if decision_id:
            payload["decision_id"] = decision_id
        payload.update(details)
        violations.append(payload)

    expected_rows = int(candidate_count) * int(source_decision_event_count)
    if expected_rows and len(candidate_rows) != expected_rows:
        add_violation(
            "candidate_row_count_mismatch",
            expected_rows=expected_rows,
            actual_rows=len(candidate_rows),
        )

    duplicate_ids = [decision_id for decision_id, count in decision_id_counts.items() if decision_id and count > 1]
    for decision_id in duplicate_ids[:25]:
        add_violation("duplicate_candidate_decision_id", decision_id, count=decision_id_counts[decision_id])

    for row in candidate_rows:
        decision_id = str(row.get("decision_id") or "")
        if not decision_id:
            add_violation("missing_candidate_decision_id")
            continue
        source_ts = parse_dt(row.get("source_feature_ts"))
        available_at = parse_dt(row.get("available_at"))
        if source_ts is not None and available_at is not None and source_ts > available_at:
            add_violation(
                "source_feature_after_decision_availability",
                decision_id,
                source_feature_ts=source_ts.isoformat(),
                available_at=available_at.isoformat(),
            )
        if not row.get("side"):
            add_violation("missing_candidate_side", decision_id)
        if parse_int(row.get("proposed_size")) is None:
            add_violation("missing_candidate_size", decision_id)
        if row.get("decision") == "approve" and parse_int(row.get("proposed_limit_cents")) is None:
            add_violation("approved_decision_missing_limit", decision_id)

    fillability_id_set = set(fillability_ids)
    outcome_id_set = set(outcome_ids)
    candidate_id_set = set(decision_id for decision_id in decision_ids if decision_id)
    for decision_id in sorted(candidate_id_set - fillability_id_set)[:25]:
        add_violation("missing_fillability_snapshot", decision_id)
    for decision_id in sorted(candidate_id_set - outcome_id_set)[:25]:
        add_violation("missing_outcome_label", decision_id)
    for decision_id in sorted(fillability_id_set - candidate_id_set)[:25]:
        add_violation("orphan_fillability_snapshot", decision_id)
    for decision_id in sorted(outcome_id_set - candidate_id_set)[:25]:
        add_violation("orphan_outcome_label", decision_id)

    for row in fillability_rows:
        decision_id = str(row.get("decision_id") or "")
        candidate = candidate_by_id.get(decision_id, {})
        decision_available_at = parse_dt(candidate.get("available_at"))
        available_at = parse_dt(row.get("available_at"))
        if available_at is not None and decision_available_at is not None and available_at > decision_available_at:
            add_violation(
                "fillability_available_after_decision",
                decision_id,
                fillability_available_at=available_at.isoformat(),
                decision_available_at=decision_available_at.isoformat(),
            )
        if not row.get("blocker"):
            add_violation("missing_fillability_blocker", decision_id)

    for row in outcome_rows:
        decision_id = str(row.get("decision_id") or "")
        candidate = candidate_by_id.get(decision_id, {})
        decision_available_at = parse_dt(candidate.get("available_at"))
        label_available_at = parse_dt(row.get("label_available_at"))
        if label_available_at is not None and decision_available_at is not None and label_available_at <= decision_available_at:
            add_violation(
                "outcome_label_available_at_or_before_decision",
                decision_id,
                label_available_at=label_available_at.isoformat(),
                decision_available_at=decision_available_at.isoformat(),
            )

    return {
        "status": "PASS" if not violations else "WARN",
        "expected_candidate_decision_rows": expected_rows,
        "candidate_decision_rows": len(candidate_rows),
        "fillability_snapshot_rows": len(fillability_rows),
        "outcome_label_rows": len(outcome_rows),
        "duplicate_decision_id_count": len(duplicate_ids),
        "missing_fillability_count": len(candidate_id_set - fillability_id_set),
        "missing_outcome_label_count": len(candidate_id_set - outcome_id_set),
        "orphan_fillability_count": len(fillability_id_set - candidate_id_set),
        "orphan_outcome_label_count": len(outcome_id_set - candidate_id_set),
        "violation_count": len(violations),
        "violations": violations,
    }


def score_candidates(
    spec: dict[str, Any],
    candidate_rows: list[dict[str, Any]],
    fillability_rows: list[dict[str, Any]],
    outcome_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gates = spec.get("promotion_gates") or {}
    min_decisions = int(gates.get("min_forward_decisions", 25))
    min_all_pnl = int(gates.get("approved_stream_pnl_cents_min", 1))
    min_fill_pnl = int(gates.get("fillability_adjusted_pnl_cents_min", 1))
    max_fp_loss = int(gates.get("max_false_positive_loss_cents", 300))
    require_side_stability = bool(gates.get("require_side_stability", True))
    require_no_unlabeled = bool(gates.get("require_no_unlabeled_settlements", True))

    fill_by_id = {row["decision_id"]: row for row in fillability_rows}
    label_by_id = {row["decision_id"]: row for row in outcome_rows}
    by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        by_candidate[str(row["candidate_id"])].append(row)

    scores: list[dict[str, Any]] = []
    for candidate in spec.get("candidates", []):
        if not candidate.get("enabled"):
            continue
        candidate_id = str(candidate["candidate_id"])
        rows = by_candidate.get(candidate_id, [])
        approved = [row for row in rows if row.get("decision") == "approve" and row.get("all_gates_passed")]
        rejected = [row for row in rows if row.get("decision") == "reject"]
        labeled_approved = [row for row in approved if label_by_id.get(row["decision_id"], {}).get("market_result")]
        unlabeled_approved = len(approved) - len(labeled_approved)
        all_pnl = int(sum(label_by_id[row["decision_id"]].get("gross_pnl_cents_for_size") or 0 for row in labeled_approved))
        false_positive_loss = int(
            -sum(
                min(0, int(label_by_id[row["decision_id"]].get("gross_pnl_cents_for_size") or 0))
                for row in labeled_approved
            )
        )
        fillability_pnl = 0
        blocker_counts: Counter[str] = Counter()
        blocker_pnl: Counter[str] = Counter()
        side_pnl: Counter[str] = Counter()
        side_counts: Counter[str] = Counter()
        winners = 0
        losers = 0
        for row in labeled_approved:
            label = label_by_id[row["decision_id"]]
            fill = fill_by_id.get(row["decision_id"], {})
            size = parse_float(row.get("proposed_size")) or 0.0
            estimated_fill = parse_float(fill.get("estimated_ioc_fill_size")) or 0.0
            per_contract = parse_float(label.get("gross_pnl_cents_per_contract")) or 0.0
            blocker = str(fill.get("blocker") or "unknown")
            pnl = int(label.get("gross_pnl_cents_for_size") or 0)
            if estimated_fill >= size and blocker == "none":
                fillability_pnl += int(round(per_contract * estimated_fill))
            else:
                blocker_counts[blocker] += 1
                blocker_pnl[blocker] += pnl
            side = str(row.get("side") or "unknown")
            side_pnl[side] += pnl
            side_counts[side] += 1
            if bool(label.get("would_win")):
                winners += 1
            else:
                losers += 1

        missed_winner_rejects = 0
        avoided_loser_rejects = 0
        unlabeled_rejected = 0
        rejected_bypass_pnl = 0
        missed_winner_reject_pnl = 0
        avoided_loser_reject_loss = 0
        reject_reason_labeled_counts: Counter[str] = Counter()
        reject_reason_pnl: Counter[str] = Counter()
        reject_reason_missed_winner_counts: Counter[str] = Counter()
        reject_reason_avoided_loser_counts: Counter[str] = Counter()
        reject_reason_missed_winner_pnl: Counter[str] = Counter()
        reject_reason_avoided_loser_loss: Counter[str] = Counter()
        for row in rejected:
            label = label_by_id.get(row["decision_id"], {})
            if not label.get("market_result"):
                unlabeled_rejected += 1
                continue
            reason = str(row.get("reject_reason") or "unknown")
            pnl = int(label.get("gross_pnl_cents_for_size") or 0)
            rejected_bypass_pnl += pnl
            reject_reason_labeled_counts[reason] += 1
            reject_reason_pnl[reason] += pnl
            if label.get("would_win") is True:
                missed_winner_rejects += 1
                missed_winner_reject_pnl += max(0, pnl)
                reject_reason_missed_winner_counts[reason] += 1
                reject_reason_missed_winner_pnl[reason] += max(0, pnl)
            elif label.get("would_win") is False:
                avoided_loser_rejects += 1
                avoided_loss = -min(0, pnl)
                avoided_loser_reject_loss += avoided_loss
                reject_reason_avoided_loser_counts[reason] += 1
                reject_reason_avoided_loser_loss[reason] += avoided_loss

        side_stable = True
        if require_side_stability:
            populated_sides = [side for side, count in side_counts.items() if count > 0]
            side_stable = bool(populated_sides) and all(side_pnl[side] >= 0 for side in populated_sides)

        gate_results = {
            "min_forward_decisions": len(labeled_approved) >= min_decisions,
            "approved_stream_pnl": all_pnl >= min_all_pnl,
            "fillability_adjusted_pnl": fillability_pnl >= min_fill_pnl,
            "false_positive_loss": false_positive_loss <= max_fp_loss,
            "side_stability": side_stable,
            "no_unlabeled_settlements": (unlabeled_approved == 0) if require_no_unlabeled else True,
        }
        promotion_fail_reasons = [name for name, passed in gate_results.items() if not passed]
        promotion_status = "PASS" if all(gate_results.values()) else "FAIL"

        reject_reason_counts: Counter[str] = Counter()
        time_bucket_counts: Counter[str] = Counter()
        time_bucket_pnl: Counter[str] = Counter()
        time_bucket_fillability_pnl: Counter[str] = Counter()
        false_positive_loss_by_side: Counter[str] = Counter()
        blocker_winner_counts: Counter[str] = Counter()
        blocker_loser_counts: Counter[str] = Counter()
        for row in rejected:
            reject_reason_counts[str(row.get("reject_reason") or "unknown")] += 1
        for row in labeled_approved:
            label = label_by_id[row["decision_id"]]
            fill = fill_by_id.get(row["decision_id"], {})
            pnl = int(label.get("gross_pnl_cents_for_size") or 0)
            bucket = time_to_close_bucket(row.get("seconds_to_close"))
            time_bucket_counts[bucket] += 1
            time_bucket_pnl[bucket] += pnl
            side = str(row.get("side") or "unknown")
            if pnl < 0:
                false_positive_loss_by_side[side] += -pnl
            blocker = str(fill.get("blocker") or "unknown")
            if bool(label.get("would_win")):
                blocker_winner_counts[blocker] += 1
            else:
                blocker_loser_counts[blocker] += 1
            size = parse_float(row.get("proposed_size")) or 0.0
            estimated_fill = parse_float(fill.get("estimated_ioc_fill_size")) or 0.0
            per_contract = parse_float(label.get("gross_pnl_cents_per_contract")) or 0.0
            if estimated_fill >= size and blocker == "none":
                time_bucket_fillability_pnl[bucket] += int(round(per_contract * estimated_fill))
        scores.append(
            {
                "candidate_id": candidate_id,
                "strategy_id": candidate.get("strategy_id"),
                "strategy_version": candidate.get("strategy_version"),
                "promotion_status": promotion_status,
                "gate_results": gate_results,
                "promotion_fail_reasons": promotion_fail_reasons,
                "total_decisions": len(rows),
                "approved_decisions": len(approved),
                "labeled_approved_decisions": len(labeled_approved),
                "unlabeled_approved_decisions": unlabeled_approved,
                "rejected_decisions": len(rejected),
                "approved_stream_pnl_cents": all_pnl,
                "fillability_adjusted_pnl_cents": int(fillability_pnl),
                "false_positive_loss_cents": false_positive_loss,
                "approved_winners": winners,
                "approved_losers": losers,
                "missed_winner_rejects": missed_winner_rejects,
                "avoided_loser_rejects": avoided_loser_rejects,
                "unlabeled_rejected_decisions": unlabeled_rejected,
                "rejected_bypass_pnl_cents": int(rejected_bypass_pnl),
                "missed_winner_reject_pnl_cents": int(missed_winner_reject_pnl),
                "avoided_loser_reject_loss_cents": int(avoided_loser_reject_loss),
                "blocker_counts": dict(blocker_counts),
                "blocker_pnl_cents": dict(blocker_pnl),
                "blocker_winner_counts": dict(blocker_winner_counts),
                "blocker_loser_counts": dict(blocker_loser_counts),
                "side_pnl_cents": dict(side_pnl),
                "side_counts": dict(side_counts),
                "false_positive_loss_by_side_cents": dict(false_positive_loss_by_side),
                "reject_reason_counts": dict(reject_reason_counts),
                "reject_reason_labeled_counts": dict(reject_reason_labeled_counts),
                "reject_reason_bypass_pnl_cents": dict(reject_reason_pnl),
                "reject_reason_missed_winner_counts": dict(reject_reason_missed_winner_counts),
                "reject_reason_avoided_loser_counts": dict(reject_reason_avoided_loser_counts),
                "reject_reason_missed_winner_pnl_cents": dict(reject_reason_missed_winner_pnl),
                "reject_reason_avoided_loser_loss_cents": dict(reject_reason_avoided_loser_loss),
                "time_to_close_bucket_counts": dict(time_bucket_counts),
                "time_to_close_bucket_pnl_cents": dict(time_bucket_pnl),
                "time_to_close_bucket_fillability_pnl_cents": dict(time_bucket_fillability_pnl),
            }
        )
    return scores


def render_report(summary: dict[str, Any], scores: list[dict[str, Any]], artifacts: dict[str, Path]) -> str:
    lines = [
        f"# Research Lab Gauntlet: {summary['dataset_tag']}",
        "",
        f"- Generated: `{summary['generated_at_utc']}`",
        "- Scope: research-only gauntlet build/score. No live entry logic, exit logic, production configs, secrets, locks, state, orders, or bot process were changed.",
        f"- Dataset recorder type: `{summary['recorder_type']}`; latest raw event: `{summary['latest_raw_event_ts']}`.",
        f"- Frozen spec: `{artifacts['spec']}`",
        "",
        "## Research Lab / Gauntlet Improvement",
        "",
        f"- Research Lab improvement status: `{summary['research_lab_improvement_status']}`",
        f"- Gauntlet improvement status: `{summary['gauntlet_improvement_status']}`",
        f"- Capture status: `{summary['capture_status']}`",
        f"- Candidate scoring status: `{summary['candidate_scoring_status']}`",
        f"- New edge status: `{summary['new_edge_status']}`",
        "",
        "Hardened gauntlet scoring explainability for the active dataset: direct top-historical candidate scoring, leak-free Research Lab online-neighbor feature scoring, feature-tape joins, promotion failure reasons, reject-reason economics, side false-positive cost, blocker winner/loser counts, time-to-close PnL buckets, tape-integrity checks, active-capture freshness, fillability quality, label quality, anti-leakage quarantine details, and source-to-tape freshness are machine-readable in the summary.",
        "",
        "## Capture And Tape Quality",
        "",
        f"- Capture quality: `{(summary.get('capture_quality') or {}).get('status')}`; raw age `{(summary.get('capture_quality') or {}).get('raw_capture_age_seconds')}` seconds; flags `{(summary.get('capture_quality') or {}).get('data_quality_flags')}`.",
        f"- Fillability quality: `{(summary.get('fillability_quality') or {}).get('status')}`; blockers `{(summary.get('fillability_quality') or {}).get('blocker_counts')}`; quality flags `{(summary.get('fillability_quality') or {}).get('depth_quality_flags')}`.",
        f"- Label quality: `{(summary.get('label_quality') or {}).get('status')}`; label sources `{(summary.get('label_quality') or {}).get('label_source_counts')}`.",
        "",
        "## Candidate Scores",
        "",
        "| Candidate | Approved | All-approved PnL | Fillability-adjusted PnL | False-positive cost | Blockers | Promotion |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for score in scores:
        lines.append(
            "| `{candidate_id}` | {approved} | {all_pnl}c | {fill_pnl}c | {fp}c | `{blockers}` | `{status}` |".format(
                candidate_id=score["candidate_id"],
                approved=score["labeled_approved_decisions"],
                all_pnl=score["approved_stream_pnl_cents"],
                fill_pnl=score["fillability_adjusted_pnl_cents"],
                fp=score["false_positive_loss_cents"],
                blockers=score["blocker_counts"],
                status=score["promotion_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Promotion Gate Detail",
            "",
            "| Candidate | Failed gates | Time-to-close PnL buckets | False-positive side cost |",
            "|---|---|---|---|",
        ]
    )
    for score in scores:
        lines.append(
            "| `{candidate_id}` | `{fails}` | `{time_buckets}` | `{side_fp}` |".format(
                candidate_id=score["candidate_id"],
                fails=", ".join(score.get("promotion_fail_reasons") or []) or "none",
                time_buckets=score.get("time_to_close_bucket_pnl_cents") or {},
                side_fp=score.get("false_positive_loss_by_side_cents") or {},
            )
        )
    lines.extend(
        [
            "",
            "## Reject Economics",
            "",
            "| Candidate | Rejected bypass PnL | Missed winner cents | Avoided loser cents | Reject reason bypass PnL |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for score in scores:
        lines.append(
            "| `{candidate_id}` | {bypass}c | {missed}c | {avoided}c | `{by_reason}` |".format(
                candidate_id=score["candidate_id"],
                bypass=score.get("rejected_bypass_pnl_cents", 0),
                missed=score.get("missed_winner_reject_pnl_cents", 0),
                avoided=score.get("avoided_loser_reject_loss_cents", 0),
                by_reason=score.get("reject_reason_bypass_pnl_cents") or {},
            )
        )
    lines.extend(
        [
            "",
            "## Tape Integrity",
            "",
            f"- Tape integrity status: `{summary.get('tape_integrity_status')}`",
            f"- Tape integrity violations: `{summary.get('tape_integrity_violation_count')}`",
            f"- Expected candidate decision rows: `{summary.get('expected_candidate_decision_rows')}`",
            f"- Tape freshness status: `{summary.get('tape_freshness_status')}`",
            f"- Latest source decision: `{(summary.get('tape_freshness') or {}).get('latest_source_decision_ts')}` `{(summary.get('tape_freshness') or {}).get('latest_source_decision_market')}` `{(summary.get('tape_freshness') or {}).get('latest_source_decision_type')}`",
            f"- Candidate lag vs source: `{(summary.get('tape_freshness') or {}).get('candidate_decision_lag_vs_source_seconds')}` seconds.",
            f"- Fillability lag vs source: `{(summary.get('tape_freshness') or {}).get('fillability_lag_vs_source_seconds')}` seconds.",
            "",
        "## Anti-Leakage And Provenance",
        "",
        f"- Anti-leakage status: `{summary.get('anti_leakage_status')}`",
        f"- Anti-leakage quarantines: `{summary['anti_leakage_violation_count']}`",
        f"- Unlabeled outcome rows: `{summary['unlabeled_outcome_count']}`",
        "- Any label whose inferred availability timestamp is not after its decision timestamp is quarantined and scored as unlabeled.",
        "- Labels are inferred only from Research Lab backfilled heartbeat outcomes at or after market close. This remains lower quality than native passive WS/depth capture.",
            "- Fillability depth is log-derived and often top-of-book/backfilled; native depth should remain a prerequisite for promotion.",
            "",
            "## Artifacts",
            "",
            f"- Summary JSON: `{artifacts['summary_json']}`",
            f"- Candidate score CSV: `{artifacts['scores_csv']}`",
            f"- Candidate decision tape: `{artifacts['candidate_decisions']}`",
            f"- Fillability snapshot tape: `{artifacts['fillability_snapshots']}`",
            f"- Outcome label tape: `{artifacts['outcome_labels']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def append_ledger(summary: dict[str, Any], artifacts: dict[str, Path]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": summary["generated_at_utc"],
        "automation_id": "hourly-research-lab-gauntlet-edge",
        "type": "research_lab_gauntlet_score",
        "dataset_tag": summary["dataset_tag"],
        "status": summary["candidate_scoring_status"],
        "research_lab_improvement_status": summary["research_lab_improvement_status"],
        "gauntlet_improvement_status": summary["gauntlet_improvement_status"],
        "capture_status": summary["capture_status"],
        "new_edge_status": summary["new_edge_status"],
        "tape_freshness_status": summary.get("tape_freshness_status"),
        "tape_freshness": summary.get("tape_freshness"),
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "scores": summary["scores"],
        "next_step": "Keep scoring frozen candidates on fresh Lab data; do not promote until approved and fillability-adjusted streams pass gates on native or higher-quality capture.",
    }
    with GAUNTLET_LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, default=str) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and score Research Lab gauntlet tapes.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--spec", default="")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    dataset_root = RESEARCH_ROOT / args.dataset
    metadata_root = dataset_root / "metadata"
    manifest = read_json(metadata_root / "dataset_manifest.json")
    spec, spec_path = load_or_create_spec(args.dataset, write=args.write, spec_path=Path(args.spec) if args.spec else None)
    if not spec.get("frozen"):
        raise SystemExit(f"Candidate spec must be frozen before scoring: {spec_path}")

    lab = load_lab(args.dataset)
    tapes = build_tapes(args.dataset, spec, lab)
    candidate_df = ensure_columns(pd.DataFrame(tapes["candidate_rows"]), CANDIDATE_COLUMNS)
    fillability_df = ensure_columns(pd.DataFrame(tapes["fillability_rows"]), FILLABILITY_COLUMNS)
    outcome_df = ensure_columns(pd.DataFrame(tapes["outcome_rows"]), OUTCOME_COLUMNS)
    if not candidate_df.empty:
        candidate_df["day"] = pd.to_datetime(candidate_df["available_at"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    if not fillability_df.empty:
        fillability_df["day"] = pd.to_datetime(fillability_df["available_at"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    if not outcome_df.empty:
        outcome_df["day"] = pd.to_datetime(outcome_df["settlement_ts"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")

    if args.write:
        write_partitioned_parquet(candidate_df, dataset_root / "candidate_decisions", ["candidate_id", "day"], "part-latest")
        write_partitioned_parquet(fillability_df, dataset_root / "fillability_snapshots", ["day"], "part-latest")
        write_partitioned_parquet(outcome_df, dataset_root / "outcome_labels", ["day"], "part-latest")

    scores = score_candidates(spec, tapes["candidate_rows"], tapes["fillability_rows"], tapes["outcome_rows"])
    tape_integrity = tape_integrity_audit(
        candidate_rows=tapes["candidate_rows"],
        fillability_rows=tapes["fillability_rows"],
        outcome_rows=tapes["outcome_rows"],
        candidate_count=int(tapes["candidate_count"]),
        source_decision_event_count=int(tapes["source_decision_event_count"]),
    )
    tape_freshness = tape_freshness_audit(
        tapes=tapes,
        candidate_df=candidate_df,
        fillability_df=fillability_df,
        outcome_df=outcome_df,
    )
    generated_at = utc_now()
    stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    report_path = EDGE_DIR / f"codex_research_lab_gauntlet_{args.dataset}_{stamp}.md"
    summary_path = EDGE_DIR / f"codex_research_lab_gauntlet_{args.dataset}_{stamp}.json"
    scores_csv = EDGE_DIR / f"codex_research_lab_gauntlet_scores_{args.dataset}_{stamp}.csv"
    write_csv(scores_csv, scores)
    latest_raw_ts = lab["latest_raw_ts"].isoformat() if lab["latest_raw_ts"] else None
    recorder_type = str(manifest.get("recorder_type") or "unknown")
    capture_quality = capture_quality_summary(
        lab=lab,
        manifest=manifest,
        tapes=tapes,
        checked_at=generated_at,
    )
    capture_status = str(capture_quality.get("status") or "FAIL")
    fillability_quality = fillability_quality_summary(fillability_df)
    label_quality = label_quality_summary(outcome_df, tapes["anti_leakage_violations"])
    anti_leakage_quarantine_count = len(tapes["anti_leakage_violations"])
    scoring_issues: list[str] = []
    if anti_leakage_quarantine_count:
        scoring_issues.append("anti_leakage_labels_quarantined")
    if tape_integrity["status"] != "PASS":
        scoring_issues.append("tape_integrity_issues")
    freshness_hard_issues = {
        "candidate_decision_tape_missing",
        "candidate_decision_tape_lags_source",
        "fillability_snapshot_tape_missing",
        "fillability_snapshot_tape_lags_source",
    }
    if freshness_hard_issues.intersection(set(tape_freshness.get("issues") or [])):
        scoring_issues.append("tape_freshness_issues")
    candidate_scoring_status = (
        "MONITOR_" + "_and_".join(scoring_issues)
        if scores and scoring_issues
        else ("PASS" if scores else "FAIL")
    )
    any_promoted = any(score.get("promotion_status") == "PASS" for score in scores)
    summary = {
        "schema_version": "research-lab-gauntlet-summary-v1",
        "dataset_tag": args.dataset,
        "generated_at_utc": generated_at.isoformat(),
        "script_version": SCRIPT_VERSION,
        "tape_version": TAPE_VERSION,
        "spec_path": str(spec_path),
        "recorder_type": recorder_type,
        "latest_raw_event_ts": latest_raw_ts,
        "source_decision_event_count": tapes["source_decision_event_count"],
        "candidate_count": tapes["candidate_count"],
        "candidate_decision_rows": int(len(candidate_df)),
        "top_historical_candidate_ids": spec.get("top_historical_candidate_ids") or [],
        "fillability_snapshot_rows": int(len(fillability_df)),
        "outcome_label_rows": int(len(outcome_df)),
        "unlabeled_outcome_count": int(outcome_df["market_result"].isna().sum()) if not outcome_df.empty else 0,
        "tape_integrity_status": tape_integrity["status"],
        "tape_integrity_violation_count": tape_integrity["violation_count"],
        "tape_integrity": tape_integrity,
        "tape_freshness_status": tape_freshness["status"],
        "tape_freshness": tape_freshness,
        "expected_candidate_decision_rows": tape_integrity["expected_candidate_decision_rows"],
        "anti_leakage_status": "WARN_labels_quarantined" if anti_leakage_quarantine_count else "PASS",
        "anti_leakage_violation_count": anti_leakage_quarantine_count,
        "anti_leakage_violations": tapes["anti_leakage_violations"][:25],
        "capture_quality": capture_quality,
        "fillability_quality": fillability_quality,
        "label_quality": label_quality,
        "research_lab_improvement_status": "PASS_capture_freshness_and_provenance_quality_summary_added",
        "gauntlet_improvement_status": "PASS_fillability_and_label_quality_summaries_added",
        "capture_status": capture_status,
        "candidate_scoring_status": candidate_scoring_status,
        "new_edge_status": "MONITOR_no_candidate_promoted" if not any_promoted else "PASS_candidate_passed_gates_needs_human_review",
        "scores": scores,
    }
    artifacts = {
        "spec": spec_path,
        "summary_json": summary_path,
        "report": report_path,
        "scores_csv": scores_csv,
        "candidate_decisions": dataset_root / "candidate_decisions",
        "fillability_snapshots": dataset_root / "fillability_snapshots",
        "outcome_labels": dataset_root / "outcome_labels",
    }
    write_json(summary_path, summary)
    report_path.write_text(render_report(summary, scores, artifacts), encoding="utf-8")
    shutil.copyfile(summary_path, EDGE_DIR / f"codex_research_lab_gauntlet_{args.dataset}_latest.json")
    shutil.copyfile(report_path, EDGE_DIR / f"codex_research_lab_gauntlet_{args.dataset}_latest.md")
    shutil.copyfile(scores_csv, EDGE_DIR / f"codex_research_lab_gauntlet_scores_{args.dataset}_latest.csv")
    append_ledger(summary, artifacts)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
