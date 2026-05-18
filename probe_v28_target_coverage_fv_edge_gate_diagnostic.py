"""FV-implied executable edge gate diagnostic for target-coverage rows.

Research-only; no live bot changes or orders.

FV calibration only helps profitability if it changes what price we are willing
to pay. This report tests whether adjusted FV says the selected side is still
worth buying at the executable ask, while explicitly tracking the coverage cost.
It is diagnostic, not promotion evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_recross_phase_fv_bakeoff import VARIANTS
from probe_v28_target_coverage_fv_overlay_validator import clamp_prob


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_edge_gate_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_edge_gate_diagnostic_latest.md"

EDGE_FLOORS = [-0.15, -0.12, -0.10, -0.08, -0.06, -0.04, -0.02, 0.0, 0.02]
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
MIN_SETTLED = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def normalized(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("p_side") is None and out.get("p_raw") is not None:
        out["p_side"] = out.get("p_raw")
    return out


def score_variant(rows: list[dict[str, Any]], denominator: int, variant: str, fn: Callable[[dict[str, Any]], float]) -> list[dict[str, Any]]:
    scored = []
    for row0 in rows:
        row = normalized(row0)
        try:
            p = clamp_prob(float(fn(row)))
            ask = float(row.get("ask_prob"))
        except (TypeError, ValueError, KeyError):
            continue
        scored.append({
            **row0,
            "variant": variant,
            "p_adjusted": p,
            "adjusted_edge": p - ask,
            "ask_prob": ask,
        })
    out = []
    for floor in EDGE_FLOORS:
        kept = [row for row in scored if float(row["adjusted_edge"]) >= floor]
        skipped = [row for row in scored if float(row["adjusted_edge"]) < floor]
        out.append(summarize(variant, floor, kept, skipped, denominator))
    return out


def summarize(
    variant: str,
    floor: float,
    kept: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    denominator: int,
) -> dict[str, Any]:
    settled = [row for row in kept if row.get("side_won") is not None]
    skipped_settled = [row for row in skipped if row.get("side_won") is not None]
    wins = sum(1 for row in settled if row.get("side_won") is True)
    losses = len(settled) - wins
    coverage = 100.0 * len(kept) / denominator if denominator else None
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    skipped_net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in skipped_settled)
    blockers = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0:
        blockers.append("net_not_positive")
    return {
        "variant": variant,
        "adjusted_edge_floor": floor,
        "entries": len(kept),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "skipped_entries": len(skipped),
        "skipped_settled": len(skipped_settled),
        "skipped_net_cents": skipped_net,
        "blockers": blockers,
        "skipped_markets": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "side_won": row.get("side_won"),
                "net_cents": row.get("net_gross_cents_after_entry_fee"),
                "p_raw": row.get("p_raw"),
                "p_adjusted": row.get("p_adjusted"),
                "ask_prob": row.get("ask_prob"),
                "adjusted_edge": row.get("adjusted_edge"),
                "raw_edge_prob": row.get("raw_edge_prob"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recross_hazard_score": row.get("recross_hazard_score"),
            }
            for row in skipped
        ],
    }


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    denominator = int(target.get("forward_denominator") or 0)
    variants = ["raw_probability", "boundary_recross_shrink_probability", "edge_phase_shrink", "confidence_leak_shrink"]
    candidates = []
    for variant in variants:
        fn = VARIANTS.get(variant)
        if fn is None:
            continue
        candidates.extend(score_variant(rows, denominator, variant, fn))
    ranked = sorted(candidates, key=lambda row: (
        bool(row.get("blockers")),
        -float(row.get("net_cents") or 0.0),
        abs(float(row.get("coverage_pct") or 0.0) - 80.0),
    ))
    return {
        "source_artifact": str(TARGET_JSON),
        "policy": target.get("policy"),
        "target_freeze_ts": target.get("freeze_ts"),
        "forward_denominator": denominator,
        "base_entries": len(rows),
        "base_coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "ranked": ranked,
        "requirements": [
            "diagnostic only; not promotion evidence",
            "must preserve 75-90% coverage before it can be useful",
            "must later be frozen and forward validated before live consideration",
        ],
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    notes = []
    feasible = [row for row in ranked if not row.get("blockers")]
    positive = [row for row in ranked if float(row.get("net_cents") or 0.0) > 0]
    if feasible:
        best = feasible[0]
        notes.append(
            f"Best blocker-free diagnostic row is {best.get('variant')} floor {best.get('adjusted_edge_floor')} with coverage {best.get('coverage_pct')} and net {best.get('net_cents')}c."
        )
    else:
        notes.append("No adjusted-edge diagnostic row clears sample, coverage, and positive-net blockers yet.")
    if positive:
        best_pos = sorted(positive, key=lambda row: -float(row.get("net_cents") or 0.0))[0]
        notes.append(
            f"Best positive-net row is {best_pos.get('variant')} floor {best_pos.get('adjusted_edge_floor')} with coverage {best_pos.get('coverage_pct')} and blockers {best_pos.get('blockers')}."
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
        "# v28 Target-Coverage FV Edge Gate Diagnostic",
        "",
        "Diagnostic-only view of adjusted FV edge versus executable ask.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Target freeze timestamp UTC: `{report.get('target_freeze_ts')}`",
        f"- Base entries/coverage/denominator: `{report.get('base_entries')}/{fmt(report.get('base_coverage_pct'))}/{report.get('forward_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | variant | edge floor | entries | settled | W/L | coverage | net c | skipped | skipped net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('variant')} | {fmt(row.get('adjusted_edge_floor'))} | "
            f"{row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {row.get('skipped_entries')} | "
            f"{fmt(row.get('skipped_net_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
