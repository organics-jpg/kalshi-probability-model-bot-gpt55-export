"""Loss-analog monitor for the frozen boundary-clock feature gate.

Research-only; no live bot changes or orders.

This uses already-frozen diagnostic selected losses as physical analog
prototypes, then scores post-freeze selected rows by similarity. It does not
search thresholds or alter candidate selection.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_loss_analog_monitor_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_loss_analog_monitor_latest.md"

VECTOR_FIELDS = ("raw_edge", "recross_hazard_score", "abs_d_sigma", "ask_prob")
SCALES = {
    "raw_edge": 0.08,
    "recross_hazard_score": 0.25,
    "abs_d_sigma": 0.60,
    "ask_prob": 0.25,
}


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


def lane_map(feature: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(lane.get("lane")): lane
        for lane in feature.get("lanes") or []
        if isinstance(lane, dict)
    }


def best_variant(lane: dict[str, Any]) -> dict[str, Any]:
    variants = lane.get("variants")
    return variants[0] if isinstance(variants, list) and variants else {}


def selected_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in variant.get("rows") or [] if isinstance(row, dict)]


def loss_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in selected_rows(variant) if row.get("side_won") is False]


def vector_distance(row: dict[str, Any], proto: dict[str, Any]) -> float | None:
    parts = []
    for field in VECTOR_FIELDS:
        a = as_float(row.get(field))
        b = as_float(proto.get(field))
        scale = SCALES[field]
        if a is None or b is None:
            continue
        parts.append(((a - b) / scale) ** 2)
    if not parts:
        return None
    return math.sqrt(sum(parts) / len(parts))


def analog_score(distance: float | None) -> float | None:
    if distance is None:
        return None
    return 1.0 / (1.0 + distance)


def risk_components(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    edge = as_float(row.get("raw_edge"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is not None and edge <= 0.07:
        out.append("thin_raw_edge")
    if recross is not None and recross >= 0.25:
        out.append("moderate_recross")
    if abs_d is not None and abs_d < 1.0:
        out.append("weak_boundary_distance")
    if ask is not None and ask >= 0.75:
        out.append("expensive_touch")
    if str(row.get("source") or "") != "approved_entry":
        out.append("reconstructed_source")
    return out or ["none"]


def score_row(row: dict[str, Any], prototypes: list[dict[str, Any]]) -> dict[str, Any]:
    best_proto = None
    best_distance = None
    for proto in prototypes:
        distance = vector_distance(row, proto)
        if distance is None:
            continue
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_proto = proto
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
        "risk_components": risk_components(row),
        "nearest_loss_market": None if best_proto is None else best_proto.get("market"),
        "nearest_loss_distance": best_distance,
        "loss_analog_score": analog_score(best_distance),
    }


def summarize_scores(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [as_float(row.get("loss_analog_score")) for row in rows]
    scores = [score for score in scores if score is not None]
    components: dict[str, int] = {}
    for row in rows:
        for component in row.get("risk_components") or []:
            components[component] = components.get(component, 0) + 1
    return {
        "rows": len(rows),
        "max_loss_analog_score": max(scores) if scores else None,
        "avg_loss_analog_score": (sum(scores) / len(scores)) if scores else None,
        "risk_component_counts": dict(sorted(components.items())),
    }


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    lanes = lane_map(feature)
    diagnostic_entry = best_variant(lanes.get("diagnostic_entry") or {})
    diagnostic_bridge = best_variant(lanes.get("diagnostic_bridge") or {})
    prototypes = loss_rows(diagnostic_entry)
    if not prototypes:
        prototypes = loss_rows(diagnostic_bridge)

    scored_lanes: dict[str, dict[str, Any]] = {}
    for lane_name in ("diagnostic_entry", "diagnostic_bridge", "post_feature_freeze_entry", "post_feature_freeze_bridge"):
        lane = lanes.get(lane_name) or {}
        variant = best_variant(lane)
        scored = [score_row(row, prototypes) for row in selected_rows(variant)]
        scored.sort(key=lambda row: as_float(row.get("loss_analog_score")) or -1.0, reverse=True)
        scored_lanes[lane_name] = {
            "candidate": variant.get("candidate"),
            "summary": variant.get("candidate_summary"),
            "prototype_count": len(prototypes),
            "summary_scores": summarize_scores(scored),
            "top_loss_analogs": scored[:12],
        }

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_gate_path": str(FEATURE_JSON),
        "freeze_ts_utc": (feature.get("state") or {}).get("freeze_ts_utc"),
        "prototype_source_candidate": diagnostic_entry.get("candidate") or diagnostic_bridge.get("candidate"),
        "prototype_loss_rows": prototypes,
        "lanes": scored_lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Loss analog scores compare selected rows to frozen diagnostic selected losses; they are warning signals, not promotion gates or new thresholds.",
    ]
    post = (report.get("lanes") or {}).get("post_feature_freeze_entry") or {}
    post_summary = post.get("summary_scores") or {}
    notes.append(
        f"Post-freeze entry has {post_summary.get('rows')} scored row(s), max analog score {post_summary.get('max_loss_analog_score')}, components {post_summary.get('risk_component_counts')}."
    )
    diag = (report.get("lanes") or {}).get("diagnostic_entry") or {}
    diag_summary = diag.get("summary_scores") or {}
    notes.append(
        f"Diagnostic entry reference has {diag_summary.get('rows')} scored row(s), max analog score {diag_summary.get('max_loss_analog_score')}, components {diag_summary.get('risk_component_counts')}."
    )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.append("| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest loss | components |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('loss_analog_score'))} | "
            f"{row.get('nearest_loss_market')} | {', '.join(row.get('risk_components') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Loss Analog Monitor",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Prototype source: `{report.get('prototype_source_candidate')}`",
        f"- Prototype loss rows: `{len(report.get('prototype_loss_rows') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane_name, lane in (report.get("lanes") or {}).items():
        lines.extend(["", f"## {lane_name}", ""])
        scores = lane.get("summary_scores") or {}
        lines.append(f"- Candidate: `{lane.get('candidate')}`")
        lines.append(f"- Rows: `{scores.get('rows')}`")
        lines.append(f"- Max analog score: `{fmt(scores.get('max_loss_analog_score'))}`")
        lines.append(f"- Avg analog score: `{fmt(scores.get('avg_loss_analog_score'))}`")
        lines.append(f"- Risk components: `{scores.get('risk_component_counts')}`")
        lines.extend(["", "### Top Analog Rows", ""])
        write_rows(lines, lane.get("top_loss_analogs") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
