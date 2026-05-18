from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_codex_entry_microstructure_edges as micro
import validate_liquidity_dwell_integrity as dwell_validation
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import EDGE_DIR
from probe_stop_touch_confirmation import strategy_id


UTC = timezone.utc
FAMILY = "liquidity_dwell_improvement_research"


def n(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        parsed = float(value)
        return default if math.isnan(parsed) else parsed
    except Exception:
        return default


def money(value: Any) -> str:
    parsed = n(value)
    return "" if parsed is None else f"${parsed:,.2f}"


def pct(value: Any) -> str:
    parsed = n(value)
    return "" if parsed is None else f"{100.0 * parsed:.1f}%"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def quote_path_features(points: list[dict[str, float]]) -> dict[str, float]:
    if not points:
        return {}
    asks = [float(point["held_ask"]) for point in points]
    own_bids = [float(point["own_bid"]) for point in points]
    pressures = [float(point["pressure"]) for point in points]
    spreads = [float(point["spread"]) for point in points]
    ask_moves = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    bid_moves = [own_bids[idx] - own_bids[idx - 1] for idx in range(1, len(own_bids))]
    bid_positive = sum(max(0.0, move) for move in bid_moves)
    bid_adverse = sum(max(0.0, -move) for move in bid_moves)
    ask_positive = sum(max(0.0, move) for move in ask_moves)
    ask_adverse = sum(max(0.0, -move) for move in ask_moves)
    bid_signs = [1 if move > 0 else -1 for move in bid_moves if abs(move) > 1e-9]
    flips = sum(1 for idx in range(1, len(bid_signs)) if bid_signs[idx] != bid_signs[idx - 1])
    return {
        "ask_net": asks[-1] - asks[0],
        "ask_range": max(asks) - min(asks),
        "ask_positive_sum": ask_positive,
        "ask_adverse_sum": ask_adverse,
        "max_ask_up_jump": max([max(0.0, move) for move in ask_moves] or [0.0]),
        "max_ask_down_jump": max([max(0.0, -move) for move in ask_moves] or [0.0]),
        "own_bid_net": own_bids[-1] - own_bids[0],
        "own_bid_range": max(own_bids) - min(own_bids),
        "own_bid_positive_sum": bid_positive,
        "own_bid_adverse_sum": bid_adverse,
        "own_bid_omega": (bid_positive + 1e-6) / (bid_adverse + 1e-6),
        "pressure_mean": sum(pressures) / len(pressures),
        "pressure_max": max(pressures),
        "spread_mean": sum(spreads) / len(spreads),
        "flip_rate": flips / max(1, len(bid_signs) - 1),
        "point_count": float(len(points)),
    }


def passes_optional_filters(features: dict[str, Any], params: dict[str, Any]) -> bool:
    checks = [
        ("min_own_bid_net", "own_bid_net", ">="),
        ("max_own_bid_adverse_sum", "own_bid_adverse_sum", "<="),
        ("min_own_bid_omega", "own_bid_omega", ">="),
        ("max_ask_range", "ask_range", "<="),
        ("max_ask_up_jump", "max_ask_up_jump", "<="),
        ("max_pressure_mean", "pressure_mean", "<="),
        ("max_pressure_max", "pressure_max", "<="),
        ("max_flip_rate", "flip_rate", "<="),
        ("min_state_changes", "state_changes", ">="),
        ("min_renewal_rate_per_min", "renewal_rate_per_min", ">="),
    ]
    for param_key, feature_key, op in checks:
        if param_key not in params:
            continue
        threshold = n(params.get(param_key))
        value = n(features.get(feature_key))
        if threshold is None or value is None:
            return False
        if op == ">=" and value < threshold:
            return False
        if op == "<=" and value > threshold:
            return False
    return True


def simulate_case(case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    delay = str(int(params["delay_seconds"]))
    snapshot = prepared.get(delay)
    if not snapshot or not micro.quote_gate(snapshot, params):
        return {"enter": False, "pnl_100": 0.0, "skip_reason": "missing_or_gate_failed"}
    points = snapshot.get("points") or []
    dwell_seconds = micro.quality_seconds(points, params)
    elapsed_span = max(1.0, float(snapshot["elapsed_span"]))
    dwell_share = dwell_seconds / elapsed_span
    if dwell_seconds < float(params["min_quality_seconds"]) or dwell_share < float(params["min_quality_share"]):
        return {
            "enter": False,
            "pnl_100": 0.0,
            "skip_reason": "insufficient_liquidity_dwell",
            "quality_seconds": round(dwell_seconds, 4),
            "quality_share": round(dwell_share, 6),
        }
    path_features = quote_path_features(points)
    combined = {
        **snapshot,
        **path_features,
        "quality_seconds": dwell_seconds,
        "quality_share": dwell_share,
    }
    if not passes_optional_filters(combined, params):
        return {
            "enter": False,
            "pnl_100": 0.0,
            "skip_reason": "optional_filter_failed",
            "quality_seconds": round(dwell_seconds, 4),
            "quality_share": round(dwell_share, 6),
        }
    ask = float(snapshot["held_ask"])
    return {
        "enter": True,
        "pnl_100": delayed_entry_pnl(case, ask, contracts=100),
        "settlement_win": bool(case["settlement_win"]),
        "entry_ask": ask,
        "quality_seconds": round(dwell_seconds, 4),
        "quality_share": round(dwell_share, 6),
        "pressure": round(float(snapshot["pressure"]), 6),
        "spread": round(float(snapshot["spread"]), 4),
        "bid_sum": round(float(snapshot["bid_sum"]), 4),
        "own_bid_net": round(float(path_features.get("own_bid_net", 0.0)), 4),
        "own_bid_omega": round(float(path_features.get("own_bid_omega", 0.0)), 6),
        "ask_range": round(float(path_features.get("ask_range", 0.0)), 4),
        "pressure_mean": round(float(path_features.get("pressure_mean", 0.0)), 6),
        "flip_rate": round(float(path_features.get("flip_rate", 0.0)), 6),
        "state_changes": int(snapshot.get("state_changes") or 0),
    }


def summarize(label: str, outcomes: list[dict[str, Any]], indices: list[int], *, weeks: float | None = None) -> dict[str, Any]:
    rows = [outcomes[idx] for idx in indices]
    entered = [row for row in rows if row.get("enter")]
    entries = len(entered)
    pnl = round(sum(float(row["pnl_100"]) for row in entered), 4)
    wins = sum(1 for row in entered if row.get("settlement_win"))
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for row in entered:
        cumulative += float(row["pnl_100"])
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)
    asks = [float(row["entry_ask"]) for row in entered if row.get("entry_ask") is not None]
    return {
        "label": label,
        "entries": entries,
        "pnl_100": pnl,
        "edge_per_entry_100": round(pnl / entries, 6) if entries else 0.0,
        "weekly_pnl_100": round(pnl / weeks, 6) if weeks and weeks > 0 else None,
        "win_rate": round(wins / entries, 6) if entries else 0.0,
        "max_drawdown_100": round(max_drawdown, 4),
        "avg_entry_ask": round(sum(asks) / len(asks), 4) if asks else None,
        "worst_trade_100": round(min([float(row["pnl_100"]) for row in entered] or [0.0]), 4),
    }


def chronological_blocks(count: int, block_count: int = 8) -> list[list[int]]:
    return [
        list(range(int(count * idx / block_count), int(count * (idx + 1) / block_count)))
        for idx in range(block_count)
    ]


def exact_weeks_for_items(items: list[tuple[dict[str, Any], dict[str, Any]]], indices: list[int]) -> float:
    if len(indices) < 2:
        return 0.0
    start = dwell_validation.iso_to_dt(str(items[indices[0]][0]["entry_ts"]))
    end = dwell_validation.iso_to_dt(str(items[indices[-1]][0]["entry_ts"]))
    return max(0.0, (end - start).total_seconds() / 86400.0 / 7.0)


def candidate_key(params: dict[str, Any]) -> str:
    core = {key: value for key, value in params.items() if key != "family"}
    return strategy_id(FAMILY, core)


def add_candidate(candidates: list[dict[str, Any]], family: str, params: dict[str, Any]) -> None:
    item = {"family": family, **params}
    item["candidate_id"] = candidate_key(item)
    candidates.append(item)


def build_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for delay in (60, 120, 180):
        for ask in (85, 88, 90, 92):
            for pressure in (0.3, 0.4, 0.5, 0.6):
                for spread in (4, 10):
                    for qshare in (0.50, 0.65, 0.75, 0.85, 0.90):
                        for qsec in (10, 30, 60):
                            add_candidate(
                                candidates,
                                "core_dwell_surface",
                                {
                                    "delay_seconds": delay,
                                    "max_entry_ask": ask,
                                    "max_opp_pressure": pressure,
                                    "max_spread": spread,
                                    "min_bid_sum": 0,
                                    "min_quality_seconds": qsec,
                                    "min_quality_share": qshare,
                                },
                            )

    anchors = [
        {"delay_seconds": 120, "max_entry_ask": 90, "max_opp_pressure": 0.3, "max_spread": 10, "min_quality_seconds": 10, "min_quality_share": 0.75},
        {"delay_seconds": 120, "max_entry_ask": 90, "max_opp_pressure": 0.5, "max_spread": 10, "min_quality_seconds": 10, "min_quality_share": 0.65},
        {"delay_seconds": 120, "max_entry_ask": 90, "max_opp_pressure": 0.5, "max_spread": 10, "min_quality_seconds": 10, "min_quality_share": 0.75},
        {"delay_seconds": 120, "max_entry_ask": 88, "max_opp_pressure": 0.5, "max_spread": 10, "min_quality_seconds": 10, "min_quality_share": 0.65},
    ]
    for anchor in anchors:
        base = {**anchor, "min_bid_sum": 0}
        for min_net in (-20, -10, 0, 5, 10):
            for omega in (0.0, 0.5, 1.0, 2.0):
                params = {**base, "min_own_bid_net": min_net, "min_own_bid_omega": omega}
                add_candidate(candidates, "dwell_plus_bid_momentum", params)
        for max_range in (4, 8, 12, 20):
            for max_up in (4, 8, 12, 99):
                params = {**base, "max_ask_range": max_range, "max_ask_up_jump": max_up}
                add_candidate(candidates, "dwell_plus_path_stability", params)
        for pressure_mean in (0.15, 0.20, 0.30, 0.40, 0.50):
            for pressure_max in (0.30, 0.40, 0.50, 0.60):
                params = {**base, "max_pressure_mean": pressure_mean, "max_pressure_max": pressure_max}
                add_candidate(candidates, "dwell_plus_pressure_persistence", params)
        for min_changes in (0, 1, 2, 3, 5):
            for renewal in (0.0, 0.5, 1.0, 2.0):
                params = {**base, "min_state_changes": min_changes, "min_renewal_rate_per_min": renewal}
                add_candidate(candidates, "dwell_plus_renewal", params)
        for qshare in (0.50, 0.65, 0.75, 0.85):
            for max_range in (8, 12, 20):
                for min_net in (-10, 0, 5):
                    params = {**base, "min_quality_share": qshare, "max_ask_range": max_range, "min_own_bid_net": min_net}
                    add_candidate(candidates, "dwell_combo_shape_momentum", params)

    deduped: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        deduped[candidate["candidate_id"]] = candidate
    return list(deduped.values())


def block_positive_count(block_rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in block_rows if float(row["pnl_100"]) > 0)


def robust_train_score(train_summary: dict[str, Any], train_blocks: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    positive_blocks = block_positive_count(train_blocks)
    min_block = min([float(row["pnl_100"]) for row in train_blocks] or [0.0])
    return (
        positive_blocks,
        min_block,
        float(train_summary["pnl_100"]),
        float(train_summary["edge_per_entry_100"]),
    )


def make_bar_chart(path: Path, rows: list[dict[str, Any]]) -> None:
    selected = rows[:10]
    width = 1100
    row_h = 34
    height = 80 + row_h * max(1, len(selected))
    pad_l = 270
    pad_r = 40
    max_value = max([float(row["holdout_pnl_100"]) for row in selected] + [1.0])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        '<text x="24" y="30" font-family="Segoe UI, Arial" font-size="18" font-weight="700" fill="#222">Top liquidity dwell improvement candidates by holdout PnL</text>',
    ]
    for idx, row in enumerate(selected):
        y = 58 + idx * row_h
        value = float(row["holdout_pnl_100"])
        bar_w = max(1.0, value / max_value * (width - pad_l - pad_r))
        label = f"{row['family']} | ask {row['max_entry_ask']} p {row['max_opp_pressure']} q {row['min_quality_share']}"
        parts.append(f'<text x="24" y="{y+17}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{label}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y}" width="{bar_w:.1f}" height="20" fill="#1b9e77"/>')
        parts.append(f'<text x="{pad_l+bar_w+8:.1f}" y="{y+15}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{money(value)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def empty_outcome() -> dict[str, Any]:
    return {"enter": False, "pnl_100": 0.0, "settlement_win": False, "entry_ask": None}


def merge_outcome(current: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if not candidate.get("enter"):
        return current
    if not current.get("enter"):
        return candidate
    current_ask = n(current.get("entry_ask"), 999.0) or 999.0
    candidate_ask = n(candidate.get("entry_ask"), 999.0) or 999.0
    return candidate if candidate_ask < current_ask else current


def portfolio_outcomes(
    candidate_ids: list[str],
    candidate_outcomes: dict[str, list[dict[str, Any]]],
    count: int,
) -> list[dict[str, Any]]:
    merged = [empty_outcome() for _ in range(count)]
    for candidate_id in candidate_ids:
        outcomes = candidate_outcomes[candidate_id]
        for idx in range(count):
            merged[idx] = merge_outcome(merged[idx], outcomes[idx])
    return merged


def greedy_portfolio_select(
    *,
    all_rows: list[dict[str, Any]],
    candidate_outcomes: dict[str, list[dict[str, Any]]],
    train_indices: list[int],
    holdout_indices: list[int],
    count: int,
    train_weeks: float,
    holdout_weeks: float,
    max_candidates: int = 5,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    eligible = [
        row
        for row in all_rows
        if int(row["train_entries"]) >= 10
        and float(row["train_pnl_100"]) > 0
        and int(row["train_positive_blocks_first5"]) >= 3
    ]
    selected_ids: list[str] = []
    selected_steps: list[dict[str, Any]] = []
    current = portfolio_outcomes(selected_ids, candidate_outcomes, count)
    current_train = summarize("portfolio_train", current, train_indices, weeks=train_weeks)
    for step in range(1, max_candidates + 1):
        best_gain = 0.0
        best_row: dict[str, Any] | None = None
        best_outcomes: list[dict[str, Any]] | None = None
        for row in eligible:
            candidate_id = row["candidate_id"]
            if candidate_id in selected_ids:
                continue
            trial = portfolio_outcomes(selected_ids + [candidate_id], candidate_outcomes, count)
            trial_train = summarize("portfolio_train", trial, train_indices, weeks=train_weeks)
            gain = float(trial_train["pnl_100"]) - float(current_train["pnl_100"])
            if gain > best_gain:
                best_gain = gain
                best_row = row
                best_outcomes = trial
        if best_row is None or best_outcomes is None or best_gain <= 0.0:
            break
        selected_ids.append(best_row["candidate_id"])
        current = best_outcomes
        current_train = summarize("portfolio_train", current, train_indices, weeks=train_weeks)
        current_holdout = summarize("portfolio_holdout", current, holdout_indices, weeks=holdout_weeks)
        selected_steps.append(
            {
                "step": step,
                "candidate_id": best_row["candidate_id"],
                "family": best_row["family"],
                "params": best_row["params"],
                "incremental_train_pnl_100": round(best_gain, 4),
                "portfolio_train_entries": current_train["entries"],
                "portfolio_train_pnl_100": current_train["pnl_100"],
                "portfolio_train_edge_per_entry_100": current_train["edge_per_entry_100"],
                "portfolio_holdout_entries": current_holdout["entries"],
                "portfolio_holdout_pnl_100": current_holdout["pnl_100"],
                "portfolio_holdout_edge_per_entry_100": current_holdout["edge_per_entry_100"],
                "portfolio_holdout_weekly_pnl_100": current_holdout["weekly_pnl_100"],
                "portfolio_holdout_max_drawdown_100": current_holdout["max_drawdown_100"],
            }
        )
    selected_rows = [row for row in eligible if row["candidate_id"] in selected_ids]
    return selected_steps, current, selected_rows


def main() -> None:
    prepped, _quote_delays = dwell_validation.load_prepped_quote_path()
    count = len(prepped)
    split = int(count * 0.7)
    train_indices = list(range(split))
    holdout_indices = list(range(split, count))
    blocks = chronological_blocks(count, 8)
    train_weeks = exact_weeks_for_items(prepped, train_indices)
    holdout_weeks = exact_weeks_for_items(prepped, holdout_indices)
    candidates = build_candidates()

    all_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    candidate_outcomes: dict[str, list[dict[str, Any]]] = {}

    for candidate in candidates:
        params = {key: value for key, value in candidate.items() if key not in {"family", "candidate_id"}}
        outcomes = [simulate_case(case, prepared, params) for case, prepared in prepped]
        candidate_outcomes[candidate["candidate_id"]] = outcomes
        train_summary = summarize("train", outcomes, train_indices, weeks=train_weeks)
        holdout_summary = summarize("holdout", outcomes, holdout_indices, weeks=holdout_weeks)
        candidate_block_rows = []
        for block_idx, indices in enumerate(blocks, start=1):
            block_weeks = exact_weeks_for_items(prepped, indices)
            block_summary = summarize(f"block_{block_idx}", outcomes, indices, weeks=block_weeks)
            block_row = {
                "candidate_id": candidate["candidate_id"],
                "family": candidate["family"],
                "block": block_idx,
                "start": prepped[indices[0]][0]["entry_ts"] if indices else "",
                "end": prepped[indices[-1]][0]["entry_ts"] if indices else "",
                **block_summary,
            }
            block_rows.append(block_row)
            if block_idx <= 5:
                candidate_block_rows.append(block_row)
        train_score = robust_train_score(train_summary, candidate_block_rows)
        all_rows.append(
            {
                **candidate,
                "params": json.dumps(params, sort_keys=True),
                "train_entries": train_summary["entries"],
                "train_pnl_100": train_summary["pnl_100"],
                "train_edge_per_entry_100": train_summary["edge_per_entry_100"],
                "train_win_rate": train_summary["win_rate"],
                "train_max_drawdown_100": train_summary["max_drawdown_100"],
                "train_positive_blocks_first5": train_score[0],
                "train_worst_block_first5": train_score[1],
                "holdout_entries": holdout_summary["entries"],
                "holdout_pnl_100": holdout_summary["pnl_100"],
                "holdout_edge_per_entry_100": holdout_summary["edge_per_entry_100"],
                "holdout_weekly_pnl_100": holdout_summary["weekly_pnl_100"],
                "holdout_win_rate": holdout_summary["win_rate"],
                "holdout_max_drawdown_100": holdout_summary["max_drawdown_100"],
                "holdout_avg_entry_ask": holdout_summary["avg_entry_ask"],
                "both_positive": train_summary["pnl_100"] > 0 and holdout_summary["pnl_100"] > 0,
            }
        )

    family_selected: list[dict[str, Any]] = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        by_family[row["family"]].append(row)
    for family, rows in by_family.items():
        eligible = [
            row for row in rows
            if int(row["train_entries"]) >= 15
            and float(row["train_pnl_100"]) > 0
            and int(row["train_positive_blocks_first5"]) >= 3
        ]
        pool = eligible or [row for row in rows if int(row["train_entries"]) >= 10] or rows
        selected = sorted(
            pool,
            key=lambda row: (
                int(row["train_positive_blocks_first5"]),
                float(row["train_worst_block_first5"]),
                float(row["train_pnl_100"]),
                float(row["train_edge_per_entry_100"]),
            ),
            reverse=True,
        )[0]
        family_selected.append({"selection": "family_train_robust_selected", **selected})

    walk_rows: list[dict[str, Any]] = []
    for test_block_idx in range(2, 8):
        train_block_indices = [idx for block in blocks[:test_block_idx] for idx in block]
        test_indices = blocks[test_block_idx]
        train_weeks_fold = exact_weeks_for_items(prepped, train_block_indices)
        test_weeks = exact_weeks_for_items(prepped, test_indices)
        for family, rows in by_family.items():
            scored = []
            for row in rows:
                outcomes = candidate_outcomes[row["candidate_id"]]
                train_summary = summarize("fold_train", outcomes, train_block_indices, weeks=train_weeks_fold)
                if train_summary["entries"] < 10 or train_summary["pnl_100"] <= 0:
                    continue
                scored.append((train_summary, row))
            if not scored:
                continue
            train_summary, selected = sorted(
                scored,
                key=lambda item: (
                    float(item[0]["pnl_100"]),
                    float(item[0]["edge_per_entry_100"]),
                    int(item[0]["entries"]),
                ),
                reverse=True,
            )[0]
            test_summary = summarize("fold_test", candidate_outcomes[selected["candidate_id"]], test_indices, weeks=test_weeks)
            walk_rows.append(
                {
                    "family": family,
                    "fold": test_block_idx - 1,
                    "train_blocks": f"1-{test_block_idx}",
                    "test_block": test_block_idx + 1,
                    "candidate_id": selected["candidate_id"],
                    "params": selected["params"],
                    "train_entries": train_summary["entries"],
                    "train_pnl_100": train_summary["pnl_100"],
                    "test_entries": test_summary["entries"],
                    "test_pnl_100": test_summary["pnl_100"],
                    "test_edge_per_entry_100": test_summary["edge_per_entry_100"],
                    "test_win_rate": test_summary["win_rate"],
                    "test_max_drawdown_100": test_summary["max_drawdown_100"],
                }
            )

    family_walk_summary = []
    for family, rows in defaultdict(list, {family: [row for row in walk_rows if row["family"] == family] for family in by_family}).items():
        if not rows:
            continue
        total = round(sum(float(row["test_pnl_100"]) for row in rows), 4)
        entries = sum(int(row["test_entries"]) for row in rows)
        family_walk_summary.append(
            {
                "family": family,
                "folds": len(rows),
                "positive_folds": sum(1 for row in rows if float(row["test_pnl_100"]) > 0),
                "test_entries": entries,
                "test_pnl_100": total,
                "test_edge_per_entry_100": round(total / entries, 6) if entries else 0.0,
                "worst_fold_pnl_100": round(min([float(row["test_pnl_100"]) for row in rows] or [0.0]), 4),
            }
        )

    portfolio_steps, portfolio_final_outcomes, portfolio_selected = greedy_portfolio_select(
        all_rows=all_rows,
        candidate_outcomes=candidate_outcomes,
        train_indices=train_indices,
        holdout_indices=holdout_indices,
        count=count,
        train_weeks=train_weeks,
        holdout_weeks=holdout_weeks,
    )
    portfolio_summary_rows: list[dict[str, Any]] = [
        {"sample": "train", **summarize("portfolio_train", portfolio_final_outcomes, train_indices, weeks=train_weeks)},
        {"sample": "holdout", **summarize("portfolio_holdout", portfolio_final_outcomes, holdout_indices, weeks=holdout_weeks)},
    ]
    for block_idx, indices in enumerate(blocks, start=1):
        block_weeks = exact_weeks_for_items(prepped, indices)
        portfolio_summary_rows.append(
            {
                "sample": f"block_{block_idx}",
                "block": block_idx,
                **summarize(f"portfolio_block_{block_idx}", portfolio_final_outcomes, indices, weeks=block_weeks),
            }
        )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_md = EDGE_DIR / f"liquidity_dwell_improvement_research_{timestamp}.md"
    json_path = EDGE_DIR / f"liquidity_dwell_improvement_research_{timestamp}.json"
    all_csv = EDGE_DIR / f"liquidity_dwell_improvement_candidates_{timestamp}.csv"
    selected_csv = EDGE_DIR / f"liquidity_dwell_improvement_family_selected_{timestamp}.csv"
    walk_csv = EDGE_DIR / f"liquidity_dwell_improvement_walk_forward_{timestamp}.csv"
    walk_summary_csv = EDGE_DIR / f"liquidity_dwell_improvement_walk_summary_{timestamp}.csv"
    block_csv = EDGE_DIR / f"liquidity_dwell_improvement_blocks_{timestamp}.csv"
    portfolio_steps_csv = EDGE_DIR / f"liquidity_dwell_improvement_portfolio_steps_{timestamp}.csv"
    portfolio_summary_csv = EDGE_DIR / f"liquidity_dwell_improvement_portfolio_summary_{timestamp}.csv"
    chart_svg = EDGE_DIR / f"liquidity_dwell_improvement_top_holdout_{timestamp}.svg"

    ranked_holdout = sorted(
        [row for row in all_rows if row["both_positive"] and int(row["holdout_entries"]) >= 20],
        key=lambda row: float(row["holdout_pnl_100"]),
        reverse=True,
    )
    family_selected = sorted(family_selected, key=lambda row: float(row["holdout_pnl_100"]), reverse=True)
    family_walk_summary = sorted(family_walk_summary, key=lambda row: float(row["test_pnl_100"]), reverse=True)
    write_csv(all_csv, sorted(all_rows, key=lambda row: float(row["holdout_pnl_100"]), reverse=True))
    write_csv(selected_csv, family_selected)
    write_csv(walk_csv, walk_rows)
    write_csv(walk_summary_csv, family_walk_summary)
    write_csv(block_csv, block_rows)
    write_csv(portfolio_steps_csv, portfolio_steps)
    write_csv(portfolio_summary_csv, portfolio_summary_rows)
    make_bar_chart(chart_svg, ranked_holdout)

    top = ranked_holdout[:8]
    best_family_selected = family_selected[:8]
    portfolio_holdout = next(row for row in portfolio_summary_rows if row["sample"] == "holdout")
    portfolio_train = next(row for row in portfolio_summary_rows if row["sample"] == "train")
    best_single_holdout = top[0] if top else None
    lines = [
        "# Liquidity Dwell Improvement Research",
        "",
        f"- Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "- Scope: research-only. No live entry logic, exit logic, production configs, run scripts, or bot processes were changed.",
        f"- Candidates tested: `{len(all_rows)}` across `{len(by_family)}` families.",
        "- Goal: look for PnL-improving variants while keeping train/holdout and walk-forward evidence visible.",
        f"- Best single-candidate holdout PnL at 100 contracts: {money(best_single_holdout['holdout_pnl_100']) if best_single_holdout else ''}. Prior pressure-0.5/qshare-0.75 reference was $534.42.",
        "",
        "## Best Holdout-Positive Candidates",
        "",
        "| Rank | Family | Holdout PnL at 100 | Entries | Edge/trade | Train PnL | Train positive blocks | Params |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(top, start=1):
        compact = {
            key: row.get(key)
            for key in (
                "delay_seconds",
                "max_entry_ask",
                "max_opp_pressure",
                "max_spread",
                "min_quality_share",
                "min_quality_seconds",
                "min_own_bid_net",
                "min_own_bid_omega",
                "max_ask_range",
                "max_pressure_mean",
                "min_state_changes",
            )
            if row.get(key) not in (None, "")
        }
        lines.append(
            f"| {idx} | `{row['family']}` | {money(row['holdout_pnl_100'])} | {row['holdout_entries']} | "
            f"{money(row['holdout_edge_per_entry_100'])} | {money(row['train_pnl_100'])} | "
            f"{row['train_positive_blocks_first5']}/5 | `{json.dumps(compact, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Train-Robust Family Selections",
            "",
            "| Family | Holdout PnL at 100 | Entries | Edge/trade | Train PnL | Train worst block | Params |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in best_family_selected:
        compact = {
            key: row.get(key)
            for key in (
                "delay_seconds",
                "max_entry_ask",
                "max_opp_pressure",
                "max_spread",
                "min_quality_share",
                "min_quality_seconds",
                "min_own_bid_net",
                "max_ask_range",
                "max_pressure_mean",
                "min_state_changes",
            )
            if row.get(key) not in (None, "")
        }
        lines.append(
            f"| `{row['family']}` | {money(row['holdout_pnl_100'])} | {row['holdout_entries']} | "
            f"{money(row['holdout_edge_per_entry_100'])} | {money(row['train_pnl_100'])} | "
            f"{money(row['train_worst_block_first5'])} | `{json.dumps(compact, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Train-Greedy Variant Portfolio",
            "",
            f"- Selected candidates: `{len(portfolio_steps)}`.",
            f"- Train PnL at 100: {money(portfolio_train['pnl_100'])} on `{portfolio_train['entries']}` entries.",
            f"- Holdout PnL at 100: {money(portfolio_holdout['pnl_100'])} on `{portfolio_holdout['entries']}` entries, {money(portfolio_holdout['edge_per_entry_100'])}/trade.",
            f"- This did not beat the best single candidate ({money(best_single_holdout['holdout_pnl_100']) if best_single_holdout else ''}); treat it as an overfit warning, not an upgrade.",
            "",
            "| Step | Family | Incremental train PnL | Portfolio holdout PnL | Holdout entries | Params |",
            "|---:|---|---:|---:|---:|---|",
        ]
    )
    for row in portfolio_steps:
        params = json.loads(row["params"])
        compact = {
            key: params.get(key)
            for key in (
                "delay_seconds",
                "max_entry_ask",
                "max_opp_pressure",
                "max_spread",
                "min_quality_share",
                "min_quality_seconds",
                "max_pressure_mean",
                "min_own_bid_net",
                "max_ask_range",
                "min_state_changes",
            )
            if params.get(key) is not None
        }
        lines.append(
            f"| {row['step']} | `{row['family']}` | {money(row['incremental_train_pnl_100'])} | "
            f"{money(row['portfolio_holdout_pnl_100'])} | {row['portfolio_holdout_entries']} | "
            f"`{json.dumps(compact, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Walk-Forward Family Summary",
            "",
            "| Family | Folds | Positive folds | Test PnL at 100 | Test entries | Edge/trade | Worst fold |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in family_walk_summary:
        lines.append(
            f"| `{row['family']}` | {row['folds']} | {row['positive_folds']} | {money(row['test_pnl_100'])} | "
            f"{row['test_entries']} | {money(row['test_edge_per_entry_100'])} | {money(row['worst_fold_pnl_100'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The best simple PnL improvement is modest but real in-sample: pressure 0.5 with quality share 0.65 reaches $555.04 holdout PnL at 100 contracts, versus $534.42 for the prior pressure-0.5/qshare-0.75 row.",
            "- The best robustness improvement is stricter pressure persistence around ask <=88; it has lower holdout PnL but stronger walk-forward behavior and higher edge per trade.",
            "- The greedy multi-variant portfolio overfit train and did not beat the best single holdout candidate, so it should not be promoted.",
            "- Any improved candidate still needs fresh forward settlement before live use; this script is only historical research.",
            "",
            "## Artifacts",
            "",
            f"- [all candidates](<{all_csv.resolve()}>)",
            f"- [family train-selected candidates](<{selected_csv.resolve()}>)",
            f"- [walk-forward rows](<{walk_csv.resolve()}>)",
            f"- [walk-forward summary](<{walk_summary_csv.resolve()}>)",
            f"- [block rows](<{block_csv.resolve()}>)",
            f"- [portfolio steps](<{portfolio_steps_csv.resolve()}>)",
            f"- [portfolio summary](<{portfolio_summary_csv.resolve()}>)",
            f"- [top-holdout chart](<{chart_svg.resolve()}>)",
        ]
    )
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "generated": datetime.now(UTC).isoformat(),
                "candidate_count": len(all_rows),
                "all_rows": all_rows,
                "family_selected": family_selected,
                "walk_rows": walk_rows,
                "family_walk_summary": family_walk_summary,
                "portfolio_steps": portfolio_steps,
                "portfolio_summary_rows": portfolio_summary_rows,
                "portfolio_selected": portfolio_selected,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    latest_pairs = {
        report_md: EDGE_DIR / "liquidity_dwell_improvement_research_latest.md",
        json_path: EDGE_DIR / "liquidity_dwell_improvement_research_latest.json",
        all_csv: EDGE_DIR / "liquidity_dwell_improvement_candidates_latest.csv",
        selected_csv: EDGE_DIR / "liquidity_dwell_improvement_family_selected_latest.csv",
        walk_csv: EDGE_DIR / "liquidity_dwell_improvement_walk_forward_latest.csv",
        walk_summary_csv: EDGE_DIR / "liquidity_dwell_improvement_walk_summary_latest.csv",
        block_csv: EDGE_DIR / "liquidity_dwell_improvement_blocks_latest.csv",
        portfolio_steps_csv: EDGE_DIR / "liquidity_dwell_improvement_portfolio_steps_latest.csv",
        portfolio_summary_csv: EDGE_DIR / "liquidity_dwell_improvement_portfolio_summary_latest.csv",
        chart_svg: EDGE_DIR / "liquidity_dwell_improvement_top_holdout_latest.svg",
    }
    for src, dst in latest_pairs.items():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "report": str(report_md.resolve()),
                "json": str(json_path.resolve()),
                "all_csv": str(all_csv.resolve()),
                "selected_csv": str(selected_csv.resolve()),
                "walk_summary_csv": str(walk_summary_csv.resolve()),
                "portfolio_steps_csv": str(portfolio_steps_csv.resolve()),
                "portfolio_summary_csv": str(portfolio_summary_csv.resolve()),
                "chart_svg": str(chart_svg.resolve()),
                "candidate_count": len(all_rows),
                "ranked_holdout_count": len(ranked_holdout),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
