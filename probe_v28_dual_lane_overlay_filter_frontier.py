"""Observable filter frontier for dual-lane-as-overlay.

Research-only; no live bot changes or orders.

This diagnostic tries to answer a narrow question: do observable candidate
features separate the rows where dual-lane improves live v28 from rows where it
clips live v28's big winners? It must not be used for promotion; any selected
filter needs its own freeze and forward proof.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_filter_frontier_latest.md"


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


def finite(row: dict[str, Any], field: str) -> float | None:
    value = fnum(row.get(field))
    return value if math.isfinite(value) else None


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    candidate = sum(fnum(row.get("candidate_net_cents"), 0.0) for row in rows)
    live = sum(fnum(row.get("live_net_cents"), 0.0) for row in rows)
    delta = sum(fnum(row.get("candidate_minus_live_cents"), 0.0) for row in rows)
    helpful = sum(1 for row in rows if fnum(row.get("candidate_minus_live_cents"), 0.0) > 0)
    harmful = sum(1 for row in rows if fnum(row.get("candidate_minus_live_cents"), 0.0) < 0)
    return {
        "rows": len(rows),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "candidate_net_cents": candidate,
        "live_net_cents": live,
        "candidate_minus_live_cents": delta,
        "helpful_rows": helpful,
        "harmful_rows": harmful,
        "helpful_share": helpful / len(rows) if rows else None,
        "candidate_full_loss_cushion": int(max(0.0, candidate) // 100.0),
        "delta_full_loss_cushion": int(max(0.0, delta) // 100.0),
        "source_counts": {
            source: sum(1 for row in rows if str(row.get("candidate_source")) == source)
            for source in sorted({str(row.get("candidate_source")) for row in rows})
        },
        "bucket_counts": {
            bucket: sum(1 for row in rows if str(row.get("comparison_bucket")) == bucket)
            for bucket in sorted({str(row.get("comparison_bucket")) for row in rows})
        },
    }


def row_passes(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if rule.get("side") and row.get("candidate_side") != rule["side"]:
        return False
    if rule.get("component") and row.get("candidate_component") != rule["component"]:
        return False
    if rule.get("allow_reconstructed") is False and row.get("candidate_source") != "approved_entry":
        return False
    for field, op, threshold in rule.get("comparisons") or []:
        value = finite(row, field)
        if value is None:
            if rule.get("missing_numeric_pass") is True:
                continue
            return False
        if op == ">=" and value < threshold:
            return False
        if op == "<=" and value > threshold:
            return False
        if op == ">" and value <= threshold:
            return False
        if op == "<" and value >= threshold:
            return False
    return True


def apply_rule(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in rows if row_passes(row, rule)]


def rule_label(rule: dict[str, Any]) -> str:
    parts = []
    if rule.get("side"):
        parts.append(f"side={rule['side']}")
    if rule.get("component"):
        parts.append(str(rule["component"]).replace(":", "="))
    if rule.get("allow_reconstructed") is False:
        parts.append("approved_only")
    if rule.get("missing_numeric_pass") is True:
        parts.append("missing_numeric_ok")
    for field, op, threshold in rule.get("comparisons") or []:
        parts.append(f"{field}{op}{threshold}")
    return "__".join(parts) or "all_rows"


def candidate_rules() -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = [
        {"name": "all_rows", "comparisons": []},
        {"name": "approved_only", "allow_reconstructed": False, "comparisons": []},
        {"name": "no_side_only", "side": "no", "comparisons": []},
        {"name": "yes_side_only", "side": "yes", "comparisons": []},
        {"name": "parent_only", "component": "strict_parent_midprice_hold_fill", "comparisons": []},
        {
            "name": "sidecar_only",
            "component": "continuous_penalty:cheap_penalty025_rank_only",
            "missing_numeric_pass": True,
            "comparisons": [],
        },
    ]
    raw_mins = [0.05, 0.08, 0.10, 0.12]
    raw_maxes = [0.09, 0.12, 0.15]
    recross_maxes = [0.30, 0.40, 0.50, 0.60]
    recross_mins = [0.25, 0.35, 0.45]
    ask_mins = [0.75, 0.78, 0.80]
    ask_maxes = [0.78, 0.82, 0.86]
    abs_mins = [0.85, 0.90, 0.95, 1.00]
    for raw_min, recross_max, abs_min in product(raw_mins, recross_maxes, abs_mins):
        rules.append(
            {
                "name": f"raw{raw_min}_recross_le{recross_max}_abs{abs_min}",
                "comparisons": [
                    ("raw_edge", ">=", raw_min),
                    ("recross_hazard_score", "<=", recross_max),
                    ("abs_d_sigma", ">=", abs_min),
                ],
            }
        )
    for raw_max, ask_min in product(raw_maxes, ask_mins):
        rules.append(
            {
                "name": f"high_cost_low_edge_raw_le{raw_max}_ask_ge{ask_min}",
                "component": "strict_parent_midprice_hold_fill",
                "comparisons": [
                    ("raw_edge", "<=", raw_max),
                    ("ask_prob", ">=", ask_min),
                ],
            }
        )
    for recross_min, ask_max in product(recross_mins, ask_maxes):
        rules.append(
            {
                "name": f"recross_ge{recross_min}_ask_le{ask_max}",
                "comparisons": [
                    ("recross_hazard_score", ">=", recross_min),
                    ("ask_prob", "<=", ask_max),
                ],
            }
        )
    for side in ("yes", "no"):
        for recross_max in recross_maxes:
            rules.append(
                {
                    "name": f"{side}_recross_le{recross_max}",
                    "side": side,
                    "comparisons": [("recross_hazard_score", "<=", recross_max)],
                }
            )
    return rules


def build_report() -> dict[str, Any]:
    compare = load_json(COMPARE_JSON)
    rows = [row for row in compare.get("comparison_rows") or [] if isinstance(row, dict)]
    denominator = int(compare.get("future_denominator") or len(rows) or 0)
    results = []
    for rule in candidate_rules():
        selected = apply_rule(rows, rule)
        summary = summarize(selected, denominator)
        if not selected:
            continue
        blockers = []
        if summary["rows"] < 3:
            blockers.append("rows_lt_3")
        if fnum(summary["candidate_minus_live_cents"], 0.0) <= 0:
            blockers.append("delta_not_positive")
        if fnum(summary["candidate_net_cents"], 0.0) <= 0:
            blockers.append("candidate_net_not_positive")
        if fnum(summary["coverage_pct"], 0.0) < 25.0:
            blockers.append("diagnostic_coverage_lt_25pct")
        if fnum(summary["helpful_share"], 0.0) < 0.70:
            blockers.append("helpful_share_lt_70pct")
        results.append(
            {
                "rule": rule,
                "label": rule.get("name") or rule_label(rule),
                "summary": summary,
                "blockers": blockers,
                "selected_markets": [row.get("market") for row in selected],
                "selected_buckets": [row.get("comparison_bucket") for row in selected],
            }
        )
    results.sort(
        key=lambda item: (
            len(item.get("blockers") or []),
            -fnum((item.get("summary") or {}).get("candidate_minus_live_cents"), -999999.0),
            -fnum((item.get("summary") or {}).get("helpful_share"), 0.0),
        )
    )
    viable = [item for item in results if not item.get("blockers")]
    best = results[0] if results else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "compare_generated_at_utc": compare.get("generated_at_utc"),
        "promotion_use": "diagnostic_only_filter_design",
        "future_denominator": denominator,
        "rows_available": len(rows),
        "rules_tested": len(results),
        "viable_diagnostic_rules": len(viable),
        "best_rule": best,
        "top_rules": results[:20],
        "read": [
            "This is not promotion evidence; it is a filter-design audit over a tiny same-window sample.",
            "A useful deployable overlay needs an observable filter, then a separate own-freeze watch.",
            "If top filters require hindsight-like separation or tiny coverage, dual-lane is not yet live-ready as an overlay.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    best = report.get("best_rule") if isinstance(report.get("best_rule"), dict) else {}
    best_summary = best.get("summary") if isinstance(best.get("summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Overlay Filter Frontier",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Same-window compare UTC: `{report.get('compare_generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Rows available / denominator: `{report.get('rows_available')}` / `{report.get('future_denominator')}`",
        f"- Rules tested: `{report.get('rules_tested')}`",
        f"- Viable diagnostic rules: `{report.get('viable_diagnostic_rules')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Best Diagnostic Rule",
            "",
            f"- Label: `{best.get('label')}`",
            f"- Rows/coverage: `{best_summary.get('rows')}` / `{pct(best_summary.get('coverage_pct'))}`",
            f"- Candidate/live/delta: `{money(best_summary.get('candidate_net_cents'))}` / `{money(best_summary.get('live_net_cents'))}` / `{money(best_summary.get('candidate_minus_live_cents'))}`",
            f"- Helpful/harmful/share: `{best_summary.get('helpful_rows')}` / `{best_summary.get('harmful_rows')}` / `{pct(100.0 * fnum(best_summary.get('helpful_share')) if best_summary.get('helpful_share') is not None else None)}`",
            f"- Blockers: `{', '.join(str(item) for item in best.get('blockers') or []) or 'none'}`",
            f"- Selected markets: `{best.get('selected_markets')}`",
            "",
            "## Top Rules",
            "",
            "| rank | rule | rows | coverage | cand net | live net | delta | helpful | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, item in enumerate(report.get("top_rules") or [], 1):
        if not isinstance(item, dict):
            continue
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        helpful_share = summary.get("helpful_share")
        lines.append(
            f"| {idx} | `{item.get('label')}` | {summary.get('rows')} | {pct(summary.get('coverage_pct'))} | "
            f"{money(summary.get('candidate_net_cents'))} | {money(summary.get('live_net_cents'))} | "
            f"{money(summary.get('candidate_minus_live_cents'))} | "
            f"{pct(100.0 * fnum(helpful_share) if helpful_share is not None else None)} | "
            f"{', '.join(str(blocker) for blocker in item.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
