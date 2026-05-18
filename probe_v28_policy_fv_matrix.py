"""Policy-by-FV calibration matrix for v28 forward shadow evidence.

Entry policy and fair-value calibration interact. A probability transform can
look good globally while being worse on the subset of rows a policy would
actually trade. This report scores each predeclared FV variant inside each
causal entry-policy selection.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from probe_v28_shadow_entry_policy_bakeoff import POLICIES, observation_pool, selected_rows, watched_markets
from probe_v28_shadow_fv_variants import VARIANTS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_policy_fv_matrix_latest.csv"
OUT_JSON = OUT_DIR / "v28_policy_fv_matrix_latest.json"
OUT_MD = OUT_DIR / "v28_policy_fv_matrix_latest.md"


def score_policy_variant(policy: str, variant: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    fn = VARIANTS[variant]
    resolved = [row for row in rows if row.get("side_won") is not None]
    brier_rows = [row for row in resolved if row.get("p_side") is not None and row.get("ask_prob") is not None]
    gross = sum(float(row["gross_cents"]) for row in resolved if row.get("gross_cents") is not None)
    avg_brier = None
    avg_p = None
    win_rate = None
    if brier_rows:
        probs = [fn(row) for row in brier_rows]
        outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in brier_rows]
        avg_p = sum(probs) / len(probs)
        win_rate = sum(outcomes) / len(outcomes)
        avg_brier = sum((p - y) ** 2 for p, y in zip(probs, outcomes)) / len(probs)
    return {
        "policy": policy,
        "variant": variant,
        "entries": len(rows),
        "resolved": len(resolved),
        "wins": sum(1 for row in resolved if row.get("side_won") is True),
        "losses": sum(1 for row in resolved if row.get("side_won") is False),
        "gross_cents": gross,
        "avg_gross_cents": (gross / len(resolved)) if resolved else None,
        "avg_p": avg_p,
        "win_rate": win_rate,
        "calibration_error": None if avg_p is None or win_rate is None else win_rate - avg_p,
        "avg_brier": avg_brier,
        "coverage_pct": (len(rows) / len(watched_markets()) * 100.0) if watched_markets() else None,
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_rows() -> list[dict[str, Any]]:
    pool = observation_pool()
    rows: list[dict[str, Any]] = []
    for policy, policy_fn in POLICIES.items():
        policy_rows = selected_rows(policy, policy_fn, pool)
        for variant in VARIANTS:
            rows.append(score_policy_variant(policy, variant, policy_rows))
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    best_by_policy: dict[str, dict[str, Any]] = {}
    for row in rows:
        policy = str(row.get("policy") or "")
        existing = best_by_policy.get(policy)
        if existing is None:
            best_by_policy[policy] = row
            continue
        old_brier = existing.get("avg_brier")
        new_brier = row.get("avg_brier")
        if new_brier is not None and (old_brier is None or float(new_brier) < float(old_brier)):
            best_by_policy[policy] = row
    ranked = sorted(
        best_by_policy.values(),
        key=lambda row: (
            -(float(row.get("gross_cents") or 0.0)),
            float("inf") if row.get("avg_brier") is None else float(row["avg_brier"]),
            str(row.get("policy") or ""),
        ),
    )
    return {
        "rows": len(rows),
        "best_by_policy": best_by_policy,
        "ranked_best_policy_variants": ranked,
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


def write_md(summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Policy x FV Matrix",
        "",
        "- Scope: causal policy selections only.",
        "- Purpose: avoid applying a globally good FV transform to a policy subset where it is worse.",
        "",
        "## Best FV Variant Per Policy",
        "",
        "| rank | policy | best variant | entries | resolved | wins | losses | coverage | gross c | avg brier | error | added rejects |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(summary["ranked_best_policy_variants"], start=1):
        lines.append(
            f"| {idx} | {row['policy']} | {row['variant']} | {row['entries']} | {row['resolved']} | "
            f"{row['wins']} | {row['losses']} | {row['coverage_pct']} | {row['gross_cents']} | "
            f"{row['avg_brier']} | {row['calibration_error']} | {row['added_reject_count']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    summary = summarize(rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
