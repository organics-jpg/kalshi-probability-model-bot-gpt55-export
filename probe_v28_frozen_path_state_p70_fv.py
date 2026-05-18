"""Frozen path/state p70 FV challenger for target-coverage rows.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A high raw p-side is not automatically high tradable certainty. If the
    executable edge is thin and geometry is only mid-range, the row has low
    confirmation energy: it may be a stale/static snapshot that should not be
    sharpened unless the later path confirms it. Strong book discount or deep
    geometry earns sharpening; thin mid-geometry p70 rows keep raw probability.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_path_state_p70_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_path_state_p70_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_path_state_p70_fv_latest.md"

MIN_SETTLED = 30
BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 286003
SHARPEN_SCALE = 1.25
MIN_SHARPEN_P = 0.70
STRONG_EDGE = 0.04
THIN_EDGE = 0.02
DEEP_ABS_D = 0.90
MID_GEOMETRY_MAX_ABS_D = 0.75


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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_policy": DEFAULT_POLICY,
        "variant": "path_state_guarded_p70_logit125",
        "source_artifact": "v28_live_collapse_reentry_registry_latest.json",
        "rule": (
            "raw p<0.70 stays raw; raw p>=0.70 sharpens only when raw_edge>=4pp "
            "or abs_d>=0.90; raw p>=0.70 with raw_edge<2pp and abs_d<0.75 is "
            "explicitly treated as low-confirmation and kept raw."
        ),
        "physics": (
            "Probability confidence needs path confirmation energy. Thin book edge "
            "near mid geometry can be a stale snapshot; deep geometry or meaningful "
            "discount is more likely to represent a physically durable state."
        ),
        "parameters": {
            "sharpen_scale": SHARPEN_SCALE,
            "min_sharpen_p": MIN_SHARPEN_P,
            "strong_edge": STRONG_EDGE,
            "thin_edge": THIN_EDGE,
            "deep_abs_d": DEEP_ABS_D,
            "mid_geometry_max_abs_d": MID_GEOMETRY_MAX_ABS_D,
        },
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def logit(p: float) -> float:
    p = clamp_prob(p)
    return math.log(p / (1.0 - p))


def inv_logit(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def sharpen(p: float, scale: float = SHARPEN_SCALE) -> float:
    return clamp_prob(inv_logit(scale * logit(p)))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_probability(row: dict[str, Any]) -> float:
    p = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if p is None:
        raise ValueError("missing p_side")
    return clamp_prob(p)


def raw_edge(row: dict[str, Any]) -> float | None:
    edge = as_float(row.get("raw_edge_prob"))
    if edge is not None:
        return edge
    p = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def path_state_action(row: dict[str, Any]) -> str:
    p = raw_probability(row)
    edge = raw_edge(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    if p < MIN_SHARPEN_P:
        return "raw_below_p70"
    if edge is not None and edge < THIN_EDGE and abs_d is not None and abs_d < MID_GEOMETRY_MAX_ABS_D:
        return "keep_raw_low_confirmation_thin_mid_geometry"
    if edge is not None and edge >= STRONG_EDGE:
        return "sharpen_strong_book_discount"
    if abs_d is not None and abs_d >= DEEP_ABS_D:
        return "sharpen_deep_geometry"
    return "keep_raw_unearned_confirmation"


def path_state_probability(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    action = path_state_action(row)
    return sharpen(p) if action.startswith("sharpen") else p


def hard_p70_probability(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    return sharpen(p) if p >= MIN_SHARPEN_P else p


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(values: list[float], seed_offset: int = 0) -> dict[str, Any]:
    if len(values) < 5:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + seed_offset + len(values))
    samples = []
    for _ in range(BOOTSTRAP_RUNS):
        samples.append(sum(rng.choice(values) for _ in values) / len(values))
    samples.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "p05": percentile(samples, 0.05),
        "p50": percentile(samples, 0.50),
        "p95": percentile(samples, 0.95),
        "prob_negative": sum(1 for value in samples if value < 0.0) / len(samples),
    }


def score_variant(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        p_raw = raw_probability(row)
        p_var = clamp_prob(fn(row))
        y = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "p_raw": p_raw,
            "p_variant": p_var,
            "action": path_state_action(row) if name == "path_state_guarded_p70_logit125" else name,
            "raw_edge_prob": raw_edge(row),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "adjusted": abs(p_var - p_raw) > 1e-9,
            "brier_delta": (p_var - y) ** 2 - (p_raw - y) ** 2,
            "logloss_delta": logloss(p_var, y) - logloss(p_raw, y),
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    bboot = bootstrap(briers, 17)
    lboot = bootstrap(losses, 31)
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if name != "raw_probability":
        if not briers or sum(briers) / len(briers) >= 0.0:
            blockers.append("mean_brier_not_better")
        if bboot.get("p95") is None or float(bboot["p95"]) >= 0.0:
            blockers.append("brier_interval_not_strictly_negative")
        if not losses or sum(losses) / len(losses) >= 0.0:
            blockers.append("mean_logloss_not_better")
        if lboot.get("p95") is None or float(lboot["p95"]) >= 0.0:
            blockers.append("logloss_interval_not_strictly_negative")
    return {
        "variant": name,
        "rows": len(scored),
        "adjusted_rows": sum(1 for row in scored if row.get("adjusted")),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "net_cents": sum(float(row.get("net_cents") or 0.0) for row in scored),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_bootstrap": bboot,
        "logloss_bootstrap": lboot,
        "blockers": blockers,
        "rows_detail": scored,
    }


def action_rollups(rows_detail: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for action in sorted({str(row.get("action") or "") for row in rows_detail}):
        bucket = [row for row in rows_detail if row.get("action") == action]
        out.append({
            "action": action,
            "rows": len(bucket),
            "adjusted": sum(1 for row in bucket if row.get("adjusted")),
            "wins": sum(1 for row in bucket if row.get("won") is True),
            "losses": sum(1 for row in bucket if row.get("won") is False),
            "brier_delta": sum(float(row.get("brier_delta") or 0.0) for row in bucket),
            "logloss_delta": sum(float(row.get("logloss_delta") or 0.0) for row in bucket),
            "net_cents": sum(float(row.get("net_cents") or 0.0) for row in bucket),
        })
    out.sort(key=lambda row: (-int(row.get("rows") or 0), str(row.get("action"))))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows = apply_policy(selected_base_rows(), str(state.get("entry_policy") or DEFAULT_POLICY))
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    future_markets = timing["clean_forward_markets"]
    future_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    diagnostic_rows = [row for row in all_rows if str(row.get("market") or "") not in future_markets]
    ranked = [
        score_variant(future_rows, "raw_probability", raw_probability),
        score_variant(future_rows, "hard_p70_logit125", hard_p70_probability),
        score_variant(future_rows, str(state.get("variant")), path_state_probability),
    ]
    ranked.sort(key=lambda row: (
        row.get("variant") == "raw_probability",
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
    ))
    diagnostic = score_variant(diagnostic_rows, str(state.get("variant")), path_state_probability)
    path_row = next((row for row in ranked if row.get("variant") == state.get("variant")), {})
    return {
        "freeze": state,
        "future_denominator": len(future_markets),
        "future_entries": len(future_rows),
        "future_settled": sum(1 for row in future_rows if row.get("side_won") is not None),
        "future_coverage_pct": 100.0 * len(future_rows) / len(future_markets) if future_markets else None,
        "ranked": ranked,
        "path_state_action_rollups": action_rollups(path_row.get("rows_detail") or []),
        "diagnostic_prefreeze": {
            "entries": len(diagnostic_rows),
            "settled": diagnostic.get("rows"),
            "brier_mean_delta": diagnostic.get("brier_mean_delta"),
            "logloss_mean_delta": diagnostic.get("logloss_mean_delta"),
            "action_rollups": action_rollups(diagnostic.get("rows_detail") or []),
        },
        "interpretation": current_read(ranked, diagnostic, future_rows, future_markets),
    }


def current_read(
    ranked: list[dict[str, Any]],
    diagnostic: dict[str, Any],
    future_rows: list[dict[str, Any]],
    future_markets: set[str],
) -> list[str]:
    best = ranked[0] if ranked else {}
    return [
        f"Future rows are frozen from this script's timestamp: {len(future_rows)} entries over {len(future_markets)} markets.",
        f"Best future variant is {best.get('variant')} with Brier/logloss deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}.",
        f"Pre-freeze diagnostic path-state Brier/logloss deltas are {diagnostic.get('brier_mean_delta')}/{diagnostic.get('logloss_mean_delta')}; this is not promotion evidence.",
        "Use this as a path/state confirmation monitor, not a live rule, until it earns forward sample size.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Path-State p70 FV",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Entry policy: `{(report.get('freeze') or {}).get('entry_policy')}`",
        f"- Variant: `{(report.get('freeze') or {}).get('variant')}`",
        f"- Future entries/settled/denominator: `{report.get('future_entries')}/{report.get('future_settled')}/{report.get('future_denominator')}`",
        f"- Future coverage: `{fmt(report.get('future_coverage_pct'))}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        bboot = row.get("brier_bootstrap") or {}
        lboot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(bboot.get('p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(lboot.get('p95'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Future Action Rollups",
        "",
        "| action | rows | adjusted | W/L | brier d sum | logloss d sum | net c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("path_state_action_rollups") or []:
        lines.append(
            f"| {row.get('action')} | {row.get('rows')} | {row.get('adjusted')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('brier_delta'))} | "
            f"{fmt(row.get('logloss_delta'))} | {fmt(row.get('net_cents'))} |"
        )
    diagnostic = report.get("diagnostic_prefreeze") or {}
    lines.extend([
        "",
        "## Pre-Freeze Diagnostic",
        "",
        f"- Entries/settled: `{diagnostic.get('entries')}/{diagnostic.get('settled')}`",
        f"- Brier/logloss mean delta: `{fmt(diagnostic.get('brier_mean_delta'))}/{fmt(diagnostic.get('logloss_mean_delta'))}`",
        "",
        "| action | rows | adjusted | W/L | brier d sum | logloss d sum | net c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in diagnostic.get("action_rollups") or []:
        lines.append(
            f"| {row.get('action')} | {row.get('rows')} | {row.get('adjusted')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('brier_delta'))} | "
            f"{fmt(row.get('logloss_delta'))} | {fmt(row.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
