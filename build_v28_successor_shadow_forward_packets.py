"""Build v28 successor shadow-forward packet rows from paired passive runs.

Research-only. This bridges paired passive book/context captures and recorded
shadow candidate snapshots into the v28 successor packet contract. It does not
touch live bot state, orders, thresholds, secrets, or processes.

The output is intentionally strict: rows can be useful causal diagnostics, but
they are not promotable unless they were recorded before close, have complete
native v28 component fields, and come from a frozen successor candidate
manifest. Current paired shadow rows are expected to remain non-promotable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from validate_v28_successor_forward_packet import FIELD_GROUPS, row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"
SHADOW_ROOT = ROOT / "logs" / "particle_research" / "real_shadow"

PACKETS_CSV = OUT_DIR / "shadow_forward_packets_latest.csv"
PACKETS_JSON = OUT_DIR / "shadow_forward_packets_latest.json"
LABELED_CSV = OUT_DIR / "shadow_forward_labeled_rows_latest.csv"
LABELED_JSON = OUT_DIR / "shadow_forward_labeled_rows_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_shadow_forward_packets_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_shadow_forward_packets_latest.md"


EXTRA_PACKET_FIELDS = [
    "run_id",
    "candidate_snapshot_recorded_ts_utc",
    "candidate_snapshot_recorded_before_close",
    "v28_match_ts_utc",
    "v28_match_age_ms",
    "v28_match_source_file",
    "v28_match_source_line",
    "v28_component_capture_status",
    "candidate_manifest_forward_allowed",
    "candidate_record_type",
    "candidate_reason",
    "shadow_brownian_p_yes",
    "shadow_market_p_yes",
    "shadow_current_calibrated_p_yes",
    "shadow_particle_p_yes",
    "btc_return_source",
    "strike_distance_dollars",
    "strike_distance_dollars_abs",
    "abs_v28_d_sigma",
    "recross_hazard_score",
    "book_spot_disagreement_cents",
]

LABEL_FIELDS = [
    "y_yes_win",
    "binary_result",
    "label_available_ts_utc",
    "settlement_ts_utc",
    "settlement_price",
    "settlement_price_is_binary_proxy",
    "label_source",
]

PACKET_FIELDS = list(dict.fromkeys([field for fields in FIELD_GROUPS.values() for field in fields] + EXTRA_PACKET_FIELDS))
LABELED_FIELDS = PACKET_FIELDS + LABEL_FIELDS

V28_FIELDS = {
    "v28_p_yes": "mushroom_v28_p_yes",
    "v28_p_side": "mushroom_v28_p_side",
    "v28_best_side": "mushroom_v28_side",
    "v28_fair_yes_cents": "mushroom_v28_fair_yes_cents",
    "v28_fair_no_cents": "mushroom_v28_fair_no_cents",
    "v28_best_fair_cents": "mushroom_v28_fair_side_cents",
    "v28_best_edge_cents": "mushroom_v28_edge_cents",
    "v28_arrow": "mushroom_v28_arrow",
    "v28_volshock": "mushroom_v28_volshock",
    "v28_effective_horizon_minutes": "mushroom_v28_effective_horizon_minutes",
    "v28_sigma_t_dollars": "mushroom_v28_sigma_t_dollars",
    "v28_d_sigma": "mushroom_v28_d_sigma",
}


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]


def parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
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


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).replace(microsecond=value.microsecond).isoformat().replace("+00:00", "Z")


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.10g}"


def cents(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                yield line_number, payload


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def discover_latest_run_root() -> Path:
    roots = [
        path
        for path in SHADOW_ROOT.glob("particle_shadow_forward_*")
        if (path / "candidate_snapshots" / "candidate_snapshots.ndjson").exists()
    ]
    if not roots:
        raise FileNotFoundError(f"no paired shadow run roots under {rel_path(SHADOW_ROOT)}")
    return max(roots, key=lambda path: path.stat().st_mtime)


def load_contexts(path: Path) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    by_market: dict[str, list[dict[str, Any]]] = {}
    global_rows: list[dict[str, Any]] = []
    for _line, row in read_jsonl(path):
        market = str(row.get("market_ticker") or "")
        decision = parse_ts(row.get("decision_ts_utc"))
        if not market or decision is None:
            continue
        row = dict(row)
        row["_decision_dt"] = decision
        key = (market, decision.isoformat())
        by_key[key] = row
        by_market.setdefault(market, []).append(row)
        global_rows.append(row)
    for rows in by_market.values():
        rows.sort(key=lambda item: item["_decision_dt"])
    global_rows.sort(key=lambda item: item["_decision_dt"])
    return by_key, by_market, global_rows


def load_candidate_snapshots(path: Path, limit_snapshots: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, row in read_jsonl(path):
        snapshot = row.get("snapshot")
        if not isinstance(snapshot, dict):
            continue
        out = dict(row)
        out["_line_number"] = line_number
        rows.append(out)
        if limit_snapshots is not None and len(rows) >= limit_snapshots:
            break
    return rows


def load_labels(run_root: Path) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for candidate in (
        run_root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        run_root / "pipeline_work" / "label_contexts.ndjson",
    ):
        if not candidate.exists():
            continue
        for _line, row in read_jsonl(candidate):
            market = str(row.get("market_ticker") or "")
            if market:
                labels[market] = row
    results_path = run_root / "market_results_full_refresh.json"
    results = read_json(results_path)
    if isinstance(results, list):
        for row in results:
            if not isinstance(row, dict):
                continue
            market = str(row.get("market") or "")
            if not market:
                continue
            labels.setdefault(market, {})
            labels[market].update(
                {
                    "binary_result": row.get("result"),
                    "label_available_ts_utc": row.get("close_time"),
                    "settlement_ts_utc": row.get("close_time"),
                    "source": row.get("source"),
                }
            )
    return labels


def load_v28_events(path: Path) -> dict[tuple[str, str], list[dict[str, Any]]]:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if not path.exists():
        return by_key
    for line_number, row in read_jsonl(path):
        market = str(row.get("market") or row.get("market_ticker") or "")
        side = str(row.get("mushroom_v28_side") or row.get("side") or "").lower()
        ts = parse_ts(row.get("ts_wall"))
        if not market or side not in {"yes", "no"} or ts is None:
            continue
        if as_float(row.get("mushroom_v28_p_yes")) is None or as_float(row.get("mushroom_v28_strike")) is None:
            continue
        payload = dict(row)
        payload["_event_dt"] = ts
        payload["_event_line"] = line_number
        by_key.setdefault((market, side), []).append(payload)
    for rows in by_key.values():
        rows.sort(key=lambda item: item["_event_dt"])
    return by_key


def latest_v28_event(
    index: dict[tuple[str, str], list[dict[str, Any]]],
    market: str,
    side: str,
    decision_dt: datetime,
) -> dict[str, Any] | None:
    rows = index.get((market, side)) or index.get((market, "yes")) or index.get((market, "no")) or []
    if not rows:
        return None
    times = [row["_event_dt"] for row in rows]
    idx = bisect_right(times, decision_dt) - 1
    if idx < 0:
        return None
    return rows[idx]


def prior_spot(rows: list[dict[str, Any]], decision_dt: datetime, seconds: int) -> float | None:
    target = decision_dt - timedelta(seconds=seconds)
    selected: dict[str, Any] | None = None
    for row in rows:
        row_dt = row.get("_decision_dt")
        if row_dt is not None and row_dt <= target:
            selected = row
        elif row_dt is not None and row_dt > target:
            break
    return as_float(selected.get("spot")) if selected else None


def path_extreme(rows: list[dict[str, Any]], decision_dt: datetime, seconds: int, current_spot: float, side: str) -> float | None:
    start = decision_dt - timedelta(seconds=seconds)
    spots = [
        as_float(row.get("spot"))
        for row in rows
        if row.get("_decision_dt") is not None and start <= row["_decision_dt"] <= decision_dt
    ]
    spots = [spot for spot in spots if spot is not None]
    if not spots:
        return None
    if side == "yes":
        return max(0.0, current_spot - min(spots))
    return max(0.0, max(spots) - current_spot)


def window_has_history(rows: list[dict[str, Any]], decision_dt: datetime, seconds: int) -> bool:
    start = decision_dt - timedelta(seconds=seconds)
    return any(row.get("_decision_dt") is not None and row["_decision_dt"] <= start for row in rows)


def build_rows(
    run_root: Path | None = None,
    event_path: Path | None = None,
    limit_snapshots: int | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    run_root = run_root or discover_latest_run_root()
    manifest = read_json(run_root / "paired_passive_run_manifest.json") or {}
    pipeline_manifest = read_json(run_root / "pipeline_work" / "pipeline_manifest.json") or {}
    candidate_snapshot_path = run_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    candidate_context_path = run_root / "pipeline_work" / "candidate_contexts.ndjson"
    event_path = event_path or Path(str(manifest.get("v28_events_input") or ""))
    if not event_path.is_absolute():
        event_path = ROOT / event_path

    contexts_by_key, contexts_by_market, global_contexts = load_contexts(candidate_context_path)
    candidate_snapshots = load_candidate_snapshots(candidate_snapshot_path, limit_snapshots=limit_snapshots)
    labels_by_market = load_labels(run_root)
    v28_index = load_v28_events(event_path)
    model_payload = {
        "candidate_id": "shadow_particle_calibrated_v001",
        "model_type": "particle_shadow_diagnostic",
        "annualized_vol": 0.65,
        "sample_count": 2000,
        "seed": 1,
        "source_run": run_root.name,
    }
    model_hash = stable_hash(model_payload)
    feature_table_hash = sha256_file(candidate_context_path) or stable_hash(candidate_context_path.as_posix())
    run_id = str(manifest.get("run_id") or run_root.name.replace("particle_shadow_forward_", ""))

    packet_rows: list[dict[str, Any]] = []
    labeled_rows: list[dict[str, Any]] = []
    exclusion_counts: Counter[str] = Counter()
    missing_contexts = 0
    missing_v28_matches = 0
    registered_before_close = 0

    for snapshot_row in candidate_snapshots:
        snapshot = snapshot_row.get("snapshot") or {}
        extra = snapshot_row.get("extra") or {}
        market = str(snapshot.get("market_ticker") or "")
        decision_dt = parse_ts(snapshot.get("decision_ts_utc"))
        recorded_dt = parse_ts(snapshot_row.get("recorded_ts_utc"))
        if not market or decision_dt is None:
            continue
        context = contexts_by_key.get((market, decision_dt.isoformat()))
        if context is None:
            missing_contexts += 1
            context = {}
        close_dt = parse_ts(context.get("settlement_ts_utc")) or parse_ts(snapshot.get("settlement_ts_utc"))
        if close_dt is None:
            continue
        label = labels_by_market.get(market, {})
        market_contexts = contexts_by_market.get(market, [])
        spot = as_float(snapshot.get("spot")) or as_float(context.get("spot"))
        if spot is None:
            continue
        btc_age_ms = as_float(context.get("btc_age_ms"))
        btc_tick_dt = decision_dt - timedelta(milliseconds=btc_age_ms) if btc_age_ms is not None else None
        pre_resolution = decision_dt <= close_dt
        recorded_before_close = recorded_dt is not None and recorded_dt <= close_dt
        if recorded_before_close:
            registered_before_close += 1
        seconds_to_close = as_float(extra.get("seconds_to_close")) or as_float(context.get("seconds_to_close"))
        if seconds_to_close is None:
            seconds_to_close = max(0.0, (close_dt - decision_dt).total_seconds())

        for side in ("yes", "no"):
            v28 = latest_v28_event(v28_index, market, side, decision_dt)
            if v28 is None:
                missing_v28_matches += 1
                v28 = {}
            v28_dt = v28.get("_event_dt")
            v28_age_ms = 1000.0 * (decision_dt - v28_dt).total_seconds() if isinstance(v28_dt, datetime) else None
            yes_ask = as_float(snapshot.get("yes_ask_cents")) or as_float(context.get("yes_ask_cents"))
            no_ask = as_float(snapshot.get("no_ask_cents")) or as_float(context.get("no_ask_cents"))
            yes_bid = as_float(context.get("yes_bid_cents"))
            no_bid = as_float(context.get("no_bid_cents"))
            ask = yes_ask if side == "yes" else no_ask
            bid = yes_bid if side == "yes" else no_bid
            book_implied_yes = None
            if side == "yes" and yes_ask is not None:
                book_implied_yes = yes_ask / 100.0
            if side == "no" and no_ask is not None:
                book_implied_yes = 1.0 - no_ask / 100.0
            book_mid = None
            if yes_bid is not None and yes_ask is not None:
                book_mid = 0.5 * (yes_bid + yes_ask)
            book_width = yes_ask - yes_bid if yes_ask is not None and yes_bid is not None else None

            candidate_p_yes = as_float(extra.get("particle_calibrated_p_yes")) or as_float(extra.get("particle_p_yes"))
            candidate_fair_yes = 100.0 * candidate_p_yes if candidate_p_yes is not None else None
            candidate_fair_no = 100.0 - candidate_fair_yes if candidate_fair_yes is not None else None
            candidate_fair_side = candidate_fair_yes if side == "yes" else candidate_fair_no
            candidate_edge = None
            if candidate_fair_side is not None and ask is not None:
                candidate_edge = candidate_fair_side - ask

            v28_p_yes = as_float(v28.get("mushroom_v28_p_yes")) or as_float(context.get("current_calibrated_p_yes"))
            v28_fair_yes = as_float(v28.get("mushroom_v28_fair_yes_cents"))
            if v28_fair_yes is None and v28_p_yes is not None:
                v28_fair_yes = 100.0 * v28_p_yes
            v28_fair_no = as_float(v28.get("mushroom_v28_fair_no_cents"))
            if v28_fair_no is None and v28_fair_yes is not None:
                v28_fair_no = 100.0 - v28_fair_yes
            v28_yes_edge = v28_fair_yes - yes_ask if v28_fair_yes is not None and yes_ask is not None else None
            v28_no_edge = v28_fair_no - no_ask if v28_fair_no is not None and no_ask is not None else None
            v28_best_edge = max(
                [edge for edge in (v28_yes_edge, v28_no_edge) if edge is not None],
                default=as_float(v28.get("mushroom_v28_edge_cents")),
            )
            d_sigma = as_float(v28.get("mushroom_v28_d_sigma"))
            recross = as_float(v28.get("mushroom_v28_feature_gate_recross_hazard_score"))
            strike = as_float(snapshot.get("strike")) or as_float(context.get("strike")) or as_float(v28.get("mushroom_v28_strike"))
            strike_distance = spot - strike if strike is not None else None
            prior_15s = prior_spot(global_contexts, decision_dt, 15)
            prior_60s = prior_spot(global_contexts, decision_dt, 60)
            prior_180s = prior_spot(global_contexts, decision_dt, 180)
            prior_300s = prior_spot(global_contexts, decision_dt, 300)
            prior_900s = prior_spot(global_contexts, decision_dt, 900)
            exclusions = [
                "not_v28_successor_frozen_manifest",
                "native_v28_component_fields_incomplete",
                "shadow_sidecar_particle_candidate_not_promotable",
            ]
            if not recorded_before_close:
                exclusions.append("candidate_recorded_after_close")
            if v28 is None or not v28:
                exclusions.append("missing_logged_v28_match")
            for reason in exclusions:
                exclusion_counts[reason] += 1

            row = {
                "row_id": stable_hash([run_id, market, decision_dt.isoformat(), side, snapshot_row.get("_line_number")]),
                "market_ticker": market,
                "decision_ts_utc": iso_z(decision_dt),
                "market_close_ts_utc": iso_z(close_dt),
                "strike": cents(strike),
                "seconds_to_close": cents(seconds_to_close),
                "side": side,
                "source_file": rel_path(candidate_snapshot_path),
                "source_line_or_offset": snapshot_row.get("_line_number"),
                "source_type": "paired_shadow_candidate_snapshot",
                "source_quality_tier": "shadow_forward_packet_not_successor_promotion",
                "is_pre_resolution": bool_text(pre_resolution),
                "is_pre_resolution_registered": bool_text(recorded_before_close),
                "is_recomputed_after_resolution": bool_text(not recorded_before_close),
                "is_backfilled": "False",
                "is_simulated": "True",
                "is_sidecar": "True",
                "is_diagnostic_only": "True",
                "allowed_for_forward_promotion": "False",
                "exclusion_reason": ";".join(exclusions),
                "yes_bid_cents": cents(yes_bid),
                "yes_ask_cents": cents(yes_ask),
                "no_bid_cents": cents(no_bid),
                "no_ask_cents": cents(no_ask),
                "ask_cents": cents(ask),
                "bid_cents": cents(bid),
                "book_implied_yes_from_side_ask": pct(book_implied_yes),
                "book_mid_yes_cents": cents(book_mid),
                "book_width_cents": cents(book_width),
                "book_source_event_count": "1",
                "raw_capture_ts_utc": iso_z(decision_dt),
                "btc_spot": cents(spot),
                "btc_source": str(v28.get("mushroom_v28_btc_source") or context.get("source") or "v28_context_tailer"),
                "btc_tick_ts_utc": iso_z(btc_tick_dt),
                "btc_tick_age_ms": cents(btc_age_ms),
                "reference_spot": cents(as_float(v28.get("mushroom_v28_btc_price")) or spot),
                "btc_stale_flag": bool_text(btc_age_ms is None or btc_age_ms > 10000.0),
                "btc_return_15s": pct((spot / prior_15s - 1.0) if prior_15s else None),
                "btc_return_60s": pct((spot / prior_60s - 1.0) if prior_60s else None),
                "btc_return_180s": pct((spot / prior_180s - 1.0) if prior_180s else None),
                "btc_return_300s": pct((spot / prior_300s - 1.0) if prior_300s else None),
                "btc_return_900s": pct((spot / prior_900s - 1.0) if prior_900s else None),
                "signed_move_1m_dollars": cents((spot - prior_60s) if prior_60s is not None else None),
                "signed_move_3m_dollars": cents((spot - prior_180s) if prior_180s is not None else None),
                "signed_move_5m_dollars": cents((spot - prior_300s) if prior_300s is not None else None),
                "max_adverse_move_3m": cents(path_extreme(global_contexts, decision_dt, 180, spot, side) if window_has_history(global_contexts, decision_dt, 180) else None),
                "max_adverse_move_5m": cents(path_extreme(global_contexts, decision_dt, 300, spot, side) if window_has_history(global_contexts, decision_dt, 300) else None),
                "max_adverse_move_15m": cents(path_extreme(global_contexts, decision_dt, 900, spot, side) if window_has_history(global_contexts, decision_dt, 900) else None),
                "v28_p_yes": pct(v28_p_yes),
                "v28_p_no": pct((1.0 - v28_p_yes) if v28_p_yes is not None else None),
                "v28_p_side": pct(as_float(v28.get("mushroom_v28_p_side"))),
                "v28_best_side": str(v28.get("mushroom_v28_side") or ""),
                "v28_fair_yes_cents": cents(v28_fair_yes),
                "v28_fair_no_cents": cents(v28_fair_no),
                "v28_best_fair_cents": cents(as_float(v28.get("mushroom_v28_fair_side_cents"))),
                "v28_yes_edge_cents": cents(v28_yes_edge),
                "v28_no_edge_cents": cents(v28_no_edge),
                "v28_best_edge_cents": cents(v28_best_edge),
                "v28_p_anchor": "",
                "v28_p_static_boundary_field": "",
                "v28_p_recent_transport": "",
                "v28_p_long_transport": "",
                "v28_edge_gate": "",
                "v28_static_gate": "",
                "v28_arrow": pct(as_float(v28.get("mushroom_v28_arrow"))),
                "v28_volshock": pct(as_float(v28.get("mushroom_v28_volshock"))),
                "v28_transport_recent_n": "",
                "v28_transport_long_n": "",
                "v28_learned_horizon_minutes": "",
                "v28_effective_horizon_minutes": pct(as_float(v28.get("mushroom_v28_effective_horizon_minutes"))),
                "v28_sigma_t_dollars": cents(as_float(v28.get("mushroom_v28_sigma_t_dollars"))),
                "v28_d_sigma": pct(d_sigma),
                "candidate_id": "shadow_particle_calibrated_v001",
                "model_hash": model_hash,
                "model_type": "particle_shadow_diagnostic",
                "model_track": "paired_passive_shadow_diagnostic",
                "candidate_p_yes": pct(candidate_p_yes),
                "candidate_fair_yes_cents": cents(candidate_fair_yes),
                "candidate_fair_no_cents": cents(candidate_fair_no),
                "candidate_fair_side_cents": cents(candidate_fair_side),
                "candidate_edge_cents": cents(candidate_edge),
                "candidate_feature_manifest_hash": model_hash,
                "candidate_feature_table_hash": feature_table_hash,
                "run_id": run_id,
                "candidate_snapshot_recorded_ts_utc": iso_z(recorded_dt),
                "candidate_snapshot_recorded_before_close": bool_text(recorded_before_close),
                "v28_match_ts_utc": iso_z(v28_dt if isinstance(v28_dt, datetime) else None),
                "v28_match_age_ms": cents(v28_age_ms),
                "v28_match_source_file": rel_path(event_path),
                "v28_match_source_line": v28.get("_event_line", ""),
                "v28_component_capture_status": "native_v28_components_missing_p_anchor_transport_fields",
                "candidate_manifest_forward_allowed": "False",
                "candidate_record_type": str(snapshot_row.get("record_type") or ""),
                "candidate_reason": str(snapshot_row.get("reason") or ""),
                "shadow_brownian_p_yes": pct(as_float(extra.get("brownian_p_yes"))),
                "shadow_market_p_yes": pct(as_float(extra.get("market_p_yes"))),
                "shadow_current_calibrated_p_yes": pct(as_float(extra.get("current_calibrated_p_yes"))),
                "shadow_particle_p_yes": pct(as_float(extra.get("particle_p_yes"))),
                "btc_return_source": "paired_candidate_context_spot_history",
                "strike_distance_dollars": cents(strike_distance),
                "strike_distance_dollars_abs": cents(abs(strike_distance) if strike_distance is not None else None),
                "abs_v28_d_sigma": pct(abs(d_sigma) if d_sigma is not None else None),
                "recross_hazard_score": pct(recross),
                "book_spot_disagreement_cents": cents((100.0 * (book_implied_yes - v28_p_yes)) if book_implied_yes is not None and v28_p_yes is not None else None),
            }
            packet_rows.append(row)
            labeled = dict(row)
            result = str(label.get("binary_result") or label.get("result") or "").lower()
            labeled.update(
                {
                    "y_yes_win": "1" if result == "yes" else ("0" if result == "no" else ""),
                    "binary_result": result,
                    "label_available_ts_utc": iso_z(parse_ts(label.get("label_available_ts_utc"))),
                    "settlement_ts_utc": iso_z(parse_ts(label.get("settlement_ts_utc"))),
                    "settlement_price": cents(as_float(label.get("settlement_price"))),
                    "settlement_price_is_binary_proxy": bool_text(str(label.get("settlement_price_is_binary_proxy", "true")).lower() != "false"),
                    "label_source": str(label.get("source") or "market_results_full_refresh"),
                }
            )
            labeled_rows.append(labeled)

    group_missing_counts: dict[str, int] = {group: 0 for group in FIELD_GROUPS}
    field_missing_counts: Counter[str] = Counter()
    temporal_blocker_counts: Counter[str] = Counter()
    for row in packet_rows:
        for group in FIELD_GROUPS:
            missing = row_group_missing(row, group)
            if missing:
                group_missing_counts[group] += 1
            for field in missing:
                field_missing_counts[field] += 1
        for blocker in row_temporal_blockers(row):
            temporal_blocker_counts[blocker] += 1
    packet_ready_rows = [
        row
        for row in packet_rows
        if not any(row_group_missing(row, group) for group in FIELD_GROUPS)
        and not row_temporal_blockers(row)
    ]
    label_count = sum(1 for row in labeled_rows if str(row.get("y_yes_win", "")).strip() != "")
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "run_root": rel_path(run_root),
        "run_id": run_id,
        "candidate_snapshots": len(candidate_snapshots),
        "packet_rows": len(packet_rows),
        "labeled_rows": len(labeled_rows),
        "markets": len({row["market_ticker"] for row in packet_rows}),
        "labels_joined_rows": label_count,
        "pre_resolution_rows": sum(1 for row in packet_rows if row["is_pre_resolution"] == "True"),
        "registered_pre_resolution_rows": sum(1 for row in packet_rows if row["is_pre_resolution_registered"] == "True"),
        "forward_promotion_rows": sum(1 for row in packet_rows if row["allowed_for_forward_promotion"] == "True"),
        "packet_ready_rows": len(packet_ready_rows),
        "packet_ready_markets": len({row["market_ticker"] for row in packet_ready_rows}),
        "missing_context_snapshots": missing_contexts,
        "missing_v28_match_side_rows": missing_v28_matches,
        "group_missing_counts": group_missing_counts,
        "field_missing_counts_top": dict(field_missing_counts.most_common(40)),
        "temporal_blocker_counts": dict(sorted(temporal_blocker_counts.items())),
        "exclusion_counts": dict(sorted(exclusion_counts.items())),
        "inputs": {
            "candidate_snapshots": rel_path(candidate_snapshot_path),
            "candidate_snapshots_hash": sha256_file(candidate_snapshot_path),
            "candidate_contexts": rel_path(candidate_context_path),
            "candidate_contexts_hash": sha256_file(candidate_context_path),
            "v28_events": rel_path(event_path),
            "v28_events_hash": sha256_file(event_path),
            "paired_manifest": rel_path(run_root / "paired_passive_run_manifest.json"),
            "pipeline_manifest": rel_path(run_root / "pipeline_work" / "pipeline_manifest.json"),
        },
        "outputs": {
            "packets_csv": rel_path(PACKETS_CSV),
            "packets_json": rel_path(PACKETS_JSON),
            "labeled_csv": rel_path(LABELED_CSV),
            "labeled_json": rel_path(LABELED_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
        "promotion_status": {
            "allowed": False,
            "reason": "shadow particle rows are diagnostic; native v28 packet components and successor frozen manifests are incomplete",
        },
        "pipeline_manifest": pipeline_manifest,
    }
    return packet_rows, labeled_rows, summary


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Shadow Forward Packets",
        "",
        "Research-only bridge from paired passive shadow captures into the v28 successor packet contract. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Run root: `{summary['run_root']}`",
        f"- Candidate snapshots: `{summary['candidate_snapshots']}`",
        f"- Packet side rows: `{summary['packet_rows']}`",
        f"- Markets: `{summary['markets']}`",
        f"- Labels joined rows: `{summary['labels_joined_rows']}`",
        f"- Registered before close rows: `{summary['registered_pre_resolution_rows']}`",
        f"- Packet-ready rows: `{summary['packet_ready_rows']}`",
        f"- Forward promotion rows: `{summary['forward_promotion_rows']}`",
        "",
        "## Packet Missing Groups",
        "",
        "| group | rows missing |",
        "|---|---:|",
    ]
    for group, count in summary["group_missing_counts"].items():
        lines.append(f"| `{group}` | {count} |")
    lines.extend(["", "## Top Missing Fields", "", "| field | rows |", "|---|---:|"])
    for field, count in summary["field_missing_counts_top"].items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(["", "## Exclusions", "", "| reason | rows |", "|---|---:|"])
    for reason, count in summary["exclusion_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(["", "## Temporal Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["temporal_blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- These rows are useful for proving the paired passive capture path can produce causal packet-shaped evidence.",
            "- They are not promotion evidence because the candidate is a shadow particle diagnostic, not a frozen v28 successor challenger.",
            "- Native v28 component fields such as p_anchor and transport components are still missing, so the packet contract correctly keeps packet-ready rows at zero.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(packet_rows: list[dict[str, Any]], labeled_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(packet_rows, PACKET_FIELDS, PACKETS_CSV)
    write_csv_rows(labeled_rows, LABELED_FIELDS, LABELED_CSV)
    PACKETS_JSON.write_text(json.dumps(packet_rows[:500], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LABELED_JSON.write_text(json.dumps(labeled_rows[:500], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "sample_rows": packet_rows[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=None, help="Paired shadow run root. Defaults to latest.")
    parser.add_argument("--v28-events", type=Path, default=None, help="Override v28 execution_events.ndjson source.")
    parser.add_argument("--limit-snapshots", type=int, default=None, help="Optional candidate snapshot limit.")
    parser.add_argument("--write", action="store_true", help="Write packet/labeled/audit artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    packet_rows, labeled_rows, summary = build_rows(
        run_root=args.run_root,
        event_path=args.v28_events,
        limit_snapshots=args.limit_snapshots,
    )
    if args.write and not args.dry_run:
        write_outputs(packet_rows, labeled_rows, summary)
    print(
        json.dumps(
            {
                "packet_rows": summary["packet_rows"],
                "labeled_rows": summary["labeled_rows"],
                "markets": summary["markets"],
                "registered_pre_resolution_rows": summary["registered_pre_resolution_rows"],
                "packet_ready_rows": summary["packet_ready_rows"],
                "forward_promotion_rows": summary["forward_promotion_rows"],
                "group_missing_counts": summary["group_missing_counts"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
