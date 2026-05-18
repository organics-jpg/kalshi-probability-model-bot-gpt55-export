"""Frozen exit-guard watch for the v28 feature-gate middle-distance core.

Research-only; no live bot changes or orders.

The middle-core exit attribution found that current-style exits often clipped
settlement winners inside the clean abs-floor core. This probe freezes a small
entry+exit watch: keep the observable middle core, then test existing exit
guard artifacts as hold/suppress overlays. Parent-window rows are diagnostic;
only post-watch-freeze rows are strict forward evidence.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    STATE_JSON as FEATURE_STATE_JSON,
    as_float,
    best_per_market,
    load_json,
    market,
    net,
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge
from probe_v28_feature_gate_near_promotion_exit_attribution import (
    EXIT_SOURCES,
    choose_exit,
    exit_current,
    exit_hold,
    parse_ts,
    side,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_feature_gate_middle_core_exit_guard_watch_state.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_middle_core_exit_guard_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_middle_core_exit_guard_watch_latest.md"

MIN_SETTLED = 30
MIN_CUSHION = 3
MAX_RECON_SHARE = 0.35
MARKET_INTERVAL_MINUTES = 15

VARIANTS = [
    {"name": "entry_hold_or_no_exit_control", "source": None, "suppress_field": None},
    {"name": "book_gap_current_exit_control", "source": "book_gap", "suppress_field": "__never__"},
    {"name": "book_gap_hold_if_suppressed", "source": "book_gap", "suppress_field": "suppressed"},
    {"name": "loss_guard_v1_hold_if_suppressed", "source": "loss_guard_v1", "suppress_field": "suppressed"},
    {"name": "loss_guard_v2_hold_if_suppressed", "source": "loss_guard_v2", "suppress_field": "suppressed"},
    {"name": "loss_guard_v3_hold_if_suppressed", "source": "loss_guard_v3", "suppress_field": "suppressed"},
    {"name": "reduce_hold_if_suppressed", "source": "reduce", "suppress_field": "suppressed"},
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def possible_market_windows_since(freeze_ts: str) -> int:
    parsed = parse_ts(freeze_ts)
    if parsed is None:
        return 0
    elapsed = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
    return int(elapsed // (MARKET_INTERVAL_MINUTES * 60))


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_middle_core_exit_guard_watch",
        "entry_rule": "raw_edge>=0.03, recross<=0.50, abs_d_sigma>=0.75, ask_prob>=0.35",
        "physics": (
            "Middle-distance core rows have strong settlement/hold behavior, but v28-style exits "
            "often clip winners. This watch tests existing exit guard suppression signals on that core."
        ),
        "variants": VARIANTS,
        "promotion_note": (
            "Parent-window rows are diagnostic only. Post-freeze rows must clear sample, source, "
            "PnL, cushion, and controlled live-test gates before any live test."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def live_net_cents() -> float:
    if not LIVE_SUMMARY_JSON.exists():
        return 0.0
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    ask_cents = as_float(row.get("ask_cents"))
    return ask_cents / 100.0 if ask_cents is not None else None


def abs_d(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("abs_d_sigma"))
    return abs(value) if value is not None else None


def pass_abs_floor_core(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    row_abs = abs_d(row)
    ask = ask_prob(row)
    return (
        edge is not None
        and edge >= 0.03
        and row_recross is not None
        and row_recross <= 0.50
        and row_abs is not None
        and row_abs >= 0.75
        and ask is not None
        and ask >= 0.35
    )


def load_exit_index() -> dict[str, dict[tuple[str, str], list[dict[str, Any]]]]:
    output: dict[str, dict[tuple[str, str], list[dict[str, Any]]]] = {}
    for name, path in EXIT_SOURCES.items():
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if isinstance(row, dict):
                grouped[(market(row), side(row))].append(row)
        for rows in grouped.values():
            rows.sort(key=lambda item: parse_ts(item.get("exit_ts") or item.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
        output[name] = grouped
    return output


def selected_entries(freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> tuple[list[dict[str, Any]], int]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    return best_per_market([row for row in rows if pass_abs_floor_core(row)]), int(denominator or 0)


def match_exit(entry: dict[str, Any], source_name: str | None, exits: dict[str, dict[tuple[str, str], list[dict[str, Any]]]]) -> dict[str, Any] | None:
    if not source_name:
        return None
    return choose_exit((exits.get(source_name) or {}).get((market(entry), side(entry))) or [])


def candidate_cents(entry: dict[str, Any], variant: dict[str, Any], exits: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    entry_hold = net(entry)
    source_name = variant.get("source")
    match = match_exit(entry, source_name, exits)
    if match is None or source_name is None:
        return entry_hold, {
            "entry_hold_cents": entry_hold,
            "current_exit_cents": entry_hold,
            "hold_cents": entry_hold,
            "joined_exit": False,
            "suppressed": False,
            "exit_source": source_name,
        }
    current = exit_current(match)
    hold = exit_hold(match)
    if current is None or hold is None:
        return entry_hold, {
            "entry_hold_cents": entry_hold,
            "current_exit_cents": entry_hold,
            "hold_cents": entry_hold,
            "joined_exit": False,
            "suppressed": False,
            "exit_source": source_name,
        }
    suppress_field = str(variant.get("suppress_field") or "")
    suppressed = bool(suppress_field != "__never__" and match.get(suppress_field))
    candidate = hold if suppressed else current
    return candidate, {
        "entry_hold_cents": entry_hold,
        "current_exit_cents": current,
        "hold_cents": hold,
        "joined_exit": True,
        "suppressed": suppressed,
        "exit_source": source_name,
        "exit_reason": match.get("exit_reason"),
        "p_hold": match.get("p_hold"),
        "fair_drawdown_cents": match.get("fair_drawdown_cents"),
        "exit_ts": match.get("exit_ts"),
    }


def source_share(rows: list[dict[str, Any]]) -> float | None:
    counts = Counter(source(row) for row in rows)
    return reconstructed_share(dict(counts))


def evaluate_variant(
    lane: str,
    strict_forward: bool,
    entries: list[dict[str, Any]],
    denominator: int,
    variant: dict[str, Any],
    exits: dict[str, Any],
    live_net: float,
) -> dict[str, Any]:
    scored = []
    for entry in entries:
        cand, detail = candidate_cents(entry, variant, exits)
        scored.append(
            {
                "market": market(entry),
                "side": side(entry),
                "source": source(entry),
                "candidate_cents": cand,
                "entry_hold_cents": detail.get("entry_hold_cents"),
                "current_exit_cents": detail.get("current_exit_cents"),
                "hold_cents": detail.get("hold_cents"),
                "joined_exit": detail.get("joined_exit"),
                "suppressed": detail.get("suppressed"),
                "exit_source": detail.get("exit_source"),
                "exit_reason": detail.get("exit_reason"),
                "p_hold": detail.get("p_hold"),
                "fair_drawdown_cents": detail.get("fair_drawdown_cents"),
                "abs_d_sigma": abs_d(entry),
                "ask_prob": ask_prob(entry),
                "recross_hazard_score": recross(entry),
                "raw_edge": raw_edge(entry),
            }
        )
    settled = scored
    net_cents = sum(fnum(row.get("candidate_cents")) for row in settled)
    entry_hold_net = sum(fnum(row.get("entry_hold_cents")) for row in settled)
    current_exit_net = sum(fnum(row.get("current_exit_cents")) for row in settled)
    coverage = 100.0 * len(entries) / denominator if denominator else None
    share = source_share(entries)
    blockers: list[str] = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if share is not None and share > MAX_RECON_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if net_cents <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net_cents) // 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net_cents <= live_net:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "lane": lane,
        "strict_forward": strict_forward,
        "variant": variant.get("name"),
        "entries": len(entries),
        "settled": len(settled),
        "wins": sum(1 for row in settled if fnum(row.get("candidate_cents")) > 0),
        "losses": sum(1 for row in settled if fnum(row.get("candidate_cents")) < 0),
        "coverage_pct": coverage,
        "source_share": share,
        "source_counts": dict(Counter(source(row) for row in entries)),
        "candidate_net_cents": net_cents,
        "entry_hold_net_cents": entry_hold_net,
        "current_exit_net_cents": current_exit_net,
        "delta_vs_entry_hold_cents": net_cents - entry_hold_net,
        "delta_vs_current_exit_cents": net_cents - current_exit_net,
        "delta_vs_live_cents": net_cents - live_net,
        "joined_exit_rows": sum(1 for row in scored if row.get("joined_exit")),
        "suppressed_rows": sum(1 for row in scored if row.get("suppressed")),
        "full_loss_cushion": int(max(0.0, net_cents) // 100.0),
        "blockers": blockers,
        "live_ready": not blockers,
        "worst_rows": sorted(scored, key=lambda row: fnum(row.get("candidate_cents")))[:10],
    }


def evaluate_lane(
    label: str,
    strict_forward: bool,
    freeze_ts: str,
    surfaces_fn: Callable[[str], Any],
    exits: dict[str, Any],
    live_net: float,
) -> dict[str, Any]:
    entries, denominator = selected_entries(freeze_ts, surfaces_fn)
    variants = [
        evaluate_variant(label, strict_forward, entries, denominator, variant, exits, live_net)
        for variant in VARIANTS
    ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum(row.get("candidate_net_cents")),
            -fnum(row.get("delta_vs_current_exit_cents")),
        )
    )
    return {
        "lane": label,
        "strict_forward": strict_forward,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "entries": len(entries),
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def presample_variant(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane": "post_middle_exit_guard_freeze",
        "strict_forward": True,
        "variant": variant.get("name"),
        "entries": 0,
        "settled": 0,
        "wins": 0,
        "losses": 0,
        "coverage_pct": 0.0,
        "source_share": None,
        "source_counts": {},
        "candidate_net_cents": 0.0,
        "entry_hold_net_cents": 0.0,
        "current_exit_net_cents": 0.0,
        "delta_vs_entry_hold_cents": 0.0,
        "delta_vs_current_exit_cents": 0.0,
        "delta_vs_live_cents": 0.0,
        "joined_exit_rows": 0,
        "suppressed_rows": 0,
        "full_loss_cushion": 0,
        "blockers": ["own_freeze_presample_window_lt_30", "settled_lt_30"],
        "live_ready": False,
        "worst_rows": [],
    }


def presample_lane(label: str, freeze_ts: str) -> dict[str, Any]:
    variants = [presample_variant(variant) for variant in VARIANTS]
    return {
        "lane": label,
        "strict_forward": True,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": 0,
        "entries": 0,
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def interpretation(lanes: list[dict[str, Any]], live_net: float) -> list[str]:
    notes = [
        "Research-only middle-core exit-guard watch; no live bot changes or orders.",
        f"Live baseline for delta math is {live_net:.0f}c.",
    ]
    for lane in lanes:
        best = lane.get("best") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('variant')} has net {best.get('candidate_net_cents')}c, "
            f"W/L {best.get('wins')}/{best.get('losses')}, source share {best.get('source_share')}, "
            f"delta vs current exit {best.get('delta_vs_current_exit_cents')}c, blockers {best.get('blockers')}."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or state["freeze_ts_utc"])
    watch_freeze = str(state["freeze_ts_utc"])
    live_net = live_net_cents()
    possible_windows = possible_market_windows_since(watch_freeze)
    if possible_windows < MIN_SETTLED:
        lanes = [
            presample_lane("post_middle_exit_guard_freeze_entry", watch_freeze),
            presample_lane("post_middle_exit_guard_freeze_bridge", watch_freeze),
        ]
        return {
            "generated_at_utc": utc_now_iso(),
            "feature_gate_freeze_ts_utc": feature_freeze,
            "state": state,
            "live_baseline_cents": live_net,
            "possible_market_windows_since_watch_freeze": possible_windows,
            "pre_sample_short_circuit": True,
            "lanes": lanes,
            "interpretation": [
                "Research-only middle-core exit-guard watch; no live bot changes or orders.",
                f"Own-freeze watch has only {possible_windows} possible 15m windows since birth, so heavy replay was skipped.",
                "This cannot be live-ready until at least 30 post-freeze market windows exist and then clear sample/source/PnL/cushion/live-baseline gates.",
            ],
        }
    exits = load_exit_index()
    lanes = [
        evaluate_lane("diagnostic_feature_window_entry", False, feature_freeze, entry_surfaces, exits, live_net),
        evaluate_lane("diagnostic_feature_window_bridge", False, feature_freeze, bridge_surfaces, exits, live_net),
        evaluate_lane("post_middle_exit_guard_freeze_entry", True, watch_freeze, entry_surfaces, exits, live_net),
        evaluate_lane("post_middle_exit_guard_freeze_bridge", True, watch_freeze, bridge_surfaces, exits, live_net),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_freeze,
        "state": state,
        "live_baseline_cents": live_net,
        "possible_market_windows_since_watch_freeze": possible_windows,
        "pre_sample_short_circuit": False,
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_net),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Middle-Core Exit-Guard Watch",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Feature-gate parent freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Possible 15m windows since watch freeze: `{report.get('possible_market_windows_since_watch_freeze')}`",
        f"- Pre-sample short-circuit: `{report.get('pre_sample_short_circuit')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Entry rows: `{lane.get('entries')}`",
                "",
                "| rank | variant | W/L | coverage | source | candidate | current exit | entry hold | delta current | delta live | joined | suppressed | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], 1):
            blockers = ", ".join(row.get("blockers") or []) or "none"
            lines.append(
                f"| {idx} | `{row.get('variant')}` | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('source_share'))} | "
                f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('current_exit_net_cents'))} | "
                f"{fmt(row.get('entry_hold_net_cents'))} | {fmt(row.get('delta_vs_current_exit_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {row.get('joined_exit_rows')} | "
                f"{row.get('suppressed_rows')} | {row.get('full_loss_cushion')} | {blockers} |"
            )
        best = lane.get("best") or {}
        if best.get("worst_rows"):
            lines.extend(
                [
                    "",
                    "### Worst Rows For Best Variant",
                    "",
                    "| market | side | source | reason | current | hold | candidate | abs d | ask | recross |",
                    "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
                ]
            )
            for row in best.get("worst_rows") or []:
                lines.append(
                    f"| `{row.get('market')}` | {row.get('side')} | {row.get('source')} | "
                    f"{row.get('exit_reason')} | {fmt(row.get('current_exit_cents'))} | "
                    f"{fmt(row.get('hold_cents'))} | {fmt(row.get('candidate_cents'))} | "
                    f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | "
                    f"{fmt(row.get('recross_hazard_score'))} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
