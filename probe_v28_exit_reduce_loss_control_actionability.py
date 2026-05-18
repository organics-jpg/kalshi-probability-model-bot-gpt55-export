"""Actionability audit for reduce-suppression loss-control signatures.

Research-only; no live bot changes or orders.

The signature report intentionally includes post-exit diagnostics. This audit
separates hindsight-only separators from features observable at the exit
decision, then checks whether the best observable separator is already covered
by a frozen forward watch.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SIGNATURE_JSON = OUT_DIR / "v28_exit_reduce_loss_control_signature_latest.json"
DEPTH_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json"
GEOMETRY_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_loss_control_actionability_latest.md"

HINDSIGHT_FEATURES = {
    "worst_post_exit_hold_mark_cents",
    "best_post_exit_hold_mark_cents",
    "post_exit_points",
}

FROZEN_WATCH_FEATURES = {
    "entry_depth": "v28_exit_reduce_depth_gate_opportunity_latest.json",
    "entry_seconds_to_close": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "trade_duration_sec": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "entry_book_age_ms": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "exit_sigma_t_dollars": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "exit_cents": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "entry_volshock": "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "exit_fair_drawdown_cents": "v28_frozen_exit_reduce_loss_control_refinement_latest.json",
    "exit_p_hold": "v28_frozen_exit_reduce_loss_control_refinement_latest.json",
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


def classify(row: dict[str, Any]) -> str:
    feature = str(row.get("feature") or "")
    if feature in HINDSIGHT_FEATURES:
        return "hindsight_post_exit"
    if feature.startswith("entry_") or feature.startswith("exit_") or feature == "trade_duration_sec":
        return "observable_at_exit"
    return "unknown_actionability"


def enriched(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    actionability = classify(row)
    out["actionability"] = actionability
    out["frozen_watch"] = FROZEN_WATCH_FEATURES.get(str(row.get("feature") or ""))
    out["needs_new_freeze"] = actionability == "observable_at_exit" and not out["frozen_watch"]
    return out


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -int(row.get("harmful_excluded") or 0),
        int(row.get("helpful_excluded") or 0),
        -float(row.get("selected_delta_cents") or -999999.0),
        -int(row.get("selected_rows") or 0),
    )


def build_report() -> dict[str, Any]:
    signature = load_json(SIGNATURE_JSON)
    depth_opportunity = load_json(DEPTH_OPPORTUNITY_JSON)
    geometry_opportunity = load_json(GEOMETRY_OPPORTUNITY_JSON)
    rows = [enriched(row) for row in signature.get("candidate_separators") or [] if isinstance(row, dict)]
    hindsight = sorted([row for row in rows if row["actionability"] == "hindsight_post_exit"], key=sort_key)
    observable = sorted([row for row in rows if row["actionability"] == "observable_at_exit"], key=sort_key)
    unknown = sorted([row for row in rows if row["actionability"] == "unknown_actionability"], key=sort_key)
    needs_freeze = [row for row in observable if row.get("needs_new_freeze")]
    best_observable = observable[0] if observable else {}
    best_hindsight = hindsight[0] if hindsight else {}
    depth_rules = depth_opportunity.get("rules") or []
    depth_best = depth_rules[0] if depth_rules else {}
    geometry_summary = geometry_opportunity.get("summary") or {}

    interpretation = [
        "This report does not create or promote an exit rule; it classifies which diagnostic separators are usable at decision time.",
        f"Best separator overall is {best_hindsight.get('feature')} {best_hindsight.get('direction')} {best_hindsight.get('threshold')} and is hindsight-only.",
        f"Best observable separator is {best_observable.get('feature')} {best_observable.get('direction')} {best_observable.get('threshold')}, selected W/L {best_observable.get('selected_helpful')}/{best_observable.get('selected_harmful')}, delta {best_observable.get('selected_delta_cents')}c.",
        f"Best observable separator is already covered by frozen watch {best_observable.get('frozen_watch')}; current depth opportunity would-suppress rows {depth_best.get('would_suppress_rows')}.",
        f"Side-geometry opportunity remains too strict so far: rejected base candidates {geometry_summary.get('geometry_rejected_base_candidates')} for {geometry_summary.get('geometry_rejected_base_delta_cents')}c.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(SIGNATURE_JSON),
        "best_hindsight": best_hindsight,
        "best_observable": best_observable,
        "hindsight_top": hindsight[:8],
        "observable_top": observable[:12],
        "unknown_top": unknown[:8],
        "observable_needing_new_freeze": needs_freeze[:8],
        "depth_opportunity_summary": depth_best,
        "geometry_opportunity_summary": geometry_summary,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| feature | dir | threshold | selected | W/L | delta c | excluded helpful/harmful | actionability | frozen watch |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row.get('feature')} | {row.get('direction')} | {fmt(row.get('threshold'))} | "
            f"{row.get('selected_rows')} | {row.get('selected_helpful')}/{row.get('selected_harmful')} | "
            f"{fmt(row.get('selected_delta_cents'))} | {row.get('helpful_excluded')}/{row.get('harmful_excluded')} | "
            f"{row.get('actionability')} | {row.get('frozen_watch') or ''} |"
        )


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Reduce Loss-Control Actionability",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Observable Separators", ""])
    write_table(lines, report.get("observable_top") or [])
    lines.extend(["", "## Hindsight-Only Separators", ""])
    write_table(lines, report.get("hindsight_top") or [])
    if report.get("observable_needing_new_freeze"):
        lines.extend(["", "## Observable Separators Needing A Separate Freeze", ""])
        write_table(lines, report.get("observable_needing_new_freeze") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
