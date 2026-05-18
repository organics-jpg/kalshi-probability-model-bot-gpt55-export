from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_exit_broad_slice_filter_scan_latest.json"
DEFAULT_BENCH_PATHS = [
    ROOT / "logs" / "truffle_exit_supervisor_bench_45s_latest.json",
    ROOT / "logs" / "truffle_exit_supervisor_bench_latest.json",
    ROOT / "logs" / "truffle_exit_supervisor_bench_105s_latest.json",
]


FEATURES = [
    "side",
    "pre.last30_move_state",
    "pre.last60_move_state",
    "pre.open_to_entry_runup",
    "pre.entry_timing_state",
    "pre.entry_pressure_state",
    "post.current_strength",
    "post.damage_state",
    "post.rebound_state",
    "post.current_vs_entry_state",
    "tech.rsi14_slope_state",
    "tech.macd_hist_state",
    "tech.price_vs_ema21_state",
]


def get_path(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def flatten_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    pre = payload.get("pre_entry") if isinstance(payload.get("pre_entry"), dict) else {}
    post = payload.get("post_entry") if isinstance(payload.get("post_entry"), dict) else {}
    technicals = payload.get("technicals") if isinstance(payload.get("technicals"), dict) else {}
    tech = technicals.get("post_entry") if isinstance(technicals.get("post_entry"), dict) else {}
    flattened = {
        "market": row.get("market"),
        "side": row.get("side"),
        "shadow_label": row.get("shadow_label"),
        "delta_dollars": float(row.get("delta_dollars") or 0.0),
    }
    for key, value in pre.items():
        flattened[f"pre.{key}"] = value
    for key, value in post.items():
        flattened[f"post.{key}"] = value
    for key, value in tech.items():
        flattened[f"tech.{key}"] = value
    return flattened


def summarize_subset(rows: list[dict[str, Any]], *, rule: str) -> dict[str, Any]:
    red = [row for row in rows if row.get("shadow_label") == "RED_LIGHT"]
    neutral = [row for row in rows if row.get("shadow_label") == "NEUTRAL"]
    green = [row for row in rows if row.get("shadow_label") == "GREEN_LIGHT"]
    delta = sum(float(row.get("delta_dollars") or 0.0) for row in rows)
    return {
        "rule": rule,
        "count": int(len(rows)),
        "delta_dollars": round(delta, 4),
        "red_count": int(len(red)),
        "neutral_count": int(len(neutral)),
        "green_count": int(len(green)),
        "red_precision": round(len(red) / len(rows), 4) if rows else None,
        "non_green_precision": round((len(red) + len(neutral)) / len(rows), 4) if rows else None,
        "markets": [str(row.get("market") or "") for row in rows],
    }


def scan_rules(rows: list[dict[str, Any]], *, min_count: int, max_width: int, max_rules: int) -> list[dict[str, Any]]:
    values_by_feature = {
        feature: sorted({row.get(feature) for row in rows if row.get(feature) is not None})
        for feature in FEATURES
    }
    results: list[dict[str, Any]] = []
    for width in range(1, max_width + 1):
        for features in combinations(FEATURES, width):
            value_lists = [values_by_feature[feature] for feature in features]
            if not all(value_lists):
                continue
            for values in product(*value_lists):
                subset = [
                    row
                    for row in rows
                    if all(row.get(feature) == value for feature, value in zip(features, values))
                ]
                if len(subset) < min_count:
                    continue
                summary = summarize_subset(
                    subset,
                    rule=" & ".join(f"{feature}={value}" for feature, value in zip(features, values)),
                )
                if float(summary["delta_dollars"]) <= 0:
                    continue
                results.append(summary)
    results.sort(
        key=lambda row: (
            float(row["delta_dollars"]),
            float(row["non_green_precision"] or 0.0),
            float(row["red_precision"] or 0.0),
            -int(row["green_count"]),
        ),
        reverse=True,
    )
    return results[:max_rules]


def analyze_bench(path: Path, *, min_count: int, max_width: int, max_rules: int) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        flatten_row(row)
        for row in data.get("rows", [])
        if "broad_no_neutral_neutral" in list(row.get("slice_tags") or [])
    ]
    return {
        "bench_path": str(path),
        "summary": data.get("summary", {}),
        "broad_slice_summary": summarize_subset(rows, rule="broad_no_neutral_neutral"),
        "top_subfilters": scan_rules(rows, min_count=min_count, max_width=max_width, max_rules=max_rules),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine simple deterministic subfilters inside the broad Truffle exit slice.")
    parser.add_argument("--bench-paths", nargs="*", default=[str(path) for path in DEFAULT_BENCH_PATHS])
    parser.add_argument("--min-count", type=int, default=2)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--max-rules", type=int, default=20)
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
        "benches": [
            analyze_bench(path, min_count=int(args.min_count), max_width=int(args.max_width), max_rules=int(args.max_rules))
            for path in bench_paths
        ],
    }
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved broad exit slice filter scan to {output_path}")
    for bench in payload["benches"]:
        delay = bench["summary"].get("delay_seconds")
        broad = bench["broad_slice_summary"]
        print(f"delay={delay} broad_delta={broad['delta_dollars']} count={broad['count']}")
        for rule in bench["top_subfilters"][:5]:
            print(
                rule["rule"],
                f"delta={rule['delta_dollars']}",
                f"count={rule['count']}",
                f"green={rule['green_count']}",
                f"red={rule['red_count']}",
            )


if __name__ == "__main__":
    main()
