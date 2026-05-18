"""Research-only locked pure-physics interval monitor.

Freezes the best pure-physics BTC 15m interval candidates found by
probe_interval_pure_physics_ablation.py and evaluates them on later resolved
markets without re-selecting thresholds.

The candidates use spot/strike, realized-volatility, drift, adverse-move, and
spread features. Book probability is not used as a chooser or model feature;
ask is retained only as an execution price cap/diagnostic.

This script reads live-derived heartbeat artifacts and writes only under
logs/edge_research. It does not submit orders, import the live bot, or modify
running bot logic.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_interval_pure_physics_ablation import (
    PhysicsPolicy,
    add_pure_physics_scores,
    choose_decision_sides,
    select_markets,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


LOCK_PATH = OUT_DIR / "locked_interval_pure_physics.json"
SHARED_LOCK_PATH = OUT_DIR / "locked_interval_candidates.json"


DEFAULT_CANDIDATES = [
    {
        "name": "pure_brownian_rv30_adverse15_high_price_20260502_1522",
        "policy": PhysicsPolicy(
            chooser="brownian_p_rv_30m",
            min_score=0.95,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            gate="adverse15<=10",
        ),
        "reason": "Top raw pure-physics 95/80 interval pass from ablation.",
    },
    {
        "name": "pure_physics_mean_rv15_rv30_high_price_20260502_1522",
        "policy": PhysicsPolicy(
            chooser="score_physics_mean_rv15_rv30",
            min_score=0.95,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            gate="none",
        ),
        "reason": "Best raw score-blend pure-physics pass from ablation.",
    },
    {
        "name": "pure_brownian_rv15_spread4_best_high_coverage_20260502_1522",
        "policy": PhysicsPolicy(
            chooser="brownian_p_rv_15m",
            min_score=0.90,
            ask_max=100.0,
            min_seconds_to_close=0.0,
            gate="spread<=4",
        ),
        "reason": "Best high-coverage physics-only row below the raw target gate.",
    },
    {
        "name": "pure_brownian_rv30_economical_adverse15_20260502_1522",
        "policy": PhysicsPolicy(
            chooser="brownian_p_rv_30m",
            min_score=0.75,
            ask_max=95.0,
            min_seconds_to_close=60.0,
            gate="adverse15<=10",
        ),
        "reason": "Best ask<=95/sec>=60 high-coverage physics-only diagnostic.",
    },
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def policy_dict(policy: PhysicsPolicy) -> Dict[str, Any]:
    return {
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "label": policy.label,
    }


def policy_from_dict(data: Dict[str, Any]) -> PhysicsPolicy:
    return PhysicsPolicy(
        chooser=str(data["chooser"]),
        min_score=float(data["min_score"]),
        ask_max=float(data["ask_max"]),
        min_seconds_to_close=float(data["min_seconds_to_close"]),
        gate=str(data.get("gate") or "none"),
    )


def inherited_lock_close_dt(base: pd.DataFrame) -> Optional[str]:
    if SHARED_LOCK_PATH.exists():
        try:
            data = json.loads(SHARED_LOCK_PATH.read_text(encoding="utf-8"))
            lock_close = data.get("lock_close_dt")
            if lock_close:
                return str(lock_close)
        except json.JSONDecodeError:
            pass
    if base.empty:
        return None
    return pd.to_datetime(base["close_dt"], utc=True, errors="coerce").max().isoformat()


def ensure_lock(base: pd.DataFrame) -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "locked_interval_pure_physics_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": inherited_lock_close_dt(base),
        "source_ablation": "logs/edge_research/interval_pure_physics_ablation_latest.md",
        "candidates": [
            {
                "name": item["name"],
                "reason": item["reason"],
                "policy": policy_dict(item["policy"]),
            }
            for item in DEFAULT_CANDIDATES
        ],
    }
    LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


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
        "gross_pnl_cents": float(
            (selected_part["win"].astype(float) * (100.0 - selected_part["ask_cents"])
             - (~selected_part["win"]).astype(float) * selected_part["ask_cents"]).sum()
        )
        if n
        else 0.0,
    }


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def write_report(path: Path, generated: str, lock: Dict[str, Any], summaries: List[Dict[str, Any]]) -> None:
    lines: List[str] = [
        "# Locked Pure-Physics Interval Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only monitor; no orders are submitted and no bot files are modified.",
        "- Candidate definitions are frozen in `logs/edge_research/locked_interval_pure_physics.json`.",
        "- Side choice uses pure physics features; book probability is not used as a chooser or model feature.",
        "- Ask is used only as an execution cap and degeneracy diagnostic.",
        "- Fresh rows are markets with close time after the lock close time.",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        "",
        "## Candidate Results",
        "",
        "| candidate | target | Wilson | all acc | all cov | all Wilson low | all median ask | fresh markets | fresh acc | fresh cov | fresh median ask | fresh ask=100 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        all_m = summary["metrics"]["all"]
        fresh = summary["metrics"]["fresh"]
        lines.append(
            f"| `{summary['name']}` | {summary['target_pass']} | {summary['wilson_pass']} | "
            f"{pct(all_m['accuracy'])} | {pct(all_m['coverage'])} | {pct(all_m['wilson95_lower'])} | "
            f"{fmt(all_m['median_ask'])} | {fresh['markets']}/{fresh['base_markets']} | "
            f"{pct(fresh['accuracy'])} | {pct(fresh['coverage'])} | {fmt(fresh['median_ask'])} | {fresh['ask_eq_100']} |"
        )
    lines += ["", "## Read", ""]
    fresh_base = max((summary["metrics"]["fresh"]["base_markets"] for summary in summaries), default=0)
    lines.append(f"- Fresh resolved intervals available for locked pure-physics candidates: {fresh_base}")
    if fresh_base < 30:
        lines.append("- Fresh sample is far below the sample-size requirement; this is monitoring evidence only.")
    if any((summary["metrics"]["all"]["median_ask"] or 0.0) >= 95.0 for summary in summaries):
        lines.append("- The strongest physics-only passes still carry high-price degeneracy warnings.")
    if not any(summary["wilson_pass"] for summary in summaries):
        lines.append("- No locked pure-physics candidate has a Wilson-robust 95% accuracy proof across splits.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    side_rows = add_pure_physics_scores(load_side_rows())
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    lock = ensure_lock(base)
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")

    summaries: List[Dict[str, Any]] = []
    selected_frames: List[pd.DataFrame] = []
    for item in lock.get("candidates", []):
        policy = policy_from_dict(item["policy"])
        chosen = choose_decision_sides(side_rows, policy.chooser)
        selected = select_markets({policy.chooser: chosen}, policy).copy()
        selected["candidate"] = item["name"]
        selected_frames.append(selected)
        metrics = {split: metric(base, selected, split, lock_close_dt) for split in ["all", "train", "validation", "holdout", "fresh"]}
        summaries.append(
            {
                "name": item["name"],
                "reason": item.get("reason"),
                "policy": policy_dict(policy),
                "metrics": metrics,
                "target_pass": target_pass(metrics),
                "wilson_pass": wilson_pass(metrics),
            }
        )

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_latest = OUT_DIR / "locked_interval_pure_physics_selected_latest.csv"
    selected_stamp = OUT_DIR / f"locked_interval_pure_physics_selected_{generated}.csv"
    md_latest = OUT_DIR / "locked_interval_pure_physics_latest.md"
    md_stamp = OUT_DIR / f"locked_interval_pure_physics_{generated}.md"
    json_latest = OUT_DIR / "locked_interval_pure_physics_latest.json"
    json_stamp = OUT_DIR / f"locked_interval_pure_physics_{generated}.json"

    selected.to_csv(selected_latest, index=False)
    selected.to_csv(selected_stamp, index=False)
    write_report(md_latest, generated, lock, summaries)
    write_report(md_stamp, generated, lock, summaries)
    payload = {"generated_utc": generated, "lock": lock, "summaries": summaries}
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Locked pure-physics interval monitor complete")
    print(f"resolved_markets={len(base)} candidates={len(summaries)}")
    print(f"lock_close_dt={lock.get('lock_close_dt')}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
