"""Compact live-market update for the v28 dual-lane candidate.

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
COLLECTION_JSON = OUT_DIR / "v28_dual_lane_freeze_collection_monitor_latest.json"
PREVIEW_JSON = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.json"
MECHANISM_JSON = OUT_DIR / "v28_dual_lane_proxy_mechanism_audit_latest.json"
STRICT_PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
VARIANT_CONTRAST_JSON = OUT_DIR / "v28_dual_lane_variant_contrast_latest.json"
LOSS_AUDIT_JSON = OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.json"
PARENT_SHRINK_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.json"
PARENT_SHRINK_FRONTIER_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.json"
SIDECAR_SAFETY_JSON = OUT_DIR / "v28_dual_lane_sidecar_safety_watch_latest.json"
SAME_WINDOW_COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OVERLAY_AUDIT_JSON = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.json"
OVERLAY_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
OVERLAY_READINESS_JSON = OUT_DIR / "v28_dual_lane_overlay_readiness_latest.json"
OVERLAY_SAME_WINDOW_JSON = OUT_DIR / "v28_dual_lane_overlay_same_window_compare_latest.json"
OVERLAY_V2_FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
OVERLAY_V2_READINESS_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_readiness_latest.json"
OVERLAY_V2_SAME_WINDOW_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_same_window_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_market_update_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_market_update_latest.md"


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


def pct(value: Any) -> str:
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return "n/a"
    return f"{amount:.2f}%"


def summary_from_preview(preview: dict[str, Any], key: str) -> dict[str, Any]:
    summary = preview.get(key)
    return summary if isinstance(summary, dict) else {}


def build_report() -> dict[str, Any]:
    gate = load_json(GATE_JSON)
    runway = load_json(RUNWAY_JSON)
    collection = load_json(COLLECTION_JSON)
    preview = load_json(PREVIEW_JSON)
    mechanism = load_json(MECHANISM_JSON)
    strict_precheck = load_json(STRICT_PRECHECK_JSON)
    variant_contrast = load_json(VARIANT_CONTRAST_JSON)
    loss_audit = load_json(LOSS_AUDIT_JSON)
    parent_shrink = load_json(PARENT_SHRINK_JSON)
    parent_shrink_frontier = load_json(PARENT_SHRINK_FRONTIER_JSON)
    sidecar_safety = load_json(SIDECAR_SAFETY_JSON)
    same_window = load_json(SAME_WINDOW_COMPARE_JSON)
    overlay_audit = load_json(OVERLAY_AUDIT_JSON)
    overlay_filter = load_json(OVERLAY_FILTER_WATCH_JSON)
    overlay_readiness = load_json(OVERLAY_READINESS_JSON)
    overlay_same = load_json(OVERLAY_SAME_WINDOW_JSON)
    overlay_v2_filter = load_json(OVERLAY_V2_FILTER_WATCH_JSON)
    overlay_v2_readiness = load_json(OVERLAY_V2_READINESS_JSON)
    overlay_v2_same = load_json(OVERLAY_V2_SAME_WINDOW_JSON)
    gate_clock = gate.get("sample_clock") if isinstance(gate.get("sample_clock"), dict) else {}
    runway_clock = runway.get("sample_clock") if isinstance(runway.get("sample_clock"), dict) else {}
    collection_clock = collection.get("sample_clock") if isinstance(collection.get("sample_clock"), dict) else {}
    gate_collection = gate.get("collection") if isinstance(gate.get("collection"), dict) else {}
    runway_collection = runway.get("collection") if isinstance(runway.get("collection"), dict) else {}
    shadow_collection = (
        collection.get("shadow_collection") if isinstance(collection.get("shadow_collection"), dict) else {}
    )
    runway_section = runway.get("runway") if isinstance(runway.get("runway"), dict) else {}
    sidecar = summary_from_preview(preview, "sidecar_preview_summary")
    primary = summary_from_preview(preview, "primary_pocket_preview_summary")
    return {
        "generated_at_utc": utc_now_iso(),
        "gate_generated_at_utc": gate.get("generated_at_utc"),
        "collection_generated_at_utc": collection.get("generated_at_utc"),
        "preview_generated_at_utc": preview.get("generated_at_utc"),
        "freeze_ts_utc": gate.get("freeze_ts_utc") or preview.get("freeze_ts_utc"),
        "freeze_local_time": gate.get("freeze_local_time") or preview.get("freeze_local_time"),
        "decision": gate.get("decision"),
        "next_action": gate.get("next_action"),
        "live_baseline_cents": gate.get("live_baseline_cents") or preview.get("live_baseline_cents"),
        "possible_windows_since_freeze": gate_clock.get("possible_market_windows_since_freeze")
        or runway_clock.get("possible_market_windows_since_freeze")
        or collection_clock.get("possible_market_windows_since_freeze"),
        "windows_remaining_to_30": gate_clock.get("windows_remaining_to_min_sample")
        or runway_clock.get("windows_remaining_to_min_sample")
        or collection_clock.get("windows_remaining_to_min_sample")
        or runway_section.get("windows_remaining_to_min_sample"),
        "earliest_30_window_local_time": gate_clock.get("earliest_min_sample_local_time")
        or runway_clock.get("earliest_min_sample_local_time")
        or collection_clock.get("earliest_min_sample_local_time"),
        "post_freeze_events": gate_collection.get("post_freeze_events")
        or runway_collection.get("post_freeze_events")
        or shadow_collection.get("post_freeze_events"),
        "post_freeze_entry_rows": gate_collection.get("post_freeze_entry_rows")
        or runway_collection.get("post_freeze_entry_rows")
        or shadow_collection.get("post_freeze_entry_rows"),
        "post_freeze_distinct_markets": preview.get("post_freeze_distinct_markets")
        or gate_collection.get("post_freeze_distinct_markets")
        or runway_collection.get("post_freeze_distinct_markets")
        or shadow_collection.get("post_freeze_distinct_markets"),
        "post_freeze_settled_exit_clock_rows": gate_collection.get("settled_post_exit_clock_rows")
        or runway_collection.get("settled_post_exit_clock_rows")
        or shadow_collection.get("settled_post_exit_clock_rows"),
        "post_freeze_pending_exit_clock_rows": gate_collection.get("pending_post_exit_clock_rows")
        or runway_collection.get("pending_post_exit_clock_rows")
        or shadow_collection.get("pending_post_exit_clock_rows"),
        "sidecar_preview": sidecar,
        "primary_proxy_preview": primary,
        "mechanism_read": mechanism.get("mechanism_read") if isinstance(mechanism.get("mechanism_read"), list) else [],
        "strict_replay_precheck": strict_precheck.get("best_union")
        if isinstance(strict_precheck.get("best_union"), dict)
        else {},
        "strict_replay_precheck_generated_at_utc": strict_precheck.get("generated_at_utc"),
        "strict_replay_precheck_promotion_use": strict_precheck.get("promotion_use"),
        "strict_replay_precheck_windows": strict_precheck.get("possible_market_windows_since_freeze"),
        "variant_contrast": {
            "generated_at_utc": variant_contrast.get("generated_at_utc"),
            "bridge_is_current_preferred": variant_contrast.get("bridge_is_current_preferred"),
            "bridge_minus_entry_net_cents": variant_contrast.get("bridge_minus_entry_net_cents"),
            "bridge_minus_entry_coverage_pct": variant_contrast.get("bridge_minus_entry_coverage_pct"),
        },
        "loss_bottleneck_audit": {
            "generated_at_utc": loss_audit.get("generated_at_utc"),
            "promotion_use": loss_audit.get("promotion_use"),
            "baseline": loss_audit.get("baseline") if isinstance(loss_audit.get("baseline"), dict) else {},
            "loss_tags": loss_audit.get("loss_tags") if isinstance(loss_audit.get("loss_tags"), list) else [],
            "variants": loss_audit.get("variants") if isinstance(loss_audit.get("variants"), list) else [],
            "next_research_action": loss_audit.get("next_research_action"),
        },
        "parent_shrink_watch": {
            "generated_at_utc": parent_shrink.get("generated_at_utc"),
            "promotion_use": parent_shrink.get("promotion_use"),
            "freeze_ts_utc": (parent_shrink.get("state") or {}).get("freeze_ts_utc")
            if isinstance(parent_shrink.get("state"), dict)
            else None,
            "freeze_local_time": parent_shrink.get("freeze_local_time"),
            "possible_market_windows_since_freeze": parent_shrink.get("possible_market_windows_since_freeze"),
            "market_windows_remaining_to_min_sample": parent_shrink.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": parent_shrink.get("earliest_min_sample_local_time"),
            "best_union": (parent_shrink.get("unions") or [{}])[0]
            if isinstance(parent_shrink.get("unions"), list)
            else {},
        },
        "parent_shrink_frontier_watch": {
            "generated_at_utc": parent_shrink_frontier.get("generated_at_utc"),
            "promotion_use": parent_shrink_frontier.get("promotion_use"),
            "freeze_ts_utc": (parent_shrink_frontier.get("state") or {}).get("freeze_ts_utc")
            if isinstance(parent_shrink_frontier.get("state"), dict)
            else None,
            "freeze_local_time": parent_shrink_frontier.get("freeze_local_time"),
            "possible_market_windows_since_freeze": parent_shrink_frontier.get("possible_market_windows_since_freeze"),
            "market_windows_remaining_to_min_sample": parent_shrink_frontier.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": parent_shrink_frontier.get("earliest_min_sample_local_time"),
            "best_union": (parent_shrink_frontier.get("unions") or [{}])[0]
            if isinstance(parent_shrink_frontier.get("unions"), list)
            else {},
        },
        "sidecar_safety_watch": {
            "generated_at_utc": sidecar_safety.get("generated_at_utc"),
            "promotion_use": sidecar_safety.get("promotion_use"),
            "freeze_ts_utc": (sidecar_safety.get("state") or {}).get("freeze_ts_utc")
            if isinstance(sidecar_safety.get("state"), dict)
            else None,
            "freeze_local_time": sidecar_safety.get("freeze_local_time"),
            "possible_market_windows_since_freeze": sidecar_safety.get("possible_market_windows_since_freeze"),
            "market_windows_remaining_to_min_sample": sidecar_safety.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": sidecar_safety.get("earliest_min_sample_local_time"),
            "best_candidate": sidecar_safety.get("best") if isinstance(sidecar_safety.get("best"), dict) else {},
        },
        "same_window_live_compare": {
            "generated_at_utc": same_window.get("generated_at_utc"),
            "promotion_use": same_window.get("promotion_use"),
            "candidate_summary": same_window.get("candidate_summary")
            if isinstance(same_window.get("candidate_summary"), dict)
            else {},
            "live_same_candidate_markets_summary": same_window.get("live_same_candidate_markets_summary")
            if isinstance(same_window.get("live_same_candidate_markets_summary"), dict)
            else {},
            "candidate_minus_live_same_markets_cents": same_window.get("candidate_minus_live_same_markets_cents"),
            "live_post_freeze_trades": same_window.get("live_post_freeze_trades"),
            "live_post_freeze_markets": same_window.get("live_post_freeze_markets"),
        },
        "overlay_opportunity_audit": {
            "generated_at_utc": overlay_audit.get("generated_at_utc"),
            "promotion_use": overlay_audit.get("promotion_use"),
            "same_window_delta_cents": overlay_audit.get("same_window_delta_cents"),
            "helpful_overlay_summary": overlay_audit.get("helpful_overlay_summary")
            if isinstance(overlay_audit.get("helpful_overlay_summary"), dict)
            else {},
            "harmful_overlay_summary": overlay_audit.get("harmful_overlay_summary")
            if isinstance(overlay_audit.get("harmful_overlay_summary"), dict)
            else {},
            "candidate_read": overlay_audit.get("candidate_read")
            if isinstance(overlay_audit.get("candidate_read"), list)
            else [],
        },
        "overlay_filter_watch": {
            "generated_at_utc": overlay_filter.get("generated_at_utc"),
            "promotion_use": overlay_filter.get("promotion_use"),
            "freeze_ts_utc": (overlay_filter.get("state") or {}).get("freeze_ts_utc")
            if isinstance(overlay_filter.get("state"), dict)
            else None,
            "freeze_local_time": overlay_filter.get("freeze_local_time"),
            "possible_market_windows_since_freeze": overlay_filter.get("possible_market_windows_since_freeze"),
            "market_windows_remaining_to_min_sample": overlay_filter.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": overlay_filter.get("earliest_min_sample_local_time"),
            "best_lane": overlay_filter.get("best_lane") if isinstance(overlay_filter.get("best_lane"), dict) else {},
        },
        "overlay_readiness": {
            "generated_at_utc": overlay_readiness.get("generated_at_utc"),
            "decision": overlay_readiness.get("decision"),
            "promotion_use": overlay_readiness.get("promotion_use"),
            "blocked_checks": overlay_readiness.get("blocked_checks")
            if isinstance(overlay_readiness.get("blocked_checks"), list)
            else [],
        },
        "overlay_same_window_compare": {
            "generated_at_utc": overlay_same.get("generated_at_utc"),
            "promotion_use": overlay_same.get("promotion_use"),
            "selected_markets": len(overlay_same.get("selected_markets") or []),
            "candidate_summary": overlay_same.get("candidate_summary")
            if isinstance(overlay_same.get("candidate_summary"), dict)
            else {},
            "live_same_selected_markets_summary": overlay_same.get("live_same_selected_markets_summary")
            if isinstance(overlay_same.get("live_same_selected_markets_summary"), dict)
            else {},
            "candidate_minus_live_same_markets_cents": overlay_same.get("candidate_minus_live_same_markets_cents"),
        },
        "overlay_v2_filter_watch": {
            "generated_at_utc": overlay_v2_filter.get("generated_at_utc"),
            "promotion_use": overlay_v2_filter.get("promotion_use"),
            "freeze_ts_utc": (overlay_v2_filter.get("state") or {}).get("freeze_ts_utc")
            if isinstance(overlay_v2_filter.get("state"), dict)
            else None,
            "freeze_local_time": overlay_v2_filter.get("freeze_local_time"),
            "possible_market_windows_since_freeze": overlay_v2_filter.get("possible_market_windows_since_freeze"),
            "market_windows_remaining_to_min_sample": overlay_v2_filter.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": overlay_v2_filter.get("earliest_min_sample_local_time"),
            "best_lane": overlay_v2_filter.get("best_lane")
            if isinstance(overlay_v2_filter.get("best_lane"), dict)
            else {},
        },
        "overlay_v2_readiness": {
            "generated_at_utc": overlay_v2_readiness.get("generated_at_utc"),
            "decision": overlay_v2_readiness.get("decision"),
            "promotion_use": overlay_v2_readiness.get("promotion_use"),
            "blocked_checks": overlay_v2_readiness.get("blocked_checks")
            if isinstance(overlay_v2_readiness.get("blocked_checks"), list)
            else [],
        },
        "overlay_v2_same_window_compare": {
            "generated_at_utc": overlay_v2_same.get("generated_at_utc"),
            "promotion_use": overlay_v2_same.get("promotion_use"),
            "selected_markets": len(overlay_v2_same.get("selected_markets") or []),
            "candidate_summary": overlay_v2_same.get("candidate_summary")
            if isinstance(overlay_v2_same.get("candidate_summary"), dict)
            else {},
            "live_same_selected_markets_summary": overlay_v2_same.get("live_same_selected_markets_summary")
            if isinstance(overlay_v2_same.get("live_same_selected_markets_summary"), dict)
            else {},
            "candidate_minus_live_same_markets_cents": overlay_v2_same.get("candidate_minus_live_same_markets_cents"),
        },
        "hard_blockers": runway_section.get("hard_blockers")
        if isinstance(runway_section.get("hard_blockers"), list)
        else [],
        "own_freeze_policies": gate.get("unions") if isinstance(gate.get("unions"), list) else [],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    sidecar = report.get("sidecar_preview") if isinstance(report.get("sidecar_preview"), dict) else {}
    primary = report.get("primary_proxy_preview") if isinstance(report.get("primary_proxy_preview"), dict) else {}
    lines = [
        "# v28 Dual-Lane Live Market Update",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Next action: {report.get('next_action')}",
        "",
        "## Incoming-Market Status",
        "",
        f"- Possible windows since freeze: `{report.get('possible_windows_since_freeze')}`",
        f"- Windows remaining to 30-row gate: `{report.get('windows_remaining_to_30')}`",
        f"- Earliest possible 30-window local time: `{report.get('earliest_30_window_local_time')}`",
        f"- Post-freeze events / entry rows / distinct markets: `{report.get('post_freeze_events')}` / `{report.get('post_freeze_entry_rows')}` / `{report.get('post_freeze_distinct_markets')}`",
        f"- Settled / pending exit-clock rows: `{report.get('post_freeze_settled_exit_clock_rows')}` / `{report.get('post_freeze_pending_exit_clock_rows')}`",
        "",
        "## Preview Performance",
        "",
        "| preview | entries | settled | W/L | coverage | net | recon | cushion | source counts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for label, summary in [
        ("sidecar exact observable", sidecar),
        ("primary sizing-pocket risk proxy", primary),
    ]:
        recon = summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.append(
            f"| {label} | {summary.get('entries')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {pct(summary.get('coverage_pct'))} | "
            f"{cents(summary.get('net_cents'))} | {recon_text} | {summary.get('full_loss_cushion')} | "
            f"`{summary.get('source_counts')}` |"
        )
    lines.extend(
        [
            "",
            "## Realized PnL Sign",
            "",
            "| preview | settlement W/L | PnL W/L/flat | note |",
            "|---|---:|---:|---|",
            (
                f"| sidecar exact observable | {sidecar.get('wins')}/{sidecar.get('losses')} | "
                f"{sidecar.get('pnl_wins')}/{sidecar.get('pnl_losses')}/{sidecar.get('pnl_flats')} | "
                "exit PnL can differ from settlement direction |"
            ),
            (
                f"| primary sizing-pocket risk proxy | {primary.get('wins')}/{primary.get('losses')} | "
                f"{primary.get('pnl_wins')}/{primary.get('pnl_losses')}/{primary.get('pnl_flats')} | "
                "risk proxy only, not actual primary selection |"
            ),
        ]
    )
    lines.extend(
        [
            "",
            "## Strict Replay Precheck",
            "",
        ]
    )
    precheck = report.get("strict_replay_precheck") if isinstance(report.get("strict_replay_precheck"), dict) else {}
    if precheck:
        recon = precheck.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.extend(
            [
                f"- Generated UTC: `{report.get('strict_replay_precheck_generated_at_utc')}`",
                f"- Promotion use: `{report.get('strict_replay_precheck_promotion_use')}`",
                f"- Precheck windows / current windows: `{report.get('strict_replay_precheck_windows')}` / `{report.get('possible_windows_since_freeze')}`",
                "",
                "| policy | settled | W/L | coverage | net | recon | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
                (
                    f"| `{precheck.get('sidecar_policy')}` | {precheck.get('settled')} | "
                    f"{precheck.get('wins')}/{precheck.get('losses')} | {pct(precheck.get('coverage_pct'))} | "
                    f"{cents(precheck.get('net_cents'))} | {recon_text} | {precheck.get('full_loss_cushion')} | "
                    f"{', '.join(str(item) for item in precheck.get('blockers') or [])} |"
                ),
            ]
        )
    else:
        lines.append("- No strict replay precheck artifact yet.")
    lines.extend(
        [
            "",
            "## Variant Contrast",
            "",
        ]
    )
    contrast = report.get("variant_contrast") if isinstance(report.get("variant_contrast"), dict) else {}
    if contrast:
        preferred = "bridge" if contrast.get("bridge_is_current_preferred") else "entry"
        lines.extend(
            [
                f"- Generated UTC: `{contrast.get('generated_at_utc')}`",
                f"- Current preferred immature precheck lane: `{preferred}`",
                f"- Bridge minus entry net: `{cents(contrast.get('bridge_minus_entry_net_cents'))}`",
                f"- Bridge minus entry coverage: `{pct(contrast.get('bridge_minus_entry_coverage_pct'))}`",
            ]
        )
    else:
        lines.append("- No variant contrast artifact yet.")
    loss_audit = report.get("loss_bottleneck_audit") if isinstance(report.get("loss_bottleneck_audit"), dict) else {}
    baseline_loss = loss_audit.get("baseline") if isinstance(loss_audit.get("baseline"), dict) else {}
    variants = [row for row in loss_audit.get("variants") or [] if isinstance(row, dict)]
    shrink_variant = next(
        (row for row in variants if row.get("name") == "shrink_high_cost_low_edge_50pct"),
        {},
    )
    lines.extend(
        [
            "",
            "## Loss Bottleneck Audit",
            "",
        ]
    )
    if loss_audit:
        lines.extend(
            [
                f"- Generated UTC: `{loss_audit.get('generated_at_utc')}`",
                f"- Promotion use: `{loss_audit.get('promotion_use')}`",
                f"- Baseline forced-precheck W/L/net: `{baseline_loss.get('wins')}/{baseline_loss.get('losses')}` / `{cents(baseline_loss.get('net_cents'))}`",
                f"- High-cost low-edge shrink stress: `{cents(shrink_variant.get('net_cents'))}` delta `{cents(shrink_variant.get('delta_vs_baseline_cents'))}`",
                f"- Loss tags: `{', '.join(str(item) for item in loss_audit.get('loss_tags') or []) or 'none'}`",
            ]
        )
    else:
        lines.append("- No loss bottleneck audit artifact yet.")
    parent_shrink = report.get("parent_shrink_watch") if isinstance(report.get("parent_shrink_watch"), dict) else {}
    repair_best = parent_shrink.get("best_union") if isinstance(parent_shrink.get("best_union"), dict) else {}
    repair_summary = repair_best.get("summary") if isinstance(repair_best.get("summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Parent-Shrink Repair Watch",
            "",
        ]
    )
    if parent_shrink:
        recon = repair_summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.extend(
            [
                f"- Freeze UTC/local: `{parent_shrink.get('freeze_ts_utc')}` / `{parent_shrink.get('freeze_local_time')}`",
                f"- Promotion use: `{parent_shrink.get('promotion_use')}`",
                f"- Windows since repair freeze / remaining: `{parent_shrink.get('possible_market_windows_since_freeze')}` / `{parent_shrink.get('market_windows_remaining_to_min_sample')}`",
                f"- Earliest repair 30-window local time: `{parent_shrink.get('earliest_min_sample_local_time')}`",
                "",
                "| repair policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|",
                (
                    f"| `{((repair_best.get('sidecar') or {}).get('policy'))}` | {repair_summary.get('settled')} | "
                    f"{repair_summary.get('wins')}/{repair_summary.get('losses')} | {pct(repair_summary.get('coverage_pct'))} | "
                    f"{cents(repair_summary.get('net_cents'))} | {recon_text} | {repair_summary.get('full_loss_cushion')} | "
                    f"`{repair_best.get('live_ready')}` | {', '.join(str(item) for item in repair_best.get('blockers') or [])} |"
                ),
            ]
        )
    else:
        lines.append("- No parent-shrink repair watch artifact yet.")
    parent_frontier = (
        report.get("parent_shrink_frontier_watch")
        if isinstance(report.get("parent_shrink_frontier_watch"), dict)
        else {}
    )
    frontier_best = parent_frontier.get("best_union") if isinstance(parent_frontier.get("best_union"), dict) else {}
    frontier_summary = frontier_best.get("summary") if isinstance(frontier_best.get("summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Parent-Shrink Weight Frontier",
            "",
        ]
    )
    if parent_frontier:
        lines.extend(
            [
                f"- Freeze UTC/local: `{parent_frontier.get('freeze_ts_utc')}` / `{parent_frontier.get('freeze_local_time')}`",
                f"- Windows since frontier freeze / remaining: `{parent_frontier.get('possible_market_windows_since_freeze')}` / `{parent_frontier.get('market_windows_remaining_to_min_sample')}`",
                f"- Earliest frontier 30-window local time: `{parent_frontier.get('earliest_min_sample_local_time')}`",
                f"- Best current label/weight: `{frontier_best.get('frontier_label')}` / `{frontier_best.get('frontier_weight')}`",
                f"- Best current settled/net: `{frontier_summary.get('settled')}` / `{cents(frontier_summary.get('net_cents'))}`",
            ]
        )
    else:
        lines.append("- No parent-shrink frontier artifact yet.")
    sidecar_safety = report.get("sidecar_safety_watch") if isinstance(report.get("sidecar_safety_watch"), dict) else {}
    safety_best = sidecar_safety.get("best_candidate") if isinstance(sidecar_safety.get("best_candidate"), dict) else {}
    safety_lane = safety_best.get("lane") if isinstance(safety_best.get("lane"), dict) else {}
    safety_summary = safety_best.get("summary") if isinstance(safety_best.get("summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Sidecar-Safety Fallback Watch",
            "",
        ]
    )
    if sidecar_safety:
        recon = safety_summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.extend(
            [
                f"- Freeze UTC/local: `{sidecar_safety.get('freeze_ts_utc')}` / `{sidecar_safety.get('freeze_local_time')}`",
                f"- Promotion use: `{sidecar_safety.get('promotion_use')}`",
                f"- Windows since safety freeze / remaining: `{sidecar_safety.get('possible_market_windows_since_freeze')}` / `{sidecar_safety.get('market_windows_remaining_to_min_sample')}`",
                f"- Earliest safety 30-window local time: `{sidecar_safety.get('earliest_min_sample_local_time')}`",
                "",
                "| safety policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|",
                (
                    f"| `{safety_lane.get('policy')}` | {safety_summary.get('settled')} | "
                    f"{safety_summary.get('wins')}/{safety_summary.get('losses')} | {pct(safety_summary.get('coverage_pct'))} | "
                    f"{cents(safety_summary.get('net_cents'))} | {recon_text} | {safety_summary.get('full_loss_cushion')} | "
                    f"`{safety_best.get('live_ready')}` | {', '.join(str(item) for item in safety_best.get('blockers') or [])} |"
                ),
            ]
        )
    else:
        lines.append("- No sidecar-safety fallback artifact yet.")
    same_window = (
        report.get("same_window_live_compare")
        if isinstance(report.get("same_window_live_compare"), dict)
        else {}
    )
    cand_cmp = same_window.get("candidate_summary") if isinstance(same_window.get("candidate_summary"), dict) else {}
    live_cmp = (
        same_window.get("live_same_candidate_markets_summary")
        if isinstance(same_window.get("live_same_candidate_markets_summary"), dict)
        else {}
    )
    lines.extend(
        [
            "",
            "## Same-Window Live Compare",
            "",
        ]
    )
    if same_window:
        lines.extend(
            [
                f"- Generated UTC: `{same_window.get('generated_at_utc')}`",
                f"- Promotion use: `{same_window.get('promotion_use')}`",
                f"- Live post-freeze trades/markets: `{same_window.get('live_post_freeze_trades')}` / `{same_window.get('live_post_freeze_markets')}`",
                f"- Candidate minus live on same markets: `{cents(same_window.get('candidate_minus_live_same_markets_cents'))}`",
                "",
                "| scope | entries/markets | W/L | coverage | net | cushion |",
                "|---|---:|---:|---:|---:|---:|",
                (
                    f"| candidate forced precheck | {cand_cmp.get('entries')} | {cand_cmp.get('wins')}/{cand_cmp.get('losses')} | "
                    f"{pct(cand_cmp.get('coverage_pct'))} | {cents(cand_cmp.get('net_cents'))} | {cand_cmp.get('full_loss_cushion')} |"
                ),
                (
                    f"| live v28 same candidate markets | {live_cmp.get('entries')} | {live_cmp.get('wins')}/{live_cmp.get('losses')} | "
                    f"{pct(live_cmp.get('coverage_pct'))} | {cents(live_cmp.get('net_cents'))} | {live_cmp.get('full_loss_cushion')} |"
                ),
            ]
        )
    else:
        lines.append("- No same-window live comparator artifact yet.")
    overlay = (
        report.get("overlay_opportunity_audit")
        if isinstance(report.get("overlay_opportunity_audit"), dict)
        else {}
    )
    helpful = overlay.get("helpful_overlay_summary") if isinstance(overlay.get("helpful_overlay_summary"), dict) else {}
    harmful = overlay.get("harmful_overlay_summary") if isinstance(overlay.get("harmful_overlay_summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Overlay Opportunity Audit",
            "",
        ]
    )
    if overlay:
        lines.extend(
            [
                f"- Generated UTC: `{overlay.get('generated_at_utc')}`",
                f"- Promotion use: `{overlay.get('promotion_use')}`",
                f"- Current same-window delta: `{cents(overlay.get('same_window_delta_cents'))}`",
                "",
                "| split | rows | candidate net | live net | candidate-live |",
                "|---|---:|---:|---:|---:|",
                (
                    f"| helpful/no-live-pnl buckets | {helpful.get('rows')} | {cents(helpful.get('candidate_net_cents'))} | "
                    f"{cents(helpful.get('live_net_cents'))} | {cents(helpful.get('candidate_minus_live_cents'))} |"
                ),
                (
                    f"| harmful buckets | {harmful.get('rows')} | {cents(harmful.get('candidate_net_cents'))} | "
                    f"{cents(harmful.get('live_net_cents'))} | {cents(harmful.get('candidate_minus_live_cents'))} |"
                ),
            ]
        )
        for item in overlay.get("candidate_read") or []:
            lines.append(f"- {item}")
    else:
        lines.append("- No overlay opportunity audit artifact yet.")
    overlay_filter = (
        report.get("overlay_filter_watch")
        if isinstance(report.get("overlay_filter_watch"), dict)
        else {}
    )
    filter_best = overlay_filter.get("best_lane") if isinstance(overlay_filter.get("best_lane"), dict) else {}
    filter_summary = filter_best.get("summary") if isinstance(filter_best.get("summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Overlay Filter Own-Freeze Watch",
            "",
        ]
    )
    if overlay_filter:
        recon = filter_summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.extend(
            [
                f"- Freeze UTC/local: `{overlay_filter.get('freeze_ts_utc')}` / `{overlay_filter.get('freeze_local_time')}`",
                f"- Promotion use: `{overlay_filter.get('promotion_use')}`",
                f"- Windows since filter freeze / remaining: `{overlay_filter.get('possible_market_windows_since_freeze')}` / `{overlay_filter.get('market_windows_remaining_to_min_sample')}`",
                f"- Earliest filter 30-window local time: `{overlay_filter.get('earliest_min_sample_local_time')}`",
                "",
                "| filter policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|",
                (
                    f"| `{filter_best.get('sidecar_policy')}` | {filter_summary.get('settled')} | "
                    f"{filter_summary.get('wins')}/{filter_summary.get('losses')} | {pct(filter_summary.get('coverage_pct'))} | "
                    f"{cents(filter_summary.get('net_cents'))} | {recon_text} | {filter_summary.get('full_loss_cushion')} | "
                    f"`{filter_best.get('live_ready')}` | {', '.join(str(item) for item in filter_best.get('blockers') or [])} |"
                ),
            ]
        )
    else:
        lines.append("- No overlay filter watch artifact yet.")
    overlay_same = (
        report.get("overlay_same_window_compare")
        if isinstance(report.get("overlay_same_window_compare"), dict)
        else {}
    )
    same_cand = overlay_same.get("candidate_summary") if isinstance(overlay_same.get("candidate_summary"), dict) else {}
    same_live = (
        overlay_same.get("live_same_selected_markets_summary")
        if isinstance(overlay_same.get("live_same_selected_markets_summary"), dict)
        else {}
    )
    lines.extend(
        [
            "",
            "## Overlay Same-Window Compare",
            "",
        ]
    )
    if overlay_same:
        lines.extend(
            [
                f"- Generated UTC: `{overlay_same.get('generated_at_utc')}`",
                f"- Promotion use: `{overlay_same.get('promotion_use')}`",
                f"- Selected markets: `{overlay_same.get('selected_markets')}`",
                f"- Candidate minus live on selected markets: `{cents(overlay_same.get('candidate_minus_live_same_markets_cents'))}`",
                "",
                "| scope | entries/markets | W/L | net | cushion |",
                "|---|---:|---:|---:|---:|",
                f"| overlay selected rows | {same_cand.get('entries')} | {same_cand.get('wins')}/{same_cand.get('losses')} | {cents(same_cand.get('net_cents'))} | {same_cand.get('full_loss_cushion')} |",
                f"| live v28 same selected markets | {same_live.get('entries')} | {same_live.get('wins')}/{same_live.get('losses')} | {cents(same_live.get('net_cents'))} | {same_live.get('full_loss_cushion')} |",
            ]
        )
    else:
        lines.append("- No overlay same-window compare artifact yet.")
    overlay_readiness = (
        report.get("overlay_readiness")
        if isinstance(report.get("overlay_readiness"), dict)
        else {}
    )
    lines.extend(
        [
            "",
            "## Overlay Readiness",
            "",
        ]
    )
    if overlay_readiness:
        blocked = overlay_readiness.get("blocked_checks") or []
        lines.extend(
            [
                f"- Generated UTC: `{overlay_readiness.get('generated_at_utc')}`",
                f"- Decision: `{overlay_readiness.get('decision')}`",
                f"- Promotion use: `{overlay_readiness.get('promotion_use')}`",
                f"- Blocked checks: `{', '.join(str(item) for item in blocked) or 'none'}`",
            ]
        )
    else:
        lines.append("- No overlay readiness artifact yet.")
    overlay_v2_filter = (
        report.get("overlay_v2_filter_watch")
        if isinstance(report.get("overlay_v2_filter_watch"), dict)
        else {}
    )
    v2_best = overlay_v2_filter.get("best_lane") if isinstance(overlay_v2_filter.get("best_lane"), dict) else {}
    v2_summary = v2_best.get("summary") if isinstance(v2_best.get("summary"), dict) else {}
    lines.extend(
        [
            "",
            "## Overlay V2 Filter Own-Freeze Watch",
            "",
        ]
    )
    if overlay_v2_filter:
        recon = v2_summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.extend(
            [
                f"- Freeze UTC/local: `{overlay_v2_filter.get('freeze_ts_utc')}` / `{overlay_v2_filter.get('freeze_local_time')}`",
                f"- Promotion use: `{overlay_v2_filter.get('promotion_use')}`",
                f"- Rule: `raw_edge >= 0.05, recross <= 0.30, abs_d_sigma >= 0.85`",
                f"- Windows since filter freeze / remaining: `{overlay_v2_filter.get('possible_market_windows_since_freeze')}` / `{overlay_v2_filter.get('market_windows_remaining_to_min_sample')}`",
                f"- Earliest filter 30-window local time: `{overlay_v2_filter.get('earliest_min_sample_local_time')}`",
                "",
                "| filter policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|",
                (
                    f"| `{v2_best.get('sidecar_policy')}` | {v2_summary.get('settled')} | "
                    f"{v2_summary.get('wins')}/{v2_summary.get('losses')} | {pct(v2_summary.get('coverage_pct'))} | "
                    f"{cents(v2_summary.get('net_cents'))} | {recon_text} | {v2_summary.get('full_loss_cushion')} | "
                    f"`{v2_best.get('live_ready')}` | {', '.join(str(item) for item in v2_best.get('blockers') or [])} |"
                ),
            ]
        )
    else:
        lines.append("- No overlay v2 filter watch artifact yet.")
    overlay_v2_same = (
        report.get("overlay_v2_same_window_compare")
        if isinstance(report.get("overlay_v2_same_window_compare"), dict)
        else {}
    )
    v2_cand = overlay_v2_same.get("candidate_summary") if isinstance(overlay_v2_same.get("candidate_summary"), dict) else {}
    v2_live = (
        overlay_v2_same.get("live_same_selected_markets_summary")
        if isinstance(overlay_v2_same.get("live_same_selected_markets_summary"), dict)
        else {}
    )
    lines.extend(
        [
            "",
            "## Overlay V2 Same-Window Compare",
            "",
        ]
    )
    if overlay_v2_same:
        lines.extend(
            [
                f"- Generated UTC: `{overlay_v2_same.get('generated_at_utc')}`",
                f"- Promotion use: `{overlay_v2_same.get('promotion_use')}`",
                f"- Selected markets: `{overlay_v2_same.get('selected_markets')}`",
                f"- Candidate minus live on selected markets: `{cents(overlay_v2_same.get('candidate_minus_live_same_markets_cents'))}`",
                "",
                "| scope | entries/markets | W/L | net | cushion |",
                "|---|---:|---:|---:|---:|",
                f"| overlay v2 selected rows | {v2_cand.get('entries')} | {v2_cand.get('wins')}/{v2_cand.get('losses')} | {cents(v2_cand.get('net_cents'))} | {v2_cand.get('full_loss_cushion')} |",
                f"| live v28 same selected markets | {v2_live.get('entries')} | {v2_live.get('wins')}/{v2_live.get('losses')} | {cents(v2_live.get('net_cents'))} | {v2_live.get('full_loss_cushion')} |",
            ]
        )
    else:
        lines.append("- No overlay v2 same-window compare artifact yet.")
    overlay_v2_readiness = (
        report.get("overlay_v2_readiness")
        if isinstance(report.get("overlay_v2_readiness"), dict)
        else {}
    )
    lines.extend(
        [
            "",
            "## Overlay V2 Readiness",
            "",
        ]
    )
    if overlay_v2_readiness:
        blocked = overlay_v2_readiness.get("blocked_checks") or []
        lines.extend(
            [
                f"- Generated UTC: `{overlay_v2_readiness.get('generated_at_utc')}`",
                f"- Decision: `{overlay_v2_readiness.get('decision')}`",
                f"- Promotion use: `{overlay_v2_readiness.get('promotion_use')}`",
                f"- Blocked checks: `{', '.join(str(item) for item in blocked) or 'none'}`",
            ]
        )
    else:
        lines.append("- No overlay v2 readiness artifact yet.")
    lines.extend(
        [
            "",
            "## Mechanism Read",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in report.get("mechanism_read") or [])
    lines.extend(
        [
            "",
            "## Hard Blockers",
            "",
        ]
    )
    blockers = report.get("hard_blockers") or []
    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Own-Freeze Promotion Rows",
            "",
            "| policy | settled | W/L | coverage | net | recon | cushion | live ready | missing gates |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    policies = report.get("own_freeze_policies") or []
    if not policies:
        lines.append("| n/a | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | waiting_for_scorecard |")
    for row in policies:
        if not isinstance(row, dict):
            continue
        recon = row.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * fnum(recon, 0.0):.2f}%"
        lines.append(
            f"| `{row.get('policy') or row.get('label')}` | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | "
            f"{cents(row.get('net_cents'))} | {recon_text} | {row.get('full_loss_cushion')} | "
            f"`{row.get('live_ready')}` | {', '.join(str(item) for item in row.get('missing_gates') or row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
