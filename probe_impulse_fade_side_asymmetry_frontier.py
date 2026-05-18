"""Side-asymmetry scan for impulse fade physics.

The first live impulse-fade row failed on a YES trigger: a huge upward impulse
near the strike continued into settlement. The original motivation, however,
came from NO-side failures after a fresh favorable downside impulse. This probe
tests whether the fade branch should be asymmetric or require a real distance
cushion before fading, while preserving the high-coverage book-margin base.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic unless separately forward-locked.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_impulse_reversal_regime_frontier import (
    BLOCK_MARKETS,
    MIN_BLOCK_MARKETS,
    POSITIVE_BLOCK_RATE_FLOOR,
    coerce_extra_numeric,
    first_market_rows,
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
)


REPORT_MD = OUT_DIR / "impulse_fade_side_asymmetry_frontier_latest.md"
REPORT_JSON = OUT_DIR / "impulse_fade_side_asymmetry_frontier_latest.json"
CSV_LATEST = OUT_DIR / "impulse_fade_side_asymmetry_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "impulse_fade_side_asymmetry_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class SideSpec:
    name: str
    trigger_side: str
    min_trigger_abs_margin: float
    max_trigger_ask: float
    impulse_col: str = "impulse_3_5m"
    impulse_abs_min: float = 60.0
    over_margin_min: float = 20.0
    min_seconds_to_close: float = 600.0
    max_margin_sigma: float = 0.75
    max_trigger_score: float = 0.82
    max_fade_ask: float = 45.0

    @property
    def label(self) -> str:
        return (
            f"base={BASE_POLICY.label}; fade_trigger_side={self.trigger_side}; "
            f"{self.impulse_col}>={self.impulse_abs_min:g}; "
            f"{self.impulse_col}-margin>={self.over_margin_min:g}; "
            f"trigger_abs_margin>={self.min_trigger_abs_margin:g}; "
            f"trigger_ask<={self.max_trigger_ask:g}; sec>={self.min_seconds_to_close:g}; "
            f"trigger_score<={self.max_trigger_score:g}; fade_ask<={self.max_fade_ask:g}"
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
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def make_specs() -> List[SideSpec]:
    specs: List[SideSpec] = [
        SideSpec("baseline_no_fade", "none", 0.0, 100.0),
        SideSpec("fade_any_original", "any", 0.0, 100.0),
    ]
    for side in ["no", "yes"]:
        for min_margin in [0.0, 10.0, 25.0, 50.0]:
            for ask_max in [70.0, 76.0, 80.0, 90.0, 100.0]:
                specs.append(
                    SideSpec(
                        name=f"fade_{side}_margin{min_margin:g}_ask{ask_max:g}",
                        trigger_side=side,
                        min_trigger_abs_margin=min_margin,
                        max_trigger_ask=ask_max,
                    )
                )
    for min_margin in [10.0, 25.0, 50.0]:
        for ask_max in [76.0, 80.0, 90.0]:
            specs.append(
                SideSpec(
                    name=f"fade_any_margin{min_margin:g}_ask{ask_max:g}",
                    trigger_side="any",
                    min_trigger_abs_margin=min_margin,
                    max_trigger_ask=ask_max,
                )
            )
    return specs


def trigger_mask(chosen: pd.DataFrame, spec: SideSpec) -> pd.Series:
    if spec.trigger_side == "none":
        return pd.Series(False, index=chosen.index)
    impulse = pd.to_numeric(chosen.get(spec.impulse_col), errors="coerce")
    over_margin = pd.to_numeric(chosen.get(f"{spec.impulse_col}_over_margin"), errors="coerce")
    score = pd.to_numeric(chosen.get(BASE_POLICY.chooser), errors="coerce")
    margin_sigma = pd.to_numeric(chosen.get("margin_per_rv_sigma_15m"), errors="coerce")
    seconds = pd.to_numeric(chosen.get("seconds_to_close"), errors="coerce")
    ask = pd.to_numeric(chosen.get("ask_cents"), errors="coerce")
    abs_margin = pd.to_numeric(chosen.get("abs_margin_dollars"), errors="coerce")
    mask = (
        impulse.ge(spec.impulse_abs_min)
        & over_margin.ge(spec.over_margin_min)
        & seconds.ge(spec.min_seconds_to_close)
        & margin_sigma.le(spec.max_margin_sigma)
        & score.le(spec.max_trigger_score)
        & ask.le(spec.max_trigger_ask)
        & abs_margin.ge(spec.min_trigger_abs_margin)
    )
    if spec.trigger_side in {"yes", "no"}:
        mask &= chosen["side"].astype(str).eq(spec.trigger_side)
    return mask.fillna(False)


def opposite_rows(rows: pd.DataFrame, triggers: pd.DataFrame, spec: SideSpec) -> pd.DataFrame:
    if rows.empty or triggers.empty:
        return rows.iloc[0:0].copy()
    key_cols = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in rows.columns]
    trigger_cols = [
        "side",
        "ask_cents",
        BASE_POLICY.chooser,
        "margin_dollars",
        "signed_move_3m",
        "signed_move_5m",
        "impulse_3_5m",
        "impulse_3_5m_over_margin",
    ]
    trigger_cols = [col for col in trigger_cols if col in triggers.columns]
    trigger = triggers[key_cols + trigger_cols].rename(
        columns={
            "side": "fade_trigger_side",
            "ask_cents": "fade_trigger_ask_cents",
            BASE_POLICY.chooser: "fade_trigger_score_value",
            "margin_dollars": "fade_trigger_margin_dollars",
            "signed_move_3m": "fade_trigger_signed_move_3m",
            "signed_move_5m": "fade_trigger_signed_move_5m",
            "impulse_3_5m": "fade_trigger_impulse_3_5m",
            "impulse_3_5m_over_margin": "fade_trigger_impulse_3_5m_over_margin",
        }
    )
    faded = rows.merge(trigger, on=key_cols, how="inner")
    faded = faded[faded["side"].astype(str).ne(faded["fade_trigger_side"].astype(str))].copy()
    if faded.empty:
        return faded
    faded = faded[pd.to_numeric(faded["ask_cents"], errors="coerce").le(spec.max_fade_ask)].copy()
    if not faded.empty:
        faded["action_taken"] = "fade"
        faded["overlay"] = spec.name
    return faded


def select_spec(side_rows: pd.DataFrame, base: pd.DataFrame, spec: SideSpec) -> pd.DataFrame:
    rows = coerce_extra_numeric(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BASE_POLICY.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    chosen = chosen[gate_mask(chosen, BASE_POLICY)].copy()
    if chosen.empty:
        return enrich_selected(chosen)
    triggers = chosen[trigger_mask(chosen, spec)].copy()
    normal = chosen[~chosen.index.isin(triggers.index)].copy()
    if not normal.empty:
        normal["action_taken"] = "base"
        normal["overlay"] = "book_margin_base"
    faded = opposite_rows(rows, triggers, spec)
    selected = pd.concat([normal, faded], ignore_index=True, sort=False)
    if selected.empty:
        return enrich_selected(selected)
    selected = first_market_rows(selected)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def flatten(dataset: str, spec: SideSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "trigger_side": spec.trigger_side,
        "min_trigger_abs_margin": spec.min_trigger_abs_margin,
        "max_trigger_ask": spec.max_trigger_ask,
        "fade_selected": int(selected.get("action_taken", pd.Series(dtype=object)).astype(str).eq("fade").sum())
        if not selected.empty
        else 0,
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )
    row["all_splits_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"]
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
        base_n = int(len(block))
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": n / base_n if base_n else None,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "positive_net": net > 0.0,
                "coverage_pass": ((n / base_n) if base_n else 0.0) >= MARKET_COVERAGE_FLOOR,
                "fade_selected": int(part.get("action_taken", pd.Series(dtype=object)).astype(str).eq("fade").sum())
                if n
                else 0,
            }
        )
    return rows


def block_stability(blocks: pd.DataFrame) -> pd.DataFrame:
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy() if not blocks.empty else blocks
    rows: List[Dict[str, Any]] = []
    if supported.empty:
        return pd.DataFrame()
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": float(part["positive_net"].mean()),
                "coverage_block_rate": float(part["coverage_pass"].mean()),
                "worst_block_net_cents": float(part["net_pnl_cents"].min()),
            }
        )
    return pd.DataFrame(rows)


def combine(current: pd.DataFrame, v21: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    frame = current.merge(v21, on="candidate", suffixes=("_current", "_v21"))
    if not stability.empty:
        stab = []
        for candidate, part in stability.groupby("candidate", sort=True):
            stab.append(
                {
                    "candidate": candidate,
                    "min_positive_block_rate": float(part["positive_block_rate"].min()),
                    "min_coverage_block_rate": float(part["coverage_block_rate"].min()),
                    "worst_block_net_cents": float(part["worst_block_net_cents"].min()),
                }
            )
        frame = frame.merge(pd.DataFrame(stab), on="candidate", how="left")
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


def scan() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = coerce_extra_numeric(load_side_rows())
    v21_side = coerce_extra_numeric(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    specs = make_specs()
    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        current_selected = select_spec(current_side, current_base, spec)
        v21_selected = select_spec(v21_side, v21_base, spec)
        current_rows.append(flatten("current", spec, current_base, current_selected))
        v21_rows.append(flatten("v21", spec, v21_base, v21_selected))
        block_out.extend(block_rows("current", spec.name, current_base, current_selected))
        block_out.extend(block_rows("v21", spec.name, v21_base, v21_selected))
    blocks = pd.DataFrame(block_out)
    stability = block_stability(blocks)
    frame = combine(pd.DataFrame(current_rows), pd.DataFrame(v21_rows), stability)
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "specs": int(len(specs)),
        "strict_pass_rows": int(frame["strict_pass"].sum()) if not frame.empty else 0,
    }
    return frame, blocks, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label_current']}` | {row['strict_pass']} | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
        f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
        f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} | "
        f"{int(row['fade_selected_current'])}/{int(row['fade_selected_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Impulse Fade Side-Asymmetry Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether the impulse fade branch should be side-restricted or require a real trigger-margin cushion.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
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
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | fades current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No side-asymmetry fade variant clears the strict gate. Do not forward-lock a replacement from this scan.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc diagnostic evidence and must be forward-locked before use.")
    for path in [REPORT_MD, OUT_DIR / f"impulse_fade_side_asymmetry_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"impulse_fade_side_asymmetry_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"impulse_fade_side_asymmetry_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"impulse_fade_side_asymmetry_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Impulse fade side-asymmetry frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
