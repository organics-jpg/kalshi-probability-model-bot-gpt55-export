"""Residual loss mechanism audit for boundary-clock feature-gate repairs.

Research-only; no live bot changes or orders.

The cheap-side ask/penalty repair explains one failure mode. This report
describes the losses that remain after that repair and watches whether new
post-birth rows start resembling those residual loss prototypes.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PENALTY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_residual_loss_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_residual_loss_mechanism_latest.md"

VECTOR_FIELDS = ("raw_edge", "recross_hazard_score", "abs_d_sigma", "ask_prob")
SCALES = {
    "raw_edge": 0.12,
    "recross_hazard_score": 0.30,
    "abs_d_sigma": 0.60,
    "ask_prob": 0.25,
}


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


def lane_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(lane.get("lane")): lane
        for lane in payload.get("lanes") or []
        if isinstance(lane, dict)
    }


def best_variant(lane: dict[str, Any]) -> dict[str, Any]:
    variants = lane.get("variants")
    return variants[0] if isinstance(variants, list) and variants else {}


def selected_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in variant.get("rows") or [] if isinstance(row, dict)]


def loss_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in selected_rows(variant) if row.get("side_won") is False]


def residual_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    side = str(row.get("side") or "")
    source = str(row.get("source") or "")
    edge = as_float(row.get("raw_edge"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if source != "approved_entry":
        tags.append("source_quality_error")
    if side == "yes" and ask is not None and ask >= 0.65 and abs_d is not None and abs_d <= 1.0:
        tags.append("expensive_yes_near_boundary")
    if recross is not None and 0.20 <= recross <= 0.45:
        tags.append("moderate_recross_reversal")
    if edge is not None and edge <= 0.07:
        tags.append("thin_edge_expensive_touch")
    if edge is not None and edge >= 0.12 and ask is not None and ask >= 0.65:
        tags.append("fv_overconfidence")
    if ask is not None and ask < 0.65:
        tags.append("cheap_side_residual")
    if abs_d is not None and abs_d < 0.95:
        tags.append("weak_boundary_distance")
    return tags or ["clean_or_unclassified"]


def vector_distance(row: dict[str, Any], proto: dict[str, Any]) -> float | None:
    parts: list[float] = []
    for field in VECTOR_FIELDS:
        a = as_float(row.get(field))
        b = as_float(proto.get(field))
        if a is None or b is None:
            continue
        parts.append(((a - b) / SCALES[field]) ** 2)
    if not parts:
        return None
    return math.sqrt(sum(parts) / len(parts))


def analog_score(row: dict[str, Any], prototypes: list[dict[str, Any]]) -> dict[str, Any]:
    best_proto = None
    best_distance = None
    for proto in prototypes:
        distance = vector_distance(row, proto)
        if distance is None:
            continue
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_proto = proto
    score = None if best_distance is None else 1.0 / (1.0 + best_distance)
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_cents"),
        "raw_edge": row.get("raw_edge"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "residual_tags": residual_tags(row),
        "nearest_residual_loss": None if best_proto is None else best_proto.get("market"),
        "residual_loss_distance": best_distance,
        "residual_loss_score": score,
    }


def summarize_scored(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [as_float(row.get("residual_loss_score")) for row in rows]
    scores = [score for score in scores if score is not None]
    tags = Counter(tag for row in rows for tag in row.get("residual_tags") or [])
    return {
        "rows": len(rows),
        "max_residual_loss_score": max(scores) if scores else None,
        "avg_residual_loss_score": (sum(scores) / len(scores)) if scores else None,
        "tag_counts": dict(sorted(tags.items())),
    }


def evaluate_lane(lane_name: str, lane: dict[str, Any], prototypes: list[dict[str, Any]]) -> dict[str, Any]:
    variant = best_variant(lane)
    rows = [analog_score(row, prototypes) for row in selected_rows(variant)]
    rows.sort(key=lambda row: as_float(row.get("residual_loss_score")) or -1.0, reverse=True)
    losses = [row for row in rows if row.get("side_won") is False]
    return {
        "candidate": variant.get("candidate"),
        "summary": variant.get("candidate_summary"),
        "residual_summary": summarize_scored(rows),
        "loss_summary": summarize_scored(losses),
        "top_residual_analogs": rows[:12],
        "loss_rows": losses,
    }


def build_report() -> dict[str, Any]:
    payload = load_json(PENALTY_JSON)
    lanes = lane_map(payload)
    diagnostic_entry = best_variant(lanes.get("diagnostic_entry") or {})
    diagnostic_bridge = best_variant(lanes.get("diagnostic_bridge") or {})
    prototypes = loss_rows(diagnostic_entry)
    if not prototypes:
        prototypes = loss_rows(diagnostic_bridge)
    scored_lanes: dict[str, dict[str, Any]] = {}
    for lane_name in (
        "diagnostic_entry",
        "diagnostic_bridge",
        "pre_penalty_birth_feature_entry",
        "pre_penalty_birth_feature_bridge",
        "post_penalty_birth_entry",
        "post_penalty_birth_bridge",
    ):
        lane = lanes.get(lane_name) or {}
        scored_lanes[lane_name] = evaluate_lane(lane_name, lane, prototypes)
    prototype_tags = Counter(tag for row in prototypes for tag in residual_tags(row))
    report = {
        "generated_at_utc": utc_now_iso(),
        "penalty_freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc"),
        "prototype_source": "diagnostic_entry",
        "prototype_count": len(prototypes),
        "prototype_tag_counts": dict(sorted(prototype_tags.items())),
        "prototype_loss_rows": [analog_score(row, prototypes) for row in prototypes],
        "lanes": scored_lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Residual loss prototypes are the selected diagnostic losses after the continuous cheap-side penalty repair.",
        f"Prototype tags are {report.get('prototype_tag_counts')}.",
    ]
    for lane_name in ("pre_penalty_birth_feature_entry", "post_penalty_birth_entry"):
        lane = (report.get("lanes") or {}).get(lane_name) or {}
        notes.append(
            f"{lane_name}: {lane.get('candidate')} has residual scores {lane.get('residual_summary')} "
            f"and loss scores {lane.get('loss_summary')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('residual_loss_score'))} | "
            f"{row.get('nearest_residual_loss')} | {', '.join(row.get('residual_tags') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Residual Loss Mechanism",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Penalty freeze UTC: `{report.get('penalty_freeze_ts_utc')}`",
        f"- Prototype source: `{report.get('prototype_source')}`",
        f"- Prototype count: `{report.get('prototype_count')}`",
        f"- Prototype tags: `{report.get('prototype_tag_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane_name, lane in (report.get("lanes") or {}).items():
        lines.extend(["", f"## {lane_name}", ""])
        lines.append(f"- Candidate: `{lane.get('candidate')}`")
        lines.append(f"- Summary: `{lane.get('summary')}`")
        lines.append(f"- Residual scores: `{lane.get('residual_summary')}`")
        lines.append(f"- Loss scores: `{lane.get('loss_summary')}`")
        lines.extend(["", "### Top Residual Analogs", ""])
        write_rows(lines, lane.get("top_residual_analogs") or [])
        lines.extend(["", "### Loss Rows", ""])
        write_rows(lines, lane.get("loss_rows") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
