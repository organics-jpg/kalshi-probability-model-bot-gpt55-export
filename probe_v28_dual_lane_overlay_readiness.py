"""Overlay-specific readiness view for the v28 dual-lane workstream.

Research-only; no live bot changes or orders.

This report is deliberately separate from the broad dual-lane readiness
checklist. A risk-control overlay should not be judged by 75-90% replacement
coverage, but it still needs strict frozen rows, positive net, source quality,
full-loss cushion, and evidence that it improves live v28 on the same markets.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
FILTER_FRONTIER_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_frontier_latest.json"
SAME_WINDOW_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OVERLAY_AUDIT_JSON = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.json"
OVERLAY_SAME_WINDOW_JSON = OUT_DIR / "v28_dual_lane_overlay_same_window_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_readiness_latest.md"

MIN_SELECTED_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
MIN_DIAGNOSTIC_ROWS = 3


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def money(value: Any) -> str:
    cents = fnum(value, 0.0)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    number = fnum(value)
    if not math.isfinite(number):
        return "n/a"
    return f"{number:.2f}%"


def gate(ok: bool, evidence: str, blocker: str = "") -> dict[str, Any]:
    return {"status": "pass" if ok else "blocked", "evidence": evidence, "blocker": "" if ok else blocker}


def build_report() -> dict[str, Any]:
    watch = load_json(FILTER_WATCH_JSON)
    frontier = load_json(FILTER_FRONTIER_JSON)
    same_window = load_json(SAME_WINDOW_JSON)
    overlay = load_json(OVERLAY_AUDIT_JSON)
    overlay_same = load_json(OVERLAY_SAME_WINDOW_JSON)

    state = watch.get("state") if isinstance(watch.get("state"), dict) else {}
    best_lane = watch.get("best_lane") if isinstance(watch.get("best_lane"), dict) else {}
    summary = best_lane.get("summary") if isinstance(best_lane.get("summary"), dict) else {}
    best_rule = frontier.get("best_rule") if isinstance(frontier.get("best_rule"), dict) else {}
    best_rule_summary = best_rule.get("summary") if isinstance(best_rule.get("summary"), dict) else {}
    helpful = overlay.get("helpful_overlay_summary") if isinstance(overlay.get("helpful_overlay_summary"), dict) else {}
    harmful = overlay.get("harmful_overlay_summary") if isinstance(overlay.get("harmful_overlay_summary"), dict) else {}

    settled = int(summary.get("settled") or 0)
    net = fnum(summary.get("net_cents"), 0.0)
    recon = summary.get("reconstructed_share")
    recon_f = fnum(recon, math.nan) if recon is not None else math.nan
    cushion = int(summary.get("full_loss_cushion") or 0)
    same_window_delta = fnum(same_window.get("candidate_minus_live_same_markets_cents"), 0.0)
    overlay_same_delta = fnum(overlay_same.get("candidate_minus_live_same_markets_cents"), 0.0)
    overlay_same_candidate = overlay_same.get("candidate_summary") if isinstance(overlay_same.get("candidate_summary"), dict) else {}
    overlay_same_live = overlay_same.get("live_same_selected_markets_summary") if isinstance(overlay_same.get("live_same_selected_markets_summary"), dict) else {}
    diagnostic_delta = fnum(best_rule_summary.get("candidate_minus_live_cents"), 0.0)
    diagnostic_rows = int(best_rule_summary.get("rows") or 0)

    checks = {
        "overlay_filter_frozen": gate(
            bool(state.get("freeze_ts_utc")),
            f"freeze={state.get('freeze_ts_utc')} local={watch.get('freeze_local_time')} rule={state.get('overlay_rule')}",
            "overlay_filter_not_registered",
        ),
        "strict_own_freeze_sample": gate(
            settled >= MIN_SELECTED_SETTLED,
            f"selected_settled={settled}/{MIN_SELECTED_SETTLED}; windows_remaining={watch.get('market_windows_remaining_to_min_sample')}",
            "overlay_waiting_for_30_selected_rows",
        ),
        "positive_selected_net": gate(
            net > 0,
            f"selected_net={money(net)}",
            "overlay_selected_net_not_positive",
        ),
        "selected_source_quality": gate(
            recon is not None and math.isfinite(recon_f) and recon_f <= MAX_RECONSTRUCTED_SHARE,
            f"selected_reconstructed_share={'n/a' if recon is None else pct(100.0 * recon_f)} max={pct(100.0 * MAX_RECONSTRUCTED_SHARE)}",
            "overlay_source_share_unknown_or_gt_35pct",
        ),
        "selected_full_loss_cushion": gate(
            cushion >= MIN_FULL_LOSS_CUSHION,
            f"selected_full_loss_cushion={cushion}/{MIN_FULL_LOSS_CUSHION}",
            "overlay_full_loss_cushion_lt_3",
        ),
        "same_window_parent_candidate_not_replacement": gate(
            bool(same_window) and same_window_delta < 0,
            f"current_union_delta_vs_live={money(same_window_delta)}",
            "same_window_compare_missing_or_not_negative",
        ),
        "diagnostic_filter_shape_positive": gate(
            diagnostic_rows >= MIN_DIAGNOSTIC_ROWS and diagnostic_delta > 0,
            f"best_filter={best_rule.get('label')} rows={diagnostic_rows} diagnostic_delta={money(diagnostic_delta)}",
            "diagnostic_filter_shape_not_positive",
        ),
        "diagnostic_overlay_split_understood": gate(
            fnum(helpful.get("candidate_minus_live_cents"), 0.0) > 0
            and fnum(harmful.get("candidate_minus_live_cents"), 0.0) < 0,
            (
                f"helpful_delta={money(helpful.get('candidate_minus_live_cents'))} "
                f"harmful_delta={money(harmful.get('candidate_minus_live_cents'))}"
            ),
            "overlay_split_not_classified",
        ),
        "selected_same_window_live_edge": gate(
            bool(overlay_same) and int(overlay_same_candidate.get("entries") or 0) > 0 and overlay_same_delta > 0,
            (
                f"selected_candidate_minus_live={money(overlay_same_delta)} "
                f"candidate={money(overlay_same_candidate.get('net_cents'))} "
                f"live_same={money(overlay_same_live.get('net_cents'))} "
                f"selected_markets={len(overlay_same.get('selected_markets') or [])}"
            ),
            "overlay_selected_rows_not_beating_live_same_markets",
        ),
    }
    blocked = [name for name, item in checks.items() if item.get("status") != "pass"]
    return {
        "generated_at_utc": utc_now_iso(),
        "decision": "overlay_live_ready" if not blocked else "not_live_ready",
        "promotion_use": "overlay_own_freeze_required",
        "checks": checks,
        "blocked_checks": blocked,
        "watch": {
            "generated_at_utc": watch.get("generated_at_utc"),
            "freeze_ts_utc": state.get("freeze_ts_utc"),
            "freeze_local_time": watch.get("freeze_local_time"),
            "windows_since_freeze": watch.get("possible_market_windows_since_freeze"),
            "windows_remaining": watch.get("market_windows_remaining_to_min_sample"),
            "earliest_min_sample_local_time": watch.get("earliest_min_sample_local_time"),
            "best_policy": best_lane.get("sidecar_policy"),
            "summary": summary,
        },
        "diagnostic": {
            "frontier_generated_at_utc": frontier.get("generated_at_utc"),
            "best_rule": best_rule.get("label"),
            "best_rule_summary": best_rule_summary,
            "same_window_delta_cents": same_window_delta,
            "overlay_same_window_delta_cents": overlay_same_delta,
            "overlay_same_window_generated_at_utc": overlay_same.get("generated_at_utc"),
        },
        "next_actions": [
            "Keep collecting strict own-freeze overlay rows; do not promote from the diagnostic filter frontier.",
            "At/after the overlay 30-window gate, force replay the overlay watch and compare selected markets against live v28 same-window PnL.",
            "If selected rows remain too sparse, keep it as a diagnostic risk flag rather than a live overlay.",
            "Do not let overlay-specific gates weaken the main broad dual-lane readiness gate.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    watch = report.get("watch") or {}
    summary = watch.get("summary") if isinstance(watch.get("summary"), dict) else {}
    diag = report.get("diagnostic") or {}
    lines = [
        "# v28 Dual-Lane Overlay Readiness",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Overlay freeze UTC/local: `{watch.get('freeze_ts_utc')}` / `{watch.get('freeze_local_time')}`",
        f"- Windows since freeze / remaining: `{watch.get('windows_since_freeze')}` / `{watch.get('windows_remaining')}`",
        f"- Earliest overlay 30-window local time: `{watch.get('earliest_min_sample_local_time')}`",
        f"- Best overlay policy: `{watch.get('best_policy')}`",
        f"- Current selected settled/net/W-L: `{summary.get('settled')}` / `{money(summary.get('net_cents'))}` / `{summary.get('wins')}/{summary.get('losses')}`",
        f"- Diagnostic best filter: `{diag.get('best_rule')}` delta `{money((diag.get('best_rule_summary') or {}).get('candidate_minus_live_cents'))}`",
        "",
        "## Checks",
        "",
        "| check | status | evidence | blocker |",
        "|---|---|---|---|",
    ]
    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}
    for name, item in checks.items():
        if not isinstance(item, dict):
            continue
        lines.append(f"| `{name}` | `{item.get('status')}` | {item.get('evidence')} | {item.get('blocker')} |")
    lines.extend(["", "## Blocked Checks", ""])
    blocked = report.get("blocked_checks") or []
    if blocked:
        lines.extend(f"- `{item}`" for item in blocked)
    else:
        lines.append("- none")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report.get("next_actions") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
