"""Late collapse-recheck rescue for feature-gate size-shrink branch.

Research-only; no live bot changes or orders.

The strict size-shrink branch still trails live after the first 60-second
delayed-recheck rescue. One remaining approved-entry loss is a deep collapse
exit that stayed weak at 60 seconds but recovered strongly around 120 seconds.
This probe freezes a slower collapse-only rescue watch and treats all parent
rows as diagnostic context.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import load_or_create_state as load_feature_gate_state
from probe_v28_feature_gate_size_shrink_delayed_recheck_rescue import (
    BOOK_GAP_JSON,
    LIVE_SUMMARY_JSON,
    REDUCE_JSON,
    build_entries,
    evaluate_variant,
    fnum,
    grouped_exit_rows,
    load_json,
    read_heartbeats,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_late_collapse_recheck_rescue_state.json"

POLICY = "repair_low_absd_quarter_else_half"

VARIANTS = [
    {"name": "base_no_exit_overlay", "mode": "none"},
    {
        "name": "combo_high60_or_late_collapse90",
        "mode": "combo",
        "delay_seconds": 90,
        "high_bid_floor": 60,
        "high_max_drop": 10,
        "collapse_exit_bid_max": 25,
        "collapse_recheck_bid_floor": 25,
        "collapse_rebound_min": 8,
        "collapse_max_drop": 15,
    },
    {
        "name": "combo_high60_or_late_collapse120",
        "mode": "combo",
        "delay_seconds": 120,
        "high_bid_floor": 60,
        "high_max_drop": 10,
        "collapse_exit_bid_max": 25,
        "collapse_recheck_bid_floor": 45,
        "collapse_rebound_min": 25,
        "collapse_max_drop": 15,
    },
    {
        "name": "late_collapse_delay90_exit25_recheck25_rebound8_drop15",
        "mode": "collapse",
        "delay_seconds": 90,
        "collapse_exit_bid_max": 25,
        "collapse_recheck_bid_floor": 25,
        "collapse_rebound_min": 8,
        "collapse_max_drop": 15,
    },
    {
        "name": "late_collapse_delay120_exit25_recheck45_rebound25_drop15",
        "mode": "collapse",
        "delay_seconds": 120,
        "collapse_exit_bid_max": 25,
        "collapse_recheck_bid_floor": 45,
        "collapse_rebound_min": 25,
        "collapse_max_drop": 15,
    },
    {
        "name": "late_collapse_delay150_exit25_recheck55_rebound30_drop15",
        "mode": "collapse",
        "delay_seconds": 150,
        "collapse_exit_bid_max": 25,
        "collapse_recheck_bid_floor": 55,
        "collapse_rebound_min": 30,
        "collapse_max_drop": 15,
    },
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    existing = load_json(STATE_JSON)
    if existing:
        if "variant_set_freeze_ts_utc" not in existing:
            existing["variant_set_freeze_ts_utc"] = utc_now_iso()
            existing["variant_set_note"] = "Updated after adding high-bid plus late-collapse combo variants; this timestamp is used for strict post-variant evidence."
            STATE_JSON.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return existing
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "variant_set_freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_late_collapse_recheck_rescue",
        "parent_policy": POLICY,
        "note": "Freeze created after diagnostic late collapse-recovery inspection; post-birth rows are the only strict-forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def evaluate_lane(label: str, strict_forward: bool, freeze_ts: str) -> dict[str, Any]:
    entries, anchor_keys, denominator = build_entries(freeze_ts)
    book_rows = grouped_exit_rows(BOOK_GAP_JSON)
    reduce_rows = grouped_exit_rows(REDUCE_JSON)
    heartbeats = read_heartbeats()
    live_cents = 100.0 * float(fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars")) or 0.0)
    variants = [
        evaluate_variant(
            variant,
            entries,
            anchor_keys,
            denominator,
            book_rows,
            reduce_rows,
            heartbeats,
            live_cents,
            label,
            strict_forward,
        )
        for variant in VARIANTS
    ]
    for row in variants:
        row["blockers"] = [
            "late_" + blocker if blocker == "rescue_overlay_not_independently_frozen" else blocker
            for blocker in (row.get("blockers") or [])
        ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("candidate_net_cents") or -999999.0),
            -float(row.get("delta_vs_current_exit_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "strict_forward": strict_forward,
        "freeze_ts_utc": freeze_ts,
        "denominator": denominator,
        "entry_rows": len(entries),
        "variants": variants,
        "best": variants[0] if variants else {},
    }


def build_report() -> dict[str, Any]:
    feature_state = load_feature_gate_state()
    state = load_or_create_state()
    diagnostic = evaluate_lane("diagnostic_prefreeze_context", False, str(feature_state["freeze_ts_utc"]))
    post = evaluate_lane("post_late_collapse_rescue_birth", True, str(state.get("variant_set_freeze_ts_utc") or state["freeze_ts_utc"]))
    best = diagnostic.get("best") or {}
    post_best = post.get("best") or {}
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_state.get("freeze_ts_utc"),
        "state": state,
        "policy": POLICY,
        "lanes": [diagnostic, post],
        "variants": diagnostic.get("variants") or [],
        "interpretation": [
            "Research-only late collapse-recheck rescue; no live bot changes or orders.",
            (
                f"Diagnostic best {((best.get('variant') or {}).get('name'))} has net {best.get('candidate_net_cents')}c, "
                f"delta vs current exits {best.get('delta_vs_current_exit_cents')}c, W/L {best.get('wins')}/{best.get('losses')}, "
                f"suppressed {best.get('suppressed_rows')}, blockers {best.get('blockers')}."
            ) if best else "No diagnostic variants scored.",
            (
                f"Post-birth best {((post_best.get('variant') or {}).get('name'))} has {post_best.get('settled')} rows and net "
                f"{post_best.get('candidate_net_cents')}c."
            ) if post_best else "No post-birth variants scored.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Late Collapse Recheck Rescue",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Late rescue freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Variant-set freeze UTC: `{(report.get('state') or {}).get('variant_set_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Variants",
        "",
        "| rank | variant | W/L | coverage | source | candidate | delta current | delta live | suppressed | H/H | adverse >=10/25 | worst adverse | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("variants") or [], start=1):
        variant = row.get("variant") or {}
        lines.append(
            f"| {idx} | `{variant.get('name')}` | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('reconstructed_share'))} | "
            f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('delta_vs_current_exit_cents'))} | "
            f"{fmt(row.get('delta_vs_live_cents'))} | {row.get('suppressed_rows')} | "
            f"{row.get('helpful_suppressed')}/{row.get('harmful_suppressed')} | "
            f"{row.get('suppressed_post_recheck_adverse_ge_10')}/{row.get('suppressed_post_recheck_adverse_ge_25')} | "
            f"{fmt(row.get('worst_suppressed_post_recheck_adverse_cents'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
