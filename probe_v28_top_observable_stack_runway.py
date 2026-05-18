"""Runway watch for the current top observable v28 stack.

Research-only; no live bot changes or orders.

This report condenses the promotion blockers for the current top observable
component stack so the shadow loop can show whether it is merely waiting for
settlement or still missing structural gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PARENT_FILL_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
GATE_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
OUT_JSON = OUT_DIR / "v28_top_observable_stack_runway_latest.json"
OUT_MD = OUT_DIR / "v28_top_observable_stack_runway_latest.md"

TOP_POLICY = "diagnostic_observable_mid_confidence_parent_fill_quarter"
POST_POLICY = "post_parent_fill_child_birth_observable_mid_confidence_parent_fill_quarter"
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
MAX_RECONSTRUCTED_SHARE = 0.35
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def find_variant(payload: dict[str, Any], label: str) -> dict[str, Any]:
    for item in payload.get("variants") or []:
        if isinstance(item, dict) and item.get("label") == label:
            return item
    return {}


def build_report() -> dict[str, Any]:
    payload = load_json(PARENT_FILL_JSON)
    gate = load_json(GATE_JSON)
    diagnostic = find_variant(payload, TOP_POLICY)
    strict = find_variant(payload, POST_POLICY)
    strict_diag = payload.get("strict_forward_diagnostics") if isinstance(payload.get("strict_forward_diagnostics"), dict) else {}
    live_baseline = gate.get("live_baseline") if isinstance(gate.get("live_baseline"), dict) else {}
    live_net = fnum(live_baseline.get("net_pnl_cents") or live_baseline.get("net_cents"), 0.0)
    if not live_net and live_baseline.get("net_pnl_total_dollars") is not None:
        live_net = 100.0 * fnum(live_baseline.get("net_pnl_total_dollars"))

    settled = int(fnum(strict.get("settled")))
    net = fnum(strict.get("net_cents"))
    coverage = strict.get("coverage_pct")
    recon = strict.get("reconstructed_share")
    cushion = int(fnum(strict.get("full_loss_cushion")))
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or fnum(coverage) < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and fnum(coverage) > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon is not None and fnum(recon) > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if net <= 0:
        blockers.append("net_not_positive")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if gate.get("decision") != "candidate_live_test_allowed":
        blockers.append("controlled_live_test_gate_not_passed")

    rows_needed = max(0, MIN_SETTLED - settled)
    net_needed_for_live = max(0.0, live_net + 1.0 - net)
    net_needed_for_cushion = max(0.0, 100.0 * MIN_FULL_LOSS_CUSHION - net)
    pending_examples = strict_diag.get("pending_parent_examples") or []
    pending_rows = [
        {
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "raw_edge": row.get("raw_edge"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "ask_prob": row.get("ask_prob"),
            "weight": row.get("weight"),
        }
        for row in pending_examples
        if isinstance(row, dict)
    ]
    settled_examples = [
        {
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "component": row.get("component"),
            "final_weighted_cents": row.get("final_weighted_cents"),
            "raw_edge": row.get("raw_edge"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "ask_prob": row.get("ask_prob"),
            "side_won": row.get("side_won"),
        }
        for row in strict.get("worst_rows") or []
        if isinstance(row, dict)
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "policy": TOP_POLICY,
        "post_policy": POST_POLICY,
        "freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc") if isinstance(payload.get("state"), dict) else None,
        "diagnostic": {
            "settled": diagnostic.get("settled"),
            "wins": diagnostic.get("wins"),
            "losses": diagnostic.get("losses"),
            "coverage_pct": diagnostic.get("coverage_pct"),
            "net_cents": diagnostic.get("net_cents"),
            "reconstructed_share": diagnostic.get("reconstructed_share"),
            "full_loss_cushion": diagnostic.get("full_loss_cushion"),
            "blockers": diagnostic.get("blockers") or [],
        },
        "strict": {
            "settled": settled,
            "wins": strict.get("wins"),
            "losses": strict.get("losses"),
            "coverage_pct": coverage,
            "net_cents": net,
            "reconstructed_share": recon,
            "full_loss_cushion": cushion,
            "rows_needed_for_30": rows_needed,
            "net_cents_needed_to_beat_live": net_needed_for_live,
            "net_cents_needed_for_cushion3": net_needed_for_cushion,
            "blockers": blockers,
        },
        "strict_runway": {
            "future_denominator": strict_diag.get("future_denominator"),
            "future_observation_rows": strict_diag.get("future_observation_rows"),
            "broad_pass_rows": strict_diag.get("broad_pass_rows"),
            "selected_parent_rows": strict_diag.get("selected_parent_rows"),
            "selected_settled_rows": strict_diag.get("selected_settled_rows"),
            "selected_pending_rows": strict_diag.get("selected_pending_rows"),
            "settled_parent_rows_with_exit_clock": strict_diag.get("settled_parent_rows_with_exit_clock"),
            "strict_absd_fill_rows": strict_diag.get("strict_absd_fill_rows"),
            "pending_rows": pending_rows,
            "settled_examples": settled_examples,
        },
        "gate": {
            "decision": gate.get("decision"),
            "open_live_positions": (
                (gate.get("live_baseline") or {}).get("open_positions")
                if isinstance(gate.get("live_baseline"), dict)
                else gate.get("open_live_positions")
            ),
            "live_net_cents": live_net,
            "broad_eligible": len(gate.get("broad_eligible") or []),
            "sidecar_eligible": len(gate.get("sidecar_eligible") or []),
        },
        "interpretation": [
            "Research-only runway watch; no live bot changes or orders.",
            f"Diagnostic top row is {diagnostic.get('net_cents')}c with W/L {diagnostic.get('wins')}/{diagnostic.get('losses')}.",
            f"Strict proof has {settled} settled rows and needs {rows_needed} more to reach the minimum sample gate.",
            "A zero strict score is not failure yet; it means the child has not accumulated settled post-freeze rows.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    diagnostic = report.get("diagnostic") if isinstance(report.get("diagnostic"), dict) else {}
    strict = report.get("strict") if isinstance(report.get("strict"), dict) else {}
    runway = report.get("strict_runway") if isinstance(report.get("strict_runway"), dict) else {}
    gate = report.get("gate") if isinstance(report.get("gate"), dict) else {}
    lines = [
        "# v28 Top Observable Stack Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Gate decision: `{gate.get('decision')}`",
        f"- Open live positions: `{gate.get('open_live_positions')}`",
        f"- Live baseline: `{fmt(gate.get('live_net_cents'))}c`",
        f"- Broad/sidecar eligible: `{gate.get('broad_eligible')}/{gate.get('sidecar_eligible')}`",
        "",
        "## Diagnostic",
        "",
        f"- Settled: `{diagnostic.get('settled')}`",
        f"- W/L: `{diagnostic.get('wins')}/{diagnostic.get('losses')}`",
        f"- Coverage: `{fmt(diagnostic.get('coverage_pct'))}%`",
        f"- Net: `{fmt(diagnostic.get('net_cents'))}c`",
        f"- Reconstructed share: `{fmt(diagnostic.get('reconstructed_share'))}`",
        f"- Full-loss cushion: `{diagnostic.get('full_loss_cushion')}`",
        f"- Blockers: `{', '.join(diagnostic.get('blockers') or [])}`",
        "",
        "## Strict Forward",
        "",
        f"- Settled: `{strict.get('settled')}`",
        f"- W/L: `{strict.get('wins')}/{strict.get('losses')}`",
        f"- Coverage: `{fmt(strict.get('coverage_pct'))}%`",
        f"- Net: `{fmt(strict.get('net_cents'))}c`",
        f"- Rows needed for 30: `{strict.get('rows_needed_for_30')}`",
        f"- Net needed to beat live: `{fmt(strict.get('net_cents_needed_to_beat_live'))}c`",
        f"- Net needed for cushion 3: `{fmt(strict.get('net_cents_needed_for_cushion3'))}c`",
        f"- Full-loss cushion: `{strict.get('full_loss_cushion')}`",
        f"- Blockers: `{', '.join(strict.get('blockers') or [])}`",
        "",
        "## Runway",
        "",
        f"- Future denominator: `{runway.get('future_denominator')}`",
        f"- Future observation rows: `{runway.get('future_observation_rows')}`",
        f"- Broad pass rows: `{runway.get('broad_pass_rows')}`",
        f"- Selected parent rows: `{runway.get('selected_parent_rows')}`",
        f"- Selected pending rows: `{runway.get('selected_pending_rows')}`",
        f"- Settled exit-clock joins: `{runway.get('settled_parent_rows_with_exit_clock')}`",
        "",
        "## Pending Rows",
        "",
        "| market | side | source | raw edge | recross | abs d | ask | weight |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in runway.get("pending_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('weight'))} |"
        )
    lines.extend(
        [
            "",
            "## Settled Strict Rows",
            "",
            "| market | side | source | component | pnl | won | raw edge | recross | abs d | ask |",
            "|---|---|---|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in runway.get("settled_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('component')} | "
            f"{fmt(row.get('final_weighted_cents'))} | {row.get('side_won')} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
