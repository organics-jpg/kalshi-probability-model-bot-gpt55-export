"""Join labels to sidecar batch frozen rows without touching promotion ledgers.

Research-only. This is the post-resolution handoff for the sidecar bundle
batch path: it consumes the non-canonical sidecar batch frozen CSV, attaches
settlement labels only after freeze and close, writes separate batch-labeled
artifacts, and never grants promotion by itself.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from join_v28_successor_forward_labels import (
    OUTPUT_FIELDS,
    as_float,
    join_rows,
    load_label_index,
    read_csv_rows,
    sha256_file,
)
from run_v28_successor_sidecar_bundle_batch_handoff import BATCH_FROZEN_CSV


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

SHADOW_LABELS_CSV = OUT_DIR / "shadow_forward_labeled_rows_latest.csv"
BATCH_SETTLEMENT_LABELS_CSV = OUT_DIR / "sidecar_bundle_batch_settlement_labels_latest.csv"
BATCH_LABELED_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"
BATCH_LABELED_JSON = OUT_DIR / "sidecar_bundle_batch_labeled_latest.json"
BATCH_LABEL_JOIN_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_label_join_latest.json"
BATCH_LABEL_JOIN_MD = EDGE_DIR / "v28_successor_sidecar_bundle_batch_label_join_latest.md"


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def candidate_metrics(joined_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for candidate_id in sorted({str(row.get("candidate_id") or "") for row in joined_rows}):
        rows = [row for row in joined_rows if str(row.get("candidate_id") or "") == candidate_id]
        if not rows:
            continue
        candidate_briers = [as_float(row.get("candidate_brier_yes")) for row in rows]
        v28_briers = [as_float(row.get("v28_brier_yes")) for row in rows]
        candidate_loglosses = [as_float(row.get("candidate_logloss_yes")) for row in rows]
        v28_loglosses = [as_float(row.get("v28_logloss_yes")) for row in rows]
        candidate_briers = [value for value in candidate_briers if value is not None]
        v28_briers = [value for value in v28_briers if value is not None]
        candidate_loglosses = [value for value in candidate_loglosses if value is not None]
        v28_loglosses = [value for value in v28_loglosses if value is not None]
        out[candidate_id] = {
            "rows": len(rows),
            "markets": len({row.get("market_ticker") for row in rows if row.get("market_ticker")}),
            "candidate_brier_yes": sum(candidate_briers) / len(candidate_briers) if candidate_briers else None,
            "v28_brier_yes": sum(v28_briers) / len(v28_briers) if v28_briers else None,
            "candidate_logloss_yes": sum(candidate_loglosses) / len(candidate_loglosses) if candidate_loglosses else None,
            "v28_logloss_yes": sum(v28_loglosses) / len(v28_loglosses) if v28_loglosses else None,
        }
    return out


def summarize(
    *,
    frozen_csv: Path,
    label_csvs: list[Path],
    frozen_rows: list[dict[str, Any]],
    labeled_rows: list[dict[str, Any]],
    label_count: int,
) -> dict[str, Any]:
    joined_rows = [row for row in labeled_rows if row.get("label_join_status") == "joined_post_resolution"]
    status_counts = Counter(str(row.get("label_join_status") or "") for row in labeled_rows)
    blocker_counts: Counter[str] = Counter()
    for row in labeled_rows:
        for blocker in str(row.get("label_join_blockers") or "").split(";"):
            if blocker:
                blocker_counts[blocker] += 1

    blockers: list[str] = []
    if not frozen_rows:
        blockers.append("no_batch_frozen_rows")
    if frozen_rows and not joined_rows:
        blockers.append("no_joined_batch_labels")
    blockers.extend(str(blocker) for blocker in blocker_counts)

    if not frozen_rows:
        status = "blocked_no_batch_frozen_rows"
    elif not joined_rows:
        status = "blocked_no_joined_batch_labels"
    else:
        status = "joined_batch_labels_available"

    return {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "batch_label_join_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "sidecar batch label join is necessary but not sufficient; source contract, coverage floors, forward evidence scoring, and promotion verifier must still pass",
        },
        "frozen_rows": len(frozen_rows),
        "labeled_rows": len(labeled_rows),
        "joined_rows": len(joined_rows),
        "joined_markets": len({row.get("market_ticker") for row in joined_rows if row.get("market_ticker")}),
        "label_source_rows": label_count,
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "blockers": sorted(set(blockers)),
        "candidate_metrics": candidate_metrics(joined_rows),
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


def build(
    *,
    frozen_csv: Path = BATCH_FROZEN_CSV,
    label_csvs: list[Path] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    label_csvs = label_csvs or [BATCH_SETTLEMENT_LABELS_CSV, SHADOW_LABELS_CSV]
    frozen_rows = read_csv_rows(frozen_csv)
    labels_by_market = load_label_index(label_csvs)
    labeled_rows = join_rows(frozen_rows, labels_by_market)
    summary = summarize(
        frozen_csv=frozen_csv,
        label_csvs=label_csvs,
        frozen_rows=frozen_rows,
        labeled_rows=labeled_rows,
        label_count=len(labels_by_market),
    )
    return {"summary": summary, "sample_rows": labeled_rows[:20]}, labeled_rows


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(OUTPUT_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Batch Label Join",
        "",
        "Research-only post-resolution label join for sidecar batch frozen rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Batch label join status: `{summary['batch_label_join_status']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Frozen rows: `{summary['frozen_rows']}`",
        f"- Label source markets: `{summary['label_source_rows']}`",
        f"- Labeled rows: `{summary['labeled_rows']}`",
        f"- Joined rows: `{summary['joined_rows']}`",
        f"- Joined markets: `{summary['joined_markets']}`",
        "",
        "## Status Counts",
        "",
        "| status | rows |",
        "|---|---:|",
    ]
    for status, count in summary["status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    if not summary["blocker_counts"]:
        lines.append("| none | 0 |")
    lines.extend(["", "## Candidate Metrics", "", "| candidate | rows | markets | candidate brier | v28 brier |", "|---|---:|---:|---:|---:|"])
    for candidate_id, metrics in summary["candidate_metrics"].items():
        lines.append(
            f"| `{candidate_id}` | {metrics['rows']} | {metrics['markets']} | "
            f"{metrics['candidate_brier_yes']} | {metrics['v28_brier_yes']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This stage attaches labels only to rows already frozen by the sidecar batch handoff.",
            "- Empty output is expected until real batch frozen rows exist and their markets settle.",
            "- Joined batch labels still require source contract, coverage checks, forward evidence scoring, and the promotion verifier.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, BATCH_LABELED_CSV)
    BATCH_LABELED_JSON.write_text(json.dumps({"rows": rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BATCH_LABEL_JOIN_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, BATCH_LABEL_JOIN_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-csv", type=Path, default=BATCH_FROZEN_CSV, help="Sidecar batch frozen prediction CSV.")
    parser.add_argument("--labels-csv", type=Path, action="append", default=None, help="Settlement label CSV; can be provided multiple times.")
    parser.add_argument("--write", action="store_true", help="Write sidecar batch label join artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()

    report, rows = build(frozen_csv=args.frozen_csv, label_csvs=args.labels_csv)
    if args.write and not args.dry_run:
        write_outputs(report, rows)
    summary = report["summary"]
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
