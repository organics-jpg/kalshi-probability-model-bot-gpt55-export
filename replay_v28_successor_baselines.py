"""Audit logged v28 baselines for the v28 successor FV dataset.

Research-only. This script does not start, stop, or modify the live bot. It
streams recorded execution events, extracts logged v28 FV outputs, joins them
back to the current seed rows when possible, and reports whether each row has:

- a seed-only v28 baseline,
- a matching logged live v28 baseline,
- enough state for true v28 API recomputation.

The last category is expected to fail for the current seed because the
calibration rows do not include strike, BTC/bar history, or serialized engine
transport state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

SEED_ROWS_CSV = OUT_DIR / "causal_rows_seed_latest.csv"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"

REPLAY_AUDIT_CSV = OUT_DIR / "v28_baseline_replay_audit_latest.csv"
REPLAY_AUDIT_JSON = OUT_DIR / "v28_baseline_replay_audit_latest.json"
REPLAY_SUMMARY_JSON = EDGE_DIR / "v28_successor_baseline_replay_latest.json"
REPLAY_SUMMARY_MD = EDGE_DIR / "v28_successor_baseline_replay_latest.md"

MATCH_SECONDS_TOLERANCE = 2.0
EPS = 1e-12


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


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]


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


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def read_csv_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
    return rows


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


def iso_z(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def normalize_v28_event(record: dict[str, Any], line_number: int) -> dict[str, Any] | None:
    if "mushroom_v28_p_yes" not in record:
        return None
    market = record.get("market") or record.get("market_ticker")
    side = record.get("mushroom_v28_side") or record.get("side")
    seconds_to_close = as_float(record.get("mushroom_v28_seconds_to_close") or record.get("seconds_to_close"))
    p_yes = as_float(record.get("mushroom_v28_p_yes"))
    if not market or not side or seconds_to_close is None or p_yes is None:
        return None
    p_no = 1.0 - p_yes
    side_text = str(side).lower()
    p_side = as_float(record.get("mushroom_v28_p_side"))
    if p_side is None:
        p_side = p_yes if side_text == "yes" else p_no
    out = {
        "event_source_file": rel_path(EXECUTION_EVENTS),
        "event_line": line_number,
        "event_type": record.get("event_type"),
        "event_ts_wall": iso_z(record.get("ts_wall")),
        "market_ticker": str(market),
        "side": side_text,
        "v28_version": record.get("mushroom_v28_version"),
        "v28_status": record.get("mushroom_v28_status"),
        "v28_approved": as_bool(record.get("mushroom_v28_approved")),
        "logged_seconds_to_close": seconds_to_close,
        "logged_p_yes": p_yes,
        "logged_p_no": p_no,
        "logged_p_side": p_side,
        "logged_fair_yes_cents": as_float(record.get("mushroom_v28_fair_yes_cents")),
        "logged_fair_no_cents": as_float(record.get("mushroom_v28_fair_no_cents")),
        "logged_fair_side_cents": as_float(record.get("mushroom_v28_fair_side_cents")),
        "logged_ask_cents": as_float(record.get("mushroom_v28_ask_cents")),
        "logged_edge_cents": as_float(record.get("mushroom_v28_edge_cents")),
        "logged_sigma_t_dollars": as_float(record.get("mushroom_v28_sigma_t_dollars")),
        "logged_d_sigma": as_float(record.get("mushroom_v28_d_sigma")),
        "logged_abs_d_sigma": as_float(record.get("mushroom_v28_abs_d_sigma")),
        "logged_arrow": as_float(record.get("mushroom_v28_arrow")),
        "logged_strike": as_float(record.get("mushroom_v28_strike")),
        "logged_btc_price": as_float(record.get("mushroom_v28_btc_price")),
        "logged_btc_age_ms": as_float(record.get("mushroom_v28_btc_age_ms")),
        "logged_book_age_ms": as_float(record.get("mushroom_v28_book_age_ms") or record.get("book_age_ms")),
        "logged_feed_age_ms": as_float(record.get("feed_age_ms")),
        "logged_history_bars": as_float(record.get("mushroom_v28_history_bars")),
        "logged_transport_recent_n": as_float(record.get("mushroom_v28_transport_recent_n")),
        "logged_transport_long_n": as_float(record.get("mushroom_v28_transport_long_n")),
        "logged_p_anchor": as_float(record.get("mushroom_v28_p_anchor")),
        "logged_p_static_boundary_field": as_float(record.get("mushroom_v28_p_static_boundary_field")),
        "logged_p_recent_transport": as_float(record.get("mushroom_v28_p_recent_transport")),
        "logged_p_long_transport": as_float(record.get("mushroom_v28_p_long_transport")),
    }
    out["has_logged_v28_probability"] = out["logged_p_yes"] is not None
    out["has_logged_v28_boundary_components"] = all(
        out.get(key) is not None
        for key in [
            "logged_p_anchor",
            "logged_p_static_boundary_field",
            "logged_p_recent_transport",
            "logged_p_long_transport",
        ]
    )
    out["has_logged_v28_market_state"] = all(
        out.get(key) is not None
        for key in ["logged_strike", "logged_btc_price", "logged_ask_cents", "logged_seconds_to_close"]
    )
    out["true_api_recompute_ready"] = False
    out["api_recompute_blockers"] = (
        "missing_serialized_btc_tick_or_bar_sequence;"
        "missing_serialized_v28_engine_transport_state;"
        "execution_event_contains_outputs_not_full_predecision_engine_state"
    )
    return out


def load_logged_v28_events(limit_events: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    parse_errors = 0
    lines_read = 0
    if not EXECUTION_EVENTS.exists():
        return [], {"exists": False, "lines_read": 0, "parse_errors": 0}
    with EXECUTION_EVENTS.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if limit_events is not None and lines_read >= limit_events:
                break
            lines_read += 1
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue
            normalized = normalize_v28_event(record, line_number)
            if normalized is not None:
                events.append(normalized)
    summary = {
        "exists": True,
        "source_path": rel_path(EXECUTION_EVENTS),
        "source_hash": sha256_file(EXECUTION_EVENTS),
        "lines_read": lines_read,
        "parse_errors": parse_errors,
        "logged_v28_events": len(events),
        "logged_v28_markets": len({event["market_ticker"] for event in events}),
        "logged_v28_time_range": {
            "start": min((event["event_ts_wall"] for event in events if event.get("event_ts_wall")), default=None),
            "end": max((event["event_ts_wall"] for event in events if event.get("event_ts_wall")), default=None),
        },
        "event_type_counts": dict(Counter(str(event.get("event_type")) for event in events)),
    }
    return events, summary


def index_events(events: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    out: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        out[(str(event["market_ticker"]), str(event["side"]).lower())].append(event)
    for key in out:
        out[key].sort(key=lambda event: float(event["logged_seconds_to_close"]))
    return out


def nearest_event(row: dict[str, Any], events_by_key: dict[tuple[str, str], list[dict[str, Any]]]) -> tuple[dict[str, Any] | None, float | None]:
    key = (str(row.get("market_ticker") or ""), str(row.get("side") or "").lower())
    candidates = events_by_key.get(key, [])
    seed_seconds = as_float(row.get("seconds_to_close"))
    if seed_seconds is None or not candidates:
        return None, None
    best = min(candidates, key=lambda event: abs(float(event["logged_seconds_to_close"]) - seed_seconds))
    delta = abs(float(best["logged_seconds_to_close"]) - seed_seconds)
    if delta <= MATCH_SECONDS_TOLERANCE:
        return best, delta
    return None, delta


def delta_or_none(a: Any, b: Any) -> float | None:
    left = as_float(a)
    right = as_float(b)
    if left is None or right is None:
        return None
    return left - right


def classify_seed_recompute_readiness(row: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if as_float(row.get("strike")) is None:
        blockers.append("seed_missing_strike")
    if as_float(row.get("seconds_to_close")) is None:
        blockers.append("seed_missing_seconds_to_close")
    if as_float(row.get("v28_p_yes")) is None:
        blockers.append("seed_missing_logged_v28_p_yes")
    blockers.extend(
        [
            "seed_missing_predecision_btc_tick_or_bar_sequence",
            "seed_missing_predecision_orderbook_snapshot",
            "seed_missing_serialized_v28_engine_transport_state",
        ]
    )
    return False, blockers


def build_replay_rows(seed_rows: list[dict[str, Any]], logged_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events_by_key = index_events(logged_events)
    out: list[dict[str, Any]] = []
    for row in seed_rows:
        event, seconds_delta = nearest_event(row, events_by_key)
        seed_ready, seed_blockers = classify_seed_recompute_readiness(row)
        matched = event is not None
        base = {
            "row_id": row.get("row_id"),
            "market_ticker": row.get("market_ticker"),
            "side": row.get("side"),
            "decision_ts_utc": row.get("decision_ts_utc"),
            "market_close_ts_utc": row.get("market_close_ts_utc"),
            "seed_source_type": row.get("source_type"),
            "seed_source_quality_tier": row.get("source_quality_tier"),
            "seed_seconds_to_close": as_float(row.get("seconds_to_close")),
            "seed_v28_p_yes": as_float(row.get("v28_p_yes")),
            "seed_v28_p_side": as_float(row.get("v28_p_side")),
            "seed_v28_fair_yes_cents": as_float(row.get("v28_fair_yes_cents")),
            "seed_v28_fair_no_cents": as_float(row.get("v28_fair_no_cents")),
            "seed_sigma_t_dollars": as_float(row.get("sigma_t_dollars")),
            "seed_ask_cents": as_float(row.get("ask_cents")),
            "seed_edge_cents": as_float(row.get("edge_cents")),
            "seed_strike": as_float(row.get("strike")),
            "seed_is_posthoc": as_bool(row.get("is_recomputed_after_resolution")),
            "seed_allowed_for_forward_promotion": as_bool(row.get("allowed_for_forward_promotion")),
            "matched_logged_v28_event": matched,
            "nearest_logged_seconds_delta": seconds_delta,
            "baseline_replay_status": "matched_logged_v28_output" if matched else "seed_only_no_matching_logged_event",
            "seed_true_api_recompute_ready": seed_ready,
            "seed_api_recompute_blockers": ";".join(seed_blockers),
        }
        if event:
            base.update(event)
            base.update(
                {
                    "delta_seed_minus_logged_p_yes": delta_or_none(row.get("v28_p_yes"), event.get("logged_p_yes")),
                    "delta_seed_minus_logged_p_side": delta_or_none(row.get("v28_p_side"), event.get("logged_p_side")),
                    "delta_seed_minus_logged_fair_yes_cents": delta_or_none(row.get("v28_fair_yes_cents"), event.get("logged_fair_yes_cents")),
                    "delta_seed_minus_logged_sigma_t_dollars": delta_or_none(row.get("sigma_t_dollars"), event.get("logged_sigma_t_dollars")),
                    "delta_seed_minus_logged_ask_cents": delta_or_none(row.get("ask_cents"), event.get("logged_ask_cents")),
                    "delta_seed_minus_logged_edge_cents": delta_or_none(row.get("edge_cents"), event.get("logged_edge_cents")),
                    "logged_true_api_recompute_ready": event.get("true_api_recompute_ready"),
                    "logged_api_recompute_blockers": event.get("api_recompute_blockers"),
                }
            )
        else:
            base.update(
                {
                    "event_source_file": "",
                    "event_line": "",
                    "event_type": "",
                    "event_ts_wall": "",
                    "logged_true_api_recompute_ready": False,
                    "logged_api_recompute_blockers": "no_matching_logged_v28_event",
                }
            )
        out.append(base)
    return out


def finite_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = as_float(row.get(key))
        if value is not None:
            values.append(value)
    return values


def value_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "mean_abs": None, "max_abs": None}
    return {
        "count": len(values),
        "mean_abs": sum(abs(value) for value in values) / len(values),
        "max_abs": max(abs(value) for value in values),
    }


def summarize(seed_rows: list[dict[str, Any]], logged_summary: dict[str, Any], replay_rows: list[dict[str, Any]]) -> dict[str, Any]:
    matched = [row for row in replay_rows if as_bool(row.get("matched_logged_v28_event"))]
    seed_posthoc = sum(1 for row in seed_rows if as_bool(row.get("is_recomputed_after_resolution")))
    forward_allowed = sum(1 for row in seed_rows if as_bool(row.get("allowed_for_forward_promotion")))
    missing_seed = {
        "strike": sum(1 for row in seed_rows if as_float(row.get("strike")) is None),
        "decision_ts_utc": sum(1 for row in seed_rows if not row.get("decision_ts_utc")),
        "v28_p_yes": sum(1 for row in seed_rows if as_float(row.get("v28_p_yes")) is None),
        "sigma_t_dollars": sum(1 for row in seed_rows if as_float(row.get("sigma_t_dollars")) is None),
    }
    logged_missing = {
        "p_anchor": sum(1 for row in matched if as_float(row.get("logged_p_anchor")) is None),
        "p_static_boundary_field": sum(1 for row in matched if as_float(row.get("logged_p_static_boundary_field")) is None),
        "p_recent_transport": sum(1 for row in matched if as_float(row.get("logged_p_recent_transport")) is None),
        "p_long_transport": sum(1 for row in matched if as_float(row.get("logged_p_long_transport")) is None),
        "transport_recent_n": sum(1 for row in matched if as_float(row.get("logged_transport_recent_n")) is None),
        "transport_long_n": sum(1 for row in matched if as_float(row.get("logged_transport_long_n")) is None),
    }
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "inputs": {
            "seed_rows_csv": rel_path(SEED_ROWS_CSV),
            "seed_rows_hash": sha256_file(SEED_ROWS_CSV),
            "execution_events": logged_summary,
        },
        "outputs": {
            "replay_audit_csv": rel_path(REPLAY_AUDIT_CSV),
            "replay_audit_json": rel_path(REPLAY_AUDIT_JSON),
            "summary_json": rel_path(REPLAY_SUMMARY_JSON),
            "summary_md": rel_path(REPLAY_SUMMARY_MD),
        },
        "seed_rows": len(seed_rows),
        "seed_markets": len({row.get("market_ticker") for row in seed_rows}),
        "matched_logged_v28_rows": len(matched),
        "matched_logged_v28_markets": len({row.get("market_ticker") for row in matched}),
        "unmatched_seed_rows": len(replay_rows) - len(matched),
        "match_seconds_tolerance": MATCH_SECONDS_TOLERANCE,
        "seed_posthoc_rows": seed_posthoc,
        "seed_forward_promotion_rows": forward_allowed,
        "missing_seed_fields": missing_seed,
        "missing_logged_component_fields_on_matches": logged_missing,
        "delta_summaries": {
            "p_yes": value_summary(finite_values(matched, "delta_seed_minus_logged_p_yes")),
            "p_side": value_summary(finite_values(matched, "delta_seed_minus_logged_p_side")),
            "fair_yes_cents": value_summary(finite_values(matched, "delta_seed_minus_logged_fair_yes_cents")),
            "sigma_t_dollars": value_summary(finite_values(matched, "delta_seed_minus_logged_sigma_t_dollars")),
            "ask_cents": value_summary(finite_values(matched, "delta_seed_minus_logged_ask_cents")),
            "edge_cents": value_summary(finite_values(matched, "delta_seed_minus_logged_edge_cents")),
        },
        "baseline_replay_verdict": "logged_baseline_audited_true_api_recompute_blocked",
        "promotion_relevance": "diagnostic_only_not_forward_promotion_evidence",
        "blockers": [
            "current seed rows are posthoc calibration rows",
            "current seed rows have zero allowed_for_forward_promotion rows",
            "seed rows are missing strike",
            "true v28 API recomputation requires predecision BTC/bar sequence and serialized engine transport state",
        ],
        "audit_hash": stable_hash(replay_rows),
    }
    return summary


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Baseline Replay Audit",
        "",
        "Research-only baseline audit. This streamed recorded execution events and seed rows only; live bot code, state, orders, thresholds, and processes were not touched.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Seed rows: `{summary['seed_rows']}` across `{summary['seed_markets']}` markets",
        f"- Logged v28 events scanned: `{summary['inputs']['execution_events'].get('logged_v28_events')}`",
        f"- Matched seed rows to logged v28 outputs: `{summary['matched_logged_v28_rows']}`",
        f"- Unmatched seed rows: `{summary['unmatched_seed_rows']}`",
        f"- Match tolerance seconds: `{summary['match_seconds_tolerance']}`",
        f"- Verdict: `{summary['baseline_replay_verdict']}`",
        "",
        "## Seed Source Quality",
        "",
        f"- Posthoc seed rows: `{summary['seed_posthoc_rows']}`",
        f"- Forward-promotion seed rows: `{summary['seed_forward_promotion_rows']}`",
        "",
        "| missing seed field | rows |",
        "|---|---:|",
    ]
    for key, count in summary["missing_seed_fields"].items():
        lines.append(f"| `{key}` | {count} |")

    lines.extend(["", "## Logged Component Coverage On Matches", "", "| logged field | missing matched rows |", "|---|---:|"])
    for key, count in summary["missing_logged_component_fields_on_matches"].items():
        lines.append(f"| `{key}` | {count} |")

    lines.extend(["", "## Seed Minus Logged Delta", "", "| field | count | mean abs | max abs |", "|---|---:|---:|---:|"])
    for key, item in summary["delta_summaries"].items():
        lines.append(
            f"| `{key}` | {item['count']} | {fmt(item['mean_abs'])} | {fmt(item['max_abs'])} |"
        )

    lines.extend(["", "## Blockers", ""])
    for blocker in summary["blockers"]:
        lines.append(f"- {blocker}.")

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- A matching logged v28 row is useful baseline evidence, but it is not the same as a true v28 API replay.",
            "- True API replay still needs the exact predecision BTC/bar history and v28 engine state that existed before the row decision.",
            "- This audit keeps the promotion gate closed because the current seed remains posthoc and has no frozen-forward rows.",
            "",
            "## Outputs",
            "",
            f"- Replay audit CSV: `{summary['outputs']['replay_audit_csv']}`",
            f"- Replay audit JSON: `{summary['outputs']['replay_audit_json']}`",
            f"- Machine summary: `{summary['outputs']['summary_json']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "NA"
    return f"{parsed:.8f}"


def build(limit_rows: int | None = None, limit_events: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    seed_rows = read_csv_rows(SEED_ROWS_CSV, limit_rows=limit_rows)
    logged_events, logged_summary = load_logged_v28_events(limit_events=limit_events)
    replay_rows = build_replay_rows(seed_rows, logged_events)
    summary = summarize(seed_rows, logged_summary, replay_rows)
    return seed_rows, replay_rows, summary


def write_outputs(replay_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(replay_rows, REPLAY_AUDIT_CSV)
    REPLAY_AUDIT_JSON.write_text(json.dumps({"rows": replay_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPLAY_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, REPLAY_SUMMARY_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit v28 successor baseline replay evidence.")
    parser.add_argument("--write", action="store_true", help="Write replay audit artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional seed row limit.")
    parser.add_argument("--limit-events", type=int, default=None, help="Optional execution-event line limit.")
    args = parser.parse_args()

    _seed_rows, replay_rows, summary = build(limit_rows=args.limit_rows, limit_events=args.limit_events)
    if args.write and not args.dry_run:
        write_outputs(replay_rows, summary)
    print(
        json.dumps(
            {
                "seed_rows": summary["seed_rows"],
                "matched_logged_v28_rows": summary["matched_logged_v28_rows"],
                "unmatched_seed_rows": summary["unmatched_seed_rows"],
                "baseline_replay_verdict": summary["baseline_replay_verdict"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
