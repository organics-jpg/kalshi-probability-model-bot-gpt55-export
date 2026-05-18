"""Strict forward monitor for the avg90 FV probability surface.

This monitor registers BTC 15m heartbeat probability predictions only while
the target market is still unresolved. Later runs join settled outcomes back
to the immutable registry and compare probability calibration for:

- current v28 close-to-close FV surface,
- v28 with effective 90s settlement-average horizon.

Research-only: no orders are submitted, no live bot files or processes are
modified, and no registry row is created after its market has already closed.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config
from btc_mushroom_forecaster_v30_fast import FastMushroomFVEngineV30, FastMushroomV30Config
from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config
from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config
from btc_mushroom_forecaster_v33_fast import FastMushroomFVEngineV33, FastMushroomV33Config
from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34, FastMushroomV34Config
from btc_mushroom_forecaster_v35_fast import FastMushroomFVEngineV35, FastMushroomV35Config
from btc_mushroom_forecaster_v36_fast import FastMushroomFVEngineV36, FastMushroomV36Config
from btc_mushroom_forecaster_v37_fast import FastMushroomFVEngineV37, FastMushroomV37Config
from btc_mushroom_forecaster_v38_fast import FastMushroomFVEngineV38, FastMushroomV38Config
from btc_mushroom_forecaster_v39_fast import FastMushroomFVEngineV39, FastMushroomV39Config
from probe_live_heartbeat_two_side_fv import heartbeat_two_side_rows, group_candidates
from probe_live_v28_fv_accuracy_volume import BOT_LOG, OUT_DIR, parse_bot_log
from probe_mushroom_v29_fv_surface import EngineSpec, load_candles, replay_predictions
from probe_probability_calibration_audit import brier, logloss
from shadow_live_v28_physics_validator import closed_market_outcomes_only


MODE = "two_side_minute_bucket"
LOCK_PATH = OUT_DIR / "fv_avg90_strict_probability_lock.json"
REGISTRY_PATH = OUT_DIR / "fv_avg90_strict_probability_registry_latest.csv"
REPORT_MD = OUT_DIR / "fv_avg90_strict_probability_monitor_latest.md"
REPORT_JSON = OUT_DIR / "fv_avg90_strict_probability_monitor_latest.json"
PROB_EPS = 1e-6
BOOK_PLATT_COEF = (-0.06557930502973691, 1.1086227109197666)
BOOK_V31_PLATT_COEF = (-0.06888340212382925, 1.1971919807365963, -0.09748120840669196)
BOOK_V32_PLATT_COEF = (-0.06895920440261558, 1.19822880025025, -0.09602925795977581)
BOOK_V33_PLATT_COEF = (-0.06891350396109047, 1.1979134871341677, -0.09537679154873029)
BOOK_V31_TIME_PLATT_COEF = (-0.004612015842067466, 1.1949037009646317, -0.09568923267788405, 0.10991831357346939)
REGISTRY_COLUMNS = [
    "opportunity_key",
    "market",
    "entry_dt",
    "close_time",
    "source_line_no",
    "strike",
    "seconds_to_close",
    "v28_live_surface_p_yes",
    "v28_live_surface_sigma_t_dollars",
    "v28_avg90_p_yes",
    "v28_avg90_sigma_t_dollars",
    "v30_avg90_exact_var_p_yes",
    "v30_avg90_exact_var_sigma_t_dollars",
    "v31_avg90_final60_exact_p_yes",
    "v31_avg90_final60_exact_sigma_t_dollars",
    "v32_avg110_final60_exact_p_yes",
    "v32_avg110_final60_exact_sigma_t_dollars",
    "v33_antipersist3_p_yes",
    "v33_antipersist3_sigma_t_dollars",
    "v34_material_antipersist3_p_yes",
    "v34_material_antipersist3_sigma_t_dollars",
    "v35_h150_t102_antipersist3_p_yes",
    "v35_h150_t102_antipersist3_sigma_t_dollars",
    "v36_piecewise_h150_t102_antipersist3_p_yes",
    "v36_piecewise_h150_t102_antipersist3_sigma_t_dollars",
    "v37_piecewise_dynamic_temp_antipersist3_p_yes",
    "v37_piecewise_dynamic_temp_antipersist3_sigma_t_dollars",
    "v38_long60_antipersist_p_yes",
    "v38_long60_antipersist_sigma_t_dollars",
    "v39_midband_v28_fallback_p_yes",
    "v39_midband_v28_fallback_sigma_t_dollars",
    "book_mid_probability_p_yes",
    "book_platt_p_yes",
    "book_v31_platt_p_yes",
    "book_v32_platt_p_yes",
    "book_v33_platt_p_yes",
    "book_v31_time_platt_p_yes",
    "registered_utc",
    "outcome",
    "resolved_utc",
]


def utc_now() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc))


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        number = float(value)
        return None if not math.isfinite(number) else number
    if isinstance(value, float):
        return None if not math.isfinite(value) else value
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def pct(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def logit_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
    return np.log(values / (1.0 - values))


def sigmoid_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").clip(-35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-values))


def load_or_create_lock(raw: pd.DataFrame) -> dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    source_line = pd.to_numeric(raw.get("source_line_no"), errors="coerce")
    lock = {
        "lock_id": "fv_avg90_strict_probability_lock_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": MODE,
        "bot_log": str(BOT_LOG),
        "initial_max_source_line_no": int(source_line.max()) if source_line.notna().any() else None,
        "initial_max_entry_dt": pd.to_datetime(raw.get("entry_dt"), utc=True, errors="coerce").max().isoformat()
        if "entry_dt" in raw
        else None,
        "candidate": "v28_avg90",
        "added_candidate": "v30_avg90_exact_var",
        "baseline": "v28_live_surface",
        "purpose": "Strict forward validation of settlement-average FV probability calibration.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def raw_mode_rows(markets: dict[str, dict[str, Any]], outcomes: dict[str, dict[str, Any]]) -> pd.DataFrame:
    raw = heartbeat_two_side_rows(markets, outcomes)
    if raw.empty:
        return raw
    frame = group_candidates(raw, MODE)
    close_rows = []
    for market, info in markets.items():
        close_rows.append(
            {
                "market": market,
                "close_time": pd.to_datetime(info.get("close_time"), utc=True, errors="coerce"),
            }
        )
    closes = pd.DataFrame(close_rows)
    frame = frame.merge(closes, on="market", how="left")
    return frame.sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


def build_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    engines = [
        EngineSpec(
            "v28_live_surface",
            FastMushroomFVEngineV28(FastMushroomV28Config()),
            "current v28 close-to-close FV surface",
        ),
        EngineSpec(
            "v28_avg90",
            FastMushroomFVEngineV28(FastMushroomV28Config(settlement_average_seconds=90.0)),
            "v28 with effective 90s settlement-average horizon",
        ),
        EngineSpec(
            "v30_avg90_exact_var",
            FastMushroomFVEngineV30(FastMushroomV30Config(settlement_average_seconds=90.0)),
            "v30 with exact Brownian variance inside a 90s settlement-average window",
        ),
        EngineSpec(
            "v31_avg90_final60_exact",
            FastMushroomFVEngineV31(
                FastMushroomV31Config(settlement_average_seconds=90.0, exact_average_inside_seconds=60.0)
            ),
            "v31 proxy-aware final-minute exact settlement-average variance",
        ),
        EngineSpec(
            "v32_avg110_final60_exact",
            FastMushroomFVEngineV32(
                FastMushroomV32Config(settlement_average_seconds=110.0, exact_average_inside_seconds=60.0)
            ),
            "v32 with 110s effective settlement/proxy horizon and final-minute exact variance",
        ),
        EngineSpec(
            "v33_antipersist3",
            FastMushroomFVEngineV33(
                FastMushroomV33Config(settlement_average_seconds=110.0, exact_average_inside_seconds=60.0)
            ),
            "v33 with time-damped 3m anti-persistence posterior",
        ),
        EngineSpec(
            "v34_material_antipersist3",
            FastMushroomFVEngineV34(
                FastMushroomV34Config(
                    settlement_average_seconds=110.0,
                    exact_average_inside_seconds=60.0,
                    anti_persistence_lag_minutes=3,
                    anti_persistence_velocity_weight=-0.50,
                    anti_persistence_time_damp_power=2.0,
                    anti_persistence_sigma_mult=1.00,
                    anti_persistence_max_logit_weight=0.10,
                    anti_persistence_shift_gate_center_dollars=40.0,
                    anti_persistence_shift_gate_width_dollars=5.0,
                    posterior_temperature=0.98,
                )
            ),
            "v34 materiality-gated 3m anti-persistence posterior",
        ),
        EngineSpec(
            "v35_h150_t102_antipersist3",
            FastMushroomFVEngineV35(FastMushroomV35Config()),
            "v35 longer proxy horizon with softer anti-persistence posterior",
        ),
        EngineSpec(
            "v36_piecewise_h150_t102_antipersist3",
            FastMushroomFVEngineV36(FastMushroomV36Config()),
            "v36 piecewise proxy horizon with softer anti-persistence posterior",
        ),
        EngineSpec(
            "v37_piecewise_dynamic_temp_antipersist3",
            FastMushroomFVEngineV37(FastMushroomV37Config()),
            "v37 piecewise proxy horizon with dynamic posterior temperature",
        ),
        EngineSpec(
            "v38_long60_antipersist",
            FastMushroomFVEngineV38(FastMushroomV38Config()),
            "v38 with v37 plus gated 60m long-memory anti-persistence",
        ),
        EngineSpec(
            "v39_midband_v28_fallback",
            FastMushroomFVEngineV39(FastMushroomV39Config()),
            "v39 with v38 plus v28 fallback in the 420-600s mid-market band",
        ),
    ]
    candles = load_candles()
    return replay_predictions(frame, candles, engines)


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists() or REGISTRY_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    try:
        rows = pd.read_csv(REGISTRY_PATH, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    for col in REGISTRY_COLUMNS:
        if col not in rows.columns:
            rows[col] = pd.NA
    for col in ["entry_dt", "close_time", "registered_utc", "resolved_utc"]:
        if col in rows.columns:
            rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    if "outcome" in rows.columns:
        rows["outcome"] = rows["outcome"].fillna("").astype(str)
    return rows[REGISTRY_COLUMNS]


def base_registry_rows(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    now = utc_now()
    yes_mid = (
        predictions[predictions["side"].astype(str).eq("yes")][["opportunity_key", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"book_mid_cents": "yes_mid_cents"})
    )
    no_mid = (
        predictions[predictions["side"].astype(str).eq("no")][["opportunity_key", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"book_mid_cents": "no_mid_cents"})
    )
    book = yes_mid.merge(no_mid, on="opportunity_key", how="outer")
    denom = pd.to_numeric(book["yes_mid_cents"], errors="coerce") + pd.to_numeric(book["no_mid_cents"], errors="coerce")
    book["book_mid_probability_p_yes"] = pd.to_numeric(book["yes_mid_cents"], errors="coerce") / denom

    rows = predictions.drop_duplicates("opportunity_key", keep="first").copy()
    rows = rows.merge(book[["opportunity_key", "book_mid_probability_p_yes"]], on="opportunity_key", how="left")
    book_logit = logit_series(rows["book_mid_probability_p_yes"])
    v31_logit = logit_series(rows["v31_avg90_final60_exact_p_yes"])
    v32_logit = logit_series(rows["v32_avg110_final60_exact_p_yes"])
    v33_logit = logit_series(rows["v33_antipersist3_p_yes"])
    rows["book_platt_p_yes"] = sigmoid_series(BOOK_PLATT_COEF[0] + BOOK_PLATT_COEF[1] * book_logit)
    rows["book_v31_platt_p_yes"] = sigmoid_series(
        BOOK_V31_PLATT_COEF[0] + BOOK_V31_PLATT_COEF[1] * book_logit + BOOK_V31_PLATT_COEF[2] * v31_logit
    )
    rows["book_v32_platt_p_yes"] = sigmoid_series(
        BOOK_V32_PLATT_COEF[0] + BOOK_V32_PLATT_COEF[1] * book_logit + BOOK_V32_PLATT_COEF[2] * v32_logit
    )
    rows["book_v33_platt_p_yes"] = sigmoid_series(
        BOOK_V33_PLATT_COEF[0] + BOOK_V33_PLATT_COEF[1] * book_logit + BOOK_V33_PLATT_COEF[2] * v33_logit
    )
    log_time = np.log(np.clip(pd.to_numeric(rows["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    rows["book_v31_time_platt_p_yes"] = sigmoid_series(
        BOOK_V31_TIME_PLATT_COEF[0]
        + BOOK_V31_TIME_PLATT_COEF[1] * book_logit
        + BOOK_V31_TIME_PLATT_COEF[2] * v31_logit
        + BOOK_V31_TIME_PLATT_COEF[3] * log_time
    )
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["close_time"] = pd.to_datetime(rows["close_time"], utc=True, errors="coerce")
    rows["source_line_no_num"] = pd.to_numeric(rows.get("source_line_no"), errors="coerce")
    initial_line = lock.get("initial_max_source_line_no")
    if initial_line is not None:
        rows = rows[rows["source_line_no_num"].gt(float(initial_line))].copy()
    initial_dt = pd.to_datetime(lock.get("initial_max_entry_dt"), utc=True, errors="coerce")
    if not pd.isna(initial_dt):
        rows = rows[rows["entry_dt"].gt(initial_dt)].copy()

    rows = rows[rows["close_time"].notna() & rows["close_time"].gt(now)].copy()
    if rows.empty:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    out = rows[
        [
            "opportunity_key",
            "market",
            "entry_dt",
            "close_time",
            "source_line_no",
            "strike",
            "seconds_to_close",
            "v28_live_surface_p_yes",
            "v28_live_surface_sigma_t_dollars",
            "v28_avg90_p_yes",
            "v28_avg90_sigma_t_dollars",
            "v30_avg90_exact_var_p_yes",
            "v30_avg90_exact_var_sigma_t_dollars",
            "v31_avg90_final60_exact_p_yes",
            "v31_avg90_final60_exact_sigma_t_dollars",
            "v32_avg110_final60_exact_p_yes",
            "v32_avg110_final60_exact_sigma_t_dollars",
            "v33_antipersist3_p_yes",
            "v33_antipersist3_sigma_t_dollars",
            "v34_material_antipersist3_p_yes",
            "v34_material_antipersist3_sigma_t_dollars",
            "v35_h150_t102_antipersist3_p_yes",
            "v35_h150_t102_antipersist3_sigma_t_dollars",
            "v36_piecewise_h150_t102_antipersist3_p_yes",
            "v36_piecewise_h150_t102_antipersist3_sigma_t_dollars",
            "v37_piecewise_dynamic_temp_antipersist3_p_yes",
            "v37_piecewise_dynamic_temp_antipersist3_sigma_t_dollars",
            "v38_long60_antipersist_p_yes",
            "v38_long60_antipersist_sigma_t_dollars",
            "v39_midband_v28_fallback_p_yes",
            "v39_midband_v28_fallback_sigma_t_dollars",
            "book_mid_probability_p_yes",
            "book_platt_p_yes",
            "book_v31_platt_p_yes",
            "book_v32_platt_p_yes",
            "book_v33_platt_p_yes",
            "book_v31_time_platt_p_yes",
        ]
    ].copy()
    out["registered_utc"] = now
    out["outcome"] = ""
    out["resolved_utc"] = pd.NaT
    return out


def update_outcomes(registry: pd.DataFrame, outcomes: dict[str, dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    if "outcome" in out.columns:
        out["outcome"] = out["outcome"].fillna("").astype(str)
    resolved_at = utc_now()
    for idx, row in out.iterrows():
        outcome = str(outcomes.get(str(row["market"]), {}).get("outcome") or "").lower()
        if outcome in {"yes", "no"} and str(row.get("outcome") or "").lower() not in {"yes", "no"}:
            out.at[idx, "outcome"] = outcome
            out.at[idx, "resolved_utc"] = resolved_at
    return out


def metrics(registry: pd.DataFrame, model: str) -> dict[str, Any]:
    if registry.empty or "outcome" not in registry.columns:
        return {
            "model": model,
            "resolved": 0,
            "brier": None,
            "logloss": None,
            "side_accuracy": None,
            "yes_rate": None,
            "mean_p_yes": None,
        }
    resolved = registry[registry["outcome"].astype(str).str.lower().isin(["yes", "no"])].copy()
    p = pd.to_numeric(resolved.get(f"{model}_p_yes"), errors="coerce").to_numpy(dtype=float)
    y = resolved["outcome"].astype(str).str.lower().eq("yes").astype(float).to_numpy()
    mask = np.isfinite(p)
    if not mask.any():
        return {
            "model": model,
            "resolved": 0,
            "brier": None,
            "logloss": None,
            "side_accuracy": None,
            "yes_rate": None,
            "mean_p_yes": None,
        }
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    y = y[mask]
    side_wins = ((p >= 0.5) == (y >= 0.5)).sum()
    return {
        "model": model,
        "resolved": int(len(y)),
        "brier": brier(y, p),
        "logloss": logloss(y, p),
        "side_accuracy": float(side_wins / len(y)),
        "yes_rate": float(y.mean()),
        "mean_p_yes": float(p.mean()),
    }


def write_report(lock: dict[str, Any], registry: pd.DataFrame, new_count: int, metric_rows: list[dict[str, Any]]) -> None:
    resolved = registry[registry["outcome"].astype(str).str.lower().isin(["yes", "no"])].copy() if not registry.empty else registry
    pending = len(registry) - len(resolved)
    lines = [
        "# FV avg90 Strict Probability Monitor",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Research-only strict forward registry for FV probability calibration.",
        "- New rows are registered only while their market close is still in the future.",
        "- Later FV candidates are only present on rows registered after those candidates were added.",
        "- No orders are submitted and no live bot code/process is touched.",
        "",
        "## Lock",
        "",
        f"- Created UTC: `{lock.get('created_utc')}`",
        f"- Initial max source line: `{lock.get('initial_max_source_line_no')}`",
        f"- Initial max entry: `{lock.get('initial_max_entry_dt')}`",
        "",
        "## Registry",
        "",
        f"- Total registered opportunities: {len(registry)}",
        f"- New opportunities this run: {new_count}",
        f"- Resolved / pending: {len(resolved)} / {pending}",
        "",
        "## Calibration",
        "",
        "| model | resolved | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metric_rows:
        lines.append(
            f"| `{row['model']}` | {row['resolved']} | "
            f"{row['brier'] if row['brier'] is not None else 'NA'} | "
            f"{row['logloss'] if row['logloss'] is not None else 'NA'} | "
            f"{pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    if len(resolved) < 30:
        lines += ["", "## Read", "", "- Too few resolved strict-forward rows for a model decision."]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes_all = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes_all)
    frame = raw_mode_rows(markets, outcomes)
    if frame.empty:
        raise SystemExit("No heartbeat rows found for avg90 strict probability monitor.")
    lock = load_or_create_lock(frame)
    predictions = build_predictions(frame)

    registry = load_registry()
    existing_keys = set(registry["opportunity_key"].astype(str)) if not registry.empty else set()
    new_rows = base_registry_rows(predictions, lock)
    if not new_rows.empty:
        new_rows = new_rows[~new_rows["opportunity_key"].astype(str).isin(existing_keys)].copy()
    if not new_rows.empty:
        if registry.empty:
            registry = new_rows.copy()
        else:
            concat_cols = [
                col
                for col in REGISTRY_COLUMNS
                if not (registry[col].isna().all() and new_rows[col].isna().all())
            ]
            registry = pd.concat(
                [registry[concat_cols].astype(object), new_rows[concat_cols].astype(object)],
                ignore_index=True,
                sort=False,
            ).reindex(columns=REGISTRY_COLUMNS)
    registry = update_outcomes(registry, outcomes)
    registry = registry.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True) if not registry.empty else registry
    registry.to_csv(REGISTRY_PATH, index=False)

    metric_rows = [
        metrics(registry, "v28_live_surface"),
        metrics(registry, "v28_avg90"),
        metrics(registry, "v30_avg90_exact_var"),
        metrics(registry, "v31_avg90_final60_exact"),
        metrics(registry, "v32_avg110_final60_exact"),
        metrics(registry, "v33_antipersist3"),
        metrics(registry, "v34_material_antipersist3"),
        metrics(registry, "v35_h150_t102_antipersist3"),
        metrics(registry, "v36_piecewise_h150_t102_antipersist3"),
        metrics(registry, "v37_piecewise_dynamic_temp_antipersist3"),
        metrics(registry, "v38_long60_antipersist"),
        metrics(registry, "v39_midband_v28_fallback"),
        metrics(registry, "book_mid_probability"),
        metrics(registry, "book_platt"),
        metrics(registry, "book_v31_platt"),
        metrics(registry, "book_v32_platt"),
        metrics(registry, "book_v33_platt"),
        metrics(registry, "book_v31_time_platt"),
    ]
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock": lock,
        "registry_path": str(REGISTRY_PATH),
        "registered": int(len(registry)),
        "new_rows": int(len(new_rows)),
        "metrics": metric_rows,
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(lock, registry, int(len(new_rows)), metric_rows)

    print("FV avg90 strict probability monitor complete")
    print(f"registered={len(registry)} new_rows={len(new_rows)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
