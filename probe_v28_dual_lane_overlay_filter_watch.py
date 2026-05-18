"""Own-freeze watch for a narrow dual-lane overlay filter.

Research-only; no live bot changes or orders.

The diagnostic overlay frontier found that NO-side, low-recross dual-lane rows
were where the candidate most clearly reduced live-v28 loss clusters without
stealing large live winners. This probe registers that rule from its own freeze
forward. Older rows are diagnostic only and cannot promote the overlay.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_own_freeze_watch as base


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.md"

OVERLAY_SIDE = "no"
OVERLAY_RECROSS_MAX = 0.30
OVERLAY_NAME = "dual_lane_overlay_no_recross_le030"


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


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "dual_lane_overlay_filter_watch",
        "base_candidate": "dual_lane_overlap_union",
        "overlay_rule": {
            "name": OVERLAY_NAME,
            "side": OVERLAY_SIDE,
            "recross_hazard_score_max": OVERLAY_RECROSS_MAX,
            "use": "risk_control_overlay_only",
        },
        "note": (
            "Born after same-window live comparison showed dual-lane is not a "
            "replacement but may reduce live-v28 loss clusters on NO-side low-recross rows."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def force_replay_enabled() -> bool:
    return str(os.environ.get("V28_DUAL_OVERLAY_FILTER_FORCE_REPLAY") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def should_keep(row: dict[str, Any]) -> bool:
    return (
        str(row.get("side") or "") == OVERLAY_SIDE
        and base.fnum(row.get("recross_hazard_score"), math.inf) <= OVERLAY_RECROSS_MAX
    )


def overlay_blockers(summary: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    settled = int(summary.get("settled") or 0)
    net_cents = base.fnum(summary.get("net_cents"))
    recon = summary.get("reconstructed_share")
    recon_f = base.fnum(recon, math.nan) if recon is not None else math.nan
    if settled < base.MIN_SETTLED:
        blockers.append("overlay_selected_settled_lt_30")
    if net_cents <= 0:
        blockers.append("overlay_net_not_positive")
    if int(max(0.0, net_cents) // 100.0) < base.MIN_FULL_LOSS_CUSHION:
        blockers.append("overlay_full_loss_cushion_lt_3")
    if recon is None or not math.isfinite(recon_f):
        blockers.append("overlay_source_share_unknown")
    elif recon_f > base.MAX_RECONSTRUCTED_SHARE:
        blockers.append("overlay_reconstructed_share_gt_35pct")
    elif int(summary.get("source_gate_row_margin") or 0) <= 0:
        blockers.append("overlay_source_gate_zero_row_margin")
    return blockers


def full_union_rows(primary: dict[str, Any], sidecar: dict[str, Any]) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    primary_rows = [row for row in primary.get("rows") or [] if isinstance(row, dict)]
    sidecar_rows = [row for row in sidecar.get("rows") or [] if isinstance(row, dict)]
    primary_by_market = {base.market(row): row for row in primary_rows if base.market(row)}
    sidecar_add_rows = [row for row in sidecar_rows if base.market(row) and base.market(row) not in primary_by_market]
    union_rows = primary_rows + sidecar_add_rows
    denominator = max(
        int(primary.get("denominator") or 0),
        int(sidecar.get("denominator") or 0),
        len({base.market(row) for row in union_rows if base.market(row)}),
    )
    return union_rows, denominator, {
        "primary_rows": len(primary_rows),
        "sidecar_rows": len(sidecar_rows),
        "sidecar_add_rows": len(sidecar_add_rows),
    }


def overlay_lane(label: str, freeze_ts: str, surfaces_fn: Any, live: float) -> dict[str, Any]:
    primary = base.primary_lane(freeze_ts)
    sidecar = base.sidecar_lane(label, freeze_ts, surfaces_fn)
    union_rows, denominator, diagnostics = full_union_rows(primary, sidecar)
    selected = [dict(row, overlay_filter=OVERLAY_NAME) for row in union_rows if should_keep(row)]
    summary = base.summarize(selected, denominator)
    blockers = overlay_blockers(summary)
    return {
        "sidecar_policy": sidecar.get("policy"),
        "overlay_rule": OVERLAY_NAME,
        "summary": summary,
        "blockers": blockers,
        "live_ready": not blockers,
        "strict_forward": True,
        "diagnostics": diagnostics,
        "selected_markets": [row.get("market") for row in selected],
        "rows": sorted(selected, key=base.net)[:30],
    }


def empty_lane(label: str, possible_windows: int, live: float) -> dict[str, Any]:
    summary = base.summarize([], max(1, possible_windows))
    blockers = overlay_blockers(summary)
    return {
        "sidecar_policy": f"{label}_{base.SIDECAR_PENALTY}",
        "overlay_rule": OVERLAY_NAME,
        "summary": summary,
        "blockers": blockers,
        "live_ready": False,
        "strict_forward": True,
        "diagnostics": {
            "pre_sample_short_circuit": True,
            "possible_market_windows_since_freeze": possible_windows,
        },
        "selected_markets": [],
        "rows": [],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live = base.live_cents()
    possible_windows = base.possible_market_windows_since(freeze_ts)
    windows_remaining = max(0, base.MIN_SETTLED - possible_windows)
    force_replay = force_replay_enabled()
    if possible_windows < base.MIN_SETTLED and not force_replay:
        lanes = [
            empty_lane("post_dual_overlay_filter_entry", possible_windows, live),
            empty_lane("post_dual_overlay_filter_bridge", possible_windows, live),
        ]
        pre_sample = True
    else:
        lanes = [
            overlay_lane("post_dual_overlay_filter_entry", freeze_ts, base.entry_surfaces, live),
            overlay_lane("post_dual_overlay_filter_bridge", freeze_ts, base.bridge_surfaces, live),
        ]
        pre_sample = False
    lanes.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -base.fnum((row.get("summary") or {}).get("net_cents"), -999999.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "promotion_use": "not_promotion_evidence_before_min_sample" if force_replay else "own_freeze_only",
        "live_baseline_cents": live,
        "possible_market_windows_since_freeze": possible_windows,
        "market_windows_remaining_to_min_sample": windows_remaining,
        "earliest_min_sample_utc": base.earliest_min_sample_time(freeze_ts),
        "freeze_local_time": base.local_time_iso(freeze_ts),
        "earliest_min_sample_local_time": base.local_time_iso(base.earliest_min_sample_time(freeze_ts)),
        "pre_sample_short_circuit": pre_sample,
        "force_replay": force_replay,
        "lanes": lanes,
        "best_lane": lanes[0] if lanes else {},
        "read": [
            "Research-only own-freeze dual-lane overlay filter; no live bot changes or orders.",
            "This is an overlay-only branch, not a replacement for live v28.",
            "The rule is observable: candidate side must be NO and recross hazard must be <= 0.30.",
            "Rows before this freeze are diagnostic only and cannot promote this branch.",
        ],
    }


def money(value: Any) -> str:
    cents = base.fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{base.fnum(value):.2f}%"


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    state = report.get("state") or {}
    best = report.get("best_lane") if isinstance(report.get("best_lane"), dict) else {}
    best_summary = best.get("summary") if isinstance(best.get("summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Overlay Filter Watch",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC/local: `{state.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Windows since freeze / remaining: `{report.get('possible_market_windows_since_freeze')}` / `{report.get('market_windows_remaining_to_min_sample')}`",
        f"- Earliest 30-window local time: `{report.get('earliest_min_sample_local_time')}`",
        f"- Pre-sample short-circuit: `{report.get('pre_sample_short_circuit')}`",
        f"- Force replay: `{report.get('force_replay')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Best Overlay Lane",
            "",
            f"- Policy: `{best.get('sidecar_policy')}`",
            f"- Settled/W-L: `{best_summary.get('settled')}` / `{best_summary.get('wins')}/{best_summary.get('losses')}`",
            f"- Coverage: `{pct(best_summary.get('coverage_pct'))}`",
            f"- Net: `{money(best_summary.get('net_cents'))}`",
            f"- Recon: `{pct(100.0 * base.fnum(best_summary.get('reconstructed_share')) if best_summary.get('reconstructed_share') is not None else None)}`",
            f"- Cushion: `{best_summary.get('full_loss_cushion')}`",
            f"- Live ready: `{best.get('live_ready')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            "",
            "## All Overlay Lanes",
            "",
            "| rank | policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, lane in enumerate(report.get("lanes") or [], 1):
        if not isinstance(lane, dict):
            continue
        summary = lane.get("summary") if isinstance(lane.get("summary"), dict) else {}
        recon = summary.get("reconstructed_share")
        lines.append(
            f"| {idx} | `{lane.get('sidecar_policy')}` | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {pct(summary.get('coverage_pct'))} | "
            f"{money(summary.get('net_cents'))} | "
            f"{pct(100.0 * base.fnum(recon) if recon is not None else None)} | "
            f"{summary.get('full_loss_cushion')} | `{lane.get('live_ready')}` | "
            f"{', '.join(str(item) for item in lane.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
