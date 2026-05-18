"""FV shrink diagnostic for weak-reversal residual loss zone.

Research-only; no live bot changes or orders.

The weak-reversal residual repair found a profitable-looking skip for NO-side
5-8pp raw-edge rows. This script asks whether that skip corresponds to an FV
calibration error: are those rows overconfident probabilities, or only bad
price geometry?
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import build_surfaces
from probe_v28_weak_boundary_reversal_bakeoff import run_variant
from probe_v28_weak_reversal_residual_repair import edge_between


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_weak_reversal_residual_fv_shrink_latest.json"
OUT_MD = OUT_DIR / "v28_weak_reversal_residual_fv_shrink_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_p(p: float) -> float:
    return min(0.99, max(0.01, p))


def residual_zone(row: dict[str, Any]) -> bool:
    return str(row.get("side")) == "no" and edge_between(row, 0.05, 0.08)


def raw_p(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side"))


def book_p(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    edge = as_float(row.get("raw_edge_prob"))
    if ask is None:
        return None
    if edge is None:
        return ask
    # Executable ask is a conservative book anchor. Add back only a tiny edge
    # for variants that should remain willing to trade.
    return ask


def transform(name: str, row: dict[str, Any]) -> float | None:
    p = raw_p(row)
    if p is None:
        return None
    if not residual_zone(row):
        return p
    ask = as_float(row.get("ask_prob"))
    if name == "raw":
        return p
    if name == "minus_03":
        return clamp_p(p - 0.03)
    if name == "minus_05":
        return clamp_p(p - 0.05)
    if name == "minus_08":
        return clamp_p(p - 0.08)
    if name == "half_to_50":
        return clamp_p(0.5 + 0.5 * (p - 0.5))
    if name == "to_book":
        return clamp_p(ask if ask is not None else p)
    if name == "book_plus_02":
        return clamp_p((ask + 0.02) if ask is not None else p)
    if name == "book_plus_03":
        return clamp_p((ask + 0.03) if ask is not None else p)
    return p


VARIANTS = ["raw", "minus_03", "minus_05", "minus_08", "half_to_50", "to_book", "book_plus_02", "book_plus_03"]


def metric_rows(rows: list[dict[str, Any]], variant: str, predicate: Callable[[dict[str, Any]], bool] | None = None) -> dict[str, Any]:
    scored = []
    for row in rows:
        if predicate is not None and not predicate(row):
            continue
        if row.get("side_won") is None:
            continue
        p = transform(variant, row)
        if p is None:
            continue
        y = 1.0 if row.get("side_won") is True else 0.0
        p = clamp_p(p)
        scored.append((p, y, row))
    if not scored:
        return {"rows": 0, "brier": None, "logloss": None, "avg_p": None, "win_rate": None}
    brier = sum((p - y) ** 2 for p, y, _ in scored) / len(scored)
    logloss = -sum(y * math.log(p) + (1.0 - y) * math.log(1.0 - p) for p, y, _ in scored) / len(scored)
    avg_p = sum(p for p, _, _ in scored) / len(scored)
    win_rate = sum(y for _, y, _ in scored) / len(scored)
    return {
        "rows": len(scored),
        "brier": brier,
        "logloss": logloss,
        "avg_p": avg_p,
        "win_rate": win_rate,
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    weak = run_variant(
        all_rows=all_rows,
        target=target,
        denominator=denominator,
        forward_markets=forward_markets,
        p_max=0.60,
        recross_floor=0.75,
        abs_d_max=0.25,
        max_delay=240.0,
        no_replacement_mode="abstain",
    )
    rows = weak.get("candidate_rows") or []
    ranked = []
    raw_all = metric_rows(rows, "raw")
    raw_zone = metric_rows(rows, "raw", residual_zone)
    for variant in VARIANTS:
        all_metrics = metric_rows(rows, variant)
        zone_metrics = metric_rows(rows, variant, residual_zone)
        ranked.append(
            {
                "variant": variant,
                "all": all_metrics,
                "zone": zone_metrics,
                "all_brier_delta_vs_raw": none_delta(all_metrics.get("brier"), raw_all.get("brier")),
                "all_logloss_delta_vs_raw": none_delta(all_metrics.get("logloss"), raw_all.get("logloss")),
                "zone_brier_delta_vs_raw": none_delta(zone_metrics.get("brier"), raw_zone.get("brier")),
                "zone_logloss_delta_vs_raw": none_delta(zone_metrics.get("logloss"), raw_zone.get("logloss")),
            }
        )
    ranked.sort(
        key=lambda row: (
            float(row.get("all_brier_delta_vs_raw") if row.get("all_brier_delta_vs_raw") is not None else 999.0),
            float(row.get("all_logloss_delta_vs_raw") if row.get("all_logloss_delta_vs_raw") is not None else 999.0),
        )
    )
    best = ranked[0] if ranked else {}
    return {
        "diagnostic": "weak_reversal_residual_fv_shrink",
        "weak_policy": weak.get("policy"),
        "forward_denominator": denominator,
        "candidate_summary": weak.get("candidate_summary"),
        "residual_zone_definition": "side=no and raw_edge_prob in [0.05, 0.08)",
        "raw_all": raw_all,
        "raw_zone": raw_zone,
        "best": best,
        "ranked": ranked,
        "interpretation": interpretation(best, raw_zone),
    }


def none_delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def interpretation(best: dict[str, Any], raw_zone: dict[str, Any]) -> list[str]:
    notes = [
        f"Residual zone raw rows: {raw_zone.get('rows')}; raw avg p {raw_zone.get('avg_p')} vs win rate {raw_zone.get('win_rate')}.",
    ]
    if best:
        notes.append(
            f"Best FV variant is {best.get('variant')} with all Brier/logloss deltas {best.get('all_brier_delta_vs_raw')}/{best.get('all_logloss_delta_vs_raw')}."
        )
        zone = best.get("zone") or {}
        notes.append(
            f"In-zone adjusted avg p is {zone.get('avg_p')} with Brier/logloss deltas {best.get('zone_brier_delta_vs_raw')}/{best.get('zone_logloss_delta_vs_raw')}."
        )
    notes.append("This is calibration evidence only; entry profitability still requires frozen forward validation.")
    return notes


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
        "# v28 Weak-Reversal Residual FV Shrink",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Weak policy: `{report.get('weak_policy')}`",
        f"- Residual zone: `{report.get('residual_zone_definition')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Ranked FV Variants",
            "",
            "| variant | all rows | all Brier d | all logloss d | zone rows | zone avg p | zone win rate | zone Brier d | zone logloss d |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("ranked") or []:
        all_metrics = row.get("all") or {}
        zone = row.get("zone") or {}
        lines.append(
            f"| {row.get('variant')} | {all_metrics.get('rows')} | {fmt(row.get('all_brier_delta_vs_raw'))} | "
            f"{fmt(row.get('all_logloss_delta_vs_raw'))} | {zone.get('rows')} | {fmt(zone.get('avg_p'))} | "
            f"{fmt(zone.get('win_rate'))} | {fmt(row.get('zone_brier_delta_vs_raw'))} | {fmt(row.get('zone_logloss_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
