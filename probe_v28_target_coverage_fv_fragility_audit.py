"""Fragility audit for the active target-coverage v28 FV overlay.

Research-only; no live bot changes or orders.

The current best target-coverage FV overlay improves Brier/logloss on a very
small forward sample. This report asks the adversarial question: is that edge
spread across plausible market physics, or is it only one lucky row?
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALIDATOR_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_fragility_audit_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_fragility_audit_latest.md"


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
    if "p_side" not in out and "p_raw" in out:
        out["p_side"] = out.get("p_raw")
    return out


def score_row(row: dict[str, Any], overlay: str) -> dict[str, Any] | None:
    side_won = row.get("side_won")
    if side_won is None or overlay not in OVERLAYS:
        return None
    norm = normalize_row(row)
    raw_p = clamp_prob(float(OVERLAYS["raw_probability"](norm)))
    overlay_p = clamp_prob(float(OVERLAYS[overlay](norm)))
    outcome = 1.0 if side_won is True else 0.0
    raw_brier = (raw_p - outcome) ** 2
    overlay_brier = (overlay_p - outcome) ** 2
    raw_logloss = logloss(raw_p, outcome)
    overlay_logloss = logloss(overlay_p, outcome)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "won": side_won,
        "reason": row.get("coverage_valve_reason"),
        "p_raw": raw_p,
        "p_overlay": overlay_p,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "brier_delta": overlay_brier - raw_brier,
        "logloss_delta": overlay_logloss - raw_logloss,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(str(row.get(key)), []).append(row)
    out = []
    for name, items in buckets.items():
        briers = [float(item["brier_delta"]) for item in items]
        losses = [float(item["logloss_delta"]) for item in items]
        out.append({
            "bucket": name,
            "rows": len(items),
            "wins": sum(1 for item in items if item.get("won") is True),
            "losses": sum(1 for item in items if item.get("won") is False),
            "brier_delta_sum": sum(briers),
            "brier_delta_mean": avg(briers),
            "logloss_delta_sum": sum(losses),
            "logloss_delta_mean": avg(losses),
        })
    out.sort(key=lambda item: (str(item["bucket"])))
    return out


def p_bucket(p: float) -> str:
    if p < 0.60:
        return "p50_60"
    if p < 0.75:
        return "p60_75"
    return "p75_plus"


def geometry_bucket(row: dict[str, Any]) -> str:
    p = float(row.get("p_raw") or 0.0)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    edge = as_float(row.get("raw_edge_prob")) or 0.0
    if p >= 0.75 and abs_d >= 0.50:
        return "strong_far_from_boundary"
    if p >= 0.60:
        return "strong_mid_geometry"
    if recross >= 0.90 and abs_d <= 0.25:
        return "weak_turbulent_boundary"
    if edge >= 0.08:
        return "weak_but_wide_edge"
    return "weak_other"


def build_report() -> dict[str, Any]:
    validator = load_json(VALIDATOR_JSON)
    seq = load_json(SEQ_JSON)
    overlay = seq.get("overlay") or "entry_conditioned_logit125_p60_only_probability"
    rows = [
        item for item in (
            score_row(row, str(overlay))
            for row in (validator.get("forward_rows") if isinstance(validator.get("forward_rows"), list) else [])
        )
        if item is not None
    ]
    for row in rows:
        row["p_bucket"] = p_bucket(float(row["p_raw"]))
        row["geometry_bucket"] = geometry_bucket(row)

    brier_deltas = [float(row["brier_delta"]) for row in rows]
    logloss_deltas = [float(row["logloss_delta"]) for row in rows]
    total_brier = sum(brier_deltas)
    total_logloss = sum(logloss_deltas)
    leave_one_out = []
    for row in rows:
        remaining = [item for item in rows if item is not row]
        n = len(remaining)
        leave_one_out.append({
            "removed_market": row.get("market"),
            "removed_brier_delta": row.get("brier_delta"),
            "remaining_rows": n,
            "remaining_brier_mean_delta": sum(float(item["brier_delta"]) for item in remaining) / n if n else None,
            "remaining_logloss_mean_delta": sum(float(item["logloss_delta"]) for item in remaining) / n if n else None,
        })
    leave_one_out.sort(key=lambda item: float(item.get("remaining_brier_mean_delta") or 999.0), reverse=True)

    positive_brier = [row for row in rows if float(row["brier_delta"]) > 0]
    negative_brier = [row for row in rows if float(row["brier_delta"]) < 0]
    biggest_help = sorted(rows, key=lambda row: float(row["brier_delta"]))[:3]
    biggest_hurt = sorted(rows, key=lambda row: float(row["brier_delta"]), reverse=True)[:3]

    return {
        "policy": validator.get("policy"),
        "overlay": overlay,
        "freeze_ts": validator.get("freeze_ts"),
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("won") is True),
        "losses": sum(1 for row in rows if row.get("won") is False),
        "brier_delta_sum": total_brier,
        "brier_delta_mean": avg(brier_deltas),
        "logloss_delta_sum": total_logloss,
        "logloss_delta_mean": avg(logloss_deltas),
        "negative_brier_rows": len(negative_brier),
        "positive_brier_rows": len(positive_brier),
        "p_bucket_summary": summarize(rows, "p_bucket"),
        "geometry_bucket_summary": summarize(rows, "geometry_bucket"),
        "reason_summary": summarize(rows, "reason"),
        "leave_one_out": leave_one_out,
        "biggest_help": biggest_help,
        "biggest_hurt": biggest_hurt,
        "fragility_flags": fragility_flags(rows, leave_one_out, total_brier),
        "scored_rows": rows,
    }


def fragility_flags(rows: list[dict[str, Any]], leave_one_out: list[dict[str, Any]], total_brier: float) -> list[str]:
    flags: list[str] = []
    if len(rows) < 30:
        flags.append("sample_lt_30")
    if any(as_float(row.get("remaining_brier_mean_delta")) is not None and float(row["remaining_brier_mean_delta"]) >= 0.0 for row in leave_one_out):
        flags.append("leave_one_out_can_erase_brier_edge")
    if total_brier >= 0.0:
        flags.append("brier_edge_not_positive")
    strong = [row for row in rows if row.get("p_bucket") in {"p60_75", "p75_plus"}]
    weak = [row for row in rows if row.get("p_bucket") == "p50_60"]
    if strong and sum(float(row["brier_delta"]) for row in strong) < 0.0 and weak and abs(sum(float(row["brier_delta"]) for row in weak)) < 1e-12:
        flags.append("edge_concentrated_in_strong_raw_rows_by_design")
    return flags


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
        "# v28 Target-Coverage FV Fragility Audit",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Rows/W/L: `{report.get('rows')}/{report.get('wins')}/{report.get('losses')}`",
        f"- Brier delta sum/mean: `{fmt(report.get('brier_delta_sum'))}/{fmt(report.get('brier_delta_mean'))}`",
        f"- Logloss delta sum/mean: `{fmt(report.get('logloss_delta_sum'))}/{fmt(report.get('logloss_delta_mean'))}`",
        f"- Negative/positive Brier rows: `{report.get('negative_brier_rows')}/{report.get('positive_brier_rows')}`",
        f"- Fragility flags: `{', '.join(report.get('fragility_flags') or []) or 'none'}`",
        "",
        "## Probability Buckets",
        "",
        "| bucket | rows | W/L | brier sum | brier mean | logloss sum |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("p_bucket_summary") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('brier_delta_sum'))} | {fmt(row.get('brier_delta_mean'))} | {fmt(row.get('logloss_delta_sum'))} |"
        )
    lines.extend(["", "## Geometry Buckets", "", "| bucket | rows | W/L | brier sum | brier mean | logloss sum |", "|---|---:|---:|---:|---:|---:|"])
    for row in report.get("geometry_bucket_summary") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('brier_delta_sum'))} | {fmt(row.get('brier_delta_mean'))} | {fmt(row.get('logloss_delta_sum'))} |"
        )
    lines.extend(["", "## Leave-One-Out Worst Cases", "", "| removed market | removed brier d | remaining brier mean d | remaining logloss mean d |", "|---|---:|---:|---:|"])
    for row in (report.get("leave_one_out") or [])[:5]:
        lines.append(
            f"| {row.get('removed_market')} | {fmt(row.get('removed_brier_delta'))} | "
            f"{fmt(row.get('remaining_brier_mean_delta'))} | {fmt(row.get('remaining_logloss_mean_delta'))} |"
        )
    lines.extend(["", "## Biggest Help/Hurt", ""])
    lines.append("- Biggest helpers:")
    for row in report.get("biggest_help") or []:
        lines.append(
            f"  - `{row.get('market')}` {row.get('side')} won `{row.get('won')}` p `{fmt(row.get('p_raw'))}->{fmt(row.get('p_overlay'))}` brier d `{fmt(row.get('brier_delta'))}`"
        )
    lines.append("- Biggest hurts:")
    for row in report.get("biggest_hurt") or []:
        lines.append(
            f"  - `{row.get('market')}` {row.get('side')} won `{row.get('won')}` p `{fmt(row.get('p_raw'))}->{fmt(row.get('p_overlay'))}` brier d `{fmt(row.get('brier_delta'))}`"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
