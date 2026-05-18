"""Source-dilution runway for the feature-gate coverage size-shrink lane.

Research-only; no live bot changes or orders.

The size-shrink audit found a near-gated broad row whose only internal blocker
is row-source share. This probe turns that into a concrete forward runway:
how many approved qualifying rows are needed, how much weighted loss cushion
remains, and whether the lane is still behind the refreshed live baseline.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state, market, net, source
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    MAX_RECON_SHARE,
    MIN_CUSHION,
    REPAIR_RULE,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SIZE_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_source_runway_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_size_shrink_source_runway_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_settled(row: dict[str, Any]) -> bool:
    return isinstance(row.get("side_won"), bool)


def is_approved(row: dict[str, Any]) -> bool:
    return source(row) == "approved_entry"


def clean_rows_needed(reconstructed_rows: int, total_rows: int) -> int:
    for rows in range(0, 500):
        if total_rows + rows > 0 and reconstructed_rows / (total_rows + rows) <= MAX_RECON_SHARE:
            return rows
    return 500


def best_size_rows() -> list[dict[str, Any]]:
    payload = load_json(SIZE_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        best = (lane.get("rows") or [{}])[0]
        if isinstance(best, dict):
            row = dict(best)
            row["lane"] = lane.get("lane")
            row["future_denominator"] = lane.get("future_denominator")
            row["anchor_rule"] = lane.get("anchor_rule")
            row["repair_rule"] = lane.get("repair_rule")
            rows.append(row)
    return rows


def rows_for_lane(lane_name: str, policy: str, freeze_ts: str) -> list[dict[str, Any]]:
    surfaces = entry_surfaces if lane_name == "post_feature_freeze_entry" else bridge_surfaces
    all_rows, _, _ = surfaces(freeze_ts)
    anchor_rows = selected(all_rows, ANCHOR_RULE)
    repair_rows = selected(all_rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    output: list[dict[str, Any]] = []
    for row in repair_rows:
        weight = repair_weight(policy, row, anchor_keys)
        if weight <= 0:
            continue
        weighted_net = weight * net(row) if is_settled(row) else None
        output.append(
            {
                "market": market(row),
                "side": row.get("side"),
                "source": source(row),
                "approved": is_approved(row),
                "settled": is_settled(row),
                "raw_net_cents": net(row) if is_settled(row) else None,
                "weight": weight,
                "weighted_net_cents": weighted_net,
                "is_anchor": row_key(row) in anchor_keys,
                "ask_prob": row.get("ask_prob"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recross_hazard_score": row.get("recross_hazard_score"),
            }
        )
    return output


def summarize_lane(best: dict[str, Any], freeze_ts: str, live_net_cents: float | None) -> dict[str, Any]:
    lane = str(best.get("lane") or "")
    policy = str(best.get("policy") or "")
    selected_rows = [
        dict(row)
        for row in (best.get("selected_rows") or [])
        if isinstance(row, dict)
    ]
    if not selected_rows:
        selected_rows = rows_for_lane(lane, policy, freeze_ts)
    total_rows = len(selected_rows)
    reconstructed_rows = sum(1 for row in selected_rows if not row["approved"])
    approved_rows = total_rows - reconstructed_rows
    settled_rows = [row for row in selected_rows if row["settled"]]
    weighted_net = sum(float(row["weighted_net_cents"] or 0.0) for row in settled_rows)
    min_cushion_cents = 100.0 * MIN_CUSHION
    cushion_surplus = weighted_net - min_cushion_cents
    clean_needed = clean_rows_needed(reconstructed_rows, total_rows)
    max_weighted_loss_per_clean_needed = cushion_surplus / clean_needed if clean_needed > 0 else None
    live_delta = None if live_net_cents is None else weighted_net - live_net_cents
    cents_to_live_tie = None if live_delta is None else max(0.0, -live_delta)
    full_weight_wins_to_live_tie = None if cents_to_live_tie is None else math.ceil(cents_to_live_tie / 100.0)
    blockers = list(best.get("blockers") or [])
    runway_blockers = list(blockers)
    if live_delta is not None and live_delta <= 0:
        runway_blockers.append("below_refreshed_live_baseline")

    return {
        "lane": lane,
        "policy": policy,
        "entries": total_rows,
        "settled": len(settled_rows),
        "wins": best.get("wins"),
        "losses": best.get("losses"),
        "coverage_pct": best.get("coverage_pct"),
        "weighted_net_cents": weighted_net,
        "row_reconstructed_share": reconstructed_rows / total_rows if total_rows else None,
        "exposure_reconstructed_share": best.get("exposure_reconstructed_share"),
        "approved_rows": approved_rows,
        "reconstructed_rows": reconstructed_rows,
        "source_counts": dict(Counter(row["source"] for row in selected_rows)),
        "clean_rows_needed_for_source": clean_needed,
        "cushion_surplus_cents_after_3_full_losses": cushion_surplus,
        "max_total_weighted_loss_for_clean_rows": max(0.0, cushion_surplus),
        "max_weighted_loss_per_clean_needed_row": max_weighted_loss_per_clean_needed,
        "live_net_cents": live_net_cents,
        "delta_vs_live_cents": live_delta,
        "cents_to_live_tie": cents_to_live_tie,
        "full_weight_wins_to_live_tie": full_weight_wins_to_live_tie,
        "blockers": blockers,
        "runway_blockers": runway_blockers,
        "approved_rows_selected": [row for row in selected_rows if row["approved"]],
        "reconstructed_rows_selected": [row for row in selected_rows if not row["approved"]],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live_summary = load_json(LIVE_SUMMARY_JSON)
    live_net_cents = None
    live_dollars = as_float(live_summary.get("net_pnl_total_dollars"))
    if live_dollars is not None:
        live_net_cents = round(live_dollars * 100.0)
    lanes = [summarize_lane(row, freeze_ts, live_net_cents) for row in best_size_rows()]
    lanes.sort(
        key=lambda row: (
            len(row.get("runway_blockers") or []),
            row.get("clean_rows_needed_for_source") or 999,
            -(as_float(row.get("weighted_net_cents")) or -1e9),
        )
    )
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "live_summary_path": str(LIVE_SUMMARY_JSON),
        "live_net_cents": live_net_cents,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a source-dilution runway for an already-frozen size-shrink audit, not a new threshold search.",
    ]
    best = (report.get("lanes") or [{}])[0]
    if best:
        notes.append(
            f"{best.get('lane')} / {best.get('policy')} needs "
            f"{best.get('clean_rows_needed_for_source')} approved qualifying row(s) to clear the row-source gate."
        )
        notes.append(
            f"Current weighted net is {best.get('weighted_net_cents')}c, leaving "
            f"{best.get('cushion_surplus_cents_after_3_full_losses')}c above the three-full-loss cushion."
        )
        notes.append(
            f"Against the refreshed live-only baseline of {report.get('live_net_cents')}c, this lane is "
            f"{best.get('delta_vs_live_cents')}c, so source dilution alone is not enough for promotion."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Size-Shrink Source Runway",
        "",
        "Research-only runway. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Refreshed live net: `{fmt(report.get('live_net_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lane Runway",
        "",
        "| lane | policy | settled | coverage | weighted net | row recon | clean rows needed | cushion surplus | delta vs live | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        lines.append(
            f"| {lane.get('lane')} | {lane.get('policy')} | {lane.get('settled')} | "
            f"{fmt(lane.get('coverage_pct'))} | {fmt(lane.get('weighted_net_cents'))} | "
            f"{fmt(lane.get('row_reconstructed_share'))} | {lane.get('clean_rows_needed_for_source')} | "
            f"{fmt(lane.get('cushion_surplus_cents_after_3_full_losses'))} | "
            f"{fmt(lane.get('delta_vs_live_cents'))} | {', '.join(lane.get('runway_blockers') or []) or 'none'} |"
        )
    best = (report.get("lanes") or [{}])[0]
    if best:
        lines.extend([
            "",
            "## Best Lane Details",
            "",
            f"- Source counts: `{best.get('source_counts')}`",
            f"- Approved/reconstructed rows: `{best.get('approved_rows')}/{best.get('reconstructed_rows')}`",
            f"- Max total weighted loss while preserving cushion: `{fmt(best.get('max_total_weighted_loss_for_clean_rows'))}c`",
            f"- Max weighted loss per needed clean row: `{fmt(best.get('max_weighted_loss_per_clean_needed_row'))}c`",
            f"- Full-weight wins needed to tie live baseline: `{best.get('full_weight_wins_to_live_tie')}`",
        ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
