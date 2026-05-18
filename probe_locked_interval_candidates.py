"""Research-only locked interval candidate monitor.

Freezes a small set of candidate interval policies and evaluates them on future
resolved BTC 15-minute markets without re-selecting thresholds. This is meant to
separate "found on the existing tape" from genuine post-lock live validation.

The script reads the live-derived two-sided heartbeat ledger and writes only
under logs/edge_research. It does not import or modify the live bot.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import (
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_staged_interval_policy import StageSpec, select_staged


LOCK_PATH = OUT_DIR / "locked_interval_candidates.json"

SIMPLE_CANDIDATES = [
    {
        "name": "raw_regime_blend_high_price_20260502_1510",
        "kind": "simple",
        "policy": Policy(
            chooser="score_regime_blend",
            min_score=0.95,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            gate="none",
        ),
    },
    {
        "name": "raw_score_min_book_rv15_existing_lock",
        "kind": "simple",
        "policy": Policy(
            chooser="score_min_book_rv15",
            min_score=0.90,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            gate="none",
        ),
    },
    {
        "name": "economical_score_min_book_rv15_20260502_1511",
        "kind": "simple",
        "policy": Policy(
            chooser="score_min_book_rv15",
            min_score=0.80,
            ask_max=95.0,
            min_seconds_to_close=60.0,
            gate="none",
        ),
    },
]

STAGED_CANDIDATES = [
    {
        "name": "staged_score_min_fallback_20260502_1511",
        "kind": "staged",
        "stage1": StageSpec(
            name="economical",
            chooser="score_min_book_rv15",
            min_score=0.90,
            ask_max=90.0,
            min_seconds_to_close=60.0,
            max_seconds_to_close=None,
            gate="none",
        ),
        "fallback": StageSpec(
            name="fallback",
            chooser="score_min_book_rv15",
            min_score=0.90,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            max_seconds_to_close=300.0,
            gate="none",
        ),
    }
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def ensure_lock(base: pd.DataFrame) -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "locked_interval_candidates_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": base["close_dt"].max().isoformat() if not base.empty else None,
        "candidates": [
            {
                "name": candidate["name"],
                "kind": "simple",
                "policy": {
                    "chooser": candidate["policy"].chooser,
                    "min_score": candidate["policy"].min_score,
                    "ask_max": candidate["policy"].ask_max,
                    "min_seconds_to_close": candidate["policy"].min_seconds_to_close,
                    "gate": candidate["policy"].gate,
                    "label": candidate["policy"].label,
                },
            }
            for candidate in SIMPLE_CANDIDATES
        ]
        + [
            {
                "name": candidate["name"],
                "kind": "staged",
                "stage1": stage_dict(candidate["stage1"]),
                "fallback": stage_dict(candidate["fallback"]),
            }
            for candidate in STAGED_CANDIDATES
        ],
    }
    LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


def stage_dict(stage: StageSpec) -> Dict[str, Any]:
    return {
        "name": stage.name,
        "chooser": stage.chooser,
        "min_score": stage.min_score,
        "ask_max": stage.ask_max,
        "min_seconds_to_close": stage.min_seconds_to_close,
        "max_seconds_to_close": stage.max_seconds_to_close,
        "gate": stage.gate,
        "label": stage.label,
    }


def metric(base: pd.DataFrame, selected: pd.DataFrame, label: str, lock_close_dt: Optional[pd.Timestamp]) -> Dict[str, Any]:
    if label == "fresh":
        if lock_close_dt is None or pd.isna(lock_close_dt):
            base_part = base.iloc[0:0]
            selected_part = selected.iloc[0:0]
        else:
            base_part = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt]
            selected_part = selected[pd.to_datetime(selected["close_dt"], utc=True, errors="coerce") > lock_close_dt]
    elif label == "all":
        base_part = base
        selected_part = selected
    else:
        base_part = base[base["split"] == label]
        selected_part = selected[selected["split"] == label]

    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    losses = n - wins
    total = int(len(base_part))
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": losses,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
    }


def evaluate_simple(candidate: Dict[str, Any], side_rows: pd.DataFrame) -> pd.DataFrame:
    policy = candidate["policy"]
    chosen = choose_decision_sides(side_rows, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy)
    selected = selected.copy()
    selected["candidate"] = candidate["name"]
    return selected


def evaluate_staged(candidate: Dict[str, Any], side_rows: pd.DataFrame) -> pd.DataFrame:
    choosers = {candidate["stage1"].chooser, candidate["fallback"].chooser}
    chosen_cache = {chooser: choose_decision_sides(side_rows, chooser) for chooser in choosers}
    selected = select_staged(chosen_cache, candidate["stage1"], candidate["fallback"])
    selected = selected.copy()
    selected["candidate"] = candidate["name"]
    return selected


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def write_report(path: Path, generated: str, lock: Dict[str, Any], summaries: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Locked Interval Candidate Monitor")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only monitor; no orders are submitted and no bot files are modified.")
    lines.append("- Candidate definitions are frozen in `logs/edge_research/locked_interval_candidates.json`.")
    lines.append("- Fresh rows are markets with close time after the lock close time.")
    lines.append(f"- Lock close time: `{lock.get('lock_close_dt')}`")
    lines.append("")
    lines.append("## Candidate Results")
    lines.append("")
    lines.append("| candidate | all acc | all cov | all median ask | fresh markets | fresh acc | fresh cov | fresh median ask | fresh ask=100 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for summary in summaries:
        all_m = summary["metrics"]["all"]
        fresh = summary["metrics"]["fresh"]
        lines.append(
            f"| `{summary['name']}` | {pct(all_m['accuracy'])} | {pct(all_m['coverage'])} | "
            f"{fmt(all_m['median_ask'])} | {fresh['markets']}/{fresh['base_markets']} | "
            f"{pct(fresh['accuracy'])} | {pct(fresh['coverage'])} | {fmt(fresh['median_ask'])} | {fresh['ask_eq_100']} |"
        )
    lines.append("")
    lines.append("## Read")
    lines.append("")
    fresh_base = max((summary["metrics"]["fresh"]["base_markets"] for summary in summaries), default=0)
    lines.append(f"- Fresh resolved intervals available for locked candidates: {fresh_base}")
    if fresh_base < 30:
        lines.append("- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.")
    if fresh_base > 0 and any((summary["metrics"]["fresh"]["coverage"] or 0.0) < 0.80 for summary in summaries):
        lines.append("- At least one locked candidate currently fails the fresh 80% interval-coverage gate.")
    lines.append("- High fresh ask/100c counts remain degeneracy warnings, not promotion evidence.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    side_rows = load_side_rows()
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    lock = ensure_lock(base)
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")

    summaries: List[Dict[str, Any]] = []
    selected_frames: List[pd.DataFrame] = []
    for candidate in SIMPLE_CANDIDATES:
        selected = evaluate_simple(candidate, side_rows)
        selected_frames.append(selected)
        summaries.append(
            {
                "name": candidate["name"],
                "kind": candidate["kind"],
                "label": candidate["policy"].label,
                "metrics": {split: metric(base, selected, split, lock_close_dt) for split in ["all", "train", "validation", "holdout", "fresh"]},
            }
        )
    for candidate in STAGED_CANDIDATES:
        selected = evaluate_staged(candidate, side_rows)
        selected_frames.append(selected)
        summaries.append(
            {
                "name": candidate["name"],
                "kind": candidate["kind"],
                "stage1": candidate["stage1"].label,
                "fallback": candidate["fallback"].label,
                "metrics": {split: metric(base, selected, split, lock_close_dt) for split in ["all", "train", "validation", "holdout", "fresh"]},
            }
        )

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_latest = OUT_DIR / "locked_interval_candidates_selected_latest.csv"
    selected_stamp = OUT_DIR / f"locked_interval_candidates_selected_{generated}.csv"
    md_latest = OUT_DIR / "locked_interval_candidates_latest.md"
    md_stamp = OUT_DIR / f"locked_interval_candidates_{generated}.md"
    json_latest = OUT_DIR / "locked_interval_candidates_latest.json"
    json_stamp = OUT_DIR / f"locked_interval_candidates_{generated}.json"

    selected.to_csv(selected_latest, index=False)
    selected.to_csv(selected_stamp, index=False)
    write_report(md_latest, generated, lock, summaries)
    write_report(md_stamp, generated, lock, summaries)
    payload = {"generated_utc": generated, "lock": lock, "summaries": summaries}
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Locked interval candidate monitor complete")
    print(f"resolved_markets={len(base)} candidates={len(summaries)}")
    print(f"lock_close_dt={lock.get('lock_close_dt')}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
