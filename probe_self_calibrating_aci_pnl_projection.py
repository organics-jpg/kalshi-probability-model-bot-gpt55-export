"""PnL projection for the locked self-calibrating ACI candidate.

Research-only. This script projects how the locked capped-ACI probability would
have behaved if used as:

- a scoring/calibration layer over recorded v28 rows
- a calibrated-edge replacement
- a veto/risk overlay on the robust hybrid gate
- a train-locked gate selected only on rows 1-200

It uses recorded filled trades only for PnL replay, so the results are a
historical projection, not a live forecast. It does not place orders or edit
live bot logic.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Callable

import probe_arxiv_strategy_priority_tests as priority
import probe_self_calibrating_aci_deep_dive as aci


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "self_calibrating_aci_pnl_projection_latest.json"
OUT_MD = OUT_DIR / "self_calibrating_aci_pnl_projection_latest.md"
TRUFFLE_PROMPT = ROOT / "truffle_arxiv_self_calibrating_aci_probability_prompt_2026-05-08.txt"

Predicate = Callable[[dict[str, Any]], bool]

WINDOWS = {
    "train_1_200": (1, 200),
    "validation_201_400": (201, 400),
    "holdout_401_end": (401, None),
    "forward_after_200": (201, None),
    "all": (1, None),
}
E_PROCESS_LAMBDAS = (0.02, 0.05, 0.10, 0.20, 0.35)
E_PROCESS_THRESHOLDS = (20.0, 100.0)


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else parsed


def ge(value: Any, threshold: float) -> bool:
    parsed = priority.maybe_float(value)
    return parsed is not None and parsed >= threshold


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def window_rows(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    out = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        out.append(row)
    return out


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    out = priority.stats(rows, denominator)
    out["model_ev_cents_sum"] = sum(fnum(row.get("calibrated_edge_qty_cents")) for row in rows)
    out["model_ev_dollars_sum"] = out["model_ev_cents_sum"] / 100.0
    out["avg_model_ev_cents"] = out["model_ev_cents_sum"] / len(rows) if rows else None
    return out


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def robust_hybrid(row: dict[str, Any]) -> bool:
    return priority.robust_hybrid(row)


def annotate_rows() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    rows, diagnostics = priority.load_rows()
    deep_report = aci.build_report()
    locked = (deep_report.get("calibrator_grid") or {}).get("locked_train200") or {}
    values, trace = aci.capped_aci_values(rows, str(locked["source_key"]), float(locked["eta"]), float(locked["cap"]))
    trace_by_idx = {item["idx"]: item for item in trace}
    annotated = []
    for idx, (row, p_cal) in enumerate(zip(rows, values), start=1):
        row = dict(row)
        row["row_idx"] = idx
        row["p_calibrated"] = p_cal
        row["aci_bias_post"] = (trace_by_idx.get(idx) or {}).get("bias_post")
        row["aci_q_post"] = (trace_by_idx.get(idx) or {}).get("q_post")
        row["calibrated_edge_cents"] = aci.calibrated_edge(row, p_cal)
        qty = fnum(row.get("qty"), 1.0) or 1.0
        row["calibrated_edge_qty_cents"] = fnum(row.get("calibrated_edge_cents")) * qty
        row["raw_edge_qty_cents"] = fnum(row.get("edge28_cents")) * qty
        annotated.append(row)
    return annotated, diagnostics, locked, deep_report


def evaluate_strategy(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        chunk = window_rows(rows, start, end)
        chosen = selected(chunk, predicate)
        out[name] = stats(chosen, len(chunk))
    return out


def fixed_strategies(rows: list[dict[str, Any]]) -> dict[str, Any]:
    strategies: dict[str, Predicate] = {
        "live_all_recorded_v28": lambda row: True,
        "robust_hybrid_base": robust_hybrid,
    }
    for min_edge in (-5.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 8.0):
        strategies[f"calibrated_edge_all_ge_{min_edge:g}c"] = (
            lambda row, threshold=min_edge: ge(row.get("calibrated_edge_cents"), threshold)
        )
    for min_p in (0.70, 0.75, 0.78, 0.80, 0.82, 0.85, 0.88):
        strategies[f"p_cal_all_ge_{min_p:.2f}"] = (
            lambda row, threshold=min_p: ge(row.get("p_calibrated"), threshold)
        )
    for min_edge in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 8.0):
        strategies[f"robust_plus_calibrated_edge_ge_{min_edge:g}c"] = (
            lambda row, threshold=min_edge: robust_hybrid(row) and ge(row.get("calibrated_edge_cents"), threshold)
        )
    for min_p in (0.75, 0.78, 0.80, 0.82, 0.85, 0.88):
        strategies[f"robust_plus_p_cal_ge_{min_p:.2f}"] = (
            lambda row, threshold=min_p: robust_hybrid(row) and ge(row.get("p_calibrated"), threshold)
        )
    return {name: evaluate_strategy(rows, predicate) for name, predicate in strategies.items()}


def family_grid() -> list[dict[str, Any]]:
    configs = []
    for min_edge in (-5.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 8.0):
        configs.append(
            {
                "name": f"calibrated_edge_all_ge_{min_edge:g}c",
                "family": "calibrated_edge_all",
                "params": {"min_calibrated_edge_cents": min_edge},
                "predicate": lambda row, threshold=min_edge: ge(row.get("calibrated_edge_cents"), threshold),
            }
        )
    for min_p in (0.70, 0.75, 0.78, 0.80, 0.82, 0.85, 0.88):
        configs.append(
            {
                "name": f"p_cal_all_ge_{min_p:.2f}",
                "family": "p_cal_all",
                "params": {"min_p_calibrated": min_p},
                "predicate": lambda row, threshold=min_p: ge(row.get("p_calibrated"), threshold),
            }
        )
    for min_edge in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 8.0):
        configs.append(
            {
                "name": f"robust_plus_calibrated_edge_ge_{min_edge:g}c",
                "family": "robust_plus_calibrated_edge",
                "params": {"min_calibrated_edge_cents": min_edge},
                "predicate": lambda row, threshold=min_edge: robust_hybrid(row) and ge(row.get("calibrated_edge_cents"), threshold),
            }
        )
    for min_p in (0.75, 0.78, 0.80, 0.82, 0.85, 0.88):
        configs.append(
            {
                "name": f"robust_plus_p_cal_ge_{min_p:.2f}",
                "family": "robust_plus_p_cal",
                "params": {"min_p_calibrated": min_p},
                "predicate": lambda row, threshold=min_p: robust_hybrid(row) and ge(row.get("p_calibrated"), threshold),
            }
        )
    for min_p in (0.75, 0.78, 0.80, 0.82, 0.85, 0.88):
        for min_edge in (0.0, 2.0, 4.0, 6.0):
            configs.append(
                {
                    "name": f"robust_plus_p_cal_ge_{min_p:.2f}_edge_ge_{min_edge:g}c",
                    "family": "robust_plus_p_cal_and_edge",
                    "params": {"min_p_calibrated": min_p, "min_calibrated_edge_cents": min_edge},
                    "predicate": lambda row, p=min_p, edge=min_edge: robust_hybrid(row)
                    and ge(row.get("p_calibrated"), p)
                    and ge(row.get("calibrated_edge_cents"), edge),
                }
            )
    return configs


def train_subsplit_nets(rows: list[dict[str, Any]], predicate: Predicate) -> list[float]:
    chunks = [
        rows[: int(len(rows) / 3)],
        rows[int(len(rows) / 3) : int(2 * len(rows) / 3)],
        rows[int(2 * len(rows) / 3) :],
    ]
    return [net_cents(selected(chunk, predicate)) for chunk in chunks if chunk]


def choose_locked_gate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    train = window_rows(rows, 1, 200)
    candidates = []
    for config in family_grid():
        predicate = config["predicate"]
        train_selected = selected(train, predicate)
        if len(train_selected) < 20:
            continue
        train_stats = stats(train_selected, len(train))
        if fnum(train_stats.get("avg_cents_per_entry")) <= 0:
            continue
        nets = train_subsplit_nets(train, predicate)
        positive_splits = sum(1 for value in nets if value > 0)
        if positive_splits < 2:
            continue
        candidates.append(
            {
                "name": config["name"],
                "family": config["family"],
                "params": config["params"],
                "train": train_stats,
                "subsplit_nets_cents": nets,
                "positive_subsplits": positive_splits,
                "score": (
                    positive_splits,
                    min(nets),
                    fnum(train_stats.get("avg_cents_per_entry")),
                    fnum(train_stats.get("net_cents")),
                    train_stats.get("entries") or 0,
                ),
                "predicate": predicate,
            }
        )
    candidates.sort(key=lambda row: row["score"], reverse=True)
    if not candidates:
        return {}
    locked = dict(candidates[0])
    predicate = locked.pop("predicate")
    locked["windows"] = evaluate_strategy(rows, predicate)
    locked["top_candidates"] = [
        {key: value for key, value in row.items() if key != "predicate"}
        for row in candidates[:12]
    ]
    return locked


def daily_slices(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    by_day: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        dt = row.get("_entry_dt")
        day = dt.date().isoformat() if hasattr(dt, "date") else "unknown"
        by_day.setdefault(day, []).append(row)
    out = []
    for day, chunk in sorted(by_day.items()):
        chosen = selected(chunk, predicate)
        out.append({"day": day, "all_entries": len(chunk), "selected": stats(chosen, len(chunk))})
    return out


def e_process_path(values: list[float], lam: float, scale: float = 200.0) -> dict[str, Any]:
    capital = 1.0
    max_capital = 1.0
    crosses = {str(int(threshold)): None for threshold in E_PROCESS_THRESHOLDS}
    for idx, value in enumerate(values, start=1):
        clipped = max(-0.95 / lam, min(0.95 / lam, value / scale))
        capital *= 1.0 + lam * clipped
        max_capital = max(max_capital, capital)
        for threshold in E_PROCESS_THRESHOLDS:
            key = str(int(threshold))
            if crosses[key] is None and capital >= threshold:
                crosses[key] = idx
    return {
        "lambda": lam,
        "scale_cents": scale,
        "final_capital": capital,
        "max_capital": max_capital,
        "cross_at": crosses,
    }


def e_process_for_predicate(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {
        "lambda_grid": list(E_PROCESS_LAMBDAS),
        "thresholds": list(E_PROCESS_THRESHOLDS),
        "windows": {},
    }
    for window_name in ("train_1_200", "forward_after_200", "all"):
        start, end = WINDOWS[window_name]
        chosen = selected(window_rows(rows, start, end), predicate)
        values = [fnum(row.get("pnl_cents")) for row in chosen]
        paths = [e_process_path(values, lam) for lam in E_PROCESS_LAMBDAS]
        best = max(paths, key=lambda row: fnum(row.get("max_capital"))) if paths else {}
        out["windows"][window_name] = {
            "entries": len(chosen),
            "net_cents": sum(values),
            "net_dollars": sum(values) / 100.0,
            "lambda_rows": paths,
            "best_by_max_capital": best,
            "crossed_20": any((path.get("cross_at") or {}).get("20") is not None for path in paths),
            "crossed_100": any((path.get("cross_at") or {}).get("100") is not None for path in paths),
        }
    out["passes_gate"] = bool((out["windows"].get("forward_after_200") or {}).get("crossed_100"))
    return out


def e_process_checks(rows: list[dict[str, Any]], locked_gate_predicate: Predicate | None) -> dict[str, Any]:
    checks = {
        "robust_hybrid_base": e_process_for_predicate(rows, robust_hybrid),
        "robust_plus_p_cal_ge_0.80": e_process_for_predicate(
            rows, lambda row: robust_hybrid(row) and ge(row.get("p_calibrated"), 0.80)
        ),
    }
    if locked_gate_predicate is not None:
        checks["train_locked_calibrated_gate"] = e_process_for_predicate(rows, locked_gate_predicate)
    return checks


def projection_summary(rows: list[dict[str, Any]], fixed: dict[str, Any], locked_gate: dict[str, Any]) -> dict[str, Any]:
    names = [
        "live_all_recorded_v28",
        "robust_hybrid_base",
        "robust_plus_calibrated_edge_ge_0c",
        "robust_plus_p_cal_ge_0.80",
        "calibrated_edge_all_ge_0c",
        "p_cal_all_ge_0.80",
    ]
    summary = {name: fixed.get(name) for name in names if fixed.get(name)}
    if locked_gate:
        summary["train_locked_calibrated_gate"] = locked_gate.get("windows")
    return summary


def write_truffle_prompt(report: dict[str, Any]) -> None:
    locked = report.get("locked_calibrator") or {}
    locked_gate = report.get("train_locked_gate") or {}
    windows = (locked_gate.get("windows") or {}) if locked_gate else {}
    forward = windows.get("forward_after_200") or {}
    robust = ((report.get("projection_summary") or {}).get("robust_hybrid_base") or {}).get("all") or {}
    overlay = ((report.get("projection_summary") or {}).get("robust_plus_p_cal_ge_0.80") or {}).get("forward_after_200") or {}
    calibration = report.get("calibration_deep_summary") or {}
    raw = calibration.get("raw_v28_all") or {}
    brownian = calibration.get("brownian_all") or {}
    capped = calibration.get("locked_capped_aci_all") or {}
    diag = report.get("diagnostics") or {}
    prompt = f"""Search arXiv and related papers for implementable methods to turn an online calibrated terminal probability into a robust trading decision for a Kalshi BTC 15m probability-value bot.

Project context:
- We price P(BTC settles above/below a strike at 15m close), compare fair value to Kalshi ask/fees, and must pass forward-shadow validation before live promotion.
- Current local v28 scorer snapshot has {diag.get('matched_trade_count')} matched filled trades and {diag.get('settled_label_rows')} settlement labels.
- Raw v28 probability is overconfident and weakly ranked: all-row Brier about {raw.get('brier')}, log loss about {raw.get('log_loss')}, AUC about {raw.get('auc')}.
- Brownian terminal probability is better: Brier about {brownian.get('brier')}, log loss about {brownian.get('log_loss')}, AUC about {brownian.get('auc')}.
- A locked capped-ACI calibrator selected only on rows 1-200 is now promising:
  calibrator_id={locked.get('calibrator_id') or locked.get('name')},
  source=Brownian terminal probability,
  eta={locked.get('eta')},
  cap={locked.get('cap')},
  max_bias={locked.get('max_bias')},
  target coverage={locked.get('target_coverage')}.
- This calibrator achieved all-row Brier about {capped.get('brier')}, log loss about {capped.get('log_loss')}, and coverage about {capped.get('coverage')} in retrospective prequential replay.
- The robust hybrid baseline replay is {robust.get('entries')} entries, net {robust.get('net_dollars')} dollars, avg {robust.get('avg_cents_per_entry')} cents per entry.
- A train-locked calibrated gate selected on rows 1-200 produced forward-after-200 replay of {forward.get('entries')} entries, net {forward.get('net_dollars')} dollars, avg {forward.get('avg_cents_per_entry')} cents per entry. This is still retrospective and must be forward-shadowed.
- The most interesting practical overlay was robust_hybrid + p_calibrated >= 0.80: forward-after-200 replay of {overlay.get('entries')} entries, net {overlay.get('net_dollars')} dollars, avg {overlay.get('avg_cents_per_entry')} cents per entry, win rate {overlay.get('win_rate_ex_flats')}.

What I need from the literature:
1. Online probability calibration for binary time series where the base model ranking is weak:
   - capped/bounded ACI,
   - calibration with probability clipping,
   - beta calibration / temperature scaling / logistic recalibration,
   - calibration that preserves ranking vs calibration that intentionally shrinks to base rates.
2. Decision rules that turn calibrated probabilities into trade/no-trade gates:
   - conformal selective classification,
   - reject-option classification,
   - risk-controlling prediction sets,
   - Kelly/fractional Kelly with imprecise probability intervals,
   - cost-sensitive calibration for asymmetric payoff/fees.
3. Validation methods specifically for small nonstationary binary trading samples:
   - prequential scoring,
   - locked train/validation/OOS protocols,
   - e-processes for calibrated edge,
   - avoiding selection bias when choosing calibration hyperparameters.

For each paper, return:
- citation, year, link;
- exact mapping to this Kalshi BTC 15m problem;
- a concrete experiment using these existing columns: p28, Brownian terminal p, p_calibrated, ACI bias/q, settlement side, ask, fee, edge, depth_ratio, book_age_ms, seconds_to_close, abs_d_sigma, realized PnL;
- promotion gates with numeric thresholds;
- failure modes and how this could overfit the {diag.get('matched_trade_count')}-row retrospective log.

Prioritize methods that can answer:
- Should p_calibrated replace p28 for fair value?
- Should p_calibrated be only a risk monitor?
- How should we size/skip trades when calibrated probability improves Brier/log loss but hard edge gates reduce replay PnL?
- What forward-shadow sample size is needed before live use?
"""
    TRUFFLE_PROMPT.write_text(prompt, encoding="utf-8")


def build_report() -> dict[str, Any]:
    rows, diagnostics, locked, deep_report = annotate_rows()
    fixed = fixed_strategies(rows)
    locked_gate = choose_locked_gate(rows)
    locked_gate_predicate: Predicate | None = None
    if locked_gate:
        # Rebuild the predicate by name from the grid; keeps JSON clean.
        for config in family_grid():
            if config["name"] == locked_gate["name"]:
                locked_gate_predicate = config["predicate"]
                break
    deep_baseline = deep_report.get("baseline") or {}
    locked_deep = ((deep_report.get("calibrator_grid") or {}).get("locked_train200") or {}).get("scores") or {}
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only PnL projection for locked capped-ACI probability candidate.",
        "diagnostics": diagnostics,
        "locked_calibrator": locked,
        "calibration_deep_summary": {
            "raw_v28_all": {
                **(((deep_baseline.get("scores") or {}).get("p28") or {}).get("all") or {}),
                "auc": ((((deep_baseline.get("discrimination") or {}).get("p28") or {}).get("all") or {}).get("auc")),
            },
            "brownian_all": {
                **(((deep_baseline.get("scores") or {}).get("brownian_terminal_p_side") or {}).get("all") or {}),
                "auc": ((((deep_baseline.get("discrimination") or {}).get("brownian_terminal_p_side") or {}).get("all") or {}).get("auc")),
            },
            "locked_capped_aci_all": locked_deep.get("all") or {},
        },
        "fixed_strategies": fixed,
        "train_locked_gate": locked_gate,
        "projection_summary": projection_summary(rows, fixed, locked_gate),
        "e_process_checks": e_process_checks(rows, locked_gate_predicate),
        "daily_slices": daily_slices(rows, locked_gate_predicate) if locked_gate_predicate is not None else [],
        "notes": [
            "PnL is replay over recorded filled v28 trades only; it does not include opportunities the live bot skipped.",
            "Model EV uses calibrated_edge_cents times recorded quantity as an approximate model-implied edge sum.",
            "Train-locked gate is selected only on rows 1-200 using positive average PnL and 2/3 positive train subsplits.",
            "E-process checks are rough anytime-valid diagnostics over realized PnL cents with a fixed lambda grid; no crossing means no promotion-level statistical proof.",
        ],
    }
    write_truffle_prompt(report)
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


def num(value: Any, digits: int = 2) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:.{digits}f}"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Self-Calibrating ACI PnL Projection",
        "",
        "Research-only PnL projection for the locked capped-ACI probability candidate. This is replay over recorded filled v28 trades, not a live-trading change.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Locked calibrator: `{(report.get('locked_calibrator') or {}).get('calibrator_id') or 'capped_aci_brownian_terminal_p_side_eta0.20_cap0.90'}`",
        f"- Truffle prompt: `{TRUFFLE_PROMPT}`",
        "",
        "## Projection Summary",
        "",
        "| strategy | window | entries | W/L | win rate | PnL | avg/entry | coverage | model EV sum |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    summary = report.get("projection_summary") or {}
    for name, windows in summary.items():
        if not isinstance(windows, dict):
            continue
        for window in ("train_1_200", "validation_201_400", "holdout_401_end", "forward_after_200", "all"):
            row = windows.get(window) or {}
            lines.append(
                f"| {name} | {window} | {row.get('entries')} | {wl(row)} | {pct(row.get('win_rate_ex_flats'))} | "
                f"{money(row.get('net_dollars'))} | {cents(row.get('avg_cents_per_entry'))} | "
                f"{pct(row.get('coverage_of_live_entries'))} | {money(row.get('model_ev_dollars_sum'))} |"
            )
    lines.extend(
        [
            "",
            "## E-Process Sanity Check",
            "",
            "Rough anytime-valid diagnostic over realized PnL cents. Threshold 20 is the loose watch level; threshold 100 is the stricter promotion-level signal.",
            "",
            "| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    checks = report.get("e_process_checks") or {}
    for name in ("robust_hybrid_base", "robust_plus_p_cal_ge_0.80", "train_locked_calibrated_gate"):
        windows = ((checks.get(name) or {}).get("windows") or {})
        for window in ("train_1_200", "forward_after_200", "all"):
            row = windows.get(window) or {}
            best = row.get("best_by_max_capital") or {}
            lines.append(
                f"| {name} | {window} | {row.get('entries')} | {num(best.get('lambda'))} | "
                f"{num(best.get('final_capital'))} | {num(best.get('max_capital'))} | "
                f"{'yes' if row.get('crossed_20') else 'no'} | {'yes' if row.get('crossed_100') else 'no'} |"
            )
    locked_gate = report.get("train_locked_gate") or {}
    lines.extend(
        [
            "",
            "## Train-Locked Gate",
            "",
            f"- Selected gate: `{locked_gate.get('name')}`",
            f"- Family: `{locked_gate.get('family')}`",
            f"- Params: `{json.dumps(locked_gate.get('params') or {}, sort_keys=True)}`",
            f"- Train subsplit nets: `{locked_gate.get('subsplit_nets_cents')}` cents",
            "",
            "| candidate | train entries | train PnL | train avg | positive subsplits | min subsplit |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in locked_gate.get("top_candidates") or []:
        train = row.get("train") or {}
        nets = row.get("subsplit_nets_cents") or []
        min_net = min(nets) if nets else None
        lines.append(
            f"| {row.get('name')} | {train.get('entries')} | {money(train.get('net_dollars'))} | "
            f"{cents(train.get('avg_cents_per_entry'))} | {row.get('positive_subsplits')} | {cents(min_net)} |"
        )
    lines.extend(
        [
            "",
            "## Daily Slices For Train-Locked Gate",
            "",
            "| day | live rows | selected | W/L | PnL | avg/entry |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("daily_slices") or []:
        selected_stats = row.get("selected") or {}
        lines.append(
            f"| {row.get('day')} | {row.get('all_entries')} | {selected_stats.get('entries')} | {wl(selected_stats)} | "
            f"{money(selected_stats.get('net_dollars'))} | {cents(selected_stats.get('avg_cents_per_entry'))} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The capped-ACI probability is valuable as a probability scorer: it improves Brier/log loss materially.",
            "- As a hard edge replacement, it tends to shrink opportunity count; the best replay PnL still comes from the robust hybrid baseline.",
            "- The train-locked calibrated gate is useful as a forward-shadow candidate only if it keeps positive PnL after row 200 without relying on the train slice.",
            "- Do not wire this into live entries until the same locked candidate accumulates fresh shadow evidence.",
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
