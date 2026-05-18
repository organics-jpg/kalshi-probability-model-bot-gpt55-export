"""PASC: PnL-aware selective classification probe.

Research-only validation of Truffle's PASC proposal. The probe replaces a fixed
probability threshold with a per-candidate expected-PnL rule:

    EV = p_cal * (100 - ask - fee) + (1 - p_cal) * (-ask)
         - c_miss * (1 - fill_prob)

It evaluates the rule over recorded filled v28 trades only. The fill probability
is a conservative depth-ratio proxy because the current 470-row replay does not
contain every unfilled/skipped candidate. Nothing here changes live bot logic or
places orders.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import probe_arxiv_strategy_priority_tests as priority
import probe_self_calibrating_aci_pnl_projection as aci_projection


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "pasc_pnl_aware_selective_classification_latest.json"
OUT_MD = OUT_DIR / "pasc_pnl_aware_selective_classification_latest.md"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"

Predicate = Callable[[dict[str, Any]], bool]

C_MISS_CENTS = 0.5
FILL_DEPTH_SCALE = 8.0
MIN_EDGE_GRID = (0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 10.0)
MIN_FILL_GRID = (0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80)
WFA_SPLITS = (
    (1, 50, 56, 75),
    (21, 70, 76, 95),
    (41, 90, 96, 115),
    (61, 110, 116, 135),
    (81, 130, 136, 155),
    (101, 150, 156, 175),
    (121, 170, 176, 195),
    (141, 190, 196, 215),
    (161, 210, 216, 235),
    (181, 230, 236, 255),
    (201, 250, 256, 275),
    (221, 270, 276, 295),
    (241, 290, 296, 315),
    (261, 310, 316, 335),
    (281, 330, 336, 355),
    (301, 350, 356, 375),
    (321, 370, 376, 395),
    (341, 390, 396, 415),
    (361, 410, 416, 435),
    (381, 430, 436, 455),
)
WINDOWS = {
    "train_1_200": (1, 200),
    "validation_201_300": (201, 300),
    "test_301_end": (301, None),
    "forward_after_200": (201, None),
    "all": (1, None),
}
E_PROCESS_LAMBDAS = (0.02, 0.05, 0.10, 0.20, 0.35)
E_PROCESS_THRESHOLDS = (20.0, 100.0)


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else parsed


def row_window(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    out = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        out.append(row)
    return out


def fill_prob_proxy(row: dict[str, Any]) -> float:
    depth_ratio = max(0.0, fnum(row.get("depth_ratio")))
    if depth_ratio <= 0.0:
        return 0.05
    return max(0.05, min(0.95, depth_ratio / (depth_ratio + FILL_DEPTH_SCALE)))


def expected_pnl_cents(row: dict[str, Any], c_miss_cents: float = C_MISS_CENTS) -> float | None:
    p_cal = priority.maybe_float(row.get("p_calibrated"))
    ask = priority.maybe_float(row.get("ask_cents"))
    fee = priority.maybe_float(row.get("fee_cents"))
    if p_cal is None or ask is None or fee is None:
        return None
    fill_prob = fill_prob_proxy(row)
    return p_cal * (100.0 - ask - fee) + (1.0 - p_cal) * (-ask) - c_miss_cents * (1.0 - fill_prob)


def p_break_even(row: dict[str, Any], c_miss_cents: float = C_MISS_CENTS) -> float | None:
    ask = priority.maybe_float(row.get("ask_cents"))
    fee = priority.maybe_float(row.get("fee_cents"))
    if ask is None or fee is None or 100.0 - fee <= 0.0:
        return None
    return (ask + c_miss_cents * (1.0 - fill_prob_proxy(row))) / (100.0 - fee)


def execution_fill_diagnostics() -> dict[str, Any]:
    if not EXECUTION_EVENTS.exists():
        return {"path": str(EXECUTION_EVENTS), "exists": False}
    counts: Counter[str] = Counter()
    success_depth = []
    reject_depth = []
    success_book_age = []
    reject_book_age = []
    success_fill_counts = []
    for line in EXECUTION_EVENTS.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = str(row.get("event_type") or "")
        if event_type not in {"order_submit_start", "order_submit_success", "order_submit_reject"}:
            continue
        counts[event_type] += 1
        depth_required = priority.maybe_float(row.get("depth_required"))
        eligible_depth = priority.maybe_float(row.get("eligible_depth"))
        depth_ratio = eligible_depth / depth_required if depth_required and eligible_depth is not None else None
        book_age = priority.maybe_float(row.get("book_age_ms"))
        if event_type == "order_submit_success":
            success_fill_counts.append(fnum(row.get("fill_count")))
            if depth_ratio is not None:
                success_depth.append(depth_ratio)
            if book_age is not None:
                success_book_age.append(book_age)
        elif event_type == "order_submit_reject":
            if depth_ratio is not None:
                reject_depth.append(depth_ratio)
            if book_age is not None:
                reject_book_age.append(book_age)
    attempts = counts["order_submit_success"] + counts["order_submit_reject"]
    positive_fills = sum(1 for value in success_fill_counts if value > 0)
    return {
        "path": str(EXECUTION_EVENTS),
        "exists": True,
        "event_counts": dict(counts),
        "submit_outcome_attempts": attempts,
        "submit_success_rate": counts["order_submit_success"] / attempts if attempts else None,
        "submit_success_positive_fill_count": positive_fills,
        "submit_success_zero_fill_count": len(success_fill_counts) - positive_fills,
        "success_fill_count_positive_rate": positive_fills / len(success_fill_counts) if success_fill_counts else None,
        "success_depth_ratio_median": sorted(success_depth)[len(success_depth) // 2] if success_depth else None,
        "reject_depth_ratio_median": sorted(reject_depth)[len(reject_depth) // 2] if reject_depth else None,
        "success_book_age_ms_median": sorted(success_book_age)[len(success_book_age) // 2] if success_book_age else None,
        "reject_book_age_ms_median": sorted(reject_book_age)[len(reject_book_age) // 2] if reject_book_age else None,
        "read": "Exchange submit acceptance is high, but positive fill_count is much lower; PASC needs candidate-level fill modeling before fill_prob can be trusted.",
    }


def annotate_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics, _, _ = aci_projection.annotate_rows()
    out = []
    for row in rows:
        item = dict(row)
        ev = expected_pnl_cents(item)
        be = p_break_even(item)
        item["fill_prob_proxy"] = fill_prob_proxy(item)
        item["pasc_expected_pnl_cents"] = ev
        item["pasc_p_break_even"] = be
        item["pasc_edge_over_break_even"] = None if ev is None else ev / max(1e-9, 100.0 - fnum(item.get("fee_cents")))
        out.append(item)
    return out, diagnostics


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def robust_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if priority.robust_hybrid(row)]


def pasc_predicate(min_edge: float, min_fill: float, *, c_miss_cents: float = C_MISS_CENTS) -> Predicate:
    def predicate(row: dict[str, Any]) -> bool:
        ev = expected_pnl_cents(row, c_miss_cents)
        return (
            ev is not None
            and priority.robust_hybrid(row)
            and fill_prob_proxy(row) > min_fill
            and ev > min_edge
        )

    return predicate


def pcal_predicate(threshold: float) -> Predicate:
    return lambda row: priority.robust_hybrid(row) and fnum(row.get("p_calibrated"), -1.0) >= threshold


def strategy_stats(rows: list[dict[str, Any]], denominator: int, robust_denominator: int) -> dict[str, Any]:
    out = priority.stats(rows, denominator)
    out["coverage_of_robust_candidates"] = len(rows) / robust_denominator if robust_denominator else None
    evs = [fnum(row.get("pasc_expected_pnl_cents")) for row in rows if row.get("pasc_expected_pnl_cents") is not None]
    out["avg_expected_pnl_cents"] = sum(evs) / len(evs) if evs else None
    return out


def evaluate_strategy(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        chunk = row_window(rows, start, end)
        chosen = selected(chunk, predicate)
        out[name] = strategy_stats(chosen, len(chunk), len(robust_rows(chunk)))
    return out


def candidate_grid(rows: list[dict[str, Any]], *, min_entries: int = 5) -> list[dict[str, Any]]:
    robust_denominator = len(robust_rows(rows))
    candidates = []
    for min_edge in MIN_EDGE_GRID:
        for min_fill in MIN_FILL_GRID:
            pred = pasc_predicate(min_edge, min_fill)
            chosen = selected(rows, pred)
            if len(chosen) < min_entries:
                continue
            row_stats = strategy_stats(chosen, len(rows), robust_denominator)
            candidates.append(
                {
                    "min_edge_cents": min_edge,
                    "min_fill": min_fill,
                    "stats": row_stats,
                    "objective_avg_x_robust_coverage": fnum(row_stats.get("avg_cents_per_entry"))
                    * fnum(row_stats.get("coverage_of_robust_candidates")),
                }
            )
    candidates.sort(
        key=lambda row: (
            row["objective_avg_x_robust_coverage"],
            fnum(row["stats"].get("net_dollars")),
            fnum(row["stats"].get("entries")),
        ),
        reverse=True,
    )
    return candidates


def lock_from_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    validation = row_window(rows, 201, 300)
    candidates = candidate_grid(validation, min_entries=5)
    if not candidates:
        return {}
    locked = dict(candidates[0])
    pred = pasc_predicate(float(locked["min_edge_cents"]), float(locked["min_fill"]))
    locked["windows"] = evaluate_strategy(rows, pred)
    locked["top_validation_candidates"] = [dict(row) for row in candidates[:12]]
    return locked


def rolling_wfa(rows: list[dict[str, Any]]) -> dict[str, Any]:
    windows = []
    aggregate_selected: list[dict[str, Any]] = []
    denominator = 0
    for split_idx, (train_start, train_end, test_start, test_end) in enumerate(WFA_SPLITS, start=1):
        train = row_window(rows, train_start, train_end)
        test = row_window(rows, test_start, test_end)
        denominator += len(test)
        candidates = candidate_grid(train, min_entries=3)
        lock = candidates[0] if candidates else None
        if lock is None:
            test_stats = strategy_stats([], len(test), len(robust_rows(test)))
            windows.append(
                {
                    "split_idx": split_idx,
                    "train": [train_start, train_end],
                    "test": [test_start, test_end],
                    "locked": None,
                    "test_stats": test_stats,
                }
            )
            continue
        pred = pasc_predicate(float(lock["min_edge_cents"]), float(lock["min_fill"]))
        chosen = selected(test, pred)
        aggregate_selected.extend(chosen)
        test_stats = strategy_stats(chosen, len(test), len(robust_rows(test)))
        windows.append(
            {
                "split_idx": split_idx,
                "train": [train_start, train_end],
                "test": [test_start, test_end],
                "locked": {
                    "min_edge_cents": lock["min_edge_cents"],
                    "min_fill": lock["min_fill"],
                    "train_stats": lock["stats"],
                },
                "test_stats": test_stats,
            }
        )
    nets = [fnum((window.get("test_stats") or {}).get("net_dollars")) for window in windows]
    entries = [fnum((window.get("test_stats") or {}).get("entries")) for window in windows]
    positive_with_trades = sum(1 for net, count in zip(nets, entries) if count > 0 and net > 0)
    windows_with_trades = sum(1 for count in entries if count > 0)
    total_net = sum(max(0.0, net) for net in nets)
    max_window_share = max((max(0.0, net) / total_net for net in nets), default=None) if total_net > 0 else None
    return {
        "split_count": len(windows),
        "windows": windows,
        "aggregate": strategy_stats(aggregate_selected, denominator, sum(len(robust_rows(row_window(rows, a, b))) for _, _, a, b in WFA_SPLITS)),
        "positive_windows_with_trades": positive_with_trades,
        "windows_with_trades": windows_with_trades,
        "max_positive_window_share": max_window_share,
    }


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
    for window_name in ("train_1_200", "validation_201_300", "test_301_end", "forward_after_200", "all"):
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


def promotion_check(locked: dict[str, Any], wfa: dict[str, Any], eproc: dict[str, Any]) -> dict[str, Any]:
    test = ((locked.get("windows") or {}).get("test_301_end") or {})
    gates = {
        "test_pnl_gt_8": fnum(test.get("net_dollars")) > 8.0,
        "test_robust_coverage_gt_20pct": fnum(test.get("coverage_of_robust_candidates")) > 0.20,
        "test_win_rate_gt_55pct": fnum(test.get("win_rate_ex_flats")) > 0.55,
        "test_avg_gt_15c": fnum(test.get("avg_cents_per_entry")) > 15.0,
        "wfa_positive_trade_windows_all": int(wfa.get("positive_windows_with_trades") or 0) == int(wfa.get("windows_with_trades") or -1)
        and int(wfa.get("windows_with_trades") or 0) > 0,
        "wfa_no_single_window_gt_40pct_positive_pnl": fnum(wfa.get("max_positive_window_share"), 1.0) <= 0.40,
        "e_process_test_crossed_100": bool(((eproc.get("test_301_end") or {}).get("best_by_max_capital") or {}).get("cross_at", {}).get("100") is not None),
        "e_process_train_not_crossed_100": not bool(((eproc.get("train_1_200") or {}).get("best_by_max_capital") or {}).get("cross_at", {}).get("100") is not None),
    }
    return {"gates": gates, "passes_all": all(gates.values())}


def build_report() -> dict[str, Any]:
    rows, diagnostics = annotate_rows()
    locked = lock_from_validation(rows)
    locked_pred = pasc_predicate(float(locked.get("min_edge_cents", 0.5)), float(locked.get("min_fill", 0.35))) if locked else pasc_predicate(0.5, 0.35)
    baselines = {
        "robust_hybrid_base": evaluate_strategy(rows, priority.robust_hybrid),
        "robust_plus_p_cal_ge_0.70": evaluate_strategy(rows, pcal_predicate(0.70)),
        "robust_plus_p_cal_ge_0.80": evaluate_strategy(rows, pcal_predicate(0.80)),
        "pasc_recommended_edge0.5_fill0.35": evaluate_strategy(rows, pasc_predicate(0.5, 0.35)),
    }
    if locked:
        baselines["pasc_validation_locked"] = locked.get("windows") or {}
    wfa = rolling_wfa(rows)
    eproc = {
        "pasc_validation_locked": e_process_for_strategy(rows, locked_pred),
        "robust_plus_p_cal_ge_0.70": e_process_for_strategy(rows, pcal_predicate(0.70)),
        "robust_plus_p_cal_ge_0.80": e_process_for_strategy(rows, pcal_predicate(0.80)),
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only validation of PASC PnL-aware selective classification.",
        "diagnostics": diagnostics,
        "ev_formula": {
            "c_miss_cents": C_MISS_CENTS,
            "fill_prob_proxy": f"depth_ratio / (depth_ratio + {FILL_DEPTH_SCALE}), clipped to [0.05, 0.95]",
            "note": "Replay has filled trades only, so fill_prob is a depth proxy, not a calibrated fill model.",
        },
        "validation_locked": locked,
        "baselines": baselines,
        "rolling_wfa": wfa,
        "e_process": eproc,
        "execution_fill_diagnostics": execution_fill_diagnostics(),
        "promotion_check": promotion_check(locked, wfa, eproc.get("pasc_validation_locked") or {}) if locked else {},
        "read": [
            "PASC is theoretically cleaner than a fixed probability threshold, but the current replay only supports it if it improves holdout and WFA metrics without test tuning.",
            "Because fill_prob is proxied from depth_ratio and all rows are filled trades, this cannot validate real IOC fillability.",
            "A live/shadow registry needs every considered candidate, including skipped and unfilled IOC attempts, before PASC can be promoted.",
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


def num(value: Any, digits: int = 2) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:.{digits}f}"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    locked = report.get("validation_locked") or {}
    lines = [
        "# PASC PnL-Aware Selective Classification",
        "",
        "Research-only replay over recorded filled trades. No live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{(report.get('diagnostics') or {}).get('matched_trade_count')}`",
        f"- Settled labels: `{(report.get('diagnostics') or {}).get('settled_label_rows')}`",
        f"- Fill probability: `{(report.get('ev_formula') or {}).get('fill_prob_proxy')}`",
        f"- Validation-locked min_edge: `{locked.get('min_edge_cents')}` cents",
        f"- Validation-locked min_fill: `{locked.get('min_fill')}`",
        "",
        "## Strategy Windows",
        "",
        "| strategy | window | entries | W/L | win rate | PnL | avg/entry | live coverage | robust coverage | avg expected PnL |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy_name, windows in (report.get("baselines") or {}).items():
        for window in ("train_1_200", "validation_201_300", "test_301_end", "forward_after_200", "all"):
            row = (windows or {}).get(window) or {}
            lines.append(
                f"| {strategy_name} | {window} | {row.get('entries')} | {wl(row)} | "
                f"{pct(row.get('win_rate_ex_flats'))} | {money(row.get('net_dollars'))} | "
                f"{cents(row.get('avg_cents_per_entry'))} | {pct(row.get('coverage_of_live_entries'))} | "
                f"{pct(row.get('coverage_of_robust_candidates'))} | {cents(row.get('avg_expected_pnl_cents'))} |"
            )
    lines.extend(
        [
            "",
            "## Top Validation Grid",
            "",
            "| min_edge | min_fill | entries | W/L | PnL | avg | robust coverage | objective |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in locked.get("top_validation_candidates") or []:
        stats_row = row.get("stats") or {}
        lines.append(
            f"| {row.get('min_edge_cents')} | {row.get('min_fill')} | {stats_row.get('entries')} | {wl(stats_row)} | "
            f"{money(stats_row.get('net_dollars'))} | {cents(stats_row.get('avg_cents_per_entry'))} | "
            f"{pct(stats_row.get('coverage_of_robust_candidates'))} | {num(row.get('objective_avg_x_robust_coverage'))} |"
        )
    wfa = report.get("rolling_wfa") or {}
    agg = wfa.get("aggregate") or {}
    lines.extend(
        [
            "",
            "## Rolling WFA",
            "",
            f"- Splits: `{wfa.get('split_count')}` rolling `50 train / 5 purge / 20 test` windows.",
            f"- Positive windows with trades: `{wfa.get('positive_windows_with_trades')}/{wfa.get('windows_with_trades')}`.",
            f"- Max positive-window PnL share: `{pct(wfa.get('max_positive_window_share'))}`.",
            "",
            "| aggregate entries | W/L | PnL | avg/entry | live coverage | robust coverage |",
            "|---:|---:|---:|---:|---:|---:|",
            f"| {agg.get('entries')} | {wl(agg)} | {money(agg.get('net_dollars'))} | {cents(agg.get('avg_cents_per_entry'))} | "
            f"{pct(agg.get('coverage_of_live_entries'))} | {pct(agg.get('coverage_of_robust_candidates'))} |",
            "",
            "| split | locked edge | locked fill | test entries | test W/L | test PnL | test avg |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for window in wfa.get("windows") or []:
        lock = window.get("locked") or {}
        test = window.get("test_stats") or {}
        lines.append(
            f"| {window.get('split_idx')} | {lock.get('min_edge_cents')} | {lock.get('min_fill')} | "
            f"{test.get('entries')} | {wl(test)} | {money(test.get('net_dollars'))} | {cents(test.get('avg_cents_per_entry'))} |"
        )
    fill = report.get("execution_fill_diagnostics") or {}
    counts = fill.get("event_counts") or {}
    lines.extend(
        [
            "",
            "## Execution Fill Diagnostic",
            "",
            f"- Entry submit starts: `{counts.get('order_submit_start')}`.",
            f"- Entry submit successes: `{counts.get('order_submit_success')}`.",
            f"- Entry submit rejects: `{counts.get('order_submit_reject')}`.",
            f"- Exchange submit success rate: `{pct(fill.get('submit_success_rate'))}`.",
            f"- Positive fill_count among submit successes: `{pct(fill.get('success_fill_count_positive_rate'))}` "
            f"(`{fill.get('submit_success_positive_fill_count')}` positive / `{fill.get('submit_success_zero_fill_count')}` zero-fill).",
            f"- Median depth_ratio success/reject: `{num(fill.get('success_depth_ratio_median'))}` / `{num(fill.get('reject_depth_ratio_median'))}`.",
            f"- Median book_age_ms success/reject: `{num(fill.get('success_book_age_ms_median'))}` / `{num(fill.get('reject_book_age_ms_median'))}`.",
        ]
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
        for window in ("train_1_200", "validation_201_300", "test_301_end", "forward_after_200", "all"):
            row = (windows or {}).get(window) or {}
            best = row.get("best_by_max_capital") or {}
            lines.append(
                f"| {name} | {window} | {row.get('entries')} | {num(best.get('lambda'), 2)} | "
                f"{num(best.get('final_capital'), 2)} | {num(best.get('max_capital'), 2)} | "
                f"{'yes' if row.get('crossed_20') else 'no'} | {'yes' if row.get('crossed_100') else 'no'} |"
            )
    promo = report.get("promotion_check") or {}
    lines.extend(
        [
            "",
            "## Promotion Check",
            "",
            f"- Passes all: `{promo.get('passes_all')}`",
            "",
            "| gate | pass |",
            "|---|---|",
        ]
    )
    for key, value in (promo.get("gates") or {}).items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- PASC is conceptually right to optimize PnL instead of classification loss, but this retrospective filled-trade replay does not beat the existing ACI threshold overlays.",
            "- The validation-locked PASC gate misses the Truffle projected PnL target on the 301-end holdout.",
            "- The right next step is logging PASC fields for every live/shadow candidate, including non-trades and unfilled IOC attempts, before treating fill_prob as real.",
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
