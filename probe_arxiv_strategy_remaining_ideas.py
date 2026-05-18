"""Remaining Truffle/arXiv idea probes for v28.

Research-only. This script covers the ideas that were not fully exercised by
the earlier projection, stress, walk-forward, and promotion-gate probes:

- S-CRC-style selective risk control proxies
- online model selection across fixed candidate gates
- exchangeability / WATCH-like regime reset diagnostics
- queue-reactive fillability and empirical depth-decay checks
- Brownian terminal and jump-adjusted probability sanity checks
- imprecise-probability interval scoring proxies

The tests read recorded v28 logs only. They do not place orders or edit live
bot logic.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable

import probe_arxiv_strategy_projection as projection
import probe_arxiv_strategy_promotion_gates as gates


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
BTC_1M_PARQUET = OUT_DIR / "coinbase_btc_usd_1m_cache.parquet"
OUT_JSON = OUT_DIR / "arxiv_strategy_remaining_ideas_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_remaining_ideas_latest.md"

Predicate = Callable[[dict[str, Any]], bool]


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = projection.as_float(value)
    return default if parsed is None else parsed


def maybe_float(value: Any) -> float | None:
    return projection.as_float(value)


def ge(value: Any, threshold: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and parsed >= threshold


def le(value: Any, threshold: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and parsed <= threshold


def between(value: Any, low: float, high: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and low <= parsed <= high


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return projection.trade_stats(rows, denominator)


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * q))
    return ordered[min(len(ordered) - 1, max(0, idx))]


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + j - 1) / 2.0
        for k in range(i, j):
            out[indexed[k][0]] = rank
        i = j
    return out


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    return pearson(ranks(xs), ranks(ys))


def slope_loglog(points: list[tuple[float, float]]) -> dict[str, Any]:
    usable = [(math.log(x), math.log(y)) for x, y in points if x and y and x > 0 and y > 0]
    if len(usable) < 3:
        return {"n": len(usable), "slope": None, "intercept": None, "r2": None}
    xs = [x for x, _ in usable]
    ys = [y for _, y in usable]
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    if vx <= 0:
        return {"n": len(usable), "slope": None, "intercept": None, "r2": None}
    slope = sum((x - mx) * (y - my) for x, y in usable) / vx
    intercept = my - slope * mx
    corr = pearson(xs, ys)
    return {"n": len(usable), "slope": slope, "intercept": intercept, "r2": corr * corr if corr is not None else None}


def money(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"{100.0 * parsed:.1f}%"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def load_detailed_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics = gates.load_rows()
    features = projection.load_feature_events()
    detailed = []
    feature_hits = 0
    for row in rows:
        row = dict(row)
        feature, match_seconds = projection.best_feature_match(features, row)
        if feature is not None:
            feature_hits += 1
            row["detail_match_seconds"] = match_seconds
            for target, source in {
                "btc_price": "mushroom_v28_btc_price",
                "strike": "mushroom_v28_strike",
                "sigma_t_dollars": "mushroom_v28_sigma_t_dollars",
                "d_sigma": "mushroom_v28_d_sigma",
                "fair_yes_cents": "mushroom_v28_fair_yes_cents",
                "fair_side_cents": "mushroom_v28_fair_side_cents",
                "fee_cents": "mushroom_v28_fee_cents",
                "slippage_cents": "mushroom_v28_slippage_cents",
                "market_p_yes": "mushroom_market_p_yes",
            }.items():
                parsed = maybe_float(feature.get(source))
                if parsed is not None:
                    row[target] = parsed
        detailed.append(row)
    diagnostics["detailed_feature_matches"] = feature_hits
    return detailed, diagnostics


def candidate_predicates() -> dict[str, Predicate]:
    candidates = {candidate.name: candidate.predicate for candidate in gates.build_candidates()}
    candidates["hybrid_fpt_depth_robust_rank1"] = lambda row: (
        ge(row.get("edge28_cents"), 3.0)
        and ge(row.get("depth_ratio"), 8.0)
        and le(row.get("book_age_ms"), 750.0)
        and le(row.get("ask_cents"), 85.0)
        and ge(row.get("seconds_to_close"), 120.0)
        and between(row.get("abs_d_sigma"), 0.80, 1.10)
    )
    return candidates


def scrc_variant(
    rows: list[dict[str, Any]],
    base_predicate: Predicate,
    *,
    name: str,
    min_lower_edge_cents: float,
    max_recent_loss_rate: float | None,
    warmup: int = 80,
    recent_window: int = 80,
) -> dict[str, Any]:
    aci_by_idx = {item["idx"]: item for item in gates.aci_sequence(rows)}
    accepted: list[dict[str, Any]] = []
    rejected_base: list[dict[str, Any]] = []
    recent_results: deque[int] = deque(maxlen=recent_window)
    accepted_indices = []
    singleton_count = 0
    risk_block_count = 0
    lower_edge_block_count = 0
    for idx, row in enumerate(rows, start=1):
        if not base_predicate(row):
            continue
        p = maybe_float(row.get("p28"))
        edge = maybe_float(row.get("edge28_cents"))
        q = maybe_float((aci_by_idx.get(idx) or {}).get("q_pre"))
        gap = maybe_float(row.get("probability_gap")) or 0.0
        if p is None or edge is None or q is None:
            rejected_base.append(row)
            continue
        singleton = (1.0 - p) <= q < p
        lower_edge = edge - 100.0 * gap
        recent_loss_rate = sum(recent_results) / len(recent_results) if recent_results else None
        risk_ok = (
            max_recent_loss_rate is None
            or len(recent_results) < 20
            or (recent_loss_rate is not None and recent_loss_rate <= max_recent_loss_rate)
        )
        if not singleton:
            rejected_base.append(row)
            continue
        singleton_count += 1
        if lower_edge < min_lower_edge_cents:
            lower_edge_block_count += 1
            rejected_base.append(row)
            continue
        if not risk_ok:
            risk_block_count += 1
            rejected_base.append(row)
            continue
        if idx <= warmup:
            rejected_base.append(row)
            recent_results.append(1 if fnum(row.get("pnl_cents")) < 0 else 0)
            continue
        accepted.append(row)
        accepted_indices.append(idx)
        recent_results.append(1 if fnum(row.get("pnl_cents")) < 0 else 0)
    base_rows = selected(rows, base_predicate)
    return {
        "name": name,
        "config": {
            "warmup": warmup,
            "recent_window": recent_window,
            "min_lower_edge_cents": min_lower_edge_cents,
            "max_recent_loss_rate": max_recent_loss_rate,
        },
        "base": stats(base_rows, len(rows)),
        "accepted": stats(accepted, len(rows)),
        "accepted_share_of_base": len(accepted) / len(base_rows) if base_rows else None,
        "rejected_base": stats(rejected_base, len(rows)),
        "accepted_indices": accepted_indices[:20],
        "singleton_base_rows": singleton_count,
        "lower_edge_block_count": lower_edge_block_count,
        "risk_block_count": risk_block_count,
        "delta_vs_base_cents": net_cents(accepted) - net_cents(base_rows),
    }


def scrc_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = candidate_predicates()["hybrid_fpt_depth_robust_rank1"]
    variants = [
        scrc_variant(
            rows,
            base,
            name="singleton_only_no_lower_edge",
            min_lower_edge_cents=-100.0,
            max_recent_loss_rate=None,
        ),
        scrc_variant(
            rows,
            base,
            name="singleton_gap_lower_edge_ge_0",
            min_lower_edge_cents=0.0,
            max_recent_loss_rate=None,
        ),
        scrc_variant(
            rows,
            base,
            name="singleton_gap_lower_edge_ge_0_lossrate_le_52pct",
            min_lower_edge_cents=0.0,
            max_recent_loss_rate=0.52,
        ),
        scrc_variant(
            rows,
            base,
            name="singleton_gap_lower_edge_ge_2_lossrate_le_52pct",
            min_lower_edge_cents=2.0,
            max_recent_loss_rate=0.52,
        ),
    ]
    variants.sort(key=lambda row: (fnum((row.get("accepted") or {}).get("net_cents")), (row.get("accepted") or {}).get("entries") or 0), reverse=True)
    return {
        "idea": "Selective conformal risk-control proxy over the robust hybrid candidate.",
        "caveat": "This is a prequential proxy, not a theorem-valid S-CRC implementation.",
        "variants": variants,
    }


def online_model_selection(
    rows: list[dict[str, Any]],
    *,
    name: str,
    warmup: int,
    window: int,
    min_history: int,
    min_mean_cents: float,
) -> dict[str, Any]:
    predicates = candidate_predicates()
    candidate_names = [
        "brownian_fpt_current",
        "depth_decay_current",
        "hybrid_fpt_depth_robust_rank1",
        "consensus_gap_robust_rank1",
    ]
    histories: dict[str, deque[float]] = {candidate: deque(maxlen=window) for candidate in candidate_names}
    selected_rows: list[dict[str, Any]] = []
    choice_counts: Counter[str] = Counter()
    switches = 0
    last_choice: str | None = None
    no_history_blocks = 0
    negative_score_blocks = 0
    for idx, row in enumerate(rows, start=1):
        eligible = [candidate for candidate in candidate_names if predicates[candidate](row)]
        choice = None
        if idx > warmup and eligible:
            scored = []
            for candidate in eligible:
                hist = histories[candidate]
                if len(hist) < min_history:
                    continue
                avg = mean(hist)
                hit = sum(1 for value in hist if value > 0) / len(hist)
                score = avg + 2.0 * (hit - 0.5)
                scored.append((score, avg, hit, candidate))
            if not scored:
                no_history_blocks += 1
            else:
                scored.sort(reverse=True)
                score, avg, _, candidate = scored[0]
                if avg >= min_mean_cents:
                    choice = candidate
                else:
                    negative_score_blocks += 1
        if choice is not None:
            selected_rows.append(row)
            choice_counts[choice] += 1
            if last_choice is not None and choice != last_choice:
                switches += 1
            last_choice = choice
        for candidate in eligible:
            histories[candidate].append(fnum(row.get("pnl_cents")))
    return {
        "name": name,
        "config": {
            "warmup": warmup,
            "window": window,
            "min_history": min_history,
            "min_mean_cents": min_mean_cents,
        },
        "selected": stats(selected_rows, len(rows)),
        "choice_counts": dict(choice_counts),
        "switches": switches,
        "no_history_blocks": no_history_blocks,
        "negative_score_blocks": negative_score_blocks,
    }


def online_model_selection_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    variants = [
        online_model_selection(rows, name="oms_warm80_win60_hist15_mean_gt_0", warmup=80, window=60, min_history=15, min_mean_cents=0.0),
        online_model_selection(rows, name="oms_warm100_win90_hist20_mean_gt_0", warmup=100, window=90, min_history=20, min_mean_cents=0.0),
        online_model_selection(rows, name="oms_warm120_win120_hist25_mean_gt_1", warmup=120, window=120, min_history=25, min_mean_cents=1.0),
    ]
    return {
        "idea": "Online model-selection proxy using only trailing candidate shadow outcomes before each row.",
        "caveat": "Uses retrospective full-information shadow labels; it is a design for forward shadow logging, not live proof.",
        "variants": variants,
    }


def power_martingale(
    scores: list[float],
    *,
    epsilon: float = 0.5,
    window: int = 80,
    threshold: float = 10.0,
) -> dict[str, Any]:
    hist: deque[float] = deque(maxlen=window)
    capital = 1.0
    max_capital = 1.0
    crossings = []
    trace = []
    for idx, score in enumerate(scores, start=1):
        if len(hist) >= 20:
            p_value = (1 + sum(1 for old in hist if old >= score)) / (len(hist) + 1)
            factor = epsilon * (p_value ** (epsilon - 1.0))
            capital *= factor
            max_capital = max(max_capital, capital)
            if capital >= threshold:
                crossings.append({"idx": idx, "capital": capital, "score": score, "p_value": p_value})
                capital = 1.0
        else:
            p_value = None
        trace.append({"idx": idx, "capital": capital, "score": score, "p_value": p_value})
        hist.append(score)
    return {
        "epsilon": epsilon,
        "window": window,
        "threshold": threshold,
        "max_capital": max_capital,
        "crossings": crossings,
        "crossing_count": len(crossings),
        "trace_tail": trace[-10:],
    }


def watch_miss_monitor(
    rows: list[dict[str, Any]],
    *,
    alpha: float = 0.10,
    ewma_lambda: float = 0.12,
    threshold: float = 0.24,
) -> dict[str, Any]:
    seq = gates.aci_sequence(rows)
    ewma = alpha
    triggers = []
    trace = []
    for item in seq:
        covered = item.get("covered")
        if covered is None:
            continue
        miss = 0.0 if covered else 1.0
        ewma = (1.0 - ewma_lambda) * ewma + ewma_lambda * miss
        idx = int(item["idx"])
        if ewma >= threshold:
            triggers.append({"idx": idx, "ewma_miss": ewma})
            ewma = alpha
        trace.append({"idx": idx, "ewma_miss": ewma, "miss": miss})
    return {
        "target_miss_rate": alpha,
        "ewma_lambda": ewma_lambda,
        "threshold": threshold,
        "triggers": triggers,
        "trigger_count": len(triggers),
        "trace_tail": trace[-10:],
    }


def trigger_impact(rows: list[dict[str, Any]], triggers: list[dict[str, Any]], predicate: Predicate, horizon: int = 40) -> dict[str, Any]:
    impacts = []
    for trigger in triggers:
        idx = int(trigger.get("idx") or 0)
        before = selected(rows[max(0, idx - horizon - 1) : max(0, idx - 1)], predicate)
        after = selected(rows[idx : min(len(rows), idx + horizon)], predicate)
        impacts.append(
            {
                "idx": idx,
                "before_entries": len(before),
                "before_net_cents": net_cents(before),
                "after_entries": len(after),
                "after_net_cents": net_cents(after),
            }
        )
    after_nets = [item["after_net_cents"] for item in impacts if item["after_entries"]]
    return {
        "horizon_rows": horizon,
        "triggered_windows": len(impacts),
        "median_after_net_cents": median(after_nets) if after_nets else None,
        "impacts": impacts[:20],
    }


def regime_monitor_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [fnum(row.get("conformal_score")) for row in rows if row.get("conformal_score") is not None]
    exchangeability = power_martingale(scores, epsilon=0.5, window=80, threshold=10.0)
    watch = watch_miss_monitor(rows, alpha=0.10, ewma_lambda=0.12, threshold=0.24)
    robust = candidate_predicates()["hybrid_fpt_depth_robust_rank1"]
    return {
        "idea": "Exchangeability and WATCH-like monitors over conformal errors.",
        "caveat": "These are lightweight diagnostics; reset thresholds need forward registration before use.",
        "exchangeability_power_martingale": exchangeability,
        "watch_ewma_miss_monitor": watch,
        "hybrid_trigger_impact": {
            "exchangeability": trigger_impact(rows, exchangeability["crossings"], robust),
            "watch": trigger_impact(rows, watch["triggers"], robust),
        },
    }


def parse_event_time(event: dict[str, Any]) -> datetime | None:
    return projection.parse_wall_to_local(event.get("ts_wall"))


def load_entry_submit_events() -> list[dict[str, Any]]:
    plan_by_client: dict[str, dict[str, Any]] = {}
    plan_by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    submit_events: list[dict[str, Any]] = []
    if not EXECUTION_EVENTS.exists():
        return submit_events
    with EXECUTION_EVENTS.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            client_id = str(event.get("client_order_id") or "")
            event_type = event.get("event_type")
            if event_type == "plan_built":
                # plan_built events often have no client id yet, so they must be
                # indexed by market/side/price/time for later submit matching.
                plan_by_client[client_id] = event
                local_dt = parse_event_time(event)
                trigger = event.get("trigger_price_cents") or event.get("mushroom_v28_ask_cents") or event.get("cap_price_cents")
                key = (str(event.get("market") or ""), str(event.get("side") or ""), projection.as_int_price(trigger))
                if local_dt is not None and key[0] and key[1] and key[2]:
                    event = dict(event)
                    event["_local_dt"] = local_dt
                    plan_by_key[key].append(event)
            elif client_id.startswith("btc15m-entry") and event_type in {"order_submit_success", "order_submit_reject"}:
                submit_events.append(event)
    for plans in plan_by_key.values():
        plans.sort(key=lambda item: item["_local_dt"])
    rows = []
    for event in submit_events:
        client_id = str(event.get("client_order_id") or "")
        plan = plan_by_client.get(client_id) or {}
        local_dt = parse_event_time(event)
        if not plan and local_dt is not None:
            trigger = event.get("trigger_price_cents") or event.get("mushroom_v28_ask_cents") or event.get("cap_price_cents")
            key = (str(event.get("market") or ""), str(event.get("side") or ""), projection.as_int_price(trigger))
            nearby = []
            for candidate in plan_by_key.get(key, []):
                delta = abs((candidate["_local_dt"] - local_dt).total_seconds())
                if delta <= 5.0:
                    nearby.append((delta, candidate))
            if nearby:
                nearby.sort(key=lambda item: item[0])
                plan = nearby[0][1]
        merged = dict(plan)
        merged.update({key: value for key, value in event.items() if value not in (None, "")})
        if local_dt is not None:
            merged["_local_dt"] = local_dt
        depth = maybe_float(merged.get("eligible_depth") or merged.get("mushroom_v28_eligible_depth"))
        required = maybe_float(merged.get("depth_required"))
        fill_count = maybe_float(merged.get("fill_count")) or 0.0
        target = maybe_float(merged.get("position_size") or merged.get("slice_target_size")) or 0.0
        merged["eligible_depth_num"] = depth
        merged["depth_required_num"] = required
        merged["depth_ratio"] = depth / required if depth is not None and required and required > 0 else None
        merged["book_age_ms_num"] = maybe_float(merged.get("book_age_ms") or merged.get("mushroom_v28_book_age_ms"))
        merged["seconds_to_close_num"] = maybe_float(merged.get("seconds_to_close") or merged.get("mushroom_v28_seconds_to_close"))
        merged["ask_cents_num"] = maybe_float(merged.get("trigger_price_cents") or merged.get("mushroom_v28_ask_cents"))
        merged["fill_count_num"] = fill_count
        merged["target_count_num"] = target
        merged["filled_any"] = 1.0 if fill_count > 0 else 0.0
        merged["fill_fraction"] = fill_count / target if target > 0 else None
        rows.append(merged)
    rows.sort(key=lambda item: item.get("_local_dt") or datetime.min)
    return rows


def binned_fill_rates(rows: list[dict[str, Any]], key: str, bins: list[tuple[str, float, float]]) -> list[dict[str, Any]]:
    out = []
    for label, low, high in bins:
        bucket = [row for row in rows if (maybe_float(row.get(key)) is not None and low <= fnum(row.get(key)) < high)]
        out.append(
            {
                "bin": label,
                "entries": len(bucket),
                "fill_any_rate": sum(row["filled_any"] for row in bucket) / len(bucket) if bucket else None,
                "avg_fill_fraction": mean([fnum(row.get("fill_fraction")) for row in bucket]) if bucket else None,
            }
        )
    return out


def fillability_and_depth_report() -> dict[str, Any]:
    rows = load_entry_submit_events()
    qr_rows = [
        row
        for row in rows
        if row.get("depth_ratio") is not None
        and row.get("book_age_ms_num") is not None
        and row.get("seconds_to_close_num") is not None
        and row.get("ask_cents_num") is not None
    ]
    xs = []
    ys = []
    proxy_values = []
    for row in qr_rows:
        depth_ratio = fnum(row.get("depth_ratio"))
        book_age = fnum(row.get("book_age_ms_num"))
        seconds = max(1.0, fnum(row.get("seconds_to_close_num")))
        ask = fnum(row.get("ask_cents_num"))
        qr_proxy = math.log1p(depth_ratio) * math.exp(-book_age / 1000.0) * (1.0 - ask / 105.0) * math.sqrt(seconds / 900.0)
        proxy_values.append(qr_proxy)
        xs.append(qr_proxy)
        ys.append(fnum(row.get("filled_any")))
    depth_points = [
        (fnum(row.get("seconds_to_close_num")), fnum(row.get("eligible_depth_num")))
        for row in rows
        if maybe_float(row.get("seconds_to_close_num")) is not None and maybe_float(row.get("eligible_depth_num")) is not None
    ]
    by_market: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        market = str(row.get("market") or "")
        seconds = maybe_float(row.get("seconds_to_close_num"))
        depth = maybe_float(row.get("eligible_depth_num"))
        if market and seconds is not None and depth is not None:
            by_market[market].append((seconds, depth))
    market_slopes = []
    for market, points in by_market.items():
        fit = slope_loglog(points)
        if fit.get("slope") is not None:
            market_slopes.append({"market": market, **fit})
    slopes = [fnum(item.get("slope")) for item in market_slopes if item.get("slope") is not None]
    return {
        "idea": "Queue-reactive fillability proxy plus empirical depth-decay slope.",
        "entry_submit_rows": len(rows),
        "filled_any_rows": int(sum(row["filled_any"] for row in rows)),
        "zero_fill_rows": int(sum(1 for row in rows if row["filled_any"] <= 0)),
        "qr_proxy_rows": len(qr_rows),
        "qr_proxy_spearman_vs_fill_any": spearman(xs, ys),
        "qr_proxy_mean_filled": mean([x for x, y in zip(proxy_values, ys) if y > 0]) if any(y > 0 for y in ys) else None,
        "qr_proxy_mean_zero_fill": mean([x for x, y in zip(proxy_values, ys) if y <= 0]) if any(y <= 0 for y in ys) else None,
        "depth_ratio_bins": binned_fill_rates(
            rows,
            "depth_ratio",
            [
                ("<1", 0.0, 1.0),
                ("1-3", 1.0, 3.0),
                ("3-8", 3.0, 8.0),
                ("8-20", 8.0, 20.0),
                (">=20", 20.0, float("inf")),
            ],
        ),
        "book_age_bins": binned_fill_rates(
            rows,
            "book_age_ms_num",
            [
                ("<100ms", 0.0, 100.0),
                ("100-250ms", 100.0, 250.0),
                ("250-500ms", 250.0, 500.0),
                ("500-750ms", 500.0, 750.0),
                (">=750ms", 750.0, float("inf")),
            ],
        ),
        "depth_decay_cross_section": slope_loglog(depth_points),
        "depth_decay_market_slope_count": len(slopes),
        "depth_decay_market_median_slope": median(slopes) if slopes else None,
        "depth_decay_market_p25_slope": quantile(slopes, 0.25),
        "depth_decay_market_p75_slope": quantile(slopes, 0.75),
        "depth_decay_share_within_dubach_0p55_pm0p20": sum(1 for slope in slopes if 0.35 <= slope <= 0.75) / len(slopes) if slopes else None,
    }


def load_btc_bars() -> Any:
    if not BTC_1M_PARQUET.exists():
        return None
    try:
        import pandas as pd  # type: ignore

        df = pd.read_parquet(BTC_1M_PARQUET)
        if "open_dt" not in df or "dollar_ret" not in df:
            return None
        df = df.dropna(subset=["open_dt", "close", "dollar_ret"]).sort_values("open_dt")
        return df
    except Exception:
        return None


def row_entry_utc(row: dict[str, Any]) -> datetime | None:
    dt = row.get("_entry_dt")
    if not isinstance(dt, datetime):
        return None
    return dt.replace(tzinfo=projection.NY_TZ).astimezone(timezone.utc)


def estimate_jump_adjustment(df: Any, entry_utc: datetime, horizon_minutes: float) -> dict[str, float] | None:
    try:
        import pandas as pd  # type: ignore
    except Exception:
        return None
    start = pd.Timestamp(entry_utc) - pd.Timedelta(hours=24)
    end = pd.Timestamp(entry_utc)
    window = df[(df["open_dt"] >= start) & (df["open_dt"] < end)]
    if len(window) < 120:
        return None
    dollar_ret = window["dollar_ret"].astype(float)
    sigma_1m = float(dollar_ret.std())
    if not math.isfinite(sigma_1m) or sigma_1m <= 0:
        return None
    jump_mask = dollar_ret.abs() > 3.0 * sigma_1m
    jumps = dollar_ret[jump_mask]
    lam_per_min = float(len(jumps) / len(window))
    if len(jumps) >= 2:
        jump_mean = float(jumps.mean())
        jump_var = float(jumps.var())
    elif len(jumps) == 1:
        jump_mean = float(jumps.iloc[0])
        jump_var = float(jumps.iloc[0] ** 2)
    else:
        jump_mean = 0.0
        jump_var = 0.0
    expected_jumps = lam_per_min * max(0.0, horizon_minutes)
    return {
        "sigma_1m": sigma_1m,
        "jump_count": float(len(jumps)),
        "lambda_per_min": lam_per_min,
        "jump_mean_dollars": jump_mean,
        "jump_var_dollars2": jump_var,
        "expected_jumps": expected_jumps,
    }


def probability_scores(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    usable = []
    for row in rows:
        p = maybe_float(row.get(key))
        y = maybe_float(row.get("side_correct"))
        if p is not None and y is not None:
            p = clamp(p, 1e-6, 1.0 - 1e-6)
            usable.append((p, y))
    if not usable:
        return {"rows": 0}
    brier = mean([(p - y) ** 2 for p, y in usable])
    log_loss = mean([-(y * math.log(p) + (1.0 - y) * math.log(1.0 - p)) for p, y in usable])
    ordered = sorted(usable, key=lambda item: item[0])
    buckets = []
    for idx in range(5):
        part = ordered[int(idx * len(ordered) / 5) : int((idx + 1) * len(ordered) / 5)]
        if not part:
            continue
        buckets.append({"bucket": idx + 1, "rows": len(part), "avg_p": mean([p for p, _ in part]), "hit_rate": mean([y for _, y in part])})
    return {"rows": len(usable), "brier": brier, "log_loss": log_loss, "calibration_buckets": buckets}


def fpt_jump_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    df = load_btc_bars()
    enriched = []
    jump_coverage = 0
    for row in rows:
        row = dict(row)
        btc = maybe_float(row.get("btc_price"))
        strike = maybe_float(row.get("strike"))
        sigma = maybe_float(row.get("sigma_t_dollars"))
        side = str(row.get("side") or "").lower()
        if btc is not None and strike is not None and sigma is not None and sigma > 0:
            p_yes = normal_cdf((btc - strike) / sigma)
            row["brownian_terminal_p_yes"] = p_yes
            row["brownian_terminal_p_side"] = p_yes if side == "yes" else 1.0 - p_yes
            if df is not None:
                entry_utc = row_entry_utc(row)
                horizon = max(1.0, fnum(row.get("seconds_to_close")) / 60.0)
                if entry_utc is not None:
                    jump = estimate_jump_adjustment(df, entry_utc, horizon)
                    if jump is not None:
                        jump_coverage += 1
                        expected_jumps = jump["expected_jumps"]
                        jump_var_total = expected_jumps * (jump["jump_var_dollars2"] + jump["jump_mean_dollars"] ** 2)
                        jump_mean_total = expected_jumps * jump["jump_mean_dollars"]
                        sigma_jump = math.sqrt(max(1e-9, sigma * sigma + jump_var_total))
                        p_jump_yes = normal_cdf((btc + jump_mean_total - strike) / sigma_jump)
                        row["jump_terminal_p_yes"] = p_jump_yes
                        row["jump_terminal_p_side"] = p_jump_yes if side == "yes" else 1.0 - p_jump_yes
                        row["jump_expected_jumps"] = expected_jumps
                        row["jump_lambda_per_min"] = jump["lambda_per_min"]
        enriched.append(row)
    return {
        "idea": "Brownian terminal and jump-inflated terminal sanity checks.",
        "caveat": "Kalshi settles terminal price, so this uses terminal Gaussian probabilities rather than literal barrier hit probability.",
        "btc_cache_available": df is not None,
        "rows_with_brownian_terminal": sum(1 for row in enriched if row.get("brownian_terminal_p_side") is not None),
        "rows_with_jump_terminal": jump_coverage,
        "scores": {
            "v28_side_probability": probability_scores(enriched, "p28"),
            "brownian_terminal": probability_scores(enriched, "brownian_terminal_p_side"),
            "jump_adjusted_terminal": probability_scores(enriched, "jump_terminal_p_side"),
        },
        "jump_parameter_summary": {
            "median_expected_jumps": median([fnum(row.get("jump_expected_jumps")) for row in enriched if row.get("jump_expected_jumps") is not None])
            if any(row.get("jump_expected_jumps") is not None for row in enriched)
            else None,
            "median_lambda_per_min": median([fnum(row.get("jump_lambda_per_min")) for row in enriched if row.get("jump_lambda_per_min") is not None])
            if any(row.get("jump_lambda_per_min") is not None for row in enriched)
            else None,
        },
    }


def imprecise_probability_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    robust = candidate_predicates()["hybrid_fpt_depth_robust_rank1"]
    annotated = []
    for row in rows:
        row = dict(row)
        p = maybe_float(row.get("p28"))
        y = maybe_float(row.get("side_correct"))
        gap = maybe_float(row.get("probability_gap"))
        if p is None or y is None or gap is None:
            continue
        width = clamp(gap, 0.0, 0.50)
        low = clamp(p - width, 0.0, 1.0)
        high = clamp(p + width, 0.0, 1.0)
        point_brier = (p - y) ** 2
        if low <= y <= high:
            interval_brier = 0.0
        else:
            interval_brier = min((low - y) ** 2, (high - y) ** 2)
        row["interval_width"] = high - low
        row["interval_low"] = low
        row["interval_high"] = high
        row["point_brier"] = point_brier
        row["interval_score_proxy"] = interval_brier + 0.02 * (high - low)
        row["lower_edge_cents"] = fnum(row.get("edge28_cents")) - 100.0 * width
        annotated.append(row)
    low_width_threshold = quantile([fnum(row.get("interval_width")) for row in annotated], 0.50)
    low_width_rows = [row for row in annotated if low_width_threshold is not None and fnum(row.get("interval_width")) <= low_width_threshold]
    high_width_rows = [row for row in annotated if low_width_threshold is not None and fnum(row.get("interval_width")) > low_width_threshold]
    interval_gate = [row for row in annotated if robust(row) and ge(row.get("lower_edge_cents"), 0.0)]
    robust_rows = selected(annotated, robust)
    widths = [fnum(row.get("interval_width")) for row in annotated]
    pnls = [fnum(row.get("pnl_cents")) for row in annotated]
    return {
        "idea": "Imprecise probability proxy using v22-v28 disagreement as interval width.",
        "caveat": "This is a practical interval proxy, not the full imprecise-probability scoring-rule implementation.",
        "rows": len(annotated),
        "mean_point_brier": mean([fnum(row.get("point_brier")) for row in annotated]) if annotated else None,
        "mean_interval_score_proxy": mean([fnum(row.get("interval_score_proxy")) for row in annotated]) if annotated else None,
        "width_pnl_spearman": spearman(widths, pnls),
        "low_width": stats(low_width_rows, len(rows)),
        "high_width": stats(high_width_rows, len(rows)),
        "robust_hybrid_base": stats(robust_rows, len(rows)),
        "robust_hybrid_interval_lower_edge_ge_0": stats(interval_gate, len(rows)),
        "interval_gate_delta_vs_robust_cents": net_cents(interval_gate) - net_cents(robust_rows),
    }


def build_report() -> dict[str, Any]:
    rows, diagnostics = load_detailed_rows()
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only probes for remaining Truffle/arXiv strategy ideas.",
        "diagnostics": diagnostics,
        "live_baseline": stats(rows, len(rows)),
        "scrc": scrc_report(rows),
        "online_model_selection": online_model_selection_report(rows),
        "regime_monitors": regime_monitor_report(rows),
        "fillability_and_depth_decay": fillability_and_depth_report(),
        "fpt_and_jump_sanity": fpt_jump_report(rows),
        "imprecise_probability": imprecise_probability_report(rows),
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# arXiv Remaining Ideas",
        "",
        "Research-only diagnostics for the Truffle ideas not fully covered in the earlier probes. These are candidate filters and monitors over recorded v28 data, not live-trading changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Detailed feature matches: `{report.get('diagnostics', {}).get('detailed_feature_matches')}`",
        "",
        "## S-CRC Proxies",
        "",
        "| variant | accepted | W/L | PnL | avg/entry | accepted/base | rejected-base PnL | delta vs base |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in (report.get("scrc") or {}).get("variants") or []:
        accepted = row.get("accepted") or {}
        rejected = row.get("rejected_base") or {}
        lines.append(
            f"| {row.get('name')} | {accepted.get('entries')} | {wl(accepted)} | {money(accepted.get('net_dollars'))} | "
            f"{cents(accepted.get('avg_cents_per_entry'))} | {pct(row.get('accepted_share_of_base'))} | "
            f"{money(rejected.get('net_dollars'))} | {cents(row.get('delta_vs_base_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Online Model Selection",
            "",
            "| variant | entries | W/L | PnL | avg/entry | switches | choices |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in (report.get("online_model_selection") or {}).get("variants") or []:
        selected_stats = row.get("selected") or {}
        choices = ", ".join(f"{key}:{value}" for key, value in (row.get("choice_counts") or {}).items())
        lines.append(
            f"| {row.get('name')} | {selected_stats.get('entries')} | {wl(selected_stats)} | "
            f"{money(selected_stats.get('net_dollars'))} | {cents(selected_stats.get('avg_cents_per_entry'))} | "
            f"{row.get('switches')} | {choices} |"
        )
    regime = report.get("regime_monitors") or {}
    exchange = regime.get("exchangeability_power_martingale") or {}
    watch = regime.get("watch_ewma_miss_monitor") or {}
    impact = regime.get("hybrid_trigger_impact") or {}
    lines.extend(
        [
            "",
            "## Regime Monitors",
            "",
            f"- Exchangeability power martingale crossings: `{exchange.get('crossing_count')}`, max capital `{fnum(exchange.get('max_capital')):.2f}`.",
            f"- WATCH-style EWMA miss triggers: `{watch.get('trigger_count')}`.",
            f"- Hybrid post-exchangeability-trigger median next-window PnL: `{cents((impact.get('exchangeability') or {}).get('median_after_net_cents'))}`.",
            f"- Hybrid post-WATCH-trigger median next-window PnL: `{cents((impact.get('watch') or {}).get('median_after_net_cents'))}`.",
            "",
            "## Fillability And Depth Decay",
            "",
        ]
    )
    fill = report.get("fillability_and_depth_decay") or {}
    cross = fill.get("depth_decay_cross_section") or {}
    lines.extend(
        [
            f"- Entry submit rows: `{fill.get('entry_submit_rows')}`; filled any: `{fill.get('filled_any_rows')}`; zero-fill: `{fill.get('zero_fill_rows')}`.",
            f"- Queue-reactive proxy Spearman vs fill-any: `{fnum(fill.get('qr_proxy_spearman_vs_fill_any')):.3f}`.",
            f"- Cross-sectional log(depth) vs log(seconds-to-close) slope: `{fnum(cross.get('slope')):.3f}` over `{cross.get('n')}` rows.",
            f"- Within-market median depth-decay slope: `{fnum(fill.get('depth_decay_market_median_slope')):.3f}` across `{fill.get('depth_decay_market_slope_count')}` markets.",
            f"- Share of market slopes in Dubach-like 0.55 +/- 0.20 band: `{pct(fill.get('depth_decay_share_within_dubach_0p55_pm0p20'))}`.",
            "",
            "| depth ratio bin | entries | fill-any | avg fill fraction |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in fill.get("depth_ratio_bins") or []:
        lines.append(f"| {row.get('bin')} | {row.get('entries')} | {pct(row.get('fill_any_rate'))} | {pct(row.get('avg_fill_fraction'))} |")
    lines.extend(
        [
            "",
            "## FPT And Jump Sanity",
            "",
        ]
    )
    fpt = report.get("fpt_and_jump_sanity") or {}
    scores = fpt.get("scores") or {}
    lines.extend(
        [
            f"- Rows with Brownian terminal probability: `{fpt.get('rows_with_brownian_terminal')}`.",
            f"- Rows with jump-adjusted terminal probability: `{fpt.get('rows_with_jump_terminal')}`.",
            "",
            "| model | rows | Brier | log loss |",
            "|---|---:|---:|---:|",
        ]
    )
    for name in ("v28_side_probability", "brownian_terminal", "jump_adjusted_terminal"):
        row = scores.get(name) or {}
        lines.append(f"| {name} | {row.get('rows')} | {fnum(row.get('brier')):.4f} | {fnum(row.get('log_loss')):.4f} |")
    imprecise = report.get("imprecise_probability") or {}
    robust = imprecise.get("robust_hybrid_base") or {}
    interval_gate = imprecise.get("robust_hybrid_interval_lower_edge_ge_0") or {}
    low_width = imprecise.get("low_width") or {}
    high_width = imprecise.get("high_width") or {}
    lines.extend(
        [
            "",
            "## Imprecise Probability Proxy",
            "",
            f"- Width/PnL Spearman: `{fnum(imprecise.get('width_pnl_spearman')):.3f}`.",
            f"- Low-width PnL: `{money(low_width.get('net_dollars'))}` from `{low_width.get('entries')}` rows.",
            f"- High-width PnL: `{money(high_width.get('net_dollars'))}` from `{high_width.get('entries')}` rows.",
            f"- Robust hybrid base: `{money(robust.get('net_dollars'))}` from `{robust.get('entries')}` rows.",
            f"- Robust hybrid with lower interval edge >= 0: `{money(interval_gate.get('net_dollars'))}` from `{interval_gate.get('entries')}` rows; delta `{cents(imprecise.get('interval_gate_delta_vs_robust_cents'))}`.",
            "",
            "## Read",
            "",
            "- S-CRC and imprecise-probability filters are useful only if they improve risk without deleting the sample down to a tiny retrospective island.",
            "- Online model selection is useful only if it survives frozen forward shadowing; this report uses retrospective shadow labels.",
            "- The queue/fillability section is the most directly operational because it includes zero-fill entry submits, not only filled trades.",
            "- None of these diagnostics should promote a strategy without a fresh forward shadow registry.",
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
