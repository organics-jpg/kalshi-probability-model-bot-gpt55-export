"""Pending forward-row sensitivity for v28 FV candidates.

Research-only; no live bot changes or orders.

For unresolved forward rows, this report asks:
    if the selected side wins or loses, which FV overlay benefits versus raw?

It prevents hindsight storytelling by writing the candidate impact before the
market settles.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_memory_fv_candidates import (
    OVERLAYS as BOUNDARY_OVERLAYS,
    selected_base_rows as boundary_selected_rows,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_reactivated_shadow_status import market_result
from probe_v28_reward_memory_fv_candidates import (
    OUT_JSON as REWARD_JSON,
    overlay_map as reward_overlay_map,
    selected_base_rows as reward_selected_rows,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BOUNDARY_STATE_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_state.json"
REWARD_STATE_JSON = OUT_DIR / "v28_reward_memory_fv_candidates_state.json"
OUT_JSON = OUT_DIR / "v28_pending_fv_sensitivity_latest.json"
OUT_MD = OUT_DIR / "v28_pending_fv_sensitivity_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def score_delta(p: float, raw_p: float, outcome: float) -> dict[str, float]:
    return {
        "brier_delta_vs_raw": (p - outcome) ** 2 - (raw_p - outcome) ** 2,
        "logloss_delta_vs_raw": logloss(p, outcome) - logloss(raw_p, outcome),
    }


def eval_overlays(
    row: dict[str, Any],
    overlays: dict[str, Callable[[dict[str, Any]], float]],
) -> list[dict[str, Any]]:
    raw_p = clamp_prob(float(overlays["raw_probability"](row)))
    out = []
    for name, fn in overlays.items():
        try:
            p = clamp_prob(float(fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        win = score_delta(p, raw_p, 1.0)
        lose = score_delta(p, raw_p, 0.0)
        out.append({
            "overlay": name,
            "p": p,
            "if_win_brier_delta_vs_raw": win["brier_delta_vs_raw"],
            "if_win_logloss_delta_vs_raw": win["logloss_delta_vs_raw"],
            "if_loss_brier_delta_vs_raw": lose["brier_delta_vs_raw"],
            "if_loss_logloss_delta_vs_raw": lose["logloss_delta_vs_raw"],
        })
    return sorted(out, key=lambda item: (item["if_win_brier_delta_vs_raw"], item["overlay"]))


def forward_pending_rows(state_path: Path, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state = load_json(state_path)
    freeze_ts = state.get("freeze_ts")
    if not freeze_ts:
        return []
    timing = market_timing(parse_ts(freeze_ts))
    forward = timing["clean_forward_markets"]
    return [
        row for row in rows
        if str(row.get("market") or "") in forward and row.get("side_won") is None
    ]


def row_identity(row: dict[str, Any], family: str) -> dict[str, Any]:
    market = str(row.get("market") or "")
    status, result = market_result(market)
    return {
        "family": family,
        "market": market,
        "status": status,
        "result": result,
        "side": row.get("side"),
        "p_raw": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close_at_selection": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "spectral_tag": row.get("spectral_tag"),
    }


def build_report() -> dict[str, Any]:
    reward_state = load_json(REWARD_STATE_JSON)
    boundary_pending = forward_pending_rows(BOUNDARY_STATE_JSON, boundary_selected_rows())
    reward_pending = forward_pending_rows(REWARD_STATE_JSON, reward_selected_rows())
    reward_overlays = reward_overlay_map(reward_state if reward_state else load_json(REWARD_JSON))
    rows = []
    seen: set[tuple[str, str]] = set()
    for family, pending, overlays in [
        ("boundary_memory", boundary_pending, BOUNDARY_OVERLAYS),
        ("reward_memory", reward_pending, reward_overlays),
    ]:
        for row in pending:
            key = (family, str(row.get("market") or ""))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                **row_identity(row, family),
                "overlay_sensitivity": eval_overlays(row, overlays),
            })
    return {
        "purpose": "Pre-settlement sensitivity for unresolved forward FV rows.",
        "pending_rows": len(rows),
        "rows": rows,
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
        "# v28 Pending FV Sensitivity",
        "",
        "Pre-settlement sensitivity for unresolved forward FV rows.",
        "",
        f"- Pending rows: `{report.get('pending_rows')}`",
        "",
    ]
    for row in report.get("rows") or []:
        lines.extend([
            f"## {row.get('family')} {row.get('market')}",
            "",
            f"- Market status/result: `{row.get('status')}` / `{row.get('result')}`",
            f"- Side/raw/ask/edge: `{row.get('side')}` / `{fmt(row.get('p_raw'))}` / `{fmt(row.get('ask_prob'))}` / `{fmt(row.get('raw_edge_prob'))}`",
            f"- Geometry: stc `{fmt(row.get('seconds_to_close_at_selection'))}`, abs_d `{fmt(row.get('abs_d_sigma'))}`, recross `{fmt(row.get('recross_hazard_score'))}`, spectral `{row.get('spectral_tag')}`",
            "",
            "| overlay | p | if selected wins brier d | if selected wins logloss d | if selected loses brier d | if selected loses logloss d |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for item in row.get("overlay_sensitivity") or []:
            lines.append(
                f"| {item.get('overlay')} | {fmt(item.get('p'))} | "
                f"{fmt(item.get('if_win_brier_delta_vs_raw'))} | {fmt(item.get('if_win_logloss_delta_vs_raw'))} | "
                f"{fmt(item.get('if_loss_brier_delta_vs_raw'))} | {fmt(item.get('if_loss_logloss_delta_vs_raw'))} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
