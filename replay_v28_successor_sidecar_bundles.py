"""Replay recorded sidecar input bundles through the v28 FV engine.

Research-only. This verifies that serialized pre-resolution market/book/BTC
bundles can reproduce the stored v28 EdgeBatch payload without touching live bot
state, order logic, thresholds, secrets, or processes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_public_rest_sidecar_bundle import edge_batch_from_btc_rows
from validate_v28_successor_sidecar_input_bundle import serialize_edge_batch


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

DEFAULT_BUNDLE_DIR = OUT_DIR / "sidecar_input_bundles"
REPLAY_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_replay_latest.json"
REPLAY_MD = EDGE_DIR / "v28_successor_sidecar_bundle_replay_latest.md"
REPLAY_CSV = EDGE_DIR / "v28_successor_sidecar_bundle_replay_latest.csv"

TOLERANCE = 1e-9

COMPARE_FIELDS = [
    ("p_yes", None),
    ("p_no", None),
    ("fair_yes_cents", None),
    ("fair_no_cents", None),
    ("yes_net_edge_cents", None),
    ("no_net_edge_cents", None),
    ("best_edge_cents", None),
    ("best_fair_cents", None),
    ("side_probability", None),
    ("components", "p_anchor"),
    ("components", "p_static_boundary_field"),
    ("components", "p_recent_transport"),
    ("components", "p_long_transport"),
    ("components", "edge_gate"),
    ("components", "static_gate"),
    ("components", "arrow"),
    ("components", "volshock"),
    ("components", "transport_recent_n"),
    ("components", "transport_long_n"),
    ("components", "learned_horizon_minutes"),
    ("components", "effective_horizon_minutes"),
    ("components", "sigma_t_dollars"),
    ("components", "d_sigma"),
]


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar(value: Any, index: int = 0) -> Any:
    if isinstance(value, list):
        return value[index] if len(value) > index else None
    return value


def numeric(value: Any) -> float | None:
    value = scalar(value)
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def payload_value(payload: dict[str, Any], field: str, component: str | None) -> Any:
    if component is None:
        if field == "p_no" and payload.get("p_no") is None and payload.get("p_yes") is not None:
            p_yes = numeric(payload.get("p_yes"))
            return None if p_yes is None else 1.0 - p_yes
        return scalar(payload.get(field))
    components = payload.get(field)
    if not isinstance(components, dict):
        return None
    return scalar(components.get(component))


def discover_bundle_paths(bundle_dir: Path, explicit_inputs: list[Path] | None = None) -> list[Path]:
    if explicit_inputs:
        return sorted({path.resolve() for path in explicit_inputs})
    if not bundle_dir.exists():
        return []
    return sorted(path for path in bundle_dir.glob("*.json") if path.is_file())


def replay_one(path: Path) -> dict[str, Any]:
    try:
        bundle = read_json(path)
    except Exception as exc:
        return {
            "bundle_path": rel_path(path),
            "market_ticker": "",
            "status": "blocked",
            "blockers": f"bundle_json_read_error:{type(exc).__name__}",
            "max_abs_delta": None,
        }

    market = bundle.get("market") if isinstance(bundle, dict) else None
    checkpoint = bundle.get("checkpoint") if isinstance(bundle, dict) else None
    btc_rows = bundle.get("btc_history_rows") if isinstance(bundle, dict) else None
    stored = bundle.get("edge_batch") if isinstance(bundle, dict) else None
    market_ticker = str((market or {}).get("market_ticker") or "")
    if not isinstance(market, dict) or not isinstance(checkpoint, dict) or not isinstance(btc_rows, list) or not isinstance(stored, dict):
        return {
            "bundle_path": rel_path(path),
            "market_ticker": market_ticker,
            "registered_utc": bundle.get("registered_utc") if isinstance(bundle, dict) else "",
            "status": "blocked",
            "blockers": "missing_market_checkpoint_btc_rows_or_edge_batch",
            "max_abs_delta": None,
        }

    try:
        replayed = serialize_edge_batch(edge_batch_from_btc_rows(btc_rows=btc_rows, market=market, checkpoint=checkpoint))
    except Exception as exc:
        return {
            "bundle_path": rel_path(path),
            "market_ticker": market_ticker,
            "registered_utc": bundle.get("registered_utc", ""),
            "status": "blocked",
            "blockers": f"v28_replay_error:{type(exc).__name__}",
            "max_abs_delta": None,
        }

    deltas: list[float] = []
    missing_fields: list[str] = []
    for field, component in COMPARE_FIELDS:
        name = field if component is None else f"{field}.{component}"
        old = numeric(payload_value(stored, field, component))
        new = numeric(payload_value(replayed, field, component))
        if old is None or new is None:
            missing_fields.append(name)
            continue
        deltas.append(abs(new - old))

    max_delta = max(deltas) if deltas else None
    blockers: list[str] = []
    if missing_fields:
        blockers.append("missing_compare_fields:" + ",".join(missing_fields))
    if max_delta is None:
        blockers.append("no_numeric_fields_compared")
    elif max_delta > TOLERANCE:
        blockers.append("replay_delta_exceeds_tolerance")

    return {
        "bundle_path": rel_path(path),
        "bundle_hash": sha256_file(path),
        "market_ticker": market_ticker,
        "registered_utc": bundle.get("registered_utc", ""),
        "decision_ts_utc": (checkpoint or {}).get("checkpoint_ts", ""),
        "market_close_ts_utc": (market or {}).get("market_close_ts_utc", ""),
        "status": "pass" if not blockers else "fail",
        "blockers": ";".join(blockers),
        "compared_fields": len(deltas),
        "missing_compare_fields": len(missing_fields),
        "max_abs_delta": max_delta,
    }


def build(
    bundle_dir: Path = DEFAULT_BUNDLE_DIR,
    input_jsons: list[Path] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    paths = discover_bundle_paths(bundle_dir, input_jsons)
    rows = [replay_one(path) for path in paths]
    replayed = [row for row in rows if row.get("status") == "pass"]
    failed = [row for row in rows if row.get("status") == "fail"]
    blocked = [row for row in rows if row.get("status") == "blocked"]
    max_delta_values = [float(row["max_abs_delta"]) for row in rows if row.get("max_abs_delta") is not None]
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "replay_status": "pass" if rows and not failed and not blocked else "blocked_no_bundles" if not rows else "fail",
        "bundle_dir": rel_path(bundle_dir),
        "bundle_count": len(paths),
        "replayed_bundle_count": len(replayed),
        "failed_bundle_count": len(failed),
        "blocked_bundle_count": len(blocked),
        "market_count": len({row.get("market_ticker") for row in replayed if row.get("market_ticker")}),
        "compare_field_count": len(COMPARE_FIELDS),
        "max_abs_delta": max(max_delta_values) if max_delta_values else None,
        "tolerance": TOLERANCE,
        "promotion_allowed": False,
        "outputs": {
            "json": rel_path(REPLAY_JSON),
            "csv": rel_path(REPLAY_CSV),
            "markdown": rel_path(REPLAY_MD),
        },
    }
    return rows, summary


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    REPLAY_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = [
        "bundle_path",
        "bundle_hash",
        "market_ticker",
        "registered_utc",
        "decision_ts_utc",
        "market_close_ts_utc",
        "status",
        "blockers",
        "compared_fields",
        "missing_compare_fields",
        "max_abs_delta",
    ]
    with REPLAY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# v28 Successor Sidecar Bundle Replay",
        "",
        "Research-only replay audit for recorded sidecar market/book/BTC bundles. Live trading code, state, orders, thresholds, and secrets were not touched.",
        "",
        "## Summary",
        "",
        f"- Replay status: `{summary['replay_status']}`",
        f"- Bundles: `{summary['bundle_count']}`",
        f"- Replayed bundles: `{summary['replayed_bundle_count']}`",
        f"- Failed bundles: `{summary['failed_bundle_count']}`",
        f"- Blocked bundles: `{summary['blocked_bundle_count']}`",
        f"- Markets: `{summary['market_count']}`",
        f"- Max absolute delta: `{summary['max_abs_delta']}`",
        f"- Tolerance: `{summary['tolerance']}`",
    ]
    REPLAY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    parser.add_argument("--input-json", action="append", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build(bundle_dir=args.bundle_dir, input_jsons=args.input_json)
    if args.write:
        write_outputs(rows, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
