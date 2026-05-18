"""Runway report for the v28 dual-lane live-readiness watch.

Research-only; no live bot changes and no orders.

The live-readiness gate says yes/no. This companion report explains what has
to change before the dual-lane own-freeze candidate can plausibly earn a live
test review.
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
COLLECTION_JSON = OUT_DIR / "v28_dual_lane_freeze_collection_monitor_latest.json"
PREVIEW_JSON = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_readiness_runway_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_readiness_runway_latest.md"


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


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def cents(value: Any) -> str:
    amount = fnum(value)
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def share(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * fnum(value):.2f}%"


def compact_preview(name: str, summary: dict[str, Any]) -> dict[str, Any]:
    entries = int(fnum(summary.get("entries")))
    settled = int(fnum(summary.get("settled")))
    net = fnum(summary.get("net_cents"))
    recon = summary.get("reconstructed_share")
    source_counts = summary.get("source_counts") if isinstance(summary.get("source_counts"), dict) else {}
    return {
        "name": name,
        "entries": entries,
        "settled": settled,
        "wins": int(fnum(summary.get("wins"))),
        "losses": int(fnum(summary.get("losses"))),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": net,
        "avg_net_cents": net / settled if settled else None,
        "reconstructed_share": recon,
        "full_loss_cushion": summary.get("full_loss_cushion"),
        "negative_raw_edge_rows": summary.get("negative_raw_edge_rows"),
        "sidecar_ineligible_rows": summary.get("sidecar_ineligible_rows"),
        "source_counts": source_counts,
        "read": preview_read(entries, settled, net, recon, source_counts),
    }


def preview_read(
    entries: int,
    settled: int,
    net: float,
    recon: Any,
    source_counts: dict[str, Any],
) -> str:
    recon_f = None if recon is None else fnum(recon)
    if entries == 0:
        return "no_post_freeze_preview_rows"
    if recon_f is not None and recon_f > 0.35:
        return "source_quality_risk_preview"
    if settled >= 1 and net <= 0:
        return "pnl_drag_preview"
    if source_counts.get("approved_entry") == entries and net > 0:
        return "clean_approved_positive_preview"
    return "mixed_preview"


def max_reconstructed_allowed(entries: int, max_share: float) -> int:
    return int(math.floor(max_share * entries))


def build_report() -> dict[str, Any]:
    gate = load_json(GATE_JSON)
    collection = load_json(COLLECTION_JSON)
    preview = load_json(PREVIEW_JSON)
    req = gate.get("requirements") if isinstance(gate.get("requirements"), dict) else {}
    clock = gate.get("sample_clock") if isinstance(gate.get("sample_clock"), dict) else {}
    stream = collection.get("shadow_collection") if isinstance(collection.get("shadow_collection"), dict) else {}
    unions = gate.get("unions") if isinstance(gate.get("unions"), list) else []
    best_union = unions[0] if unions and isinstance(unions[0], dict) else {}
    min_settled = int(fnum(req.get("min_settled"), 30))
    min_cushion = int(fnum(req.get("min_full_loss_cushion"), 3))
    max_recon_share = fnum(req.get("max_reconstructed_share"), 0.35)
    live_baseline = fnum(req.get("must_beat_live_baseline_cents"))
    windows_remaining = int(fnum(clock.get("windows_remaining_to_min_sample"), min_settled))
    own_settled = int(fnum(best_union.get("settled")))
    own_net = fnum(best_union.get("net_cents"))
    own_entries_needed = max(0, min_settled - own_settled)
    current_max_reconstructed_at_min_sample = max_reconstructed_allowed(min_settled, max_recon_share)
    current_recon = best_union.get("reconstructed_share")
    own_missing = best_union.get("missing_gates") if isinstance(best_union.get("missing_gates"), list) else []

    sidecar_preview = compact_preview(
        "post-freeze sidecar feature preview",
        preview.get("sidecar_preview_summary") if isinstance(preview.get("sidecar_preview_summary"), dict) else {},
    )
    primary_preview = compact_preview(
        "post-freeze primary sizing-pocket risk proxy",
        preview.get("primary_pocket_preview_summary")
        if isinstance(preview.get("primary_pocket_preview_summary"), dict)
        else {},
    )
    strict_replay_status = "not_due_yet" if windows_remaining > 0 else "due_now_or_running"
    hard_blockers = []
    if windows_remaining > 0:
        hard_blockers.append("waiting_for_30_market_windows")
    if own_settled < min_settled:
        hard_blockers.append("own_freeze_settled_lt_30")
    if own_net <= 0:
        hard_blockers.append("own_freeze_net_not_positive")
    if own_net <= live_baseline:
        hard_blockers.append("own_freeze_does_not_beat_live_baseline")
    if int(max(0.0, own_net) // 100.0) < min_cushion:
        hard_blockers.append("own_freeze_full_loss_cushion_lt_3")
    if current_recon is None:
        hard_blockers.append("own_freeze_source_share_unknown")
    elif fnum(current_recon) > max_recon_share:
        hard_blockers.append("own_freeze_reconstructed_share_gt_35pct")

    return {
        "generated_at_utc": utc_now_iso(),
        "decision": gate.get("decision"),
        "freeze_ts_utc": gate.get("freeze_ts_utc"),
        "freeze_local_time": gate.get("freeze_local_time"),
        "live_baseline_cents": gate.get("live_baseline_cents"),
        "requirements": req,
        "sample_clock": clock,
        "strict_replay_status": strict_replay_status,
        "collection": {
            "post_freeze_events": stream.get("post_freeze_events"),
            "post_freeze_entry_rows": stream.get("post_freeze_entry_rows"),
            "post_freeze_distinct_markets": stream.get("post_freeze_distinct_markets"),
            "settled_post_exit_clock_rows": stream.get("settled_post_exit_clock_rows"),
            "pending_post_exit_clock_rows": stream.get("pending_post_exit_clock_rows"),
        },
        "own_freeze_current": best_union,
        "runway": {
            "windows_remaining_to_min_sample": windows_remaining,
            "own_freeze_entries_needed_to_min_settled": own_entries_needed,
            "min_sample_max_reconstructed_rows": current_max_reconstructed_at_min_sample,
            "net_cents_needed_for_min_cushion": max(0.0, 100.0 * min_cushion - own_net),
            "net_cents_needed_to_beat_live": max(0.0, live_baseline + 1.0 - own_net),
            "current_missing_gates": own_missing,
            "hard_blockers": hard_blockers,
        },
        "preview_lane_reads": [sidecar_preview, primary_preview],
        "interpretation": [
            "This is a runway report, not a live-test approval.",
            "The dedicated dual-lane watch loop is keeping the inputs fresh while the strict own-freeze scorer waits for the sample clock.",
            "The sidecar preview is the constructive signal right now; the primary sizing-pocket proxy is a caution flag, not the actual parent-fill selection.",
            "A live-test review cannot start until the own-freeze promotion score has at least 30 settled strict-forward rows and clears every gate.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    runway = report.get("runway") or {}
    collection = report.get("collection") or {}
    clock = report.get("sample_clock") or {}
    lines = [
        "# v28 Dual-Lane Live-Readiness Runway",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Strict replay status: `{report.get('strict_replay_status')}`",
        f"- Earliest 30-window local time: `{clock.get('earliest_min_sample_local_time')}`",
        "",
        "## Runway",
        "",
        f"- Windows remaining to minimum sample: `{runway.get('windows_remaining_to_min_sample')}`",
        f"- Own-freeze settled rows still needed: `{runway.get('own_freeze_entries_needed_to_min_settled')}`",
        f"- At 30 rows, max reconstructed/rejected rows allowed: `{runway.get('min_sample_max_reconstructed_rows')}`",
        f"- Net needed for full-loss cushion gate: `{cents(runway.get('net_cents_needed_for_min_cushion'))}`",
        f"- Net needed to beat refreshed live baseline: `{cents(runway.get('net_cents_needed_to_beat_live'))}`",
        f"- Hard blockers: `{', '.join(runway.get('hard_blockers') or []) or 'none'}`",
        "",
        "## Collection",
        "",
        f"- Post-freeze events/entries/markets: `{collection.get('post_freeze_events')}` / "
        f"`{collection.get('post_freeze_entry_rows')}` / `{collection.get('post_freeze_distinct_markets')}`",
        f"- Settled/pending exit-clock rows: `{collection.get('settled_post_exit_clock_rows')}` / "
        f"`{collection.get('pending_post_exit_clock_rows')}`",
        "",
        "## Preview Reads",
        "",
        "| preview | entries | settled | W/L | coverage | net | avg settled | recon | neg edge | ineligible | cushion | read |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.get("preview_lane_reads") or []:
        lines.append(
            f"| {row.get('name')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | "
            f"{cents(row.get('net_cents'))} | {cents(row.get('avg_net_cents')) if row.get('avg_net_cents') is not None else 'n/a'} | "
            f"{share(row.get('reconstructed_share'))} | {row.get('negative_raw_edge_rows')} | "
            f"{row.get('sidecar_ineligible_rows')} | {row.get('full_loss_cushion')} | `{row.get('read')}` |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
