"""Score settled sidecar-batch evidence without touching promotion ledgers.

Research-only. This wrapper applies the same probability-first evidence scorer
used by the canonical frozen-forward path to the non-canonical sidecar batch
labeled rows. It writes separate metrics/audit artifacts and never grants
promotion by itself.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from score_v28_successor_forward_evidence import (
    BIN_FIELDS,
    METRIC_FIELDS,
    read_csv_rows,
    score_rows,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

BATCH_LABELED_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"
BATCH_METRICS_CSV = EDGE_DIR / "v28_successor_sidecar_batch_evidence_metrics_latest.csv"
BATCH_BINS_CSV = EDGE_DIR / "v28_successor_sidecar_batch_evidence_bins_latest.csv"
BATCH_EVIDENCE_JSON = EDGE_DIR / "v28_successor_sidecar_batch_evidence_score_latest.json"
BATCH_EVIDENCE_MD = EDGE_DIR / "v28_successor_sidecar_batch_evidence_score_latest.md"


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(labeled_csv: Path = BATCH_LABELED_CSV) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    metrics, bins, summary = score_rows(read_csv_rows(labeled_csv))
    clean_rows = int(summary.get("clean_forward_rows") or 0)
    summary = {
        **summary,
        "builder_script": Path(__file__).name,
        "evidence_family": "sidecar_batch",
        "evidence_status": "scored_sidecar_batch_evidence" if clean_rows else "blocked_no_joined_sidecar_batch_rows",
        "canonical_promotion_ledger": False,
        "promotion_status": {
            "allowed": False,
            "reason": "sidecar batch evidence is non-canonical and below/subject to source-contract, coverage, forward-evidence, and promotion-verifier gates",
        },
        "inputs": {
            "labeled_csv": rel_path(labeled_csv),
            "labeled_hash": sha256_file(labeled_csv),
        },
        "outputs": {
            "metrics_csv": rel_path(BATCH_METRICS_CSV),
            "bins_csv": rel_path(BATCH_BINS_CSV),
            "audit_json": rel_path(BATCH_EVIDENCE_JSON),
            "audit_md": rel_path(BATCH_EVIDENCE_MD),
        },
    }
    return metrics, bins, summary


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], metrics: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# v28 Successor Sidecar Batch Evidence Score",
        "",
        "Research-only scorer for settled sidecar batch evidence. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Evidence status: `{summary['evidence_status']}`",
        f"- Evidence family: `{summary['evidence_family']}`",
        f"- Canonical promotion ledger: `{summary['canonical_promotion_ledger']}`",
        f"- Clean rows: `{summary['clean_forward_rows']}`",
        f"- Clean markets: `{summary['clean_forward_markets']}`",
        f"- Candidates: `{summary['candidate_count']}`",
        f"- Promotable by sidecar evidence alone: `{summary['promotable_candidate_count']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed']}`",
        "",
        "## Candidate Gates",
        "",
        "| candidate | status | fail reasons |",
        "|---|---|---|",
    ]
    for gate in summary["candidate_gates"]:
        lines.append(f"| `{gate['candidate_id']}` | `{gate['status']}` | `{gate['fail_reasons']}` |")
    lines.extend(
        [
            "",
            "## All-Rows Metrics",
            "",
            "| candidate | rows | markets | cand brier | v28 brier | cand logloss | v28 logloss |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in metrics:
        if row["slice"] != "all_rows":
            continue
        lines.append(
            f"| `{row['candidate_id']}` | {row['rows']} | {row['markets']} | {row['candidate_brier']} | "
            f"{row['v28_brier']} | {row['candidate_logloss']} | {row['v28_logloss']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- These rows are scored with the same probability-first metrics as canonical forward evidence.",
            "- This artifact is useful evidence plumbing, not promotion approval.",
            "- Promotion remains blocked until canonical/source-contract coverage and verifier gates pass.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(metrics: list[dict[str, Any]], bins: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(metrics, METRIC_FIELDS, BATCH_METRICS_CSV)
    write_csv_rows(bins, BIN_FIELDS, BATCH_BINS_CSV)
    BATCH_EVIDENCE_JSON.write_text(
        json.dumps({"summary": summary, "metrics": metrics, "bins": bins[:200]}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(summary, metrics, BATCH_EVIDENCE_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write sidecar batch evidence score artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--labeled-csv", type=Path, default=BATCH_LABELED_CSV, help="Sidecar batch joined-label CSV.")
    args = parser.parse_args()
    metrics, bins, summary = build(labeled_csv=args.labeled_csv)
    if args.write and not args.dry_run:
        write_outputs(metrics, bins, summary)
    print(
        json.dumps(
            {
                "evidence_status": summary["evidence_status"],
                "clean_forward_rows": summary["clean_forward_rows"],
                "clean_forward_markets": summary["clean_forward_markets"],
                "candidate_count": summary["candidate_count"],
                "promotable_candidate_count": summary["promotable_candidate_count"],
                "promotion_allowed": summary["promotion_status"]["allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
