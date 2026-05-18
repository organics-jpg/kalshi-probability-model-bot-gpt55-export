"""Join settlement labels to frozen v28 successor forward predictions.

Research-only. This is the post-resolution handoff after a prediction has
already been frozen before market close. It refuses to create supervised rows
unless the prediction was frozen before close and the label became available
only after resolution.

Current expected output is empty because there are no frozen forward
predictions yet.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

FROZEN_CSV = OUT_DIR / "frozen_forward_predictions_latest.csv"
SHADOW_LABELS_CSV = OUT_DIR / "shadow_forward_labeled_rows_latest.csv"
SIDECAR_BATCH_LABELS_CSV = OUT_DIR / "sidecar_bundle_batch_settlement_labels_latest.csv"

LABELED_CSV = OUT_DIR / "forward_labeled_predictions_latest.csv"
LABELED_JSON = OUT_DIR / "forward_labeled_predictions_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_forward_label_join_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_forward_label_join_latest.md"

EPS = 1e-9

OUTPUT_FIELDS = [
    "labeled_row_id",
    "label_join_status",
    "label_join_blockers",
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
    "candidate_edge_cents",
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
    "source_status",
    "y_yes_win",
    "settlement_price",
    "settlement_margin_dollars",
    "settlement_side",
    "settlement_ts_utc",
    "label_available_ts_utc",
    "settlement_source",
    "candidate_brier_yes",
    "candidate_logloss_yes",
    "v28_brier_yes",
    "v28_logloss_yes",
    "candidate_side_brier",
    "v28_side_brier",
    "probability_delta_brier_yes_vs_v28",
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


def clamp_probability(value: Any) -> float | None:
    parsed = as_float(value)
    if parsed is None:
        return None
    return min(1.0 - EPS, max(EPS, parsed))


def logloss(p: float | None, y: float | None) -> float | None:
    if p is None or y is None:
        return None
    p = min(1.0 - EPS, max(EPS, p))
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def brier(p: float | None, y: float | None) -> float | None:
    if p is None or y is None:
        return None
    return (p - y) ** 2


def fmt_float(value: Any, places: int = 10) -> str:
    parsed = as_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.{places}g}"


def fmt_cents(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


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


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def yes_label_from_row(row: dict[str, Any], strike: Any = None) -> float | None:
    explicit = as_float(row.get("y_yes_win") or row.get("yes_win") or row.get("settlement_yes"))
    if explicit is not None:
        return 1.0 if explicit >= 0.5 else 0.0
    result = str(row.get("binary_result") or row.get("result") or row.get("settlement_side") or "").strip().lower()
    if result in {"yes", "y", "above", "1", "true"}:
        return 1.0
    if result in {"no", "n", "below", "0", "false"}:
        return 0.0
    settlement_price = as_float(row.get("settlement_price"))
    parsed_strike = as_float(row.get("strike") if strike is None else strike)
    if settlement_price is None or parsed_strike is None:
        return None
    return 1.0 if settlement_price > parsed_strike else 0.0


def canonical_label(row: dict[str, Any], *, strike: Any = None) -> dict[str, Any]:
    market = str(row.get("market_ticker") or row.get("market") or "").strip()
    y_yes = yes_label_from_row(row, strike=strike)
    settlement_ts = parse_ts(row.get("settlement_ts_utc") or row.get("close_time") or row.get("resolved_ts_utc"))
    label_available_ts = parse_ts(row.get("label_available_ts_utc") or row.get("observed_ts_utc") or row.get("close_time") or row.get("settlement_ts_utc"))
    settlement_price = as_float(row.get("settlement_price"))
    parsed_strike = as_float(row.get("strike") if strike is None else strike)
    margin = None if settlement_price is None or parsed_strike is None else settlement_price - parsed_strike
    side = "yes" if y_yes == 1.0 else "no" if y_yes == 0.0 else ""
    return {
        "market_ticker": market,
        "y_yes_win": y_yes,
        "settlement_price": settlement_price,
        "settlement_margin_dollars": margin,
        "settlement_side": side,
        "settlement_ts_utc": iso_z(settlement_ts),
        "label_available_ts_utc": iso_z(label_available_ts),
        "settlement_source": row.get("label_source") or row.get("source") or row.get("settlement_source") or "unknown_label_source",
    }


def load_label_index(label_csvs: list[Path]) -> dict[str, dict[str, Any]]:
    by_market: dict[str, dict[str, Any]] = {}
    for path in label_csvs:
        for raw in read_csv_rows(path):
            label = canonical_label(raw)
            market = str(label.get("market_ticker") or "")
            if not market:
                continue
            existing = by_market.get(market)
            if existing is None:
                by_market[market] = label
                continue
            old_ts = parse_ts(existing.get("label_available_ts_utc"))
            new_ts = parse_ts(label.get("label_available_ts_utc"))
            if old_ts is None or (new_ts is not None and new_ts < old_ts):
                by_market[market] = label
    return by_market


def join_blockers(frozen: dict[str, Any], label: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    frozen_ts = parse_ts(frozen.get("frozen_utc"))
    decision_ts = parse_ts(frozen.get("decision_ts_utc"))
    close_ts = parse_ts(frozen.get("market_close_ts_utc"))
    if frozen_ts is None:
        blockers.append("missing_frozen_utc")
    if decision_ts is None:
        blockers.append("missing_decision_ts")
    if close_ts is None:
        blockers.append("missing_market_close_ts")
    if decision_ts is not None and close_ts is not None and decision_ts > close_ts:
        blockers.append("decision_after_close")
    if frozen_ts is not None and close_ts is not None and frozen_ts > close_ts:
        blockers.append("frozen_after_close")
    if label is None:
        blockers.append("missing_settlement_label")
        return blockers
    y_yes = as_float(label.get("y_yes_win"))
    settlement_ts = parse_ts(label.get("settlement_ts_utc"))
    available_ts = parse_ts(label.get("label_available_ts_utc"))
    if y_yes is None:
        blockers.append("missing_y_yes_win")
    if settlement_ts is None:
        blockers.append("missing_settlement_ts")
    if available_ts is None:
        blockers.append("missing_label_available_ts")
    if close_ts is not None and settlement_ts is not None and settlement_ts < close_ts:
        blockers.append("settlement_before_close")
    if close_ts is not None and available_ts is not None and available_ts < close_ts:
        blockers.append("label_available_before_close")
    if frozen_ts is not None and available_ts is not None and available_ts <= frozen_ts:
        blockers.append("label_available_not_after_freeze")
    return blockers


def join_rows(frozen_rows: list[dict[str, Any]], labels_by_market: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for frozen in frozen_rows:
        market = str(frozen.get("market_ticker") or "")
        label = labels_by_market.get(market)
        blockers = join_blockers(frozen, label)
        y_yes = as_float(label.get("y_yes_win")) if label else None
        candidate_p = clamp_probability(frozen.get("candidate_p_yes"))
        v28_p = clamp_probability(frozen.get("v28_p_yes"))
        side = str(frozen.get("side") or "").lower()
        side_y = y_yes if side == "yes" else 1.0 - y_yes if y_yes is not None and side == "no" else None
        candidate_side_p = candidate_p if side == "yes" else 1.0 - candidate_p if candidate_p is not None and side == "no" else None
        v28_side_p = v28_p if side == "yes" else 1.0 - v28_p if v28_p is not None and side == "no" else None
        candidate_brier = brier(candidate_p, y_yes)
        v28_brier = brier(v28_p, y_yes)
        row = {
            **{field: frozen.get(field, "") for field in OUTPUT_FIELDS if field in frozen},
            "labeled_row_id": stable_hash([frozen.get("frozen_prediction_id"), market, label.get("settlement_ts_utc") if label else "missing"]),
            "label_join_status": "joined_post_resolution" if not blockers else "blocked",
            "label_join_blockers": ";".join(blockers),
            "y_yes_win": fmt_float(y_yes),
            "settlement_price": fmt_cents(label.get("settlement_price") if label else None),
            "settlement_margin_dollars": fmt_cents(label.get("settlement_margin_dollars") if label else None),
            "settlement_side": label.get("settlement_side", "") if label else "",
            "settlement_ts_utc": label.get("settlement_ts_utc", "") if label else "",
            "label_available_ts_utc": label.get("label_available_ts_utc", "") if label else "",
            "settlement_source": label.get("settlement_source", "") if label else "",
            "candidate_brier_yes": fmt_float(candidate_brier),
            "candidate_logloss_yes": fmt_float(logloss(candidate_p, y_yes)),
            "v28_brier_yes": fmt_float(v28_brier),
            "v28_logloss_yes": fmt_float(logloss(v28_p, y_yes)),
            "candidate_side_brier": fmt_float(brier(candidate_side_p, side_y)),
            "v28_side_brier": fmt_float(brier(v28_side_p, side_y)),
            "probability_delta_brier_yes_vs_v28": fmt_float((candidate_brier - v28_brier) if candidate_brier is not None and v28_brier is not None else None),
        }
        for field in OUTPUT_FIELDS:
            row.setdefault(field, frozen.get(field, ""))
        out.append(row)
    return out


def summarize(frozen_rows: list[dict[str, Any]], attempted_rows: list[dict[str, Any]], output_rows: list[dict[str, Any]], label_csvs: list[Path], labels_by_market: dict[str, dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(row.get("label_join_status", "") for row in attempted_rows)
    blocker_counts: Counter[str] = Counter()
    for row in attempted_rows:
        for blocker in str(row.get("label_join_blockers") or "").split(";"):
            if blocker:
                blocker_counts[blocker] += 1
    joined = [row for row in output_rows if row.get("label_join_status") == "joined_post_resolution"]
    by_candidate: dict[str, dict[str, Any]] = {}
    for cid in sorted({str(row.get("candidate_id") or "") for row in joined}):
        rows = [row for row in joined if str(row.get("candidate_id") or "") == cid]
        if not rows:
            continue
        cand_briers = [as_float(row.get("candidate_brier_yes")) for row in rows]
        v28_briers = [as_float(row.get("v28_brier_yes")) for row in rows]
        cand_briers = [value for value in cand_briers if value is not None]
        v28_briers = [value for value in v28_briers if value is not None]
        by_candidate[cid] = {
            "rows": len(rows),
            "markets": len({row.get("market_ticker") for row in rows}),
            "candidate_brier_yes": sum(cand_briers) / len(cand_briers) if cand_briers else None,
            "v28_brier_yes": sum(v28_briers) / len(v28_briers) if v28_briers else None,
        }
    return {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "join_status": "joined_labels_available" if joined else "blocked_no_joined_forward_labels",
        "frozen_rows": len(frozen_rows),
        "label_source_rows": len(labels_by_market),
        "attempted_label_rows": len(attempted_rows),
        "labeled_rows": len(output_rows),
        "joined_rows": len(joined),
        "joined_markets": len({row.get("market_ticker") for row in joined}),
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "candidate_metrics": by_candidate,
        "promotion_status": {
            "allowed": False,
            "reason": "label join is necessary but not sufficient; source contract and promotion verifier must still pass",
        },
        "inputs": {
            "frozen_csv": rel_path(FROZEN_CSV),
            "frozen_hash": sha256_file(FROZEN_CSV),
            "label_csvs": [rel_path(path) for path in label_csvs],
            "label_hashes": {rel_path(path): sha256_file(path) for path in label_csvs},
        },
        "outputs": {
            "labeled_csv": rel_path(LABELED_CSV),
            "labeled_json": rel_path(LABELED_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }


def build(frozen_csv: Path = FROZEN_CSV, label_csvs: list[Path] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    label_csvs = label_csvs or [SIDECAR_BATCH_LABELS_CSV, SHADOW_LABELS_CSV]
    frozen_rows = read_csv_rows(frozen_csv)
    labels = load_label_index(label_csvs)
    attempted_rows = join_rows(frozen_rows, labels)
    output_rows = [row for row in attempted_rows if row.get("label_join_status") == "joined_post_resolution"]
    return output_rows, summarize(frozen_rows, attempted_rows, output_rows, label_csvs, labels)


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(OUTPUT_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Label Join",
        "",
        "Research-only post-resolution label join. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Join status: `{summary['join_status']}`",
        f"- Frozen rows: `{summary['frozen_rows']}`",
        f"- Label source markets: `{summary['label_source_rows']}`",
        f"- Attempted label rows: `{summary['attempted_label_rows']}`",
        f"- Labeled rows: `{summary['labeled_rows']}`",
        f"- Joined rows: `{summary['joined_rows']}`",
        f"- Joined markets: `{summary['joined_markets']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed']}`",
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
            "- Labels are joined only after the frozen prediction timestamp and market close are validated.",
            "- Empty output is expected until real frozen forward predictions exist.",
            "- This stage does not grant promotion by itself.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, LABELED_CSV)
    LABELED_JSON.write_text(json.dumps({"rows": rows[:500]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "sample_rows": rows[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write joined label artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--frozen-csv", type=Path, default=FROZEN_CSV, help="Frozen prediction CSV.")
    parser.add_argument("--labels-csv", type=Path, action="append", default=None, help="Settlement label CSV; can be provided multiple times.")
    args = parser.parse_args()
    rows, summary = build(frozen_csv=args.frozen_csv, label_csvs=args.labels_csv)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "join_status": summary["join_status"],
                "frozen_rows": summary["frozen_rows"],
                "labeled_rows": summary["labeled_rows"],
                "joined_rows": summary["joined_rows"],
                "joined_markets": summary["joined_markets"],
                "promotion_allowed": summary["promotion_status"]["allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
