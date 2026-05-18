from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = ROOT / "logs" / "ambiguity_slice_cases_latest.json"
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "ambiguity_break_even_latest.json"


def summarize_slice(rows: list[dict[str, Any]]) -> dict[str, Any]:
    losers = [row for row in rows if int(row.get("net_negative", 0)) == 1]
    winners = [row for row in rows if int(row.get("net_negative", 0)) == 0]
    loser_loss_total = round(sum(-float(row.get("net_pnl_dollars", 0.0)) for row in losers), 4)
    winner_profit_total = round(sum(float(row.get("net_pnl_dollars", 0.0)) for row in winners), 4)
    avg_loser_loss = round(loser_loss_total / len(losers), 4) if losers else None
    avg_winner_profit = round(winner_profit_total / len(winners), 4) if winners else None
    return {
        "count": len(rows),
        "net_negative_count": len(losers),
        "net_positive_or_flat_count": len(winners),
        "slice_net_pnl_dollars": round(sum(float(row.get("net_pnl_dollars", 0.0)) for row in rows), 4),
        "loser_loss_total_dollars": loser_loss_total,
        "winner_profit_total_dollars": winner_profit_total,
        "avg_loser_loss_abs": avg_loser_loss,
        "avg_winner_profit": avg_winner_profit,
        "max_wrong_winners_per_average_loser": (
            round(avg_loser_loss / avg_winner_profit, 4)
            if avg_loser_loss is not None and avg_winner_profit not in (None, 0.0)
            else None
        ),
    }


def best_subset_frontier(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_rows = list(enumerate(rows))
    results: list[dict[str, Any]] = []
    for block_count in range(1, len(indexed_rows) + 1):
        best_delta = None
        best_record: dict[str, Any] | None = None
        for combo in combinations(indexed_rows, block_count):
            blocked_rows = [row for _, row in combo]
            delta = round(sum(-float(row.get("net_pnl_dollars", 0.0)) for row in blocked_rows), 4)
            losers = int(sum(int(row.get("net_negative", 0)) for row in blocked_rows))
            winners = block_count - losers
            record = {
                "blocked_count": block_count,
                "blocked_net_negative": losers,
                "blocked_profitable_or_flat": winners,
                "delta_dollars": delta,
                "blocked_markets": [str(row.get("market") or "") for row in blocked_rows],
            }
            if best_delta is None or delta > best_delta:
                best_delta = delta
                best_record = record
        if best_record is not None:
            results.append(best_record)
    return results


def minimum_profitable_precision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    indexed_rows = list(enumerate(rows))
    profitable = []
    for block_count in range(1, len(indexed_rows) + 1):
        for combo in combinations(indexed_rows, block_count):
            blocked_rows = [row for _, row in combo]
            delta = round(sum(-float(row.get("net_pnl_dollars", 0.0)) for row in blocked_rows), 4)
            if delta <= 0:
                continue
            losers = int(sum(int(row.get("net_negative", 0)) for row in blocked_rows))
            winners = block_count - losers
            profitable.append(
                {
                    "blocked_count": block_count,
                    "blocked_net_negative": losers,
                    "blocked_profitable_or_flat": winners,
                    "precision_net_negative": round(losers / block_count, 4),
                    "delta_dollars": delta,
                    "blocked_markets": [str(row.get("market") or "") for row in blocked_rows],
                }
            )
    if not profitable:
        return {"exists": False}
    profitable.sort(
        key=lambda item: (
            item["precision_net_negative"],
            -item["blocked_count"],
            -item["delta_dollars"],
        )
    )
    return {"exists": True, "minimum_profitable_example": profitable[0], "top_profitable_examples": profitable[:10]}


def error_budget_by_losers_caught(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_rows = list(enumerate(rows))
    loser_total = sum(1 for _, row in indexed_rows if int(row.get("net_negative", 0)) == 1)
    results: list[dict[str, Any]] = []
    for loser_caught in range(1, loser_total + 1):
        best: dict[str, Any] | None = None
        for block_count in range(loser_caught, len(indexed_rows) + 1):
            for combo in combinations(indexed_rows, block_count):
                blocked_rows = [row for _, row in combo]
                blocked_losers = int(sum(int(row.get("net_negative", 0)) for row in blocked_rows))
                if blocked_losers != loser_caught:
                    continue
                blocked_winners = block_count - blocked_losers
                delta = round(sum(-float(row.get("net_pnl_dollars", 0.0)) for row in blocked_rows), 4)
                record = {
                    "losers_caught": blocked_losers,
                    "winners_wrongly_blocked": blocked_winners,
                    "precision_net_negative": round(blocked_losers / block_count, 4),
                    "delta_dollars": delta,
                    "blocked_markets": [str(row.get("market") or "") for row in blocked_rows],
                }
                if delta <= 0:
                    continue
                if best is None:
                    best = record
                    continue
                # Prefer allowing more mistakes while remaining profitable, then larger positive delta.
                if (
                    record["winners_wrongly_blocked"] > best["winners_wrongly_blocked"]
                    or (
                        record["winners_wrongly_blocked"] == best["winners_wrongly_blocked"]
                        and record["delta_dollars"] > best["delta_dollars"]
                    )
                ):
                    best = record
        if best is None:
            results.append(
                {
                    "losers_caught": loser_caught,
                    "profitable": False,
                }
            )
        else:
            best["profitable"] = True
            results.append(best)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze break-even accuracy requirements for ambiguity-only Truffle slices.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    data = json.loads(input_path.read_text(encoding="utf-8"))

    payload = {
        "source": str(input_path),
        "summary": data.get("summary", {}),
        "slice_analysis": {},
    }

    slices = data.get("slices", {})
    for name, slice_payload in slices.items():
        rows = list(slice_payload.get("rows") or [])
        payload["slice_analysis"][name] = {
            "slice_summary": summarize_slice(rows),
            "best_subset_frontier": best_subset_frontier(rows),
            "minimum_profitable_precision": minimum_profitable_precision(rows),
            "error_budget_by_losers_caught": error_budget_by_losers_caught(rows),
        }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved ambiguity break-even analysis to {output_path}")
    for name, info in payload["slice_analysis"].items():
        print(name)
        print(json.dumps(info["slice_summary"], indent=2))
        print(json.dumps(info["minimum_profitable_precision"], indent=2))


if __name__ == "__main__":
    main()
