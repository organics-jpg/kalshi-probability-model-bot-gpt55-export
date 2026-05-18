"""Forward bakeoff for broader v28-style entry policies.

This is shadow-only research. It combines actual approved v28 entries with
actionable rejected observations and scores predeclared broadening policies
after settlement. The goal is to understand the coverage/profit tradeoff
without changing bot logic or placing orders.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_forward_physics_registry import build_rows as build_entry_rows, recross_hazard_score
from probe_v28_shadow_fv_variants import variant_book_when_v28_coinflip_else_edge
from probe_v28_reactivated_shadow_status import market_result, read_events
from probe_v28_rejected_opportunity_score import as_int, outcome_for_side


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.csv"
OUT_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def observation_pool() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_entry_rows():
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        ask = as_float(row.get("ask_cents"))
        p_side = as_float(row.get("p_side"))
        if not market or side not in {"yes", "no"} or ask is None or p_side is None:
            continue
        rows.append(
            {
                "source": "approved_entry",
                "market": market,
                "ts_wall": row.get("entry_ts"),
                "side": side,
                "reason": "approved_entry",
                "p_side": p_side,
                "ask_cents": ask,
                "ask_prob": ask / 100.0,
                "v28_minus_ask_prob": p_side - (ask / 100.0),
                "edge_cents": as_float(row.get("edge_cents")),
                "raw_edge_cents": as_float(row.get("raw_edge_cents")),
                "seconds_to_close": as_float(row.get("seconds_to_close")),
                "sigma_t_dollars": as_float(row.get("sigma_t_dollars")),
                "abs_d_sigma": as_float(row.get("abs_d_sigma")),
                "eligible_depth": as_float(row.get("eligible_depth")),
                "recross_hazard_score": as_float(row.get("recross_hazard_score")),
                "h6_recross_hazard_high": row.get("h6_recross_hazard_high"),
                "book_age_ms": as_float(row.get("book_age_ms")),
                "btc_age_ms": as_float(row.get("btc_age_ms")),
                "actionable": True,
                "status": row.get("status"),
                "result": row.get("result"),
                "side_won": row.get("side_won"),
                "gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
            }
        )
    for event in read_events():
        if event.get("event_type") != "mushroom_v28_rejected":
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        ask = as_float(event.get("mushroom_v28_ask_cents") or event.get("trigger_price_cents"))
        p_side = as_float(event.get("mushroom_v28_p_side"))
        if not market or side not in {"yes", "no"} or ask is None or p_side is None:
            continue
        actionable_shadow = bool(
            1.0 <= ask <= 99.0
            and event.get("mushroom_v28_book_ok") is True
            and event.get("mushroom_v28_btc_ok") is True
            and event.get("mushroom_v28_time_ok") is True
            and event.get("mushroom_v28_risk_ok") is True
        )
        if not actionable_shadow:
            continue
        status, result = market_result(market)
        side_won = outcome_for_side(result, side)
        qty = max(1, as_int(event.get("mushroom_v28_target_count")) or 1)
        gross_cents = None
        if side_won is not None:
            gross_cents = ((100 if side_won else 0) - int(ask)) * qty
        abs_d_sigma = as_float(event.get("mushroom_v28_abs_d_sigma"))
        seconds_to_close = as_float(event.get("mushroom_v28_seconds_to_close"))
        sigma_t_dollars = as_float(event.get("mushroom_v28_sigma_t_dollars"))
        recross_hazard = recross_hazard_score(abs_d_sigma, seconds_to_close, sigma_t_dollars)
        rows.append(
            {
                "source": "rejected_actionable",
                "market": market,
                "ts_wall": event.get("ts_wall"),
                "side": side,
                "reason": event.get("mushroom_v28_reject_reason") or event.get("decision_reason"),
                "p_side": p_side,
                "ask_cents": ask,
                "ask_prob": ask / 100.0,
                "v28_minus_ask_prob": p_side - (ask / 100.0),
                "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
                "raw_edge_cents": as_float(event.get("mushroom_v28_raw_edge_cents")),
                "seconds_to_close": seconds_to_close,
                "sigma_t_dollars": sigma_t_dollars,
                "abs_d_sigma": abs_d_sigma,
                "eligible_depth": as_float(event.get("mushroom_v28_eligible_depth")),
                "recross_hazard_score": recross_hazard,
                "h6_recross_hazard_high": recross_hazard is not None and recross_hazard >= 0.25,
                "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms")),
                "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
                "actionable": True,
                "status": status,
                "result": result,
                "side_won": side_won,
                "gross_cents": gross_cents,
                "hold_gross_cents": gross_cents,
            }
        )
    return rows


def base_tradeable(row: dict[str, Any]) -> bool:
    ask = as_float(row.get("ask_cents"))
    return ask is not None and 1.0 <= ask <= 90.0


def large_disagreement_book_anchor_p(row: dict[str, Any]) -> float | None:
    p_side = as_float(row.get("p_side"))
    ask_prob = as_float(row.get("ask_prob"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    if p_side is None or ask_prob is None or delta is None:
        return None
    if abs(delta) >= 0.15:
        alpha_v28 = 0.35
    elif abs(delta) >= 0.08:
        alpha_v28 = 0.55
    else:
        alpha_v28 = 1.0
    return alpha_v28 * p_side + (1.0 - alpha_v28) * ask_prob


def v28_premium_book_anchor_p(row: dict[str, Any]) -> float | None:
    p_side = as_float(row.get("p_side"))
    ask_prob = as_float(row.get("ask_prob"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    if p_side is None or ask_prob is None or delta is None:
        return None
    if delta >= 0.15:
        alpha_v28 = 0.30
    elif delta >= 0.08:
        alpha_v28 = 0.50
    else:
        alpha_v28 = 1.0
    return alpha_v28 * p_side + (1.0 - alpha_v28) * ask_prob


def policy_baseline(row: dict[str, Any]) -> bool:
    return row.get("source") == "approved_entry"


def policy_book_plus_03(row: dict[str, Any]) -> bool:
    delta = as_float(row.get("v28_minus_ask_prob"))
    return base_tradeable(row) and delta is not None and delta >= 0.03


def policy_book_plus_05(row: dict[str, Any]) -> bool:
    delta = as_float(row.get("v28_minus_ask_prob"))
    return base_tradeable(row) and delta is not None and delta >= 0.05


def policy_book_plus_05_no_cheap_yes_boundary(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    side = str(row.get("side") or "").lower()
    cheap_yes_boundary_pull = side == "yes" and p_side is not None and p_side < 0.45
    return (
        base_tradeable(row)
        and delta is not None
        and delta >= 0.05
        and not cheap_yes_boundary_pull
    )


def policy_book_plus_03_avoid_coinflip(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    return (
        base_tradeable(row)
        and p_side is not None
        and abs(p_side - 0.50) >= 0.08
        and delta is not None
        and delta >= 0.03
    )


def policy_book_plus_02_avoid_coinflip(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    return (
        base_tradeable(row)
        and p_side is not None
        and abs(p_side - 0.50) >= 0.08
        and delta is not None
        and delta >= 0.02
    )


def policy_book_plus_02_avoid_coinflip_liquid(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    depth = as_float(row.get("eligible_depth"))
    return (
        base_tradeable(row)
        and p_side is not None
        and abs(p_side - 0.50) >= 0.08
        and delta is not None
        and delta >= 0.02
        and depth is not None
        and depth >= 2.0
    )


def policy_book_plus_03_cheap_convex(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    ask = as_float(row.get("ask_cents"))
    return (
        base_tradeable(row)
        and p_side is not None
        and 0.30 <= p_side <= 0.45
        and ask is not None
        and ask <= 40.0
        and delta is not None
        and delta >= 0.03
    )


def policy_p65_book_plus_02(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    return base_tradeable(row) and p_side is not None and p_side >= 0.65 and delta is not None and delta >= 0.02


def policy_p65_book_plus_03(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    return base_tradeable(row) and p_side is not None and p_side >= 0.65 and delta is not None and delta >= 0.03


def policy_p65_large_disagreement_anchor_plus_02(row: dict[str, Any]) -> bool:
    p_eff = large_disagreement_book_anchor_p(row)
    ask_prob = as_float(row.get("ask_prob"))
    return (
        base_tradeable(row)
        and p_eff is not None
        and ask_prob is not None
        and p_eff >= 0.65
        and (p_eff - ask_prob) >= 0.02
    )


def policy_p65_v28_premium_anchor_plus_02(row: dict[str, Any]) -> bool:
    p_eff = v28_premium_book_anchor_p(row)
    ask_prob = as_float(row.get("ask_prob"))
    return (
        base_tradeable(row)
        and p_eff is not None
        and ask_prob is not None
        and p_eff >= 0.65
        and (p_eff - ask_prob) >= 0.02
    )


def policy_p55_edge_nonnegative(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    edge = as_float(row.get("edge_cents"))
    return base_tradeable(row) and p_side is not None and p_side >= 0.55 and edge is not None and edge >= 0.0


def policy_p50_book_plus_05_edge_nonnegative(row: dict[str, Any]) -> bool:
    p_side = as_float(row.get("p_side"))
    delta = as_float(row.get("v28_minus_ask_prob"))
    edge = as_float(row.get("edge_cents"))
    return (
        base_tradeable(row)
        and p_side is not None
        and p_side >= 0.50
        and delta is not None
        and delta >= 0.05
        and edge is not None
        and edge >= 0.0
    )


POLICIES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "baseline_v28_approved": policy_baseline,
    "book_plus_03": policy_book_plus_03,
    "book_plus_05": policy_book_plus_05,
    "book_plus_05_no_cheap_yes_boundary": policy_book_plus_05_no_cheap_yes_boundary,
    "book_plus_03_avoid_coinflip": policy_book_plus_03_avoid_coinflip,
    "book_plus_02_avoid_coinflip": policy_book_plus_02_avoid_coinflip,
    "book_plus_02_avoid_coinflip_liquid": policy_book_plus_02_avoid_coinflip_liquid,
    "book_plus_03_cheap_convex": policy_book_plus_03_cheap_convex,
    "p65_book_plus_02": policy_p65_book_plus_02,
    "p65_book_plus_03": policy_p65_book_plus_03,
    "p65_large_disagreement_anchor_plus_02": policy_p65_large_disagreement_anchor_plus_02,
    "p65_v28_premium_anchor_plus_02": policy_p65_v28_premium_anchor_plus_02,
    "p55_edge_nonnegative": policy_p55_edge_nonnegative,
    "p50_book_plus_05_edge_nonnegative": policy_p50_book_plus_05_edge_nonnegative,
}


def selected_rows(policy_name: str, fn: Callable[[dict[str, Any]], bool], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not fn(row):
            continue
        market = str(row.get("market") or "")
        if not market:
            continue
        if market not in picked:
            picked[market] = row
    return [
        {
            "policy": policy_name,
            **row,
        }
        for _, row in sorted(picked.items())
    ]


def summarize_policy(rows: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    count = len(rows)
    gross = sum(float(row["gross_cents"]) for row in resolved)
    brier_rows = [row for row in settled if row.get("p_side") is not None]
    raw_brier = None
    book_brier = None
    best_fv_brier = None
    if brier_rows:
        raw_brier = sum((float(row["p_side"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2 for row in brier_rows) / len(brier_rows)
        book_brier = sum((float(row["ask_prob"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2 for row in brier_rows) / len(brier_rows)
        best_fv_brier = sum(
            (variant_book_when_v28_coinflip_else_edge(row) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
            for row in brier_rows
        ) / len(brier_rows)
    return {
        "entries": count,
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": (count / watched_count * 100.0) if watched_count else None,
        "gross_cents": gross,
        "avg_gross_cents": (gross / len(resolved)) if resolved else None,
        "raw_v28_brier": raw_brier,
        "book_brier": book_brier,
        "best_fv_brier": best_fv_brier,
        "best_fv_minus_raw_brier": None if best_fv_brier is None or raw_brier is None else best_fv_brier - raw_brier,
        "best_fv_minus_book_brier": None if best_fv_brier is None or book_brier is None else best_fv_brier - book_brier,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    rows = observation_pool()
    watched_count = len(watched_markets())
    selected: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for name, fn in POLICIES.items():
        policy_rows = selected_rows(name, fn, rows)
        selected.extend(policy_rows)
        summary[name] = summarize_policy(policy_rows, watched_count)
    ranked = [
        {"policy": name, **bucket}
        for name, bucket in summary.items()
    ]
    ranked.sort(key=lambda row: (-(float(row["gross_cents"] or 0.0)), -(float(row["coverage_pct"] or 0.0)), row["policy"]))
    return {
        "watched_markets": watched_count,
        "observation_rows": len(rows),
        "summary": summary,
        "ranked": ranked,
        "rows": selected,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Shadow Entry Policy Bakeoff",
        "",
        "- Scope: approved entries plus actionable rejected observations only.",
        "- Rule: one selected side per market, first qualifying observation by telemetry time.",
        "- Warning: this is not an optimizer; tiny samples are descriptive only.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        f"- Observation rows: `{report['observation_rows']}`",
        "",
        "## Ranked Policies",
        "",
        "| rank | policy | entries | resolved/settled | wins | losses | coverage | gross c | raw brier | book brier | best fv brier | best fv vs raw | added rejects |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['policy']} | {row['entries']} | {row['resolved']}/{row['settled']} | {row['wins']} | {row['losses']} | "
            f"{row['coverage_pct']} | {row['gross_cents']} | {row['raw_v28_brier']} | {row['book_brier']} | "
            f"{row['best_fv_brier']} | {row['best_fv_minus_raw_brier']} | {row['added_reject_count']} |"
        )
    lines.extend(["", "## Selected Rows", ""])
    if report["rows"]:
        lines.append("| policy | market | source | side | reason | p | ask | delta | edge c | abs d sigma | recross | stc | gross c | result |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for row in report["rows"][-30:]:
            lines.append(
                "| {policy} | {market} | {source} | {side} | {reason} | {p_side} | {ask_cents} | {v28_minus_ask_prob} | {edge_cents} | {abs_d_sigma} | {recross_hazard_score} | {seconds_to_close} | {gross_cents} | {result} |".format(
                    **row
                )
            )
    else:
        lines.append("No selected rows yet.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
