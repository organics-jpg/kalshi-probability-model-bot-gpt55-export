"""Frozen forward validator for reward-calibrated FV memory controllers.

Research-only; no live bot changes or orders.

This is the constrained version of a reward model:
- fixed entry selection: raw v28 p50 edge0;
- no side flips and no new market selection;
- the model can only choose a retention value in [0, 1];
- adjusted FV = raw FV + retention * (candidate FV - raw FV);
- coefficients are frozen on first run and future rows validate out of sample.

The "reward" is calibration loss on settled discovery rows, with regularization
and simple physics features. This intentionally avoids a free-form P&L optimizer
because small BTC 15m samples can overfit beautifully and betray us live.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_state.json"
OUT_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_reward_memory_fv_candidates_latest.md"

MIN_SETTLED = 30
L2_PENALTY = 0.003


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def sigmoid(value: float) -> float:
    if value >= 40.0:
        return 1.0
    if value <= -40.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))


def logit_sharpen(p: float, scale: float) -> float:
    p = clamp_prob(p)
    logit = math.log(p / (1.0 - p))
    return clamp_prob(sigmoid(scale * logit))


def logloss(p: float, y: float) -> float:
    p = clamp_prob(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def raw_edge(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side") or row.get("p_eff"))
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def selected_base_rows() -> list[dict[str, Any]]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    return [{**row, "raw_edge_prob": raw_edge(row)} for row in picked]


def feature_vector(row: dict[str, Any]) -> dict[str, float]:
    p = p_raw(row)
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    spectral = str(row.get("spectral_tag") or "")
    return {
        "bias": 1.0,
        "raw_strength": max(0.0, min(1.0, (p - 0.50) / 0.35)),
        "edge_strength": max(0.0, min(1.0, (edge or 0.0) / 0.12)),
        "weak_raw": 1.0 if p < 0.60 else 0.0,
        "thin_edge": 1.0 if edge is not None and edge < 0.04 else 0.0,
        "near_strike": 1.0 if abs_d <= 0.25 else 0.0,
        "high_recross": 1.0 if recross >= 0.75 else 0.0,
        "turbulent_boundary": 1.0 if p < 0.60 and edge is not None and edge < 0.04 and abs_d <= 0.25 and recross >= 0.75 else 0.0,
        "spectral_noise": 1.0 if spectral == "spectral_noise" else 0.0,
        "spectral_dominant_weak": 1.0 if spectral == "spectral_dominant_factor" and p < 0.60 else 0.0,
    }


FEATURES = [
    "bias",
    "raw_strength",
    "edge_strength",
    "weak_raw",
    "thin_edge",
    "near_strike",
    "high_recross",
    "turbulent_boundary",
    "spectral_noise",
    "spectral_dominant_weak",
]


def retention(row: dict[str, Any], weights: dict[str, float]) -> float:
    features = feature_vector(row)
    score = sum(float(weights.get(name, 0.0)) * features[name] for name in FEATURES)
    return max(0.0, min(1.0, sigmoid(score)))


def p_plus05(row: dict[str, Any]) -> float:
    return clamp_prob(p_raw(row) + 0.05)


def p_logit125(row: dict[str, Any]) -> float:
    return logit_sharpen(p_raw(row), 1.25)


def p_reward(row: dict[str, Any], weights: dict[str, float], candidate_fn: Callable[[dict[str, Any]], float]) -> float:
    raw = p_raw(row)
    candidate = candidate_fn(row)
    return clamp_prob(raw + retention(row, weights) * (candidate - raw))


def row_loss(row: dict[str, Any], p: float) -> float:
    y = 1.0 if row.get("side_won") is True else 0.0
    brier = (p - y) ** 2
    return logloss(p, y) + 0.50 * brier


def objective(rows: list[dict[str, Any]], weights: dict[str, float], candidate_fn: Callable[[dict[str, Any]], float]) -> float:
    settled = [row for row in rows if row.get("side_won") is not None]
    if not settled:
        return 999.0
    losses = [row_loss(row, p_reward(row, weights, candidate_fn)) for row in settled]
    l2 = sum(value * value for key, value in weights.items() if key != "bias")
    return (sum(losses) / len(losses)) + L2_PENALTY * l2


def candidate_weight_grid() -> list[dict[str, float]]:
    grids = {
        "bias": [-2.0, -1.0, 0.0, 1.0],
        "raw_strength": [0.0, 1.0, 2.0],
        "edge_strength": [0.0, 0.75, 1.5],
        "weak_raw": [-2.0, -1.0, 0.0],
        "thin_edge": [-1.0, -0.5, 0.0],
        "near_strike": [-1.0, -0.5, 0.0],
        "high_recross": [-1.0, -0.5, 0.0],
        "turbulent_boundary": [-2.0, -1.0, 0.0],
        "spectral_noise": [-0.5, 0.0],
        "spectral_dominant_weak": [-0.5, 0.0],
    }
    names = list(grids)
    out = []
    for values in product(*(grids[name] for name in names)):
        out.append(dict(zip(names, values)))
    return out


def train_weights(rows: list[dict[str, Any]], candidate_fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    best_weights: dict[str, float] | None = None
    best_score = 999.0
    for weights in candidate_weight_grid():
        score = objective(settled, weights, candidate_fn)
        if score < best_score:
            best_score = score
            best_weights = weights
    return {
        "weights": best_weights or {name: 0.0 for name in FEATURES},
        "objective": best_score,
        "training_settled_rows": len(settled),
        "candidate_name": "plus05" if candidate_fn is p_plus05 else "logit125",
    }


def load_or_create_state(discovery_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts") and payload.get("controllers"):
            return payload
    controllers = {
        "reward_memory_plus05": train_weights(discovery_rows, p_plus05),
        "reward_memory_logit125": train_weights(discovery_rows, p_logit125),
    }
    payload = {
        "freeze_ts": utc_now_iso(),
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "hypothesis": "A tiny reward-calibrated controller can learn how much FV adjustment to retain without changing entry selection.",
        "features": FEATURES,
        "l2_penalty": L2_PENALTY,
        "controllers": controllers,
        "promotion_floor": {
            "min_settled": MIN_SETTLED,
            "must_improve_brier_vs_raw": True,
            "must_improve_logloss_vs_raw": True,
            "must_not_change_entry_selection": True,
            "must_validate_only_post_freeze": True,
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def overlay_map(state: dict[str, Any]) -> dict[str, Callable[[dict[str, Any]], float]]:
    plus_weights = ((state.get("controllers") or {}).get("reward_memory_plus05") or {}).get("weights") or {}
    logit_weights = ((state.get("controllers") or {}).get("reward_memory_logit125") or {}).get("weights") or {}
    return {
        "raw_probability": p_raw,
        "plus05_probability": p_plus05,
        "logit125_probability": p_logit125,
        "reward_memory_plus05": lambda row: p_reward(row, plus_weights, p_plus05),
        "reward_memory_logit125": lambda row: p_reward(row, logit_weights, p_logit125),
    }


def score_rows(rows: list[dict[str, Any]], overlay: str, fn: Callable[[dict[str, Any]], float], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        p = clamp_prob(float(fn(row)))
        y = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "p": p,
            "outcome": y,
            "brier": (p - y) ** 2,
            "logloss": logloss(p, y),
        })
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "overlay": overlay,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "avg_brier": avg([float(row["brier"]) for row in scored]),
        "avg_logloss": avg([float(row["logloss"]) for row in scored]),
        "avg_p": avg([float(row["p"]) for row in scored]),
        "win_rate": avg([float(row["outcome"]) for row in scored]),
        "net_cents_after_entry_fee": net,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def rank_scores(scores: list[dict[str, Any]], raw_name: str = "raw_probability") -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == raw_name), {})
    raw_brier = as_float(raw.get("avg_brier"))
    raw_logloss = as_float(raw.get("avg_logloss"))
    ranked = []
    for row in scores:
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        blockers = []
        if int(as_float(row.get("settled")) or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if row.get("overlay") != raw_name:
            if brier is None or raw_brier is None or brier >= raw_brier:
                blockers.append("brier_not_better_than_raw")
            if loss is None or raw_logloss is None or loss >= raw_logloss:
                blockers.append("logloss_not_better_than_raw")
        ranked.append({
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else loss - raw_logloss,
            "blockers": blockers,
        })
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return ranked


def retention_summary(rows: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    controllers = state.get("controllers") or {}
    for name, payload in controllers.items():
        weights = payload.get("weights") or {}
        values = [retention(row, weights) for row in rows]
        out.append({
            "controller": name,
            "avg_retention": avg(values),
            "min_retention": min(values) if values else None,
            "max_retention": max(values) if values else None,
            "training_objective": payload.get("objective"),
            "training_settled_rows": payload.get("training_settled_rows"),
            "weights": weights,
        })
    return out


def detail_rows(rows: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    controllers = state.get("controllers") or {}
    plus_weights = (controllers.get("reward_memory_plus05") or {}).get("weights") or {}
    logit_weights = (controllers.get("reward_memory_logit125") or {}).get("weights") or {}
    return [
        {
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "p_raw": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "spectral_tag": row.get("spectral_tag"),
            "retention_plus05": retention(row, plus_weights),
            "retention_logit125": retention(row, logit_weights),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
        }
        for row in rows
    ]


def build_report() -> dict[str, Any]:
    rows = selected_base_rows()
    state = load_or_create_state(rows)
    freeze_dt = parse_ts(state["freeze_ts"])
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    forward_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    discovery_denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    forward_denominator = len(forward_markets)
    overlays = overlay_map(state)
    discovery_scores = [score_rows(rows, name, fn, discovery_denominator) for name, fn in overlays.items()]
    forward_scores = [score_rows(forward_rows, name, fn, forward_denominator) for name, fn in overlays.items()]
    return {
        "freeze_ts": state.get("freeze_ts"),
        "hypothesis": state.get("hypothesis"),
        "entry_policy": state.get("entry_policy"),
        "features": state.get("features"),
        "l2_penalty": state.get("l2_penalty"),
        "controllers": state.get("controllers"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "discovery": rank_scores(discovery_scores),
        "forward": rank_scores(forward_scores),
        "discovery_retention": retention_summary(rows, state),
        "forward_retention": retention_summary(forward_rows, state),
        "forward_rows": detail_rows(forward_rows, state),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Reward-Memory FV Candidates",
        "",
        "Frozen forward validator for a constrained reward-calibrated FV memory controller.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Hypothesis: {report.get('hypothesis')}",
        "",
        "## Forward Ranking",
        "",
        "| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(report.get("forward") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Discovery Context",
        "",
        "Not promotion evidence. Coefficients were frozen from this slice; only post-freeze rows count for validation.",
        "",
        "| rank | overlay | entries | settled | W/L | brier | d brier | logloss | d logloss | avg p | win rate | net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("discovery") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('net_cents_after_entry_fee'))} |"
        )
    lines.extend(["", "## Frozen Controllers", ""])
    for row in report.get("discovery_retention") or []:
        lines.append(
            f"- `{row.get('controller')}`: training rows `{row.get('training_settled_rows')}`, "
            f"objective `{fmt(row.get('training_objective'))}`, avg retention `{fmt(row.get('avg_retention'))}`, "
            f"min/max `{fmt(row.get('min_retention'))}/{fmt(row.get('max_retention'))}`, weights `{row.get('weights')}`"
        )
    lines.extend([
        "",
        "## Forward Rows",
        "",
        "| market | side | p raw | ask | edge | stc | abs d | recross | spectral | retain +5 | retain logit | won | net c |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|",
    ])
    for row in report.get("forward_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('spectral_tag')} | "
            f"{fmt(row.get('retention_plus05'))} | {fmt(row.get('retention_logit125'))} | "
            f"{row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
