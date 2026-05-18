"""Frozen weight frontier for the v28 dual-lane parent-shrink repair.

Research-only; no live bot changes and no orders.

The fixed 50% parent-shrink branch is conservative. This companion watch
freezes several continuous shrink weights at one birth time so forward evidence
can choose among them without retrofitting the weight after seeing outcomes.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_own_freeze_watch as base
import probe_v28_dual_lane_parent_shrink_watch as shrink50


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_parent_shrink_frontier_watch_latest.md"

WEIGHTS = [
    ("shrink25_weight075", 0.75),
    ("shrink50_weight050", 0.50),
    ("shrink75_weight025", 0.25),
]


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
        "candidate_family": "dual_lane_parent_shrink_frontier_watch",
        "base_candidate": "dual_lane_overlap_union",
        "repair_mechanism": "parent_fill_high_cost_low_edge_confidence_shrink",
        "shrink_rule": {
            "ask_prob_min": shrink50.SHRINK_ASK_MIN,
            "raw_edge_max": shrink50.SHRINK_RAW_EDGE_MAX,
            "component": "strict_parent_midprice_hold_fill",
        },
        "weights": [{"label": label, "weight": weight} for label, weight in WEIGHTS],
        "note": (
            "Frozen frontier for continuous confidence shrink strengths. Rows "
            "before this freeze are diagnostic only for this frontier."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def force_replay_enabled() -> bool:
    return str(os.environ.get("V28_DUAL_PARENT_SHRINK_FRONTIER_FORCE_REPLAY") or "").strip().lower() in {
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


def shrink_primary_rows(rows: list[dict[str, Any]], weight: float, label: str) -> list[dict[str, Any]]:
    repaired: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if shrink50.should_shrink(item):
            before = base.net(item)
            after = before * weight
            item["parent_shrink_frontier_label"] = label
            item["parent_shrink_frontier_weight"] = weight
            item["parent_shrink_delta_cents"] = after - before
            for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents"):
                if item.get(field) is not None:
                    item[field] = base.fnum(item.get(field)) * weight
        repaired.append(item)
    return repaired


def repaired_primary(base_primary: dict[str, Any], label: str, weight: float) -> dict[str, Any]:
    rows = [row for row in base_primary.get("rows") or [] if isinstance(row, dict)]
    repaired_rows = shrink_primary_rows(rows, weight, label)
    denominator = int(base_primary.get("denominator") or 0)
    primary = dict(base_primary)
    primary["rows"] = repaired_rows
    primary["summary"] = base.summarize(repaired_rows, denominator)
    primary["policy"] = f"{base_primary.get('policy')}_{label}"
    primary["repair"] = {
        "label": label,
        "weight": weight,
        "shrink_count": sum(1 for row in repaired_rows if row.get("parent_shrink_frontier_label") == label),
        "shrink_net_delta_cents": sum(base.fnum(row.get("parent_shrink_delta_cents")) for row in repaired_rows),
    }
    return primary


def stub_union(label: str, weight: float, sidecar_label: str, denominator: int, live: float, reason: str) -> dict[str, Any]:
    summary = base.summarize([], denominator)
    return {
        "frontier_label": label,
        "frontier_weight": weight,
        "primary": {
            "policy": f"{base.PRIMARY_RULE}_{label}",
            "repair": {"label": label, "weight": weight},
            "summary": summary,
        },
        "sidecar": {
            "policy": f"{sidecar_label}_{base.SIDECAR_PENALTY}",
            "summary": summary,
            "skipped": True,
            "skip_reason": reason,
        },
        "summary": summary,
        "blockers": base.hard_blockers(summary, live),
        "live_ready": False,
        "sidecar_add_net_cents": 0,
        "shared_markets": 0,
        "rows": [],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live = base.live_cents()
    possible_windows = base.possible_market_windows_since(freeze_ts)
    windows_remaining = max(0, base.MIN_SETTLED - possible_windows)
    min_sample_time = base.earliest_min_sample_time(freeze_ts)
    force_replay = force_replay_enabled()

    if possible_windows < base.MIN_SETTLED and not force_replay:
        denominator = max(1, possible_windows)
        reason = f"possible_market_windows_{possible_windows}_lt_{base.MIN_SETTLED}"
        unions = [
            stub_union(label, weight, sidecar_label, denominator, live, reason)
            for label, weight in WEIGHTS
            for sidecar_label in ("post_dual_parent_shrink_frontier_entry", "post_dual_parent_shrink_frontier_bridge")
        ]
    else:
        base_primary = base.primary_lane(freeze_ts)
        sidecars = [
            base.sidecar_lane("post_dual_parent_shrink_frontier_entry", freeze_ts, base.entry_surfaces),
            base.sidecar_lane("post_dual_parent_shrink_frontier_bridge", freeze_ts, base.bridge_surfaces),
        ]
        unions = []
        for label, weight in WEIGHTS:
            primary = repaired_primary(base_primary, label, weight)
            for sidecar in sidecars:
                union = base.union_lane(primary, sidecar, live)
                union["frontier_label"] = label
                union["frontier_weight"] = weight
                unions.append(union)
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
        "pre_sample_short_circuit": possible_windows < base.MIN_SETTLED and not force_replay,
        "force_replay": force_replay,
        "unions": unions,
        "interpretation": [
            "Research-only dual-lane parent-shrink weight frontier; no live bot changes or orders.",
            "All weights share one freeze timestamp so forward evidence can compare shrink strength cleanly.",
            "Do not use pre-freeze diagnostic rows to promote this frontier.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    best = (report.get("unions") or [{}])[0]
    best_summary = best.get("summary") if isinstance(best.get("summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Parent-Shrink Frontier Watch",
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
            "## Best Frontier Union",
            "",
            f"- Label/weight: `{best.get('frontier_label')}` / `{best.get('frontier_weight')}`",
            f"- Settled/W-L: `{best_summary.get('settled')}` / `{best_summary.get('wins')}/{best_summary.get('losses')}`",
            f"- Coverage: `{fmt(best_summary.get('coverage_pct'))}%`",
            f"- Net: `{money(best_summary.get('net_cents'))}`",
            f"- Cushion: `{best_summary.get('full_loss_cushion')}`",
            f"- Live ready: `{best.get('live_ready')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            "",
            "## All Frontier Unions",
            "",
            "| rank | label | weight | sidecar | settled | W/L | coverage | net | recon | cushion | live ready | blockers |",
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, row in enumerate(report.get("unions") or [], 1):
        if not isinstance(row, dict):
            continue
        summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
        sidecar = row.get("sidecar") if isinstance(row.get("sidecar"), dict) else {}
        recon = summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * base.fnum(recon):.2f}%"
        lines.append(
            f"| {idx} | `{row.get('frontier_label')}` | {row.get('frontier_weight')} | "
            f"`{sidecar.get('policy')}` | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))}% | {money(summary.get('net_cents'))} | {recon_text} | "
            f"{summary.get('full_loss_cushion')} | `{row.get('live_ready')}` | "
            f"{', '.join(str(item) for item in row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
