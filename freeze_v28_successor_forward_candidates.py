"""Freeze v28 successor forward candidate predictions when rows are ready.

Research-only. This is the strict handoff from passive staging/preflight into a
frozen forward prediction ledger. It refuses to freeze rows unless all required
pre-resolution inputs are already present and at least one candidate manifest is
explicitly allowed for forward collection.

Current expected output is an empty ledger, because passive rows lack BTC state,
v28 baseline, candidate predictions, and pre-resolution freeze readiness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_v28_successor_forward_packet import row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PASSIVE_SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"
CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_logged_events_latest.json"
FORWARD_PREFLIGHT_JSON = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.json"

FROZEN_CSV = OUT_DIR / "frozen_forward_predictions_latest.csv"
FROZEN_JSON = OUT_DIR / "frozen_forward_predictions_latest.json"
FROZEN_SUMMARY_JSON = EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.json"
FROZEN_SUMMARY_MD = EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.md"

FROZEN_FIELDS = [
    "frozen_prediction_id",
    "frozen_utc",
    "row_id",
    "market_ticker",
    "market_close_ts_utc",
    "decision_ts_utc",
    "side",
    "strike",
    "seconds_to_close",
    "candidate_id",
    "model_hash",
    "model_type",
    "model_track",
    "candidate_p_yes",
    "candidate_fair_yes_cents",
    "candidate_fair_no_cents",
    "candidate_fair_side_cents",
    "v28_p_yes",
    "v28_fair_yes_cents",
    "v28_fair_no_cents",
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
    "v28_d_sigma",
    "v28_sigma_t_dollars",
    "ask_cents",
    "book_implied_yes_from_side_ask",
    "candidate_edge_cents",
    "source_status",
]


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


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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


def candidate_is_forward_allowed(manifest: dict[str, Any]) -> bool:
    return as_bool(manifest.get("allowed_for_forward_collection"))


def row_candidate_id(row: dict[str, Any]) -> str:
    return str(row.get("candidate_id") or "").strip()


def row_candidate_allowed(row: dict[str, Any], forward_allowed_candidates: list[dict[str, Any]]) -> bool:
    candidate_id = row_candidate_id(row)
    if not candidate_id:
        return True
    allowed_ids = {str(manifest.get("candidate_id") or "").strip() for manifest in forward_allowed_candidates}
    return candidate_id in allowed_ids


def row_manifest_applicable(row: dict[str, Any], candidate_id: str) -> bool:
    if as_float(row.get(f"{candidate_id}_p_yes")) is not None:
        return True
    row_level_candidate_id = row_candidate_id(row)
    return not row_level_candidate_id or row_level_candidate_id == candidate_id


def row_manifest_p_yes(row: dict[str, Any], candidate_id: str) -> float | None:
    wide_value = as_float(row.get(f"{candidate_id}_p_yes"))
    if wide_value is not None:
        return wide_value
    if row_candidate_id(row) == candidate_id:
        return as_float(row.get("candidate_p_yes"))
    return None


def packet_group_complete(row: dict[str, Any], group: str) -> bool:
    return not row_group_missing(row, group)


def row_freeze_blockers(row: dict[str, Any], now_utc: datetime, forward_allowed_candidates: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    close_ts = parse_ts(row.get("market_close_ts_utc"))
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    if close_ts is None:
        blockers.append("missing_market_close_ts")
    elif now_utc >= close_ts:
        blockers.append("market_already_closed_now")
    if decision_ts is None or close_ts is None or decision_ts > close_ts:
        blockers.append("decision_not_pre_resolution")
    if not as_bool(row.get("is_pre_resolution")):
        blockers.append("row_not_marked_pre_resolution")
    if not as_bool(row.get("is_pre_resolution_registered")):
        blockers.append("row_not_registered_pre_resolution")
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
    if not forward_allowed_candidates:
        blockers.append("no_forward_collection_candidate_manifest")
    elif not row_candidate_allowed(row, forward_allowed_candidates):
        blockers.append("row_candidate_not_forward_collection_allowed")
    if as_bool(row.get("has_settlement_label")):
        blockers.append("settlement_label_present_before_freeze")
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
    frozen_utc = now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    passive_rows = read_csv_rows(source_csv)
    manifests = read_json(CANDIDATE_MANIFESTS_JSON) or []
    preflight = read_json(FORWARD_PREFLIGHT_JSON) or {}
    preflight_summary = preflight.get("summary", {}) if isinstance(preflight, dict) else {}
    forward_allowed_candidates = [manifest for manifest in manifests if candidate_is_forward_allowed(manifest)]

    blocker_counts: dict[str, int] = {}
    freeze_ready_input_rows = 0
    frozen_rows: list[dict[str, Any]] = []

    for row in passive_rows:
        blockers = row_freeze_blockers(row, now_utc, forward_allowed_candidates)
        for blocker in blockers:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
        if blockers:
            continue
        freeze_ready_input_rows += 1
        for manifest in forward_allowed_candidates:
            candidate_id = str(manifest.get("candidate_id") or "")
            if not row_manifest_applicable(row, candidate_id):
                continue
            p_yes = row_manifest_p_yes(row, candidate_id)
            if p_yes is None:
                blocker_counts["candidate_prediction_field_missing_by_id"] = blocker_counts.get("candidate_prediction_field_missing_by_id", 0) + 1
                continue
            ask_cents = as_float(row.get("ask_cents"))
            side = str(row.get("side") or "").lower()
            fair_yes = 100.0 * p_yes
            fair_no = 100.0 * (1.0 - p_yes)
            fair_side = fair_yes if side == "yes" else fair_no if side == "no" else None
            edge = None if fair_side is None or ask_cents is None else fair_side - ask_cents
            frozen_rows.append(
                {
                    "frozen_prediction_id": stable_hash([row.get("row_id"), candidate_id, frozen_utc]),
                    "frozen_utc": frozen_utc,
                    "row_id": row.get("row_id"),
                    "market_ticker": row.get("market_ticker"),
                    "market_close_ts_utc": row.get("market_close_ts_utc"),
                    "decision_ts_utc": row.get("decision_ts_utc"),
                    "side": side,
                    "strike": row.get("strike"),
                    "seconds_to_close": row.get("seconds_to_close"),
                    "candidate_id": candidate_id,
                    "model_hash": manifest.get("model_hash"),
                    "model_type": manifest.get("model_type"),
                    "model_track": manifest.get("model_track"),
                    "candidate_p_yes": p_yes,
                    "candidate_fair_yes_cents": fair_yes,
                    "candidate_fair_no_cents": fair_no,
                    "candidate_fair_side_cents": fair_side,
                    "v28_p_yes": row.get("v28_p_yes"),
                    "v28_fair_yes_cents": row.get("v28_fair_yes_cents"),
                    "v28_fair_no_cents": row.get("v28_fair_no_cents"),
                    "v28_p_anchor": row.get("v28_p_anchor"),
                    "v28_p_static_boundary_field": row.get("v28_p_static_boundary_field"),
                    "v28_p_recent_transport": row.get("v28_p_recent_transport"),
                    "v28_p_long_transport": row.get("v28_p_long_transport"),
                    "v28_edge_gate": row.get("v28_edge_gate"),
                    "v28_static_gate": row.get("v28_static_gate"),
                    "v28_arrow": row.get("v28_arrow"),
                    "v28_volshock": row.get("v28_volshock"),
                    "v28_transport_recent_n": row.get("v28_transport_recent_n"),
                    "v28_transport_long_n": row.get("v28_transport_long_n"),
                    "v28_learned_horizon_minutes": row.get("v28_learned_horizon_minutes"),
                    "v28_effective_horizon_minutes": row.get("v28_effective_horizon_minutes"),
                    "v28_d_sigma": row.get("v28_d_sigma"),
                    "v28_sigma_t_dollars": row.get("v28_sigma_t_dollars"),
                    "ask_cents": ask_cents,
                    "book_implied_yes_from_side_ask": row.get("book_implied_yes_from_side_ask"),
                    "candidate_edge_cents": edge,
                    "source_status": "frozen_pre_resolution_prediction",
                }
            )

    freeze_markets = len({str(row.get("market_ticker") or "") for row in frozen_rows if row.get("market_ticker")})
    summary = {
        "generated_utc": frozen_utc,
        "builder_script": Path(__file__).name,
        "freeze_status": "frozen_predictions_written" if frozen_rows else "blocked_no_frozen_predictions",
        "passive_input_rows": len(passive_rows),
        "freeze_ready_input_rows": freeze_ready_input_rows,
        "frozen_prediction_rows": len(frozen_rows),
        "frozen_prediction_markets": freeze_markets,
        "candidate_manifest_count": len(manifests),
        "forward_collection_candidate_count": len(forward_allowed_candidates),
        "forward_collection_candidates": [manifest.get("candidate_id") for manifest in forward_allowed_candidates],
        "forward_allowed_candidate_count": len(forward_allowed_candidates),
        "forward_allowed_candidates": [manifest.get("candidate_id") for manifest in forward_allowed_candidates],
        "preflight_status": preflight_summary.get("preflight_status"),
        "preflight_freeze_ready_rows": preflight_summary.get("freeze_ready_rows"),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "inputs": {
            "passive_snapshots_csv": rel_path(source_csv),
            "passive_snapshots_hash": sha256_file(source_csv),
            "candidate_manifests_json": rel_path(CANDIDATE_MANIFESTS_JSON),
            "candidate_manifests_hash": sha256_file(CANDIDATE_MANIFESTS_JSON),
            "forward_preflight_json": rel_path(FORWARD_PREFLIGHT_JSON),
            "forward_preflight_hash": sha256_file(FORWARD_PREFLIGHT_JSON),
        },
        "outputs": {
            "frozen_csv": rel_path(FROZEN_CSV),
            "frozen_json": rel_path(FROZEN_JSON),
            "summary_json": rel_path(FROZEN_SUMMARY_JSON),
            "summary_md": rel_path(FROZEN_SUMMARY_MD),
        },
        "promotion_status": {
            "allowed_for_promotion_scoring": bool(frozen_rows),
            "reason": "requires frozen rows plus later settlement labels and verifier pass",
        },
    }
    return frozen_rows, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Frozen Forward Predictions",
        "",
        "Research-only frozen prediction ledger. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Freeze status: `{summary['freeze_status']}`",
        f"- Passive input rows: `{summary['passive_input_rows']}`",
        f"- Freeze-ready input rows: `{summary['freeze_ready_input_rows']}`",
        f"- Frozen prediction rows: `{summary['frozen_prediction_rows']}`",
        f"- Frozen prediction markets: `{summary['frozen_prediction_markets']}`",
        f"- Forward-collection candidates: `{summary['forward_collection_candidate_count']}`",
        f"- Preflight status: `{summary['preflight_status']}`",
        f"- Preflight freeze-ready rows: `{summary['preflight_freeze_ready_rows']}`",
        "",
        "## Blockers",
        "",
        "| blocker | rows |",
        "|---|---:|",
    ]
    for blocker, count in summary["blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This ledger is intentionally empty until a row is complete and still pre-resolution at freeze time.",
            "- Empty output is a safe result, not a failure of the guardrail.",
            "- Promotion scoring still requires settled post-lock rows and the promotion verifier.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, FROZEN_CSV)
    FROZEN_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FROZEN_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, FROZEN_SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write frozen forward prediction artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--input-csv", type=Path, default=PASSIVE_SNAPSHOTS_CSV, help="Input staging/packet CSV to freeze.")
    args = parser.parse_args()
    rows, summary = build(source_csv=args.input_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "freeze_status": summary["freeze_status"],
                "passive_input_rows": summary["passive_input_rows"],
                "freeze_ready_input_rows": summary["freeze_ready_input_rows"],
                "frozen_prediction_rows": summary["frozen_prediction_rows"],
                "forward_allowed_candidate_count": summary["forward_allowed_candidate_count"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
