"""Focused registry-vs-recompute audit for key high-coverage policies.

The broad recompute frontier can make policies look excellent after the raw
physics ledger is refreshed, while the immutable pre-resolution registry shows
what would actually have been selected live. This audit focuses on the core
policies that matter for the current goal: book_margin and score_min60.

Research-only: no orders are submitted and no live bot files or processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents
from probe_market_interval_80coverage import (
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
REPORT_MD = OUT_DIR / "key_policy_registry_recompute_audit_latest.md"
REPORT_JSON = OUT_DIR / "key_policy_registry_recompute_audit_latest.json"
CSV_LATEST = OUT_DIR / "key_policy_registry_recompute_audit_latest.csv"

POLICIES = {
    "book_margin": Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0"),
    "score_min60": Policy("score_min_book_rv15", 0.60, 95.0, 120.0, "none"),
    "book_p80_profit_frontier": Policy("book_p_side", 0.80, 95.0, 120.0, "none"),
    "book_p80_ask90_frontier": Policy("book_p_side", 0.80, 90.0, 0.0, "none"),
}


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def load_registry() -> pd.DataFrame:
    if not REGISTRY.exists():
        return pd.DataFrame()
    rows = pd.read_csv(REGISTRY)
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    for col in ["registered_utc", "entry_dt", "close_dt"]:
        rows[col] = pd.to_datetime(rows.get(col), utc=True, errors="coerce")
    rows = rows[rows["registered_utc"].notna() & rows["close_dt"].notna() & rows["registered_utc"].lt(rows["close_dt"])].copy()
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value).fillna(False)
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in ["ask_cents", "net_pnl_cents", "score_value"]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def select_policy(side_rows: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    base = market_base(side_rows)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    selected = enrich_selected(select_markets_from_chosen(chosen, policy))
    selected["policy_label"] = policy.label
    return selected


def registry_for_lock(registry: pd.DataFrame, lock_name: str) -> pd.DataFrame:
    if registry.empty:
        return registry
    rows = registry[registry["lock_name"].eq(lock_name) & registry["outcome_available_bool"]].copy()
    if rows.empty:
        return rows
    return rows.sort_values(["market", "entry_dt"]).groupby("market", as_index=False, sort=False).first()


def summarize_side(side: pd.DataFrame) -> Dict[str, Any]:
    n = int(len(side))
    wins = int(side["win_bool"].sum()) if "win_bool" in side.columns and n else int(side["win"].astype(bool).sum()) if n else 0
    net_col = "net_pnl_cents"
    return {
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "net_pnl_cents": float(pd.to_numeric(side.get(net_col), errors="coerce").sum()) if n else 0.0,
        "median_ask": float(pd.to_numeric(side.get("ask_cents"), errors="coerce").median()) if n else None,
    }


def compare(lock_name: str, registry_rows: pd.DataFrame, recompute_rows: pd.DataFrame) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    reg = registry_for_lock(registry_rows, lock_name)
    rec = recompute_rows.sort_values(["market", "entry_dt"]).groupby("market", as_index=False, sort=False).first()
    reg_by = {str(row["market"]): row for _, row in reg.iterrows()}
    rec_by = {str(row["market"]): row for _, row in rec.iterrows()}
    markets = sorted(set(reg_by) | set(rec_by))
    diffs: List[Dict[str, Any]] = []
    for market in markets:
        r = reg_by.get(market)
        c = rec_by.get(market)
        reasons: List[str] = []
        if r is None:
            reasons.append("recompute_only")
        if c is None:
            reasons.append("registry_only")
        r_entry = r.get("entry_dt") if r is not None else pd.NaT
        c_entry = c.get("entry_dt") if c is not None else pd.NaT
        entry_diff = None
        if pd.notna(r_entry) and pd.notna(c_entry):
            entry_diff = (c_entry - r_entry).total_seconds()
            if abs(entry_diff) > 1.0:
                reasons.append("entry_dt")
        r_side = str(r.get("side")) if r is not None else ""
        c_side = str(c.get("side")) if c is not None else ""
        if r is not None and c is not None and r_side != c_side:
            reasons.append("side")
        r_win = bool_value(r.get("win")) if r is not None else None
        c_win = bool_value(c.get("win")) if c is not None else None
        if r is not None and c is not None and r_win != c_win:
            reasons.append("win")
        r_ask = float(r.get("ask_cents")) if r is not None and pd.notna(r.get("ask_cents")) else None
        c_ask = float(c.get("ask_cents")) if c is not None and pd.notna(c.get("ask_cents")) else None
        if r_ask is not None and c_ask is not None and abs(c_ask - r_ask) > 0.001:
            reasons.append("ask")
        r_net = float(r.get("net_pnl_cents")) if r is not None and pd.notna(r.get("net_pnl_cents")) else None
        c_net = float(c.get("net_pnl_cents")) if c is not None and pd.notna(c.get("net_pnl_cents")) else None
        net_diff = (c_net - r_net) if r_net is not None and c_net is not None else None
        if net_diff is not None and abs(net_diff) > 0.001:
            reasons.append("net")
        if reasons:
            diffs.append(
                {
                    "lock_name": lock_name,
                    "market": market,
                    "registry_entry_dt": r_entry,
                    "recompute_entry_dt": c_entry,
                    "entry_dt_diff_sec": entry_diff,
                    "registry_side": r_side,
                    "recompute_side": c_side,
                    "registry_ask_cents": r_ask,
                    "recompute_ask_cents": c_ask,
                    "registry_win": r_win,
                    "recompute_win": c_win,
                    "registry_net_pnl_cents": r_net,
                    "recompute_net_pnl_cents": c_net,
                    "net_delta_recompute_minus_registry": net_diff,
                    "mismatch_reasons": ",".join(reasons),
                }
            )
    reg_summary = summarize_side(reg)
    rec_summary = summarize_side(rec.rename(columns={"win": "win_bool"}))
    common = [market for market in reg_by if market in rec_by]
    common_reg_net = sum(float(reg_by[m].get("net_pnl_cents") or 0.0) for m in common)
    common_rec_net = sum(float(rec_by[m].get("net_pnl_cents") or 0.0) for m in common)
    summary = {
        "lock_name": lock_name,
        "registry_markets": reg_summary["markets"],
        "registry_wins": reg_summary["wins"],
        "registry_losses": reg_summary["losses"],
        "registry_accuracy": reg_summary["accuracy"],
        "registry_net_pnl_cents": reg_summary["net_pnl_cents"],
        "registry_median_ask": reg_summary["median_ask"],
        "recompute_markets": rec_summary["markets"],
        "recompute_wins": rec_summary["wins"],
        "recompute_losses": rec_summary["losses"],
        "recompute_accuracy": rec_summary["accuracy"],
        "recompute_net_pnl_cents": rec_summary["net_pnl_cents"],
        "recompute_median_ask": rec_summary["median_ask"],
        "common_markets": len(common),
        "common_registry_net_pnl_cents": common_reg_net,
        "common_recompute_net_pnl_cents": common_rec_net,
        "common_net_delta_recompute_minus_registry": common_rec_net - common_reg_net,
        "mismatch_count": len(diffs),
        "entry_mismatches": sum("entry_dt" in row["mismatch_reasons"] for row in diffs),
        "side_mismatches": sum("side" in row["mismatch_reasons"] for row in diffs),
        "win_mismatches": sum("win" in row["mismatch_reasons"] for row in diffs),
        "registry_only": sum("registry_only" in row["mismatch_reasons"] for row in diffs),
        "recompute_only": sum("recompute_only" in row["mismatch_reasons"] for row in diffs),
    }
    return summary, diffs


def pct_local(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def write_report(generated: str, summaries: List[Dict[str, Any]], diffs: pd.DataFrame) -> None:
    lines = [
        "# Key Policy Registry/Recompute Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no live bot files or processes are touched.",
        "- Compares immutable registered rows with recomputed selections from the latest resolved physics ledger.",
        "- Recompute-only improvement is not promotion evidence; it can reflect later candle/physics availability.",
        "",
        "## Summary",
        "",
        "| policy | registry W/L/net | recompute W/L/net | common | common net delta | mismatches | side/win | registry-only/recompute-only |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['lock_name']}` | "
            f"{row['registry_wins']}/{row['registry_losses']}/{fmt_cents(row['registry_net_pnl_cents'])} | "
            f"{row['recompute_wins']}/{row['recompute_losses']}/{fmt_cents(row['recompute_net_pnl_cents'])} | "
            f"{row['common_markets']} | {fmt_cents(row['common_net_delta_recompute_minus_registry'])} | "
            f"{row['mismatch_count']} | {row['side_mismatches']}/{row['win_mismatches']} | "
            f"{row['registry_only']}/{row['recompute_only']} |"
        )
    lines += ["", "## Largest Common Deltas", ""]
    lines += [
        "| policy | market | registry | recompute | side | win | delta | reasons |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    if not diffs.empty:
        focus = diffs[diffs["net_delta_recompute_minus_registry"].notna()].copy()
        focus["abs_delta"] = pd.to_numeric(focus["net_delta_recompute_minus_registry"], errors="coerce").abs()
        for _, row in focus.sort_values("abs_delta", ascending=False).head(30).iterrows():
            lines.append(
                f"| `{row['lock_name']}` | `{row['market']}` | "
                f"{fmt_cents(row['registry_ask_cents'])}/{fmt_cents(row['registry_net_pnl_cents'])} | "
                f"{fmt_cents(row['recompute_ask_cents'])}/{fmt_cents(row['recompute_net_pnl_cents'])} | "
                f"{row['registry_side']}->{row['recompute_side']} | {row['registry_win']}->{row['recompute_win']} | "
                f"{fmt_cents(row['net_delta_recompute_minus_registry'])} | {row['mismatch_reasons']} |"
            )
    lines += ["", "## Read", ""]
    lines.append("- Treat recomputed frontier wins as hypothesis generation unless the same policy has matching pre-resolution registry evidence.")
    lines.append("- Large common-market deltas indicate timing/physics-state availability, not just sample-size noise.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registry = load_registry()
    side_rows = load_side_rows()
    summaries: List[Dict[str, Any]] = []
    all_diffs: List[Dict[str, Any]] = []
    for name, policy in POLICIES.items():
        selected = select_policy(side_rows, policy)
        summary, diffs = compare(name, registry, selected)
        summaries.append(summary)
        all_diffs.extend(diffs)
    diff_frame = pd.DataFrame(all_diffs)
    diff_frame.to_csv(CSV_LATEST, index=False)
    diff_frame.to_csv(OUT_DIR / f"key_policy_registry_recompute_audit_{generated}.csv", index=False)
    write_report(generated, summaries, diff_frame)
    payload = {"generated_utc": generated, "summaries": summaries, "diffs": all_diffs}
    for path in [REPORT_JSON, OUT_DIR / f"key_policy_registry_recompute_audit_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Key policy registry/recompute audit complete")
    print(f"policies={len(summaries)} diffs={len(all_diffs)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
