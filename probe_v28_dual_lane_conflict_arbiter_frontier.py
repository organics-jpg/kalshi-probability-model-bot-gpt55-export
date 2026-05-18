"""Observable conflict-arbiter frontier for dual-lane coordinator work.

Research-only. This does not place orders, stop the live bot, or change live
bot behavior.

The paper coordinator replay showed that same-side rows are roughly neutral to
slightly helpful, while live side-flip rows are the large deficit. This probe
tests simple observable suppress/allow rules over the current same-window rows
to find candidate arbitration shapes for a future single-process coordinator.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_conflict_arbiter_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_conflict_arbiter_frontier_latest.md"


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def money(value: Any) -> str:
    cents = fnum(value, 0.0)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    number = fnum(value)
    if not math.isfinite(number):
        return "n/a"
    return f"{number:.2f}%"


def live_conflict(row: dict[str, Any]) -> str:
    live_trades = int(fnum(row.get("live_trade_count"), 0.0))
    candidate_side = str(row.get("candidate_side") or "")
    live_sides = {item for item in str(row.get("live_sides") or "").split(",") if item}
    if live_trades <= 0:
        return "dual_lane_only"
    if len(live_sides) > 1:
        return "same_market_live_side_flip"
    if candidate_side in live_sides:
        return "same_market_same_side"
    return "same_market_opposite_side"


def raw_missing_or_le(row: dict[str, Any], threshold: float) -> bool:
    raw = fnum(row.get("raw_edge"))
    return (not math.isfinite(raw)) or raw <= threshold


def suppresses(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    name = str(rule.get("name") or "")
    ask = fnum(row.get("ask_prob"))
    recross = fnum(row.get("recross_hazard_score"))
    raw = fnum(row.get("raw_edge"))
    side = str(row.get("candidate_side") or "")
    component = str(row.get("candidate_component") or "")
    source = str(row.get("candidate_source") or "")

    if name == "none":
        return False
    if name == "high_cost_recross":
        return ask >= rule["ask_min"] and recross >= rule["recross_min"]
    if name == "high_cost_low_or_missing_raw":
        return ask >= rule["ask_min"] and raw_missing_or_le(row, rule["raw_max"])
    if name == "yes_high_cost":
        return side == "yes" and ask >= rule["ask_min"]
    if name == "yes_recross":
        return side == "yes" and recross >= rule["recross_min"]
    if name == "delayed_recheck_recross":
        return "strict_delayed_recheck_rescue" in component and recross >= rule["recross_min"]
    if name == "continuous_high_cost":
        return "continuous_penalty" in component and ask >= rule["ask_min"]
    if name == "rejected_high_cost":
        return source == "rejected_actionable" and ask >= rule["ask_min"]
    if name == "high_cost_low_raw_or_yes":
        return ask >= rule["ask_min"] and (raw_missing_or_le(row, rule["raw_max"]) or side == "yes")
    if name == "recross_cost_combo":
        cost_pressure = max(0.0, ask - rule["ask_base"]) + max(0.0, recross - rule["recross_base"])
        return cost_pressure >= rule["combo_min"]
    return False


def candidate_rules() -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = [{"name": "none", "label": "allow_all"}]
    for ask_min, recross_min in product([0.78, 0.80, 0.82, 0.85], [0.25, 0.30, 0.35, 0.40]):
        rules.append(
            {
                "name": "high_cost_recross",
                "label": f"suppress_ask_ge{ask_min}_recross_ge{recross_min}",
                "ask_min": ask_min,
                "recross_min": recross_min,
            }
        )
    for ask_min, raw_max in product([0.78, 0.80, 0.82, 0.85], [0.05, 0.07, 0.09, 0.12]):
        rules.append(
            {
                "name": "high_cost_low_or_missing_raw",
                "label": f"suppress_ask_ge{ask_min}_raw_missing_or_le{raw_max}",
                "ask_min": ask_min,
                "raw_max": raw_max,
            }
        )
    for ask_min in [0.78, 0.80, 0.82, 0.85]:
        rules.append({"name": "yes_high_cost", "label": f"suppress_yes_ask_ge{ask_min}", "ask_min": ask_min})
        rules.append(
            {
                "name": "continuous_high_cost",
                "label": f"suppress_continuous_ask_ge{ask_min}",
                "ask_min": ask_min,
            }
        )
        rules.append({"name": "rejected_high_cost", "label": f"suppress_rejected_ask_ge{ask_min}", "ask_min": ask_min})
    for recross_min in [0.25, 0.30, 0.35, 0.40]:
        rules.append(
            {
                "name": "yes_recross",
                "label": f"suppress_yes_recross_ge{recross_min}",
                "recross_min": recross_min,
            }
        )
        rules.append(
            {
                "name": "delayed_recheck_recross",
                "label": f"suppress_delayed_recheck_recross_ge{recross_min}",
                "recross_min": recross_min,
            }
        )
    for ask_min, raw_max in product([0.78, 0.80, 0.82], [0.07, 0.09, 0.12]):
        rules.append(
            {
                "name": "high_cost_low_raw_or_yes",
                "label": f"suppress_ask_ge{ask_min}_raw_missing_or_le{raw_max}_or_yes",
                "ask_min": ask_min,
                "raw_max": raw_max,
            }
        )
    for combo_min in [0.04, 0.06, 0.08, 0.10]:
        rules.append(
            {
                "name": "recross_cost_combo",
                "label": f"suppress_cost_recross_combo_ge{combo_min}",
                "ask_base": 0.78,
                "recross_base": 0.30,
                "combo_min": combo_min,
            }
        )
    return rules


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    candidate = sum(fnum(row.get("candidate_net_cents"), 0.0) for row in rows)
    live = sum(fnum(row.get("live_net_cents"), 0.0) for row in rows)
    delta = sum(fnum(row.get("candidate_minus_live_cents"), 0.0) for row in rows)
    return {
        "rows": len(rows),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "candidate_net_cents": candidate,
        "live_net_cents": live,
        "candidate_minus_live_cents": delta,
        "wins": sum(1 for row in rows if fnum(row.get("candidate_net_cents"), 0.0) > 0),
        "losses": sum(1 for row in rows if fnum(row.get("candidate_net_cents"), 0.0) < 0),
        "full_loss_cushion": int(max(0.0, candidate) // 100.0),
        "source_counts": {
            source: sum(1 for row in rows if str(row.get("candidate_source")) == source)
            for source in sorted({str(row.get("candidate_source")) for row in rows})
        },
        "conflict_counts": {
            conflict: sum(1 for row in rows if live_conflict(row) == conflict)
            for conflict in sorted({live_conflict(row) for row in rows})
        },
    }


def evaluate_rule(rows: list[dict[str, Any]], denominator: int, rule: dict[str, Any]) -> dict[str, Any]:
    allowed = [row for row in rows if not suppresses(row, rule)]
    suppressed = [row for row in rows if suppresses(row, rule)]
    allowed_summary = summarize(allowed, denominator)
    suppressed_summary = summarize(suppressed, denominator)
    side_flip_total = sum(1 for row in rows if live_conflict(row) == "same_market_live_side_flip")
    side_flip_suppressed = sum(1 for row in suppressed if live_conflict(row) == "same_market_live_side_flip")
    blockers = ["diagnostic_only_not_frozen_forward"]
    if allowed_summary["rows"] < 3:
        blockers.append("allowed_rows_lt_3")
    if fnum(allowed_summary["candidate_net_cents"], 0.0) <= 0:
        blockers.append("allowed_candidate_net_not_positive")
    if fnum(allowed_summary["candidate_minus_live_cents"], 0.0) <= 0:
        blockers.append("allowed_delta_not_positive")
    if int(allowed_summary["full_loss_cushion"]) < 1:
        blockers.append("allowed_full_loss_cushion_lt_1")
    if side_flip_total and side_flip_suppressed < side_flip_total:
        blockers.append("does_not_suppress_all_current_side_flips")
    if fnum(allowed_summary["coverage_pct"], 0.0) < 25.0:
        blockers.append("allowed_coverage_lt_25pct")
    return {
        "rule": rule,
        "label": rule.get("label") or rule.get("name"),
        "allowed_summary": allowed_summary,
        "suppressed_summary": suppressed_summary,
        "side_flip_total": side_flip_total,
        "side_flip_suppressed": side_flip_suppressed,
        "blockers": blockers,
        "allowed_markets": [row.get("market") for row in allowed],
        "suppressed_markets": [row.get("market") for row in suppressed],
    }


def build_report() -> dict[str, Any]:
    compare = load_json(COMPARE_JSON)
    rows = [row for row in compare.get("comparison_rows") or [] if isinstance(row, dict)]
    denominator = int(compare.get("future_denominator") or len(rows) or 0)
    results = [evaluate_rule(rows, denominator, rule) for rule in candidate_rules()]
    results.sort(
        key=lambda item: (
            len(item.get("blockers") or []),
            -fnum((item.get("allowed_summary") or {}).get("candidate_minus_live_cents"), -999999.0),
            -fnum((item.get("allowed_summary") or {}).get("candidate_net_cents"), -999999.0),
            -int(item.get("side_flip_suppressed") or 0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "diagnostic_conflict_arbiter_design_only",
        "compare_generated_at_utc": compare.get("generated_at_utc"),
        "candidate_policy": compare.get("candidate_policy"),
        "future_denominator": denominator,
        "rows_available": len(rows),
        "rules_tested": len(results),
        "best_rule": results[0] if results else {},
        "top_rules": results[:20],
        "read": [
            "This is not promotion evidence; it is a same-window design audit.",
            "A deployable arbiter must use only observable pre-entry features and then get its own freeze.",
            "The desired physical mechanism is suppressing high-cost/path-unstable rows where live v28 may need side-flip state management.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    best = report.get("best_rule") if isinstance(report.get("best_rule"), dict) else {}
    allowed = best.get("allowed_summary") if isinstance(best.get("allowed_summary"), dict) else {}
    suppressed = best.get("suppressed_summary") if isinstance(best.get("suppressed_summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Conflict-Arbiter Frontier",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Same-window compare UTC: `{report.get('compare_generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Rows available / denominator: `{report.get('rows_available')}` / `{report.get('future_denominator')}`",
        f"- Rules tested: `{report.get('rules_tested')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Best Diagnostic Arbiter",
            "",
            f"- Rule: `{best.get('label')}`",
            f"- Allowed rows/coverage: `{allowed.get('rows')}` / `{pct(allowed.get('coverage_pct'))}`",
            f"- Allowed candidate/live/delta: `{money(allowed.get('candidate_net_cents'))}` / `{money(allowed.get('live_net_cents'))}` / `{money(allowed.get('candidate_minus_live_cents'))}`",
            f"- Allowed W/L/cushion: `{allowed.get('wins')}/{allowed.get('losses')}` / `{allowed.get('full_loss_cushion')}`",
            f"- Suppressed rows candidate/live/delta: `{suppressed.get('rows')}` / `{money(suppressed.get('candidate_net_cents'))}` / `{money(suppressed.get('live_net_cents'))}` / `{money(suppressed.get('candidate_minus_live_cents'))}`",
            f"- Side-flips suppressed: `{best.get('side_flip_suppressed')}` / `{best.get('side_flip_total')}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            f"- Suppressed markets: `{best.get('suppressed_markets')}`",
            "",
            "## Top Rules",
            "",
            "| rank | rule | allowed rows | allowed cov | allowed net | live net | delta | suppressed rows | side-flips | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, item in enumerate(report.get("top_rules") or [], 1):
        if not isinstance(item, dict):
            continue
        allowed_summary = item.get("allowed_summary") if isinstance(item.get("allowed_summary"), dict) else {}
        suppressed_summary = item.get("suppressed_summary") if isinstance(item.get("suppressed_summary"), dict) else {}
        lines.append(
            f"| {idx} | `{item.get('label')}` | {allowed_summary.get('rows')} | "
            f"{pct(allowed_summary.get('coverage_pct'))} | {money(allowed_summary.get('candidate_net_cents'))} | "
            f"{money(allowed_summary.get('live_net_cents'))} | {money(allowed_summary.get('candidate_minus_live_cents'))} | "
            f"{suppressed_summary.get('rows')} | {item.get('side_flip_suppressed')}/{item.get('side_flip_total')} | "
            f"{', '.join(str(blocker) for blocker in item.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
