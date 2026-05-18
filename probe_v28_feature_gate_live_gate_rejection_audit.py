"""Read-only rejection audit for the active v28 feature-gate live stream.

This probe does not touch live bot logic or orders. It parses the current
feature-gate live execution events and summarizes which observable gate is
blocking entries, plus counterfactual pass counts for nearby ask floors.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_LOCK = ROOT / "state" / "live_trading.lock"
STORAGE_BY_STRATEGY_TAG = {
    "mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live": "live_mushroom_v28_feature_gate_size1",
    "mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live": "live_mushroom_v28_feature_gate_ask65_size1",
}
OUT_JSON = OUT_DIR / "v28_feature_gate_live_gate_rejection_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_live_gate_rejection_audit_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def load_events(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def pct(num: int, den: int) -> float:
    return (100.0 * num / den) if den else 0.0


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts_wall": row.get("ts_wall"),
        "market": row.get("market"),
        "side": row.get("side"),
        "reason": row.get("decision_reason") or row.get("mushroom_v28_reject_reason"),
        "ask": row.get("mushroom_v28_feature_gate_ask_prob"),
        "raw_edge_prob": row.get("mushroom_v28_feature_gate_raw_edge_prob"),
        "abs_d": row.get("mushroom_v28_abs_d_sigma"),
        "recross": row.get("mushroom_v28_feature_gate_recross_hazard_score"),
        "p_side": row.get("mushroom_v28_p_side"),
        "edge_cents": row.get("mushroom_v28_edge_cents"),
        "book_age_ms": row.get("mushroom_v28_book_age_ms"),
        "btc_age_ms": row.get("mushroom_v28_btc_age_ms"),
        "depth": row.get("mushroom_v28_depth_count"),
    }


def counterfactual_counts(decision_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = [
        {
            "variant": "raw05_recross60_abs085_no_ask",
            "raw_edge_min": 0.05,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": None,
        },
        {
            "variant": "raw05_recross60_abs085_ask55",
            "raw_edge_min": 0.05,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.55,
        },
        {
            "variant": "raw05_recross60_abs085_ask60",
            "raw_edge_min": 0.05,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.60,
        },
        {
            "variant": "raw05_recross60_abs085_ask65",
            "raw_edge_min": 0.05,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.65,
        },
        {
            "variant": "raw05_recross60_abs085_ask70",
            "raw_edge_min": 0.05,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.70,
        },
        {
            "variant": "frontier_raw03_recross60_abs85_ask35",
            "raw_edge_min": 0.03,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.35,
        },
        {
            "variant": "frontier_raw03_recross60_abs85_ask45",
            "raw_edge_min": 0.03,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.45,
        },
        {
            "variant": "frontier_raw03_recross60_abs85_ask55",
            "raw_edge_min": 0.03,
            "recross_max": 0.60,
            "abs_d_min": 0.85,
            "ask_min": 0.55,
        },
    ]
    out: list[dict[str, Any]] = []
    for variant in variants:
        label = str(variant["variant"])
        raw_edge_min = float(variant["raw_edge_min"])
        recross_max = float(variant["recross_max"])
        abs_d_min = float(variant["abs_d_min"])
        ask_min = variant["ask_min"]
        passed: list[dict[str, Any]] = []
        for row in decision_rows:
            raw_edge = as_float(row.get("mushroom_v28_feature_gate_raw_edge_prob"))
            recross = as_float(row.get("mushroom_v28_feature_gate_recross_hazard_score"))
            abs_d = as_float(row.get("mushroom_v28_abs_d_sigma"))
            ask = as_float(row.get("mushroom_v28_feature_gate_ask_prob"))
            if raw_edge is None or recross is None or abs_d is None or ask is None:
                continue
            if raw_edge < raw_edge_min or recross > recross_max or abs_d < abs_d_min:
                continue
            if ask_min is not None and ask < ask_min:
                continue
            passed.append(row)
        market_counts = Counter(str(row.get("market") or "") for row in passed if row.get("market"))
        out.append(
            {
                "variant": label,
                "rule": {
                    "raw_edge_min": raw_edge_min,
                    "recross_max": recross_max,
                    "abs_d_min": abs_d_min,
                    "ask_min": ask_min,
                },
                "ask_min": ask_min,
                "pass_count": len(passed),
                "sides": dict(Counter(str(row.get("side") or "") for row in passed)),
                "markets": sorted(market_counts),
                "market_counts": dict(market_counts.most_common()),
                "recent_examples": [compact_row(row) for row in passed[-5:]],
            }
        )
    return out


def build_report() -> dict[str, Any]:
    lock = load_json(LIVE_LOCK)
    strategy_tag = str(lock.get("strategy_tag") or "")
    storage_tag = STORAGE_BY_STRATEGY_TAG.get(strategy_tag, "")
    event_path = ROOT / "logs" / storage_tag / "execution_events.ndjson" if storage_tag else Path()
    rows = load_events(event_path)
    decision_rows = [
        row
        for row in rows
        if row.get("event_type") in {"mushroom_v28_rejected", "mushroom_v28_approved"}
        and row.get("mushroom_v28_status") == "ok"
    ]
    gate_rows = [
        row
        for row in decision_rows
        if row.get("mushroom_v28_feature_gate_enabled") is True
        and row.get("mushroom_v28_feature_gate_raw_edge_prob") is not None
    ]
    reason_counts = Counter(str(row.get("decision_reason") or row.get("mushroom_v28_reject_reason") or "") for row in decision_rows)
    side_counts = Counter(str(row.get("side") or "") for row in decision_rows)
    gate_counts = Counter()
    for row in gate_rows:
        for field, label in [
            ("mushroom_v28_feature_gate_raw_edge_ok", "raw_edge_ok"),
            ("mushroom_v28_feature_gate_recross_ok", "recross_ok"),
            ("mushroom_v28_feature_gate_abs_d_ok", "abs_d_ok"),
            ("mushroom_v28_feature_gate_ask_ok", "ask_ok"),
            ("mushroom_v28_feature_gate_pass", "feature_gate_pass"),
            ("mushroom_v28_model_price_ok", "model_price_ok"),
            ("mushroom_v28_book_ok", "book_ok"),
            ("mushroom_v28_btc_ok", "btc_ok"),
            ("mushroom_v28_risk_ok", "risk_ok"),
            ("mushroom_v28_balance_ok", "balance_ok"),
        ]:
            if as_bool(row.get(field)) is True:
                gate_counts[label] += 1

    raw_edges = [value for row in gate_rows if (value := as_float(row.get("mushroom_v28_feature_gate_raw_edge_prob"))) is not None]
    asks = [value for row in gate_rows if (value := as_float(row.get("mushroom_v28_feature_gate_ask_prob"))) is not None]
    abs_ds = [value for row in gate_rows if (value := as_float(row.get("mushroom_v28_abs_d_sigma"))) is not None]
    recrosses = [value for row in gate_rows if (value := as_float(row.get("mushroom_v28_feature_gate_recross_hazard_score"))) is not None]
    near_misses = sorted(
        gate_rows,
        key=lambda row: (
            as_float(row.get("mushroom_v28_feature_gate_raw_edge_prob")) or -999.0,
            as_float(row.get("mushroom_v28_abs_d_sigma")) or -999.0,
        ),
        reverse=True,
    )[:12]

    blocker_notes: list[str] = []
    if not storage_tag:
        blocker_notes.append("live_lock_not_mapped_to_feature_gate_storage")
    if not gate_rows:
        blocker_notes.append("no_feature_gate_decision_rows")
    else:
        total = len(gate_rows)
        if gate_counts["feature_gate_pass"] == 0:
            blocker_notes.append("zero_feature_gate_passes_observed")
        if gate_counts["raw_edge_ok"] < total:
            blocker_notes.append("raw_edge_is_primary_or_secondary_bottleneck")
        if gate_counts["abs_d_ok"] < total:
            blocker_notes.append("abs_d_boundary_geometry_filters_many_rows")
        if gate_counts["ask_ok"] < total:
            blocker_notes.append("ask_floor_filters_cheap_or_mid_contracts")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "live_lock": lock,
        "strategy_tag": strategy_tag,
        "storage_tag": storage_tag,
        "event_path": str(event_path),
        "event_rows": len(rows),
        "decision_rows": len(decision_rows),
        "feature_gate_rows": len(gate_rows),
        "reason_counts": dict(reason_counts.most_common()),
        "side_counts": dict(side_counts.most_common()),
        "gate_pass_counts": dict(gate_counts.most_common()),
        "gate_pass_rates_pct": {
            key: pct(gate_counts[key], len(gate_rows))
            for key in [
                "raw_edge_ok",
                "recross_ok",
                "abs_d_ok",
                "ask_ok",
                "feature_gate_pass",
                "model_price_ok",
                "book_ok",
                "btc_ok",
                "risk_ok",
                "balance_ok",
            ]
        },
        "feature_ranges": {
            "raw_edge_prob_min_median_max": [min(raw_edges), median(raw_edges), max(raw_edges)] if raw_edges else None,
            "ask_prob_min_median_max": [min(asks), median(asks), max(asks)] if asks else None,
            "abs_d_min_median_max": [min(abs_ds), median(abs_ds), max(abs_ds)] if abs_ds else None,
            "recross_min_median_max": [min(recrosses), median(recrosses), max(recrosses)] if recrosses else None,
        },
        "counterfactual_variants": counterfactual_counts(decision_rows),
        "near_misses": [compact_row(row) for row in near_misses],
        "blocker_notes": blocker_notes,
        "interpretation": [
            "This report is observational; counterfactual pass counts do not imply fills or profitability.",
            "If no-ask has many passes but ask65 has zero, the ask floor is the live coverage bottleneck.",
            "If no-ask also has zero passes, the current market simply did not show the raw-edge plus boundary geometry setup.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Live Gate Rejection Audit",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Strategy/storage: `{report.get('strategy_tag')}` / `{report.get('storage_tag')}`",
        f"- Event path: `{report.get('event_path')}`",
        f"- Events / decisions / feature rows: `{report.get('event_rows')}` / `{report.get('decision_rows')}` / `{report.get('feature_gate_rows')}`",
        f"- Reasons: `{report.get('reason_counts')}`",
        f"- Gate pass counts: `{report.get('gate_pass_counts')}`",
        f"- Gate pass rates pct: `{report.get('gate_pass_rates_pct')}`",
        f"- Feature ranges: `{report.get('feature_ranges')}`",
        f"- Blocker notes: `{', '.join(report.get('blocker_notes') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Counterfactual Pass Counts", ""])
    lines.append("| variant | ask min | pass count | sides | markets |")
    lines.append("|---|---:|---:|---|---|")
    for row in report.get("counterfactual_variants") or []:
        lines.append(
            f"| `{row.get('variant')}` | {row.get('ask_min')} | {row.get('pass_count')} | "
            f"`{row.get('sides')}` | `{row.get('markets')}` |"
        )
    lines.extend(["", "## Top Near Misses", ""])
    lines.append("| ts | market | side | reason | ask | raw edge | abs d | recross | p side | edge c |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|")
    for row in report.get("near_misses") or []:
        lines.append(
            f"| `{row.get('ts_wall')}` | `{row.get('market')}` | `{row.get('side')}` | `{row.get('reason')}` | "
            f"{row.get('ask')} | {row.get('raw_edge_prob')} | {row.get('abs_d')} | {row.get('recross')} | "
            f"{row.get('p_side')} | {row.get('edge_cents')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
