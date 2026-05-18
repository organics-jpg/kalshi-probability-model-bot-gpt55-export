"""Validate, preflight, freeze, and register v28 successor packet rows.

Research-only. This is the reproducible handoff from a real sidecar packet CSV
to frozen forward evidence plumbing. It does not touch live bot state, orders,
thresholds, secrets, or processes.

By default this script writes only its own handoff audit/artifacts and does not
overwrite the canonical frozen-forward registry. Use the existing freezer and
registry scripts with the same input CSV when you intentionally want to update
the canonical latest files after a real open-market collection run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from freeze_v28_successor_forward_candidates import (
    FROZEN_FIELDS,
    build as build_frozen_rows,
)
from preflight_v28_successor_forward_freeze import build as build_preflight
from register_v28_successor_forward_predictions import REGISTRY_FIELDS
from register_v28_successor_forward_predictions import stable_hash as registry_hash
from validate_v28_successor_forward_packet import build as build_packet_contract


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEFAULT_PACKET_CSV = OUT_DIR / "forward_sidecar_packet_collection_demo_latest.csv"
HANDOFF_FROZEN_CSV = OUT_DIR / "forward_packet_freeze_handoff_frozen_latest.csv"
HANDOFF_REGISTRY_CSV = OUT_DIR / "forward_packet_freeze_handoff_registry_latest.csv"
HANDOFF_JSON = EDGE_DIR / "v28_successor_forward_packet_freeze_handoff_latest.json"
HANDOFF_MD = EDGE_DIR / "v28_successor_forward_packet_freeze_handoff_latest.md"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40


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


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def registry_rows_from_frozen(frozen_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registry_rows: list[dict[str, Any]] = []
    for frozen in frozen_rows:
        source_status = str(frozen.get("source_status") or "")
        if source_status != "frozen_pre_resolution_prediction":
            continue
        candidate_id = str(frozen.get("candidate_id") or "")
        registry_rows.append(
            {
                "registry_id": registry_hash([frozen.get("frozen_prediction_id"), frozen.get("row_id"), candidate_id]),
                "registered_utc": frozen.get("frozen_utc"),
                "frozen_prediction_id": frozen.get("frozen_prediction_id"),
                "frozen_utc": frozen.get("frozen_utc"),
                "row_id": frozen.get("row_id"),
                "market_ticker": frozen.get("market_ticker"),
                "market_close_ts_utc": frozen.get("market_close_ts_utc"),
                "decision_ts_utc": frozen.get("decision_ts_utc"),
                "candidate_id": candidate_id,
                "model_hash": frozen.get("model_hash"),
                "model_type": frozen.get("model_type"),
                "model_track": frozen.get("model_track"),
                "candidate_p_yes": frozen.get("candidate_p_yes"),
                "candidate_fair_yes_cents": frozen.get("candidate_fair_yes_cents"),
                "candidate_fair_no_cents": frozen.get("candidate_fair_no_cents"),
                "v28_p_yes": frozen.get("v28_p_yes"),
                "v28_p_anchor": frozen.get("v28_p_anchor"),
                "v28_p_static_boundary_field": frozen.get("v28_p_static_boundary_field"),
                "v28_p_recent_transport": frozen.get("v28_p_recent_transport"),
                "v28_p_long_transport": frozen.get("v28_p_long_transport"),
                "v28_transport_recent_n": frozen.get("v28_transport_recent_n"),
                "v28_transport_long_n": frozen.get("v28_transport_long_n"),
                "side": frozen.get("side"),
                "candidate_fair_side_cents": frozen.get("candidate_fair_side_cents"),
                "ask_cents": frozen.get("ask_cents"),
                "candidate_edge_cents": frozen.get("candidate_edge_cents"),
                "source_status": source_status,
            }
        )
    return registry_rows


def input_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "input_rows": len(rows),
        "input_markets": len({row.get("market_ticker") for row in rows if row.get("market_ticker")}),
        "simulated_rows": sum(1 for row in rows if as_bool(row.get("is_simulated"))),
        "diagnostic_rows": sum(1 for row in rows if as_bool(row.get("is_diagnostic_only"))),
        "after_fact_rows": sum(
            1
            for row in rows
            if as_bool(row.get("is_recomputed_after_resolution")) or as_bool(row.get("is_backfilled"))
        ),
    }


def build(
    *,
    source_csv: Path = DEFAULT_PACKET_CSV,
    now_utc: datetime | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    packet_evaluations, packet_summary, _template = build_packet_contract(source_csv=source_csv)
    preflight_rows, preflight_summary = build_preflight(source_csv=source_csv, now_utc=now_utc)
    frozen_rows, freeze_summary = build_frozen_rows(source_csv=source_csv, now_utc=now_utc)
    registry_rows = registry_rows_from_frozen(frozen_rows)
    source_rows = read_csv_rows(source_csv)
    quality = input_quality(source_rows)
    registry_markets = len({row.get("market_ticker") for row in registry_rows if row.get("market_ticker")})
    blocker_counts: Counter[str] = Counter()
    for row in preflight_rows:
        for blocker in str(row.get("blockers") or "").split(";"):
            if blocker:
                blocker_counts[blocker] += 1
    blockers: list[str] = []
    if not source_csv.exists():
        blockers.append("input_csv_missing")
    if packet_summary.get("packet_ready_rows", 0) <= 0:
        blockers.append("no_packet_ready_rows")
    if preflight_summary.get("freeze_ready_rows", 0) <= 0:
        blockers.append("no_preflight_freeze_ready_rows")
    if freeze_summary.get("frozen_prediction_rows", 0) <= 0:
        blockers.append("no_frozen_predictions_from_input")
    if quality["simulated_rows"] > 0:
        blockers.append("input_contains_simulated_rows")
    if quality["diagnostic_rows"] > 0:
        blockers.append("input_contains_diagnostic_rows")
    if quality["after_fact_rows"] > 0:
        blockers.append("input_contains_after_fact_rows")
    if len(registry_rows) < MIN_FORWARD_ROWS:
        blockers.append("frozen_registry_below_row_floor")
    if registry_markets < MIN_FORWARD_MARKETS:
        blockers.append("frozen_registry_below_market_floor")

    if not frozen_rows:
        status = "blocked_no_frozen_rows"
    elif len(registry_rows) < MIN_FORWARD_ROWS or registry_markets < MIN_FORWARD_MARKETS:
        status = "frozen_handoff_below_coverage_floor"
    else:
        status = "frozen_handoff_ready_for_settlement_labels"
    if quality["simulated_rows"] or quality["diagnostic_rows"] or quality["after_fact_rows"]:
        status = "blocked_non_promotable_input_rows"

    summary = {
        "generated_utc": now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "handoff_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "packet freeze handoff is not promotion; settled labels, source contract, forward evidence scoring, and promotion verifier are still required",
        },
        "blockers": sorted(set(blockers)),
        "row_blocker_counts": dict(sorted(blocker_counts.items())),
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "input_quality": quality,
        "packet_contract": {
            "packet_status": packet_summary.get("packet_status"),
            "input_rows": packet_summary.get("input_rows"),
            "packet_ready_rows": packet_summary.get("packet_ready_rows"),
            "packet_ready_markets": packet_summary.get("packet_ready_markets"),
            "group_missing_counts": packet_summary.get("group_missing_counts"),
        },
        "preflight": {
            "preflight_status": preflight_summary.get("preflight_status"),
            "freeze_ready_rows": preflight_summary.get("freeze_ready_rows"),
            "freeze_ready_markets": preflight_summary.get("freeze_ready_markets"),
            "readiness_blockers": preflight_summary.get("readiness_blockers"),
        },
        "freeze": {
            "freeze_status": freeze_summary.get("freeze_status"),
            "freeze_ready_input_rows": freeze_summary.get("freeze_ready_input_rows"),
            "frozen_prediction_rows": freeze_summary.get("frozen_prediction_rows"),
            "frozen_prediction_markets": freeze_summary.get("frozen_prediction_markets"),
            "blocker_counts": freeze_summary.get("blocker_counts"),
        },
        "registry": {
            "row_count": len(registry_rows),
            "market_count": registry_markets,
            "source_status_counts": dict(Counter(row.get("source_status") for row in registry_rows)),
            "coverage_ready": len(registry_rows) >= MIN_FORWARD_ROWS and registry_markets >= MIN_FORWARD_MARKETS,
        },
        "inputs": {
            "source_csv": rel_path(source_csv),
            "source_hash": sha256_file(source_csv),
        },
        "outputs": {
            "handoff_json": rel_path(HANDOFF_JSON),
            "handoff_md": rel_path(HANDOFF_MD),
            "handoff_frozen_csv": rel_path(HANDOFF_FROZEN_CSV),
            "handoff_registry_csv": rel_path(HANDOFF_REGISTRY_CSV),
        },
    }
    return {"summary": summary, "packet_rows": packet_evaluations[:200]}, frozen_rows, registry_rows


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Forward Packet Freeze Handoff",
        "",
        "Research-only handoff audit. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Handoff status: `{summary['handoff_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Input rows: `{summary['input_quality']['input_rows']}`",
        f"- Packet-ready rows: `{summary['packet_contract']['packet_ready_rows']}`",
        f"- Freeze-ready rows: `{summary['preflight']['freeze_ready_rows']}`",
        f"- Frozen prediction rows: `{summary['freeze']['frozen_prediction_rows']}`",
        f"- Registry rows: `{summary['registry']['row_count']}`",
        f"- Registry markets: `{summary['registry']['market_count']}`",
        "",
        "## Blockers",
        "",
    ]
    for blocker in summary["blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Use this handoff on real sidecar packet CSVs captured before close.",
            "- Demo, simulated, diagnostic, backfilled, or after-the-fact rows remain blocked.",
            "- Even a successful freeze handoff still needs post-resolution label join, forward evidence scoring, source contract, and promotion verifier.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], frozen_rows: list[dict[str, Any]], registry_rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(frozen_rows, FROZEN_FIELDS, HANDOFF_FROZEN_CSV)
    write_csv_rows(registry_rows, REGISTRY_FIELDS, HANDOFF_REGISTRY_CSV)
    HANDOFF_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, HANDOFF_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_PACKET_CSV, help="Sidecar packet CSV to validate/freeze/register in handoff artifacts.")
    parser.add_argument("--now-utc", default="", help="Override current UTC timestamp for deterministic pre-close runs.")
    parser.add_argument("--write", action="store_true", help="Write handoff audit and handoff CSV artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report, frozen_rows, registry_rows = build(source_csv=args.input_csv, now_utc=now_utc)
    if args.write and not args.dry_run:
        write_outputs(report, frozen_rows, registry_rows)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "handoff_status": summary["handoff_status"],
                "packet_ready_rows": summary["packet_contract"]["packet_ready_rows"],
                "freeze_ready_rows": summary["preflight"]["freeze_ready_rows"],
                "frozen_prediction_rows": summary["freeze"]["frozen_prediction_rows"],
                "registry_rows": summary["registry"]["row_count"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
