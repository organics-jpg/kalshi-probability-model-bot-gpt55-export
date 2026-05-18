"""Plateau test for entry-conditioned probability lift.

If a +5pp posterior lift only works at exactly +5pp, it is likely curve-fit.
If a broad positive-lift band improves Brier/logloss on fixed raw-p50 entries,
that supports the physics claim that clearing the executable entry gate is
itself additional evidence not fully captured in raw v28.

Research-only; fixed entry selection; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import clamp_prob, score_overlay
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_entry_conditioned_lift_plateau_latest.json"
OUT_MD = OUT_DIR / "v28_entry_conditioned_lift_plateau_latest.md"

LIFTS = [value / 100.0 for value in range(-10, 16)]


def overlay_for_lift(lift: float):
    return lambda row: clamp_prob(p_raw(row) + lift)


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    scored = []
    for lift in LIFTS:
        score = score_overlay(picked, f"lift_{lift:+.2f}", overlay_for_lift(lift))
        scored.append({key: value for key, value in score.items() if key not in {"buckets", "scored_rows"}})
    raw_row = next(row for row in scored if row["overlay"] == "lift_+0.00")
    raw_brier = raw_row.get("avg_brier")
    raw_logloss = raw_row.get("avg_logloss")
    for row in scored:
        row["lift_pp"] = int(round(float(row["overlay"].replace("lift_", "")) * 100.0))
        row["brier_delta_vs_raw"] = None if raw_brier is None or row.get("avg_brier") is None else float(row["avg_brier"]) - float(raw_brier)
        row["logloss_delta_vs_raw"] = None if raw_logloss is None or row.get("avg_logloss") is None else float(row["avg_logloss"]) - float(raw_logloss)
    ranked = sorted(scored, key=lambda row: (float(row.get("avg_brier") or 999.0), abs(int(row["lift_pp"]))))
    improving = [row for row in scored if row.get("brier_delta_vs_raw") is not None and float(row["brier_delta_vs_raw"]) < 0.0]
    return {
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "selected_entries": len(picked),
        "settled_entries": sum(1 for row in picked if row.get("side_won") is not None),
        "raw_brier": raw_brier,
        "raw_logloss": raw_logloss,
        "ranked": ranked,
        "by_lift": sorted(scored, key=lambda row: int(row["lift_pp"])),
        "improving_lift_pp": [row["lift_pp"] for row in sorted(improving, key=lambda row: int(row["lift_pp"]))],
        "best_lift_pp": ranked[0]["lift_pp"] if ranked else None,
        "plateau_width_count": len(improving),
        "interpretation": "Broad positive lift support is less overfit-prone than a single sharp optimum.",
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
    lines = [
        "# v28 Entry-Conditioned Lift Plateau",
        "",
        "Fixed entry selector: raw v28 p50 edge0. Tests whether posterior lift improvement is broad or point-fit.",
        "",
        f"- Selected entries: `{report['selected_entries']}`",
        f"- Settled entries: `{report['settled_entries']}`",
        f"- Best lift: `{report['best_lift_pp']}pp`",
        f"- Improving lift values: `{report['improving_lift_pp']}`",
        "",
        "| lift pp | brier | delta | logloss | delta | avg p | win rate | ece |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["by_lift"]:
        lines.append(
            f"| {row['lift_pp']} | {fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('ece_10bucket'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
