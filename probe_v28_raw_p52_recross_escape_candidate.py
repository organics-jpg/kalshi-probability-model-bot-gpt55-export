"""Raw p52 recross-escape candidates.

Research-only. This does not change live bot logic or place orders.

Physics hypothesis:
- Raw v28 p52 is the best broad shape so far, but fresh forward losses cluster
  in weak raw probability, near-strike, high-recross states.
- Those states are not necessarily "take the opposite immediately"; they mean
  the path has not resolved yet.
- Keep high raw-edge danger rows, follow a later opposite confirmation when it
  appears quickly, and skip only the weakest low-edge unresolved danger rows.
"""
from __future__ import annotations

import csv
import json
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_frozen_forward_candidates import parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_recross_escape_candidate_latest.json"
OUT_CSV = OUT_DIR / "v28_raw_p52_recross_escape_candidate_latest.csv"
OUT_MD = OUT_DIR / "v28_raw_p52_recross_escape_candidate_latest.md"
BOOTSTRAP_SEED = 28211
BOOTSTRAP_RUNS = 2000

POLICIES = [
    {
        "policy": "p52_recross_escape_opp120_skip_edge5",
        "wait_seconds": 120,
        "low_edge_skip": 0.05,
        "high_edge_keep": 0.10,
        "min_opposite_edge": 0.0,
        "physics": "In weak near-strike recross states, keep raw edge >=10pp, skip edge <5pp, otherwise follow a quick opposite p52 confirmation within 120s.",
    },
    {
        "policy": "p52_recross_escape_opp240_skip_edge5",
        "wait_seconds": 240,
        "low_edge_skip": 0.05,
        "high_edge_keep": 0.10,
        "min_opposite_edge": 0.0,
        "physics": "Same recross escape, but allows up to 240s for opposite confirmation.",
    },
    {
        "policy": "p52_recross_escape_opp240_skip_edge10",
        "wait_seconds": 240,
        "low_edge_skip": 0.10,
        "high_edge_keep": 0.10,
        "min_opposite_edge": 0.0,
        "physics": "Strict ambiguous-band version: only keep weak recross rows with >=10pp raw edge or a 240s opposite confirmation.",
    },
    {
        "policy": "p52_recross_escape_opp240_oppedge5_keep",
        "wait_seconds": 240,
        "low_edge_skip": -1.0,
        "high_edge_keep": 0.10,
        "min_opposite_edge": 0.05,
        "physics": "Coverage-preserving version: in weak recross states, keep >=10pp raw edge, follow only opposite confirmations with >=5pp edge, otherwise keep raw p52.",
    },
    {
        "policy": "p52_recross_escape_opp240_oppedge5_skip_edge5",
        "wait_seconds": 240,
        "low_edge_skip": 0.05,
        "high_edge_keep": 0.10,
        "min_opposite_edge": 0.05,
        "physics": "Same as oppedge5, but skips unresolved weak recross rows below 5pp edge.",
    },
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_prob(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def raw_edge(row: dict[str, Any]) -> float | None:
    ask = ask_prob(row)
    if ask is None:
        return None
    return p_raw(row) - ask


def danger_bucket(row: dict[str, Any]) -> bool:
    return (
        p_raw(row) < 0.60
        and (as_float(row.get("abs_d_sigma")) or 999.0) <= 0.20
        and (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.90
    )


def qualifies_p52(row: dict[str, Any], side: str | None = None) -> bool:
    if side is not None and str(row.get("side") or "").lower() != side:
        return False
    edge = raw_edge(row)
    return base_tradeable(row) and p_raw(row) >= 0.52 and edge is not None and edge >= 0.0


def opposite_side(side: str) -> str:
    return "no" if side == "yes" else "yes"


def row_after_opposite(
    rows: list[dict[str, Any]],
    base: dict[str, Any],
    wait_seconds: int,
    min_opposite_edge: float = 0.0,
) -> dict[str, Any] | None:
    base_ts = parse_ts(base.get("ts_wall"))
    side = str(base.get("side") or "").lower()
    if base_ts is None or side not in {"yes", "no"}:
        return None
    deadline = base_ts + timedelta(seconds=wait_seconds)
    opposite = opposite_side(side)
    for row in rows:
        ts = parse_ts(row.get("ts_wall"))
        if ts is None or ts < base_ts or ts > deadline:
            continue
        edge = raw_edge(row)
        if qualifies_p52(row, opposite) and edge is not None and edge >= min_opposite_edge:
            return row
    return None


def detail(row: dict[str, Any], policy: str, mode: str, base: dict[str, Any]) -> dict[str, Any]:
    ask = ask_prob(row) or 0.0
    net = None
    if row.get("gross_cents") is not None:
        net = float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row)
    base_ts = parse_ts(base.get("ts_wall"))
    row_ts = parse_ts(row.get("ts_wall"))
    return {
        **row,
        "policy": policy,
        "mode": mode,
        "p_eff": p_raw(row),
        "raw_p_eff": p_raw(row),
        "eff_edge_prob": p_raw(row) - ask,
        "raw_edge_prob": p_raw(row) - ask,
        "net_gross_cents_after_entry_fee": net,
        "base_market": base.get("market"),
        "base_side": base.get("side"),
        "base_p": p_raw(base),
        "base_ask": ask_prob(base),
        "base_edge": raw_edge(base),
        "delay_seconds": None if base_ts is None or row_ts is None else (row_ts - base_ts).total_seconds(),
    }


def select_policy(
    base_rows: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    policy: str,
    wait_seconds: int,
    low_edge_skip: float,
    high_edge_keep: float,
    min_opposite_edge: float = 0.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in observations:
        by_market.setdefault(str(row.get("market") or ""), []).append(row)
    selected: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for base in base_rows:
        market = str(base.get("market") or "")
        edge = raw_edge(base)
        if edge is None:
            continue
        if not danger_bucket(base):
            selected.append(detail(base, policy, "base", base))
            continue
        if edge >= high_edge_keep:
            selected.append(detail(base, policy, "danger_keep_high_edge", base))
            continue
        rows = sorted(by_market.get(market, []), key=lambda item: str(item.get("ts_wall") or ""))
        opposite = row_after_opposite(rows, base, wait_seconds, min_opposite_edge)
        if opposite is not None:
            selected.append(detail(opposite, policy, "danger_follow_opposite", base))
            continue
        if edge < low_edge_skip:
            blocked.append({"market": market, "reason": "danger_low_edge_skip", "base": base})
            continue
        selected.append(detail(base, policy, "danger_no_opposite_keep", base))
    return selected, blocked


def summarize(policy: str, rows: list[dict[str, Any]], blocked: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in resolved)
    briers = [
        (float(row.get("p_eff") or 0.5) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
    ]
    mode_counts: dict[str, int] = {}
    for row in rows:
        mode = str(row.get("mode") or "unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    return {
        "policy": policy,
        "entries": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / watched_count * 100.0 if watched_count else None,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "mode_counts": mode_counts,
        "blocked_count": len(blocked),
        "blocked_reasons": reason_counts(blocked),
        "bootstrap": bootstrap(rows),
        "rows": rows,
        "blocked": blocked,
    }


def reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        reason = str(row.get("reason") or "unknown")
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_market: dict[str, float] = {}
    for row in rows:
        if row.get("gross_cents") is None:
            continue
        market = str(row.get("market") or "")
        by_market[market] = by_market.get(market, 0.0) + float(row.get("net_gross_cents_after_entry_fee") or 0.0)
    markets = sorted(by_market)
    if len(markets) < 5:
        return {"market_count": len(markets), "runs": 0, "net_p10": None, "net_p50": None, "prob_positive": None}
    rng = random.Random(BOOTSTRAP_SEED + sum(ord(ch) for ch in "|".join(markets)))
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RUNS):
        total = 0.0
        for _ in markets:
            total += by_market[rng.choice(markets)]
        samples.append(total)
    samples.sort()
    return {
        "market_count": len(markets),
        "runs": BOOTSTRAP_RUNS,
        "net_p10": percentile(samples, 0.10),
        "net_p50": percentile(samples, 0.50),
        "prob_positive": sum(1 for value in samples if value > 0.0) / len(samples),
    }


def build_report() -> dict[str, Any]:
    observations = enrich_state(attach_regime_rows(observation_pool()))
    watched = watched_markets()
    base_rows = selected_rows(observations, "v28_raw", p_raw, 0.52, 0.0)
    base_detail_rows = [detail(row, "v28_raw_p52_edge0_base", "base", row) for row in base_rows]
    summaries = [summarize("v28_raw_p52_edge0_base", base_detail_rows, [], max(1, len(watched)))]
    all_rows = list(base_detail_rows)
    for item in POLICIES:
        rows, blocked = select_policy(
            base_rows,
            observations,
            item["policy"],
            int(item["wait_seconds"]),
            float(item["low_edge_skip"]),
            float(item["high_edge_keep"]),
            float(item.get("min_opposite_edge") or 0.0),
        )
        summary = summarize(item["policy"], rows, blocked, max(1, len(watched)))
        summary["physics"] = item["physics"]
        summaries.append(summary)
        all_rows.extend(rows)
    baseline = summaries[0] if summaries else {}
    for summary in summaries:
        summary["vs_raw_p52_base"] = compare(summary, baseline)
    return {
        "watched_markets": len(watched),
        "base_policy": "v28_raw_p52_edge0",
        "base_entries": len(base_rows),
        "base_rows": base_rows,
        "policies": POLICIES,
        "summaries": summaries,
        "rows": all_rows,
    }


def compare(row: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    if not baseline or row.get("policy") == baseline.get("policy"):
        return {
            "net_cents_delta": 0.0 if baseline else None,
            "brier_delta": 0.0 if baseline else None,
            "entries_delta": 0 if baseline else None,
            "coverage_delta": 0.0 if baseline else None,
        }
    net = row.get("net_cents_after_entry_fee")
    base_net = baseline.get("net_cents_after_entry_fee")
    brier = row.get("avg_brier")
    base_brier = baseline.get("avg_brier")
    coverage = row.get("coverage_pct")
    base_coverage = baseline.get("coverage_pct")
    return {
        "net_cents_delta": None if net is None or base_net is None else float(net) - float(base_net),
        "brier_delta": None if brier is None or base_brier is None else float(brier) - float(base_brier),
        "entries_delta": int(row.get("entries") or 0) - int(baseline.get("entries") or 0),
        "coverage_delta": None if coverage is None or base_coverage is None else float(coverage) - float(base_coverage),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "policy",
            "market",
            "ts_wall",
            "side",
            "source",
            "mode",
            "p_eff",
            "ask_prob",
            "eff_edge_prob",
            "side_won",
            "net_gross_cents_after_entry_fee",
            "base_side",
            "base_p",
            "base_ask",
            "base_edge",
            "delay_seconds",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report.get("rows") or [])
    lines = [
        "# v28 Raw p52 Recross Escape Candidate",
        "",
        "Research-only candidate family. Rows were selected from raw p52, then danger-bucket rows were handled by predeclared recross/path rules.",
        "",
        f"- Watched markets: `{report.get('watched_markets')}`",
        f"- Base p52 entries: `{report.get('base_entries')}`",
        "",
        "## Scorecard",
        "",
        "| policy | entries | settled | W/L | coverage | net c | net vs raw | brier | brier vs raw | actual/sim | modes | blocked | boot p10/p>0 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for row in report.get("summaries") or []:
        boot = row.get("bootstrap") or {}
        vs_raw = row.get("vs_raw_p52_base") or {}
        lines.append(
            f"| {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {fmt(vs_raw.get('net_cents_delta'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(vs_raw.get('brier_delta'))} | "
            f"{row.get('approved_entry_count')}/{row.get('added_reject_count')} | "
            f"{row.get('mode_counts')} | {row.get('blocked_count')} | {fmt(boot.get('net_p10'))}/{fmt(boot.get('prob_positive'))} |"
        )
    lines.extend(["", "## Selected Rows", ""])
    for summary in report.get("summaries") or []:
        lines.extend([f"### {summary.get('policy')}", ""])
        lines.append("| market | mode | side | source | p | ask | edge | base side | base p | base edge | delay | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|---:|")
        for row in summary.get("rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('mode')} | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('p_eff'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('eff_edge_prob'))} | "
                f"{row.get('base_side')} | {fmt(row.get('base_p'))} | {fmt(row.get('base_edge'))} | "
                f"{fmt(row.get('delay_seconds'))} | {row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
