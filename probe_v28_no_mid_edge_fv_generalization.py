"""NO-side mid-edge FV generalization diagnostic.

Research-only; no live bot changes or orders.

The weak-reversal residual discovery says NO-side 5-8pp raw-edge rows may be
overconfident. This diagnostic checks whether the same calibration idea appears
on broader target-coverage rows, not only inside the repaired candidate.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import build_surfaces, summarize
from probe_v28_weak_reversal_residual_repair import edge_between


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_no_mid_edge_fv_generalization_latest.json"
OUT_MD = OUT_DIR / "v28_no_mid_edge_fv_generalization_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_p(p: float) -> float:
    return min(0.99, max(0.01, p))


def no_mid_edge(row: dict[str, Any]) -> bool:
    return str(row.get("side")) == "no" and edge_between(row, 0.05, 0.08)


def yes_mid_edge(row: dict[str, Any]) -> bool:
    return str(row.get("side")) == "yes" and edge_between(row, 0.05, 0.08)


def any_mid_edge(row: dict[str, Any]) -> bool:
    return edge_between(row, 0.05, 0.08)


def metric(rows: list[dict[str, Any]], transform: Callable[[float, dict[str, Any]], float], predicate: Callable[[dict[str, Any]], bool] | None = None) -> dict[str, Any]:
    scored = []
    for row in rows:
        if predicate is not None and not predicate(row):
            continue
        if row.get("side_won") is None:
            continue
        p_raw = as_float(row.get("p_side"))
        if p_raw is None:
            continue
        p = clamp_p(transform(p_raw, row))
        y = 1.0 if row.get("side_won") is True else 0.0
        scored.append((p, y, row))
    if not scored:
        return {"rows": 0, "wins": 0, "losses": 0, "avg_p": None, "win_rate": None, "brier": None, "logloss": None, "net_cents": 0.0}
    wins = sum(1 for _, y, _ in scored if y == 1.0)
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for _, _, row in scored)
    return {
        "rows": len(scored),
        "wins": wins,
        "losses": len(scored) - wins,
        "avg_p": sum(p for p, _, _ in scored) / len(scored),
        "win_rate": sum(y for _, y, _ in scored) / len(scored),
        "brier": sum((p - y) ** 2 for p, y, _ in scored) / len(scored),
        "logloss": -sum(y * math.log(p) + (1.0 - y) * math.log(1.0 - p) for p, y, _ in scored) / len(scored),
        "net_cents": net,
        "avg_net_cents": net / len(scored),
    }


def raw_transform(p: float, row: dict[str, Any]) -> float:
    return p


def no_mid_half_to_50(p: float, row: dict[str, Any]) -> float:
    if no_mid_edge(row):
        return 0.5 + 0.5 * (p - 0.5)
    return p


def no_mid_to_book(p: float, row: dict[str, Any]) -> float:
    if no_mid_edge(row):
        ask = as_float(row.get("ask_prob"))
        return ask if ask is not None else p
    return p


VARIANTS: list[tuple[str, Callable[[float, dict[str, Any]], float]]] = [
    ("raw", raw_transform),
    ("no_mid_half_to_50", no_mid_half_to_50),
    ("no_mid_to_book", no_mid_to_book),
]


def with_deltas(row: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["brier_delta_vs_raw"] = delta(row.get("brier"), raw.get("brier"))
    out["logloss_delta_vs_raw"] = delta(row.get("logloss"), raw.get("logloss"))
    return out


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def build_report() -> dict[str, Any]:
    _, target, denominator, _ = build_surfaces()
    raw_all = metric(target, raw_transform)
    rows = []
    for name, fn in VARIANTS:
        all_m = metric(target, fn)
        rows.append(
            {
                "variant": name,
                "all": with_deltas(all_m, raw_all),
                "no_mid": metric(target, fn, no_mid_edge),
                "yes_mid": metric(target, fn, yes_mid_edge),
                "any_mid": metric(target, fn, any_mid_edge),
            }
        )
    rows.sort(key=lambda row: (row["all"].get("brier_delta_vs_raw") or 0.0, row["all"].get("logloss_delta_vs_raw") or 0.0))
    return {
        "diagnostic": "no_mid_edge_fv_generalization",
        "forward_denominator": denominator,
        "target_summary": summarize(target, denominator),
        "zone_definition": "raw target-coverage rows with side=no and raw_edge_prob in [0.05,0.08)",
        "ranked": rows,
        "best": rows[0] if rows else {},
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    raw = next((row for row in rows if row.get("variant") == "raw"), {})
    no_mid = (raw.get("no_mid") or {})
    notes = [
        f"Raw NO mid-edge rows: {no_mid.get('rows')}; W/L {no_mid.get('wins')}/{no_mid.get('losses')}; net {no_mid.get('net_cents')}c; avg p {no_mid.get('avg_p')} vs win rate {no_mid.get('win_rate')}.",
    ]
    best = rows[0] if rows else {}
    if best:
        all_m = best.get("all") or {}
        notes.append(
            f"Best broader FV variant is {best.get('variant')} with all-row Brier/logloss deltas {all_m.get('brier_delta_vs_raw')}/{all_m.get('logloss_delta_vs_raw')}."
        )
    notes.append("If this broader check disagrees with weak-reversal repair, treat the repair as candidate-specific until forward rows mature.")
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
        "# v28 NO Mid-Edge FV Generalization",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Zone: `{report.get('zone_definition')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| variant | all rows | all Brier d | all logloss d | NO mid rows | NO mid W/L | NO mid net | NO mid avg p | NO mid win rate |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("ranked") or []:
        all_m = row.get("all") or {}
        no_mid = row.get("no_mid") or {}
        lines.append(
            f"| {row.get('variant')} | {all_m.get('rows')} | {fmt(all_m.get('brier_delta_vs_raw'))} | "
            f"{fmt(all_m.get('logloss_delta_vs_raw'))} | {no_mid.get('rows')} | {no_mid.get('wins')}/{no_mid.get('losses')} | "
            f"{fmt(no_mid.get('net_cents'))} | {fmt(no_mid.get('avg_p'))} | {fmt(no_mid.get('win_rate'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
