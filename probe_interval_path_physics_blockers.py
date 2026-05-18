"""Research-only path-physics blocker scan for BTC 15m intervals.

The economical 80%-coverage frontier loses despite apparently favorable
terminal Brownian/book probabilities. This probe questions that prior by adding
path-dependent diagnostics: how much of the current strike cushion was created
by recent side-favorable movement, whether the move is decelerating, and whether
realized volatility is expanding or compressed.

It starts from the best economical interval policy and applies simple one- and
two-condition blockers. It writes only under logs/edge_research and does not
touch live bot code or orders.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_interval_policy_degeneracy_audit import bool_col, policy_from_row, wilson_lower
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


MAX_BLOCKERS_IN_COMBO = 2


@dataclass(frozen=True)
class Blocker:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"block {self.feature}{self.op}{self.threshold:g}"

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        values = pd.to_numeric(rows.get(self.feature), errors="coerce")
        if self.op == ">=":
            return values.ge(self.threshold).fillna(False)
        if self.op == "<=":
            return values.le(self.threshold).fillna(False)
        raise ValueError(f"unknown op: {self.op}")


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.2f}"


def add_path_features(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    margin = pd.to_numeric(out["margin_dollars"], errors="coerce").abs().replace(0, np.nan)
    sec = pd.to_numeric(out["seconds_to_close"], errors="coerce").replace(0, np.nan)

    for window in [1, 3, 5, 10, 15, 30, 60]:
        move_col = f"signed_move_{window}m"
        if move_col not in out.columns:
            continue
        move = pd.to_numeric(out[move_col], errors="coerce")
        out[f"fav_move_{window}m"] = move.clip(lower=0.0)
        out[f"adv_move_signed_{window}m"] = (-move).clip(lower=0.0)
        out[f"fav_move_to_margin_{window}m"] = out[f"fav_move_{window}m"] / margin
        out[f"abs_move_to_margin_{window}m"] = move.abs() / margin

    if {"signed_move_1m", "signed_move_5m"}.issubset(out.columns):
        out["decel_1v5"] = (
            pd.to_numeric(out["signed_move_1m"], errors="coerce")
            / pd.to_numeric(out["signed_move_5m"], errors="coerce").replace(0, np.nan)
        )
    if {"signed_move_5m", "signed_move_15m"}.issubset(out.columns):
        out["decel_5v15"] = (
            pd.to_numeric(out["signed_move_5m"], errors="coerce")
            / pd.to_numeric(out["signed_move_15m"], errors="coerce").replace(0, np.nan)
        )
    if {"signed_move_15m", "signed_move_30m"}.issubset(out.columns):
        out["decel_15v30"] = (
            pd.to_numeric(out["signed_move_15m"], errors="coerce")
            / pd.to_numeric(out["signed_move_30m"], errors="coerce").replace(0, np.nan)
        )

    for a, b in [(5, 15), (15, 30), (30, 60), (5, 30)]:
        ca = f"rv_sigma_t_{a}m"
        cb = f"rv_sigma_t_{b}m"
        if ca in out.columns and cb in out.columns:
            out[f"rv_ratio_{a}_{b}"] = pd.to_numeric(out[ca], errors="coerce") / pd.to_numeric(
                out[cb], errors="coerce"
            ).replace(0, np.nan)

    if {"margin_dollars", "signed_move_15m"}.issubset(out.columns):
        out["pre_15m_margin_proxy"] = (
            pd.to_numeric(out["margin_dollars"], errors="coerce")
            - pd.to_numeric(out["signed_move_15m"], errors="coerce")
        )
        out["pre_15m_margin_per_current"] = out["pre_15m_margin_proxy"] / margin
    if {"margin_dollars", "signed_move_5m"}.issubset(out.columns):
        out["pre_5m_margin_proxy"] = (
            pd.to_numeric(out["margin_dollars"], errors="coerce")
            - pd.to_numeric(out["signed_move_5m"], errors="coerce")
        )
        out["pre_5m_margin_per_current"] = out["pre_5m_margin_proxy"] / margin

    out["margin_per_sqrt_remaining"] = pd.to_numeric(out["margin_dollars"], errors="coerce") / np.sqrt(sec)
    return out


def choose_base_policy(candidates: pd.DataFrame) -> Policy:
    frame = candidates.copy()
    for col in ["coverage_pass", "target_pass", "nondegenerate_pass"]:
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
        & frame["ask_max"].le(95.0)
        & frame["min_seconds_to_close"].ge(60.0)
        & frame["all_median_ask"].le(90.0)
    ].sort_values(
        ["min_test_accuracy", "all_accuracy", "min_test_coverage", "all_coverage"],
        ascending=[False, False, False, False],
    )
    if economical.empty:
        raise SystemExit("No economical 80%-coverage candidate found")
    return policy_from_row(economical.iloc[0])


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy).copy()
    selected["settlement_pnl_cents"] = np.where(selected["win"], 100.0 - selected["ask_cents"], -selected["ask_cents"])
    return add_path_features(selected)


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    return {
        "base_markets": int(len(base_part)),
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / len(base_part) if len(base_part) else None,
        "wilson95_lower": wilson_lower(wins, n),
        "gross_pnl_cents": float(selected_part["settlement_pnl_cents"].sum()) if n else 0.0,
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and (metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def flatten(label: str, selected: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "blocker": label,
        "target_pass": target_pass(metrics),
        "wilson_pass": wilson_pass(metrics),
        "min_test_accuracy": min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0),
        "min_test_coverage": min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0),
        "min_test_wilson": min(
            metrics["validation"]["wilson95_lower"] or 0.0,
            metrics["holdout"]["wilson95_lower"] or 0.0,
        ),
    }
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def threshold_values(rows: pd.DataFrame, feature: str) -> List[float]:
    values = pd.to_numeric(rows.get(feature), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return []
    thresholds = set(float(values.quantile(q)) for q in [0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90])
    domain = {
        "fav_move_to_margin_5m": [0.5, 0.75, 1.0, 1.25, 1.5],
        "fav_move_to_margin_15m": [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        "fav_move_to_margin_30m": [0.5, 1.0, 1.5, 2.0, 3.0],
        "pre_15m_margin_per_current": [-2.0, -1.0, -0.5, 0.0, 0.5],
        "pre_5m_margin_per_current": [-1.0, -0.5, 0.0, 0.5],
        "decel_1v5": [-1.0, 0.0, 0.25, 0.5, 1.0],
        "decel_5v15": [-1.0, 0.0, 0.25, 0.5, 1.0, 1.5],
        "rv_ratio_5_15": [0.5, 0.75, 1.0, 1.25, 1.5],
        "rv_ratio_15_30": [0.5, 0.75, 1.0, 1.25, 1.5],
        "margin_per_sqrt_remaining": [1.0, 1.5, 2.0, 2.5, 3.0],
    }.get(feature, [])
    thresholds.update(float(x) for x in domain)
    return sorted(x for x in thresholds if math.isfinite(x) and values.min() <= x <= values.max())


def make_blockers(rows: pd.DataFrame) -> List[Blocker]:
    features = [
        "fav_move_to_margin_1m",
        "fav_move_to_margin_3m",
        "fav_move_to_margin_5m",
        "fav_move_to_margin_15m",
        "fav_move_to_margin_30m",
        "pre_5m_margin_per_current",
        "pre_15m_margin_per_current",
        "decel_1v5",
        "decel_5v15",
        "decel_15v30",
        "rv_ratio_5_15",
        "rv_ratio_15_30",
        "rv_ratio_30_60",
        "margin_per_sqrt_remaining",
    ]
    blockers: List[Blocker] = []
    for feature in features:
        if feature not in rows.columns:
            continue
        for threshold in threshold_values(rows, feature):
            blockers.append(Blocker(feature, ">=", threshold))
            blockers.append(Blocker(feature, "<=", threshold))
    return blockers


def apply_blockers(rows: pd.DataFrame, blockers: Iterable[Blocker]) -> pd.DataFrame:
    mask = pd.Series(False, index=rows.index)
    for blocker in blockers:
        mask |= blocker.mask(rows)
    return rows[~mask].copy()


def scan(base: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = [flatten("no blocker", selected, base)]
    blockers = make_blockers(selected)
    masks: List[tuple[Blocker, pd.Series]] = []
    min_all_markets = math.ceil(MARKET_COVERAGE_FLOOR * len(base))
    max_drop = max(0, len(selected) - min_all_markets)
    for blocker in blockers:
        mask = blocker.mask(selected)
        drop = int(mask.sum())
        if drop == 0 or drop > max_drop:
            continue
        masks.append((blocker, mask))
        rows.append(flatten(blocker.label, selected[~mask].copy(), base))

    seen = set()
    for idx, (first, first_mask) in enumerate(masks):
        for second, second_mask in masks[idx + 1 :]:
            combo_mask = first_mask | second_mask
            key = tuple(combo_mask[combo_mask].index.tolist())
            if key in seen:
                continue
            seen.add(key)
            drop = int(combo_mask.sum())
            if drop == 0 or drop > max_drop:
                continue
            rows.append(flatten(f"{first.label} OR {second.label}", selected[~combo_mask].copy(), base))
    return pd.DataFrame(rows)


def rank_results(results: pd.DataFrame) -> pd.DataFrame:
    out = results.copy()
    out["_rank"] = list(
        zip(
            out["wilson_pass"].astype(int),
            out["target_pass"].astype(int),
            out["min_test_accuracy"],
            out["all_accuracy"],
            out["min_test_coverage"],
            out["min_test_wilson"],
            out["all_coverage"],
            out["all_gross_pnl_cents"],
        )
    )
    return out.sort_values("_rank", ascending=False).drop(columns=["_rank"]).reset_index(drop=True)


def table_lines(title: str, rows: pd.DataFrame, limit: int = 20) -> List[str]:
    lines = ["", title, ""]
    if rows.empty:
        lines.append("No rows.")
        return lines
    lines.append(
        "| rank | blocker | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | target | Wilson pass |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for idx, row in enumerate(rows.head(limit).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['blocker']}` | {pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | "
            f"{pct(row['validation_accuracy'])} | {pct(row['validation_coverage'])} | "
            f"{pct(row['holdout_accuracy'])} | {pct(row['holdout_coverage'])} | "
            f"{pct(row['validation_wilson95_lower'])} | {pct(row['holdout_wilson95_lower'])} | "
            f"{row['target_pass']} | {row['wilson_pass']} |"
        )
    return lines


def write_report(path, generated: str, base_policy: Policy, base: pd.DataFrame, results: pd.DataFrame) -> None:
    ranked = rank_results(results)
    top80 = ranked[
        (ranked["all_coverage"] >= MARKET_COVERAGE_FLOOR)
        & (ranked["validation_coverage"] >= MARKET_COVERAGE_FLOOR)
        & (ranked["holdout_coverage"] >= MARKET_COVERAGE_FLOOR)
    ]
    lines: List[str] = [
        "# Interval Path-Physics Blocker Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files are modified.",
        "- Starts from the best economical 80%-coverage interval policy.",
        "- Tests path-dependent physics blockers: recent favorable impulse, cushion created by recent move, deceleration, and realized-volatility ratios.",
        "- Unit of volume remains recurring BTC 15-minute market intervals.",
        "",
        "## Base Policy",
        "",
        f"- `{base_policy.label}`",
        f"- Resolved intervals: {len(base)}",
        "",
        "## Search Summary",
        "",
        f"- Candidate blocker rows evaluated: {len(results)}",
        f"- Target-pass rows: {int(results['target_pass'].sum())}",
        f"- Wilson-pass rows: {int(results['wilson_pass'].sum())}",
    ]
    lines.extend(table_lines("## Top Path-Physics Blockers", ranked))
    lines.extend(table_lines("## 80%-Coverage Path-Physics Blockers", top80))

    best = top80.iloc[0].to_dict() if not top80.empty else ranked.iloc[0].to_dict()
    lines += [
        "",
        "## Read",
        "",
        f"- Best scanned path blocker: `{best['blocker']}`.",
        f"- It selected {int(best['all_markets'])}/{int(best['all_base_markets'])} intervals ({pct(best['all_coverage'])}) at {pct(best['all_accuracy'])} accuracy.",
        f"- validation: {pct(best['validation_accuracy'])} at {pct(best['validation_coverage'])}; holdout: {pct(best['holdout_accuracy'])} at {pct(best['holdout_coverage'])}.",
        "- If no target-pass rows are present, the side-favorable impulse prior does not rescue the economical 80%-coverage frontier by itself.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = load_side_rows()
    base = market_base(side_rows)
    candidates_path = OUT_DIR / "market_interval_80coverage_candidates_latest.csv"
    candidates = pd.read_csv(candidates_path)
    base_policy = choose_base_policy(candidates)
    selected = select_for_policy(side_rows, base, base_policy)
    results = scan(base, selected)
    ranked = rank_results(results)

    csv_latest = OUT_DIR / "interval_path_physics_blockers_latest.csv"
    csv_stamp = OUT_DIR / f"interval_path_physics_blockers_{generated}.csv"
    md_latest = OUT_DIR / "interval_path_physics_blockers_latest.md"
    md_stamp = OUT_DIR / f"interval_path_physics_blockers_{generated}.md"
    json_latest = OUT_DIR / "interval_path_physics_blockers_latest.json"
    json_stamp = OUT_DIR / f"interval_path_physics_blockers_{generated}.json"

    ranked.to_csv(csv_latest, index=False)
    ranked.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, base_policy, base, ranked)
    write_report(md_stamp, generated, base_policy, base, ranked)
    payload = {
        "generated_utc": generated,
        "resolved_intervals": int(len(base)),
        "base_policy": base_policy.label,
        "rows": int(len(ranked)),
        "target_pass": int(ranked["target_pass"].sum()),
        "wilson_pass": int(ranked["wilson_pass"].sum()),
        "top": ranked.head(20).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Interval path-physics blocker scan complete")
    print(f"resolved_intervals={len(base)} rows={len(ranked)} target_pass={int(ranked['target_pass'].sum())} wilson_pass={int(ranked['wilson_pass'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
