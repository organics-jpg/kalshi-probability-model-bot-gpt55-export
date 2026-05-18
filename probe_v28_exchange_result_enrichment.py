"""Research-only exchange-result enrichment for v28 validators.

This module reads public Kalshi market results to reduce local outcome lag in
research reports. It does not mutate live bot state or submit orders.
"""
from __future__ import annotations

import math
from typing import Any


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def fetch_exchange_results(markets: set[str]) -> dict[str, str]:
    unresolved = sorted(market for market in markets if market)
    if not unresolved:
        return {}
    try:
        from kalshi_btc15m_bot_ws import KalshiClient, load_config

        client = KalshiClient(load_config())
        out: dict[str, str] = {}
        for market in unresolved:
            payload = client.get_market(market)
            result = str((payload or {}).get("result") or "").strip().lower()
            if result in {"yes", "no"}:
                out[market] = result
        return out
    except Exception:
        return {}


def impute_net_cents(row: dict[str, Any], won: bool) -> float | None:
    ask = as_float(row.get("ask_cents"))
    if ask is None:
        ask_prob = as_float(row.get("ask_prob"))
        if ask_prob is not None:
            ask = 100.0 * ask_prob if ask_prob <= 1.0 else ask_prob
    if ask is None:
        return None
    return (100.0 - ask) if won else -ask


def attach_exchange_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pending_markets = {
        str(row.get("market") or "")
        for row in rows
        if row.get("side_won") is None and row.get("market")
    }
    exchange_results = fetch_exchange_results(pending_markets)
    if not exchange_results:
        return rows
    enriched = []
    for row in rows:
        market = str(row.get("market") or "")
        result = exchange_results.get(market)
        if not result or row.get("side_won") is not None:
            enriched.append(row)
            continue
        updated = dict(row)
        side = str(updated.get("side") or updated.get("mushroom_v28_side") or "").strip().lower()
        won = side == result
        updated["side_won"] = won
        updated["exchange_result"] = result
        if updated.get("net_gross_cents_after_entry_fee") is None:
            net = impute_net_cents(updated, won)
            if net is not None:
                updated["net_gross_cents_after_entry_fee"] = net
                updated["net_imputed_from_exchange_result"] = True
        enriched.append(updated)
    return enriched
