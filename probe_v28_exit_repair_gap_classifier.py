"""Classify unresolved v28 loss rows after current frozen exit repairs.

Research-only; no live bot changes or orders.

The loss-count blocker is not solved by knowing that exit_reduce helps some
rows. This report separates the remaining losing rows into: no frozen exit
observation, matched but unchanged, worsened by repair, and flipped by repair.
It then ranks the physical gaps that should drive the next exit/state research.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
OBSERVABLE_OPPORTUNITY_JSON = OUT_DIR / "v28_exit_reduce_observable_loss_control_opportunity_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_repair_gap_classifier_latest.json"
OUT_MD = OUT_DIR / "v28_exit_repair_gap_classifier_latest.md"

POLICY_ARTIFACTS = {
    "exit_reduce": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
    "exit_book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "loss_guard_v1": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
    "dual_exit": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
}


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


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def pct(part: int, total: int) -> float | None:
    if not total:
        return None
    return part / total * 100.0


def money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def tags_key(row: dict[str, Any]) -> str:
    tags = [str(tag) for tag in row.get("physics_tags") or []]
    priority = [
        "fv_or_entry_timing_error",
        "exit_policy_cost",
        "exited_unsettled",
        "execution_or_state_error",
        "near_boundary",
        "recross_hazard_high",
        "thin_raw_edge",
        "rich_entry",
        "crowded_depth",
        "thin_touch_depth",
        "hold_result_unknown",
    ]
    selected = [tag for tag in priority if tag in tags]
    return "+".join(selected[:4]) or "unclassified"


def row_delta(row: dict[str, Any]) -> float:
    best = row.get("best_policy_effect") or {}
    return as_float(best.get("delta_cents")) or 0.0


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    actual = [as_float(row.get("actual_gross_cents")) or 0.0 for row in rows]
    best_delta = [row_delta(row) for row in rows]
    hold_known = [row for row in rows if hold_delta(row) is not None]
    hold_helpful = [row for row in hold_known if (hold_delta(row) or 0.0) > 0.0]
    hold_harmful = [row for row in hold_known if (hold_delta(row) or 0.0) < 0.0]
    return {
        "rows": len(rows),
        "actual_loss_cents": sum(actual),
        "best_repair_delta_cents": sum(best_delta),
        "known_hold_rows": len(hold_known),
        "hold_helpful_rows": len(hold_helpful),
        "hold_harmful_rows": len(hold_harmful),
        "hold_unknown_rows": len(rows) - len(hold_known),
    }


def counter_rows(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    counter = Counter(str(row.get(field) or "unknown") for row in rows)
    loss_by_key: dict[str, float] = defaultdict(float)
    for row in rows:
        key = str(row.get(field) or "unknown")
        loss_by_key[key] += as_float(row.get("actual_gross_cents")) or 0.0
    return [
        {"name": key, "rows": count, "actual_loss_cents": loss_by_key[key]}
        for key, count in counter.most_common()
    ]


def top_examples(rows: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: as_float(row.get("actual_gross_cents")) or 0.0)
    examples = []
    for row in ranked[:limit]:
        best = row.get("best_policy_effect") or {}
        examples.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "entry_ts": row.get("entry_ts"),
            "loss_cents": row.get("actual_gross_cents"),
            "exit_reason": row.get("exit_reason"),
            "exit_cents": row.get("exit_cents"),
            "p_hold": best.get("p_hold"),
            "best_policy": best.get("policy"),
            "best_effect": best.get("effect"),
            "best_delta_cents": best.get("delta_cents"),
            "hold_gross_cents": row.get("hold_gross_cents"),
            "tags": row.get("physics_tags") or [],
        })
    return examples


def build_report() -> dict[str, Any]:
    loss_escape = load_json(LOSS_ESCAPE_JSON)
    observable_opp = load_json(OBSERVABLE_OPPORTUNITY_JSON)
    policy_freezes: dict[str, str] = {}
    freeze_times: list[datetime] = []
    for policy, path in POLICY_ARTIFACTS.items():
        payload = load_json(path)
        freeze_ts = (payload.get("freeze") or {}).get("freeze_ts_utc")
        if freeze_ts:
            policy_freezes[policy] = str(freeze_ts)
            parsed = parse_ts(freeze_ts)
            if parsed:
                freeze_times.append(parsed)
    first_freeze = min(freeze_times) if freeze_times else None
    rows = loss_escape.get("loss_rows_with_details") or []
    if not isinstance(rows, list):
        rows = []

    by_escape: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_failure: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_tag_combo: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_exit_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_escape[str(row.get("escape_class") or "unknown")].append(row)
        by_failure[str(row.get("failure_class") or "unknown")].append(row)
        by_tag_combo[tags_key(row)].append(row)
        by_exit_reason[str(row.get("exit_reason") or "unknown")].append(row)

    unresolved = [
        row for row in rows
        if row.get("escape_class") in {"no_exit_repair_observation", "loss_escapes_current_exit_repairs"}
    ]
    no_observation = by_escape.get("no_exit_repair_observation", [])
    unchanged = by_escape.get("loss_escapes_current_exit_repairs", [])
    flipped = by_escape.get("repair_flips_loss", [])
    worsened = by_escape.get("repair_would_worsen", [])

    opportunity_rules = observable_opp.get("rules") or []
    probability_reduce_rows = max(
        [int(rule.get("probability_reduce_rows") or 0) for rule in opportunity_rules] or [0]
    )
    would_suppress_rows = max(
        [int(rule.get("would_suppress_rows") or 0) for rule in opportunity_rules] or [0]
    )
    harmful_suppress_delta = min(
        [as_float(rule.get("would_suppress_delta_cents")) or 0.0 for rule in opportunity_rules] or [0.0]
    )
    no_observation_pre_first_freeze = [
        row for row in no_observation
        if first_freeze is not None
        and (parse_ts(row.get("entry_ts") or row.get("exit_ts")) or datetime.max.replace(tzinfo=timezone.utc)) < first_freeze
    ]
    no_observation_post_first_freeze = [
        row for row in no_observation
        if row not in no_observation_pre_first_freeze
    ]

    report = {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "observable_opportunity_source": str(OBSERVABLE_OPPORTUNITY_JSON),
        "policy_freeze_ts_utc": policy_freezes,
        "first_exit_repair_freeze_ts_utc": first_freeze.isoformat() if first_freeze else None,
        "summary": {
            "loss_rows": len(rows),
            "unresolved_rows": len(unresolved),
            "unresolved_share": pct(len(unresolved), len(rows)),
            "no_exit_repair_observation_rows": len(no_observation),
            "no_exit_repair_observation_pre_first_freeze_rows": len(no_observation_pre_first_freeze),
            "no_exit_repair_observation_post_first_freeze_rows": len(no_observation_post_first_freeze),
            "matched_but_unchanged_rows": len(unchanged),
            "repair_flips_loss_rows": len(flipped),
            "repair_would_worsen_rows": len(worsened),
            "actual_loss_cents": sum(as_float(row.get("actual_gross_cents")) or 0.0 for row in rows),
            "best_repair_delta_cents": sum(row_delta(row) for row in rows),
            "observable_post_birth_probability_reduce_rows": probability_reduce_rows,
            "observable_post_birth_would_suppress_rows": would_suppress_rows,
            "observable_post_birth_worst_suppress_delta_cents": harmful_suppress_delta,
        },
        "by_escape_class": [
            {"escape_class": key, **summarize_group(group)}
            for key, group in sorted(by_escape.items(), key=lambda item: len(item[1]), reverse=True)
        ],
        "by_failure_class": [
            {"failure_class": key, **summarize_group(group)}
            for key, group in sorted(by_failure.items(), key=lambda item: len(item[1]), reverse=True)
        ],
        "unresolved_by_failure_class": [
            {"failure_class": key, **summarize_group([row for row in unresolved if row.get("failure_class") == key])}
            for key in sorted({str(row.get("failure_class") or "unknown") for row in unresolved})
        ],
        "unresolved_tag_combos": [
            {"tags": key, **summarize_group(group)}
            for key, group in sorted(
                ((key, [row for row in unresolved if tags_key(row) == key]) for key in by_tag_combo),
                key=lambda item: len(item[1]),
                reverse=True,
            )
            if group
        ],
        "unresolved_exit_reasons": counter_rows(unresolved, "exit_reason"),
        "no_observation_examples": top_examples(no_observation),
        "matched_unchanged_examples": top_examples(unchanged),
        "worsened_examples": top_examples(worsened),
        "flipped_examples": top_examples(flipped),
        "interpretation": [],
    }

    summary = report["summary"]
    report["interpretation"] = [
        "Research-only diagnostic; this does not create or promote an exit rule.",
        (
            f"{summary['unresolved_rows']} of {summary['loss_rows']} losing control rows remain unresolved "
            f"by the current frozen exit repair family."
        ),
        (
            f"{summary['no_exit_repair_observation_rows']} losses have no matching frozen exit observation; "
            f"{summary['no_exit_repair_observation_pre_first_freeze_rows']} of them predate the first frozen "
            "exit-repair window, so they are historical context rather than a current denominator miss."
        ),
        (
            f"{summary['matched_but_unchanged_rows']} losses are matched but unchanged; these are mostly true "
            "collapse/value-exit or low-p_hold states where broad suppressions risk holding losers."
        ),
        (
            "The observable loss-control watch has only "
            f"{summary['observable_post_birth_probability_reduce_rows']} post-birth probability-reduce row(s), "
            f"{summary['observable_post_birth_would_suppress_rows']} would-suppress row(s), and worst delta "
            f"{summary['observable_post_birth_worst_suppress_delta_cents']}c, so it remains watch-only."
        ),
    ]
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    lines = [
        "# v28 Exit Repair Gap Classifier",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Loss rows: `{summary.get('loss_rows')}`",
        f"- Unresolved rows: `{summary.get('unresolved_rows')}` / `{fmt(summary.get('unresolved_share'))}%`",
        f"- No exit-repair observation: `{summary.get('no_exit_repair_observation_rows')}`",
        f"- No-observation pre/post first exit-repair freeze: "
        f"`{summary.get('no_exit_repair_observation_pre_first_freeze_rows')}/{summary.get('no_exit_repair_observation_post_first_freeze_rows')}`",
        f"- First exit-repair freeze UTC: `{report.get('first_exit_repair_freeze_ts_utc')}`",
        f"- Matched but unchanged: `{summary.get('matched_but_unchanged_rows')}`",
        f"- Repair flips loss: `{summary.get('repair_flips_loss_rows')}`",
        f"- Repair would worsen: `{summary.get('repair_would_worsen_rows')}`",
        f"- Observable post-birth probability-reduce/would-suppress: `{summary.get('observable_post_birth_probability_reduce_rows')}/{summary.get('observable_post_birth_would_suppress_rows')}`",
        f"- Observable post-birth worst suppress delta: `{money(summary.get('observable_post_birth_worst_suppress_delta_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Escape Classes",
        "",
        "| class | rows | actual loss c | best repair delta c | known hold | hold helpful | hold harmful | hold unknown |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("by_escape_class") or []:
        lines.append(
            f"| {row.get('escape_class')} | {row.get('rows')} | {money(row.get('actual_loss_cents'))} | "
            f"{money(row.get('best_repair_delta_cents'))} | {row.get('known_hold_rows')} | "
            f"{row.get('hold_helpful_rows')} | {row.get('hold_harmful_rows')} | {row.get('hold_unknown_rows')} |"
        )

    lines.extend([
        "",
        "## Unresolved Failure Classes",
        "",
        "| failure class | rows | actual loss c | known hold | hold helpful | hold harmful | hold unknown |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("unresolved_by_failure_class") or []:
        if not row.get("rows"):
            continue
        lines.append(
            f"| {row.get('failure_class')} | {row.get('rows')} | {money(row.get('actual_loss_cents'))} | "
            f"{row.get('known_hold_rows')} | {row.get('hold_helpful_rows')} | "
            f"{row.get('hold_harmful_rows')} | {row.get('hold_unknown_rows')} |"
        )

    lines.extend([
        "",
        "## Unresolved Tag Combos",
        "",
        "| tags | rows | actual loss c | hold helpful | hold harmful | hold unknown |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in (report.get("unresolved_tag_combos") or [])[:10]:
        lines.append(
            f"| {row.get('tags')} | {row.get('rows')} | {money(row.get('actual_loss_cents'))} | "
            f"{row.get('hold_helpful_rows')} | {row.get('hold_harmful_rows')} | {row.get('hold_unknown_rows')} |"
        )

    lines.extend([
        "",
        "## Unresolved Exit Reasons",
        "",
        "| reason | rows | actual loss c |",
        "|---|---:|---:|",
    ])
    for row in report.get("unresolved_exit_reasons") or []:
        lines.append(f"| {row.get('name')} | {row.get('rows')} | {money(row.get('actual_loss_cents'))} |")

    lines.extend([
        "",
        "## Largest No-Observation Losses",
        "",
        "| market | side | loss c | exit | hold c | tags |",
        "|---|---|---:|---|---:|---|",
    ])
    for row in (report.get("no_observation_examples") or [])[:5]:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {money(row.get('loss_cents'))} | "
            f"{row.get('exit_reason')}@{row.get('exit_cents')} | {money(row.get('hold_gross_cents'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )

    lines.extend([
        "",
        "## Largest Matched-Unchanged Losses",
        "",
        "| market | side | loss c | best policy | p_hold | exit | hold c | tags |",
        "|---|---|---:|---|---:|---|---:|---|",
    ])
    for row in (report.get("matched_unchanged_examples") or [])[:5]:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {money(row.get('loss_cents'))} | "
            f"{row.get('best_policy')} | {fmt(row.get('p_hold'))} | {row.get('exit_reason')}@{row.get('exit_cents')} | "
            f"{money(row.get('hold_gross_cents'))} | {', '.join(row.get('tags') or [])} |"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
