"""Collect v28 successor sidecar packet rows from pre-resolution checkpoints.

Research-only. This module is the executable bridge a passive recorder can call
when it has, at the same decision timestamp:

- Kalshi market metadata and top-of-book state;
- BTC tick/history state available before the checkpoint;
- a v28 EdgeBatch computed before close;
- frozen collection-candidate manifests.

The default CLI writes a deterministic contract demo only. Demo rows are
simulated and diagnostic, so they are never promotion evidence. Real collection
must call ``packet_rows_from_checkpoint`` during an open market and freeze the
rows before settlement using ``freeze_v28_successor_forward_candidates.py``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from build_v28_successor_forward_packet_adapter import (
    CANDIDATE_MANIFESTS_JSON,
    PACKET_FIELDS,
    build_candidate_packet_rows,
    collection_manifests,
    demo_btc_history,
    demo_edge_batch,
    iso_z,
    side_book_implied_yes,
)
from build_v28_successor_passive_forward_snapshots import as_float
from validate_v28_successor_forward_packet import FIELD_GROUPS, row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEMO_PACKETS_CSV = OUT_DIR / "forward_sidecar_packet_collection_demo_latest.csv"
DEMO_PACKETS_JSON = OUT_DIR / "forward_sidecar_packet_collection_demo_latest.json"
REAL_PACKETS_CSV = OUT_DIR / "forward_sidecar_packet_collection_latest.csv"
REAL_PACKETS_JSON = OUT_DIR / "forward_sidecar_packet_collection_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_sidecar_packet_collector_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_sidecar_packet_collector_latest.md"


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


def bool_text(value: bool) -> str:
    return "True" if value else "False"


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


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def listify(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    return [value]


def edge_batch_from_payload(payload: dict[str, Any]) -> Any:
    """Hydrate the minimal EdgeBatch shape needed by the packet adapter."""
    edge_payload = payload.get("edge_batch") if "edge_batch" in payload else payload
    if not isinstance(edge_payload, dict):
        raise ValueError("edge_batch payload must be a JSON object")
    components = edge_payload.get("components") or {}
    if not isinstance(components, dict):
        raise ValueError("edge_batch.components must be a JSON object")
    return SimpleNamespace(
        p_yes=listify(edge_payload.get("p_yes")),
        p_no=listify(edge_payload.get("p_no")),
        fair_yes_cents=listify(edge_payload.get("fair_yes_cents")),
        fair_no_cents=listify(edge_payload.get("fair_no_cents")),
        yes_net_edge_cents=listify(edge_payload.get("yes_net_edge_cents")),
        no_net_edge_cents=listify(edge_payload.get("no_net_edge_cents")),
        best_side=listify(edge_payload.get("best_side")),
        best_edge_cents=listify(edge_payload.get("best_edge_cents")),
        best_fair_cents=listify(edge_payload.get("best_fair_cents")),
        side_probability=listify(edge_payload.get("side_probability")),
        components=components,
    )


def seconds_to_close(decision_ts: Any, close_ts: Any) -> float | None:
    decision = parse_ts(decision_ts)
    close = parse_ts(close_ts)
    if decision is None or close is None:
        return None
    return (close - decision).total_seconds()


def best_price(values: Any) -> float | None:
    if not isinstance(values, list) or not values:
        return None
    return as_float(values[0])


def best_depth(values: Any) -> float:
    if not isinstance(values, list) or not values:
        return 0.0
    return float(as_float(values[0]) or 0.0)


def side_rows_from_checkpoint(
    *,
    market: dict[str, Any],
    checkpoint: dict[str, Any],
    registered_utc: str,
    source_file: str = "research_v28_successor_sidecar_packet_collector",
    source_line_or_offset: Any = "0",
    simulated: bool = False,
    diagnostic_only: bool = False,
) -> list[dict[str, Any]]:
    market_ticker = str(market.get("market_ticker") or market.get("ticker") or checkpoint.get("market_ticker") or "")
    close_ts = iso_z(parse_ts(market.get("market_close_ts_utc") or market.get("close_time")))
    decision_ts = iso_z(parse_ts(checkpoint.get("checkpoint_ts") or checkpoint.get("ts_wall") or registered_utc))
    strike = as_float(market.get("strike"))
    yes_bid = best_price(checkpoint.get("yes_bid_prices"))
    no_bid = best_price(checkpoint.get("no_bid_prices"))
    yes_ask = 100.0 - no_bid if no_bid is not None else None
    no_ask = 100.0 - yes_bid if yes_bid is not None else None
    yes_depth = best_depth(checkpoint.get("yes_bid_sizes"))
    no_depth = best_depth(checkpoint.get("no_bid_sizes"))
    book_mid_yes = None
    book_width = None
    if yes_bid is not None and yes_ask is not None:
        book_mid_yes = 0.5 * (yes_bid + yes_ask)
        book_width = max(0.0, yes_ask - yes_bid)
    is_pre = (seconds_to_close(decision_ts, close_ts) or -1.0) >= 0.0
    registered_pre = (seconds_to_close(registered_utc, close_ts) or -1.0) >= 0.0
    rows: list[dict[str, Any]] = []
    for side in ("yes", "no"):
        ask = yes_ask if side == "yes" else no_ask
        bid = yes_bid if side == "yes" else no_bid
        depth = yes_depth if side == "yes" else no_depth
        row_id = stable_hash([market_ticker, decision_ts, side, checkpoint.get("sequence_number"), source_file])
        rows.append(
            {
                "row_id": row_id,
                "market_ticker": market_ticker,
                "decision_ts_utc": decision_ts,
                "market_close_ts_utc": close_ts,
                "strike": "" if strike is None else f"{strike:.8g}",
                "seconds_to_close": "" if decision_ts == "" or close_ts == "" else f"{seconds_to_close(decision_ts, close_ts):.6f}",
                "side": side,
                "source_file": source_file,
                "source_line_or_offset": source_line_or_offset,
                "source_type": "v28_successor_sidecar_packet_checkpoint",
                "source_quality_tier": "native_predecision_sidecar_packet" if not simulated else "synthetic_contract_fixture_not_evidence",
                "is_pre_resolution": bool_text(is_pre),
                "is_pre_resolution_registered": bool_text(is_pre and registered_pre),
                "is_recomputed_after_resolution": "False",
                "is_backfilled": "False",
                "is_simulated": bool_text(simulated),
                "is_sidecar": "True",
                "is_diagnostic_only": bool_text(diagnostic_only),
                "allowed_for_forward_promotion": "False",
                "exclusion_reason": "not_frozen_candidate_prediction_registry",
                "yes_bid_cents": "" if yes_bid is None else f"{yes_bid:.6f}",
                "yes_ask_cents": "" if yes_ask is None else f"{yes_ask:.6f}",
                "no_bid_cents": "" if no_bid is None else f"{no_bid:.6f}",
                "no_ask_cents": "" if no_ask is None else f"{no_ask:.6f}",
                "ask_cents": "" if ask is None else f"{ask:.6f}",
                "bid_cents": "" if bid is None else f"{bid:.6f}",
                "book_implied_yes_from_side_ask": "" if ask is None else f"{side_book_implied_yes(side, ask):.10g}",
                "book_mid_yes_cents": "" if book_mid_yes is None else f"{book_mid_yes:.6f}",
                "book_width_cents": "" if book_width is None else f"{book_width:.6f}",
                "book_source_event_count": checkpoint.get("source_event_count", ""),
                "raw_capture_ts_utc": decision_ts,
                "depth": f"{depth:.6f}",
            }
        )
    return rows


def packet_rows_from_checkpoint(
    *,
    market: dict[str, Any],
    checkpoint: dict[str, Any],
    btc_history_rows: list[dict[str, Any]],
    edge_batch: Any,
    candidate_manifests: list[dict[str, Any]],
    registered_utc: str,
    simulated: bool = False,
    diagnostic_only: bool = False,
    source_file: str = "research_v28_successor_sidecar_packet_collector",
    source_line_or_offset: Any = "0",
) -> list[dict[str, Any]]:
    passive_rows = side_rows_from_checkpoint(
        market=market,
        checkpoint=checkpoint,
        registered_utc=registered_utc,
        simulated=simulated,
        diagnostic_only=diagnostic_only,
        source_file=source_file,
        source_line_or_offset=source_line_or_offset,
    )
    out: list[dict[str, Any]] = []
    for passive_row in passive_rows:
        out.extend(
            build_candidate_packet_rows(
                passive_row,
                btc_history_rows=btc_history_rows,
                edge_batch=edge_batch,
                candidate_manifests=candidate_manifests,
            )
        )
    return out


def packet_rows_from_input_bundle(
    *,
    input_bundle: dict[str, Any],
    registered_utc: str | None = None,
    candidate_manifests: list[dict[str, Any]] | None = None,
    source_file: str = "research_v28_successor_sidecar_packet_bundle",
    source_line_or_offset: Any = "bundle",
) -> list[dict[str, Any]]:
    market = input_bundle.get("market") or {}
    checkpoint = input_bundle.get("checkpoint") or {}
    btc_history_rows = input_bundle.get("btc_history_rows") or input_bundle.get("btc_history") or []
    edge_payload = input_bundle.get("edge_batch") or {}
    if not isinstance(market, dict):
        raise ValueError("input bundle market must be a JSON object")
    if not isinstance(checkpoint, dict):
        raise ValueError("input bundle checkpoint must be a JSON object")
    if not isinstance(btc_history_rows, list):
        raise ValueError("input bundle btc_history_rows must be a JSON array")
    edge_batch = edge_batch_from_payload(edge_payload)
    manifests = candidate_manifests
    if manifests is None:
        bundle_manifests = input_bundle.get("candidate_manifests")
        manifests = bundle_manifests if isinstance(bundle_manifests, list) else collection_manifests()
    bundle_registered_utc = registered_utc or str(input_bundle.get("registered_utc") or "").strip() or iso_now()
    return packet_rows_from_checkpoint(
        market=market,
        checkpoint=checkpoint,
        btc_history_rows=btc_history_rows,
        edge_batch=edge_batch,
        candidate_manifests=manifests,
        registered_utc=bundle_registered_utc,
        simulated=bool(input_bundle.get("simulated", False)),
        diagnostic_only=bool(input_bundle.get("diagnostic_only", False)),
        source_file=source_file,
        source_line_or_offset=source_line_or_offset,
    )


def build_from_input_bundle(
    *,
    input_json: Path,
    manifest_json: Path = CANDIDATE_MANIFESTS_JSON,
    registered_utc: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bundle = read_json(input_json)
    if not isinstance(bundle, dict):
        raise ValueError("input bundle must be a JSON object")
    manifests = bundle.get("candidate_manifests")
    if not isinstance(manifests, list):
        manifests = collection_manifests(manifest_json)
    rows = packet_rows_from_input_bundle(
        input_bundle=bundle,
        registered_utc=registered_utc,
        candidate_manifests=manifests,
        source_file=rel_path(input_json),
        source_line_or_offset="bundle",
    )
    return rows, summarize(rows, manifests, collector_mode="input_bundle", source_input=rel_path(input_json))


def demo_market_and_checkpoint() -> tuple[dict[str, Any], dict[str, Any], str]:
    decision = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
    close = datetime(2026, 5, 11, 12, 10, tzinfo=timezone.utc)
    market = {
        "market_ticker": "KXBTC15M-26MAY111210-100000",
        "market_close_ts_utc": iso_z(close),
        "strike": 100000.0,
    }
    checkpoint = {
        "checkpoint_ts": iso_z(decision),
        "market_ticker": market["market_ticker"],
        "yes_bid_prices": [52.0],
        "yes_bid_sizes": [120.0],
        "no_bid_prices": [46.0],
        "no_bid_sizes": [95.0],
        "sequence_number": 10,
        "source_event_count": 25,
    }
    return market, checkpoint, iso_z(decision)


def summarize(
    rows: list[dict[str, Any]],
    manifests: list[dict[str, Any]],
    *,
    collector_mode: str = "demo",
    source_input: str | None = None,
) -> dict[str, Any]:
    group_missing_counts: dict[str, int] = {group: 0 for group in FIELD_GROUPS}
    field_missing_counts: Counter[str] = Counter()
    temporal_blocker_counts: Counter[str] = Counter()
    for row in rows:
        for group in FIELD_GROUPS:
            missing = row_group_missing(row, group)
            if missing:
                group_missing_counts[group] += 1
            for field in missing:
                field_missing_counts[field] += 1
        for blocker in row_temporal_blockers(row):
            temporal_blocker_counts[blocker] += 1
    packet_ready_rows = [
        row
        for row in rows
        if not any(row_group_missing(row, group) for group in FIELD_GROUPS)
        and not row_temporal_blockers(row)
    ]
    simulated_rows = sum(1 for row in rows if str(row.get("is_simulated")).lower() == "true")
    diagnostic_rows = sum(1 for row in rows if str(row.get("is_diagnostic_only")).lower() == "true")
    if collector_mode == "demo":
        collector_status = "contract_demo_ready_not_evidence" if packet_ready_rows else "contract_demo_blocked"
        promotion_reason = "collector demo rows are simulated contract fixtures; real rows still require pre-close freeze, post-resolution labels, source contract, and promotion verifier"
    else:
        collector_status = "input_bundle_packet_ready_for_freeze_handoff" if packet_ready_rows else "input_bundle_packet_blocked"
        promotion_reason = "collector input bundles only create candidate packet rows; promotion still requires pre-close freeze, post-resolution labels, source contract, and promotion verifier"
    return {
        "generated_utc": iso_now(),
        "builder_script": Path(__file__).name,
        "collector_status": collector_status,
        "collector_mode": collector_mode,
        "input_modes": ["demo", "input_bundle_json"],
        "source_input": source_input,
        "rows": len(rows),
        "packet_ready_rows": len(packet_ready_rows),
        "markets": len({row.get("market_ticker") for row in rows if row.get("market_ticker")}),
        "demo_rows": len(rows),
        "demo_packet_ready_rows": len(packet_ready_rows),
        "demo_markets": len({row.get("market_ticker") for row in rows if row.get("market_ticker")}),
        "candidate_count": len(manifests),
        "simulated_rows": simulated_rows,
        "diagnostic_rows": diagnostic_rows,
        "group_missing_counts": group_missing_counts,
        "field_missing_counts_top": dict(field_missing_counts.most_common(20)),
        "temporal_blocker_counts": dict(sorted(temporal_blocker_counts.items())),
        "promotion_status": {
            "allowed": False,
            "reason": promotion_reason,
        },
        "outputs": {
            "demo_csv": rel_path(DEMO_PACKETS_CSV),
            "demo_json": rel_path(DEMO_PACKETS_JSON),
            "input_bundle_csv": rel_path(REAL_PACKETS_CSV),
            "input_bundle_json": rel_path(REAL_PACKETS_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }


def build_demo() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    market, checkpoint, registered_utc = demo_market_and_checkpoint()
    manifests = collection_manifests()
    rows = packet_rows_from_checkpoint(
        market=market,
        checkpoint=checkpoint,
        btc_history_rows=demo_btc_history(),
        edge_batch=demo_edge_batch(),
        candidate_manifests=manifests,
        registered_utc=registered_utc,
        simulated=True,
        diagnostic_only=True,
        source_file="research_v28_successor_sidecar_packet_collector_demo",
        source_line_or_offset="1",
    )
    return rows, summarize(rows, manifests)


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(PACKET_FIELDS + [key for row in rows for key in row.keys()]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    mode = summary.get("collector_mode") or "demo"
    lines = [
        "# v28 Successor Sidecar Packet Collector",
        "",
        "Research-only collector bridge. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Collector mode: `{mode}`",
        f"- Collector status: `{summary['collector_status']}`",
        f"- Rows: `{summary['rows']}`",
        f"- Packet-ready rows: `{summary['packet_ready_rows']}`",
        f"- Markets: `{summary['markets']}`",
        f"- Candidate manifests: `{summary['candidate_count']}`",
        f"- Simulated rows: `{summary['simulated_rows']}`",
        f"- Diagnostic rows: `{summary['diagnostic_rows']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed']}`",
        "",
        "## Missing Groups",
        "",
        "| group | rows missing |",
        "|---|---:|",
    ]
    for group, count in summary["group_missing_counts"].items():
        lines.append(f"| `{group}` | {count} |")
    lines.extend(["", "## Temporal Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["temporal_blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The demo proves the sidecar collector can emit complete YES/NO packet rows at checkpoint time.",
            "- Input-bundle mode lets a passive recorder write market, checkpoint, BTC history, v28 EdgeBatch, and candidate manifest payloads to disk without importing internals.",
            "- Demo, simulated, diagnostic, or after-the-fact rows must not be frozen or promoted.",
            "- Real collection should run during an open market and then run packet validation, preflight, freeze, registry, label join, and forward evidence scoring.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    if summary.get("collector_mode") == "input_bundle":
        csv_path = REAL_PACKETS_CSV
        json_path = REAL_PACKETS_JSON
    else:
        csv_path = DEMO_PACKETS_CSV
        json_path = DEMO_PACKETS_JSON
    write_csv_rows(rows, csv_path)
    json_path.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "sample_rows": rows[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, default=None, help="Optional real sidecar input bundle JSON containing market, checkpoint, btc_history_rows, edge_batch, and optional candidate_manifests.")
    parser.add_argument("--manifest-json", type=Path, default=CANDIDATE_MANIFESTS_JSON, help="Candidate manifest JSON for input-bundle mode when the bundle does not include candidate_manifests.")
    parser.add_argument("--registered-utc", default="", help="Override registered UTC for input-bundle mode; defaults to bundle registered_utc or current UTC.")
    parser.add_argument("--write", action="store_true", help="Write sidecar collector demo artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build demo rows in memory only.")
    args = parser.parse_args()
    if args.input_json is not None:
        rows, summary = build_from_input_bundle(
            input_json=args.input_json,
            manifest_json=args.manifest_json,
            registered_utc=args.registered_utc or None,
        )
    else:
        rows, summary = build_demo()
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "collector_status": summary["collector_status"],
                "collector_mode": summary["collector_mode"],
                "rows": summary["rows"],
                "packet_ready_rows": summary["packet_ready_rows"],
                "promotion_allowed": summary["promotion_status"]["allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
