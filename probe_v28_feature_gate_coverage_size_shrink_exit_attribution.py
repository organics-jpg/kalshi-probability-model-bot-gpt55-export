"""Exit attribution for the feature-gate coverage size-shrink lane.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state, market, net, source
from probe_v28_feature_gate_near_promotion_exit_attribution import (
    EXIT_SOURCES,
    choose_exit,
    classify_exit,
    exit_current,
    exit_hold,
    parse_ts,
    side,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SIZE_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_exit_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_coverage_size_shrink_exit_attribution_latest.md"


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


def load_exit_index() -> dict[str, dict[tuple[str, str], list[dict[str, Any]]]]:
    output: dict[str, dict[tuple[str, str], list[dict[str, Any]]]] = {}
    for name, path in EXIT_SOURCES.items():
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if isinstance(row, dict):
                grouped[(market(row), side(row))].append(row)
        for rows in grouped.values():
            rows.sort(key=lambda item: parse_ts(item.get("exit_ts") or item.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
        output[name] = grouped
    return output


def best_policy_for(lane_name: str) -> str:
    payload = load_json(SIZE_JSON)
    for lane in payload.get("lanes") or []:
        if isinstance(lane, dict) and lane.get("lane") == lane_name:
            best = (lane.get("rows") or [{}])[0]
            return str(best.get("policy") or "repair_low_absd_quarter_else_half")
    return "repair_low_absd_quarter_else_half"


def selected_weighted_losses(lane_name: str, freeze_ts: str) -> list[dict[str, Any]]:
    surfaces = entry_surfaces if lane_name == "post_feature_freeze_entry" else bridge_surfaces
    rows, _, _ = surfaces(freeze_ts)
    anchor_rows = selected(rows, ANCHOR_RULE)
    repair_rows = selected(rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    policy = best_policy_for(lane_name)
    losses: list[dict[str, Any]] = []
    for row in repair_rows:
        weight = repair_weight(policy, row, anchor_keys)
        if weight <= 0:
            continue
        row_net = net(row)
        if row_net >= 0:
            continue
        losses.append({
            "row": row,
            "weight": weight,
            "weighted_net_cents": row_net * weight,
            "policy": policy,
            "is_anchor": row_key(row) in anchor_keys,
        })
    return losses


def classify_weighted_loss(item: dict[str, Any], exits: dict[str, dict[tuple[str, str], list[dict[str, Any]]]]) -> dict[str, Any]:
    row = item["row"]
    key = (market(row), side(row))
    exit_matches: dict[str, Any] = {}
    class_counts: Counter[str] = Counter()
    best_delta = None
    for name, index in exits.items():
        match = choose_exit(index.get(key) or [])
        if not match:
            continue
        current = exit_current(match)
        hold = exit_hold(match)
        delta = None if current is None or hold is None else hold - current
        classification = classify_exit(current, hold)
        class_counts[classification] += 1
        if delta is not None and (best_delta is None or abs(delta) > abs(best_delta)):
            best_delta = delta
        exit_matches[name] = {
            "current_cents": current,
            "hold_cents": hold,
            "hold_minus_current_cents": delta,
            "classification": classification,
            "exit_reason": match.get("exit_reason"),
            "p_hold": match.get("p_hold"),
            "fair_drawdown_cents": match.get("fair_drawdown_cents"),
            "hold_book_gap": match.get("hold_book_gap"),
            "suppressed": match.get("suppressed"),
            "exit_ts": match.get("exit_ts"),
        }
    if not exit_matches:
        primary_class = "no_exit_observation"
    elif class_counts.get("exit_helped_vs_hold", 0) >= max(class_counts.values()):
        primary_class = "entry_or_fv_failure_exit_helped"
    elif class_counts.get("exit_hurt_or_clipped_winner", 0):
        primary_class = "exit_policy_failure_candidate"
    else:
        primary_class = class_counts.most_common(1)[0][0]
    return {
        "market": market(row),
        "side": side(row),
        "source": source(row),
        "is_anchor": item.get("is_anchor"),
        "raw_net_cents": net(row),
        "weight": item.get("weight"),
        "weighted_net_cents": item.get("weighted_net_cents"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "primary_failure_class": primary_class,
        "best_hold_minus_current_cents": best_delta,
        "exit_matches": exit_matches,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    exits = load_exit_index()
    lanes = []
    for lane_name in ("post_feature_freeze_entry", "post_feature_freeze_bridge"):
        losses = selected_weighted_losses(lane_name, freeze_ts)
        rows = [classify_weighted_loss(item, exits) for item in losses]
        lanes.append({
            "lane": lane_name,
            "policy": best_policy_for(lane_name),
            "loss_rows": len(rows),
            "weighted_loss_cents": sum(float(row.get("weighted_net_cents") or 0.0) for row in rows),
            "raw_loss_cents": sum(float(row.get("raw_net_cents") or 0.0) for row in rows),
            "source_counts": dict(Counter(row["source"] for row in rows)),
            "failure_class_counts": dict(Counter(row["primary_failure_class"] for row in rows)),
            "rows": rows,
        })
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This attribution uses frozen exit artifacts as evidence only; it does not change exit logic.",
    ]
    for lane in lanes:
        notes.append(
            f"{lane.get('lane')} {lane.get('policy')} has {lane.get('loss_rows')} losing rows, "
            f"weighted loss {lane.get('weighted_loss_cents')}c, failure classes {lane.get('failure_class_counts')}."
        )
    return notes


def fmt_cents(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:.1f}c (${number / 100.0:.2f})"


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Coverage Size-Shrink Exit Attribution",
        "",
        "Research-only attribution. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Policy: `{lane.get('policy')}`",
            f"- Raw/weighted loss cents: `{fmt_cents(lane.get('raw_loss_cents'))}/{fmt_cents(lane.get('weighted_loss_cents'))}`",
            f"- Source counts: `{lane.get('source_counts')}`",
            f"- Failure classes: `{lane.get('failure_class_counts')}`",
            "",
            "| market | source | anchor | side | raw net | weight | weighted net | primary class | best hold-current |",
            "|---|---|---:|---|---:|---:|---:|---|---:|",
        ])
        for row in lane.get("rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('is_anchor')} | {row.get('side')} | "
                f"{fmt_cents(row.get('raw_net_cents'))} | {row.get('weight')} | "
                f"{fmt_cents(row.get('weighted_net_cents'))} | {row.get('primary_failure_class')} | "
                f"{fmt_cents(row.get('best_hold_minus_current_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())


if __name__ == "__main__":
    main()
