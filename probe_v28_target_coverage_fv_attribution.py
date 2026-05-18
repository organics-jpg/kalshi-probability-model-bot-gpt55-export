"""Attribution for the target-coverage v28 FV overlay.

Research-only; no live bot changes or orders.

The target-coverage sequential report says the current best FV overlay improves
paired calibration versus raw on the same 80% coverage rows. This report asks
where that improvement comes from so we can distinguish a physics-backed signal
from a few lucky rows.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_fv_overlay_validator import LOCAL_OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_attribution_latest.md"


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
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if "p_side" not in out and out.get("p_raw") is not None:
        out["p_side"] = out.get("p_raw")
    return out


def score_row(row: dict[str, Any], overlay: str) -> dict[str, Any] | None:
    if row.get("side_won") is None:
        return None
    source = normalize_row(row)
    try:
        raw_p = clamp_prob(float(LOCAL_OVERLAYS["raw_probability"](source)))
        overlay_p = clamp_prob(float(LOCAL_OVERLAYS[overlay](source)))
    except (KeyError, TypeError, ValueError):
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return {
        **row,
        "p_raw_scored": raw_p,
        "p_overlay": overlay_p,
        "outcome": outcome,
        "brier_delta": (overlay_p - outcome) ** 2 - (raw_p - outcome) ** 2,
        "logloss_delta": logloss(overlay_p, outcome) - logloss(raw_p, outcome),
    }


def bucket_tags(row: dict[str, Any]) -> list[str]:
    p_raw = as_float(row.get("p_raw") or row.get("p_side")) or 0.0
    ask = as_float(row.get("ask_prob")) or 0.0
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    reason = str(row.get("coverage_valve_reason") or "")
    tags = ["all"]
    tags.append("won" if row.get("side_won") is True else "lost")
    tags.append("raw_p_ge_60" if p_raw >= 0.60 else "raw_p_50_60")
    tags.append("ask_gt_70" if ask > 0.70 else "ask_lte_70")
    if edge is not None:
        tags.append("edge_ge_4pp" if edge >= 0.04 else "edge_lt_4pp")
        tags.append("edge_ge_10pp" if edge >= 0.10 else "edge_lt_10pp")
    tags.append("near_strike" if abs_d <= 0.25 else "away_from_strike")
    tags.append("high_recross" if recross >= 0.75 else "lower_recross")
    if reason:
        tags.append(f"reason_{reason}")
    if p_raw < 0.60 and edge is not None and edge >= 0.04:
        tags.append("weak_raw_but_edge_kept")
    if p_raw >= 0.60 and edge is not None and edge < 0.04:
        tags.append("strong_raw_thin_edge")
    return tags


def summarize_bucket(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    briers = [float(row["brier_delta"]) for row in rows]
    losses = [float(row["logloss_delta"]) for row in rows]
    net = [float(row.get("net_gross_cents_after_entry_fee") or row.get("net_cents") or 0.0) for row in rows]
    return {
        "bucket": name,
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("side_won") is True),
        "losses": sum(1 for row in rows if row.get("side_won") is False),
        "net_cents": sum(net),
        "brier_delta_mean": avg(briers),
        "brier_delta_sum": sum(briers),
        "brier_negative_count": sum(1 for value in briers if value < 0.0),
        "brier_positive_count": sum(1 for value in briers if value > 0.0),
        "logloss_delta_mean": avg(losses),
        "logloss_delta_sum": sum(losses),
        "logloss_negative_count": sum(1 for value in losses if value < 0.0),
        "logloss_positive_count": sum(1 for value in losses if value > 0.0),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_report() -> dict[str, Any]:
    seq = load_json(SEQ_JSON)
    target = load_json(TARGET_JSON)
    overlay = str(seq.get("overlay") or "entry_conditioned_logit125_p60_only_probability")
    scored = [
        score_row(row, overlay)
        for row in (target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else [])
    ]
    rows = [row for row in scored if row is not None]
    buckets = []
    for tag in sorted({tag for row in rows for tag in bucket_tags(row)}):
        tag_rows = [row for row in rows if tag in bucket_tags(row)]
        buckets.append(summarize_bucket(tag, tag_rows))
    buckets.sort(key=lambda row: (-(row.get("rows") or 0), row.get("bucket") or ""))
    return {
        "policy": seq.get("policy"),
        "overlay": overlay,
        "entries": seq.get("entries"),
        "settled_rows": len(rows),
        "coverage_pct": seq.get("coverage_pct"),
        "overall": summarize_bucket("all", rows) if rows else {},
        "buckets": buckets,
        "interpretation": interpretation(buckets),
    }


def interpretation(buckets: list[dict[str, Any]]) -> list[str]:
    by_name = {row.get("bucket"): row for row in buckets}
    notes = []
    strong = by_name.get("raw_p_ge_60") or {}
    weak = by_name.get("raw_p_50_60") or {}
    if strong:
        notes.append(
            f"Strong raw-p>=60 rows drive brier sum {strong.get('brier_delta_sum')} over {strong.get('rows')} rows."
        )
    if weak:
        notes.append(
            f"Weak raw 50-60 rows contribute brier sum {weak.get('brier_delta_sum')} over {weak.get('rows')} rows."
        )
    edge_kept = by_name.get("weak_raw_but_edge_kept") or {}
    if edge_kept:
        notes.append(
            f"Weak-but-edge-kept rows are mostly unadjusted by the selected overlay; brier sum {edge_kept.get('brier_delta_sum')}."
        )
    thin = by_name.get("strong_raw_thin_edge") or {}
    if thin:
        notes.append(
            f"Strong-raw thin-edge rows still benefited from sharpening; brier sum {thin.get('brier_delta_sum')}."
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
        "# v28 Target-Coverage FV Attribution",
        "",
        "Bucket attribution for the best target-coverage FV overlay.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Entries/settled/coverage: `{report.get('entries')}/{report.get('settled_rows')}/{fmt(report.get('coverage_pct'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Buckets",
        "",
        "| bucket | rows | W/L | net c | brier mean | brier sum | brier -/+ | logloss mean | logloss sum | logloss -/+ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("buckets") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('brier_delta_mean'))} | {fmt(row.get('brier_delta_sum'))} | "
            f"{row.get('brier_negative_count')}/{row.get('brier_positive_count')} | "
            f"{fmt(row.get('logloss_delta_mean'))} | {fmt(row.get('logloss_delta_sum'))} | "
            f"{row.get('logloss_negative_count')}/{row.get('logloss_positive_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
