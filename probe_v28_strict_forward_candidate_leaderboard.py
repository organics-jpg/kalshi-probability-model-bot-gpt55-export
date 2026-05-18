"""Strict-forward candidate leaderboard for v28 research.

Research-only; no live bot changes or orders.

The broad tracker intentionally includes diagnostics, discovery slices, and
frozen forward lanes. This report separates them so promotion discussions are
anchored only on rows that are not explicitly diagnostic/pre-freeze.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
INTEGRITY_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_strict_forward_candidate_leaderboard_latest.json"
OUT_MD = OUT_DIR / "v28_strict_forward_candidate_leaderboard_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

DIAGNOSTIC_BLOCKER_MARKERS = (
    "diagnostic_only",
    "diagnostic_bakeoff",
    "not_fresh_forward_gate",
)


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


def as_int(value: Any) -> int | None:
    value_f = as_float(value)
    if value_f is None:
        return None
    return int(value_f)


def net_cents(row: dict[str, Any]) -> float | None:
    return as_float(row.get("net_cents_after_entry_fee") if "net_cents_after_entry_fee" in row else row.get("net_cents"))


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("gate") or ""), str(row.get("policy") or ""))


def is_diagnostic(row: dict[str, Any]) -> bool:
    policy = str(row.get("policy") or "").lower()
    if policy.startswith("diagnostic_") or "_diagnostic_" in policy:
        return True
    if row.get("strict_forward") is False:
        return True
    blockers = [str(item).lower() for item in row.get("blockers") or []]
    return any(any(marker in blocker for marker in DIAGNOSTIC_BLOCKER_MARKERS) for blocker in blockers)


def source_share(row: dict[str, Any]) -> float | None:
    share = as_float(row.get("simulated_share"))
    if share is not None:
        return share
    approved = as_float(row.get("approved_entry_count"))
    rejected = as_float(row.get("added_reject_count"))
    if approved is None or rejected is None:
        return None
    total = approved + rejected
    if total <= 0:
        return None
    return rejected / total


def full_loss_cushion(row: dict[str, Any]) -> int | None:
    cushion = as_int(row.get("full_loss_cushion_estimate"))
    if cushion is not None:
        return cushion
    net = net_cents(row)
    if net is None or net <= 0:
        return 0
    return int(net // 100.0)


def gate_missing(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    settled = as_int(row.get("settled")) or 0
    coverage = as_float(row.get("coverage_pct"))
    net = net_cents(row)
    share = source_share(row)
    cushion = full_loss_cushion(row)
    if is_diagnostic(row):
        missing.append("strict_forward_evidence")
    if settled < MIN_SETTLED:
        missing.append(f"settled+{MIN_SETTLED - settled}")
    if net is None or net <= 0:
        missing.append("positive_pnl")
    if coverage is not None:
        if coverage < MIN_COVERAGE:
            missing.append(f"coverage_low_by_{MIN_COVERAGE - coverage:.1f}pp")
        elif coverage > MAX_COVERAGE:
            missing.append(f"coverage_high_by_{coverage - MAX_COVERAGE:.1f}pp")
    if coverage is None and not str(row.get("gate") or "").startswith("exit_"):
        missing.append("coverage_unknown")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        missing.append(f"source_share_high_by_{share - MAX_RECONSTRUCTED_SHARE:.2f}")
    elif share is None and not str(row.get("gate") or "").startswith("exit_"):
        missing.append("source_share_unknown")
    if cushion is None or cushion < MIN_FULL_LOSS_CUSHION:
        missing.append(f"cushion+{MIN_FULL_LOSS_CUSHION - (cushion or 0)}")
    if row.get("live_ready") is not True:
        missing.append("live_ready_false")
    return list(dict.fromkeys(missing))


def compact(row: dict[str, Any], integrity: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    integ = integrity.get(row_key(row), {})
    blockers = list(dict.fromkeys([*(row.get("blockers") or []), *(integ.get("blockers") or [])]))
    merged = dict(row)
    merged["blockers"] = blockers
    integ_share = as_float(integ.get("stress_reconstructed_share"))
    if integ_share is not None:
        merged["simulated_share"] = integ_share
    integ_cushion = as_int(integ.get("stress_full_loss_cushion"))
    if integ_cushion is not None:
        merged["full_loss_cushion_estimate"] = integ_cushion
    missing = gate_missing(merged)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": as_float(row.get("coverage_pct")),
        "net_cents": net_cents(row),
        "simulated_share": source_share(merged),
        "full_loss_cushion_estimate": full_loss_cushion(merged),
        "live_ready": row.get("live_ready"),
        "strict_forward": not is_diagnostic(row),
        "target_coverage": row.get("target_coverage"),
        "missing_gates": missing,
        "blockers": blockers,
    }


def readiness_score(row: dict[str, Any]) -> float:
    missing = row.get("missing_gates") or []
    score = 10.0 * len(missing)
    settled = as_float(row.get("settled")) or 0.0
    net = as_float(row.get("net_cents")) or 0.0
    score -= min(settled / 10.0, 5.0)
    score -= min(max(net, 0.0) / 100.0, 8.0)
    return score


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    integrity_payload = load_json(INTEGRITY_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    integrity_rows = {
        row_key(row): row
        for row in integrity_payload.get("candidates") or []
        if isinstance(row, dict)
    }
    rows = [
        compact(row, integrity_rows)
        for row in tracker.get("rows") or []
        if isinstance(row, dict) and net_cents(row) is not None
    ]
    strict = [row for row in rows if row.get("strict_forward")]
    diagnostic = [row for row in rows if not row.get("strict_forward")]
    strict_positive = [row for row in strict if (as_float(row.get("net_cents")) or 0.0) > 0.0]
    strict_target_positive = [
        row for row in strict_positive
        if row.get("target_coverage") is True
    ]
    strict_live_ready = [row for row in strict if row.get("live_ready") is True]
    top_strict = sorted(strict_positive, key=lambda row: as_float(row.get("net_cents")) or -999999.0, reverse=True)[:20]
    closest_target = sorted(strict_target_positive, key=lambda row: readiness_score(row))[:20]
    excluded_diagnostics = sorted(
        diagnostic,
        key=lambda row: as_float(row.get("net_cents")) or -999999.0,
        reverse=True,
    )[:20]
    live_cents = round(float(live.get("net_pnl_total_dollars") or 0.0) * 100.0)
    return {
        "generated_at_utc": utc_now_iso(),
        "live_net_cents": live_cents,
        "summary": {
            "all_rows": len(rows),
            "strict_forward_rows": len(strict),
            "diagnostic_or_prefreeze_rows": len(diagnostic),
            "strict_positive_rows": len(strict_positive),
            "strict_target_positive_rows": len(strict_target_positive),
            "strict_live_ready_rows": len(strict_live_ready),
        },
        "top_strict_forward_positive": top_strict,
        "closest_strict_target_positive": closest_target,
        "excluded_top_diagnostics": excluded_diagnostics,
        "sources": {
            "tracker": str(TRACKER_JSON),
            "integrity": str(INTEGRITY_JSON),
            "live_summary": str(LIVE_SUMMARY_JSON),
        },
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def fmt_pct(value: Any, scale: float = 1.0) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * scale:.2f}%"


def wl(row: dict[str, Any]) -> str:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None or losses is None:
        return "n/a"
    return f"{wins}/{losses}"


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| gate | policy | settled | W/L | coverage | net | recon | cushion | missing gates |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        lines.append(
            "| {gate} | `{policy}` | {settled} | {wl} | {coverage} | {net} | {recon} | {cushion} | {missing} |".format(
                gate=row.get("gate"),
                policy=row.get("policy"),
                settled=row.get("settled"),
                wl=wl(row),
                coverage=fmt_pct(row.get("coverage_pct")),
                net=fmt_cents(row.get("net_cents")),
                recon=fmt_pct(row.get("simulated_share"), 100.0),
                cushion=row.get("full_loss_cushion_estimate"),
                missing=", ".join(row.get("missing_gates") or []) or "none",
            )
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report["summary"]
    lines = [
        "# v28 Strict-Forward Candidate Leaderboard",
        "",
        "Research-only. Diagnostic/pre-freeze rows are excluded from promotion-ranked tables.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Live baseline: `{fmt_cents(report.get('live_net_cents'))}`",
        f"- All tracked rows with PnL: `{summary['all_rows']}`",
        f"- Strict-forward rows: `{summary['strict_forward_rows']}`",
        f"- Diagnostic/pre-freeze rows excluded: `{summary['diagnostic_or_prefreeze_rows']}`",
        f"- Strict positive rows: `{summary['strict_positive_rows']}`",
        f"- Strict target-coverage positive rows: `{summary['strict_target_positive_rows']}`",
        f"- Strict live-ready rows: `{summary['strict_live_ready_rows']}`",
        "",
        "## Top Strict-Forward Positive Rows",
        "",
    ]
    write_table(lines, report.get("top_strict_forward_positive") or [])
    lines.extend([
        "",
        "## Closest Strict Target-Coverage Positive Rows",
        "",
    ])
    write_table(lines, report.get("closest_strict_target_positive") or [])
    lines.extend([
        "",
        "## Excluded Top Diagnostic Rows",
        "",
    ])
    write_table(lines, report.get("excluded_top_diagnostics") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
