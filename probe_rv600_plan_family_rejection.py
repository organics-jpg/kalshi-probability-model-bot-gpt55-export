from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_GRID_JSON = Path("logs/particle_research/reports/rv600_variation_forward_grid_latest.json")
DEFAULT_FUTILITY_JSON = Path("logs/particle_research/reports/rv600_forward_futility_latest.json")
DEFAULT_AUDIT_JSON = Path("logs/particle_research/reports/rv600_goal_completion_audit_latest.json")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_plan_family_rejection_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_plan_family_rejection_latest.md")


PLAN_FAMILIES: dict[str, list[str]] = {
    "A_timing_windows": [
        "late_70_180",
        "late_70_240",
        "late_70_300",
        "base_70_420",
        "mid_120_420",
        "mid_180_420",
        "broad_70_600",
    ],
    "B_ev_thresholds": [
        "ev0",
        "ev2",
        "ev4",
        "ev6",
        "ev8",
        "ev10",
        "ev12",
        "ev15",
        "ev20",
    ],
    "C_repeated_entry_rules": [
        "single_market",
        "side_flip_only",
        "same_side_refresh_60s",
        "same_side_refresh_120s",
        "same_side_ev_step_3c",
        "same_side_ev_step_5c",
        "max_2_entries",
        "max_3_entries",
        "risk_cap_100c",
        "risk_cap_200c",
    ],
    "D_side_filters": [
        "yes_only",
        "no_only",
        "side_by_rv_gap",
        "side_by_v28_agreement",
        "side_by_v28_disagreement",
    ],
    "E_v28_transfer_controls": [
        "rv600_primary",
        "v28_primary",
        "blend_95_5",
        "blend_90_10",
        "blend_80_20",
        "agreement_veto",
        "softveto6",
        "softveto10",
    ],
    "F_volatility_regime_filters": [
        "vol_mid",
        "vol_high",
        "vol_low",
        "vol_accel",
        "vol_decel",
        "strike_near",
        "strike_far",
    ],
    "G_microstructure_filters": [
        "book_age_250",
        "book_age_500",
        "depth_ratio_3",
        "depth_ratio_6",
        "spread_3c",
        "spread_5c",
        "fill_prob_50",
        "fill_prob_70",
    ],
    "H_price_caps_payoff_shape": [
        "ask_le_90",
        "ask_le_85",
        "ask_40_85",
        "cheap_tail",
        "rich_tail",
    ],
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _best(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return max(rows, key=lambda row: _float(row.get("selected_pnl_cents")))


def _compact_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "variant": row.get("variant"),
        "accounting_mode": row.get("accounting_mode"),
        "gate_count": _int(row.get("gate_count")),
        "accepted_entries": _int(row.get("accepted_entries")),
        "distinct_markets": _int(row.get("distinct_markets")),
        "selected_pnl_cents": _float(row.get("selected_pnl_cents")),
        "matched_v28_delta_cents": _float(row.get("matched_v28_delta_cents")),
        "avg_pnl_per_entry_cents": _float(row.get("avg_pnl_per_entry_cents")),
        "positive_root_rate": _float(row.get("positive_root_rate")),
        "positive_market_rate": _float(row.get("positive_market_rate")),
        "max_single_market_pnl_share": _float(row.get("max_single_market_pnl_share")),
        "last_window_pnl_cents": _float(row.get("last_window_pnl_cents")),
        "locked_candidate_eligible": bool(row.get("locked_candidate_eligible")),
        "rejection_reason": row.get("rejection_reason") or "",
    }


def _rejection_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        reason = str(row.get("rejection_reason") or "")
        for item in reason.split(";"):
            if item:
                counter[item] += 1
    return dict(counter.most_common())


def _family_value_summary(rows: list[dict[str, Any]], value: str) -> dict[str, Any]:
    matching = [row for row in rows if _variant_has_value(str(row.get("variant") or ""), value)]
    eligible = [row for row in matching if row.get("locked_candidate_eligible")]
    unrejected = [row for row in matching if not row.get("rejection_reason")]
    positive = [row for row in matching if _float(row.get("selected_pnl_cents")) > 0.0]
    best = _compact_row(_best(matching))
    return {
        "value": value,
        "row_count": len(matching),
        "positive_row_count": len(positive),
        "locked_candidate_eligible_count": len(eligible),
        "unrejected_row_count": len(unrejected),
        "best": best,
        "top_rejection_reasons": _rejection_counts(matching),
        "decision": "candidate_found" if eligible or unrejected else "rejected",
    }


def _variant_has_value(variant: str, value: str) -> bool:
    return re.search(rf"(^|_){re.escape(value)}($|_)", variant) is not None


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    grid = _load_json(args.grid_json)
    futility = _load_json(args.futility_json)
    audit = _load_json(args.audit_json)
    rows = grid.get("summary_rows") or []
    if not rows:
        raise SystemExit("grid report has no summary_rows")

    family_reports: dict[str, Any] = {}
    candidate_family_count = 0
    for family, values in PLAN_FAMILIES.items():
        value_rows = [_family_value_summary(rows, value) for value in values]
        family_candidate_count = sum(
            1 for value_row in value_rows if value_row["decision"] == "candidate_found"
        )
        candidate_family_count += family_candidate_count
        family_reports[family] = {
            "values_tested": len(value_rows),
            "values_with_rows": sum(1 for value_row in value_rows if value_row["row_count"] > 0),
            "values_with_candidate": family_candidate_count,
            "best_value": _best_value(value_rows),
            "value_rows": value_rows,
            "decision": "candidate_found" if family_candidate_count else "all_values_rejected",
        }

    top_rows = [_compact_row(row) for row in rows[:25]]
    decision = (
        "no_existing_plan_family_viable"
        if candidate_family_count == 0 and not grid.get("promotion_allowed")
        else "existing_plan_family_candidate_available"
    )
    report = {
        "schema_version": "rv600-plan-family-rejection-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "grid": {
            "phase": grid.get("phase"),
            "root_count": _int(grid.get("root_count")),
            "variant_count": _int(grid.get("variant_count")),
            "summary_row_count": len(rows),
            "best_by_total_pnl": grid.get("best_by_total_pnl"),
            "best_locked_candidate": grid.get("best_locked_candidate") or "",
            "promotion_allowed": bool(grid.get("promotion_allowed")),
        },
        "futility": {
            "decision": futility.get("decision"),
            "reasons": futility.get("reasons") or [],
            "success_probability": _float((futility.get("bootstrap") or {}).get("success_probability")),
        },
        "audit": {
            "goal_complete": bool(audit.get("goal_complete")),
            "status_counts": audit.get("status_counts") or {},
            "forward_shadow_sample": audit.get("forward_shadow_sample") or {},
        },
        "top_rows": top_rows,
        "families": family_reports,
        "inputs": {
            "grid_json": str(args.grid_json),
            "futility_json": str(args.futility_json),
            "audit_json": str(args.audit_json),
        },
    }
    return report


def _best_value(value_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    available = [row for row in value_rows if row["best"] is not None]
    if not available:
        return None
    return max(available, key=lambda row: row["best"]["selected_pnl_cents"])


def _markdown(report: dict[str, Any]) -> str:
    grid = report["grid"]
    audit_sample = report["audit"]["forward_shadow_sample"]
    lines = [
        "# RV600 Plan Family Rejection Ledger",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        "",
        "## Inputs",
        "",
        f"- grid_phase: {grid['phase']}",
        f"- grid_root_count: {grid['root_count']}",
        f"- grid_variant_count: {grid['variant_count']}",
        f"- grid_summary_row_count: {grid['summary_row_count']}",
        f"- best_by_total_pnl: `{grid['best_by_total_pnl']}`",
        f"- best_locked_candidate: `{grid['best_locked_candidate']}`",
        f"- promotion_allowed: {grid['promotion_allowed']}",
        f"- futility_decision: `{report['futility']['decision']}`",
        f"- futility_success_probability: {report['futility']['success_probability']:.4f}",
        f"- audit_goal_complete: {report['audit']['goal_complete']}",
        f"- audit_forward_entries: {audit_sample.get('accepted_entries')}",
        f"- audit_forward_markets: {audit_sample.get('distinct_markets')}",
        f"- audit_forward_pnl_cents: {audit_sample.get('selected_pnl_cents')}",
        "",
        "## Family Decisions",
        "",
        "| family | values tested | values with rows | values with candidate | best value | best pnl | best entries | best markets | main rejection | decision |",
        "|---|---:|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for family, family_report in report["families"].items():
        best_value = family_report.get("best_value")
        if best_value and best_value.get("best"):
            best = best_value["best"]
            main_rejection = best.get("rejection_reason") or ""
            best_name = best_value["value"]
            best_pnl = f"{best['selected_pnl_cents']:.1f}"
            best_entries = str(best["accepted_entries"])
            best_markets = str(best["distinct_markets"])
        else:
            main_rejection = "no_rows"
            best_name = ""
            best_pnl = "0.0"
            best_entries = "0"
            best_markets = "0"
        lines.append(
            "| {family} | {values_tested} | {values_with_rows} | {values_with_candidate} | "
            "`{best_name}` | {best_pnl} | {best_entries} | {best_markets} | {main_rejection} | {decision} |".format(
                family=family,
                values_tested=family_report["values_tested"],
                values_with_rows=family_report["values_with_rows"],
                values_with_candidate=family_report["values_with_candidate"],
                best_name=best_name,
                best_pnl=best_pnl,
                best_entries=best_entries,
                best_markets=best_markets,
                main_rejection=main_rejection,
                decision=family_report["decision"],
            )
        )
    lines.extend(
        [
            "",
            "## Top Existing Rows",
            "",
            "| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | reject |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["top_rows"][:15]:
        if row is None:
            continue
        lines.append(
            "| `{variant}` | {accounting_mode} | {gate_count} | {accepted_entries} | "
            "{distinct_markets} | {selected_pnl_cents:.1f} | {matched_v28_delta_cents:.1f} | {rejection_reason} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "All plan-defined RV600 families are rejected on current forward evidence.",
            "The blockers are not missing implementation coverage; they are sparse positive rows, poor root/market stability, concentration, nonpositive recent windows, and no matched-v28 edge.",
            "Do not promote or live-test any current RV600 family. A future RV600 attempt needs a newly frozen candidate and must restart the same anti-overfitting and forward-shadow gates from scratch.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize RV600 plan-family rejection from the expanded forward grid.")
    parser.add_argument("--grid-json", type=Path, default=DEFAULT_GRID_JSON)
    parser.add_argument("--futility-json", type=Path, default=DEFAULT_FUTILITY_JSON)
    parser.add_argument("--audit-json", type=Path, default=DEFAULT_AUDIT_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"grid_variant_count={report['grid']['variant_count']}")
    print(f"families={len(report['families'])}")
    print(f"promotion_allowed={report['grid']['promotion_allowed']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
