"""Coverage repair for the feature-gate source-quality proxy.

Research-only; no live bot changes or orders.

The source-quality proxy scan found that requiring seconds_to_close >= 240
improves row-source quality and keeps a three-full-loss cushion, but under-
covers. This probe keeps that observable late-core and adds the minimum number
of observable filler markets needed to restore target coverage.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import as_float, load_or_create_state, market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, raw_edge, rule_name
from probe_v28_feature_gate_coverage_size_shrink import ANCHOR_RULE, REPAIR_RULE, repair_weight, row_key, summarize_policy
from probe_v28_feature_gate_source_quality_proxy import STATE_JSON as PROXY_STATE_JSON, load_json as proxy_load_json, load_or_create_proxy_state
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_proxy_coverage_repair_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_proxy_coverage_repair_latest.md"

POLICY = "repair_low_absd_quarter_else_half"
TARGET_COVERAGE_MIN = 75.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def p_side(row: dict[str, Any]) -> float:
    return fnum(row.get("p_side"))


def ask(row: dict[str, Any]) -> float:
    return fnum(row.get("ask_prob"))


def seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("seconds_to_close"))


def depth(row: dict[str, Any]) -> float:
    return fnum(row.get("eligible_depth"))


def raw_score(row: dict[str, Any]) -> float:
    return fnum(raw_edge(row), -999.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def selected_by_market(
    rows: list[dict[str, Any]],
    ranker: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=ranker) for items in grouped.values()]


def rank_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (raw_score(row), abs_d(row), -recross(row), str(row.get("ts_wall") or ""))


def rank_p_side(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (p_side(row), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


def rank_ask(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (ask(row), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


def rank_absd(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (abs_d(row), raw_score(row), -recross(row), str(row.get("ts_wall") or ""))


def rank_low_recross(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (-recross(row), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


def rank_source_proxy(row: dict[str, Any]) -> tuple[float, float, float, str]:
    # Diagnostic contrast: approved rows were higher p_side/ask/abs_d and lower recross.
    score = 0.40 * p_side(row) + 0.20 * ask(row) + 0.08 * abs_d(row) - 0.20 * recross(row) + 0.01 * math.log1p(depth(row))
    return (score, raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


FILLER_RANKERS: dict[str, Callable[[dict[str, Any]], tuple[Any, ...]]] = {
    "raw_edge": rank_raw,
    "p_side": rank_p_side,
    "ask": rank_ask,
    "absd": rank_absd,
    "low_recross": rank_low_recross,
    "source_proxy_score": rank_source_proxy,
}


def required_entries(denominator: int) -> int:
    return int(math.ceil((TARGET_COVERAGE_MIN / 100.0) * denominator))


def row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]], role: str) -> dict[str, Any]:
    return {
        "role": role,
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weight": repair_weight(POLICY, row, anchor_keys),
        "raw_edge": raw_edge(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "side_won": row.get("side_won"),
    }


def build_candidate(
    base_pool: list[dict[str, Any]],
    core_rows: list[dict[str, Any]],
    denominator: int,
    ranker: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    core_markets = {market(row) for row in core_rows}
    needed = max(0, required_entries(denominator) - len(core_rows))
    filler_pool = [row for row in base_pool if market(row) not in core_markets]
    filler_by_market = selected_by_market(filler_pool, ranker)
    filler_by_market.sort(key=ranker, reverse=True)
    fillers = filler_by_market[:needed]
    return core_rows + fillers, fillers


def evaluate_variant(
    lane: str,
    label: str,
    candidate: list[dict[str, Any]],
    fillers: list[dict[str, Any]],
    denominator: int,
    anchor_keys: set[tuple[str, str]],
) -> dict[str, Any]:
    summary = summarize_policy(lane, POLICY, candidate, denominator, anchor_keys)
    summary.update({
        "candidate_id": label,
        "core_entries": len(candidate) - len(fillers),
        "filler_entries": len(fillers),
        "filler_source_counts": source_counts(fillers),
        "source_counts": source_counts(candidate),
        "selected_rows": [
            row_view(row, anchor_keys, "filler" if row in fillers else "core")
            for row in candidate
        ],
    })
    return summary


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any], strict_forward: bool) -> dict[str, Any]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_rows = selected_by_market([row for row in rows if passes_rule(row, ANCHOR_RULE)], rank_raw)
    anchor_keys = {row_key(row) for row in anchor_rows}
    base_pool = [row for row in rows if passes_rule(row, REPAIR_RULE)]
    core_pool = [row for row in base_pool if seconds_to_close(row) >= 240.0]
    core_rows = selected_by_market(core_pool, rank_raw)
    variants = []
    for ranker_name, ranker in FILLER_RANKERS.items():
        candidate, fillers = build_candidate(base_pool, core_rows, denominator, ranker)
        variants.append(evaluate_variant(
            label,
            f"stc240_core_plus_{ranker_name}_fillers",
            candidate,
            fillers,
            denominator,
            anchor_keys,
        ))
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_net_cents") or -999999.0),
            float(row.get("row_reconstructed_share") or 1.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "strict_forward": strict_forward,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "repair_rule": rule_name(REPAIR_RULE),
        "core_rule": "seconds_to_close>=240 plus repair rule",
        "anchor_entries": len(anchor_rows),
        "base_pool_rows": len(base_pool),
        "core_entries": len(core_rows),
        "required_entries_for_75pct": required_entries(denominator),
        "top_variants": variants,
        "gate_clear_variants": [row for row in variants if row.get("live_ready")][:20],
    }


def build_report() -> dict[str, Any]:
    feature_state = load_or_create_state()
    proxy_state = load_or_create_proxy_state()
    feature_freeze_ts = str(feature_state["freeze_ts_utc"])
    proxy_freeze_ts = str(proxy_state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_freeze_ts,
        "source_proxy_freeze_ts_utc": proxy_freeze_ts,
        "purpose": "Repair coverage for the cleaner seconds-to-close source proxy using observable filler ranking.",
        "lanes": [
            evaluate_lane("diagnostic_feature_freeze_entry", feature_freeze_ts, entry_surfaces, False),
            evaluate_lane("diagnostic_feature_freeze_bridge", feature_freeze_ts, bridge_surfaces, False),
            evaluate_lane("post_source_proxy_birth_entry", proxy_freeze_ts, entry_surfaces, True),
            evaluate_lane("post_source_proxy_birth_bridge", proxy_freeze_ts, bridge_surfaces, True),
        ],
        "proxy_state": proxy_load_json(PROXY_STATE_JSON),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "The core and filler rankings use observable fields only; source labels are audit-only.",
    ]
    for lane in report.get("lanes") or []:
        clears = lane.get("gate_clear_variants") or []
        best = (lane.get("top_variants") or [{}])[0]
        if clears:
            first = clears[0]
            notes.append(
                f"{lane.get('lane')}: {len(clears)} variant(s) clear current gates; best {first.get('candidate_id')} has "
                f"{first.get('entries')}/{lane.get('future_denominator')} entries, W/L {first.get('wins')}/{first.get('losses')}, "
                f"weighted net {first.get('weighted_net_cents')}c, row recon {first.get('row_reconstructed_share')}."
            )
        else:
            notes.append(
                f"{lane.get('lane')}: no variant clears all gates. Best {best.get('candidate_id')} has "
                f"{best.get('entries')}/{lane.get('future_denominator')} entries, W/L {best.get('wins')}/{best.get('losses')}, "
                f"weighted net {best.get('weighted_net_cents')}c, row recon {best.get('row_reconstructed_share')}, "
                f"blockers {best.get('blockers')}."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source-Proxy Coverage Repair",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Source-proxy freeze UTC: `{report.get('source_proxy_freeze_ts_utc')}`",
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
            f"- Freeze UTC: `{lane.get('freeze_ts_utc')}`",
            f"- Strict forward: `{lane.get('strict_forward')}`",
            f"- Core/required entries: `{lane.get('core_entries')}/{lane.get('required_entries_for_75pct')}`",
            "",
            "| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | filler source | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for row in lane.get("top_variants") or []:
            lines.append(
                f"| {row.get('candidate_id')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))}% | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('exposure_reconstructed_share'))} | {row.get('full_loss_cushion')} | "
                f"{row.get('filler_source_counts')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
