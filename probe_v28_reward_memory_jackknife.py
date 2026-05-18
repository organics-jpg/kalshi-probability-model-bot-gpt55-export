"""Jackknife robustness for reward-memory FV controllers.

Research-only; no live bot changes or orders.

The reward-memory probe freezes tiny retention controllers. This script checks
whether their discovery-slice calibration advantage survives leave-one-market-
out stress. It is not promotion evidence; it is an anti-overfit diagnostic.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_reward_memory_fv_candidates import (
    OUT_JSON as REWARD_JSON,
    overlay_map,
    rank_scores,
    score_rows,
    selected_base_rows,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_reward_memory_jackknife_latest.json"
OUT_MD = OUT_DIR / "v28_reward_memory_jackknife_latest.md"

WATCH_OVERLAYS = [
    "plus05_probability",
    "logit125_probability",
    "reward_memory_plus05",
    "reward_memory_logit125",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def score_subset(rows: list[dict[str, Any]], overlays: dict[str, Callable[[dict[str, Any]], float]]) -> list[dict[str, Any]]:
    denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    return rank_scores([score_rows(rows, name, fn, denominator) for name, fn in overlays.items()])


def by_overlay(scores: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("overlay") or ""): row for row in scores}


def build_report() -> dict[str, Any]:
    reward = load_json(REWARD_JSON)
    rows = selected_base_rows()
    settled = [row for row in rows if row.get("side_won") is not None]
    overlays = overlay_map(reward)
    full_scores = score_subset(settled, overlays)
    full_by_overlay = by_overlay(full_scores)
    markets = sorted({str(row.get("market") or "") for row in settled})
    jackknife = []
    for market in markets:
        kept = [row for row in settled if str(row.get("market") or "") != market]
        removed = [row for row in settled if str(row.get("market") or "") == market]
        scores = by_overlay(score_subset(kept, overlays))
        item = {
            "removed_market": market,
            "removed_rows": len(removed),
            "removed_wins": sum(1 for row in removed if row.get("side_won") is True),
            "removed_losses": sum(1 for row in removed if row.get("side_won") is False),
            "removed_net_cents": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in removed),
            "kept_count": len(kept),
            "overlays": {},
        }
        for name in WATCH_OVERLAYS:
            row = scores.get(name) or {}
            item["overlays"][name] = {
                "brier_delta_vs_raw": row.get("brier_delta_vs_raw"),
                "logloss_delta_vs_raw": row.get("logloss_delta_vs_raw"),
                "avg_brier": row.get("avg_brier"),
                "avg_logloss": row.get("avg_logloss"),
            }
        jackknife.append(item)
    robustness = []
    for name in WATCH_OVERLAYS:
        deltas = [
            item.get("overlays", {}).get(name, {}).get("brier_delta_vs_raw")
            for item in jackknife
        ]
        deltas = [float(value) for value in deltas if value is not None]
        loss_deltas = [
            item.get("overlays", {}).get(name, {}).get("logloss_delta_vs_raw")
            for item in jackknife
        ]
        loss_deltas = [float(value) for value in loss_deltas if value is not None]
        failures = [
            item for item in jackknife
            if item.get("overlays", {}).get(name, {}).get("brier_delta_vs_raw") is None
            or float(item["overlays"][name]["brier_delta_vs_raw"]) >= 0.0
        ]
        robustness.append({
            "overlay": name,
            "full_brier_delta_vs_raw": (full_by_overlay.get(name) or {}).get("brier_delta_vs_raw"),
            "full_logloss_delta_vs_raw": (full_by_overlay.get(name) or {}).get("logloss_delta_vs_raw"),
            "jackknife_count": len(deltas),
            "failure_count": len(failures),
            "pass": len(failures) == 0,
            "worst_brier_delta_vs_raw": max(deltas) if deltas else None,
            "best_brier_delta_vs_raw": min(deltas) if deltas else None,
            "worst_logloss_delta_vs_raw": max(loss_deltas) if loss_deltas else None,
            "best_logloss_delta_vs_raw": min(loss_deltas) if loss_deltas else None,
            "failure_markets": [item.get("removed_market") for item in failures],
        })
    robustness.sort(key=lambda row: (row["failure_count"], float(row.get("worst_brier_delta_vs_raw") or 999.0)))
    return {
        "source_reward_report": str(REWARD_JSON),
        "freeze_ts": reward.get("freeze_ts"),
        "selected_entries": len(rows),
        "settled_entries": len(settled),
        "markets": len(markets),
        "full_scores": full_scores,
        "robustness": robustness,
        "jackknife": jackknife,
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
        "# v28 Reward-Memory Jackknife",
        "",
        "Leave-one-market-out anti-overfit check for reward-memory FV controllers.",
        "",
        f"- Reward freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Selected/settled/markets: `{report.get('selected_entries')}/{report.get('settled_entries')}/{report.get('markets')}`",
        "",
        "## Robustness",
        "",
        "| overlay | pass | failures | full brier d | worst brier d | best brier d | full logloss d | worst logloss d |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("robustness") or []:
        lines.append(
            f"| {row.get('overlay')} | {row.get('pass')} | {row.get('failure_count')} | "
            f"{fmt(row.get('full_brier_delta_vs_raw'))} | {fmt(row.get('worst_brier_delta_vs_raw'))} | "
            f"{fmt(row.get('best_brier_delta_vs_raw'))} | {fmt(row.get('full_logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('worst_logloss_delta_vs_raw'))} |"
        )
    lines.extend([
        "",
        "## Worst Removals",
        "",
        "| overlay | removed market | removed W/L | removed net c | brier d | logloss d |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for robust in report.get("robustness") or []:
        name = robust.get("overlay")
        rows = []
        for item in report.get("jackknife") or []:
            score = (item.get("overlays") or {}).get(name) or {}
            rows.append({**item, **score})
        rows.sort(key=lambda row: float(row.get("brier_delta_vs_raw") if row.get("brier_delta_vs_raw") is not None else 999.0), reverse=True)
        for row in rows[:3]:
            lines.append(
                f"| {name} | {row.get('removed_market')} | {row.get('removed_wins')}/{row.get('removed_losses')} | "
                f"{fmt(row.get('removed_net_cents'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
                f"{fmt(row.get('logloss_delta_vs_raw'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
