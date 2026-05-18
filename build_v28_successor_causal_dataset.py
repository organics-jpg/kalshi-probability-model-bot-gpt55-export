"""Build the first causal dataset seed for the v28 successor FV project.

This is research-only plumbing. It reads existing reports/log artifacts and
writes auditable dataset artifacts under research_particle/ and
logs/edge_research/. It does not touch live bot state, processes, secrets, or
order logic.

Milestone scope:
- Discover the local v28 successor source artifacts.
- Normalize v28_forward_calibration_latest.csv into a canonical side-row table.
- Recover YES-axis probability from side probability when possible.
- Mark source quality and promotion eligibility conservatively.
- Write source manifest, canonical rows, machine-readable summary, and markdown
  audit report.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"
OUT_DIR = ROOT / "research_particle" / "v28_successor"

CALIBRATION_CSV = EDGE_DIR / "v28_forward_calibration_latest.csv"

ROWS_CSV = OUT_DIR / "causal_rows_seed_latest.csv"
ROWS_JSON = OUT_DIR / "causal_rows_seed_latest.json"
SOURCE_MANIFEST_JSON = OUT_DIR / "source_manifest_latest.json"
SUMMARY_JSON = EDGE_DIR / "v28_successor_dataset_audit_latest.json"
SUMMARY_MD = EDGE_DIR / "v28_successor_dataset_audit_latest.md"
INVENTORY_JSON = EDGE_DIR / "v28_successor_inventory_latest.json"
INVENTORY_MD = EDGE_DIR / "v28_successor_inventory_latest.md"

HASH_LIMIT_BYTES = 20_000_000

MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

MARKET_RE = re.compile(r"KXBTC15M-(?P<year>\d{2})(?P<mon>[A-Z]{3})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})-(?P<suffix>\d{2})")


@dataclass(frozen=True)
class SourceInfo:
    path: Path
    source_kind: str
    exists: bool
    file_size_bytes: int | None = None
    last_write_time_utc: str | None = None
    content_hash: str | None = None
    rows_read: int | None = None
    rows_accepted: int | None = None
    rows_rejected: int | None = None
    rejection_reasons: dict[str, int] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_path": rel_path(self.path),
            "source_kind": self.source_kind,
            "exists": self.exists,
            "file_size_bytes": self.file_size_bytes,
            "last_write_time_utc": self.last_write_time_utc,
            "content_hash": self.content_hash,
            "rows_read": self.rows_read,
            "rows_accepted": self.rows_accepted,
            "rows_rejected": self.rows_rejected,
            "rejection_reasons": self.rejection_reasons or {},
        }


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def utc_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    if path.stat().st_size > HASH_LIMIT_BYTES:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_info(path: Path, kind: str) -> SourceInfo:
    if not path.exists():
        return SourceInfo(path=path, source_kind=kind, exists=False)
    stat = path.stat()
    rows_read = None
    if path.suffix.lower() == ".csv":
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows_read = max(0, sum(1 for _ in handle) - 1)
        except UnicodeDecodeError:
            rows_read = None
    return SourceInfo(
        path=path,
        source_kind=kind,
        exists=True,
        file_size_bytes=int(stat.st_size),
        last_write_time_utc=utc_from_timestamp(stat.st_mtime),
        content_hash=sha256_file(path),
        rows_read=rows_read,
    )


def discover_sources() -> list[SourceInfo]:
    known = [
        (EDGE_DIR / "v28_forward_calibration_latest.csv", "calibration_rows_csv"),
        (EDGE_DIR / "v28_forward_calibration_latest.json", "calibration_rows_json"),
        (EDGE_DIR / "v28_forward_calibration_latest.md", "calibration_report_md"),
        (EDGE_DIR / "v28_forward_shadow_registry_schema_latest.md", "registry_schema_md"),
        (EDGE_DIR / "v28_source_quality_ceiling_audit_latest.md", "source_quality_report_md"),
        (EDGE_DIR / "v28_source_quality_ceiling_audit_latest.json", "source_quality_report_json"),
        (EDGE_DIR / "v28_fv_model_readiness_latest.md", "fv_readiness_report_md"),
        (EDGE_DIR / "v28_fv_model_readiness_latest.json", "fv_readiness_report_json"),
        (EDGE_DIR / "v28_calibrated_fv_sample_plan_latest.md", "fv_sample_plan_md"),
        (EDGE_DIR / "v28_calibrated_fv_sample_plan_latest.json", "fv_sample_plan_json"),
        (ROOT / "logs" / "live_mushroom_v28_size2" / "bot.log", "live_bot_log_inventory_only"),
        (ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson", "execution_events_inventory_only"),
    ]
    infos = [source_info(path, kind) for path, kind in known]

    # Add a few discovered v28 successor-adjacent reports for inventory context.
    if EDGE_DIR.exists():
        for path in sorted(EDGE_DIR.glob("v28_*latest.md"))[:500]:
            if any(info.path == path for info in infos):
                continue
            name = path.name
            if any(token in name for token in ["fv", "calibrat", "source", "readiness", "forward", "scorecard"]):
                infos.append(source_info(path, "discovered_v28_report_md"))
    return infos


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def clamp_probability(value: float | None) -> float | None:
    if value is None:
        return None
    return min(1.0 - 1e-12, max(1e-12, float(value)))


def logloss(p: float | None, y: float | None) -> float | None:
    p = clamp_probability(p)
    if p is None or y is None:
        return None
    return -(float(y) * math.log(p) + (1.0 - float(y)) * math.log(1.0 - p))


def parse_market_close_ts(market: str | None) -> str | None:
    if not market:
        return None
    match = MARKET_RE.search(str(market).upper())
    if not match:
        return None
    mon = MONTHS.get(match.group("mon"))
    if mon is None:
        return None
    year = 2000 + int(match.group("year"))
    try:
        dt = datetime(
            year=year,
            month=mon,
            day=int(match.group("day")),
            hour=int(match.group("hour")),
            minute=int(match.group("minute")),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None
    return dt.isoformat().replace("+00:00", "Z")


def infer_decision_ts(close_ts: str | None, seconds_to_close: float | None) -> str | None:
    if close_ts is None or seconds_to_close is None:
        return None
    try:
        close = datetime.fromisoformat(close_ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    decision = close - timedelta(seconds=float(seconds_to_close))
    return decision.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def stable_hash(parts: Iterable[Any]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(str(part if part is not None else "").encode("utf-8"))
        digest.update(b"\x1f")
    return digest.hexdigest()[:24]


def source_quality_for(source: str, decision_ts_utc: str | None) -> tuple[str, bool, bool, bool, str]:
    """Return tier, train, validation, forward promotion, exclusion reason."""
    if source == "entry":
        tier = "approved_entry_from_posthoc_calibration_report"
        train = True
        validation = True
        forward = False
        reason = "posthoc_calibration_report_not_forward_registry"
    elif source == "rejected_actionable":
        tier = "rejected_actionable_from_posthoc_calibration_report"
        train = True
        validation = True
        forward = False
        reason = "rejected_actionable_posthoc_not_promotion_source"
    else:
        tier = "unknown_or_diagnostic"
        train = False
        validation = False
        forward = False
        reason = "unknown_source_type"
    if decision_ts_utc is None:
        train = False
        validation = False
        forward = False
        reason = "missing_decision_timestamp"
    return tier, train, validation, forward, reason


def canonicalize_calibration_row(raw: dict[str, Any], *, line_number: int, source_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    market = str(raw.get("market") or "").strip()
    side = str(raw.get("side") or "").strip().lower()
    source = str(raw.get("source") or "").strip()
    reason = str(raw.get("reason") or "").strip()
    if not market:
        return None, "missing_market"
    if side not in {"yes", "no"}:
        return None, "invalid_side"

    p_side = as_float(raw.get("p_side"))
    outcome = as_float(raw.get("outcome"))
    if p_side is None:
        return None, "missing_p_side"
    if outcome not in {0.0, 1.0}:
        return None, "missing_or_invalid_outcome"

    y_yes = outcome if side == "yes" else 1.0 - outcome
    p_yes = p_side if side == "yes" else 1.0 - p_side
    p_no = 1.0 - p_yes

    seconds_to_close = as_float(raw.get("seconds_to_close"))
    close_ts = parse_market_close_ts(market)
    decision_ts = infer_decision_ts(close_ts, seconds_to_close)
    source_quality_tier, allowed_train, allowed_validation, allowed_forward, exclusion_reason = source_quality_for(source, decision_ts)

    brier_yes = (p_yes - y_yes) ** 2
    brier_side = (p_side - outcome) ** 2
    row_id = stable_hash([market, decision_ts, side, source, reason, rel_path(source_path), line_number])

    is_pre_resolution = None
    if close_ts and decision_ts:
        try:
            is_pre_resolution = datetime.fromisoformat(decision_ts.replace("Z", "+00:00")) < datetime.fromisoformat(close_ts.replace("Z", "+00:00"))
        except ValueError:
            is_pre_resolution = None

    row = {
        "row_id": row_id,
        "dataset_role": "causal_seed_from_v28_forward_calibration",
        "source_file": rel_path(source_path),
        "source_line_or_offset": line_number,
        "source_type": source,
        "source_reason": reason,
        "source_quality_tier": source_quality_tier,
        "market_ticker": market,
        "market_close_ts_utc": close_ts,
        "decision_ts_utc": decision_ts,
        "decision_ts_basis": "market_close_minus_seconds_to_close" if decision_ts else "missing",
        "side": side,
        "side_or_axis": f"side={side}",
        "strike": "",
        "strike_source": "missing_in_forward_calibration_seed",
        "seconds_to_close": seconds_to_close,
        "v28_p_side": p_side,
        "v28_p_yes": p_yes,
        "v28_p_no": p_no,
        "v28_fair_yes_cents": 100.0 * p_yes,
        "v28_fair_no_cents": 100.0 * p_no,
        "v28_side_outcome": outcome,
        "y_yes_win": y_yes,
        "brier_side": brier_side,
        "brier_yes": brier_yes,
        "logloss_yes": logloss(p_yes, y_yes),
        "bucket": raw.get("bucket") or "",
        "actionable": as_bool(raw.get("actionable")),
        "edge_cents": as_float(raw.get("edge_cents")),
        "ask_cents": as_float(raw.get("ask_cents")),
        "sigma_t_dollars": as_float(raw.get("sigma_t_dollars")),
        "recross_hazard_score": as_float(raw.get("recross_hazard_score")),
        "h6_recross_hazard_high": as_bool(raw.get("h6_recross_hazard_high")),
        "gross_cents": as_float(raw.get("gross_cents")),
        "is_pre_resolution": is_pre_resolution,
        "is_pre_resolution_registered": False,
        "is_recomputed_after_resolution": True,
        "is_backfilled": False,
        "is_simulated": source != "entry",
        "is_sidecar": False,
        "is_diagnostic_only": True,
        "allowed_for_training": allowed_train,
        "allowed_for_validation": allowed_validation,
        "allowed_for_holdout": False,
        "allowed_for_forward_promotion": allowed_forward,
        "exclusion_reason": exclusion_reason,
    }
    return row, None


def read_calibration_rows(path: Path, limit_rows: int | None = None) -> tuple[list[dict[str, Any]], Counter[str]]:
    rows: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    if not path.exists():
        rejections["missing_calibration_csv"] += 1
        return rows, rejections

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw in enumerate(reader, start=2):
            if limit_rows is not None and len(rows) >= limit_rows:
                break
            row, rejection = canonicalize_calibration_row(raw, line_number=idx, source_path=path)
            if row is None:
                rejections[rejection or "unknown_rejection"] += 1
                continue
            rows.append(row)
    return rows, rejections


def duplicate_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_row_id = Counter(row["row_id"] for row in rows)
    by_market_second_side = Counter(
        (
            row.get("market_ticker"),
            str(row.get("decision_ts_utc") or "")[:19],
            row.get("side"),
        )
        for row in rows
    )
    return {
        "row_id_duplicates": sum(count - 1 for count in by_row_id.values() if count > 1),
        "same_market_second_side_duplicates": sum(count - 1 for count in by_market_second_side.values() if count > 1),
        "duplicate_row_ids": [key for key, count in by_row_id.items() if count > 1][:20],
    }


def summarize_numeric(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [float(row[key]) for row in rows if row.get(key) not in {None, ""}]
    if not vals:
        return None
    return sum(vals) / len(vals)


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "markets": 0,
            "avg_p_yes": None,
            "yes_win_rate": None,
            "avg_brier_yes": None,
            "avg_logloss_yes": None,
            "gross_cents": 0.0,
        }
    return {
        "rows": len(rows),
        "markets": len({row["market_ticker"] for row in rows}),
        "avg_p_yes": summarize_numeric(rows, "v28_p_yes"),
        "yes_win_rate": summarize_numeric(rows, "y_yes_win"),
        "avg_brier_yes": summarize_numeric(rows, "brier_yes"),
        "avg_logloss_yes": summarize_numeric(rows, "logloss_yes"),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in rows),
    }


def summarize(rows: list[dict[str, Any]], sources: list[SourceInfo], rejections: Counter[str]) -> dict[str, Any]:
    by_source = {source: summarize_group([row for row in rows if row.get("source_type") == source]) for source in sorted({str(row.get("source_type")) for row in rows})}
    by_bucket = {bucket: summarize_group([row for row in rows if row.get("bucket") == bucket]) for bucket in sorted({str(row.get("bucket")) for row in rows})}
    by_quality = {
        tier: summarize_group([row for row in rows if row.get("source_quality_tier") == tier])
        for tier in sorted({str(row.get("source_quality_tier")) for row in rows})
    }
    missing_counts = {
        "decision_ts_utc": sum(1 for row in rows if not row.get("decision_ts_utc")),
        "market_close_ts_utc": sum(1 for row in rows if not row.get("market_close_ts_utc")),
        "strike": sum(1 for row in rows if not row.get("strike")),
        "v28_p_yes": sum(1 for row in rows if row.get("v28_p_yes") in {None, ""}),
        "v28_p_side": sum(1 for row in rows if row.get("v28_p_side") in {None, ""}),
        "y_yes_win": sum(1 for row in rows if row.get("y_yes_win") in {None, ""}),
    }
    eligibility = {
        "training": sum(1 for row in rows if row.get("allowed_for_training") is True),
        "validation": sum(1 for row in rows if row.get("allowed_for_validation") is True),
        "holdout": sum(1 for row in rows if row.get("allowed_for_holdout") is True),
        "forward_promotion": sum(1 for row in rows if row.get("allowed_for_forward_promotion") is True),
    }
    source_manifest_hash = stable_hash([json.dumps([source.as_dict() for source in sources], sort_keys=True)])
    return {
        "dataset_id": "v28_successor_causal_seed",
        "dataset_version": "seed_v001",
        "created_utc": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": rel_path(Path(__file__)),
        "source_manifest_hash": source_manifest_hash,
        "row_count": len(rows),
        "market_count": len({row["market_ticker"] for row in rows}),
        "min_decision_ts_utc": min([row["decision_ts_utc"] for row in rows if row.get("decision_ts_utc")] or [None]),
        "max_decision_ts_utc": max([row["decision_ts_utc"] for row in rows if row.get("decision_ts_utc")] or [None]),
        "label_coverage_pct": 100.0 * (1.0 - missing_counts["y_yes_win"] / max(1, len(rows))),
        "yes_axis_probability_coverage_pct": 100.0 * (1.0 - missing_counts["v28_p_yes"] / max(1, len(rows))),
        "side_axis_probability_coverage_pct": 100.0 * (1.0 - missing_counts["v28_p_side"] / max(1, len(rows))),
        "overall": summarize_group(rows),
        "by_source": by_source,
        "by_bucket": by_bucket,
        "by_quality": by_quality,
        "missing_counts": missing_counts,
        "eligibility_counts": eligibility,
        "duplicate_summary": duplicate_summary(rows),
        "row_rejections": dict(rejections),
        "source_inventory": [source.as_dict() for source in sources],
        "leakage_audit": {
            "status": "pass_for_diagnostic_seed_not_promotion",
            "notes": [
                "Rows include labels and model features in one table; training code must use feature manifests to exclude labels.",
                "decision_ts_utc is inferred from market close minus seconds_to_close for the calibration CSV seed.",
                "All rows are marked allowed_for_forward_promotion=false because this source is a posthoc calibration artifact.",
                "Strike is missing in the calibration CSV seed and must be recovered from richer sources before boundary modeling.",
            ],
        },
    }


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    overall = summary["overall"]
    lines = [
        "# v28 Successor Dataset Audit",
        "",
        "Research-only dataset seed. No live bot state, process, order logic, thresholds, or secrets were touched.",
        "",
        "## Dataset",
        "",
        f"- Dataset id/version: `{summary['dataset_id']}` / `{summary['dataset_version']}`",
        f"- Created UTC: `{summary['created_utc']}`",
        f"- Builder: `{summary['builder_script']}`",
        f"- Source manifest hash: `{summary['source_manifest_hash']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Unique markets: `{summary['market_count']}`",
        f"- Decision time range: `{summary['min_decision_ts_utc']}` to `{summary['max_decision_ts_utc']}`",
        f"- Label coverage: `{summary['label_coverage_pct']:.2f}%`",
        f"- YES-axis probability coverage: `{summary['yes_axis_probability_coverage_pct']:.2f}%`",
        f"- Side-axis probability coverage: `{summary['side_axis_probability_coverage_pct']:.2f}%`",
        "",
        "## Baseline V28 Seed Metrics",
        "",
        f"- Avg YES probability: `{fmt(overall['avg_p_yes'])}`",
        f"- YES win rate: `{fmt(overall['yes_win_rate'])}`",
        f"- Avg YES-axis Brier: `{fmt(overall['avg_brier_yes'])}`",
        f"- Avg YES-axis logloss: `{fmt(overall['avg_logloss_yes'])}`",
        f"- Gross cents proxy: `{fmt(overall['gross_cents'])}`",
        "",
        "## Eligibility",
        "",
        "| bucket | rows |",
        "|---|---:|",
    ]
    for key, value in summary["eligibility_counts"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## By Source", "", "| source | rows | markets | avg p_yes | win rate | brier | logloss | gross c |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for source, bucket in summary["by_source"].items():
        lines.append(
            f"| {source} | {bucket['rows']} | {bucket['markets']} | {fmt(bucket['avg_p_yes'])} | "
            f"{fmt(bucket['yes_win_rate'])} | {fmt(bucket['avg_brier_yes'])} | {fmt(bucket['avg_logloss_yes'])} | {fmt(bucket['gross_cents'])} |"
        )

    lines.extend(["", "## By Probability Bucket", "", "| bucket | rows | markets | avg p_yes | win rate | brier | logloss | gross c |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for bucket_name, bucket in summary["by_bucket"].items():
        lines.append(
            f"| {bucket_name} | {bucket['rows']} | {bucket['markets']} | {fmt(bucket['avg_p_yes'])} | "
            f"{fmt(bucket['yes_win_rate'])} | {fmt(bucket['avg_brier_yes'])} | {fmt(bucket['avg_logloss_yes'])} | {fmt(bucket['gross_cents'])} |"
        )

    lines.extend(["", "## Source Quality", "", "| tier | rows | markets | avg p_yes | win rate | brier |", "|---|---:|---:|---:|---:|---:|"])
    for tier, bucket in summary["by_quality"].items():
        lines.append(
            f"| {tier} | {bucket['rows']} | {bucket['markets']} | {fmt(bucket['avg_p_yes'])} | "
            f"{fmt(bucket['yes_win_rate'])} | {fmt(bucket['avg_brier_yes'])} |"
        )

    lines.extend(["", "## Missing Counts", "", "| field | missing rows |", "|---|---:|"])
    for key, value in summary["missing_counts"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Duplicate Summary", "", "| check | count |", "|---|---:|"])
    for key, value in summary["duplicate_summary"].items():
        if isinstance(value, list):
            continue
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Row Rejections", "", "| reason | rows |", "|---|---:|"])
    if summary["row_rejections"]:
        for key, value in summary["row_rejections"].items():
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(["", "## Leakage Audit", "", f"- Status: `{summary['leakage_audit']['status']}`"])
    for note in summary["leakage_audit"]["notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Source Inventory", "", "| source | kind | exists | size | rows read | last write UTC | hash |", "|---|---|---:|---:|---:|---|---|"])
    for source in summary["source_inventory"]:
        digest = source.get("content_hash") or ""
        if digest:
            digest = digest[:12]
        lines.append(
            f"| `{source['source_path']}` | {source['source_kind']} | {source['exists']} | "
            f"{source.get('file_size_bytes') or ''} | {source.get('rows_read') or ''} | "
            f"{source.get('last_write_time_utc') or ''} | {digest} |"
        )

    lines.extend([
        "",
        "## Read",
        "",
        "- This is a seed dataset, not a promotable forward registry.",
        "- The useful milestone achieved here is a deterministic row ledger with YES-axis recovery, source-quality flags, and baseline probability metrics.",
        "- Main blockers before model training: recover richer timestamp/strike/book/BTC fields from underlying event ledgers, add feature manifests, and keep posthoc calibration rows out of promotion evidence.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_inventory_markdown(sources: list[SourceInfo], path: Path) -> None:
    existing = [source for source in sources if source.exists]
    missing = [source for source in sources if not source.exists]
    by_kind = Counter(source.source_kind for source in existing)
    lines = [
        "# v28 Successor Source Inventory",
        "",
        "Research-only source inventory for the v28 successor FV pipeline. This report only inspects files; it does not touch live bot state or processes.",
        "",
        "## Summary",
        "",
        f"- Existing sources: `{len(existing)}`",
        f"- Missing expected sources: `{len(missing)}`",
        f"- Generated UTC: `{datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}`",
        "",
        "## By Kind",
        "",
        "| kind | count |",
        "|---|---:|",
    ]
    for kind, count in sorted(by_kind.items()):
        lines.append(f"| {kind} | {count} |")

    lines.extend(["", "## Sources", "", "| source | kind | exists | size | rows read | last write UTC | hash |", "|---|---|---:|---:|---:|---|---|"])
    for source in sources:
        item = source.as_dict()
        digest = item.get("content_hash") or ""
        if digest:
            digest = digest[:12]
        lines.append(
            f"| `{item['source_path']}` | {item['source_kind']} | {item['exists']} | "
            f"{item.get('file_size_bytes') or ''} | {item.get('rows_read') or ''} | "
            f"{item.get('last_write_time_utc') or ''} | {digest} |"
        )

    lines.extend([
        "",
        "## Read",
        "",
        "- `v28_forward_calibration_latest.csv` is the first parsed seed source.",
        "- Large live bot logs are inventoried only in this milestone; they are not parsed yet.",
        "- A source appearing here does not make its rows promotion-grade. Source quality is assigned at row-build time.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[SourceInfo], Counter[str], dict[str, Any]]:
    sources = discover_sources()
    rows, rejections = read_calibration_rows(CALIBRATION_CSV, limit_rows=limit_rows)

    updated_sources: list[SourceInfo] = []
    for info in sources:
        if info.path == CALIBRATION_CSV:
            updated_sources.append(
                SourceInfo(
                    path=info.path,
                    source_kind=info.source_kind,
                    exists=info.exists,
                    file_size_bytes=info.file_size_bytes,
                    last_write_time_utc=info.last_write_time_utc,
                    content_hash=info.content_hash,
                    rows_read=info.rows_read,
                    rows_accepted=len(rows),
                    rows_rejected=sum(rejections.values()),
                    rejection_reasons=dict(rejections),
                )
            )
        else:
            updated_sources.append(info)
    summary = summarize(rows, updated_sources, rejections)
    return rows, updated_sources, rejections, summary


def write_outputs(rows: list[dict[str, Any]], sources: list[SourceInfo], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, ROWS_CSV)
    ROWS_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SOURCE_MANIFEST_JSON.write_text(json.dumps([source.as_dict() for source in sources], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    INVENTORY_JSON.write_text(json.dumps([source.as_dict() for source in sources], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_inventory_markdown(sources, INVENTORY_MD)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover-sources", action="store_true", help="Include source discovery in the printed summary.")
    parser.add_argument("--write", action="store_true", help="Write dataset and audit artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build and print summary without writing artifacts.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Limit accepted rows for smoke testing.")
    args = parser.parse_args()

    rows, sources, _rejections, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(rows, sources, summary)

    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "market_count": summary["market_count"],
                "avg_brier_yes": summary["overall"]["avg_brier_yes"],
                "avg_logloss_yes": summary["overall"]["avg_logloss_yes"],
                "training_rows": summary["eligibility_counts"]["training"],
                "forward_promotion_rows": summary["eligibility_counts"]["forward_promotion"],
                "written": bool(args.write and not args.dry_run),
                "rows_csv": rel_path(ROWS_CSV),
                "audit_md": rel_path(SUMMARY_MD),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.discover_sources:
        existing = [source.as_dict() for source in sources if source.exists]
        print(json.dumps({"existing_sources": existing[:30], "existing_source_count": len(existing)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
