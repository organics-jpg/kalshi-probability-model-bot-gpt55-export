"""Map v28 control/live losses to frozen exit-repair opportunities.

Research-only; no live bot changes or orders.

The control risk-stop is currently driven by loss-count churn. This report
asks a sharper question than the aggregate churn scorecard: for each losing
control row, did a frozen exit repair have a matching real exit row, and would
it have flipped the loss, reduced it, worsened it, or left it unchanged?
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
OUT_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
OUT_MD = OUT_DIR / "v28_live_loss_escape_analysis_latest.md"

POLICY_ROW_ARTIFACTS = {
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


def loss_bucket(value: float) -> str:
    loss = abs(value)
    if loss < 10.0:
        return "micro_lt_10c"
    if loss < 25.0:
        return "small_10_24c"
    if loss < 50.0:
        return "medium_25_49c"
    if loss < 100.0:
        return "large_50_99c"
    return "full_loss_ge_100c"


def key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def build_policy_index() -> dict[str, dict[tuple[str, str], list[dict[str, Any]]]]:
    indexes: dict[str, dict[tuple[str, str], list[dict[str, Any]]]] = {}
    for label, path in POLICY_ROW_ARTIFACTS.items():
        payload = load_json(path)
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in payload.get("rows") or []:
            if as_float(row.get("current_cents")) is None or as_float(row.get("candidate_cents")) is None:
                continue
            grouped[key(row)].append(row)
        indexes[label] = grouped
    return indexes


def nearest_match(loss_row: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    loss_ts = parse_ts(loss_row.get("entry_ts") or loss_row.get("exit_ts"))
    if loss_ts is None:
        return candidates[0]
    best = None
    best_delta = None
    for row in candidates:
        row_ts = parse_ts(row.get("entry_ts") or row.get("exit_ts"))
        if row_ts is None:
            delta = 10**18
        else:
            delta = abs((row_ts - loss_ts).total_seconds())
        if best_delta is None or delta < best_delta:
            best = row
            best_delta = delta
    return best


def effect_label(current: float, candidate: float) -> str:
    if current < 0.0 <= candidate:
        return "loss_to_non_loss"
    if current < candidate < 0.0:
        return "loss_reduced"
    if candidate < current:
        return "worsened"
    if candidate == current:
        return "unchanged"
    return "other_improved"


def compact_policy_effect(policy: str, row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {"policy": policy, "matched": False, "effect": "no_matching_exit_row"}
    current = as_float(row.get("current_cents")) or 0.0
    candidate = as_float(row.get("candidate_cents")) or 0.0
    return {
        "policy": policy,
        "matched": True,
        "effect": effect_label(current, candidate),
        "current_cents": current,
        "candidate_cents": candidate,
        "delta_cents": candidate - current,
        "suppressed": bool(row.get("suppressed")),
        "exit_reason": row.get("exit_reason"),
        "p_hold": row.get("p_hold"),
        "hold_book_gap": row.get("hold_book_gap"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "exit_cents": row.get("exit_cents"),
        "exit_ts": row.get("exit_ts"),
    }


def best_effect(effects: list[dict[str, Any]]) -> dict[str, Any]:
    matched = [row for row in effects if row.get("matched")]
    if not matched:
        return {"policy": None, "matched": False, "effect": "no_policy_matched", "delta_cents": 0.0}
    return sorted(matched, key=lambda row: as_float(row.get("delta_cents")) or 0.0, reverse=True)[0]


def classify_escape(row: dict[str, Any], best: dict[str, Any]) -> str:
    if not best.get("matched"):
        return "no_exit_repair_observation"
    effect = str(best.get("effect") or "")
    if effect == "loss_to_non_loss":
        return "repair_flips_loss"
    if effect in {"loss_reduced", "other_improved"}:
        return "repair_reduces_loss"
    if effect == "worsened":
        return "repair_would_worsen"
    return "loss_escapes_current_exit_repairs"


def physics_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    gross = as_float(row.get("actual_gross_cents")) or 0.0
    tags.append(loss_bucket(gross))
    tags.append(str(row.get("failure_class") or "unknown_failure"))
    if row.get("h6_recross_hazard_high") is True:
        tags.append("recross_hazard_high")
    if row.get("h2_thin_touch_depth") is True:
        tags.append("thin_touch_depth")
    if row.get("h2_crowded_depth") is True:
        tags.append("crowded_depth")
    if row.get("hold_gross_cents") is None:
        tags.append("hold_result_unknown")
    elif (as_float(row.get("hold_gross_cents")) or 0.0) > gross:
        tags.append("exit_policy_clip_vs_hold")
    if (as_float(row.get("raw_edge_cents")) or 0.0) < 5.0:
        tags.append("thin_raw_edge")
    if (as_float(row.get("ask_cents")) or 0.0) >= 80.0:
        tags.append("rich_entry")
    if (as_float(row.get("abs_d_sigma")) or 0.0) < 1.0:
        tags.append("near_boundary")
    return tags


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    rows = scorecard.get("rows") or []
    losing = [
        row for row in rows
        if as_float(row.get("actual_gross_cents")) is not None
        and (as_float(row.get("actual_gross_cents")) or 0.0) < 0.0
    ]
    losing.sort(key=lambda row: str(row.get("entry_ts") or row.get("exit_ts") or ""))
    policy_index = build_policy_index()
    details = []
    for row in losing:
        effects = []
        for policy, grouped in policy_index.items():
            match = nearest_match(row, grouped.get(key(row)) or [])
            effects.append(compact_policy_effect(policy, match))
        best = best_effect(effects)
        actual = as_float(row.get("actual_gross_cents")) or 0.0
        details.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "actual_gross_cents": actual,
            "loss_bucket": loss_bucket(actual),
            "failure_class": row.get("failure_class"),
            "exit_reason": row.get("exit_reason"),
            "exit_cents": row.get("exit_cents"),
            "hold_gross_cents": row.get("hold_gross_cents"),
            "p_side": row.get("p_side"),
            "raw_edge_cents": row.get("raw_edge_cents"),
            "ask_cents": row.get("ask_cents"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "eligible_depth": row.get("eligible_depth"),
            "physics_tags": physics_tags(row),
            "best_policy_effect": best,
            "escape_class": classify_escape(row, best),
            "policy_effects": effects,
        })
    by_escape = Counter(row["escape_class"] for row in details)
    by_failure_escape: dict[str, Counter] = defaultdict(Counter)
    tag_escape: dict[str, Counter] = defaultdict(Counter)
    for row in details:
        by_failure_escape[str(row.get("failure_class") or "unknown")][row["escape_class"]] += 1
        for tag in row.get("physics_tags") or []:
            tag_escape[tag][row["escape_class"]] += 1
    policy_best_counter = Counter(
        (row.get("best_policy_effect") or {}).get("policy") or "none"
        for row in details
        if row.get("escape_class") in {"repair_flips_loss", "repair_reduces_loss"}
    )
    escaped = [row for row in details if row["escape_class"] == "loss_escapes_current_exit_repairs"]
    report = {
        "generated_at_utc": utc_now_iso(),
        "scorecard_path": str(SCORECARD_JSON),
        "policy_artifacts": {label: str(path) for label, path in POLICY_ROW_ARTIFACTS.items()},
        "loss_rows": len(details),
        "escape_class_counts": dict(by_escape),
        "failure_escape_counts": {key: dict(value) for key, value in sorted(by_failure_escape.items())},
        "tag_escape_counts": {key: dict(value) for key, value in sorted(tag_escape.items())},
        "best_repair_policy_counts": dict(policy_best_counter),
        "loss_rows_with_details": details,
        "largest_escaped_losses": sorted(
            escaped,
            key=lambda row: as_float(row.get("actual_gross_cents")) or 0.0,
        )[:12],
        "recent_loss_rows": details[-12:],
        "interpretation": [],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    counts = report.get("escape_class_counts") or {}
    notes = [
        "This report is diagnostic only; it does not clear live-readiness or change exit logic.",
        (
            f"Among {report.get('loss_rows')} losing control rows, frozen exit repairs flip "
            f"{counts.get('repair_flips_loss', 0)} losses and reduce {counts.get('repair_reduces_loss', 0)} more in matched row replay."
        ),
        (
            f"{counts.get('loss_escapes_current_exit_repairs', 0)} losses have a matching exit-repair row but still escape the current repair family; "
            f"{counts.get('no_exit_repair_observation', 0)} have no matching row in the tracked exit artifacts."
        ),
    ]
    policy_counts = report.get("best_repair_policy_counts") or {}
    if policy_counts:
        notes.append(f"Best repair policy counts for save/reduce rows: {policy_counts}.")
    return notes


def money(value: Any) -> str:
    numeric = as_float(value)
    if numeric is None:
        return "n/a"
    return f"{numeric:.0f}c (${numeric / 100.0:.2f})"


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Live Loss Escape Analysis",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Losing control rows: `{report.get('loss_rows')}`",
        f"- Escape class counts: `{report.get('escape_class_counts')}`",
        f"- Best repair policy counts: `{report.get('best_repair_policy_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Failure Class x Escape",
        "",
        "| failure class | escape counts |",
        "|---|---|",
    ])
    for label, counts in (report.get("failure_escape_counts") or {}).items():
        lines.append(f"| `{label}` | `{counts}` |")
    lines.extend([
        "",
        "## Largest Escaped Losses",
        "",
        "| market | side/result | loss | failure | exit/hold | best policy | best effect | tags |",
        "|---|---|---:|---|---:|---|---|---|",
    ])
    for row in report.get("largest_escaped_losses") or []:
        best = row.get("best_policy_effect") or {}
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | {money(row.get('actual_gross_cents'))} | "
            f"`{row.get('failure_class')}` | {money(row.get('exit_cents'))}/{money(row.get('hold_gross_cents'))} | "
            f"`{best.get('policy')}` | `{best.get('effect')}` {money(best.get('delta_cents'))} | "
            f"`{', '.join(row.get('physics_tags') or [])}` |"
        )
    lines.extend([
        "",
        "## Recent Loss Rows",
        "",
        "| market | ts | side/result | loss | escape | best policy | best effect | tags |",
        "|---|---|---|---:|---|---|---|---|",
    ])
    for row in report.get("recent_loss_rows") or []:
        best = row.get("best_policy_effect") or {}
        lines.append(
            f"| `{row.get('market')}` | `{row.get('entry_ts')}` | {row.get('side')}/{row.get('result')} | "
            f"{money(row.get('actual_gross_cents'))} | `{row.get('escape_class')}` | `{best.get('policy')}` | "
            f"`{best.get('effect')}` {money(best.get('delta_cents'))} | `{', '.join(row.get('physics_tags') or [])}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
