"""Run sidecar input bundle through packet collection and freeze handoff.

Research-only. This is a one-command bridge from a serialized sidecar input
bundle to packet rows, packet validation, freeze preflight, frozen prediction
handoff rows, and registry-shaped handoff rows. It does not touch live bot
state, orders, thresholds, secrets, or processes, and it never grants
promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from collect_v28_successor_forward_packets import PACKET_FIELDS, packet_rows_from_input_bundle
from run_v28_successor_forward_packet_freeze import build as build_freeze_handoff
from validate_v28_successor_sidecar_input_bundle import build as build_bundle_contract


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PACKETS_CSV = OUT_DIR / "sidecar_bundle_freeze_handoff_packets_latest.csv"
PACKETS_JSON = OUT_DIR / "sidecar_bundle_freeze_handoff_packets_latest.json"
HANDOFF_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_freeze_handoff_latest.json"
HANDOFF_MD = EDGE_DIR / "v28_successor_sidecar_bundle_freeze_handoff_latest.md"


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


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(PACKET_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def materialize_packet_rows(
    *,
    bundle: dict[str, Any],
    bundle_ready: bool,
    packet_csv: Path,
    source_input: str,
) -> list[dict[str, Any]]:
    if not bundle_ready:
        write_csv_rows([], packet_csv)
        return []
    rows = packet_rows_from_input_bundle(
        input_bundle=bundle,
        source_file=source_input,
        source_line_or_offset="bundle",
    )
    write_csv_rows(rows, packet_csv)
    return rows


def build(
    *,
    input_json: Path | None = None,
    now_utc: datetime | None = None,
    packet_csv: Path = PACKETS_CSV,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    bundle_report, bundle = build_bundle_contract(input_json=input_json)
    bundle_summary = bundle_report["summary"]
    source_input = str(bundle_summary.get("source_input") or "generated_template_demo")
    packet_rows = materialize_packet_rows(
        bundle=bundle,
        bundle_ready=bool(bundle_summary.get("bundle_ready")),
        packet_csv=packet_csv,
        source_input=source_input,
    )
    freeze_report, frozen_rows, registry_rows = build_freeze_handoff(source_csv=packet_csv, now_utc=now_utc)
    freeze_summary = freeze_report["summary"]
    simulated_rows = sum(1 for row in packet_rows if str(row.get("is_simulated")).strip().lower() == "true")
    diagnostic_rows = sum(1 for row in packet_rows if str(row.get("is_diagnostic_only")).strip().lower() == "true")
    blockers: list[str] = []
    if not bundle_summary.get("bundle_ready"):
        blockers.append("sidecar_input_bundle_not_ready")
    if simulated_rows:
        blockers.append("packet_rows_contain_simulated_rows")
    if diagnostic_rows:
        blockers.append("packet_rows_contain_diagnostic_rows")
    blockers.extend(str(blocker) for blocker in freeze_summary.get("blockers", []))
    if not frozen_rows:
        status = "blocked_no_frozen_rows"
    elif freeze_summary.get("handoff_status") == "frozen_handoff_ready_for_settlement_labels":
        status = "bundle_handoff_ready_for_settlement_labels"
    else:
        status = str(freeze_summary.get("handoff_status") or "bundle_handoff_built")
    if simulated_rows or diagnostic_rows or not bundle_summary.get("bundle_ready"):
        status = "blocked_non_promotable_bundle_rows"

    summary = {
        "generated_utc": now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "bundle_handoff_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "sidecar bundle freeze handoff is not promotion; labels, source contract, forward evidence scoring, coverage, and promotion verifier are still required",
        },
        "source_input": source_input,
        "bundle": {
            "bundle_status": bundle_summary.get("bundle_status"),
            "bundle_ready": bundle_summary.get("bundle_ready"),
            "simulated": bundle_summary.get("simulated"),
            "diagnostic_only": bundle_summary.get("diagnostic_only"),
            "blocker_counts": bundle_summary.get("blocker_counts"),
        },
        "packet_rows": {
            "csv": rel_path(packet_csv),
            "rows": len(packet_rows),
            "markets": len({row.get("market_ticker") for row in packet_rows if row.get("market_ticker")}),
            "simulated_rows": simulated_rows,
            "diagnostic_rows": diagnostic_rows,
        },
        "freeze_handoff": {
            "handoff_status": freeze_summary.get("handoff_status"),
            "packet_ready_rows": (freeze_summary.get("packet_contract") or {}).get("packet_ready_rows"),
            "freeze_ready_rows": (freeze_summary.get("preflight") or {}).get("freeze_ready_rows"),
            "frozen_prediction_rows": (freeze_summary.get("freeze") or {}).get("frozen_prediction_rows"),
            "registry_rows": (freeze_summary.get("registry") or {}).get("row_count"),
            "blockers": freeze_summary.get("blockers"),
        },
        "blockers": sorted(set(blockers)),
        "outputs": {
            "packets_csv": rel_path(packet_csv),
            "packets_json": rel_path(PACKETS_JSON),
            "handoff_json": rel_path(HANDOFF_JSON),
            "handoff_md": rel_path(HANDOFF_MD),
        },
    }
    return {"summary": summary, "bundle_contract": bundle_report, "freeze_handoff": freeze_report}, packet_rows, frozen_rows, registry_rows


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Bundle Freeze Handoff",
        "",
        "Research-only one-command handoff from sidecar input bundle to packet rows and freeze handoff. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Bundle handoff status: `{summary['bundle_handoff_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Source input: `{summary['source_input']}`",
        f"- Bundle status: `{summary['bundle']['bundle_status']}`",
        f"- Bundle ready: `{summary['bundle']['bundle_ready']}`",
        f"- Packet rows: `{summary['packet_rows']['rows']}`",
        f"- Packet markets: `{summary['packet_rows']['markets']}`",
        f"- Simulated packet rows: `{summary['packet_rows']['simulated_rows']}`",
        f"- Diagnostic packet rows: `{summary['packet_rows']['diagnostic_rows']}`",
        f"- Freeze handoff status: `{summary['freeze_handoff']['handoff_status']}`",
        f"- Frozen prediction rows: `{summary['freeze_handoff']['frozen_prediction_rows']}`",
        f"- Registry rows: `{summary['freeze_handoff']['registry_rows']}`",
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
            "## Read",
            "",
            "- Template/demo bundles are intentionally non-promotable.",
            "- Real bundles can produce frozen handoff rows only if captured before close and free of labels, simulation flags, and after-the-fact sources.",
            "- Even successful frozen handoff rows still need post-resolution label join, source contract, forward evidence scoring, and promotion verification.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], packet_rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    PACKETS_JSON.write_text(json.dumps({"rows": packet_rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    HANDOFF_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, HANDOFF_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, default=None, help="Optional sidecar input bundle JSON. Defaults to generated synthetic template.")
    parser.add_argument("--now-utc", default="", help="Override current UTC timestamp for deterministic pre-close runs.")
    parser.add_argument("--write", action="store_true", help="Write sidecar bundle freeze handoff artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report, packet_rows, _frozen_rows, _registry_rows = build(input_json=args.input_json, now_utc=now_utc)
    if args.write and not args.dry_run:
        write_outputs(report, packet_rows)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "bundle_handoff_status": summary["bundle_handoff_status"],
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
