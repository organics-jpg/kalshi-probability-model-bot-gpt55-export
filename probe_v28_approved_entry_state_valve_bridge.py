"""Bridge approved-entry-only state valves into the v28 promotion gate language.

Research-only; no live bot changes or orders.

The frozen state-valve probes validate actual v28-approved entries after their
own freeze timestamps. That is useful forward evidence, but it is not the same
surface as the broad candidate tracker because rejected/reconstructed simulated
entries are absent by construction. This report makes that distinction explicit
before these valves are used in candidate-vs-live discussions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

FROZEN_VALVES = [
    (
        "danger_zone_entry_valve",
        OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json",
    ),
    (
        "approved_entry_state_valve",
        OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json",
    ),
]

LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
CANDIDATE_VS_LIVE_MD = OUT_DIR / "v28_candidate_vs_live_full_table_latest.md"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"

OUT_JSON = OUT_DIR / "v28_approved_entry_state_valve_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_state_valve_bridge_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_SOURCE_SHARE = 0.35
MIN_CUSHION = 3


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


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def live_net_cents() -> float | None:
    summary = load_json(LIVE_SUMMARY_JSON)
    dollars = as_float(summary.get("net_pnl_total_dollars"))
    return None if dollars is None else round(dollars * 100.0, 6)


def text_contains(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    try:
        return needle.lower() in path.read_text(encoding="utf-8").lower()
    except OSError:
        return False


def full_loss_cushion(cents: float | None) -> int | None:
    if cents is None:
        return None
    if cents <= 0:
        return 0
    return int(cents // 100)


def valve_row(label: str, payload: dict[str, Any], live_cents: float | None) -> dict[str, Any]:
    candidate = payload.get("candidate") or {}
    control = payload.get("control") or {}
    freeze = payload.get("freeze") or {}
    policy = str(candidate.get("policy") or freeze.get("policy") or label)

    settled = as_int(candidate.get("settled"))
    entries = as_int(candidate.get("entries"))
    coverage = as_float(candidate.get("market_coverage_pct"))
    gross = as_float(candidate.get("gross_cents"))
    control_gross = as_float(control.get("gross_cents"))
    delta_control = as_float(candidate.get("delta_vs_control_cents"))
    skipped = as_int(candidate.get("skipped_entries"))
    losses = as_int(candidate.get("losses"))
    wins = as_int(candidate.get("wins"))

    # These rows are all actual approved entries. The row-source share is clean
    # on this surface, but the surface itself is narrower than broad strategy
    # coverage because rejected/reconstructed simulated entries are absent.
    row_source_share = 0.0
    cushion = full_loss_cushion(gross)
    delta_cushion = full_loss_cushion(delta_control)
    delta_live = None if live_cents is None or gross is None else gross - live_cents

    table_present = text_contains(CANDIDATE_VS_LIVE_MD, policy)

    gates = {
        "strict_frozen_forward": bool(freeze.get("freeze_ts_utc")) and (settled or 0) >= MIN_SETTLED,
        "positive_on_approved_surface": gross is not None and gross > 0,
        "positive_delta_vs_approved_control": delta_control is not None and delta_control > 0,
        "approved_surface_coverage_ge_75": coverage is not None and coverage >= MIN_COVERAGE,
        "approved_surface_coverage_le_90": coverage is not None and coverage <= MAX_COVERAGE,
        "approved_row_source_share_le_35": row_source_share <= MAX_SOURCE_SHARE,
        "gross_full_loss_cushion_ge_3": cushion is not None and cushion >= MIN_CUSHION,
        "delta_full_loss_cushion_ge_3": delta_cushion is not None and delta_cushion >= MIN_CUSHION,
        "present_in_candidate_vs_live": table_present,
        "beats_live_cents_naive": delta_live is not None and delta_live > 0,
    }

    blockers: list[str] = []
    if not gates["strict_frozen_forward"]:
        blockers.append("strict_settled_lt_30_or_missing_freeze")
    if not gates["positive_on_approved_surface"]:
        blockers.append("approved_surface_net_not_positive")
    if not gates["positive_delta_vs_approved_control"]:
        blockers.append("delta_vs_approved_control_not_positive")
    if not gates["approved_surface_coverage_ge_75"]:
        blockers.append("approved_surface_coverage_below_75")
    if not gates["approved_surface_coverage_le_90"]:
        blockers.append("approved_surface_coverage_above_90_not_broad_strategy_comparable")
    if not gates["gross_full_loss_cushion_ge_3"]:
        blockers.append("gross_full_loss_cushion_lt_3")
    if not gates["delta_full_loss_cushion_ge_3"]:
        blockers.append("delta_full_loss_cushion_lt_3")
    if not table_present:
        blockers.append("not_in_candidate_vs_live_table")
    blockers.append("approved_entry_surface_only_not_full_strategy_surface")
    blockers.append("live_readiness_not_evaluated_for_valve")
    if not gates["beats_live_cents_naive"]:
        blockers.append("does_not_beat_live_on_naive_cents_comparison")

    return {
        "label": label,
        "policy": policy,
        "freeze_ts_utc": freeze.get("freeze_ts_utc"),
        "future_rows": payload.get("future_rows"),
        "future_markets": payload.get("future_markets"),
        "entries": entries,
        "settled": settled,
        "wins": wins,
        "losses": losses,
        "approved_surface_coverage_pct": coverage,
        "gross_cents": gross,
        "control_gross_cents": control_gross,
        "delta_vs_approved_control_cents": delta_control,
        "skipped_entries": skipped,
        "approved_row_source_share": row_source_share,
        "gross_full_loss_cushion": cushion,
        "delta_full_loss_cushion": delta_cushion,
        "naive_delta_vs_live_cents": delta_live,
        "candidate_vs_live_table_present": table_present,
        "gates": gates,
        "blockers": blockers,
        "promotion_ready": False,
        "skipped_examples": candidate.get("skipped_examples") or [],
    }


def build_report() -> dict[str, Any]:
    live_cents = live_net_cents()
    tracker = load_json(TRACKER_JSON)
    rows = []
    missing = []
    for label, path in FROZEN_VALVES:
        payload = load_json(path)
        if payload:
            rows.append(valve_row(label, payload, live_cents))
        else:
            missing.append(str(path))

    promising = [
        row for row in rows
        if row.get("gates", {}).get("strict_frozen_forward")
        and row.get("gates", {}).get("positive_delta_vs_approved_control")
    ]
    next_steps = [
        "Keep both valves research-only; they validate actual approved entries only.",
        "Before tracker integration, build a full-surface replay that computes market coverage against the same denominator used by broad entry lanes.",
        "Compare the valve output to current live-only baseline, source-quality gates, full-loss cushion, and live-readiness gates in one candidate row.",
        "Inspect skipped winners separately; danger-zone skips include some winners, so the physical rule must prove it removes more exit/state churn than upside.",
    ]
    return {
        "live_net_cents": live_cents,
        "tracker_counts": tracker.get("counts") or {},
        "rows": rows,
        "missing_sources": missing,
        "promising_approved_only_rows": len(promising),
        "any_promotion_ready": False,
        "interpretation": [
            f"{len(promising)} approved-entry-only frozen valve(s) are positive versus approved-entry control.",
            "No valve is promotion-ready from this bridge because the validation surface is approved-entry-only and not yet in candidate-vs-live/live-readiness gates.",
            "The strongest immediate research action is a full-surface replay/adapter, not a live change.",
        ],
        "next_steps": next_steps,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Approved-Entry State Valve Bridge",
        "",
        "Research-only bridge; no live bot changes or orders.",
        "",
        f"- Live baseline net: `{fmt(report.get('live_net_cents'))}c`",
        f"- Positive approved-only frozen valves: `{report.get('promising_approved_only_rows')}`",
        f"- Promotion-ready valves: `{report.get('any_promotion_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")

    lines.extend([
        "",
        "## Gate Bridge",
        "",
        "| valve | policy | settled | W/L | approved cov | gross c | delta vs approved control | naive delta vs live | skipped | source share | cushion gross/delta | in candidate-vs-live | promotion ready | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('label')}` | `{row.get('policy')}` | {fmt(row.get('settled'))} | "
            f"{fmt(row.get('wins'))}/{fmt(row.get('losses'))} | {fmt(row.get('approved_surface_coverage_pct'))}% | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('delta_vs_approved_control_cents'))} | "
            f"{fmt(row.get('naive_delta_vs_live_cents'))} | {fmt(row.get('skipped_entries'))} | "
            f"{fmt(row.get('approved_row_source_share'))} | {fmt(row.get('gross_full_loss_cushion'))}/{fmt(row.get('delta_full_loss_cushion'))} | "
            f"{row.get('candidate_vs_live_table_present')} | {row.get('promotion_ready')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )

    lines.extend(["", "## Skipped Examples", ""])
    for row in report.get("rows") or []:
        examples = row.get("skipped_examples") or []
        if not examples:
            continue
        lines.append(f"### {row.get('label')}")
        for ex in examples[:8]:
            lines.append(
                f"- `{ex.get('market')}` `{ex.get('side')}` won `{ex.get('won')}`, "
                f"gross/hold `{fmt(ex.get('gross_cents'))}/{fmt(ex.get('hold_gross_cents'))}`, "
                f"gap `{fmt(ex.get('raw_book_gap'))}`, same-side idx `{ex.get('market_side_entry_index')}`"
            )
        lines.append("")

    lines.extend(["## Next Steps", ""])
    for step in report.get("next_steps") or []:
        lines.append(f"- {step}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
