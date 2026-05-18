"""Contrast global value-exit suppression with feature-gate entry geometry.

Research-only; no live bot changes or orders.

The global value-only exit watch has a post-birth suppressed loser, while the
feature-gate-selected live overlap showed clean value-over-hold suppression.
This probe checks whether feature-gate side agreement would have filtered the
global bad suppressions without using settlement outcomes as the rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALUE_ONLY_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
FEATURE_ALIGNMENT_JSON = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json"
OUT_JSON = OUT_DIR / "v28_value_exit_feature_gate_contrast_latest.json"
OUT_MD = OUT_DIR / "v28_value_exit_feature_gate_contrast_latest.md"

TARGET_FEATURE_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"
TARGET_VALUE_VARIANT = "value_only_gap15_or_p75"


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


def side_won(row: dict[str, Any]) -> bool:
    return str(row.get("side") or "").lower() == str(row.get("result") or "").lower()


def feature_rows_by_market() -> dict[str, dict[str, Any]]:
    payload = load_json(FEATURE_ALIGNMENT_JSON)
    for variant in payload.get("variants") or []:
        if variant.get("candidate") == TARGET_FEATURE_CANDIDATE:
            return {
                str(row.get("market") or ""): row
                for row in variant.get("rows") or []
                if isinstance(row, dict) and row.get("market")
            }
    return {}


def feature_class(row: dict[str, Any], feature: dict[str, Any] | None) -> str:
    if not feature:
        return "no_feature_gate_row"
    if str(row.get("side") or "").lower() == str(feature.get("side") or "").lower():
        return "feature_gate_same_side"
    return "feature_gate_opposite_side"


def candidate_with_feature_side_guard(row: dict[str, Any], feature: dict[str, Any] | None) -> float:
    if not row.get("value_only_suppressed"):
        return fnum(row.get("current_cents"))
    if feature_class(row, feature) == "feature_gate_same_side":
        return fnum(row.get("hold_cents"))
    return fnum(row.get("current_cents"))


def compact_row(row: dict[str, Any], feature: dict[str, Any] | None) -> dict[str, Any]:
    classification = feature_class(row, feature)
    guarded = candidate_with_feature_side_guard(row, feature)
    current = fnum(row.get("current_cents"))
    value_candidate = fnum(row.get("value_only_candidate_cents"))
    value_suppressed = bool(row.get("value_only_suppressed"))
    guard_suppressed = value_suppressed and classification == "feature_gate_same_side"
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "p_hold": row.get("p_hold"),
        "hold_book_gap": row.get("hold_book_gap"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "exit_bid_prob": row.get("exit_bid_prob"),
        "current_cents": current,
        "hold_cents": fnum(row.get("hold_cents")),
        "value_only_candidate_cents": value_candidate,
        "value_only_delta_cents": value_candidate - current,
        "feature_side_guard_candidate_cents": guarded,
        "feature_side_guard_delta_cents": guarded - current,
        "value_only_suppressed": value_suppressed,
        "feature_side_guard_suppressed": guard_suppressed,
        "feature_class": classification,
        "feature_gate_side": None if not feature else feature.get("side"),
        "feature_gate_side_won": None if not feature else feature.get("side_won"),
        "feature_gate_source": None if not feature else feature.get("source"),
        "feature_gate_raw_edge": None if not feature else feature.get("raw_edge"),
        "feature_gate_recross_hazard_score": None if not feature else feature.get("recross_hazard_score"),
        "feature_gate_abs_d_sigma": None if not feature else feature.get("abs_d_sigma"),
        "feature_gate_ask_prob": None if not feature else feature.get("ask_prob"),
        "feature_gate_theory_net_cents": None if not feature else feature.get("theory_net_cents"),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    suppressed = [row for row in rows if row.get("value_only_suppressed")]
    suppressed_winners = [row for row in suppressed if row.get("side_won")]
    suppressed_losers = [row for row in suppressed if not row.get("side_won")]
    value_net = sum(fnum(row.get("value_only_candidate_cents")) for row in rows)
    guarded_net = sum(fnum(row.get("feature_side_guard_candidate_cents")) for row in rows)
    current_net = sum(fnum(row.get("current_cents")) for row in rows)
    return {
        "rows": len(rows),
        "current_net_cents": current_net,
        "value_only_net_cents": value_net,
        "feature_side_guard_net_cents": guarded_net,
        "value_only_delta_cents": value_net - current_net,
        "feature_side_guard_delta_cents": guarded_net - current_net,
        "feature_side_guard_delta_vs_value_only_cents": guarded_net - value_net,
        "value_only_wins": sum(1 for row in rows if fnum(row.get("value_only_candidate_cents")) >= 0.0),
        "value_only_losses": sum(1 for row in rows if fnum(row.get("value_only_candidate_cents")) < 0.0),
        "feature_side_guard_wins": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) >= 0.0),
        "feature_side_guard_losses": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) < 0.0),
        "suppressed": len(suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "suppressed_loser_cost_cents": sum(fnum(row.get("value_only_delta_cents")) for row in suppressed_losers),
        "feature_class_counts": dict(Counter(row.get("feature_class") for row in suppressed)),
        "suppressed_loser_markets": [row for row in suppressed_losers],
    }


def lane_reports() -> list[dict[str, Any]]:
    value_payload = load_json(VALUE_ONLY_JSON)
    features = feature_rows_by_market()
    reports: list[dict[str, Any]] = []
    for lane in value_payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict) or variant.get("variant") != TARGET_VALUE_VARIANT:
                continue
            compacted = [
                compact_row(row, features.get(str(row.get("market") or "")))
                for row in variant.get("rows") or []
                if isinstance(row, dict)
            ]
            reports.append(
                {
                    "lane": lane_name,
                    "variant": TARGET_VALUE_VARIANT,
                    "summary": summarize_rows(compacted),
                    "suppressed_rows": [row for row in compacted if row.get("value_only_suppressed")],
                }
            )
    return reports


def build_report() -> dict[str, Any]:
    lanes = lane_reports()
    post = next((row for row in lanes if row.get("lane") == "post_value_only_birth"), {})
    post_summary = post.get("summary") or {}
    interpretation = [
        "Research-only contrast; no live bot changes or orders.",
        (
            "Feature-gate side agreement is an observable guard: it uses the feature-gate selected side, "
            "not settlement outcome, to decide whether a value-over-hold exit belongs to the same thesis."
        ),
        (
            f"Post-birth value-only net {post_summary.get('value_only_net_cents')}c versus "
            f"feature-side-guard net {post_summary.get('feature_side_guard_net_cents')}c."
        ),
        (
            f"Suppressed loser cost under value-only was {post_summary.get('suppressed_loser_cost_cents')}c; "
            "the key test is whether feature-side agreement filters that loser without deleting too much winner recovery."
        ),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "value_only_source": str(VALUE_ONLY_JSON),
        "feature_alignment_source": str(FEATURE_ALIGNMENT_JSON),
        "target_feature_candidate": TARGET_FEATURE_CANDIDATE,
        "target_value_variant": TARGET_VALUE_VARIANT,
        "interpretation": interpretation,
        "lanes": lanes,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Value Exit / Feature-Gate Contrast",
        "",
        "Research-only contrast. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature candidate: `{report.get('target_feature_candidate')}`",
        f"- Value-exit variant: `{report.get('target_value_variant')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lanes",
            "",
            "| lane | rows | value net c | guarded net c | guarded delta vs value c | value W/L | guarded W/L | suppressed | sup W/L | sup loser cost c | feature class counts |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.append(
            f"| `{lane.get('lane')}` | {summary.get('rows')} | {fmt(summary.get('value_only_net_cents'))} | "
            f"{fmt(summary.get('feature_side_guard_net_cents'))} | "
            f"{fmt(summary.get('feature_side_guard_delta_vs_value_only_cents'))} | "
            f"{summary.get('value_only_wins')}/{summary.get('value_only_losses')} | "
            f"{summary.get('feature_side_guard_wins')}/{summary.get('feature_side_guard_losses')} | "
            f"{summary.get('suppressed')} | {summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
            f"{fmt(summary.get('suppressed_loser_cost_cents'))} | `{summary.get('feature_class_counts')}` |"
        )
    lines.extend(
        [
            "",
            "## Suppressed Losers",
            "",
            "| lane | market | value side | result | feature side | feature class | value delta c | guarded delta c | p_hold | exit bid | raw edge | recross | abs d | ask |",
            "|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for lane in report.get("lanes") or []:
        for row in (lane.get("summary") or {}).get("suppressed_loser_markets") or []:
            lines.append(
                f"| `{lane.get('lane')}` | {row.get('market')} | {row.get('side')} | {row.get('result')} | "
                f"{row.get('feature_gate_side')} | {row.get('feature_class')} | "
                f"{fmt(row.get('value_only_delta_cents'))} | {fmt(row.get('feature_side_guard_delta_cents'))} | "
                f"{fmt(row.get('p_hold'))} | {fmt(row.get('exit_bid_prob'))} | "
                f"{fmt(row.get('feature_gate_raw_edge'))} | {fmt(row.get('feature_gate_recross_hazard_score'))} | "
                f"{fmt(row.get('feature_gate_abs_d_sigma'))} | {fmt(row.get('feature_gate_ask_prob'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
