"""Current-denominator size proxy for feature-gate raw03 marginal rows.

Research-only; no live bot changes, no process control, no orders.

This tests whether continuous notional shrinkage on raw03-only coverage rows
can make the current feature-gate branch cleaner than a hard raw03/raw05
choice. It uses only the latest feature-gate artifact.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
FORWARD_COLLECTION_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"

OUT_JSON = OUT_DIR / "v28_feature_gate_current_margin_size_proxy_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_current_margin_size_proxy_latest.md"

TARGET_COVERAGE = 75.0
MAX_SOURCE_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.1f}c (${cents / 100.0:.2f})"


def row_key(row: dict[str, Any]) -> tuple[Any, Any]:
    return row.get("market"), row.get("side")


def source_risky(row: dict[str, Any]) -> bool:
    return row.get("source") != "approved_entry"


def find_variant(feature_gate: dict[str, Any], lane_name: str, candidate: str) -> tuple[dict[str, Any], int]:
    for lane in feature_gate.get("lanes") or []:
        if lane.get("lane") != lane_name:
            continue
        for variant in lane.get("variants") or []:
            if variant.get("candidate") == candidate:
                return variant, int(lane.get("future_denominator") or 0)
    return {}, 0


def summarize_policy(
    lane_name: str,
    denominator: int,
    anchor: dict[str, Any],
    broad: dict[str, Any],
    marginal_weight: float,
    live_net: float,
    live_collection_healthy: bool,
) -> dict[str, Any]:
    anchor_rows = [row for row in (anchor.get("rows") or []) if isinstance(row, dict)]
    broad_rows = [row for row in (broad.get("rows") or []) if isinstance(row, dict)]
    anchor_keys = {row_key(row) for row in anchor_rows}
    selected_rows = []
    marginal_rows = []
    for row in anchor_rows:
        enriched = dict(row)
        enriched["is_marginal"] = False
        enriched["weight"] = 1.0
        enriched["weighted_net_cents"] = fnum(row.get("net_cents"))
        selected_rows.append(enriched)
    for row in broad_rows:
        if row_key(row) in anchor_keys or marginal_weight <= 0:
            continue
        weight = marginal_weight
        enriched = dict(row)
        enriched["is_marginal"] = True
        enriched["weight"] = weight
        enriched["weighted_net_cents"] = fnum(row.get("net_cents")) * weight
        selected_rows.append(enriched)
        marginal_rows.append(enriched)
    entries = len(selected_rows)
    settled = sum(1 for row in selected_rows if row.get("side_won") is not None)
    coverage = (entries / denominator * 100.0) if denominator else 0.0
    weighted_net = sum(fnum(row.get("weighted_net_cents")) for row in selected_rows)
    row_risky = sum(1 for row in selected_rows if source_risky(row))
    row_source_share = row_risky / entries if entries else 0.0
    exposure_total = sum(fnum(row.get("weight")) for row in selected_rows)
    exposure_risky = sum(fnum(row.get("weight")) for row in selected_rows if source_risky(row))
    exposure_source_share = exposure_risky / exposure_total if exposure_total else 0.0
    marginal_net = sum(fnum(row.get("net_cents")) for row in marginal_rows)
    marginal_weighted_net = sum(fnum(row.get("weighted_net_cents")) for row in marginal_rows)
    marginal_risky_rows = sum(1 for row in marginal_rows if source_risky(row))
    blockers = ["research_only", "not_frozen_as_size_policy"]
    if coverage < TARGET_COVERAGE:
        blockers.append("coverage_too_low")
    if row_source_share > MAX_SOURCE_SHARE:
        blockers.append("row_source_share_gt_35pct")
    if exposure_source_share > MAX_SOURCE_SHARE:
        blockers.append("exposure_source_share_gt_35pct")
    if weighted_net < MIN_FULL_LOSS_CUSHION_CENTS:
        blockers.append("weighted_full_loss_cushion_lt_3")
    if weighted_net < live_net:
        blockers.append("does_not_beat_live_snapshot")
    if not live_collection_healthy:
        blockers.append("fresh_v28_live_collection_unhealthy")
    return {
        "lane": lane_name,
        "policy": f"raw05_anchor_plus_raw03_marginal_weight_{marginal_weight:g}",
        "marginal_weight": marginal_weight,
        "denominator": denominator,
        "entries": entries,
        "settled": settled,
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "row_source_share": row_source_share,
        "exposure_source_share": exposure_source_share,
        "full_loss_cushion": int(max(0.0, weighted_net) // 100.0),
        "live_snapshot_net_cents": live_net,
        "delta_vs_live_snapshot_cents": weighted_net - live_net,
        "marginal_rows": len(marginal_rows),
        "marginal_net_cents": marginal_net,
        "marginal_weighted_net_cents": marginal_weighted_net,
        "marginal_risky_rows": marginal_risky_rows,
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    feature_gate = load_json(FEATURE_GATE_JSON)
    live = load_json(CANDIDATE_VS_LIVE_JSON)
    forward = load_json(FORWARD_COLLECTION_JSON)
    live_net = fnum(live.get("live_net_cents"))
    live_blockers = forward.get("blockers") or []
    live_collection_healthy = (
        "live_watchdog_restart_failed" not in live_blockers
        and "live_lock_not_v28" not in live_blockers
    )
    weights = [1.0, 0.5, 0.25, 0.125, 0.05, 0.0]
    rows = []
    for lane_name in ["post_feature_freeze_entry", "post_feature_freeze_bridge"]:
        anchor, denominator = find_variant(feature_gate, lane_name, f"{lane_name}_raw05_recross60_abs085")
        broad, denominator2 = find_variant(feature_gate, lane_name, f"{lane_name}_raw03_recross70_abs075")
        denominator = denominator or denominator2
        for weight in weights:
            rows.append(summarize_policy(lane_name, denominator, anchor, broad, weight, live_net, live_collection_healthy))
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum(row.get("weighted_net_cents")),
            fnum(row.get("row_source_share")),
        )
    )
    clean_exposure_rows = [
        row for row in rows
        if row["coverage_pct"] >= TARGET_COVERAGE
        and row["exposure_source_share"] <= MAX_SOURCE_SHARE
        and row["weighted_net_cents"] >= MIN_FULL_LOSS_CUSHION_CENTS
    ]
    official_clean_rows = [
        row for row in clean_exposure_rows
        if row["row_source_share"] <= MAX_SOURCE_SHARE
    ]
    blockers = ["research_only", "not_promotion_evidence"]
    if clean_exposure_rows and not official_clean_rows:
        blockers.append("exposure_clean_but_row_source_blocked")
    if not official_clean_rows:
        blockers.append("no_policy_clears_official_row_source_gate")
    if "live_watchdog_restart_failed" in live_blockers:
        blockers.append("fresh_v28_live_collection_unhealthy")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_gate_generated_at_utc": feature_gate.get("generated_at_utc"),
        "feature_gate_freeze_ts_utc": (feature_gate.get("state") or {}).get("freeze_ts_utc"),
        "candidate_vs_live_generated_at_utc": live.get("generated_at_utc"),
        "live_snapshot_net_cents": live_net,
        "live_collection_healthy": live_collection_healthy,
        "rows": rows,
        "best_exposure_clean": clean_exposure_rows[0] if clean_exposure_rows else {},
        "best_official_clean": official_clean_rows[0] if official_clean_rows else {},
        "blockers": blockers,
        "interpretation": [
            "Marginal-size shrinkage can make exposure-source share look cleaner, but official row-source share remains above the 35% gate whenever raw03-only coverage rows are kept.",
            "Zeroing marginal rows restores the cleaner raw05 source profile, but then coverage drops below target.",
            "The current-denominator size proxy is therefore useful risk-sizing context, not a promotion repair.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best_exp = report.get("best_exposure_clean") or {}
    lines = [
        "# v28 Feature-Gate Current Marginal Size Proxy",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate generated UTC: `{report.get('feature_gate_generated_at_utc')}`",
        f"- Live snapshot net: `{money(report.get('live_snapshot_net_cents'))}`",
        f"- Best exposure-clean policy: `{best_exp.get('lane')}` / `{best_exp.get('policy')}`",
        f"- Best exposure-clean coverage/net/row-source/exposure-source: `{fnum(best_exp.get('coverage_pct')):.2f}%` / `{money(best_exp.get('weighted_net_cents'))}` / `{fnum(best_exp.get('row_source_share')):.3f}` / `{fnum(best_exp.get('exposure_source_share')):.3f}`",
        f"- Official clean policy: `{(report.get('best_official_clean') or {}).get('policy')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Policies",
        "",
        "| lane | policy | entries/settled | coverage | weighted net | row source | exposure source | cushion | delta live | marginal rows/net | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('policy')}` | {row.get('entries')}/{row.get('settled')} | "
            f"{fnum(row.get('coverage_pct')):.2f}% | {money(row.get('weighted_net_cents'))} | "
            f"{fnum(row.get('row_source_share')):.3f} | {fnum(row.get('exposure_source_share')):.3f} | "
            f"{row.get('full_loss_cushion')} | {money(row.get('delta_vs_live_snapshot_cents'))} | "
            f"{row.get('marginal_rows')}/{money(row.get('marginal_weighted_net_cents'))} | "
            f"`{', '.join(row.get('blockers') or [])}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
