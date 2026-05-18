"""FV overlay validator on the target-coverage v28 entry surface.

Research-only; no live bot changes or orders.

Most FV overlay diagnostics use the broad raw-v28 p50 surface. That is useful
for calibration, but the active goal also requires trading roughly 75-80%+ of
new BTC 15m markets. This probe scores FV overlays on the current best
raw-entry coverage valve, so calibration is measured on the rows that are
closest to the intended trade surface.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Callable
from datetime import datetime, timezone

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_calibrated_probability import OVERLAYS
from probe_v28_raw_entry_coverage_valve import (
    STATE_JSON as COVERAGE_STATE_JSON,
    apply_turbulence_valve,
    apply_valve,
    selected_base_rows,
)
from probe_v28_exchange_result_enrichment import attach_exchange_results


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COVERAGE_VALVE_JSON = OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"
STATE_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_state.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0

DEFAULT_POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
OVERLAY_NAMES = [
    "raw_probability",
    "entry_conditioned_plus03_probability",
    "entry_conditioned_plus05_probability",
    "entry_conditioned_logit125_probability",
    "entry_conditioned_logit125_p60_only_probability",
    "danger_to_book_probability",
    "boundary_recross_shrink_probability",
    "noise_shrink_light_probability",
    "book_probability",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("policy") and payload.get("freeze_ts"):
            return payload
    coverage_payload = load_json(COVERAGE_VALVE_JSON)
    payload = {
        "freeze_ts": utc_now_iso(),
        "source_coverage_freeze_ts": load_json(COVERAGE_STATE_JSON).get("freeze_ts"),
        "entry_surface": "frozen_target_coverage_raw_entry_valve",
        "policy": coverage_payload.get("best_policy") or DEFAULT_POLICY,
        "overlay_names": OVERLAY_NAMES,
        "hypothesis": "Target-coverage FV validation must use a fixed coverage valve, not chase the current best row.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


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


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def danger_to_book_probability(row: dict[str, Any]) -> float:
    raw = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    book = as_float(row.get("ask_prob"))
    if book is None and row.get("ask_cents") is not None:
        book = as_float(row.get("ask_cents"))
        book = None if book is None else book / 100.0
    if raw is None:
        raise ValueError("missing raw probability")
    if book is None:
        return raw
    gap = raw - book
    # On broad target-coverage rows there is usually only one selected row per
    # market, so the portable danger signal is the large raw/book gap.
    if gap > 0.30:
        return book
    return raw


def boundary_recross_shrink_probability(row: dict[str, Any]) -> float:
    raw = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if raw is None:
        raise ValueError("missing raw probability")
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    if recross is None or abs_d is None:
        return raw
    shallow_high_recross = recross >= 0.55 and abs_d < 0.45
    thin_turbulent_touch = edge is not None and edge < 0.03 and recross >= 0.40
    if shallow_high_recross or thin_turbulent_touch:
        return clamp_prob(0.5 + 0.5 * (raw - 0.5))
    return raw


LOCAL_OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    **OVERLAYS,
    "danger_to_book_probability": danger_to_book_probability,
    "boundary_recross_shrink_probability": boundary_recross_shrink_probability,
}


def parse_policy(policy: str) -> dict[str, Any]:
    turbulence = re.search(r"edge(\d+)_p60_recross(\d+)_near(\d+)", policy)
    if turbulence:
        return {
            "kind": "turbulence",
            "edge": float(turbulence.group(1)) / 100.0,
            "recross": float(turbulence.group(2)) / 100.0,
            "near": float(turbulence.group(3)) / 100.0,
        }
    ladder = re.search(r"edge(\d+)_or_p60", policy)
    if ladder:
        return {
            "kind": "ladder",
            "edge": float(ladder.group(1)) / 100.0,
        }
    return {"kind": "turbulence", "edge": 0.04, "recross": 0.75, "near": 0.25}


def apply_policy(rows: list[dict[str, Any]], policy: str) -> list[dict[str, Any]]:
    parsed = parse_policy(policy)
    if parsed["kind"] == "ladder":
        return apply_valve(rows, float(parsed["edge"]))
    return apply_turbulence_valve(
        rows,
        min_edge_keep=float(parsed["edge"]),
        recross_floor=float(parsed["recross"]),
        near_abs_d=float(parsed["near"]),
    )


def score_overlay(rows: list[dict[str, Any]], denominator: int, name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        try:
            p = clamp_prob(float(fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "p": p,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
        })
    return {
        "overlay": name,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "avg_brier": avg([float(row["brier"]) for row in scored]),
        "avg_logloss": avg([float(row["logloss"]) for row in scored]),
        "avg_p": avg([float(row["p"]) for row in scored]),
        "win_rate": avg([float(row["outcome"]) for row in scored]),
        "net_cents_after_entry_fee": sum(float(row.get("net_cents") or 0.0) for row in scored),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def blockers(row: dict[str, Any], raw: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = int(as_float(row.get("settled")) or 0)
    coverage = as_float(row.get("coverage_pct"))
    brier_delta = as_float(row.get("brier_delta_vs_raw"))
    logloss_delta = as_float(row.get("logloss_delta_vs_raw"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if row.get("overlay") != "raw_probability":
        if brier_delta is None or brier_delta >= 0.0:
            out.append("brier_not_better_than_raw")
        if logloss_delta is None or logloss_delta >= 0.0:
            out.append("logloss_not_better_than_raw")
    return out


def enrich_ranked(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == "raw_probability"), {})
    raw_brier = as_float(raw.get("avg_brier"))
    raw_logloss = as_float(raw.get("avg_logloss"))
    ranked = []
    for row in scores:
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        enriched = {
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else loss - raw_logloss,
        }
        enriched["blockers"] = blockers(enriched, raw)
        ranked.append(enriched)
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return ranked


def detail_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_raw": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "coverage_valve_reason": row.get("coverage_valve_reason"),
        })
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    source_state = load_json(COVERAGE_STATE_JSON)
    freeze_dt = parse_ts(source_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    policy = state.get("policy") or DEFAULT_POLICY
    all_rows = selected_base_rows()
    target_rows = apply_policy(all_rows, str(policy))
    forward_rows = attach_exchange_results([row for row in target_rows if str(row.get("market") or "") in forward_markets])
    discovery_denominator = len({str(row.get("market") or "") for row in all_rows if row.get("market")})
    forward_denominator = len(forward_markets)
    overlay_names = state.get("overlay_names") if isinstance(state.get("overlay_names"), list) else OVERLAY_NAMES
    overlay_names = list(dict.fromkeys([*overlay_names, "boundary_recross_shrink_probability"]))
    discovery_scores = [
        score_overlay(target_rows, discovery_denominator, name, LOCAL_OVERLAYS[name])
        for name in overlay_names
        if name in LOCAL_OVERLAYS
    ]
    forward_scores = [
        score_overlay(forward_rows, forward_denominator, name, LOCAL_OVERLAYS[name])
        for name in overlay_names
        if name in LOCAL_OVERLAYS
    ]
    return {
        "entry_surface": state.get("entry_surface"),
        "policy": policy,
        "freeze_ts": state.get("freeze_ts"),
        "source_coverage_freeze_ts": state.get("source_coverage_freeze_ts"),
        "state_path": str(STATE_JSON),
        "forward_denominator": forward_denominator,
        "discovery_denominator": discovery_denominator,
        "forward": enrich_ranked(forward_scores),
        "discovery": enrich_ranked(discovery_scores),
        "forward_rows": detail_rows(forward_rows),
        "requirements": [
            "frozen target-coverage entry surface",
            "75-90% forward coverage",
            "at least 30 settled forward rows",
            "Brier and logloss better than raw on same selected rows",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Target-Coverage FV Overlay Validator",
        "",
        "Scores FV overlays on the current best raw-entry coverage valve, not the broad 100% raw-p50 surface.",
        "",
        f"- Entry surface: `{report.get('entry_surface')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
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
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('net_cents_after_entry_fee'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Discovery Context",
        "",
        "Not promotion evidence. Used only to see whether the target-coverage slice is directionally coherent.",
        "",
        "| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("discovery") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('net_cents_after_entry_fee'))} |"
        )
    lines.extend([
        "",
        "## Forward Rows",
        "",
        "| market | side | p raw | ask | edge | stc | abs d | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("forward_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee'))} | {row.get('coverage_valve_reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
