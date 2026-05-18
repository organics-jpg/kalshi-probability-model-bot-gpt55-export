"""Register frozen forward predictions for v28 successor candidates.

Research-only scaffold. It writes a forward registry only for rows already
frozen before resolution by freeze_v28_successor_forward_candidates.py. The
current workspace still has zero frozen rows, so the expected output today is an
empty registry with a blocked verdict.

This script never reads live state, never places orders, and never mutates the
live bot. It exists to make the promotion path explicit and auditable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

FEATURES_CSV = OUT_DIR / "features_latest.csv"
CANDIDATE_MANIFEST_JSON = OUT_DIR / "candidate_manifests_latest.json"
CANDIDATE_PREDICTIONS_CSV = OUT_DIR / "candidate_predictions_latest.csv"
FROZEN_FORWARD_CSV = OUT_DIR / "frozen_forward_predictions_latest.csv"
PASSIVE_FORWARD_SNAPSHOTS_JSON = EDGE_DIR / "v28_successor_passive_forward_snapshots_latest.json"
FORWARD_PREFLIGHT_JSON = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.json"
FROZEN_FORWARD_SUMMARY_JSON = EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.json"
FORWARD_PACKET_CONTRACT_JSON = EDGE_DIR / "v28_successor_forward_packet_contract_latest.json"

FORWARD_REGISTRY_CSV = OUT_DIR / "forward_registry_latest.csv"
FORWARD_REGISTRY_JSON = OUT_DIR / "forward_registry_latest.json"
FORWARD_REGISTRY_SUMMARY_JSON = EDGE_DIR / "v28_successor_forward_registry_latest.json"
FORWARD_REGISTRY_SUMMARY_MD = EDGE_DIR / "v28_successor_forward_registry_latest.md"


REGISTRY_FIELDS = [
    "registry_id",
    "registered_utc",
    "frozen_prediction_id",
    "frozen_utc",
    "row_id",
    "market_ticker",
    "market_close_ts_utc",
    "decision_ts_utc",
    "candidate_id",
    "model_hash",
    "model_type",
    "model_track",
    "candidate_p_yes",
    "candidate_fair_yes_cents",
    "candidate_fair_no_cents",
    "v28_p_yes",
    "v28_p_anchor",
    "v28_p_static_boundary_field",
    "v28_p_recent_transport",
    "v28_p_long_transport",
    "v28_transport_recent_n",
    "v28_transport_long_n",
    "side",
    "candidate_fair_side_cents",
    "ask_cents",
    "candidate_edge_cents",
    "source_status",
]


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


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_registry_rows(frozen_csv: Path = FROZEN_FORWARD_CSV) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    features = read_csv_rows(FEATURES_CSV)
    predictions = read_csv_rows(CANDIDATE_PREDICTIONS_CSV)
    frozen_predictions = read_csv_rows(frozen_csv)
    manifests = read_json(CANDIDATE_MANIFEST_JSON) or []
    passive_snapshots = read_json(PASSIVE_FORWARD_SNAPSHOTS_JSON) or {}
    forward_preflight = read_json(FORWARD_PREFLIGHT_JSON) or {}
    forward_preflight_summary = forward_preflight.get("summary", {}) if isinstance(forward_preflight, dict) else {}
    frozen_forward = read_json(FROZEN_FORWARD_SUMMARY_JSON) or {}
    packet_contract = read_json(FORWARD_PACKET_CONTRACT_JSON) or {}
    packet_summary = packet_contract.get("summary", {}) if isinstance(packet_contract, dict) else {}
    forward_row_ids = {
        str(row.get("row_id"))
        for row in features
        if as_bool(row.get("allowed_for_forward_promotion"))
    }
    registered_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    registry_rows: list[dict[str, Any]] = []
    source_status_counts: dict[str, int] = {}
    for frozen in frozen_predictions:
        source_status = str(frozen.get("source_status") or "")
        source_status_counts[source_status] = source_status_counts.get(source_status, 0) + 1
        if source_status != "frozen_pre_resolution_prediction":
            continue
        candidate_id = str(frozen.get("candidate_id") or "")
        payload = {
            "registry_id": stable_hash([frozen.get("frozen_prediction_id"), frozen.get("row_id"), candidate_id]),
            "registered_utc": frozen.get("frozen_utc") or registered_utc,
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
        registry_rows.append(payload)

    registry_markets = len({str(row.get("market_ticker") or "") for row in registry_rows if row.get("market_ticker")})
    promotion_ready = len(registry_rows) >= 200 and registry_markets >= 40
    summary = {
        "generated_utc": registered_utc,
        "builder_script": Path(__file__).name,
        "registry_status": "active_empty_no_forward_rows" if not registry_rows else "active",
        "promotion_ready": promotion_ready,
        "row_count": len(registry_rows),
        "market_count": registry_markets,
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "feature_forward_row_ids": len(forward_row_ids),
        "candidate_count": len(manifests),
        "forward_collection_candidate_count": sum(1 for manifest in manifests if as_bool(manifest.get("allowed_for_forward_collection"))),
        "forward_collection_candidates": [
            manifest.get("candidate_id")
            for manifest in manifests
            if as_bool(manifest.get("allowed_for_forward_collection"))
        ],
        "passive_forward_staging": {
            "audit_json": rel_path(PASSIVE_FORWARD_SNAPSHOTS_JSON),
            "rows": passive_snapshots.get("row_count") if isinstance(passive_snapshots, dict) else None,
            "markets": passive_snapshots.get("market_count") if isinstance(passive_snapshots, dict) else None,
            "registered_pre_resolution_rows": passive_snapshots.get("registered_pre_resolution_rows") if isinstance(passive_snapshots, dict) else None,
            "forward_promotion_rows": passive_snapshots.get("forward_promotion_rows") if isinstance(passive_snapshots, dict) else None,
            "missing_counts": passive_snapshots.get("missing_counts") if isinstance(passive_snapshots, dict) else None,
        },
        "forward_freeze_preflight": {
            "audit_json": rel_path(FORWARD_PREFLIGHT_JSON),
            "preflight_status": forward_preflight_summary.get("preflight_status"),
            "open_input_rows_now": forward_preflight_summary.get("open_input_rows_now"),
            "freeze_ready_rows": forward_preflight_summary.get("freeze_ready_rows"),
            "freeze_ready_markets": forward_preflight_summary.get("freeze_ready_markets"),
            "readiness_blockers": forward_preflight_summary.get("readiness_blockers"),
        },
        "frozen_forward_predictions": {
            "summary_json": rel_path(FROZEN_FORWARD_SUMMARY_JSON),
            "freeze_status": frozen_forward.get("freeze_status") if isinstance(frozen_forward, dict) else None,
            "frozen_prediction_rows": frozen_forward.get("frozen_prediction_rows") if isinstance(frozen_forward, dict) else None,
            "frozen_prediction_markets": frozen_forward.get("frozen_prediction_markets") if isinstance(frozen_forward, dict) else None,
            "forward_collection_candidate_count": frozen_forward.get("forward_collection_candidate_count") if isinstance(frozen_forward, dict) else None,
            "forward_allowed_candidate_count": frozen_forward.get("forward_allowed_candidate_count") if isinstance(frozen_forward, dict) else None,
        },
        "forward_packet_contract": {
            "audit_json": rel_path(FORWARD_PACKET_CONTRACT_JSON),
            "packet_status": packet_summary.get("packet_status"),
            "packet_ready_rows": packet_summary.get("packet_ready_rows"),
            "packet_ready_markets": packet_summary.get("packet_ready_markets"),
            "group_missing_counts": packet_summary.get("group_missing_counts"),
        },
        "inputs": {
            "frozen_forward_csv": rel_path(frozen_csv),
            "frozen_forward_hash": sha256_file(frozen_csv),
            "features_csv": rel_path(FEATURES_CSV),
            "features_hash": sha256_file(FEATURES_CSV),
            "candidate_predictions_csv": rel_path(CANDIDATE_PREDICTIONS_CSV),
            "candidate_predictions_hash": sha256_file(CANDIDATE_PREDICTIONS_CSV),
            "candidate_manifest_json": rel_path(CANDIDATE_MANIFEST_JSON),
            "candidate_manifest_hash": sha256_file(CANDIDATE_MANIFEST_JSON),
        },
        "outputs": {
            "forward_registry_csv": rel_path(FORWARD_REGISTRY_CSV),
            "forward_registry_json": rel_path(FORWARD_REGISTRY_JSON),
            "forward_registry_summary_json": rel_path(FORWARD_REGISTRY_SUMMARY_JSON),
            "forward_registry_summary_md": rel_path(FORWARD_REGISTRY_SUMMARY_MD),
        },
        "blockers": [
            "frozen forward prediction ledger is empty",
            "no source_status=frozen_pre_resolution_prediction rows are available to register",
            "passive forward snapshots lack BTC state, v28 baseline, candidate predictions, and settlement labels",
            "forward-freeze preflight has zero freeze-ready rows",
            "forward packet contract has zero packet-ready rows",
        ]
        if not registry_rows
        else (
            [
                "frozen registry exists but is below forward evidence coverage floors",
                "settled label join and forward evidence scoring are still required before promotion",
            ]
            if not promotion_ready
            else ["settled label join and forward evidence scoring are still required before promotion"]
        ),
    }
    return registry_rows, summary


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Registry",
        "",
        "Research-only frozen-prediction registry scaffold. It does not touch live bot state, orders, thresholds, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Registry status: `{summary['registry_status']}`",
        f"- Registry rows: `{summary['row_count']}`",
        f"- Registry markets: `{summary['market_count']}`",
        f"- Feature rows eligible for forward promotion: `{summary['feature_forward_row_ids']}`",
        f"- Candidate manifests: `{summary['candidate_count']}`",
        f"- Forward-collection candidates: `{summary['forward_collection_candidate_count']}`",
        f"- Passive staging rows: `{summary['passive_forward_staging']['rows']}`",
        f"- Passive staging registered before close: `{summary['passive_forward_staging']['registered_pre_resolution_rows']}`",
        f"- Forward-freeze preflight status: `{summary['forward_freeze_preflight']['preflight_status']}`",
        f"- Freeze-ready rows: `{summary['forward_freeze_preflight']['freeze_ready_rows']}`",
        f"- Frozen prediction rows: `{summary['frozen_forward_predictions']['frozen_prediction_rows']}`",
        f"- Packet-ready rows: `{summary['forward_packet_contract']['packet_ready_rows']}`",
        f"- Promotion ready: `{summary['promotion_ready']}`",
        "",
        "## Inputs",
        "",
        f"- Frozen forward predictions: `{summary['inputs']['frozen_forward_csv']}`",
        f"- Features: `{summary['inputs']['features_csv']}`",
        f"- Candidate predictions: `{summary['inputs']['candidate_predictions_csv']}`",
        f"- Candidate manifests: `{summary['inputs']['candidate_manifest_json']}`",
        "",
        "## Blockers",
        "",
    ]
    if summary["blockers"]:
        for blocker in summary["blockers"]:
            lines.append(f"- {blocker}.")
    else:
        lines.append("- None recorded by this registry scaffold.")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This file is the handoff point for future pre-resolution predictions.",
            "- The current run correctly registers zero predictions because every current row is diagnostic/posthoc.",
            "- Promotion remains impossible until rows are frozen before settlement and later scored after settlement.",
            "",
            "## Outputs",
            "",
            f"- Registry CSV: `{summary['outputs']['forward_registry_csv']}`",
            f"- Registry JSON: `{summary['outputs']['forward_registry_json']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, FORWARD_REGISTRY_CSV)
    FORWARD_REGISTRY_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FORWARD_REGISTRY_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, FORWARD_REGISTRY_SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register v28 successor forward predictions.")
    parser.add_argument("--write", action="store_true", help="Write registry artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build registry in memory only.")
    parser.add_argument("--frozen-csv", type=Path, default=FROZEN_FORWARD_CSV, help="Frozen prediction CSV to register.")
    args = parser.parse_args()

    rows, summary = build_registry_rows(frozen_csv=args.frozen_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "registry_status": summary["registry_status"],
                "row_count": summary["row_count"],
                "feature_forward_row_ids": summary["feature_forward_row_ids"],
                "promotion_ready": summary["promotion_ready"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
