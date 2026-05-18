"""Coverage repair scan for the guarded v28 feature-gate branch.

Research-only. This starts from the side-displacement-guarded raw03 feature-gate
lane and asks whether small observable relaxations can reach 75% coverage without
reopening source-quality, cushion, or live-baseline blockers. It uses source
labels and realized PnL only for audit/ranking, not as deployable proof.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    best_per_market,
    load_json as fg_load_json,
    market,
    net,
    passes,
    raw_edge,
    recross,
    source,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_feature_gate_side_displacement_guard import live_net_cents


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_guarded_coverage_repair_scan_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_guarded_coverage_repair_scan_latest.md"

FEATURE_STATE = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_state.json"
SIDE_GUARD = OUT_DIR / "v28_feature_gate_side_displacement_guard_latest.json"

MIN_COVERAGE = 75.0
MAX_RECON_SHARE = 0.35
MIN_CUSHION = 3
BASE_RULE_NAME = "raw03_recross70_abs075"
ASK65_RULE_NAME = "raw05_recross60_abs085_ask65"

RELAXATIONS = {
    "absd65_keep_raw03_recross70": {"raw_edge_min": 0.03, "recross_max": 0.70, "abs_d_min": 0.65, "ask_min": None},
    "absd50_keep_raw03_recross70": {"raw_edge_min": 0.03, "recross_max": 0.70, "abs_d_min": 0.50, "ask_min": None},
    "recross85_keep_raw03_abs075": {"raw_edge_min": 0.03, "recross_max": 0.85, "abs_d_min": 0.75, "ask_min": None},
    "raw00_keep_recross70_abs075": {"raw_edge_min": 0.00, "recross_max": 0.70, "abs_d_min": 0.75, "ask_min": None},
    "ask35_absd65_raw03_recross70": {"raw_edge_min": 0.03, "recross_max": 0.70, "abs_d_min": 0.65, "ask_min": 0.35},
    "ask50_absd65_raw03_recross70": {"raw_edge_min": 0.03, "recross_max": 0.70, "abs_d_min": 0.65, "ask_min": 0.50},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fmt_cents(value: Any) -> str:
    try:
        return f"{float(value):.0f}c"
    except (TypeError, ValueError):
        return "n/a"


def fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def fmt_num(value: Any, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def load_json(path: Path) -> dict[str, Any]:
    return fg_load_json(path)


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (market(row), str(row.get("side") or ""))


def best_by_market(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected = best_per_market(rows)
    return {market(row): row for row in selected}


def apply_high_ask_guard(base_rows: list[dict[str, Any]], ask65_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ask_by_market: dict[str, list[dict[str, Any]]] = {}
    for row in ask65_rows:
        ask_by_market.setdefault(market(row), []).append(row)
    guarded = []
    for row in base_rows:
        ask = as_float(row.get("ask_prob"))
        alternatives = [
            alt
            for alt in ask_by_market.get(market(row), [])
            if row_key(alt) != row_key(row)
            and as_float(alt.get("ask_prob")) is not None
            and float(as_float(alt.get("ask_prob")) or 0.0) >= 0.85
        ]
        if ask is not None and ask <= 0.10 and alternatives:
            guarded.append(max(alternatives, key=lambda item: as_float(item.get("ask_prob")) or 0.0))
        else:
            guarded.append(row)
    return guarded


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def summarize(rows: list[dict[str, Any]], entries: int, denominator: int, live_cents: float) -> dict[str, Any]:
    counts = source_counts(rows)
    settled = len(rows)
    wins = sum(1 for row in rows if net(row) > 0)
    losses = sum(1 for row in rows if net(row) < 0)
    net_cents = sum(net(row) for row in rows)
    recon_share = ((settled - int(counts.get("approved_entry", 0))) / settled) if settled else None
    coverage = entries / denominator * 100.0 if denominator else 0.0
    blockers = []
    if settled < 30:
        blockers.append("settled_lt_30")
    if coverage < MIN_COVERAGE:
        blockers.append("coverage_too_low")
    if net_cents <= 0:
        blockers.append("net_not_positive")
    if recon_share is not None and recon_share > MAX_RECON_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    cushion = int(net_cents // 100) if net_cents > 0 else 0
    if cushion < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net_cents <= live_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return {
        "entries": entries,
        "settled": settled,
        "coverage_pct": coverage,
        "wins": wins,
        "losses": losses,
        "net_cents": net_cents,
        "delta_vs_live_cents": net_cents - live_cents,
        "reconstructed_share": recon_share,
        "source_counts": counts,
        "full_loss_cushion": cushion,
        "blockers": blockers,
    }


def miss_reasons(row: dict[str, Any], base_rule: dict[str, Any]) -> list[str]:
    reasons = []
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    if edge is None or edge < float(base_rule["raw_edge_min"]):
        reasons.append("raw_edge_below_min")
    if row_recross is None or row_recross > float(base_rule["recross_max"]):
        reasons.append("recross_above_max")
    if abs_d is None or abs_d < float(base_rule["abs_d_min"]):
        reasons.append("abs_d_below_min")
    return reasons


def candidate_row_payload(row: dict[str, Any], relaxation: str, base_rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "side_won": row.get("side_won"),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "relaxation": relaxation,
        "base_miss_reasons": miss_reasons(row, base_rule),
    }


def scan_lane(label: str, surfaces_fn: Any, freeze_ts: str, live_cents: float) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    base_rule = RULES[BASE_RULE_NAME]
    ask65_rule = RULES[ASK65_RULE_NAME]

    base_rows = best_per_market([row for row in all_rows if passes(row, base_rule)])
    ask65_rows = best_per_market([row for row in all_rows if passes(row, ask65_rule)])
    guarded_rows = apply_high_ask_guard(base_rows, ask65_rows)
    guarded_markets = {market(row) for row in guarded_rows}

    base_summary = summarize(guarded_rows, len(guarded_rows), denominator, live_cents)
    row_by_market_side = {row_key(row): row for row in all_rows}

    candidates: list[dict[str, Any]] = []
    for relaxation_name, rule in RELAXATIONS.items():
        relaxed_rows = best_per_market([row for row in all_rows if passes(row, rule)])
        for row in relaxed_rows:
            if market(row) in guarded_markets:
                continue
            repaired_rows = guarded_rows + [row]
            summary = summarize(repaired_rows, len(guarded_rows) + 1, denominator, live_cents)
            payload = {
                "repair": f"{BASE_RULE_NAME}_guarded_plus_{relaxation_name}_one_row",
                "relaxation": relaxation_name,
                "added_row": candidate_row_payload(row, relaxation_name, base_rule),
                "summary": summary,
            }
            candidates.append(payload)

    # Keep the most relevant rows: gate-near first, then PnL.
    candidates.sort(
        key=lambda item: (
            len((item.get("summary") or {}).get("blockers") or []),
            -float((item.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )
    unique: list[dict[str, Any]] = []
    seen = set()
    for item in candidates:
        key = (item["added_row"]["market"], item["added_row"]["side"], item["relaxation"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    addable_by_row: dict[tuple[str, str], dict[str, Any]] = {}
    for item in unique:
        row = item.get("added_row") or {}
        key = (str(row.get("market") or ""), str(row.get("side") or ""))
        if not key[0]:
            continue
        if key not in addable_by_row:
            addable_by_row[key] = item
    addable = list(addable_by_row.values())
    pair_candidates: list[dict[str, Any]] = []
    for left, right in combinations(addable, 2):
        left_row = left["added_row"]
        right_row = right["added_row"]
        if left_row["market"] == right_row["market"]:
            continue
        left_actual = row_by_market_side.get((str(left_row["market"]), str(left_row.get("side") or ""))) or left_row
        right_actual = row_by_market_side.get((str(right_row["market"]), str(right_row.get("side") or ""))) or right_row
        repaired_rows = guarded_rows + [
            left_actual,
            right_actual,
        ]
        summary = summarize(repaired_rows, len(guarded_rows) + 2, denominator, live_cents)
        pair_candidates.append(
            {
                "repair": f"{BASE_RULE_NAME}_guarded_plus_two_relaxed_rows",
                "relaxations": [left.get("relaxation"), right.get("relaxation")],
                "added_rows": [left_row, right_row],
                "added_net_cents": net(left_actual) + net(right_actual),
                "summary": summary,
            }
        )
    pair_candidates.sort(
        key=lambda item: (
            len((item.get("summary") or {}).get("blockers") or []),
            -float((item.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )

    triple_candidates: list[dict[str, Any]] = []
    for left, middle, right in combinations(addable, 3):
        rows = [left["added_row"], middle["added_row"], right["added_row"]]
        markets = {str(row.get("market") or "") for row in rows}
        if len(markets) != 3:
            continue
        actuals = [
            row_by_market_side.get((str(row["market"]), str(row.get("side") or ""))) or row
            for row in rows
        ]
        repaired_rows = guarded_rows + actuals
        summary = summarize(repaired_rows, len(guarded_rows) + 3, denominator, live_cents)
        triple_candidates.append(
            {
                "repair": f"{BASE_RULE_NAME}_guarded_plus_three_relaxed_rows",
                "relaxations": [left.get("relaxation"), middle.get("relaxation"), right.get("relaxation")],
                "added_rows": rows,
                "added_net_cents": sum(net(row) for row in actuals),
                "summary": summary,
            }
        )
    triple_candidates.sort(
        key=lambda item: (
            len((item.get("summary") or {}).get("blockers") or []),
            -float((item.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )

    return {
        "lane": label,
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "base_policy": f"{BASE_RULE_NAME}_ask85_over_cheap10_priority",
        "base_summary": base_summary,
        "repair_candidates": unique[:30],
        "pair_repair_candidates": pair_candidates[:30],
        "triple_repair_candidates": triple_candidates[:30],
        "best_by_gate_distance": unique[0] if unique else {},
        "best_pair_by_gate_distance": pair_candidates[0] if pair_candidates else {},
        "best_triple_by_gate_distance": triple_candidates[0] if triple_candidates else {},
    }


def build_report() -> dict[str, Any]:
    state = load_json(FEATURE_STATE)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    live_cents = live_net_cents()
    lanes = [
        scan_lane("post_feature_freeze_entry", entry_surfaces, freeze_ts, live_cents),
        scan_lane("post_feature_freeze_bridge", bridge_surfaces, freeze_ts, live_cents),
    ]
    best_repairs = [lane.get("best_by_gate_distance") or {} for lane in lanes]
    best_pair_repairs = [lane.get("best_pair_by_gate_distance") or {} for lane in lanes]
    best_triple_repairs = [lane.get("best_triple_by_gate_distance") or {} for lane in lanes]
    best_coverage = max(
        (as_float((repair.get("summary") or {}).get("coverage_pct")) for repair in best_repairs if repair),
        default=0.0,
    )
    best_pair_coverage = max(
        (as_float((repair.get("summary") or {}).get("coverage_pct")) for repair in best_pair_repairs if repair),
        default=0.0,
    )
    best_triple_coverage = max(
        (as_float((repair.get("summary") or {}).get("coverage_pct")) for repair in best_triple_repairs if repair),
        default=0.0,
    )
    largest_gap = max(
        (
            max(0, math.ceil(MIN_COVERAGE / 100.0 * int(lane.get("future_denominator") or 0)) - int((lane.get("base_summary") or {}).get("entries") or 0))
            for lane in lanes
        ),
        default=0,
    )
    if best_coverage >= MIN_COVERAGE:
        coverage_note = (
            f"One-row observable coverage repair reaches {fmt_pct(best_coverage)} nominal coverage, "
            "but current candidates still fail live-baseline and/or cushion gates."
        )
    else:
        coverage_note = (
            f"After the current denominator update, one-row observable repairs reach only {fmt_pct(best_coverage)} coverage; "
            f"at least {largest_gap} added markets are required for the 75% gate."
        )
    interpretation = [
        "Research-only guarded coverage repair scan; no live bot changes or orders.",
        "The scan starts from the raw03 feature-gate lane plus the high-ask-over-cheap side guard.",
        coverage_note,
        (
            f"The two-row relaxation frontier reaches {fmt_pct(best_pair_coverage)} nominal coverage, "
            "but remains a post-hoc diagnostic unless it gets its own frozen birth."
        ),
        (
            f"The three-row relaxation frontier reaches {fmt_pct(best_triple_coverage)} nominal coverage; "
            "use it as a source-quality stress test, not as a promotion candidate."
        ),
        "The best one-row additions remain source-fragile diagnostics; they are selected by relaxed predicates after seeing the frozen sample and do not clear source/live gates.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": freeze_ts,
        "live_net_cents": live_cents,
        "sources": {
            "feature_state": str(FEATURE_STATE),
            "side_guard": str(SIDE_GUARD),
        },
        "lanes": lanes,
        "interpretation": interpretation,
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Feature-Gate Guarded Coverage Repair Scan",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Live baseline: `{fmt_cents(report.get('live_net_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])

    for lane in report.get("lanes") or []:
        base = lane.get("base_summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Base guarded raw03: `{base.get('entries')}` entries, `{fmt_pct(base.get('coverage_pct'))}` coverage, `{fmt_cents(base.get('net_cents'))}`, W/L `{base.get('wins')}/{base.get('losses')}`, recon `{fmt_num(base.get('reconstructed_share'))}`, cushion `{base.get('full_loss_cushion')}`, blockers `{', '.join(base.get('blockers') or []) or 'none'}`.",
                "",
                "### Best One-Row Repairs",
                "",
                "| rank | repair | added market | source | net | miss reasons | coverage | total net | delta live | recon | cushion | blockers |",
                "|---:|---|---|---|---:|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, item in enumerate((lane.get("repair_candidates") or [])[:12], start=1):
            summary = item.get("summary") or {}
            row = item.get("added_row") or {}
            blockers = ", ".join(summary.get("blockers") or []) or "none"
            reasons = ",".join(row.get("base_miss_reasons") or []) or "none"
            lines.append(
                "| "
                f"{idx} | "
                f"`{item.get('relaxation')}` | "
                f"`{row.get('market')}` `{row.get('side')}` | "
                f"`{row.get('source')}` | "
                f"{fmt_cents(row.get('net_cents'))} | "
                f"{reasons} | "
                f"{fmt_pct(summary.get('coverage_pct'))} | "
                f"{fmt_cents(summary.get('net_cents'))} | "
                f"{fmt_cents(summary.get('delta_vs_live_cents'))} | "
                f"{fmt_num(summary.get('reconstructed_share'))} | "
                f"{summary.get('full_loss_cushion')} | "
                f"{blockers} |"
            )

        lines.extend(
            [
                "",
                "### Best Two-Row Repairs",
                "",
                "| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |",
                "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, item in enumerate((lane.get("pair_repair_candidates") or [])[:12], start=1):
            summary = item.get("summary") or {}
            rows = item.get("added_rows") or []
            blockers = ", ".join(summary.get("blockers") or []) or "none"
            markets = "; ".join(f"`{row.get('market')}` `{row.get('side')}`" for row in rows)
            sources = ", ".join(str(row.get("source")) for row in rows)
            lines.append(
                "| "
                f"{idx} | "
                f"{markets} | "
                f"{sources} | "
                f"{fmt_cents(item.get('added_net_cents'))} | "
                f"{fmt_pct(summary.get('coverage_pct'))} | "
                f"{fmt_cents(summary.get('net_cents'))} | "
                f"{fmt_cents(summary.get('delta_vs_live_cents'))} | "
                f"{fmt_num(summary.get('reconstructed_share'))} | "
                f"{summary.get('full_loss_cushion')} | "
                f"{blockers} |"
            )

        lines.extend(
            [
                "",
                "### Best Three-Row Repairs",
                "",
                "| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |",
                "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, item in enumerate((lane.get("triple_repair_candidates") or [])[:12], start=1):
            summary = item.get("summary") or {}
            rows = item.get("added_rows") or []
            blockers = ", ".join(summary.get("blockers") or []) or "none"
            markets = "; ".join(f"`{row.get('market')}` `{row.get('side')}`" for row in rows)
            sources = ", ".join(str(row.get("source")) for row in rows)
            lines.append(
                "| "
                f"{idx} | "
                f"{markets} | "
                f"{sources} | "
                f"{fmt_cents(item.get('added_net_cents'))} | "
                f"{fmt_pct(summary.get('coverage_pct'))} | "
                f"{fmt_cents(summary.get('net_cents'))} | "
                f"{fmt_cents(summary.get('delta_vs_live_cents'))} | "
                f"{fmt_num(summary.get('reconstructed_share'))} | "
                f"{summary.get('full_loss_cushion')} | "
                f"{blockers} |"
            )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
