"""False-negative rescue child for the v28 top-component mix.

Research-only; no live bot changes or orders.

The top-component loss drilldown shows a small approved-entry loss pocket where
the delayed recheck still exited but settlement would have paid. This probe
tests observable exit-state rules that would rescue those false negatives while
penalizing rules that also rescue true losers. It creates its own freeze clock;
diagnostic rows are mechanism discovery only.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TOP_COMPONENT_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
STATE_JSON = OUT_DIR / "v28_top_component_false_negative_rescue_child_state.json"
OUT_JSON = OUT_DIR / "v28_top_component_false_negative_rescue_child_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_false_negative_rescue_child_latest.md"

PARENT_LABEL = "rescue_drop15_plus_absd_parent_fill_to75"
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
MAX_RECONSTRUCTED_SHARE = 0.35
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


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "top_component_false_negative_rescue_child",
        "parent_candidate": PARENT_LABEL,
        "note": "Freeze created after loss-cluster drilldown found approved-entry false-negative exit rescues. Pre-freeze rows are diagnostic only.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def live_cents() -> float:
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def choose_parent(payload: dict[str, Any], label: str = PARENT_LABEL) -> dict[str, Any]:
    variants = [row for row in payload.get("variants") or [] if isinstance(row, dict)]
    for row in variants:
        if row.get("label") == label:
            return row
    for row in variants:
        if not str(row.get("label") or "").startswith("post_birth_"):
            return row
    return variants[0] if variants else {}


def has_exit_marks(row: dict[str, Any]) -> bool:
    return row.get("hold_cents") is not None and row.get("current_cents") is not None


def is_exit_row(row: dict[str, Any]) -> bool:
    return str(row.get("component") or "").startswith("delayed_recheck")


def base_selected_cents(row: dict[str, Any]) -> float:
    return fnum(row.get("selected_cents"))


def base_weighted_cents(row: dict[str, Any]) -> float:
    return fnum(row.get("selected_weighted_cents"))


def row_weight(row: dict[str, Any]) -> float:
    selected = base_selected_cents(row)
    if abs(selected) > 1e-9:
        return base_weighted_cents(row) / selected
    return fnum(row.get("entry_weight"), 1.0)


def low_exit_collapse_rebound(row: dict[str, Any]) -> bool:
    return (
        is_exit_row(row)
        and not bool(row.get("selected_suppressed"))
        and "collapse" in str(row.get("exit_reason") or "")
        and fnum(row.get("exit_bid"), 999.0) <= 30.0
        and fnum(row.get("recheck_bid"), -999.0) >= 10.0
        and fnum(row.get("window_drop_cents"), 999.0) <= 12.0
        and fnum(row.get("fair_drawdown_cents"), -999.0) >= 10.0
    )


def mid_recheck_value_rebound(row: dict[str, Any]) -> bool:
    return (
        is_exit_row(row)
        and not bool(row.get("selected_suppressed"))
        and fnum(row.get("recheck_bid"), -999.0) >= 40.0
        and fnum(row.get("window_drop_cents"), 999.0) <= 12.0
        and fnum(row.get("fair_drawdown_cents"), -999.0) >= 10.0
        and fnum(row.get("p_hold"), -999.0) <= 0.62
    )


def approved_only(rule: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return lambda row: source(row) == "approved_entry" and rule(row)


RULES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "diagnostic_low_exit_collapse_rebound": low_exit_collapse_rebound,
    "diagnostic_mid_recheck_value_rebound": mid_recheck_value_rebound,
    "diagnostic_union_rebound": lambda row: low_exit_collapse_rebound(row) or mid_recheck_value_rebound(row),
    "diagnostic_approved_union_rebound": approved_only(lambda row: low_exit_collapse_rebound(row) or mid_recheck_value_rebound(row)),
}


def score_rows(label: str, rows: list[dict[str, Any]], denominator: int, strict_forward: bool) -> dict[str, Any]:
    rule = RULES[label]
    scored = []
    rescued_rows = []
    helpful = []
    harmful = []
    for row in rows:
        item = dict(row)
        original = base_selected_cents(row)
        candidate = original
        child_rescue = False
        if has_exit_marks(row) and rule(row):
            candidate = fnum(row.get("hold_cents"))
            child_rescue = True
        weight = row_weight(row)
        weighted = weight * candidate
        delta = weight * (candidate - original)
        item.update(
            {
                "child_rescue": child_rescue,
                "child_selected_cents": candidate,
                "child_weighted_cents": weighted,
                "child_delta_cents": delta,
            }
        )
        if child_rescue:
            rescued_rows.append(item)
            if delta > 0:
                helpful.append(item)
            elif delta < 0:
                harmful.append(item)
        scored.append(item)

    net = sum(fnum(row.get("child_weighted_cents")) for row in scored)
    wins = sum(1 for row in scored if fnum(row.get("child_weighted_cents")) > 0)
    losses = sum(1 for row in scored if fnum(row.get("child_weighted_cents")) < 0)
    counts = Counter(source(row) for row in scored)
    reconstructed = len(scored) - int(counts.get("approved_entry") or 0)
    recon_share = reconstructed / len(scored) if scored else None
    coverage = 100.0 * len(scored) / denominator if denominator else None
    live = live_cents()
    blockers = []
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if net <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if harmful:
        blockers.append("harmful_child_rescue_present")

    return {
        "label": label.replace("diagnostic_", "post_child_birth_" if strict_forward else "diagnostic_"),
        "rule": label,
        "strict_forward": strict_forward,
        "entries": len(scored),
        "settled": len(scored),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "delta_vs_parent_cents": sum(fnum(row.get("child_delta_cents")) for row in scored),
        "delta_vs_live_cents": net - live,
        "reconstructed_share": recon_share,
        "source_counts": dict(counts),
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "rescued_rows": len(rescued_rows),
        "helpful_rescues": len(helpful),
        "harmful_rescues": len(harmful),
        "helpful_delta_cents": sum(fnum(row.get("child_delta_cents")) for row in helpful),
        "harmful_delta_cents": sum(fnum(row.get("child_delta_cents")) for row in harmful),
        "blockers": blockers,
        "worst_rows": sorted(scored, key=lambda row: fnum(row.get("child_weighted_cents")))[:16],
        "rescued_examples": sorted(rescued_rows, key=lambda row: fnum(row.get("child_delta_cents")), reverse=True)[:16],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    payload = load_json(TOP_COMPONENT_JSON)
    denominator = int(payload.get("denominator") or 0)
    parent = choose_parent(payload)
    parent_rows = [row for row in parent.get("rows") or [] if isinstance(row, dict)]
    freeze_ts = str(state.get("freeze_ts_utc"))
    strict_rows = [
        row for row in parent_rows
        if str(row.get("exit_ts") or "") >= freeze_ts
    ]
    diagnostic = [score_rows(label, parent_rows, denominator, False) for label in RULES]
    strict_denominator = max(0, len({str(row.get("market") or "") for row in strict_rows}))
    strict = [score_rows(label, strict_rows, strict_denominator, True) for label in RULES]
    variants = diagnostic + strict
    variants.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            int(row.get("harmful_rescues") or 0),
            -fnum(row.get("net_cents"), -999999.0),
        )
    )
    best_diag = next((row for row in variants if not row.get("strict_forward")), {})
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "source_report": str(TOP_COMPONENT_JSON),
        "parent_report_utc": payload.get("generated_at_utc"),
        "parent_label": parent.get("label"),
        "parent_net_cents": parent.get("net_cents"),
        "parent_wins": parent.get("wins"),
        "parent_losses": parent.get("losses"),
        "denominator": denominator,
        "strict_denominator_proxy": strict_denominator,
        "strict_rows_from_parent_exit_ts": len(strict_rows),
        "diagnostic_variants": diagnostic,
        "strict_variants": strict,
        "variants": variants,
        "interpretation": [
            "Research-only false-negative rescue child; no live bot changes or orders.",
            (
                f"Best diagnostic child {best_diag.get('label')} changes parent by "
                f"{best_diag.get('delta_vs_parent_cents')}c with "
                f"{best_diag.get('helpful_rescues')}/{best_diag.get('harmful_rescues')} helpful/harmful rescues."
            ) if best_diag else "No diagnostic child scored.",
            f"Child freeze UTC is {freeze_ts}; strict rows from this child freeze are the only promotion evidence.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Top-Component False-Negative Rescue Child",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Parent: `{report.get('parent_label')}` `{fmt(report.get('parent_net_cents'))}c` `{report.get('parent_wins')}/{report.get('parent_losses')}`",
        f"- Strict rows from parent exit timestamps: `{report.get('strict_rows_from_parent_exit_ts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| label | settled | W/L | coverage | net | delta parent | rescues H/H | rescue delta H/H | recon | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("variants") or []:
        lines.append(
            f"| `{row.get('label')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_parent_cents'))} | "
            f"{row.get('helpful_rescues')}/{row.get('harmful_rescues')} | "
            f"{fmt(row.get('helpful_delta_cents'))}/{fmt(row.get('harmful_delta_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {', '.join(row.get('blockers') or [])} |"
        )
    best = (report.get("variants") or [{}])[0]
    lines.extend(
        [
            "",
            "## Best Rescued Examples",
            "",
            "| market | side | source | weighted | delta | exit | p_hold | drawdown | exit bid | recheck | drop | hold | current |",
            "|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in best.get("rescued_examples") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {source(row)} | {fmt(row.get('child_weighted_cents'))} | "
            f"{fmt(row.get('child_delta_cents'))} | {row.get('exit_reason')} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('exit_bid'))} | {fmt(row.get('recheck_bid'))} | "
            f"{fmt(row.get('window_drop_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('current_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
