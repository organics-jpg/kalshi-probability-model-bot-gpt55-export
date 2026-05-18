"""Train diagnostic v28 successor candidates on logged-event features.

This is a research-only wrapper around train_v28_successor_candidates.py. It
uses the richer logged-event feature table and writes separate outputs so the
seed calibration run remains intact. Promotion gates remain closed because the
logged-event labels are diagnostic/posthoc-label-sourced and there are no
frozen-forward rows.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import train_v28_successor_candidates as trainer


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"


PATH_NAMES = [
    "FEATURES_CSV",
    "FEATURE_MANIFEST_JSON",
    "PREDICTIONS_CSV",
    "PREDICTIONS_JSON",
    "CANDIDATE_MANIFEST_JSON",
    "CALIBRATION_JSON",
    "CALIBRATION_MD",
    "METRICS_CSV",
    "BINS_CSV",
]


def configure_logged_event_paths() -> dict[str, Path]:
    old = {name: getattr(trainer, name) for name in PATH_NAMES}
    trainer.FEATURES_CSV = OUT_DIR / "features_logged_events_latest.csv"
    trainer.FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_logged_events_latest.json"
    trainer.PREDICTIONS_CSV = OUT_DIR / "candidate_predictions_logged_events_latest.csv"
    trainer.PREDICTIONS_JSON = OUT_DIR / "candidate_predictions_logged_events_latest.json"
    trainer.CANDIDATE_MANIFEST_JSON = OUT_DIR / "candidate_manifests_logged_events_latest.json"
    trainer.CALIBRATION_JSON = EDGE_DIR / "v28_successor_logged_event_calibration_latest.json"
    trainer.CALIBRATION_MD = EDGE_DIR / "v28_successor_logged_event_calibration_latest.md"
    trainer.METRICS_CSV = EDGE_DIR / "v28_successor_logged_event_calibration_metrics_latest.csv"
    trainer.BINS_CSV = EDGE_DIR / "v28_successor_logged_event_calibration_bins_latest.csv"
    return old


def restore_paths(old: dict[str, Path]) -> None:
    for name, value in old.items():
        setattr(trainer, name, value)


def build(limit_rows: int | None = None):
    old = configure_logged_event_paths()
    try:
        rows, predictions, manifests, metrics, bins, summary = trainer.build(limit_rows=limit_rows)
    finally:
        restore_paths(old)
    summary["dataset_variant"] = "logged_events_diagnostic"
    summary["notes"].append("This run uses logged v28 event features with posthoc seed labels; it is diagnostic-only.")
    return rows, predictions, manifests, metrics, bins, summary


def write_outputs(predictions, manifests, metrics, bins, summary) -> None:
    old = configure_logged_event_paths()
    try:
        trainer.write_outputs(predictions, manifests, metrics, bins, summary)
    finally:
        restore_paths(old)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write logged-event candidate artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build artifacts in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional smoke-test row limit.")
    args = parser.parse_args()

    _rows, predictions, manifests, metrics, bins, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(predictions, manifests, metrics, bins, summary)
    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "candidate_count": summary["candidate_count"],
                "promotion_verdict": summary["promotion_verdict"],
                "split_summary": summary["split_summary"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
