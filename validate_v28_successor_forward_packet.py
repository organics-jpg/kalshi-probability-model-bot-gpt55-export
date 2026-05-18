"""Validate the complete forward input packet required by the v28 successor spec.

Research-only. This is the contract between passive staging and frozen forward
prediction rows. It checks whether rows have the complete pre-resolution packet
needed to compute v28 baseline, challenger probabilities, fair cents, and later
settlement scoring without after-the-fact reconstruction.

Current passive rows are expected to fail this contract because they contain
Kalshi market/book state only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PASSIVE_SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"

PACKET_JSON = EDGE_DIR / "v28_successor_forward_packet_contract_latest.json"
PACKET_MD = EDGE_DIR / "v28_successor_forward_packet_contract_latest.md"
PACKET_CSV = EDGE_DIR / "v28_successor_forward_packet_contract_latest.csv"
PACKET_TEMPLATE_JSON = OUT_DIR / "forward_packet_template_latest.json"


FIELD_GROUPS: dict[str, list[str]] = {
    "identity_and_clock": [
        "row_id",
        "market_ticker",
        "decision_ts_utc",
        "market_close_ts_utc",
        "strike",
        "seconds_to_close",
        "side",
        "source_file",
        "source_line_or_offset",
        "source_type",
        "source_quality_tier",
    ],
    "causality": [
        "is_pre_resolution",
        "is_pre_resolution_registered",
        "is_recomputed_after_resolution",
        "is_backfilled",
        "is_simulated",
        "is_sidecar",
        "is_diagnostic_only",
        "allowed_for_forward_promotion",
        "exclusion_reason",
    ],
    "market_and_book": [
        "yes_bid_cents",
        "yes_ask_cents",
        "no_bid_cents",
        "no_ask_cents",
        "ask_cents",
        "bid_cents",
        "book_implied_yes_from_side_ask",
        "book_mid_yes_cents",
        "book_width_cents",
        "book_source_event_count",
        "raw_capture_ts_utc",
    ],
    "btc_and_feed": [
        "btc_spot",
        "btc_source",
        "btc_tick_ts_utc",
        "btc_tick_age_ms",
        "reference_spot",
        "btc_stale_flag",
        "btc_return_15s",
        "btc_return_60s",
        "btc_return_180s",
        "btc_return_300s",
        "btc_return_900s",
        "signed_move_1m_dollars",
        "signed_move_3m_dollars",
        "signed_move_5m_dollars",
        "max_adverse_move_3m",
        "max_adverse_move_5m",
        "max_adverse_move_15m",
    ],
    "v28_baseline": [
        "v28_p_yes",
        "v28_p_no",
        "v28_p_side",
        "v28_best_side",
        "v28_fair_yes_cents",
        "v28_fair_no_cents",
        "v28_best_fair_cents",
        "v28_yes_edge_cents",
        "v28_no_edge_cents",
        "v28_best_edge_cents",
        "v28_p_anchor",
        "v28_p_static_boundary_field",
        "v28_p_recent_transport",
        "v28_p_long_transport",
        "v28_edge_gate",
        "v28_static_gate",
        "v28_arrow",
        "v28_volshock",
        "v28_transport_recent_n",
        "v28_transport_long_n",
        "v28_learned_horizon_minutes",
        "v28_effective_horizon_minutes",
        "v28_sigma_t_dollars",
        "v28_d_sigma",
    ],
    "candidate_prediction": [
        "candidate_id",
        "model_hash",
        "model_type",
        "model_track",
        "candidate_p_yes",
        "candidate_fair_yes_cents",
        "candidate_fair_no_cents",
        "candidate_fair_side_cents",
        "candidate_edge_cents",
        "candidate_feature_manifest_hash",
        "candidate_feature_table_hash",
    ],
}

FORBIDDEN_BEFORE_FREEZE = [
    "y_yes_win",
    "settlement_price",
    "settlement_ts_utc",
    "settlement_source",
    "settlement_margin_dollars",
    "settlement_side",
    "final_average_window_end_utc",
]

NUMERIC_FIELDS = {
    "strike",
    "seconds_to_close",
    "yes_bid_cents",
    "yes_ask_cents",
    "no_bid_cents",
    "no_ask_cents",
    "ask_cents",
    "bid_cents",
    "book_implied_yes_from_side_ask",
    "book_mid_yes_cents",
    "book_width_cents",
    "btc_spot",
    "btc_tick_age_ms",
    "reference_spot",
    "v28_p_yes",
    "v28_p_no",
    "v28_p_side",
    "v28_fair_yes_cents",
    "v28_fair_no_cents",
    "candidate_p_yes",
    "candidate_fair_yes_cents",
    "candidate_fair_no_cents",
}

BOOLEAN_FIELDS = {
    "is_pre_resolution",
    "is_pre_resolution_registered",
    "is_recomputed_after_resolution",
    "is_backfilled",
    "is_simulated",
    "is_sidecar",
    "is_diagnostic_only",
    "allowed_for_forward_promotion",
    "btc_stale_flag",
}

TIMESTAMP_FIELDS = {
    "decision_ts_utc",
    "market_close_ts_utc",
    "raw_capture_ts_utc",
    "btc_tick_ts_utc",
}


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader], list(reader.fieldnames or [])


def has_value(row: dict[str, Any], field: str) -> bool:
    return field in row and str(row.get(field, "")).strip() != ""


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


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


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


def field_valid(row: dict[str, Any], field: str) -> bool:
    if not has_value(row, field):
        return False
    if field in NUMERIC_FIELDS:
        return as_float(row.get(field)) is not None
    if field in BOOLEAN_FIELDS:
        return as_bool(row.get(field)) is not None
    if field in TIMESTAMP_FIELDS:
        return parse_ts(row.get(field)) is not None
    return True


def row_group_missing(row: dict[str, Any], group: str) -> list[str]:
    return [field for field in FIELD_GROUPS[group] if not field_valid(row, field)]


def row_temporal_blockers(row: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    decision = parse_ts(row.get("decision_ts_utc"))
    close = parse_ts(row.get("market_close_ts_utc"))
    btc_tick = parse_ts(row.get("btc_tick_ts_utc"))
    raw_capture = parse_ts(row.get("raw_capture_ts_utc"))
    if decision is None or close is None or decision > close:
        blockers.append("decision_after_close_or_unparseable")
    if btc_tick is not None and decision is not None and btc_tick > decision:
        blockers.append("btc_tick_after_decision")
    if raw_capture is not None and close is not None and raw_capture > close:
        blockers.append("book_capture_after_close")
    for field in FORBIDDEN_BEFORE_FREEZE:
        if has_value(row, field):
            blockers.append(f"forbidden_pre_freeze_field_present:{field}")
    if as_bool(row.get("is_recomputed_after_resolution")) is True:
        blockers.append("is_recomputed_after_resolution_true")
    if as_bool(row.get("is_backfilled")) is True:
        blockers.append("is_backfilled_true")
    return blockers


def build_template() -> dict[str, Any]:
    return {
        "contract": "v28_successor_forward_packet_v1",
        "purpose": "Complete pre-resolution packet required before freezing v28 successor candidate predictions.",
        "field_groups": FIELD_GROUPS,
        "forbidden_before_freeze": FORBIDDEN_BEFORE_FREEZE,
        "notes": [
            "Settlement labels must be joined only after freeze and market resolution.",
            "v28 component fields should be captured at decision time; reconstructed replay may be stored separately but is not promotion-grade by itself.",
            "Candidate fields must come from a frozen manifest/model hash allowed for forward registry.",
        ],
    }


def build(
    limit_rows: int | None = None,
    source_csv: Path = PASSIVE_SNAPSHOTS_CSV,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    rows, fieldnames = read_csv_rows(source_csv)
    if limit_rows is not None:
        rows = rows[:limit_rows]
    evaluations: list[dict[str, Any]] = []
    group_missing_counts: dict[str, int] = {group: 0 for group in FIELD_GROUPS}
    field_missing_counts: Counter[str] = Counter()
    temporal_blocker_counts: Counter[str] = Counter()

    for row in rows:
        missing_by_group = {group: row_group_missing(row, group) for group in FIELD_GROUPS}
        temporal_blockers = row_temporal_blockers(row)
        for group, missing in missing_by_group.items():
            if missing:
                group_missing_counts[group] += 1
            for field in missing:
                field_missing_counts[field] += 1
        for blocker in temporal_blockers:
            temporal_blocker_counts[blocker] += 1
        packet_ready = not any(missing_by_group.values()) and not temporal_blockers
        evaluations.append(
            {
                "row_id": row.get("row_id"),
                "market_ticker": row.get("market_ticker"),
                "side": row.get("side"),
                "decision_ts_utc": row.get("decision_ts_utc"),
                "market_close_ts_utc": row.get("market_close_ts_utc"),
                "packet_ready": packet_ready,
                "missing_groups": ";".join(group for group, missing in missing_by_group.items() if missing),
                "temporal_blockers": ";".join(temporal_blockers),
            }
        )

    ready_rows = [row for row in evaluations if row["packet_ready"]]
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "contract": "v28_successor_forward_packet_v1",
        "packet_status": "ready" if ready_rows else "blocked",
        "input_rows": len(rows),
        "input_columns": len(fieldnames),
        "packet_ready_rows": len(ready_rows),
        "packet_ready_markets": len({str(row.get("market_ticker") or "") for row in ready_rows if row.get("market_ticker")}),
        "group_missing_counts": group_missing_counts,
        "field_missing_counts_top": dict(field_missing_counts.most_common(40)),
        "temporal_blocker_counts": dict(sorted(temporal_blocker_counts.items())),
        "inputs": {
            "source_csv": rel_path(source_csv),
            "default_passive_snapshots_csv": rel_path(PASSIVE_SNAPSHOTS_CSV),
        },
        "outputs": {
            "json": rel_path(PACKET_JSON),
            "markdown": rel_path(PACKET_MD),
            "csv": rel_path(PACKET_CSV),
            "template_json": rel_path(PACKET_TEMPLATE_JSON),
        },
    }
    return evaluations, summary, build_template()


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "market_ticker",
        "side",
        "decision_ts_utc",
        "market_close_ts_utc",
        "packet_ready",
        "missing_groups",
        "temporal_blockers",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], template: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Packet Contract",
        "",
        "Research-only packet validator. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Contract: `{summary['contract']}`",
        f"- Packet status: `{summary['packet_status']}`",
        f"- Input rows: `{summary['input_rows']}`",
        f"- Packet-ready rows: `{summary['packet_ready_rows']}`",
        f"- Packet-ready markets: `{summary['packet_ready_markets']}`",
        "",
        "## Missing Groups",
        "",
        "| group | rows missing | required fields |",
        "|---|---:|---|",
    ]
    for group, fields in template["field_groups"].items():
        lines.append(f"| `{group}` | {summary['group_missing_counts'].get(group, 0)} | `{', '.join(fields)}` |")
    lines.extend(["", "## Top Missing Fields", "", "| field | rows missing |", "|---|---:|"])
    for field, count in summary["field_missing_counts_top"].items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(["", "## Temporal Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["temporal_blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Forbidden Before Freeze",
            "",
        ]
    )
    for field in template["forbidden_before_freeze"]:
        lines.append(f"- `{field}`")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is the exact packet contract a future live/passive recorder must satisfy before freezing candidate predictions.",
            "- Current passive rows fail because they lack BTC/feed, v28 baseline, and candidate prediction groups.",
            "- Settlement fields are explicitly forbidden before freeze and should be joined only after market resolution.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any], template: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, PACKET_CSV)
    PACKET_JSON.write_text(json.dumps({"summary": summary, "template": template, "rows": rows[:200]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PACKET_TEMPLATE_JSON.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, template, PACKET_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write packet contract artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--input-csv", type=Path, default=PASSIVE_SNAPSHOTS_CSV, help="Input staging/packet CSV to validate.")
    args = parser.parse_args()
    rows, summary, template = build(limit_rows=args.limit_rows, source_csv=args.input_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary, template)
    print(
        json.dumps(
            {
                "packet_status": summary["packet_status"],
                "input_rows": summary["input_rows"],
                "packet_ready_rows": summary["packet_ready_rows"],
                "packet_ready_markets": summary["packet_ready_markets"],
                "group_missing_counts": summary["group_missing_counts"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
