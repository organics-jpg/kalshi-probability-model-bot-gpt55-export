"""Research-only physics scan on live v28 websocket opportunities.

This probe reads v28-approved `signal_seen` events from the live execution
ledger, dedupes them into opportunity sets, labels resolved markets from the
bot log, and evaluates the same physics-prior rule family used by the fill
validator.

It is deliberately separate from the running bot: no orders, process signals,
or bot files are touched.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_live_v28_fv_accuracy_volume import (
    BOT_LOG,
    EXECUTION_LOG,
    OUT_DIR,
    as_bool,
    as_float,
    as_int,
    first_present,
    iter_json_lines,
    parse_bot_log,
)
from probe_physics_priors_boundary_models import (
    MIN_TARGET_ACCURACY,
    add_candle_physics,
    clean_json,
    evaluate_dataset,
    make_rules,
    oracle_bound,
    write_candidates_csv,
)
from shadow_live_v28_physics_validator import (
    closed_market_outcomes_only,
    ensure_candles_for_entries,
    mark_fresh_after_lock,
    shadow_physics_features,
)


LOCK_PATH = OUT_DIR / "live_v28_websocket_opportunity_shadow_lock.json"
PRIMARY_MODE = "first_per_market"
FIXED_RULE_LABEL = "ask<=100; block 15m adverse>10 unless v28 cushion>0.5"
ORACLE_RETENTION_FLOORS = [0.75, 0.80]


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def iso_ts(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).isoformat()


def create_lock(raw: pd.DataFrame) -> Dict[str, Any]:
    line_no = pd.to_numeric(raw.get("source_line_no"), errors="coerce")
    max_line = int(line_no.max()) if line_no.notna().any() else None
    max_entry_dt = raw["entry_dt"].max() if "entry_dt" in raw.columns and not raw.empty else None
    lock = {
        "lock_id": "live_v28_websocket_opportunity_shadow_lock_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "execution_log": str(EXECUTION_LOG),
        "bot_log": str(BOT_LOG),
        "initial_max_source_line_no": max_line,
        "initial_max_entry_dt": iso_ts(max_entry_dt),
        "purpose": "Out-of-sample boundary for future current-v28 websocket opportunity validation.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


def load_or_create_lock(raw: pd.DataFrame) -> Dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return create_lock(raw)


def load_v28_signal_opportunities(outcomes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for event in iter_json_lines(EXECUTION_LOG):
        if event.get("event_type") != "signal_seen":
            continue
        if as_bool(event.get("mushroom_v28_approved")) is not True:
            continue

        side = str(event.get("mushroom_v28_side") or event.get("side") or "").lower()
        if side not in {"yes", "no"}:
            continue
        market = str(event.get("market") or "")
        entry_dt = pd.to_datetime(event.get("ts_wall"), utc=True, errors="coerce")
        if pd.isna(entry_dt):
            continue

        qty = (
            as_int(event.get("mushroom_v28_target_count"))
            or as_int(event.get("slice_target_size"))
            or as_int(event.get("position_size"))
            or 1
        )
        if qty <= 0:
            qty = 1

        outcome = outcomes.get(market, {}).get("outcome")
        rows.append(
            {
                "dataset": "current_v28_websocket_opportunities",
                "entry_key": f"signal:{event.get('_line_no')}",
                "entry_dt": entry_dt,
                "market": market,
                "side": side,
                "outcome": outcome,
                "outcome_available": outcome in {"yes", "no"},
                "win": bool(side == outcome) if outcome in {"yes", "no"} else None,
                "qty": int(qty),
                "ask_cents": as_float(
                    first_present(
                        event,
                        "mushroom_v28_ask_cents",
                        "trigger_price_cents",
                        "top_of_book_limit_cents",
                        "cap_price_cents",
                    )
                ),
                "spot": as_float(event.get("mushroom_v28_btc_price")),
                "strike": as_float(event.get("mushroom_v28_strike")),
                "seconds_to_close": as_float(event.get("mushroom_v28_seconds_to_close")),
                "v28_sigma_t_dollars": as_float(event.get("mushroom_v28_sigma_t_dollars")),
                "v28_p_side": as_float(event.get("mushroom_v28_p_side")),
                "v28_edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
                "v28_model_max_buy_price_cents": as_float(event.get("mushroom_v28_model_max_buy_price_cents")),
                "v28_depth_count": as_float(event.get("mushroom_v28_depth_count")),
                "v28_balance_count": as_float(event.get("mushroom_v28_balance_count")),
                "v28_book_age_ms": as_float(event.get("mushroom_v28_book_age_ms")),
                "v28_btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
                "source_line_no": event.get("_line_no"),
                "outcome_method": outcomes.get(market, {}).get("method"),
                "outcome_source": outcomes.get(market, {}).get("source"),
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)


def dedupe_opportunities(raw: pd.DataFrame, mode: str) -> pd.DataFrame:
    if raw.empty:
        return raw.copy()
    ordered = raw.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)
    if mode == "all_signals":
        out = ordered.copy()
    elif mode == "first_per_market_side":
        out = ordered.groupby(["market", "side"], as_index=False, sort=False).first()
    elif mode == "first_per_market":
        out = ordered.groupby(["market"], as_index=False, sort=False).first()
    else:
        raise ValueError(f"unknown dedupe mode: {mode}")
    out = out.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)
    out["opportunity_mode"] = mode
    return out


def prepare_mode(raw: pd.DataFrame, mode: str, fetch_btc_candles: bool, lock: Dict[str, Any]) -> pd.DataFrame:
    deduped = dedupe_opportunities(raw, mode)
    if deduped.empty:
        return deduped
    candles = ensure_candles_for_entries(deduped, fetch_missing=fetch_btc_candles)
    features = shadow_physics_features(deduped)
    features = add_candle_physics(features, candles)
    features = mark_fresh_after_lock(features, lock)
    features["opportunity_mode"] = mode
    return features.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)


def baseline_line(evaluation: Dict[str, Any], split: str) -> str:
    metric = evaluation["baseline"][split]
    return (
        f"{metric['contract_wins']}/{metric['contracts']} contracts "
        f"({pct(metric['contract_accuracy'])}), "
        f"{metric['trade_wins']}/{metric['trades']} trades ({pct(metric['trade_accuracy'])})"
    )


def find_fixed_rule(evaluation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for result in evaluation["results"]:
        if result["label"] == FIXED_RULE_LABEL:
            return result
    return None


def fresh_counts(df: pd.DataFrame) -> Dict[str, Any]:
    fresh = df[df.get("fresh_after_lock", False)].copy() if "fresh_after_lock" in df.columns else df.iloc[0:0].copy()
    resolved = fresh[fresh["outcome_available"]].copy() if not fresh.empty else fresh
    return {
        "rows": int(len(fresh)),
        "resolved_rows": int(len(resolved)),
        "contracts": int(resolved["qty"].sum()) if not resolved.empty else 0,
    }


def oracle_bounds_for_evaluation(evaluation: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for split in ["all", "validation", "holdout"]:
        split_bounds: List[Dict[str, Any]] = []
        for floor in ORACLE_RETENTION_FLOORS:
            bound = oracle_bound(evaluation["baseline"][split], floor)
            bound["contract_target_possible"] = (bound["max_contract_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
            bound["trade_target_possible"] = (bound["max_trade_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
            split_bounds.append(bound)
        out[split] = split_bounds
    return out


def write_report(
    path: Path,
    generated: str,
    raw: pd.DataFrame,
    mode_frames: Dict[str, pd.DataFrame],
    evaluations: Dict[str, Any],
    lock: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Live v28 Websocket Opportunity Physics Scan")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append("- Source: v28-approved `signal_seen` rows from `logs/live_mushroom_v28_size2/execution_events.ndjson`.")
    lines.append("- Outcomes are inferred from resolved market quotes in `logs/live_mushroom_v28_size2/bot.log`.")
    lines.append("- Primary dedupe mode is first v28-approved opportunity per market; all-signal counts are sensitivity only.")
    lines.append(f"- Fresh evidence starts after source line `{lock.get('initial_max_source_line_no')}` / `{lock.get('created_utc')}`.")
    lines.append("")
    lines.append("## Raw Coverage")
    lines.append("")
    lines.append(f"- Raw v28-approved signal rows: {len(raw)}")
    lines.append(f"- Resolved raw signal rows: {int(raw['outcome_available'].sum()) if not raw.empty else 0}")
    lines.append(f"- Unique markets: {raw['market'].nunique() if not raw.empty else 0}")
    lines.append(f"- Unique market/side pairs: {raw[['market', 'side']].drop_duplicates().shape[0] if not raw.empty else 0}")
    lines.append("")
    lines.append("## Mode Results")
    lines.append("")
    for mode in ["first_per_market", "first_per_market_side", "all_signals"]:
        frame = mode_frames.get(mode, pd.DataFrame())
        evaluation = evaluations.get(mode)
        if frame.empty or not evaluation:
            continue
        fresh = fresh_counts(frame)
        lines.append(f"### `{mode}`")
        lines.append("")
        lines.append(f"- Rows after dedupe: {len(frame)}")
        lines.append(f"- Resolved rows: {int(frame['outcome_available'].sum())}")
        lines.append(f"- Contracts: {int(frame[frame['outcome_available']]['qty'].sum())}")
        lines.append(f"- Fresh rows after opportunity lock: {fresh['rows']} rows / {fresh['resolved_rows']} resolved / {fresh['contracts']} contracts")
        lines.append(f"- Baseline all: {baseline_line(evaluation, 'all')}")
        lines.append(f"- Baseline holdout: {baseline_line(evaluation, 'holdout')}")
        lines.append(f"- Physics target-pass rules: {evaluation['target_pass_count']}")
        lines.append("")
        lines.append("Perfect-selector oracle bounds:")
        lines.append("")
        lines.append("| split | retention floor | required contracts | max contract acc | required trades | max trade acc | 95% possible |")
        lines.append("|---|---:|---:|---:|---:|---:|---|")
        for split in ["all", "validation", "holdout"]:
            for bound in evaluation.get("oracle_bounds", {}).get(split, []):
                possible = bool(bound.get("contract_target_possible")) and bool(bound.get("trade_target_possible"))
                lines.append(
                    f"| {split} | {pct(bound['retention_floor'])} | {bound['required_contracts']} | "
                    f"{pct(bound['max_contract_accuracy'])} | {bound['required_trades']} | "
                    f"{pct(bound['max_trade_accuracy'])} | {possible} |"
                )
        lines.append("")
        fixed = find_fixed_rule(evaluation)
        if fixed:
            all_m = fixed["metrics"]["all"]
            hold_m = fixed["metrics"]["holdout"]
            lines.append("Fixed adverse-drift rule:")
            lines.append("")
            lines.append("| split | contracts | contract acc | contract ret | trades | trade acc |")
            lines.append("|---|---:|---:|---:|---:|---:|")
            for split in ["all", "validation", "holdout"]:
                metric = fixed["metrics"][split]
                lines.append(
                    f"| {split} | {metric['contract_wins']}/{metric['contracts']} | {pct(metric['contract_accuracy'])} | "
                    f"{pct(metric['contract_retention'])} | {metric['trade_wins']}/{metric['trades']} | {pct(metric['trade_accuracy'])} |"
                )
            lines.append("")
            lines.append(
                f"Fixed-rule read: all contracts {pct(all_m['contract_accuracy'])} at {pct(all_m['contract_retention'])} retention; "
                f"holdout contracts {pct(hold_m['contract_accuracy'])} at {pct(hold_m['contract_retention'])} retention."
            )
            lines.append("")
        lines.append("Top high-volume physics rules:")
        lines.append("")
        lines.append("| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts | target |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---|")
        high_volume = [
            result
            for result in evaluation["results"]
            if (result["metrics"]["all"]["contract_retention"] or 0.0) >= 0.75
        ][:10]
        for idx, result in enumerate(high_volume, start=1):
            all_m = result["metrics"]["all"]
            hold_m = result["metrics"]["holdout"]
            lines.append(
                f"| {idx} | {result['family']} | `{result['label']}` | {pct(all_m['contract_accuracy'])} | "
                f"{pct(all_m['contract_retention'])} | {pct(hold_m['contract_accuracy'])} | "
                f"{pct(hold_m['contract_retention'])} | {all_m['contracts']} | {result['target_pass']} |"
            )
        lines.append("")
    lines.append("## Completion Read")
    lines.append("")
    primary = evaluations.get(PRIMARY_MODE)
    if primary and primary["target_pass_count"] > 0:
        lines.append(
            "The primary opportunity tape has at least one exploratory physics rule that meets the configured "
            "95% accuracy and 75% retention gates on chronological all/validation/holdout splits."
        )
    else:
        lines.append(
            "The primary opportunity tape does not have a physics rule that clears the configured "
            "95% accuracy and 75% retention gates with sample floors."
        )
    lines.append(
        "This opportunity scan is not by itself completion evidence for the active goal: it is live websocket "
        "telemetry, but it is not the locked fresh fill sample. It is useful for questioning v28 priors while "
        "the live bot has no post-lock fills."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    raw = load_v28_signal_opportunities(outcomes)
    if raw.empty:
        raise SystemExit("No v28-approved signal_seen opportunities found.")

    lock = load_or_create_lock(raw)
    rules = make_rules()
    mode_frames: Dict[str, pd.DataFrame] = {}
    evaluations: Dict[str, Any] = {}
    for mode in ["first_per_market", "first_per_market_side", "all_signals"]:
        frame = prepare_mode(raw, mode, fetch_btc_candles=bool(args.fetch_btc_candles), lock=lock)
        mode_frames[mode] = frame
        resolved = frame[frame["outcome_available"]].copy()
        if not resolved.empty:
            evaluations[mode] = evaluate_dataset(resolved, rules)
            evaluations[mode]["oracle_bounds"] = oracle_bounds_for_evaluation(evaluations[mode])

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    json_latest = OUT_DIR / "live_v28_websocket_opportunity_physics_latest.json"
    json_stamp = OUT_DIR / f"live_v28_websocket_opportunity_physics_{generated}.json"
    md_latest = OUT_DIR / "live_v28_websocket_opportunity_physics_latest.md"
    md_stamp = OUT_DIR / f"live_v28_websocket_opportunity_physics_{generated}.md"
    candidates_latest = OUT_DIR / "live_v28_websocket_opportunity_physics_candidates_latest.csv"
    candidates_stamp = OUT_DIR / f"live_v28_websocket_opportunity_physics_candidates_{generated}.csv"
    ledger_latest = OUT_DIR / "live_v28_websocket_opportunity_physics_trades_latest.csv"
    ledger_stamp = OUT_DIR / f"live_v28_websocket_opportunity_physics_trades_{generated}.csv"

    combined = pd.concat([frame for frame in mode_frames.values() if not frame.empty], ignore_index=True)
    combined.to_csv(ledger_latest, index=False)
    combined.to_csv(ledger_stamp, index=False)
    write_candidates_csv(evaluations, candidates_latest)
    write_candidates_csv(evaluations, candidates_stamp)
    summary = {
        "generated_utc": generated,
        "lock": lock,
        "raw_rows": int(len(raw)),
        "raw_resolved_rows": int(raw["outcome_available"].sum()),
        "unique_markets": int(raw["market"].nunique()),
        "unique_market_sides": int(raw[["market", "side"]].drop_duplicates().shape[0]),
        "evaluations": evaluations,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")
    write_report(md_latest, generated, raw, mode_frames, evaluations, lock)
    write_report(md_stamp, generated, raw, mode_frames, evaluations, lock)

    primary = evaluations.get(PRIMARY_MODE, {})
    print("Live v28 websocket opportunity physics scan complete")
    print(
        f"raw_signals={len(raw)} resolved={int(raw['outcome_available'].sum())} "
        f"unique_markets={raw['market'].nunique()}"
    )
    if primary:
        base = primary["baseline"]["all"]
        print(
            f"primary={PRIMARY_MODE} rows={primary['row_count']} contracts={primary['contract_count']} "
            f"baseline={base['contract_wins']}/{base['contracts']} "
            f"target_pass={primary['target_pass_count']}"
        )
    print(f"report={md_latest}")
    print(f"ledger={ledger_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
