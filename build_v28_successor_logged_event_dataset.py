"""Build a labeled logged-event dataset for v28 successor diagnostics.

Research-only. This uses recorded v28 execution-event outputs as predecision
features and attaches market-level YES labels from the current seed dataset.
Because those labels come from the posthoc calibration seed, this dataset is
diagnostic only and never forward-promotable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from replay_v28_successor_baselines import (
    EXECUTION_EVENTS,
    SEED_ROWS_CSV,
    as_float,
    load_logged_v28_events,
    rel_path,
    sha256_file,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

LOGGED_ROWS_CSV = OUT_DIR / "causal_rows_logged_events_latest.csv"
LOGGED_ROWS_JSON = OUT_DIR / "causal_rows_logged_events_latest.json"
LOGGED_AUDIT_JSON = EDGE_DIR / "v28_successor_logged_event_dataset_audit_latest.json"
LOGGED_AUDIT_MD = EDGE_DIR / "v28_successor_logged_event_dataset_audit_latest.md"

EPS = 1e-12


def stable_hash(parts: list[Any]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(str(part if part is not None else "").encode("utf-8"))
        digest.update(b"\x1f")
    return digest.hexdigest()[:24]


def clamp_probability(value: Any) -> float:
    parsed = as_float(value)
    if parsed is None:
        return 0.5
    return min(1.0 - EPS, max(EPS, parsed))


def logloss(p: float, y: float) -> float:
    p = clamp_probability(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def read_seed_rows(limit_rows: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with SEED_ROWS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
    return rows


def label_lookup(seed_rows: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, Any]]:
    values: dict[str, set[float]] = {}
    for row in seed_rows:
        market = str(row.get("market_ticker") or "")
        label = as_float(row.get("y_yes_win"))
        if market and label is not None:
            values.setdefault(market, set()).add(1.0 if label >= 0.5 else 0.0)
    conflicts = {market: sorted(labels) for market, labels in values.items() if len(labels) > 1}
    lookup = {market: next(iter(labels)) for market, labels in values.items() if len(labels) == 1}
    summary = {
        "seed_rows": len(seed_rows),
        "label_markets": len(lookup),
        "conflicting_label_markets": len(conflicts),
        "conflicts": conflicts,
    }
    return lookup, summary


def iso_before(a: str | None, b: str | None) -> bool | None:
    if not a or not b:
        return None
    try:
        left = datetime.fromisoformat(str(a).replace("Z", "+00:00"))
        right = datetime.fromisoformat(str(b).replace("Z", "+00:00"))
    except ValueError:
        return None
    return left <= right


def parse_iso_ts(ts: Any) -> datetime | None:
    if not ts:
        return None
    try:
        parsed = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def add_seconds(ts: str | None, seconds: Any) -> str | None:
    if not ts:
        return None
    parsed_seconds = as_float(seconds)
    if parsed_seconds is None:
        return None
    try:
        base = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    close_ts = base.astimezone(timezone.utc) + timedelta(seconds=parsed_seconds)
    return close_ts.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def add_causal_path_memory(rows: list[dict[str, Any]]) -> None:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_market.setdefault(str(row.get("market_ticker") or ""), []).append(row)

    for market_rows in by_market.values():
        market_rows.sort(key=lambda row: (str(row.get("decision_ts_utc") or ""), str(row.get("source_line_or_offset") or "")))
        prior_count = 0
        first_btc: float | None = None
        prev_btc: float | None = None
        prev_ts: datetime | None = None
        min_btc: float | None = None
        max_btc: float | None = None
        for row in market_rows:
            current_btc = as_float(row.get("btc_price"))
            current_ts = parse_iso_ts(row.get("decision_ts_utc"))
            strike = as_float(row.get("strike"))
            sigma = as_float(row.get("sigma_t_dollars"))
            side = str(row.get("side") or "").lower()

            prior_range = 0.0 if min_btc is None or max_btc is None else max_btc - min_btc
            if side == "yes" and strike is not None and min_btc is not None:
                adverse = max(0.0, strike - min_btc)
            elif side == "no" and strike is not None and max_btc is not None:
                adverse = max(0.0, max_btc - strike)
            else:
                adverse = 0.0
            prior_recross = bool(
                prior_count > 0
                and strike is not None
                and min_btc is not None
                and max_btc is not None
                and min_btc <= strike <= max_btc
            )

            row["prior_logged_event_count"] = prior_count
            row["btc_drift_from_prev_event_dollars"] = 0.0 if current_btc is None or prev_btc is None else current_btc - prev_btc
            row["btc_drift_from_first_event_dollars"] = 0.0 if current_btc is None or first_btc is None else current_btc - first_btc
            row["prior_btc_path_range_dollars"] = prior_range
            row["prior_btc_path_range_per_sigma"] = 0.0 if sigma is None or abs(sigma) < 1e-9 else prior_range / sigma
            row["prior_adverse_path_memory_dollars"] = adverse
            row["prior_adverse_path_memory_per_sigma"] = 0.0 if sigma is None or abs(sigma) < 1e-9 else adverse / sigma
            row["prior_recross_seen"] = prior_recross
            row["btc_event_dt_seconds"] = (
                0.0
                if current_ts is None or prev_ts is None
                else max(0.0, (current_ts - prev_ts).total_seconds())
            )

            if current_btc is not None:
                if first_btc is None:
                    first_btc = current_btc
                prev_btc = current_btc
                min_btc = current_btc if min_btc is None else min(min_btc, current_btc)
                max_btc = current_btc if max_btc is None else max(max_btc, current_btc)
            if current_ts is not None:
                prev_ts = current_ts
            prior_count += 1


def event_to_row(event: dict[str, Any], y_yes: float) -> dict[str, Any]:
    market = str(event.get("market_ticker") or "")
    side = str(event.get("side") or "").lower()
    p_yes = clamp_probability(event.get("logged_p_yes"))
    p_no = 1.0 - p_yes
    p_side = clamp_probability(event.get("logged_p_side"))
    side_outcome = y_yes if side == "yes" else 1.0 - y_yes if side == "no" else y_yes
    decision_ts = event.get("event_ts_wall")
    close_ts = add_seconds(str(decision_ts) if decision_ts else None, event.get("logged_seconds_to_close"))
    pre_resolution = iso_before(str(decision_ts) if decision_ts else None, close_ts)
    row_id = stable_hash([event.get("event_source_file"), event.get("event_line"), market, side, event.get("logged_seconds_to_close"), p_yes])
    return {
        "row_id": row_id,
        "dataset_role": "logged_v28_event_with_seed_market_label",
        "source_file": event.get("event_source_file"),
        "source_line_or_offset": event.get("event_line"),
        "source_type": event.get("event_type"),
        "source_quality_tier": "logged_predecision_v28_output_with_posthoc_seed_label",
        "market_ticker": market,
        "market_close_ts_utc": close_ts,
        "market_close_ts_basis": "event_ts_wall_plus_logged_seconds_to_close",
        "decision_ts_utc": decision_ts,
        "decision_ts_basis": "execution_event_ts_wall",
        "side": side,
        "strike": event.get("logged_strike"),
        "strike_source": "logged_mushroom_v28_strike",
        "seconds_to_close": event.get("logged_seconds_to_close"),
        "v28_p_yes": p_yes,
        "v28_p_no": p_no,
        "v28_p_side": p_side,
        "v28_fair_yes_cents": event.get("logged_fair_yes_cents") if event.get("logged_fair_yes_cents") is not None else 100.0 * p_yes,
        "v28_fair_no_cents": event.get("logged_fair_no_cents") if event.get("logged_fair_no_cents") is not None else 100.0 * p_no,
        "v28_fair_side_cents": event.get("logged_fair_side_cents"),
        "v28_side_outcome": side_outcome,
        "y_yes_win": y_yes,
        "brier_yes": (p_yes - y_yes) ** 2,
        "logloss_yes": logloss(p_yes, y_yes),
        "ask_cents": event.get("logged_ask_cents"),
        "edge_cents": event.get("logged_edge_cents"),
        "sigma_t_dollars": event.get("logged_sigma_t_dollars"),
        "d_sigma": event.get("logged_d_sigma"),
        "abs_d_sigma": event.get("logged_abs_d_sigma"),
        "arrow": event.get("logged_arrow"),
        "btc_price": event.get("logged_btc_price"),
        "btc_age_ms": event.get("logged_btc_age_ms"),
        "book_age_ms": event.get("logged_book_age_ms"),
        "feed_age_ms": event.get("logged_feed_age_ms"),
        "history_bars": event.get("logged_history_bars"),
        "v28_status": event.get("v28_status"),
        "v28_version": event.get("v28_version"),
        "v28_approved": event.get("v28_approved"),
        "is_pre_resolution": bool(pre_resolution),
        "is_pre_resolution_registered": False,
        "is_recomputed_after_resolution": False,
        "is_backfilled": False,
        "is_simulated": False,
        "is_sidecar": True,
        "is_diagnostic_only": True,
        "allowed_for_training": True,
        "allowed_for_validation": True,
        "allowed_for_holdout": False,
        "allowed_for_forward_promotion": False,
        "label_source": "seed_market_outcome_from_posthoc_calibration",
        "exclusion_reason": "posthoc_seed_label_not_forward_registry",
    }


def build(limit_seed_rows: int | None = None, limit_events: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seed_rows = read_seed_rows(limit_rows=limit_seed_rows)
    labels, label_summary = label_lookup(seed_rows)
    events, event_summary = load_logged_v28_events(limit_events=limit_events)
    rows = [event_to_row(event, labels[str(event["market_ticker"])]) for event in events if str(event.get("market_ticker")) in labels]
    add_causal_path_memory(rows)
    summary = summarize(rows, label_summary, event_summary)
    return rows, summary


def summarize(rows: list[dict[str, Any]], label_summary: dict[str, Any], event_summary: dict[str, Any]) -> dict[str, Any]:
    missing_counts = {
        "strike": sum(1 for row in rows if as_float(row.get("strike")) is None),
        "decision_ts_utc": sum(1 for row in rows if not row.get("decision_ts_utc")),
        "btc_price": sum(1 for row in rows if as_float(row.get("btc_price")) is None),
        "book_age_ms": sum(1 for row in rows if as_float(row.get("book_age_ms")) is None),
        "d_sigma": sum(1 for row in rows if as_float(row.get("d_sigma")) is None),
        "arrow": sum(1 for row in rows if as_float(row.get("arrow")) is None),
        "prior_logged_event_count": sum(1 for row in rows if as_float(row.get("prior_logged_event_count")) is None),
        "prior_adverse_path_memory_dollars": sum(1 for row in rows if as_float(row.get("prior_adverse_path_memory_dollars")) is None),
        "y_yes_win": sum(1 for row in rows if as_float(row.get("y_yes_win")) is None),
    }
    by_event_type = dict(Counter(str(row.get("source_type")) for row in rows))
    by_side = dict(Counter(str(row.get("side")) for row in rows))
    avg_brier = None
    if rows:
        avg_brier = sum(float(row["brier_yes"]) for row in rows) / len(rows)
    return {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "inputs": {
            "seed_rows_csv": rel_path(SEED_ROWS_CSV),
            "seed_rows_hash": sha256_file(SEED_ROWS_CSV),
            "execution_events": event_summary,
        },
        "outputs": {
            "logged_rows_csv": rel_path(LOGGED_ROWS_CSV),
            "logged_rows_json": rel_path(LOGGED_ROWS_JSON),
            "audit_json": rel_path(LOGGED_AUDIT_JSON),
            "audit_md": rel_path(LOGGED_AUDIT_MD),
        },
        "row_count": len(rows),
        "market_count": len({row.get("market_ticker") for row in rows}),
        "label_summary": label_summary,
        "missing_counts": missing_counts,
        "by_event_type": by_event_type,
        "by_side": by_side,
        "avg_brier_yes": avg_brier,
        "pre_resolution_rows": sum(1 for row in rows if row.get("is_pre_resolution")),
        "eligibility_counts": {
            "training": sum(1 for row in rows if row.get("allowed_for_training")),
            "validation": sum(1 for row in rows if row.get("allowed_for_validation")),
            "holdout": sum(1 for row in rows if row.get("allowed_for_holdout")),
            "forward_promotion": sum(1 for row in rows if row.get("allowed_for_forward_promotion")),
        },
        "leakage_audit": {
            "status": "pass_for_logged_event_diagnostic_not_promotion",
            "notes": [
                "Logged v28 event fields are predecision outputs.",
                "Market labels are attached after resolution from the posthoc seed label lookup.",
                "Rows are diagnostic only and not allowed for forward promotion.",
            ],
        },
    }


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Logged Event Dataset Audit",
        "",
        "Research-only dataset built from recorded v28 execution-event outputs with posthoc seed labels attached by market. Live bot state, orders, thresholds, and processes were not touched.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Markets: `{summary['market_count']}`",
        f"- Avg YES Brier: `{summary['avg_brier_yes']}`",
        f"- Pre-resolution rows by event clock: `{summary['pre_resolution_rows']}`",
        f"- Forward-promotion rows: `{summary['eligibility_counts']['forward_promotion']}`",
        f"- Leakage status: `{summary['leakage_audit']['status']}`",
        "",
        "## Source Labels",
        "",
        f"- Seed rows read: `{summary['label_summary']['seed_rows']}`",
        f"- Labeled markets: `{summary['label_summary']['label_markets']}`",
        f"- Conflicting label markets: `{summary['label_summary']['conflicting_label_markets']}`",
        "",
        "## Missing Counts",
        "",
        "| field | missing rows |",
        "|---|---:|",
    ]
    for key, count in summary["missing_counts"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(["", "## By Event Type", "", "| event type | rows |", "|---|---:|"])
    for key, count in summary["by_event_type"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This dataset is richer than the calibration seed for strike, d_sigma, arrow, BTC price, and freshness features.",
            "- It is still diagnostic-only because labels come from the posthoc seed label lookup and no rows are frozen forward registry rows.",
            "- It should be used to develop feature plumbing and sanity checks, not to promote a live candidate.",
            "",
            "## Outputs",
            "",
            f"- Logged rows CSV: `{summary['outputs']['logged_rows_csv']}`",
            f"- Logged rows JSON: `{summary['outputs']['logged_rows_json']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(rows, LOGGED_ROWS_CSV)
    LOGGED_ROWS_JSON.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LOGGED_AUDIT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, LOGGED_AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build v28 successor logged-event dataset.")
    parser.add_argument("--write", action="store_true", help="Write logged-event dataset artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-seed-rows", type=int, default=None)
    parser.add_argument("--limit-events", type=int, default=None)
    args = parser.parse_args()

    rows, summary = build(limit_seed_rows=args.limit_seed_rows, limit_events=args.limit_events)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "market_count": summary["market_count"],
                "forward_promotion_rows": summary["eligibility_counts"]["forward_promotion"],
                "leakage_status": summary["leakage_audit"]["status"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
