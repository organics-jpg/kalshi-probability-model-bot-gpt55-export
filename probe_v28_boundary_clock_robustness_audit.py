"""Robustness audit for the v28 boundary-clock repair diagnostic.

Research-only; no live bot changes or orders.

The boundary-clock diagnostic found a large retrospective PnL lift. This audit
does not promote it. It asks a narrower anti-overfit question: does the lift
survive obvious stress tests, or is it carried by a tiny number of rows?
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_hazard_repair import RULES, evaluate_rule


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_robustness_audit_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_robustness_audit_latest.md"

RULE = "clock_composite"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def settled_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in (payload.get("removed_rows") or []) + (payload.get("repair_rows") or []):
        if row.get("side_won") is not None:
            out.append(row)
    return out


def pending_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row for row in (payload.get("removed_rows") or []) + (payload.get("repair_rows") or [])
        if row.get("side_won") is None
    ]


def net(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents")) or 0.0)


def adverse_pending_loss(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return -100.0
    return -100.0 * ask - 2.0


def market_rollups(rows: list[dict[str, Any]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for row in rows:
        market = str(row.get("market") or "")
        out[market] = out.get(market, 0.0) + net(row)
    return out


def build_report() -> dict[str, Any]:
    base = evaluate_rule(RULE, RULES[RULE])
    candidate = base.get("candidate_summary") or {}
    removed = base.get("removed_summary") or {}
    repairs = base.get("repair_summary") or {}
    base_delta = float(base.get("delta_vs_target_cents") or 0.0)
    base_net = float(candidate.get("net_cents") or 0.0)
    settled = settled_rows(base)
    pending = pending_rows(base)
    rollups = market_rollups(settled)
    leave_one = []
    for market, contribution in rollups.items():
        # Conservative row-level stress: remove this market's observed net from
        # the candidate headline. This is not a re-optimization; it asks whether
        # the reported lift depends on one observed market.
        leave_one.append({
            "market": market,
            "observed_contribution_cents": contribution,
            "candidate_net_without_market_cents": base_net - contribution,
            "delta_without_market_cents": base_delta - contribution,
        })
    leave_one.sort(key=lambda row: float(row["delta_without_market_cents"]))
    pending_loss = sum(adverse_pending_loss(row) for row in pending)
    adverse_net = base_net + pending_loss
    adverse_delta = base_delta + pending_loss
    return {
        "rule": RULE,
        "purpose": "Stress-test the diagnostic before treating it as a serious frozen candidate.",
        "base": {
            "candidate_entries": candidate.get("entries"),
            "candidate_settled": candidate.get("settled"),
            "candidate_coverage_pct": candidate.get("coverage_pct"),
            "candidate_net_cents": base_net,
            "delta_vs_target_cents": base_delta,
            "removed_net_cents": removed.get("net_cents"),
            "repair_net_cents": repairs.get("net_cents"),
            "pending_rows": len(pending),
        },
        "leave_one_market": leave_one,
        "worst_leave_one": leave_one[0] if leave_one else None,
        "pending_adverse": {
            "pending_rows": pending,
            "assumed_loss_cents": pending_loss,
            "candidate_net_cents": adverse_net,
            "delta_vs_target_cents": adverse_delta,
        },
        "passes_basic_robustness": (
            bool(leave_one)
            and float(leave_one[0]["delta_without_market_cents"]) > 0.0
            and adverse_delta > 0.0
            and int(candidate.get("settled") or 0) >= 20
        ),
        "interpretation": interpretation(base_net, base_delta, leave_one, pending_loss, adverse_delta, candidate),
    }


def interpretation(
    base_net: float,
    base_delta: float,
    leave_one: list[dict[str, Any]],
    pending_loss: float,
    adverse_delta: float,
    candidate: dict[str, Any],
) -> list[str]:
    notes = [
        f"Base diagnostic candidate net is {base_net}c with delta {base_delta}c over {candidate.get('settled')} settled rows.",
    ]
    if leave_one:
        worst = leave_one[0]
        notes.append(
            f"Worst leave-one-market delta is {worst.get('delta_without_market_cents')}c after removing {worst.get('market')}."
        )
    notes.append(
        f"If all pending rows lose at ask-sized loss, pending stress is {pending_loss}c and stressed delta is {adverse_delta}c."
    )
    notes.append("This audit is still diagnostic; promotion still requires frozen future rows.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    base = report.get("base") or {}
    pending = report.get("pending_adverse") or {}
    lines = [
        "# v28 Boundary-Clock Robustness Audit",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Rule: `{report.get('rule')}`",
        f"- Passes basic robustness: `{report.get('passes_basic_robustness')}`",
        f"- Candidate entries/settled/coverage: `{base.get('candidate_entries')}/{base.get('candidate_settled')}/{fmt(base.get('candidate_coverage_pct'))}`",
        f"- Candidate net/delta: `{fmt(base.get('candidate_net_cents'))}/{fmt(base.get('delta_vs_target_cents'))}c`",
        f"- Pending adverse net/delta: `{fmt(pending.get('candidate_net_cents'))}/{fmt(pending.get('delta_vs_target_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Worst Leave-One Markets",
        "",
        "| market | contribution c | candidate net without | delta without |",
        "|---|---:|---:|---:|",
    ])
    for row in (report.get("leave_one_market") or [])[:12]:
        lines.append(
            f"| {row.get('market')} | {fmt(row.get('observed_contribution_cents'))} | "
            f"{fmt(row.get('candidate_net_without_market_cents'))} | {fmt(row.get('delta_without_market_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
