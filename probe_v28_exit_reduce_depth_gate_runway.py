"""Promotion runway for the frozen exit reduce entry-depth gate.

Research-only; no live bot changes or orders.

This report does not search for new exit rules. It reads the already-frozen
entry-depth gate watch and quantifies what the post-birth lane still needs
before it can be considered meaningful forward evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_runway_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_depth_gate_runway_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 5
MIN_FULL_LOSS_CUSHION = 3
FULL_LOSS_CENTS = 100.0


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


def first_lane(payload: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = payload.get("lanes")
    if not isinstance(lanes, list):
        return {}
    return next((lane for lane in lanes if lane.get("lane") == lane_name), {})


def first_variant(lane: dict[str, Any]) -> dict[str, Any]:
    variants = lane.get("variants")
    return variants[0] if isinstance(variants, list) and variants else {}


def runway_for_variant(variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("summary") or {}
    settled = int(as_float(summary.get("settled")) or 0)
    suppressed = int(as_float(summary.get("suppressed_exits")) or 0)
    suppressed_losers = int(as_float(summary.get("suppressed_losers")) or 0)
    delta = float(as_float(summary.get("delta_vs_current_cents")) or 0.0)
    cushion = int(as_float(summary.get("full_loss_cushion_estimate")) or 0)
    rows_needed = max(0, MIN_SETTLED - settled)
    suppressed_needed = max(0, MIN_SUPPRESSED - suppressed)
    cushion_cents_needed = max(0.0, (MIN_FULL_LOSS_CUSHION * FULL_LOSS_CENTS) - max(0.0, delta))
    full_losses_absorbable = int(max(0.0, delta) // FULL_LOSS_CENTS)
    blockers = list(variant.get("blockers") or [])
    return {
        "candidate": variant.get("candidate"),
        "settled": settled,
        "suppressed_exits": suppressed,
        "suppressed_losers": suppressed_losers,
        "delta_vs_current_cents": delta,
        "full_loss_cushion": cushion,
        "future_settled_rows_needed": rows_needed,
        "future_suppressed_exits_needed": suppressed_needed,
        "net_cents_needed_for_cushion3": cushion_cents_needed,
        "full_losses_absorbable": full_losses_absorbable,
        "has_harmful_suppressed_exit": suppressed_losers > 0,
        "blockers": blockers,
        "ready_for_consideration": (
            settled >= MIN_SETTLED
            and suppressed >= MIN_SUPPRESSED
            and suppressed_losers == 0
            and delta > 0.0
            and full_losses_absorbable >= MIN_FULL_LOSS_CUSHION
        ),
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    diag_lane = first_lane(source, "diagnostic_from_reduce_freeze")
    post_lane = first_lane(source, "post_depth_gate_birth")
    diag_best = first_variant(diag_lane)
    post_best = first_variant(post_lane)
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_path": str(SOURCE_JSON),
        "depth_gate_freeze_ts_utc": (source.get("state") or {}).get("freeze_ts_utc"),
        "diagnostic_best": runway_for_variant(diag_best),
        "post_birth_best": runway_for_variant(post_best),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    post = report.get("post_birth_best") or {}
    diag = report.get("diagnostic_best") or {}
    return [
        "This is a runway report only; diagnostic rows are mechanism evidence, not promotion evidence.",
        (
            f"Diagnostic best {diag.get('candidate')} has settled {diag.get('settled')}, "
            f"suppressed {diag.get('suppressed_exits')}, delta {diag.get('delta_vs_current_cents')}c, "
            f"and full-loss cushion {diag.get('full_loss_cushion')}."
        ),
        (
            f"Post-birth best {post.get('candidate')} has settled {post.get('settled')}, "
            f"suppressed {post.get('suppressed_exits')}, delta {post.get('delta_vs_current_cents')}c, "
            f"full-loss cushion {post.get('full_loss_cushion')}, and blockers {post.get('blockers')}."
        ),
        (
            f"Post-birth still needs {post.get('future_settled_rows_needed')} settled rows, "
            f"{post.get('future_suppressed_exits_needed')} suppressed exits, and "
            f"{post.get('net_cents_needed_for_cushion3')}c of net cushion before this exit repair is promotion-reviewable."
        ),
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Reduce Depth-Gate Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Depth-gate freeze UTC: `{report.get('depth_gate_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Runway",
            "",
            "| lane | candidate | settled | suppressed | harmful suppressed | delta c | cushion | rows needed | suppressed needed | cushion c needed | absorbable losses | ready | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for lane_name, row in (
        ("diagnostic", report.get("diagnostic_best") or {}),
        ("post_birth", report.get("post_birth_best") or {}),
    ):
        lines.append(
            f"| {lane_name} | {row.get('candidate')} | {row.get('settled')} | "
            f"{row.get('suppressed_exits')} | {row.get('suppressed_losers')} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('full_loss_cushion')} | "
            f"{row.get('future_settled_rows_needed')} | {row.get('future_suppressed_exits_needed')} | "
            f"{fmt(row.get('net_cents_needed_for_cushion3'))} | {row.get('full_losses_absorbable')} | "
            f"{row.get('ready_for_consideration')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
