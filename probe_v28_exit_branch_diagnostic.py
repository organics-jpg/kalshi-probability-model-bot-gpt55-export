"""Forward diagnostic for v28 exit branch economics.

This report is descriptive only. It asks whether each observed v28 exit branch
improved realized P&L versus holding the actual filled position to settlement.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
EXIT_JSON = OUT_DIR / "v28_exit_branch_diagnostic_latest.json"
EXIT_MD = OUT_DIR / "v28_exit_branch_diagnostic_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def side_won(row: dict[str, Any]) -> bool | None:
    result = str(row.get("result") or "").lower()
    side = str(row.get("side") or "").lower()
    if result not in {"yes", "no"} or side not in {"yes", "no"}:
        return None
    return result == side


def exit_bucket(row: dict[str, Any]) -> str:
    won = side_won(row)
    exit_value = as_float(row.get("exit_value_cents"))
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if won is None or exit_value is None:
        return "unresolved_exit"
    if won is True and exit_value < 0:
        return "winner_clipped"
    if won is True:
        return "winner_not_clipped"
    if hold is not None and actual is not None and actual > hold:
        return "loss_saved"
    return "loss_not_saved"


def branch_key(row: dict[str, Any]) -> str:
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    reason = str(exit_features.get("mushroom_v28_exit_reason") or row.get("exit_reason") or "")
    return reason or "no_exit_reason"


def build_rows() -> list[dict[str, Any]]:
    trades = reconstruct_trades(read_events())
    rows: list[dict[str, Any]] = []
    for trade in trades:
        score = score_trade(trade)
        if score.get("exit_cents") is None:
            continue
        entry_features = score.get("entry_features") if isinstance(score.get("entry_features"), dict) else {}
        exit_features = score.get("exit_features") if isinstance(score.get("exit_features"), dict) else {}
        row = {
            "market": score.get("market"),
            "side": score.get("side"),
            "qty": score.get("qty"),
            "entry_cents": score.get("entry_cents"),
            "exit_cents": score.get("exit_cents"),
            "status": score.get("status"),
            "result": score.get("result"),
            "side_won": side_won(score),
            "actual_gross_cents": score.get("actual_gross_cents"),
            "hold_gross_cents": score.get("hold_gross_cents"),
            "exit_value_cents": score.get("exit_value_cents"),
            "entry_ts": score.get("entry_ts"),
            "exit_ts": score.get("exit_ts"),
            "exit_branch": branch_key(score),
            "exit_bucket": exit_bucket(score),
            "entry_p_side": entry_features.get("mushroom_v28_p_side"),
            "entry_edge_cents": entry_features.get("mushroom_v28_edge_cents"),
            "entry_abs_d_sigma": entry_features.get("mushroom_v28_abs_d_sigma"),
            "entry_seconds_to_close": entry_features.get("mushroom_v28_seconds_to_close"),
            "entry_depth": entry_features.get("mushroom_v28_eligible_depth"),
            "exit_p_hold": exit_features.get("mushroom_v28_p_hold"),
            "exit_fair_hold_cents": exit_features.get("mushroom_v28_fair_hold_cents"),
            "exit_fair_drawdown_cents": exit_features.get("mushroom_v28_fair_drawdown_cents"),
            "exit_sigma_t_dollars": exit_features.get("mushroom_v28_sigma_t_dollars"),
            "exit_d_sigma": exit_features.get("mushroom_v28_d_sigma"),
            "exit_btc_age_ms": exit_features.get("mushroom_v28_btc_age_ms"),
            "exit_book_age_ms": exit_features.get("mushroom_v28_book_age_ms"),
        }
        rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_branch: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["exit_branch"])].append(row)

    for key, bucket in sorted(grouped.items()):
        resolved = [row for row in bucket if row.get("exit_value_cents") is not None]
        by_bucket: dict[str, int] = {}
        for row in bucket:
            by_bucket[str(row.get("exit_bucket"))] = by_bucket.get(str(row.get("exit_bucket")), 0) + 1
        by_branch[key] = {
            "exits": len(bucket),
            "resolved": len(resolved),
            "actual_gross_cents": sum(float(row["actual_gross_cents"]) for row in bucket if row.get("actual_gross_cents") is not None),
            "hold_gross_cents": sum(float(row["hold_gross_cents"]) for row in resolved),
            "exit_value_cents": sum(float(row["exit_value_cents"]) for row in resolved),
            "winner_clipped": sum(1 for row in bucket if row.get("exit_bucket") == "winner_clipped"),
            "loss_saved": sum(1 for row in bucket if row.get("exit_bucket") == "loss_saved"),
            "unresolved_exit": sum(1 for row in bucket if row.get("exit_bucket") == "unresolved_exit"),
            "by_bucket": dict(sorted(by_bucket.items())),
        }

    resolved_all = [row for row in rows if row.get("exit_value_cents") is not None]
    return {
        "exits": len(rows),
        "resolved": len(resolved_all),
        "actual_gross_cents": sum(float(row["actual_gross_cents"]) for row in rows if row.get("actual_gross_cents") is not None),
        "hold_gross_cents": sum(float(row["hold_gross_cents"]) for row in resolved_all),
        "exit_value_cents": sum(float(row["exit_value_cents"]) for row in resolved_all),
        "winner_clipped": sum(1 for row in rows if row.get("exit_bucket") == "winner_clipped"),
        "loss_saved": sum(1 for row in rows if row.get("exit_bucket") == "loss_saved"),
        "unresolved_exit": sum(1 for row in rows if row.get("exit_bucket") == "unresolved_exit"),
        "by_branch": by_branch,
    }


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Branch Diagnostic",
        "",
        "Forward-only diagnostic. It compares actual exited P&L against holding the same filled position to settlement.",
        "",
        f"- Exits: `{summary['exits']}`",
        f"- Resolved exits: `{summary['resolved']}`",
        f"- Actual exited P&L: `${summary['actual_gross_cents'] / 100.0:.2f}`",
        f"- Comparable hold P&L: `${summary['hold_gross_cents'] / 100.0:.2f}`",
        f"- Exit value vs hold: `${summary['exit_value_cents'] / 100.0:.2f}`",
        f"- Winner clipped count: `{summary['winner_clipped']}`",
        f"- Loss saved count: `{summary['loss_saved']}`",
        f"- Unresolved exits: `{summary['unresolved_exit']}`",
        "",
        "## Branches",
        "",
        "| branch | exits | resolved | actual c | hold c | exit value c | winner clipped | loss saved | unresolved | buckets |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for branch, row in summary["by_branch"].items():
        lines.append(
            "| {branch} | {exits} | {resolved} | {actual_gross_cents} | {hold_gross_cents} | {exit_value_cents} | {winner_clipped} | {loss_saved} | {unresolved_exit} | {buckets} |".format(
                branch=branch,
                buckets=",".join(f"{k}:{v}" for k, v in row["by_bucket"].items()),
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## Exit Rows",
            "",
            "| market | side | entry | exit | result | actual c | hold c | exit value c | bucket | p_hold | fair drawdown | sigma |",
            "|---|---|---:|---:|---|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {market} | {side} | {entry_cents} | {exit_cents} | {result} | {actual_gross_cents} | {hold_gross_cents} | {exit_value_cents} | {exit_bucket} | {exit_p_hold} | {exit_fair_drawdown_cents} | {exit_sigma_t_dollars} |".format(
                **row
            )
        )
    EXIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    summary = summarize(rows)
    EXIT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(rows, summary)
    print(str(EXIT_MD))


if __name__ == "__main__":
    main()
