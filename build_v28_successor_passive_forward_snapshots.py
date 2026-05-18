"""Build passive forward snapshot rows from native Kalshi book captures.

Research-only. This consumes recorded passive websocket data under
research_data/particle_shadow_forward_* and creates a causal staging table for
future v28 successor forward prediction registration.

The rows are not promotion evidence by themselves: the current passive captures
record Kalshi market/book data but not BTC spot/bars, v28 outputs, candidate
predictions, or settlement labels. This script keeps those distinctions explicit
so after-the-fact reconstruction cannot accidentally become promotable.
"""
from __future__ import annotations

import argparse
import csv
import json
import hashlib
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RESEARCH_DATA = ROOT / "research_data"
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PASSIVE_GLOB = "particle_shadow_forward_*"
SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"
SNAPSHOTS_JSON = OUT_DIR / "passive_forward_snapshots_latest.json"
SNAPSHOT_AUDIT_JSON = EDGE_DIR / "v28_successor_passive_forward_snapshots_latest.json"
SNAPSHOT_AUDIT_MD = EDGE_DIR / "v28_successor_passive_forward_snapshots_latest.md"


SNAPSHOT_FIELDS = [
    "row_id",
    "dataset_role",
    "source_dataset_tag",
    "source_file",
    "source_line_or_offset",
    "source_type",
    "source_quality_tier",
    "run_id",
    "market_ticker",
    "market_close_ts_utc",
    "decision_ts_utc",
    "decision_ts_basis",
    "side",
    "strike",
    "strike_source",
    "seconds_to_close",
    "yes_bid_cents",
    "no_bid_cents",
    "yes_ask_cents",
    "no_ask_cents",
    "yes_depth",
    "no_depth",
    "ask_cents",
    "bid_cents",
    "book_implied_yes_from_side_ask",
    "book_mid_yes_cents",
    "book_width_cents",
    "book_source_event_count",
    "book_sequence_number",
    "checkpoint_reason",
    "raw_capture_ts_utc",
    "registered_utc",
    "is_pre_resolution",
    "is_pre_resolution_registered",
    "is_recomputed_after_resolution",
    "is_backfilled",
    "is_simulated",
    "is_sidecar",
    "is_diagnostic_only",
    "has_market_metadata",
    "has_top_book",
    "has_btc_state",
    "has_v28_baseline",
    "has_candidate_prediction",
    "has_settlement_label",
    "eligible_for_candidate_prediction",
    "allowed_for_training",
    "allowed_for_validation",
    "allowed_for_holdout",
    "allowed_for_forward_promotion",
    "exclusion_reason",
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


def iso_z(value: Any) -> str | None:
    parsed = parse_ts(value)
    if parsed is None:
        return None
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def iter_ndjson(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((line_number, json.loads(line)))
            except json.JSONDecodeError:
                continue
    return rows


def passive_dirs() -> list[Path]:
    return sorted([path for path in RESEARCH_DATA.glob(PASSIVE_GLOB) if path.is_dir()], key=lambda p: p.name)


def load_market_metadata(dataset_dir: Path) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for path in dataset_dir.glob("raw_events/type=watch_market/**/*.ndjson"):
        for _line_number, record in iter_ndjson(path):
            payload = record.get("payload_json") or {}
            market = str(payload.get("market_ticker") or record.get("market_ticker") or "")
            if not market:
                continue
            metadata[market] = {
                "market_ticker": market,
                "close_time": iso_z(payload.get("close_time")),
                "strike": as_float(payload.get("strike")),
                "status": payload.get("status"),
                "source_file": rel_path(path),
                "source_ts_wall": iso_z(record.get("ts_wall") or record.get("local_recv_ts")),
            }
    return metadata


def best_price(values: Any) -> float | None:
    if not isinstance(values, list) or not values:
        return None
    return as_float(values[0])


def best_depth(values: Any) -> float:
    if not isinstance(values, list) or not values:
        return 0.0
    return float(as_float(values[0]) or 0.0)


def cents_from_bid_complement(value: float | None) -> float | None:
    if value is None:
        return None
    return 100.0 - float(value)


def side_book_implied_yes(side: str, ask_cents: float | None) -> float | None:
    if ask_cents is None:
        return None
    ask_p = max(0.0, min(1.0, ask_cents / 100.0))
    if side == "yes":
        return ask_p
    if side == "no":
        return 1.0 - ask_p
    return None


def seconds_to_close(decision_ts: str | None, close_ts: str | None) -> float | None:
    decision = parse_ts(decision_ts)
    close = parse_ts(close_ts)
    if decision is None or close is None:
        return None
    return (close - decision).total_seconds()


def pre_resolution(decision_ts: str | None, close_ts: str | None) -> bool:
    seconds = seconds_to_close(decision_ts, close_ts)
    return seconds is not None and seconds >= 0.0


def checkpoint_rows(
    *,
    dataset_dir: Path,
    checkpoint_path: Path,
    line_number: int,
    record: dict[str, Any],
    metadata: dict[str, dict[str, Any]],
    registered_utc: str,
) -> list[dict[str, Any]]:
    market = str(record.get("market_ticker") or "")
    meta = metadata.get(market, {})
    close_ts = meta.get("close_time")
    strike = as_float(meta.get("strike"))
    decision_ts = iso_z(record.get("checkpoint_ts") or record.get("ts_wall"))
    raw_capture_ts = iso_z(record.get("ts_wall") or record.get("checkpoint_ts"))
    yes_bid = best_price(record.get("yes_bid_prices"))
    no_bid = best_price(record.get("no_bid_prices"))
    yes_depth = best_depth(record.get("yes_bid_sizes"))
    no_depth = best_depth(record.get("no_bid_sizes"))
    yes_ask = cents_from_bid_complement(no_bid)
    no_ask = cents_from_bid_complement(yes_bid)
    book_mid_yes = None
    book_width = None
    if yes_bid is not None and yes_ask is not None:
        book_mid_yes = 0.5 * (yes_bid + yes_ask)
        book_width = max(0.0, yes_ask - yes_bid)
    has_metadata = bool(close_ts and strike is not None)
    has_top_book = yes_bid is not None and no_bid is not None and yes_ask is not None and no_ask is not None
    row_seconds_to_close = seconds_to_close(decision_ts, close_ts)
    is_pre = pre_resolution(decision_ts, close_ts)
    registered_before_close = pre_resolution(registered_utc, close_ts)
    rows: list[dict[str, Any]] = []
    for side in ("yes", "no"):
        if side == "yes":
            ask = yes_ask
            bid = yes_bid
            depth = yes_depth
        else:
            ask = no_ask
            bid = no_bid
            depth = no_depth
        exclusion_reasons = []
        if not has_metadata:
            exclusion_reasons.append("missing_market_metadata")
        if not has_top_book:
            exclusion_reasons.append("missing_top_book")
        exclusion_reasons.extend(
            [
                "missing_btc_state",
                "missing_v28_baseline",
                "missing_candidate_prediction",
                "missing_settlement_label",
                "not_frozen_candidate_prediction_registry",
            ]
        )
        row_id = stable_hash([dataset_dir.name, rel_path(checkpoint_path), line_number, market, decision_ts, side])
        rows.append(
            {
                "row_id": row_id,
                "dataset_role": "passive_forward_snapshot_staging",
                "source_dataset_tag": dataset_dir.name,
                "source_file": rel_path(checkpoint_path),
                "source_line_or_offset": line_number,
                "source_type": "passive_book_checkpoint",
                "source_quality_tier": "passive_predecision_market_book_no_btc_no_strategy",
                "run_id": record.get("run_id"),
                "market_ticker": market,
                "market_close_ts_utc": close_ts,
                "decision_ts_utc": decision_ts,
                "decision_ts_basis": "native_passive_book_checkpoint_ts",
                "side": side,
                "strike": strike,
                "strike_source": "native_passive_watch_market_metadata" if strike is not None else "",
                "seconds_to_close": row_seconds_to_close,
                "yes_bid_cents": yes_bid,
                "no_bid_cents": no_bid,
                "yes_ask_cents": yes_ask,
                "no_ask_cents": no_ask,
                "yes_depth": yes_depth,
                "no_depth": no_depth,
                "ask_cents": ask,
                "bid_cents": bid,
                "book_implied_yes_from_side_ask": side_book_implied_yes(side, ask),
                "book_mid_yes_cents": book_mid_yes,
                "book_width_cents": book_width,
                "book_source_event_count": record.get("source_event_count"),
                "book_sequence_number": record.get("sequence_number"),
                "checkpoint_reason": record.get("reason"),
                "raw_capture_ts_utc": raw_capture_ts,
                "registered_utc": registered_utc,
                "is_pre_resolution": is_pre,
                "is_pre_resolution_registered": is_pre and registered_before_close,
                "is_recomputed_after_resolution": False,
                "is_backfilled": False,
                "is_simulated": False,
                "is_sidecar": True,
                "is_diagnostic_only": False,
                "has_market_metadata": has_metadata,
                "has_top_book": has_top_book,
                "has_btc_state": False,
                "has_v28_baseline": False,
                "has_candidate_prediction": False,
                "has_settlement_label": False,
                "eligible_for_candidate_prediction": bool(is_pre and has_metadata and has_top_book),
                "allowed_for_training": False,
                "allowed_for_validation": False,
                "allowed_for_holdout": False,
                "allowed_for_forward_promotion": False,
                "exclusion_reason": ";".join(exclusion_reasons),
            }
        )
        rows[-1]["depth"] = depth
    return rows


def build(limit_checkpoints: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    registered_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, Any]] = []
    dataset_summaries: list[dict[str, Any]] = []
    checkpoints_seen = 0
    post_resolution_rejected_rows = 0
    for dataset_dir in passive_dirs():
        manifest = read_json(dataset_dir / "metadata" / "dataset_manifest.json") or {}
        metadata = load_market_metadata(dataset_dir)
        dataset_checkpoint_count = 0
        dataset_row_count = 0
        for checkpoint_path in dataset_dir.glob("book_checkpoints/**/*.ndjson"):
            for line_number, record in iter_ndjson(checkpoint_path):
                if limit_checkpoints is not None and checkpoints_seen >= limit_checkpoints:
                    break
                checkpoints_seen += 1
                dataset_checkpoint_count += 1
                new_rows = checkpoint_rows(
                    dataset_dir=dataset_dir,
                    checkpoint_path=checkpoint_path,
                    line_number=line_number,
                    record=record,
                    metadata=metadata,
                    registered_utc=registered_utc,
                )
                included_rows = [row for row in new_rows if row["is_pre_resolution"]]
                post_resolution_rejected_rows += len(new_rows) - len(included_rows)
                rows.extend(included_rows)
                dataset_row_count += len(included_rows)
            if limit_checkpoints is not None and checkpoints_seen >= limit_checkpoints:
                break
        dataset_summaries.append(
            {
                "dataset_tag": dataset_dir.name,
                "manifest_dataset_tag": manifest.get("dataset_tag"),
                "started_at_utc": manifest.get("started_at_utc"),
                "ended_at_utc": manifest.get("ended_at_utc"),
                "manifest_markets": manifest.get("market_tickers", []),
                "metadata_markets": sorted(metadata),
                "checkpoint_count": dataset_checkpoint_count,
                "row_count": dataset_row_count,
                "manifest_records_book_checkpoints": manifest.get("records_book_checkpoints"),
                "manifest_records_raw_market_feed": manifest.get("records_raw_market_feed"),
                "manifest_records_settlement_labels": manifest.get("records_settlement_labels"),
                "manifest_records_strategy_decisions": manifest.get("records_strategy_decisions"),
            }
        )
        if limit_checkpoints is not None and checkpoints_seen >= limit_checkpoints:
            break

    row_count = len(rows)
    market_count = len({row["market_ticker"] for row in rows if row.get("market_ticker")})
    pre_resolution_rows = sum(1 for row in rows if row["is_pre_resolution"])
    registered_pre_resolution_rows = sum(1 for row in rows if row["is_pre_resolution_registered"])
    eligible_candidate_rows = sum(1 for row in rows if row["eligible_for_candidate_prediction"])
    source_counts = Counter(row["source_dataset_tag"] for row in rows)
    side_counts = Counter(row["side"] for row in rows)
    exclusion_counts = Counter()
    for row in rows:
        for reason in str(row.get("exclusion_reason") or "").split(";"):
            if reason:
                exclusion_counts[reason] += 1
    summary = {
        "generated_utc": registered_utc,
        "builder_script": Path(__file__).name,
        "snapshot_status": "staging_not_promotable",
        "row_count": row_count,
        "checkpoint_count": checkpoints_seen,
        "market_count": market_count,
        "dataset_count": len(dataset_summaries),
        "source_dataset_counts": dict(sorted(source_counts.items())),
        "side_counts": dict(sorted(side_counts.items())),
        "pre_resolution_rows": pre_resolution_rows,
        "post_resolution_rejected_rows": post_resolution_rejected_rows,
        "registered_pre_resolution_rows": registered_pre_resolution_rows,
        "eligible_for_candidate_prediction_rows": eligible_candidate_rows,
        "forward_promotion_rows": sum(1 for row in rows if row["allowed_for_forward_promotion"]),
        "missing_counts": {
            "market_close_ts_utc": sum(1 for row in rows if not row.get("market_close_ts_utc")),
            "strike": sum(1 for row in rows if as_float(row.get("strike")) is None),
            "ask_cents": sum(1 for row in rows if as_float(row.get("ask_cents")) is None),
            "btc_state": sum(1 for row in rows if not row["has_btc_state"]),
            "v28_baseline": sum(1 for row in rows if not row["has_v28_baseline"]),
            "candidate_prediction": sum(1 for row in rows if not row["has_candidate_prediction"]),
            "settlement_label": sum(1 for row in rows if not row["has_settlement_label"]),
        },
        "exclusion_reason_counts": dict(sorted(exclusion_counts.items())),
        "dataset_summaries": dataset_summaries,
        "outputs": {
            "snapshots_csv": rel_path(SNAPSHOTS_CSV),
            "snapshots_json": rel_path(SNAPSHOTS_JSON),
            "audit_json": rel_path(SNAPSHOT_AUDIT_JSON),
            "audit_md": rel_path(SNAPSHOT_AUDIT_MD),
        },
        "promotion_status": {
            "allowed_for_forward_promotion": False,
            "reason": "passive rows lack BTC state, v28 baseline, frozen candidate prediction, and settlement label",
        },
    }
    return rows, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SNAPSHOT_FIELDS + ["depth"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Passive Forward Snapshots",
        "",
        "Research-only passive capture staging. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Snapshot status: `{summary['snapshot_status']}`",
        f"- Datasets: `{summary['dataset_count']}`",
        f"- Checkpoints: `{summary['checkpoint_count']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Markets: `{summary['market_count']}`",
        f"- Pre-resolution rows: `{summary['pre_resolution_rows']}`",
        f"- Post-resolution rows rejected: `{summary['post_resolution_rejected_rows']}`",
        f"- Registered-before-close rows: `{summary['registered_pre_resolution_rows']}`",
        f"- Candidate-ready staging rows: `{summary['eligible_for_candidate_prediction_rows']}`",
        f"- Forward-promotion rows: `{summary['forward_promotion_rows']}`",
        "",
        "## Missing Pieces",
        "",
        "| item | rows missing |",
        "|---|---:|",
    ]
    for key, count in summary["missing_counts"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Source Datasets",
            "",
            "| dataset | checkpoints | rows | markets | records labels | records decisions |",
            "|---|---:|---:|---|---:|---:|",
        ]
    )
    for dataset in summary["dataset_summaries"]:
        lines.append(
            f"| `{dataset['dataset_tag']}` | {dataset['checkpoint_count']} | {dataset['row_count']} | "
            f"`{dataset['metadata_markets']}` | {dataset['manifest_records_settlement_labels']} | {dataset['manifest_records_strategy_decisions']} |"
        )
    lines.extend(
        [
            "",
            "## Exclusion Reasons",
            "",
            "| reason | rows |",
            "|---|---:|",
        ]
    )
    for reason, count in summary["exclusion_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- These rows are useful staging inputs for a future frozen forward registry.",
            "- They are not sufficient for promotion because they do not contain BTC state, v28 API outputs, candidate predictions, or settlement labels.",
            "- Rows generated after a market close must remain non-promotable even if their raw capture timestamps were pre-resolution.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, SNAPSHOTS_CSV)
    SNAPSHOTS_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SNAPSHOT_AUDIT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, SNAPSHOT_AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write passive forward snapshot artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-checkpoints", type=int, default=None, help="Optional checkpoint limit for smoke tests.")
    args = parser.parse_args()
    rows, summary = build(limit_checkpoints=args.limit_checkpoints)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "snapshot_status": summary["snapshot_status"],
                "datasets": summary["dataset_count"],
                "checkpoints": summary["checkpoint_count"],
                "rows": summary["row_count"],
                "markets": summary["market_count"],
                "pre_resolution_rows": summary["pre_resolution_rows"],
                "registered_pre_resolution_rows": summary["registered_pre_resolution_rows"],
                "forward_promotion_rows": summary["forward_promotion_rows"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
