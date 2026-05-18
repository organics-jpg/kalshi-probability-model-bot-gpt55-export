"""Durable handoff report for the v28 dual-lane live-readiness push.

Research-only; no live bot changes and no orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
UPDATE_JSON = OUT_DIR / "v28_dual_lane_live_market_update_latest.json"
CHECKLIST_JSON = OUT_DIR / "v28_dual_lane_readiness_checklist_latest.json"
LEDGER_JSON = OUT_DIR / "v28_dual_lane_live_market_snapshot_ledger_latest.md"
ACCOUNTING_JSON = OUT_DIR / "v28_dual_lane_strict_replay_accounting_audit_latest.json"
CONTRAST_JSON = OUT_DIR / "v28_dual_lane_variant_contrast_latest.json"
LOSS_AUDIT_JSON = OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.json"
PARENT_SHRINK_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.json"
PARENT_SHRINK_FRONTIER_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.json"
SAME_WINDOW_COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OVERLAY_AUDIT_JSON = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.json"
OVERLAY_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
OVERLAY_V2_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
OVERLAY_V2_READINESS_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_ready_handoff_latest.md"


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


def money(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any, already_pct: bool = True) -> str:
    if value is None:
        return "n/a"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not already_pct:
        number *= 100.0
    return f"{number:.2f}%"


def build_report() -> dict[str, Any]:
    update = load_json(UPDATE_JSON)
    checklist = load_json(CHECKLIST_JSON)
    accounting = load_json(ACCOUNTING_JSON)
    contrast = load_json(CONTRAST_JSON)
    loss_audit = load_json(LOSS_AUDIT_JSON)
    parent_shrink = load_json(PARENT_SHRINK_JSON)
    parent_shrink_frontier = load_json(PARENT_SHRINK_FRONTIER_JSON)
    same_window = load_json(SAME_WINDOW_COMPARE_JSON)
    overlay_audit = load_json(OVERLAY_AUDIT_JSON)
    overlay_filter = load_json(OVERLAY_FILTER_WATCH_JSON)
    overlay_v2_filter = load_json(OVERLAY_V2_FILTER_WATCH_JSON)
    overlay_v2_readiness = load_json(OVERLAY_V2_READINESS_JSON)
    sidecar = update.get("sidecar_preview") if isinstance(update.get("sidecar_preview"), dict) else {}
    primary = update.get("primary_proxy_preview") if isinstance(update.get("primary_proxy_preview"), dict) else {}
    strict_precheck = update.get("strict_replay_precheck") if isinstance(update.get("strict_replay_precheck"), dict) else {}
    checks = checklist.get("checks") if isinstance(checklist.get("checks"), dict) else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "decision": update.get("decision"),
        "freeze_ts_utc": update.get("freeze_ts_utc"),
        "freeze_local_time": update.get("freeze_local_time"),
        "live_baseline_cents": update.get("live_baseline_cents"),
        "possible_windows_since_freeze": update.get("possible_windows_since_freeze"),
        "windows_remaining_to_30": update.get("windows_remaining_to_30"),
        "earliest_30_window_local_time": update.get("earliest_30_window_local_time"),
        "post_freeze_events": update.get("post_freeze_events"),
        "post_freeze_entry_rows": update.get("post_freeze_entry_rows"),
        "post_freeze_distinct_markets": update.get("post_freeze_distinct_markets"),
        "sidecar_preview": sidecar,
        "primary_proxy_preview": primary,
        "strict_precheck": strict_precheck,
        "strict_precheck_generated_at_utc": update.get("strict_replay_precheck_generated_at_utc"),
        "strict_precheck_windows": update.get("strict_replay_precheck_windows"),
        "variant_contrast": contrast,
        "loss_bottleneck_audit": loss_audit,
        "parent_shrink_watch": parent_shrink,
        "parent_shrink_frontier_watch": parent_shrink_frontier,
        "same_window_live_compare": same_window,
        "overlay_opportunity_audit": overlay_audit,
        "overlay_filter_watch": overlay_filter,
        "overlay_v2_filter_watch": overlay_v2_filter,
        "overlay_v2_readiness": overlay_v2_readiness,
        "accounting_audit": {
            "generated_at_utc": accounting.get("generated_at_utc"),
            "accounting_patch_verified": accounting.get("accounting_patch_verified"),
            "score_path_read": accounting.get("score_path_read"),
        },
        "passed_checks": [name for name, row in checks.items() if isinstance(row, dict) and row.get("status") == "pass"],
        "blocked_checks": checklist.get("blocked_checks") if isinstance(checklist.get("blocked_checks"), list) else [],
        "hard_blockers": update.get("hard_blockers") if isinstance(update.get("hard_blockers"), list) else [],
        "artifact_paths": {
            "checkpoint_runner": str(ROOT / "scripts" / "run_v28_dual_lane_30_window_checkpoint.ps1"),
            "live_market_update": str(UPDATE_JSON),
            "readiness_checklist": str(CHECKLIST_JSON),
            "snapshot_ledger": str(LEDGER_JSON),
            "strict_replay_precheck": str(OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.md"),
            "accounting_audit": str(OUT_DIR / "v28_dual_lane_strict_replay_accounting_audit_latest.md"),
            "variant_contrast": str(OUT_DIR / "v28_dual_lane_variant_contrast_latest.md"),
            "loss_bottleneck_audit": str(OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.md"),
            "parent_shrink_watch": str(OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.md"),
            "parent_shrink_frontier_watch": str(OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.md"),
            "same_window_live_compare": str(OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.md"),
            "overlay_opportunity_audit": str(OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.md"),
            "overlay_filter_watch": str(OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.md"),
            "overlay_v2_filter_watch": str(OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.md"),
            "overlay_v2_readiness": str(OUT_DIR / "v28_dual_lane_overlay_v2_readiness_latest.md"),
            "live_test_blocker_audit": str(OUT_DIR / "v28_dual_lane_live_test_blocker_audit_latest.md"),
            "live_test_coordinator_spec": str(OUT_DIR / "v28_dual_lane_live_test_coordinator_spec_latest.md"),
            "paper_coordinator_replay": str(OUT_DIR / "v28_dual_lane_paper_coordinator_replay_latest.md"),
        },
        "next_actions": [
            "Do not live-test before the normal own-freeze gate reaches at least 30 settled strict-forward rows.",
            "At or after the 4:30pm ET 30-window checkpoint, refresh live baseline and run the normal own-freeze watch without force.",
            "If the normal own-freeze watch still reports zero rows after the checkpoint, debug scorer joins immediately; the forced precheck proved the heavy path can execute.",
            "If both entry and bridge clear sample/source/coverage/PnL gates, prefer the one with better full-loss cushion and live-baseline delta.",
            "If bridge remains higher PnL but entry remains higher coverage, do not collapse the choice to PnL alone; use full promotion gates.",
            "Refresh the manual strict precheck if its window lag exceeds one before the 30-window gate.",
            "Track the parent-shrink repair branch from its own freeze and do not promote it before its own 30-row gate.",
            "Use the parent-shrink frontier to compare shrink strengths under one freeze before choosing a live candidate weight.",
            "Treat the current broad dual-lane branch as blocked by same-window live underperformance until it beats live v28 on the same post-freeze markets.",
            "Track overlay v1 and v2 as risk-control overlays only; do not use their diagnostic green rows as promotion evidence before their own freezes mature.",
            "If live testing remains desired, build the paper coordinator milestone first; do not launch a second independent live bot.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    sidecar = report.get("sidecar_preview") if isinstance(report.get("sidecar_preview"), dict) else {}
    primary = report.get("primary_proxy_preview") if isinstance(report.get("primary_proxy_preview"), dict) else {}
    precheck = report.get("strict_precheck") if isinstance(report.get("strict_precheck"), dict) else {}
    contrast = report.get("variant_contrast") if isinstance(report.get("variant_contrast"), dict) else {}
    loss_audit = report.get("loss_bottleneck_audit") if isinstance(report.get("loss_bottleneck_audit"), dict) else {}
    parent_shrink = report.get("parent_shrink_watch") if isinstance(report.get("parent_shrink_watch"), dict) else {}
    parent_frontier = (
        report.get("parent_shrink_frontier_watch")
        if isinstance(report.get("parent_shrink_frontier_watch"), dict)
        else {}
    )
    same_window = (
        report.get("same_window_live_compare")
        if isinstance(report.get("same_window_live_compare"), dict)
        else {}
    )
    overlay = (
        report.get("overlay_opportunity_audit")
        if isinstance(report.get("overlay_opportunity_audit"), dict)
        else {}
    )
    overlay_filter = (
        report.get("overlay_filter_watch")
        if isinstance(report.get("overlay_filter_watch"), dict)
        else {}
    )
    overlay_v2_filter = (
        report.get("overlay_v2_filter_watch")
        if isinstance(report.get("overlay_v2_filter_watch"), dict)
        else {}
    )
    overlay_v2_readiness = (
        report.get("overlay_v2_readiness")
        if isinstance(report.get("overlay_v2_readiness"), dict)
        else {}
    )
    accounting = report.get("accounting_audit") if isinstance(report.get("accounting_audit"), dict) else {}
    artifacts = report.get("artifact_paths") if isinstance(report.get("artifact_paths"), dict) else {}
    loss_baseline = loss_audit.get("baseline") if isinstance(loss_audit.get("baseline"), dict) else {}
    loss_variants = [row for row in loss_audit.get("variants") or [] if isinstance(row, dict)]
    shrink_variant = next(
        (row for row in loss_variants if row.get("name") == "shrink_high_cost_low_edge_50pct"),
        {},
    )
    parent_state = parent_shrink.get("state") if isinstance(parent_shrink.get("state"), dict) else {}
    parent_unions = parent_shrink.get("unions") if isinstance(parent_shrink.get("unions"), list) else []
    parent_best = parent_unions[0] if parent_unions and isinstance(parent_unions[0], dict) else {}
    parent_summary = parent_best.get("summary") if isinstance(parent_best.get("summary"), dict) else {}
    frontier_state = parent_frontier.get("state") if isinstance(parent_frontier.get("state"), dict) else {}
    frontier_unions = parent_frontier.get("unions") if isinstance(parent_frontier.get("unions"), list) else []
    frontier_best = frontier_unions[0] if frontier_unions and isinstance(frontier_unions[0], dict) else {}
    frontier_summary = frontier_best.get("summary") if isinstance(frontier_best.get("summary"), dict) else {}
    same_candidate = same_window.get("candidate_summary") if isinstance(same_window.get("candidate_summary"), dict) else {}
    same_live = (
        same_window.get("live_same_candidate_markets_summary")
        if isinstance(same_window.get("live_same_candidate_markets_summary"), dict)
        else {}
    )
    helpful_overlay = overlay.get("helpful_overlay_summary") if isinstance(overlay.get("helpful_overlay_summary"), dict) else {}
    harmful_overlay = overlay.get("harmful_overlay_summary") if isinstance(overlay.get("harmful_overlay_summary"), dict) else {}
    overlay_filter_state = overlay_filter.get("state") if isinstance(overlay_filter.get("state"), dict) else {}
    overlay_v2_state = overlay_v2_filter.get("state") if isinstance(overlay_v2_filter.get("state"), dict) else {}
    overlay_v2_best = (
        overlay_v2_filter.get("best_lane") if isinstance(overlay_v2_filter.get("best_lane"), dict) else {}
    )
    overlay_v2_summary = (
        overlay_v2_best.get("summary") if isinstance(overlay_v2_best.get("summary"), dict) else {}
    )
    lines = [
        "# v28 Dual-Lane Live-Ready Handoff",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Windows since freeze / remaining: `{report.get('possible_windows_since_freeze')}` / `{report.get('windows_remaining_to_30')}`",
        f"- Earliest 30-window local checkpoint: `{report.get('earliest_30_window_local_time')}`",
        f"- Post-freeze events / entry rows / markets: `{report.get('post_freeze_events')}` / `{report.get('post_freeze_entry_rows')}` / `{report.get('post_freeze_distinct_markets')}`",
        "",
        "## Current Read",
        "",
        "- The dual-lane candidate is collecting live/shadow market evidence, but is not live-ready.",
        "- The sidecar observable preview is the constructive approved-source signal.",
        "- The primary sizing-pocket proxy remains source-quality/FV-risk context only, not the actual primary selection.",
        "- The corrected heavy strict replay path is verified and should be trusted over preview rows at the 30-window gate.",
        "- The current loss bottleneck is expensive low-edge parent fills; a parent-shrink repair branch is now frozen separately.",
        "- The broad dual-lane branch currently trails live v28 on the same post-freeze markets, so it is not merely waiting on sample size.",
        "- The strongest current repair shape is a narrow overlay, not a replacement: avoid live-v28 loss clusters without clipping live's large winners.",
        "",
        "## Current Metrics",
        "",
        "| layer | entries | settled | W/L | PnL W/L | coverage | net | recon | cushion |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| sidecar preview | {sidecar.get('entries')} | {sidecar.get('settled')} | "
            f"{sidecar.get('wins')}/{sidecar.get('losses')} | {sidecar.get('pnl_wins')}/{sidecar.get('pnl_losses')} | "
            f"{pct(sidecar.get('coverage_pct'))} | {money(sidecar.get('net_cents'))} | "
            f"{pct(sidecar.get('reconstructed_share'), False)} | {sidecar.get('full_loss_cushion')} |"
        ),
        (
            f"| primary proxy | {primary.get('entries')} | {primary.get('settled')} | "
            f"{primary.get('wins')}/{primary.get('losses')} | {primary.get('pnl_wins')}/{primary.get('pnl_losses')} | "
            f"{pct(primary.get('coverage_pct'))} | {money(primary.get('net_cents'))} | "
            f"{pct(primary.get('reconstructed_share'), False)} | {primary.get('full_loss_cushion')} |"
        ),
        (
            f"| strict precheck `{precheck.get('sidecar_policy')}` | n/a | {precheck.get('settled')} | "
            f"{precheck.get('wins')}/{precheck.get('losses')} | n/a | "
            f"{pct(precheck.get('coverage_pct'))} | {money(precheck.get('net_cents'))} | "
            f"{pct(precheck.get('reconstructed_share'), False)} | {precheck.get('full_loss_cushion')} |"
        ),
        "",
        "## Variant Contrast",
        "",
        f"- Current immature precheck preference: `{'bridge' if contrast.get('bridge_is_current_preferred') else 'entry'}`",
        f"- Bridge minus entry net: `{money(contrast.get('bridge_minus_entry_net_cents'))}`",
        f"- Bridge minus entry coverage: `{pct(contrast.get('bridge_minus_entry_coverage_pct'))}`",
        f"- Precheck/current windows: `{contrast.get('precheck_windows')}` / `{contrast.get('current_windows')}`",
        "",
        "## Loss Bottleneck And Repair",
        "",
        f"- Loss audit tags: `{', '.join(str(item) for item in loss_audit.get('loss_tags') or []) or 'none'}`",
        f"- Original forced-precheck baseline: `{loss_baseline.get('wins')}/{loss_baseline.get('losses')}` / `{money(loss_baseline.get('net_cents'))}`",
        f"- Parent-shrink stress result on diagnostic rows: `{money(shrink_variant.get('net_cents'))}` delta `{money(shrink_variant.get('delta_vs_baseline_cents'))}`",
        f"- Parent-shrink repair freeze: `{parent_state.get('freeze_ts_utc')}` / `{parent_shrink.get('freeze_local_time')}`",
        f"- Parent-shrink windows since freeze / remaining: `{parent_shrink.get('possible_market_windows_since_freeze')}` / `{parent_shrink.get('market_windows_remaining_to_min_sample')}`",
        f"- Parent-shrink best own-freeze row count/net: `{parent_summary.get('settled')}` / `{money(parent_summary.get('net_cents'))}`",
        f"- Frontier freeze: `{frontier_state.get('freeze_ts_utc')}` / `{parent_frontier.get('freeze_local_time')}`",
        f"- Frontier best label/weight: `{frontier_best.get('frontier_label')}` / `{frontier_best.get('frontier_weight')}`",
        f"- Frontier best own-freeze row count/net: `{frontier_summary.get('settled')}` / `{money(frontier_summary.get('net_cents'))}`",
        "",
        "## Same-Window Live Comparison",
        "",
        f"- Candidate policy: `{same_window.get('candidate_policy')}`",
        f"- Candidate W/L/net: `{same_candidate.get('wins')}/{same_candidate.get('losses')}` / `{money(same_candidate.get('net_cents'))}`",
        f"- Live v28 same-market W/L/net: `{same_live.get('wins')}/{same_live.get('losses')}` / `{money(same_live.get('net_cents'))}`",
        f"- Candidate minus live on same markets: `{money(same_window.get('candidate_minus_live_same_markets_cents'))}`",
        "",
        "## Overlay Branches",
        "",
        f"- Overlay split helpful/no-live rows: `{helpful_overlay.get('rows')}` rows, delta `{money(helpful_overlay.get('candidate_minus_live_cents'))}`",
        f"- Overlay split harmful rows: `{harmful_overlay.get('rows')}` rows, delta `{money(harmful_overlay.get('candidate_minus_live_cents'))}`",
        f"- Overlay v1 freeze/rule: `{overlay_filter_state.get('freeze_ts_utc')}` / `{overlay_filter_state.get('overlay_rule')}`",
        f"- Overlay v2 freeze/rule: `{overlay_v2_state.get('freeze_ts_utc')}` / `{overlay_v2_state.get('overlay_rule')}`",
        f"- Overlay v2 current own-freeze selected rows/net: `{overlay_v2_summary.get('settled')}` / `{money(overlay_v2_summary.get('net_cents'))}`",
        f"- Overlay v2 readiness: `{overlay_v2_readiness.get('decision')}` blocked `{', '.join(str(item) for item in overlay_v2_readiness.get('blocked_checks') or [])}`",
        "",
        "## Verified Tooling",
        "",
        f"- Strict replay accounting patch verified: `{accounting.get('accounting_patch_verified')}`",
        f"- Score path read: `{accounting.get('score_path_read')}`",
        f"- Accounting audit UTC: `{accounting.get('generated_at_utc')}`",
        "",
        "## Passed Checks",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.get("passed_checks") or [])
    lines.extend(["", "## Blocked Checks", ""])
    lines.extend(f"- `{item}`" for item in report.get("blocked_checks") or [])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report.get("next_actions") or [])
    lines.extend(
        [
            "",
            "## Checkpoint Command",
            "",
            "```powershell",
            ".\\scripts\\run_v28_dual_lane_30_window_checkpoint.ps1",
            "```",
            "",
            "Optional diagnostic precheck, not promotion evidence before sample maturity:",
            "",
            "```powershell",
            ".\\scripts\\run_v28_dual_lane_30_window_checkpoint.ps1 -RunStrictPrecheck",
            "```",
        ]
    )
    lines.extend(["", "## Key Artifacts", ""])
    for name, path in artifacts.items():
        lines.append(f"- `{name}`: `{path}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
