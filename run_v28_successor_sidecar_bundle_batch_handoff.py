"""Batch sidecar input bundles into packet and freeze handoff artifacts.

Research-only. This scans serialized sidecar input bundle JSON files, validates
each bundle, materializes packet rows for ready bundles, then runs the same
non-promoting freeze handoff on the combined packet CSV. It is the broad-market
collection handoff: many markets and checkpoints can be dropped into a bundle
directory without touching live bot state, orders, thresholds, secrets, or
processes.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from collect_v28_successor_forward_packets import PACKET_FIELDS, packet_rows_from_input_bundle
from freeze_v28_successor_forward_candidates import FROZEN_FIELDS
from register_v28_successor_forward_predictions import REGISTRY_FIELDS
from run_v28_successor_forward_packet_freeze import build as build_freeze_handoff
from run_v28_successor_forward_packet_freeze import registry_rows_from_frozen
from validate_v28_successor_sidecar_input_bundle import build as build_bundle_contract


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEFAULT_BUNDLE_DIR = OUT_DIR / "sidecar_input_bundles"
BATCH_PACKETS_CSV = OUT_DIR / "sidecar_bundle_batch_packets_latest.csv"
BATCH_PACKETS_JSON = OUT_DIR / "sidecar_bundle_batch_packets_latest.json"
BATCH_FROZEN_CSV = OUT_DIR / "sidecar_bundle_batch_frozen_latest.csv"
BATCH_REGISTRY_CSV = OUT_DIR / "sidecar_bundle_batch_registry_latest.csv"
BATCH_HANDOFF_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_handoff_latest.json"
BATCH_HANDOFF_MD = EDGE_DIR / "v28_successor_sidecar_bundle_batch_handoff_latest.md"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


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


def discover_bundle_paths(bundle_dir: Path, explicit_inputs: list[Path] | None = None) -> list[Path]:
    if explicit_inputs:
        return sorted({path.resolve() for path in explicit_inputs})
    if not bundle_dir.exists():
        return []
    return sorted(path for path in bundle_dir.glob("*.json") if path.is_file())


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def packet_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(PACKET_FIELDS + [key for row in rows for key in row.keys()]))


def as_bool_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def frozen_semantic_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("market_ticker") or ""),
        str(row.get("row_id") or ""),
        str(row.get("candidate_id") or ""),
        str(row.get("side") or ""),
        str(row.get("decision_ts_utc") or ""),
    )


def existing_frozen_row_is_valid(row: dict[str, Any]) -> bool:
    if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction":
        return False
    frozen_ts = parse_ts(row.get("frozen_utc"))
    close_ts = parse_ts(row.get("market_close_ts_utc"))
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    if frozen_ts is None or close_ts is None or decision_ts is None:
        return False
    if frozen_ts >= close_ts:
        return False
    if decision_ts > close_ts:
        return False
    if not str(row.get("market_ticker") or "").startswith("KXBTC15M-"):
        return False
    if not str(row.get("frozen_prediction_id") or "").strip():
        return False
    return True


def merge_preserved_frozen_rows(
    new_rows: list[dict[str, Any]],
    existing_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    valid_existing = [row for row in existing_rows if existing_frozen_row_is_valid(row)]
    merged: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str, str, str]] = set()
    seen_ids: set[str] = set()
    invalid_existing_rows = len(existing_rows) - len(valid_existing)
    duplicate_existing_rows = 0
    duplicate_new_rows = 0

    for row in valid_existing:
        key = frozen_semantic_key(row)
        frozen_id = str(row.get("frozen_prediction_id") or "")
        if key in seen_keys or frozen_id in seen_ids:
            duplicate_existing_rows += 1
            continue
        merged.append(row)
        seen_keys.add(key)
        seen_ids.add(frozen_id)

    for row in new_rows:
        if not existing_frozen_row_is_valid(row):
            duplicate_new_rows += 1
            continue
        key = frozen_semantic_key(row)
        frozen_id = str(row.get("frozen_prediction_id") or "")
        if key in seen_keys or frozen_id in seen_ids:
            duplicate_new_rows += 1
            continue
        merged.append(row)
        seen_keys.add(key)
        seen_ids.add(frozen_id)

    return merged, {
        "existing_frozen_rows": len(existing_rows),
        "valid_existing_frozen_rows": len(valid_existing),
        "invalid_existing_frozen_rows": invalid_existing_rows,
        "duplicate_existing_rows": duplicate_existing_rows,
        "newly_frozen_rows": len(new_rows),
        "deduped_or_invalid_new_rows": duplicate_new_rows,
        "merged_frozen_rows": len(merged),
    }


V28_COMPONENT_FIELDS = [
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
]


def nonempty(value: Any) -> bool:
    return str(value if value is not None else "").strip() != ""


def enrich_preserved_frozen_rows_from_packets(
    frozen_rows: list[dict[str, Any]],
    packet_rows: list[dict[str, Any]],
) -> dict[str, int]:
    by_key = {frozen_semantic_key(row): row for row in packet_rows}
    enriched_rows = 0
    enriched_fields = 0
    for frozen in frozen_rows:
        packet = by_key.get(frozen_semantic_key(frozen))
        if not packet:
            continue
        row_enriched = False
        for field in V28_COMPONENT_FIELDS:
            if nonempty(frozen.get(field)) or not nonempty(packet.get(field)):
                continue
            frozen[field] = packet.get(field)
            row_enriched = True
            enriched_fields += 1
        if row_enriched:
            enriched_rows += 1
    return {
        "component_enriched_rows": enriched_rows,
        "component_enriched_fields": enriched_fields,
    }


def build(
    *,
    bundle_dir: Path = DEFAULT_BUNDLE_DIR,
    input_jsons: list[Path] | None = None,
    now_utc: datetime | None = None,
    packet_csv: Path = BATCH_PACKETS_CSV,
    preserve_existing_frozen: bool = False,
    existing_frozen_csv: Path = BATCH_FROZEN_CSV,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    bundle_paths = discover_bundle_paths(bundle_dir, input_jsons)
    bundle_reports: list[dict[str, Any]] = []
    packet_rows: list[dict[str, Any]] = []
    bundle_blockers: Counter[str] = Counter()

    for bundle_path in bundle_paths:
        bundle_report, bundle = build_bundle_contract(input_json=bundle_path)
        bundle_summary = bundle_report["summary"]
        compact = {
            "source_input": bundle_summary.get("source_input"),
            "bundle_status": bundle_summary.get("bundle_status"),
            "bundle_ready": bundle_summary.get("bundle_ready"),
            "market_ticker": bundle_summary.get("market_ticker"),
            "simulated": bundle_summary.get("simulated"),
            "diagnostic_only": bundle_summary.get("diagnostic_only"),
            "btc_history_rows": bundle_summary.get("btc_history_rows"),
            "forward_collection_candidate_count": bundle_summary.get("forward_collection_candidate_count"),
            "blocker_counts": bundle_summary.get("blocker_counts"),
        }
        bundle_reports.append(compact)
        for blocker, count in (bundle_summary.get("blocker_counts") or {}).items():
            bundle_blockers[str(blocker)] += int(count)
        if not bundle_summary.get("bundle_ready"):
            continue
        packet_rows.extend(
            packet_rows_from_input_bundle(
                input_bundle=bundle,
                source_file=str(bundle_summary.get("source_input") or rel_path(bundle_path)),
                source_line_or_offset="bundle",
            )
        )

    write_csv_rows(packet_rows, packet_fieldnames(packet_rows), packet_csv)
    freeze_report, newly_frozen_rows, newly_registry_rows = build_freeze_handoff(source_csv=packet_csv, now_utc=now_utc)
    freeze_summary = freeze_report["summary"]
    existing_frozen_rows = read_csv_rows(existing_frozen_csv) if preserve_existing_frozen else []
    if preserve_existing_frozen:
        frozen_rows, preservation_counts = merge_preserved_frozen_rows(newly_frozen_rows, existing_frozen_rows)
        preservation_counts.update(enrich_preserved_frozen_rows_from_packets(frozen_rows, packet_rows))
        registry_rows = registry_rows_from_frozen(frozen_rows)
    else:
        frozen_rows = newly_frozen_rows
        registry_rows = newly_registry_rows
        preservation_counts = {
            "existing_frozen_rows": 0,
            "valid_existing_frozen_rows": 0,
            "invalid_existing_frozen_rows": 0,
            "duplicate_existing_rows": 0,
            "newly_frozen_rows": len(newly_frozen_rows),
            "deduped_or_invalid_new_rows": 0,
            "merged_frozen_rows": len(frozen_rows),
            "component_enriched_rows": 0,
            "component_enriched_fields": 0,
        }

    simulated_rows = sum(1 for row in packet_rows if as_bool_text(row.get("is_simulated")))
    diagnostic_rows = sum(1 for row in packet_rows if as_bool_text(row.get("is_diagnostic_only")))
    packet_markets = len({row.get("market_ticker") for row in packet_rows if row.get("market_ticker")})
    registry_markets = len({row.get("market_ticker") for row in registry_rows if row.get("market_ticker")})
    blockers: list[str] = []
    if not bundle_paths:
        blockers.append("no_input_bundle_files")
    if not packet_rows:
        blockers.append("no_packet_rows_from_ready_bundles")
    if simulated_rows:
        blockers.append("packet_rows_contain_simulated_rows")
    if diagnostic_rows:
        blockers.append("packet_rows_contain_diagnostic_rows")
    if len(registry_rows) < MIN_FORWARD_ROWS:
        blockers.append("frozen_registry_below_row_floor")
    if registry_markets < MIN_FORWARD_MARKETS:
        blockers.append("frozen_registry_below_market_floor")
    if not frozen_rows:
        blockers.extend(str(blocker) for blocker in freeze_summary.get("blockers", []))
    elif preserve_existing_frozen and not newly_frozen_rows:
        blockers.append("current_replay_produced_no_new_frozen_rows_existing_ledger_preserved")
    blockers.extend(f"bundle_blocker:{blocker}" for blocker in bundle_blockers)

    if not bundle_paths:
        status = "blocked_no_input_bundles"
    elif simulated_rows or diagnostic_rows:
        status = "blocked_non_promotable_bundle_rows"
    elif not frozen_rows:
        status = "blocked_no_frozen_rows"
    elif len(registry_rows) < MIN_FORWARD_ROWS or registry_markets < MIN_FORWARD_MARKETS:
        status = "frozen_batch_handoff_below_coverage_floor"
    else:
        status = "frozen_batch_handoff_ready_for_settlement_labels"

    summary = {
        "generated_utc": now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "batch_handoff_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "sidecar bundle batch handoff is not promotion; labels, source contract, forward evidence scoring, coverage, and promotion verifier are still required",
        },
        "bundle_dir": rel_path(bundle_dir),
        "input_bundle_files": len(bundle_paths),
        "ready_bundle_files": sum(1 for row in bundle_reports if row.get("bundle_ready")),
        "blocked_bundle_files": sum(1 for row in bundle_reports if not row.get("bundle_ready")),
        "bundle_status_counts": dict(sorted(Counter(str(row.get("bundle_status")) for row in bundle_reports).items())),
        "bundle_blocker_counts": dict(sorted(bundle_blockers.items())),
        "packet_rows": {
            "csv": rel_path(packet_csv),
            "rows": len(packet_rows),
            "markets": packet_markets,
            "simulated_rows": simulated_rows,
            "diagnostic_rows": diagnostic_rows,
        },
        "freeze_handoff": {
            "handoff_status": freeze_summary.get("handoff_status"),
            "packet_ready_rows": (freeze_summary.get("packet_contract") or {}).get("packet_ready_rows"),
            "freeze_ready_rows": (freeze_summary.get("preflight") or {}).get("freeze_ready_rows"),
            "newly_frozen_prediction_rows": len(newly_frozen_rows),
            "frozen_prediction_rows": len(frozen_rows),
            "registry_rows": len(registry_rows),
            "registry_markets": registry_markets,
            "current_attempt_frozen_prediction_rows": (freeze_summary.get("freeze") or {}).get("frozen_prediction_rows"),
            "current_attempt_registry_rows": (freeze_summary.get("registry") or {}).get("row_count"),
            "current_attempt_registry_markets": (freeze_summary.get("registry") or {}).get("market_count"),
            "current_attempt_blockers": freeze_summary.get("blockers"),
        },
        "preservation": {
            "enabled": preserve_existing_frozen,
            "existing_frozen_csv": rel_path(existing_frozen_csv),
            **preservation_counts,
        },
        "blockers": sorted(set(blockers)),
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "outputs": {
            "packets_csv": rel_path(packet_csv),
            "packets_json": rel_path(BATCH_PACKETS_JSON),
            "frozen_csv": rel_path(BATCH_FROZEN_CSV),
            "registry_csv": rel_path(BATCH_REGISTRY_CSV),
            "handoff_json": rel_path(BATCH_HANDOFF_JSON),
            "handoff_md": rel_path(BATCH_HANDOFF_MD),
        },
    }
    return {"summary": summary, "bundles": bundle_reports, "freeze_handoff": freeze_report}, packet_rows, frozen_rows, registry_rows


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Bundle Batch Handoff",
        "",
        "Research-only batch handoff for broad sidecar bundle collection. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Batch handoff status: `{summary['batch_handoff_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Bundle directory: `{summary['bundle_dir']}`",
        f"- Input bundle files: `{summary['input_bundle_files']}`",
        f"- Ready bundle files: `{summary['ready_bundle_files']}`",
        f"- Packet rows: `{summary['packet_rows']['rows']}`",
        f"- Packet markets: `{summary['packet_rows']['markets']}`",
        f"- Frozen prediction rows: `{summary['freeze_handoff']['frozen_prediction_rows']}`",
        f"- Registry rows: `{summary['freeze_handoff']['registry_rows']}`",
        f"- Registry markets: `{summary['freeze_handoff']['registry_markets']}`",
        "",
        "## Blockers",
        "",
    ]
    for blocker in summary["blockers"]:
        lines.append(f"- `{blocker}`")
    if not summary["blockers"]:
        lines.append("- None recorded by this handoff.")
    lines.extend(
        [
            "",
            "## Bundle Status Counts",
            "",
            "| status | files |",
            "|---|---:|",
        ]
    )
    for status, count in summary["bundle_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Drop real pre-close sidecar input bundle JSON files into the bundle directory, then rerun this handoff.",
            "- The CLI preserves valid existing frozen batch rows by default so post-close refreshes cannot erase pre-close evidence.",
            "- Empty, simulated, diagnostic, after-the-fact, or label-contaminated batches remain non-promotable.",
            "- Even successful frozen batch rows still need post-resolution label join, source contract, forward evidence scoring, and promotion verification.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(
    report: dict[str, Any],
    packet_rows: list[dict[str, Any]],
    frozen_rows: list[dict[str, Any]],
    registry_rows: list[dict[str, Any]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_PACKETS_JSON.write_text(json.dumps({"rows": packet_rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(frozen_rows, FROZEN_FIELDS, BATCH_FROZEN_CSV)
    write_csv_rows(registry_rows, REGISTRY_FIELDS, BATCH_REGISTRY_CSV)
    BATCH_HANDOFF_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, BATCH_HANDOFF_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE_DIR, help="Directory containing sidecar input bundle JSON files.")
    parser.add_argument("--input-json", action="append", type=Path, default=None, help="Explicit sidecar input bundle JSON. Can be supplied multiple times.")
    parser.add_argument("--now-utc", default="", help="Override current UTC timestamp for deterministic pre-close runs.")
    parser.add_argument(
        "--no-preserve-existing",
        action="store_true",
        help="Replace latest frozen rows instead of preserving the existing valid pre-close frozen ledger.",
    )
    parser.add_argument("--write", action="store_true", help="Write sidecar bundle batch handoff artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report, packet_rows, frozen_rows, registry_rows = build(
        bundle_dir=args.bundle_dir,
        input_jsons=args.input_json,
        now_utc=now_utc,
        preserve_existing_frozen=not args.no_preserve_existing,
    )
    if args.write and not args.dry_run:
        write_outputs(report, packet_rows, frozen_rows, registry_rows)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "batch_handoff_status": summary["batch_handoff_status"],
                "input_bundle_files": summary["input_bundle_files"],
                "packet_rows": summary["packet_rows"]["rows"],
                "frozen_prediction_rows": summary["freeze_handoff"]["frozen_prediction_rows"],
                "registry_rows": summary["freeze_handoff"]["registry_rows"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
