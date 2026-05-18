"""Preflight passive rows before freezing v28 successor forward predictions.

Research-only. This script inspects passive forward staging rows, candidate
manifests, and the current forward registry, then explains whether any row can
be frozen into a true pre-resolution prediction registry right now.

It never reads live bot state, never places orders, and never mutates live
thresholds, secrets, or order logic.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_v28_successor_forward_packet import row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PASSIVE_SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"
CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_logged_events_latest.json"
FORWARD_REGISTRY_JSON = EDGE_DIR / "v28_successor_forward_registry_latest.json"

PREFLIGHT_CSV = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.csv"
PREFLIGHT_JSON = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.json"
PREFLIGHT_MD = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.md"

MIN_FREEZE_ROWS = 200
MIN_FREEZE_MARKETS = 40


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


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


def packet_group_complete(row: dict[str, Any], group: str) -> bool:
    return not row_group_missing(row, group)


def row_blockers(row: dict[str, Any], now_utc: datetime, any_forward_collection_candidate: bool) -> list[str]:
    blockers: list[str] = []
    close_ts = parse_ts(row.get("market_close_ts_utc"))
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    registered_ts = parse_ts(row.get("registered_utc"))
    if close_ts is None:
        blockers.append("missing_market_close_ts")
    elif now_utc >= close_ts:
        blockers.append("market_already_closed_now")
    if decision_ts is None or close_ts is None or decision_ts > close_ts:
        blockers.append("decision_not_pre_resolution")
    if not as_bool(row.get("is_pre_resolution_registered")):
        blockers.append("row_not_registered_pre_resolution")
    if registered_ts is not None and close_ts is not None and registered_ts > close_ts:
        blockers.append("staging_registration_not_before_close")
    if not as_bool(row.get("has_market_metadata")) and not packet_group_complete(row, "identity_and_clock"):
        blockers.append("missing_market_metadata")
    if not as_bool(row.get("has_top_book")) and not packet_group_complete(row, "market_and_book"):
        blockers.append("missing_top_book")
    if not as_bool(row.get("has_btc_state")) and not packet_group_complete(row, "btc_and_feed"):
        blockers.append("missing_btc_state")
    if not as_bool(row.get("has_v28_baseline")) and not packet_group_complete(row, "v28_baseline"):
        blockers.append("missing_v28_baseline")
    if not as_bool(row.get("has_candidate_prediction")) and not packet_group_complete(row, "candidate_prediction"):
        blockers.append("missing_candidate_prediction")
    if not any_forward_collection_candidate:
        blockers.append("no_candidate_manifest_allowed_for_forward_collection")
    if as_bool(row.get("has_settlement_label")):
        blockers.append("settlement_label_present_before_freeze_review")
    if as_bool(row.get("is_simulated")):
        blockers.append("simulated_row_not_freezable")
    if as_bool(row.get("is_diagnostic_only")):
        blockers.append("diagnostic_row_not_freezable")
    if as_bool(row.get("is_recomputed_after_resolution")) or as_bool(row.get("is_backfilled")):
        blockers.append("after_the_fact_row")
    blockers.extend(row_temporal_blockers(row))
    return blockers


def build(now_utc: datetime | None = None, source_csv: Path = PASSIVE_SNAPSHOTS_CSV) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    rows = read_csv_rows(source_csv)
    manifests = read_json(CANDIDATE_MANIFESTS_JSON) or []
    forward_registry = read_json(FORWARD_REGISTRY_JSON) or {}
    forward_collection_candidates = [
        manifest
        for manifest in manifests
        if as_bool(manifest.get("allowed_for_forward_collection"))
    ]
    any_forward_collection_candidate = bool(forward_collection_candidates)

    evaluations: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    open_input_rows = 0
    top_book_rows = 0
    registered_before_close_rows = 0
    for row in rows:
        blockers = row_blockers(row, now_utc, any_forward_collection_candidate)
        for blocker in blockers:
            blocker_counts[blocker] += 1
        close_ts = parse_ts(row.get("market_close_ts_utc"))
        if close_ts is not None and now_utc < close_ts:
            open_input_rows += 1
        if as_bool(row.get("has_top_book")):
            top_book_rows += 1
        if as_bool(row.get("is_pre_resolution_registered")):
            registered_before_close_rows += 1
        evaluations.append(
            {
                "row_id": row.get("row_id"),
                "market_ticker": row.get("market_ticker"),
                "side": row.get("side"),
                "decision_ts_utc": row.get("decision_ts_utc"),
                "market_close_ts_utc": row.get("market_close_ts_utc"),
                "registered_utc": row.get("registered_utc"),
                "freeze_ready": not blockers,
                "blockers": ";".join(blockers),
            }
        )

    freeze_ready_rows = [row for row in evaluations if row["freeze_ready"]]
    freeze_ready_markets = len({str(row.get("market_ticker") or "") for row in freeze_ready_rows if row.get("market_ticker")})
    readiness_blockers = set(blocker_counts)
    if len(freeze_ready_rows) < MIN_FREEZE_ROWS:
        readiness_blockers.add("insufficient_freeze_ready_rows")
    if freeze_ready_markets < MIN_FREEZE_MARKETS:
        readiness_blockers.add("insufficient_freeze_ready_markets")
    summary = {
        "generated_utc": now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "preflight_status": "ready_to_freeze" if freeze_ready_rows and not readiness_blockers else "blocked",
        "passive_rows": len(rows),
        "passive_markets": len({str(row.get("market_ticker") or "") for row in rows if row.get("market_ticker")}),
        "open_input_rows_now": open_input_rows,
        "rows_with_top_book": top_book_rows,
        "registered_before_close_rows": registered_before_close_rows,
        "freeze_ready_rows": len(freeze_ready_rows),
        "freeze_ready_markets": freeze_ready_markets,
        "minimum_freeze_rows": MIN_FREEZE_ROWS,
        "minimum_freeze_markets": MIN_FREEZE_MARKETS,
        "candidate_manifest_count": len(manifests),
        "forward_collection_candidate_count": len(forward_collection_candidates),
        "forward_collection_candidates": [manifest.get("candidate_id") for manifest in forward_collection_candidates],
        "forward_allowed_candidate_count": len(forward_collection_candidates),
        "forward_allowed_candidates": [manifest.get("candidate_id") for manifest in forward_collection_candidates],
        "forward_registry_status": forward_registry.get("registry_status"),
        "forward_registry_rows": forward_registry.get("row_count"),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "readiness_blockers": sorted(readiness_blockers),
        "inputs": {
            "passive_snapshots_csv": rel_path(source_csv),
            "candidate_manifests_json": rel_path(CANDIDATE_MANIFESTS_JSON),
            "forward_registry_json": rel_path(FORWARD_REGISTRY_JSON),
        },
        "outputs": {
            "csv": rel_path(PREFLIGHT_CSV),
            "json": rel_path(PREFLIGHT_JSON),
            "markdown": rel_path(PREFLIGHT_MD),
        },
    }
    return evaluations, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "market_ticker",
        "side",
        "decision_ts_utc",
        "market_close_ts_utc",
        "registered_utc",
        "freeze_ready",
        "blockers",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Freeze Preflight",
        "",
        "Research-only forward-freeze readiness check. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Preflight status: `{summary['preflight_status']}`",
        f"- Passive rows: `{summary['passive_rows']}`",
        f"- Passive markets: `{summary['passive_markets']}`",
        f"- Open input rows now: `{summary['open_input_rows_now']}`",
        f"- Registered-before-close rows: `{summary['registered_before_close_rows']}`",
        f"- Freeze-ready rows: `{summary['freeze_ready_rows']}`",
        f"- Freeze-ready markets: `{summary['freeze_ready_markets']}`",
        f"- Forward-collection candidates: `{summary['forward_collection_candidate_count']}`",
        f"- Forward registry rows: `{summary['forward_registry_rows']}`",
        "",
        "## Readiness Blockers",
        "",
    ]
    for blocker in summary["readiness_blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(
        [
            "",
            "## Row Blockers",
            "",
            "| blocker | rows |",
            "|---|---:|",
        ]
    )
    for blocker, count in summary["blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    sample = [row for row in rows if not row["freeze_ready"]][:20]
    lines.extend(
        [
            "",
            "## Blocked Row Sample",
            "",
            "| market | side | close | blockers |",
            "|---|---|---|---|",
        ]
    )
    for row in sample:
        lines.append(
            f"| `{row['market_ticker']}` | `{row['side']}` | `{row['market_close_ts_utc']}` | `{row['blockers']}` |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- A row can only freeze when it is still pre-resolution, has market/book/BTC/v28 state, has a frozen candidate prediction, and belongs to a forward-collection candidate manifest.",
            "- The current passive rows are useful staging inputs, but this preflight correctly keeps the frozen registry closed.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, PREFLIGHT_CSV)
    PREFLIGHT_JSON.write_text(json.dumps({"summary": summary, "rows": rows[:200]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(rows, summary, PREFLIGHT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write preflight artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--input-csv", type=Path, default=PASSIVE_SNAPSHOTS_CSV, help="Input staging/packet CSV to preflight.")
    args = parser.parse_args()

    rows, summary = build(source_csv=args.input_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "preflight_status": summary["preflight_status"],
                "passive_rows": summary["passive_rows"],
                "open_input_rows_now": summary["open_input_rows_now"],
                "freeze_ready_rows": summary["freeze_ready_rows"],
                "freeze_ready_markets": summary["freeze_ready_markets"],
                "readiness_blockers": summary["readiness_blockers"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
