"""Research-only audit for interval-coverage fair-value candidates.

This script stress-checks the raw policies that appear to satisfy 95% realized
accuracy with >=80% recurring BTC 15-minute market coverage. The main question
is whether those passes are real fair-value edge or mostly high-price/late-market
settlement proximity.

It reads existing live-derived telemetry and writes audit artifacts under
logs/edge_research. It does not import or modify the live bot.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    TARGET_ACCURACY,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


CANDIDATES = OUT_DIR / "market_interval_80coverage_candidates_latest.csv"
MIN_WILSON_LOWER = 0.95


def wilson_lower(wins: int, n: int, z: float = 1.959963984540054) -> Optional[float]:
    if n <= 0:
        return None
    phat = wins / n
    denom = 1.0 + z * z / n
    center = phat + z * z / (2.0 * n)
    radius = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * n)) / n)
    return (center - radius) / denom


def policy_from_row(row: pd.Series) -> Policy:
    return Policy(
        chooser=str(row["chooser"]),
        min_score=float(row["min_score"]),
        ask_max=float(row["ask_max"]),
        min_seconds_to_close=float(row["min_seconds_to_close"]),
        gate=str(row["gate"]),
    )


def bool_col(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def split_summary(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    losses = rows - wins
    cost = float(selected_part["ask_cents"].sum()) if rows else 0.0
    pnl = float(selected_part["settlement_pnl_cents"].sum()) if rows else 0.0
    return {
        "base_markets": int(len(base_part)),
        "markets": rows,
        "wins": wins,
        "losses": losses,
        "accuracy": wins / rows if rows else None,
        "coverage": rows / len(base_part) if len(base_part) else None,
        "wilson95_lower": wilson_lower(wins, rows),
        "gross_pnl_cents": pnl,
        "cost_cents": cost,
        "roi_on_cost": pnl / cost if cost > 0 else None,
        "median_ask": float(selected_part["ask_cents"].median()) if rows else None,
        "p75_ask": float(selected_part["ask_cents"].quantile(0.75)) if rows else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if rows else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if rows else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if rows else None,
        "p25_seconds_to_close": float(selected_part["seconds_to_close"].quantile(0.25)) if rows else None,
    }


def enrich_selected(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    out["settlement_pnl_cents"] = np.where(out["win"], 100.0 - out["ask_cents"], -out["ask_cents"])
    return out


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(side_rows, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy)
    return enrich_selected(selected)


def summarize_policy(name: str, row: pd.Series, side_rows: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    policy = policy_from_row(row)
    selected = select_for_policy(side_rows, base, policy)
    splits = {split: split_summary(base, selected, split) for split in ["all", "train", "validation", "holdout"]}
    losses = selected[~selected["win"]].copy()
    loss_cols = [
        "entry_dt",
        "market",
        "side",
        "outcome",
        "ask_cents",
        "seconds_to_close",
        "book_p_side",
        "brownian_p_rv_15m",
        "drift_p_5m_rv_15m",
        "margin_per_rv_sigma_15m",
        "adverse_move_15m",
        "settlement_pnl_cents",
    ]
    for col in loss_cols:
        if col not in losses.columns:
            losses[col] = None
    all_summary = splits["all"]
    return {
        "name": name,
        "label": policy.label,
        "policy": {
            "chooser": policy.chooser,
            "min_score": policy.min_score,
            "ask_max": policy.ask_max,
            "min_seconds_to_close": policy.min_seconds_to_close,
            "gate": policy.gate,
        },
        "splits": splits,
        "target_pass": bool(row.get("target_pass", False)),
        "coverage_pass": bool(row.get("coverage_pass", False)),
        "nondegenerate_pass": bool(row.get("nondegenerate_pass", False)),
        "degeneracy_flags": {
            "median_ask_ge_95": bool((all_summary["median_ask"] or 0.0) >= 95.0),
            "p75_ask_ge_97": bool((all_summary["p75_ask"] or 0.0) >= 97.0),
            "uses_ask_cap_100": bool(policy.ask_max >= 100.0),
            "wilson_lower_below_95": bool((all_summary["wilson95_lower"] or 0.0) < MIN_WILSON_LOWER),
            "not_non_degenerate": not bool(row.get("nondegenerate_pass", False)),
        },
        "loss_examples": losses.sort_values(["entry_dt", "market"])[loss_cols].head(20).to_dict("records"),
    }


def choose_audit_rows(candidates: pd.DataFrame) -> List[tuple[str, pd.Series]]:
    candidates = candidates.copy()
    for col in ["target_pass", "coverage_pass", "nondegenerate_pass"]:
        candidates[col] = bool_col(candidates[col])
    for col in [
        "all_accuracy",
        "all_coverage",
        "validation_accuracy",
        "validation_coverage",
        "holdout_accuracy",
        "holdout_coverage",
        "all_median_ask",
        "all_median_seconds_to_close",
        "ask_max",
        "min_seconds_to_close",
        "min_test_accuracy",
        "min_test_coverage",
    ]:
        candidates[col] = pd.to_numeric(candidates[col], errors="coerce")

    rows: List[tuple[str, pd.Series]] = []
    raw_target = candidates[candidates["target_pass"]].head(1)
    if not raw_target.empty:
        rows.append(("best_raw_target_pass", raw_target.iloc[0]))

    economical_coverage = candidates[
        candidates["coverage_pass"]
        & candidates["ask_max"].le(95)
        & candidates["min_seconds_to_close"].ge(60)
        & candidates["all_median_ask"].le(90)
    ].sort_values(
        ["min_test_accuracy", "all_accuracy", "min_test_coverage", "all_coverage"],
        ascending=[False, False, False, False],
    )
    if not economical_coverage.empty:
        rows.append(("best_economical_80coverage", economical_coverage.iloc[0]))

    economical_accuracy = candidates[
        candidates["all_accuracy"].ge(TARGET_ACCURACY)
        & candidates["ask_max"].le(95)
        & candidates["min_seconds_to_close"].ge(60)
    ].sort_values(
        ["min_test_accuracy", "all_accuracy", "all_coverage"],
        ascending=[False, False, False],
    )
    if not economical_accuracy.empty:
        rows.append(("best_economical_95accuracy", economical_accuracy.iloc[0]))

    high_coverage = candidates[candidates["coverage_pass"]].sort_values(
        ["min_test_accuracy", "all_accuracy", "all_coverage"],
        ascending=[False, False, False],
    )
    if not high_coverage.empty:
        label = "best_any_80coverage_by_test_accuracy"
        if not any(existing_label == label for existing_label, _ in rows):
            rows.append((label, high_coverage.iloc[0]))

    return rows


def fmt_money(cents: Optional[float]) -> str:
    if cents is None or not math.isfinite(float(cents)):
        return "NA"
    return f"{float(cents):.1f}c"


def fmt_float(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.2f}"


def audit_clean_json(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): audit_clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [audit_clean_json(v) for v in value]
    return clean_json(value)


def write_report(path: Path, generated: str, base: pd.DataFrame, audits: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Interval Policy Degeneracy Audit")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only audit; no orders are submitted and no bot files are modified.")
    lines.append(f"- Resolved recurring BTC 15-minute market intervals: {len(base)}")
    lines.append("- P&L is held-to-settlement proxy before Kalshi fees.")
    lines.append("- Wilson lower bounds are 95% confidence lower bounds for realized accuracy.")
    lines.append("")
    lines.append("## Audited Policies")
    lines.append("")
    lines.append(
        "| policy | acc | Wilson low | coverage | gross P&L | ROI | median ask | ask>=95 | ask=100 | median sec | flags |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for audit in audits:
        all_summary = audit["splits"]["all"]
        flags = ", ".join(k for k, v in audit["degeneracy_flags"].items() if v) or "none"
        lines.append(
            f"| `{audit['name']}` | {pct(all_summary['accuracy'])} | "
            f"{pct(all_summary['wilson95_lower'])} | {pct(all_summary['coverage'])} | "
            f"{fmt_money(all_summary['gross_pnl_cents'])} | {pct(all_summary['roi_on_cost'])} | "
            f"{fmt_float(all_summary['median_ask'])} | {all_summary['ask_ge_95']} | "
            f"{all_summary['ask_eq_100']} | {fmt_float(all_summary['median_seconds_to_close'])} | {flags} |"
        )
    lines.append("")
    for audit in audits:
        lines.append(f"## {audit['name']}")
        lines.append("")
        lines.append(f"- Policy: `{audit['label']}`")
        lines.append(
            f"- Target pass: {audit['target_pass']}; coverage pass: {audit['coverage_pass']}; nondegenerate pass: {audit['nondegenerate_pass']}"
        )
        for split in ["train", "validation", "holdout"]:
            metric = audit["splits"][split]
            lines.append(
                f"- {split}: {metric['wins']}/{metric['markets']} wins, "
                f"{pct(metric['accuracy'])} accuracy, {pct(metric['coverage'])} coverage, "
                f"Wilson low {pct(metric['wilson95_lower'])}, P&L {fmt_money(metric['gross_pnl_cents'])}"
            )
        losses = audit["loss_examples"]
        if losses:
            lines.append("")
            lines.append("| loss | entry utc | market | side | outcome | ask | sec left | book p | rv15 p | drift p | margin rv15 | adverse15 | pnl |")
            lines.append("|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
            for idx, loss in enumerate(losses, start=1):
                lines.append(
                    f"| {idx} | {loss.get('entry_dt')} | `{loss.get('market')}` | {loss.get('side')} | "
                    f"{loss.get('outcome')} | {fmt_float(loss.get('ask_cents'))} | "
                    f"{fmt_float(loss.get('seconds_to_close'))} | {fmt_float(loss.get('book_p_side'))} | "
                    f"{fmt_float(loss.get('brownian_p_rv_15m'))} | {fmt_float(loss.get('drift_p_5m_rv_15m'))} | "
                    f"{fmt_float(loss.get('margin_per_rv_sigma_15m'))} | {fmt_float(loss.get('adverse_move_15m'))} | "
                    f"{fmt_money(loss.get('settlement_pnl_cents'))} |"
                )
        lines.append("")
    lines.append("## Read")
    lines.append("")
    raw = next((audit for audit in audits if audit["name"] == "best_raw_target_pass"), None)
    econ_cov = next((audit for audit in audits if audit["name"] == "best_economical_80coverage"), None)
    econ_acc = next((audit for audit in audits if audit["name"] == "best_economical_95accuracy"), None)
    if raw:
        raw_all = raw["splits"]["all"]
        lines.append(
            f"- The raw target pass covers {raw_all['markets']}/{raw_all['base_markets']} intervals at {pct(raw_all['accuracy'])}, "
            f"but its Wilson lower bound is only {pct(raw_all['wilson95_lower'])} and median ask is {fmt_float(raw_all['median_ask'])}c."
        )
    if econ_cov:
        econ_all = econ_cov["splits"]["all"]
        lines.append(
            f"- The best economical 80%-coverage policy covers {pct(econ_all['coverage'])}, but accuracy is only {pct(econ_all['accuracy'])}."
        )
    if econ_acc:
        econ_acc_all = econ_acc["splits"]["all"]
        lines.append(
            f"- The best economical >=95%-accuracy policy reaches {pct(econ_acc_all['accuracy'])}, but coverage is only {pct(econ_acc_all['coverage'])}."
        )
    lines.append(
        "- Current evidence does not verify a nondegenerate, sample-size-safe fair-value model that clears both 95% realized accuracy and >=80% recurring market coverage."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not CANDIDATES.exists():
        raise SystemExit(f"Missing candidate CSV: {CANDIDATES}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    side_rows = load_side_rows()
    base = market_base(side_rows)
    candidates = pd.read_csv(CANDIDATES, low_memory=False)
    audit_rows = choose_audit_rows(candidates)
    audits = [summarize_policy(name, row, side_rows, base) for name, row in audit_rows]

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    md_latest = OUT_DIR / "interval_policy_degeneracy_audit_latest.md"
    md_stamp = OUT_DIR / f"interval_policy_degeneracy_audit_{generated}.md"
    json_latest = OUT_DIR / "interval_policy_degeneracy_audit_latest.json"
    json_stamp = OUT_DIR / f"interval_policy_degeneracy_audit_{generated}.json"

    write_report(md_latest, generated, base, audits)
    write_report(md_stamp, generated, base, audits)
    summary = {
        "generated_utc": generated,
        "resolved_markets": int(len(base)),
        "target_accuracy": TARGET_ACCURACY,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "min_wilson_lower": MIN_WILSON_LOWER,
        "audits": audits,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(audit_clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Interval policy degeneracy audit complete")
    print(f"resolved_markets={len(base)} audited={len(audits)}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
