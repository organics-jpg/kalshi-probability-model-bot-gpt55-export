"""Full-policy scorecard for the leading v28-derived candidates.

Research-only; this probe never places orders or edits live bot logic.

The candidate tracker has many entry, exit, sizing, and overlay rows. This
report turns the strongest existing rows into complete policy cards so the next
decision is tied to an end-to-end strategy contract rather than an isolated
component win.
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
READINESS_JSON = OUT_DIR / "v28_candidate_readiness_distance_latest.json"
EXIT_DASHBOARD_JSON = OUT_DIR / "v28_exit_policy_watch_dashboard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
OUT_MD = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_EXITS = 30
MAX_RECON_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
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


def live_net_cents() -> float:
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def full_loss_cushion(net_cents: Any) -> int:
    return int(max(0.0, fnum(net_cents)) // 100.0)


def row_id(row: dict[str, Any]) -> str:
    gate = row.get("gate") or row.get("lane") or ""
    policy = row.get("policy") or row.get("candidate") or ""
    return f"{gate}::{policy}"


def compact_tracker_row(row: dict[str, Any], live_cents: float) -> dict[str, Any]:
    net = fnum(row.get("net_cents_after_entry_fee"))
    return {
        "source": "candidate_tracker",
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": inum(row.get("entries")),
        "settled": inum(row.get("settled")),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "reconstructed_share": row.get("simulated_share"),
        "full_loss_cushion": row.get("full_loss_cushion_estimate", full_loss_cushion(net)),
        "live_ready": bool(row.get("live_ready")),
        "strict_forward": bool(row.get("strict_forward")),
        "target_coverage": bool(row.get("target_coverage")),
        "blockers": list(row.get("blockers") or []),
        "candidate_type": "exit_policy" if str(row.get("gate") or "").startswith("exit_") else "entry_or_stack",
    }


def compact_gate_row(row: dict[str, Any], live_cents: float) -> dict[str, Any]:
    net = fnum(row.get("net_cents"))
    return {
        "source": "controlled_live_test_gate",
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": inum(row.get("entries")),
        "settled": inum(row.get("settled")),
        "wins_losses": row.get("wins_losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_live_cents": fnum(row.get("delta_vs_live_cents"), net - live_cents),
        "reconstructed_share": row.get("reconstructed_share"),
        "full_loss_cushion": row.get("full_loss_cushion", full_loss_cushion(net)),
        "live_ready": bool(row.get("live_ready")),
        "strict_forward": bool(row.get("strict_forward")),
        "target_coverage": bool(row.get("target_coverage")),
        "blockers": list(row.get("missing_gates") or []),
        "candidate_type": "entry_or_stack",
    }


def compact_exit_row(row: dict[str, Any]) -> dict[str, Any]:
    net = fnum(row.get("candidate_net_cents"))
    return {
        "source": "exit_policy_watch_dashboard",
        "gate": row.get("lane"),
        "policy": row.get("candidate"),
        "entries": inum(row.get("rows")),
        "settled": inum(row.get("settled")),
        "coverage_pct": None,
        "net_cents": net,
        "delta_vs_current_cents": fnum(row.get("delta_vs_current_cents")),
        "loss_control_cost_cents": fnum(row.get("loss_control_cost_cents")),
        "suppressed_exits": inum(row.get("suppressed_exits")),
        "full_loss_cushion": row.get("full_loss_cushion", full_loss_cushion(net)),
        "status": row.get("status"),
        "live_ready": False,
        "strict_forward": True,
        "target_coverage": False,
        "blockers": list(row.get("blockers") or []),
        "candidate_type": "exit_policy",
    }


def infer_entry_rule(card: dict[str, Any]) -> str:
    gate = str(card.get("gate") or "")
    policy = str(card.get("policy") or "")
    if card.get("candidate_type") == "exit_policy" or gate.startswith("common_clock"):
        return "Current live v28 approved entry stream."
    if "dual_lane_overlap" in gate:
        return "Existing dual-lane overlap/portfolio entry stack from frozen dual-lane artifacts."
    if "soft_frontier" in gate or "midprice" in policy:
        return "Existing soft-frontier or midprice-boundary v28-derived entry stack."
    if "top_component" in gate:
        return "Existing top-component parent/fill or false-negative-rescue entry stack."
    if "approved_entry" in gate:
        return "Existing approved-entry v28 stream with the named FV overlay."
    if "feature_gate" in gate:
        return "Existing boundary-clock/feature-gate v28-derived entry stream."
    return f"Existing candidate entry policy: {gate} / {policy}."


def infer_exit_rule(card: dict[str, Any]) -> str:
    gate = str(card.get("gate") or "")
    policy = str(card.get("policy") or "")
    if card.get("candidate_type") == "exit_policy" or gate.startswith("common_clock"):
        return f"Replace or suppress selected current v28 exits using {policy}."
    if "delayed_recheck" in gate or "delay" in policy:
        return "Use the frozen delayed/rechecked exit rule named in the policy; otherwise current v28 exits."
    if "exit_stack" in gate or "book_gap" in policy or "rescue" in policy:
        return "Use the existing candidate exit stack/rescue rule from its frozen artifact; otherwise current v28 exits."
    return "Current live v28 exit/state machine."


def infer_sizing_rule(card: dict[str, Any]) -> str:
    gate = str(card.get("gate") or "")
    policy = str(card.get("policy") or "")
    text = f"{gate} {policy}".lower()
    if "quarter" in text:
        return "Quarter-size notional on the candidate's named risk slice; base size otherwise."
    if "half" in text:
        return "Half-size notional on the candidate's named risk slice; base size otherwise."
    if "shrink" in text or "penalty" in text:
        return "Candidate-specific continuous shrink/penalty sizing from the frozen artifact."
    return "Current controlled v28 size discipline unless a future live-test spec narrows to size 1."


def risk_kill_rule(card: dict[str, Any]) -> str:
    blockers = set(str(item) for item in card.get("blockers") or [])
    reasons = []
    if "live_ready_false" in blockers or not card.get("live_ready"):
        reasons.append("not live-ready")
    if "not_strict_forward" in blockers or not card.get("strict_forward"):
        reasons.append("insufficient strict-forward evidence")
    recon = card.get("reconstructed_share")
    if recon is not None and fnum(recon) > MAX_RECON_SHARE:
        reasons.append("source share above 35%")
    if inum(card.get("settled")) < MIN_SETTLED:
        reasons.append("sample below 30 settled")
    if inum(card.get("full_loss_cushion")) < MIN_FULL_LOSS_CUSHION:
        reasons.append("full-loss cushion below 3")
    if card.get("candidate_type") == "exit_policy":
        if inum(card.get("suppressed_exits")) < MIN_SUPPRESSED_EXITS:
            reasons.append("suppressed exit decisions below 30")
        if fnum(card.get("loss_control_cost_cents")) < 0:
            reasons.append("loss-control cost present")
    if not reasons:
        reasons.append("eligible for manual review only")
    return "Kill or block live testing while " + "; ".join(reasons) + "."


def live_test_rule(card: dict[str, Any]) -> str:
    if card.get("live_ready"):
        return "Manual review required before a separate size-controlled live sidecar with its own logs and scorer."
    return "No live candidate trades. Continue frozen forward collection in separate research artifacts."


def accounting_rule(card: dict[str, Any]) -> str:
    if card.get("candidate_type") == "exit_policy":
        return "Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted."
    return "Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees."


def iteration_rule(card: dict[str, Any]) -> str:
    if card.get("candidate_type") == "exit_policy":
        return "Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review."
    blockers = set(str(item) for item in card.get("blockers") or [])
    if "not_strict_forward" in blockers or "diagnostic_prefreeze" in blockers:
        return "Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy."
    return "Keep versioned as its own policy; only tweak thresholds after an independent scorecard names the blocker."


def candidate_missing_gates(card: dict[str, Any], live_cents: float) -> list[str]:
    missing: list[str] = []
    net = fnum(card.get("net_cents"))
    if not card.get("live_ready"):
        missing.append("live_ready_false")
    if not card.get("strict_forward"):
        missing.append("not_strict_forward")
    if inum(card.get("settled")) < MIN_SETTLED:
        missing.append("settled_lt_30")
    if net <= 0:
        missing.append("net_not_positive")
    if card.get("candidate_type") != "exit_policy":
        coverage = card.get("coverage_pct")
        if coverage is None:
            missing.append("coverage_unknown")
        elif fnum(coverage) < TARGET_COVERAGE_MIN:
            missing.append("coverage_lt_75")
        elif fnum(coverage) > TARGET_COVERAGE_MAX:
            missing.append("coverage_gt_90")
        recon = card.get("reconstructed_share")
        if recon is None:
            missing.append("source_share_unknown")
        elif fnum(recon) > MAX_RECON_SHARE:
            missing.append("source_share_gt_35pct")
        if net <= live_cents:
            missing.append("does_not_beat_refreshed_live_baseline")
    else:
        if inum(card.get("suppressed_exits")) < MIN_SUPPRESSED_EXITS:
            missing.append("suppressed_decisions_lt_30")
        if fnum(card.get("delta_vs_current_cents")) <= 0:
            missing.append("delta_vs_current_not_positive")
        if fnum(card.get("loss_control_cost_cents")) < 0:
            missing.append("loss_control_cost_negative")
    if inum(card.get("full_loss_cushion")) < MIN_FULL_LOSS_CUSHION:
        missing.append("full_loss_cushion_lt_3")
    for blocker in card.get("blockers") or []:
        if blocker and blocker not in missing:
            missing.append(str(blocker))
    return missing


def build_policy_card(card: dict[str, Any], live_cents: float) -> dict[str, Any]:
    missing = candidate_missing_gates(card, live_cents)
    return {
        "gate": card.get("gate"),
        "policy": card.get("policy"),
        "source": card.get("source"),
        "candidate_type": card.get("candidate_type"),
        "evidence": {
            "entries": card.get("entries"),
            "settled": card.get("settled"),
            "wins": card.get("wins"),
            "losses": card.get("losses"),
            "wins_losses": card.get("wins_losses"),
            "coverage_pct": card.get("coverage_pct"),
            "net_cents": card.get("net_cents"),
            "delta_vs_live_cents": card.get("delta_vs_live_cents"),
            "delta_vs_current_cents": card.get("delta_vs_current_cents"),
            "reconstructed_share": card.get("reconstructed_share"),
            "full_loss_cushion": card.get("full_loss_cushion"),
            "suppressed_exits": card.get("suppressed_exits"),
            "loss_control_cost_cents": card.get("loss_control_cost_cents"),
        },
        "full_policy": {
            "entry_rule": infer_entry_rule(card),
            "exit_state_rule": infer_exit_rule(card),
            "sizing_rule": infer_sizing_rule(card),
            "risk_kill_rule": risk_kill_rule(card),
            "live_test_rule": live_test_rule(card),
            "accounting_pnl_rule": accounting_rule(card),
            "iteration_rule": iteration_rule(card),
        },
        "missing_gates": missing,
        "live_test_allowed": not missing,
    }


def unique_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for card in cards:
        key = row_id(card)
        if key in seen:
            continue
        seen.add(key)
        out.append(card)
    return out


def build_report() -> dict[str, Any]:
    live_cents = live_net_cents()
    tracker = load_json(TRACKER_JSON)
    gate = load_json(CONTROLLED_GATE_JSON)
    readiness = load_json(READINESS_JSON)
    exit_dash = load_json(EXIT_DASHBOARD_JSON)
    tracker_rows = [row for row in tracker.get("rows") or [] if isinstance(row, dict)]

    cards: list[dict[str, Any]] = []
    for row in gate.get("closest_broad") or []:
        cards.append(compact_gate_row(row, live_cents))
    for row in gate.get("closest_sidecar") or []:
        cards.append(compact_gate_row(row, live_cents))
    for row in gate.get("top_pnl_reference") or []:
        cards.append(compact_gate_row(row, live_cents))
    for row in readiness.get("closest_broad_positive") or []:
        cards.append(
            {
                "source": "candidate_readiness_distance",
                "gate": row.get("gate"),
                "policy": row.get("policy"),
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "wins": row.get("wins"),
                "losses": row.get("losses"),
                "coverage_pct": row.get("coverage_pct"),
                "net_cents": row.get("net_cents"),
                "delta_vs_live_cents": fnum(row.get("net_cents")) - live_cents,
                "reconstructed_share": row.get("simulated_share"),
                "full_loss_cushion": row.get("full_loss_cushion_estimate"),
                "live_ready": bool(row.get("live_ready")),
                "strict_forward": False,
                "target_coverage": True,
                "blockers": list(row.get("blockers") or []) + list(row.get("missing_gates") or []),
                "candidate_type": row.get("candidate_type") or "entry_or_stack",
            }
        )
    for row in exit_dash.get("rows") or []:
        if fnum(row.get("delta_vs_current_cents")) > 0 or row.get("status") == "forward_positive_under_review":
            cards.append(compact_exit_row(row))
    for row in tracker_rows:
        if row.get("live_ready") or row.get("gate") == "approved_entry_book_raw_blend_fv":
            cards.append(compact_tracker_row(row, live_cents))

    cards = unique_cards(cards)
    policy_cards = [build_policy_card(card, live_cents) for card in cards]

    def sort_key(card: dict[str, Any]) -> tuple[Any, ...]:
        evidence = card.get("evidence") or {}
        return (
            len(card.get("missing_gates") or []),
            not bool(card.get("live_test_allowed")),
            -fnum(evidence.get("net_cents")),
            str(card.get("gate") or ""),
            str(card.get("policy") or ""),
        )

    policy_cards.sort(key=sort_key)

    live_allowed = [card for card in policy_cards if card.get("live_test_allowed")]
    closest = policy_cards[:12]
    report = {
        "generated_at_utc": utc_now_iso(),
        "purpose": "End-to-end policy cards for existing v28-derived candidates. Research-only; no orders.",
        "live_baseline_cents": live_cents,
        "candidate_cards": len(policy_cards),
        "live_test_allowed_count": len(live_allowed),
        "decision": "no_live_test" if not live_allowed else "manual_live_test_review_required",
        "interpretation": [],
        "closest_policy_cards": closest,
        "all_policy_cards": policy_cards,
        "sources": {
            "tracker": str(TRACKER_JSON),
            "controlled_gate": str(CONTROLLED_GATE_JSON),
            "readiness": str(READINESS_JSON),
            "exit_dashboard": str(EXIT_DASHBOARD_JSON),
            "live_summary": str(LIVE_SUMMARY_JSON),
        },
    }
    if not live_allowed:
        report["interpretation"].append(
            "No complete policy card clears the live-test gates; continue frozen forward collection."
        )
    else:
        report["interpretation"].append(
            "At least one policy card clears this report; review exchange/accounting risk before any live test."
        )
    if closest:
        first = closest[0]
        report["interpretation"].append(
            f"Closest full policy is {first['gate']} / {first['policy']} with missing gates {first['missing_gates']}."
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
    lines: list[str] = []
    lines.append("# v28 Full-Policy Candidate Scorecard")
    lines.append("")
    lines.append("Research-only. This probe does not place orders or edit live bot logic.")
    lines.append("")
    lines.append(f"- Generated UTC: `{report['generated_at_utc']}`")
    lines.append(f"- Decision: `{report['decision']}`")
    lines.append(f"- Live baseline: `{fmt_cents(report['live_baseline_cents'])}`")
    lines.append(f"- Candidate cards: `{report['candidate_cards']}`")
    lines.append(f"- Live-test allowed cards: `{report['live_test_allowed_count']}`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    for item in report.get("interpretation") or []:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Closest Full Policies")
    lines.append("")
    lines.append(
        "| gate | policy | source | settled | net | delta live/current | coverage | recon | suppressions | missing gates |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|")
    for card in report.get("closest_policy_cards") or []:
        ev = card.get("evidence") or {}
        delta = ev.get("delta_vs_live_cents")
        if delta is None:
            delta = ev.get("delta_vs_current_cents")
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{card.get('gate')}`",
                    f"`{card.get('policy')}`",
                    str(card.get("source")),
                    str(ev.get("settled") or 0),
                    fmt_cents(ev.get("net_cents")),
                    fmt_cents(delta),
                    fmt_pct(ev.get("coverage_pct")),
                    fmt_pct(100.0 * fnum(ev.get("reconstructed_share"))) if ev.get("reconstructed_share") is not None else "n/a",
                    str(ev.get("suppressed_exits") or ""),
                    ", ".join(card.get("missing_gates") or []),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Policy Contracts")
    lines.append("")
    for card in report.get("closest_policy_cards") or []:
        lines.append(f"### `{card.get('gate')} / {card.get('policy')}`")
        lines.append("")
        for key, value in (card.get("full_policy") or {}).items():
            label = key.replace("_", " ")
            lines.append(f"- {label}: {value}")
        lines.append(f"- missing gates: {', '.join(card.get('missing_gates') or [])}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
