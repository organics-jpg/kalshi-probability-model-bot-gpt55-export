from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from probe_truffle_historical_replay import build_ordered_market_records

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "meta_classifier_probe_latest.json"
SESSION_KEYS = ["afternoon", "evening", "late_evening", "morning", "overnight", "unknown"]


def build_feature_frame(dataset_tag: str) -> pd.DataFrame:
    records = build_ordered_market_records(dataset_tag)
    rows: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        if not record.traded:
            continue
        previous_all = records[:idx]
        previous_traded = [row for row in previous_all if row.traded]
        if len(previous_traded) < 4:
            continue

        def streak(predicate: Callable[[Any], bool]) -> int:
            count = 0
            for prior in reversed(previous_traded):
                if predicate(prior):
                    count += 1
                else:
                    break
            return count

        def tail_stats(items: list[Any]) -> dict[str, float | int]:
            pnls = [float(row.pnl_dollars or 0.0) for row in items]
            return {
                "pnl": float(sum(pnls)),
                "wins": int(sum(1 for value in pnls if value > 0)),
                "losses": int(sum(1 for value in pnls if value < 0)),
                "exits": int(sum(1 for row in items if row.outcome_type == "exit")),
                "avg": float(sum(pnls) / len(pnls)) if pnls else 0.0,
            }

        recent_traded = {
            1: previous_traded[-1:],
            2: previous_traded[-2:],
            4: previous_traded[-4:],
            8: previous_traded[-8:],
        }
        recent_all4 = previous_all[-4:]
        latency_samples_4 = [value for row in recent_all4 for value in row.submit_latency_samples_ms]

        row: dict[str, Any] = {
            "dataset": dataset_tag,
            "market": record.market,
            "entry_date": (
                pd.Timestamp(record.market_close_time).tz_convert("America/New_York").strftime("%Y-%m-%d")
                if record.market_close_time
                else ""
            ),
            "session": record.session or "unknown",
            "next_pnl": float(record.pnl_dollars or 0.0),
            "target_win": 1 if float(record.pnl_dollars or 0.0) > 0 else 0,
            "win_streak": streak(lambda item: float(item.pnl_dollars or 0.0) > 0),
            "loss_streak": streak(lambda item: float(item.pnl_dollars or 0.0) < 0),
            "stale4": int(sum(int(row.stale_book_deferral_count or 0) for row in recent_all4)),
            "ioc4": int(sum(int(row.ioc_zero_fill_count or 0) for row in recent_all4)),
            "signals4": int(sum(int(row.signal_count or 0) for row in recent_all4)),
            "lat95_4": float(pd.Series(latency_samples_4).quantile(0.95)) if latency_samples_4 else 0.0,
        }
        for window, items in recent_traded.items():
            stats = tail_stats(items)
            for name, value in stats.items():
                row[f"{name}{window}"] = value
        row["staleps4"] = row["stale4"] / max(1, row["signals4"])
        row["pf4"] = row["wins4"] / max(1, row["wins4"] + row["losses4"])
        rows.append(row)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    session_dummies = pd.get_dummies(frame["session"], prefix="session")
    for session_key in SESSION_KEYS:
        column = f"session_{session_key}"
        if column not in session_dummies.columns:
            session_dummies[column] = 0
    return pd.concat([frame.drop(columns=["session"]), session_dummies[sorted(session_dummies.columns)]], axis=1)


def choose_threshold(probabilities: np.ndarray, pnls: np.ndarray, *, min_keep_ratio: float = 0.45) -> float:
    best_threshold = 0.5
    best_score: tuple[float, float, float] | None = None
    for threshold in [value / 100.0 for value in range(45, 91, 5)]:
        keep_mask = probabilities >= threshold
        if float(keep_mask.mean()) < min_keep_ratio:
            continue
        kept_pnls = pnls[keep_mask]
        if kept_pnls.size == 0:
            continue
        score = (
            float(kept_pnls.sum()),
            float((kept_pnls > 0).mean()),
            float(keep_mask.mean()),
        )
        if best_score is None or score > best_score:
            best_score = score
            best_threshold = threshold
    return best_threshold


def walkforward(frame: pd.DataFrame, name: str, model_factory: Callable[[], Any]) -> dict[str, Any]:
    feature_columns = [column for column in frame.columns if column not in {"dataset", "market", "entry_date", "next_pnl", "target_win"}]
    dates = sorted(str(value) for value in frame["entry_date"].dropna().unique())
    rows: list[dict[str, Any]] = []
    kept_net = 0.0
    baseline_net = 0.0
    kept_trades = 0
    baseline_trades = 0

    for idx in range(3, len(dates)):
        train = frame[frame["entry_date"].isin(dates[:idx])].copy()
        test = frame[frame["entry_date"] == dates[idx]].copy()
        model = model_factory()
        model.fit(train[feature_columns].fillna(0.0), train["target_win"])
        train_prob = model.predict_proba(train[feature_columns].fillna(0.0))[:, 1]
        threshold = choose_threshold(train_prob, train["next_pnl"].to_numpy())
        test_prob = model.predict_proba(test[feature_columns].fillna(0.0))[:, 1]
        keep_mask = test_prob >= threshold
        kept = test.loc[keep_mask].copy()

        kept_net += float(kept["next_pnl"].sum())
        baseline_net += float(test["next_pnl"].sum())
        kept_trades += int(len(kept))
        baseline_trades += int(len(test))
        rows.append(
            {
                "test_date": dates[idx],
                "threshold": threshold,
                "kept_trades": int(len(kept)),
                "baseline_trades": int(len(test)),
                "kept_net_pnl_dollars": round(float(kept["next_pnl"].sum()), 4),
                "baseline_net_pnl_dollars": round(float(test["next_pnl"].sum()), 4),
                "net_delta_dollars": round(float(kept["next_pnl"].sum()) - float(test["next_pnl"].sum()), 4),
            }
        )

    return {
        "model": name,
        "kept_trades": int(kept_trades),
        "baseline_trades": int(baseline_trades),
        "kept_net_pnl_dollars": round(kept_net, 4),
        "baseline_net_pnl_dollars": round(baseline_net, 4),
        "net_delta_dollars": round(kept_net - baseline_net, 4),
        "days": rows,
    }


def cross_dataset_transfer(train_frame: pd.DataFrame, test_frame: pd.DataFrame) -> dict[str, Any]:
    feature_columns = [column for column in train_frame.columns if column not in {"dataset", "market", "entry_date", "next_pnl", "target_win"}]
    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("logreg", LogisticRegression(max_iter=5000)),
        ]
    )
    model.fit(train_frame[feature_columns].fillna(0.0), train_frame["target_win"])
    train_prob = model.predict_proba(train_frame[feature_columns].fillna(0.0))[:, 1]
    threshold = choose_threshold(train_prob, train_frame["next_pnl"].to_numpy())
    test_prob = model.predict_proba(test_frame[feature_columns].fillna(0.0))[:, 1]
    keep_mask = test_prob >= threshold
    kept = test_frame.loc[keep_mask].copy()

    coefficients = model.named_steps["logreg"].coef_[0]
    coefficient_frame = pd.DataFrame({"feature": feature_columns, "coef": coefficients}).sort_values("coef")
    return {
        "threshold": threshold,
        "kept_trades": int(len(kept)),
        "baseline_trades": int(len(test_frame)),
        "kept_net_pnl_dollars": round(float(kept["next_pnl"].sum()), 4),
        "baseline_net_pnl_dollars": round(float(test_frame["next_pnl"].sum()), 4),
        "net_delta_dollars": round(float(kept["next_pnl"].sum()) - float(test_frame["next_pnl"].sum()), 4),
        "kept_win_rate": round(float((kept["next_pnl"] > 0).mean()), 4) if not kept.empty else 0.0,
        "top_negative_coefficients": coefficient_frame.head(10).to_dict("records"),
        "top_positive_coefficients": coefficient_frame.tail(10).iloc[::-1].to_dict("records"),
    }


def evaluate_datasets(dataset_tags: list[str]) -> dict[str, Any]:
    frames = {tag: build_feature_frame(tag) for tag in dataset_tags}
    models = [
        ("logreg_scaled", lambda: Pipeline([("scaler", StandardScaler()), ("logreg", LogisticRegression(max_iter=5000))])),
        ("tree_depth_2_leaf_20", lambda: DecisionTreeClassifier(max_depth=2, min_samples_leaf=20, random_state=0)),
        ("tree_depth_3_leaf_20", lambda: DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=0)),
        ("rf_depth_3_leaf_20", lambda: RandomForestClassifier(n_estimators=200, max_depth=3, min_samples_leaf=20, random_state=0)),
    ]

    payload: dict[str, Any] = {"datasets": [], "cross_dataset_transfer": []}
    for dataset_tag in dataset_tags:
        frame = frames[dataset_tag]
        if frame.empty:
            raise RuntimeError(f"No classifier rows found for dataset {dataset_tag}")
        model_rows = [walkforward(frame, name, factory) for name, factory in models]
        payload["datasets"].append(
            {
                "dataset_tag": dataset_tag,
                "row_count": int(len(frame)),
                "day_count": int(frame["entry_date"].nunique()),
                "model_results": sorted(model_rows, key=lambda row: float(row["net_delta_dollars"]), reverse=True),
            }
        )

    if len(dataset_tags) >= 2:
        for train_tag in dataset_tags:
            for test_tag in dataset_tags:
                if train_tag == test_tag:
                    continue
                payload["cross_dataset_transfer"].append(
                    {
                        "train_dataset": train_tag,
                        "test_dataset": test_tag,
                        **cross_dataset_transfer(frames[train_tag], frames[test_tag]),
                    }
                )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark shallow walk-forward classifiers against recent-window trade features.")
    parser.add_argument("--datasets", nargs="+", default=["live_90_78", "live_90_70"])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        **evaluate_datasets(args.datasets),
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved meta-classifier probe to {output_path}")
    for dataset in payload["datasets"]:
        best = dataset["model_results"][0]
        print(
            dataset["dataset_tag"],
            f"best_model={best['model']}",
            f"delta={best['net_delta_dollars']:.2f}",
            f"kept={best['kept_trades']}",
            f"base={best['baseline_trades']}",
        )


if __name__ == "__main__":
    main()
