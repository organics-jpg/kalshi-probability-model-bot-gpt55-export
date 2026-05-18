"""Research-only two-sided FV probe on live heartbeat states.

The heartbeat prior audit tests whether the current book favorite can be
filtered into a 95% / 75% selected set. This probe asks the next physics
question: if a fair-value surface may choose either YES or NO at each heartbeat,
can simple book/realized-vol/drift scores choose the right side at high volume?

It reads only existing logs/caches and writes under logs/edge_research. It does
not import or modify the live bot, submit orders, or control any process.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_live_heartbeat_physics_priors import (
    LOCAL_TZ,
    MIN_HOLDOUT_ROWS,
    MIN_RETENTION,
    MIN_SELECTED_ROWS,
    RETENTION_FLOORS,
    attach_physics,
    local_log_ts_to_utc,
    pct,
    safe_mid,
)
from probe_live_v28_fv_accuracy_volume import (
    BOT_LOG,
    OUT_DIR,
    as_float,
    parse_bot_log,
    parse_quote_token,
)
from probe_physics_priors_boundary_models import (
    MIN_TARGET_ACCURACY,
    clean_json,
    oracle_bound,
)
from shadow_live_v28_physics_validator import closed_market_outcomes_only


PRIMARY_MODE = "two_side_minute_bucket"


def heartbeat_two_side_rows(
    markets: Dict[str, Dict[str, Any]],
    outcomes: Dict[str, Dict[str, Any]],
) -> pd.DataFrame:
    heartbeat_re = re.compile(
        r"^(?P<log_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| .*?Heartbeat \| "
        r"watch=(?P<market>\S+) yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
        r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+) "
        r"book_ready=(?P<book_ready>\S+) position=(?P<position>\S+) "
        r"pending=(?P<pending>\S+) dry_run=(?P<dry_run>\S+) trust=(?P<trust>\S+)"
    )
    rows: List[Dict[str, Any]] = []
    with BOT_LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            match = heartbeat_re.search(line)
            if not match or match.group("book_ready") != "True":
                continue
            market = match.group("market")
            market_info = markets.get(market) or {}
            close_dt = pd.to_datetime(market_info.get("close_time"), utc=True, errors="coerce")
            strike = as_float(market_info.get("strike"))
            entry_dt = local_log_ts_to_utc(match.group("log_ts"))
            if entry_dt is None or pd.isna(close_dt) or strike is None:
                continue
            seconds_to_close = (close_dt - entry_dt).total_seconds()
            if seconds_to_close <= 0:
                continue

            yes_bid = parse_quote_token(match.group("yes_bid"))
            yes_ask = parse_quote_token(match.group("yes_ask"))
            no_bid = parse_quote_token(match.group("no_bid"))
            no_ask = parse_quote_token(match.group("no_ask"))
            yes_mid = safe_mid(yes_bid, yes_ask)
            no_mid = safe_mid(no_bid, no_ask)
            if yes_mid is None or no_mid is None:
                continue
            quote_by_side = {
                "yes": {"bid": yes_bid, "ask": yes_ask, "mid": yes_mid, "other_mid": no_mid},
                "no": {"bid": no_bid, "ask": no_ask, "mid": no_mid, "other_mid": yes_mid},
            }
            outcome = outcomes.get(market, {}).get("outcome")
            for side, quote in quote_by_side.items():
                if quote["bid"] is None or quote["ask"] is None:
                    continue
                rows.append(
                    {
                        "dataset": "live_heartbeat_two_side",
                        "decision_key": f"heartbeat:{line_no}",
                        "entry_key": f"heartbeat:{line_no}:{side}",
                        "entry_dt": entry_dt,
                        "entry_minute": entry_dt.floor("min"),
                        "market": market,
                        "side": side,
                        "outcome": outcome,
                        "outcome_available": outcome in {"yes", "no"},
                        "win": bool(side == outcome) if outcome in {"yes", "no"} else None,
                        "qty": 1,
                        "ask_cents": float(quote["ask"]),
                        "bid_cents": float(quote["bid"]),
                        "book_mid_cents": float(quote["mid"]),
                        "book_p_side": float(quote["mid"]) / 100.0,
                        "book_other_mid_cents": float(quote["other_mid"]),
                        "book_margin_cents": float(quote["mid"] - quote["other_mid"]),
                        "spread_cents": float(quote["ask"] - quote["bid"]),
                        "spot": np.nan,
                        "strike": strike,
                        "seconds_to_close": float(seconds_to_close),
                        "v28_sigma_t_dollars": np.nan,
                        "source_line_no": line_no,
                        "position_open_logged": match.group("position") == "True",
                        "pending_logged": match.group("pending") == "True",
                        "trust_state": match.group("trust"),
                        "outcome_method": outcomes.get(market, {}).get("method"),
                        "outcome_source": outcomes.get(market, {}).get("source"),
                    }
                )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["entry_dt", "source_line_no", "side"]).reset_index(drop=True)


def group_candidates(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.sort_values(["entry_dt", "source_line_no", "side"]).copy()
    if mode == "two_side_all_heartbeats":
        out["opportunity_key"] = out["decision_key"]
    elif mode == "two_side_minute_bucket":
        first_keys = (
            out.groupby(["market", "entry_minute"], as_index=False, sort=False)["decision_key"]
            .first()
            .rename(columns={"decision_key": "kept_decision_key"})
        )
        out = out.merge(first_keys, on=["market", "entry_minute"], how="inner")
        out = out[out["decision_key"] == out["kept_decision_key"]].drop(columns=["kept_decision_key"])
        out["opportunity_key"] = out["market"] + "|" + out["entry_minute"].astype(str)
    elif mode == "two_side_first_per_market":
        first_keys = (
            out.groupby(["market"], as_index=False, sort=False)["decision_key"]
            .first()
            .rename(columns={"decision_key": "kept_decision_key"})
        )
        out = out.merge(first_keys, on=["market"], how="inner")
        out = out[out["decision_key"] == out["kept_decision_key"]].drop(columns=["kept_decision_key"])
        out["opportunity_key"] = out["market"]
    else:
        raise ValueError(f"unknown mode: {mode}")
    out["two_side_mode"] = mode
    return out.sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


@dataclass(frozen=True)
class DecisionModel:
    family: str
    label: str
    score_feature: str
    min_score: float
    ask_max: float
    require_book_agreement: bool = False


def make_models() -> List[DecisionModel]:
    models: List[DecisionModel] = []

    def add(
        family: str,
        label: str,
        score_feature: str,
        min_score: float,
        ask_max: float,
        require_book_agreement: bool = False,
    ) -> None:
        models.append(
            DecisionModel(
                family=family,
                label=label,
                score_feature=score_feature,
                min_score=min_score,
                ask_max=ask_max,
                require_book_agreement=require_book_agreement,
            )
        )

    score_specs = [
        ("book", "book_p_side", [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
        ("brownian_rv15", "brownian_p_rv_15m", [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
        ("brownian_rv30", "brownian_p_rv_30m", [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
        ("drift_rv15", "drift_p_5m_rv_15m", [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
    ]
    for family, feature, thresholds in score_specs:
        for ask_max in [90.0, 95.0, 100.0]:
            for threshold in thresholds:
                add(family, f"{feature}>={threshold:.2f}; ask<={ask_max:g}", feature, threshold, ask_max)
                if family != "book":
                    add(
                        f"{family}_book_agree",
                        f"{feature}>={threshold:.2f}; book agrees; ask<={ask_max:g}",
                        feature,
                        threshold,
                        ask_max,
                        require_book_agreement=True,
                    )
    return models


def add_composite_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["score_mean_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].mean(axis=1)
    out["score_mean_book_rv15_drift5"] = out[["book_p_side", "brownian_p_rv_15m", "drift_p_5m_rv_15m"]].mean(axis=1)
    out["score_min_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].min(axis=1)
    return out


def add_composite_models(models: List[DecisionModel]) -> List[DecisionModel]:
    out = list(models)
    for family, feature in [
        ("mean_book_rv15", "score_mean_book_rv15"),
        ("mean_book_rv15_drift5", "score_mean_book_rv15_drift5"),
        ("min_book_rv15", "score_min_book_rv15"),
    ]:
        for ask_max in [90.0, 95.0, 100.0]:
            for threshold in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
                out.append(
                    DecisionModel(
                        family=family,
                        label=f"{feature}>={threshold:.2f}; ask<={ask_max:g}",
                        score_feature=feature,
                        min_score=threshold,
                        ask_max=ask_max,
                    )
                )
    return out


def choose_decisions(df: pd.DataFrame, model: DecisionModel) -> pd.DataFrame:
    if df.empty or model.score_feature not in df.columns:
        return df.iloc[0:0].copy()
    candidates = df[df[model.score_feature].notna() & df["ask_cents"].notna()].copy()
    candidates = candidates[candidates["ask_cents"] <= model.ask_max]
    if candidates.empty:
        return candidates

    if model.require_book_agreement:
        best_book_side = (
            df.sort_values(["opportunity_key", "book_p_side"], ascending=[True, False])
            .groupby("opportunity_key", as_index=False, sort=False)
            .first()[["opportunity_key", "side"]]
            .rename(columns={"side": "best_book_side"})
        )
        candidates = candidates.merge(best_book_side, on="opportunity_key", how="left")
        candidates = candidates[candidates["side"] == candidates["best_book_side"]].copy()
        if candidates.empty:
            return candidates

    chosen = (
        candidates.sort_values(["opportunity_key", model.score_feature, "book_p_side"], ascending=[True, False, False])
        .groupby("opportunity_key", as_index=False, sort=False)
        .first()
    )
    chosen = chosen[chosen[model.score_feature] >= model.min_score].copy()
    return chosen.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


def split_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("entry_dt").reset_index(drop=True).copy()
    n = len(out)
    train_end = int(math.floor(n * 0.60))
    val_end = int(math.floor(n * 0.80))
    split = np.full(n, "holdout", dtype=object)
    split[:train_end] = "train"
    split[train_end:val_end] = "validation"
    out["split"] = split
    return out


def metrics_for_selected(selected: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    rows = int(len(selected))
    wins = int(selected["win"].sum()) if rows else 0
    total = int(len(base))
    return {
        "rows": rows,
        "wins": wins,
        "accuracy": wins / rows if rows else None,
        "retention": rows / total if total else None,
        "total_rows": total,
    }


def selected_metrics(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    out = {"all": metrics_for_selected(selected, base)}
    for split in ["train", "validation", "holdout"]:
        base_part = base[base["split"] == split]
        selected_part = selected[selected["split"] == split] if "split" in selected.columns else selected.iloc[0:0]
        out[split] = metrics_for_selected(selected_part, base_part)
    return out


def rule_passes(metrics: Dict[str, Dict[str, Any]], with_samples: bool) -> bool:
    for split in ["all", "validation", "holdout"]:
        metric = metrics[split]
        if (metric["accuracy"] or 0.0) < MIN_TARGET_ACCURACY:
            return False
        if (metric["retention"] or 0.0) < MIN_RETENTION:
            return False
    if with_samples:
        if metrics["all"]["rows"] < MIN_SELECTED_ROWS:
            return False
        if metrics["holdout"]["rows"] < MIN_HOLDOUT_ROWS:
            return False
    return True


def ranking_tuple(result: Dict[str, Any]) -> tuple:
    metrics = result["metrics"]
    all_m = metrics["all"]
    val_m = metrics["validation"]
    hold_m = metrics["holdout"]
    min_acc = min(all_m["accuracy"] or 0.0, val_m["accuracy"] or 0.0, hold_m["accuracy"] or 0.0)
    min_ret = min(all_m["retention"] or 0.0, val_m["retention"] or 0.0, hold_m["retention"] or 0.0)
    return (
        int(result["target_pass"]),
        int(result["observed_pass"]),
        min_acc,
        hold_m["accuracy"] or 0.0,
        min_ret,
        all_m["rows"],
    )


def oracle_bounds(base: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for split in ["all", "validation", "holdout"]:
        part = base if split == "all" else base[base["split"] == split]
        # With two sides present per opportunity, a perfect side chooser can be
        # 100% accurate, but this keeps the checklist shape comparable.
        raw = {
            "trades": int(len(part)),
            "contracts": int(len(part)),
            "trade_wins": int(len(part)),
            "contract_wins": int(len(part)),
        }
        split_bounds: List[Dict[str, Any]] = []
        for floor in RETENTION_FLOORS:
            bound = oracle_bound(raw, floor)
            bound["target_possible"] = (bound["max_contract_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
            split_bounds.append(bound)
        out[split] = split_bounds
    return out


def evaluate_mode(df: pd.DataFrame, models: Iterable[DecisionModel]) -> Dict[str, Any]:
    base = (
        df.sort_values(["entry_dt", "opportunity_key"])
        .drop_duplicates("opportunity_key", keep="first")[["opportunity_key", "entry_dt"]]
        .reset_index(drop=True)
    )
    base = split_dataset(base)
    split_by_key = base[["opportunity_key", "split"]]
    side_rows = df.merge(split_by_key, on="opportunity_key", how="inner")
    results: List[Dict[str, Any]] = []
    for model in models:
        chosen = choose_decisions(side_rows, model)
        metrics = selected_metrics(base, chosen)
        observed_pass = rule_passes(metrics, with_samples=False)
        target_pass = rule_passes(metrics, with_samples=True)
        results.append(
            {
                "family": model.family,
                "label": model.label,
                "score_feature": model.score_feature,
                "min_score": model.min_score,
                "ask_max": model.ask_max,
                "require_book_agreement": model.require_book_agreement,
                "metrics": metrics,
                "observed_pass": observed_pass,
                "target_pass": target_pass,
            }
        )
    results.sort(key=ranking_tuple, reverse=True)
    return {
        "baseline_opportunities": {
            "all": {"rows": int(len(base))},
            "train": {"rows": int((base["split"] == "train").sum())},
            "validation": {"rows": int((base["split"] == "validation").sum())},
            "holdout": {"rows": int((base["split"] == "holdout").sum())},
        },
        "oracle_bounds": oracle_bounds(base),
        "results": results,
        "target_pass_count": sum(1 for row in results if row["target_pass"]),
        "observed_pass_count": sum(1 for row in results if row["observed_pass"]),
        "row_count": int(len(base)),
    }


def flatten_candidates(evaluations: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for mode, evaluation in evaluations.items():
        for result in evaluation["results"]:
            row: Dict[str, Any] = {
                "mode": mode,
                "family": result["family"],
                "label": result["label"],
                "score_feature": result["score_feature"],
                "min_score": result["min_score"],
                "ask_max": result["ask_max"],
                "require_book_agreement": result["require_book_agreement"],
                "observed_pass": result["observed_pass"],
                "target_pass": result["target_pass"],
            }
            for split, metrics in result["metrics"].items():
                for key, value in metrics.items():
                    row[f"{split}_{key}"] = value
            rows.append(row)
    return pd.DataFrame(rows)


def write_report(
    path,
    generated: str,
    raw: pd.DataFrame,
    physics: pd.DataFrame,
    mode_frames: Dict[str, pd.DataFrame],
    evaluations: Dict[str, Any],
    candle_info: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Live Heartbeat Two-sided FV Probe")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append("- Source: live websocket heartbeat rows from `logs/live_mushroom_v28_size2/bot.log`.")
    lines.append("- Each heartbeat contributes both YES and NO candidate sides; score families choose one side or skip.")
    lines.append("- BTC spot and realized-volatility physics use cached/refreshed Coinbase 1m candles.")
    lines.append("- This is broad live telemetry, not fresh filled-trade completion evidence.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Raw two-sided rows: {len(raw)}")
    lines.append(f"- Rows with candle physics: {len(physics)}")
    lines.append(f"- Unique markets with physics: {physics['market'].nunique() if not physics.empty else 0}")
    lines.append(f"- Candle rows: {candle_info.get('rows', 0)}")
    lines.append(f"- Candle range: {candle_info.get('start')} to {candle_info.get('end')}")
    lines.append("")
    lines.append("## Mode Results")
    lines.append("")
    for mode in ["two_side_minute_bucket", "two_side_first_per_market", "two_side_all_heartbeats"]:
        frame = mode_frames.get(mode, pd.DataFrame())
        evaluation = evaluations.get(mode)
        if frame.empty or not evaluation:
            continue
        lines.append(f"### `{mode}`")
        lines.append("")
        lines.append(f"- Opportunity rows: {evaluation['row_count']}")
        lines.append(f"- Side candidate rows: {len(frame)}")
        lines.append(f"- Unique markets: {frame['market'].nunique()}")
        lines.append(f"- Target-pass models: {evaluation['target_pass_count']}")
        lines.append("")
        lines.append("Perfect side-choice oracle:")
        lines.append("")
        lines.append("| split | retention floor | required opportunities | max accuracy |")
        lines.append("|---|---:|---:|---:|")
        for split in ["all", "validation", "holdout"]:
            for bound in evaluation["oracle_bounds"][split]:
                lines.append(
                    f"| {split} | {pct(bound['retention_floor'])} | {bound['required_contracts']} | "
                    f"{pct(bound['max_contract_accuracy'])} |"
                )
        lines.append("")
        lines.append("Top high-retention side-choice models:")
        lines.append("")
        lines.append("| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---|")
        high_ret = [
            row
            for row in evaluation["results"]
            if (row["metrics"]["all"]["retention"] or 0.0) >= MIN_RETENTION
            and (row["metrics"]["holdout"]["retention"] or 0.0) >= MIN_RETENTION
        ][:10]
        if not high_ret:
            lines.append("|  |  | no model retained at least 75% of all and holdout opportunities |  |  |  |  |  |  |  |")
        for idx, result in enumerate(high_ret, start=1):
            all_m = result["metrics"]["all"]
            val_m = result["metrics"]["validation"]
            hold_m = result["metrics"]["holdout"]
            lines.append(
                f"| {idx} | {result['family']} | `{result['label']}` | {pct(all_m['accuracy'])} | "
                f"{pct(all_m['retention'])} | {pct(val_m['accuracy'])} | {pct(hold_m['accuracy'])} | "
                f"{pct(hold_m['retention'])} | {all_m['rows']} | {result['target_pass']} |"
            )
        lines.append("")
        lines.append("Top accuracy models:")
        lines.append("")
        lines.append("| rank | family | model | all acc | all ret | validation acc | holdout acc | holdout ret | selected | target |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---|")
        for idx, result in enumerate(evaluation["results"][:10], start=1):
            all_m = result["metrics"]["all"]
            val_m = result["metrics"]["validation"]
            hold_m = result["metrics"]["holdout"]
            lines.append(
                f"| {idx} | {result['family']} | `{result['label']}` | {pct(all_m['accuracy'])} | "
                f"{pct(all_m['retention'])} | {pct(val_m['accuracy'])} | {pct(hold_m['accuracy'])} | "
                f"{pct(hold_m['retention'])} | {all_m['rows']} | {result['target_pass']} |"
            )
        lines.append("")
    lines.append("## Completion Read")
    lines.append("")
    primary = evaluations.get(PRIMARY_MODE)
    if primary and primary["target_pass_count"] > 0:
        lines.append(
            "The primary two-sided heartbeat tape has a simple side-choice model meeting 95% accuracy "
            "and 75% retention on chronological splits. This remains broad telemetry, not fresh fill proof."
        )
    else:
        lines.append(
            "The primary two-sided heartbeat tape does not produce a simple non-overfit 95% / 75% side-choice model."
        )
    lines.append(
        "This falsifies the idea that merely allowing contrarian side choice fixes the current FV prior at high volume."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    raw = heartbeat_two_side_rows(markets, outcomes)
    if raw.empty:
        raise SystemExit("No usable two-sided heartbeat rows found.")
    physics, candle_info = attach_physics(raw, fetch_btc_candles=bool(args.fetch_btc_candles))
    physics = physics[physics["outcome_available"]].copy()
    physics = add_composite_scores(physics)
    if physics.empty:
        raise SystemExit("No resolved two-sided heartbeat rows with candle physics found.")

    models = add_composite_models(make_models())
    mode_frames: Dict[str, pd.DataFrame] = {}
    evaluations: Dict[str, Any] = {}
    for mode in ["two_side_minute_bucket", "two_side_first_per_market", "two_side_all_heartbeats"]:
        frame = group_candidates(physics, mode)
        mode_frames[mode] = frame
        if not frame.empty:
            evaluations[mode] = evaluate_mode(frame, models)

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    md_latest = OUT_DIR / "live_heartbeat_two_side_fv_latest.md"
    md_stamp = OUT_DIR / f"live_heartbeat_two_side_fv_{generated}.md"
    json_latest = OUT_DIR / "live_heartbeat_two_side_fv_latest.json"
    json_stamp = OUT_DIR / f"live_heartbeat_two_side_fv_{generated}.json"
    ledger_latest = OUT_DIR / "live_heartbeat_two_side_fv_ledger_latest.csv"
    ledger_stamp = OUT_DIR / f"live_heartbeat_two_side_fv_ledger_{generated}.csv"
    candidates_latest = OUT_DIR / "live_heartbeat_two_side_fv_candidates_latest.csv"
    candidates_stamp = OUT_DIR / f"live_heartbeat_two_side_fv_candidates_{generated}.csv"

    combined = pd.concat([frame for frame in mode_frames.values() if not frame.empty], ignore_index=True)
    combined.to_csv(ledger_latest, index=False)
    combined.to_csv(ledger_stamp, index=False)
    candidates = flatten_candidates(evaluations)
    candidates.to_csv(candidates_latest, index=False)
    candidates.to_csv(candidates_stamp, index=False)

    summary = {
        "generated_utc": generated,
        "raw_rows": int(len(raw)),
        "physics_rows": int(len(physics)),
        "candle_info": candle_info,
        "evaluations": evaluations,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")
    write_report(md_latest, generated, raw, physics, mode_frames, evaluations, candle_info)
    write_report(md_stamp, generated, raw, physics, mode_frames, evaluations, candle_info)

    primary = evaluations.get(PRIMARY_MODE, {})
    print("Live heartbeat two-sided FV probe complete")
    print(f"raw_rows={len(raw)} physics_rows={len(physics)}")
    if primary:
        print(
            f"primary={PRIMARY_MODE} opportunities={primary['row_count']} "
            f"target_pass={primary['target_pass_count']} observed_pass={primary['observed_pass_count']}"
        )
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
