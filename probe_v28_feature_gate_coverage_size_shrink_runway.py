"""Runway for feature-gate coverage size-shrink promotion gates.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_runway_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_coverage_size_shrink_runway_latest.md"

SOURCE_SHARE_MAX = 0.35
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MIN_CUSHION_CENTS = 300.0
MIN_SETTLED = 30


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


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def current_reconstructed_count(row: dict[str, Any]) -> int:
    entries = as_int(row.get("entries"))
    share = as_float(row.get("row_reconstructed_share"))
    return int(round(entries * share))


def clean_rows_needed(entries: int, reconstructed: int) -> int:
    needed = 0
    while entries + needed > 0 and reconstructed / (entries + needed) > SOURCE_SHARE_MAX:
        needed += 1
    return needed


def coverage_after(entries: int, denominator: int, selected_future: int, missed_future: int) -> float:
    den = denominator + selected_future + missed_future
    return 100.0 * (entries + selected_future) / den if den else 0.0


def live_net_cents() -> float | None:
    summary = load_json(LIVE_SUMMARY_JSON)
    dollars = summary.get("net_pnl_total_dollars")
    if dollars is None:
        return None
    return round(as_float(dollars) * 100.0)


def summarize_best(lane: dict[str, Any], live_net: float | None) -> dict[str, Any]:
    best = (lane.get("rows") or [{}])[0]
    entries = as_int(best.get("entries"))
    settled = as_int(best.get("settled"))
    denominator = as_int(lane.get("future_denominator"))
    reconstructed = current_reconstructed_count(best)
    net_cents = as_float(best.get("weighted_net_cents"))
    clean_needed = clean_rows_needed(entries, reconstructed)
    cushion_surplus = net_cents - MIN_CUSHION_CENTS
    required_entries_now = math.ceil(TARGET_COVERAGE_MIN * denominator / 100.0)
    selected_needed_now = max(0, required_entries_now - entries)

    clean_scenarios = []
    for future_clean in range(0, 8):
        for avg_net in (-100.0, -50.0, 0.0, 10.0, 25.0):
            future_net = net_cents + future_clean * avg_net
            future_entries = entries + future_clean
            future_den = denominator + future_clean
            future_share = reconstructed / future_entries if future_entries else 0.0
            future_cov = 100.0 * future_entries / future_den if future_den else 0.0
            future_delta_vs_live = None if live_net is None else future_net - live_net
            blockers: list[str] = []
            if settled + future_clean < MIN_SETTLED:
                blockers.append("settled_lt_30")
            if future_cov < TARGET_COVERAGE_MIN:
                blockers.append("coverage_too_low")
            if future_cov > TARGET_COVERAGE_MAX:
                blockers.append("coverage_too_high")
            if future_share > SOURCE_SHARE_MAX:
                blockers.append("row_reconstructed_share_gt_35pct")
            if future_net < MIN_CUSHION_CENTS:
                blockers.append("weighted_full_loss_cushion_lt_3")
            clean_scenarios.append({
                "future_clean_selected_rows": future_clean,
                "avg_future_net_cents": avg_net,
                "future_entries": future_entries,
                "future_denominator": future_den,
                "future_coverage_pct": future_cov,
                "future_row_reconstructed_share": future_share,
                "future_weighted_net_cents": future_net,
                "future_delta_vs_live_cents": future_delta_vs_live,
                "live_ready_by_count_gates": not blockers,
                "blockers": blockers,
            })

    missed_scenarios = []
    for missed in range(0, 8):
        missed_scenarios.append({
            "missed_future_markets": missed,
            "coverage_if_no_new_selected_rows": coverage_after(entries, denominator, 0, missed),
            "coverage_if_two_clean_selected_rows": coverage_after(entries, denominator, 2, missed),
        })

    viable_clean_scenarios = [
        row for row in clean_scenarios
        if row["live_ready_by_count_gates"]
    ]
    viable_clean_scenarios.sort(
        key=lambda row: (
            row["future_clean_selected_rows"],
            row["avg_future_net_cents"],
        )
    )
    delta_vs_live = None if live_net is None else net_cents - live_net
    cents_to_live_tie = None if delta_vs_live is None else max(0.0, -delta_vs_live)

    return {
        "lane": lane.get("lane"),
        "policy": best.get("policy"),
        "entries": entries,
        "settled": settled,
        "wins": best.get("wins"),
        "losses": best.get("losses"),
        "future_denominator": denominator,
        "coverage_pct": best.get("coverage_pct"),
        "weighted_net_cents": net_cents,
        "row_reconstructed_share": best.get("row_reconstructed_share"),
        "exposure_reconstructed_share": best.get("exposure_reconstructed_share"),
        "reconstructed_rows_estimate": reconstructed,
        "clean_selected_rows_needed_for_source": clean_needed,
        "selected_rows_needed_for_current_coverage_gate": selected_needed_now,
        "weighted_cushion_surplus_cents": cushion_surplus,
        "max_full_size_clean_losses_before_cushion_breaks": math.floor(max(0.0, cushion_surplus) / 100.0),
        "live_net_cents": live_net,
        "delta_vs_live_cents": delta_vs_live,
        "cents_to_live_tie": cents_to_live_tie,
        "full_weight_wins_to_live_tie": None if cents_to_live_tie is None else math.ceil(cents_to_live_tie / 100.0),
        "blockers": best.get("blockers") or [],
        "first_viable_clean_scenario": viable_clean_scenarios[0] if viable_clean_scenarios else None,
        "clean_selected_row_scenarios": clean_scenarios,
        "missed_market_coverage_scenarios": missed_scenarios,
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    live_net = live_net_cents()
    lanes = [
        summarize_best(lane, live_net)
        for lane in source.get("lanes") or []
        if isinstance(lane, dict)
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "source": str(SOURCE_JSON),
        "live_summary": str(LIVE_SUMMARY_JSON),
        "live_net_cents": live_net,
        "feature_gate_freeze_ts_utc": source.get("freeze_ts_utc"),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Runway is count-gate math only; it does not promote the candidate or prove future PnL.",
    ]
    for lane in report.get("lanes") or []:
        viable = lane.get("first_viable_clean_scenario") or {}
        if viable:
            notes.append(
                f"{lane.get('lane')}: needs {lane.get('clean_selected_rows_needed_for_source')} clean selected rows; "
                f"first count-gate viable scenario is {viable.get('future_clean_selected_rows')} clean rows averaging "
                f"{viable.get('avg_future_net_cents')}c, resulting net {viable.get('future_weighted_net_cents')}c and "
                f"source share {viable.get('future_row_reconstructed_share')}."
            )
            if lane.get("delta_vs_live_cents") is not None:
                notes.append(
                    f"{lane.get('lane')}: current weighted net is {lane.get('delta_vs_live_cents')}c versus the "
                    "refreshed live-only baseline, so count-gate viability alone is not promotion readiness."
                )
        else:
            notes.append(
                f"{lane.get('lane')}: no tested clean-row scenario clears count gates."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Coverage Size-Shrink Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Refreshed live net: `{fmt(report.get('live_net_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        viable = lane.get("first_viable_clean_scenario") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Policy: `{lane.get('policy')}`",
            f"- Current entries/denominator: `{lane.get('entries')}/{lane.get('future_denominator')}`",
            f"- Current W/L/net/coverage: `{lane.get('wins')}/{lane.get('losses')}` / `{fmt(lane.get('weighted_net_cents'))}c` / `{fmt(lane.get('coverage_pct'))}%`",
            f"- Row/exposure reconstructed share: `{fmt(lane.get('row_reconstructed_share'))}/{fmt(lane.get('exposure_reconstructed_share'))}`",
            f"- Clean selected rows needed for source gate: `{lane.get('clean_selected_rows_needed_for_source')}`",
            f"- Weighted cushion surplus above 300c: `{fmt(lane.get('weighted_cushion_surplus_cents'))}c`",
            f"- Delta versus refreshed live net: `{fmt(lane.get('delta_vs_live_cents'))}c`",
            f"- Full-weight wins needed to tie live: `{lane.get('full_weight_wins_to_live_tie')}`",
            f"- First viable count-gate scenario: `{viable or 'none'}`",
            "",
            "### Coverage If Future Markets Are Missed",
            "",
            "| missed markets | no new selected coverage | with 2 clean selected coverage |",
            "|---:|---:|---:|",
        ])
        for row in lane.get("missed_market_coverage_scenarios") or []:
            lines.append(
                f"| {row.get('missed_future_markets')} | {fmt(row.get('coverage_if_no_new_selected_rows'))}% | "
                f"{fmt(row.get('coverage_if_two_clean_selected_rows'))}% |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())


if __name__ == "__main__":
    main()
