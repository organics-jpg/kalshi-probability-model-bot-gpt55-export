"""Sidecar live-test readiness watch for v28 research candidates.

Research-only; no live bot changes or orders.

Broad-entry promotion still requires target coverage. This report is narrower:
it asks whether any low-coverage sidecar has enough strict forward evidence to
deserve a tiny live-test review later. Coverage is not a blocker here, but
sample size, positive net, source quality, full-loss cushion, and non-diagnostic
forward status remain blockers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
CONTROLLED_GATE_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
OUT_JSON = OUT_DIR / "v28_sidecar_live_test_watch_latest.json"
OUT_MD = OUT_DIR / "v28_sidecar_live_test_watch_latest.md"

MIN_SETTLED = 30
MAX_SIM_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
FORWARD_EVIDENCE_BLOCKERS = {
    "diagnostic_prefreeze",
    "diagnostic_or_prefreeze_context",
    "diagnostic_only_prefreeze",
    "needs_own_frozen_forward_birth",
    "not_strict_forward",
    "entry_lane_not_strict_combo_forward",
    "entry_lane_not_strict_forward",
    "diagnostic_bakeoff",
    "not_fresh_forward_gate",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def as_int(value: Any) -> int:
    number = as_float(value)
    return int(number or 0)


def net_cents(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents_after_entry_fee")) or 0.0)


def live_baseline_cents() -> float:
    payload = load_json(CONTROLLED_GATE_JSON)
    baseline = payload.get("live_baseline") if isinstance(payload.get("live_baseline"), dict) else {}
    return float(as_float(baseline.get("net_cents")) or 0.0)


def sim_share(row: dict[str, Any]) -> float | None:
    return as_float(row.get("simulated_share"))


def is_candidate_row(row: dict[str, Any]) -> bool:
    gate = str(row.get("gate") or "")
    policy = str(row.get("policy") or "")
    blockers = {str(item) for item in row.get("blockers") or []}
    if gate.startswith("exit_"):
        return False
    if "diagnostic_bakeoff" in blockers or "not_fresh_forward_gate" in blockers:
        return False
    if policy.startswith("diagnostic_"):
        return False
    return bool(row.get("has_settled_pnl"))


def blockers(row: dict[str, Any], live_net: float) -> list[str]:
    out: list[str] = []
    settled = as_int(row.get("settled"))
    net = net_cents(row)
    share = sim_share(row)
    cushion = int(max(0.0, net) // 100.0)
    existing = {str(item) for item in row.get("blockers") or []}
    if settled < MIN_SETTLED:
        out.append(f"sample+{MIN_SETTLED - settled}")
    if net <= 0.0:
        out.append("net_not_positive")
    if share is None:
        out.append("source_unknown")
    elif share > MAX_SIM_SHARE:
        clean_needed = int(((share * max(1, as_int(row.get("entries")))) - MAX_SIM_SHARE * max(1, as_int(row.get("entries")))) // MAX_SIM_SHARE) + 1
        out.append(f"source_clean_rows+{max(1, clean_needed)}")
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append(f"cushion+{MIN_FULL_LOSS_CUSHION - cushion}")
    if live_net and net <= live_net:
        out.append("does_not_beat_refreshed_live_baseline")
    if "control_risk_stop_active" in existing:
        out.append("control_risk_stop_active")
    for blocker in sorted(existing & FORWARD_EVIDENCE_BLOCKERS):
        if blocker not in out:
            out.append(blocker)
    policy = str(row.get("policy") or "")
    if "diagnostic_" in policy and not any(item in out for item in FORWARD_EVIDENCE_BLOCKERS):
        out.append("diagnostic_policy_context")
    if row.get("live_ready") is not True:
        out.append("live_ready_false")
    return out


def score(row: dict[str, Any], missing: list[str]) -> float:
    settled = min(as_int(row.get("settled")), MIN_SETTLED)
    net = max(0.0, net_cents(row))
    share = sim_share(row)
    source_penalty = 0.0 if share is not None and share <= MAX_SIM_SHARE else 15.0
    forward_penalty = 150.0 if any(item in FORWARD_EVIDENCE_BLOCKERS for item in missing) else 0.0
    return len(missing) * 100.0 + forward_penalty - settled - min(net / 10.0, 50.0) + source_penalty


def compact(row: dict[str, Any], live_net: float) -> dict[str, Any]:
    missing = blockers(row, live_net)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": net_cents(row),
        "delta_vs_live_cents": net_cents(row) - live_net,
        "simulated_share": sim_share(row),
        "full_loss_cushion": int(max(0.0, net_cents(row)) // 100.0),
        "live_ready": bool(row.get("live_ready")),
        "sidecar_ready": not missing,
        "missing_gates": missing,
        "distance": score(row, missing),
    }


def build_report() -> dict[str, Any]:
    rows = [row for row in load_json(TRACKER_JSON).get("rows") or [] if isinstance(row, dict)]
    live_net = live_baseline_cents()
    candidates = [compact(row, live_net) for row in rows if is_candidate_row(row)]
    positive = [row for row in candidates if float(row.get("net_cents") or 0.0) > 0.0]
    candidates.sort(key=lambda row: (bool(row.get("sidecar_ready")), -float(row.get("net_cents") or 0.0)), reverse=True)
    positive.sort(key=lambda row: (float(row.get("distance") or 999999.0), -float(row.get("net_cents") or 0.0)))
    ready = [row for row in candidates if row.get("sidecar_ready")]
    return {
        "generated_at_utc": utc_now_iso(),
        "requirements": {
            "coverage_requirement": "none_for_sidecar_watch",
            "min_settled": MIN_SETTLED,
            "max_simulated_or_reconstructed_share": MAX_SIM_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
            "live_baseline_cents": live_net,
        },
        "counts": {
            "candidate_rows": len(candidates),
            "positive_rows": len(positive),
            "sidecar_ready_rows": len(ready),
        },
        "closest_positive": positive[:20],
        "top_net": sorted(positive, key=lambda row: float(row.get("net_cents") or 0.0), reverse=True)[:20],
        "ready": ready,
        "interpretation": interpretation(positive, ready, live_net),
    }


def interpretation(positive: list[dict[str, Any]], ready: list[dict[str, Any]], live_net: float) -> list[str]:
    notes = [
        "Sidecar watch intentionally ignores broad coverage, but keeps sample, net, source-quality, cushion, and readiness gates.",
        f"Live-baseline comparison is {live_net:.0f}c from the controlled live-test gate.",
        "This report is a live-test review aid only; it does not place orders or change live logic.",
    ]
    if ready:
        best = ready[0]
        notes.append(f"Ready sidecar candidate found: {best.get('gate')} / {best.get('policy')}.")
    elif positive:
        best = positive[0]
        notes.append(
            f"Closest positive sidecar is {best.get('gate')} / {best.get('policy')} with "
            f"{best.get('settled')} settled, net {best.get('net_cents')}c, sim share {best.get('simulated_share')}, "
            f"delta live {best.get('delta_vs_live_cents')}c, "
            f"missing {best.get('missing_gates')}."
        )
    else:
        notes.append("No positive sidecar rows are currently available.")
    return notes


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number * 100.0:.1f}%"


def money(value: Any) -> str:
    number = as_float(value) or 0.0
    return f"{number:.0f}c (${number / 100.0:.2f})"


def wl(row: dict[str, Any]) -> str:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None and losses is None:
        return "n/a"
    return f"{wins or 0}/{losses or 0}"


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Sidecar Live-Test Watch",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Requirements: `{report.get('requirements')}`",
        f"- Counts: `{report.get('counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for title, rows in [
        ("Closest Positive Sidecars", report.get("closest_positive") or []),
        ("Top Net Sidecars", report.get("top_net") or []),
    ]:
        lines.extend([
            "",
            f"## {title}",
            "",
            "| rank | gate | policy | settled | W/L | coverage | net | delta live | sim share | cushion | ready | missing gates |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for idx, row in enumerate(rows, start=1):
            lines.append(
                f"| {idx} | `{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | {wl(row)} | "
                f"{fmt_pct((as_float(row.get('coverage_pct')) or 0.0) / 100.0) if row.get('coverage_pct') is not None else 'n/a'} | "
                f"{money(row.get('net_cents'))} | {money(row.get('delta_vs_live_cents'))} | {fmt_pct(row.get('simulated_share'))} | "
                f"{row.get('full_loss_cushion')} | {row.get('sidecar_ready')} | {', '.join(row.get('missing_gates') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
