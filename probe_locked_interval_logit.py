"""Research-only frozen logistic interval candidate monitor.

This freezes the strongest chronological logistic interval candidate and then
monitors it on future resolved BTC 15-minute markets. The point is to avoid
quietly re-training or re-selecting thresholds after new intervals resolve.

The script writes only under logs/edge_research and does not import or modify
the live bot.
"""
from __future__ import annotations

import json
import math
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_interval_online_logit import build_model, predict_frame, select_markets
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct


MODEL_PATH = OUT_DIR / "locked_interval_logit_model.pkl"
LOCK_PATH = OUT_DIR / "locked_interval_logit_model.json"

FEATURES = [
    "book_p_side",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "drift_p_5m_rv_15m",
    "drift_p_15m_rv_15m",
    "margin_per_rv_sigma_15m",
    "margin_per_rv_sigma_30m",
    "abs_book_rv15_gap",
    "abs_book_rv30_gap",
    "adverse_move_3m",
    "adverse_move_5m",
    "adverse_move_15m",
    "spread_cents",
    "seconds_to_close",
]

CANDIDATE = {
    "name": "locked_logit_book_physics_c005_p095_20260502_1512",
    "feature_set": "book_physics",
    "c_value": 0.05,
    "prob_threshold": 0.95,
    "ask_cap": 100.0,
    "min_seconds": 0.0,
    "label": "book_physics; C=0.05; p>=0.95; ask<=100; sec>=0",
}


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def candidate_object():
    from probe_interval_online_logit import Candidate

    return Candidate(
        feature_set=CANDIDATE["feature_set"],
        c_value=CANDIDATE["c_value"],
        prob_threshold=CANDIDATE["prob_threshold"],
        ask_cap=CANDIDATE["ask_cap"],
        min_seconds=CANDIDATE["min_seconds"],
    )


def prepare_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    side_rows = load_side_rows()
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return base, side_rows


def train_and_lock(base: pd.DataFrame, side_rows: pd.DataFrame) -> Dict[str, Any]:
    train_rows = side_rows[side_rows["split"] == "train"].copy()
    if train_rows["win"].nunique() < 2:
        raise SystemExit("Training split does not contain both classes")
    for feature in FEATURES:
        if feature not in train_rows.columns:
            train_rows[feature] = np.nan
    model = build_model(CANDIDATE["c_value"])
    model.fit(train_rows[FEATURES], train_rows["win"].astype(int))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as fh:
        pickle.dump(model, fh)
    lock = {
        "lock_id": "locked_interval_logit_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": base["close_dt"].max().isoformat() if not base.empty else None,
        "model_path": str(MODEL_PATH),
        "candidate": CANDIDATE,
        "features": FEATURES,
        "training": {
            "train_markets": int(train_rows["market"].nunique()),
            "train_side_rows": int(len(train_rows)),
            "train_start": train_rows["entry_dt"].min().isoformat() if not train_rows.empty else None,
            "train_end": train_rows["entry_dt"].max().isoformat() if not train_rows.empty else None,
        },
    }
    LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


def load_or_train(base: pd.DataFrame, side_rows: pd.DataFrame):
    if LOCK_PATH.exists() and MODEL_PATH.exists():
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        with MODEL_PATH.open("rb") as fh:
            model = pickle.load(fh)
        return lock, model
    lock = train_and_lock(base, side_rows)
    with MODEL_PATH.open("rb") as fh:
        model = pickle.load(fh)
    return lock, model


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str, lock_close_dt: Optional[pd.Timestamp]) -> Dict[str, Any]:
    if split == "all":
        base_part = base
        selected_part = selected
    elif split == "fresh":
        if lock_close_dt is None or pd.isna(lock_close_dt):
            base_part = base.iloc[0:0]
            selected_part = selected.iloc[0:0]
        else:
            base_part = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt]
            selected_part = selected[pd.to_datetime(selected["close_dt"], utc=True, errors="coerce") > lock_close_dt]
    else:
        base_part = base[base["split"] == split]
        selected_part = selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
    }


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def write_report(path: Path, generated: str, lock: Dict[str, Any], metrics: Dict[str, Dict[str, Any]]) -> None:
    all_m = metrics["all"]
    fresh = metrics["fresh"]
    lines: List[str] = []
    lines.append("# Locked Interval Logistic Monitor")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only monitor; no orders are submitted and no bot files are modified.")
    lines.append("- The logistic model is serialized once and loaded on later runs.")
    lines.append("- Fresh rows are markets with close time after the model lock close time.")
    lines.append(f"- Lock close time: `{lock.get('lock_close_dt')}`")
    lines.append(f"- Candidate: `{CANDIDATE['label']}`")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| split | acc | coverage | Wilson low | markets | median ask | ask>=95 | ask=100 | median sec |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for split in ["all", "train", "validation", "holdout", "fresh"]:
        metric_row = metrics[split]
        lines.append(
            f"| {split} | {pct(metric_row['accuracy'])} | {pct(metric_row['coverage'])} | "
            f"{pct(metric_row['wilson95_lower'])} | {metric_row['markets']}/{metric_row['base_markets']} | "
            f"{fmt(metric_row['median_ask'])} | {metric_row['ask_ge_95']} | {metric_row['ask_eq_100']} | "
            f"{fmt(metric_row['median_seconds_to_close'])} |"
        )
    lines.append("")
    lines.append("## Read")
    lines.append("")
    if fresh["base_markets"] < 30:
        lines.append("- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.")
    if fresh["base_markets"] == 0:
        lines.append("- No post-lock resolved intervals are available yet.")
    elif (fresh["coverage"] or 0.0) < 0.80:
        lines.append("- Fresh interval coverage is currently below the 80% target.")
    if (all_m["median_ask"] or 0.0) >= 95.0:
        lines.append("- All-sample median ask remains high, so degeneracy remains unresolved.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    base, side_rows = prepare_rows()
    lock, model = load_or_train(base, side_rows)
    scored = predict_frame(model, side_rows, FEATURES)
    selected = select_markets(scored, candidate_object())
    selected = selected.copy()
    selected["candidate"] = CANDIDATE["name"]
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
    metrics = {split: metric(base, selected, split, lock_close_dt) for split in ["all", "train", "validation", "holdout", "fresh"]}
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    selected_latest = OUT_DIR / "locked_interval_logit_selected_latest.csv"
    selected_stamp = OUT_DIR / f"locked_interval_logit_selected_{generated}.csv"
    md_latest = OUT_DIR / "locked_interval_logit_latest.md"
    md_stamp = OUT_DIR / f"locked_interval_logit_{generated}.md"
    json_latest = OUT_DIR / "locked_interval_logit_latest.json"
    json_stamp = OUT_DIR / f"locked_interval_logit_{generated}.json"

    selected.to_csv(selected_latest, index=False)
    selected.to_csv(selected_stamp, index=False)
    write_report(md_latest, generated, lock, metrics)
    write_report(md_stamp, generated, lock, metrics)
    payload = {"generated_utc": generated, "lock": lock, "metrics": metrics, "selected_markets": int(len(selected))}
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Locked interval logistic monitor complete")
    print(f"resolved_markets={len(base)} selected={len(selected)}")
    print(f"lock_close_dt={lock.get('lock_close_dt')}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
