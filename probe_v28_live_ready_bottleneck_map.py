"""Live-readiness bottleneck map for v28 candidate lanes.

Research-only. This probe reads existing scorecards and summarizes what is
actually preventing the best current candidates from controlled live-test
status. It does not touch live bot logic, state, processes, or orders.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
GATE_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
NEAR_GATE_JSON = OUT_DIR / "v28_near_gate_runway_latest.json"
OWN_FREEZE_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json"
SOURCE_FEASIBILITY_JSON = OUT_DIR / "v28_feature_gate_source_feasibility_bound_latest.json"
SOURCE_SLICE_JSON = OUT_DIR / "v28_feature_gate_size_shrink_source_slice_latest.json"

OUT_JSON = OUT_DIR / "v28_live_ready_bottleneck_map_latest.json"
OUT_MD = OUT_DIR / "v28_live_ready_bottleneck_map_latest.md"

MIN_SETTLED = 30
MIN_CUSHION = 3
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_SOURCE_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def inum(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def net(row: dict[str, Any]) -> float:
    for key in ("net_cents_after_entry_fee", "weighted_net_cents", "net_cents", "candidate_net_cents"):
        if key in row:
            return fnum(row.get(key))
    return 0.0


def source_share(row: dict[str, Any]) -> float | None:
    for key in (
        "simulated_share",
        "reconstructed_share",
        "row_reconstructed_share",
        "source_share",
        "entry_reconstructed_share",
    ):
        if row.get(key) is not None:
            return fnum(row.get(key))
    return None


def cushion(row: dict[str, Any]) -> int | None:
    for key in ("full_loss_cushion", "full_loss_cushion_estimate", "weighted_full_loss_cushion"):
        if row.get(key) is not None:
            return inum(row.get(key))
    row_net = net(row)
    if row_net > 0:
        return int(row_net // 100)
    return None


def coverage(row: dict[str, Any]) -> float | None:
    if row.get("coverage_pct") is None:
        return None
    return fnum(row.get("coverage_pct"))


def wins_losses(row: dict[str, Any]) -> str:
    if row.get("wins_losses"):
        return str(row.get("wins_losses"))
    return f"{inum(row.get('wins'))}/{inum(row.get('losses'))}"


def strict_forward(row: dict[str, Any]) -> bool:
    return bool(row.get("strict_forward"))


def target_coverage(row: dict[str, Any]) -> bool:
    if row.get("target_coverage") is True:
        return True
    cov = coverage(row)
    return cov is not None and MIN_COVERAGE <= cov <= MAX_COVERAGE


def base_blockers(row: dict[str, Any], live_baseline_cents: float, require_broad: bool = True) -> list[str]:
    blockers = [str(item) for item in (row.get("blockers") or row.get("missing_gates") or [])]
    blockers = [item for item in blockers if item != "live_ready_false"]

    if inum(row.get("settled")) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if net(row) <= 0:
        blockers.append("net_not_positive")
    if require_broad and not target_coverage(row):
        cov = coverage(row)
        if cov is None or cov < MIN_COVERAGE:
            blockers.append("coverage_lt_75pct")
        elif cov > MAX_COVERAGE:
            blockers.append("coverage_gt_90pct")
    share = source_share(row)
    if share is None:
        blockers.append("source_share_unknown")
    elif share > MAX_SOURCE_SHARE:
        blockers.append("source_share_gt_35pct")
    row_cushion = cushion(row)
    if row_cushion is None or row_cushion < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net(row) <= live_baseline_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if not strict_forward(row):
        blockers.append("not_strict_forward")

    seen: set[str] = set()
    deduped: list[str] = []
    for item in blockers:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def bottleneck_tags(blockers: list[str]) -> list[str]:
    tags: list[str] = []
    joined = " ".join(blockers)
    if "needs_own_frozen_forward_birth" in joined or "not_strict_forward" in joined or "diagnostic" in joined:
        tags.append("frozen_forward_evidence")
    if "source" in joined or "reconstructed" in joined or "simulated_share" in joined:
        tags.append("source_quality")
    if "does_not_beat_refreshed_live_baseline" in blockers:
        tags.append("live_baseline_gap")
    if "settled_lt_30" in blockers or "joined_rows_lt_30" in joined or "suppressed_decisions_lt_30" in joined:
        tags.append("sample_or_exit_density")
    if "coverage" in joined:
        tags.append("coverage")
    if "full_loss_cushion_lt_3" in blockers or "cushion" in joined:
        tags.append("fragility")
    if "net_not_positive" in blockers or "weighted_net_not_positive" in blockers or "delta_not_positive" in blockers:
        tags.append("edge_negative")
    return tags or ["other"]


def compact_row(row: dict[str, Any], live_baseline_cents: float) -> dict[str, Any]:
    blockers = base_blockers(row, live_baseline_cents)
    entries = inum(row.get("entries"), inum(row.get("settled")))
    settled = inum(row.get("settled"))
    share = source_share(row)
    reconstructed = None if share is None else int(round(share * entries))
    clean_rows_needed = None
    if reconstructed is not None:
        clean_rows_needed = 0
        while entries + clean_rows_needed > 0 and reconstructed / (entries + clean_rows_needed) > MAX_SOURCE_SHARE:
            clean_rows_needed += 1
    cov = coverage(row)
    coverage_rows_needed = 0
    if cov is not None and cov > 0 and entries > 0:
        denominator_est = entries / (cov / 100.0)
        coverage_rows_needed = max(0, int((MIN_COVERAGE / 100.0 * denominator_est) + 0.999999) - entries)
    row_cushion = cushion(row)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": entries,
        "settled": settled,
        "wins_losses": wins_losses(row),
        "coverage_pct": cov,
        "net_cents": net(row),
        "delta_vs_live_cents": net(row) - live_baseline_cents,
        "source_share": share,
        "cushion": row_cushion,
        "strict_forward": strict_forward(row),
        "live_ready": bool(row.get("live_ready")),
        "sample_rows_needed": max(0, MIN_SETTLED - settled),
        "coverage_rows_needed": coverage_rows_needed,
        "clean_rows_needed_if_current_kept": clean_rows_needed,
        "net_cents_needed_to_live": max(0.0, live_baseline_cents + 1.0 - net(row)),
        "cushion_cents_needed": max(0.0, 100.0 * MIN_CUSHION - net(row)) if row_cushion is not None and row_cushion < MIN_CUSHION else 0.0,
        "blockers": blockers,
        "bottlenecks": bottleneck_tags(blockers),
    }


def dedupe_top(rows: list[dict[str, Any]], live_baseline_cents: float, limit: int = 12) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("gate")), str(row.get("policy")))
        current = by_key.get(key)
        if current is None or net(row) > net(current):
            by_key[key] = row
    ranked = sorted(
        by_key.values(),
        key=lambda row: (
            len(base_blockers(row, live_baseline_cents)),
            -net(row),
            -inum(row.get("settled")),
        ),
    )
    return [compact_row(row, live_baseline_cents) for row in ranked[:limit]]


def source_feasibility_summary(report: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for lane in report.get("lanes") or []:
        rows = lane.get("target_bounds") or lane.get("coverage_targets") or lane.get("targets") or []
        target75 = None
        for item in rows:
            if abs(fnum(item.get("target_coverage_pct") or item.get("target_coverage")) - 75.0) < 0.01:
                target75 = item
                break
        out.append({
            "lane": lane.get("lane"),
            "denominator": lane.get("future_denominator") or lane.get("denominator"),
            "approved_markets_available": lane.get("approved_markets_available"),
            "target75_feasible_under_source_gate": None if target75 is None else (
                target75.get("source_gate_feasible")
                if "source_gate_feasible" in target75
                else target75.get("feasible_under_source_gate")
            ),
            "target75_min_recon_share": None if target75 is None else (
                target75.get("min_reconstructed_share_needed")
                if "min_reconstructed_share_needed" in target75
                else target75.get("min_recon_share")
            ),
            "max_source_clean_coverage_pct": None if target75 is None else target75.get("max_source_clean_coverage_pct"),
        })
    return out


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON, {})
    gate = load_json(GATE_JSON, {})
    near = load_json(NEAR_GATE_JSON, {})
    own_freeze = load_json(OWN_FREEZE_JSON, {})
    source_feas = load_json(SOURCE_FEASIBILITY_JSON, {})
    source_slice = load_json(SOURCE_SLICE_JSON, {})

    live_baseline = fnum(
        ((gate.get("live_baseline") or {}).get("net_pnl_total_cents") if isinstance(gate.get("live_baseline"), dict) else None),
        fnum(gate.get("live_baseline_cents"), fnum(near.get("live_baseline_cents"))),
    )
    if live_baseline == 0.0:
        live_baseline = 100.0 * fnum((gate.get("live_baseline") or {}).get("net_pnl_total_dollars") if isinstance(gate.get("live_baseline"), dict) else 0.0)

    rows = [row for row in tracker.get("rows") or [] if isinstance(row, dict)]
    positive = [row for row in rows if net(row) > 0]
    target_positive = [row for row in positive if target_coverage(row)]
    strict_target_positive = [row for row in target_positive if strict_forward(row)]
    strict_sidecar_positive = [
        row for row in positive
        if strict_forward(row)
        and inum(row.get("settled")) >= MIN_SETTLED
        and source_share(row) is not None
        and fnum(source_share(row)) <= MAX_SOURCE_SHARE
        and (cushion(row) or 0) >= MIN_CUSHION
    ]

    blocker_counts = Counter()
    bottleneck_counts = Counter()
    for row in target_positive:
        blockers = base_blockers(row, live_baseline)
        blocker_counts.update(blockers)
        bottleneck_counts.update(bottleneck_tags(blockers))

    strict_blocker_counts = Counter()
    strict_bottleneck_counts = Counter()
    for row in strict_target_positive:
        blockers = base_blockers(row, live_baseline)
        strict_blocker_counts.update(blockers)
        strict_bottleneck_counts.update(bottleneck_tags(blockers))

    own_best = None
    unions = own_freeze.get("unions") or own_freeze.get("own_freeze_unions") or []
    if unions:
        own_best = compact_row(unions[0], live_baseline)

    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Map the exact bottlenecks stopping current v28 candidates from controlled live-test status.",
        "live_baseline_cents": live_baseline,
        "counts": {
            "rows": len(rows),
            "positive": len(positive),
            "target_positive": len(target_positive),
            "strict_target_positive": len(strict_target_positive),
            "strict_sidecar_positive_sample_source_cushion": len(strict_sidecar_positive),
            "strict_sidecar_positive_sample_source_cushion_beats_live": sum(1 for row in strict_sidecar_positive if net(row) > live_baseline),
            "live_ready": sum(1 for row in rows if row.get("live_ready") is True),
        },
        "bottleneck_counts_target_positive": dict(bottleneck_counts),
        "bottleneck_counts_strict_target_positive": dict(strict_bottleneck_counts),
        "blocker_counts_target_positive": dict(blocker_counts),
        "blocker_counts_strict_target_positive": dict(strict_blocker_counts),
        "top_overall_target_positive": dedupe_top(target_positive, live_baseline, 16),
        "top_strict_target_positive": dedupe_top(strict_target_positive, live_baseline, 16),
        "top_strict_sidecar_positive": dedupe_top(strict_sidecar_positive, live_baseline, 16),
        "controlled_gate_decision": gate.get("decision"),
        "controlled_gate_broad_eligible": len(gate.get("broad_eligible") or []),
        "controlled_gate_sidecar_eligible": len(gate.get("sidecar_eligible") or []),
        "dual_lane_own_freeze_best": own_best,
        "feature_gate_source_feasibility": source_feasibility_summary(source_feas),
        "source_slice_interpretation": source_slice.get("interpretation") or [],
        "recommended_work_queue": recommended_work_queue(live_baseline, gate, own_best, source_feas, source_slice),
    }


def recommended_work_queue(
    live_baseline: float,
    gate: dict[str, Any],
    own_best: dict[str, Any] | None,
    source_feas: dict[str, Any],
    source_slice: dict[str, Any],
) -> list[dict[str, Any]]:
    closest = (gate.get("closest_broad") or [{}])[0]
    source_notes = source_slice.get("interpretation") or []
    feasibility_notes = source_feas.get("interpretation") or []
    queue = [
        {
            "priority": 1,
            "branch": "dual_lane_overlap_union",
            "candidate": closest.get("policy"),
            "main_bottleneck": "frozen_forward_evidence",
            "why": "It beats the live baseline diagnostically with broad coverage and source share under 35%, but the scored row is not strict-forward and needs its own post-birth evidence.",
            "work": "Keep the own-freeze watch alive and score only rows after its birth. Do not tune the old diagnostic row into live status.",
            "ready_when": "Own-freeze union has >=30 settled, 75-90% coverage, <=35% source share, positive PnL, cushion >=3, and net above refreshed live baseline.",
            "current_state": own_best,
        },
        {
            "priority": 2,
            "branch": "feature_gate_coverage_size_shrink",
            "candidate": "raw05 anchor + low-abs-d repair size shrink",
            "main_bottleneck": "source_quality_plus_live_baseline_gap",
            "why": "The strict branch has sample, coverage, and cushion, but its source share is too high and its PnL is below the refreshed live baseline.",
            "work": "Stop widening repair rows. Focus on fresh approved middle-distance rows or observable confirmation that can replace low-abs reconstructed repair filler.",
            "ready_when": "A child born from this rule has <=35% row-source share, still covers >=75%, and closes the live-baseline gap without post-hoc source labels.",
            "source_feasibility_notes": feasibility_notes[:2],
            "source_slice_notes": source_notes[:4],
        },
        {
            "priority": 3,
            "branch": "boundary_clock_feature_gate_continuous_penalty",
            "candidate": "post_penalty_birth_entry/bridge_cheap_penalty025_rank_only",
            "main_bottleneck": "live_baseline_gap",
            "why": "This is the closest existing strict sidecar shape: sample, source quality, and cushion are already acceptable if coverage is not required, but net is far below the refreshed live baseline.",
            "work": "Do not mix it into size-shrink; cached union check showed only three non-overlap rows, -9c added net, and worse source share. Let it accumulate or find a pre-frozen complementary strict component that adds clean positive non-overlap rows.",
            "ready_when": "A strict sidecar row clears positive PnL, >=30 settled, <=35% source share, cushion >=3, and beats or materially improves the refreshed live baseline under the controlled gate.",
        },
        {
            "priority": 4,
            "branch": "exit_policy_children",
            "candidate": "soft-frontier/midprice delayed-recheck, book-gap/loss-guard, value-exit guards",
            "main_bottleneck": "sample_or_exit_density",
            "why": "Exit diagnostics show real winner clipping, but strict children mostly have too few joined rows or too few suppressed decisions.",
            "work": "Track post-birth joined-exit density and adverse-path safety. Promote no exit child until the suppression population is large enough.",
            "ready_when": ">=30 joined rows, >=30 suppressed decisions where applicable, positive delta/net, cushion >=3, no harmful suppression cluster.",
        },
        {
            "priority": 5,
            "branch": "top_component_mix_portfolio",
            "candidate": "parent-fill repair plus rescue/quarantine children",
            "main_bottleneck": "child_birth_evidence",
            "why": "This is the strongest diagnostic blueprint after dual-lane work, but the useful children have immature or zero post-child rows.",
            "work": "Keep child watches separated; do not merge parent diagnostic PnL with child rules as if it were frozen evidence.",
            "ready_when": "Each child clears sample/source/coverage/cushion/live-baseline gates from its own freeze.",
        },
    ]
    if live_baseline <= 0:
        queue.append({
            "priority": 99,
            "branch": "scorecard_integrity",
            "candidate": "live baseline refresh",
            "main_bottleneck": "missing_live_baseline",
            "why": "No positive live baseline was available in the loaded gate file.",
            "work": "Refresh score_bot_log.py before making candidate-vs-live claims.",
            "ready_when": "Controlled gate report has a nonzero refreshed live baseline.",
        })
    return queue


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value) * 100:.1f}%" if fnum(value) <= 1.0 else f"{fnum(value):.2f}%"


def cents(value: Any) -> str:
    return f"{fnum(value):.1f}c"


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Live-Ready Bottleneck Map",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Controlled gate decision: `{report.get('controlled_gate_decision')}`",
        f"- Broad/sidecar eligible: `{report.get('controlled_gate_broad_eligible')}/{report.get('controlled_gate_sidecar_eligible')}`",
        "",
        "## Counts",
        "",
    ]
    counts = report.get("counts") or {}
    lines.extend([
        f"- Rows / positive / target-positive / strict-target-positive / live-ready: "
        f"`{counts.get('rows')}/{counts.get('positive')}/{counts.get('target_positive')}/"
        f"{counts.get('strict_target_positive')}/{counts.get('live_ready')}`",
        f"- Strict sidecar-positive sample/source/cushion lanes / beating live: "
        f"`{counts.get('strict_sidecar_positive_sample_source_cushion')}/"
        f"{counts.get('strict_sidecar_positive_sample_source_cushion_beats_live')}`",
        "",
        "## Main Bottlenecks",
        "",
        "### Target-Positive Rows",
        "",
    ])
    for key, value in sorted((report.get("bottleneck_counts_target_positive") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "### Strict Target-Positive Rows", ""])
    for key, value in sorted((report.get("bottleneck_counts_strict_target_positive") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")

    lines.extend([
        "",
        "## Recommended Work Queue",
        "",
        "| priority | branch | bottleneck | work | ready when |",
        "|---:|---|---|---|---|",
    ])
    for item in report.get("recommended_work_queue") or []:
        lines.append(
            f"| {item.get('priority')} | `{item.get('branch')}` | `{item.get('main_bottleneck')}` | "
            f"{item.get('work')} | {item.get('ready_when')} |"
        )

    def row_table(title: str, rows: list[dict[str, Any]]) -> None:
        lines.extend([
            "",
            f"## {title}",
            "",
        "| gate | policy | settled | W/L | coverage | net | delta live | source | cushion | strict | bottlenecks | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
        ])
        for row in rows:
            lines.append(
                f"| `{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | "
                f"{row.get('wins_losses')} | {pct(row.get('coverage_pct'))} | {cents(row.get('net_cents'))} | "
                f"{cents(row.get('delta_vs_live_cents'))} | {pct(row.get('source_share'))} | "
                f"{row.get('cushion')} | `{row.get('strict_forward')}` | "
                f"{', '.join(row.get('bottlenecks') or [])} | {', '.join(row.get('blockers') or [])} |"
            )
        lines.extend([
            "",
            "| gate | policy | sample need | coverage need | clean source need | cents to live | cushion cents need |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for row in rows:
            lines.append(
                f"| `{row.get('gate')}` | `{row.get('policy')}` | {row.get('sample_rows_needed')} | "
                f"{row.get('coverage_rows_needed')} | {row.get('clean_rows_needed_if_current_kept')} | "
                f"{cents(row.get('net_cents_needed_to_live'))} | {cents(row.get('cushion_cents_needed'))} |"
            )

    row_table("Closest Overall Target-Positive", report.get("top_overall_target_positive") or [])
    row_table("Closest Strict Target-Positive", report.get("top_strict_target_positive") or [])
    row_table("Closest Strict Sidecar-Positive", report.get("top_strict_sidecar_positive") or [])

    if report.get("feature_gate_source_feasibility"):
        lines.extend([
            "",
            "## Feature-Gate Source Feasibility",
            "",
            "| lane | denominator | approved markets | 75% feasible under source gate | min recon share at 75% | max source-clean coverage |",
            "|---|---:|---:|---|---:|---:|",
        ])
        for row in report.get("feature_gate_source_feasibility") or []:
            lines.append(
                f"| `{row.get('lane')}` | {row.get('denominator')} | {row.get('approved_markets_available')} | "
                f"`{row.get('target75_feasible_under_source_gate')}` | {pct(row.get('target75_min_recon_share'))} | "
                f"{pct(row.get('max_source_clean_coverage_pct'))} |"
            )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
