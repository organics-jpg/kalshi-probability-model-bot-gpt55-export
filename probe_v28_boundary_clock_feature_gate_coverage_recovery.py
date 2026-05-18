"""Post-freeze coverage recovery audit for the boundary-clock feature gate.

Research-only; no live bot changes or orders.

This compares the current clean strict ask-floor rule against broader
observable rules market-by-market. The purpose is to classify whether missing
coverage is a recoverable physical signal or mostly source/fragility risk.
Rules tested here are analysis surfaces, not promotion candidates.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    blockers,
    load_or_create_state,
    market,
    net,
    passes,
    reconstructed_share,
    source,
    source_counts,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_recovery_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_recovery_latest.md"

STRICT_RULE = "raw05_recross60_abs085_ask65"
TARGET_COVERAGE = 0.75
MAX_RECONSTRUCTED_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def select_by_market(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_market = market(row)
        if not row_market or not passes(row, rule):
            continue
        current = selected.get(row_market)
        if current is None or (raw_edge(row) or -999.0) > (raw_edge(current) or -999.0):
            selected[row_market] = row
    return selected


def row_digest(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": as_float(row.get("recross_hazard_score")),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
    }


def win_loss(rows: list[dict[str, Any]]) -> dict[str, int]:
    wins = sum(1 for row in rows if net(row) > 0)
    losses = sum(1 for row in rows if net(row) < 0)
    flats = sum(1 for row in rows if net(row) == 0)
    return {"wins": wins, "losses": losses, "flats": flats}


def compare_rule(
    strict_selected: dict[str, dict[str, Any]],
    candidate_selected: dict[str, dict[str, Any]],
    denominator: int,
) -> dict[str, Any]:
    strict_markets = set(strict_selected)
    candidate_markets = set(candidate_selected)
    added_markets = sorted(candidate_markets - strict_markets)
    common_markets = sorted(candidate_markets & strict_markets)

    added_rows = [candidate_selected[row_market] for row_market in added_markets]
    replacement_rows = []
    replacement_delta_cents = 0.0
    replacement_source_pairs: Counter[str] = Counter()
    for row_market in common_markets:
        strict_row = strict_selected[row_market]
        candidate_row = candidate_selected[row_market]
        strict_digest = row_digest(strict_row)
        candidate_digest = row_digest(candidate_row)
        if strict_digest == candidate_digest:
            continue
        delta = net(candidate_row) - net(strict_row)
        replacement_delta_cents += delta
        replacement_source_pairs[f"{source(strict_row)}->{source(candidate_row)}"] += 1
        replacement_rows.append(
            {
                "market": row_market,
                "strict": strict_digest,
                "candidate": candidate_digest,
                "delta_cents": delta,
            }
        )

    added_net_cents = sum(net(row) for row in added_rows)
    total_delta_cents = added_net_cents + replacement_delta_cents
    target_rows = math.ceil(float(denominator or 0) * TARGET_COVERAGE)
    rows_needed_for_target_coverage = max(0, target_rows - len(candidate_selected))
    clean_rows_needed_for_source = 0
    approved = int(source_counts(list(candidate_selected.values())).get("approved_entry") or 0)
    total = len(candidate_selected)
    while total > 0 and (total - approved) / total > MAX_RECONSTRUCTED_SHARE:
        clean_rows_needed_for_source += 1
        approved += 1
        total += 1

    return {
        "added_markets": len(added_markets),
        "added_net_cents": added_net_cents,
        "added_wl": win_loss(added_rows),
        "added_source_counts": source_counts(added_rows),
        "added_rows": [row_digest(row) for row in added_rows],
        "replacement_count": len(replacement_rows),
        "replacement_delta_cents": replacement_delta_cents,
        "replacement_source_pairs": dict(replacement_source_pairs),
        "replacement_examples": replacement_rows[:10],
        "total_delta_cents_vs_strict": total_delta_cents,
        "rows_needed_for_75pct_coverage": rows_needed_for_target_coverage,
        "clean_rows_needed_for_source_gate": clean_rows_needed_for_source,
    }


def evaluate_lane(label: str, surfaces_fn: Any, freeze_ts: str) -> dict[str, Any]:
    all_rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    strict_selected = select_by_market(all_rows, RULES[STRICT_RULE])
    strict_rows = list(strict_selected.values())
    strict_summary = summarize(strict_rows, denominator)
    strict_counts = source_counts(strict_rows)
    strict_share = reconstructed_share(strict_counts)

    variants = []
    for rule_name, rule in RULES.items():
        candidate_selected = select_by_market(all_rows, rule)
        rows = list(candidate_selected.values())
        summary = summarize(rows, denominator)
        counts = source_counts(rows)
        share = reconstructed_share(counts)
        variants.append(
            {
                "rule": rule_name,
                "summary": summary,
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "blockers": blockers(summary, share),
                "strict_comparison": compare_rule(strict_selected, candidate_selected, denominator),
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -(float((row.get("summary") or {}).get("coverage_pct") or 0.0)),
            -(float((row.get("summary") or {}).get("net_cents") or -999999.0)),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "strict_rule": STRICT_RULE,
        "strict_summary": strict_summary,
        "strict_source_counts": strict_counts,
        "strict_reconstructed_share": strict_share,
        "strict_blockers": blockers(strict_summary, strict_share),
        "variants": variants,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a post-freeze mechanism audit, not a promotion candidate.",
        "The strict ask-floor rule is clean but under-covered; broader rules are judged by source mix, added/replaced row PnL, and runway to 75% coverage.",
    ]
    for lane in lanes:
        strict = lane.get("strict_summary") or {}
        notes.append(
            f"{lane.get('lane')} strict {lane.get('strict_rule')} has {strict.get('settled')} settled, "
            f"coverage {strict.get('coverage_pct')}%, net {strict.get('net_cents')}c, "
            f"recon share {lane.get('strict_reconstructed_share')}, blockers {lane.get('strict_blockers')}."
        )
        variants = lane.get("variants") or []
        best_broad = next((row for row in variants if row.get("rule") != STRICT_RULE), {})
        if best_broad:
            summary = best_broad.get("summary") or {}
            comp = best_broad.get("strict_comparison") or {}
            notes.append(
                f"{lane.get('lane')} best broader rule {best_broad.get('rule')} has coverage "
                f"{summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, recon share "
                f"{best_broad.get('reconstructed_share')}, adds {comp.get('added_markets')} markets for "
                f"{comp.get('added_net_cents')}c and needs {comp.get('rows_needed_for_75pct_coverage')} "
                "more selected rows for 75% coverage."
            )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", entry_surfaces, freeze_ts),
        evaluate_lane("post_feature_freeze_bridge", bridge_surfaces, freeze_ts),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "target_coverage": TARGET_COVERAGE,
        "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Boundary-Clock Feature-Gate Coverage Recovery",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")

    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend(
            [
                "| rule | selected/den | settled | W/L | coverage | net c | recon share | cushion | delta vs strict | added markets/net | rows to 75% | clean rows to source | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("variants") or []:
            summary = row.get("summary") or {}
            comp = row.get("strict_comparison") or {}
            lines.append(
                f"| {row.get('rule')} | {summary.get('entries')}/{lane.get('future_denominator')} | "
                f"{summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion_estimate')} | "
                f"{fmt(comp.get('total_delta_cents_vs_strict'))} | "
                f"{comp.get('added_markets')}/{fmt(comp.get('added_net_cents'))} | "
                f"{comp.get('rows_needed_for_75pct_coverage')} | "
                f"{comp.get('clean_rows_needed_for_source_gate')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
        lines.extend(["", "### Added Rows Versus Strict Ask-Floor", ""])
        lines.extend(
            [
                "| rule | market | source | side | side won | net c | edge | recross | abs d | ask |",
                "|---|---|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("variants") or []:
            if row.get("rule") == STRICT_RULE:
                continue
            for added in (row.get("strict_comparison") or {}).get("added_rows") or []:
                lines.append(
                    f"| {row.get('rule')} | {added.get('market')} | {added.get('source')} | "
                    f"{added.get('side')} | {added.get('side_won')} | {fmt(added.get('net_cents'))} | "
                    f"{fmt(added.get('raw_edge'))} | {fmt(added.get('recross_hazard_score'))} | "
                    f"{fmt(added.get('abs_d_sigma'))} | {fmt(added.get('ask_prob'))} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
