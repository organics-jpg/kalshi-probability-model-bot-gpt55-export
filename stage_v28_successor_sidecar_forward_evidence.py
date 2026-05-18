"""Stage sidecar batch frozen rows as canonical forward evidence inputs.

Research-only. This is a bridge from the complete sidecar bundle path into the
canonical frozen-forward artifacts used by the source contract and promotion
verifier. It copies only rows that were frozen before close, keeps labels out of
the frozen ledger, preserves the usual coverage floors, and never grants
promotion by itself.

The bridge exists because passive staging may be incomplete while sidecar
bundles can already contain complete pre-resolution BTC/book/v28/candidate
packets. Promotion still requires the canonical registry, post-resolution label
join, forward evidence scoring, source contract, and verifier to pass.
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
    FROZEN_CSV,
    FROZEN_FIELDS,
    FROZEN_JSON,
    FROZEN_SUMMARY_JSON,
    FROZEN_SUMMARY_MD,
)
from join_v28_successor_forward_labels import parse_ts
from run_v28_successor_sidecar_bundle_batch_handoff import BATCH_FROZEN_CSV


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

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


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def stable_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("market_ticker") or ""),
        str(row.get("row_id") or ""),
        str(row.get("candidate_id") or ""),
        str(row.get("side") or ""),
        str(row.get("decision_ts_utc") or ""),
    )


def row_blockers(row: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction":
        blockers.append("source_not_frozen_pre_resolution_prediction")
    ticker = str(row.get("market_ticker") or "")
    if not ticker.startswith("KXBTC15M-"):
        blockers.append("not_btc15m_market")
    if not str(row.get("frozen_prediction_id") or "").strip():
        blockers.append("missing_frozen_prediction_id")
    if not str(row.get("candidate_id") or "").strip():
        blockers.append("missing_candidate_id")
    frozen_ts = parse_ts(row.get("frozen_utc"))
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    close_ts = parse_ts(row.get("market_close_ts_utc"))
    if frozen_ts is None:
        blockers.append("missing_or_bad_frozen_utc")
    if decision_ts is None:
        blockers.append("missing_or_bad_decision_ts")
    if close_ts is None:
        blockers.append("missing_or_bad_market_close_ts")
    if frozen_ts is not None and close_ts is not None and frozen_ts >= close_ts:
        blockers.append("frozen_not_before_close")
    if decision_ts is not None and close_ts is not None and decision_ts > close_ts:
        blockers.append("decision_after_close")
    if str(row.get("y_yes_win") or "").strip() or str(row.get("settlement_ts_utc") or "").strip():
        blockers.append("label_field_present_in_frozen_row")
    return blockers


def canonicalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field, "") for field in FROZEN_FIELDS}


def build(source_csv: Path = BATCH_FROZEN_CSV) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_rows = read_csv_rows(source_csv)
    staged: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    duplicate_rows = 0
    seen_keys: set[tuple[str, str, str, str, str]] = set()
    seen_ids: set[str] = set()

    for row in source_rows:
        blockers = row_blockers(row)
        for blocker in blockers:
            blocker_counts[blocker] += 1
        if blockers:
            continue
        key = stable_key(row)
        frozen_id = str(row.get("frozen_prediction_id") or "")
        if key in seen_keys or frozen_id in seen_ids:
            duplicate_rows += 1
            continue
        seen_keys.add(key)
        seen_ids.add(frozen_id)
        staged.append(canonicalize_row(row))

    markets = len({row.get("market_ticker") for row in staged if row.get("market_ticker")})
    coverage_ready = len(staged) >= MIN_FORWARD_ROWS and markets >= MIN_FORWARD_MARKETS
    if not staged:
        status = "blocked_no_valid_sidecar_frozen_rows"
    elif not coverage_ready:
        status = "sidecar_forward_staged_below_coverage_floor"
    else:
        status = "sidecar_forward_staged_ready_for_label_join"

    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary = {
        "generated_utc": generated_utc,
        "builder_script": Path(__file__).name,
        "freeze_status": status,
        "stage_status": status,
        "source_family": "sidecar_batch",
        "source_frozen_rows": len(source_rows),
        "valid_source_rows": len(staged),
        "duplicate_source_rows": duplicate_rows,
        "passive_input_rows": 0,
        "freeze_ready_input_rows": len(staged),
        "frozen_prediction_rows": len(staged),
        "frozen_prediction_markets": markets,
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "coverage_ready": coverage_ready,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "inputs": {
            "sidecar_batch_frozen_csv": rel_path(source_csv),
            "sidecar_batch_frozen_hash": sha256_file(source_csv),
        },
        "outputs": {
            "frozen_csv": rel_path(FROZEN_CSV),
            "frozen_json": rel_path(FROZEN_JSON),
            "summary_json": rel_path(FROZEN_SUMMARY_JSON),
            "summary_md": rel_path(FROZEN_SUMMARY_MD),
        },
        "promotion_status": {
            "allowed_for_promotion_scoring": False,
            "reason": "staged sidecar rows are canonical forward evidence inputs only; promotion still requires labels, source contract, coverage, evidence scoring, and verifier approval",
        },
    }
    return staged, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FROZEN_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Sidecar Forward Evidence Stage",
        "",
        "Research-only bridge from sidecar frozen rows to canonical frozen-forward inputs. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed_for_promotion_scoring']}`",
        f"- Source frozen rows: `{summary['source_frozen_rows']}`",
        f"- Staged frozen rows: `{summary['frozen_prediction_rows']}`",
        f"- Staged markets: `{summary['frozen_prediction_markets']}`",
        f"- Coverage ready: `{summary['coverage_ready']}`",
        "",
        "## Blockers",
        "",
    ]
    if summary["blocker_counts"]:
        for blocker, count in summary["blocker_counts"].items():
            lines.append(f"- `{blocker}`: `{count}`")
    else:
        lines.append("- None recorded.")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This stage copies only already-frozen pre-resolution sidecar rows.",
            "- Settlement labels remain outside the frozen ledger and are joined later.",
            "- Below-floor staged rows are useful source evidence, not promotion approval.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, FROZEN_CSV)
    FROZEN_JSON.write_text(json.dumps({"rows": rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FROZEN_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, FROZEN_SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, default=BATCH_FROZEN_CSV)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows, summary = build(source_csv=args.source_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "source_frozen_rows": summary["source_frozen_rows"],
                "frozen_prediction_rows": summary["frozen_prediction_rows"],
                "frozen_prediction_markets": summary["frozen_prediction_markets"],
                "coverage_ready": summary["coverage_ready"],
                "promotion_allowed": summary["promotion_status"]["allowed_for_promotion_scoring"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
