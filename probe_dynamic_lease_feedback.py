from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from probe_truffle_historical_replay import build_ordered_market_records

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "dynamic_lease_feedback_latest.json"


def simulate_dynamic_lease(
    dataset_tag: str,
    *,
    pnl_threshold: float,
    stale_threshold: float,
    exit_exception: int,
    lease_length_markets: int,
    pnl_source: str = "kept",
) -> dict[str, Any]:
    records = build_ordered_market_records(dataset_tag)
    observed_history: list[Any] = []
    kept_trade_history: list[Any] = []
    blocked_remaining = 0
    decision_rows: list[dict[str, Any]] = []
    trade_dates = sorted(
        {
            pd.Timestamp(row.market_close_time).tz_convert("America/New_York").strftime("%Y-%m-%d")
            for row in records
            if row.traded and row.market_close_time
        }
    )
    held_out_dates = set(trade_dates[3:])

    for record in records:
        recent_observed_4 = observed_history[-4:]
        if str(pnl_source or "").strip().lower() == "observed":
            recent_pnl_source_4 = [row for row in recent_observed_4 if row.traded]
        else:
            recent_pnl_source_4 = kept_trade_history[-4:]
        recent_signal_count = sum(int(row.signal_count or 0) for row in recent_observed_4)
        stale_per_signal_4 = (
            sum(int(row.stale_book_deferral_count or 0) for row in recent_observed_4) / max(1, recent_signal_count)
            if recent_observed_4
            else 0.0
        )
        pnl_4 = float(sum(float(row.pnl_dollars or 0.0) for row in recent_pnl_source_4))
        exits_4 = int(sum(1 for row in recent_pnl_source_4 if row.outcome_type == "exit"))

        decision = "PASS"
        if blocked_remaining > 0:
            decision = "LEASE_BLOCK"
        elif record.traded and (((pnl_4 >= pnl_threshold) or (stale_per_signal_4 >= stale_threshold)) and not (exits_4 >= exit_exception)):
            decision = "TRIGGER_BLOCK"
            blocked_remaining = max(0, lease_length_markets - 1)

        if record.traded:
            if decision == "PASS":
                kept_trade_history.append(record)
            decision_rows.append(
                {
                    "market": record.market,
                    "entry_date": (
                        pd.Timestamp(record.market_close_time).tz_convert("America/New_York").strftime("%Y-%m-%d")
                        if record.market_close_time
                        else ""
                    ),
                    "decision": decision,
                    "pnl_dollars": float(record.pnl_dollars or 0.0),
                    "recent_kept_pnl4": round(pnl_4, 4),
                    "recent_observed_stale_per_signal4": round(stale_per_signal_4, 4),
                    "recent_kept_exits4": exits_4,
                }
            )

        observed_history.append(record)
        if blocked_remaining > 0 and decision != "TRIGGER_BLOCK":
            blocked_remaining -= 1

    decisions = pd.DataFrame(decision_rows)
    kept = decisions[decisions["decision"] == "PASS"].copy()
    held_out = decisions[decisions["entry_date"].isin(held_out_dates)].copy()
    held_out_kept = held_out[held_out["decision"] == "PASS"].copy()
    return {
        "dataset_tag": dataset_tag,
        "pnl_source": str(pnl_source or "kept"),
        "lease_length_markets": lease_length_markets,
        "pnl_threshold": pnl_threshold,
        "stale_threshold": stale_threshold,
        "exit_exception": exit_exception,
        "kept_trades": int(len(kept)),
        "blocked_trades": int((decisions["decision"] != "PASS").sum()),
        "kept_net_pnl_dollars": round(float(kept["pnl_dollars"].sum()), 4) if not kept.empty else 0.0,
        "kept_win_rate": round(float((kept["pnl_dollars"] > 0).mean()), 4) if not kept.empty else 0.0,
        "held_out_dates": sorted(held_out_dates),
        "held_out_kept_trades": int(len(held_out_kept)),
        "held_out_blocked_trades": int((held_out["decision"] != "PASS").sum()),
        "held_out_kept_net_pnl_dollars": round(float(held_out_kept["pnl_dollars"].sum()), 4) if not held_out_kept.empty else 0.0,
        "held_out_kept_win_rate": round(float((held_out_kept["pnl_dollars"] > 0).mean()), 4) if not held_out_kept.empty else 0.0,
        "first_20_decisions": decisions.head(20).to_dict("records"),
    }


def build_scan(dataset_tag: str) -> dict[str, Any]:
    configs = [
        ("old_fixed", 3.0, 1.5, 3),
        ("tuned_fixed", 2.5, 1.25, 3),
        ("pnl_only_3", 3.0, 999.0, 99),
    ]
    rows: list[dict[str, Any]] = []
    for pnl_source in ["kept", "observed"]:
        for name, pnl_threshold, stale_threshold, exit_exception in configs:
            for lease_length in [1, 2, 3, 4, 5, 6]:
                rows.append(
                    {
                        "rule_name": name,
                        **simulate_dynamic_lease(
                            dataset_tag,
                            pnl_threshold=pnl_threshold,
                            stale_threshold=stale_threshold,
                            exit_exception=exit_exception,
                            lease_length_markets=lease_length,
                            pnl_source=pnl_source,
                        ),
                    }
                )
    return {
        "dataset_tag": dataset_tag,
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe feedback-loop risk in realized-PnL-driven dynamic leases.")
    parser.add_argument("--datasets", nargs="+", default=["live_90_78", "live_90_70"])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "datasets": [build_scan(tag) for tag in args.datasets],
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved dynamic lease feedback probe to {output_path}")
    for dataset in payload["datasets"]:
        max_kept = max(int(row["held_out_kept_trades"]) for row in dataset["results"])
        viable = [
            row
            for row in dataset["results"]
            if int(row["held_out_kept_trades"]) >= max(1, int(max_kept * 0.25))
        ]
        best = max(viable or dataset["results"], key=lambda row: float(row["held_out_kept_net_pnl_dollars"]))
        print(
            dataset["dataset_tag"],
            f"best_rule={best['rule_name']}",
            f"pnl_source={best['pnl_source']}",
            f"lease_len={best['lease_length_markets']}",
            f"held_out_kept={best['held_out_kept_trades']}",
            f"held_out_net={best['held_out_kept_net_pnl_dollars']:.2f}",
        )


if __name__ == "__main__":
    main()
