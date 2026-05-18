"""Validate v28 successor sidecar input bundles before packet collection.

Research-only. This checks the serialized handoff a passive recorder should
write before calling collect_v28_successor_forward_packets.py. It validates
market metadata, a Kalshi book checkpoint, BTC history available before the
checkpoint, a serialized v28 EdgeBatch, and frozen collection-candidate
manifests. It does not touch live bot state, orders, thresholds, secrets, or
processes.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_forward_packet_adapter import collection_manifests, demo_btc_history, demo_edge_batch
from collect_v28_successor_forward_packets import demo_market_and_checkpoint


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

TEMPLATE_JSON = OUT_DIR / "sidecar_input_bundle_template_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_sidecar_input_bundle_contract_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_sidecar_input_bundle_contract_latest.md"

REQUIRED_MARKET_FIELDS = ["market_ticker", "market_close_ts_utc", "strike"]
REQUIRED_CHECKPOINT_FIELDS = [
    "checkpoint_ts",
    "market_ticker",
    "yes_bid_prices",
    "yes_bid_sizes",
    "no_bid_prices",
    "no_bid_sizes",
]
REQUIRED_BTC_FIELDS = ["ts_utc", "price"]
REQUIRED_EDGE_FIELDS = [
    "p_yes",
    "p_no",
    "fair_yes_cents",
    "fair_no_cents",
    "yes_net_edge_cents",
    "no_net_edge_cents",
    "best_side",
    "best_edge_cents",
    "best_fair_cents",
]
REQUIRED_EDGE_COMPONENTS = [
    "p_anchor",
    "p_static_boundary_field",
    "p_recent_transport",
    "p_long_transport",
    "edge_gate",
    "static_gate",
    "arrow",
    "volshock",
    "transport_recent_n",
    "transport_long_n",
    "learned_horizon_minutes",
    "effective_horizon_minutes",
    "sigma_t_dollars",
    "d_sigma",
]
FORBIDDEN_PRE_FREEZE_KEYS = {
    "y_yes_win",
    "settlement_price",
    "settlement_ts_utc",
    "settlement_source",
    "settlement_margin_dollars",
    "settlement_side",
    "final_average_window_end_utc",
}
REQUIRED_MARKET_PREFIX = "KXBTC15M-"


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


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


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def has_value(row: dict[str, Any], field: str) -> bool:
    return field in row and str(row.get(field, "")).strip() != ""


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def scalar_at(value: Any, index: int = 0) -> Any:
    if isinstance(value, list):
        if not value:
            return None
        return value[index]
    return value


def jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if hasattr(value, "tolist"):
        return jsonable(value.tolist())
    return value


def serialize_edge_batch(edge_batch: Any) -> dict[str, Any]:
    return {
        "p_yes": jsonable(getattr(edge_batch, "p_yes", None)),
        "p_no": jsonable(getattr(edge_batch, "p_no", None)),
        "fair_yes_cents": jsonable(getattr(edge_batch, "fair_yes_cents", None)),
        "fair_no_cents": jsonable(getattr(edge_batch, "fair_no_cents", None)),
        "yes_net_edge_cents": jsonable(getattr(edge_batch, "yes_net_edge_cents", None)),
        "no_net_edge_cents": jsonable(getattr(edge_batch, "no_net_edge_cents", None)),
        "best_side": jsonable(getattr(edge_batch, "best_side", None)),
        "best_edge_cents": jsonable(getattr(edge_batch, "best_edge_cents", None)),
        "best_fair_cents": jsonable(getattr(edge_batch, "best_fair_cents", None)),
        "side_probability": jsonable(getattr(edge_batch, "side_probability", None)),
        "components": jsonable(getattr(edge_batch, "components", {}) or {}),
    }


def build_template_bundle() -> dict[str, Any]:
    market, checkpoint, registered_utc = demo_market_and_checkpoint()
    return {
        "bundle_schema": "v28_successor_sidecar_input_bundle_v1",
        "registered_utc": registered_utc,
        "simulated": True,
        "diagnostic_only": True,
        "market": market,
        "checkpoint": checkpoint,
        "btc_history_rows": demo_btc_history(),
        "edge_batch": serialize_edge_batch(demo_edge_batch()),
        "candidate_manifests": collection_manifests(),
        "notes": [
            "Template rows are synthetic and diagnostic only.",
            "Real bundles must be written before market close with only pre-decision BTC/book/v28 data.",
            "Settlement labels belong only after freeze and resolution.",
        ],
    }


def find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}"
            if key in FORBIDDEN_PRE_FREEZE_KEYS and str(item).strip() != "":
                found.append(path)
            found.extend(find_forbidden_keys(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_forbidden_keys(item, f"{prefix}[{index}]"))
    return found


def validate_bundle(bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    blockers: Counter[str] = Counter()
    details: list[dict[str, Any]] = []

    market = bundle.get("market") if isinstance(bundle.get("market"), dict) else {}
    checkpoint = bundle.get("checkpoint") if isinstance(bundle.get("checkpoint"), dict) else {}
    btc_history = bundle.get("btc_history_rows") or bundle.get("btc_history") or []
    edge_batch = bundle.get("edge_batch") if isinstance(bundle.get("edge_batch"), dict) else {}
    components = edge_batch.get("components") if isinstance(edge_batch.get("components"), dict) else {}
    manifests = bundle.get("candidate_manifests")
    if manifests is None:
        manifests = collection_manifests()

    for field in REQUIRED_MARKET_FIELDS:
        if not has_value(market, field):
            blockers[f"missing_market_field:{field}"] += 1
    for field in REQUIRED_CHECKPOINT_FIELDS:
        if not has_value(checkpoint, field):
            blockers[f"missing_checkpoint_field:{field}"] += 1
    if not isinstance(btc_history, list) or not btc_history:
        blockers["missing_btc_history_rows"] += 1
    else:
        for index, row in enumerate(btc_history):
            if not isinstance(row, dict):
                blockers["btc_history_row_not_object"] += 1
                continue
            for field in REQUIRED_BTC_FIELDS:
                if not has_value(row, field):
                    blockers[f"missing_btc_history_field:{field}"] += 1
            if as_float(row.get("price")) is None:
                blockers["btc_history_price_unparseable"] += 1
            details.append({"group": "btc_history", "row_index": index, "status": "checked"})

    for field in REQUIRED_EDGE_FIELDS:
        if scalar_at(edge_batch.get(field)) is None:
            blockers[f"missing_edge_batch_field:{field}"] += 1
    for field in REQUIRED_EDGE_COMPONENTS:
        if scalar_at(components.get(field)) is None:
            blockers[f"missing_edge_component:{field}"] += 1

    decision_ts = parse_ts(checkpoint.get("checkpoint_ts"))
    close_ts = parse_ts(market.get("market_close_ts_utc") or market.get("close_time"))
    registered_ts = parse_ts(bundle.get("registered_utc"))
    if decision_ts is None:
        blockers["checkpoint_ts_unparseable"] += 1
    if close_ts is None:
        blockers["market_close_ts_unparseable"] += 1
    if registered_ts is None:
        blockers["registered_utc_unparseable"] += 1
    if decision_ts is not None and close_ts is not None and decision_ts > close_ts:
        blockers["checkpoint_after_close"] += 1
    if registered_ts is not None and close_ts is not None and registered_ts > close_ts:
        blockers["registered_after_close"] += 1
    if isinstance(btc_history, list) and decision_ts is not None:
        for row in btc_history:
            if not isinstance(row, dict):
                continue
            tick_ts = parse_ts(row.get("ts_utc"))
            if tick_ts is None:
                blockers["btc_tick_ts_unparseable"] += 1
            elif tick_ts > decision_ts:
                blockers["btc_tick_after_checkpoint"] += 1

    market_ticker = str(market.get("market_ticker") or market.get("ticker") or "")
    checkpoint_ticker = str(checkpoint.get("market_ticker") or checkpoint.get("ticker") or "")
    if market_ticker and not market_ticker.startswith(REQUIRED_MARKET_PREFIX):
        blockers["market_not_btc15m_boundary"] += 1
    if market_ticker and checkpoint_ticker and market_ticker != checkpoint_ticker:
        blockers["market_checkpoint_ticker_mismatch"] += 1
    if as_float(market.get("strike")) is None:
        blockers["strike_unparseable"] += 1

    if not isinstance(manifests, list) or not manifests:
        blockers["missing_candidate_manifests"] += 1
    else:
        allowed_count = sum(1 for row in manifests if isinstance(row, dict) and as_bool(row.get("allowed_for_forward_collection")))
        if allowed_count <= 0:
            blockers["no_manifest_allowed_for_forward_collection"] += 1

    forbidden_paths = find_forbidden_keys(bundle)
    for _path in forbidden_paths:
        blockers["forbidden_pre_freeze_field_present"] += 1

    simulated = as_bool(bundle.get("simulated"))
    diagnostic = as_bool(bundle.get("diagnostic_only"))
    structural_blockers = dict(sorted(blockers.items()))
    ready = not structural_blockers
    if not ready:
        status = "blocked"
    elif simulated or diagnostic:
        status = "contract_demo_ready_not_evidence"
    else:
        status = "input_bundle_ready_for_collection"

    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "bundle_contract": "v28_successor_sidecar_input_bundle_v1",
        "bundle_status": status,
        "bundle_ready": ready,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "input bundles are pre-freeze collector inputs only; promotion requires frozen rows, post-resolution labels, source contract, forward evidence scoring, and promotion verifier",
        },
        "simulated": simulated,
        "diagnostic_only": diagnostic,
        "market_ticker": market_ticker,
        "decision_ts_utc": iso_z(decision_ts),
        "market_close_ts_utc": iso_z(close_ts),
        "registered_utc": iso_z(registered_ts),
        "btc_history_rows": len(btc_history) if isinstance(btc_history, list) else 0,
        "candidate_manifest_count": len(manifests) if isinstance(manifests, list) else 0,
        "forward_collection_candidate_count": sum(
            1 for row in manifests if isinstance(row, dict) and as_bool(row.get("allowed_for_forward_collection"))
        )
        if isinstance(manifests, list)
        else 0,
        "forbidden_pre_freeze_field_paths": forbidden_paths[:20],
        "blocker_counts": structural_blockers,
        "outputs": {
            "template_json": rel_path(TEMPLATE_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }
    return details, summary


def build(input_json: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if input_json is None:
        bundle = build_template_bundle()
        source_input = "generated_template_demo"
    else:
        payload = read_json(input_json)
        if not isinstance(payload, dict):
            raise ValueError("sidecar input bundle must be a JSON object")
        bundle = payload
        source_input = rel_path(input_json)
    details, summary = validate_bundle(bundle)
    summary["source_input"] = source_input
    report = {"summary": summary, "details": details[:200], "template_bundle": build_template_bundle()}
    return report, bundle


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Input Bundle Contract",
        "",
        "Research-only bundle validator. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Bundle status: `{summary['bundle_status']}`",
        f"- Bundle ready: `{summary['bundle_ready']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Source input: `{summary['source_input']}`",
        f"- Market: `{summary['market_ticker']}`",
        f"- BTC history rows: `{summary['btc_history_rows']}`",
        f"- Candidate manifests: `{summary['candidate_manifest_count']}`",
        f"- Forward-collection candidates: `{summary['forward_collection_candidate_count']}`",
        f"- Simulated: `{summary['simulated']}`",
        f"- Diagnostic only: `{summary['diagnostic_only']}`",
        "",
        "## Blockers",
        "",
        "| blocker | count |",
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
            "- This contract validates the serialized input before packet collection.",
            "- A ready bundle is still not evidence until packet rows are frozen before close and labeled only after resolution.",
            "- Simulated or diagnostic bundles must remain non-promotable.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], bundle: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_JSON.write_text(json.dumps(build_template_bundle(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, default=None, help="Optional sidecar input bundle JSON to validate. Defaults to generated synthetic template.")
    parser.add_argument("--write", action="store_true", help="Write bundle contract artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    report, bundle = build(input_json=args.input_json)
    if args.write and not args.dry_run:
        write_outputs(report, bundle)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "bundle_status": summary["bundle_status"],
                "bundle_ready": summary["bundle_ready"],
                "promotion_allowed": summary["promotion_allowed"],
                "blockers": summary["blocker_counts"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
