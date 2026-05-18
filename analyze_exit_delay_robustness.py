from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = ROOT / "logs" / "post_entry_exit_delay_sweep_wide_latest.json"
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "post_entry_exit_delay_robustness_latest.json"


def robust_summary(values: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [float(row["delta_dollars"]) for row in values]
    counts = [int(row["count"]) for row in values]
    return {
        "delay_count": int(len(values)),
        "positive_delay_count": int(sum(1 for value in deltas if value > 0)),
        "negative_delay_count": int(sum(1 for value in deltas if value < 0)),
        "avg_delta_dollars": round(sum(deltas) / max(1, len(deltas)), 4),
        "min_delta_dollars": round(min(deltas), 4) if deltas else None,
        "max_delta_dollars": round(max(deltas), 4) if deltas else None,
        "avg_count": round(sum(counts) / max(1, len(counts)), 2),
        "best_delay_seconds": int(values[deltas.index(max(deltas))]["delay_seconds"]) if deltas else None,
        "worst_delay_seconds": int(values[deltas.index(min(deltas))]["delay_seconds"]) if deltas else None,
        "by_delay": values,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize robustness of post-entry exit policies across delay sweeps.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--core-delays", default="45,60,75,90,105,120")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    data = json.loads(input_path.read_text(encoding="utf-8"))

    core_delay_set = {int(chunk.strip()) for chunk in str(args.core_delays).split(",") if chunk.strip()}
    all_policy_rows: dict[str, list[dict[str, Any]]] = {}
    core_policy_rows: dict[str, list[dict[str, Any]]] = {}
    for result in data.get("results", []):
        delay = int(result.get("delay_seconds"))
        for name, summary in (result.get("policy_summaries") or {}).items():
            row = {
                "delay_seconds": delay,
                "delta_dollars": float(summary.get("delta_dollars") or 0.0),
                "count": int(summary.get("count") or 0),
                "improved_trade_count": int(summary.get("improved_trade_count") or 0),
                "harmed_trade_count": int(summary.get("harmed_trade_count") or 0),
                "avg_positive_delta": summary.get("avg_positive_delta"),
                "avg_negative_delta_abs": summary.get("avg_negative_delta_abs"),
            }
            all_policy_rows.setdefault(name, []).append(row)
            if delay in core_delay_set:
                core_policy_rows.setdefault(name, []).append(row)

    all_policy_summary = {
        name: robust_summary(rows)
        for name, rows in sorted(all_policy_rows.items())
    }
    core_policy_summary = {
        name: robust_summary(rows)
        for name, rows in sorted(core_policy_rows.items())
    }
    ranked_core = sorted(
        [
            {"policy": name, **summary}
            for name, summary in core_policy_summary.items()
        ],
        key=lambda row: (
            int(row["positive_delay_count"]),
            float(row["min_delta_dollars"] or 0.0),
            float(row["avg_delta_dollars"]),
        ),
        reverse=True,
    )

    payload = {
        "source": str(input_path),
        "summary": data.get("summary", {}),
        "core_delays": sorted(core_delay_set),
        "policy_robustness_all_delays": all_policy_summary,
        "policy_robustness_core_delays": core_policy_summary,
        "ranked_core_policies": ranked_core,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved exit delay robustness analysis to {output_path}")
    for row in ranked_core[:8]:
        print(
            row["policy"],
            f"positive={row['positive_delay_count']}/{row['delay_count']}",
            f"avg_delta={row['avg_delta_dollars']}",
            f"min_delta={row['min_delta_dollars']}",
            f"best_delay={row['best_delay_seconds']}",
        )


if __name__ == "__main__":
    main()
