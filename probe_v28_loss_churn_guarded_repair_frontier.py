"""Guarded diagnostic frontier for v28 loss-count churn repairs.

Research-only; no live bot changes or orders.

This looks only at losing live/control rows and asks which observable exit/entry
features separate hold-helpful clipped-winner losses from hold-harmful FV/entry
losers. It is a prioritizer for future frozen exit children, not promotion
evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
GAP_CLASSIFIER_JSON = OUT_DIR / "v28_exit_repair_gap_classifier_latest.json"
OUT_JSON = OUT_DIR / "v28_loss_churn_guarded_repair_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_loss_churn_guarded_repair_frontier_latest.md"


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


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = row.get("actual_gross_cents")
    hold = row.get("hold_gross_cents")
    if actual is None or hold is None:
        return None
    return fnum(hold) - fnum(actual)


def is_known(row: dict[str, Any]) -> bool:
    return hold_delta(row) is not None


def is_hold_helpful(row: dict[str, Any]) -> bool:
    delta = hold_delta(row)
    return delta is not None and delta > 0


def is_hold_harmful(row: dict[str, Any]) -> bool:
    delta = hold_delta(row)
    return delta is not None and delta < 0


def flips_loss(row: dict[str, Any]) -> bool:
    return is_hold_helpful(row) and fnum(row.get("hold_gross_cents")) >= 0


def tags(row: dict[str, Any]) -> set[str]:
    return {str(tag) for tag in row.get("physics_tags") or []}


def value(row: dict[str, Any], field: str) -> float | None:
    if field == "p_hold":
        return fnum((row.get("best_policy_effect") or {}).get("p_hold"), None)  # type: ignore[arg-type]
    if field == "exit_cents":
        best = row.get("best_policy_effect") or {}
        if best.get("exit_cents") is not None:
            return fnum(best.get("exit_cents"))
        if row.get("exit_cents") is not None:
            return fnum(row.get("exit_cents"))
        return None
    if row.get(field) is None:
        return None
    return fnum(row.get(field))


RuleFn = Callable[[dict[str, Any]], bool]


def threshold_rule(label: str, field: str, op: str, threshold: float) -> tuple[str, RuleFn]:
    def predicate(row: dict[str, Any]) -> bool:
        val = value(row, field)
        if val is None:
            return False
        if op == "ge":
            return val >= threshold
        if op == "le":
            return val <= threshold
        return False

    return label, predicate


def tag_rule(label: str, tag: str, present: bool = True) -> tuple[str, RuleFn]:
    def predicate(row: dict[str, Any]) -> bool:
        has_tag = tag in tags(row)
        return has_tag if present else not has_tag

    return label, predicate


def base_rules() -> list[tuple[str, RuleFn]]:
    rules: list[tuple[str, RuleFn]] = [
        tag_rule("tag_near_boundary", "near_boundary"),
        tag_rule("tag_recross_high", "recross_hazard_high"),
        tag_rule("tag_thin_raw_edge", "thin_raw_edge"),
        tag_rule("tag_rich_entry", "rich_entry"),
        tag_rule("tag_crowded_depth", "crowded_depth"),
        tag_rule("tag_thin_touch_depth", "thin_touch_depth"),
        tag_rule("not_fv_entry_timing", "fv_or_entry_timing_error", present=False),
        tag_rule("not_medium_25_49", "medium_25_49c", present=False),
        threshold_rule("p_hold_ge_075", "p_hold", "ge", 0.75),
        threshold_rule("p_hold_ge_060", "p_hold", "ge", 0.60),
        threshold_rule("p_hold_le_060", "p_hold", "le", 0.60),
        threshold_rule("exit_cents_ge_60", "exit_cents", "ge", 60),
        threshold_rule("exit_cents_ge_50", "exit_cents", "ge", 50),
        threshold_rule("exit_cents_le_40", "exit_cents", "le", 40),
        threshold_rule("ask_cents_ge_70", "ask_cents", "ge", 70),
        threshold_rule("ask_cents_ge_80", "ask_cents", "ge", 80),
        threshold_rule("raw_edge_cents_le_10", "raw_edge_cents", "le", 10),
        threshold_rule("raw_edge_cents_ge_15", "raw_edge_cents", "ge", 15),
        threshold_rule("recross_ge_030", "recross_hazard_score", "ge", 0.30),
        threshold_rule("recross_ge_045", "recross_hazard_score", "ge", 0.45),
        threshold_rule("depth_lte_384", "eligible_depth", "le", 384),
        threshold_rule("depth_lte_150", "eligible_depth", "le", 150),
        threshold_rule("absd_ge_085", "abs_d_sigma", "ge", 0.85),
    ]
    return rules


def evaluate(label: str, predicate: RuleFn, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    selected = [row for row in rows if predicate(row)]
    if not selected:
        return None
    helpful = [row for row in selected if is_hold_helpful(row)]
    harmful = [row for row in selected if is_hold_harmful(row)]
    unknown = [row for row in selected if not is_known(row)]
    flipped = [row for row in selected if flips_loss(row)]
    actual_loss = sum(fnum(row.get("actual_gross_cents")) for row in selected)
    hold_net = sum(fnum(row.get("hold_gross_cents")) for row in selected if row.get("hold_gross_cents") is not None)
    delta = sum(hold_delta(row) or 0.0 for row in selected)
    helpful_delta = sum(hold_delta(row) or 0.0 for row in helpful)
    harmful_delta = sum(hold_delta(row) or 0.0 for row in harmful)
    blockers: list[str] = ["diagnostic_loss_rows_only", "not_frozen_forward", "needs_full_denominator_replay"]
    if harmful:
        blockers.append("hold_harmful_rows_present")
    if unknown:
        blockers.append("hold_unknown_rows_present")
    if len(selected) < 10:
        blockers.append("selected_loss_rows_lt_10")
    if len(flipped) < 3:
        blockers.append("loss_flips_lt_3")
    if delta <= 0:
        blockers.append("hold_delta_not_positive")
    return {
        "rule": label,
        "selected_loss_rows": len(selected),
        "actual_loss_cents": actual_loss,
        "hold_net_cents": hold_net,
        "hold_delta_cents": delta,
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "unknown_rows": len(unknown),
        "loss_flips": len(flipped),
        "helpful_delta_cents": helpful_delta,
        "harmful_delta_cents": harmful_delta,
        "blockers": blockers,
        "examples": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "hold_delta_cents": hold_delta(row),
                "failure_class": row.get("failure_class"),
                "escape_class": row.get("escape_class"),
                "tags": row.get("physics_tags") or [],
            }
            for row in sorted(selected, key=lambda item: hold_delta(item) or 0.0)[:8]
        ],
    }


def build_report() -> dict[str, Any]:
    loss_escape = load_json(LOSS_ESCAPE_JSON)
    gap = load_json(GAP_CLASSIFIER_JSON)
    rows = [row for row in loss_escape.get("loss_rows_with_details") or [] if isinstance(row, dict)]
    known_rows = [row for row in rows if is_known(row)]
    unresolved = [
        row for row in known_rows
        if row.get("escape_class") in {"loss_escapes_current_exit_repairs", "no_exit_repair_observation"}
    ]
    rules = base_rules()
    candidates: list[tuple[str, RuleFn]] = list(rules)
    for (left_label, left), (right_label, right) in combinations(rules, 2):
        candidates.append((f"{left_label}__and__{right_label}", lambda row, l=left, r=right: l(row) and r(row)))
    evaluated = [result for label, predicate in candidates if (result := evaluate(label, predicate, unresolved))]
    evaluated.sort(
        key=lambda row: (
            -int(row.get("harmful_rows") or 0),
            int(row.get("unknown_rows") or 0),
            -float(row.get("loss_flips") or 0),
            -float(row.get("hold_delta_cents") or 0),
        )
    )
    clean = [
        row for row in evaluated
        if not row.get("harmful_rows") and not row.get("unknown_rows") and fnum(row.get("hold_delta_cents")) > 0
    ]
    clean.sort(key=lambda row: (-(row.get("loss_flips") or 0), -fnum(row.get("hold_delta_cents")), -(row.get("selected_loss_rows") or 0)))
    diagnostic_only_tokens = ("not_fv_entry_timing", "not_medium_25_49")
    observable_clean = [
        row for row in clean
        if not any(token in str(row.get("rule") or "") for token in diagnostic_only_tokens)
    ]
    observable_clean.sort(
        key=lambda row: (-(row.get("loss_flips") or 0), -fnum(row.get("hold_delta_cents")), -(row.get("selected_loss_rows") or 0))
    )
    risky = [row for row in evaluated if row.get("harmful_rows")]
    risky.sort(key=lambda row: (-fnum(row.get("hold_delta_cents")), fnum(row.get("harmful_delta_cents"))))
    summary = gap.get("summary") or {}
    interpretation = [
        "This is a diagnostic loss-row frontier, not a candidate or live exit rule.",
        "Rules are evaluated only on losing rows with known hold outcomes; any useful row needs full-denominator replay and its own freeze.",
    ]
    if clean:
        best = clean[0]
        interpretation.append(
            f"Best clean diagnostic guard is {best.get('rule')} with {best.get('loss_flips')} loss flips, "
            f"{best.get('selected_loss_rows')} selected loss rows, and {money(best.get('hold_delta_cents'))} hold delta."
        )
    if observable_clean:
        best_obs = observable_clean[0]
        interpretation.append(
            f"Best observable-only clean guard is {best_obs.get('rule')} with {best_obs.get('loss_flips')} loss flips, "
            f"{best_obs.get('selected_loss_rows')} selected loss rows, and {money(best_obs.get('hold_delta_cents'))} hold delta."
        )
    else:
        interpretation.append("No observable-only clean guard survived; clean separation currently depends on diagnostic labels.")
    if risky:
        interpretation.append(
            f"Top risky rules still show false-hold exposure; worst selected examples should remain guardrail material."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "diagnostic_loss_rows_only",
        "loss_escape_generated_at_utc": loss_escape.get("generated_at_utc"),
        "gap_classifier_generated_at_utc": gap.get("generated_at_utc"),
        "gap_summary": summary,
        "known_loss_rows": len(known_rows),
        "unresolved_known_loss_rows": len(unresolved),
        "clean_frontier": clean[:20],
        "observable_clean_frontier": observable_clean[:20],
        "risky_frontier": risky[:20],
        "all_evaluated_count": len(evaluated),
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Loss-Churn Guarded Repair Frontier",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Known loss rows / unresolved known rows: `{report.get('known_loss_rows')}` / `{report.get('unresolved_known_loss_rows')}`",
        f"- Evaluated rules: `{report.get('all_evaluated_count')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Clean Diagnostic Frontier",
            "",
            "| rule | selected losses | flips | hold delta | helpful/harmful/unknown | blockers |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("clean_frontier") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_loss_rows')} | {row.get('loss_flips')} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('unknown_rows')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Observable-Only Clean Frontier",
            "",
            "| rule | selected losses | flips | hold delta | helpful/harmful/unknown | blockers |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("observable_clean_frontier") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_loss_rows')} | {row.get('loss_flips')} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('unknown_rows')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Risky High-Delta Frontier",
            "",
            "| rule | selected losses | flips | hold delta | helpful/harmful/unknown | harmful delta | blockers |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("risky_frontier") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_loss_rows')} | {row.get('loss_flips')} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('unknown_rows')} | "
            f"{money(row.get('harmful_delta_cents'))} | {', '.join(row.get('blockers') or [])} |"
        )
    best = (report.get("clean_frontier") or [{}])[0]
    if best:
        lines.extend(["", "## Best Clean Examples", "", "| market | side | actual | hold | delta | failure | escape | tags |", "|---|---|---:|---:|---:|---|---|---|"])
        for row in best.get("examples") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {money(row.get('actual_gross_cents'))} | "
                f"{money(row.get('hold_gross_cents'))} | {money(row.get('hold_delta_cents'))} | "
                f"`{row.get('failure_class')}` | `{row.get('escape_class')}` | {', '.join(row.get('tags') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
