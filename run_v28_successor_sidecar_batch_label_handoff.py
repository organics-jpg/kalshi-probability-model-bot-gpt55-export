"""Join labels to sidecar batch frozen rows without touching canonical outputs.

Research-only. This handoff consumes the batch frozen rows produced by
run_v28_successor_sidecar_bundle_batch_handoff.py and joins settlement labels
only after the prediction was frozen before close and the label became
available after resolution. It writes sidecar-batch artifacts only; it does not
modify canonical forward labeled rows or promote anything.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from join_v28_successor_forward_labels import (
    OUTPUT_FIELDS,
    join_rows,
    load_label_index,
    read_csv_rows,
    summarize as summarize_join,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

BATCH_FROZEN_CSV = OUT_DIR / "sidecar_bundle_batch_frozen_latest.csv"
SHADOW_LABELS_CSV = OUT_DIR / "shadow_forward_labeled_rows_latest.csv"

BATCH_LABELED_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"
BATCH_LABELED_JSON = OUT_DIR / "sidecar_bundle_batch_labeled_latest.json"
BATCH_LABEL_JOIN_JSON = EDGE_DIR / "v28_successor_sidecar_batch_label_join_latest.json"
BATCH_LABEL_JOIN_MD = EDGE_DIR / "v28_successor_sidecar_batch_label_join_latest.md"

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


def build(
    *,
    frozen_csv: Path = BATCH_FROZEN_CSV,
    label_csvs: list[Path] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    label_csvs = label_csvs or [SHADOW_LABELS_CSV]
    frozen_rows = read_csv_rows(frozen_csv)
    labels_by_market = load_label_index(label_csvs)
    labeled_rows = join_rows(frozen_rows, labels_by_market)
    base_summary = summarize_join(frozen_rows, labeled_rows, label_csvs, labels_by_market)
    joined_rows = [row for row in labeled_rows if row.get("label_join_status") == "joined_post_resolution"]
    blockers: Counter[str] = Counter()
    if not frozen_rows:
        blockers["no_batch_frozen_rows"] += 1
    if not joined_rows:
        blockers["no_joined_batch_labels"] += 1
    if len(joined_rows) < MIN_FORWARD_ROWS:
        blockers["joined_batch_below_row_floor"] += 1
    if len({row.get("market_ticker") for row in joined_rows if row.get("market_ticker")}) < MIN_FORWARD_MARKETS:
        blockers["joined_batch_below_market_floor"] += 1
    for blocker, count in base_summary.get("blocker_counts", {}).items():
        blockers[str(blocker)] += int(count)

    if not frozen_rows:
        status = "blocked_no_batch_frozen_rows"
    elif not joined_rows:
        status = "blocked_no_joined_batch_labels"
    elif len(joined_rows) < MIN_FORWARD_ROWS or len({row.get("market_ticker") for row in joined_rows if row.get("market_ticker")}) < MIN_FORWARD_MARKETS:
        status = "joined_batch_below_coverage_floor"
    else:
        status = "joined_batch_ready_for_forward_evidence_scoring"

    summary = {
        **base_summary,
        "builder_script": Path(__file__).name,
        "batch_label_join_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "batch label join is not promotion; source contract, forward evidence scoring, coverage, and promotion verifier are still required",
        },
        "blocker_counts": dict(sorted(blockers.items())),
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "inputs": {
            "frozen_csv": rel_path(frozen_csv),
            "frozen_hash": sha256_file(frozen_csv),
            "label_csvs": [rel_path(path) for path in label_csvs],
            "label_hashes": {rel_path(path): sha256_file(path) for path in label_csvs},
        },
        "outputs": {
            "labeled_csv": rel_path(BATCH_LABELED_CSV),
            "labeled_json": rel_path(BATCH_LABELED_JSON),
            "audit_json": rel_path(BATCH_LABEL_JOIN_JSON),
            "audit_md": rel_path(BATCH_LABEL_JOIN_MD),
        },
    }
    return labeled_rows, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(OUTPUT_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Sidecar Batch Label Join",
        "",
        "Research-only label join for sidecar batch frozen rows. This report does not touch live bot state, orders, thresholds, secrets, or canonical promotion artifacts.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Batch label join status: `{summary['batch_label_join_status']}`",
        f"- Frozen rows: `{summary['frozen_rows']}`",
        f"- Labeled rows: `{summary['labeled_rows']}`",
        f"- Joined rows: `{summary['joined_rows']}`",
        f"- Joined markets: `{summary['joined_markets']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        "",
        "## Blockers",
        "",
        "| blocker | rows |",
        "|---|---:|",
    ]
    for blocker, count in summary["blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    if not summary["blocker_counts"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Labels are joined only through the same post-resolution checks used by the canonical joiner.",
            "- Empty output is expected until real batch frozen rows exist and settle.",
            "- This stage does not grant promotion by itself.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, BATCH_LABELED_CSV)
    BATCH_LABELED_JSON.write_text(json.dumps({"rows": rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BATCH_LABEL_JOIN_JSON.write_text(json.dumps({"summary": summary, "sample_rows": rows[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, BATCH_LABEL_JOIN_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write sidecar batch label join artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--frozen-csv", type=Path, default=BATCH_FROZEN_CSV, help="Sidecar batch frozen CSV.")
    parser.add_argument("--labels-csv", type=Path, action="append", default=None, help="Settlement label CSV; can be provided multiple times.")
    args = parser.parse_args()
    rows, summary = build(frozen_csv=args.frozen_csv, label_csvs=args.labels_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "batch_label_join_status": summary["batch_label_join_status"],
                "frozen_rows": summary["frozen_rows"],
                "labeled_rows": summary["labeled_rows"],
                "joined_rows": summary["joined_rows"],
                "joined_markets": summary["joined_markets"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
