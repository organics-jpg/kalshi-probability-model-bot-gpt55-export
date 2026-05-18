"""Observable source-confirmation replacement audit for size-shrink lane.

Research-only; no live bot changes or orders.

The strict feature-gate size-shrink lane is just above the row-source gate.
This probe tests a source-label-free replacement idea: when the selected row is
weak boundary/mid-ask/moderate-p-side but the same market/side later shows a
stronger observable confirmation row, replace the weak row with the stronger
confirmation row.

Important caveat: exit artifacts are keyed by market/side, not by candidate
entry row. This probe therefore reports entry-hold evidence and a conservative
exit-adjusted diagnostic estimate, rather than promotion evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state, market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    repair_weight,
    row_key,
    selected,
)
from probe_v28_feature_gate_size_shrink_delayed_recheck_rescue import (
    BOOK_GAP_JSON,
    LIVE_SUMMARY_JSON,
    REDUCE_JSON,
    evaluate_lane as evaluate_rescue_lane,
    fnum,
    grouped_exit_rows,
    load_json,
    read_heartbeats,
)
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_confirmation_replacement_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_confirmation_replacement_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_source_confirmation_replacement_state.json"

POLICY = "repair_low_absd_quarter_else_half"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_replacement_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing:
        return existing
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_source_confirmation_replacement",
        "parent_policy": POLICY,
        "note": "Freeze created after diagnostic source-confirmation replacement audit; post-birth rows are the only strict-forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def val(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key) if row.get(key) is not None else default)
    except (TypeError, ValueError):
        return default


def weak_selected(row: dict[str, Any]) -> bool:
    return val(row, "abs_d_sigma") < 0.65 and val(row, "ask_prob") < 0.65 and val(row, "p_side") < 0.85


def strong_confirmation(row: dict[str, Any]) -> bool:
    return (
        val(row, "abs_d_sigma") >= 0.95
        and val(row, "ask_prob") >= 0.75
        and val(row, "p_side") >= 0.88
        and val(row, "recross_hazard_score", 1.0) <= 0.35
    )


def confirmation_rank(row: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        val(row, "p_side"),
        val(row, "abs_d_sigma"),
        val(row, "ask_prob"),
        -val(row, "recross_hazard_score", 1.0),
        str(row.get("ts_wall") or ""),
    )


def row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    weight = repair_weight(POLICY, row, anchor_keys)
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weight": weight,
        "weighted_net_cents": weight * net(row),
        "raw_edge": row.get("raw_edge"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "reason": row.get("reason"),
        "ts_wall": row.get("ts_wall"),
    }


def summarize_entries(entries: list[dict[str, Any]], denominator: int, anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    counts = Counter(source(row) for row in entries)
    weighted = sum(repair_weight(POLICY, row, anchor_keys) * net(row) for row in entries)
    return {
        "entries": len(entries),
        "settled": len(entries),
        "wins": sum(1 for row in entries if repair_weight(POLICY, row, anchor_keys) * net(row) > 0),
        "losses": sum(1 for row in entries if repair_weight(POLICY, row, anchor_keys) * net(row) < 0),
        "coverage_pct": 100.0 * len(entries) / denominator if denominator else 0.0,
        "source_counts": dict(counts),
        "reconstructed_share": (len(entries) - int(counts.get("approved_entry") or 0)) / len(entries) if entries else None,
        "weighted_entry_hold_net_cents": weighted,
        "full_loss_cushion": int(max(0.0, weighted) // 100.0),
    }


def build_entries(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[tuple[str, str]], int, list[dict[str, Any]]]:
    rows, _, denominator_raw = entry_surfaces(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_rows = selected(rows, ANCHOR_RULE)
    base_rows = selected(rows, REPAIR_RULE)
    anchor_keys = {row_key(row) for row in anchor_rows}
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row) and passes_rule(row, REPAIR_RULE):
            by_market[market(row)].append(row)
    replacements = []
    replaced_rows = []
    for row in base_rows:
        alternatives = [
            alt for alt in by_market.get(market(row), [])
            if row_key(alt) == row_key(row) and strong_confirmation(alt)
        ]
        if weak_selected(row) and alternatives:
            replacement = max(alternatives, key=confirmation_rank)
            replacements.append(replacement)
            replaced_rows.append({
                "old": row_view(row, anchor_keys),
                "new": row_view(replacement, anchor_keys),
                "weighted_delta_cents": (
                    repair_weight(POLICY, replacement, anchor_keys) * net(replacement)
                    - repair_weight(POLICY, row, anchor_keys) * net(row)
                ),
            })
        else:
            replacements.append(row)
    return base_rows, replacements, anchor_keys, denominator, replaced_rows


def build_lane(label: str, strict_forward: bool, freeze_ts: str) -> dict[str, Any]:
    base_entries, replacement_entries, anchor_keys, denominator, replaced_rows = build_entries(freeze_ts)
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    live_cents = 100.0 * float(fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars")) or 0.0)
    base_entry = summarize_entries(base_entries, denominator, anchor_keys)
    replacement_entry = summarize_entries(replacement_entries, denominator, anchor_keys)
    base_rescue = evaluate_rescue_lane(
        label,
        strict_forward,
        base_entries,
        anchor_keys,
        denominator,
        book_rows,
        reduce_rows,
        heartbeats,
        live_cents,
    )
    replacement_rescue = evaluate_rescue_lane(
        label,
        strict_forward,
        replacement_entries,
        anchor_keys,
        denominator,
        book_rows,
        reduce_rows,
        heartbeats,
        live_cents,
    )
    entry_delta = replacement_entry["weighted_entry_hold_net_cents"] - base_entry["weighted_entry_hold_net_cents"]
    adjusted_variants = []
    for item in replacement_rescue.get("variants") or []:
        adjusted = dict(item)
        adjusted["candidate_net_cents_unadjusted_market_side_exit_basis"] = item.get("candidate_net_cents")
        adjusted["entry_hold_delta_vs_base_cents"] = entry_delta
        adjusted["candidate_net_cents_conservative_entry_adjusted"] = (float(item.get("candidate_net_cents") or 0.0) + entry_delta)
        adjusted["delta_vs_live_cents_conservative_entry_adjusted"] = adjusted["candidate_net_cents_conservative_entry_adjusted"] - live_cents
        adjusted["blockers"] = list(adjusted.get("blockers") or []) + [
            "exit_artifact_market_side_basis_caveat",
            "diagnostic_replacement_audit" if not strict_forward else "post_birth_replacement_watch",
        ]
        adjusted_variants.append(adjusted)
    adjusted_variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("candidate_net_cents_conservative_entry_adjusted") or -999999),
        )
    )
    return {
        "lane": label,
        "strict_forward": strict_forward,
        "freeze_ts_utc": freeze_ts,
        "denominator": denominator,
        "base_entry_summary": base_entry,
        "replacement_entry_summary": replacement_entry,
        "replacements": replaced_rows,
        "base_rescue_best": base_rescue.get("best"),
        "replacement_rescue_variants": adjusted_variants,
        "replacement_rescue_best": adjusted_variants[0] if adjusted_variants else {},
    }


def build_report() -> dict[str, Any]:
    feature_state = load_or_create_state()
    replacement_state = load_or_create_replacement_state()
    diagnostic = build_lane("diagnostic_prefreeze_context", False, str(feature_state["freeze_ts_utc"]))
    post = build_lane("post_confirmation_replacement_birth", True, str(replacement_state["freeze_ts_utc"]))
    best = diagnostic.get("replacement_rescue_best") or {}
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_state.get("freeze_ts_utc"),
        "state": replacement_state,
        "rule": {
            "replace_when": "selected row has abs_d<0.65, ask<0.65, p_side<0.85",
            "replacement_required": "same market/side row with abs_d>=0.95, ask>=0.75, p_side>=0.88, recross<=0.35",
            "rank": "highest p_side, abs_d, ask, then lower recross",
        },
        "lanes": [diagnostic, post],
        "interpretation": [
            "Research-only source-confirmation replacement audit; no live bot changes or orders.",
            "The rule is observable, but the exit overlay estimate has a market/side entry-price basis caveat.",
            (
                f"Diagnostic best adjusted net {best.get('candidate_net_cents_conservative_entry_adjusted')}c, "
                f"row source share {(diagnostic.get('replacement_entry_summary') or {}).get('reconstructed_share')}, "
                f"replacements {len(diagnostic.get('replacements') or [])}, blockers {best.get('blockers')}."
            ) if best else "No diagnostic replacement variant scored.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source Confirmation Replacement",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Replacement freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(["", "## Rule", ""])
    for key, value in (report.get("rule") or {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | strict | denominator | replacements | base source | repl source | base entry net | repl entry net | best adjusted rescue net | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        base = lane.get("base_entry_summary") or {}
        repl = lane.get("replacement_entry_summary") or {}
        best = lane.get("replacement_rescue_best") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {lane.get('strict_forward')} | {lane.get('denominator')} | "
            f"{len(lane.get('replacements') or [])} | {fmt(base.get('reconstructed_share'))} | "
            f"{fmt(repl.get('reconstructed_share'))} | {fmt(base.get('weighted_entry_hold_net_cents'))} | "
            f"{fmt(repl.get('weighted_entry_hold_net_cents'))} | "
            f"{fmt(best.get('candidate_net_cents_conservative_entry_adjusted'))} | "
            f"{', '.join(best.get('blockers') or [])} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')} Replacements",
            "",
            "| market | old source | old net | old abs_d | old ask | old p_side | new source | new net | new abs_d | new ask | new p_side | weighted delta |",
            "|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
        ])
        for item in lane.get("replacements") or []:
            old = item.get("old") or {}
            new = item.get("new") or {}
            lines.append(
                f"| {old.get('market')} | {old.get('source')} | {fmt(old.get('net_cents'))} | "
                f"{fmt(old.get('abs_d_sigma'))} | {fmt(old.get('ask_prob'))} | {fmt(old.get('p_side'))} | "
                f"{new.get('source')} | {fmt(new.get('net_cents'))} | {fmt(new.get('abs_d_sigma'))} | "
                f"{fmt(new.get('ask_prob'))} | {fmt(new.get('p_side'))} | {fmt(item.get('weighted_delta_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
