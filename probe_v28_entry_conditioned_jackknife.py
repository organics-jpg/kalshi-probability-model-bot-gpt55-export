"""Jackknife robustness for the entry-conditioned FV posterior.

Fixed selection: raw v28 p50 edge0.
Question: does the +5pp FV calibration improvement survive when each market is
removed one at a time, or is it carried by one lucky market?

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS, score_overlay
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_entry_conditioned_jackknife_latest.json"
OUT_MD = OUT_DIR / "v28_entry_conditioned_jackknife_latest.md"


def compact_score(rows: list[dict[str, Any]], overlay: str) -> dict[str, Any]:
    score = score_overlay(rows, overlay, OVERLAYS[overlay])
    return {key: value for key, value in score.items() if key not in {"buckets", "scored_rows"}}


def delta_score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw = compact_score(rows, "raw_probability")
    plus05 = compact_score(rows, "entry_conditioned_plus05_probability")
    return {
        "count": raw.get("count"),
        "raw_brier": raw.get("avg_brier"),
        "plus05_brier": plus05.get("avg_brier"),
        "brier_delta_vs_raw": None if raw.get("avg_brier") is None or plus05.get("avg_brier") is None else float(plus05["avg_brier"]) - float(raw["avg_brier"]),
        "raw_logloss": raw.get("avg_logloss"),
        "plus05_logloss": plus05.get("avg_logloss"),
        "logloss_delta_vs_raw": None if raw.get("avg_logloss") is None or plus05.get("avg_logloss") is None else float(plus05["avg_logloss"]) - float(raw["avg_logloss"]),
        "raw_ece": raw.get("ece_10bucket"),
        "plus05_ece": plus05.get("ece_10bucket"),
        "ece_delta_vs_raw": None if raw.get("ece_10bucket") is None or plus05.get("ece_10bucket") is None else float(plus05["ece_10bucket"]) - float(raw["ece_10bucket"]),
    }


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    settled = [row for row in picked if row.get("side_won") is not None]
    full = delta_score(settled)
    markets = sorted({str(row.get("market") or "") for row in settled})
    jackknife = []
    for market in markets:
        kept = [row for row in settled if str(row.get("market") or "") != market]
        removed = [row for row in settled if str(row.get("market") or "") == market]
        score = delta_score(kept)
        jackknife.append({
            "removed_market": market,
            "removed_rows": len(removed),
            "removed_wins": sum(1 for row in removed if row.get("side_won") is True),
            "removed_losses": sum(1 for row in removed if row.get("side_won") is False),
            "removed_net_cents": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in removed),
            **score,
        })
    failures = [
        row for row in jackknife
        if row.get("brier_delta_vs_raw") is None or float(row["brier_delta_vs_raw"]) >= 0.0
    ]
    worst = sorted(
        jackknife,
        key=lambda row: float(row.get("brier_delta_vs_raw") if row.get("brier_delta_vs_raw") is not None else 999.0),
        reverse=True,
    )[:5]
    best = sorted(
        jackknife,
        key=lambda row: float(row.get("brier_delta_vs_raw") if row.get("brier_delta_vs_raw") is not None else 999.0),
    )[:5]
    return {
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "candidate": "entry_conditioned_plus05_probability",
        "selected_entries": len(picked),
        "settled_entries": len(settled),
        "markets": len(markets),
        "full_sample": full,
        "jackknife": jackknife,
        "failure_count": len(failures),
        "failures": failures,
        "worst_removals": worst,
        "best_removals": best,
        "jackknife_pass": len(failures) == 0,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    full = report["full_sample"]
    lines = [
        "# v28 Entry-Conditioned Jackknife",
        "",
        "Fixed entry selector: raw v28 p50 edge0. Removes one market at a time and rechecks +5pp FV calibration improvement.",
        "",
        f"- Selected entries: `{report['selected_entries']}`",
        f"- Settled entries: `{report['settled_entries']}`",
        f"- Markets: `{report['markets']}`",
        f"- Jackknife pass: `{report['jackknife_pass']}`",
        f"- Failure count: `{report['failure_count']}`",
        f"- Full-sample Brier delta: `{fmt(full.get('brier_delta_vs_raw'))}`",
        f"- Full-sample logloss delta: `{fmt(full.get('logloss_delta_vs_raw'))}`",
        "",
        "## Worst Removals",
        "",
        "| removed market | removed W/L | removed net c | count kept | brier delta | logloss delta | ece delta |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["worst_removals"]:
        lines.append(
            f"| {row['removed_market']} | {row['removed_wins']}/{row['removed_losses']} | "
            f"{fmt(row['removed_net_cents'])} | {row['count']} | {fmt(row['brier_delta_vs_raw'])} | "
            f"{fmt(row['logloss_delta_vs_raw'])} | {fmt(row['ece_delta_vs_raw'])} |"
        )
    lines.extend(["", "## Best Removals", ""])
    lines.append("| removed market | removed W/L | removed net c | count kept | brier delta | logloss delta | ece delta |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in report["best_removals"]:
        lines.append(
            f"| {row['removed_market']} | {row['removed_wins']}/{row['removed_losses']} | "
            f"{fmt(row['removed_net_cents'])} | {row['count']} | {fmt(row['brier_delta_vs_raw'])} | "
            f"{fmt(row['logloss_delta_vs_raw'])} | {fmt(row['ece_delta_vs_raw'])} |"
        )
    if report["failures"]:
        lines.extend(["", "## Failures", ""])
        for row in report["failures"]:
            lines.append(f"- `{row['removed_market']}` brier delta `{fmt(row['brier_delta_vs_raw'])}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
