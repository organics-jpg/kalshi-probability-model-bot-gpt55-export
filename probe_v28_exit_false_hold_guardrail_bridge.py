"""Bridge strict harmful exit suppressions to observable false-hold guardrails.

Research-only; no live bot changes or orders.

The true-loser hold-risk audit says broad exit suppression can hold real
FV/entry losers. The strict failure drilldown shows the concrete suppressed
rows where this already happened. This report turns those harmful suppressions
into guardrail signals future exit watches must avoid under strict evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STRICT_FAILURE_JSON = OUT_DIR / "v28_exit_policy_strict_failure_drilldown_latest.json"
TRUE_LOSER_JSON = OUT_DIR / "v28_exit_true_loser_hold_risk_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.md"


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def derived_tags(example: dict[str, Any]) -> set[str]:
    tags = {str(tag) for tag in example.get("tags") or []}
    exit_price = as_float(example.get("exit_price_cents"))
    p_hold = as_float(example.get("p_hold"))
    gap = as_float(example.get("hold_book_gap"))
    drawdown = as_float(example.get("fair_drawdown_cents"))
    reason = str(example.get("exit_reason") or "")

    if exit_price is not None:
        if exit_price >= 80:
            tags.add("exit_cents_gte80")
        if exit_price >= 60:
            tags.add("exit_cents_gte60")
    if p_hold is not None:
        if p_hold < 0.75:
            tags.add("p_hold_lt75")
        elif p_hold < 0.85:
            tags.add("p_hold_75_85")
        else:
            tags.add("p_hold_gte85")
    if gap is not None:
        if gap < 0:
            tags.add("negative_book_gap")
        if gap >= 0.05:
            tags.add("positive_book_gap_ge05")
    if drawdown is not None:
        if drawdown > 0:
            tags.add("positive_fair_drawdown")
        if drawdown < -5:
            tags.add("deep_negative_fair_drawdown")
    if "probability_reduce" in reason:
        tags.add("probability_reduce")
    if "value_over_hold" in reason:
        tags.add("value_over_hold")
    return tags


def unique_key(example: dict[str, Any]) -> tuple[Any, ...]:
    return (
        example.get("window"),
        example.get("market"),
        example.get("side"),
        example.get("exit_ts"),
        example.get("policy"),
    )


def build_report() -> dict[str, Any]:
    strict = load_json(STRICT_FAILURE_JSON)
    true_loser = load_json(TRUE_LOSER_JSON)
    avoid_tags = [
        str(row.get("tag"))
        for row in true_loser.get("avoid_broad_hold_tags") or []
        if row.get("tag")
    ]
    examples: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    for summary in strict.get("summaries") or []:
        window = str(summary.get("window") or "")
        if not window.startswith("new_exit_mix_common_forward"):
            continue
        window_examples = []
        for raw in summary.get("examples") or []:
            example = dict(raw)
            example["window"] = window
            example["derived_tags"] = sorted(derived_tags(example))
            example["true_loser_avoid_tag_overlap"] = sorted(set(example["derived_tags"]) & set(avoid_tags))
            window_examples.append(example)
            examples.append(example)
        tag_counts = Counter(tag for ex in window_examples for tag in ex["derived_tags"])
        policy_counts = Counter(str(ex.get("policy") or "unknown") for ex in window_examples)
        window_rows.append({
            "window": window,
            "rows": summary.get("rows"),
            "harmful_suppressions": summary.get("harmful_suppressions"),
            "net_harm_cents": summary.get("net_harm_cents"),
            "policy_counts": dict(policy_counts),
            "top_guardrail_tags": dict(tag_counts.most_common(12)),
        })

    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ex in examples:
        by_policy[str(ex.get("policy") or "unknown")].append(ex)

    policy_rows = []
    for policy, rows in by_policy.items():
        tag_counts = Counter(tag for ex in rows for tag in ex["derived_tags"])
        policy_rows.append({
            "policy": policy,
            "harmful_rows": len(rows),
            "net_harm_cents": sum(as_float(ex.get("delta_cents")) or 0.0 for ex in rows),
            "top_guardrail_tags": dict(tag_counts.most_common(10)),
            "avoid_tag_overlap_rows": sum(1 for ex in rows if ex.get("true_loser_avoid_tag_overlap")),
        })
    policy_rows.sort(key=lambda row: (row["net_harm_cents"], -row["harmful_rows"]))

    all_tags = Counter(tag for ex in examples for tag in ex["derived_tags"])
    unique_examples = {}
    for ex in examples:
        unique_examples[unique_key(ex)] = ex

    return {
        "generated_at_utc": utc_now_iso(),
        "strict_failure_source": str(STRICT_FAILURE_JSON),
        "true_loser_source": str(TRUE_LOSER_JSON),
        "strict_harmful_suppressions": strict.get("strict_harmful_suppressions"),
        "strict_net_harm_cents": strict.get("strict_net_harm_cents"),
        "true_loser_avoid_tags": avoid_tags,
        "summary": {
            "strict_windows": len(window_rows),
            "harmful_policy_examples": len(examples),
            "unique_harmful_policy_examples": len(unique_examples),
            "net_harm_cents": sum(as_float(ex.get("delta_cents")) or 0.0 for ex in examples),
            "top_guardrail_tags": dict(all_tags.most_common(15)),
        },
        "window_rows": window_rows,
        "policy_rows": policy_rows,
        "examples": sorted(
            unique_examples.values(),
            key=lambda ex: as_float(ex.get("delta_cents")) or 0.0,
        )[:15],
        "interpretation": [
            "Research-only bridge; it does not create or promote a rule.",
            "Strict harmful suppressions are concrete false-hold cases where taking the exit would have prevented loss.",
            "Future exit watches should reject or explicitly guard these signals before any promotion review.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Exit False-Hold Guardrail Bridge",
        "",
        "Research-only bridge. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Strict harmful suppressions: `{report.get('strict_harmful_suppressions')}`",
        f"- Strict net harm: `{cents(report.get('strict_net_harm_cents'))}`",
        f"- Harmful policy examples in strict windows: `{summary['harmful_policy_examples']}`",
        f"- Unique harmful policy examples: `{summary['unique_harmful_policy_examples']}`",
        "",
        "## Interpretation",
        "",
        "- Strict harmful suppressions are the false-hold side of the exit problem.",
        "- Promotion should require candidate exits to avoid these states, not only show positive clipped-winner recovery.",
        f"- Top strict guardrail tags: `{summary['top_guardrail_tags']}`",
        "",
        "## Strict Window Guardrails",
        "",
        "| window | rows | harmful | net harm | top tags | policies |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in report["window_rows"]:
        lines.append(
            f"| `{row['window']}` | {row.get('rows')} | {row.get('harmful_suppressions')} | "
            f"{cents(row.get('net_harm_cents'))} | `{row.get('top_guardrail_tags')}` | `{row.get('policy_counts')}` |"
        )

    lines.extend([
        "",
        "## Policy Harm",
        "",
        "| policy | harmful rows | net harm | avoid-tag overlap rows | top tags |",
        "|---|---:|---:|---:|---|",
    ])
    for row in report["policy_rows"]:
        lines.append(
            f"| `{row['policy']}` | {row['harmful_rows']} | {cents(row['net_harm_cents'])} | "
            f"{row['avoid_tag_overlap_rows']} | `{row['top_guardrail_tags']}` |"
        )

    lines.extend([
        "",
        "## Worst False-Hold Examples",
        "",
        "| window | policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for ex in report["examples"]:
        lines.append(
            f"| `{ex.get('window')}` | `{ex.get('policy')}` | `{ex.get('market')}` | "
            f"{ex.get('side')}/{ex.get('result')} | `{ex.get('exit_reason')}` | "
            f"{ex.get('p_hold')} | {ex.get('hold_book_gap')} | {ex.get('fair_drawdown_cents')} | "
            f"{ex.get('exit_price_cents')} | {cents(ex.get('delta_cents'))} | "
            f"{', '.join(ex.get('derived_tags') or [])} |"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
