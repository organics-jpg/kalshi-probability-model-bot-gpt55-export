"""Continuation/exhaustion state frontier for BTC 15m fair value.

Recent live rows split into two regimes:

1. Continuation: book, hazard, p80, and touch agree; earlier cheap same-side
   touch can be a better entry than later expensive book confidence.
2. Exhaustion/conflict: book confidence is high, but the latest path/touch cue
   is opposite; fading has failed, so the safer hypothesis is a limited veto.

This probe preserves broad book-margin coverage as the anchor and scans small,
interpretable overlays. Research-only: no orders are submitted and no bot files
or live processes are modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_impulse_reversal_regime_frontier import (
    BLOCK_MARKETS,
    MIN_BLOCK_MARKETS,
    POSITIVE_BLOCK_RATE_FLOOR,
    coerce_extra_numeric,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "continuation_exhaustion_state_frontier_latest.md"
REPORT_JSON = OUT_DIR / "continuation_exhaustion_state_frontier_latest.json"
CSV_LATEST = OUT_DIR / "continuation_exhaustion_state_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "continuation_exhaustion_state_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class StateSpec:
    name: str
    same_side_reprice: bool
    conflict_veto: bool
    min_touch_score: float
    max_touch_ask: float
    max_touch_age_sec: float
    max_conflict_book_score: float

    @property
    def label(self) -> str:
        actions: List[str] = []
        if self.same_side_reprice:
            actions.append("same-side touch reprice")
        if self.conflict_veto:
            actions.append("opposite-touch veto")
        if not actions:
            actions.append("baseline")
        return (
            f"{'+'.join(actions)}; base={BASE_POLICY.label}; "
            f"touch>={self.min_touch_score:g}; touch_ask<={self.max_touch_ask:g}; "
            f"touch_age<={self.max_touch_age_sec:g}s; "
            f"conflict_book<={self.max_conflict_book_score:g}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.{digits}f}"


def make_specs() -> List[StateSpec]:
    specs = [
        StateSpec("baseline_book_margin", False, False, 0.0, 100.0, 0.0, 1.0),
    ]
    for min_touch in [0.40, 0.50]:
        for max_ask in [55.0, 60.0]:
            for max_age in [300.0, 900.0]:
                specs.append(
                    StateSpec(
                        f"same_reprice_t{min_touch:g}_ask{max_ask:g}_age{max_age:g}",
                        True,
                        False,
                        min_touch,
                        max_ask,
                        max_age,
                        1.0,
                    )
                )
                for max_book in [0.80, 0.90]:
                    specs.append(
                        StateSpec(
                            f"conflict_veto_t{min_touch:g}_ask{max_ask:g}_age{max_age:g}_book{max_book:g}",
                            False,
                            True,
                            min_touch,
                            max_ask,
                            max_age,
                            max_book,
                        )
                    )
                    specs.append(
                        StateSpec(
                            f"same_reprice_conflict_veto_t{min_touch:g}_ask{max_ask:g}_age{max_age:g}_book{max_book:g}",
                            True,
                            True,
                            min_touch,
                            max_ask,
                            max_age,
                            max_book,
                        )
                    )
    return specs


def prepare(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    rows = add_touch_hazard_scores(coerce_extra_numeric(side_rows)).merge(
        base[["market", "split"]], on="market", how="inner"
    )
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in [
        "ask_cents",
        "book_p_side",
        "book_touch_blend_15",
        "hazard_discounted_mean_15",
        "seconds_to_close",
        "margin_per_rv_sigma_15m",
    ]:
        if col not in rows.columns:
            rows[col] = np.nan
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows.sort_values(["market", "entry_dt", "side"]).reset_index(drop=True)


def base_selected(prepared: pd.DataFrame) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, BASE_POLICY.chooser)
    selected = select_markets_from_chosen(chosen, BASE_POLICY)
    if selected.empty:
        return selected.copy()
    selected = selected.copy()
    selected["chooser"] = BASE_POLICY.chooser
    selected["score_value"] = selected[BASE_POLICY.chooser]
    selected["action_taken"] = "book_base"
    selected["overlay"] = "book_margin_base"
    return selected


def touch_candidates(touch_chosen: pd.DataFrame, spec: StateSpec) -> Dict[str, pd.DataFrame]:
    chosen = touch_chosen
    if chosen.empty:
        return {}
    selected = chosen[
        pd.to_numeric(chosen["book_touch_blend_15"], errors="coerce").ge(spec.min_touch_score)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(spec.max_touch_ask)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(120.0)
    ].copy()
    if selected.empty:
        return {}
    selected["chooser"] = "book_touch_blend_15"
    selected["score_value"] = selected["book_touch_blend_15"]
    selected = selected.sort_values(["market", "entry_dt", "ask_cents"]).reset_index(drop=True)
    return {str(market): part.copy() for market, part in selected.groupby("market", sort=False)}


def make_touch_cache(touch_chosen: pd.DataFrame, specs: List[StateSpec]) -> Dict[Tuple[float, float], Dict[str, pd.DataFrame]]:
    cache: Dict[Tuple[float, float], Dict[str, pd.DataFrame]] = {}
    for spec in specs:
        key = (spec.min_touch_score, spec.max_touch_ask)
        if key not in cache:
            cache[key] = touch_candidates(touch_chosen, spec)
    return cache


def latest_touch_before(base_row: pd.Series, by_market: Dict[str, pd.DataFrame], spec: StateSpec) -> Optional[pd.Series]:
    base_dt = pd.to_datetime(base_row.get("entry_dt"), utc=True, errors="coerce")
    if pd.isna(base_dt):
        return None
    candidates = by_market.get(str(base_row.get("market")))
    if candidates is None or candidates.empty:
        return None
    before = candidates[pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce").lt(base_dt)].copy()
    if before.empty:
        return None
    before["age_sec"] = (base_dt - pd.to_datetime(before["entry_dt"], utc=True, errors="coerce")).dt.total_seconds()
    before = before[before["age_sec"].between(0.0, spec.max_touch_age_sec)].copy()
    if before.empty:
        return None
    return before.sort_values(["entry_dt", "ask_cents"], ascending=[False, True]).iloc[0].copy()


def select_spec(base_rows: pd.DataFrame, spec: StateSpec, by_market: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    if base_rows.empty:
        return enrich_selected(base_rows.copy())
    if not spec.same_side_reprice and not spec.conflict_veto:
        return enrich_selected(base_rows.copy())
    if not by_market:
        return enrich_selected(base_rows.copy())

    out: List[pd.Series] = []
    repriced = 0
    vetoed = 0
    for _, base_row in base_rows.sort_values(["market", "entry_dt"]).iterrows():
        touch = latest_touch_before(base_row, by_market, spec)
        if touch is None:
            out.append(base_row.copy())
            continue

        same_side = str(touch.get("side")) == str(base_row.get("side"))
        book_score = float(base_row.get("book_p_side", float("nan")))

        if same_side and spec.same_side_reprice:
            chosen = touch.copy()
            chosen["action_taken"] = "same_touch_reprice"
            chosen["overlay"] = spec.name
            chosen["book_entry_dt"] = base_row.get("entry_dt")
            chosen["book_ask_cents"] = base_row.get("ask_cents")
            chosen["book_score_value"] = base_row.get("book_p_side")
            repriced += 1
            out.append(chosen)
            continue

        if (not same_side) and spec.conflict_veto and math.isfinite(book_score) and book_score <= spec.max_conflict_book_score:
            vetoed += 1
            continue

        out.append(base_row.copy())

    selected = pd.DataFrame(out)
    if selected.empty:
        selected = base_rows.iloc[0:0].copy()
    else:
        selected = (
            selected.sort_values(["market", "entry_dt", "side"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
        )
        selected["candidate"] = spec.name
    selected = enrich_selected(selected)
    selected.attrs["same_touch_repriced"] = repriced
    selected.attrs["conflict_vetoed"] = vetoed
    return selected


def flatten(dataset: str, spec: StateSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("book_base").astype(str)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "same_side_reprice": spec.same_side_reprice,
        "conflict_veto": spec.conflict_veto,
        "min_touch_score": spec.min_touch_score,
        "max_touch_ask": spec.max_touch_ask,
        "max_touch_age_sec": spec.max_touch_age_sec,
        "max_conflict_book_score": spec.max_conflict_book_score,
        "same_touch_repriced": int(actions.eq("same_touch_reprice").sum()) if not actions.empty else 0,
        "conflict_vetoed": int(selected.attrs.get("conflict_vetoed", 0)),
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )
    row["all_splits_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["oos_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"]
    )
    row["min_split_coverage"] = min((metrics[split]["coverage"] or 0.0) for split in ["train", "validation", "holdout"])
    return row


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = base.sort_values(["close_dt", "market"]).reset_index(drop=True).copy()
    base_blocks["block_index"] = base_blocks.index // BLOCK_MARKETS
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": coverage,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
            }
        )
    return rows


def block_stability(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return pd.DataFrame()
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": float(part["positive_net"].mean()) if len(part) else None,
                "coverage_block_rate": float(part["coverage_pass"].mean()) if len(part) else None,
                "worst_block_net_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
            }
        )
    return pd.DataFrame(rows)


def combine(current: pd.DataFrame, v21: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    frame = current.merge(v21, on="candidate", suffixes=("_current", "_v21"))
    if not stability.empty:
        stab_rows = []
        for candidate, part in stability.groupby("candidate", sort=True):
            stab_rows.append(
                {
                    "candidate": candidate,
                    "min_positive_block_rate": float(part["positive_block_rate"].min()),
                    "min_coverage_block_rate": float(part["coverage_block_rate"].min()),
                    "worst_block_net_cents": float(part["worst_block_net_cents"].min()),
                }
            )
        frame = frame.merge(pd.DataFrame(stab_rows), on="candidate", how="left")
    else:
        frame["min_positive_block_rate"] = np.nan
        frame["min_coverage_block_rate"] = np.nan
        frame["worst_block_net_cents"] = np.nan

    frame["combined_all_net_pnl_cents"] = (
        pd.to_numeric(frame["all_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["all_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["combined_oos_net_pnl_cents"] = (
        pd.to_numeric(frame["validation_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["validation_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["both_coverage_pass"] = frame["coverage_pass_current"].astype(bool) & frame["coverage_pass_v21"].astype(bool)
    frame["both_oos_positive"] = frame["oos_positive_current"].astype(bool) & frame["oos_positive_v21"].astype(bool)
    frame["both_all_splits_positive"] = (
        frame["all_splits_positive_current"].astype(bool) & frame["all_splits_positive_v21"].astype(bool)
    )
    frame["block_stability_pass"] = (
        pd.to_numeric(frame["min_positive_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
        & pd.to_numeric(frame["min_coverage_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
    )
    frame["strict_pass"] = (
        frame["both_coverage_pass"]
        & frame["both_oos_positive"]
        & frame["both_all_splits_positive"]
        & frame["block_stability_pass"]
    )
    frame["min_split_coverage"] = frame[["min_split_coverage_current", "min_split_coverage_v21"]].min(axis=1)
    return frame.sort_values(
        [
            "strict_pass",
            "both_coverage_pass",
            "both_oos_positive",
            "combined_oos_net_pnl_cents",
            "combined_all_net_pnl_cents",
        ],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def scan() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(add_touch_hazard_scores(current_side))
    v21_base = market_base(add_touch_hazard_scores(v21_side))
    current_prepared = prepare(current_side, current_base)
    v21_prepared = prepare(v21_side, v21_base)
    current_base_selected = base_selected(current_prepared)
    v21_base_selected = base_selected(v21_prepared)
    specs = make_specs()
    current_touch_chosen = choose_decision_sides(current_prepared, "book_touch_blend_15")
    v21_touch_chosen = choose_decision_sides(v21_prepared, "book_touch_blend_15")
    current_touch_cache = make_touch_cache(current_touch_chosen, specs)
    v21_touch_cache = make_touch_cache(v21_touch_chosen, specs)

    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        current_selected = select_spec(
            current_base_selected,
            spec,
            current_touch_cache.get((spec.min_touch_score, spec.max_touch_ask), {}),
        )
        v21_selected = select_spec(
            v21_base_selected,
            spec,
            v21_touch_cache.get((spec.min_touch_score, spec.max_touch_ask), {}),
        )
        current_rows.append(flatten("current", spec, current_base, current_selected))
        v21_rows.append(flatten("v21", spec, v21_base, v21_selected))
        block_out.extend(block_rows("current", spec.name, current_base, current_selected))
        block_out.extend(block_rows("v21", spec.name, v21_base, v21_selected))

    blocks = pd.DataFrame(block_out)
    frame = combine(pd.DataFrame(current_rows), pd.DataFrame(v21_rows), block_stability(blocks))
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "specs": int(len(specs)),
        "strict_pass_rows": int(frame["strict_pass"].sum()) if not frame.empty else 0,
    }
    return frame, blocks, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label_current']}` | {row['strict_pass']} | "
        f"{fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | "
        f"{pct(row['min_split_coverage'])} | "
        f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
        f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} | "
        f"{int(row['same_touch_repriced_current'])}/{int(row['same_touch_repriced_v21'])} | "
        f"{int(row['conflict_vetoed_current'])}/{int(row['conflict_vetoed_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Continuation/Exhaustion State Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Uses broad book-margin as the coverage anchor, then tests same-side touch repricing and opposite-touch veto.",
        "- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Candidate specs: {diagnostics['specs']}",
        f"- Strict pass rows: {diagnostics['strict_pass_rows']}",
        "",
        "## Top Rows",
        "",
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | repriced current/v21 | vetoed current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(35).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No continuation/exhaustion overlay clears the full strict gate. Do not promote a row from this scan.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc diagnostic evidence and must be forward-locked before live use.")
    lines.append(
        "- Same-side touch repricing is a distinct hypothesis from opposite-touch preemption: it asks whether path/book agreement can improve entry price without changing side."
    )
    lines.append(
        "- Caveat: same-side repricing uses later book confirmation to choose an earlier touch row, so it is diagnostic physics, not directly tradable as written."
    )
    lines.append(
        "- Opposite-touch veto is a conservative exhaustion hypothesis; it skips conflict rather than buying the opposite side."
    )
    for path in [REPORT_MD, OUT_DIR / f"continuation_exhaustion_state_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"continuation_exhaustion_state_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"continuation_exhaustion_state_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"continuation_exhaustion_state_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Continuation/exhaustion state frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
