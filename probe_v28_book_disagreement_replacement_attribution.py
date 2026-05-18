"""Replacement attribution for raw p52 book-disagreement shrink.

Research-only; no live bot changes or orders.

The shrink candidate can change the first qualifying row in a market. This
diagnostic separates true probability improvement from accidental replacement
of the original trade with a later opposite-side trade.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_raw_p52_book_shrink_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_book_disagreement_replacement_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_book_disagreement_replacement_attribution_latest.md"

BASE_POLICY = "raw_probability_p52_edge0"
CANDIDATE_POLICIES = [
    "gap15_book25_p52_edge0",
    "gap15_book50_p52_edge0",
    "gap15_book75_p52_edge0",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def net(row: dict[str, Any] | None) -> float:
    if not row:
        return 0.0
    return float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)


def row_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("side"), row.get("source"), row.get("ts_wall"))


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    by_policy: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_policy.setdefault(str(row.get("policy") or ""), {})[str(row.get("market") or "")] = row
    base = by_policy.get(BASE_POLICY, {})
    reports = []
    for policy in CANDIDATE_POLICIES:
        cand = by_policy.get(policy, {})
        replacements = []
        abstentions = []
        additions = []
        unchanged = 0
        for market, base_row in sorted(base.items()):
            cand_row = cand.get(market)
            if cand_row is None:
                abstentions.append({"market": market, "base": base_row, "delta_cents": -net(base_row)})
            elif row_key(cand_row) == row_key(base_row):
                unchanged += 1
            else:
                replacements.append({
                    "market": market,
                    "base": base_row,
                    "candidate": cand_row,
                    "delta_cents": net(cand_row) - net(base_row),
                })
        for market, cand_row in sorted(cand.items()):
            if market not in base:
                additions.append({"market": market, "candidate": cand_row, "delta_cents": net(cand_row)})
        reports.append({
            "policy": policy,
            "unchanged": unchanged,
            "replacements": replacements,
            "abstentions": abstentions,
            "additions": additions,
            "replacement_count": len(replacements),
            "abstention_count": len(abstentions),
            "addition_count": len(additions),
            "replacement_delta_cents": sum(float(row["delta_cents"]) for row in replacements),
            "abstention_delta_cents": sum(float(row["delta_cents"]) for row in abstentions),
            "addition_delta_cents": sum(float(row["delta_cents"]) for row in additions),
        })
    return {
        "source": str(SOURCE_JSON),
        "base_policy": BASE_POLICY,
        "candidate_policies": CANDIDATE_POLICIES,
        "reports": reports,
        "interpretation": (
            "If shrinkage creates large replacement deltas, hard abstention is cleaner than "
            "letting the first qualifying side search continue after an overconfidence veto."
        ),
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Book-Disagreement Replacement Attribution",
        "",
        report["interpretation"],
        "",
        "| policy | unchanged | replacements | abstentions | additions | repl delta c | abstain delta c | add delta c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["reports"]:
        lines.append(
            f"| {item['policy']} | {item['unchanged']} | {item['replacement_count']} | {item['abstention_count']} | "
            f"{item['addition_count']} | {fmt(item['replacement_delta_cents'])} | {fmt(item['abstention_delta_cents'])} | "
            f"{fmt(item['addition_delta_cents'])} |"
        )
    for item in report["reports"]:
        lines.extend(["", f"## {item['policy']}", "", "| market | base | candidate | delta c |", "|---|---|---|---:|"])
        for row in item["replacements"]:
            base = row["base"]
            cand = row["candidate"]
            lines.append(
                f"| {row['market']} | {base.get('side')} {base.get('source')} p={fmt(base.get('p_eff'))} "
                f"ask={fmt(base.get('ask_prob'))} won={base.get('side_won')} net={fmt(net(base))} | "
                f"{cand.get('side')} {cand.get('source')} p={fmt(cand.get('p_eff'))} ask={fmt(cand.get('ask_prob'))} "
                f"won={cand.get('side_won')} net={fmt(net(cand))} | {fmt(row['delta_cents'])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
