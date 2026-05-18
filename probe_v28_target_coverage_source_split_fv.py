"""Source split for target-coverage FV diagnostics.

Research-only; no live bot changes or orders.

The target-coverage surface blends actual approved entries with
rejected-actionable shadow rows. This report splits calibration by source so
we do not mistake simulated-row behavior for live-like evidence.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_target_coverage_conservative_fv_variants import (
    logit125_p70,
    logit125_p75,
    raw_probability,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_source_split_fv_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_source_split_fv_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def score_group(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        p_raw = clamp_prob(float(raw_probability(row)))
        p_var = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "brier_delta": (p_var - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_var, outcome) - logloss(p_raw, outcome),
            "net_cents": float(row.get("net_gross_cents_after_entry_fee") or 0.0),
            "won": row.get("side_won") is True,
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    return {
        "variant": name,
        "rows": len(scored),
        "wins": sum(1 for row in scored if row["won"]),
        "losses": sum(1 for row in scored if not row["won"]),
        "net_cents": sum(float(row["net_cents"]) for row in scored),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_positive_count": sum(1 for value in briers if value > 0.0),
        "brier_negative_count": sum(1 for value in briers if value < 0.0),
        "logloss_positive_count": sum(1 for value in losses if value > 0.0),
        "logloss_negative_count": sum(1 for value in losses if value < 0.0),
    }


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_probability,
    "logit125_p70": logit125_p70,
    "logit125_p75": logit125_p75,
}


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    settled = [row for row in rows if row.get("side_won") is not None]
    sources = sorted({str(row.get("source") or "unknown") for row in settled})
    groups = {"all": settled}
    for source in sources:
        groups[source] = [row for row in settled if str(row.get("source") or "unknown") == source]
    scored_groups = []
    for group_name, group_rows in groups.items():
        ranked = [score_group(group_rows, name, fn) for name, fn in VARIANTS.items()]
        ranked.sort(key=lambda row: (
            row.get("variant") == "raw_probability",
            float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
        ))
        scored_groups.append({
            "source": group_name,
            "rows": len(group_rows),
            "ranked": ranked,
            "best_variant": ranked[0].get("variant") if ranked else None,
        })
    return {
        "policy": target.get("policy"),
        "freeze_ts": target.get("freeze_ts"),
        "entries": len(rows),
        "settled": len(settled),
        "forward_denominator": target.get("forward_denominator"),
        "source_groups": scored_groups,
        "interpretation": interpretation(scored_groups),
    }


def interpretation(groups: list[dict[str, Any]]) -> list[str]:
    notes = []
    for group in groups:
        best = (group.get("ranked") or [{}])[0]
        notes.append(
            f"{group.get('source')} best is {best.get('variant')} over {group.get('rows')} rows with Brier/logloss deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
        )
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
        "# v28 Target-Coverage Source-Split FV",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('forward_denominator')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Groups", ""])
    for group in report.get("source_groups") or []:
        lines.extend([
            f"### {group.get('source')}",
            "",
            "| variant | rows | W/L | net c | brier mean | brier -/+ | logloss mean | logloss -/+ |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in group.get("ranked") or []:
            lines.append(
                f"| `{row.get('variant')}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('brier_mean_delta'))} | "
                f"{row.get('brier_negative_count')}/{row.get('brier_positive_count')} | "
                f"{fmt(row.get('logloss_mean_delta'))} | {row.get('logloss_negative_count')}/{row.get('logloss_positive_count')} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
