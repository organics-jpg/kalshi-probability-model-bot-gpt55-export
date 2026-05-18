"""Low-edge guard tradeoff for the fixed exit-clock hold frontier.

Research-only; no live bot changes or orders.

The broad fixed-snapshot hold rule finds a large clipped-winner pocket but has
one low-entry-edge false hold. This probe tests whether a raw-edge guard or
continuous low-edge shrink can remove the false hold without giving back the
useful recovery.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SNAPSHOT_JSON = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_clock_low_edge_hold_guard_tradeoff_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clock_low_edge_hold_guard_tradeoff_latest.md"

MIN_SELECTED = 30
MIN_CUSHION = 3


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


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def base_rule(row: dict[str, Any]) -> bool:
    return (
        row.get("exit_fair_drawdown_cents") not in (None, "")
        and row.get("exit_cents") not in (None, "")
        and row.get("entry_ask_cents") not in (None, "")
        and fnum(row.get("exit_fair_drawdown_cents")) <= 5.0
        and fnum(row.get("exit_cents")) >= 50.0
        and fnum(row.get("entry_ask_cents")) <= 80.0
    )


def selected_weight(row: dict[str, Any], raw_edge_floor: float, low_edge_weight: float) -> float:
    if not base_rule(row):
        return 0.0
    raw_edge = fnum(row.get("entry_raw_edge_cents"), -999.0)
    return 1.0 if raw_edge >= raw_edge_floor else low_edge_weight


def summarize(rows: list[dict[str, Any]], raw_edge_floor: float, low_edge_weight: float) -> dict[str, Any]:
    current_net = sum(fnum(row.get("actual_gross_cents")) for row in rows)
    selected = [row for row in rows if selected_weight(row, raw_edge_floor, low_edge_weight) > 0.0]
    candidate_values = []
    weighted_delta = 0.0
    helpful = harmful = flat = 0
    loss_flips = new_losses = 0
    harmful_rows = []
    for row in rows:
        current = fnum(row.get("actual_gross_cents"))
        hold = fnum(row.get("hold_gross_cents"))
        weight = selected_weight(row, raw_edge_floor, low_edge_weight)
        candidate = current + ((hold - current) * weight)
        candidate_values.append(candidate)
        if weight > 0:
            weighted_delta += candidate - current
            if hold > current:
                helpful += 1
            elif hold < current:
                harmful += 1
                harmful_rows.append({**row, "candidate_cents": candidate, "weight": weight, "weighted_delta_cents": candidate - current})
            else:
                flat += 1
            if current < 0 <= candidate:
                loss_flips += 1
            if current >= 0 > candidate:
                new_losses += 1
    candidate_net = sum(candidate_values)
    blockers = ["diagnostic_snapshot_tradeoff", "not_frozen_forward"]
    if len(selected) < MIN_SELECTED:
        blockers.append("selected_decisions_lt_30")
    if weighted_delta <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if new_losses:
        blockers.append("new_losses_created")
    if int(max(0.0, candidate_net) // 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "policy": f"base_exit_hold_raw_edge_ge_{raw_edge_floor:g}_else_weight_{low_edge_weight:g}",
        "raw_edge_floor": raw_edge_floor,
        "low_edge_weight": low_edge_weight,
        "rows": len(rows),
        "selected_rows": len(selected),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": weighted_delta,
        "helpful_rows": helpful,
        "harmful_rows": harmful,
        "flat_rows": flat,
        "loss_flips": loss_flips,
        "new_losses": new_losses,
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "harmful_examples": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "entry_ts": row.get("entry_ts"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "candidate_cents": row.get("candidate_cents"),
                "weighted_delta_cents": row.get("weighted_delta_cents"),
                "weight": row.get("weight"),
                "entry_raw_edge_cents": row.get("entry_raw_edge_cents"),
                "entry_ask_cents": row.get("entry_ask_cents"),
                "exit_cents": row.get("exit_cents"),
                "exit_fair_drawdown_cents": row.get("exit_fair_drawdown_cents"),
                "exit_p_hold": row.get("exit_p_hold"),
            }
            for row in sorted(harmful_rows, key=lambda item: fnum(item.get("weighted_delta_cents")))[:8]
        ],
    }


def build_report() -> dict[str, Any]:
    snapshot = load_json(SNAPSHOT_JSON)
    rows = [
        row for row in snapshot.get("rows") or []
        if isinstance(row, dict)
        and row.get("actual_gross_cents") is not None
        and row.get("hold_gross_cents") is not None
    ]
    floors = [4.0, 5.0, 6.0, 6.5, 7.0, 8.0, 9.0, 10.0, 12.0]
    weights = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 1.0]
    policies = [summarize(rows, floor, weight) for floor in floors for weight in weights]
    policies.sort(
        key=lambda row: (
            int(bool(row.get("harmful_rows"))),
            int(bool(row.get("new_losses"))),
            -fnum(row.get("delta_cents")),
            -fnum(row.get("selected_rows")),
        )
    )
    clean = [row for row in policies if not row.get("harmful_rows") and not row.get("new_losses")]
    clean_sample = [row for row in clean if (row.get("selected_rows") or 0) >= MIN_SELECTED]
    best_clean = clean[0] if clean else {}
    best_clean_sample = clean_sample[0] if clean_sample else {}
    full_broad = next(
        (
            row for row in policies
            if row.get("raw_edge_floor") == 4.0 and row.get("low_edge_weight") == 1.0
        ),
        {},
    )
    blockers = ["research_only", "not_frozen_forward", "diagnostic_snapshot_tradeoff"]
    if not best_clean_sample:
        blockers.append("no_clean_tradeoff_with_30_selected_decisions")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_snapshot": str(SNAPSHOT_JSON),
        "snapshot_generated_at_utc": snapshot.get("generated_at_utc"),
        "base_rule": "exit_fair_drawdown_cents <= 5 and exit_cents >= 50 and entry_ask_cents <= 80",
        "rows": len(rows),
        "policies": policies,
        "best_clean": best_clean,
        "best_clean_sample": best_clean_sample,
        "full_broad_reference": full_broad,
        "blockers": blockers,
        "interpretation": [
            "The broad hold pocket has strong diagnostic recovery but one low-edge false hold.",
            "Raw-edge hard guarding removes the false hold but leaves the rule below the 30-decision floor.",
            "Low-edge fractional shrink still creates a new loss unless the harmful row is effectively excluded, so this is not a clean continuous-sizing candidate yet.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_clean") or {}
    best_sample = report.get("best_clean_sample") or {}
    broad = report.get("full_broad_reference") or {}
    lines = [
        "# v28 Exit-Clock Low-Edge Hold Guard Tradeoff",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Base rule: `{report.get('base_rule')}`",
        f"- Full broad selected/delta/harm: `{broad.get('selected_rows')}` / `{money(broad.get('delta_cents'))}` / `{broad.get('harmful_rows')}`",
        f"- Best clean policy: `{best.get('policy')}`",
        f"- Best clean selected/delta/net: `{best.get('selected_rows')}` / `{money(best.get('delta_cents'))}` / `{money(best.get('candidate_net_cents'))}`",
        f"- Best clean >=30 policy: `{best_sample.get('policy')}`",
        f"- Best clean >=30 selected/delta/net: `{best_sample.get('selected_rows')}` / `{money(best_sample.get('delta_cents'))}` / `{money(best_sample.get('candidate_net_cents'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Policy Frontier",
        "",
        "| policy | selected | delta | net | helpful/harmful/flat | flips/new losses | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in (report.get("policies") or [])[:40]:
        lines.append(
            f"| `{row.get('policy')}` | {row.get('selected_rows')} | {money(row.get('delta_cents'))} | "
            f"{money(row.get('candidate_net_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{row.get('loss_flips')}/{row.get('new_losses')} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
