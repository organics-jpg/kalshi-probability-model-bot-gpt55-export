"""Physics/path posterior strategy projection.

Research-only. This probes whether the v38/v39 FV priors can be improved by a
train-only posterior built from path physics: distance to strike, realized-vol
margin, signed/adverse moves, anti-persistence shifts, time-to-close, and a
small optional book-observation residual.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import fit_logistic, logit, predict_logistic


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v41_physics_path_posterior_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v41_physics_path_posterior_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v41_physics_path_posterior_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v41_physics_path_posterior_strategy_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v41_physics_path_posterior_strategy_selected_trades_latest.csv"

PROB_EPS = 1e-6
MIN_SPLIT_COVERAGE = 0.80
ASK_FLOOR_CENTS = 1.0

RAW_MODELS = {
    "v38": "v38_long60_antipersist",
    "v39": "v39_midband_v28_fallback",
}

ENTRY_POLICIES = [
    base.EntryPolicy(edge, ask, pside, max_stc, 0.0)
    for edge in [-3.0, 0.0, 1.0]
    for ask in [100.0, 95.0]
    for pside in [0.60, 0.65]
    for max_stc in [600.0, 780.0]
]

EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob52", probability_floor=0.52),
    base.ExitPolicy("prob54", probability_floor=0.54),
    base.ExitPolicy("prob56", probability_floor=0.56),
    base.ExitPolicy("take8_or_prob52", take_profit_cents=8.0, probability_floor=0.52),
    base.ExitPolicy("take10_or_prob52", take_profit_cents=10.0, probability_floor=0.52),
]


@dataclass(frozen=True)
class VetoPolicy:
    name: str
    low: float | None = None
    high: float | None = None


VETO_POLICIES = [
    VetoPolicy("none"),
    VetoPolicy("block_first_edge_8_20", 8.0, 20.0),
    VetoPolicy("block_first_edge_10_20", 10.0, 20.0),
]


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def load_rows() -> pd.DataFrame:
    usecols = {
        "opportunity_key",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "book_margin_cents",
        "spread_cents",
        "seconds_to_close",
        "split",
        "margin_per_v28_sigma",
        "margin_per_rv_sigma_5m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "margin_per_rv_sigma_60m",
        "rv_sigma_t_5m",
        "rv_sigma_t_15m",
        "rv_sigma_t_30m",
        "rv_sigma_t_60m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_10m",
        "signed_move_15m",
        "signed_move_30m",
        "signed_move_60m",
        "adverse_move_1m",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_10m",
        "adverse_move_15m",
        "adverse_move_30m",
        "adverse_move_60m",
        "drift_projected_margin_1m",
        "drift_projected_margin_3m",
        "drift_projected_margin_5m",
        "drift_projected_margin_10m",
        "drift_projected_margin_15m",
        "drift_projected_margin_30m",
        "book_minus_brownian_rv15",
        "physics_confirmed_book",
        "score_mean_book_rv15",
        "score_mean_book_rv15_drift5",
        "score_min_book_rv15",
    }
    for model in RAW_MODELS.values():
        usecols.add(f"{model}_p_yes")
        usecols.add(f"{model}_d_sigma")
        usecols.add(f"{model}_anti_persistence_shift_dollars")
        usecols.add(f"{model}_anti_persistence_logit_weight")
        usecols.add(f"{model}_anti_persistence_materiality_gate")
        usecols.add(f"{model}_long_anti_persistence_shift_dollars")
        usecols.add(f"{model}_long_anti_persistence_logit_weight")
        usecols.add(f"{model}_long_anti_persistence_materiality_gate")

    rows = pd.read_csv(INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in rows.columns:
        if col not in {"opportunity_key", "entry_dt", "market", "side", "outcome", "win", "split", "physics_confirmed_book"}:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    rows["physics_confirmed_book"] = rows["physics_confirmed_book"].astype(str).str.lower().isin({"true", "1", "yes"}).astype(float)
    return rows.dropna(subset=["opportunity_key", "entry_dt", "market", "side", "ask_cents", "seconds_to_close", "split"]).sort_values(
        ["market", "entry_dt", "side"]
    ).reset_index(drop=True)


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    den = pd.to_numeric(den, errors="coerce").abs().clip(lower=1e-6)
    return pd.to_numeric(num, errors="coerce") / den


def opportunity_table(rows: pd.DataFrame) -> pd.DataFrame:
    yes = rows[rows["side"].astype(str).eq("yes")].drop_duplicates("opportunity_key").copy()
    piv = rows.pivot_table(index="opportunity_key", columns="side", values="book_mid_cents", aggfunc="first").rename(
        columns={"yes": "yes_book_mid_cents", "no": "no_book_mid_cents"}
    )
    ops = yes.merge(piv, left_on="opportunity_key", right_index=True, how="left")
    denom = ops["yes_book_mid_cents"] + ops["no_book_mid_cents"]
    ops["book_mid_p_yes"] = (ops["yes_book_mid_cents"] / denom).clip(PROB_EPS, 1.0 - PROB_EPS)
    ops["outcome_yes"] = ops["outcome"].astype(str).str.lower().eq("yes").astype(float)
    ops["log_time_to_close"] = np.log(np.clip(pd.to_numeric(ops["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    ops["spread_cents"] = pd.to_numeric(ops["spread_cents"], errors="coerce").fillna(0.0)

    rv15 = pd.to_numeric(ops["rv_sigma_t_15m"], errors="coerce").abs().clip(lower=1e-6)
    rv60 = pd.to_numeric(ops["rv_sigma_t_60m"], errors="coerce").abs().clip(lower=1e-6)
    for horizon in ["1m", "3m", "5m", "10m", "15m", "30m", "60m"]:
        ops[f"signed_move_{horizon}_per_rv15"] = safe_div(ops[f"signed_move_{horizon}"], rv15)
        ops[f"adverse_move_{horizon}_per_rv15"] = safe_div(ops[f"adverse_move_{horizon}"], rv15)
    for horizon in ["1m", "3m", "5m", "10m", "15m", "30m"]:
        ops[f"drift_margin_{horizon}_per_rv15"] = safe_div(ops[f"drift_projected_margin_{horizon}"], rv15)
    ops["rv15_over_rv60"] = rv15 / rv60

    for short, model in RAW_MODELS.items():
        ops[f"{short}_p_yes"] = pd.to_numeric(ops[f"{model}_p_yes"], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
        ops[f"{short}_logit"] = logit(ops[f"{short}_p_yes"])
        ops[f"{short}_d_sigma"] = pd.to_numeric(ops[f"{model}_d_sigma"], errors="coerce")
        ops[f"{short}_shift_per_rv15"] = safe_div(ops[f"{model}_anti_persistence_shift_dollars"], rv15)
        ops[f"{short}_long_shift_per_rv15"] = safe_div(ops[f"{model}_long_anti_persistence_shift_dollars"], rv15)
        ops[f"{short}_anti_weight"] = pd.to_numeric(ops[f"{model}_anti_persistence_logit_weight"], errors="coerce")
        ops[f"{short}_long_anti_weight"] = pd.to_numeric(ops[f"{model}_long_anti_persistence_logit_weight"], errors="coerce")
        ops[f"{short}_material_gate"] = pd.to_numeric(ops[f"{model}_anti_persistence_materiality_gate"], errors="coerce")
        ops[f"{short}_long_material_gate"] = pd.to_numeric(
            ops[f"{model}_long_anti_persistence_materiality_gate"], errors="coerce"
        )
        ops[f"book_gap_{short}"] = logit(ops["book_mid_p_yes"]) - ops[f"{short}_logit"]

    needed = ["opportunity_key", "entry_dt", "market", "split", "outcome_yes", "book_mid_p_yes", "v38_p_yes", "v39_p_yes"]
    return ops.dropna(subset=needed).reset_index(drop=True)


CORE_PATH_FEATURES = [
    "log_time_to_close",
    "margin_per_v28_sigma",
    "margin_per_rv_sigma_15m",
    "margin_per_rv_sigma_60m",
    "rv15_over_rv60",
    "signed_move_3m_per_rv15",
    "signed_move_5m_per_rv15",
    "signed_move_15m_per_rv15",
    "adverse_move_5m_per_rv15",
    "adverse_move_15m_per_rv15",
    "drift_margin_3m_per_rv15",
    "drift_margin_5m_per_rv15",
]

RICH_PATH_FEATURES = CORE_PATH_FEATURES + [
    "signed_move_1m_per_rv15",
    "signed_move_10m_per_rv15",
    "signed_move_30m_per_rv15",
    "signed_move_60m_per_rv15",
    "adverse_move_1m_per_rv15",
    "adverse_move_3m_per_rv15",
    "adverse_move_10m_per_rv15",
    "adverse_move_30m_per_rv15",
    "adverse_move_60m_per_rv15",
    "drift_margin_1m_per_rv15",
    "drift_margin_10m_per_rv15",
    "drift_margin_15m_per_rv15",
    "book_minus_brownian_rv15",
    "physics_confirmed_book",
    "score_mean_book_rv15",
    "score_mean_book_rv15_drift5",
    "score_min_book_rv15",
    "spread_cents",
]


def feature_sets_for(base_name: str) -> dict[str, list[str]]:
    own = [
        f"{base_name}_logit",
        f"{base_name}_d_sigma",
        f"{base_name}_shift_per_rv15",
        f"{base_name}_long_shift_per_rv15",
        f"{base_name}_anti_weight",
        f"{base_name}_long_anti_weight",
        f"{base_name}_material_gate",
        f"{base_name}_long_material_gate",
    ]
    return {
        f"{base_name}_physics_core": [f"{base_name}_logit", f"{base_name}_d_sigma", *CORE_PATH_FEATURES[:8], f"{base_name}_long_shift_per_rv15"],
        f"{base_name}_physics_path": [*own, *CORE_PATH_FEATURES],
        f"{base_name}_physics_rich": [*own, *RICH_PATH_FEATURES],
        f"{base_name}_physics_book_residual": [*own, *CORE_PATH_FEATURES, f"book_gap_{base_name}", "spread_cents"],
    }


def finite_matrix(frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    out = frame[features].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    out[~np.isfinite(out)] = np.nan
    return out


def fit_scaled_imputed_logistic(x: np.ndarray, y: np.ndarray, *, l2: float) -> dict[str, Any]:
    x = np.asarray(x, dtype=float)
    medians = np.zeros(x.shape[1], dtype=float)
    for idx in range(x.shape[1]):
        col = x[:, idx]
        finite = col[np.isfinite(col)]
        medians[idx] = float(np.median(finite)) if len(finite) else 0.0
    clean = np.where(np.isfinite(x), x, medians)
    means = clean.mean(axis=0)
    scales = clean.std(axis=0)
    scales = np.where(scales > 1e-9, scales, 1.0)
    beta = fit_logistic((clean - means) / scales, y, l2=l2)
    return {"beta": beta.tolist(), "medians": medians.tolist(), "means": means.tolist(), "scales": scales.tolist(), "l2": float(l2)}


def predict_scaled_imputed(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    medians = np.asarray(model["medians"], dtype=float)
    means = np.asarray(model["means"], dtype=float)
    scales = np.asarray(model["scales"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    clean = np.where(np.isfinite(x), x, medians)
    return predict_logistic(beta, (clean - means) / scales)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], list[str]]:
    out = ops.copy()
    train = out[out["split"].eq("train")].copy()
    y = train["outcome_yes"].to_numpy(dtype=float)
    model_specs: dict[str, Any] = {}
    candidate_cols: list[str] = []

    for short in RAW_MODELS:
        col = f"{short}_raw_p_yes_candidate"
        out[col] = out[f"{short}_p_yes"]
        candidate_cols.append(col)

    for short in RAW_MODELS:
        for family, features in feature_sets_for(short).items():
            usable = [f for f in features if f in out.columns]
            if len(usable) < 3:
                continue
            for l2 in [10.0, 30.0]:
                name = f"v41_{family}_l2{int(l2)}"
                col = f"{name}_p_yes_candidate"
                fitted = fit_scaled_imputed_logistic(finite_matrix(train, usable), y, l2=l2)
                fitted["features"] = usable
                model_specs[name] = fitted
                out[col] = predict_scaled_imputed(fitted, finite_matrix(out, usable)).clip(PROB_EPS, 1.0 - PROB_EPS)
                candidate_cols.append(col)

    return out, model_specs, candidate_cols


def probability_metrics(ops: pd.DataFrame, candidate_cols: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for col in candidate_cols:
        for split in ["train", "validation", "holdout", "all"]:
            part = ops if split == "all" else ops[ops["split"].eq(split)]
            y = part["outcome_yes"].to_numpy(dtype=float)
            p = np.clip(part[col].to_numpy(dtype=float), PROB_EPS, 1.0 - PROB_EPS)
            records.append(
                {
                    "candidate": col.replace("_p_yes_candidate", ""),
                    "split": split,
                    "rows": int(len(part)),
                    "brier": float(np.mean((p - y) ** 2)),
                    "logloss": float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean()),
                    "side_accuracy": float(((p >= 0.5) == (y >= 0.5)).mean()),
                    "mean_p_yes": float(p.mean()),
                    "yes_rate": float(y.mean()),
                }
            )
    return records


def frame_for_candidate(rows: pd.DataFrame, ops: pd.DataFrame, candidate_col: str) -> pd.DataFrame:
    probs = ops[["opportunity_key", candidate_col]].rename(columns={candidate_col: "p_yes"})
    frame = rows.merge(probs, on="opportunity_key", how="inner")
    frame["model"] = candidate_col.replace("_p_yes_candidate", "")
    frame["p_yes"] = pd.to_numeric(frame["p_yes"], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
    frame["p_side"] = np.where(frame["side"].astype(str).eq("yes"), frame["p_yes"], 1.0 - frame["p_yes"])
    frame["entry_edge_cents"] = 100.0 * frame["p_side"] - frame["ask_cents"]
    frame["fair_side_cents"] = 100.0 * frame["p_side"]
    return frame.dropna(subset=["p_yes", "p_side", "entry_edge_cents"]).copy()


def choose_entries_with_veto(best_opp: pd.DataFrame, entry: base.EntryPolicy, veto: VetoPolicy) -> pd.DataFrame:
    eligible = best_opp[
        best_opp["entry_edge_cents"].ge(entry.edge_floor_cents)
        & best_opp["ask_cents"].ge(ASK_FLOOR_CENTS)
        & best_opp["ask_cents"].le(entry.ask_cap_cents)
        & best_opp["p_side"].ge(entry.min_p_side)
        & best_opp["seconds_to_close"].le(entry.max_seconds_to_close)
        & best_opp["seconds_to_close"].ge(entry.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return eligible
    first = eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    if veto.low is None or veto.high is None:
        return first
    in_hole = first["entry_edge_cents"].gt(veto.low) & first["entry_edge_cents"].le(veto.high)
    return first[~in_hole].reset_index(drop=True)


def row_1c_positive(record: dict[str, Any]) -> bool:
    return all(float(record[f"{split}_net_after_fees_1c_entry_dollars"]) > 0.0 for split in ["train", "validation", "holdout"])


def day_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {"positive_days": 0, "total_days": 0, "worst_day_cents": None}
    rows = trades.copy()
    rows["entry_day_utc"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    rows["fee_net_1c_entry_cents"] = rows["pnl_cents"] - rows["total_fee_cents"] - base.QTY
    values = rows.groupby("entry_day_utc")["fee_net_1c_entry_cents"].sum().to_numpy(dtype=float)
    return {
        "positive_days": int((values > 0).sum()),
        "total_days": int(len(values)),
        "worst_day_cents": float(values.min()) if len(values) else None,
    }


def block_metrics(trades: pd.DataFrame, blocks: int) -> dict[str, Any]:
    if trades.empty:
        return {"positive_blocks": 0, "worst_cents": None}
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    indices = np.array_split(np.arange(len(ordered)), blocks)
    values = [
        float((ordered.iloc[idx]["pnl_cents"] - ordered.iloc[idx]["total_fee_cents"] - base.QTY).sum())
        for idx in indices
        if len(idx)
    ]
    return {
        "positive_blocks": int(sum(v > 0 for v in values)),
        "worst_cents": float(min(values)) if values else None,
    }


def build_strategy(rows: pd.DataFrame, ops: pd.DataFrame, candidate_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    universes = base.market_universes(rows)
    records: list[dict[str, Any]] = []
    selected_trade_frames: list[pd.DataFrame] = []
    selected_keys: set[tuple[str, str, str, str]] = set()

    for col in candidate_cols:
        frame = frame_for_candidate(rows, ops, col)
        best_opp = base.best_side_per_opportunity(frame)
        paths = base.quote_paths(frame)
        for entry_policy in ENTRY_POLICIES:
            for veto in VETO_POLICIES:
                entries = choose_entries_with_veto(best_opp, entry_policy, veto)
                if entries.empty:
                    continue
                min_coverage = min(
                    len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                    for split in ["train", "validation", "holdout"]
                )
                if min_coverage < MIN_SPLIT_COVERAGE:
                    continue
                for exit_policy in EXIT_POLICIES:
                    trades = base.simulate(entries, paths, exit_policy)
                    if trades.empty:
                        continue
                    record = base.flatten_metrics(str(frame["model"].iloc[0]), entry_policy, exit_policy, trades, universes)
                    record["veto_policy"] = veto.name
                    record["veto_low"] = veto.low
                    record["veto_high"] = veto.high
                    record["min_split_net_after_fees_1c_entry_dollars"] = float(
                        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
                    )
                    record["all_splits_1c_entry_positive"] = row_1c_positive(record)
                    days = day_metrics(trades)
                    record["positive_1c_days"] = days["positive_days"]
                    record["total_days"] = days["total_days"]
                    record["worst_1c_day_cents"] = days["worst_day_cents"]
                    block10 = block_metrics(trades, 10)
                    record["block10_positive"] = block10["positive_blocks"]
                    record["block10_worst_cents"] = block10["worst_cents"]
                    records.append(record)

    summary = pd.DataFrame(records)
    if summary.empty:
        return summary, pd.DataFrame()

    selected = selected_rows(summary)
    for _, row in selected.head(12).iterrows():
        key = (str(row["model"]), str(row["entry_policy"]), str(row["exit_policy"]), str(row["veto_policy"]))
        if key in selected_keys:
            continue
        selected_keys.add(key)
        entry = base.EntryPolicy(
            float(row["entry_edge_floor_cents"]),
            float(row["entry_ask_cap_cents"]),
            float(row["entry_min_p_side"]),
            float(row["entry_max_seconds_to_close"]),
            float(row["entry_min_seconds_to_close"]),
        )
        veto = VetoPolicy(str(row["veto_policy"]), None if pd.isna(row["veto_low"]) else float(row["veto_low"]), None if pd.isna(row["veto_high"]) else float(row["veto_high"]))
        exit_policy = exit_policy_from_name(str(row["exit_policy"]))
        frame = frame_for_candidate(rows, ops, f"{row['model']}_p_yes_candidate")
        trades = base.simulate(choose_entries_with_veto(base.best_side_per_opportunity(frame), entry, veto), base.quote_paths(frame), exit_policy)
        trades["entry_policy"] = row["entry_policy"]
        trades["exit_policy"] = row["exit_policy"]
        trades["veto_policy"] = row["veto_policy"]
        selected_trade_frames.append(trades)
    selected_trades = pd.concat(selected_trade_frames, ignore_index=True, sort=False) if selected_trade_frames else pd.DataFrame()
    return summary, selected_trades


def exit_policy_from_name(name: str) -> base.ExitPolicy:
    if name == "hold":
        return base.ExitPolicy("hold")
    if name.startswith("prob"):
        return base.ExitPolicy(name, probability_floor=float(name.replace("prob", "")) / 100.0)
    if name.startswith("take"):
        parts = name.split("_or_")
        take = float(parts[0].replace("take", ""))
        prob = None
        if len(parts) > 1 and parts[1].startswith("prob"):
            prob = float(parts[1].replace("prob", "")) / 100.0
        return base.ExitPolicy(name, take_profit_cents=take, probability_floor=prob)
    raise ValueError(f"Unknown exit policy: {name}")


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    pieces: list[pd.DataFrame] = []
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(8)
    ].copy()
    if not robust.empty:
        pieces.append(
            robust.sort_values(
                [
                    "min_split_net_after_fees_1c_entry_dollars",
                    "worst_1c_day_cents",
                    "block10_worst_cents",
                    "all_net_after_fees_1c_entry_dollars",
                ],
                ascending=[False, False, False, False],
            ).head(30)
        )
    split_positive = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not split_positive.empty:
        pieces.append(
            split_positive.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False],
            ).head(30)
        )
    pieces.append(
        eligible.sort_values(
            [
                "min_split_net_after_fees_1c_entry_dollars",
                "positive_1c_days",
                "block10_positive",
                "all_net_after_fees_1c_entry_dollars",
            ],
            ascending=[False, False, False, False],
        ).head(30)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(["model", "entry_policy", "exit_policy", "veto_policy"])


def model_family(model: str) -> str:
    if model in {"v38_raw", "v39_raw"}:
        return "raw"
    if "book_residual" in model:
        return "book_residual"
    if "physics_core" in model:
        return "physics_core"
    if "physics_path" in model:
        return "physics_path"
    if "physics_rich" in model:
        return "physics_rich"
    return "other"


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    specs: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    all_day = one_cent[one_cent["positive_1c_days"].eq(one_cent["total_days"])].copy() if not one_cent.empty else one_cent
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"]).head(15)

    selected_out = selected.copy()
    if not selected_out.empty:
        selected_out["family"] = selected_out["model"].map(model_family)
    family_best = (
        selected_out.sort_values(["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"], ascending=[False, False])
        .groupby("family", as_index=False)
        .head(1)
        if not selected_out.empty
        else selected_out
    )

    lines = [
        "# v41 Physics/Path Posterior Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Train-only posterior probability models from v38/v39 plus path physics.",
        "- Strategy projection requires at least 80% coverage in every chronological split.",
        "- Entry simulation has an executable ask floor of 1c.",
        "- Research-only; live bot untouched.",
        "",
        "## Probability Holdout",
        "",
        "| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {int(row['rows'])} | {float(row['brier']):.5f} | "
            f"{float(row['logloss']):.5f} | {pct(row['side_accuracy'])} | "
            f"{pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Strategy Search",
        "",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive train/validation/holdout rows: {len(one_cent)}",
        f"- Fee+1c positive across all UTC days rows: {len(all_day)}",
        "",
        "## Best By Family",
        "",
        "| family | model | veto | entry | exit | min cov | min 1c | all 1c | days | b10 | trades |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in family_best.iterrows():
        lines.append(
            f"| `{row['family']}` | `{row['model']}` | `{row['veto_policy']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{pct(row['min_split_coverage'])} | {dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )

    lines += [
        "",
        "## Selected Strategy Rows",
        "",
        "| model | veto | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | b10 | trades |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(35).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['veto_policy']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{pct(row['min_split_coverage'])} | {dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | {dollars(row['all_net_after_fees_dollars'])} | "
            f"{dollars(row['all_pnl_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )

    lines += ["", "## Read", ""]
    if one_cent.empty:
        lines.append("- No v41 posterior row produced fee+1c-positive P&L across train/validation/holdout at 80% split coverage.")
    else:
        best = one_cent.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best fee+1c split-positive row is `{best['model']}` / `{best['veto_policy']}` / `{best['entry_policy']}` / "
            f"`{best['exit_policy']}` with min split fee+1c {dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    if not all_day.empty:
        best_day = all_day.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-day-positive row is `{best_day['model']}` with min split fee+1c "
            f"{dollars(best_day['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Book-residual rows are labeled separately because they are observation-aided, not purely physical.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_positive_rows": int(len(all_day)),
                    "probability_records": prob_records,
                    "model_specs": specs,
                    "selected": selected.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = load_rows()
    ops = opportunity_table(rows)
    ops, specs, candidate_cols = build_probability_candidates(ops)
    prob_records = probability_metrics(ops, candidate_cols)
    summary, selected_trades = build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_rows(summary) if not summary.empty else summary
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, specs, candidate_cols)
    one_cent = summary[summary["all_splits_1c_entry_positive"]] if not summary.empty else summary
    print("v41 physics/path posterior strategy complete")
    print(f"summary_rows={len(summary)} one_cent_rows={len(one_cent)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['veto_policy']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
