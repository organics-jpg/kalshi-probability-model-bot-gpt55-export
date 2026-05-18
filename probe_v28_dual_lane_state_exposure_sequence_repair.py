"""Diagnostic state/exposure sequencing repair for the v28 dual-lane branch.

Research-only; no live bot changes or orders.

The same-window sequence audit showed live v28 beating the current one-shot
dual-lane precheck through larger terminal same-side exposure, same-side exit
capture at scale, and side-flip escapes. This probe tests whether simple
observable exposure weighting could address that mechanism without hand-picking
markets.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DELTA_JSON = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json"
SEQUENCE_JSON = OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_state_exposure_sequence_repair_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_state_exposure_sequence_repair_latest.md"


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
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def row_net(row: dict[str, Any]) -> float:
    return fnum(row.get("candidate_net_cents"))


def row_live_net(row: dict[str, Any]) -> float:
    return fnum(row.get("live_net_cents"))


def high_cost_low_edge(row: dict[str, Any]) -> bool:
    return fnum(row.get("ask_prob")) >= 0.78 and fnum(row.get("raw_edge")) < 0.09


def strong_same_side_exposure(row: dict[str, Any]) -> bool:
    return (
        row.get("candidate_source") == "approved_entry"
        and fnum(row.get("raw_edge")) >= 0.12
        and fnum(row.get("ask_prob")) <= 0.75
        and fnum(row.get("recross_hazard_score")) <= 0.50
    )


def mid_confidence_scale(row: dict[str, Any]) -> bool:
    return (
        row.get("candidate_source") == "approved_entry"
        and fnum(row.get("raw_edge")) >= 0.10
        and fnum(row.get("ask_prob")) <= 0.80
        and fnum(row.get("recross_hazard_score")) <= 0.50
    )


def continuous_weight(row: dict[str, Any]) -> float:
    raw_edge = fnum(row.get("raw_edge"))
    ask = fnum(row.get("ask_prob"))
    recross = fnum(row.get("recross_hazard_score"))
    if raw_edge <= 0.0:
        return 1.0
    weight = 1.0
    weight += max(0.0, raw_edge - 0.09) * 5.0
    weight -= max(0.0, ask - 0.78) * 2.0
    weight -= max(0.0, recross - 0.50) * 0.8
    return max(0.35, min(1.8, weight))


def variant_weight(name: str, row: dict[str, Any]) -> float:
    if name == "baseline":
        return 1.0
    if name == "shrink_high_cost_low_edge_50":
        return 0.5 if high_cost_low_edge(row) else 1.0
    if name == "scale_strong_same_side_2x":
        return 2.0 if strong_same_side_exposure(row) else 1.0
    if name == "scale_mid_confidence_1p5x":
        return 1.5 if mid_confidence_scale(row) else 1.0
    if name == "sequence_combo_strong2x_shrink50":
        if high_cost_low_edge(row):
            return 0.5
        if strong_same_side_exposure(row):
            return 2.0
        return 1.0
    if name == "sequence_combo_mid1p5_shrink50":
        if high_cost_low_edge(row):
            return 0.5
        if mid_confidence_scale(row):
            return 1.5
        return 1.0
    if name == "continuous_edge_cost_weight":
        return continuous_weight(row)
    return 1.0


def summarize_variant(name: str, rows: list[dict[str, Any]], denominator: int, live_baseline_cents: float) -> dict[str, Any]:
    scored_rows: list[dict[str, Any]] = []
    for row in rows:
        weight = variant_weight(name, row)
        adjusted = row_net(row) * weight
        live = row_live_net(row)
        item = dict(row)
        item["exposure_weight"] = weight
        item["adjusted_candidate_net_cents"] = adjusted
        item["adjusted_candidate_minus_live_cents"] = adjusted - live
        if weight != 1.0:
            item["weight_reason"] = (
                "high_cost_low_edge_shrink"
                if high_cost_low_edge(row)
                else "strong_same_side_scale"
                if strong_same_side_exposure(row)
                else "mid_confidence_scale"
                if mid_confidence_scale(row)
                else "continuous_edge_cost_weight"
            )
        scored_rows.append(item)
    net = sum(fnum(row.get("adjusted_candidate_net_cents")) for row in scored_rows)
    live_same_net = sum(row_live_net(row) for row in rows)
    adjusted_delta = net - live_same_net
    weights_changed = [row for row in scored_rows if fnum(row.get("exposure_weight"), 1.0) != 1.0]
    amplified_losers = [
        row for row in weights_changed
        if fnum(row.get("exposure_weight")) > 1.0 and row_net(row) < 0
    ]
    shrunk_winners = [
        row for row in weights_changed
        if fnum(row.get("exposure_weight")) < 1.0 and row_net(row) > 0
    ]
    blockers: list[str] = ["diagnostic_only_same_window", "not_frozen_forward", "state_sequence_not_live_ready"]
    if adjusted_delta <= 0:
        blockers.append("still_trails_live_same_window")
    if net <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    if amplified_losers:
        blockers.append("amplifies_losing_rows")
    if shrunk_winners:
        blockers.append("shrinks_winning_rows")
    if net <= live_baseline_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return {
        "variant": name,
        "entries": len(scored_rows),
        "coverage_pct": 100.0 * len(scored_rows) / denominator if denominator else None,
        "wins": sum(1 for row in scored_rows if fnum(row.get("adjusted_candidate_net_cents")) > 0),
        "losses": sum(1 for row in scored_rows if fnum(row.get("adjusted_candidate_net_cents")) < 0),
        "adjusted_candidate_net_cents": net,
        "live_same_market_net_cents": live_same_net,
        "adjusted_candidate_minus_live_cents": adjusted_delta,
        "delta_vs_baseline_candidate_cents": net - sum(row_net(row) for row in rows),
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "weights_changed": len(weights_changed),
        "amplified_losing_rows": len(amplified_losers),
        "shrunk_winning_rows": len(shrunk_winners),
        "blockers": blockers,
        "weighted_rows": sorted(scored_rows, key=lambda row: fnum(row.get("adjusted_candidate_minus_live_cents")))[:8],
    }


def build_report() -> dict[str, Any]:
    delta = load_json(DELTA_JSON)
    sequence = load_json(SEQUENCE_JSON)
    live_summary = load_json(LIVE_SUMMARY_JSON)
    rows = [row for row in delta.get("rows") or [] if isinstance(row, dict)]
    denominator = int(delta.get("future_denominator") or len(rows) or 0)
    live_baseline_cents = round(100.0 * fnum(live_summary.get("net_pnl_total_dollars")), 4)
    variants = [
        summarize_variant(name, rows, denominator, live_baseline_cents)
        for name in [
            "baseline",
            "shrink_high_cost_low_edge_50",
            "scale_strong_same_side_2x",
            "scale_mid_confidence_1p5x",
            "sequence_combo_strong2x_shrink50",
            "sequence_combo_mid1p5_shrink50",
            "continuous_edge_cost_weight",
        ]
    ]
    variants.sort(key=lambda row: fnum(row.get("adjusted_candidate_minus_live_cents")), reverse=True)
    best = variants[0] if variants else {}
    interpretation = [
        "This is diagnostic same-window exposure research, not a frozen candidate and not live-test approval.",
        "The probe tests observable exposure weights suggested by the sequence mechanism audit, without changing live bot logic.",
    ]
    if best:
        interpretation.append(
            f"Best diagnostic variant is {best.get('variant')} with {money(best.get('adjusted_candidate_net_cents'))} "
            f"candidate net and {money(best.get('adjusted_candidate_minus_live_cents'))} vs live on the same markets."
        )
    if best and "amplifies_losing_rows" in (best.get("blockers") or []):
        interpretation.append("Best variant amplifies at least one losing row, so path-risk and drawdown checks would be required before any freeze.")
    if best and "still_trails_live_same_window" in (best.get("blockers") or []):
        interpretation.append("Even the best diagnostic exposure rule still trails live on the same markets.")

    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "diagnostic_same_window_only",
        "freeze_ts_utc": delta.get("freeze_ts_utc"),
        "delta_autopsy_generated_at_utc": delta.get("generated_at_utc"),
        "sequence_mechanism_generated_at_utc": sequence.get("generated_at_utc"),
        "candidate_policy": delta.get("candidate_policy"),
        "future_denominator": denominator,
        "live_baseline_cents": live_baseline_cents,
        "sequence_mechanism_summary": sequence.get("mechanism_summary"),
        "variants": variants,
        "best_variant": best,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_variant") or {}
    lines = [
        "# v28 Dual-Lane State/Exposure Sequence Repair",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Best Variant",
            "",
            f"- Variant: `{best.get('variant')}`",
            f"- Entries/coverage: `{best.get('entries')}` / `{pct(best.get('coverage_pct'))}`",
            f"- Adjusted candidate net: `{money(best.get('adjusted_candidate_net_cents'))}`",
            f"- Same-window candidate-live: `{money(best.get('adjusted_candidate_minus_live_cents'))}`",
            f"- Delta vs baseline candidate: `{money(best.get('delta_vs_baseline_candidate_cents'))}`",
            f"- Full-loss cushion: `{best.get('full_loss_cushion')}`",
            f"- Weights changed / amplified losers / shrunk winners: `{best.get('weights_changed')}` / `{best.get('amplified_losing_rows')}` / `{best.get('shrunk_winning_rows')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or [])}`",
            "",
            "## Variants",
            "",
            "| variant | net | candidate-live | delta vs baseline | cushion | changed | amp losers | shrunk winners | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("variants") or []:
        lines.append(
            f"| `{row.get('variant')}` | {money(row.get('adjusted_candidate_net_cents'))} | "
            f"{money(row.get('adjusted_candidate_minus_live_cents'))} | "
            f"{money(row.get('delta_vs_baseline_candidate_cents'))} | {row.get('full_loss_cushion')} | "
            f"{row.get('weights_changed')} | {row.get('amplified_losing_rows')} | {row.get('shrunk_winning_rows')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Best Weighted Rows",
            "",
            "| market | side | net | live | adjusted | adjusted-live | weight | reason |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in best.get("weighted_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('candidate_side')} | {money(row.get('candidate_net_cents'))} | "
            f"{money(row.get('live_net_cents'))} | {money(row.get('adjusted_candidate_net_cents'))} | "
            f"{money(row.get('adjusted_candidate_minus_live_cents'))} | {fnum(row.get('exposure_weight'), 1.0):.3f} | "
            f"{row.get('weight_reason') or ''} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
