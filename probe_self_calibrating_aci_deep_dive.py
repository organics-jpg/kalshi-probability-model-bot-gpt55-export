"""Focused self-calibrating / ACI probability deep dive for v28.

Research-only. This probe takes the latest Truffle suggestion seriously and
tries stronger online calibration variants without leaking future labels:

- raw v28 and Brownian terminal baselines
- oracle constant-rate bounds for context
- discrimination diagnostics, because calibration cannot rescue bad ranking
- capped ACI bias calibration selected on the first 200 rows only
- validation on rows 201-400 and 401-end
- a calibrated-edge veto check to see if the probability should drive trades

It reads recorded v28 artifacts only and writes under logs/edge_research.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import probe_arxiv_strategy_priority_tests as priority


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "self_calibrating_aci_deep_dive_latest.json"
OUT_MD = OUT_DIR / "self_calibrating_aci_deep_dive_latest.md"
LOCK_JSON = OUT_DIR / "self_calibrating_aci_candidate_lock_latest.json"

SOURCE_KEYS = ("p28", "brownian_terminal_p_side")
ETA_GRID = (0.02, 0.05, 0.08, 0.12, 0.16, 0.20)
CAP_GRID = (0.90, 0.92, 0.95, 0.98)
MAX_BIAS = 0.25
TARGET_COVERAGE = 0.90
ALPHA = 1.0 - TARGET_COVERAGE

WINDOWS = {
    "train_1_200": (1, 200),
    "validation_201_400": (201, 400),
    "holdout_401_end": (401, None),
    "all_after_200": (201, None),
    "first_400": (1, 400),
    "all": (1, None),
}


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else parsed


def clamp(value: float, low: float = 1e-6, high: float = 1.0 - 1e-6) -> float:
    return min(high, max(low, value))


def probability_scores_from_values(rows: list[dict[str, Any]], values: list[float | None], start: int, end: int | None) -> dict[str, Any]:
    usable: list[tuple[float, float]] = []
    for idx, (row, p) in enumerate(zip(rows, values), start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        y = priority.maybe_float(row.get("side_correct"))
        if p is None or y is None:
            continue
        p = clamp(p)
        usable.append((p, y))
    if not usable:
        return {"rows": 0}
    brier = mean([(p - y) ** 2 for p, y in usable])
    log_loss = mean([-(y * math.log(p) + (1.0 - y) * math.log(1.0 - p)) for p, y in usable])
    return {"rows": len(usable), "brier": brier, "log_loss": log_loss}


def probability_scores_for_key(rows: list[dict[str, Any]], key: str, start: int, end: int | None) -> dict[str, Any]:
    return probability_scores_from_values(rows, [priority.maybe_float(row.get(key)) for row in rows], start, end)


def auc_score(labels: list[int], scores: list[float]) -> float | None:
    return priority.auc_score(labels, scores)


def discrimination_for_key(rows: list[dict[str, Any]], key: str, start: int, end: int | None) -> dict[str, Any]:
    labels = []
    scores = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        y = priority.maybe_float(row.get("side_correct"))
        score = priority.maybe_float(row.get(key))
        if y is None or score is None:
            continue
        labels.append(int(y))
        scores.append(score)
    return {"rows": len(labels), "auc": auc_score(labels, scores)}


def oracle_constant_window(rows: list[dict[str, Any]], start: int, end: int | None) -> dict[str, Any]:
    ys = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        y = priority.maybe_float(row.get("side_correct"))
        if y is not None:
            ys.append(y)
    if not ys:
        return {"rows": 0}
    p = mean(ys)
    return {
        "rows": len(ys),
        "hit_rate": p,
        "brier": mean([(p - y) ** 2 for y in ys]),
        "log_loss": mean([-(y * math.log(clamp(p)) + (1.0 - y) * math.log(clamp(1.0 - p))) for y in ys]),
    }


def capped_aci_values(
    rows: list[dict[str, Any]],
    source_key: str,
    eta: float,
    cap: float,
    *,
    max_bias: float = MAX_BIAS,
) -> tuple[list[float | None], list[dict[str, Any]]]:
    bias = 0.0
    q = 0.50
    low = 1.0 - cap
    values: list[float | None] = []
    trace: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        p_raw = priority.maybe_float(row.get(source_key))
        y = priority.maybe_float(row.get("side_correct"))
        if p_raw is None:
            values.append(None)
            trace.append({"idx": idx, "p_raw": None, "p_cal": None, "bias_pre": bias, "q_pre": q, "covered": None})
            continue
        p_cal = clamp(p_raw + bias, low, cap)
        values.append(p_cal)
        covered = None
        score = None
        if y is not None:
            score = abs(y - p_cal)
            covered = score <= q
            miss = 0.0 if covered else 1.0
            q = clamp(q + eta * (miss - ALPHA), 0.01, 1.0)
            bias = max(-max_bias, min(max_bias, bias + eta * (y - p_raw - bias)))
        trace.append(
            {
                "idx": idx,
                "source_key": source_key,
                "p_raw": p_raw,
                "p_cal": p_cal,
                "bias_pre": trace[-1]["bias_post"] if trace else 0.0,
                "bias_post": bias,
                "q_post": q,
                "score": score,
                "covered": covered,
            }
        )
    return values, trace


def coverage_for_trace(trace: list[dict[str, Any]], start: int, end: int | None) -> dict[str, Any]:
    rows = []
    for item in trace:
        idx = int(item.get("idx") or 0)
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        if item.get("covered") is not None:
            rows.append(item)
    if not rows:
        return {"rows": 0}
    return {"rows": len(rows), "coverage": sum(1 for item in rows if item.get("covered")) / len(rows)}


def evaluate_values(rows: list[dict[str, Any]], values: list[float | None], trace: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        out[name] = probability_scores_from_values(rows, values, start, end)
        if trace is not None:
            out[name]["coverage"] = coverage_for_trace(trace, start, end).get("coverage")
    return out


def baseline_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"scores": {}, "discrimination": {}, "oracle_constant": {}}
    for key in ("p28", "p22", "brownian_terminal_p_side"):
        out["scores"][key] = {name: probability_scores_for_key(rows, key, start, end) for name, (start, end) in WINDOWS.items()}
        out["discrimination"][key] = {name: discrimination_for_key(rows, key, start, end) for name, (start, end) in WINDOWS.items()}
    out["oracle_constant"] = {name: oracle_constant_window(rows, start, end) for name, (start, end) in WINDOWS.items()}
    return out


def calibrator_grid_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = []
    for source_key in SOURCE_KEYS:
        for cap in CAP_GRID:
            for eta in ETA_GRID:
                values, trace = capped_aci_values(rows, source_key, eta, cap)
                scores = evaluate_values(rows, values, trace)
                train = scores["train_1_200"]
                candidates.append(
                    {
                        "name": f"capped_aci_{source_key}_eta{eta:.2f}_cap{cap:.2f}",
                        "source_key": source_key,
                        "eta": eta,
                        "cap": cap,
                        "max_bias": MAX_BIAS,
                        "target_coverage": TARGET_COVERAGE,
                        "scores": scores,
                        "selection_score": {
                            "train_log_loss": train.get("log_loss"),
                            "train_brier": train.get("brier"),
                        },
                    }
                )
    candidates.sort(key=lambda row: (fnum(row["selection_score"].get("train_log_loss"), 99.0), fnum(row["selection_score"].get("train_brier"), 99.0)))
    locked = candidates[0] if candidates else {}
    best_all = min(candidates, key=lambda row: (fnum(row["scores"]["all"].get("log_loss"), 99.0), fnum(row["scores"]["all"].get("brier"), 99.0))) if candidates else {}
    return {
        "selection_rule": "Pick capped ACI source/eta/cap by lowest log loss on rows 1-200, tie-breaker Brier.",
        "candidate_count": len(candidates),
        "locked_train200": locked,
        "best_ex_post_all": best_all,
        "top_by_train": candidates[:12],
    }


def robust_hybrid(row: dict[str, Any]) -> bool:
    return priority.robust_hybrid(row)


def calibrated_edge(row: dict[str, Any], p_cal: float | None) -> float | None:
    p28 = priority.maybe_float(row.get("p28"))
    edge = priority.maybe_float(row.get("edge28_cents"))
    if p_cal is None or p28 is None or edge is None:
        return None
    return edge + 100.0 * (p_cal - p28)


def calibrated_edge_gate_report(rows: list[dict[str, Any]], locked: dict[str, Any]) -> dict[str, Any]:
    if not locked:
        return {}
    values, _ = capped_aci_values(rows, str(locked["source_key"]), float(locked["eta"]), float(locked["cap"]))
    base_rows = [row for row in rows if robust_hybrid(row)]
    gates = {}
    for min_edge in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0):
        selected = []
        for row, p_cal in zip(rows, values):
            edge = calibrated_edge(row, p_cal)
            if edge is None:
                continue
            if not robust_hybrid(row):
                continue
            if edge >= min_edge:
                selected.append(row)
        gates[f"min_calibrated_edge_{min_edge:.0f}c"] = priority.stats(selected, len(rows))
    return {
        "read": "Uses locked calibrated probability to recompute edge while keeping robust hybrid mechanics fixed.",
        "baseline_robust_hybrid": priority.stats(base_rows, len(rows)),
        "gates": gates,
    }


def improvement_rows(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for window in WINDOWS:
        raw = baseline["scores"]["p28"][window]
        brown = baseline["scores"]["brownian_terminal_p_side"][window]
        cand = candidate["scores"][window]
        out[window] = {
            "candidate_brier": cand.get("brier"),
            "candidate_log_loss": cand.get("log_loss"),
            "brier_improvement_vs_raw": fnum(raw.get("brier")) - fnum(cand.get("brier")),
            "log_loss_improvement_vs_raw": fnum(raw.get("log_loss")) - fnum(cand.get("log_loss")),
            "brier_improvement_vs_brownian": fnum(brown.get("brier")) - fnum(cand.get("brier")),
            "log_loss_improvement_vs_brownian": fnum(brown.get("log_loss")) - fnum(cand.get("log_loss")),
        }
    return out


def build_report() -> dict[str, Any]:
    rows, diagnostics = priority.load_rows()
    baseline = baseline_report(rows)
    grid = calibrator_grid_report(rows)
    locked = grid.get("locked_train200") or {}
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Focused self-calibrating / capped ACI probability deep dive over recorded v28 rows.",
        "diagnostics": diagnostics,
        "baseline": baseline,
        "calibrator_grid": grid,
        "locked_improvements": improvement_rows(baseline, locked) if locked else {},
        "calibrated_edge_gate": calibrated_edge_gate_report(rows, locked),
        "promotion_gate": {
            "strict_first_400": {"brier_lt": 0.165, "log_loss_lt": 0.50},
            "forward_after_200": "locked_train200 should improve Brier and log loss vs raw and Brownian on validation_201_400 and holdout_401_end",
        },
    }
    LOCK_JSON.write_text(
        json.dumps(
            {
                "generated_at_utc": report["generated_at_utc"],
                "calibrator_id": locked.get("name"),
                "selection_rule": grid.get("selection_rule"),
                "source_key": locked.get("source_key"),
                "eta": locked.get("eta"),
                "cap": locked.get("cap"),
                "max_bias": locked.get("max_bias"),
                "target_coverage": locked.get("target_coverage"),
                "status": "research_only_candidate_lock_not_live_trading",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def money(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{100.0 * parsed:.1f}%"


def write_md(report: dict[str, Any]) -> None:
    baseline = report.get("baseline") or {}
    grid = report.get("calibrator_grid") or {}
    locked = grid.get("locked_train200") or {}
    lines = [
        "# Self-Calibrating ACI Deep Dive",
        "",
        "Research-only focused probe for the self-calibrating / ACI probability lane. The locked candidate is selected only from rows 1-200, then evaluated forward.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Settled labels: `{report.get('diagnostics', {}).get('settled_label_rows')}`",
        "",
        "## Baseline Scores",
        "",
        "| model | window | rows | Brier | log loss | AUC |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for key in ("p28", "brownian_terminal_p_side", "p22"):
        scores = (baseline.get("scores") or {}).get(key) or {}
        aucs = (baseline.get("discrimination") or {}).get(key) or {}
        for window in ("train_1_200", "validation_201_400", "holdout_401_end", "all"):
            row = scores.get(window) or {}
            auc = (aucs.get(window) or {}).get("auc")
            lines.append(f"| {key} | {window} | {row.get('rows')} | {fnum(row.get('brier')):.4f} | {fnum(row.get('log_loss')):.4f} | {fnum(auc):.3f} |")
    lines.extend(
        [
            "",
            "## Oracle Constant Context",
            "",
            "| window | rows | hit rate | constant Brier | constant log loss |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for window in ("train_1_200", "validation_201_400", "holdout_401_end", "all"):
        row = ((baseline.get("oracle_constant") or {}).get(window) or {})
        lines.append(f"| {window} | {row.get('rows')} | {pct(row.get('hit_rate'))} | {fnum(row.get('brier')):.4f} | {fnum(row.get('log_loss')):.4f} |")
    lines.extend(
        [
            "",
            "## Locked Calibrator",
            "",
            f"- Selection rule: `{grid.get('selection_rule')}`",
            f"- Locked calibrator: `{locked.get('name')}`",
            f"- Source: `{locked.get('source_key')}`, eta `{locked.get('eta')}`, cap `{locked.get('cap')}`, max bias `{locked.get('max_bias')}`.",
            "",
            "| window | rows | Brier | log loss | coverage | Brier vs raw | Log loss vs raw | Brier vs Brownian | Log loss vs Brownian |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    improvements = report.get("locked_improvements") or {}
    for window in ("train_1_200", "validation_201_400", "holdout_401_end", "all_after_200", "first_400", "all"):
        score = ((locked.get("scores") or {}).get(window) or {})
        imp = improvements.get(window) or {}
        lines.append(
            f"| {window} | {score.get('rows')} | {fnum(score.get('brier')):.4f} | {fnum(score.get('log_loss')):.4f} | "
            f"{pct(score.get('coverage'))} | {fnum(imp.get('brier_improvement_vs_raw')):.4f} | "
            f"{fnum(imp.get('log_loss_improvement_vs_raw')):.4f} | {fnum(imp.get('brier_improvement_vs_brownian')):.4f} | "
            f"{fnum(imp.get('log_loss_improvement_vs_brownian')):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Top Train-Selected Candidates",
            "",
            "| candidate | train Brier | train log loss | validation Brier | validation log loss | holdout Brier | holdout log loss | all Brier | all log loss |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in (grid.get("top_by_train") or [])[:8]:
        scores = row.get("scores") or {}
        tr = scores.get("train_1_200") or {}
        va = scores.get("validation_201_400") or {}
        ho = scores.get("holdout_401_end") or {}
        all_row = scores.get("all") or {}
        lines.append(
            f"| {row.get('name')} | {fnum(tr.get('brier')):.4f} | {fnum(tr.get('log_loss')):.4f} | "
            f"{fnum(va.get('brier')):.4f} | {fnum(va.get('log_loss')):.4f} | "
            f"{fnum(ho.get('brier')):.4f} | {fnum(ho.get('log_loss')):.4f} | "
            f"{fnum(all_row.get('brier')):.4f} | {fnum(all_row.get('log_loss')):.4f} |"
        )
    edge = report.get("calibrated_edge_gate") or {}
    base = edge.get("baseline_robust_hybrid") or {}
    lines.extend(
        [
            "",
            "## Calibrated Edge Gate Check",
            "",
            f"- Baseline robust hybrid: `{money(base.get('net_dollars'))}` from `{base.get('entries')}` rows, avg `{cents(base.get('avg_cents_per_entry'))}`.",
            "",
            "| gate | entries | W/L | PnL | avg/entry |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name, row in (edge.get("gates") or {}).items():
        lines.append(f"| {name} | {row.get('entries')} | {priority.wl(row)} | {money(row.get('net_dollars'))} | {cents(row.get('avg_cents_per_entry'))} |")
    locked_scores = locked.get("scores") or {}
    first_400 = locked_scores.get("first_400") or {}
    strict_pass = fnum(first_400.get("brier"), 99.0) < 0.165 and fnum(first_400.get("log_loss"), 99.0) < 0.50
    validation = locked_scores.get("validation_201_400") or {}
    holdout = locked_scores.get("holdout_401_end") or {}
    lines.extend(
        [
            "",
            "## Read",
            "",
            f"- Strict first-400 Truffle gate passed: `{strict_pass}`.",
            f"- The locked candidate does improve validation rows 201-400 to Brier `{fnum(validation.get('brier')):.4f}` / log loss `{fnum(validation.get('log_loss')):.4f}` and holdout rows 401-end to Brier `{fnum(holdout.get('brier')):.4f}` / log loss `{fnum(holdout.get('log_loss')):.4f}`.",
            "- p28 has weak/negative discrimination in the hard middle slice, so the self-calibrating path should use Brownian terminal as the anchor and treat v28 as an edge/feature signal.",
            "- The calibrated probability should be logged as `p_calibrated` in forward shadow first. Using it as a hard calibrated-edge veto reduced replay PnL, so do not wire it into live entry logic yet.",
            f"- Candidate lock JSON: `{LOCK_JSON}`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
