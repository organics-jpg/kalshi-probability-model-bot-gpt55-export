"""Gate checklist for making the v28 dual-lane candidate live ready.

Research-only; no live bot changes and no orders.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
GATE_JSON = OUT_DIR / "v28_dual_lane_live_readiness_gate_latest.json"
RUNWAY_JSON = OUT_DIR / "v28_dual_lane_live_readiness_runway_latest.json"
UPDATE_JSON = OUT_DIR / "v28_dual_lane_live_market_update_latest.json"
MECHANISM_JSON = OUT_DIR / "v28_dual_lane_proxy_mechanism_audit_latest.json"
STRICT_PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
LOSS_AUDIT_JSON = OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.json"
PARENT_SHRINK_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.json"
PARENT_SHRINK_FRONTIER_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.json"
SIDECAR_SAFETY_JSON = OUT_DIR / "v28_dual_lane_sidecar_safety_watch_latest.json"
SAME_WINDOW_COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OVERLAY_AUDIT_JSON = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.json"
OVERLAY_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
OVERLAY_V2_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_readiness_checklist_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_readiness_checklist_latest.md"


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


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def cents(value: Any) -> str:
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return "n/a"
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def gate_status(ok: bool, evidence: str, blocker: str | None = None) -> dict[str, Any]:
    return {
        "status": "pass" if ok else "blocked",
        "evidence": evidence,
        "blocker": "" if ok else (blocker or ""),
    }


def build_report() -> dict[str, Any]:
    gate = load_json(GATE_JSON)
    runway = load_json(RUNWAY_JSON)
    update = load_json(UPDATE_JSON)
    mechanism = load_json(MECHANISM_JSON)
    strict_precheck = load_json(STRICT_PRECHECK_JSON)
    loss_audit = load_json(LOSS_AUDIT_JSON)
    parent_shrink = load_json(PARENT_SHRINK_JSON)
    parent_frontier = load_json(PARENT_SHRINK_FRONTIER_JSON)
    sidecar_safety = load_json(SIDECAR_SAFETY_JSON)
    same_window = load_json(SAME_WINDOW_COMPARE_JSON)
    overlay_audit = load_json(OVERLAY_AUDIT_JSON)
    overlay_filter = load_json(OVERLAY_FILTER_WATCH_JSON)
    overlay_v2_filter = load_json(OVERLAY_V2_FILTER_WATCH_JSON)
    requirements = gate.get("requirements") if isinstance(gate.get("requirements"), dict) else {}
    unions = gate.get("unions") if isinstance(gate.get("unions"), list) else []
    current = unions[0] if unions and isinstance(unions[0], dict) else {}
    sample_clock = gate.get("sample_clock") if isinstance(gate.get("sample_clock"), dict) else {}
    runway_section = runway.get("runway") if isinstance(runway.get("runway"), dict) else {}
    sidecar = update.get("sidecar_preview") if isinstance(update.get("sidecar_preview"), dict) else {}
    primary = update.get("primary_proxy_preview") if isinstance(update.get("primary_proxy_preview"), dict) else {}
    precheck = strict_precheck.get("best_union") if isinstance(strict_precheck.get("best_union"), dict) else {}
    repair_state = parent_shrink.get("state") if isinstance(parent_shrink.get("state"), dict) else {}
    repair_unions = parent_shrink.get("unions") if isinstance(parent_shrink.get("unions"), list) else []
    repair_best = repair_unions[0] if repair_unions and isinstance(repair_unions[0], dict) else {}
    repair_summary = repair_best.get("summary") if isinstance(repair_best.get("summary"), dict) else {}
    frontier_state = parent_frontier.get("state") if isinstance(parent_frontier.get("state"), dict) else {}
    frontier_unions = parent_frontier.get("unions") if isinstance(parent_frontier.get("unions"), list) else []
    frontier_best = frontier_unions[0] if frontier_unions and isinstance(frontier_unions[0], dict) else {}
    frontier_summary = frontier_best.get("summary") if isinstance(frontier_best.get("summary"), dict) else {}
    safety_state = sidecar_safety.get("state") if isinstance(sidecar_safety.get("state"), dict) else {}
    safety_best = sidecar_safety.get("best") if isinstance(sidecar_safety.get("best"), dict) else {}
    safety_summary = safety_best.get("summary") if isinstance(safety_best.get("summary"), dict) else {}
    same_window_delta = fnum(same_window.get("candidate_minus_live_same_markets_cents"), 0.0)
    helpful_overlay = overlay_audit.get("helpful_overlay_summary") if isinstance(overlay_audit.get("helpful_overlay_summary"), dict) else {}
    harmful_overlay = overlay_audit.get("harmful_overlay_summary") if isinstance(overlay_audit.get("harmful_overlay_summary"), dict) else {}
    filter_state = overlay_filter.get("state") if isinstance(overlay_filter.get("state"), dict) else {}
    filter_best = overlay_filter.get("best_lane") if isinstance(overlay_filter.get("best_lane"), dict) else {}
    filter_summary = filter_best.get("summary") if isinstance(filter_best.get("summary"), dict) else {}
    filter_v2_state = overlay_v2_filter.get("state") if isinstance(overlay_v2_filter.get("state"), dict) else {}
    filter_v2_best = overlay_v2_filter.get("best_lane") if isinstance(overlay_v2_filter.get("best_lane"), dict) else {}
    filter_v2_summary = filter_v2_best.get("summary") if isinstance(filter_v2_best.get("summary"), dict) else {}
    current_windows = int(update.get("possible_windows_since_freeze") or 0)
    precheck_windows = int(strict_precheck.get("possible_market_windows_since_freeze") or -1)
    precheck_window_lag = current_windows - precheck_windows if precheck_windows >= 0 else None

    settled = int(current.get("settled") or 0)
    net = fnum(current.get("net_cents"), 0.0)
    coverage = fnum(current.get("coverage_pct"), math.nan)
    recon = current.get("reconstructed_share")
    cushion = int(current.get("full_loss_cushion") or 0)
    live = fnum(gate.get("live_baseline_cents") or update.get("live_baseline_cents"), 0.0)
    min_settled = int(requirements.get("min_settled") or 30)
    coverage_min = fnum(requirements.get("coverage_min_pct"), 75.0)
    coverage_max = fnum(requirements.get("coverage_max_pct"), 90.0)
    max_recon = fnum(requirements.get("max_reconstructed_share"), 0.35)
    min_cushion = int(requirements.get("min_full_loss_cushion") or 3)

    checks = {
        "frozen_candidate_birth": gate_status(
            bool(gate.get("freeze_ts_utc")),
            f"freeze={gate.get('freeze_ts_utc')} local={gate.get('freeze_local_time')}",
        ),
        "shadow_collection_flowing": gate_status(
            int(update.get("post_freeze_events") or 0) > 0 and int(update.get("post_freeze_distinct_markets") or 0) > 0,
            (
                f"events={update.get('post_freeze_events')} entry_rows={update.get('post_freeze_entry_rows')} "
                f"markets={update.get('post_freeze_distinct_markets')}"
            ),
            "no_post_freeze_shadow_flow",
        ),
        "minimum_forward_sample": gate_status(
            settled >= min_settled,
            f"own_freeze_settled={settled}/{min_settled}; windows_remaining={sample_clock.get('windows_remaining_to_min_sample')}",
            "waiting_for_30_strict_rows",
        ),
        "positive_after_fees": gate_status(
            net > 0,
            f"own_freeze_net={cents(net)}",
            "own_freeze_net_not_positive",
        ),
        "beats_live_baseline": gate_status(
            net > live,
            f"own_freeze_net={cents(net)} live_baseline={cents(live)} needed={cents(runway_section.get('net_cents_needed_to_beat_live'))}",
            "does_not_beat_refreshed_live_baseline",
        ),
        "coverage_band": gate_status(
            math.isfinite(coverage) and coverage_min <= coverage <= coverage_max,
            f"own_freeze_coverage={coverage:.2f}% target={coverage_min:.1f}-{coverage_max:.1f}%",
            "coverage_outside_target_or_unknown",
        ),
        "source_quality": gate_status(
            recon is not None and fnum(recon) <= max_recon,
            f"own_freeze_reconstructed_share={'n/a' if recon is None else f'{100.0 * fnum(recon):.2f}%'} max={100.0 * max_recon:.2f}%",
            "source_share_unknown_or_gt_35pct",
        ),
        "fragility_cushion": gate_status(
            cushion >= min_cushion,
            f"own_freeze_full_loss_cushion={cushion}/{min_cushion}",
            "full_loss_cushion_lt_3",
        ),
        "preview_sidecar_shape": gate_status(
            fnum(sidecar.get("net_cents"), 0.0) > 0
            and fnum(sidecar.get("reconstructed_share"), 1.0) <= max_recon,
            (
                f"sidecar_preview={cents(sidecar.get('net_cents'))} "
                f"W/L={sidecar.get('wins')}/{sidecar.get('losses')} "
                f"recon={'n/a' if sidecar.get('reconstructed_share') is None else f'{100.0 * fnum(sidecar.get('reconstructed_share')):.2f}%'}"
            ),
            "sidecar_preview_not_clean_positive",
        ),
        "primary_proxy_risk_understood": gate_status(
            "do_not_use_primary_proxy_as_live_ready_evidence" in (mechanism.get("mechanism_read") or []),
            f"primary_proxy={cents(primary.get('net_cents'))} source_counts={primary.get('source_counts')}",
            "primary_proxy_risk_not_classified",
        ),
        "strict_replay_path_prechecked": gate_status(
            bool(precheck) and int(precheck.get("settled") or 0) > 0,
            (
                f"precheck_settled={precheck.get('settled')} "
                f"net={cents(precheck.get('net_cents'))} "
                f"precheck_windows={precheck_windows} current_windows={current_windows} "
                f"promotion_use={strict_precheck.get('promotion_use')}"
            ),
            "strict_replay_precheck_missing_or_empty",
        ),
        "strict_precheck_freshness": gate_status(
            precheck_window_lag is not None and 0 <= precheck_window_lag <= 1,
            (
                f"precheck_windows={precheck_windows} current_windows={current_windows} "
                f"lag={precheck_window_lag}"
            ),
            "strict_replay_precheck_stale",
        ),
        "loss_bottleneck_classified": gate_status(
            "losses_share_high_cost_low_edge_shape" in (loss_audit.get("loss_tags") or []),
            f"tags={loss_audit.get('loss_tags')} next={loss_audit.get('next_research_action')}",
            "current_losses_not_classified_into_actionable_shape",
        ),
        "parent_shrink_repair_registered": gate_status(
            bool(repair_state.get("freeze_ts_utc")),
            (
                f"repair_freeze={repair_state.get('freeze_ts_utc')} "
                f"local={parent_shrink.get('freeze_local_time')} "
                f"rule={(repair_state.get('shrink_rule') or {})}"
            ),
            "repair_branch_not_born",
        ),
        "parent_shrink_forward_sample": gate_status(
            int(repair_summary.get("settled") or 0) >= min_settled,
            (
                f"repair_settled={repair_summary.get('settled')}/{min_settled}; "
                f"repair_windows_remaining={parent_shrink.get('market_windows_remaining_to_min_sample')}"
            ),
            "repair_branch_waiting_for_30_strict_rows",
        ),
        "parent_shrink_frontier_registered": gate_status(
            bool(frontier_state.get("freeze_ts_utc")),
            (
                f"frontier_freeze={frontier_state.get('freeze_ts_utc')} "
                f"local={parent_frontier.get('freeze_local_time')} "
                f"weights={frontier_state.get('weights')}"
            ),
            "frontier_branch_not_born",
        ),
        "parent_shrink_frontier_forward_sample": gate_status(
            int(frontier_summary.get("settled") or 0) >= min_settled,
            (
                f"frontier_best={frontier_best.get('frontier_label')} "
                f"settled={frontier_summary.get('settled')}/{min_settled}; "
                f"frontier_windows_remaining={parent_frontier.get('market_windows_remaining_to_min_sample')}"
            ),
            "frontier_branch_waiting_for_30_strict_rows",
        ),
        "sidecar_safety_registered": gate_status(
            bool(safety_state.get("freeze_ts_utc")),
            (
                f"safety_freeze={safety_state.get('freeze_ts_utc')} "
                f"local={sidecar_safety.get('freeze_local_time')} "
                f"rule={safety_state.get('rule')}"
            ),
            "sidecar_safety_branch_not_born",
        ),
        "sidecar_safety_forward_sample": gate_status(
            int(safety_summary.get("settled") or 0) >= min_settled,
            (
                f"safety_best={((safety_best.get('lane') or {}).get('policy'))} "
                f"settled={safety_summary.get('settled')}/{min_settled}; "
                f"safety_windows_remaining={sidecar_safety.get('market_windows_remaining_to_min_sample')}"
            ),
            "sidecar_safety_waiting_for_30_strict_rows",
        ),
        "same_window_live_edge": gate_status(
            bool(same_window) and same_window_delta > 0,
            (
                f"candidate_minus_live_same_markets={cents(same_window_delta)} "
                f"candidate={(same_window.get('candidate_summary') or {}).get('net_cents')}c "
                f"live_same={(same_window.get('live_same_candidate_markets_summary') or {}).get('net_cents')}c"
            ),
            "candidate_not_beating_live_on_same_post_freeze_markets",
        ),
        "overlay_shape_classified": gate_status(
            bool(overlay_audit) and fnum(helpful_overlay.get("candidate_minus_live_cents"), 0.0) > 0,
            (
                f"helpful_delta={cents(helpful_overlay.get('candidate_minus_live_cents'))} "
                f"harmful_delta={cents(harmful_overlay.get('candidate_minus_live_cents'))} "
                f"read={(overlay_audit.get('candidate_read') or [])[:1]}"
            ),
            "overlay_opportunity_not_classified",
        ),
        "overlay_filter_registered": gate_status(
            bool(filter_state.get("freeze_ts_utc")),
            (
                f"filter_freeze={filter_state.get('freeze_ts_utc')} "
                f"local={overlay_filter.get('freeze_local_time')} "
                f"rule={(filter_state.get('overlay_rule') or {})}"
            ),
            "overlay_filter_branch_not_born",
        ),
        "overlay_filter_forward_sample": gate_status(
            int(filter_summary.get("settled") or 0) >= min_settled,
            (
                f"filter_best={filter_best.get('sidecar_policy')} "
                f"settled={filter_summary.get('settled')}/{min_settled}; "
                f"filter_windows_remaining={overlay_filter.get('market_windows_remaining_to_min_sample')}"
            ),
            "overlay_filter_waiting_for_30_strict_rows",
        ),
        "overlay_v2_filter_registered": gate_status(
            bool(filter_v2_state.get("freeze_ts_utc")),
            (
                f"filter_v2_freeze={filter_v2_state.get('freeze_ts_utc')} "
                f"local={overlay_v2_filter.get('freeze_local_time')} "
                f"rule={(filter_v2_state.get('overlay_rule') or {})}"
            ),
            "overlay_v2_filter_branch_not_born",
        ),
        "overlay_v2_filter_forward_sample": gate_status(
            int(filter_v2_summary.get("settled") or 0) >= min_settled,
            (
                f"filter_v2_best={filter_v2_best.get('sidecar_policy')} "
                f"settled={filter_v2_summary.get('settled')}/{min_settled}; "
                f"filter_v2_windows_remaining={overlay_v2_filter.get('market_windows_remaining_to_min_sample')}"
            ),
            "overlay_v2_filter_waiting_for_30_strict_rows",
        ),
    }
    blocked = [name for name, item in checks.items() if item.get("status") != "pass"]
    return {
        "generated_at_utc": utc_now_iso(),
        "decision": "live_ready" if not blocked and current.get("live_ready") else "not_live_ready",
        "freeze_ts_utc": gate.get("freeze_ts_utc"),
        "freeze_local_time": gate.get("freeze_local_time"),
        "live_baseline_cents": live,
        "current_policy": current.get("policy"),
        "checks": checks,
        "blocked_checks": blocked,
        "next_readiness_actions": [
            "Keep collecting until strict own-freeze scorer has at least 30 settled rows.",
            "At the 30-window mark, run the heavy own-freeze replay and trust those rows over preview rows.",
            "Refresh the manual strict replay precheck if its window lag grows beyond one window before the 30-window gate.",
            "If source share remains unknown/high, inspect scorer joins before considering any live test.",
            "If sidecar stays clean but union fails because of primary source risk, isolate that as a dual-lane component issue before any promotion.",
            "Track the parent-shrink repair branch from its own freeze; do not use rows before that repair freeze as promotion evidence.",
            "Track the parent-shrink weight frontier from its own freeze; use it only to choose shrink strength after forward evidence matures.",
            "Track the sidecar-safety fallback from its own freeze as the clean fallback if parent-lane repairs remain unsafe.",
            "Use same-window live comparison as a bottleneck diagnostic; do not treat total-live-baseline comparison as the only signal.",
            "Track the NO-side low-recross overlay filter from its own freeze before considering it as a risk-control overlay.",
            "Track the raw-edge/low-recross/distance overlay v2 filter from its own freeze before considering it as a risk-control overlay.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Dual-Lane Readiness Checklist",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Current policy: `{report.get('current_policy')}`",
        "",
        "## Checklist",
        "",
        "| check | status | evidence | blocker |",
        "|---|---|---|---|",
    ]
    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}
    for name, item in checks.items():
        if not isinstance(item, dict):
            continue
        lines.append(
            f"| `{name}` | `{item.get('status')}` | {item.get('evidence')} | {item.get('blocker')} |"
        )
    lines.extend(
        [
            "",
            "## Blocked Checks",
            "",
        ]
    )
    blocked = report.get("blocked_checks") or []
    if blocked:
        lines.extend(f"- `{item}`" for item in blocked)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Readiness Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report.get("next_readiness_actions") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
