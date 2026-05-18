"""Frozen watch for cheap-tail size shrinkage on the feature-gate branch.

Research-only; no live bot changes or orders.

The companion cheap-tail audit found that the broad observable feature gate
leans on very cheap selected rows to regain coverage. This watch freezes
observable notional-shrink policies from its own birth timestamp so only future
rows can count toward promotion-style evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    load_or_create_state as load_feature_gate_state,
    market,
    net,
    passes,
    reconstructed_share,
    source,
    source_counts,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_PATH = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_feature_gate_cheap_tail_shrink_watch_latest.md"

BROAD_RULE = "raw03_recross70_abs075"
TARGET_COVERAGE = 0.75
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
POLICIES = [
    "no_shrink_control",
    "cheap_lt10_half",
    "cheap_lt10_quarter",
    "cheap_lt15_half",
    "cheap_lt15_quarter",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "parent_feature_gate_freeze_ts_utc": load_feature_gate_state().get("freeze_ts_utc"),
        "rule": BROAD_RULE,
        "policies": POLICIES,
        "notes": [
            "Research-only frozen watch; no live logic changes.",
            "Selection uses the existing broad feature-gate rule; notional weights use only observable ask_prob.",
            "Source labels are audit-only and remain official blockers when row share is above 35%.",
        ],
    }
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return state


def ask(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def select_by_market(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_market = market(row)
        if not row_market or not passes(row, rule):
            continue
        current = selected.get(row_market)
        if current is None or (raw_edge(row) or -999.0) > (raw_edge(current) or -999.0):
            selected[row_market] = row
    return selected


def policy_weight(row: dict[str, Any], policy: str) -> float:
    row_ask = ask(row)
    if row_ask is None or policy == "no_shrink_control":
        return 1.0
    if policy == "cheap_lt10_half":
        return 0.5 if row_ask < 0.10 else 1.0
    if policy == "cheap_lt10_quarter":
        return 0.25 if row_ask < 0.10 else 1.0
    if policy == "cheap_lt15_half":
        return 0.5 if row_ask < 0.15 else 1.0
    if policy == "cheap_lt15_quarter":
        return 0.25 if row_ask < 0.15 else 1.0
    raise ValueError(f"unknown policy {policy}")


def weighted_reconstructed_share(rows: list[dict[str, Any]], policy: str) -> float | None:
    total = 0.0
    reconstructed = 0.0
    for row in rows:
        weight = policy_weight(row, policy)
        total += weight
        if source(row) != "approved_entry":
            reconstructed += weight
    if total <= 0.0:
        return None
    return reconstructed / total


def row_digest(row: dict[str, Any], policy: str) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "ask_prob": ask(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": as_float(row.get("recross_hazard_score")),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "net_cents": net(row),
        "weight": policy_weight(row, policy),
        "weighted_net_cents": net(row) * policy_weight(row, policy),
    }


def summarize_policy(rows: list[dict[str, Any]], denominator: int, policy: str) -> dict[str, Any]:
    weighted_net = sum(net(row) * policy_weight(row, policy) for row in rows)
    counts = source_counts(rows)
    row_reconstructed_share = reconstructed_share(counts)
    weighted_recon = weighted_reconstructed_share(rows, policy)
    settled = sum(1 for row in rows if row.get("side_won") is not None or net(row) != 0)
    wins = sum(1 for row in rows if net(row) > 0)
    losses = sum(1 for row in rows if net(row) < 0)
    coverage = (len(rows) / denominator * 100.0) if denominator else 0.0
    full_loss_cushion = int(max(0.0, weighted_net) // 100.0)
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < TARGET_COVERAGE * 100.0:
        blockers.append("coverage_too_low")
    if row_reconstructed_share is not None and row_reconstructed_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if weighted_net <= 0.0:
        blockers.append("net_not_positive")
    if full_loss_cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "policy": policy,
        "entries": len(rows),
        "settled": settled,
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "wins": wins,
        "losses": losses,
        "source_counts": counts,
        "row_reconstructed_share": row_reconstructed_share,
        "weighted_reconstructed_share": weighted_recon,
        "total_notional_weight": sum(policy_weight(row, policy) for row in rows),
        "full_loss_cushion_estimate": full_loss_cushion,
        "blockers": blockers,
        "cheap_rows": sum(1 for row in rows if ask(row) is not None and ask(row) < 0.10),
        "cheap_net_cents": sum(net(row) for row in rows if ask(row) is not None and ask(row) < 0.10),
        "examples": [row_digest(row, policy) for row in rows[:12]],
    }


def evaluate_lane(label: str, surfaces_fn: Any, freeze_ts: str) -> dict[str, Any]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    selected = list(select_by_market(rows, RULES[BROAD_RULE]).values())
    policies = [summarize_policy(selected, denominator, policy) for policy in POLICIES]
    policies.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -(float(row.get("coverage_pct") or 0.0)),
            -(float(row.get("weighted_net_cents") or -999999.0)),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "rule": BROAD_RULE,
        "policies": policies,
    }


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a frozen forward watch, not promotion evidence yet.",
        "Rows before this watch freeze are diagnostic only; only post-freeze rows below count for this cheap-tail shrink mechanism.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("policies") or [{}])[0]
        notes.append(
            f"{lane.get('lane')} best policy {best.get('policy')} has {best.get('settled')} settled, "
            f"coverage {best.get('coverage_pct')}%, weighted net {best.get('weighted_net_cents')}c, "
            f"row reconstructed share {best.get('row_reconstructed_share')}, blockers {best.get('blockers')}."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "lanes": [
            evaluate_lane("post_cheap_tail_shrink_birth_entry", entry_surfaces, freeze_ts),
            evaluate_lane("post_cheap_tail_shrink_birth_bridge", bridge_surfaces, freeze_ts),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Feature-Gate Cheap-Tail Shrink Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Parent feature-gate freeze UTC: `{state.get('parent_feature_gate_freeze_ts_utc')}`",
        f"- Rule: `{state.get('rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| rank | policy | entries | settled | coverage | weighted net c | W/L | row recon | weighted recon | weight | cheap rows/net | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, policy in enumerate(lane.get("policies") or [], start=1):
            lines.append(
                f"| {idx} | {policy.get('policy')} | {policy.get('entries')} | {policy.get('settled')} | "
                f"{fmt(policy.get('coverage_pct'))} | {fmt(policy.get('weighted_net_cents'))} | "
                f"{policy.get('wins')}/{policy.get('losses')} | {fmt(policy.get('row_reconstructed_share'))} | "
                f"{fmt(policy.get('weighted_reconstructed_share'))} | {fmt(policy.get('total_notional_weight'))} | "
                f"{policy.get('cheap_rows')}/{fmt(policy.get('cheap_net_cents'))} | "
                f"{policy.get('full_loss_cushion_estimate')} | {', '.join(policy.get('blockers') or []) or 'none'} |"
            )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
