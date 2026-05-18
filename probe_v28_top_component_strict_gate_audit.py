"""Strict gate audit for the v28 top-component portfolio branch.

Research-only. This consolidates existing top-component reports into one
promotion/readiness view and does not change live bot logic or order behavior.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_top_component_strict_gate_audit_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_strict_gate_audit_latest.md"

MIX = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
PARENT_FILL_CHILD = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
LOSS_DRILLDOWN = OUT_DIR / "v28_top_component_loss_cluster_drilldown_latest.json"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def live_net_cents() -> float:
    live = load_json(LIVE_SUMMARY)
    try:
        return round(float(live.get("net_pnl_total_dollars") or 0.0) * 100.0, 6)
    except (TypeError, ValueError):
        return 0.0


def fmt_cents(value: Any) -> str:
    try:
        return f"{float(value):.0f}c"
    except (TypeError, ValueError):
        return ""


def fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return ""


def wl(row: dict[str, Any]) -> str:
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}"


def row_blockers(row: dict[str, Any], live_cents: float, require_exit_join: bool = False) -> list[str]:
    blockers = set(str(item) for item in row.get("blockers") or [])

    settled = int(row.get("settled") or row.get("entries") or 0)
    coverage = float(row.get("coverage_pct") or 0.0)
    net = float(row.get("net_cents") or 0.0)
    recon = row.get("reconstructed_share")
    recon_value = float(recon) if recon is not None else 1.0
    cushion = int(row.get("full_loss_cushion") or 0)
    delta_value = net - live_cents

    if settled < 30:
        blockers.add("settled_lt_30")
    if coverage < 75.0:
        blockers.add("coverage_too_low")
    if net <= 0:
        blockers.add("net_not_positive")
    if recon_value > 0.35:
        blockers.add("row_reconstructed_share_gt_35pct")
    if cushion < 3:
        blockers.add("full_loss_cushion_lt_3")
    if delta_value <= 0:
        blockers.add("does_not_beat_refreshed_live_baseline")
    if require_exit_join:
        counts = row.get("component_counts") if isinstance(row.get("component_counts"), dict) else {}
        exit_rows = sum(
            int(value or 0)
            for key, value in counts.items()
            if "exit" in str(key) or "rescue" in str(key)
        )
        if exit_rows <= 0:
            blockers.add("exit_clock_join_missing")

    return sorted(blockers)


def summarize_variant(row: dict[str, Any], live_cents: float, require_exit_join: bool = False) -> dict[str, Any]:
    blockers = row_blockers(row, live_cents=live_cents, require_exit_join=require_exit_join)
    return {
        "label": row.get("label"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": row.get("net_cents"),
        "delta_vs_live_cents": float(row.get("net_cents") or 0.0) - live_cents,
        "reconstructed_share": row.get("reconstructed_share"),
        "source_gate_row_margin": row.get("source_gate_row_margin"),
        "full_loss_cushion": row.get("full_loss_cushion"),
        "helpful_suppressed": row.get("helpful_suppressed"),
        "harmful_suppressed": row.get("harmful_suppressed"),
        "blockers": blockers,
        "live_review_ready": not blockers,
    }


def best_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    return max(rows, key=lambda row: float(row.get("net_cents") or -10**9))


def best_gate_distance(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    return sorted(
        rows,
        key=lambda row: (
            len(row.get("blockers") or []),
            -int(row.get("settled") or row.get("entries") or 0),
            -float(row.get("net_cents") or -10**9),
        ),
    )[0]


def build_report() -> dict[str, Any]:
    mix = load_json(MIX)
    child = load_json(PARENT_FILL_CHILD)
    losses = load_json(LOSS_DRILLDOWN)
    live_cents = live_net_cents()

    mix_diag = best_diagnostic(mix.get("variants", []))
    child_diag = best_diagnostic(child.get("variants", []))

    mix_strict = [
        summarize_variant(row, live_cents=live_cents, require_exit_join=True)
        for row in mix.get("strict_variants", [])
        if isinstance(row, dict)
    ]
    child_strict = [
        summarize_variant(row, live_cents=live_cents, require_exit_join=True)
        for row in child.get("strict_variants", [])
        if isinstance(row, dict)
    ]

    strict_rows = mix_strict + child_strict
    live_ready = [row for row in strict_rows if row.get("live_review_ready")]

    mix_diag_summary = summarize_variant(mix_diag, live_cents=live_cents)
    child_diag_summary = summarize_variant(child_diag, live_cents=live_cents)
    mix_diag_summary["diagnostic_prefreeze"] = True
    child_diag_summary["diagnostic_prefreeze"] = True

    mix_forward = mix.get("strict_forward_diagnostics") if isinstance(mix.get("strict_forward_diagnostics"), dict) else {}
    child_forward = (
        child.get("strict_forward_diagnostics")
        if isinstance(child.get("strict_forward_diagnostics"), dict)
        else {}
    )

    interpretation = [
        "Research-only top-component gate audit; no live bot changes or orders.",
        f"Live baseline used for deltas is {fmt_cents(live_cents)} from the refreshed live summary.",
        "The top-component stack remains diagnostic only: strict post-birth evidence is too small and does not beat live.",
        "The parent portfolio has no settled strict selected rows joined to exit-clock rows, so the exit-rescue mechanism has not been forward-proven in this branch.",
        "The loss drilldown argues against broad holding: on losses with both marks, holding would worsen losses by "
        f"{fmt_cents(losses.get('counterfactual_hold_delta_on_losses_cents'))}.",
    ]

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "mix_portfolio": str(MIX),
            "parent_fill_child": str(PARENT_FILL_CHILD),
            "loss_drilldown": str(LOSS_DRILLDOWN),
            "live_summary": str(LIVE_SUMMARY),
        },
        "live_net_cents": live_cents,
        "promotion_gate_pass_count": len(live_ready),
        "live_ready_rows": live_ready,
        "best_gate_distance_row": best_gate_distance(strict_rows),
        "diagnostic_blueprints": {
            "mix_best": mix_diag_summary,
            "parent_fill_child_best": child_diag_summary,
        },
        "strict_forward_diagnostics": {
            "mix": {
                "future_denominator": mix_forward.get("future_denominator"),
                "selected_parent_rows": mix_forward.get("selected_parent_rows"),
                "selected_settled_rows": mix_forward.get("selected_settled_rows"),
                "selected_pending_rows": mix_forward.get("selected_pending_rows"),
                "settled_parent_rows_with_exit_clock": mix_forward.get("settled_parent_rows_with_exit_clock"),
                "settled_parent_rows_without_exit_clock": mix_forward.get("settled_parent_rows_without_exit_clock"),
                "strict_all_scored_rows": mix_forward.get("strict_all_scored_rows"),
            },
            "parent_fill_child": {
                "future_denominator": child_forward.get("future_denominator"),
                "selected_parent_rows": child_forward.get("selected_parent_rows"),
                "selected_settled_rows": child_forward.get("selected_settled_rows"),
                "selected_pending_rows": child_forward.get("selected_pending_rows"),
                "settled_parent_rows_with_exit_clock": child_forward.get("settled_parent_rows_with_exit_clock"),
                "settled_parent_rows_without_exit_clock": child_forward.get("settled_parent_rows_without_exit_clock"),
                "strict_absd_fill_rows": child_forward.get("strict_absd_fill_rows"),
            },
        },
        "strict_rows": strict_rows,
        "loss_drilldown": {
            "loss_count": losses.get("loss_count"),
            "loss_net_cents": losses.get("loss_net_cents"),
            "by_mode": losses.get("by_mode", {}),
            "counterfactual_hold_delta_on_losses_cents": losses.get(
                "counterfactual_hold_delta_on_losses_cents"
            ),
        },
        "interpretation": interpretation,
    }


def md_table(rows: list[dict[str, Any]], limit: int = 10) -> list[str]:
    lines = [
        "| label | settled | W/L | coverage | net | delta live | recon | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows[:limit]:
        blockers = ", ".join(str(item) for item in row.get("blockers") or []) or "none"
        recon = row.get("reconstructed_share")
        recon_text = f"{float(recon):.3f}" if recon is not None else "n/a"
        lines.append(
            "| "
            f"`{row.get('label')}` | "
            f"{row.get('settled') or row.get('entries') or 0} | "
            f"{wl(row)} | "
            f"{fmt_pct(row.get('coverage_pct'))} | "
            f"{fmt_cents(row.get('net_cents'))} | "
            f"{fmt_cents(row.get('delta_vs_live_cents'))} | "
            f"{recon_text} | "
            f"{row.get('full_loss_cushion') or 0} | "
            f"{blockers} |"
        )
    return lines


def write_markdown(report: dict[str, Any]) -> None:
    best = report.get("best_gate_distance_row") or {}
    diag = report.get("diagnostic_blueprints") or {}
    mix_diag = diag.get("mix_best") or {}
    child_diag = diag.get("parent_fill_child_best") or {}
    strict = report.get("strict_forward_diagnostics") or {}
    mix_forward = strict.get("mix") or {}
    child_forward = strict.get("parent_fill_child") or {}
    losses = report.get("loss_drilldown") or {}

    lines = [
        "# v28 Top-Component Strict Gate Audit",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Live baseline: `{fmt_cents(report.get('live_net_cents'))}`",
        f"- Promotion gate passes: `{report.get('promotion_gate_pass_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Diagnostic Blueprint",
            "",
            f"- Mix best: `{mix_diag.get('label')}` with `{mix_diag.get('entries')}` entries, "
            f"{fmt_pct(mix_diag.get('coverage_pct'))} coverage, `{fmt_cents(mix_diag.get('net_cents'))}`, "
            f"W/L `{wl(mix_diag)}`, reconstructed share `{float(mix_diag.get('reconstructed_share') or 0.0):.3f}`, "
            f"cushion `{mix_diag.get('full_loss_cushion')}`. This is diagnostic/prefreeze only.",
            f"- Parent-fill child best: `{child_diag.get('label')}` with `{child_diag.get('entries')}` entries, "
            f"{fmt_pct(child_diag.get('coverage_pct'))} coverage, `{fmt_cents(child_diag.get('net_cents'))}`, "
            f"W/L `{wl(child_diag)}`, reconstructed share `{float(child_diag.get('reconstructed_share') or 0.0):.3f}`, "
            f"cushion `{child_diag.get('full_loss_cushion')}`. This is diagnostic/prefreeze only.",
            "",
            "## Strict Forward Denominators",
            "",
            f"- Mix portfolio: denominator `{mix_forward.get('future_denominator')}`, selected `{mix_forward.get('selected_parent_rows')}`, settled `{mix_forward.get('selected_settled_rows')}`, pending `{mix_forward.get('selected_pending_rows')}`, exit-clock joined `{mix_forward.get('settled_parent_rows_with_exit_clock')}`, strict scored `{mix_forward.get('strict_all_scored_rows')}`.",
            f"- Parent-fill child: denominator `{child_forward.get('future_denominator')}`, selected `{child_forward.get('selected_parent_rows')}`, settled `{child_forward.get('selected_settled_rows')}`, pending `{child_forward.get('selected_pending_rows')}`, exit-clock joined `{child_forward.get('settled_parent_rows_with_exit_clock')}`, strict absd-fill rows `{child_forward.get('strict_absd_fill_rows')}`.",
            "",
            "## Closest Strict Row",
            "",
        ]
    )
    if best:
        lines.extend(md_table([best], limit=1))
    else:
        lines.append("- No strict rows available.")

    strict_rows = sorted(
        report.get("strict_rows") or [],
        key=lambda row: (
            len(row.get("blockers") or []),
            -int(row.get("settled") or row.get("entries") or 0),
            -float(row.get("net_cents") or -10**9),
        ),
    )
    lines.extend(["", "## Strict Rows", ""])
    lines.extend(md_table(strict_rows, limit=12))

    by_mode = losses.get("by_mode") if isinstance(losses.get("by_mode"), dict) else {}
    lines.extend(
        [
            "",
            "## Loss Modes",
            "",
            f"- Diagnostic best loss net: `{fmt_cents(losses.get('loss_net_cents'))}` across `{losses.get('loss_count')}` rows.",
            f"- Hold counterfactual on losses with both marks: `{fmt_cents(losses.get('counterfactual_hold_delta_on_losses_cents'))}`.",
            "",
            "| mode | rows | net |",
            "|---|---:|---:|",
        ]
    )
    for mode, row in by_mode.items():
        if not isinstance(row, dict):
            continue
        lines.append(f"| `{mode}` | {row.get('rows')} | {fmt_cents(row.get('net_cents'))} |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
