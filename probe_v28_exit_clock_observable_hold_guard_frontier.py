"""Observable hold-guard frontier on the materialized v28 exit-clock snapshot.

Research-only; no live bot changes or orders.

This scans simple observable exit/entry state rules on a fixed exit-clock
denominator. It is meant to find physical mechanisms, not promotion candidates.
Any rule found here still needs its own frozen forward clock.
"""
from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SNAPSHOT_JSON = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_clock_observable_hold_guard_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clock_observable_hold_guard_frontier_latest.md"

MIN_SELECTED = 30
MIN_CUSHION = 3


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


def token_predicate(token: str) -> Callable[[dict[str, Any]], bool]:
    field, op, raw = token.rsplit("_", 2)
    threshold = float(raw.replace("n", "-").replace("p", "."))
    if op == "ge":
        return lambda row: row.get(field) not in (None, "") and fnum(row.get(field)) >= threshold
    if op == "le":
        return lambda row: row.get(field) not in (None, "") and fnum(row.get(field)) <= threshold
    raise ValueError(f"Unsupported token: {token}")


def make_token(field: str, op: str, threshold: float) -> str:
    encoded = ("%g" % threshold).replace("-", "n").replace(".", "p")
    return f"{field}_{op}_{encoded}"


def build_tokens() -> list[str]:
    tokens: list[str] = []
    for threshold in [0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        tokens.append(make_token("exit_p_hold", "ge", threshold))
    for threshold in [-10, -5, 0, 5, 10, 15]:
        tokens.append(make_token("exit_fair_drawdown_cents", "le", threshold))
    for threshold in [50, 60, 70, 80, 90]:
        tokens.append(make_token("exit_cents", "ge", threshold))
    for threshold in [0.85, 1.0, 1.25, 1.5, 2.0]:
        tokens.append(make_token("entry_abs_d_sigma", "ge", threshold))
    for threshold in [5, 10, 15, 25, 50]:
        tokens.append(make_token("entry_raw_edge_cents", "ge", threshold))
    for threshold in [60, 70, 80]:
        tokens.append(make_token("entry_ask_cents", "ge", threshold))
    for threshold in [60, 70, 80]:
        tokens.append(make_token("entry_ask_cents", "le", threshold))
    for threshold in [0.90, 0.95, 0.98]:
        tokens.append(make_token("entry_p_side", "ge", threshold))
    return tokens


def rule_predicate(tokens: tuple[str, ...]) -> Callable[[dict[str, Any]], bool]:
    predicates = [token_predicate(token) for token in tokens]
    return lambda row: all(predicate(row) for predicate in predicates)


def valid_combo(tokens: tuple[str, ...]) -> bool:
    fields = [token.rsplit("_", 2)[0] for token in tokens]
    # Avoid redundant same-field threshold conjunctions; the tighter threshold is already a single-token rule.
    return len(fields) == len(set(fields))


def rule_name(tokens: tuple[str, ...]) -> str:
    return "__and__".join(tokens)


def summarize_rule(rows: list[dict[str, Any]], tokens: tuple[str, ...]) -> dict[str, Any]:
    predicate = rule_predicate(tokens)
    selected = [row for row in rows if predicate(row)]
    current_net = sum(fnum(row.get("actual_gross_cents")) for row in rows)
    selected_current = sum(fnum(row.get("actual_gross_cents")) for row in selected)
    selected_hold = sum(fnum(row.get("hold_gross_cents")) for row in selected)
    candidate_net = current_net - selected_current + selected_hold
    delta = selected_hold - selected_current
    helpful = [row for row in selected if fnum(row.get("hold_gross_cents")) > fnum(row.get("actual_gross_cents"))]
    harmful = [row for row in selected if fnum(row.get("hold_gross_cents")) < fnum(row.get("actual_gross_cents"))]
    flat = [row for row in selected if fnum(row.get("hold_gross_cents")) == fnum(row.get("actual_gross_cents"))]
    loss_flips = [
        row for row in selected
        if fnum(row.get("actual_gross_cents")) < 0 <= fnum(row.get("hold_gross_cents"))
    ]
    new_losses = [
        row for row in selected
        if fnum(row.get("actual_gross_cents")) >= 0 > fnum(row.get("hold_gross_cents"))
    ]
    blockers = ["diagnostic_snapshot_frontier", "not_frozen_forward"]
    if len(selected) < MIN_SELECTED:
        blockers.append("selected_decisions_lt_30")
    if delta <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("harmful_hold_rows_present")
    if new_losses:
        blockers.append("new_losses_created")
    if int(max(0.0, candidate_net) // 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "rule": rule_name(tokens),
        "token_count": len(tokens),
        "rows": len(rows),
        "selected_rows": len(selected),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": delta,
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "loss_flips": len(loss_flips),
        "new_losses": len(new_losses),
        "full_loss_cushion": int(max(0.0, candidate_net) // 100.0),
        "blockers": blockers,
        "selected_examples": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "entry_ts": row.get("entry_ts"),
                "exit_ts": row.get("exit_ts"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "hold_delta_cents": fnum(row.get("hold_gross_cents")) - fnum(row.get("actual_gross_cents")),
                "exit_p_hold": row.get("exit_p_hold"),
                "exit_fair_drawdown_cents": row.get("exit_fair_drawdown_cents"),
                "exit_cents": row.get("exit_cents"),
                "entry_abs_d_sigma": row.get("entry_abs_d_sigma"),
                "entry_raw_edge_cents": row.get("entry_raw_edge_cents"),
                "entry_ask_cents": row.get("entry_ask_cents"),
            }
            for row in sorted(
                selected,
                key=lambda item: fnum(item.get("hold_gross_cents")) - fnum(item.get("actual_gross_cents")),
            )[:12]
        ],
    }


def build_report() -> dict[str, Any]:
    snapshot = load_json(SNAPSHOT_JSON)
    rows = [
        row for row in snapshot.get("rows") or []
        if isinstance(row, dict)
        and row.get("actual_gross_cents") is not None
        and row.get("hold_gross_cents") is not None
    ]
    tokens = build_tokens()
    combos: list[tuple[str, ...]] = []
    combos.extend((token,) for token in tokens)
    combos.extend(combo for combo in itertools.combinations(tokens, 2) if valid_combo(combo))
    combos.extend(combo for combo in itertools.combinations(tokens, 3) if valid_combo(combo))
    summaries = [summarize_rule(rows, combo) for combo in combos]
    summaries.sort(
        key=lambda row: (
            int(bool(row.get("harmful_rows"))),
            int(bool(row.get("new_losses"))),
            -fnum(row.get("delta_cents")),
            -fnum(row.get("selected_rows")),
            fnum(row.get("token_count")),
        )
    )
    clean = [row for row in summaries if not row.get("harmful_rows") and not row.get("new_losses")]
    clean_sample = [row for row in clean if (row.get("selected_rows") or 0) >= MIN_SELECTED]
    best_clean = clean[0] if clean else {}
    best_clean_sample = clean_sample[0] if clean_sample else {}
    broad_positive = [
        row for row in summaries
        if (row.get("selected_rows") or 0) >= MIN_SELECTED and fnum(row.get("delta_cents")) > 0
    ]
    blockers = ["research_only", "not_frozen_forward", "diagnostic_snapshot_scan"]
    if not best_clean_sample:
        blockers.append("no_clean_rule_with_30_selected_decisions")
    interpretation = [
        "This fixed-denominator scan is diagnostic only.",
        "Clean observable hold guards exist, but the clean high-delta rules are sparse.",
    ]
    if best_clean_sample:
        interpretation.append(
            f"Best clean >=30-decision rule is {best_clean_sample.get('rule')} with "
            f"{best_clean_sample.get('selected_rows')} rows and {money(best_clean_sample.get('delta_cents'))} delta."
        )
    else:
        interpretation.append("No clean rule clears the 30 selected-decision evidence floor.")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_snapshot": str(SNAPSHOT_JSON),
        "snapshot_generated_at_utc": snapshot.get("generated_at_utc"),
        "rows": len(rows),
        "rules_scanned": len(summaries),
        "frontier_top": summaries[:50],
        "best_clean": best_clean,
        "best_clean_sample": best_clean_sample,
        "broad_positive_top": broad_positive[:20],
        "blockers": blockers,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_clean") or {}
    best_sample = report.get("best_clean_sample") or {}
    lines = [
        "# v28 Exit-Clock Observable Hold-Guard Frontier",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Rows / rules scanned: `{report.get('rows')}` / `{report.get('rules_scanned')}`",
        f"- Best clean rule: `{best.get('rule')}`",
        f"- Best clean selected/delta/net: `{best.get('selected_rows')}` / `{money(best.get('delta_cents'))}` / `{money(best.get('candidate_net_cents'))}`",
        f"- Best clean >=30 selected rule: `{best_sample.get('rule')}`",
        f"- Best clean >=30 selected/delta/net: `{best_sample.get('selected_rows')}` / `{money(best_sample.get('delta_cents'))}` / `{money(best_sample.get('candidate_net_cents'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Frontier",
        "",
        "| rule | selected | delta | candidate net | helpful/harmful/flat | flips/new losses | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("frontier_top") or []:
        lines.append(
            f"| `{row.get('rule')}` | {row.get('selected_rows')} | {money(row.get('delta_cents'))} | "
            f"{money(row.get('candidate_net_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('flat_rows')} | "
            f"{row.get('loss_flips')}/{row.get('new_losses')} | {row.get('full_loss_cushion')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
