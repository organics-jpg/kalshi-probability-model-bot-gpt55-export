"""Full-denominator replay for observable loss-churn exit guards.

Research-only; no live bot changes or orders.

The guarded loss-row frontier can overstate a repair because it only looks at
losses. This replay applies the top observable loss guards to every known
continuous-scorecard row and scores hold-vs-current effects on winners, losers,
and flat rows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
FRONTIER_JSON = OUT_DIR / "v28_loss_churn_guarded_repair_frontier_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_loss_churn_observable_full_denominator_replay_latest.json"
OUT_MD = OUT_DIR / "v28_loss_churn_observable_full_denominator_replay_latest.md"


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


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def value(row: dict[str, Any], field: str) -> float | None:
    if field == "p_hold":
        return None
    if field == "exit_cents" and row.get("exit_cents") is None:
        return None
    if row.get(field) is None:
        return None
    return fnum(row.get(field))


def has_tag(row: dict[str, Any], token: str) -> bool:
    if token == "tag_near_boundary":
        return fnum(row.get("abs_d_sigma"), 99.0) < 1.0
    if token == "tag_recross_high":
        return row.get("h6_recross_hazard_high") is True
    if token == "tag_thin_raw_edge":
        return fnum(row.get("raw_edge_cents")) < 5.0
    if token == "tag_rich_entry":
        return fnum(row.get("ask_cents")) >= 80.0
    if token == "tag_crowded_depth":
        return row.get("h2_crowded_depth") is True
    if token == "tag_thin_touch_depth":
        return row.get("h2_thin_touch_depth") is True
    return False


def token_predicate(token: str) -> Callable[[dict[str, Any]], bool]:
    if token.startswith("tag_"):
        return lambda row: has_tag(row, token)
    if token == "recross_ge_045":
        return lambda row: fnum(row.get("recross_hazard_score"), -1.0) >= 0.45
    if token == "recross_ge_030":
        return lambda row: fnum(row.get("recross_hazard_score"), -1.0) >= 0.30
    if token == "exit_cents_ge_50":
        return lambda row: value(row, "exit_cents") is not None and fnum(row.get("exit_cents")) >= 50
    if token == "exit_cents_ge_60":
        return lambda row: value(row, "exit_cents") is not None and fnum(row.get("exit_cents")) >= 60
    if token == "exit_cents_le_40":
        return lambda row: value(row, "exit_cents") is not None and fnum(row.get("exit_cents")) <= 40
    if token == "ask_cents_ge_70":
        return lambda row: fnum(row.get("ask_cents")) >= 70
    if token == "ask_cents_ge_80":
        return lambda row: fnum(row.get("ask_cents")) >= 80
    if token == "raw_edge_cents_le_10":
        return lambda row: fnum(row.get("raw_edge_cents")) <= 10
    if token == "raw_edge_cents_ge_15":
        return lambda row: fnum(row.get("raw_edge_cents")) >= 15
    if token == "depth_lte_384":
        return lambda row: fnum(row.get("eligible_depth"), 10**9) <= 384
    if token == "depth_lte_150":
        return lambda row: fnum(row.get("eligible_depth"), 10**9) <= 150
    if token == "absd_ge_085":
        return lambda row: fnum(row.get("abs_d_sigma")) >= 0.85
    if token.startswith("not_"):
        # These are diagnostic labels in the loss frontier; exclude from observable replay.
        return lambda row: False
    return lambda row: False


def build_rule(rule: str) -> Callable[[dict[str, Any]], bool]:
    tokens = [token for token in str(rule).split("__and__") if token]
    predicates = [token_predicate(token) for token in tokens]
    return lambda row: all(predicate(row) for predicate in predicates)


def row_known(row: dict[str, Any]) -> bool:
    return row.get("actual_gross_cents") is not None and row.get("hold_gross_cents") is not None


def summarize_rule(rule: str, rows: list[dict[str, Any]], live_baseline_cents: float) -> dict[str, Any]:
    predicate = build_rule(rule)
    known = [row for row in rows if row_known(row)]
    selected = [row for row in known if predicate(row)]
    current_net = sum(fnum(row.get("actual_gross_cents")) for row in known)
    selected_current = sum(fnum(row.get("actual_gross_cents")) for row in selected)
    selected_hold = sum(fnum(row.get("hold_gross_cents")) for row in selected)
    candidate_net = current_net - selected_current + selected_hold
    selected_delta = selected_hold - selected_current
    helpful = [
        row for row in selected
        if fnum(row.get("hold_gross_cents")) > fnum(row.get("actual_gross_cents"))
    ]
    harmful = [
        row for row in selected
        if fnum(row.get("hold_gross_cents")) < fnum(row.get("actual_gross_cents"))
    ]
    loss_flips = [
        row for row in selected
        if fnum(row.get("actual_gross_cents")) < 0 <= fnum(row.get("hold_gross_cents"))
    ]
    new_losses = [
        row for row in selected
        if fnum(row.get("actual_gross_cents")) >= 0 > fnum(row.get("hold_gross_cents"))
    ]
    current_losses = sum(1 for row in known if fnum(row.get("actual_gross_cents")) < 0)
    candidate_losses = 0
    for row in known:
        candidate = fnum(row.get("hold_gross_cents")) if row in selected else fnum(row.get("actual_gross_cents"))
        if candidate < 0:
            candidate_losses += 1
    blockers: list[str] = ["diagnostic_full_denominator_replay", "not_frozen_forward"]
    if len(selected) < 30:
        blockers.append("selected_decisions_lt_30")
    if len(loss_flips) < 3:
        blockers.append("loss_flips_lt_3")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if new_losses:
        blockers.append("new_losses_created")
    if selected_delta <= 0:
        blockers.append("delta_not_positive")
    if int(max(0.0, candidate_net) // 100.0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    if candidate_net <= live_baseline_cents:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return {
        "rule": rule,
        "known_rows": len(known),
        "selected_rows": len(selected),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": selected_delta,
        "selected_current_cents": selected_current,
        "selected_hold_cents": selected_hold,
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "harmful_delta_cents": sum(fnum(row.get("hold_gross_cents")) - fnum(row.get("actual_gross_cents")) for row in harmful),
        "loss_flips": len(loss_flips),
        "new_losses": len(new_losses),
        "current_losses": current_losses,
        "candidate_losses": candidate_losses,
        "loss_count_delta": current_losses - candidate_losses,
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "selected_examples": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "delta_cents": fnum(row.get("hold_gross_cents")) - fnum(row.get("actual_gross_cents")),
                "failure_class": row.get("failure_class"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "exit_cents": row.get("exit_cents"),
                "ask_cents": row.get("ask_cents"),
            }
            for row in sorted(selected, key=lambda item: fnum(item.get("hold_gross_cents")) - fnum(item.get("actual_gross_cents")))[:10]
        ],
    }


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    frontier = load_json(FRONTIER_JSON)
    live_summary = load_json(LIVE_SUMMARY_JSON)
    rows = [row for row in scorecard.get("rows") or [] if isinstance(row, dict)]
    live_baseline_cents = round(100.0 * fnum(live_summary.get("net_pnl_total_dollars")), 4)
    frontier_rules = [
        row.get("rule") for row in frontier.get("observable_clean_frontier") or []
        if isinstance(row, dict) and row.get("rule")
    ][:12]
    rules = list(dict.fromkeys(["recross_ge_045", *frontier_rules]))
    replays = [summarize_rule(rule, rows, live_baseline_cents) for rule in rules]
    replays.sort(
        key=lambda row: (
            int("harmful_hold_rows_present" in (row.get("blockers") or [])),
            -fnum(row.get("delta_cents")),
            -fnum(row.get("loss_count_delta")),
        )
    )
    clean = [row for row in replays if not row.get("harmful_rows") and not row.get("new_losses")]
    best_clean = clean[0] if clean else {}
    interpretation = [
        "This is a full-denominator diagnostic replay, not a frozen exit candidate.",
        "It applies observable loss-frontier guards to all known scorecard rows so winner harm is visible.",
    ]
    if best_clean:
        interpretation.append(
            f"Best clean full-denominator guard is {best_clean.get('rule')} with "
            f"{best_clean.get('selected_rows')} selected rows, {best_clean.get('loss_flips')} loss flips, "
            f"{money(best_clean.get('delta_cents'))} delta, and blockers {best_clean.get('blockers')}."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "diagnostic_full_denominator_replay",
        "scorecard_rows": len(rows),
        "scorecard_summary": scorecard.get("summary"),
        "frontier_generated_at_utc": frontier.get("generated_at_utc"),
        "live_baseline_cents": live_baseline_cents,
        "replays": replays,
        "best_clean_replay": best_clean,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_clean_replay") or {}
    lines = [
        "# v28 Loss-Churn Observable Full-Denominator Replay",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Scorecard rows: `{report.get('scorecard_rows')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Best Clean Replay",
            "",
            f"- Rule: `{best.get('rule')}`",
            f"- Selected rows / loss flips: `{best.get('selected_rows')}` / `{best.get('loss_flips')}`",
            f"- Delta / candidate net: `{money(best.get('delta_cents'))}` / `{money(best.get('candidate_net_cents'))}`",
            f"- Loss count delta: `{best.get('loss_count_delta')}`",
            f"- Helpful/harmful/new losses: `{best.get('helpful_rows')}` / `{best.get('harmful_rows')}` / `{best.get('new_losses')}`",
            f"- Blockers: `{', '.join(best.get('blockers') or [])}`",
            "",
            "## Replays",
            "",
            "| rule | selected | flips | loss delta | delta | candidate net | helpful/harmful/new | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("replays") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {row.get('loss_flips')} | "
            f"{row.get('loss_count_delta')} | {money(row.get('delta_cents'))} | {money(row.get('candidate_net_cents'))} | "
            f"{row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('new_losses')} | "
            f"{row.get('full_loss_cushion')} | {', '.join(row.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Best Selected Examples",
            "",
            "| market | side | actual | hold | delta | failure | recross | exit | ask |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    for row in best.get("selected_examples") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {money(row.get('actual_gross_cents'))} | "
            f"{money(row.get('hold_gross_cents'))} | {money(row.get('delta_cents'))} | "
            f"`{row.get('failure_class')}` | {row.get('recross_hazard_score')} | {row.get('exit_cents')} | {row.get('ask_cents')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
