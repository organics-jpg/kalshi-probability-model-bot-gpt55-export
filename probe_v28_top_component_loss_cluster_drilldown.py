"""Residual loss-cluster drilldown for the v28 top-component mix.

Research-only; no live bot changes or orders.

This reads the latest top-component mix portfolio report and classifies the
best diagnostic variant's losing rows into physical failure modes. It is meant
to answer whether the remaining losses are exit false negatives, harmful exit
suppression, parent-fill entry/FV losses, source-quality risk, or true losers.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TOP_COMPONENT_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
OUT_JSON = OUT_DIR / "v28_top_component_loss_cluster_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_loss_cluster_drilldown_latest.md"

PREFERRED_LABEL = "rescue_drop15_plus_absd_parent_fill_to75"


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


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def choose_variant(payload: dict[str, Any]) -> dict[str, Any]:
    variants = [row for row in payload.get("variants") or [] if isinstance(row, dict)]
    for row in variants:
        if row.get("label") == PREFERRED_LABEL:
            return row
    candidates = [
        row for row in variants
        if not str(row.get("label") or "").startswith("post_birth_")
        and "coverage_too_low" not in (row.get("blockers") or [])
        and "coverage_too_high" not in (row.get("blockers") or [])
        and "row_reconstructed_share_gt_35pct" not in (row.get("blockers") or [])
    ]
    candidates.sort(key=lambda row: fnum(row.get("net_cents")), reverse=True)
    return candidates[0] if candidates else (variants[0] if variants else {})


def classify_loss(row: dict[str, Any]) -> tuple[str, list[str]]:
    component = str(row.get("component") or "")
    tags: list[str] = []
    if source(row) != "approved_entry":
        tags.append("source_quality_risk")
    if component.startswith("parent_midprice"):
        tags.append("entry_timing_or_fv_error")
        return "parent_fill_entry_or_fv_loss", tags
    if bool(row.get("selected_suppressed")):
        tags.append("exit_policy_error")
        return "harmful_exit_suppression", tags

    current = fnum(row.get("current_cents"), None) if row.get("current_cents") is not None else None
    hold = fnum(row.get("hold_cents"), None) if row.get("hold_cents") is not None else None
    if current is not None and current < 0 and hold is not None and hold > 0:
        tags.append("exit_policy_error")
        return "missed_exit_rescue_false_negative", tags
    if current is not None and current < 0 and hold is not None and hold < 0:
        tags.append("fv_or_entry_error")
        return "true_loser_entry_or_fv_loss", tags
    if current is not None and current < 0 and hold is None:
        tags.append("execution_or_source_quality_error")
        return "exit_clock_missing_or_unscored_loss", tags
    return "residual_negative_weighted", tags


def compact_loss(row: dict[str, Any]) -> dict[str, Any]:
    mode, tags = classify_loss(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": source(row),
        "component": row.get("component"),
        "weighted_cents": row.get("selected_weighted_cents"),
        "raw_selected_cents": row.get("selected_cents"),
        "mode": mode,
        "tags": tags,
        "selected_suppressed": bool(row.get("selected_suppressed")),
        "selected_delta_cents": row.get("selected_delta_cents"),
        "exit_reason": row.get("exit_reason"),
        "p_hold": row.get("p_hold"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "exit_bid": row.get("exit_bid"),
        "recheck_bid": row.get("recheck_bid"),
        "window_drop_cents": row.get("window_drop_cents"),
        "hold_cents": row.get("hold_cents"),
        "current_cents": row.get("current_cents"),
        "raw_edge": row.get("raw_edge"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
    }


def build_report() -> dict[str, Any]:
    payload = load_json(TOP_COMPONENT_JSON)
    variant = choose_variant(payload)
    rows = [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    losses = [row for row in rows if fnum(row.get("selected_weighted_cents")) < 0]
    loss_rows = [compact_loss(row) for row in losses]

    by_mode: dict[str, dict[str, Any]] = {}
    for mode in sorted({row["mode"] for row in loss_rows}):
        bucket = [row for row in loss_rows if row["mode"] == mode]
        by_mode[mode] = {
            "rows": len(bucket),
            "net_cents": sum(fnum(row.get("weighted_cents")) for row in bucket),
            "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in bucket)),
            "tag_counts": dict(Counter(tag for row in bucket for tag in row.get("tags") or [])),
        }
    by_component = {
        component: {
            "rows": len(bucket),
            "net_cents": sum(fnum(row.get("weighted_cents")) for row in bucket),
        }
        for component, bucket in group_by(loss_rows, "component").items()
    }
    by_source = {
        source_name: {
            "rows": len(bucket),
            "net_cents": sum(fnum(row.get("weighted_cents")) for row in bucket),
        }
        for source_name, bucket in group_by(loss_rows, "source").items()
    }
    counterfactual_hold_delta = sum(
        fnum(row.get("hold_cents")) - fnum(row.get("current_cents"))
        for row in loss_rows
        if row.get("hold_cents") is not None and row.get("current_cents") is not None
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "source_report": str(TOP_COMPONENT_JSON),
        "portfolio_generated_at_utc": payload.get("generated_at_utc"),
        "portfolio_freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc") if isinstance(payload.get("state"), dict) else None,
        "variant": variant.get("label"),
        "variant_net_cents": variant.get("net_cents"),
        "variant_wins": variant.get("wins"),
        "variant_losses": variant.get("losses"),
        "variant_coverage_pct": variant.get("coverage_pct"),
        "variant_blockers": variant.get("blockers") or [],
        "loss_count": len(loss_rows),
        "loss_net_cents": sum(fnum(row.get("weighted_cents")) for row in loss_rows),
        "by_mode": by_mode,
        "by_component": by_component,
        "by_source": by_source,
        "counterfactual_hold_delta_on_losses_cents": counterfactual_hold_delta,
        "worst_losses": sorted(loss_rows, key=lambda row: fnum(row.get("weighted_cents")))[:20],
        "interpretation": interpretation(variant, by_mode, by_source, counterfactual_hold_delta),
    }


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key) or "unknown")].append(row)
    return dict(grouped)


def interpretation(
    variant: dict[str, Any],
    by_mode: dict[str, dict[str, Any]],
    by_source: dict[str, dict[str, Any]],
    hold_delta: float,
) -> list[str]:
    notes = [
        "Research-only loss drilldown; no live bot changes or orders.",
        f"Best inspected variant is {variant.get('label')} with net {variant.get('net_cents')}c and W/L {variant.get('wins')}/{variant.get('losses')}.",
    ]
    if by_mode.get("missed_exit_rescue_false_negative"):
        bucket = by_mode["missed_exit_rescue_false_negative"]
        notes.append(
            f"Exit-policy false negatives remain: {bucket['rows']} losing rows would have been helped by holding instead of taking current exit marks."
        )
    if by_mode.get("parent_fill_entry_or_fv_loss"):
        bucket = by_mode["parent_fill_entry_or_fv_loss"]
        notes.append(
            f"Parent-fill losses are the entry/FV repair target: {bucket['rows']} rows for {bucket['net_cents']}c."
        )
    if by_source.get("rejected_actionable"):
        bucket = by_source["rejected_actionable"]
        notes.append(
            f"Rejected/reconstructed losses are still material: {bucket['rows']} losing rows for {bucket['net_cents']}c."
        )
    if hold_delta > 0:
        notes.append(f"On losing rows with both marks, hold-vs-current counterfactual is +{hold_delta}c, so the remaining edge likely lives in a cleaner recheck/exit-state filter.")
    elif hold_delta < 0:
        notes.append(f"On losing rows with both marks, holding would worsen losses by {hold_delta}c, so these are mostly true FV/entry losers rather than clipped winners.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Top-Component Loss Cluster Drilldown",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source report UTC: `{report.get('portfolio_generated_at_utc')}`",
        f"- Variant: `{report.get('variant')}`",
        f"- Variant PnL/WL/Coverage: `{fmt(report.get('variant_net_cents'))}c`, `{report.get('variant_wins')}/{report.get('variant_losses')}`, `{fmt(report.get('variant_coverage_pct'))}%`",
        f"- Loss net: `{fmt(report.get('loss_net_cents'))}c` across `{report.get('loss_count')}` rows",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(["", "## Losses By Mode", "", "| mode | rows | net | source counts | tags |", "|---|---:|---:|---|---|"])
    for mode, row in sorted((report.get("by_mode") or {}).items(), key=lambda item: float(item[1].get("net_cents") or 0.0)):
        lines.append(f"| `{mode}` | {row.get('rows')} | {fmt(row.get('net_cents'))} | `{row.get('source_counts')}` | `{row.get('tag_counts')}` |")
    lines.extend(["", "## Worst Loss Rows", "", "| market | side | source | mode | component | weighted | hold | current | exit | p_hold | drawdown | recheck |", "|---|---|---|---|---|---:|---:|---:|---|---:|---:|---:|"])
    for row in report.get("worst_losses") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | `{row.get('mode')}` | {row.get('component')} | "
            f"{fmt(row.get('weighted_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('current_cents'))} | "
            f"{row.get('exit_reason')} | {fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('recheck_bid'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
