"""Guard refinement for the matched-unchanged exit-loss separator.

Research-only; no live bot changes or orders.

The first separator scan found a plausible exit-policy clue:

    abs_d_sigma <= 0.888798 AND exit_cents >= 51

On the full scored-exit denominator it is positive, but not clean: three rows
are harmful holds. This probe scans observable add-on guards inside that base
selection to find whether the harmful rows can be removed without throwing away
the physical clipped-winner signal.

All output is diagnostic only. A clean row here is a hypothesis for a future
frozen watch, not promotion evidence.
"""
from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_book_gap_candidates import hold_book_gap
from probe_v28_exit_policy_common_clock_watch import build_scored_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_matched_unchanged_loss_guard_refinement_latest.json"
OUT_MD = OUT_DIR / "v28_matched_unchanged_loss_guard_refinement_latest.md"

BASE_RULE = "abs_d_sigma <= 0.888798 AND exit_cents >= 51"
MIN_HELPFUL_ROWS = 5

NUMERIC_FEATURES = [
    "ask_cents",
    "eligible_depth",
    "exit_cents",
    "exit_fair_drawdown_cents",
    "exit_p_hold",
    "exit_sigma_t_dollars",
    "hold_book_gap",
    "p_side",
    "raw_edge_cents",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_feature(row: dict[str, Any], feature: str) -> float | None:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    mapping = {
        "abs_d_sigma": entry.get("mushroom_v28_abs_d_sigma"),
        "ask_cents": entry.get("mushroom_v28_ask_cents"),
        "eligible_depth": entry.get("mushroom_v28_eligible_depth"),
        "exit_cents": exit_features.get("mushroom_v28_exit_bid_cents") or row.get("exit_cents"),
        "exit_fair_drawdown_cents": exit_features.get("mushroom_v28_fair_drawdown_cents"),
        "exit_p_hold": exit_features.get("mushroom_v28_p_hold"),
        "exit_sigma_t_dollars": exit_features.get("mushroom_v28_sigma_t_dollars"),
        "hold_book_gap": hold_book_gap(row),
        "p_side": entry.get("mushroom_v28_p_side"),
        "raw_edge_cents": entry.get("mushroom_v28_raw_edge_cents"),
    }
    return fnum(mapping.get(feature))


def hold_delta(row: dict[str, Any]) -> float | None:
    current = fnum(row.get("actual_gross_cents"))
    hold = fnum(row.get("hold_gross_cents"))
    if current is None or hold is None:
        return None
    return hold - current


def base_selector(row: dict[str, Any]) -> bool:
    abs_d = row_feature(row, "abs_d_sigma")
    exit_cents = row_feature(row, "exit_cents")
    return abs_d is not None and exit_cents is not None and abs_d <= 0.888798 and exit_cents >= 51.0


def quantiles(values: list[float]) -> list[float]:
    vals = sorted(set(values))
    if not vals:
        return []
    idxs = {
        0,
        len(vals) // 5,
        len(vals) // 4,
        len(vals) // 3,
        len(vals) // 2,
        (len(vals) * 2) // 3,
        (len(vals) * 3) // 4,
        (len(vals) * 4) // 5,
        len(vals) - 1,
    }
    return [vals[idx] for idx in sorted(idxs)]


def pred_label(feature: str, op: str, threshold: float) -> str:
    return f"{feature} {op} {threshold:.6g}"


def pred_fn(feature: str, op: str, threshold: float) -> Callable[[dict[str, Any]], bool]:
    def check(row: dict[str, Any]) -> bool:
        value = row_feature(row, feature)
        if value is None:
            return False
        return value <= threshold if op == "<=" else value >= threshold

    return check


def build_predicates(rows: list[dict[str, Any]]) -> list[tuple[str, Callable[[dict[str, Any]], bool]]]:
    predicates: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    seen = set()
    for feature in NUMERIC_FEATURES:
        values = [row_feature(row, feature) for row in rows]
        clean = [float(value) for value in values if value is not None]
        for threshold in quantiles(clean):
            for op in ("<=", ">="):
                label = pred_label(feature, op, threshold)
                if label in seen:
                    continue
                seen.add(label)
                predicates.append((label, pred_fn(feature, op, threshold)))
    return predicates


def summarize(rows: list[dict[str, Any]], rule: str, base_rows: list[dict[str, Any]]) -> dict[str, Any]:
    current_vals = [fnum(row.get("actual_gross_cents")) or 0.0 for row in rows]
    hold_vals = [fnum(row.get("hold_gross_cents")) or 0.0 for row in rows]
    deltas = [float(hold_delta(row) or 0.0) for row in rows]
    helpful = [row for row in rows if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in rows if (hold_delta(row) or 0.0) < 0.0]
    flat = [row for row in rows if (hold_delta(row) or 0.0) == 0.0]
    base_harmful = [row for row in base_rows if (hold_delta(row) or 0.0) < 0.0]
    selected_keys = {row_key(row) for row in rows}
    removed_harmful = [row for row in base_harmful if row_key(row) not in selected_keys]
    return {
        "rule": rule,
        "selected_rows": len(rows),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "current_net_cents": sum(current_vals),
        "hold_net_cents": sum(hold_vals),
        "hold_delta_cents": sum(deltas),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "hold_losses": sum(1 for value in hold_vals if value < 0.0),
        "loss_count_reduction": (
            sum(1 for value in current_vals if value < 0.0)
            - sum(1 for value in hold_vals if value < 0.0)
        ),
        "worst_harm_cents": min([float(hold_delta(row) or 0.0) for row in harmful] or [0.0]),
        "removed_base_harmful_rows": len(removed_harmful),
        "largest_kept_helpful": compact_rows(helpful, reverse=True),
        "largest_kept_harmful": compact_rows(harmful, reverse=False),
        "removed_harmful_examples": compact_rows(removed_harmful, reverse=False),
    }


def row_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("market"), row.get("side"), row.get("entry_ts"))


def compact_rows(rows: list[dict[str, Any]], reverse: bool, limit: int = 6) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: float(hold_delta(row) or 0.0), reverse=reverse)
    out = []
    for row in ranked[:limit]:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "actual_gross_cents": row.get("actual_gross_cents"),
            "hold_gross_cents": row.get("hold_gross_cents"),
            "hold_delta_cents": hold_delta(row),
            "exit_reason": row.get("exit_reason"),
            "ask_cents": row_feature(row, "ask_cents"),
            "exit_cents": row_feature(row, "exit_cents"),
            "exit_p_hold": row_feature(row, "exit_p_hold"),
            "exit_fair_drawdown_cents": row_feature(row, "exit_fair_drawdown_cents"),
            "hold_book_gap": row_feature(row, "hold_book_gap"),
            "p_side": row_feature(row, "p_side"),
            "raw_edge_cents": row_feature(row, "raw_edge_cents"),
            "abs_d_sigma": row_feature(row, "abs_d_sigma"),
        })
    return out


def score(row: dict[str, Any]) -> tuple[int, int, float, int, int, float]:
    return (
        1 if int(row.get("harmful_rows") or 0) == 0 else 0,
        int(row.get("removed_base_harmful_rows") or 0),
        float(row.get("hold_delta_cents") or 0.0),
        int(row.get("loss_count_reduction") or 0),
        int(row.get("selected_rows") or 0),
        -abs(float(row.get("worst_harm_cents") or 0.0)),
    )


def scan(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicates = build_predicates(base_rows)
    rows: list[dict[str, Any]] = []
    for label, fn in predicates:
        selected = [row for row in base_rows if fn(row)]
        if len([row for row in selected if (hold_delta(row) or 0.0) > 0.0]) >= MIN_HELPFUL_ROWS:
            rows.append(summarize(selected, f"{BASE_RULE} AND {label}", base_rows))
    for (label_a, fn_a), (label_b, fn_b) in itertools.combinations(predicates, 2):
        if label_a == label_b:
            continue
        selected = [row for row in base_rows if fn_a(row) and fn_b(row)]
        if len([row for row in selected if (hold_delta(row) or 0.0) > 0.0]) >= MIN_HELPFUL_ROWS:
            rows.append(summarize(selected, f"{BASE_RULE} AND {label_a} AND {label_b}", base_rows))
    by_rule = {str(row.get("rule")): row for row in rows}
    return sorted(by_rule.values(), key=score, reverse=True)


def build_report() -> dict[str, Any]:
    scored_rows = build_scored_rows()
    base_rows = [row for row in scored_rows if base_selector(row) and hold_delta(row) is not None]
    base_summary = summarize(base_rows, BASE_RULE, base_rows)
    candidates = scan(base_rows)
    clean_candidates = [row for row in candidates if int(row.get("harmful_rows") or 0) == 0]
    report = {
        "generated_at_utc": utc_now_iso(),
        "base_rule": BASE_RULE,
        "base_summary": base_summary,
        "min_helpful_rows": MIN_HELPFUL_ROWS,
        "top_clean_guards": clean_candidates[:20],
        "top_overall_guards": candidates[:20],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    base = report.get("base_summary") or {}
    clean = report.get("top_clean_guards") or []
    notes = [
        "Research-only guard scan; this does not freeze, promote, or change an exit rule.",
        (
            f"Base separator selects {base.get('selected_rows')} full-denominator rows with "
            f"{base.get('helpful_rows')}/{base.get('harmful_rows')} helpful/harmful and "
            f"{base.get('hold_delta_cents')}c hold delta."
        ),
    ]
    if clean:
        best = clean[0]
        notes.append(
            f"Best clean guard is `{best.get('rule')}`: {best.get('selected_rows')} rows, "
            f"{best.get('helpful_rows')}/0 helpful/harmful, {best.get('hold_delta_cents')}c delta, "
            f"losses {best.get('current_losses')} -> {best.get('hold_losses')}."
        )
        notes.append(
            "This is still diagnostic-only because it was selected on historical denominator rows and needs its own frozen post-birth watch before trust."
        )
    else:
        notes.append("No zero-harm guard with enough helpful rows was found.")
    return notes


def money(value: Any) -> str:
    number = fnum(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "None"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    base = report.get("base_summary") or {}
    lines = [
        "# v28 Matched-Unchanged Loss Guard Refinement",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Base rule: `{report.get('base_rule')}`",
        f"- Base selected/helpful/harmful: `{base.get('selected_rows')}/{base.get('helpful_rows')}/{base.get('harmful_rows')}`",
        f"- Base hold delta: `{money(base.get('hold_delta_cents'))}`",
        f"- Minimum helpful rows for guard scan: `{report.get('min_helpful_rows')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Clean Guards",
        "",
        "| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | losses current -> hold | removed harmful | worst harm c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("top_clean_guards") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{money(row.get('current_net_cents'))} | {money(row.get('hold_net_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('current_losses')} -> {row.get('hold_losses')} | "
            f"{row.get('removed_base_harmful_rows')} | {money(row.get('worst_harm_cents'))} |"
        )
    lines.extend([
        "",
        "## Top Overall Guards",
        "",
        "| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | losses current -> hold | removed harmful | worst harm c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("top_overall_guards") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{money(row.get('current_net_cents'))} | {money(row.get('hold_net_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('current_losses')} -> {row.get('hold_losses')} | "
            f"{row.get('removed_base_harmful_rows')} | {money(row.get('worst_harm_cents'))} |"
        )
    best = (report.get("top_clean_guards") or [{}])[0]
    if best:
        lines.extend([
            "",
            "## Best Guard Kept Helpful Examples",
            "",
            "| market | side/result | actual | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("largest_kept_helpful") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
                f"{money(row.get('actual_gross_cents'))} | {money(row.get('hold_gross_cents'))} | "
                f"{money(row.get('hold_delta_cents'))} | {row.get('exit_reason')}@{fmt(row.get('exit_cents'))} | "
                f"{fmt(row.get('exit_p_hold'))} | {fmt(row.get('exit_fair_drawdown_cents'))} | "
                f"{fmt(row.get('hold_book_gap'))} | {fmt(row.get('p_side'))} | "
                f"{fmt(row.get('raw_edge_cents'))} | {fmt(row.get('abs_d_sigma'))} |"
            )
        lines.extend([
            "",
            "## Best Guard Removed Harmful Examples",
            "",
            "| market | side/result | actual | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("removed_harmful_examples") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
                f"{money(row.get('actual_gross_cents'))} | {money(row.get('hold_gross_cents'))} | "
                f"{money(row.get('hold_delta_cents'))} | {row.get('exit_reason')}@{fmt(row.get('exit_cents'))} | "
                f"{fmt(row.get('exit_p_hold'))} | {fmt(row.get('exit_fair_drawdown_cents'))} | "
                f"{fmt(row.get('hold_book_gap'))} | {fmt(row.get('p_side'))} | "
                f"{fmt(row.get('raw_edge_cents'))} | {fmt(row.get('abs_d_sigma'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
