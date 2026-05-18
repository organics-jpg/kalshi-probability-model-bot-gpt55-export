"""Strict pre-resolution failure attribution for profit-lock registries.

This probe uses only rows registered before market close. It is diagnostic:
small-sample slices can explain failure modes, but they are not promotion
evidence and do not update any locks.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents
from probe_market_interval_80coverage import OUT_DIR, clean_json, pct
from probe_profit_lock_pending_signal_monitor import REGISTRY_PATH as MAIN_REGISTRY_PATH


PATH_REGISTRY_PATH = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"

FEATURES = [
    "ask_cents",
    "book_p_side",
    "brownian_p_rv_15m",
    "margin_dollars",
    "signed_move_3m",
    "signed_move_5m",
    "signed_move_15m",
    "signed_move_30m",
    "impulse_3_5m",
    "impulse_3_5m_over_margin",
    "adverse_move_15m",
    "touch_loss_rv_15m",
    "hazard_discounted_mean_15",
    "kinetic_touch_score_15",
    "blend_logit_book_rv_hazard_mean",
    "fair_edge_cents",
    "score_value",
    "seconds_to_close",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    for col in ["registered_utc", "entry_dt", "close_dt"]:
        rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    rows = rows[rows["registered_utc"].notna() & rows["close_dt"].notna() & rows["registered_utc"].lt(rows["close_dt"])].copy()
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in FEATURES + ["net_pnl_cents"]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
        else:
            rows[col] = math.nan
    return rows


def combined_resolved() -> pd.DataFrame:
    frames = [read_registry(MAIN_REGISTRY_PATH), read_registry(PATH_REGISTRY_PATH)]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    rows = pd.concat(frames, ignore_index=True, sort=False)
    rows = rows[rows["outcome_available_bool"]].copy()
    return rows


def lock_summary(rows: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lock_name, part in rows.groupby("lock_name", sort=True):
        n = int(len(part))
        wins = int(part["win_bool"].sum())
        losses = n - wins
        out.append({
            "lock_name": lock_name,
            "resolved": n,
            "wins": wins,
            "losses": losses,
            "accuracy": wins / n if n else None,
            "net_pnl_cents": float(part["net_pnl_cents"].sum()) if n else 0.0,
            "median_ask": float(part["ask_cents"].median()) if n else None,
            "median_score": float(part["kinetic_touch_score_15"].median()) if part["kinetic_touch_score_15"].notna().any() else None,
            "median_adverse15": float(part["adverse_move_15m"].median()) if part["adverse_move_15m"].notna().any() else None,
        })
    return out


def feature_contrast(rows: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lock_name, part in rows.groupby("lock_name", sort=True):
        wins = part[part["win_bool"]]
        losses = part[~part["win_bool"]]
        for feature in FEATURES:
            if feature not in part.columns or not part[feature].notna().any():
                continue
            out.append({
                "lock_name": lock_name,
                "feature": feature,
                "win_median": float(wins[feature].median()) if not wins.empty and wins[feature].notna().any() else None,
                "loss_median": float(losses[feature].median()) if not losses.empty and losses[feature].notna().any() else None,
                "loss_minus_win_median": (
                    float(losses[feature].median()) - float(wins[feature].median())
                    if not wins.empty and not losses.empty and wins[feature].notna().any() and losses[feature].notna().any()
                    else None
                ),
            })
    return out


def mask_for(rows: pd.DataFrame, rule: str) -> pd.Series:
    if rule.startswith("ask<="):
        return rows["ask_cents"].le(float(rule.split("<=")[1]))
    if rule.startswith("score>="):
        return rows["kinetic_touch_score_15"].ge(float(rule.split(">=")[1]))
    if rule.startswith("adverse15<="):
        return rows["adverse_move_15m"].le(float(rule.split("<=")[1]))
    if rule.startswith("impulse_over_margin<="):
        return rows["impulse_3_5m_over_margin"].le(float(rule.split("<=")[1]))
    if rule.startswith("impulse<="):
        return rows["impulse_3_5m"].le(float(rule.split("<=")[1]))
    if rule.startswith("touch_loss<="):
        return rows["touch_loss_rv_15m"].le(float(rule.split("<=")[1]))
    if rule.startswith("hazard>="):
        return rows["hazard_discounted_mean_15"].ge(float(rule.split(">=")[1]))
    if rule.startswith("blend>="):
        return rows["blend_logit_book_rv_hazard_mean"].ge(float(rule.split(">=")[1]))
    if rule.startswith("fair_edge>="):
        return rows["fair_edge_cents"].ge(float(rule.split(">=")[1]))
    if rule.startswith("book>="):
        return rows["book_p_side"].ge(float(rule.split(">=")[1]))
    if rule.startswith("signal_score>="):
        return rows["score_value"].ge(float(rule.split(">=")[1]))
    if rule == "score>=0.60 AND ask<=70":
        return rows["kinetic_touch_score_15"].ge(0.60) & rows["ask_cents"].le(70)
    if rule == "score>=0.60 AND adverse15<=25":
        return rows["kinetic_touch_score_15"].ge(0.60) & rows["adverse_move_15m"].le(25)
    if rule == "ask<=70 AND adverse15<=50":
        return rows["ask_cents"].le(70) & rows["adverse_move_15m"].le(50)
    if rule == "blend>=0.45 AND ask<=70":
        return rows["blend_logit_book_rv_hazard_mean"].ge(0.45) & rows["ask_cents"].le(70)
    if rule == "fair_edge>=-5 AND ask<=70":
        return rows["fair_edge_cents"].ge(-5) & rows["ask_cents"].le(70)
    raise ValueError(rule)


def diagnostic_blockers(rows: pd.DataFrame) -> List[Dict[str, Any]]:
    rules = (
        [f"ask<={x}" for x in [55, 60, 65, 70, 75]]
        + [f"score>={x:.2f}" for x in [0.55, 0.60, 0.65, 0.70]]
        + [f"adverse15<={x}" for x in [0, 10, 25, 50, 100]]
        + [f"impulse<={x}" for x in [40, 60, 80, 120]]
        + [f"impulse_over_margin<={x}" for x in [-20, 0, 20, 40]]
        + [f"touch_loss<={x:.2f}" for x in [0.75, 0.85, 0.95]]
        + [f"hazard>={x:.2f}" for x in [0.45, 0.50, 0.55, 0.60]]
        + [f"blend>={x:.2f}" for x in [0.45, 0.50, 0.55, 0.60]]
        + [f"fair_edge>={x}" for x in [-10, -5, 0, 5]]
        + [f"book>={x:.2f}" for x in [0.55, 0.60, 0.65]]
        + [f"signal_score>={x:.2f}" for x in [0.55, 0.60, 0.65, 0.70]]
        + [
            "score>=0.60 AND ask<=70",
            "score>=0.60 AND adverse15<=25",
            "ask<=70 AND adverse15<=50",
            "blend>=0.45 AND ask<=70",
            "fair_edge>=-5 AND ask<=70",
        ]
    )
    locks = [
        "book_margin",
        "book_margin_early",
        "book_margin_gap015",
        "book_margin_delayed_adv100_brownian55",
        "book_refmargin_score_switch",
        "score_min60",
        "score_min60_gap020",
        "v2_wait_score_min60_early",
        "v2_wait_score_min60_brownian70_early",
        "kinetic_touch",
        "hazard_mean_touch80",
        "hazard_mean_touch80_ask76",
        "logit_blend_edge10",
        "logit_blend_thresh55_edge15",
        "hazard_fallback_logit55",
        "hazard_fallback_logit55_wait8",
        "hazard_fallback_score60",
        "impulse_reversal_book_margin_fade",
        "kinetic_guard",
        "kinetic_price_guard",
        "kinetic_combo_price_guard",
        "kinetic_path_confirm",
    ]
    out: List[Dict[str, Any]] = []
    for lock_name in locks:
        part = rows[rows["lock_name"].eq(lock_name)].copy()
        if part.empty:
            continue
        base_n = int(len(part))
        base_net = float(part["net_pnl_cents"].sum())
        for rule in rules:
            try:
                kept = part[mask_for(part, rule).fillna(False)].copy()
            except Exception:
                continue
            n = int(len(kept))
            if n == 0:
                continue
            wins = int(kept["win_bool"].sum())
            net = float(kept["net_pnl_cents"].sum())
            out.append({
                "lock_name": lock_name,
                "rule": rule,
                "kept": n,
                "base": base_n,
                "retention": n / base_n if base_n else None,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_delta_vs_base": net - base_net,
                "diagnostic_only": True,
            })
    out.sort(
        key=lambda row: (
            row["net_pnl_cents"],
            row["retention"] or 0.0,
            row["accuracy"] or 0.0,
        ),
        reverse=True,
    )
    return out


def write_report(generated: str, rows: pd.DataFrame, summaries: List[Dict[str, Any]], contrasts: List[Dict[str, Any]], blockers: List[Dict[str, Any]]) -> None:
    lines = [
        "# Profit Lock Strict Failure Attribution",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only attribution; no orders are submitted and no bot files or live processes are touched.",
        "- Uses only clean rows registered before market close and already resolved.",
        "- Blocker rows are diagnostic only; they are not promotion evidence and do not update locks.",
        "",
        f"- Strict resolved rows: {len(rows)}",
        "",
        "## Lock Summary",
        "",
        "| lock | resolved | wins/losses | acc | net P&L | median ask | median score | median adverse15 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['lock_name']} | {row['resolved']} | {row['wins']}/{row['losses']} | "
            f"{pct(row['accuracy'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_cents(row['median_ask'])} | {row['median_score'] if row['median_score'] is not None else 'NA'} | "
            f"{fmt_cents(row['median_adverse15'])} |"
        )
    lines += [
        "",
        "## Largest Win/Loss Feature Separations",
        "",
        "| lock | feature | win median | loss median | loss-win |",
        "|---|---|---:|---:|---:|",
    ]
    contrast_rows = [row for row in contrasts if row["loss_minus_win_median"] is not None]
    contrast_rows.sort(key=lambda row: abs(float(row["loss_minus_win_median"])), reverse=True)
    for row in contrast_rows[:25]:
        lines.append(
            f"| {row['lock_name']} | `{row['feature']}` | {row['win_median']:.3f} | "
            f"{row['loss_median']:.3f} | {row['loss_minus_win_median']:.3f} |"
        )
    lines += [
        "",
        "## Top Diagnostic Blockers",
        "",
        "| lock | rule | kept/base | retention | wins/losses | acc | net P&L | delta vs base |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in blockers[:25]:
        lines.append(
            f"| {row['lock_name']} | `{row['rule']}` | {row['kept']}/{row['base']} | "
            f"{pct(row['retention'])} | {row['wins']}/{row['losses']} | {pct(row['accuracy'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_delta_vs_base'])} |"
        )
    lines += ["", "## Read", ""]
    positive = [row for row in blockers if row["net_pnl_cents"] > 0 and (row["retention"] or 0.0) >= 0.8]
    if positive:
        lines.append("- At least one diagnostic blocker is positive while retaining >=80% of that lock's strict registered rows, but sample size is too small and it must be forward-locked before use.")
    else:
        lines.append("- No diagnostic blocker is both positive and >=80% retaining within strict registered kinetic rows.")
    lines.append("- Current strict evidence supports rejection of the existing locks, not promotion.")

    md_latest = OUT_DIR / "profit_lock_strict_failure_attribution_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_strict_failure_attribution_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_strict_failure_attribution_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_strict_failure_attribution_{generated}.json"
    csv_summary = OUT_DIR / "profit_lock_strict_failure_attribution_summary_latest.csv"
    csv_blockers = OUT_DIR / "profit_lock_strict_failure_attribution_blockers_latest.csv"
    for path in [md_latest, md_stamp]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(summaries).to_csv(csv_summary, index=False)
    pd.DataFrame(blockers).to_csv(csv_blockers, index=False)
    payload = {
        "generated_utc": generated,
        "summaries": summaries,
        "contrasts": contrasts,
        "blockers": blockers,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows = combined_resolved()
    summaries = lock_summary(rows) if not rows.empty else []
    contrasts = feature_contrast(rows) if not rows.empty else []
    blockers = diagnostic_blockers(rows) if not rows.empty else []
    write_report(generated, rows, summaries, contrasts, blockers)
    print("Profit lock strict failure attribution complete")
    print(f"resolved_rows={len(rows)} blockers={len(blockers)}")
    print(f"report={OUT_DIR / 'profit_lock_strict_failure_attribution_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
