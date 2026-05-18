"""Build and validate v28 successor forward-packet adapter rows.

Research-only. This module is the sidecar adapter future passive collection
should call after a book checkpoint has BTC history, a v28 EdgeBatch, and frozen
collection-candidate manifests available before close. It never reads live bot
state, places orders, or mutates strategy logic.

The default CLI writes a deterministic demo packet set so the packet contract
can be tested end to end without pretending there are real forward rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from score_v28_successor_forward_packets import candidate_predict, feature_row
from validate_v28_successor_forward_packet import FIELD_GROUPS, row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_logged_events_latest.json"
ADAPTER_DEMO_CSV = OUT_DIR / "forward_packet_adapter_demo_latest.csv"
ADAPTER_DEMO_JSON = OUT_DIR / "forward_packet_adapter_demo_latest.json"
ADAPTER_AUDIT_JSON = EDGE_DIR / "v28_successor_forward_packet_adapter_latest.json"
ADAPTER_AUDIT_MD = EDGE_DIR / "v28_successor_forward_packet_adapter_latest.md"

PACKET_FIELDS = list(dict.fromkeys([field for fields in FIELD_GROUPS.values() for field in fields]))


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def stable_hash(parts: list[Any]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(str(part if part is not None else "").encode("utf-8"))
        digest.update(b"\x1f")
    return digest.hexdigest()[:24]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


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


def fmt_float(value: Any, places: int = 10) -> str:
    parsed = as_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.{places}g}"


def fmt_cents(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def scalar_at(value: Any, index: int = 0) -> Any:
    if value is None or isinstance(value, (str, bytes)):
        return value
    if isinstance(value, dict):
        return value
    try:
        return value[index]
    except (TypeError, KeyError, IndexError):
        return value


def side_book_implied_yes(side: str, ask_cents: Any) -> float | None:
    ask = as_float(ask_cents)
    if ask is None:
        return None
    ask_p = min(1.0, max(0.0, ask / 100.0))
    if side == "yes":
        return ask_p
    if side == "no":
        return 1.0 - ask_p
    return None


def latest_tick_before(history_rows: list[dict[str, Any]], decision_dt: datetime) -> dict[str, Any] | None:
    selected: dict[str, Any] | None = None
    for row in sorted(history_rows, key=lambda item: parse_ts(item.get("ts_utc")) or datetime.min.replace(tzinfo=timezone.utc)):
        row_dt = parse_ts(row.get("ts_utc"))
        if row_dt is None:
            continue
        if row_dt <= decision_dt:
            selected = row
        else:
            break
    return selected


def prior_spot(history_rows: list[dict[str, Any]], decision_dt: datetime, seconds: int) -> float | None:
    target = decision_dt - timedelta(seconds=seconds)
    selected = latest_tick_before(history_rows, target)
    return as_float(selected.get("price")) if selected else None


def window_has_history(history_rows: list[dict[str, Any]], decision_dt: datetime, seconds: int) -> bool:
    start = decision_dt - timedelta(seconds=seconds)
    return any((parse_ts(row.get("ts_utc")) or decision_dt) <= start for row in history_rows)


def adverse_move(history_rows: list[dict[str, Any]], decision_dt: datetime, seconds: int, current_spot: float, side: str) -> float | None:
    start = decision_dt - timedelta(seconds=seconds)
    spots = []
    for row in history_rows:
        row_dt = parse_ts(row.get("ts_utc"))
        spot = as_float(row.get("price"))
        if row_dt is not None and spot is not None and start <= row_dt <= decision_dt:
            spots.append(spot)
    if not spots:
        return None
    if side == "yes":
        return max(0.0, current_spot - min(spots))
    return max(0.0, max(spots) - current_spot)


def btc_feed_fields(
    history_rows: list[dict[str, Any]],
    *,
    decision_ts_utc: Any,
    side: str,
    stale_after_ms: float = 2500.0,
) -> dict[str, Any]:
    decision_dt = parse_ts(decision_ts_utc)
    if decision_dt is None:
        return {field: "" for field in FIELD_GROUPS["btc_and_feed"]}
    latest = latest_tick_before(history_rows, decision_dt)
    if not latest:
        return {field: "" for field in FIELD_GROUPS["btc_and_feed"]}
    tick_dt = parse_ts(latest.get("ts_utc"))
    spot = as_float(latest.get("price"))
    if tick_dt is None or spot is None:
        return {field: "" for field in FIELD_GROUPS["btc_and_feed"]}

    age_ms = max(0.0, 1000.0 * (decision_dt - tick_dt).total_seconds())
    prior_15s = prior_spot(history_rows, decision_dt, 15)
    prior_60s = prior_spot(history_rows, decision_dt, 60)
    prior_180s = prior_spot(history_rows, decision_dt, 180)
    prior_300s = prior_spot(history_rows, decision_dt, 300)
    prior_900s = prior_spot(history_rows, decision_dt, 900)
    return {
        "btc_spot": fmt_cents(spot),
        "btc_source": str(latest.get("source") or "research_sidecar_btc_history"),
        "btc_tick_ts_utc": iso_z(tick_dt),
        "btc_tick_age_ms": fmt_cents(age_ms),
        "reference_spot": fmt_cents(spot),
        "btc_stale_flag": bool_text(age_ms > stale_after_ms),
        "btc_return_15s": fmt_float((spot / prior_15s - 1.0) if prior_15s else None),
        "btc_return_60s": fmt_float((spot / prior_60s - 1.0) if prior_60s else None),
        "btc_return_180s": fmt_float((spot / prior_180s - 1.0) if prior_180s else None),
        "btc_return_300s": fmt_float((spot / prior_300s - 1.0) if prior_300s else None),
        "btc_return_900s": fmt_float((spot / prior_900s - 1.0) if prior_900s else None),
        "signed_move_1m_dollars": fmt_cents((spot - prior_60s) if prior_60s is not None else None),
        "signed_move_3m_dollars": fmt_cents((spot - prior_180s) if prior_180s is not None else None),
        "signed_move_5m_dollars": fmt_cents((spot - prior_300s) if prior_300s is not None else None),
        "max_adverse_move_3m": fmt_cents(adverse_move(history_rows, decision_dt, 180, spot, side) if window_has_history(history_rows, decision_dt, 180) else None),
        "max_adverse_move_5m": fmt_cents(adverse_move(history_rows, decision_dt, 300, spot, side) if window_has_history(history_rows, decision_dt, 300) else None),
        "max_adverse_move_15m": fmt_cents(adverse_move(history_rows, decision_dt, 900, spot, side) if window_has_history(history_rows, decision_dt, 900) else None),
    }


def component(edge_batch: Any, name: str, index: int = 0) -> Any:
    components = getattr(edge_batch, "components", {}) or {}
    return scalar_at(components.get(name), index)


def v28_baseline_fields_from_edge_batch(edge_batch: Any, *, side: str, index: int = 0) -> dict[str, Any]:
    p_yes = as_float(scalar_at(getattr(edge_batch, "p_yes", None), index))
    p_no = as_float(scalar_at(getattr(edge_batch, "p_no", None), index))
    if p_no is None and p_yes is not None:
        p_no = 1.0 - p_yes
    fair_yes = as_float(scalar_at(getattr(edge_batch, "fair_yes_cents", None), index))
    if fair_yes is None and p_yes is not None:
        fair_yes = 100.0 * p_yes
    fair_no = as_float(scalar_at(getattr(edge_batch, "fair_no_cents", None), index))
    if fair_no is None and fair_yes is not None:
        fair_no = 100.0 - fair_yes
    yes_edge = as_float(scalar_at(getattr(edge_batch, "yes_net_edge_cents", None), index))
    no_edge = as_float(scalar_at(getattr(edge_batch, "no_net_edge_cents", None), index))
    best_side = scalar_at(getattr(edge_batch, "best_side", None), index)
    if not best_side and yes_edge is not None and no_edge is not None:
        best_side = "yes" if yes_edge >= no_edge else "no"
    best_fair = as_float(scalar_at(getattr(edge_batch, "best_fair_cents", None), index))
    if best_fair is None:
        best_fair = fair_yes if str(best_side).lower() == "yes" else fair_no
    best_edge = as_float(scalar_at(getattr(edge_batch, "best_edge_cents", None), index))
    if best_edge is None:
        best_edge = yes_edge if str(best_side).lower() == "yes" else no_edge
    p_side = p_yes if side == "yes" else p_no
    return {
        "v28_p_yes": fmt_float(p_yes),
        "v28_p_no": fmt_float(p_no),
        "v28_p_side": fmt_float(p_side),
        "v28_best_side": str(best_side or ""),
        "v28_fair_yes_cents": fmt_cents(fair_yes),
        "v28_fair_no_cents": fmt_cents(fair_no),
        "v28_best_fair_cents": fmt_cents(best_fair),
        "v28_yes_edge_cents": fmt_cents(yes_edge),
        "v28_no_edge_cents": fmt_cents(no_edge),
        "v28_best_edge_cents": fmt_cents(best_edge),
        "v28_p_anchor": fmt_float(component(edge_batch, "p_anchor", index)),
        "v28_p_static_boundary_field": fmt_float(component(edge_batch, "p_static_boundary_field", index)),
        "v28_p_recent_transport": fmt_float(component(edge_batch, "p_recent_transport", index)),
        "v28_p_long_transport": fmt_float(component(edge_batch, "p_long_transport", index)),
        "v28_edge_gate": fmt_float(component(edge_batch, "edge_gate", index)),
        "v28_static_gate": fmt_float(component(edge_batch, "static_gate", index)),
        "v28_arrow": fmt_float(component(edge_batch, "arrow", index)),
        "v28_volshock": fmt_float(component(edge_batch, "volshock", index)),
        "v28_transport_recent_n": fmt_float(component(edge_batch, "transport_recent_n", index)),
        "v28_transport_long_n": fmt_float(component(edge_batch, "transport_long_n", index)),
        "v28_learned_horizon_minutes": fmt_float(component(edge_batch, "learned_horizon_minutes", index)),
        "v28_effective_horizon_minutes": fmt_float(component(edge_batch, "effective_horizon_minutes", index)),
        "v28_sigma_t_dollars": fmt_cents(component(edge_batch, "sigma_t_dollars", index)),
        "v28_d_sigma": fmt_float(component(edge_batch, "d_sigma", index)),
    }


def collection_manifests(path: Path = CANDIDATE_MANIFESTS_JSON) -> list[dict[str, Any]]:
    rows = read_json(path) or []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if str(row.get("allowed_for_forward_collection")).lower() == "true"]


def base_packet_from_passive_row(
    passive_row: dict[str, Any],
    *,
    btc_history_rows: list[dict[str, Any]],
    edge_batch: Any,
    strike_index: int = 0,
) -> dict[str, Any]:
    side = str(passive_row.get("side") or "").lower()
    is_simulated = as_bool(passive_row.get("is_simulated"))
    is_diagnostic = as_bool(passive_row.get("is_diagnostic_only"))
    exclusion_reason = str(passive_row.get("exclusion_reason") or "").strip()
    if not is_simulated and not is_diagnostic:
        exclusion_reason = "not_frozen_candidate_prediction_registry"
    row = {
        field: passive_row.get(field, "")
        for group in ("identity_and_clock", "causality", "market_and_book")
        for field in FIELD_GROUPS[group]
    }
    row["is_pre_resolution"] = bool_text(as_bool(passive_row.get("is_pre_resolution")))
    row["is_pre_resolution_registered"] = bool_text(as_bool(passive_row.get("is_pre_resolution_registered")))
    row["is_recomputed_after_resolution"] = "False"
    row["is_backfilled"] = "False"
    row["is_simulated"] = bool_text(is_simulated)
    row["is_sidecar"] = "True"
    row["is_diagnostic_only"] = bool_text(is_diagnostic)
    row["allowed_for_forward_promotion"] = "False"
    row["exclusion_reason"] = exclusion_reason or "not_frozen_candidate_prediction_registry"
    row.update(btc_feed_fields(btc_history_rows, decision_ts_utc=row.get("decision_ts_utc"), side=side))
    row.update(v28_baseline_fields_from_edge_batch(edge_batch, side=side, index=strike_index))
    row.update(
        {
            "has_btc_state": "True",
            "has_v28_baseline": "True",
            "has_candidate_prediction": "False",
            "has_settlement_label": "False",
            "eligible_for_candidate_prediction": "True",
        }
    )
    return row


def build_candidate_packet_rows(
    passive_row: dict[str, Any],
    *,
    btc_history_rows: list[dict[str, Any]],
    edge_batch: Any,
    candidate_manifests: list[dict[str, Any]],
    strike_index: int = 0,
) -> list[dict[str, Any]]:
    base = base_packet_from_passive_row(
        passive_row,
        btc_history_rows=btc_history_rows,
        edge_batch=edge_batch,
        strike_index=strike_index,
    )
    rows: list[dict[str, Any]] = []
    for manifest in candidate_manifests:
        features = feature_row(base)
        p_yes = candidate_predict(manifest, features)
        side = str(base.get("side") or "").lower()
        ask = as_float(base.get("ask_cents")) or 100.0
        fair_yes = 100.0 * p_yes
        fair_no = 100.0 * (1.0 - p_yes)
        fair_side = fair_yes if side == "yes" else fair_no
        row = dict(base)
        row.update(
            {
                "row_id": stable_hash([base.get("row_id"), manifest.get("candidate_id"), manifest.get("model_hash")]),
                "candidate_id": manifest.get("candidate_id"),
                "model_hash": manifest.get("model_hash"),
                "model_type": manifest.get("model_type"),
                "model_track": manifest.get("model_track"),
                "candidate_p_yes": fmt_float(p_yes),
                "candidate_fair_yes_cents": fmt_cents(fair_yes),
                "candidate_fair_no_cents": fmt_cents(fair_no),
                "candidate_fair_side_cents": fmt_cents(fair_side),
                "candidate_edge_cents": fmt_cents(fair_side - ask),
                "candidate_feature_manifest_hash": manifest.get("feature_manifest_hash"),
                "candidate_feature_table_hash": manifest.get("feature_table_hash"),
                "has_candidate_prediction": "True",
            }
        )
        rows.append(row)
    return rows


def demo_passive_row() -> dict[str, Any]:
    decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
    close = decision + timedelta(minutes=10)
    return {
        "row_id": "adapter_demo_passive_yes",
        "market_ticker": "KXBTC15M-26MAY111210-100000",
        "decision_ts_utc": iso_z(decision),
        "market_close_ts_utc": iso_z(close),
        "strike": "100000",
        "seconds_to_close": "600",
        "side": "yes",
        "source_file": "research_packet_adapter_demo",
        "source_line_or_offset": "1",
        "source_type": "research_sidecar_adapter_demo",
        "source_quality_tier": "synthetic_contract_fixture_not_evidence",
        "is_pre_resolution": "True",
        "is_pre_resolution_registered": "True",
        "is_recomputed_after_resolution": "False",
        "is_backfilled": "False",
        "is_simulated": "True",
        "is_sidecar": "True",
        "is_diagnostic_only": "True",
        "allowed_for_forward_promotion": "False",
        "exclusion_reason": "adapter_demo_not_real_forward_evidence",
        "yes_bid_cents": "52",
        "yes_ask_cents": "54",
        "no_bid_cents": "46",
        "no_ask_cents": "48",
        "ask_cents": "54",
        "bid_cents": "52",
        "book_implied_yes_from_side_ask": fmt_float(side_book_implied_yes("yes", "54")),
        "book_mid_yes_cents": "53",
        "book_width_cents": "2",
        "book_source_event_count": "4",
        "raw_capture_ts_utc": iso_z(decision),
    }


def demo_btc_history() -> list[dict[str, Any]]:
    decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
    rows: list[dict[str, Any]] = []
    for step in range(0, 65):
        ts = decision - timedelta(seconds=(64 - step) * 15)
        price = 99930.0 + 1.4 * step
        rows.append({"ts_utc": iso_z(ts), "price": price, "source": "adapter_demo_btc_history"})
    rows.append({"ts_utc": iso_z(decision), "price": 100020.0, "source": "adapter_demo_btc_history"})
    return rows


def demo_edge_batch() -> Any:
    return SimpleNamespace(
        p_yes=[0.571],
        p_no=[0.429],
        fair_yes_cents=[57.1],
        fair_no_cents=[42.9],
        yes_net_edge_cents=[2.1],
        no_net_edge_cents=[-5.1],
        best_side=["yes"],
        best_edge_cents=[2.1],
        best_fair_cents=[57.1],
        side_probability=[0.571],
        components={
            "p_anchor": [0.552],
            "p_static_boundary_field": [0.558],
            "p_recent_transport": [0.568],
            "p_long_transport": [0.561],
            "edge_gate": [0.52],
            "static_gate": [0.91],
            "arrow": 0.04,
            "volshock": 0.12,
            "transport_recent_n": 320.0,
            "transport_long_n": 2100.0,
            "learned_horizon_minutes": 10.0,
            "effective_horizon_minutes": 10.0,
            "sigma_t_dollars": 115.0,
            "d_sigma": [-0.1739130435],
        },
    )


def summarize(rows: list[dict[str, Any]], manifests: list[dict[str, Any]]) -> dict[str, Any]:
    group_missing_counts: dict[str, int] = {group: 0 for group in FIELD_GROUPS}
    field_missing_counts: Counter[str] = Counter()
    temporal_blocker_counts: Counter[str] = Counter()
    for row in rows:
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
        for row in rows
        if not any(row_group_missing(row, group) for group in FIELD_GROUPS)
        and not row_temporal_blockers(row)
    ]
    return {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "adapter_status": "contract_demo_ready" if packet_ready_rows else "contract_demo_blocked",
        "demo_rows": len(rows),
        "demo_packet_ready_rows": len(packet_ready_rows),
        "demo_packet_ready_markets": len({row.get("market_ticker") for row in packet_ready_rows}),
        "candidate_count": len(manifests),
        "candidate_ids": [row.get("candidate_id") for row in manifests],
        "group_missing_counts": group_missing_counts,
        "field_missing_counts_top": dict(field_missing_counts.most_common(20)),
        "temporal_blocker_counts": dict(sorted(temporal_blocker_counts.items())),
        "promotion_status": {
            "allowed": False,
            "reason": "adapter demo rows are synthetic contract fixtures, not frozen forward evidence",
        },
        "inputs": {
            "candidate_manifests_json": rel_path(CANDIDATE_MANIFESTS_JSON),
            "candidate_manifests_hash": sha256_file(CANDIDATE_MANIFESTS_JSON),
        },
        "outputs": {
            "demo_csv": rel_path(ADAPTER_DEMO_CSV),
            "demo_json": rel_path(ADAPTER_DEMO_JSON),
            "audit_json": rel_path(ADAPTER_AUDIT_JSON),
            "audit_md": rel_path(ADAPTER_AUDIT_MD),
        },
    }


def build_demo() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifests = collection_manifests()
    rows = build_candidate_packet_rows(
        demo_passive_row(),
        btc_history_rows=demo_btc_history(),
        edge_batch=demo_edge_batch(),
        candidate_manifests=manifests,
    )
    return rows, summarize(rows, manifests)


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(PACKET_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Packet Adapter",
        "",
        "Research-only sidecar adapter demo. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Adapter status: `{summary['adapter_status']}`",
        f"- Demo rows: `{summary['demo_rows']}`",
        f"- Demo packet-ready rows: `{summary['demo_packet_ready_rows']}`",
        f"- Candidate manifests: `{summary['candidate_count']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed']}`",
        "",
        "## Missing Groups",
        "",
        "| group | rows missing |",
        "|---|---:|",
    ]
    for group, count in summary["group_missing_counts"].items():
        lines.append(f"| `{group}` | {count} |")
    lines.extend(["", "## Temporal Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["temporal_blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The adapter demonstrates the exact sidecar shape future passive collection should emit before close.",
            "- Demo rows are synthetic contract fixtures and must not be promoted or joined as forward evidence.",
            "- Real promotion still requires broad frozen rows captured before settlement and later settled labels.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, ADAPTER_DEMO_CSV)
    ADAPTER_DEMO_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ADAPTER_AUDIT_JSON.write_text(json.dumps({"summary": summary, "sample_rows": rows[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, ADAPTER_AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write demo adapter artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build demo rows in memory only.")
    args = parser.parse_args()
    rows, summary = build_demo()
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "adapter_status": summary["adapter_status"],
                "demo_rows": summary["demo_rows"],
                "demo_packet_ready_rows": summary["demo_packet_ready_rows"],
                "candidate_count": summary["candidate_count"],
                "promotion_allowed": summary["promotion_status"]["allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
