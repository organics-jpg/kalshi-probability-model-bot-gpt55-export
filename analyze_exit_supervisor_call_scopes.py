from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "logs" / "online_exit_supervisor_shadow_replay_60s_all_latest.json"
DEFAULT_OUTPUT = ROOT / "logs" / "exit_supervisor_call_scope_latest.json"


def load_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows") if isinstance(data, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def payload(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("payload")
    return value if isinstance(value, dict) else {}


def hint(row: dict[str, Any], name: str) -> dict[str, Any]:
    value = payload(row).get(name)
    return value if isinstance(value, dict) else {}


def tags(row: dict[str, Any]) -> list[str]:
    raw_tags = row.get("slice_tags")
    if not isinstance(raw_tags, list):
        raw_tags = payload(row).get("candidate_slice_tags")
    return [str(tag) for tag in raw_tags] if isinstance(raw_tags, list) else []


def post_entry(row: dict[str, Any]) -> dict[str, Any]:
    value = payload(row).get("post_entry")
    if isinstance(value, dict):
        return value
    context = payload(row).get("context") if isinstance(payload(row).get("context"), dict) else {}
    value = context.get("post_entry")
    return value if isinstance(value, dict) else {}


def pre_entry(row: dict[str, Any]) -> dict[str, Any]:
    value = payload(row).get("pre_entry")
    if isinstance(value, dict):
        return value
    context = payload(row).get("context") if isinstance(payload(row).get("context"), dict) else {}
    value = context.get("pre_entry")
    return value if isinstance(value, dict) else {}


def summarize(rows: list[dict[str, Any]], selected: list[dict[str, Any]], *, selector_name: str) -> dict[str, Any]:
    deltas = [float(row.get("delta_dollars") or 0.0) for row in selected]
    positives = [delta for delta in deltas if delta > 0]
    negatives = [delta for delta in deltas if delta < 0]
    red_rows = [row for row in selected if str(row.get("shadow_label") or "") == "RED_LIGHT"]
    green_rows = [row for row in selected if str(row.get("shadow_label") or "") == "GREEN_LIGHT"]
    neutral_rows = [row for row in selected if str(row.get("shadow_label") or "") == "NEUTRAL"]
    call_count = len(selected)
    total_count = len(rows)
    false_exit_cost = -sum(negatives)
    oracle_value = sum(positives)
    exit_all_delta = sum(deltas)
    return {
        "selector": selector_name,
        "call_count": int(call_count),
        "call_rate": round(call_count / total_count, 4) if total_count else None,
        "red_truth_count": int(len(red_rows)),
        "green_truth_count": int(len(green_rows)),
        "neutral_truth_count": int(len(neutral_rows)),
        "red_truth_rate": round(len(red_rows) / call_count, 4) if call_count else None,
        "exit_all_delta_dollars": round(float(exit_all_delta), 4),
        "false_exit_cost_dollars": round(float(false_exit_cost), 4),
        "oracle_exit_value_dollars": round(float(oracle_value), 4),
        "oracle_value_per_call_dollars": round(float(oracle_value / call_count), 4) if call_count else None,
        "false_cost_per_call_dollars": round(float(false_exit_cost / call_count), 4) if call_count else None,
        "avg_positive_delta_dollars": round(float(sum(positives) / len(positives)), 4) if positives else None,
        "avg_negative_delta_dollars": round(float(sum(negatives) / len(negatives)), 4) if negatives else None,
        "break_even_false_exit_rate_if_all_true_caught": round(
            float(oracle_value / (oracle_value + false_exit_cost)),
            4,
        ) if (oracle_value + false_exit_cost) > 0 else None,
    }


def build_selectors() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "all_entries": lambda row: True,
        "any_candidate_slice_tag": lambda row: bool(tags(row)),
        "deterministic_exit_candidate": lambda row: hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE",
        "deterministic_hold_guard": lambda row: bool(hint(row, "deterministic_policy_hints").get("conservative_hold_guard")),
        "exit_candidate_memory_positive": lambda row: (
            hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE"
            and hint(row, "shadow_memory_policy_hint").get("state") == "same_slice_recent_positive"
        ),
        "exit_candidate_memory_not_negative": lambda row: (
            hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE"
            and hint(row, "shadow_memory_policy_hint").get("state") != "same_slice_recent_negative"
        ),
        "broad_no_neutral_neutral": lambda row: "broad_no_neutral_neutral" in tags(row),
        "broad_no_neutral_neutral_macd_flat": lambda row: "broad_no_neutral_neutral_macd_flat" in tags(row),
        "hard_red_weak_strength": lambda row: "hard_red_weak_strength" in tags(row),
        "damage_heavy_rsi_slope_flat": lambda row: "damage_heavy_rsi_slope_flat" in tags(row),
        "post_below_or_well_below": lambda row: str(post_entry(row).get("current_vs_entry_state") or "") in {"below_entry", "well_below_entry"},
        "post_weak_or_recovering": lambda row: str(post_entry(row).get("current_strength") or "") in {"weak", "recovering"},
        "post_below_or_weak": lambda row: (
            str(post_entry(row).get("current_vs_entry_state") or "") in {"below_entry", "well_below_entry"}
            or str(post_entry(row).get("current_strength") or "") in {"weak", "recovering"}
        ),
        "strong_above_guard_avoid": lambda row: not bool(hint(row, "deterministic_policy_hints").get("conservative_hold_guard")),
        "late_entry": lambda row: str(pre_entry(row).get("entry_timing_state") or "") == "late_entry",
    }


def analyze(input_path: Path) -> dict[str, Any]:
    rows = load_rows(input_path)
    selectors = build_selectors()
    summaries = [
        summarize(rows, [row for row in rows if selector(row)], selector_name=name)
        for name, selector in selectors.items()
    ]
    ranked_by_oracle_per_call = sorted(
        summaries,
        key=lambda row: (
            float(row.get("oracle_value_per_call_dollars") or -999),
            float(row.get("exit_all_delta_dollars") or -999),
        ),
        reverse=True,
    )
    ranked_by_exit_all = sorted(
        summaries,
        key=lambda row: float(row.get("exit_all_delta_dollars") or -999),
        reverse=True,
    )
    return {
        "input_path": str(input_path),
        "case_count": int(len(rows)),
        "summaries": summaries,
        "ranked_by_oracle_value_per_call": ranked_by_oracle_per_call,
        "ranked_by_exit_all_delta": ranked_by_exit_all,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank candidate Truffle call scopes for post-entry exit supervision.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    payload = analyze(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved exit-supervisor call scope analysis to {output_path}")
    print(json.dumps({
        "case_count": payload["case_count"],
        "top_oracle_per_call": payload["ranked_by_oracle_value_per_call"][:6],
        "top_exit_all": payload["ranked_by_exit_all_delta"][:6],
    }, indent=2))


if __name__ == "__main__":
    main()
