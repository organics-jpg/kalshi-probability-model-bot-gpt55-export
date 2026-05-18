"""Observable separator scan for matched-but-unchanged v28 loss rows.

Research-only; no live bot changes or orders.

The exit-repair gap classifier shows many losing control rows have matching
frozen exit observations but are unchanged by the current repair family. This
probe asks whether observable entry/exit features separate rows where holding
would have helped from rows where holding would have made the loss worse.

All rows here are historical diagnostic rows. A clean diagnostic separator is
only a hypothesis for a future frozen watch, not promotion evidence.
"""
from __future__ import annotations

import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_policy_common_clock_watch import build_scored_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
OUT_JSON = OUT_DIR / "v28_matched_unchanged_loss_separator_latest.json"
OUT_MD = OUT_DIR / "v28_matched_unchanged_loss_separator_latest.md"

NUMERIC_FEATURES = [
    "abs_d_sigma",
    "ask_cents",
    "eligible_depth",
    "exit_cents",
    "p_side",
    "raw_edge_cents",
    "recross_hazard_score",
]

OBSERVABLE_TAGS = [
    "near_boundary",
    "recross_hazard_high",
    "thin_raw_edge",
    "rich_entry",
    "crowded_depth",
    "thin_touch_depth",
]


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


def fnum(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_feature(row: dict[str, Any], feature: str) -> float | None:
    direct = fnum(row.get(feature))
    if direct is not None:
        return direct
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    mapping = {
        "abs_d_sigma": entry.get("mushroom_v28_abs_d_sigma"),
        "ask_cents": entry.get("mushroom_v28_ask_cents"),
        "eligible_depth": entry.get("mushroom_v28_eligible_depth"),
        "exit_cents": exit_features.get("mushroom_v28_exit_bid_cents") or row.get("exit_cents"),
        "p_side": entry.get("mushroom_v28_p_side"),
        "raw_edge_cents": entry.get("mushroom_v28_raw_edge_cents"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }
    return fnum(mapping.get(feature))


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = fnum(row.get("actual_gross_cents"))
    hold = fnum(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def is_matched_unchanged(row: dict[str, Any]) -> bool:
    return row.get("escape_class") == "loss_escapes_current_exit_repairs"


def clean_rows(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if not isinstance(row, dict) or not is_matched_unchanged(row):
            continue
        if hold_delta(row) is None:
            continue
        out.append(row)
    return out


def quantiles(values: list[float]) -> list[float]:
    vals = sorted(set(values))
    if not vals:
        return []
    idxs = {
        0,
        len(vals) // 4,
        len(vals) // 3,
        len(vals) // 2,
        (len(vals) * 2) // 3,
        (len(vals) * 3) // 4,
        len(vals) - 1,
    }
    return [vals[idx] for idx in sorted(idxs)]


def predicate_label(pred: dict[str, Any]) -> str:
    kind = pred.get("kind")
    if kind == "num":
        threshold = pred.get("threshold")
        if isinstance(threshold, float):
            threshold_text = f"{threshold:.6g}"
        else:
            threshold_text = str(threshold)
        return f"{pred.get('feature')} {pred.get('op')} {threshold_text}"
    if kind == "tag":
        return f"tag:{pred.get('tag')}"
    return str(pred)


def predicate_fn(pred: dict[str, Any]) -> Callable[[dict[str, Any]], bool]:
    kind = pred.get("kind")
    if kind == "num":
        feature = str(pred.get("feature"))
        threshold = float(pred.get("threshold"))
        op = str(pred.get("op"))

        def check(row: dict[str, Any]) -> bool:
            value = row_feature(row, feature)
            if value is None:
                return False
            return value <= threshold if op == "<=" else value >= threshold

        return check
    if kind == "tag":
        tag = str(pred.get("tag"))

        def check(row: dict[str, Any]) -> bool:
            return tag in set(str(item) for item in (row.get("physics_tags") or []))

        return check
    return lambda row: False


def build_predicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicates: list[dict[str, Any]] = []
    for feature in NUMERIC_FEATURES:
        values = [row_feature(row, feature) for row in rows]
        clean = [float(value) for value in values if value is not None]
        for threshold in quantiles(clean):
            predicates.append({"kind": "num", "feature": feature, "op": "<=", "threshold": threshold})
            predicates.append({"kind": "num", "feature": feature, "op": ">=", "threshold": threshold})
    for tag in OBSERVABLE_TAGS:
        predicates.append({"kind": "tag", "tag": tag})
    seen = set()
    unique = []
    for pred in predicates:
        label = predicate_label(pred)
        if label in seen:
            continue
        seen.add(label)
        unique.append(pred)
    return unique


def summarize_selection(rows: list[dict[str, Any]], labels: list[str]) -> dict[str, Any]:
    deltas = [float(hold_delta(row) or 0.0) for row in rows]
    helpful = [row for row in rows if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in rows if (hold_delta(row) or 0.0) < 0.0]
    flat = [row for row in rows if (hold_delta(row) or 0.0) == 0.0]
    candidate_nonloss = [
        row for row in rows
        if (fnum(row.get("hold_gross_cents")) or 0.0) >= 0.0
    ]
    actual_loss = sum(fnum(row.get("actual_gross_cents")) or 0.0 for row in rows)
    hold_net = sum(fnum(row.get("hold_gross_cents")) or 0.0 for row in rows)
    return {
        "rule": " AND ".join(labels),
        "selected_rows": len(rows),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "actual_loss_cents": actual_loss,
        "hold_net_cents": hold_net,
        "hold_delta_cents": sum(deltas),
        "candidate_nonloss_rows": len(candidate_nonloss),
        "loss_count_reduction": len(candidate_nonloss),
        "worst_harm_cents": min([float(hold_delta(row) or 0.0) for row in harmful] or [0.0]),
        "features": labels,
        "markets": [row.get("market") for row in rows[:10]],
    }


def scan_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predicates = build_predicates(rows)
    pred_items = [(predicate_label(pred), predicate_fn(pred)) for pred in predicates]
    candidates: list[dict[str, Any]] = []
    for label, fn in pred_items:
        selected = [row for row in rows if fn(row)]
        if selected:
            candidates.append(summarize_selection(selected, [label]))
    for (label_a, fn_a), (label_b, fn_b) in itertools.combinations(pred_items, 2):
        if label_a == label_b:
            continue
        selected = [row for row in rows if fn_a(row) and fn_b(row)]
        if selected:
            candidates.append(summarize_selection(selected, [label_a, label_b]))
    # Collapse identical rule strings that can arise from equal thresholds.
    best_by_rule: dict[str, dict[str, Any]] = {}
    for row in candidates:
        best_by_rule[str(row.get("rule"))] = row
    return list(best_by_rule.values())


def score_key(row: dict[str, Any]) -> tuple[int, float, int, int, float]:
    return (
        1 if int(row.get("harmful_rows") or 0) == 0 else 0,
        float(row.get("hold_delta_cents") or 0.0),
        int(row.get("loss_count_reduction") or 0),
        int(row.get("selected_rows") or 0),
        -abs(float(row.get("worst_harm_cents") or 0.0)),
    )


def compact_examples(rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: float(hold_delta(row) or 0.0), reverse=True)
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
            "exit_cents": row_feature(row, "exit_cents"),
            "p_side": row_feature(row, "p_side"),
            "raw_edge_cents": row_feature(row, "raw_edge_cents"),
            "recross_hazard_score": row_feature(row, "recross_hazard_score"),
            "abs_d_sigma": row_feature(row, "abs_d_sigma"),
            "physics_tags": row.get("physics_tags") or [],
        })
    return out


def full_denominator_rule_audits(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = build_scored_rows()
    out = []
    for rule in rules[:12]:
        labels = list(rule.get("features") or [])
        checks = []
        for label in labels:
            pred = parse_label(label)
            if pred is None:
                checks = []
                break
            checks.append(predicate_fn(pred))
        if not checks:
            continue
        selected = [row for row in scored if all(check(row) for check in checks)]
        if not selected:
            continue
        deltas = [float(hold_delta(row) or 0.0) for row in selected]
        current_vals = [fnum(row.get("actual_gross_cents")) or 0.0 for row in selected]
        hold_vals = [fnum(row.get("hold_gross_cents")) or 0.0 for row in selected]
        helpful = [row for row in selected if (hold_delta(row) or 0.0) > 0.0]
        harmful = [row for row in selected if (hold_delta(row) or 0.0) < 0.0]
        out.append({
            "rule": rule.get("rule"),
            "selected_rows": len(selected),
            "helpful_rows": len(helpful),
            "harmful_rows": len(harmful),
            "flat_rows": len(selected) - len(helpful) - len(harmful),
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
            "source_loss_subset": {
                "selected_rows": rule.get("selected_rows"),
                "helpful_rows": rule.get("helpful_rows"),
                "harmful_rows": rule.get("harmful_rows"),
                "hold_delta_cents": rule.get("hold_delta_cents"),
            },
        })
    return sorted(
        out,
        key=lambda row: (
            1 if int(row.get("harmful_rows") or 0) == 0 else 0,
            float(row.get("hold_delta_cents") or 0.0),
            int(row.get("loss_count_reduction") or 0),
        ),
        reverse=True,
    )


def parse_label(label: str) -> dict[str, Any] | None:
    if label.startswith("tag:"):
        return {"kind": "tag", "tag": label.split(":", 1)[1]}
    parts = label.split()
    if len(parts) != 3:
        return None
    feature, op, threshold = parts
    if op not in {"<=", ">="}:
        return None
    try:
        return {"kind": "num", "feature": feature, "op": op, "threshold": float(threshold)}
    except ValueError:
        return None


def build_report() -> dict[str, Any]:
    payload = load_json(LOSS_ESCAPE_JSON)
    rows = clean_rows(payload.get("loss_rows_with_details") or [])
    helpful = [row for row in rows if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in rows if (hold_delta(row) or 0.0) < 0.0]
    rules = scan_rules(rows)
    clean_rules = [
        row for row in rules
        if int(row.get("harmful_rows") or 0) == 0
        and int(row.get("helpful_rows") or 0) >= 2
        and float(row.get("hold_delta_cents") or 0.0) > 0.0
    ]
    top_clean = sorted(clean_rules, key=score_key, reverse=True)[:20]
    top_overall = sorted(rules, key=score_key, reverse=True)[:20]
    full_audits = full_denominator_rule_audits(top_clean or top_overall)
    tag_counts = {
        "helpful": dict(Counter(tag for row in helpful for tag in (row.get("physics_tags") or [])).most_common()),
        "harmful": dict(Counter(tag for row in harmful for tag in (row.get("physics_tags") or [])).most_common()),
    }
    report = {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "matched_unchanged_rows": len(rows),
        "helpful_hold_rows": len(helpful),
        "harmful_hold_rows": len(harmful),
        "flat_hold_rows": len(rows) - len(helpful) - len(harmful),
        "total_actual_loss_cents": sum(fnum(row.get("actual_gross_cents")) or 0.0 for row in rows),
        "total_hold_delta_cents": sum(hold_delta(row) or 0.0 for row in rows),
        "tag_counts": tag_counts,
        "top_clean_rules": top_clean,
        "top_overall_rules": top_overall,
        "full_denominator_rule_audits": full_audits,
        "largest_helpful_rows": compact_examples(helpful),
        "largest_harmful_rows": compact_examples(harmful),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    clean = report.get("top_clean_rules") or []
    notes = [
        "Research-only diagnostic separator; it does not freeze, promote, or change an exit rule.",
        (
            f"Matched-unchanged loss rows split into {report.get('helpful_hold_rows')} hold-helpful, "
            f"{report.get('harmful_hold_rows')} hold-harmful, and {report.get('flat_hold_rows')} flat rows."
        ),
        (
            "The all-row hold delta is "
            f"{report.get('total_hold_delta_cents')}c, but this is not deployable because the harmful rows are true FV/entry failures."
        ),
    ]
    if clean:
        best = clean[0]
        notes.append(
            f"Best clean observable diagnostic separator is `{best.get('rule')}` with "
            f"{best.get('selected_rows')} selected rows, {best.get('helpful_rows')}/"
            f"{best.get('harmful_rows')} helpful/harmful, and {best.get('hold_delta_cents')}c hold delta."
        )
    else:
        notes.append("No clean observable separator with at least two helpful rows was found.")
    full = report.get("full_denominator_rule_audits") or []
    if full:
        best_full = full[0]
        notes.append(
            f"On the full scored exit denominator, the best audited separator `{best_full.get('rule')}` selects "
            f"{best_full.get('selected_rows')} rows with {best_full.get('helpful_rows')}/"
            f"{best_full.get('harmful_rows')} helpful/harmful and {best_full.get('hold_delta_cents')}c delta."
        )
    notes.append("Use this only to decide what future frozen watch might be worth testing; old rows remain diagnostic context.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def money(value: Any) -> str:
    number = fnum(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Matched-Unchanged Loss Separator",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched-unchanged rows: `{report.get('matched_unchanged_rows')}`",
        f"- Hold helpful/harmful/flat: `{report.get('helpful_hold_rows')}/{report.get('harmful_hold_rows')}/{report.get('flat_hold_rows')}`",
        f"- Actual loss total: `{money(report.get('total_actual_loss_cents'))}`",
        f"- Hold delta total: `{money(report.get('total_hold_delta_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Clean Observable Separators",
        "",
        "| rule | selected | helpful/harmful/flat | actual loss c | hold net c | hold delta c | loss count reduction | worst harm c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("top_clean_rules") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{money(row.get('actual_loss_cents'))} | {money(row.get('hold_net_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('loss_count_reduction')} | "
            f"{money(row.get('worst_harm_cents'))} |"
        )
    lines.extend([
        "",
        "## Top Overall Observable Separators",
        "",
        "| rule | selected | helpful/harmful/flat | actual loss c | hold net c | hold delta c | loss count reduction | worst harm c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("top_overall_rules") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{money(row.get('actual_loss_cents'))} | {money(row.get('hold_net_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('loss_count_reduction')} | "
            f"{money(row.get('worst_harm_cents'))} |"
        )
    lines.extend([
        "",
        "## Full Exit-Denominator Sanity Check",
        "",
        "These rows apply the loss-derived separator to all scored exit rows, not just losing rows.",
        "",
        "| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | current losses -> hold losses | loss count reduction | worst harm c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("full_denominator_rule_audits") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{money(row.get('current_net_cents'))} | {money(row.get('hold_net_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('current_losses')} -> {row.get('hold_losses')} | "
            f"{row.get('loss_count_reduction')} | {money(row.get('worst_harm_cents'))} |"
        )
    lines.extend([
        "",
        "## Largest Hold-Helpful Rows",
        "",
        "| market | side/result | actual | hold | delta | exit | p_side | raw edge | recross | abs d | tags |",
        "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("largest_helpful_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
            f"{money(row.get('actual_gross_cents'))} | {money(row.get('hold_gross_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('exit_reason')}@{row.get('exit_cents')} | "
            f"{fmt(row.get('p_side'))} | {fmt(row.get('raw_edge_cents'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{', '.join(row.get('physics_tags') or [])} |"
        )
    lines.extend([
        "",
        "## Largest Hold-Harmful Rows",
        "",
        "| market | side/result | actual | hold | delta | exit | p_side | raw edge | recross | abs d | tags |",
        "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("largest_harmful_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
            f"{money(row.get('actual_gross_cents'))} | {money(row.get('hold_gross_cents'))} | "
            f"{money(row.get('hold_delta_cents'))} | {row.get('exit_reason')}@{row.get('exit_cents')} | "
            f"{fmt(row.get('p_side'))} | {fmt(row.get('raw_edge_cents'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{', '.join(row.get('physics_tags') or [])} |"
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
