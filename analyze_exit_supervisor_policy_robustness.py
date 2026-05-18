from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "logs" / "online_exit_supervisor_policy_eval_latest.json"
DEFAULT_OUTPUT = ROOT / "logs" / "exit_supervisor_policy_robustness_latest.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return data


def iter_policy_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[int, str, str]] = set()
    for delay_payload in data.get("delays", []):
        if not isinstance(delay_payload, dict):
            continue
        for row in delay_payload.get("all_policies", []):
            if not isinstance(row, dict):
                continue
            key = (int(row.get("delay_seconds") or delay_payload.get("delay_seconds") or 0), str(row.get("policy") or ""), str(row.get("rule") or ""))
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
    return rows


def summarize_day_robustness(row: dict[str, Any], *, false_exit_penalty: float) -> dict[str, Any]:
    by_day = [item for item in row.get("by_day", []) if isinstance(item, dict)]
    day_deltas = [float(item.get("delta_dollars") or 0.0) for item in by_day]
    total_delta = float(row.get("delta_dollars") or 0.0)
    false_exit_cost = float(row.get("false_exit_cost_dollars") or 0.0)
    oracle_value = float(row.get("oracle_positive_only_delta_dollars") or 0.0)
    max_day_delta = max(day_deltas) if day_deltas else 0.0
    min_day_delta = min(day_deltas) if day_deltas else 0.0
    leave_one_day_min_delta = total_delta - max_day_delta if day_deltas else total_delta
    positive_day_count = sum(1 for value in day_deltas if value > 0)
    negative_day_count = sum(1 for value in day_deltas if value < 0)
    day_count = len(day_deltas)
    best_day_share = (max_day_delta / total_delta) if total_delta > 0 and max_day_delta > 0 else None
    false_cost_share_of_oracle = (false_exit_cost / oracle_value) if oracle_value > 0 else None
    risk_adjusted_delta = total_delta - (false_exit_penalty * false_exit_cost)
    overfit_flags: list[str] = []
    if day_count < 2:
        overfit_flags.append("too_few_days")
    if day_count >= 2 and positive_day_count < day_count:
        overfit_flags.append("has_negative_day")
    if best_day_share is not None and best_day_share >= 0.75:
        overfit_flags.append("one_day_carried")
    if leave_one_day_min_delta <= 0:
        overfit_flags.append("fails_leave_one_best_day_out")
    if false_cost_share_of_oracle is not None and false_cost_share_of_oracle >= 0.4:
        overfit_flags.append("high_false_exit_drag")
    if int(row.get("exit_count") or 0) < 5:
        overfit_flags.append("tiny_exit_sample")
    return {
        "delay_seconds": int(row.get("delay_seconds") or 0),
        "policy": str(row.get("policy") or ""),
        "rule": str(row.get("rule") or ""),
        "exit_count": int(row.get("exit_count") or 0),
        "delta_dollars": round(total_delta, 4),
        "risk_adjusted_delta_dollars": round(risk_adjusted_delta, 4),
        "false_exit_cost_dollars": round(false_exit_cost, 4),
        "oracle_positive_only_delta_dollars": round(oracle_value, 4),
        "positive_count": int(row.get("positive_count") or 0),
        "negative_count": int(row.get("negative_count") or 0),
        "exit_now_truth_count": int(row.get("exit_now_truth_count") or 0),
        "hold_truth_count": int(row.get("hold_truth_count") or 0),
        "day_count": day_count,
        "positive_day_count": int(positive_day_count),
        "negative_day_count": int(negative_day_count),
        "min_day_delta_dollars": round(min_day_delta, 4),
        "max_day_delta_dollars": round(max_day_delta, 4),
        "leave_one_best_day_out_delta_dollars": round(leave_one_day_min_delta, 4),
        "best_day_share": round(best_day_share, 4) if best_day_share is not None else None,
        "false_cost_share_of_oracle": round(false_cost_share_of_oracle, 4) if false_cost_share_of_oracle is not None else None,
        "overfit_flags": overfit_flags,
        "by_day": by_day,
    }


def policy_family(row: dict[str, Any]) -> str:
    policy = str(row.get("policy") or "")
    if policy == "static":
        return "static_rule"
    if "same_rule" in policy or "same_day_rule" in policy:
        return "slice_memory_gate"
    if "actual" in policy:
        return "recent_strategy_pnl_gate"
    return "other"


def analyze(input_path: Path, *, false_exit_penalty: float, min_delta: float) -> dict[str, Any]:
    data = load_json(input_path)
    rows = [
        summarize_day_robustness(row, false_exit_penalty=false_exit_penalty)
        for row in iter_policy_rows(data)
    ]
    rows = [row for row in rows if float(row["delta_dollars"]) >= min_delta]
    for row in rows:
        row["family"] = policy_family(row)
    robust = [
        row
        for row in rows
        if row["day_count"] >= 2
        and row["positive_day_count"] == row["day_count"]
        and row["leave_one_best_day_out_delta_dollars"] > 0
        and row["exit_count"] >= 5
    ]
    robust.sort(
        key=lambda row: (
            float(row["risk_adjusted_delta_dollars"]),
            float(row["delta_dollars"]),
            -float(row["false_exit_cost_dollars"]),
        ),
        reverse=True,
    )
    rows.sort(
        key=lambda row: (
            len(row["overfit_flags"]) == 0,
            float(row["risk_adjusted_delta_dollars"]),
            float(row["delta_dollars"]),
        ),
        reverse=True,
    )
    family_counts: dict[str, int] = {}
    for row in robust:
        family_counts[str(row["family"])] = family_counts.get(str(row["family"]), 0) + 1
    return {
        "source": str(input_path),
        "false_exit_penalty": float(false_exit_penalty),
        "min_delta_filter_dollars": float(min_delta),
        "candidate_count": int(len(rows)),
        "robust_candidate_count": int(len(robust)),
        "robust_family_counts": family_counts,
        "top_robust_candidates": robust[:20],
        "top_candidates_including_flagged": rows[:30],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress-test online exit-supervisor policies for day-level overfit risk.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--false-exit-penalty", type=float, default=0.5)
    parser.add_argument("--min-delta", type=float, default=8.0)
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    payload = analyze(input_path, false_exit_penalty=float(args.false_exit_penalty), min_delta=float(args.min_delta))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved exit-supervisor policy robustness to {output_path}")
    print(json.dumps({
        "candidate_count": payload["candidate_count"],
        "robust_candidate_count": payload["robust_candidate_count"],
        "robust_family_counts": payload["robust_family_counts"],
        "top_robust_candidates": payload["top_robust_candidates"][:5],
    }, indent=2))


if __name__ == "__main__":
    main()
