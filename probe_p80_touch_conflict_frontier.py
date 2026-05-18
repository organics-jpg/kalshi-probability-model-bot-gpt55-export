"""P80 touch-conflict frontier for BTC 15m markets.

Two live p80 failures after the forward lock had the same shape: p80 terminal
book confidence selected one side, while an earlier cheap touch-hazard row on
the opposite side won. This probe tests that narrow causal conflict.

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


REPORT_MD = OUT_DIR / "p80_touch_conflict_frontier_latest.md"
REPORT_JSON = OUT_DIR / "p80_touch_conflict_frontier_latest.json"
CSV_LATEST = OUT_DIR / "p80_touch_conflict_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "p80_touch_conflict_blocks_latest.csv"
BLOCK_SIZE = 20

BASES = {
    "p80_ask95_sec120": Policy("book_p_side", 0.80, 95.0, 120.0, "none"),
    "p80_ask90_sec0": Policy("book_p_side", 0.80, 90.0, 0.0, "none"),
}


@dataclass(frozen=True)
class Spec:
    base_name: str
    name: str
    max_book_score: float
    min_touch_score: float
    max_touch_ask: float
    max_age_sec: float

    @property
    def label(self) -> str:
        base = BASES[self.base_name]
        if self.name.endswith("_baseline"):
            return base.label
        return (
            f"{base.label}; preempt earlier opposite touch if "
            f"book<={self.max_book_score:g}, touch>={self.min_touch_score:g}, "
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


def make_specs() -> List[Spec]:
    specs: List[Spec] = []
    for base_name in BASES:
        specs.append(Spec(base_name, f"{base_name}_baseline", 0.0, 0.0, 100.0, 0.0))
        for max_book in [0.85, 1.00]:
            for min_touch in [0.35, 0.40, 0.45]:
                for max_ask in [55.0, 60.0]:
                    for max_age in [300.0, 900.0]:
                        specs.append(
                            Spec(
                                base_name,
                                f"{base_name}_touch_preempt_book{max_book:g}_touch{min_touch:g}_ask{max_ask:g}_age{max_age:g}",
                                max_book,
                                min_touch,
                                max_ask,
                                max_age,
                            )
                        )
    return specs


def prepare(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    rows = add_touch_hazard_scores(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "book_p_side", "seconds_to_close", "book_touch_blend_15"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def base_selected(prepared: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy)
    if selected.empty:
        return selected
    selected["chooser"] = policy.chooser
    selected["score_value"] = selected[policy.chooser]
    selected["action_taken"] = "book_p80"
    selected["overlay"] = "p80_base"
    return selected


def touch_rows(prepared: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, "book_touch_blend_15")
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


def select_spec(prepared: pd.DataFrame, base_rows: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    if spec.name.endswith("_baseline") or base_rows.empty:
        return enrich_selected(base_rows)
    touch = touch_rows(prepared, spec)
    if touch.empty:
        return enrich_selected(base_rows)
    touch_by_market = {
        str(market): part.sort_values(["entry_dt", "ask_cents"]).copy()
        for market, part in touch.groupby("market", sort=False)
    }
    out: List[pd.Series] = []
    for _, base_row in base_rows.sort_values(["market", "entry_dt"]).iterrows():
        base_dt = pd.to_datetime(base_row.get("entry_dt"), utc=True, errors="coerce")
        book_score = float(base_row.get("book_p_side", float("nan")))
        candidates = touch_by_market.get(str(base_row.get("market")))
        if candidates is None or candidates.empty or pd.isna(base_dt) or not math.isfinite(book_score) or book_score > spec.max_book_score:
            out.append(base_row.copy())
            continue
        before = candidates[pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce").lt(base_dt)].copy()
        before = before[before["side"].astype(str).ne(str(base_row.get("side")))].copy()
        if before.empty:
            out.append(base_row.copy())
            continue
        before["age_sec"] = (base_dt - pd.to_datetime(before["entry_dt"], utc=True, errors="coerce")).dt.total_seconds()
        before = before[before["age_sec"].between(0.0, spec.max_age_sec)].copy()
        if before.empty:
            out.append(base_row.copy())
            continue
        chosen = before.sort_values(["entry_dt", "ask_cents"], ascending=[False, True]).iloc[0].copy()
        chosen["action_taken"] = "touch_preempt"
        chosen["overlay"] = spec.name
        chosen["p80_entry_dt"] = base_dt.isoformat()
        chosen["p80_side"] = base_row.get("side")
        chosen["p80_ask_cents"] = base_row.get("ask_cents")
        chosen["p80_score_value"] = base_row.get("book_p_side")
        out.append(chosen)
    selected = pd.DataFrame(out).drop_duplicates(subset=["market"], keep="first")
    selected = selected.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    return enrich_selected(selected)


def block_rows(dataset: str, spec: Spec, selected: pd.DataFrame) -> List[Dict[str, Any]]:
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


def flatten(prefix: str, metrics: Dict[str, Dict[str, Any]], row: Dict[str, Any]) -> None:
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{prefix}_{split}_{key}"] = value


def scan_dataset(dataset: str, side_rows: pd.DataFrame, specs: List[Spec]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    base = market_base(add_touch_hazard_scores(side_rows))
    prepared = prepare(side_rows, base)
    base_cache = {name: base_selected(prepared, policy) for name, policy in BASES.items()}
    rows: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    for spec in specs:
        selected = select_spec(prepared, base_cache[spec.base_name], spec)
        actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("book_p80").astype(str)
        row: Dict[str, Any] = {
            "dataset": dataset,
            "policy": spec.name,
            "base_name": spec.base_name,
            "label": spec.label,
            "touch_preempts": int(actions.eq("touch_preempt").sum()) if not actions.empty else 0,
        }
        flatten("", metrics_for(base, selected), row)
        rows.append(row)
        blocks.extend(block_rows(dataset, spec, selected))
    return pd.DataFrame(rows), pd.DataFrame(blocks)


def combine(current: pd.DataFrame, v21: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    c = current.set_index("policy")
    v = v21.set_index("policy")
    out: List[Dict[str, Any]] = []
    for policy in sorted(set(c.index) & set(v.index)):
        cr = c.loc[policy]
        vr = v.loc[policy]
        row = {
            "policy": policy,
            "base_name": cr["base_name"],
            "label": cr["label"],
            "current_all_net_pnl_cents": cr["_all_net_pnl_cents"],
            "v21_all_net_pnl_cents": vr["_all_net_pnl_cents"],
            "combined_all_net_pnl_cents": cr["_all_net_pnl_cents"] + vr["_all_net_pnl_cents"],
            "combined_oos_net_pnl_cents": cr["_validation_net_pnl_cents"] + cr["_holdout_net_pnl_cents"] + vr["_validation_net_pnl_cents"] + vr["_holdout_net_pnl_cents"],
            "min_split_coverage": min(cr["_train_coverage"], cr["_validation_coverage"], cr["_holdout_coverage"], vr["_train_coverage"], vr["_validation_coverage"], vr["_holdout_coverage"]),
            "current_all_accuracy": cr["_all_accuracy"],
            "v21_all_accuracy": vr["_all_accuracy"],
            "current_touch_preempts": cr["touch_preempts"],
            "v21_touch_preempts": vr["touch_preempts"],
            "all_splits_positive": all(value > 0 for value in [cr["_train_net_pnl_cents"], cr["_validation_net_pnl_cents"], cr["_holdout_net_pnl_cents"], vr["_train_net_pnl_cents"], vr["_validation_net_pnl_cents"], vr["_holdout_net_pnl_cents"]]),
            "oos_positive": all(value > 0 for value in [cr["_validation_net_pnl_cents"], cr["_holdout_net_pnl_cents"], vr["_validation_net_pnl_cents"], vr["_holdout_net_pnl_cents"]]),
        }
        part = blocks[blocks["policy"].eq(policy)]
        nets = pd.to_numeric(part["net_pnl_cents"], errors="coerce")
        row["min_positive_block_rate"] = float(nets.gt(0).mean()) if len(nets) else None
        row["worst_block_net_cents"] = float(nets.min()) if len(nets) else None
        row["strict_pass"] = bool(
            row["min_split_coverage"] >= MARKET_COVERAGE_FLOOR
            and row["all_splits_positive"]
            and row["oos_positive"]
            and row["min_positive_block_rate"] is not None
            and row["min_positive_block_rate"] >= 0.65
            and row["worst_block_net_cents"] > -400.0
        )
        out.append(row)
    frame = pd.DataFrame(out)
    return frame.sort_values(["strict_pass", "combined_oos_net_pnl_cents", "combined_all_net_pnl_cents"], ascending=[False, False, False]).reset_index(drop=True)


def write_report(generated: str, frame: pd.DataFrame) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# P80 Touch-Conflict Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether an earlier opposite touch-hazard row should preempt p80 terminal book confidence.",
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
    for _, row in frame.head(18).iterrows():
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
        lines.append("- No p80 touch-conflict rule clears the strict gate.")
    else:
        lines.append(f"- Best strict row: `{strict.iloc[0]['policy']}`.")
    lines.append("- This is post-hoc research and must be forward-locked before any live use.")
    for path in [REPORT_MD, OUT_DIR / f"p80_touch_conflict_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    specs = make_specs()
    current, current_blocks = scan_dataset("current", load_side_rows(), specs)
    v21, v21_blocks = scan_dataset("v21", load_v21_side_rows(), specs)
    blocks = pd.concat([current_blocks, v21_blocks], ignore_index=True)
    frame = combine(current, v21, blocks)
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"p80_touch_conflict_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"p80_touch_conflict_blocks_{generated}.csv", index=False)
    write_report(generated, frame)
    payload = {"generated_utc": generated, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"p80_touch_conflict_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("P80 touch-conflict frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={int(frame['strict_pass'].sum()) if not frame.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
