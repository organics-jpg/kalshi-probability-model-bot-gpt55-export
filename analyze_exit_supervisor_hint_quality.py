from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUTS = [
    ROOT / "logs" / "online_exit_supervisor_shadow_replay_60s_tagged_latest.json",
    ROOT / "logs" / "online_exit_supervisor_shadow_replay_60s_all_latest.json",
]
DEFAULT_OUTPUT = ROOT / "logs" / "exit_supervisor_hint_quality_latest.json"


def load_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows") if isinstance(data, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [float(row.get("delta_dollars") or 0.0) for row in rows]
    return {
        "count": int(len(rows)),
        "label_counts": dict(collections.Counter(str(row.get("shadow_label") or "") for row in rows)),
        "delta_dollars": round(float(sum(deltas)), 4),
        "false_exit_cost_dollars": round(float(-sum(delta for delta in deltas if delta < 0)), 4),
        "oracle_exit_value_dollars": round(float(sum(delta for delta in deltas if delta > 0)), 4),
    }


def get_hint(row: dict[str, Any], name: str) -> dict[str, Any]:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    hint = payload.get(name)
    return hint if isinstance(hint, dict) else {}


def selector_rows(rows: list[dict[str, Any]], selector: Callable[[dict[str, Any]], bool]) -> list[dict[str, Any]]:
    return [row for row in rows if selector(row)]


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selectors: dict[str, Callable[[dict[str, Any]], bool]] = {
        "deterministic_exit_candidate": lambda row: get_hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE",
        "deterministic_hold": lambda row: get_hint(row, "deterministic_policy_hints").get("default_decision_hint") == "HOLD",
        "memory_same_slice_recent_positive": lambda row: get_hint(row, "shadow_memory_policy_hint").get("state") == "same_slice_recent_positive",
        "memory_same_slice_recent_negative": lambda row: get_hint(row, "shadow_memory_policy_hint").get("state") == "same_slice_recent_negative",
        "exit_candidate_and_memory_positive": lambda row: (
            get_hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE"
            and get_hint(row, "shadow_memory_policy_hint").get("state") == "same_slice_recent_positive"
        ),
        "exit_candidate_and_not_memory_negative": lambda row: (
            get_hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE"
            and get_hint(row, "shadow_memory_policy_hint").get("state") != "same_slice_recent_negative"
        ),
        "exit_candidate_and_no_hold_guard": lambda row: (
            get_hint(row, "deterministic_policy_hints").get("default_decision_hint") == "EXIT_CANDIDATE"
            and not bool(get_hint(row, "deterministic_policy_hints").get("conservative_hold_guard"))
        ),
    }
    by_selector = {
        name: metric_summary(selector_rows(rows, selector))
        for name, selector in selectors.items()
    }
    by_memory_state: dict[str, Any] = {}
    for state in sorted({str(get_hint(row, "shadow_memory_policy_hint").get("state") or "missing") for row in rows}):
        by_memory_state[state] = metric_summary(
            [row for row in rows if str(get_hint(row, "shadow_memory_policy_hint").get("state") or "missing") == state]
        )
    by_default_hint: dict[str, Any] = {}
    for state in sorted({str(get_hint(row, "deterministic_policy_hints").get("default_decision_hint") or "missing") for row in rows}):
        by_default_hint[state] = metric_summary(
            [row for row in rows if str(get_hint(row, "deterministic_policy_hints").get("default_decision_hint") or "missing") == state]
        )
    return {
        "overall": metric_summary(rows),
        "by_default_hint": by_default_hint,
        "by_memory_state": by_memory_state,
        "selectors": by_selector,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate deterministic and memory hints in exit-supervisor replay payloads.")
    parser.add_argument("--input-paths", nargs="*", default=[str(path) for path in DEFAULT_INPUTS])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    results: dict[str, Any] = {}
    for raw_path in args.input_paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            continue
        results[str(path)] = analyze_rows(load_rows(path))

    payload = {"inputs": list(results.keys()), "results": results}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved exit-supervisor hint quality to {output_path}")
    for path, result in results.items():
        selectors = result.get("selectors", {})
        print(path)
        print(json.dumps({
            "overall": result.get("overall"),
            "deterministic_exit_candidate": selectors.get("deterministic_exit_candidate"),
            "exit_candidate_and_memory_positive": selectors.get("exit_candidate_and_memory_positive"),
            "exit_candidate_and_not_memory_negative": selectors.get("exit_candidate_and_not_memory_negative"),
        }, indent=2))


if __name__ == "__main__":
    main()
