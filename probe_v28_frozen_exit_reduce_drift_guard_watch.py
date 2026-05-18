"""Frozen watch for drift-guarded probability-reduce suppression.

Research-only; no live bot changes or orders.

The blanket p_hold>=0.75 reduce suppressor recovered clipped winners, but the
drift audit shows loss-control harm when the exit-time state is not physically
consistent with benign turbulence. This freezes a small set of observable
exit-time guards from the current timestamp and scores future rows separately
from the diagnostic window.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_probability_reduce,
    side_won,
)
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_state.json"
DRIFT_AUDIT_JSON = OUT_DIR / "v28_exit_reduce_suppression_drift_audit_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3
FULL_LOSS_CENTS = 100.0

RULES: dict[str, dict[str, Any]] = {
    "diagnostic_blanket_p75_control": {
        "p_hold_min": 0.75,
        "physics": "Control row: the original blanket p_hold>=0.75 probability-reduce suppression.",
    },
    "high_p_favorable_fv": {
        "p_hold_min": 0.79,
        "fair_drawdown_max": 0.0,
        "physics": "Suppress only when held-side probability is very high and v28 FV says the current exit is not a real drawdown.",
    },
    "mid_p_moderate_drawdown": {
        "p_hold_min": 0.75,
        "p_hold_max": 0.79,
        "fair_drawdown_min": 0.0,
        "fair_drawdown_max": 5.0,
        "physics": "Suppress marginal high-p reduces only when drawdown is shallow enough to look like churn, not collapse.",
    },
    "two_regime_drift_guard": {
        "union": ["high_p_favorable_fv", "mid_p_moderate_drawdown"],
        "physics": "Two-regime guard: hold favorable-FV very-high-p exits, or shallow-drawdown marginal-p exits; reject large drawdown states.",
    },
    "entry_band_moderate_drawdown": {
        "p_hold_min": 0.75,
        "entry_cents_min": 70.0,
        "entry_cents_max": 82.0,
        "fair_drawdown_min": 0.0,
        "fair_drawdown_max": 5.0,
        "physics": "Observable entry-price band plus shallow drawdown: avoids the rich-entry harmful row and late full-loss drawdown state.",
    },
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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    drift = load_json(DRIFT_AUDIT_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "exit_reduce_drift_guard_watch",
        "origin": "Frozen after v28_exit_reduce_suppression_drift_audit showed blanket suppression loss-control harm.",
        "drift_interpretation": drift.get("interpretation") or [],
        "rules": RULES,
        "strict_forward_note": "Only post_drift_guard_birth rows count as promotion evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def rows_since(rows: list[dict[str, Any]], ts: str | None) -> list[dict[str, Any]]:
    cutoff = parse_ts(ts)
    if cutoff is None:
        return rows
    kept = []
    for row in rows:
        row_ts = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if row_ts is None or row_ts >= cutoff:
            kept.append(row)
    return kept


def value_passes(value: float | None, min_value: Any = None, max_value: Any = None) -> bool:
    if value is None:
        return False
    if min_value is not None and value < float(min_value):
        return False
    if max_value is not None and value > float(max_value):
        return False
    return True


def primitive_rule_passes(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_probability_reduce(row):
        return False
    p_hold = exit_p_hold(row)
    if not value_passes(p_hold, min_value=rule.get("p_hold_min"), max_value=rule.get("p_hold_max")):
        return False
    if not value_passes(
        exit_fair_drawdown(row),
        min_value=rule.get("fair_drawdown_min"),
        max_value=rule.get("fair_drawdown_max"),
    ):
        return False
    if not value_passes(
        as_float(row.get("entry_cents")),
        min_value=rule.get("entry_cents_min"),
        max_value=rule.get("entry_cents_max"),
    ):
        return False
    return True


def should_suppress(row: dict[str, Any], policy: str, rules: dict[str, dict[str, Any]]) -> bool:
    rule = rules[policy]
    union = rule.get("union")
    if union:
        return any(should_suppress(row, str(child), rules) for child in union)
    return primitive_rule_passes(row, rule)


def candidate_gross(row: dict[str, Any], policy: str, rules: dict[str, dict[str, Any]]) -> float | None:
    if should_suppress(row, policy, rules):
        return hold_to_settlement(row)
    return current_exit(row)


def full_loss_cushion(net_cents: float) -> int:
    if net_cents <= 0:
        return 0
    return int(net_cents // FULL_LOSS_CENTS)


def summarize(rows: list[dict[str, Any]], policy: str, rules: dict[str, dict[str, Any]]) -> dict[str, Any]:
    current_vals: list[float] = []
    candidate_vals: list[float] = []
    suppressed: list[dict[str, Any]] = []
    for row in rows:
        cur = current_exit(row)
        cand = candidate_gross(row, policy, rules)
        if cur is None or cand is None:
            continue
        current_vals.append(float(cur))
        candidate_vals.append(float(cand))
        if should_suppress(row, policy, rules):
            suppressed.append(row)
    current_cents = sum(current_vals)
    candidate_cents = sum(candidate_vals)
    helpful_delta = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    )
    harmful_delta = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    )
    suppressed_delta = helpful_delta + harmful_delta
    blockers = []
    if len(candidate_vals) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_cents <= 0.0:
        blockers.append("net_not_positive")
    if suppressed_delta <= 0.0:
        blockers.append("suppressed_delta_not_positive")
    if harmful_delta < 0.0:
        blockers.append("suppressed_losers_present")
        blockers.append("suppressed_loss_control_cost_negative")
    if full_loss_cushion(candidate_cents) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "policy": policy,
        "rows": len(rows),
        "settled": len(candidate_vals),
        "current_cents": current_cents,
        "candidate_cents": candidate_cents,
        "delta_vs_current_cents": candidate_cents - current_cents,
        "suppressed": len(suppressed),
        "suppressed_helpful": sum(1 for row in suppressed if side_won(row) is True),
        "suppressed_harmful": sum(1 for row in suppressed if side_won(row) is False),
        "suppressed_delta_cents": suppressed_delta,
        "helpful_delta_cents": helpful_delta,
        "harmful_delta_cents": harmful_delta,
        "full_loss_cushion": full_loss_cushion(candidate_cents),
        "blockers": blockers,
    }


def detail_rows(rows: list[dict[str, Any]], policy: str, rules: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    out = []
    for row in rows:
        if not should_suppress(row, policy, rules):
            continue
        cur = current_exit(row)
        hold = hold_to_settlement(row)
        if cur is None or hold is None:
            continue
        path = path_by_market.get(str(row.get("market"))) or {}
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "exit_reason": exit_reason(row),
            "p_hold": exit_p_hold(row),
            "fair_drawdown_cents": exit_fair_drawdown(row),
            "current_cents": cur,
            "hold_cents": hold,
            "delta_cents": float(hold) - float(cur),
            "side_won": side_won(row),
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        })
    out.sort(key=lambda item: str(item.get("exit_ts") or item.get("entry_ts") or ""))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rules = state.get("rules") if isinstance(state.get("rules"), dict) else RULES
    all_rows = build_rows()
    base_state = load_json(BASE_STATE_JSON)
    base_freeze = base_state.get("freeze_ts_utc")
    diagnostic_rows = rows_since(all_rows, str(base_freeze) if base_freeze else None)
    post_birth_rows = rows_since(all_rows, str(state.get("freeze_ts_utc")))
    diagnostic = [summarize(diagnostic_rows, policy, rules) for policy in rules]
    post_birth = [summarize(post_birth_rows, policy, rules) for policy in rules]
    diagnostic.sort(key=lambda row: (row["delta_vs_current_cents"], row["suppressed_delta_cents"]), reverse=True)
    post_birth.sort(key=lambda row: (row["delta_vs_current_cents"], row["suppressed_delta_cents"]), reverse=True)
    best_diag = diagnostic[0] if diagnostic else {}
    best_post = post_birth[0] if post_birth else {}
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "base_freeze_ts_utc": base_freeze,
        "diagnostic_since_base_freeze": diagnostic,
        "post_drift_guard_birth": post_birth,
        "best_diagnostic_policy": best_diag.get("policy"),
        "best_post_birth_policy": best_post.get("policy"),
        "best_post_birth_suppressed_rows": detail_rows(post_birth_rows, str(best_post.get("policy")), rules) if best_post else [],
        "interpretation": [
            "This is a frozen research watch only; it does not change live exits.",
            "Diagnostic rows reuse the old reduce-suppression freeze only to classify the mechanism.",
            "Only post_drift_guard_birth rows after this probe's own freeze timestamp count as forward evidence.",
            f"Best diagnostic policy is {best_diag.get('policy')} with delta {best_diag.get('delta_vs_current_cents')}c and blockers {best_diag.get('blockers')}.",
            f"Best post-birth policy is {best_post.get('policy')} with {best_post.get('settled')} settled rows, {best_post.get('suppressed')} suppressions, delta {best_post.get('delta_vs_current_cents')}c, and blockers {best_post.get('blockers')}.",
        ],
    }
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| policy | settled | suppressed | W/L suppressed | current c | candidate c | delta c | suppressed delta c | loss cost c | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        lines.append(
            f"| `{row.get('policy')}` | {row.get('settled')} | {row.get('suppressed')} | "
            f"{row.get('suppressed_helpful')}/{row.get('suppressed_harmful')} | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('candidate_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {fmt(row.get('suppressed_delta_cents'))} | "
            f"{fmt(row.get('harmful_delta_cents'))} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Exit Reduce Drift-Guard Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Guard freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Base reduce freeze UTC: `{report.get('base_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Diagnostic Since Base Reduce Freeze", ""])
    write_table(lines, report.get("diagnostic_since_base_freeze") or [])
    lines.extend(["", "## Strict Post Drift-Guard Birth", ""])
    write_table(lines, report.get("post_drift_guard_birth") or [])
    detail_rows = report.get("best_post_birth_suppressed_rows") or []
    if detail_rows:
        lines.extend([
            "",
            "## Best Post-Birth Suppressed Rows",
            "",
            "| market | side | result | exit_ts | p_hold | drawdown | current c | hold c | delta c | worst mark |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in detail_rows:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('result')} | {row.get('exit_ts')} | "
                f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
                f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
                f"{fmt(row.get('delta_cents'))} | {fmt(row.get('worst_post_exit_hold_mark_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
