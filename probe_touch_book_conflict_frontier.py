"""Touch-vs-book conflict frontier for BTC 15m markets.

The 2026-05-04 13:45Z live failure had an early cheap touch-hazard row on
NO that won, followed by later book/hazard rows on YES that lost. This probe
tests the causal version of that physics:

1. keep book_margin as the high-coverage base,
2. if an earlier cheap touch row chose the opposite side, allow it to preempt
   the later book row under a small grid of age/price/score constraints.

Research-only: no orders are submitted and no live bot files or processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, metrics_for
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "touch_book_conflict_frontier_latest.md"
REPORT_JSON = OUT_DIR / "touch_book_conflict_frontier_latest.json"
CSV_LATEST = OUT_DIR / "touch_book_conflict_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "touch_book_conflict_blocks_latest.csv"

BASE = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")
BLOCK_SIZE = 20


@dataclass(frozen=True)
class ConflictSpec:
    name: str
    max_book_score: float
    min_touch_score: float
    max_touch_ask: float
    max_age_sec: float

    @property
    def label(self) -> str:
        if self.name == "book_margin_baseline":
            return BASE.label
        return (
            f"{BASE.label}; preempt earlier opposite touch if "
            f"book<={self.max_book_score:g}, touch>= {self.min_touch_score:g}, "
            f"touch_ask<={self.max_touch_ask:g}, age<={self.max_age_sec:g}s"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.3f}"


def make_specs() -> List[ConflictSpec]:
    specs = [ConflictSpec("book_margin_baseline", 0.0, 0.0, 100.0, 0.0)]
    for max_book in [0.65, 0.70, 0.80, 1.00]:
        for min_touch in [0.35, 0.40, 0.45, 0.50]:
            for max_ask in [55.0, 60.0, 70.0]:
                for max_age in [180.0, 300.0, 600.0]:
                    specs.append(
                        ConflictSpec(
                            name=(
                                f"touch_preempt_book{max_book:g}_touch{min_touch:g}_"
                                f"ask{max_ask:g}_age{max_age:g}"
                            ),
                            max_book_score=max_book,
                            min_touch_score=min_touch,
                            max_touch_ask=max_ask,
                            max_age_sec=max_age,
                        )
                    )
    return specs


def prepare(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    rows = add_touch_hazard_scores(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in [
        "ask_cents",
        "book_p_side",
        "seconds_to_close",
        "book_touch_blend_15",
        "touch_loss_rv_15m",
        "margin_dollars",
        "signed_move_15m",
        "signed_move_30m",
    ]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def base_rows(prepared: pd.DataFrame) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, BASE.chooser)
    selected = select_markets_from_chosen(chosen, BASE)
    if selected.empty:
        return selected
    selected["chooser"] = BASE.chooser
    selected["score_value"] = selected[BASE.chooser]
    selected["action_taken"] = "book"
    selected["overlay"] = "book_margin_base"
    return selected


def touch_candidates(prepared: pd.DataFrame, spec: ConflictSpec) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, "book_touch_blend_15")
    if chosen.empty:
        return chosen
    selected = chosen[
        pd.to_numeric(chosen["book_touch_blend_15"], errors="coerce").ge(spec.min_touch_score)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(spec.max_touch_ask)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(120.0)
    ].copy()
    if selected.empty:
        return selected
    selected["chooser"] = "book_touch_blend_15"
    selected["score_value"] = selected["book_touch_blend_15"]
    return selected.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def select_spec(prepared: pd.DataFrame, base_selected: pd.DataFrame, spec: ConflictSpec) -> pd.DataFrame:
    if spec.name == "book_margin_baseline" or base_selected.empty:
        return enrich_selected(base_selected)
    touch = touch_candidates(prepared, spec)
    if touch.empty:
        return enrich_selected(base_selected)
    touch_by_market = {
        str(market): part.sort_values(["entry_dt", "ask_cents"]).copy()
        for market, part in touch.groupby("market", sort=False)
    }
    rows: List[pd.Series] = []
    for _, base_row in base_selected.sort_values(["market", "entry_dt"]).iterrows():
        book_score = float(base_row.get("book_p_side", float("nan")))
        base_dt = pd.to_datetime(base_row.get("entry_dt"), utc=True, errors="coerce")
        candidates = touch_by_market.get(str(base_row.get("market")))
        if (
            candidates is None
            or candidates.empty
            or pd.isna(base_dt)
            or not math.isfinite(book_score)
            or book_score > spec.max_book_score
        ):
            rows.append(base_row.copy())
            continue
        before = candidates[pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce").lt(base_dt)].copy()
        if before.empty:
            rows.append(base_row.copy())
            continue
        before = before[before["side"].astype(str).ne(str(base_row.get("side")))].copy()
        if before.empty:
            rows.append(base_row.copy())
            continue
        before["age_sec"] = (base_dt - pd.to_datetime(before["entry_dt"], utc=True, errors="coerce")).dt.total_seconds()
        before = before[before["age_sec"].ge(0.0) & before["age_sec"].le(spec.max_age_sec)].copy()
        if before.empty:
            rows.append(base_row.copy())
            continue
        chosen = before.sort_values(["entry_dt", "ask_cents"], ascending=[False, True]).iloc[0].copy()
        chosen["action_taken"] = "touch_preempt"
        chosen["overlay"] = spec.name
        chosen["book_entry_dt"] = base_dt.isoformat()
        chosen["book_side"] = base_row.get("side")
        chosen["book_ask_cents"] = base_row.get("ask_cents")
        chosen["book_score_value"] = base_row.get("book_p_side")
        rows.append(chosen)
    selected = pd.DataFrame(rows).drop_duplicates(subset=["market"], keep="first")
    selected = selected.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    return enrich_selected(selected)


def block_rows(dataset: str, spec: ConflictSpec, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    ordered = selected.sort_values(["close_dt", "entry_dt", "market"]).reset_index(drop=True)
    for block, start in enumerate(range(0, len(ordered), BLOCK_SIZE), start=1):
        part = ordered.iloc[start : start + BLOCK_SIZE]
        n = int(len(part))
        wins = int(part["win"].sum()) if n else 0
        rows.append(
            {
                "dataset": dataset,
                "policy": spec.name,
                "block": block,
                "markets": n,
                "wins": wins,
                "losses": n - wins,
                "net_pnl_cents": float(part["net_pnl_cents"].sum()) if n else 0.0,
            }
        )
    return rows


def flatten_metrics(prefix: str, metrics: Dict[str, Dict[str, Any]], row: Dict[str, Any]) -> None:
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{prefix}_{split}_{key}"] = value


def row_for(dataset: str, spec: ConflictSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("book").astype(str)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "policy": spec.name,
        "label": spec.label,
        "max_book_score": spec.max_book_score,
        "min_touch_score": spec.min_touch_score,
        "max_touch_ask": spec.max_touch_ask,
        "max_age_sec": spec.max_age_sec,
        "touch_preempts": int(actions.eq("touch_preempt").sum()) if not actions.empty else 0,
    }
    flatten_metrics("", metrics, row)
    return row


def scan_dataset(dataset: str, side_rows: pd.DataFrame, specs: List[ConflictSpec]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    base = market_base(add_touch_hazard_scores(side_rows))
    prepared = prepare(side_rows, base)
    base_selected = base_rows(prepared)
    out: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    for spec in specs:
        selected = select_spec(prepared, base_selected, spec)
        out.append(row_for(dataset, spec, base, selected))
        blocks.extend(block_rows(dataset, spec, selected))
    return pd.DataFrame(out), pd.DataFrame(blocks)


def combine(current: pd.DataFrame, v21: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    c = current.set_index("policy")
    v = v21.set_index("policy")
    rows: List[Dict[str, Any]] = []
    for policy in sorted(set(c.index) & set(v.index)):
        cr = c.loc[policy]
        vr = v.loc[policy]
        row = {
            "policy": policy,
            "label": cr["label"],
            "current_all_net_pnl_cents": cr["_all_net_pnl_cents"],
            "v21_all_net_pnl_cents": vr["_all_net_pnl_cents"],
            "combined_all_net_pnl_cents": cr["_all_net_pnl_cents"] + vr["_all_net_pnl_cents"],
            "combined_oos_net_pnl_cents": (
                cr["_validation_net_pnl_cents"]
                + cr["_holdout_net_pnl_cents"]
                + vr["_validation_net_pnl_cents"]
                + vr["_holdout_net_pnl_cents"]
            ),
            "min_split_coverage": min(
                cr["_train_coverage"],
                cr["_validation_coverage"],
                cr["_holdout_coverage"],
                vr["_train_coverage"],
                vr["_validation_coverage"],
                vr["_holdout_coverage"],
            ),
            "current_all_accuracy": cr["_all_accuracy"],
            "v21_all_accuracy": vr["_all_accuracy"],
            "current_touch_preempts": cr["touch_preempts"],
            "v21_touch_preempts": vr["touch_preempts"],
            "all_splits_positive": all(
                value > 0
                for value in [
                    cr["_train_net_pnl_cents"],
                    cr["_validation_net_pnl_cents"],
                    cr["_holdout_net_pnl_cents"],
                    vr["_train_net_pnl_cents"],
                    vr["_validation_net_pnl_cents"],
                    vr["_holdout_net_pnl_cents"],
                ]
            ),
            "oos_positive": all(
                value > 0
                for value in [
                    cr["_validation_net_pnl_cents"],
                    cr["_holdout_net_pnl_cents"],
                    vr["_validation_net_pnl_cents"],
                    vr["_holdout_net_pnl_cents"],
                ]
            ),
        }
        part = blocks[blocks["policy"].eq(policy)]
        block_nets = pd.to_numeric(part["net_pnl_cents"], errors="coerce")
        row["min_positive_block_rate"] = float(block_nets.gt(0).mean()) if len(block_nets) else None
        row["worst_block_net_cents"] = float(block_nets.min()) if len(block_nets) else None
        row["strict_pass"] = bool(
            row["min_split_coverage"] >= MARKET_COVERAGE_FLOOR
            and row["all_splits_positive"]
            and row["oos_positive"]
            and (row["min_positive_block_rate"] is not None and row["min_positive_block_rate"] >= 0.65)
            and row["worst_block_net_cents"] > -400.0
        )
        rows.append(row)
    frame = pd.DataFrame(rows)
    return frame.sort_values(
        ["strict_pass", "combined_oos_net_pnl_cents", "combined_all_net_pnl_cents"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def write_report(generated: str, frame: pd.DataFrame) -> None:
    strict = frame[frame["strict_pass"]].copy()
    lines = [
        "# Touch-Book Conflict Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Keeps `book_margin` as coverage base and tests whether an earlier opposite touch-hazard row should preempt later book confidence.",
        "- Strict pass requires current+v21 coverage, positive all train/validation/holdout splits, positive OOS, and block stability.",
        "",
        "## Summary",
        "",
        f"- Policies scanned: {len(frame)}",
        f"- Strict pass rows: {len(strict)}",
        "",
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | preempts current/v21 | block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(15).iterrows():
        lines.append(
            f"| `{row['policy']}` | {bool(row['strict_pass'])} | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
            f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_cents(row['v21_all_net_pnl_cents'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['v21_all_accuracy'])} | "
            f"{int(row['current_touch_preempts'])}/{int(row['v21_touch_preempts'])} | "
            f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
        )
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No touch-book conflict rule clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(f"- Best strict row: `{best['policy']}`.")
    lines.append("- This is post-hoc research and must be forward-locked before any live use.")
    for path in [REPORT_MD, OUT_DIR / f"touch_book_conflict_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    specs = make_specs()
    current_rows, current_blocks = scan_dataset("current", load_side_rows(), specs)
    v21_rows, v21_blocks = scan_dataset("v21", load_v21_side_rows(), specs)
    blocks = pd.concat([current_blocks, v21_blocks], ignore_index=True)
    frame = combine(current_rows, v21_rows, blocks)
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"touch_book_conflict_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"touch_book_conflict_blocks_{generated}.csv", index=False)
    write_report(generated, frame)
    payload = {"generated_utc": generated, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"touch_book_conflict_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Touch-book conflict frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={int(frame['strict_pass'].sum()) if not frame.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
