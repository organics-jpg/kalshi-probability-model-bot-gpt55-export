"""Raw p50 with p52 side-flip confirmation candidate.

Discovery-only candidate from the p52 confirmation-path diagnostic:
- Use raw p50 for early same-side entries.
- If raw p52 later qualifies on the opposite side, use that p52 row instead.
- Do not pay up for same-side confirmation.

This tests a physical idea: low-confidence early geometry can be wrong near
the boundary, but same-side confirmation mostly pays more for the same thesis.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_p52_sideflip_candidate_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_sideflip_candidate_latest.md"
BASE_POLICY = "v28_raw_p50_edge0"
P52_POLICY = "v28_raw_p52_edge0"
CANDIDATE_POLICY = "raw_p50_else_p52_sideflip_confirm"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    if value is not None:
        return value
    return as_float(row.get("gross_cents"))


def summarize(policy: str, rows: list[dict[str, Any]], watched: int) -> dict[str, Any]:
    resolved = [row for row in rows if net(row) is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    total = sum(float(net(row) or 0.0) for row in resolved)
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    return {
        "policy": policy,
        "entries": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / watched * 100.0 if watched else None,
        "net_cents_after_entry_fee": total,
        "avg_net_cents_after_entry_fee": total / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "sideflip_confirm_count": sum(1 for row in rows if row.get("candidate_mode") == "p52_sideflip_confirm"),
        "base_raw_count": sum(1 for row in rows if row.get("candidate_mode") == "base_raw_p50"),
    }


def build_report() -> dict[str, Any]:
    payload = build_raw_physics_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    watched = int(payload.get("watched_markets") or 0)
    by_policy_market = {
        (str(row.get("policy") or ""), str(row.get("market") or "")): row
        for row in rows
        if row.get("policy") in {BASE_POLICY, P52_POLICY}
    }
    selected: list[dict[str, Any]] = []
    for _, market in sorted(k for k in by_policy_market if k[0] == BASE_POLICY):
        base = by_policy_market.get((BASE_POLICY, market))
        p52 = by_policy_market.get((P52_POLICY, market))
        if not base:
            continue
        use = base
        mode = "base_raw_p50"
        if p52 and p52.get("side") != base.get("side"):
            use = p52
            mode = "p52_sideflip_confirm"
        selected.append({**use, "policy": CANDIDATE_POLICY, "candidate_mode": mode, "base_row": base, "p52_row": p52})
    base_rows = [row for row in rows if row.get("policy") == BASE_POLICY]
    p52_rows = [row for row in rows if row.get("policy") == P52_POLICY]
    return {
        "policy": CANDIDATE_POLICY,
        "base_policy": BASE_POLICY,
        "p52_policy": P52_POLICY,
        "watched_markets": watched,
        "summary": [
            summarize(BASE_POLICY, base_rows, watched),
            summarize(P52_POLICY, p52_rows, watched),
            summarize(CANDIDATE_POLICY, selected, watched),
        ],
        "selected_rows": selected,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Raw p52 Side-Flip Candidate",
        "",
        "Discovery-only. Use raw p50 unless p52 confirmation flips side.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        "",
        "## Summary",
        "",
        "| policy | entries | settled | W/L | coverage | net c | avg c | brier | actual/sim | modes base/sideflip |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_net_cents_after_entry_fee'])} | "
            f"{fmt(row['avg_brier'])} | {row['approved_entry_count']}/{row['added_reject_count']} | "
            f"{row.get('base_raw_count', 0)}/{row.get('sideflip_confirm_count', 0)} |"
        )
    lines.extend([
        "",
        "## Selected Rows",
        "",
        "| market | mode | side | p | ask | edge | won | net c |",
        "|---|---|---|---:|---:|---:|---|---:|",
    ])
    for row in report["selected_rows"]:
        lines.append(
            f"| {row.get('market')} | {row.get('candidate_mode')} | {row.get('side')} | "
            f"{fmt(row.get('p_eff'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('eff_edge_prob'))} | "
            f"{row.get('side_won')} | {fmt(net(row))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
