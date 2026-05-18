"""Live-evidence audit for the active target-coverage FV overlay.

Research-only; no live bot changes or orders.

The target-coverage FV overlay can improve calibration on selected rows while
still being mostly or entirely backed by actionable rejected observations. This
audit makes that evidence-quality split explicit so the model is not promoted
from simulated shadow rows masquerading as live evidence.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_fv_overlay_validator import LOCAL_OVERLAYS as OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALIDATOR_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_live_evidence_audit_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_live_evidence_audit_latest.md"

MIN_SETTLED = 30
MAX_SIMULATED_SHARE = 0.35
MIN_ACTUAL_ROWS = 10


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


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if "p_side" not in out and "p_raw" in out:
        out["p_side"] = out.get("p_raw")
    return out


def score_row(row: dict[str, Any], overlay: str) -> dict[str, Any] | None:
    if row.get("side_won") is None:
        return None
    norm = normalize_row(row)
    raw_p = clamp_prob(float(OVERLAYS["raw_probability"](norm)))
    overlay_p = clamp_prob(float(OVERLAYS[overlay](norm)))
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source") or "unknown",
        "won": row.get("side_won"),
        "p_raw": raw_p,
        "p_overlay": overlay_p,
        "raw_brier": (raw_p - outcome) ** 2,
        "overlay_brier": (overlay_p - outcome) ** 2,
        "brier_delta": (overlay_p - outcome) ** 2 - (raw_p - outcome) ** 2,
        "raw_logloss": logloss(raw_p, outcome),
        "overlay_logloss": logloss(overlay_p, outcome),
        "logloss_delta": logloss(overlay_p, outcome) - logloss(raw_p, outcome),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "reason": row.get("coverage_valve_reason"),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    briers = [float(row["brier_delta"]) for row in rows]
    loglosses = [float(row["logloss_delta"]) for row in rows]
    return {
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("won") is True),
        "losses": sum(1 for row in rows if row.get("won") is False),
        "net_cents": sum(float(row.get("net_cents") or 0.0) for row in rows),
        "brier_delta_sum": sum(briers),
        "brier_delta_mean": avg(briers),
        "logloss_delta_sum": sum(loglosses),
        "logloss_delta_mean": avg(loglosses),
    }


def build_report() -> dict[str, Any]:
    validator = load_json(VALIDATOR_JSON)
    seq = load_json(SEQ_JSON)
    overlay = str(seq.get("overlay") or "entry_conditioned_logit125_p60_only_probability")
    raw_rows = validator.get("forward_rows") if isinstance(validator.get("forward_rows"), list) else []
    scored = [item for item in (score_row(row, overlay) for row in raw_rows) if item is not None]
    by_source: dict[str, list[dict[str, Any]]] = {}
    for row in scored:
        by_source.setdefault(str(row.get("source") or "unknown"), []).append(row)
    actual_rows = by_source.get("approved_entry", [])
    simulated_rows = [row for row in scored if row.get("source") != "approved_entry"]
    simulated_share = len(simulated_rows) / len(scored) if scored else None
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(actual_rows) < MIN_ACTUAL_ROWS:
        blockers.append("actual_approved_rows_lt_10")
    if simulated_share is None or simulated_share > MAX_SIMULATED_SHARE:
        blockers.append("simulated_share_gt_35pct")
    return {
        "policy": validator.get("policy"),
        "overlay": overlay,
        "freeze_ts": validator.get("freeze_ts"),
        "source_coverage_freeze_ts": validator.get("source_coverage_freeze_ts"),
        "total": summarize(scored),
        "by_source": {source: summarize(rows) for source, rows in sorted(by_source.items())},
        "approved_entry_rows": len(actual_rows),
        "simulated_or_rejected_rows": len(simulated_rows),
        "simulated_share": simulated_share,
        "blockers": blockers,
        "scored_rows": scored,
        "interpretation": interpretation(len(actual_rows), simulated_share, blockers),
    }


def interpretation(actual_rows: int, simulated_share: float | None, blockers: list[str]) -> list[str]:
    notes = []
    notes.append(
        f"Actual approved-entry evidence is {actual_rows} rows; the rest is actionable rejected shadow evidence."
    )
    if simulated_share is not None:
        notes.append(f"Simulated/rejected evidence share is {simulated_share:.2%}.")
    if blockers:
        notes.append(f"Live-evidence blockers remain: {', '.join(blockers)}.")
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
    total = report.get("total") or {}
    lines = [
        "# v28 Target-Coverage FV Live Evidence Audit",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Total rows/W-L/net: `{total.get('rows')}/{total.get('wins')}-{total.get('losses')}/{fmt(total.get('net_cents'))}c`",
        f"- Approved-entry rows: `{report.get('approved_entry_rows')}`",
        f"- Simulated/rejected rows/share: `{report.get('simulated_or_rejected_rows')}/{fmt(report.get('simulated_share'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## By Source",
        "",
        "| source | rows | W/L | net c | brier d mean | logloss d mean |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for source, row in (report.get("by_source") or {}).items():
        lines.append(
            f"| {source} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('brier_delta_mean'))} | {fmt(row.get('logloss_delta_mean'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
