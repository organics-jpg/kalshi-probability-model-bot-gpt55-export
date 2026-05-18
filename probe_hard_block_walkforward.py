from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from probe_edge_rules import build_case_frame

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "hard_block_walkforward_latest.json"

PNL_THRESHOLDS = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
STALE_THRESHOLDS = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
EXIT_EXCEPTIONS = [2, 3, 4]


def make_keep_mask(frame: pd.DataFrame, pnl_threshold: float, stale_threshold: float, exit_exception: int) -> pd.Series:
    return ~(
        ((frame["pnl4"] >= pnl_threshold) | (frame["stale_per_signal4"] >= stale_threshold))
        & ~(frame["exits4"] >= exit_exception)
    )


def summarize_kept(frame: pd.DataFrame, keep_mask: pd.Series) -> dict[str, float | int]:
    kept = frame.loc[keep_mask].copy()
    return {
        "trades": int(len(kept)),
        "net_pnl_dollars": round(float(kept["next_pnl"].sum()), 4) if not kept.empty else 0.0,
        "win_rate": round(float((kept["next_pnl"] > 0).mean()), 4) if not kept.empty else 0.0,
        "avg_pnl_dollars": round(float(kept["next_pnl"].mean()), 4) if not kept.empty else 0.0,
        "keep_ratio": round(float(len(kept) / len(frame)), 4) if len(frame) else 0.0,
    }


def contiguous_fold_dates(dates: list[str], fold_count: int = 4) -> list[list[str]]:
    if not dates:
        return []
    chunk_size = math.ceil(len(dates) / fold_count)
    return [dates[idx * chunk_size : (idx + 1) * chunk_size] for idx in range(fold_count)]


def contiguous_fold_summaries(frame: pd.DataFrame, keep_mask: pd.Series, fold_count: int = 4) -> tuple[list[dict[str, object]], float]:
    dates = sorted(str(value) for value in frame["entry_date"].dropna().unique())
    folds = contiguous_fold_dates(dates, fold_count=fold_count)
    summaries: list[dict[str, object]] = []
    fold_nets: list[float] = []
    kept = frame.loc[keep_mask].copy()
    for idx, fold_dates in enumerate(folds, start=1):
        fold = kept[kept["entry_date"].isin(fold_dates)].copy()
        net = float(fold["next_pnl"].sum()) if not fold.empty else 0.0
        fold_nets.append(net)
        summaries.append(
            {
                "fold_index": idx,
                "fold_dates": list(fold_dates),
                "trades": int(len(fold)),
                "net_pnl_dollars": round(net, 4),
                "win_rate": round(float((fold["next_pnl"] > 0).mean()), 4) if not fold.empty else 0.0,
            }
        )
    min_fold = round(min(fold_nets), 4) if fold_nets else 0.0
    return summaries, min_fold


def fixed_rule_result(frame: pd.DataFrame, name: str, *, params: tuple[float, float, int] | None) -> dict[str, object]:
    keep_mask = pd.Series(True, index=frame.index) if params is None else make_keep_mask(frame, *params)
    folds, min_fold = contiguous_fold_summaries(frame, keep_mask)
    return {
        "name": name,
        "params": list(params) if params is not None else None,
        "all_days": summarize_kept(frame, keep_mask),
        "contiguous_folds": folds,
        "min_contiguous_fold_net_pnl_dollars": min_fold,
    }


def full_grid_scan(frame: pd.DataFrame) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for pnl_threshold in PNL_THRESHOLDS:
        for stale_threshold in STALE_THRESHOLDS:
            for exit_exception in EXIT_EXCEPTIONS:
                keep_mask = make_keep_mask(frame, pnl_threshold, stale_threshold, exit_exception)
                folds, min_fold = contiguous_fold_summaries(frame, keep_mask)
                summary = summarize_kept(frame, keep_mask)
                rows.append(
                    {
                        "params": [pnl_threshold, stale_threshold, exit_exception],
                        **summary,
                        "min_contiguous_fold_net_pnl_dollars": min_fold,
                        "contiguous_folds": folds,
                    }
                )

    ranked_by_net = sorted(
        rows,
        key=lambda rec: (
            float(rec["net_pnl_dollars"]),
            float(rec["min_contiguous_fold_net_pnl_dollars"]),
            float(rec["win_rate"]),
        ),
        reverse=True,
    )
    stable_pool = [row for row in rows if int(row["trades"]) >= max(1, int(len(frame) * 0.7))]
    ranked_by_stability = sorted(
        stable_pool,
        key=lambda rec: (
            float(rec["min_contiguous_fold_net_pnl_dollars"]),
            float(rec["net_pnl_dollars"]),
            float(rec["win_rate"]),
        ),
        reverse=True,
    )
    return ranked_by_net[:10], ranked_by_stability[:10]


def walkforward_search(frame: pd.DataFrame, *, min_train_days: int = 3) -> dict[str, object]:
    dates = sorted(str(value) for value in frame["entry_date"].dropna().unique())
    rows: list[dict[str, object]] = []
    aggregate_kept_net = 0.0
    aggregate_base_net = 0.0
    aggregate_kept_trades = 0
    aggregate_base_trades = 0

    for idx in range(min_train_days, len(dates)):
        train_dates = dates[:idx]
        test_date = dates[idx]
        train = frame[frame["entry_date"].isin(train_dates)].copy()
        test = frame[frame["entry_date"] == test_date].copy()
        baseline_test = summarize_kept(test, pd.Series(True, index=test.index))

        min_keep_ratio = 0.65
        min_train_trades = max(30, int(len(train) * min_keep_ratio))
        candidates: list[tuple[tuple[float, float, int], dict[str, float | int]]] = []
        for pnl_threshold in PNL_THRESHOLDS:
            for stale_threshold in STALE_THRESHOLDS:
                for exit_exception in EXIT_EXCEPTIONS:
                    params = (pnl_threshold, stale_threshold, exit_exception)
                    summary = summarize_kept(train, make_keep_mask(train, *params))
                    if int(summary["trades"]) < min_train_trades:
                        continue
                    candidates.append((params, summary))

        if not candidates:
            best_params = None
            test_keep = pd.Series(True, index=test.index)
            train_choice = {"trades": int(len(train)), "net_pnl_dollars": 0.0, "win_rate": 0.0, "keep_ratio": 1.0}
        else:
            candidates.sort(
                key=lambda item: (
                    float(item[1]["net_pnl_dollars"]),
                    float(item[1]["win_rate"]),
                    float(item[1]["keep_ratio"]),
                ),
                reverse=True,
            )
            best_params, train_choice = candidates[0]
            test_keep = make_keep_mask(test, *best_params)

        test_summary = summarize_kept(test, test_keep)
        aggregate_kept_net += float(test_summary["net_pnl_dollars"])
        aggregate_base_net += float(baseline_test["net_pnl_dollars"])
        aggregate_kept_trades += int(test_summary["trades"])
        aggregate_base_trades += int(baseline_test["trades"])

        rows.append(
            {
                "test_date": test_date,
                "selected_params": list(best_params) if best_params is not None else None,
                "train_choice": train_choice,
                "test_kept": test_summary,
                "test_baseline": baseline_test,
                "test_net_delta_dollars": round(
                    float(test_summary["net_pnl_dollars"]) - float(baseline_test["net_pnl_dollars"]),
                    4,
                ),
            }
        )

    return {
        "min_train_days": min_train_days,
        "selection_constraints": {
            "min_keep_ratio": 0.65,
            "min_train_trades": "max(30, floor(train_rows * 0.65))",
            "ranking": ["train net_pnl_dollars", "train win_rate", "train keep_ratio"],
        },
        "days": rows,
        "aggregate": {
            "kept_trades": int(aggregate_kept_trades),
            "baseline_trades": int(aggregate_base_trades),
            "kept_net_pnl_dollars": round(aggregate_kept_net, 4),
            "baseline_net_pnl_dollars": round(aggregate_base_net, 4),
            "net_delta_dollars": round(aggregate_kept_net - aggregate_base_net, 4),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward stress test for simple 90_78 hard-block rules.")
    parser.add_argument("--dataset-tag", default="live_90_78")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    frame = build_case_frame(args.dataset_tag)
    if frame.empty:
        raise RuntimeError(f"No cases found for dataset {args.dataset_tag}")

    frame = frame.sort_values(["entry_date", "market"]).reset_index(drop=True)
    top_by_net, top_by_stability = full_grid_scan(frame)
    payload = {
        "dataset_tag": args.dataset_tag,
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "case_count": int(len(frame)),
        "unique_days": int(frame["entry_date"].nunique()),
        "grid": {
            "pnl_thresholds": PNL_THRESHOLDS,
            "stale_thresholds": STALE_THRESHOLDS,
            "exit_exceptions": EXIT_EXCEPTIONS,
        },
        "fixed_rules": {
            "baseline": fixed_rule_result(frame, "baseline", params=None),
            "old_fixed": fixed_rule_result(frame, "old_fixed", params=(3.0, 1.5, 3)),
            "tuned_fixed": fixed_rule_result(frame, "tuned_fixed", params=(2.5, 1.25, 3)),
        },
        "top_fixed_rules_by_net": top_by_net,
        "top_fixed_rules_by_stability": top_by_stability,
        "walkforward": walkforward_search(frame, min_train_days=3),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    tuned = payload["fixed_rules"]["tuned_fixed"]["all_days"]
    wf = payload["walkforward"]["aggregate"]
    print(f"Saved hard-block walk-forward probe to {output_path}")
    print(
        "tuned_fixed:",
        f"trades={tuned['trades']}",
        f"net={tuned['net_pnl_dollars']:.2f}",
        f"win_rate={tuned['win_rate']:.2%}",
    )
    print(
        "walkforward:",
        f"kept_trades={wf['kept_trades']}",
        f"baseline_trades={wf['baseline_trades']}",
        f"delta={wf['net_delta_dollars']:.2f}",
    )


if __name__ == "__main__":
    main()
