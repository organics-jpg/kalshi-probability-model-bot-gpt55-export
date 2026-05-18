"""Own-freeze watch for the dual-lane conflict arbiter.

Research-only; no live bot changes or orders.

The paper coordinator replay showed that the broad dual-lane union is not a
clean replacement for live v28, largely because the bad rows cluster in
high-cost, path-unstable markets where v28 sometimes side-flips or exits better.
This registers the best observable arbiter shape from its own freeze forward:
allow dual-lane rows except when ask_prob >= 0.78 and recross hazard >= 0.30.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_overlay_filter_watch as watch


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_conflict_arbiter_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_conflict_arbiter_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_conflict_arbiter_watch_latest.md"

ARBITER_NAME = "dual_lane_conflict_arbiter_suppress_ask_ge078_recross_ge030"
ASK_SUPPRESS_MIN = 0.78
RECROSS_SUPPRESS_MIN = 0.30


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
        "candidate_family": "dual_lane_conflict_arbiter_watch",
        "base_candidate": "dual_lane_overlap_union",
        "arbiter_rule": {
            "name": ARBITER_NAME,
            "suppress_when": {
                "ask_prob_min": ASK_SUPPRESS_MIN,
                "recross_hazard_score_min": RECROSS_SUPPRESS_MIN,
            },
            "use": "single_process_live_coordinator_conflict_arbiter_candidate",
        },
        "physical_hypothesis": (
            "High ask cost plus elevated recross hazard marks path-unstable rows where "
            "a simple dual-lane entry is likely to need v28-style side-flip or exit-state "
            "management. The arbiter suppresses those rows and keeps the lower-conflict "
            "dual-lane opportunities."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def should_keep(row: dict[str, Any]) -> bool:
    ask = watch.base.fnum(row.get("ask_prob"), -math.inf)
    recross = watch.base.fnum(row.get("recross_hazard_score"), -math.inf)
    return not (ask >= ASK_SUPPRESS_MIN and recross >= RECROSS_SUPPRESS_MIN)


def money(value: Any) -> str:
    cents = watch.base.fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{watch.base.fnum(value):.2f}%"


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    state = report.get("state") or {}
    best = report.get("best_lane") if isinstance(report.get("best_lane"), dict) else {}
    best_summary = best.get("summary") if isinstance(best.get("summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Conflict-Arbiter Watch",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC/local: `{state.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Rule: `suppress ask_prob >= {ASK_SUPPRESS_MIN:.2f} and recross_hazard_score >= {RECROSS_SUPPRESS_MIN:.2f}`",
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
            "## Best Arbiter Lane",
            "",
            f"- Policy: `{best.get('sidecar_policy')}`",
            f"- Settled/W-L: `{best_summary.get('settled')}` / `{best_summary.get('wins')}/{best_summary.get('losses')}`",
            f"- Coverage: `{pct(best_summary.get('coverage_pct'))}`",
            f"- Net: `{money(best_summary.get('net_cents'))}`",
            f"- Recon: `{pct(100.0 * watch.base.fnum(best_summary.get('reconstructed_share')) if best_summary.get('reconstructed_share') is not None else None)}`",
            f"- Cushion: `{best_summary.get('full_loss_cushion')}`",
            f"- Live ready: `{best.get('live_ready')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            "",
            "## All Arbiter Lanes",
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
            f"{pct(100.0 * watch.base.fnum(recon) if recon is not None else None)} | "
            f"{summary.get('full_loss_cushion')} | `{lane.get('live_ready')}` | "
            f"{', '.join(str(item) for item in lane.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    watch.STATE_JSON = STATE_JSON
    watch.OUT_JSON = OUT_JSON
    watch.OUT_MD = OUT_MD
    watch.OVERLAY_NAME = ARBITER_NAME
    watch.OVERLAY_SIDE = ""
    watch.OVERLAY_RECROSS_MAX = RECROSS_SUPPRESS_MIN
    watch.load_or_create_state = load_or_create_state
    watch.should_keep = should_keep
    report = watch.build_report()
    report["read"] = [
        "Research-only own-freeze dual-lane conflict arbiter; no live bot changes or orders.",
        "This is a coordinator arbiter candidate, not a second independent live bot.",
        "The rule is observable before entry: suppress rows with ask_prob >= 0.78 and recross hazard >= 0.30.",
        "Rows before this freeze are diagnostic only and cannot promote this branch.",
    ]
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
