"""Source-aware FV overlay validator for v28.

Research-only; no live bot changes or orders.

New hypothesis from forward evidence:
- actual v28-approved entries are overconfident, so executable book anchoring
  calibrates better;
- target-coverage actionable rejected rows benefit from sharpening only strong
  raw p>=60 rows.

This validator scores that source-aware FV overlay against raw/book/logit on
the combined approved-entry plus target-coverage evidence pool.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_source_aware_fv_overlay_validator_latest.json"
OUT_MD = OUT_DIR / "v28_source_aware_fv_overlay_validator_latest.md"

MIN_SETTLED = 30
MIN_APPROVED_ROWS = 10
MAX_SIMULATED_SHARE = 0.35


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


def normalize_approved(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["source"] = "approved_entry"
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        out["ask_prob"] = float(out["ask_cents"]) / 100.0
    out["net_gross_cents_after_entry_fee"] = out.get("actual_gross_cents")
    return out


def normalize_target(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["source"] = row.get("source") or "rejected_actionable"
    out["p_side"] = row.get("p_side", row.get("p_raw"))
    return out


def p_source_aware(row: dict[str, Any]) -> float:
    if row.get("source") == "approved_entry":
        return clamp_prob(float(OVERLAYS["book_probability"](row)))
    return clamp_prob(float(OVERLAYS["entry_conditioned_logit125_p60_only_probability"](row)))


def p_approved_book_else_raw(row: dict[str, Any]) -> float:
    if row.get("source") == "approved_entry":
        return clamp_prob(float(OVERLAYS["book_probability"](row)))
    return clamp_prob(float(OVERLAYS["raw_probability"](row)))


def p_approved_book_else_plus05(row: dict[str, Any]) -> float:
    if row.get("source") == "approved_entry":
        return clamp_prob(float(OVERLAYS["book_probability"](row)))
    return clamp_prob(float(OVERLAYS["entry_conditioned_plus05_probability"](row)))


OVERLAY_FNS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": OVERLAYS["raw_probability"],
    "book_probability": OVERLAYS["book_probability"],
    "entry_conditioned_logit125_p60_only_probability": OVERLAYS["entry_conditioned_logit125_p60_only_probability"],
    "entry_conditioned_plus05_probability": OVERLAYS["entry_conditioned_plus05_probability"],
    "source_aware_approved_book_target_logit125_p60_only": p_source_aware,
    "source_aware_approved_book_target_raw": p_approved_book_else_raw,
    "source_aware_approved_book_target_plus05": p_approved_book_else_plus05,
}


def score_overlay(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        try:
            p = clamp_prob(float(fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "source": row.get("source"),
            "market": row.get("market"),
            "side": row.get("side"),
            "p": p,
            "outcome": outcome,
            "won": row.get("side_won"),
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
        })
    probs = [float(row["p"]) for row in scored]
    outcomes = [float(row["outcome"]) for row in scored]
    return {
        "overlay": name,
        "entries": len(rows),
        "settled": len(scored),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": avg(probs),
        "win_rate": avg(outcomes),
        "calibration_error": None if avg(probs) is None or avg(outcomes) is None else avg(outcomes) - avg(probs),
        "avg_brier": avg([float(row["brier"]) for row in scored]),
        "avg_logloss": avg([float(row["logloss"]) for row in scored]),
        "net_cents": sum(float(row.get("net_cents") or 0.0) for row in scored),
        "by_source": summarize_by_source(scored),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize_by_source(scored: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for source in sorted({str(row.get("source") or "unknown") for row in scored}):
        rows = [row for row in scored if str(row.get("source") or "unknown") == source]
        probs = [float(row["p"]) for row in rows]
        outcomes = [float(row["outcome"]) for row in rows]
        out[source] = {
            "rows": len(rows),
            "wins": sum(1 for row in rows if row.get("won") is True),
            "losses": sum(1 for row in rows if row.get("won") is False),
            "avg_p": avg(probs),
            "win_rate": avg(outcomes),
            "calibration_error": None if avg(probs) is None or avg(outcomes) is None else avg(outcomes) - avg(probs),
            "avg_brier": avg([float(row["brier"]) for row in rows]),
            "avg_logloss": avg([float(row["logloss"]) for row in rows]),
        }
    return out


def enrich(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    ranked = []
    for row in scores:
        enriched = {
            **row,
            "brier_delta_vs_raw": None if row.get("avg_brier") is None or raw_brier is None else float(row["avg_brier"]) - float(raw_brier),
            "logloss_delta_vs_raw": None if row.get("avg_logloss") is None or raw_logloss is None else float(row["avg_logloss"]) - float(raw_logloss),
        }
        blockers = []
        if int(enriched.get("settled") or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if row.get("overlay") != "raw_probability":
            if enriched["brier_delta_vs_raw"] is None or enriched["brier_delta_vs_raw"] >= 0:
                blockers.append("brier_not_better_than_raw")
            if enriched["logloss_delta_vs_raw"] is None or enriched["logloss_delta_vs_raw"] >= 0:
                blockers.append("logloss_not_better_than_raw")
        enriched["blockers"] = blockers
        ranked.append(enriched)
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return ranked


def build_rows() -> list[dict[str, Any]]:
    target = load_json(TARGET_JSON)
    approved = [normalize_approved(row) for row in approved_entry_rows()]
    target_rows = [
        normalize_target(row)
        for row in (target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else [])
    ]
    # Keep exact source rows; same market may appear in approved and rejected views.
    return approved + target_rows


def build_report() -> dict[str, Any]:
    rows = build_rows()
    scores = [score_overlay(rows, name, fn) for name, fn in OVERLAY_FNS.items()]
    ranked = enrich(scores)
    approved_count = sum(1 for row in rows if row.get("source") == "approved_entry" and row.get("side_won") is not None)
    simulated_count = sum(1 for row in rows if row.get("source") != "approved_entry" and row.get("side_won") is not None)
    simulated_share = simulated_count / (approved_count + simulated_count) if (approved_count + simulated_count) else None
    evidence_blockers = []
    if approved_count < MIN_APPROVED_ROWS:
        evidence_blockers.append("approved_rows_lt_10")
    if simulated_share is None or simulated_share > MAX_SIMULATED_SHARE:
        evidence_blockers.append("simulated_share_gt_35pct")
    return {
        "entry_surface": "approved_entries_plus_target_coverage_forward_rows",
        "rows": len(rows),
        "settled": approved_count + simulated_count,
        "approved_settled": approved_count,
        "simulated_settled": simulated_count,
        "simulated_share": simulated_share,
        "ranked": ranked,
        "best_overlay": ranked[0].get("overlay") if ranked else None,
        "evidence_blockers": evidence_blockers,
        "interpretation": current_read(ranked, approved_count, simulated_count, simulated_share),
    }


def current_read(ranked: list[dict[str, Any]], approved: int, simulated: int, sim_share: float | None) -> list[str]:
    notes = []
    if ranked:
        best = ranked[0]
        notes.append(
            f"Best combined FV overlay is {best['overlay']} with Brier delta {best.get('brier_delta_vs_raw')} and logloss delta {best.get('logloss_delta_vs_raw')}."
        )
    notes.append(f"Evidence mix is {approved} approved settled rows and {simulated} target/rejected settled rows.")
    if sim_share is not None:
        notes.append(f"Simulated/rejected share is {sim_share:.2%}.")
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
        "# v28 Source-Aware FV Overlay Validator",
        "",
        "Scores FV overlays on approved entries plus the frozen target-coverage forward slice.",
        "",
        f"- Rows/settled: `{report.get('rows')}/{report.get('settled')}`",
        f"- Approved/rejected settled: `{report.get('approved_settled')}/{report.get('simulated_settled')}`",
        f"- Simulated share: `{fmt(report.get('simulated_share'))}`",
        f"- Best overlay: `{report.get('best_overlay')}`",
        f"- Evidence blockers: `{', '.join(report.get('evidence_blockers') or []) or 'none'}`",
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
        "| rank | overlay | settled | W/L | avg p | win rate | cal err | brier | d brier | logloss | d logloss | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('overlay')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Best Overlay By Source",
        "",
        "| source | rows | W/L | avg p | win rate | cal err | brier | logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    best = (report.get("ranked") or [{}])[0]
    for source, row in (best.get("by_source") or {}).items():
        lines.append(
            f"| {source} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('avg_logloss'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
