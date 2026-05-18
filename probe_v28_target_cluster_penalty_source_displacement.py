"""Observable displacement audit for cluster-penalty source quality.

Research-only; no live bot changes or orders.

The source-feasibility audit showed approved rows exist but the ranking often
chooses rejected-actionable rows first. This report describes the observable
features of the selected rejected rows versus omitted approved rows so future
repairs can use market physics, not source labels.
"""
from __future__ import annotations

import json
from statistics import mean
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee, summarize
from probe_v28_target_coverage_cluster_penalty_watch import (
    VARIANTS,
    abs_d,
    adjusted_edge,
    ask_prob,
    clean_forward_rows,
    compact,
    raw_edge,
    recross,
    seconds_to_close,
    selected_rows,
    target_freeze_ts,
)
from probe_v28_target_cluster_penalty_source_feasibility import (
    best_by_market,
    is_approved,
    load_json,
    required_entries,
    tradeable_scored_rows,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_state.json"
OUT_JSON = OUT_DIR / "v28_target_cluster_penalty_source_displacement_latest.json"
OUT_MD = OUT_DIR / "v28_target_cluster_penalty_source_displacement_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def avg(rows: list[dict[str, Any]], getter) -> float | None:
    values = []
    for row in rows:
        value = getter(row)
        if value is not None:
            values.append(float(value))
    return None if not values else mean(values)


def source_label(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def feature_summary(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    summary = summarize(rows, denominator)
    return {
        "rows": len(rows),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "net_cents": summary.get("net_cents"),
        "avg_net_cents": summary.get("avg_net_cents"),
        "approved_rows": sum(1 for row in rows if is_approved(row)),
        "rejected_rows": sum(1 for row in rows if not is_approved(row)),
        "no_side_rows": sum(1 for row in rows if str(row.get("side") or "").lower() == "no"),
        "yes_side_rows": sum(1 for row in rows if str(row.get("side") or "").lower() == "yes"),
        "avg_adjusted_edge": avg(rows, lambda row: as_float(row.get("adjusted_edge"))),
        "avg_raw_edge": avg(rows, lambda row: raw_edge(row)),
        "avg_ask_prob": avg(rows, ask_prob),
        "avg_p_side": avg(rows, lambda row: as_float(row.get("p_side"))),
        "avg_abs_d_sigma": avg(rows, abs_d),
        "avg_recross_hazard": avg(rows, recross),
        "avg_seconds_to_close": avg(rows, seconds_to_close),
    }


def enrich_selected(rows: list[dict[str, Any]], params: dict[str, float]) -> list[dict[str, Any]]:
    enriched = []
    for row in rows:
        if row.get("adjusted_edge") is not None:
            enriched.append(row)
            continue
        score = adjusted_edge(row, params)
        enriched.append({
            **row,
            "adjusted_edge": score,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        })
    return enriched


def lane_freezes() -> dict[str, str]:
    state = load_json(STATE_JSON)
    return {
        "diagnostic_target_window": target_freeze_ts(),
        "post_cluster_penalty_birth": str(state.get("freeze_ts_utc") or utc_now_iso()),
    }


def audit_variant(
    lane: str,
    freeze_ts: str,
    rows: list[dict[str, Any]],
    denominator: int,
    variant: str,
    params: dict[str, float],
) -> dict[str, Any]:
    need = required_entries(denominator)
    scored = tradeable_scored_rows(rows, params)
    best_all = best_by_market(scored)
    best_approved = best_by_market([row for row in scored if is_approved(row)])
    selected = enrich_selected(selected_rows(rows, denominator, params), params)
    selected_markets = {str(row.get("market") or "") for row in selected}
    selected_rejected = [row for row in selected if not is_approved(row)]
    selected_approved = [row for row in selected if is_approved(row)]
    omitted_approved = [
        row for market, row in best_approved.items()
        if market not in selected_markets
    ]
    selected_rejected.sort(key=lambda row: float(row_net_after_fee(row) or 0.0))
    omitted_approved.sort(key=lambda row: float(row_net_after_fee(row) or 0.0))
    approved_preferred = sorted(
        list(best_approved.values()) + [
            row for market, row in best_all.items()
            if market not in best_approved
        ],
        key=lambda row: (is_approved(row), float(row.get("adjusted_edge") or -999.0)),
        reverse=True,
    )[:need]
    return {
        "lane": lane,
        "variant": variant,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "required_entries": need,
        "selected_summary": feature_summary(selected, denominator),
        "selected_approved_summary": feature_summary(selected_approved, denominator),
        "selected_rejected_summary": feature_summary(selected_rejected, denominator),
        "omitted_approved_summary": feature_summary(omitted_approved, denominator),
        "approved_preferred_summary": feature_summary(approved_preferred, denominator),
        "selected_rejected_worst_examples": [compact(row) for row in selected_rejected[:12]],
        "omitted_approved_worst_examples": [compact(row) for row in omitted_approved[:12]],
    }


def build_report() -> dict[str, Any]:
    lanes = []
    for lane, freeze_ts in lane_freezes().items():
        rows, _target, denominator = clean_forward_rows(freeze_ts)
        variants = [
            audit_variant(lane, freeze_ts, rows, denominator, name, params)
            for name, params in VARIANTS.items()
        ]
        variants.sort(
            key=lambda row: (
                -float(as_float((row.get("selected_summary") or {}).get("net_cents")) or -999999.0),
                str(row.get("variant") or ""),
            )
        )
        lanes.append({"lane": lane, "freeze_ts_utc": freeze_ts, "variants": variants, "best": variants[0] if variants else {}})
    report = {"generated_at_utc": utc_now_iso(), "lanes": lanes}
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This audit is diagnostic only; source labels are not deployable live features.",
    ]
    for lane in report.get("lanes") or []:
        best = lane.get("best") or {}
        rejected = best.get("selected_rejected_summary") or {}
        omitted = best.get("omitted_approved_summary") or {}
        preferred = best.get("approved_preferred_summary") or {}
        notes.append(
            f"{lane.get('lane')}: selected rejected rows net {rejected.get('net_cents')}c over {rejected.get('settled')} settled, "
            f"omitted approved rows net {omitted.get('net_cents')}c over {omitted.get('settled')} settled, "
            f"approved-preferred net {preferred.get('net_cents')}c."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Target Cluster-Penalty Source Displacement",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        best = lane.get("best") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Best variant: `{best.get('variant')}`",
            "",
            "| group | rows | settled | W/L | net c | avg adjusted edge | avg raw edge | avg ask | avg abs d | avg recross | avg stc |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        groups = [
            ("selected_all", best.get("selected_summary") or {}),
            ("selected_approved", best.get("selected_approved_summary") or {}),
            ("selected_rejected", best.get("selected_rejected_summary") or {}),
            ("omitted_approved", best.get("omitted_approved_summary") or {}),
            ("approved_preferred", best.get("approved_preferred_summary") or {}),
        ]
        for label, row in groups:
            lines.append(
                f"| `{label}` | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_adjusted_edge'))} | {fmt(row.get('avg_raw_edge'))} | "
                f"{fmt(row.get('avg_ask_prob'))} | {fmt(row.get('avg_abs_d_sigma'))} | "
                f"{fmt(row.get('avg_recross_hazard'))} | {fmt(row.get('avg_seconds_to_close'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
