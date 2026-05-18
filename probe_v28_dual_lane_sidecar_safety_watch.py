"""Own-freeze watch for a dual-lane sidecar-safety fallback.

Research-only; no live bot changes or orders.

The current dual-lane watch is blocked by parent/proxy damage while the
observable boundary-clock sidecar has a clean live-market shape. This probe
registers a separate freeze for a sidecar-first fallback inside the dual-lane
family, so it can collect strict forward evidence instead of remaining only a
preview.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_own_freeze_watch as base


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_sidecar_safety_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_sidecar_safety_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_sidecar_safety_watch_latest.md"


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
        "candidate_family": "dual_lane_sidecar_safety_watch",
        "base_candidate": "dual_lane_overlap_union",
        "rule": "sidecar_first_until_parent_lane_proves_forward_safety",
        "sidecar_penalty": base.SIDECAR_PENALTY,
        "note": (
            "Born after live-market preview showed approved-source sidecar strength "
            "and parent/proxy damage. This is a dual-lane family fallback, not a "
            "promotion of the original union."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def force_replay_enabled() -> bool:
    return str(os.environ.get("V28_DUAL_SIDECAR_SAFETY_FORCE_REPLAY") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def money(value: Any) -> str:
    cents = base.fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def sidecar_candidates(freeze_ts: str) -> list[dict[str, Any]]:
    lanes = [
        base.sidecar_lane("post_dual_sidecar_safety_entry", freeze_ts, base.entry_surfaces),
        base.sidecar_lane("post_dual_sidecar_safety_bridge", freeze_ts, base.bridge_surfaces),
    ]
    live = base.live_cents()
    out: list[dict[str, Any]] = []
    for lane in lanes:
        summary = lane.get("summary") or {}
        blockers = base.hard_blockers(summary, live)
        out.append(
            {
                "lane": {key: lane.get(key) for key in ("source", "policy", "lane", "denominator")},
                "summary": summary,
                "blockers": blockers,
                "live_ready": not blockers,
                "strict_forward": True,
                "promotion_scope": "dual_lane_sidecar_safety_only",
                "rows": sorted([row for row in lane.get("rows") or [] if isinstance(row, dict)], key=base.net)[:30],
            }
        )
    out.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -base.fnum((row.get("summary") or {}).get("net_cents"), -999999.0),
        )
    )
    return out


def empty_candidates(possible_windows: int, live: float) -> list[dict[str, Any]]:
    denominator = max(1, possible_windows)
    rows = []
    for label in ("post_dual_sidecar_safety_entry", "post_dual_sidecar_safety_bridge"):
        summary = base.summarize([], denominator)
        blockers = base.hard_blockers(summary, live)
        rows.append(
            {
                "lane": {
                    "source": "boundary_clock_feature_gate_continuous_penalty",
                    "policy": f"{label}_{base.SIDECAR_PENALTY}",
                    "lane": label,
                    "denominator": denominator,
                    "skipped": True,
                    "skip_reason": f"possible_market_windows_{possible_windows}_lt_{base.MIN_SETTLED}",
                },
                "summary": summary,
                "blockers": blockers,
                "live_ready": False,
                "strict_forward": True,
                "promotion_scope": "dual_lane_sidecar_safety_only",
                "rows": [],
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live = base.live_cents()
    possible_windows = base.possible_market_windows_since(freeze_ts)
    windows_remaining = max(0, base.MIN_SETTLED - possible_windows)
    min_sample_time = base.earliest_min_sample_time(freeze_ts)
    force_replay = force_replay_enabled()
    if possible_windows < base.MIN_SETTLED and not force_replay:
        candidates = empty_candidates(possible_windows, live)
        pre_sample = True
    else:
        candidates = sidecar_candidates(freeze_ts)
        pre_sample = False
    best = candidates[0] if candidates else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "promotion_use": "not_promotion_evidence_before_min_sample" if force_replay else "own_freeze_only",
        "live_baseline_cents": live,
        "possible_market_windows_since_freeze": possible_windows,
        "market_windows_remaining_to_min_sample": windows_remaining,
        "earliest_min_sample_utc": min_sample_time,
        "freeze_local_time": base.local_time_iso(freeze_ts),
        "earliest_min_sample_local_time": base.local_time_iso(min_sample_time),
        "pre_sample_short_circuit": pre_sample,
        "force_replay": force_replay,
        "readiness_requirements": {
            "min_settled": base.MIN_SETTLED,
            "coverage_min_pct": base.TARGET_COVERAGE_MIN,
            "coverage_max_pct": base.TARGET_COVERAGE_MAX,
            "max_reconstructed_share": base.MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion": base.MIN_FULL_LOSS_CUSHION,
            "must_beat_live_baseline_cents": live,
            "strict_forward_only": True,
        },
        "candidates": candidates,
        "best": best,
        "interpretation": [
            "Research-only dual-lane sidecar-safety watch; no live bot changes or orders.",
            "This branch tests whether the clean observable sidecar can be a deployable fallback while parent-lane repairs mature.",
            "Rows before this freeze are diagnostic only and cannot promote this branch.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    best = report.get("best") or {}
    best_summary = best.get("summary") or {}
    lines = [
        "# v28 Dual-Lane Sidecar-Safety Watch",
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
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Best Sidecar-Safety Lane",
            "",
            f"- Settled/W-L: `{best_summary.get('settled')}` / `{best_summary.get('wins')}/{best_summary.get('losses')}`",
            f"- Coverage: `{fmt(best_summary.get('coverage_pct'))}%`",
            f"- Net: `{money(best_summary.get('net_cents'))}`",
            f"- Recon: `{fmt(100.0 * base.fnum(best_summary.get('reconstructed_share')) if best_summary.get('reconstructed_share') is not None else None)}%`",
            f"- Cushion: `{best_summary.get('full_loss_cushion')}`",
            f"- Live ready: `{best.get('live_ready')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            "",
            "## All Sidecar-Safety Lanes",
            "",
            "| rank | lane | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, row in enumerate(report.get("candidates") or [], 1):
        lane = row.get("lane") or {}
        summary = row.get("summary") or {}
        blockers = ", ".join(str(item) for item in row.get("blockers") or []) or "none"
        recon = summary.get("reconstructed_share")
        lines.append(
            f"| {idx} | `{lane.get('policy')}` | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
            f"{money(summary.get('net_cents'))} | "
            f"{fmt(100.0 * base.fnum(recon) if recon is not None else None)}% | "
            f"{summary.get('full_loss_cushion')} | `{row.get('live_ready')}` | {blockers} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_json(OUT_JSON, report)
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
