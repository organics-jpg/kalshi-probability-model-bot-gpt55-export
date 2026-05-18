"""Expansion bound for the v28 feature-gate middle-distance core.

Research-only; no live bot changes or orders.

The middle-distance core watch found a clean, high-win, low-source-share pocket,
but it is too narrow. This probe asks whether the currently observed approved
row pool can expand that pocket toward broad coverage without reopening the
source-quality blocker.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    STATE_JSON as FEATURE_STATE_JSON,
    as_float,
    best_per_market,
    load_json,
    market,
    net,
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDDLE_STATE_JSON = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_state.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_middle_core_expansion_bound_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_middle_core_expansion_bound_latest.md"

TARGET_COVERAGE_MIN = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    ask_cents = as_float(row.get("ask_cents"))
    return ask_cents / 100.0 if ask_cents is not None else None


def abs_d(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("abs_d_sigma"))
    return abs(value) if value is not None else None


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(market(row) or ""), str(row.get("side") or "")


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def live_net_cents() -> float:
    if not LIVE_SUMMARY_JSON.exists():
        return 0.0
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def pass_abs_floor_core(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    row_abs = abs_d(row)
    ask = ask_prob(row)
    return (
        edge is not None
        and edge >= 0.03
        and row_recross is not None
        and row_recross <= 0.50
        and row_abs is not None
        and row_abs >= 0.75
        and ask is not None
        and ask >= 0.35
    )


def approved_candidate_predicates() -> list[tuple[str, Callable[[dict[str, Any]], bool]]]:
    return [
        ("any_omitted_approved", lambda row: True),
        (
            "approved_raw03_recross70_ask35",
            lambda row: (raw_edge(row) or -99.0) >= 0.03
            and (recross(row) or 99.0) <= 0.70
            and (ask_prob(row) or -1.0) >= 0.35,
        ),
        (
            "approved_raw00_recross70_ask35",
            lambda row: (recross(row) or 99.0) <= 0.70 and (ask_prob(row) or -1.0) >= 0.35,
        ),
        (
            "approved_raw03_recross90_ask35",
            lambda row: (raw_edge(row) or -99.0) >= 0.03
            and (recross(row) or 99.0) <= 0.90
            and (ask_prob(row) or -1.0) >= 0.35,
        ),
        (
            "approved_abs50_raw03_recross70_ask35",
            lambda row: (raw_edge(row) or -99.0) >= 0.03
            and (recross(row) or 99.0) <= 0.70
            and (ask_prob(row) or -1.0) >= 0.35
            and (abs_d(row) or 0.0) >= 0.50,
        ),
    ]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "side_won": row.get("side_won"),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "ask_prob": ask_prob(row),
        "p_side": row.get("p_side"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
    }


def row_source_share(rows: list[dict[str, Any]]) -> float | None:
    counts = Counter(source(row) for row in rows)
    return reconstructed_share(dict(counts))


def scenario(
    label: str,
    rows: list[dict[str, Any]],
    denominator: int,
    live_net: float,
    broad_required: bool,
) -> dict[str, Any]:
    summary = summarize(rows, denominator)
    share = row_source_share(rows)
    net_cents = fnum(summary.get("net_cents"))
    blockers: list[str] = []
    if int(fnum(summary.get("settled"))) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if broad_required and fnum(summary.get("coverage_pct")) < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if net_cents <= 0:
        blockers.append("net_not_positive")
    if math.floor(max(0.0, net_cents) / 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net_cents <= live_net:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return {
        "scenario": label,
        "summary": summary,
        "source_counts": dict(Counter(source(row) for row in rows)),
        "reconstructed_share": share,
        "full_loss_cushion_estimate": math.floor(max(0.0, net_cents) / 100.0),
        "delta_vs_live_cents": net_cents - live_net,
        "blockers": blockers,
        "live_ready": not blockers,
        "rows": [compact_row(row) for row in sorted(rows, key=lambda item: net(item))],
    }


def best_reconstructed_fill(core_rows: list[dict[str, Any]], omitted_rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    required = max(0, math.ceil((TARGET_COVERAGE_MIN / 100.0) * denominator) - len(core_rows))
    recon = [
        row
        for row in omitted_rows
        if source(row) != "approved_entry" and is_settled(row)
    ]
    recon_sorted = sorted(recon, key=lambda row: net(row), reverse=True)
    candidate = list(core_rows)
    for row in recon_sorted:
        if len(candidate) >= len(core_rows) + required:
            break
        test = candidate + [row]
        share = row_source_share(test)
        if share is None or share <= MAX_RECONSTRUCTED_SHARE:
            candidate.append(row)
    return candidate


def evaluate_lane(label: str, rows: list[dict[str, Any]], denominator: int, live_net: float) -> dict[str, Any]:
    denominator = int(denominator or 0)
    core_rows = best_per_market([row for row in rows if pass_abs_floor_core(row)])
    core_keys = {row_key(row) for row in core_rows}
    omitted = [row for row in rows if row_key(row) not in core_keys]
    required_for_75 = max(0, math.ceil((TARGET_COVERAGE_MIN / 100.0) * denominator) - len(core_rows))

    approved_expansions = []
    for name, pred in approved_candidate_predicates():
        pool = [
            row
            for row in omitted
            if source(row) == "approved_entry" and is_settled(row) and pred(row)
        ]
        selected = best_per_market(pool)
        combined = core_rows + selected
        approved_expansions.append(
            {
                "rule": name,
                "approved_addable_rows": len(selected),
                "approved_addable_net_cents": sum(net(row) for row in selected),
                "approved_addable_wins": sum(1 for row in selected if net(row) > 0),
                "approved_addable_losses": sum(1 for row in selected if net(row) < 0),
                "scenario": scenario(f"core_plus_{name}", combined, denominator, live_net, broad_required=True),
                "addable_rows": [compact_row(row) for row in sorted(selected, key=lambda item: net(item))],
            }
        )
    approved_expansions.sort(
        key=lambda item: (
            len(((item.get("scenario") or {}).get("blockers") or [])),
            -fnum(((item.get("scenario") or {}).get("summary") or {}).get("net_cents")),
            -fnum(((item.get("scenario") or {}).get("summary") or {}).get("coverage_pct")),
        )
    )

    source_gate_fill = best_reconstructed_fill(core_rows, omitted, denominator)
    return {
        "lane": label,
        "future_denominator": denominator,
        "required_entries_for_75pct": math.ceil((TARGET_COVERAGE_MIN / 100.0) * denominator) if denominator else 0,
        "core_entries": len(core_rows),
        "entries_needed_to_75pct": required_for_75,
        "omitted_rows": len(omitted),
        "omitted_approved_settled_market_side_count": len(
            best_per_market([row for row in omitted if source(row) == "approved_entry" and is_settled(row)])
        ),
        "core": scenario("abs_floor_core_raw03_recross50_abs075_ask35", core_rows, denominator, live_net, broad_required=True),
        "approved_expansions": approved_expansions,
        "best_source_gate_fill": scenario(
            "best_reconstructed_fill_under_35pct_source_gate",
            source_gate_fill,
            denominator,
            live_net,
            broad_required=True,
        ),
        "source_gate_fill_added_rows": [
            compact_row(row) for row in source_gate_fill if row_key(row) not in core_keys
        ],
    }


def interpretation(lanes: list[dict[str, Any]], live_net: float) -> list[str]:
    notes = [
        "Research-only expansion-bound audit; no live bot changes or orders.",
        f"Live baseline for delta math is {live_net:.0f}c.",
    ]
    for lane in lanes:
        core_summary = (lane.get("core") or {}).get("summary") or {}
        best_approved = (lane.get("approved_expansions") or [{}])[0]
        best_approved_scenario = best_approved.get("scenario") or {}
        best_approved_summary = best_approved_scenario.get("summary") or {}
        best_fill = lane.get("best_source_gate_fill") or {}
        best_fill_summary = best_fill.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: core has {lane.get('core_entries')} entries vs "
            f"{lane.get('required_entries_for_75pct')} required for 75%; it needs "
            f"{lane.get('entries_needed_to_75pct')} more entries."
        )
        notes.append(
            f"{lane.get('lane')}: best approved-only expansion adds "
            f"{best_approved.get('approved_addable_rows')} rows with "
            f"{best_approved.get('approved_addable_net_cents')}c addable PnL; combined coverage "
            f"{best_approved_summary.get('coverage_pct')}% and net {best_approved_summary.get('net_cents')}c."
        )
        notes.append(
            f"{lane.get('lane')}: even the best reconstructed fill that stays under the 35% source gate reaches "
            f"{best_fill_summary.get('coverage_pct')}% coverage and {best_fill_summary.get('net_cents')}c; "
            f"blockers {best_fill.get('blockers')}."
        )
        if core_summary:
            notes.append(
                f"{lane.get('lane')}: conclusion is source/coverage supply, not core quality; current core W/L is "
                f"{core_summary.get('wins')}/{core_summary.get('losses')} with {core_summary.get('net_cents')}c."
            )
    return notes


def build_report() -> dict[str, Any]:
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or "")
    middle_state = load_json(MIDDLE_STATE_JSON)
    middle_freeze = str(middle_state.get("freeze_ts_utc") or "")
    live_net = live_net_cents()
    feature_entry_rows, _, feature_entry_denominator = entry_surfaces(feature_freeze)
    feature_bridge_rows, _, feature_bridge_denominator = bridge_surfaces(feature_freeze)
    middle_entry_rows, _, middle_entry_denominator = entry_surfaces(middle_freeze) if middle_freeze else ([], [], 0)
    middle_bridge_rows, _, middle_bridge_denominator = bridge_surfaces(middle_freeze) if middle_freeze else ([], [], 0)
    lanes = [
        evaluate_lane("diagnostic_feature_window_entry", feature_entry_rows, int(feature_entry_denominator or 0), live_net),
        evaluate_lane("diagnostic_feature_window_bridge", feature_bridge_rows, int(feature_bridge_denominator or 0), live_net),
        evaluate_lane("post_middle_core_freeze_entry", middle_entry_rows, int(middle_entry_denominator or 0), live_net),
        evaluate_lane("post_middle_core_freeze_bridge", middle_bridge_rows, int(middle_bridge_denominator or 0), live_net),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_freeze,
        "middle_core_freeze_ts_utc": middle_freeze,
        "live_baseline_cents": live_net,
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_net),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Middle-Core Expansion Bound",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate parent freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Middle-core watch freeze UTC: `{report.get('middle_core_freeze_ts_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Denominator: `{lane.get('future_denominator')}`",
                f"- Core entries: `{lane.get('core_entries')}`",
                f"- Required entries for 75%: `{lane.get('required_entries_for_75pct')}`",
                f"- Entries needed to 75%: `{lane.get('entries_needed_to_75pct')}`",
                f"- Omitted approved settled market/sides: `{lane.get('omitted_approved_settled_market_side_count')}`",
                "",
                "### Scenarios",
                "",
                "| scenario | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        scenario_rows = [lane.get("core") or {}, lane.get("best_source_gate_fill") or {}]
        scenario_rows.extend((item.get("scenario") or {}) for item in lane.get("approved_expansions") or [])
        seen = set()
        for scenario_row in scenario_rows:
            name = scenario_row.get("scenario")
            if not name or name in seen:
                continue
            seen.add(name)
            summary = scenario_row.get("summary") or {}
            blockers = ", ".join(scenario_row.get("blockers") or []) or "none"
            lines.append(
                f"| `{name}` | {summary.get('entries')} | {summary.get('settled')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
                f"{fmt(summary.get('net_cents'))} | {fmt(scenario_row.get('delta_vs_live_cents'))} | "
                f"{fmt(scenario_row.get('reconstructed_share'))} | {scenario_row.get('full_loss_cushion_estimate')} | {blockers} |"
            )
        lines.extend(
            [
                "",
                "### Approved Addable Rows",
                "",
                "| rule | add rows | add W/L | add net c | combined coverage | combined net c |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for item in lane.get("approved_expansions") or []:
            combined = (item.get("scenario") or {}).get("summary") or {}
            lines.append(
                f"| `{item.get('rule')}` | {item.get('approved_addable_rows')} | "
                f"{item.get('approved_addable_wins')}/{item.get('approved_addable_losses')} | "
                f"{fmt(item.get('approved_addable_net_cents'))} | {fmt(combined.get('coverage_pct'))}% | "
                f"{fmt(combined.get('net_cents'))} |"
            )
        if lane.get("approved_expansions"):
            first_rows = (lane["approved_expansions"][0].get("addable_rows") or [])
            if first_rows:
                lines.extend(
                    [
                        "",
                        "### Best Approved Addable Row Detail",
                        "",
                        "| market | side | net | raw edge | recross | abs d | ask | p_side |",
                        "|---|---|---:|---:|---:|---:|---:|---:|",
                    ]
                )
                for row in first_rows:
                    lines.append(
                        f"| `{row.get('market')}` | {row.get('side')} | {fmt(row.get('net_cents'))} | "
                        f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                        f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('p_side'))} |"
                    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
