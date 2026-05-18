"""Own-freeze watch for a dual-lane parent-fill shrink repair.

Research-only; no live bot changes and no orders.

This is a pre-registered repair branch derived from the dual-lane loss
bottleneck audit. It keeps the dual-lane overlap structure, then applies a
continuous confidence shrink to expensive low-edge parent fills. Evidence from
before this probe's own freeze is diagnostic only and cannot promote it.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_own_freeze_watch as base


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_parent_shrink_watch_latest.md"

SHRINK_ASK_MIN = 0.78
SHRINK_RAW_EDGE_MAX = 0.09
SHRINK_WEIGHT = 0.50
REPAIR_NAME = "dual_lane_parent_fill_high_cost_low_edge_shrink50"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def local_time_iso(value: str | None) -> str | None:
    parsed = parse_ts(value or "")
    if parsed is None:
        return None
    return parsed.astimezone().isoformat()


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
        "candidate_family": "dual_lane_parent_shrink_watch",
        "repair_name": REPAIR_NAME,
        "base_candidate": "dual_lane_overlap_union",
        "shrink_rule": {
            "ask_prob_min": SHRINK_ASK_MIN,
            "raw_edge_max": SHRINK_RAW_EDGE_MAX,
            "weight": SHRINK_WEIGHT,
            "component": "strict_parent_midprice_hold_fill",
        },
        "note": (
            "Born after the dual-lane loss bottleneck audit found expensive "
            "low-edge parent-fill losses. Rows before this freeze are not "
            "promotion evidence for the repair."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def force_replay_enabled() -> bool:
    return str(os.environ.get("V28_DUAL_PARENT_SHRINK_FORCE_REPLAY") or "").strip().lower() in {"1", "true", "yes", "on"}


def money(value: Any) -> str:
    cents = base.fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def should_shrink(row: dict[str, Any]) -> bool:
    return (
        row.get("component") == "strict_parent_midprice_hold_fill"
        and base.fnum(row.get("ask_prob")) >= SHRINK_ASK_MIN
        and base.fnum(row.get("raw_edge")) < SHRINK_RAW_EDGE_MAX
    )


def shrink_primary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    repaired: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if should_shrink(item):
            before = base.net(item)
            after = before * SHRINK_WEIGHT
            item["parent_shrink_repair"] = REPAIR_NAME
            item["parent_shrink_weight"] = SHRINK_WEIGHT
            item["parent_shrink_delta_cents"] = after - before
            for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents"):
                if item.get(field) is not None:
                    item[field] = base.fnum(item.get(field)) * SHRINK_WEIGHT
            if item.get("raw_net_cents") is not None:
                item["raw_net_cents_before_parent_shrink"] = item.get("raw_net_cents")
        repaired.append(item)
    return repaired


def repaired_primary_lane(freeze_ts: str) -> dict[str, Any]:
    primary = base.primary_lane(freeze_ts)
    rows = [row for row in primary.get("rows") or [] if isinstance(row, dict)]
    repaired_rows = shrink_primary_rows(rows)
    denominator = int(primary.get("denominator") or 0)
    summary = base.summarize(repaired_rows, denominator)
    primary["rows"] = repaired_rows
    primary["summary"] = summary
    primary["repair"] = {
        "name": REPAIR_NAME,
        "shrink_count": sum(1 for row in repaired_rows if row.get("parent_shrink_repair") == REPAIR_NAME),
        "shrink_net_delta_cents": sum(base.fnum(row.get("parent_shrink_delta_cents")) for row in repaired_rows),
        "ask_prob_min": SHRINK_ASK_MIN,
        "raw_edge_max": SHRINK_RAW_EDGE_MAX,
        "weight": SHRINK_WEIGHT,
    }
    return primary


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live = base.live_cents()
    possible_windows = base.possible_market_windows_since(freeze_ts)
    windows_remaining = max(0, base.MIN_SETTLED - possible_windows)
    min_sample_time = base.earliest_min_sample_time(freeze_ts)
    force_replay = force_replay_enabled()

    if possible_windows < base.MIN_SETTLED and not force_replay:
        empty_summary = base.summarize([], max(1, possible_windows))
        unions = []
        for label in ("post_dual_parent_shrink_entry", "post_dual_parent_shrink_bridge"):
            summary = dict(empty_summary)
            blockers = base.hard_blockers(summary, live)
            unions.append(
                {
                    "primary": {
                        "source": "top_component_parent_fill_repair_child",
                        "policy": f"{base.PRIMARY_RULE}_{REPAIR_NAME}",
                        "rule": base.PRIMARY_RULE,
                        "denominator": max(1, possible_windows),
                        "summary": empty_summary,
                        "repair": state.get("shrink_rule"),
                    },
                    "sidecar": {
                        "source": "boundary_clock_feature_gate_continuous_penalty",
                        "policy": f"{label}_{base.SIDECAR_PENALTY}",
                        "denominator": max(1, possible_windows),
                        "summary": empty_summary,
                        "skipped": True,
                        "skip_reason": f"possible_market_windows_{possible_windows}_lt_{base.MIN_SETTLED}",
                    },
                    "summary": summary,
                    "blockers": blockers,
                    "live_ready": False,
                    "rows": [],
                    "sidecar_add_net_cents": 0,
                    "shared_markets": 0,
                }
            )
        return {
            "generated_at_utc": utc_now_iso(),
            "state": state,
            "promotion_use": "own_freeze_only",
            "live_baseline_cents": live,
            "possible_market_windows_since_freeze": possible_windows,
            "market_windows_remaining_to_min_sample": windows_remaining,
            "earliest_min_sample_utc": min_sample_time,
            "freeze_local_time": local_time_iso(freeze_ts),
            "earliest_min_sample_local_time": local_time_iso(min_sample_time),
            "pre_sample_short_circuit": True,
            "force_replay": force_replay,
            "unions": unions,
            "interpretation": [
                "Repair branch is born and collecting, but its own sample is too young for live readiness.",
                "The shrink rule is pre-registered from this freeze forward; older rows are diagnostic only.",
            ],
        }

    primary = repaired_primary_lane(freeze_ts)
    sidecars = [
        base.sidecar_lane("post_dual_parent_shrink_entry", freeze_ts, base.entry_surfaces),
        base.sidecar_lane("post_dual_parent_shrink_bridge", freeze_ts, base.bridge_surfaces),
    ]
    unions = [base.union_lane(primary, sidecar, live) for sidecar in sidecars]
    unions.sort(
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
        "earliest_min_sample_utc": min_sample_time,
        "freeze_local_time": local_time_iso(freeze_ts),
        "earliest_min_sample_local_time": local_time_iso(min_sample_time),
        "pre_sample_short_circuit": False,
        "force_replay": force_replay,
        "primary_repair": primary.get("repair"),
        "unions": unions,
        "interpretation": [
            "Research-only dual-lane parent-shrink watch; no live bot changes or orders.",
            "This branch keeps coverage by shrinking confidence on expensive low-edge parent fills instead of suppressing them.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    best = (report.get("unions") or [{}])[0]
    best_summary = best.get("summary") or {}
    lines = [
        "# v28 Dual-Lane Parent-Shrink Watch",
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
        "## Repair Rule",
        "",
        f"- Name: `{state.get('repair_name')}`",
        f"- Shrink parent-fill rows when `ask_prob >= {SHRINK_ASK_MIN}` and `raw_edge < {SHRINK_RAW_EDGE_MAX}`.",
        f"- Weight: `{SHRINK_WEIGHT}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Best Own-Freeze Repair Union",
            "",
            f"- Settled/W-L: `{best_summary.get('settled')}` / `{best_summary.get('wins')}/{best_summary.get('losses')}`",
            f"- Coverage: `{fmt(best_summary.get('coverage_pct'))}%`",
            f"- Net: `{money(best_summary.get('net_cents'))}`",
            f"- Recon: `{fmt(100.0 * base.fnum(best_summary.get('reconstructed_share')) if best_summary.get('reconstructed_share') is not None else None)}%`",
            f"- Cushion: `{best_summary.get('full_loss_cushion')}`",
            f"- Live ready: `{best.get('live_ready')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            "",
            "## All Repair Unions",
            "",
            "| rank | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | live ready | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, row in enumerate(report.get("unions") or [], 1):
        summary = row.get("summary") or {}
        sidecar = row.get("sidecar") or {}
        lines.append(
            f"| {idx} | `{sidecar.get('policy')}` | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
            f"{money(summary.get('net_cents'))} | "
            f"{fmt(100.0 * base.fnum(summary.get('reconstructed_share')) if summary.get('reconstructed_share') is not None else None)}% | "
            f"{summary.get('full_loss_cushion')} | {money(row.get('sidecar_add_net_cents'))} | "
            f"{row.get('shared_markets')} | `{row.get('live_ready')}` | "
            f"{', '.join(str(item) for item in row.get('blockers') or []) or 'none'} |"
        )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
