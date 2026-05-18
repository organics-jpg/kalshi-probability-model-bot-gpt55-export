from __future__ import annotations

import json
import time
from pathlib import Path

from truffle_regime_lease import (
    issue_truffle_http_lease,
    load_prompt_text,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
)

SAMPLE_PAYLOAD = {
    "schema_version": "lease_input_v1",
    "strategy_family": "btc15m_supervisor",
    "candidate_profile_if_allowed": "90_78",
    "configured_profile": "90_78",
    "lease_scope": "next_market_only",
    "next_market_ticker": "KXBTC15M-PROBE",
    "next_market_session": "afternoon",
    "deterministic_precheck": "PASS",
    "generated_at": "2026-04-20T16:05:00+00:00",
    "recent_4_markets": {
        "count": 4,
        "trade_count": 3,
        "win_count": 2,
        "loss_count": 1,
        "skip_count": 1,
        "net_pnl_dollars": 12.0,
        "avg_pnl_dollars": 4.0,
        "win_rate": 0.6667,
        "avg_entry_fill_cents": 90.0,
        "avg_exit_fill_cents": 72.0,
        "avg_submit_latency_ms": 210.0,
        "p95_submit_latency_ms": 330.0,
        "stale_book_deferral_count": 0,
        "dead_market_deferral_count": 0,
        "ioc_zero_fill_count": 0,
    },
    "recent_8_markets": {
        "count": 8,
        "trade_count": 6,
        "win_count": 4,
        "loss_count": 2,
        "skip_count": 2,
        "net_pnl_dollars": 20.0,
        "avg_pnl_dollars": 3.3333,
        "win_rate": 0.6667,
        "avg_entry_fill_cents": 89.7,
        "avg_exit_fill_cents": 74.5,
        "avg_submit_latency_ms": 240.0,
        "p95_submit_latency_ms": 380.0,
        "stale_book_deferral_count": 1,
        "dead_market_deferral_count": 0,
        "ioc_zero_fill_count": 1,
    },
    "last_4_market_sequence": [
        {"market": "m1", "outcome_type": "win", "pnl_dollars": 10.0, "signal_count": 1, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
        {"market": "m2", "outcome_type": "loss", "pnl_dollars": -6.0, "signal_count": 1, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
        {"market": "m3", "outcome_type": "win", "pnl_dollars": 8.0, "signal_count": 1, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
        {"market": "m4", "outcome_type": "skipped", "pnl_dollars": 0.0, "signal_count": 0, "stale_book_deferral_count": 0, "ioc_zero_fill_count": 0},
    ],
}


def main() -> None:
    endpoint = resolve_truffle_chat_completion_endpoint("")
    model = resolve_truffle_model_id("", endpoint=endpoint, timeout_ms=8000)
    prompt = load_prompt_text(Path("truffle_regime_lease_prompt.txt"))

    started = time.perf_counter()
    decision = issue_truffle_http_lease(
        SAMPLE_PAYLOAD,
        endpoint=endpoint,
        model=model,
        timeout_ms=45000,
        prompt_text=prompt,
    )
    elapsed = round(time.perf_counter() - started, 3)
    result = {
        "endpoint": endpoint,
        "model": model,
        "elapsed_seconds": elapsed,
        "decision": decision.to_dict(),
    }
    output_path = Path("logs") / "truffle_regime_probe_latest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
