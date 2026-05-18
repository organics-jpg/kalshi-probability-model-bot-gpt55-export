"""Runway check for the closest v28 full-policy candidate.

Research-only; this probe never places orders or edits live bot logic.

The current full-policy scorecard identifies the common-clock loss guard as the
nearest complete policy. This report keeps that exact candidate honest by
checking only strict forward common-clock windows and spelling out the remaining
row-density, loss-control, cushion, and live-test blockers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMMON_CLOCK_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"
FULL_POLICY_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_common_clock_exit_guard_runway_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_exit_guard_runway_latest.md"

TARGET_POLICY = "loss_guard_value_p85_reduce_p79_gap0"
STRICT_WINDOW_PREFIX = "new_exit_mix_common_forward"
MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION = 3


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


def live_net_cents() -> float:
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def find_target_summary(window: dict[str, Any]) -> dict[str, Any] | None:
    for summary in window.get("summaries") or []:
        if isinstance(summary, dict) and summary.get("policy") == TARGET_POLICY:
            return summary
    return None


def classify_row(window: dict[str, Any], summary: dict[str, Any], live_ready: bool) -> dict[str, Any]:
    settled = max(inum(summary.get("settled")), inum(window.get("row_count")))
    suppressed = inum(summary.get("suppressed_exits"))
    current_cents = fnum(summary.get("current_gross_cents"))
    candidate_cents = fnum(summary.get("candidate_gross_cents"))
    delta_cents = fnum(summary.get("delta_vs_current_cents"))
    loss_cost = fnum(summary.get("loss_control_cost_cents"))
    cushion = inum(summary.get("full_loss_cushion_estimate"))
    harmful = inum(summary.get("harmful_suppressed_rows"))
    helpful = inum(summary.get("helpful_suppressed_rows"))

    missing: list[str] = []
    if not live_ready:
        missing.append("live_ready_false")
    if settled < MIN_SETTLED:
        missing.append(f"settled_needed_{MIN_SETTLED - settled}")
    if suppressed < MIN_SUPPRESSED_DECISIONS:
        missing.append(f"suppressed_needed_{MIN_SUPPRESSED_DECISIONS - suppressed}")
    if candidate_cents <= 0:
        missing.append("candidate_net_not_positive")
    if delta_cents <= 0:
        missing.append("delta_vs_current_not_positive")
    if loss_cost < 0:
        missing.append("loss_control_cost_negative")
    if harmful > 0:
        missing.append("harmful_suppressed_rows_present")
    if cushion < MIN_FULL_LOSS_CUSHION:
        missing.append(f"cushion_needed_{MIN_FULL_LOSS_CUSHION - cushion}")

    review_ready_except_global_live = (
        missing == ["live_ready_false"]
        or (not missing and not live_ready)
    )
    return {
        "window": window.get("window"),
        "freeze_ts_utc": window.get("freeze_ts_utc"),
        "settled": settled,
        "current_cents": current_cents,
        "candidate_cents": candidate_cents,
        "delta_vs_current_cents": delta_cents,
        "current_wl": f"{inum(summary.get('current_wins'))}/{inum(summary.get('current_losses'))}",
        "candidate_wl": f"{inum(summary.get('candidate_wins'))}/{inum(summary.get('candidate_losses'))}",
        "suppressed_exits": suppressed,
        "helpful_suppressed_rows": helpful,
        "harmful_suppressed_rows": harmful,
        "loss_control_cost_cents": loss_cost,
        "full_loss_cushion": cushion,
        "blockers_from_source": list(summary.get("blockers") or []),
        "missing_gates": missing,
        "review_ready_except_global_live": review_ready_except_global_live,
    }


def build_report() -> dict[str, Any]:
    common = load_json(COMMON_CLOCK_JSON)
    full = load_json(FULL_POLICY_JSON)
    live_cents = live_net_cents()
    live_ready = any(card.get("live_test_allowed") for card in full.get("all_policy_cards") or [])

    rows: list[dict[str, Any]] = []
    for window in common.get("windows") or []:
        if not isinstance(window, dict):
            continue
        name = str(window.get("window") or "")
        if not name.startswith(STRICT_WINDOW_PREFIX):
            continue
        summary = find_target_summary(window)
        if summary:
            rows.append(classify_row(window, summary, live_ready=live_ready))

    rows.sort(key=lambda row: (len(row["missing_gates"]), -row["candidate_cents"], row["window"]))
    best = rows[0] if rows else None
    decision = "wait_for_forward_density"
    if best and best["review_ready_except_global_live"]:
        decision = "exit_policy_review_ready_after_global_live_gate"
    if best and not best["missing_gates"]:
        decision = "manual_live_test_review_required"

    report = {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Strict-forward runway for the nearest full-policy exit candidate. Research-only; no orders.",
        "target_policy": TARGET_POLICY,
        "live_baseline_cents": live_cents,
        "decision": decision,
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED_DECISIONS,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
            "zero_harmful_suppressed_rows": True,
            "non_negative_loss_control_cost": True,
        },
        "interpretation": [],
        "best_window": best,
        "strict_windows": rows,
        "sources": {
            "common_clock": str(COMMON_CLOCK_JSON),
            "full_policy": str(FULL_POLICY_JSON),
            "live_summary": str(LIVE_SUMMARY_JSON),
        },
    }
    if not best:
        report["interpretation"].append("No strict common-clock target-policy rows were found.")
    else:
        report["interpretation"].append(
            f"Best strict window is {best['window']} with {best['suppressed_exits']} suppressions, "
            f"{best['delta_vs_current_cents']}c delta, {best['harmful_suppressed_rows']} harmful suppressions, "
            f"and missing gates {best['missing_gates']}."
        )
        if any(str(item).startswith("suppressed_needed_") for item in best["missing_gates"]):
            needed = MIN_SUPPRESSED_DECISIONS - int(best["suppressed_exits"])
            report["interpretation"].append(
                f"Next concrete requirement: collect {needed} more strict suppressions without adding harmful holds."
            )
    return report


def fmt_cents(value: Any) -> str:
    return f"{fnum(value):.0f}c"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# v28 Common-Clock Exit Guard Runway")
    lines.append("")
    lines.append("Research-only. This probe does not place orders or edit live bot logic.")
    lines.append("")
    lines.append(f"- Generated UTC: `{report['generated_at_utc']}`")
    lines.append(f"- Decision: `{report['decision']}`")
    lines.append(f"- Target policy: `{report['target_policy']}`")
    lines.append(f"- Live baseline: `{fmt_cents(report['live_baseline_cents'])}`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Strict Windows")
    lines.append("")
    lines.append(
        "| window | settled | current | candidate | delta | W/L current | W/L candidate | suppressions | helpful/harmful | loss cost | cushion | missing gates |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in report.get("strict_windows") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['window']}`",
                    str(row["settled"]),
                    fmt_cents(row["current_cents"]),
                    fmt_cents(row["candidate_cents"]),
                    fmt_cents(row["delta_vs_current_cents"]),
                    str(row["current_wl"]),
                    str(row["candidate_wl"]),
                    str(row["suppressed_exits"]),
                    f"{row['helpful_suppressed_rows']}/{row['harmful_suppressed_rows']}",
                    fmt_cents(row["loss_control_cost_cents"]),
                    str(row["full_loss_cushion"]),
                    ", ".join(row["missing_gates"]),
                ]
            )
            + " |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
