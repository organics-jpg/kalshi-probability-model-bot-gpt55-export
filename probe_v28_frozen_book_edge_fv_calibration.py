"""FV calibration for frozen book-edge entry lanes.

Research-only; no live bot changes or orders.

The frozen book-edge entry validators answer whether the entry rule makes
money. This companion answers the FV question: conditional on those frozen
entries, which probability estimate is better calibrated?
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
P50_JSON = OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"
BOOK05_JSON = OUT_DIR / "v28_frozen_book_plus05_entry_latest.json"
BOOK05_NO_CHEAP_YES_JSON = OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_book_edge_fv_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_book_edge_fv_calibration_latest.md"

MIN_SETTLED = 30


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


def clipped(p: float) -> float:
    return min(0.999, max(0.001, p))


def logloss(p: float, y: float) -> float:
    p = clipped(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def brier(p: float, y: float) -> float:
    return (p - y) ** 2


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def probability_variants(row: dict[str, Any]) -> dict[str, float]:
    raw = as_float(row.get("p_side"))
    book = as_float(row.get("ask_prob"))
    if raw is None or book is None:
        return {}
    delta = raw - book
    # Candidate priors, intentionally simple and predeclared:
    # - raw_v28: current FV.
    # - book: market executable ask probability.
    # - blend_25raw: mostly book when v28/book disagree.
    # - blend_50raw: equal weight.
    # - disagreement_shrink: raw when close; otherwise pull most of the way to book.
    if abs(delta) >= 0.15:
        shrink_alpha = 0.25
    elif abs(delta) >= 0.08:
        shrink_alpha = 0.50
    else:
        shrink_alpha = 0.80
    return {
        "raw_v28": clipped(raw),
        "book_ask": clipped(book),
        "blend_25raw": clipped(0.25 * raw + 0.75 * book),
        "blend_50raw": clipped(0.50 * raw + 0.50 * book),
        "disagreement_shrink": clipped(shrink_alpha * raw + (1.0 - shrink_alpha) * book),
    }


def score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    variants: dict[str, list[tuple[float, float]]] = {}
    for row in rows:
        if not settled(row):
            continue
        y = 1.0 if row.get("side_won") is True else 0.0
        for name, p in probability_variants(row).items():
            variants.setdefault(name, []).append((p, y))
    raw_pairs = variants.get("raw_v28") or []
    raw_brier = sum(brier(p, y) for p, y in raw_pairs) / len(raw_pairs) if raw_pairs else None
    raw_logloss = sum(logloss(p, y) for p, y in raw_pairs) / len(raw_pairs) if raw_pairs else None
    scored = []
    for name, pairs in variants.items():
        avg_brier = sum(brier(p, y) for p, y in pairs) / len(pairs) if pairs else None
        avg_logloss = sum(logloss(p, y) for p, y in pairs) / len(pairs) if pairs else None
        scored.append({
            "variant": name,
            "rows": len(pairs),
            "avg_probability": sum(p for p, _ in pairs) / len(pairs) if pairs else None,
            "win_rate": sum(y for _, y in pairs) / len(pairs) if pairs else None,
            "avg_brier": avg_brier,
            "avg_logloss": avg_logloss,
            "brier_delta_vs_raw": (avg_brier - raw_brier) if avg_brier is not None and raw_brier is not None else None,
            "logloss_delta_vs_raw": (avg_logloss - raw_logloss) if avg_logloss is not None and raw_logloss is not None else None,
        })
    return sorted(
        scored,
        key=lambda row: (
            row.get("rows", 0) < MIN_SETTLED,
            row.get("brier_delta_vs_raw") if row.get("brier_delta_vs_raw") is not None else 999.0,
            row.get("logloss_delta_vs_raw") if row.get("logloss_delta_vs_raw") is not None else 999.0,
        ),
    )


def source_rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rollups = []
    sources = sorted({str(row.get("source") or "unknown") for row in rows})
    for source in sources:
        source_rows = [row for row in rows if str(row.get("source") or "unknown") == source]
        settled_rows = [row for row in source_rows if settled(row)]
        gross = sum(float(row.get("gross_cents") or 0.0) for row in settled_rows)
        scored = score_rows(source_rows)
        best = scored[0] if scored else {}
        rollups.append({
            "source": source,
            "entries": len(source_rows),
            "settled": len(settled_rows),
            "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
            "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
            "gross_cents": gross,
            "best_variant": best.get("variant"),
            "best_brier_delta_vs_raw": best.get("brier_delta_vs_raw"),
            "best_logloss_delta_vs_raw": best.get("logloss_delta_vs_raw"),
        })
    return rollups


def physics_rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets = {
        "high_conf_p65_plus": lambda row: (as_float(row.get("p_side")) or 0.0) >= 0.65,
        "mid_conf_45_65": lambda row: 0.45 <= (as_float(row.get("p_side")) or -1.0) < 0.65,
        "yes_side": lambda row: str(row.get("side") or "").lower() == "yes",
        "no_side": lambda row: str(row.get("side") or "").lower() == "no",
        "high_recross_075_plus": lambda row: (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75,
        "near_strike_sigma_lt025": lambda row: (as_float(row.get("abs_d_sigma")) or 999.0) < 0.25,
    }
    rollups = []
    for name, predicate in buckets.items():
        bucket_rows = [row for row in rows if predicate(row)]
        settled_rows = [row for row in bucket_rows if settled(row)]
        gross = sum(float(row.get("gross_cents") or 0.0) for row in settled_rows)
        scored = score_rows(bucket_rows)
        best = scored[0] if scored else {}
        rollups.append({
            "bucket": name,
            "entries": len(bucket_rows),
            "settled": len(settled_rows),
            "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
            "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
            "gross_cents": gross,
            "best_variant": best.get("variant"),
            "best_brier_delta_vs_raw": best.get("brier_delta_vs_raw"),
            "best_logloss_delta_vs_raw": best.get("logloss_delta_vs_raw"),
        })
    return rollups


def lane_report(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    ranked = score_rows(rows)
    best = ranked[0] if ranked else {}
    blockers = []
    if int(best.get("rows") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if best.get("brier_delta_vs_raw") is None or float(best.get("brier_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("brier_not_better_than_raw")
    if best.get("logloss_delta_vs_raw") is None or float(best.get("logloss_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("logloss_not_better_than_raw")
    return {
        "lane": name,
        "freeze": payload.get("freeze") or {},
        "future_denominator_markets": payload.get("future_denominator_markets"),
        "entry_summary": payload.get("summary") or {},
        "ranked": ranked,
        "source_rollups": source_rollups(rows),
        "physics_rollups": physics_rollups(rows),
        "best": best,
        "blockers": blockers,
        "fv_ready": not blockers,
    }


def build_report() -> dict[str, Any]:
    lanes = [
        lane_report("p50_book_plus_05_edge_nonnegative", load_json(P50_JSON)),
        lane_report("book_plus_05", load_json(BOOK05_JSON)),
        lane_report("book_plus_05_no_cheap_yes_boundary", load_json(BOOK05_NO_CHEAP_YES_JSON)),
    ]
    return {
        "min_settled": MIN_SETTLED,
        "lanes": lanes,
        "any_fv_ready": any(lane.get("fv_ready") for lane in lanes),
        "interpretation": current_read(lanes),
    }


def current_read(lanes: list[dict[str, Any]]) -> list[str]:
    notes = []
    for lane in lanes:
        best = lane.get("best") or {}
        notes.append(
            f"{lane.get('lane')}: best FV variant is {best.get('variant')} on {best.get('rows', 0)} settled rows; blockers {', '.join(lane.get('blockers') or []) or 'none'}."
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
        "# v28 Frozen Book-Edge FV Calibration",
        "",
        "Future-only FV calibration for frozen book-edge entry lanes. No live orders.",
        "",
        f"- Any FV-ready lane: `{report.get('any_fv_ready')}`",
        f"- Minimum settled rows: `{report.get('min_settled')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- FV ready: `{lane.get('fv_ready')}`",
            f"- Future denominator markets: `{lane.get('future_denominator_markets')}`",
            f"- Blockers: `{', '.join(lane.get('blockers') or []) or 'none'}`",
            "",
            "| variant | rows | avg p | win rate | brier | brier d | logloss | logloss d |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in lane.get("ranked") or []:
            lines.append(
                f"| {row.get('variant')} | {row.get('rows')} | {fmt(row.get('avg_probability'))} | "
                f"{fmt(row.get('win_rate'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
                f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} |"
            )
        lines.extend([
            "",
            "### Source Rollups",
            "",
            "| source | entries | settled | W-L | gross c | best variant | brier d | logloss d |",
            "|---|---:|---:|---:|---:|---|---:|---:|",
        ])
        for row in lane.get("source_rollups") or []:
            lines.append(
                f"| {row.get('source')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}-{row.get('losses')} | {fmt(row.get('gross_cents'))} | "
                f"{row.get('best_variant')} | {fmt(row.get('best_brier_delta_vs_raw'))} | "
                f"{fmt(row.get('best_logloss_delta_vs_raw'))} |"
            )
        lines.extend([
            "",
            "### Physics Rollups",
            "",
            "| bucket | entries | settled | W-L | gross c | best variant | brier d | logloss d |",
            "|---|---:|---:|---:|---:|---|---:|---:|",
        ])
        for row in lane.get("physics_rollups") or []:
            lines.append(
                f"| {row.get('bucket')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}-{row.get('losses')} | {fmt(row.get('gross_cents'))} | "
                f"{row.get('best_variant')} | {fmt(row.get('best_brier_delta_vs_raw'))} | "
                f"{fmt(row.get('best_logloss_delta_vs_raw'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
