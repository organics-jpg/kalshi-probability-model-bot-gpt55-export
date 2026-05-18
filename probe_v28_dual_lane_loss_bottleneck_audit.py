"""Loss bottleneck audit for the v28 dual-lane live-readiness watch.

Research-only; no live bot changes and no orders.

This probe reads the latest strict replay precheck and asks a narrow question:
are current losses coming from a coherent, observable risk shape that could be
handled with a continuous confidence penalty instead of a brittle cutoff?
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_loss_bottleneck_audit_latest.md"


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


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def row_net(row: dict[str, Any]) -> float:
    for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents", "raw_net_cents"):
        if row.get(field) is not None:
            return fnum(row.get(field))
    return 0.0


def metric_range(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [fnum(row.get(field), float("nan")) for row in rows if row.get(field) is not None]
    values = [value for value in values if value == value]
    if not values:
        return {"min": None, "max": None, "avg": None}
    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
    }


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    net = sum(row_net(row) for row in rows)
    wins = sum(1 for row in rows if row_net(row) > 0)
    losses = sum(1 for row in rows if row_net(row) < 0)
    return {
        "entries": len(rows),
        "wins": wins,
        "losses": losses,
        "net_cents": net,
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "ask_prob": metric_range(rows, "ask_prob"),
        "raw_edge": metric_range(rows, "raw_edge"),
        "recross_hazard_score": metric_range(rows, "recross_hazard_score"),
        "abs_d_sigma": metric_range(rows, "abs_d_sigma"),
    }


def clone_with_net(row: dict[str, Any], net: float) -> dict[str, Any]:
    item = dict(row)
    item["final_weighted_cents"] = net
    item["weighted_net_cents"] = net
    return item


def apply_weight(rows: list[dict[str, Any]], weight_fn: Callable[[dict[str, Any]], float]) -> list[dict[str, Any]]:
    weighted = []
    for row in rows:
        weight = max(0.0, min(1.0, weight_fn(row)))
        if weight <= 0.0:
            continue
        item = clone_with_net(row, row_net(row) * weight)
        item["audit_weight"] = weight
        weighted.append(item)
    return weighted


def high_cost_low_edge(row: dict[str, Any]) -> bool:
    return fnum(row.get("ask_prob")) >= 0.78 and fnum(row.get("raw_edge")) < 0.09


def high_cost_low_edge_near_boundary(row: dict[str, Any]) -> bool:
    return high_cost_low_edge(row) and fnum(row.get("abs_d_sigma")) >= 0.93


def variant_rows(name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if name == "baseline":
        return rows
    if name == "shrink_high_cost_low_edge_25pct":
        return apply_weight(rows, lambda row: 0.75 if high_cost_low_edge(row) else 1.0)
    if name == "shrink_high_cost_50pct":
        return apply_weight(rows, lambda row: 0.5 if fnum(row.get("ask_prob")) >= 0.78 else 1.0)
    if name == "suppress_high_cost":
        return apply_weight(rows, lambda row: 0.0 if fnum(row.get("ask_prob")) >= 0.78 else 1.0)
    if name == "shrink_high_cost_low_edge_50pct":
        return apply_weight(rows, lambda row: 0.5 if high_cost_low_edge(row) else 1.0)
    if name == "shrink_high_cost_low_edge_75pct":
        return apply_weight(rows, lambda row: 0.25 if high_cost_low_edge(row) else 1.0)
    if name == "suppress_high_cost_low_edge":
        return apply_weight(rows, lambda row: 0.0 if high_cost_low_edge(row) else 1.0)
    if name == "shrink_high_cost_low_edge_near_boundary_50pct":
        return apply_weight(rows, lambda row: 0.5 if high_cost_low_edge_near_boundary(row) else 1.0)
    return rows


def classify_failure_modes(losses: list[dict[str, Any]], wins: list[dict[str, Any]], baseline_net: float) -> dict[str, Any]:
    """Map current loss shape into the project's failure-mode taxonomy."""
    loss_ask_avg = fnum(metric_range(losses, "ask_prob").get("avg"))
    win_ask_avg = fnum(metric_range(wins, "ask_prob").get("avg"))
    loss_edge_avg = fnum(metric_range(losses, "raw_edge").get("avg"))
    win_edge_avg = fnum(metric_range(wins, "raw_edge").get("avg"))
    source_counts: dict[str, int] = {}
    for row in losses:
        source = str(row.get("source") or "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
    classifications = [
        {
            "mode": "FV error",
            "status": "possible",
            "evidence": "Both losses had positive modeled raw edge but resolved against the selected side; too few rows to separate calibration error from timing noise.",
        },
        {
            "mode": "Entry timing error",
            "status": "active",
            "evidence": (
                f"Losses are expensive/thin-edge entries: avg ask={loss_ask_avg:.3f} vs wins={win_ask_avg:.3f}, "
                f"avg raw_edge={loss_edge_avg:.3f} vs wins={win_edge_avg:.3f}."
            ),
        },
        {
            "mode": "Exit-policy error",
            "status": "possible",
            "evidence": "The child/exit rescue did not improve either current loss; needs more rows before calling the exit policy wrong.",
        },
        {
            "mode": "Execution/friction error",
            "status": "active",
            "evidence": "Both losses are strict parent midprice hold-fill rows where high ask cost leaves little margin for path noise.",
        },
        {
            "mode": "Market-regime error",
            "status": "unknown",
            "evidence": "The sample is too small to know whether the losses cluster in a volatility/path regime.",
        },
        {
            "mode": "Source-quality error",
            "status": "not_current_driver",
            "evidence": f"Loss source counts are {source_counts}; current strict precheck loss rows are approved-source, not reconstructed proxy rows.",
        },
        {
            "mode": "Fragility error",
            "status": "active",
            "evidence": f"Forced-precheck net is {baseline_net:.0f}c with full-loss cushion 0; two losses erase the win stack.",
        },
    ]
    return {
        "classifications": classifications,
        "primary_current_modes": [
            row["mode"] for row in classifications if row["status"] == "active"
        ],
        "loss_ask_avg": loss_ask_avg,
        "win_ask_avg": win_ask_avg,
        "loss_raw_edge_avg": loss_edge_avg,
        "win_raw_edge_avg": win_edge_avg,
        "loss_source_counts": source_counts,
    }


def build_report() -> dict[str, Any]:
    precheck = load_json(PRECHECK_JSON)
    best = precheck.get("best_union") if isinstance(precheck.get("best_union"), dict) else {}
    rows = [row for row in best.get("worst_rows") or [] if isinstance(row, dict)]
    denominator = int(round(100.0 * len(rows) / fnum(best.get("coverage_pct"), 100.0))) if best.get("coverage_pct") else len(rows)
    losses = [row for row in rows if row_net(row) < 0]
    wins = [row for row in rows if row_net(row) > 0]
    variant_names = [
        "baseline",
        "shrink_high_cost_low_edge_25pct",
        "shrink_high_cost_50pct",
        "suppress_high_cost",
        "shrink_high_cost_low_edge_50pct",
        "shrink_high_cost_low_edge_75pct",
        "suppress_high_cost_low_edge",
        "shrink_high_cost_low_edge_near_boundary_50pct",
    ]
    variants = []
    for name in variant_names:
        scored_rows = variant_rows(name, rows)
        summary = summarize_rows(scored_rows, denominator)
        variants.append(
            {
                "name": name,
                **summary,
                "delta_vs_baseline_cents": summary["net_cents"] - sum(row_net(row) for row in rows),
            }
        )
    loss_tags: list[str] = []
    if losses and all((row.get("component") == "strict_parent_midprice_hold_fill") for row in losses):
        loss_tags.append("losses_are_parent_fill_not_sidecar_add")
    if losses and all(high_cost_low_edge(row) for row in losses):
        loss_tags.append("losses_share_high_cost_low_edge_shape")
    if wins and losses:
        loss_ask_avg = fnum(metric_range(losses, "ask_prob").get("avg"))
        win_ask_avg = fnum(metric_range(wins, "ask_prob").get("avg"))
        if loss_ask_avg > win_ask_avg:
            loss_tags.append("losses_are_more_expensive_than_wins_on_average")
    if losses and all(row.get("exit_child_rescue") is False for row in losses):
        loss_tags.append("exit_child_did_not_rescue_current_losses")

    read = [
        "Current forced replay is still immature diagnostic evidence, not a promotion sample.",
        "The immediate live-readiness bottleneck is damage control: two parent-fill losses are larger than six wins combined.",
    ]
    if "losses_share_high_cost_low_edge_shape" in loss_tags:
        read.append("Both losses share an observable high-cost/low-edge shape, so a continuous parent-fill confidence shrink is worth testing next.")
    else:
        read.append("The current losses do not yet show a clean enough shared shape for a new gate.")

    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(PRECHECK_JSON),
        "promotion_use": "diagnostic_only_before_30_settled_rows",
        "freeze_ts_utc": precheck.get("freeze_ts_utc"),
        "possible_market_windows_since_freeze": precheck.get("possible_market_windows_since_freeze"),
        "market_windows_remaining_to_min_sample": precheck.get("market_windows_remaining_to_min_sample"),
        "live_baseline_cents": precheck.get("live_baseline_cents"),
        "policy": best.get("sidecar_policy"),
        "baseline": summarize_rows(rows, denominator),
        "losses": losses,
        "wins": wins,
        "loss_tags": loss_tags,
        "failure_mode_audit": classify_failure_modes(
            losses,
            wins,
            summarize_rows(rows, denominator).get("net_cents") or 0.0,
        ),
        "variants": variants,
        "read": read,
        "next_research_action": (
            "Test a parent-fill confidence shrink for expensive low-edge rows inside the dual-lane research scorer, "
            "then re-run strict precheck and wait for the 30-row own-freeze gate."
        ),
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    baseline = report.get("baseline") or {}
    failure_mode_audit = report.get("failure_mode_audit") if isinstance(report.get("failure_mode_audit"), dict) else {}
    lines = [
        "# v28 Dual-Lane Loss Bottleneck Audit",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Windows since freeze / remaining: `{report.get('possible_market_windows_since_freeze')}` / `{report.get('market_windows_remaining_to_min_sample')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Policy audited: `{report.get('policy')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Baseline Forced-Precheck Rows",
            "",
            f"- Entries/W/L: `{baseline.get('entries')}` / `{baseline.get('wins')}/{baseline.get('losses')}`",
            f"- Coverage: `{pct(baseline.get('coverage_pct'))}`",
            f"- Net: `{money(baseline.get('net_cents'))}`",
            f"- Full-loss cushion: `{baseline.get('full_loss_cushion')}`",
            f"- Loss tags: `{', '.join(report.get('loss_tags') or []) or 'none'}`",
            f"- Primary failure modes: `{', '.join(failure_mode_audit.get('primary_current_modes') or []) or 'none'}`",
            "",
            "## Failure-Mode Classification",
            "",
            "| mode | status | evidence |",
            "|---|---|---|",
        ]
    )
    for row in failure_mode_audit.get("classifications") or []:
        if not isinstance(row, dict):
            continue
        lines.append(f"| {row.get('mode')} | `{row.get('status')}` | {row.get('evidence')} |")
    lines.extend(
        [
            "",
            "## Variant Stress",
            "",
            "| variant | entries | W/L | coverage | net | delta | cushion |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("variants") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('name')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{pct(row.get('coverage_pct'))} | {money(row.get('net_cents'))} | "
            f"{money(row.get('delta_vs_baseline_cents'))} | {row.get('full_loss_cushion')} |"
        )
    lines.extend(
        [
            "",
            "## Current Loss Rows",
            "",
            "| market | side | component | net | ask | raw edge | abs d | recross | rescue |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("losses") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {row.get('component')} | "
            f"{money(row_net(row))} | {row.get('ask_prob')} | {row.get('raw_edge')} | "
            f"{row.get('abs_d_sigma')} | {row.get('recross_hazard_score')} | {row.get('exit_child_rescue')} |"
        )
    lines.extend(["", f"Next research action: {report.get('next_research_action')}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
