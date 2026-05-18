from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from truffle_regime_lease import (
    ALLOW_90_78_NEXT_MARKET,
    BLOCK_NEXT_MARKET,
    DEFAULT_TRUFFLE_LEASE_PROMPT,
    DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT,
    MarketOutcomeRecord,
    build_last_market_sequence,
    build_recent_market_summary,
    compact_reasoning_payload,
    infer_session_label,
    issue_stub_lease,
    issue_truffle_http_lease,
    load_prompt_text,
    maybe_build_deterministic_lease_decision,
    parse_iso,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_historical_replay_latest.json"


@dataclass
class LeaseCase:
    case_id: str
    source: str
    scenario: str
    expected_decision: str
    expected_reason: str
    next_market_ticker: str
    next_market_session: str
    next_market_close_time: str
    payload: dict[str, Any]
    actual_next_outcome_type: str = ""
    actual_next_pnl_dollars: float | None = None
    recent4_trade_count: int = 0
    recent4_win_count: int = 0
    recent4_exit_count: int = 0
    recent4_net_pnl_dollars: float = 0.0
    recent4_positive_trade_fraction: float = 0.0
    recent4_exit_loss_dollars: float = 0.0
    recent4_stale_book_deferral_count: int = 0
    recent4_ioc_zero_fill_count: int = 0
    recent4_submit_latency_p95_ms: float = 0.0


def coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_path_from_env(value: str, *, default: Path) -> Path:
    text = str(value or "").strip()
    if not text:
        return default
    path = Path(text)
    if not path.is_absolute():
        path = ROOT / path
    return path


def load_market_results(dataset_tag: str) -> list[dict[str, str]]:
    path = ROOT / "stats" / dataset_tag / "market_results.csv"
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    clean_rows: list[dict[str, str]] = []
    for row in rows:
        market = str(row.get("market") or "").strip()
        if not market or market == "None":
            continue
        clean_rows.append(row)
    return clean_rows


def load_trades(dataset_tag: str) -> list[dict[str, str]]:
    path = ROOT / "stats" / dataset_tag / "trades.csv"
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_ordered_market_records(dataset_tag: str) -> list[MarketOutcomeRecord]:
    market_rows = load_market_results(dataset_tag)
    trade_rows = load_trades(dataset_tag)
    execution_events_path = ROOT / "logs" / dataset_tag / "execution_events.ndjson"

    records: dict[str, MarketOutcomeRecord] = {}
    ordered_markets: list[str] = []

    for row in market_rows:
        market = str(row.get("market") or "").strip()
        close_time = str(row.get("close_time") or "").strip()
        close_dt = parse_iso(close_time) if close_time else None
        local_close_dt = close_dt.astimezone() if close_dt is not None else None
        record = MarketOutcomeRecord(
            market=market,
            session=infer_session_label(local_close_dt),
            watched_at=str(row.get("first_seen_ts") or "").strip(),
            market_close_time=close_time,
            resolved_at=str(row.get("settlement_ts") or "").strip(),
        )
        records[market] = record
        ordered_markets.append(market)

    if execution_events_path.exists():
        with execution_events_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                market = str(event.get("market") or "").strip()
                record = records.get(market)
                if record is None:
                    continue
                event_type = str(event.get("event_type") or "").strip()
                result = str(event.get("result") or "").strip()
                if event_type == "signal_seen":
                    record.signal_count += 1
                if event_type == "execution_deferred" and result == "stale_book":
                    record.stale_book_deferral_count += 1
                if result == "ioc_zero_fill":
                    record.ioc_zero_fill_count += 1
                submit_latency_ms = event.get("submit_latency_ms")
                if submit_latency_ms is not None:
                    try:
                        record.add_submit_latency(float(submit_latency_ms))
                    except Exception:
                        pass

    for row in trade_rows:
        market = str(row.get("market") or "").strip()
        record = records.get(market)
        if record is None:
            continue
        qty = coerce_int(row.get("qty"), 0)
        entry_fill_cents = coerce_int(row.get("entry_fill_cents_used"), 0)
        entry_trigger_cents = None
        if str(row.get("entry_trigger_cents") or "").strip():
            entry_trigger_cents = coerce_int(row.get("entry_trigger_cents"), 0)
        side = str(row.get("side") or "").strip().lower()
        if qty > 0 and entry_fill_cents > 0 and side:
            record.record_entry(
                side=side,
                qty=qty,
                fill_price_cents=entry_fill_cents,
                fee_cents=0,
                trigger_price_cents=entry_trigger_cents,
            )
        exit_ts = str(row.get("exit_ts") or "").strip()
        if exit_ts:
            exit_fill_cents = coerce_int(row.get("exit_fill_cents_used"), 0)
            if qty > 0 and exit_fill_cents > 0:
                record.record_exit_fill(
                    qty=qty,
                    fill_price_cents=exit_fill_cents,
                    fee_cents=0,
                    remaining_position=0,
                    resolved_at=exit_ts,
                )
            continue
        market_result = str(row.get("market_result") or "").strip().lower()
        resolved_at = str(row.get("settlement_ts") or row.get("entry_ts") or "").strip()
        if market_result in {"yes", "no", "void"}:
            record.finalize_settlement(result=market_result, resolved_at=resolved_at)

    ordered_records = [records[market] for market in ordered_markets if market in records]
    for record in ordered_records:
        if not record.traded and record.outcome_type == "open_or_unresolved":
            record.finalize_no_trade(
                resolved_at=str(record.resolved_at or record.market_close_time or record.watched_at)
            )
    return ordered_records


def augment_window_summary(summary: dict[str, Any], window_records: list[MarketOutcomeRecord]) -> dict[str, Any]:
    augmented = dict(summary)
    traded_records = [record for record in window_records if record.traded]
    total_signal_count = sum(int(record.signal_count or 0) for record in window_records)
    traded_win_count = sum(1 for record in traded_records if float(record.pnl_dollars or 0.0) > 0)
    traded_exit_count = sum(1 for record in traded_records if record.outcome_type == "exit")
    traded_loss_count = sum(1 for record in traded_records if float(record.pnl_dollars or 0.0) < 0)
    stale_count = coerce_int(summary.get("stale_book_deferral_count"), 0)
    ioc_count = coerce_int(summary.get("ioc_zero_fill_count"), 0)
    traded_markets = max(1, coerce_int(summary.get("traded_markets"), 0))
    augmented["signal_count_total"] = int(total_signal_count)
    augmented["traded_win_count"] = int(traded_win_count)
    augmented["traded_exit_count"] = int(traded_exit_count)
    augmented["traded_loss_count"] = int(traded_loss_count)
    augmented["stale_deferrals_per_signal"] = round(stale_count / max(1, total_signal_count), 4)
    augmented["ioc_zero_fills_per_trade"] = round(ioc_count / traded_markets, 4)
    return augmented


def build_historical_cases(
    ordered_records: list[MarketOutcomeRecord],
    *,
    per_scenario: int,
) -> list[LeaseCase]:
    candidates: list[dict[str, Any]] = []
    for idx, record in enumerate(ordered_records):
        if idx < 4 or not record.traded or record.outcome_type == "open_or_unresolved":
            continue
        recent4 = ordered_records[max(0, idx - 4) : idx]
        recent8 = ordered_records[max(0, idx - 8) : idx]
        trade_recent4 = [row for row in recent4 if row.traded]
        close_dt = parse_iso(record.market_close_time) if record.market_close_time else None
        local_close_dt = close_dt.astimezone() if close_dt is not None else None
        payload = {
            "schema_version": "lease_input_v1",
            "strategy_family": "btc15m_supervisor",
            "candidate_profile_if_allowed": "90_78",
            "configured_profile": "90_78",
            "lease_scope": "next_market_only",
            "next_market_ticker": record.market,
            "next_market_session": infer_session_label(local_close_dt),
            "deterministic_precheck": "PASS",
            "generated_at": record.market_close_time or record.resolved_at or "",
            "recent_4_markets": augment_window_summary(build_recent_market_summary(recent4), recent4),
            "recent_8_markets": augment_window_summary(build_recent_market_summary(recent8), recent8),
            "last_4_market_sequence": build_last_market_sequence(recent4),
        }
        summary4 = payload["recent_4_markets"]
        candidates.append(
            {
                "record": record,
                "payload": payload,
                "recent4_trade_count": len(trade_recent4),
                "recent4_win_count": sum(1 for row in trade_recent4 if row.pnl_dollars > 0),
                "recent4_exit_count": sum(1 for row in trade_recent4 if row.outcome_type == "exit"),
                "recent4_net_pnl_dollars": coerce_float(summary4.get("net_pnl_dollars")),
                "recent4_positive_trade_fraction": coerce_float(summary4.get("positive_trade_fraction")),
                "recent4_exit_loss_dollars": coerce_float(summary4.get("exit_loss_dollars")),
                "recent4_stale_book_deferral_count": coerce_int(summary4.get("stale_book_deferral_count")),
                "recent4_ioc_zero_fill_count": coerce_int(summary4.get("ioc_zero_fill_count")),
                "recent4_submit_latency_p95_ms": coerce_float(summary4.get("submit_latency_p95_ms")),
            }
        )

    def material_allow(candidate: dict[str, Any]) -> bool:
        return candidate["record"].pnl_dollars >= 0.5

    def material_block(candidate: dict[str, Any]) -> bool:
        return candidate["record"].pnl_dollars <= -0.7

    used_markets: set[str] = set()
    selected: list[tuple[str, str, str, dict[str, Any]]] = []

    def pick(
        *,
        scenario: str,
        expected_decision: str,
        explanation: str,
        predicate: Any,
        sort_key: Any,
    ) -> None:
        ordered = sorted((candidate for candidate in candidates if predicate(candidate)), key=sort_key)
        count = 0
        for candidate in ordered:
            market = candidate["record"].market
            if market in used_markets:
                continue
            selected.append((scenario, expected_decision, explanation, candidate))
            used_markets.add(market)
            count += 1
            if count >= per_scenario:
                break

    pick(
        scenario="historical_win_continuation",
        expected_decision=ALLOW_90_78_NEXT_MARKET,
        explanation="Recent markets were mostly wins and the next historical trade was also a material win.",
        predicate=lambda candidate: candidate["recent4_win_count"] >= 3 and material_allow(candidate),
        sort_key=lambda candidate: (
            -candidate["record"].pnl_dollars,
            -candidate["recent4_net_pnl_dollars"],
            candidate["recent4_ioc_zero_fill_count"],
            candidate["record"].market,
        ),
    )
    pick(
        scenario="historical_win_streak_trap",
        expected_decision=BLOCK_NEXT_MARKET,
        explanation="Recent markets looked strong, but the next historical trade was a material loss.",
        predicate=lambda candidate: candidate["recent4_win_count"] >= 3 and material_block(candidate),
        sort_key=lambda candidate: (
            candidate["record"].pnl_dollars,
            -candidate["recent4_net_pnl_dollars"],
            candidate["recent4_ioc_zero_fill_count"],
            candidate["record"].market,
        ),
    )
    pick(
        scenario="historical_loss_cluster_rebound",
        expected_decision=ALLOW_90_78_NEXT_MARKET,
        explanation="Recent markets had multiple exit losses, but the next historical trade rebounded into a material win.",
        predicate=lambda candidate: candidate["recent4_exit_count"] >= 2 and material_allow(candidate),
        sort_key=lambda candidate: (
            -candidate["record"].pnl_dollars,
            candidate["recent4_net_pnl_dollars"],
            -candidate["recent4_exit_count"],
            candidate["record"].market,
        ),
    )
    pick(
        scenario="historical_loss_continuation",
        expected_decision=BLOCK_NEXT_MARKET,
        explanation="Recent markets had multiple exit losses and the next historical trade was also a material loss.",
        predicate=lambda candidate: candidate["recent4_exit_count"] >= 2 and material_block(candidate),
        sort_key=lambda candidate: (
            candidate["record"].pnl_dollars,
            candidate["recent4_net_pnl_dollars"],
            -candidate["recent4_exit_count"],
            candidate["record"].market,
        ),
    )

    cases: list[LeaseCase] = []
    for scenario, expected_decision, explanation, candidate in selected:
        record = candidate["record"]
        payload = candidate["payload"]
        cases.append(
            LeaseCase(
                case_id=f"historical::{scenario}::{record.market}",
                source="historical",
                scenario=scenario,
                expected_decision=expected_decision,
                expected_reason=explanation,
                next_market_ticker=record.market,
                next_market_session=str(payload.get("next_market_session") or "unknown"),
                next_market_close_time=record.market_close_time,
                payload=payload,
                actual_next_outcome_type=record.outcome_type,
                actual_next_pnl_dollars=round(float(record.pnl_dollars), 4),
                recent4_trade_count=int(candidate["recent4_trade_count"]),
                recent4_win_count=int(candidate["recent4_win_count"]),
                recent4_exit_count=int(candidate["recent4_exit_count"]),
                recent4_net_pnl_dollars=round(float(candidate["recent4_net_pnl_dollars"]), 4),
                recent4_positive_trade_fraction=round(float(candidate["recent4_positive_trade_fraction"]), 4),
                recent4_exit_loss_dollars=round(float(candidate["recent4_exit_loss_dollars"]), 4),
                recent4_stale_book_deferral_count=int(candidate["recent4_stale_book_deferral_count"]),
                recent4_ioc_zero_fill_count=int(candidate["recent4_ioc_zero_fill_count"]),
                recent4_submit_latency_p95_ms=round(float(candidate["recent4_submit_latency_p95_ms"]), 4),
            )
        )
    return cases


def build_synthetic_cases() -> list[LeaseCase]:
    return [
        LeaseCase(
            case_id="synthetic::obvious_allow",
            source="synthetic",
            scenario="synthetic_obvious_allow",
            expected_decision=ALLOW_90_78_NEXT_MARKET,
            expected_reason="Everything is clean, recent realized edge is strong, and there is no obvious friction.",
            next_market_ticker="KXBTC15M-SYNTH-ALLOW",
            next_market_session="afternoon",
            next_market_close_time="2026-04-20T16:15:00Z",
            payload={
                "schema_version": "lease_input_v1",
                "strategy_family": "btc15m_supervisor",
                "candidate_profile_if_allowed": "90_78",
                "configured_profile": "90_78",
                "lease_scope": "next_market_only",
                "next_market_ticker": "KXBTC15M-SYNTH-ALLOW",
                "next_market_session": "afternoon",
                "deterministic_precheck": "PASS",
                "generated_at": "2026-04-20T16:00:00Z",
                "recent_4_markets": {
                    "traded_markets": 4,
                    "signal_markets": 4,
                    "net_pnl_dollars": 6.4,
                    "exit_count": 0,
                    "exit_loss_dollars": 0.0,
                    "settlement_loss_count": 0,
                    "avg_entry_trigger_cents": 90.0,
                    "stale_book_deferral_count": 0,
                    "ioc_zero_fill_count": 0,
                    "submit_latency_p95_ms": 62.0,
                    "positive_trade_fraction": 1.0,
                },
                "recent_8_markets": {
                    "traded_markets": 8,
                    "signal_markets": 8,
                    "net_pnl_dollars": 10.8,
                    "exit_count": 1,
                    "exit_loss_dollars": 0.6,
                    "settlement_loss_count": 0,
                    "avg_entry_trigger_cents": 90.25,
                    "stale_book_deferral_count": 2,
                    "ioc_zero_fill_count": 0,
                    "submit_latency_p95_ms": 70.0,
                    "positive_trade_fraction": 0.875,
                },
                "last_4_market_sequence": [
                    {"market": "m1", "session": "afternoon", "traded": True, "signal_count": 1, "outcome_type": "win", "pnl_dollars": 2.0, "entry_trigger_cents": 90, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
                    {"market": "m2", "session": "afternoon", "traded": True, "signal_count": 1, "outcome_type": "win", "pnl_dollars": 1.8, "entry_trigger_cents": 90, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
                    {"market": "m3", "session": "afternoon", "traded": True, "signal_count": 1, "outcome_type": "win", "pnl_dollars": 1.4, "entry_trigger_cents": 90, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
                    {"market": "m4", "session": "afternoon", "traded": True, "signal_count": 1, "outcome_type": "win", "pnl_dollars": 1.2, "entry_trigger_cents": 90, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
                ],
            },
            recent4_trade_count=4,
            recent4_win_count=4,
            recent4_exit_count=0,
            recent4_net_pnl_dollars=6.4,
            recent4_positive_trade_fraction=1.0,
            recent4_exit_loss_dollars=0.0,
            recent4_stale_book_deferral_count=0,
            recent4_ioc_zero_fill_count=0,
            recent4_submit_latency_p95_ms=62.0,
        ),
        LeaseCase(
            case_id="synthetic::obvious_block",
            source="synthetic",
            scenario="synthetic_obvious_block",
            expected_decision=BLOCK_NEXT_MARKET,
            expected_reason="Recent realized edge is sharply negative and friction is elevated.",
            next_market_ticker="KXBTC15M-SYNTH-BLOCK",
            next_market_session="evening",
            next_market_close_time="2026-04-20T21:15:00Z",
            payload={
                "schema_version": "lease_input_v1",
                "strategy_family": "btc15m_supervisor",
                "candidate_profile_if_allowed": "90_78",
                "configured_profile": "90_78",
                "lease_scope": "next_market_only",
                "next_market_ticker": "KXBTC15M-SYNTH-BLOCK",
                "next_market_session": "evening",
                "deterministic_precheck": "PASS",
                "generated_at": "2026-04-20T21:00:00Z",
                "recent_4_markets": {
                    "traded_markets": 4,
                    "signal_markets": 4,
                    "net_pnl_dollars": -5.2,
                    "exit_count": 3,
                    "exit_loss_dollars": 6.4,
                    "settlement_loss_count": 1,
                    "avg_entry_trigger_cents": 90.0,
                    "stale_book_deferral_count": 180,
                    "ioc_zero_fill_count": 2,
                    "submit_latency_p95_ms": 146.0,
                    "positive_trade_fraction": 0.0,
                },
                "recent_8_markets": {
                    "traded_markets": 8,
                    "signal_markets": 8,
                    "net_pnl_dollars": -7.6,
                    "exit_count": 5,
                    "exit_loss_dollars": 8.2,
                    "settlement_loss_count": 1,
                    "avg_entry_trigger_cents": 90.25,
                    "stale_book_deferral_count": 260,
                    "ioc_zero_fill_count": 4,
                    "submit_latency_p95_ms": 152.0,
                    "positive_trade_fraction": 0.125,
                },
                "last_4_market_sequence": [
                    {"market": "m1", "session": "evening", "traded": True, "signal_count": 1, "outcome_type": "exit", "pnl_dollars": -2.0, "entry_trigger_cents": 90, "stale_book_deferral_count": 50, "ioc_zero_fill_count": 1},
                    {"market": "m2", "session": "evening", "traded": True, "signal_count": 1, "outcome_type": "exit", "pnl_dollars": -1.8, "entry_trigger_cents": 90, "stale_book_deferral_count": 60, "ioc_zero_fill_count": 1},
                    {"market": "m3", "session": "evening", "traded": True, "signal_count": 1, "outcome_type": "settlement_loss", "pnl_dollars": -0.9, "entry_trigger_cents": 90, "stale_book_deferral_count": 40, "ioc_zero_fill_count": 0},
                    {"market": "m4", "session": "evening", "traded": True, "signal_count": 1, "outcome_type": "exit", "pnl_dollars": -0.5, "entry_trigger_cents": 90, "stale_book_deferral_count": 30, "ioc_zero_fill_count": 0},
                ],
            },
            recent4_trade_count=4,
            recent4_win_count=0,
            recent4_exit_count=3,
            recent4_net_pnl_dollars=-5.2,
            recent4_positive_trade_fraction=0.0,
            recent4_exit_loss_dollars=6.4,
            recent4_stale_book_deferral_count=180,
            recent4_ioc_zero_fill_count=2,
            recent4_submit_latency_p95_ms=146.0,
        ),
        LeaseCase(
            case_id="synthetic::no_recent_data",
            source="synthetic",
            scenario="synthetic_no_recent_data",
            expected_decision=BLOCK_NEXT_MARKET,
            expected_reason="No recent regime evidence should fail closed and block the next market.",
            next_market_ticker="KXBTC15M-SYNTH-NODATA",
            next_market_session="morning",
            next_market_close_time="2026-04-20T14:15:00Z",
            payload={
                "schema_version": "lease_input_v1",
                "strategy_family": "btc15m_supervisor",
                "candidate_profile_if_allowed": "90_78",
                "configured_profile": "90_78",
                "lease_scope": "next_market_only",
                "next_market_ticker": "KXBTC15M-SYNTH-NODATA",
                "next_market_session": "morning",
                "deterministic_precheck": "PASS",
                "generated_at": "2026-04-20T14:00:00Z",
                "recent_4_markets": {"traded_markets": 0, "signal_markets": 0, "net_pnl_dollars": 0.0, "exit_count": 0, "exit_loss_dollars": 0.0, "settlement_loss_count": 0, "avg_entry_trigger_cents": 0.0, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0, "submit_latency_p95_ms": 0.0, "positive_trade_fraction": 0.0},
                "recent_8_markets": {"traded_markets": 0, "signal_markets": 0, "net_pnl_dollars": 0.0, "exit_count": 0, "exit_loss_dollars": 0.0, "settlement_loss_count": 0, "avg_entry_trigger_cents": 0.0, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0, "submit_latency_p95_ms": 0.0, "positive_trade_fraction": 0.0},
                "last_4_market_sequence": [],
            },
        ),
    ]


def evaluate_cases(
    cases: list[LeaseCase],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    tool_prompt_text: str,
    api_key: str,
    max_tokens: int,
    reasoning_enabled: str | bool,
    repeats: int,
) -> dict[str, Any]:
    case_outputs: list[dict[str, Any]] = []
    parse_errors = Counter()
    total_attempts = 0
    total_valid_attempts = 0
    total_expected_match_attempts = 0
    case_majority_matches = 0
    case_full_consistency = 0
    stub_matches = 0
    deterministic_matches = 0

    for case in cases:
        attempts: list[dict[str, Any]] = []
        deterministic_floor = maybe_build_deterministic_lease_decision(case.payload, issuer="deterministic_floor")
        deterministic_dict = deterministic_floor.to_dict() if deterministic_floor is not None else None
        if deterministic_floor is not None and deterministic_floor.decision == case.expected_decision:
            deterministic_matches += 1
        stub_decision = issue_stub_lease(case.payload)
        stub_dict = stub_decision.to_dict()
        if stub_decision.is_valid and stub_decision.decision == case.expected_decision:
            stub_matches += 1

        for repeat_index in range(repeats):
            started = time.perf_counter()
            decision = issue_truffle_http_lease(
                case.payload,
                endpoint=endpoint,
                model=model,
                timeout_ms=timeout_ms,
                prompt_text=prompt_text,
                tool_prompt_text=tool_prompt_text,
                api_key=api_key,
                max_tokens=max_tokens,
                reasoning_enabled=reasoning_enabled,
            )
            latency_ms = round((time.perf_counter() - started) * 1000.0, 1)
            decision_dict = decision.to_dict()
            decision_dict["attempt_latency_ms"] = latency_ms
            decision_dict["repeat_index"] = repeat_index + 1
            attempts.append(decision_dict)
            total_attempts += 1
            if decision.is_valid:
                total_valid_attempts += 1
                if decision.decision == case.expected_decision:
                    total_expected_match_attempts += 1
            else:
                parse_errors[decision.parse_error or "unknown"] += 1

        valid_attempts = [attempt for attempt in attempts if not attempt.get("parse_error")]
        valid_decisions = [attempt.get("decision") for attempt in valid_attempts if attempt.get("decision")]
        decision_counts = Counter(valid_decisions)
        majority_decision = decision_counts.most_common(1)[0][0] if decision_counts else ""
        full_consistency = len(valid_attempts) == repeats and len(decision_counts) == 1
        majority_matches = bool(majority_decision and majority_decision == case.expected_decision)
        if majority_matches:
            case_majority_matches += 1
        if full_consistency:
            case_full_consistency += 1

        case_outputs.append(
            {
                **asdict(case),
                "payload_compact": compact_reasoning_payload(case.payload),
                "deterministic_floor_decision": deterministic_dict,
                "stub_decision": stub_dict,
                "stub_matches_expected": bool(stub_decision.is_valid and stub_decision.decision == case.expected_decision),
                "deterministic_floor_matches_expected": bool(
                    deterministic_floor is not None and deterministic_floor.decision == case.expected_decision
                ),
                "attempts": attempts,
                "valid_attempt_count": len(valid_attempts),
                "valid_rate": round(len(valid_attempts) / max(1, repeats), 4),
                "expected_match_count": sum(
                    1 for attempt in valid_attempts if attempt.get("decision") == case.expected_decision
                ),
                "expected_match_rate_over_all_attempts": round(
                    sum(1 for attempt in valid_attempts if attempt.get("decision") == case.expected_decision)
                    / max(1, repeats),
                    4,
                ),
                "expected_match_rate_over_valid_attempts": round(
                    (
                        sum(1 for attempt in valid_attempts if attempt.get("decision") == case.expected_decision)
                        / len(valid_attempts)
                    ),
                    4,
                )
                if valid_attempts
                else 0.0,
                "majority_decision": majority_decision,
                "majority_matches_expected": majority_matches,
                "full_consistency": full_consistency,
                "decision_counts": dict(decision_counts),
            }
        )

    scenario_summary: dict[str, dict[str, Any]] = {}
    for result in case_outputs:
        scenario = str(result.get("scenario") or "unknown")
        bucket = scenario_summary.setdefault(
            scenario,
            {
                "case_count": 0,
                "attempt_count": 0,
                "valid_attempt_count": 0,
                "expected_match_attempt_count": 0,
                "majority_match_case_count": 0,
                "full_consistency_case_count": 0,
                "stub_match_case_count": 0,
                "deterministic_match_case_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["attempt_count"] += len(result.get("attempts", []))
        bucket["valid_attempt_count"] += int(result.get("valid_attempt_count", 0))
        bucket["expected_match_attempt_count"] += int(
            sum(
                1
                for attempt in result.get("attempts", [])
                if not attempt.get("parse_error") and attempt.get("decision") == result.get("expected_decision")
            )
        )
        bucket["majority_match_case_count"] += int(bool(result.get("majority_matches_expected")))
        bucket["full_consistency_case_count"] += int(bool(result.get("full_consistency")))
        bucket["stub_match_case_count"] += int(bool(result.get("stub_matches_expected")))
        bucket["deterministic_match_case_count"] += int(bool(result.get("deterministic_floor_matches_expected")))

    for bucket in scenario_summary.values():
        bucket["valid_attempt_rate"] = round(bucket["valid_attempt_count"] / max(1, bucket["attempt_count"]), 4)
        bucket["expected_match_attempt_rate"] = round(
            bucket["expected_match_attempt_count"] / max(1, bucket["attempt_count"]),
            4,
        )
        bucket["majority_match_case_rate"] = round(bucket["majority_match_case_count"] / max(1, bucket["case_count"]), 4)
        bucket["full_consistency_case_rate"] = round(
            bucket["full_consistency_case_count"] / max(1, bucket["case_count"]),
            4,
        )
        bucket["stub_match_case_rate"] = round(bucket["stub_match_case_count"] / max(1, bucket["case_count"]), 4)
        bucket["deterministic_match_case_rate"] = round(
            bucket["deterministic_match_case_count"] / max(1, bucket["case_count"]),
            4,
        )

    return {
        "aggregate": {
            "case_count": len(case_outputs),
            "repeat_count": repeats,
            "attempt_count": total_attempts,
            "valid_attempt_count": total_valid_attempts,
            "valid_attempt_rate": round(total_valid_attempts / max(1, total_attempts), 4),
            "expected_match_attempt_count": total_expected_match_attempts,
            "expected_match_attempt_rate": round(total_expected_match_attempts / max(1, total_attempts), 4),
            "majority_match_case_count": case_majority_matches,
            "majority_match_case_rate": round(case_majority_matches / max(1, len(case_outputs)), 4),
            "full_consistency_case_count": case_full_consistency,
            "full_consistency_case_rate": round(case_full_consistency / max(1, len(case_outputs)), 4),
            "stub_match_case_count": stub_matches,
            "stub_match_case_rate": round(stub_matches / max(1, len(case_outputs)), 4),
            "deterministic_match_case_count": deterministic_matches,
            "deterministic_match_case_rate": round(deterministic_matches / max(1, len(case_outputs)), 4),
            "parse_error_histogram": dict(parse_errors),
        },
        "scenario_summary": scenario_summary,
        "cases": case_outputs,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay historical and synthetic regime lease cases through Truffle.")
    parser.add_argument("--dataset-tag", default="live_90_78")
    parser.add_argument("--historical-per-scenario", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-ms", type=int, default=0)
    parser.add_argument("--max-tokens", type=int, default=0)
    parser.add_argument("--reasoning-enabled", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--synthetic-only", action="store_true")
    parser.add_argument("--historical-only", action="store_true")
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    load_env_file(ROOT / ".env")

    prompt_path = resolve_path_from_env(
        os.environ.get("TRUFFLE_REGIME_LEASE_PROMPT_PATH", ""),
        default=ROOT / "truffle_regime_lease_prompt.txt",
    )
    tool_prompt_path = resolve_path_from_env(
        os.environ.get("TRUFFLE_REGIME_LEASE_TOOL_PROMPT_PATH", ""),
        default=ROOT / "truffle_regime_lease_tool_prompt.txt",
    )
    prompt_text = load_prompt_text(prompt_path if prompt_path.exists() else None, default_text=DEFAULT_TRUFFLE_LEASE_PROMPT)
    tool_prompt_text = load_prompt_text(
        tool_prompt_path if tool_prompt_path.exists() else None,
        default_text=DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT,
    )

    configured_timeout_ms = coerce_int(os.environ.get("TRUFFLE_REGIME_LEASE_TIMEOUT_MS"), 90000)
    timeout_ms = int(args.timeout_ms or configured_timeout_ms or 90000)
    configured_max_tokens = coerce_int(os.environ.get("TRUFFLE_REGIME_LEASE_MAX_TOKENS"), 0)
    max_tokens = int(args.max_tokens or configured_max_tokens or 0)
    reasoning_enabled = (
        args.reasoning_enabled.strip()
        if str(args.reasoning_enabled or "").strip()
        else os.environ.get("TRUFFLE_REGIME_LEASE_REASONING_ENABLED", "auto")
    )
    endpoint = str(args.endpoint or os.environ.get("TRUFFLE_REGIME_LEASE_ENDPOINT") or "").strip()
    api_key = str(args.api_key or os.environ.get("TRUFFLE_REGIME_LEASE_API_KEY") or "").strip()
    model = str(args.model or os.environ.get("TRUFFLE_REGIME_LEASE_MODEL") or "").strip()

    cases: list[LeaseCase] = []
    if not args.historical_only:
        cases.extend(build_synthetic_cases())
    if not args.synthetic_only:
        ordered_records = build_ordered_market_records(args.dataset_tag)
        cases.extend(build_historical_cases(ordered_records, per_scenario=max(1, args.historical_per_scenario)))

    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) if resolved_endpoint else ""

    evaluation = evaluate_cases(
        cases,
        endpoint=endpoint,
        model=model,
        timeout_ms=timeout_ms,
        prompt_text=prompt_text,
        tool_prompt_text=tool_prompt_text,
        api_key=api_key,
        max_tokens=max_tokens,
        reasoning_enabled=reasoning_enabled,
        repeats=max(1, args.repeats),
    )

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset_tag": args.dataset_tag,
        "resolved_endpoint": resolved_endpoint,
        "resolved_model": resolved_model or model,
        "timeout_ms": timeout_ms,
        "max_tokens": max_tokens,
        "reasoning_enabled": reasoning_enabled,
        "prompt_path": str(prompt_path),
        "tool_prompt_path": str(tool_prompt_path),
        "prompt_chars": len(prompt_text),
        "tool_prompt_chars": len(tool_prompt_text),
        **evaluation,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    aggregate = payload["aggregate"]
    print(f"Saved replay results to {output_path}")
    print(
        "Cases={case_count} Attempts={attempt_count} ValidRate={valid_attempt_rate:.2%} "
        "ExpectedMatchRate={expected_match_attempt_rate:.2%} MajorityCaseRate={majority_match_case_rate:.2%} "
        "ConsistencyCaseRate={full_consistency_case_rate:.2%}".format(**aggregate)
    )
    print(
        "StubCaseRate={stub_match_case_rate:.2%} DeterministicCaseRate={deterministic_match_case_rate:.2%}".format(
            **aggregate
        )
    )
    if aggregate["parse_error_histogram"]:
        print("ParseErrors:", json.dumps(aggregate["parse_error_histogram"], sort_keys=True))
    for scenario, summary in payload["scenario_summary"].items():
        print(
            f"{scenario}: cases={summary['case_count']} valid={summary['valid_attempt_rate']:.2%} "
            f"expected={summary['expected_match_attempt_rate']:.2%} "
            f"majority={summary['majority_match_case_rate']:.2%} consistency={summary['full_consistency_case_rate']:.2%}"
        )


if __name__ == "__main__":
    main()
