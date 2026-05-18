"""Triage the second Truffle strategy batch against current local evidence.

Research-only. This probe checks which ideas can be validated with the current
470-row matched filled-trade replay and which require new shadow/logging data.

Key distinction: Kalshi BTC 15m resolves on terminal settlement above/below
strike, not on whether BTC touched/crossed the strike before expiry.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable

import probe_arxiv_strategy_priority_tests as priority
import probe_self_calibrating_aci_pnl_projection as aci_projection


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "truffle_second_output_triage_latest.json"
OUT_MD = OUT_DIR / "truffle_second_output_triage_latest.md"

WINDOWS = {
    "train_1_200": (1, 200),
    "validation_201_300": (201, 300),
    "test_301_end": (301, None),
    "forward_after_200": (201, None),
    "all": (1, None),
}
PROB_THRESHOLDS = (0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
E_PROCESS_LAMBDAS = (0.02, 0.05, 0.10, 0.20, 0.35)
E_PROCESS_THRESHOLDS = (20.0, 100.0)

Predicate = Callable[[dict[str, Any]], bool]


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else parsed


def clamp(value: float, low: float = 1e-6, high: float = 1.0 - 1e-6) -> float:
    return min(high, max(low, value))


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def row_window(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    out = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        out.append(row)
    return out


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def robust_hybrid(row: dict[str, Any]) -> bool:
    return priority.robust_hybrid(row)


def brownian_touch_probability_side(row: dict[str, Any]) -> float | None:
    """Zero-drift Brownian probability of touching the strike before expiry.

    This is useful as a sanity test, but it is not Kalshi's terminal settlement
    probability. For a YES side, already above strike implies touch probability
    1; below strike uses reflection principle. For NO, symmetric.
    """
    btc = priority.maybe_float(row.get("btc_price"))
    strike = priority.maybe_float(row.get("strike"))
    sigma = priority.maybe_float(row.get("sigma_t_dollars"))
    side = str(row.get("side") or "").lower()
    if btc is None or strike is None or sigma is None or sigma <= 0 or side not in {"yes", "no"}:
        return None
    z = abs(btc - strike) / sigma
    cross = clamp(2.0 * (1.0 - normal_cdf(z)))
    if side == "yes":
        return 1.0 if btc >= strike else cross
    return 1.0 if btc <= strike else cross


def annotate_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics, _, _ = aci_projection.annotate_rows()
    out = []
    for row in rows:
        item = dict(row)
        item["brownian_touch_p_side"] = brownian_touch_probability_side(item)
        btc = priority.maybe_float(item.get("btc_price"))
        strike = priority.maybe_float(item.get("strike"))
        side = str(item.get("side") or "").lower()
        if btc is not None and strike is not None and strike > 0:
            item["distance_from_strike_pct"] = abs(btc - strike) / strike
            item["current_above_strike"] = btc > strike
            if side in {"yes", "no"}:
                item["side_matches_current_location"] = (side == "yes" and btc > strike) or (side == "no" and btc < strike)
        out.append(item)
    return out, diagnostics


def probability_scores(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        pairs = []
        labels = []
        scores = []
        for row in row_window(rows, start, end):
            y = priority.maybe_float(row.get("side_correct"))
            p = priority.maybe_float(row.get(key))
            if y is None or p is None:
                continue
            p = clamp(p)
            pairs.append((p, y))
            labels.append(int(y))
            scores.append(p)
        if not pairs:
            out[name] = {"rows": 0}
            continue
        out[name] = {
            "rows": len(pairs),
            "brier": mean([(p - y) ** 2 for p, y in pairs]),
            "log_loss": mean([-(y * math.log(p) + (1.0 - y) * math.log(1.0 - p)) for p, y in pairs]),
            "auc": priority.auc_score(labels, scores),
        }
    return out


def strategy_stats(rows: list[dict[str, Any]], denominator: int, robust_denominator: int) -> dict[str, Any]:
    out = priority.stats(rows, denominator)
    out["coverage_of_robust_candidates"] = len(rows) / robust_denominator if robust_denominator else None
    return out


def evaluate_strategy(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        chunk = row_window(rows, start, end)
        chosen = selected(chunk, predicate)
        robust_count = sum(1 for row in chunk if robust_hybrid(row))
        out[name] = strategy_stats(chosen, len(chunk), robust_count)
    return out


def robust_plus_probability(key: str, threshold: float) -> Predicate:
    return lambda row: robust_hybrid(row) and fnum(row.get(key), -1.0) >= threshold


def probability_overlay_grid(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for key in ("brownian_terminal_p_side", "brownian_touch_p_side", "p_calibrated"):
        for threshold in PROB_THRESHOLDS:
            name = f"robust_plus_{key}_ge_{threshold:.2f}"
            out[name] = {"probability_key": key, "threshold": threshold, "windows": evaluate_strategy(rows, robust_plus_probability(key, threshold))}
    return out


def best_overlays(grid: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, item in grid.items():
        train = (item.get("windows") or {}).get("train_1_200") or {}
        test = (item.get("windows") or {}).get("test_301_end") or {}
        forward = (item.get("windows") or {}).get("forward_after_200") or {}
        if fnum(train.get("avg_cents_per_entry")) <= 0 or fnum(test.get("entries")) < 10:
            continue
        rows.append(
            {
                "name": name,
                "probability_key": item.get("probability_key"),
                "threshold": item.get("threshold"),
                "train": train,
                "test_301_end": test,
                "forward_after_200": forward,
                "score": (fnum(test.get("net_dollars")), fnum(test.get("avg_cents_per_entry")), fnum(forward.get("net_dollars"))),
            }
        )
    rows.sort(key=lambda row: row["score"], reverse=True)
    return rows[:15]


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
    return {"lambda": lam, "final_capital": capital, "max_capital": max_capital, "cross_at": crosses}


def e_process_for_strategy(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {}
    for window_name in ("train_1_200", "test_301_end", "forward_after_200", "all"):
        start, end = WINDOWS[window_name]
        chosen = selected(row_window(rows, start, end), predicate)
        values = [fnum(row.get("pnl_cents")) for row in chosen]
        paths = [e_process_path(values, lam) for lam in E_PROCESS_LAMBDAS]
        best = max(paths, key=lambda row: fnum(row.get("max_capital"))) if paths else {}
        out[window_name] = {
            "entries": len(chosen),
            "net_dollars": sum(values) / 100.0,
            "best_by_max_capital": best,
            "crossed_20": any((path.get("cross_at") or {}).get("20") is not None for path in paths),
            "crossed_100": any((path.get("cross_at") or {}).get("100") is not None for path in paths),
        }
    return out


def settlement_reversion_tests(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Test Strategy 5 as label-only evidence, not executable PnL.

    Fade-current-location wins if BTC is currently above strike and the market
    settles NO, or currently below strike and settles YES.
    """
    out = {}
    for seconds_max in (180, 240, 300):
        for distance_pct in (0.0002, 0.0005, 0.0010, 0.0015):
            subset = []
            for row in rows:
                y = priority.maybe_float(row.get("side_correct"))
                current_above = row.get("current_above_strike")
                seconds = priority.maybe_float(row.get("seconds_to_close"))
                distance = priority.maybe_float(row.get("distance_from_strike_pct"))
                if y is None or current_above is None or seconds is None or distance is None:
                    continue
                if seconds > seconds_max or distance < distance_pct:
                    continue
                actual_yes = str(row.get("settlement_result") or "").lower() == "yes"
                fade_wins = (current_above and not actual_yes) or ((not current_above) and actual_yes)
                subset.append({"fade_wins": fade_wins, "row": row})
            wins = sum(1 for item in subset if item["fade_wins"])
            n = len(subset)
            out[f"last_{seconds_max}s_dist_ge_{distance_pct:.4f}"] = {
                "seconds_max": seconds_max,
                "distance_pct": distance_pct,
                "rows": n,
                "fade_win_rate": wins / n if n else None,
                "wins": wins,
                "losses": n - wins,
            }
    return out


def data_readiness(rows: list[dict[str, Any]]) -> dict[str, Any]:
    first = rows[0] if rows else {}
    return {
        "brownian_bridge_crossing": {
            "status": "testable_as_sanity_check",
            "caveat": "Kalshi resolves terminal above/below strike; touch/crossing probability is not the settlement target.",
            "available_columns": ["btc_price", "strike", "sigma_t_dollars", "seconds_to_close", "settlement_result"],
        },
        "kalshi_spot_lead_lag": {
            "status": "not_testable_from_470_row_replay",
            "missing": ["synchronized 100ms BTC spot ticks", "Kalshi quote update timestamps for every tick", "counterfactual executable asks before/after lag"],
        },
        "conformal_predictive_band": {
            "status": "partially_testable_only_as_binary_calibration",
            "missing": ["continuous settlement price label per market", "rolling OHLCV feature matrix at every candidate timestamp"],
            "available_binary_columns": [key for key in ("p28", "brownian_terminal_p_side", "p_calibrated", "side_correct") if key in first],
        },
        "order_book_imbalance_regime": {
            "status": "not_testable_from_matched_trade_rows",
            "missing": ["top bid/ask depth on both sides at every snapshot", "persistent imbalance windows", "BTC ATR/ADX regime features"],
        },
        "settlement_window_mean_reversion": {
            "status": "label_testable_not_pnl_testable",
            "missing": ["opposite-side executable ask/bid near settlement", "continuous last-3-minute BTC path", "news/event filter"],
        },
    }


def build_report() -> dict[str, Any]:
    rows, diagnostics = annotate_rows()
    scores = {
        "terminal_brownian": probability_scores(rows, "brownian_terminal_p_side"),
        "touch_brownian": probability_scores(rows, "brownian_touch_p_side"),
        "capped_aci": probability_scores(rows, "p_calibrated"),
        "raw_p28": probability_scores(rows, "p28"),
    }
    overlay_grid = probability_overlay_grid(rows)
    best = best_overlays(overlay_grid)
    eproc = {
        "robust_hybrid_base": e_process_for_strategy(rows, robust_hybrid),
        "robust_plus_p_cal_ge_0.70": e_process_for_strategy(rows, robust_plus_probability("p_calibrated", 0.70)),
        "robust_plus_p_cal_ge_0.80": e_process_for_strategy(rows, robust_plus_probability("p_calibrated", 0.80)),
        "robust_plus_touch_ge_0.80": e_process_for_strategy(rows, robust_plus_probability("brownian_touch_p_side", 0.80)),
        "robust_plus_terminal_ge_0.70": e_process_for_strategy(rows, robust_plus_probability("brownian_terminal_p_side", 0.70)),
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only triage of second Truffle strategy output.",
        "diagnostics": diagnostics,
        "probability_scores": scores,
        "probability_overlay_grid": overlay_grid,
        "best_overlays": best,
        "e_process": eproc,
        "settlement_reversion_label_tests": settlement_reversion_tests(rows),
        "data_readiness": data_readiness(rows),
        "read": [
            "Brownian terminal probability is aligned with Kalshi settlement; Brownian touch/crossing is a sanity check but not the target label.",
            "The current log can compare probability transforms and filled-trade selectors, but cannot validate lead-lag, order-book imbalance, or full conformal price bands.",
            "Settlement-window mean reversion can be label-tested, but executable counterfactual PnL needs opposite-side quotes near settlement.",
        ],
    }


def money(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{100.0 * parsed:.1f}%"


def num(value: Any, digits: int = 4) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:.{digits}f}"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Truffle Second Output Triage",
        "",
        "Research-only stress test over the current matched filled-trade replay. No live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{(report.get('diagnostics') or {}).get('matched_trade_count')}`",
        f"- Settled labels: `{(report.get('diagnostics') or {}).get('settled_label_rows')}`",
        "",
        "## Probability Sanity Check",
        "",
        "| model | window | rows | Brier | log loss | AUC |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for model_name, windows in (report.get("probability_scores") or {}).items():
        for window in ("train_1_200", "validation_201_300", "test_301_end", "forward_after_200", "all"):
            row = (windows or {}).get(window) or {}
            lines.append(
                f"| {model_name} | {window} | {row.get('rows')} | {num(row.get('brier'))} | "
                f"{num(row.get('log_loss'))} | {num(row.get('auc'), 3)} |"
            )
    lines.extend(
        [
            "",
            "## Best Filled-Trade Overlays",
            "",
            "| rank | strategy | train PnL | test entries | test W/L | test PnL | test avg | forward PnL | forward avg |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for idx, row in enumerate(report.get("best_overlays") or [], start=1):
        train = row.get("train") or {}
        test = row.get("test_301_end") or {}
        forward = row.get("forward_after_200") or {}
        lines.append(
            f"| {idx} | {row.get('name')} | {money(train.get('net_dollars'))} | {test.get('entries')} | "
            f"{wl(test)} | {money(test.get('net_dollars'))} | {cents(test.get('avg_cents_per_entry'))} | "
            f"{money(forward.get('net_dollars'))} | {cents(forward.get('avg_cents_per_entry'))} |"
        )
    lines.extend(
        [
            "",
            "## E-Process",
            "",
            "| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for name, windows in (report.get("e_process") or {}).items():
        for window in ("train_1_200", "test_301_end", "forward_after_200", "all"):
            row = (windows or {}).get(window) or {}
            best = row.get("best_by_max_capital") or {}
            lines.append(
                f"| {name} | {window} | {row.get('entries')} | {num(best.get('lambda'), 2)} | "
                f"{num(best.get('final_capital'), 2)} | {num(best.get('max_capital'), 2)} | "
                f"{'yes' if row.get('crossed_20') else 'no'} | {'yes' if row.get('crossed_100') else 'no'} |"
            )
    lines.extend(
        [
            "",
            "## Settlement Reversion Label Test",
            "",
            "| rule | rows | fade W/L | fade win rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for name, row in (report.get("settlement_reversion_label_tests") or {}).items():
        if fnum(row.get("rows")) < 5:
            continue
        lines.append(f"| {name} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | {pct(row.get('fade_win_rate'))} |")
    lines.extend(
        [
            "",
            "## Data Readiness",
            "",
            "| strategy family | status | missing/caveat |",
            "|---|---|---|",
        ]
    )
    for name, row in (report.get("data_readiness") or {}).items():
        missing = row.get("missing") or row.get("caveat") or ""
        if isinstance(missing, list):
            missing = "; ".join(str(item) for item in missing)
        lines.append(f"| {name} | {row.get('status')} | {missing} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The Brownian bridge/crossing strategy should be reframed as terminal probability for Kalshi settlement; touch probability is overconfident for this label.",
            "- The current best immediate candidate remains the capped-ACI terminal-probability overlay, not pure Brownian crossing.",
            "- Lead-lag, conformal price bands, OBI/regime, and settlement mean reversion all need richer candidate-level logging before honest PnL validation.",
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
