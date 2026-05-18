"""Promotion-gap audit for the v28 boundary-clock feature-gate branch.

Research-only. This probe consolidates existing frozen/post-freeze evidence and
does not change live bot logic or candidate rules.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_promotion_gap_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_promotion_gap_audit_latest.md"

LINKED_SOURCE = OUT_DIR / "v28_feature_gate_linked_source_runway_latest.json"
SIZE_SHRINK = OUT_DIR / "v28_feature_gate_size_shrink_source_runway_latest.json"
SOURCE_FEASIBILITY = OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.json"
SOURCE_MECHANISM = OUT_DIR / "v28_feature_gate_source_blocker_mechanism_latest.json"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
FEATURE_GATE_CANDIDATE = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
TARGET_COVERAGES = (75.0, 80.0, 90.0)


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


def cents_from_live_summary(payload: dict[str, Any]) -> float:
    dollars = payload.get("net_pnl_total_dollars")
    try:
        return round(float(dollars) * 100.0, 6)
    except (TypeError, ValueError):
        return 0.0


def pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return ""


def cents(value: Any) -> str:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{c:.0f}c"


def choose_linked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = {
        "post_feature_freeze_entry_raw03_recross70_abs075",
        "post_feature_freeze_entry_raw05_recross60_abs085",
        "post_feature_freeze_entry_raw05_recross60_abs085_ask65",
    }
    return [row for row in rows if row.get("candidate") in wanted and row.get("lane") == "post_feature_freeze_entry"]


def clean_rows_needed_for_source(selected_entries: int, approved_entries: int, source_cap: float = 0.35) -> int:
    reconstructed = max(0, selected_entries - approved_entries)
    if selected_entries <= 0 or reconstructed / selected_entries <= source_cap:
        return 0
    return max(0, ceil((reconstructed / source_cap) - selected_entries))


def coverage_target_gaps(entries: int, denominator: int) -> dict[str, dict[str, Any]]:
    out = {}
    for target in TARGET_COVERAGES:
        required = ceil(denominator * target / 100.0)
        out[str(target)] = {
            "required_entries": required,
            "entries_needed": max(0, required - entries),
        }
    return out


def lane_summary_from_variant(lane: dict[str, Any], variant: dict[str, Any], live_net_cents: float) -> dict[str, Any]:
    summary = variant.get("candidate_summary") if isinstance(variant.get("candidate_summary"), dict) else {}
    counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
    source_net: dict[str, float] = {}
    source_wl: dict[str, dict[str, int]] = {}
    for row in variant.get("rows") or []:
        if not isinstance(row, dict):
            continue
        src = str(row.get("source") or "unknown")
        net_cents = float(row.get("net_cents") or 0.0)
        source_net[src] = source_net.get(src, 0.0) + net_cents
        bucket = source_wl.setdefault(src, {"wins": 0, "losses": 0})
        if net_cents > 0:
            bucket["wins"] += 1
        elif net_cents < 0:
            bucket["losses"] += 1
    entries = int(summary.get("entries") or 0)
    denominator = int(lane.get("future_denominator") or 0)
    approved = int(counts.get("approved_entry") or 0)
    return {
        "candidate": variant.get("candidate"),
        "entries": entries,
        "settled": summary.get("settled"),
        "denominator": denominator,
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "delta_vs_live_cents": (float(summary.get("net_cents") or 0.0) - live_net_cents),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "reconstructed_share": variant.get("reconstructed_share"),
        "source_counts": counts,
        "source_net_cents": source_net,
        "source_wl": source_wl,
        "full_loss_cushion": variant.get("full_loss_cushion_estimate"),
        "clean_rows_needed": clean_rows_needed_for_source(entries, approved),
        "coverage_target_gaps": coverage_target_gaps(entries, denominator),
        "blockers": variant.get("blockers", []),
    }


def current_feature_gate_rows(feature_gate: dict[str, Any], live_net_cents: float) -> list[dict[str, Any]]:
    rows = []
    for lane in feature_gate.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != "post_feature_freeze_entry":
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                rows.append(lane_summary_from_variant(lane, variant, live_net_cents))
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("net_cents") or -999999.0),
        )
    )
    return rows


def source_feasibility_by_coverage(lane: dict[str, Any]) -> dict[str, Any]:
    targets = lane.get("target_bounds") if isinstance(lane.get("target_bounds"), list) else []
    result: dict[str, Any] = {}
    for item in targets:
        target = item.get("target_coverage_pct")
        if target is None:
            continue
        result[str(target)] = item
    return result


def top_source_tags(lane: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    tags = lane.get("mechanism_attribution_source_only")
    if not isinstance(tags, dict):
        return []
    counts = tags.get("counts") if isinstance(tags.get("counts"), dict) else {}
    wins = tags.get("wins") if isinstance(tags.get("wins"), dict) else {}
    losses = tags.get("losses") if isinstance(tags.get("losses"), dict) else {}
    weighted = tags.get("weighted_net_cents") if isinstance(tags.get("weighted_net_cents"), dict) else {}
    rows = []
    for tag, count in counts.items():
        rows.append(
            {
                "tag": tag,
                "count": count,
                "weighted_net_cents": weighted.get(tag, 0.0),
                "wl": f"{wins.get(tag, 0)}/{losses.get(tag, 0)}",
            }
            )
    rows.sort(key=lambda item: (float(item.get("weighted_net_cents") or 0), -int(item.get("count") or 0)))
    return rows[:limit]


def feature_gate_interpretation(
    official_rows: list[dict[str, Any]],
    shrink_best: dict[str, Any],
    feasibility_lane: dict[str, Any],
) -> list[str]:
    notes = ["No feature-gate lane is live-ready."]
    broad = next(
        (row for row in official_rows if row.get("candidate") == "post_feature_freeze_entry_raw03_recross70_abs075"),
        official_rows[0] if official_rows else {},
    )
    blockers = set(str(item) for item in broad.get("blockers") or [])
    cleared: list[str] = []
    missing: list[str] = []
    for blocker, label in [
        ("settled_lt_30", "sample"),
        ("coverage_too_low", "coverage"),
        ("net_not_positive", "positive PnL"),
        ("reconstructed_share_gt_35pct", "source share"),
        ("full_loss_cushion_lt_3", "full-loss cushion"),
    ]:
        (missing if blocker in blockers else cleared).append(label)
    if float(broad.get("delta_vs_live_cents") or 0.0) < 0:
        missing.append("live-baseline delta")
    else:
        cleared.append("live-baseline delta")

    notes.append(
        "Official broad post-freeze lane clears "
        f"{', '.join(cleared) if cleared else 'no promotion gates'} but still misses "
        f"{', '.join(missing) if missing else 'no listed gates'}."
    )

    shrink_blockers = ", ".join(str(item) for item in shrink_best.get("blockers") or []) or "none"
    notes.append(
        "Size-shrink remains watch-only: "
        f"{cents(shrink_best.get('weighted_net_cents'))} weighted net, "
        f"{pct(shrink_best.get('coverage_pct'))} coverage, "
        f"{float(shrink_best.get('row_reconstructed_share') or 0.0):.2%} row reconstructed share, "
        f"{cents(shrink_best.get('delta_vs_live_cents'))} versus live, blockers {shrink_blockers}."
    )

    target_rows = source_feasibility_by_coverage(feasibility_lane)
    target75 = target_rows.get("75.0") or {}
    target80 = target_rows.get("80.0") or {}
    notes.append(
        "Source feasibility remains narrow: "
        f"75% target feasible={target75.get('source_gate_feasible')} at minimum reconstructed share "
        f"{float(target75.get('min_reconstructed_share_needed') or 0.0):.2%}; "
        f"80% target feasible={target80.get('source_gate_feasible')}."
    )
    return notes


def current_feature_gate_interpretation(
    official_rows: list[dict[str, Any]],
    shrink_best: dict[str, Any],
    feasibility_lane: dict[str, Any],
) -> list[str]:
    notes = ["No feature-gate lane is live-ready."]
    broad = next(
        (row for row in official_rows if row.get("candidate") == "post_feature_freeze_entry_raw03_recross70_abs075"),
        official_rows[0] if official_rows else {},
    )
    blockers = set(str(item) for item in broad.get("blockers") or [])
    cleared: list[str] = []
    missing: list[str] = []
    for blocker, label in [
        ("settled_lt_30", "sample"),
        ("coverage_too_low", "coverage"),
        ("net_not_positive", "positive PnL"),
        ("reconstructed_share_gt_35pct", "source share"),
        ("full_loss_cushion_lt_3", "full-loss cushion"),
    ]:
        (missing if blocker in blockers else cleared).append(label)
    if float(broad.get("delta_vs_live_cents") or 0.0) < 0:
        missing.append("live-baseline delta")
    else:
        cleared.append("live-baseline delta")

    target75 = (broad.get("coverage_target_gaps") or {}).get("75.0") or {}
    notes.append(
        "Current broad post-freeze lane clears "
        f"{', '.join(cleared) if cleared else 'no promotion gates'} but still misses "
        f"{', '.join(missing) if missing else 'no listed gates'}; "
        f"it needs {target75.get('entries_needed')} more selected markets for 75% coverage "
        f"and {broad.get('clean_rows_needed')} clean approved additions to satisfy the source-share cap if all else stayed constant."
    )

    shrink_blockers = ", ".join(str(item) for item in shrink_best.get("blockers") or []) or "none"
    notes.append(
        "Size-shrink remains watch-only: "
        f"{cents(shrink_best.get('weighted_net_cents'))} weighted net, "
        f"{pct(shrink_best.get('coverage_pct'))} coverage, "
        f"{float(shrink_best.get('row_reconstructed_share') or 0.0):.2%} row reconstructed share, "
        f"{cents(shrink_best.get('delta_vs_live_cents'))} versus live, blockers {shrink_blockers}."
    )

    target_rows = source_feasibility_by_coverage(feasibility_lane)
    target75_feas = target_rows.get("75.0") or {}
    target80_feas = target_rows.get("80.0") or {}
    notes.append(
        "Source feasibility artifact remains a bound, not a rule: "
        f"75% target feasible={target75_feas.get('source_gate_feasible')} at minimum reconstructed share "
        f"{float(target75_feas.get('min_reconstructed_share_needed') or 0.0):.2%}; "
        f"80% target feasible={target80_feas.get('source_gate_feasible')}."
    )
    return notes


def lane_summary(row: dict[str, Any], live_net_cents: float) -> dict[str, Any]:
    summary = row.get("linked_summary") if isinstance(row.get("linked_summary"), dict) else {}
    return {
        "candidate": row.get("candidate"),
        "entries": summary.get("entries"),
        "settled": summary.get("settled"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "delta_vs_live_cents": (float(summary.get("net_cents") or 0.0) - live_net_cents),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion_estimate"),
        "clean_rows_needed": row.get("approved_future_rows_needed_for_source_gate"),
        "blockers": row.get("linked_blockers", []),
        "approved_net_cents": (row.get("approved_summary") or {}).get("net_cents"),
        "rejected_net_cents": (row.get("rejected_or_reconstructed_summary") or {}).get("net_cents"),
    }


def build_report() -> dict[str, Any]:
    linked = load_json(LINKED_SOURCE)
    shrink = load_json(SIZE_SHRINK)
    feasibility = load_json(SOURCE_FEASIBILITY)
    mechanism = load_json(SOURCE_MECHANISM)
    live = load_json(LIVE_SUMMARY)
    feature_gate = load_json(FEATURE_GATE_CANDIDATE)
    live_net_cents = cents_from_live_summary(live)

    official_rows = current_feature_gate_rows(feature_gate, live_net_cents)
    if not official_rows:
        linked_rows = choose_linked_rows(linked.get("rows", []))
        official_rows = [lane_summary(row, live_net_cents) for row in linked_rows]

    shrink_lanes = [
        lane
        for lane in shrink.get("lanes", [])
        if isinstance(lane, dict) and lane.get("lane") == "post_feature_freeze_entry"
    ]
    shrink_best = shrink_lanes[0] if shrink_lanes else {}

    feasibility_lane = next(
        (lane for lane in feasibility.get("lanes", []) if lane.get("lane") == "post_feature_freeze_entry"),
        {},
    )
    mechanism_lane = next(
        (lane for lane in mechanism.get("lanes", []) if lane.get("lane") == "post_feature_freeze_entry"),
        {},
    )

    blockers = current_feature_gate_interpretation(official_rows, shrink_best, feasibility_lane)

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "linked_source": str(LINKED_SOURCE),
            "size_shrink": str(SIZE_SHRINK),
            "source_feasibility": str(SOURCE_FEASIBILITY),
            "source_mechanism": str(SOURCE_MECHANISM),
            "feature_gate_candidate": str(FEATURE_GATE_CANDIDATE),
            "live_summary": str(LIVE_SUMMARY),
        },
        "live_net_cents": live_net_cents,
        "feature_gate_candidate_generated_at_utc": feature_gate.get("generated_at_utc"),
        "official_feature_gate_rows": official_rows,
        "size_shrink_best": {
            "policy": shrink_best.get("policy"),
            "settled": shrink_best.get("settled"),
            "coverage_pct": shrink_best.get("coverage_pct"),
            "weighted_net_cents": shrink_best.get("weighted_net_cents"),
            "delta_vs_live_cents": shrink_best.get("delta_vs_live_cents"),
            "row_reconstructed_share": shrink_best.get("row_reconstructed_share"),
            "clean_rows_needed_for_source": shrink_best.get("clean_rows_needed_for_source"),
            "cushion_surplus_cents_after_3_full_losses": shrink_best.get("cushion_surplus_cents_after_3_full_losses"),
            "full_weight_wins_to_live_tie": shrink_best.get("full_weight_wins_to_live_tie"),
            "blockers": shrink_best.get("blockers", []),
        },
        "source_feasibility": {
            "future_denominator": feasibility_lane.get("future_denominator"),
            "approved_markets_available": feasibility_lane.get("approved_markets_available"),
            "target_rows": source_feasibility_by_coverage(feasibility_lane),
        },
        "source_mechanism": {
            "selected_weighted_net_cents": (mechanism_lane.get("selected_summary") or {}).get("weighted_net_cents"),
            "row_reconstructed_share": (mechanism_lane.get("selected_summary") or {}).get("row_reconstructed_share"),
            "source_only_weighted_net_cents": (mechanism_lane.get("source_selected_summary") or {}).get("weighted_net_cents"),
            "source_only_rows": (mechanism_lane.get("source_selected_summary") or {}).get("entries"),
            "top_negative_tags": top_source_tags(mechanism_lane),
        },
        "promotion_gap": blockers,
        "conclusion": "watch_only_not_promotable",
    }


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# v28 Feature-Gate Promotion Gap Audit",
        "",
        "Research-only consolidation. No live bot changes, no orders, no new candidate rule.",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        f"- Refreshed live-only baseline: `{cents(payload['live_net_cents'])}`",
        f"- Conclusion: `{payload['conclusion']}`",
        "",
        "## Official Post-Freeze Lanes",
        "",
        "| candidate | entries | settled | coverage | W/L | net | delta vs live | recon share | cushion | source net | target gaps | clean rows needed | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|",
    ]
    for row in payload["official_feature_gate_rows"]:
        lines.append(
            "| {candidate} | {entries} | {settled} | {coverage} | {wl} | {net} | {delta} | {recon:.2%} | {cushion} | {source_net} | {target_gaps} | {clean} | {blockers} |".format(
                candidate=row.get("candidate"),
                entries=row.get("entries"),
                settled=row.get("settled"),
                coverage=pct(row.get("coverage_pct")),
                wl=f"{row.get('wins')}/{row.get('losses')}",
                net=cents(row.get("net_cents")),
                delta=cents(row.get("delta_vs_live_cents")),
                recon=float(row.get("reconstructed_share") or 0.0),
                cushion=row.get("full_loss_cushion"),
                source_net=", ".join(
                    f"{src}:{cents(value)}" for src, value in sorted((row.get("source_net_cents") or {}).items())
                ),
                target_gaps=", ".join(
                    f"{target}%:+{gap.get('entries_needed')}"
                    for target, gap in sorted((row.get("coverage_target_gaps") or {}).items(), key=lambda item: float(item[0]))
                ),
                clean=row.get("clean_rows_needed"),
                blockers=", ".join(row.get("blockers") or []),
            )
        )

    shrink = payload["size_shrink_best"]
    lines.extend(
        [
            "",
            "## Size-Shrink Runway",
            "",
            f"- Policy: `{shrink.get('policy')}`",
            f"- Settled / coverage: `{shrink.get('settled')}` / `{pct(shrink.get('coverage_pct'))}`",
            f"- Weighted net: `{cents(shrink.get('weighted_net_cents'))}`",
            f"- Delta versus live: `{cents(shrink.get('delta_vs_live_cents'))}`",
            f"- Row reconstructed share: `{float(shrink.get('row_reconstructed_share') or 0.0):.2%}`",
            f"- Clean approved rows needed for source: `{shrink.get('clean_rows_needed_for_source')}`",
            f"- Cushion surplus after three full losses: `{cents(shrink.get('cushion_surplus_cents_after_3_full_losses'))}`",
            f"- Full-weight wins needed to tie live: `{shrink.get('full_weight_wins_to_live_tie')}`",
            f"- Blockers: `{', '.join(shrink.get('blockers') or [])}`",
            "",
            "## Source Feasibility",
            "",
        ]
    )
    feasibility = payload["source_feasibility"]
    lines.append(f"- Future denominator: `{feasibility.get('future_denominator')}`")
    lines.append(f"- Approved markets available: `{feasibility.get('approved_markets_available')}`")
    for target, row in sorted(feasibility.get("target_rows", {}).items(), key=lambda item: float(item[0])):
        lines.append(
            "- Target {target}%: required `{required}`, min reconstructed share `{share:.2%}`, feasible under source gate `{feasible}`.".format(
                target=target,
                required=row.get("required_markets"),
                share=float(row.get("min_reconstructed_share_needed") or 0.0),
                feasible=row.get("source_gate_feasible"),
            )
        )

    mechanism = payload["source_mechanism"]
    lines.extend(
        [
            "",
            "## Source Mechanism",
            "",
            f"- Source-only weighted net: `{cents(mechanism.get('source_only_weighted_net_cents'))}` on `{mechanism.get('source_only_rows')}` rows.",
            "",
            "| tag | count | W/L | weighted net |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in mechanism.get("top_negative_tags") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('count')} | {row.get('wl')} | {cents(row.get('weighted_net_cents'))} |"
        )

    lines.extend(
        [
            "",
            "## Promotion Gap",
            "",
        ]
    )
    for item in payload["promotion_gap"]:
        lines.append(f"- {item}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_report()
    write_report(payload)
    print(OUT_MD)


if __name__ == "__main__":
    main()
