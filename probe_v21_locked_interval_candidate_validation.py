"""Validate frozen non-pure interval candidates on v21 passive websocket data.

This is an independent validation pass over the native passive ticker recorder
in `research_data/live_mushroom_v21_size2`. It does not discover thresholds,
train new models, submit orders, touch bot state, or modify live bot code.

The purpose is to test whether the frozen simple/staged/logit interval locks
survive a different live websocket capture at the user's volume unit:
recurring BTC 15-minute markets.
"""
from __future__ import annotations

import json
import math
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_interval_online_logit import Candidate as LogitCandidate
from probe_interval_online_logit import predict_frame, select_markets as select_logit_markets
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_live_heartbeat_physics_priors import attach_physics
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    Policy,
    add_scores,
    choose_decision_sides,
    clean_json,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_staged_interval_policy import StageSpec, select_staged
from probe_v21_native_passive_interval_validation import (
    infer_outcomes,
    load_watch_markets,
    quote_rows_for_ticker,
)


CANDIDATE_LOCK_PATH = OUT_DIR / "locked_interval_candidates.json"
LOGIT_LOCK_PATH = OUT_DIR / "locked_interval_logit_model.json"
LOGIT_MODEL_PATH = OUT_DIR / "locked_interval_logit_model.pkl"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def load_candidate_lock() -> List[Dict[str, Any]]:
    if not CANDIDATE_LOCK_PATH.exists():
        return []
    data = json.loads(CANDIDATE_LOCK_PATH.read_text(encoding="utf-8"))
    out: List[Dict[str, Any]] = []
    for item in data.get("candidates", []):
        kind = str(item.get("kind") or "")
        if kind == "simple":
            policy = item.get("policy") or {}
            out.append(
                {
                    "kind": "simple",
                    "name": str(item.get("name")),
                    "source_lock": str(CANDIDATE_LOCK_PATH),
                    "policy": Policy(
                        chooser=str(policy["chooser"]),
                        min_score=float(policy["min_score"]),
                        ask_max=float(policy["ask_max"]),
                        min_seconds_to_close=float(policy["min_seconds_to_close"]),
                        gate=str(policy.get("gate") or "none"),
                    ),
                }
            )
        elif kind == "staged":
            stage1 = item.get("stage1") or {}
            fallback = item.get("fallback") or {}
            out.append(
                {
                    "kind": "staged",
                    "name": str(item.get("name")),
                    "source_lock": str(CANDIDATE_LOCK_PATH),
                    "stage1": stage_spec(stage1),
                    "fallback": stage_spec(fallback),
                }
            )
    return out


def stage_spec(data: Dict[str, Any]) -> StageSpec:
    return StageSpec(
        name=str(data["name"]),
        chooser=str(data["chooser"]),
        min_score=float(data["min_score"]),
        ask_max=float(data["ask_max"]),
        min_seconds_to_close=float(data["min_seconds_to_close"]),
        max_seconds_to_close=(
            None if data.get("max_seconds_to_close") is None else float(data.get("max_seconds_to_close"))
        ),
        gate=str(data.get("gate") or "none"),
    )


def load_logit_lock() -> Optional[Dict[str, Any]]:
    if not LOGIT_LOCK_PATH.exists() or not LOGIT_MODEL_PATH.exists():
        return None
    lock = json.loads(LOGIT_LOCK_PATH.read_text(encoding="utf-8"))
    with LOGIT_MODEL_PATH.open("rb") as handle:
        model = pickle.load(handle)
    candidate = lock.get("candidate") or {}
    features = [str(feature) for feature in lock.get("features", [])]
    return {
        "kind": "logit",
        "name": str(candidate.get("name") or "locked_interval_logit"),
        "source_lock": str(LOGIT_LOCK_PATH),
        "model": model,
        "features": features,
        "candidate": LogitCandidate(
            feature_set=str(candidate["feature_set"]),
            c_value=float(candidate["c_value"]),
            prob_threshold=float(candidate["prob_threshold"]),
            ask_cap=float(candidate["ask_cap"]),
            min_seconds=float(candidate["min_seconds"]),
        ),
        "lock": lock,
    }


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    stake = float(selected_part["ask_cents"].sum()) if n else 0.0
    pnl = (
        float(((100.0 - selected_part["ask_cents"]) * selected_part["win"] - selected_part["ask_cents"] * (~selected_part["win"])).sum())
        if n
        else 0.0
    )
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
        "gross_pnl_cents": pnl,
        "stake_cents": stake,
        "gross_roi": pnl / stake if stake else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


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


def prepare_rows() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    markets = load_watch_markets()
    outcomes = infer_outcomes(markets)
    raw = quote_rows_for_ticker(markets, outcomes)
    physics, candle_info = attach_physics(raw, fetch_btc_candles=False)
    side_rows = add_scores(physics)
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    diagnostics = {
        "watch_markets": int(len(markets)),
        "outcome_markets": int(len(outcomes)),
        "raw_side_rows": int(len(raw)),
        "physics_side_rows": int(len(side_rows)),
        "resolved_intervals": int(len(base)),
        "candle_info": candle_info,
    }
    return base, side_rows, diagnostics


def select_simple(side_rows: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    chosen = choose_decision_sides(side_rows, policy.chooser)
    return select_markets_from_chosen(chosen, policy)


def select_staged_candidate(side_rows: pd.DataFrame, stage1: StageSpec, fallback: StageSpec) -> pd.DataFrame:
    choosers = sorted({stage1.chooser, fallback.chooser})
    chosen_cache = {chooser: choose_decision_sides(side_rows, chooser) for chooser in choosers}
    return select_staged(chosen_cache, stage1, fallback)


def summarize(name: str, kind: str, source_lock: str, selected: pd.DataFrame, metrics: Dict[str, Dict[str, Any]], spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": name,
        "kind": kind,
        "source_lock": source_lock,
        "spec": spec,
        "metrics": metrics,
        "target_pass": target_pass(metrics),
        "wilson_pass": wilson_pass(metrics),
    }


def evaluate(base: pd.DataFrame, side_rows: pd.DataFrame) -> tuple[List[Dict[str, Any]], pd.DataFrame]:
    summaries: List[Dict[str, Any]] = []
    selected_frames: List[pd.DataFrame] = []

    for item in load_candidate_lock():
        if item["kind"] == "simple":
            policy = item["policy"]
            selected = select_simple(side_rows, policy).copy()
            spec = {
                "label": policy.label,
                "chooser": policy.chooser,
                "min_score": policy.min_score,
                "ask_max": policy.ask_max,
                "min_seconds_to_close": policy.min_seconds_to_close,
                "gate": policy.gate,
            }
        else:
            selected = select_staged_candidate(side_rows, item["stage1"], item["fallback"]).copy()
            spec = {"stage1": item["stage1"].label, "fallback": item["fallback"].label}
        selected["candidate"] = item["name"]
        selected["candidate_kind"] = item["kind"]
        selected_frames.append(selected)
        metrics = metrics_for(base, selected)
        summaries.append(summarize(item["name"], item["kind"], item["source_lock"], selected, metrics, spec))

    logit = load_logit_lock()
    if logit is not None:
        scored = predict_frame(logit["model"], side_rows, logit["features"])
        selected = select_logit_markets(scored, logit["candidate"]).copy()
        selected["candidate"] = logit["name"]
        selected["candidate_kind"] = "logit"
        selected_frames.append(selected)
        metrics = metrics_for(base, selected)
        summaries.append(
            summarize(
                logit["name"],
                "logit",
                logit["source_lock"],
                selected,
                metrics,
                {
                    "label": logit["candidate"].label,
                    "features": logit["features"],
                    "training": (logit["lock"].get("training") or {}),
                },
            )
        )

    selected_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    summaries.sort(
        key=lambda row: (
            int(row["wilson_pass"]),
            int(row["target_pass"]),
            row["metrics"]["all"]["accuracy"] or 0.0,
            row["metrics"]["all"]["coverage"] or 0.0,
            -(row["metrics"]["all"]["median_ask"] or 100.0),
        ),
        reverse=True,
    )
    return summaries, selected_all


def write_report(path: Path, generated: str, diagnostics: Dict[str, Any], summaries: List[Dict[str, Any]]) -> None:
    lines: List[str] = [
        "# V21 Locked Interval Candidate Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Source dataset: `research_data/live_mushroom_v21_size2` native passive ticker websocket stream.",
        "- Outcomes are inferred from cached Coinbase BTC 1m close at market expiry versus recorded strike.",
        "- Candidate policies are loaded from frozen simple/staged/logit locks; no threshold search is performed.",
        "- Volume denominator is recurring BTC 15-minute markets.",
        "",
        "## Data",
        "",
        f"- Watch markets parsed: {diagnostics['watch_markets']}",
        f"- Markets with inferred outcomes: {diagnostics['outcome_markets']}",
        f"- Minute decision rows before physics: {diagnostics['raw_side_rows']}",
        f"- Minute decision rows after candle physics: {diagnostics['physics_side_rows']}",
        f"- Resolved interval denominator: {diagnostics['resolved_intervals']}",
        "",
        "## Frozen Candidate Validation",
        "",
        "| candidate | kind | target | Wilson | all acc | all cov | all Wilson low | holdout acc | holdout cov | median ask | ask=100 | ROI |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        all_m = summary["metrics"]["all"]
        holdout = summary["metrics"]["holdout"]
        lines.append(
            f"| `{summary['name']}` | {summary['kind']} | {summary['target_pass']} | {summary['wilson_pass']} | "
            f"{pct(all_m['accuracy'])} | {pct(all_m['coverage'])} | {pct(all_m['wilson95_lower'])} | "
            f"{pct(holdout['accuracy'])} | {pct(holdout['coverage'])} | {fmt(all_m['median_ask'])} | "
            f"{all_m['ask_eq_100']} | {pct(all_m['gross_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if not summaries:
        lines.append("No frozen non-pure interval candidates were available to validate.")
    elif any(summary["wilson_pass"] for summary in summaries):
        lines.append("At least one frozen candidate passes the 95% / 80% interval target with Wilson-robust split evidence on this independent live websocket dataset.")
    elif any(summary["target_pass"] for summary in summaries):
        lines.append("At least one frozen candidate passes the literal split target on this independent live websocket dataset, but not the Wilson-robust proof.")
    else:
        lines.append("No frozen simple/staged/logit candidate clears the 95% / 80% split target on this independent live websocket dataset.")
    if any((summary["metrics"]["all"]["median_ask"] or 0.0) >= 95.0 for summary in summaries):
        lines.append("The high-price degeneracy warning remains visible on at least one candidate.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    base, side_rows, diagnostics = prepare_rows()
    summaries, selected = evaluate(base, side_rows)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_latest = OUT_DIR / "v21_locked_interval_candidate_validation_latest.md"
    md_stamp = OUT_DIR / f"v21_locked_interval_candidate_validation_{generated}.md"
    json_latest = OUT_DIR / "v21_locked_interval_candidate_validation_latest.json"
    json_stamp = OUT_DIR / f"v21_locked_interval_candidate_validation_{generated}.json"
    selected_latest = OUT_DIR / "v21_locked_interval_candidate_validation_selected_latest.csv"
    selected_stamp = OUT_DIR / f"v21_locked_interval_candidate_validation_selected_{generated}.csv"
    ledger_latest = OUT_DIR / "v21_locked_interval_candidate_validation_ledger_latest.csv"
    ledger_stamp = OUT_DIR / f"v21_locked_interval_candidate_validation_ledger_{generated}.csv"

    selected.to_csv(selected_latest, index=False)
    selected.to_csv(selected_stamp, index=False)
    side_rows.to_csv(ledger_latest, index=False)
    side_rows.to_csv(ledger_stamp, index=False)
    write_report(md_latest, generated, diagnostics, summaries)
    write_report(md_stamp, generated, diagnostics, summaries)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "summaries": summaries}
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("V21 locked interval candidate validation complete")
    print(f"resolved_intervals={len(base)} candidates={len(summaries)} selected_rows={len(selected)}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
