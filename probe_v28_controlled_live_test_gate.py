"""Controlled live-test gate for v28 shadow candidates.

Research-only; this probe never places orders or edits live bot logic.

The user is open to controlled live testing when a shadow strategy is genuinely
ready. This scorecard keeps that decision tied to the frozen-forward gates
instead of diagnostic PnL.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
OUT_MD = OUT_DIR / "v28_controlled_live_test_gate_latest.md"

MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
MAX_RECON_SHARE = 0.35
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(value: Any) -> int:
    return int(fnum(value))


def live_net_cents(live: dict[str, Any]) -> float:
    return 100.0 * fnum(live.get("net_pnl_total_dollars"))


def full_loss_cushion(row: dict[str, Any]) -> int:
    return int(max(0.0, fnum(row.get("net_cents_after_entry_fee"))) // 100.0)


def wl(row: dict[str, Any]) -> str:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None and losses is None:
        return ""
    return f"{inum(wins)}/{inum(losses)}"


def has_settled_pnl(row: dict[str, Any]) -> bool:
    return inum(row.get("settled")) > 0 and row.get("net_cents_after_entry_fee") is not None


def sidecar_candidate_row(row: dict[str, Any]) -> bool:
    gate = str(row.get("gate") or "")
    policy = str(row.get("policy") or "")
    blockers = {str(item) for item in row.get("blockers") or []}
    if gate.startswith("exit_"):
        return False
    if policy.startswith("diagnostic_"):
        return False
    if "diagnostic_only_prefreeze" in blockers:
        return False
    if "diagnostic_bakeoff" in blockers or "not_fresh_forward_gate" in blockers:
        return False
    return has_settled_pnl(row)


def missing_hard_gates(row: dict[str, Any], live_cents: float, require_target: bool = True) -> list[str]:
    missing: list[str] = []
    settled = inum(row.get("settled"))
    net = fnum(row.get("net_cents_after_entry_fee"))
    coverage = row.get("coverage_pct")
    coverage_f = fnum(coverage) if coverage is not None else None
    recon = row.get("simulated_share")
    recon_f = fnum(recon) if recon is not None else None

    if not bool(row.get("live_ready")):
        missing.append("live_ready_false")
    if not bool(row.get("strict_forward")):
        missing.append("not_strict_forward")
    if settled < MIN_SETTLED:
        missing.append("settled_lt_30")
    if net <= 0:
        missing.append("net_not_positive")
    if full_loss_cushion(row) < MIN_FULL_LOSS_CUSHION:
        missing.append("full_loss_cushion_lt_3")
    if recon_f is None:
        missing.append("source_share_unknown")
    elif recon_f > MAX_RECON_SHARE:
        missing.append("reconstructed_share_gt_35pct")
    if require_target:
        if coverage_f is None:
            missing.append("coverage_unknown")
        elif coverage_f < TARGET_COVERAGE_MIN:
            missing.append("coverage_lt_75pct")
        elif coverage_f > TARGET_COVERAGE_MAX:
            missing.append("coverage_gt_90pct")
    if net <= live_cents:
        missing.append("does_not_beat_refreshed_live_baseline")

    for blocker in row.get("blockers") or []:
        if blocker and blocker not in missing:
            missing.append(str(blocker))
    return missing


def compact_row(row: dict[str, Any], live_cents: float, require_target: bool = True) -> dict[str, Any]:
    net = fnum(row.get("net_cents_after_entry_fee"))
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": inum(row.get("entries")),
        "settled": inum(row.get("settled")),
        "wins_losses": wl(row),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "reconstructed_share": row.get("simulated_share"),
        "full_loss_cushion": full_loss_cushion(row),
        "live_ready": bool(row.get("live_ready")),
        "strict_forward": bool(row.get("strict_forward")),
        "target_coverage": bool(row.get("target_coverage")),
        "missing_gates": missing_hard_gates(row, live_cents, require_target=require_target),
    }


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        len(row.get("missing_gates") or []),
        -fnum(row.get("net_cents")),
        -fnum(row.get("coverage_pct")),
        row.get("gate") or "",
        row.get("policy") or "",
    )


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    live_cents = live_net_cents(live)
    rows = [row for row in tracker.get("rows") or [] if isinstance(row, dict)]

    broad = [compact_row(row, live_cents, require_target=True) for row in rows]
    broad.sort(key=sort_key)
    sidecar = [compact_row(row, live_cents, require_target=False) for row in rows if sidecar_candidate_row(row)]
    sidecar.sort(key=sort_key)

    broad_eligible = [row for row in broad if not row["missing_gates"]]
    sidecar_eligible = [row for row in sidecar if not row["missing_gates"]]
    top_pnl = sorted(
        [compact_row(row, live_cents, require_target=True) for row in rows if row.get("has_settled_pnl")],
        key=lambda row: -fnum(row.get("net_cents")),
    )[:12]

    decision = "no_live_test"
    if broad_eligible:
        decision = "broad_candidate_live_test_review"
    elif sidecar_eligible:
        decision = "sidecar_candidate_live_test_review"

    report = {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Controlled live-test readiness gate. Research-only; no orders.",
        "decision": decision,
        "live_baseline": {
            "strategy_tag": live.get("strategy_tag"),
            "score_mode": live.get("score_mode"),
            "entries_total": live.get("entries_total"),
            "completed_round_trips": live.get("completed_round_trips"),
            "net_cents": live_cents,
            "open_positions": live.get("open_positions"),
            "diagnosis": live.get("diagnosis"),
        },
        "counts": {
            "candidate_rows": len(rows),
            "broad_eligible": len(broad_eligible),
            "sidecar_eligible": len(sidecar_eligible),
            "tracker_live_ready_rows": sum(1 for row in rows if row.get("live_ready")),
            "positive_rows": sum(1 for row in rows if fnum(row.get("net_cents_after_entry_fee")) > 0),
            "positive_target_rows": sum(
                1
                for row in rows
                if fnum(row.get("net_cents_after_entry_fee")) > 0 and row.get("target_coverage")
            ),
        },
        "interpretation": [],
        "broad_eligible": broad_eligible,
        "sidecar_eligible": sidecar_eligible,
        "closest_broad": broad[:15],
        "closest_sidecar": sidecar[:15],
        "top_pnl_reference": top_pnl,
    }

    if decision == "no_live_test":
        report["interpretation"].append(
            "No candidate clears the controlled live-test gates; do not place live candidate trades."
        )
    else:
        report["interpretation"].append(
            "At least one candidate clears the scorecard gates and should be reviewed before any controlled live test."
        )
    if broad[:1]:
        first = broad[0]
        report["interpretation"].append(
            f"Closest broad row is {first['gate']} / {first['policy']} with net {first['net_cents']}c, "
            f"W/L {first['wins_losses']}, coverage {first['coverage_pct']}%, and missing gates {first['missing_gates']}."
        )
    if sidecar[:1]:
        first = sidecar[0]
        report["interpretation"].append(
            f"Closest sidecar row is {first['gate']} / {first['policy']} with net {first['net_cents']}c, "
            f"W/L {first['wins_losses']}, source share {first['reconstructed_share']}, and missing gates {first['missing_gates']}."
        )
    if top_pnl[:1]:
        first = top_pnl[0]
        report["interpretation"].append(
            f"Top PnL row remains {first['gate']} / {first['policy']} at {first['net_cents']}c, "
            f"but missing gates are {first['missing_gates']}."
        )
    return report


def fmt_cents(value: Any) -> str:
    return f"{fnum(value):.0f}c"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def table(rows: list[dict[str, Any]]) -> list[str]:
        out = [
            "| gate | policy | settled | W/L | coverage | net | delta live | recon | cushion | missing gates |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
        for row in rows:
            out.append(
                "| "
                f"`{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | "
                f"{row.get('wins_losses') or 'n/a'} | {fmt_pct(row.get('coverage_pct'))} | "
                f"{fmt_cents(row.get('net_cents'))} | {fmt_cents(row.get('delta_vs_live_cents'))} | "
                f"{fmt_pct(100.0 * fnum(row.get('reconstructed_share'))) if row.get('reconstructed_share') is not None else 'n/a'} | "
                f"{row.get('full_loss_cushion')} | {', '.join(row.get('missing_gates') or []) or 'none'} |"
            )
        return out

    live = report.get("live_baseline") or {}
    counts = report.get("counts") or {}
    lines = [
        "# v28 Controlled Live-Test Gate",
        "",
        "Research-only. This probe does not place orders or edit live bot logic.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Live baseline: `{fmt_cents(live.get('net_cents'))}` from `{live.get('strategy_tag')}` / `{live.get('score_mode')}`",
        f"- Open live positions: `{live.get('open_positions')}`",
        f"- Candidate rows: `{counts.get('candidate_rows')}`",
        f"- Broad eligible: `{counts.get('broad_eligible')}`",
        f"- Sidecar eligible: `{counts.get('sidecar_eligible')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(["", "## Broad Eligible", ""])
    lines.extend(table(report.get("broad_eligible") or []))
    lines.extend(["", "## Sidecar Eligible", ""])
    lines.extend(table(report.get("sidecar_eligible") or []))
    lines.extend(["", "## Closest Broad Rows", ""])
    lines.extend(table(report.get("closest_broad") or []))
    lines.extend(["", "## Closest Sidecar Rows", ""])
    lines.extend(table(report.get("closest_sidecar") or []))
    lines.extend(["", "## Top PnL Reference", ""])
    lines.extend(table(report.get("top_pnl_reference") or []))
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
