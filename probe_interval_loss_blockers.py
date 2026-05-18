"""Research-only loss-blocker search for recurring BTC 15m interval coverage.

Starts from the best economical 80%-coverage interval policy, then searches
simple pre-settlement physics blockers that may remove wrong-side markets while
keeping at least 80% of recurring market intervals.

This is exploratory evidence only. The ranking reports chronological train,
validation, and holdout splits, plus Wilson lower bounds, so raw in-sample wins
are not treated as proof.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_interval_policy_degeneracy_audit import (
    CANDIDATES,
    bool_col,
    policy_from_row,
    wilson_lower,
)
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


FEATURES = [
    "ask_cents",
    "seconds_to_close",
    "book_p_side",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "drift_p_5m_rv_15m",
    "margin_per_rv_sigma_15m",
    "margin_per_rv_sigma_30m",
    "adverse_move_3m",
    "adverse_move_5m",
    "adverse_move_15m",
    "signed_move_5m",
    "signed_move_15m",
    "abs_book_rv15_gap",
    "spread_cents",
]

DOMAIN_THRESHOLDS = {
    "ask_cents": [80, 85, 90, 92, 95],
    "seconds_to_close": [60, 120, 240, 360, 480, 720],
    "book_p_side": [0.80, 0.85, 0.90, 0.95],
    "brownian_p_rv_15m": [0.55, 0.65, 0.75, 0.85, 0.90, 0.95],
    "brownian_p_rv_30m": [0.55, 0.65, 0.75, 0.85, 0.90, 0.95],
    "brownian_p_rv_60m": [0.55, 0.65, 0.75, 0.85, 0.90, 0.95],
    "drift_p_5m_rv_15m": [0.55, 0.65, 0.75, 0.85, 0.90, 0.95],
    "drift_p_15m_rv_15m": [0.55, 0.65, 0.75, 0.85, 0.90, 0.95],
    "margin_per_rv_sigma_15m": [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
    "margin_per_rv_sigma_30m": [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
    "adverse_move_1m": [0, 5, 10, 20, 35, 50],
    "adverse_move_3m": [0, 5, 10, 20, 35, 50],
    "adverse_move_5m": [0, 5, 10, 20, 35, 50],
    "adverse_move_15m": [0, 5, 10, 20, 35, 50],
    "spread_cents": [1, 2, 3, 4, 5],
}


@dataclass(frozen=True)
class Blocker:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"block {self.feature}{self.op}{self.threshold:g}"

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        if self.feature not in rows.columns:
            return pd.Series(False, index=rows.index)
        values = pd.to_numeric(rows[self.feature], errors="coerce")
        if self.op == "<=":
            return values.le(self.threshold).fillna(False)
        if self.op == ">=":
            return values.ge(self.threshold).fillna(False)
        raise ValueError(f"unknown op: {self.op}")


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.2f}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def choose_base_policy(candidates: pd.DataFrame) -> Policy:
    frame = candidates.copy()
    for col in ["target_pass", "coverage_pass", "nondegenerate_pass"]:
        frame[col] = bool_col(frame[col])
    for col in [
        "ask_max",
        "min_seconds_to_close",
        "all_median_ask",
        "min_test_accuracy",
        "all_accuracy",
        "min_test_coverage",
        "all_coverage",
    ]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    economical = frame[
        frame["coverage_pass"]
        & frame["ask_max"].le(95)
        & frame["min_seconds_to_close"].ge(60)
        & frame["all_median_ask"].le(90)
    ].sort_values(
        ["min_test_accuracy", "all_accuracy", "min_test_coverage", "all_coverage"],
        ascending=[False, False, False, False],
    )
    if economical.empty:
        raise SystemExit("No economical 80%-coverage base policy found")
    return policy_from_row(economical.iloc[0])


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(side_rows, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy)
    selected = selected.copy()
    selected["settlement_pnl_cents"] = np.where(selected["win"], 100.0 - selected["ask_cents"], -selected["ask_cents"])
    return selected


def threshold_values(rows: pd.DataFrame, feature: str) -> List[float]:
    if feature not in rows.columns:
        return []
    values = pd.to_numeric(rows[feature], errors="coerce").dropna()
    if values.empty:
        return []
    thresholds = set(float(x) for x in DOMAIN_THRESHOLDS.get(feature, []))
    for q in [0.20, 0.40, 0.60, 0.80]:
        thresholds.add(float(values.quantile(q)))
    return sorted(x for x in thresholds if math.isfinite(x))


def make_blockers(rows: pd.DataFrame) -> List[Blocker]:
    blockers: List[Blocker] = []
    for feature in FEATURES:
        for threshold in threshold_values(rows, feature):
            blockers.append(Blocker(feature, "<=", threshold))
            blockers.append(Blocker(feature, ">=", threshold))
    return blockers


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    losses = rows - wins
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
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    for split in ["all", "train", "validation", "holdout"]:
        metric = metrics[split]
        if (metric["coverage"] or 0.0) < MARKET_COVERAGE_FLOOR:
            return False
        if (metric["accuracy"] or 0.0) < TARGET_ACCURACY:
            return False
    return True


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def flatten(label: str, selected: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "label": label,
        "target_pass": target_pass(metrics),
        "wilson_pass": wilson_pass(metrics),
    }
    row["min_test_accuracy"] = min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0)
    row["min_test_coverage"] = min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0)
    row["min_test_wilson"] = min(metrics["validation"]["wilson95_lower"] or 0.0, metrics["holdout"]["wilson95_lower"] or 0.0)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["wilson_pass"]),
        int(row["target_pass"]),
        row["min_test_accuracy"],
        row["all_accuracy"] or 0.0,
        row["min_test_coverage"],
        row["min_test_wilson"],
        row["all_coverage"] or 0.0,
    )


def apply_blockers(rows: pd.DataFrame, blockers: Iterable[Blocker]) -> pd.DataFrame:
    block_mask = pd.Series(False, index=rows.index)
    for blocker in blockers:
        block_mask |= blocker.mask(rows)
    return rows[~block_mask].copy()


def scan_blockers(base: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    blockers = make_blockers(selected)
    rows: List[Dict[str, Any]] = [flatten("no blocker", selected, base)]

    min_all_markets = math.ceil(MARKET_COVERAGE_FLOOR * len(base))
    max_drop_total = max(0, len(selected) - min_all_markets)
    seen_masks = set()
    blocker_masks = []
    for blocker in blockers:
        mask = blocker.mask(selected)
        drop_count = int(mask.sum())
        if drop_count <= 0 or drop_count > max_drop_total:
            continue
        key = tuple(bool(x) for x in mask.to_numpy())
        if key in seen_masks:
            continue
        seen_masks.add(key)
        blocker_masks.append((blocker, mask))

    for blocker, mask in blocker_masks:
        kept = selected[~mask].copy()
        row = flatten(blocker.label, kept, base)
        rows.append(row)

    for i, (left, left_mask) in enumerate(blocker_masks):
        for right, right_mask in blocker_masks[i + 1 :]:
            if left.feature == right.feature and left.op == right.op:
                continue
            combined = left_mask | right_mask
            if int(combined.sum()) > max_drop_total:
                continue
            kept = selected[~combined].copy()
            row = flatten(f"{left.label} OR {right.label}", kept, base)
            rows.append(row)

    rows.sort(key=rank_key, reverse=True)
    return pd.DataFrame(rows)


def block_needed(metric: Dict[str, Any]) -> Optional[int]:
    markets = int(metric["markets"])
    wins = int(metric["wins"])
    if markets <= 0:
        return None
    if wins / markets >= TARGET_ACCURACY:
        return 0
    max_markets_at_target = math.floor(wins / TARGET_ACCURACY)
    return max(0, markets - max_markets_at_target)


def write_report(path: Path, generated: str, base_policy: Policy, base: pd.DataFrame, selected: pd.DataFrame, results: pd.DataFrame) -> None:
    lines: List[str] = []
    lines.append("# Interval Loss-blocker Search")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only scan; no orders are submitted and no bot files are modified.")
    lines.append("- Starts from the best economical 80%-coverage interval policy, then applies one or two simple blockers.")
    lines.append("- Unit of volume is the recurring BTC 15-minute market interval.")
    lines.append("- Candidate blockers are exploratory; chronological validation/holdout and Wilson bounds are shown to avoid in-sample promotion.")
    lines.append("")
    lines.append("## Base Policy")
    lines.append("")
    lines.append(f"- `{base_policy.label}`")
    base_row = results[results["label"] == "no blocker"].iloc[0]
    lines.append(
        f"- Selected {int(base_row['all_markets'])}/{int(base_row['all_base_markets'])} intervals "
        f"({pct(base_row['all_coverage'])}) at {pct(base_row['all_accuracy'])} accuracy."
    )
    lines.append("")
    lines.append("## Search Summary")
    lines.append("")
    lines.append(f"- Resolved intervals: {len(base)}")
    lines.append(f"- Base selected intervals: {len(selected)}")
    lines.append(f"- Candidate blocker policies scanned: {len(results)}")
    lines.append(f"- Target-pass blocker policies: {int(results['target_pass'].sum())}")
    lines.append(f"- Wilson-pass blocker policies: {int(results['wilson_pass'].sum())}")
    lines.append("")

    def table(title: str, frame: pd.DataFrame, n: int = 20) -> None:
        lines.append(title)
        lines.append("")
        if frame.empty:
            lines.append("_No rows._")
            lines.append("")
            return
        lines.append(
            "| rank | blocker | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | target | Wilson pass |"
        )
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
        for idx, row in enumerate(frame.head(n).to_dict("records"), start=1):
            lines.append(
                f"| {idx} | `{row['label']}` | {pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | "
                f"{pct(row['validation_accuracy'])} | {pct(row['validation_coverage'])} | "
                f"{pct(row['holdout_accuracy'])} | {pct(row['holdout_coverage'])} | "
                f"{pct(row['validation_wilson95_lower'])} | {pct(row['holdout_wilson95_lower'])} | "
                f"{row['target_pass']} | {row['wilson_pass']} |"
            )
        lines.append("")

    table("## Top Blocker Policies", results)
    table("## 80%-Coverage Blocker Policies", results[(results["all_coverage"] >= MARKET_COVERAGE_FLOOR)])

    best = results.iloc[0].to_dict()
    lines.append("## Read")
    lines.append("")
    lines.append(f"- Best scanned blocker: `{best['label']}`.")
    lines.append(
        f"- It selected {int(best['all_markets'])}/{int(best['all_base_markets'])} intervals "
        f"({pct(best['all_coverage'])}) at {pct(best['all_accuracy'])} accuracy."
    )
    for split in ["validation", "holdout"]:
        metric = {
            "markets": best[f"{split}_markets"],
            "wins": best[f"{split}_wins"],
        }
        needed = block_needed(metric)
        lines.append(
            f"- {split}: {pct(best[f'{split}_accuracy'])} accuracy at {pct(best[f'{split}_coverage'])} coverage; "
            f"needs {needed} additional selected losses blocked without losing wins to reach 95%."
        )
    if int(results["target_pass"].sum()) == 0:
        lines.append("- No blocker combination found a nondegenerate 95% / 80% recurring-market policy.")
    if int(results["wilson_pass"].sum()) == 0:
        lines.append("- No blocker combination produced a sample-size-safe 95% Wilson lower bound across splits.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not CANDIDATES.exists():
        raise SystemExit(f"Missing candidate CSV: {CANDIDATES}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    side_rows = load_side_rows()
    base = market_base(side_rows)
    candidates = pd.read_csv(CANDIDATES, low_memory=False)
    base_policy = choose_base_policy(candidates)
    selected = select_for_policy(side_rows, base, base_policy)
    results = scan_blockers(base, selected)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    csv_latest = OUT_DIR / "interval_loss_blockers_latest.csv"
    csv_stamp = OUT_DIR / f"interval_loss_blockers_{generated}.csv"
    md_latest = OUT_DIR / "interval_loss_blockers_latest.md"
    md_stamp = OUT_DIR / f"interval_loss_blockers_{generated}.md"
    json_latest = OUT_DIR / "interval_loss_blockers_latest.json"
    json_stamp = OUT_DIR / f"interval_loss_blockers_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, base_policy, base, selected, results)
    write_report(md_stamp, generated, base_policy, base, selected, results)
    summary = {
        "generated_utc": generated,
        "resolved_markets": int(len(base)),
        "base_policy": base_policy.label,
        "base_selected_markets": int(len(selected)),
        "candidate_count": int(len(results)),
        "target_pass_count": int(results["target_pass"].sum()),
        "wilson_pass_count": int(results["wilson_pass"].sum()),
        "top": results.head(20).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Interval loss-blocker search complete")
    print(f"resolved_markets={len(base)} base_selected={len(selected)} candidates={len(results)}")
    print(f"target_pass={int(results['target_pass'].sum())} wilson_pass={int(results['wilson_pass'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
