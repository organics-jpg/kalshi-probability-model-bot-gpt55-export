"""Promotion audit for the current target-coverage v28 FV candidate.

Research-only; no live bot changes or orders.

This is a narrow acceptance checklist for the strongest current candidate:
    raw_p50_turbulence_valve_edge4_p60_recross75_near25
    + entry_conditioned_logit125_p60_only_probability

It does not approve promotion. It simply makes the remaining blockers explicit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_promotion_audit_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_promotion_audit_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
MIN_NET_CENTS = 0.0


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


def check(name: str, passed: bool, actual: Any, required: Any, evidence: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "evidence": evidence,
    }


def build_report() -> dict[str, Any]:
    seq = load_json(SEQ_JSON)
    live = load_json(LIVE_READINESS_JSON)
    brier = seq.get("brier") or {}
    logloss = seq.get("logloss") or {}
    b_boot = brier.get("bootstrap") or {}
    l_boot = logloss.get("bootstrap") or {}
    settled = int(as_float(seq.get("settled_rows")) or 0)
    coverage = as_float(seq.get("coverage_pct"))
    net = as_float(seq.get("net_cents_after_entry_fee"))
    brier_p95 = as_float(b_boot.get("p95"))
    logloss_p95 = as_float(l_boot.get("p95"))
    any_live_ready = live.get("any_live_ready")
    checks = [
        check(
            "target_coverage_band",
            coverage is not None and COVERAGE_MIN <= coverage <= COVERAGE_MAX,
            coverage,
            f"{COVERAGE_MIN}-{COVERAGE_MAX}",
            str(SEQ_JSON),
        ),
        check(
            "settled_forward_sample",
            settled >= MIN_SETTLED,
            settled,
            f">= {MIN_SETTLED}",
            str(SEQ_JSON),
        ),
        check(
            "positive_forward_pnl",
            net is not None and net > MIN_NET_CENTS,
            net,
            f"> {MIN_NET_CENTS}",
            str(SEQ_JSON),
        ),
        check(
            "brier_interval_strictly_better_than_raw",
            brier_p95 is not None and brier_p95 < 0.0,
            brier_p95,
            "< 0",
            str(SEQ_JSON),
        ),
        check(
            "logloss_interval_strictly_better_than_raw",
            logloss_p95 is not None and logloss_p95 < 0.0,
            logloss_p95,
            "< 0",
            str(SEQ_JSON),
        ),
        check(
            "live_gate_not_accidentally_ready",
            any_live_ready is False,
            any_live_ready,
            "False until all blockers clear intentionally",
            str(LIVE_READINESS_JSON),
        ),
    ]
    ready = all(item["passed"] for item in checks[:-1])
    return {
        "candidate": {
            "policy": seq.get("policy"),
            "overlay": seq.get("overlay"),
            "entries": seq.get("entries"),
            "settled_rows": settled,
            "coverage_pct": coverage,
            "net_cents_after_entry_fee": net,
            "brier_mean_delta": brier.get("mean_delta"),
            "brier_p95_delta": brier_p95,
            "logloss_mean_delta": logloss.get("mean_delta"),
            "logloss_p95_delta": logloss_p95,
        },
        "ready_for_promotion_review": ready,
        "checks": checks,
        "remaining": {
            "settled_rows_to_30": max(0, MIN_SETTLED - settled),
        },
        "notes": [
            "This is only a promotion-review audit; it does not change live behavior.",
            "The live-readiness gate should remain false until sample size and risk controls are intentionally cleared.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    c = report.get("candidate") or {}
    lines = [
        "# v28 Target-Coverage Promotion Audit",
        "",
        f"- Ready for promotion review: `{report.get('ready_for_promotion_review')}`",
        f"- Policy: `{c.get('policy')}`",
        f"- Overlay: `{c.get('overlay')}`",
        f"- Entries/settled/coverage: `{c.get('entries')}/{c.get('settled_rows')}/{fmt(c.get('coverage_pct'))}`",
        f"- Net cents: `{fmt(c.get('net_cents_after_entry_fee'))}`",
        f"- Brier mean/p95: `{fmt(c.get('brier_mean_delta'))}/{fmt(c.get('brier_p95_delta'))}`",
        f"- Logloss mean/p95: `{fmt(c.get('logloss_mean_delta'))}/{fmt(c.get('logloss_p95_delta'))}`",
        f"- Settled rows to 30: `{(report.get('remaining') or {}).get('settled_rows_to_30')}`",
        "",
        "## Checks",
        "",
        "| check | pass | actual | required | evidence |",
        "|---|---:|---|---|---|",
    ]
    for item in report.get("checks") or []:
        lines.append(
            f"| {item.get('name')} | {item.get('passed')} | `{item.get('actual')}` | `{item.get('required')}` | {item.get('evidence')} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in report.get("notes") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
