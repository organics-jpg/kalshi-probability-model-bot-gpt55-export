"""Exit attribution for the v28 feature-gate middle-distance core.

Research-only; no live bot changes or orders.

The middle-distance core is source-clean and high win-rate but narrow. This
probe checks whether its remaining damage is exit-policy/state damage or true
entry/FV failure. It reports both settlement/hold losses and current-exit vs
hold deltas, because an exit can hurt rows that eventually settle as winners.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
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
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge
from probe_v28_feature_gate_near_promotion_exit_attribution import (
    EXIT_SOURCES,
    choose_exit,
    classify_exit,
    exit_current,
    exit_hold,
    parse_ts,
    side,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDDLE_STATE_JSON = OUT_DIR / "v28_feature_gate_middle_distance_core_watch_state.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_middle_core_exit_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_middle_core_exit_attribution_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    ask_cents = as_float(row.get("ask_cents"))
    return ask_cents / 100.0 if ask_cents is not None else None


def abs_d(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("abs_d_sigma"))
    return abs(value) if value is not None else None


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


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


def exit_matches_for(row: dict[str, Any], exits: dict[str, dict[tuple[str, str], list[dict[str, Any]]]]) -> dict[str, Any]:
    key = (market(row), side(row))
    matches: dict[str, Any] = {}
    for name, index in exits.items():
        match = choose_exit(index.get(key) or [])
        if not match:
            continue
        current = exit_current(match)
        hold = exit_hold(match)
        delta = None if current is None or hold is None else hold - current
        matches[name] = {
            "current_cents": current,
            "hold_cents": hold,
            "hold_minus_current_cents": delta,
            "classification": classify_exit(current, hold),
            "exit_reason": match.get("exit_reason"),
            "p_hold": match.get("p_hold"),
            "fair_drawdown_cents": match.get("fair_drawdown_cents"),
            "hold_book_gap": match.get("hold_book_gap"),
            "suppressed": match.get("suppressed"),
            "exit_ts": match.get("exit_ts"),
        }
    return matches


def best_exit_delta(matches: dict[str, Any]) -> float | None:
    deltas = [
        as_float(match.get("hold_minus_current_cents"))
        for match in matches.values()
        if as_float(match.get("hold_minus_current_cents")) is not None
    ]
    if not deltas:
        return None
    return max(deltas, key=lambda value: abs(value))


def primary_class(matches: dict[str, Any]) -> str:
    if not matches:
        return "no_exit_observation"
    counts = Counter(match.get("classification") for match in matches.values())
    if counts.get("exit_helped_vs_hold", 0) >= max(counts.values()):
        return "entry_or_fv_failure_exit_helped"
    if counts.get("exit_hurt_or_clipped_winner", 0):
        return "exit_policy_failure_candidate"
    return str(counts.most_common(1)[0][0])


def compact_row(row: dict[str, Any], matches: dict[str, Any]) -> dict[str, Any]:
    delta = best_exit_delta(matches)
    return {
        "market": market(row),
        "side": side(row),
        "source": source(row),
        "entry_hold_cents": net(row),
        "side_won": row.get("side_won"),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "ask_prob": ask_prob(row),
        "primary_exit_class": primary_class(matches),
        "best_hold_minus_current_cents": delta,
        "exit_matches": matches,
    }


def selected_core_rows(freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> tuple[list[dict[str, Any]], int]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    return best_per_market([row for row in rows if pass_abs_floor_core(row)]), int(denominator or 0)


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any], exits: dict[str, Any]) -> dict[str, Any]:
    rows, denominator = selected_core_rows(freeze_ts, surfaces_fn)
    attributed = [compact_row(row, exit_matches_for(row, exits)) for row in rows]
    settled = [row for row in attributed if row.get("side_won") is not None]
    hold_net = sum(float(row.get("entry_hold_cents") or 0.0) for row in settled)
    matched = [row for row in attributed if row.get("exit_matches")]
    current_by_source: dict[str, float] = {}
    hold_by_source: dict[str, float] = {}
    delta_by_source: dict[str, float] = {}
    class_by_source: dict[str, dict[str, int]] = {}
    for name in EXIT_SOURCES:
        current_sum = 0.0
        hold_sum = 0.0
        count = Counter()
        matched_count = 0
        for row in attributed:
            match = (row.get("exit_matches") or {}).get(name)
            if not match:
                continue
            current = as_float(match.get("current_cents"))
            hold = as_float(match.get("hold_cents"))
            if current is None or hold is None:
                continue
            matched_count += 1
            current_sum += current
            hold_sum += hold
            count[str(match.get("classification"))] += 1
        if matched_count:
            current_by_source[name] = current_sum
            hold_by_source[name] = hold_sum
            delta_by_source[name] = hold_sum - current_sum
            class_by_source[name] = dict(count)
    settlement_losses = [row for row in attributed if float(row.get("entry_hold_cents") or 0.0) < 0]
    exit_harm = [
        row for row in attributed
        if (row.get("best_hold_minus_current_cents") is not None and float(row["best_hold_minus_current_cents"]) > 0)
    ]
    exit_help = [
        row for row in attributed
        if (row.get("best_hold_minus_current_cents") is not None and float(row["best_hold_minus_current_cents"]) < 0)
    ]
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if float(row.get("entry_hold_cents") or 0.0) > 0),
        "losses": sum(1 for row in settled if float(row.get("entry_hold_cents") or 0.0) < 0),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "entry_hold_net_cents": hold_net,
        "source_counts": dict(Counter(row.get("source") for row in attributed)),
        "settlement_loss_count": len(settlement_losses),
        "settlement_loss_cents": sum(float(row.get("entry_hold_cents") or 0.0) for row in settlement_losses),
        "settlement_loss_failure_classes": dict(Counter(row.get("primary_exit_class") for row in settlement_losses)),
        "exit_matched_rows": len(matched),
        "exit_harm_rows": len(exit_harm),
        "exit_harm_cents_if_held": sum(float(row.get("best_hold_minus_current_cents") or 0.0) for row in exit_harm),
        "exit_help_rows": len(exit_help),
        "exit_help_cents_vs_hold": sum(float(row.get("best_hold_minus_current_cents") or 0.0) for row in exit_help),
        "current_by_exit_source_cents": current_by_source,
        "hold_by_exit_source_cents": hold_by_source,
        "hold_minus_current_by_exit_source_cents": delta_by_source,
        "classification_by_exit_source": class_by_source,
        "worst_settlement_rows": sorted(settlement_losses, key=lambda row: float(row.get("entry_hold_cents") or 0.0))[:10],
        "largest_exit_harm_rows": sorted(exit_harm, key=lambda row: float(row.get("best_hold_minus_current_cents") or 0.0), reverse=True)[:10],
        "largest_exit_help_rows": sorted(exit_help, key=lambda row: float(row.get("best_hold_minus_current_cents") or 0.0))[:10],
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Research-only exit attribution; no live bot changes or orders.",
        "Entry-hold PnL uses settlement/hold rows; exit-source deltas use frozen exit artifacts and are diagnostic only.",
    ]
    for lane in lanes:
        notes.append(
            f"{lane.get('lane')}: core W/L {lane.get('wins')}/{lane.get('losses')}, "
            f"entry-hold net {lane.get('entry_hold_net_cents')}c, settlement loss classes "
            f"{lane.get('settlement_loss_failure_classes')}, exit-harm rows {lane.get('exit_harm_rows')} "
            f"worth {lane.get('exit_harm_cents_if_held')}c if held."
        )
    return notes


def build_report() -> dict[str, Any]:
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or "")
    middle_state = load_json(MIDDLE_STATE_JSON)
    middle_freeze = str(middle_state.get("freeze_ts_utc") or "")
    exits = load_exit_index()
    lanes = [
        evaluate_lane("diagnostic_feature_window_entry", feature_freeze, entry_surfaces, exits),
        evaluate_lane("diagnostic_feature_window_bridge", feature_freeze, bridge_surfaces, exits),
        evaluate_lane("post_middle_core_freeze_entry", middle_freeze, entry_surfaces, exits) if middle_freeze else {},
        evaluate_lane("post_middle_core_freeze_bridge", middle_freeze, bridge_surfaces, exits) if middle_freeze else {},
    ]
    lanes = [lane for lane in lanes if lane]
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_freeze,
        "middle_core_freeze_ts_utc": middle_freeze,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
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
        "# v28 Feature-Gate Middle-Core Exit Attribution",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate parent freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Middle-core watch freeze UTC: `{report.get('middle_core_freeze_ts_utc')}`",
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
                f"- Entries / settled: `{lane.get('entries')}/{lane.get('settled')}`",
                f"- W/L: `{lane.get('wins')}/{lane.get('losses')}`",
                f"- Coverage: `{fmt(lane.get('coverage_pct'))}%`",
                f"- Entry-hold net: `{fmt(lane.get('entry_hold_net_cents'))}c`",
                f"- Source counts: `{lane.get('source_counts')}`",
                f"- Settlement loss classes: `{lane.get('settlement_loss_failure_classes')}`",
                f"- Exit-harm rows/cents-if-held: `{lane.get('exit_harm_rows')}/{fmt(lane.get('exit_harm_cents_if_held'))}c`",
                f"- Exit-help rows/cents-vs-hold: `{lane.get('exit_help_rows')}/{fmt(lane.get('exit_help_cents_vs_hold'))}c`",
                "",
                "### Exit Source Rollup",
                "",
                "| source | current c | hold c | hold-current c | classes |",
                "|---|---:|---:|---:|---|",
            ]
        )
        current_by = lane.get("current_by_exit_source_cents") or {}
        hold_by = lane.get("hold_by_exit_source_cents") or {}
        delta_by = lane.get("hold_minus_current_by_exit_source_cents") or {}
        classes_by = lane.get("classification_by_exit_source") or {}
        for name in sorted(set(current_by) | set(hold_by) | set(delta_by)):
            lines.append(
                f"| `{name}` | {fmt(current_by.get(name))} | {fmt(hold_by.get(name))} | "
                f"{fmt(delta_by.get(name))} | `{classes_by.get(name)}` |"
            )
        lines.extend(
            [
                "",
                "### Settlement Loss Rows",
                "",
                "| market | side | source | hold net | primary class | best hold-current | abs d | ask | recross |",
                "|---|---|---|---:|---|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("worst_settlement_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('entry_hold_cents'))} | {row.get('primary_exit_class')} | "
                f"{fmt(row.get('best_hold_minus_current_cents'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('recross_hazard_score'))} |"
            )
        lines.extend(
            [
                "",
                "### Largest Exit-Harm Rows",
                "",
                "| market | side | source | hold net | best hold-current | primary class |",
                "|---|---|---|---:|---:|---|",
            ]
        )
        for row in lane.get("largest_exit_harm_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('entry_hold_cents'))} | {fmt(row.get('best_hold_minus_current_cents'))} | "
                f"{row.get('primary_exit_class')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
