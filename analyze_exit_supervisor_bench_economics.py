from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_exit_supervisor_bench_economics_latest.json"
DEFAULT_BENCH_PATHS = [
    ROOT / "logs" / "truffle_exit_supervisor_bench_45s_latest.json",
    ROOT / "logs" / "truffle_exit_supervisor_bench_latest.json",
    ROOT / "logs" / "truffle_exit_supervisor_bench_105s_latest.json",
]


def summarize_rows(rows: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    red_rows = [row for row in rows if str(row.get("shadow_label") or "") == "RED_LIGHT"]
    neutral_rows = [row for row in rows if str(row.get("shadow_label") or "") == "NEUTRAL"]
    green_rows = [row for row in rows if str(row.get("shadow_label") or "") == "GREEN_LIGHT"]
    positive_deltas = [float(row.get("delta_dollars") or 0.0) for row in rows if float(row.get("delta_dollars") or 0.0) > 0]
    negative_deltas = [float(row.get("delta_dollars") or 0.0) for row in rows if float(row.get("delta_dollars") or 0.0) < 0]
    red_deltas = [float(row.get("delta_dollars") or 0.0) for row in red_rows]
    non_red_negative_deltas = [
        float(row.get("delta_dollars") or 0.0)
        for row in neutral_rows + green_rows
        if float(row.get("delta_dollars") or 0.0) < 0
    ]

    avg_red_save = sum(red_deltas) / len(red_deltas) if red_deltas else None
    avg_wrong_cost = -sum(non_red_negative_deltas) / len(non_red_negative_deltas) if non_red_negative_deltas else None
    break_even_precision = (
        avg_wrong_cost / (avg_red_save + avg_wrong_cost)
        if avg_red_save is not None and avg_wrong_cost not in (None, 0.0)
        else None
    )
    wrong_calls_per_red_budget = (
        avg_red_save / avg_wrong_cost
        if avg_red_save is not None and avg_wrong_cost not in (None, 0.0)
        else None
    )

    return {
        "label": label,
        "count": int(len(rows)),
        "red_count": int(len(red_rows)),
        "neutral_count": int(len(neutral_rows)),
        "green_count": int(len(green_rows)),
        "delta_if_exit_all_dollars": round(sum(float(row.get("delta_dollars") or 0.0) for row in rows), 4),
        "upper_bound_exit_red_only_dollars": round(sum(red_deltas), 4),
        "delta_if_exit_red_and_neutral_dollars": round(
            sum(float(row.get("delta_dollars") or 0.0) for row in red_rows + neutral_rows),
            4,
        ),
        "positive_delta_count": int(len(positive_deltas)),
        "negative_delta_count": int(len(negative_deltas)),
        "avg_positive_delta": round(sum(positive_deltas) / len(positive_deltas), 4) if positive_deltas else None,
        "avg_negative_delta_abs": round(-sum(negative_deltas) / len(negative_deltas), 4) if negative_deltas else None,
        "avg_red_save": round(avg_red_save, 4) if avg_red_save is not None else None,
        "avg_wrong_non_red_cost": round(avg_wrong_cost, 4) if avg_wrong_cost is not None else None,
        "break_even_precision_vs_non_red_wrong_cost": round(break_even_precision, 4) if break_even_precision is not None else None,
        "wrong_non_red_calls_budget_per_red_call": round(wrong_calls_per_red_budget, 4) if wrong_calls_per_red_budget is not None else None,
    }


def analyze_bench(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = list(data.get("rows") or [])
    tags = sorted({tag for row in rows for tag in list(row.get("slice_tags") or [])})
    tagged_rows = [row for row in rows if row.get("slice_tags")]
    untagged_rows = [row for row in rows if not row.get("slice_tags")]
    by_tag = {
        tag: summarize_rows([row for row in rows if tag in list(row.get("slice_tags") or [])], label=tag)
        for tag in tags
    }
    return {
        "bench_path": str(path),
        "summary": data.get("summary", {}),
        "all_rows": summarize_rows(rows, label="all_rows"),
        "tagged_rows": summarize_rows(tagged_rows, label="tagged_rows"),
        "untagged_holdout_rows": summarize_rows(untagged_rows, label="untagged_holdout_rows"),
        "by_tag": by_tag,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze economic break-even requirements for Truffle exit-supervisor bench cases.")
    parser.add_argument("--bench-paths", nargs="*", default=[str(path) for path in DEFAULT_BENCH_PATHS])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    bench_paths = []
    for raw_path in args.bench_paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            bench_paths.append(path)

    payload = {
        "benches": [analyze_bench(path) for path in bench_paths],
    }
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved Truffle exit bench economics to {output_path}")
    for bench in payload["benches"]:
        summary = bench.get("summary", {})
        print(f"delay={summary.get('delay_seconds')} bench_count={summary.get('bench_count')}")
        ranked = sorted(
            bench["by_tag"].values(),
            key=lambda row: (
                float(row.get("delta_if_exit_all_dollars") or 0.0),
                float(row.get("upper_bound_exit_red_only_dollars") or 0.0),
            ),
            reverse=True,
        )
        for row in ranked[:4]:
            print(
                row["label"],
                f"exit_all_delta={row['delta_if_exit_all_dollars']}",
                f"red={row['red_count']}",
                f"green={row['green_count']}",
                f"breakeven_precision={row['break_even_precision_vs_non_red_wrong_cost']}",
                f"wrong_budget={row['wrong_non_red_calls_budget_per_red_call']}",
            )


if __name__ == "__main__":
    main()
