"""Current-strategy improvement audit for BTC 15m Kalshi research.

This report reframes the research goal around improving the current live
baseline strategy (`mushroom_v28_live_gate_ev_exit_size2`) instead of replacing
the model in isolation. It compares research-only candidate evidence against
the live v28 baseline and the user-specified +50% net-P&L hurdle.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


OUT_DIR = Path("logs/edge_research")
REPORT_MD = OUT_DIR / "current_strategy_improvement_audit_latest.md"
REPORT_JSON = OUT_DIR / "current_strategy_improvement_audit_latest.json"

BASELINE_STRATEGY = "mushroom_v28_live_gate_ev_exit_size2"
PNL_IMPROVEMENT_TARGET = 1.50
BROAD_COVERAGE_FLOOR = 0.75
BROAD_COVERAGE_PREFERRED = 0.80
BROAD_FORWARD_SAMPLE_GATE = 200
OVERLAY_FORWARD_SAMPLE_GATE = 100
BAYES_PROB_GATE = 0.95

V39_JSON = OUT_DIR / "v39_entry_exit_strategy_projection_latest.json"
SAMPLE_JSON = OUT_DIR / "profit_lock_sample_size_requirements_latest.json"
BAYES_JSON = OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.json"
READINESS_JSON = OUT_DIR / "profit_lock_registered_signal_readiness_latest.json"
EXIT_VALUE_JSON = OUT_DIR / "live_v28_exit_value_audit_latest.json"
EDGE_HOLE_GATE_JSON = OUT_DIR / "v38_edge_hole_promotion_gate_latest.json"
REGISTRY_CSV = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def finite_float(value: Any) -> Optional[float]:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def fmt_money(value: Any) -> str:
    number = finite_float(value)
    if number is None:
        return "NA"
    return f"${number:,.2f}"


def fmt_pct(value: Any) -> str:
    number = finite_float(value)
    if number is None:
        return "NA"
    return f"{100.0 * number:.2f}%"


def fmt_ratio(value: Any) -> str:
    number = finite_float(value)
    if number is None:
        return "NA"
    return f"{number:.3f}"


def safe_min(values: Iterable[Any]) -> Optional[float]:
    parsed = [finite_float(value) for value in values]
    clean = [value for value in parsed if value is not None]
    if not clean:
        return None
    return min(clean)


def baseline_state(v39: Dict[str, Any]) -> Dict[str, Any]:
    live = v39.get("live_summary") if isinstance(v39.get("live_summary"), dict) else {}
    baseline_net = finite_float(live.get("net_pnl_total_dollars"))
    return {
        "strategy": BASELINE_STRATEGY,
        "artifact": str(V39_JSON),
        "entries": int(live.get("entries_total") or 0),
        "completed_round_trips": int(live.get("completed_round_trips") or 0),
        "open_positions": int(live.get("open_positions") or 0),
        "resolved_markets": int(live.get("resolved_markets") or 0),
        "cost_basis_dollars": finite_float(live.get("gross_cost_basis_dollars")),
        "net_pnl_dollars": baseline_net,
        "roi": finite_float(live.get("net_pnl_total_percent")) / 100.0
        if finite_float(live.get("net_pnl_total_percent")) is not None
        else None,
        "target_net_pnl_dollars": baseline_net * PNL_IMPROVEMENT_TARGET if baseline_net is not None else None,
        "target_delta_dollars": baseline_net * (PNL_IMPROVEMENT_TARGET - 1.0) if baseline_net is not None else None,
    }


def split_pnl_positive(row: Dict[str, Any]) -> bool:
    if isinstance(row.get("all_splits_positive"), bool):
        return bool(row["all_splits_positive"])
    values = [
        row.get("train_pnl_dollars"),
        row.get("validation_pnl_dollars"),
        row.get("val_pnl_dollars"),
        row.get("holdout_pnl_dollars"),
        row.get("hold_pnl_dollars"),
    ]
    parsed = [finite_float(value) for value in values if finite_float(value) is not None]
    return bool(parsed) and all(value > 0 for value in parsed)


def projection_candidates(v39: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
    selected = v39.get("selected")
    if not isinstance(selected, list):
        return []
    target = baseline.get("target_net_pnl_dollars")
    rows: List[Dict[str, Any]] = []
    for row in selected:
        if not isinstance(row, dict):
            continue
        all_pnl = finite_float(row.get("all_pnl_dollars"))
        min_cov = finite_float(row.get("min_split_coverage"))
        if min_cov is None:
            min_cov = safe_min(
                [
                    row.get("train_coverage"),
                    row.get("validation_coverage"),
                    row.get("val_coverage"),
                    row.get("holdout_coverage"),
                    row.get("hold_coverage"),
                    row.get("all_coverage"),
                ]
            )
        target_pass = all_pnl is not None and target is not None and all_pnl >= target
        rows.append(
            {
                "kind": "entry_exit_replay",
                "name": f"{row.get('model')} | {row.get('entry_policy')} | {row.get('exit_policy')}",
                "model": row.get("model"),
                "entry_policy": row.get("entry_policy"),
                "exit_policy": row.get("exit_policy"),
                "net_pnl_dollars": all_pnl,
                "roi": finite_float(row.get("all_roi")),
                "coverage": min_cov,
                "all_coverage": finite_float(row.get("all_coverage")),
                "train_pnl_dollars": finite_float(row.get("train_pnl_dollars")),
                "validation_pnl_dollars": finite_float(row.get("validation_pnl_dollars") or row.get("val_pnl_dollars")),
                "holdout_pnl_dollars": finite_float(row.get("holdout_pnl_dollars") or row.get("hold_pnl_dollars")),
                "all_trades": int(row.get("all_trades") or 0),
                "all_markets": int(row.get("all_markets") or 0),
                "all_wins": int(row.get("all_wins") or 0),
                "all_losses": int(row.get("all_losses") or 0),
                "coverage_pass": min_cov is not None and min_cov >= BROAD_COVERAGE_FLOOR,
                "preferred_coverage_pass": min_cov is not None and min_cov >= BROAD_COVERAGE_PREFERRED,
                "split_positive": split_pnl_positive(row),
                "target_pass": target_pass,
                "forward_proof": False,
                "ready": False,
                "blocker": "observed-quote replay only; needs pre-registered forward proof"
                if not target_pass
                else "target passes replay, but still needs pre-registered forward proof",
            }
        )
    return sorted(rows, key=lambda item: finite_float(item.get("net_pnl_dollars")) or -10**9, reverse=True)


def rows_by_name(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("name")): row
        for row in rows
        if isinstance(row, dict) and row.get("name") is not None
    }


def strict_shadow_candidates(
    sample: Dict[str, Any],
    bayes: Dict[str, Any],
    baseline: Dict[str, Any],
) -> List[Dict[str, Any]]:
    sample_rows = rows_by_name(sample)
    bayes_rows = rows_by_name(bayes)
    target = finite_float(baseline.get("target_net_pnl_dollars"))
    baseline_entries = int(baseline.get("entries") or 0)
    rows: List[Dict[str, Any]] = []
    for name, row in sample_rows.items():
        fresh_markets = int(row.get("fresh_markets") or 0)
        fresh_net_cents = finite_float(row.get("fresh_net_pnl_cents"))
        observed_size2_net = fresh_net_cents * 2.0 / 100.0 if fresh_net_cents is not None else None
        scaled_size2_net = None
        if observed_size2_net is not None and fresh_markets > 0 and baseline_entries > 0:
            scaled_size2_net = observed_size2_net * baseline_entries / fresh_markets
        bayes_row = bayes_rows.get(name, {})
        coverage = finite_float(row.get("fresh_coverage"))
        posterior_prob = finite_float(bayes_row.get("prob_win_rate_gt_break_even"))
        p05_edge = finite_float(bayes_row.get("posterior_p05_edge_cents"))
        wilson_pass = bool(row.get("fresh_ev_wilson_pass"))
        sample_gate_100 = fresh_markets >= OVERLAY_FORWARD_SAMPLE_GATE
        sample_gate_200 = fresh_markets >= BROAD_FORWARD_SAMPLE_GATE
        target_pass = scaled_size2_net is not None and target is not None and scaled_size2_net >= target
        confidence_pass = (
            wilson_pass
            and posterior_prob is not None
            and posterior_prob >= BAYES_PROB_GATE
            and p05_edge is not None
            and p05_edge > 0
        )
        rows.append(
            {
                "kind": "strict_shadow_lock",
                "name": name,
                "overlay": row.get("overlay") or "",
                "fresh_markets": fresh_markets,
                "fresh_wins": int(row.get("fresh_wins") or 0),
                "fresh_losses": int(row.get("fresh_losses") or 0),
                "accuracy": finite_float(row.get("fresh_accuracy")),
                "break_even": finite_float(row.get("fresh_break_even")),
                "wilson_low": finite_float(row.get("fresh_wilson_lower")),
                "coverage": coverage,
                "fresh_net_pnl_cents": fresh_net_cents,
                "observed_size2_net_dollars": observed_size2_net,
                "scaled_to_baseline_entries_dollars": scaled_size2_net,
                "posterior_prob_edge": posterior_prob,
                "posterior_p05_edge_cents": p05_edge,
                "extra_perfect_wins_wilson": row.get("extra_perfect_wins_for_fresh_ev_wilson"),
                "extra_perfect_wins_bayes": bayes_row.get("posterior_extra_perfect_wins_to_gate"),
                "coverage_pass": coverage is not None and coverage >= BROAD_COVERAGE_FLOOR,
                "preferred_coverage_pass": coverage is not None and coverage >= BROAD_COVERAGE_PREFERRED,
                "sample_gate_100": sample_gate_100,
                "sample_gate_200": sample_gate_200,
                "wilson_pass": wilson_pass,
                "confidence_pass": confidence_pass,
                "target_pass": target_pass,
                "forward_proof": True,
                "ready": target_pass and confidence_pass and sample_gate_200 and coverage is not None and coverage >= BROAD_COVERAGE_FLOOR,
            }
        )
    return sorted(
        rows,
        key=lambda item: finite_float(item.get("scaled_to_baseline_entries_dollars"))
        if item.get("scaled_to_baseline_entries_dollars") is not None
        else -10**9,
        reverse=True,
    )


def exit_overlay_candidates(exit_value: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = exit_value.get("top_candidates")
    if not isinstance(candidates, list):
        return []
    target_delta = finite_float(baseline.get("target_delta_dollars"))
    rows: List[Dict[str, Any]] = []
    for row in candidates:
        if not isinstance(row, dict):
            continue
        delta = finite_float(row.get("delta_vs_actual_exit_dollars"))
        rows.append(
            {
                "kind": "exit_overlay_diagnostic",
                "name": row.get("rule"),
                "delta_vs_actual_exit_dollars": delta,
                "adjusted_net_dollars": finite_float(row.get("adjusted_net_dollars")),
                "suppressed_exits": int(row.get("suppressed_exits") or 0),
                "suppressed_share": finite_float(row.get("suppressed_share")),
                "train_adjusted_net": finite_float(row.get("train_adjusted_net")),
                "validation_adjusted_net": finite_float(row.get("validation_adjusted_net")),
                "holdout_adjusted_net": finite_float(row.get("holdout_adjusted_net")),
                "strict_pass": bool(row.get("strict_pass")),
                "target_delta_pass": delta is not None and target_delta is not None and delta >= target_delta,
                "forward_proof": False,
                "ready": False,
                "blocker": "diagnostic exit replay; no split gate and no forward proof",
            }
        )
    return sorted(rows, key=lambda item: finite_float(item.get("delta_vs_actual_exit_dollars")) or -10**9, reverse=True)


def forward_gate_candidates(edge_gate: Dict[str, Any], baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not edge_gate:
        return []
    gates = edge_gate.get("gates") if isinstance(edge_gate.get("gates"), dict) else {}
    strict = gates.get("strict_forward") if isinstance(gates.get("strict_forward"), dict) else {}
    retro = gates.get("retrospective") if isinstance(gates.get("retrospective"), dict) else {}
    retro_record = retro.get("record") if isinstance(retro.get("record"), dict) else {}
    thresholds = edge_gate.get("thresholds") if isinstance(edge_gate.get("thresholds"), dict) else {}
    target = finite_float(baseline.get("target_net_pnl_dollars"))
    forward_net = finite_float(strict.get("fee_net_cents"))
    forward_net_dollars = forward_net / 100.0 if forward_net is not None else None
    retro_net = finite_float(retro_record.get("all_net_after_fees_1c_entry_dollars"))
    target_pass = retro_net is not None and target is not None and retro_net >= target
    return [
        {
            "kind": "forward_shadow_gate",
            "name": edge_gate.get("candidate") or "v38_edge_hole",
            "overall_pass": bool(edge_gate.get("pass")),
            "retrospective_pass": bool(retro.get("pass")),
            "temporal_pass": bool((gates.get("temporal") or {}).get("pass")) if isinstance(gates.get("temporal"), dict) else False,
            "leave_one_day_out_pass": bool((gates.get("leave_one_day_out") or {}).get("pass"))
            if isinstance(gates.get("leave_one_day_out"), dict)
            else False,
            "strict_forward_pass": bool(strict.get("pass")),
            "registered": int(strict.get("registered") or 0),
            "finalized": int(strict.get("finalized") or 0),
            "markets": int(strict.get("markets") or 0),
            "days": int(strict.get("days") or 0),
            "coverage": finite_float(strict.get("coverage")),
            "forward_fee_net_dollars": forward_net_dollars,
            "forward_fee_net_roi": finite_float(strict.get("fee_net_roi")),
            "retro_fee_1c_net_dollars": retro_net,
            "retro_fee_net_dollars": finite_float(retro_record.get("all_net_after_fees_dollars")),
            "retro_gross_pnl_dollars": finite_float(retro_record.get("all_pnl_dollars")),
            "retro_min_split_coverage": finite_float(retro_record.get("min_split_coverage")),
            "min_forward_finalized": int(thresholds.get("min_forward_finalized") or 0),
            "min_forward_markets": int(thresholds.get("min_forward_markets") or 0),
            "min_forward_days": int(thresholds.get("min_forward_days") or 0),
            "target_pass": target_pass,
            "ready": bool(edge_gate.get("pass")) and target_pass,
            "blocker": "strict-forward sample size / forward P&L" if not bool(strict.get("pass")) else "target P&L",
        }
    ]


def pending_registry_count(path: Path) -> int:
    if not path.exists():
        return 0
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return 0
    header = lines[0].split(",")
    try:
        outcome_idx = header.index("outcome")
    except ValueError:
        return 0
    pending = 0
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) <= outcome_idx or not parts[outcome_idx].strip():
            pending += 1
    return pending


def audit() -> Dict[str, Any]:
    v39 = load_json(V39_JSON)
    sample = load_json(SAMPLE_JSON)
    bayes = load_json(BAYES_JSON)
    readiness = load_json(READINESS_JSON)
    exit_value = load_json(EXIT_VALUE_JSON)
    edge_gate = load_json(EDGE_HOLE_GATE_JSON)
    baseline = baseline_state(v39)

    projection = projection_candidates(v39, baseline)
    strict = strict_shadow_candidates(sample, bayes, baseline)
    exits = exit_overlay_candidates(exit_value, baseline)
    forward_gates = forward_gate_candidates(edge_gate, baseline)
    all_candidates = [*projection, *strict, *exits, *forward_gates]
    all_ready = [row for row in all_candidates if row.get("ready")]
    target_pass = [row for row in all_candidates if row.get("target_pass") or row.get("target_delta_pass")]

    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ"),
        "objective": {
            "baseline_strategy": BASELINE_STRATEGY,
            "target": "+50% projected net P&L versus current live baseline",
            "broad_coverage_floor": BROAD_COVERAGE_FLOOR,
            "broad_coverage_preferred": BROAD_COVERAGE_PREFERRED,
            "broad_forward_sample_gate": BROAD_FORWARD_SAMPLE_GATE,
            "overlay_forward_sample_gate": OVERLAY_FORWARD_SAMPLE_GATE,
            "bayes_prob_gate": BAYES_PROB_GATE,
        },
        "artifacts": {
            "v39_projection": str(V39_JSON),
            "sample_size": str(SAMPLE_JSON),
            "bayesian": str(BAYES_JSON),
            "readiness": str(READINESS_JSON),
            "exit_value": str(EXIT_VALUE_JSON),
            "edge_hole_gate": str(EDGE_HOLE_GATE_JSON),
            "registry": str(REGISTRY_CSV),
        },
        "baseline": baseline,
        "counts": {
            "projection_candidates": len(projection),
            "strict_shadow_candidates": len(strict),
            "exit_overlay_candidates": len(exits),
            "forward_gate_candidates": len(forward_gates),
            "ready_candidates": len(all_ready),
            "target_pass_candidates": len(target_pass),
            "pending_registry_rows": pending_registry_count(REGISTRY_CSV),
            "strict_ready_count": int(readiness.get("ready_count") or 0),
        },
        "projection_candidates": projection,
        "strict_shadow_candidates": strict,
        "exit_overlay_candidates": exits,
        "forward_gate_candidates": forward_gates,
        "ready_candidates": all_ready,
        "complete": len(all_ready) > 0,
    }


def write_report(payload: Dict[str, Any]) -> None:
    baseline = payload["baseline"]
    target = baseline.get("target_net_pnl_dollars")
    projection = payload["projection_candidates"][:10]
    strict = payload["strict_shadow_candidates"][:10]
    exits = payload["exit_overlay_candidates"][:5]
    forward_gates = payload["forward_gate_candidates"]
    counts = payload["counts"]

    lines: List[str] = [
        "# Current Strategy Improvement Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Objective Restatement",
        "",
        f"- Baseline strategy: `{BASELINE_STRATEGY}`.",
        "- Improve net P&L through research-only shadow analysis across entries, exits, sizing, fills, filters, and fair-value logic.",
        f"- Target: at least +50% projected net P&L versus baseline, which currently means {fmt_money(target)}.",
        "- Never change live code, stop the bot, or place research trades under this goal.",
        "- Require pre-registered forward proof and anti-overfit gates before any recommendation.",
        "",
        "## Prompt-to-Artifact Checklist",
        "",
        "| requirement | evidence artifact | current evidence | status |",
        "|---|---|---|---|",
        f"| Current live baseline | `{payload['artifacts']['v39_projection']}` | {baseline.get('entries')} entries; net {fmt_money(baseline.get('net_pnl_dollars'))}; target {fmt_money(target)} | pass |",
        f"| +50% net-P&L target | candidate rows below | target-pass candidates: {counts['target_pass_candidates']}; ready candidates: {counts['ready_candidates']} | fail |",
        f"| 75-80% coverage | projection and strict rows below | broad floor {fmt_pct(BROAD_COVERAGE_FLOOR)}, preferred {fmt_pct(BROAD_COVERAGE_PREFERRED)} | mixed |",
        f"| Forward sample size | `{payload['artifacts']['sample_size']}` | broad gate {BROAD_FORWARD_SAMPLE_GATE}; overlay gate {OVERLAY_FORWARD_SAMPLE_GATE} | fail |",
        f"| Bayesian/Wilson confidence | `{payload['artifacts']['bayesian']}` | strict ready count: {counts['strict_ready_count']} | fail |",
        f"| Pre-registration state | `{payload['artifacts']['registry']}` | pending registry rows: {counts['pending_registry_rows']} | pass |",
        f"| Entry/exit/fair-value search | `{payload['artifacts']['v39_projection']}` | projection candidates: {counts['projection_candidates']} | diagnostic |",
        f"| Exit overlay search | `{payload['artifacts']['exit_value']}` | exit candidates: {counts['exit_overlay_candidates']} | diagnostic |",
        f"| Existing forward-shadow gates | `{payload['artifacts']['edge_hole_gate']}` | forward-gate candidates: {counts['forward_gate_candidates']} | in progress |",
        "| Live safety | process/log checks in thread | no live-code edits required by this audit | pass |",
        "",
        "## Baseline",
        "",
        f"- Strategy: `{baseline.get('strategy')}`",
        f"- Entries: {baseline.get('entries')}",
        f"- Completed round trips: {baseline.get('completed_round_trips')}",
        f"- Net P&L: {fmt_money(baseline.get('net_pnl_dollars'))} on {fmt_money(baseline.get('cost_basis_dollars'))}",
        f"- ROI: {fmt_pct(baseline.get('roi'))}",
        f"- +50% target: {fmt_money(target)}; required delta: {fmt_money(baseline.get('target_delta_dollars'))}",
        "",
        "## Entry/Exit Replay Candidates",
        "",
        "| candidate | net | ROI | coverage | splits+ | target | forward proof | ready |",
        "|---|---:|---:|---:|---|---|---|---|",
    ]
    for row in projection:
        lines.append(
            f"| `{row.get('name')}` | {fmt_money(row.get('net_pnl_dollars'))} | {fmt_pct(row.get('roi'))} | "
            f"{fmt_pct(row.get('coverage'))} | {row.get('split_positive')} | {row.get('target_pass')} | "
            f"{row.get('forward_proof')} | {row.get('ready')} |"
        )

    lines += [
        "",
        "## Strict Shadow Candidates",
        "",
        "| lock | fresh | acc | coverage | size2 observed | scaled to baseline entries | P(edge) | p05 edge | Wilson | target | ready |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in strict:
        lines.append(
            f"| `{row.get('name')}` | {row.get('fresh_wins')}/{row.get('fresh_losses')} of {row.get('fresh_markets')} | "
            f"{fmt_pct(row.get('accuracy'))} | {fmt_pct(row.get('coverage'))} | "
            f"{fmt_money(row.get('observed_size2_net_dollars'))} | {fmt_money(row.get('scaled_to_baseline_entries_dollars'))} | "
            f"{fmt_ratio(row.get('posterior_prob_edge'))} | {row.get('posterior_p05_edge_cents') if row.get('posterior_p05_edge_cents') is not None else 'NA'}c | "
            f"{row.get('wilson_pass')} | {row.get('target_pass')} | {row.get('ready')} |"
        )

    lines += [
        "",
        "## Exit Overlay Diagnostics",
        "",
        "| rule | delta vs actual exits | adjusted net | suppressed | strict | target delta | ready |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for row in exits:
        lines.append(
            f"| `{row.get('name')}` | {fmt_money(row.get('delta_vs_actual_exit_dollars'))} | "
            f"{fmt_money(row.get('adjusted_net_dollars'))} | {row.get('suppressed_exits')} | "
            f"{row.get('strict_pass')} | {row.get('target_delta_pass')} | {row.get('ready')} |"
        )

    lines += [
        "",
        "## Forward-Shadow Gates",
        "",
        "| candidate | finalized/required | coverage | forward net | forward ROI | retro fee+1c net | gate pass | target | ready |",
        "|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in forward_gates:
        required = row.get("min_forward_finalized") or row.get("min_forward_markets")
        lines.append(
            f"| `{row.get('name')}` | {row.get('finalized')}/{required} | "
            f"{fmt_pct(row.get('coverage'))} | {fmt_money(row.get('forward_fee_net_dollars'))} | "
            f"{fmt_pct(row.get('forward_fee_net_roi'))} | {fmt_money(row.get('retro_fee_1c_net_dollars'))} | "
            f"{row.get('overall_pass')} | {row.get('target_pass')} | {row.get('ready')} |"
        )

    lines += [
        "",
        "## Decision",
        "",
    ]
    if payload["complete"]:
        lines.append("- Complete: at least one candidate clears the revised-goal readiness gates.")
    else:
        lines.append("- Not complete: no candidate clears the +50% baseline P&L target with forward-proof and anti-overfit gates.")
        lines.append("- Continue shadow collection and only report material changes: new leader, target pass, gate failure/pass, or major failure pattern.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = audit()
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (OUT_DIR / f"current_strategy_improvement_audit_{payload['generated_utc']}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(payload)
    (OUT_DIR / f"current_strategy_improvement_audit_{payload['generated_utc']}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Current strategy improvement audit complete")
    print(f"complete={payload['complete']}")
    print(f"ready_candidates={payload['counts']['ready_candidates']}")
    print(f"target_pass_candidates={payload['counts']['target_pass_candidates']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
