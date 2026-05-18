"""Executability audit for session-switch research locks.

Some switch probes choose between an early book anchor and a later reference
row. A backtest is not executable if it waits to observe the later reference
condition and then records the earlier book price. This audit compares the
legacy recomputed selector with an executable selector that can only use
information available by the selected row's timestamp.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, metrics_for
from probe_frontier_candidate_v2_diagnostic import simple_condition_mask
from probe_market_interval_80coverage import OUT_DIR, clean_json, pct, load_side_rows, market_base
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_lock_pending_signal_monitor import (
    BOOK_HOUR04_V2_SWITCH_LOCK_PATH,
    BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH,
    condition_matches,
    first_base_policy_selection,
    select_session_switch_rows,
)


REPORT_MD = OUT_DIR / "session_switch_executability_audit_latest.md"
REPORT_JSON = OUT_DIR / "session_switch_executability_audit_latest.json"
DETAIL_CSV = OUT_DIR / "session_switch_executability_audit_details_latest.csv"

LOCKS = [
    ("book_hour04_v2_switch", BOOK_HOUR04_V2_SWITCH_LOCK_PATH),
    ("book_refmargin_score_switch", BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def entry_hour(row: pd.Series) -> int | None:
    dt = pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce")
    if pd.isna(dt):
        return None
    return int(dt.hour)


def executable_session_switch_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    return select_session_switch_rows(rows, lock)


def legacy_session_switch_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    if rows.empty:
        return rows.iloc[0:0].copy()
    anchor_policy = policy_from_record(lock["anchor_policy"])
    reference_policy = policy_from_record(lock["reference_policy"])
    anchor = first_base_policy_selection(rows, anchor_policy, lock.get("anchor_veto"))
    reference = first_base_policy_selection(rows, reference_policy, lock.get("reference_veto"))
    if anchor.empty and reference.empty:
        return rows.iloc[0:0].copy()

    switch_rule = lock.get("switch_rule", {})
    switch_hours = {int(hour) for hour in switch_rule.get("anchor_entry_hours_utc", [])}
    switch_condition = switch_rule.get("condition")
    condition_source = str(switch_rule.get("condition_source") or "anchor")
    anchor_by_market = {str(row["market"]): row for _, row in anchor.iterrows()}
    reference_by_market = {str(row["market"]): row for _, row in reference.iterrows()}

    selected: List[pd.Series] = []
    for market in sorted(set(anchor_by_market) | set(reference_by_market)):
        anchor_row = anchor_by_market.get(market)
        reference_row = reference_by_market.get(market)
        use_reference = False
        if anchor_row is not None:
            anchor_hour = entry_hour(anchor_row)
            if switch_hours:
                use_reference = anchor_hour in switch_hours and reference_row is not None
            elif switch_condition and reference_row is not None:
                source_row = reference_row if condition_source == "reference" else anchor_row
                use_reference = condition_matches(source_row, switch_condition)
        elif reference_row is not None:
            use_reference = bool(switch_rule.get("use_reference_when_anchor_missing", True))

        if use_reference and reference_row is not None:
            row = reference_row.copy()
            row["chooser"] = reference_policy.chooser
            row["score_value"] = row.get(reference_policy.chooser, np.nan)
            row["overlay"] = switch_rule.get("reference_label", "session_switch:frontier_v2")
            selected.append(row)
        elif anchor_row is not None:
            row = anchor_row.copy()
            row["chooser"] = anchor_policy.chooser
            row["score_value"] = row.get(anchor_policy.chooser, np.nan)
            row["overlay"] = switch_rule.get("anchor_label", "session_switch:book_margin")
            selected.append(row)

    if not selected:
        return rows.iloc[0:0].copy()
    out = pd.DataFrame(selected).drop_duplicates(subset=["market"], keep="first")
    return out.sort_values(["entry_dt", "market"]).reset_index(drop=True)


def metric_row(prefix: str, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = metrics_for(base, enrich_selected(selected))["all"]
    return {
        f"{prefix}_markets": metric["markets"],
        f"{prefix}_base_markets": metric["base_markets"],
        f"{prefix}_coverage": metric["coverage"],
        f"{prefix}_wins": metric["wins"],
        f"{prefix}_losses": metric["losses"],
        f"{prefix}_accuracy": metric["accuracy"],
        f"{prefix}_break_even": metric["fee_aware_break_even_accuracy"],
        f"{prefix}_net_pnl_cents": metric["net_pnl_cents"],
    }


def stale_anchor_details(legacy: pd.DataFrame, executable: pd.DataFrame, rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    anchor_policy = policy_from_record(lock["anchor_policy"])
    reference_policy = policy_from_record(lock["reference_policy"])
    anchor = first_base_policy_selection(rows, anchor_policy, lock.get("anchor_veto"))
    reference = first_base_policy_selection(rows, reference_policy, lock.get("reference_veto"))
    exe_keys = set(zip(executable["market"].astype(str), executable["entry_dt"].astype(str), executable["side"].astype(str))) if not executable.empty else set()
    detail = legacy[["market", "entry_dt", "side", "ask_cents", "overlay", "net_pnl_cents"]].copy()
    detail = detail.merge(anchor[["market", "entry_dt"]], on="market", how="left", suffixes=("", "_anchor"))
    detail = detail.merge(reference[["market", "entry_dt"]], on="market", how="left", suffixes=("", "_reference"))
    detail["entry_dt"] = pd.to_datetime(detail["entry_dt"], utc=True, errors="coerce")
    detail["entry_dt_reference"] = pd.to_datetime(detail["entry_dt_reference"], utc=True, errors="coerce")
    detail["legacy_key"] = list(zip(detail["market"].astype(str), detail["entry_dt"].astype(str), detail["side"].astype(str)))
    detail["executable_match"] = detail["legacy_key"].isin(exe_keys)
    detail["selected_anchor"] = detail["overlay"].astype(str).str.contains("book_margin", na=False)
    detail["reference_after_selected"] = detail["entry_dt_reference"].notna() & detail["entry_dt_reference"].gt(detail["entry_dt"])
    detail["stale_anchor_after_future_reference"] = detail["selected_anchor"] & detail["reference_after_selected"] & ~detail["executable_match"]
    return detail


def run_dataset(dataset: str, side_rows: pd.DataFrame, lock_name: str, path: Path) -> tuple[Dict[str, Any], pd.DataFrame]:
    lock = json.loads(path.read_text(encoding="utf-8"))
    base = market_base(side_rows)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    legacy = enrich_selected(legacy_session_switch_rows(rows, lock))
    executable = enrich_selected(executable_session_switch_rows(rows, lock))
    detail = stale_anchor_details(legacy, executable, rows, lock)
    stale_count = int(detail["stale_anchor_after_future_reference"].sum()) if not detail.empty else 0
    mismatched = int((~detail["executable_match"]).sum()) if not detail.empty else 0
    out = {
        "dataset": dataset,
        "lock": lock_name,
        "switch_label": lock.get("switch_rule", {}).get("label"),
        "condition_source": lock.get("switch_rule", {}).get("condition_source", "anchor_hour"),
        "legacy_not_executable": mismatched,
        "stale_anchor_after_future_reference": stale_count,
        **metric_row("legacy", base, legacy),
        **metric_row("executable", base, executable),
    }
    out["coverage_delta"] = (out["executable_coverage"] or 0.0) - (out["legacy_coverage"] or 0.0)
    out["net_delta_cents"] = (out["executable_net_pnl_cents"] or 0.0) - (out["legacy_net_pnl_cents"] or 0.0)
    detail["dataset"] = dataset
    detail["lock"] = lock_name
    return out, detail


def write_report(generated: str, rows: List[Dict[str, Any]], detail: pd.DataFrame) -> None:
    lines = [
        "# Session Switch Executability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Flags switch rows that require observing a later reference before selecting an earlier anchor price.",
        "- Executable metrics skip those stale-anchor rows or wait for the reference row, depending on the locked rule.",
        "",
        "## Summary",
        "",
        "| dataset | lock | legacy markets/cov/net | executable markets/cov/net | legacy not executable | stale anchor rows | net delta |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | `{row['lock']}` | "
            f"{int(row['legacy_markets'])}/{pct(row['legacy_coverage'])}/{fmt_cents(row['legacy_net_pnl_cents'])} | "
            f"{int(row['executable_markets'])}/{pct(row['executable_coverage'])}/{fmt_cents(row['executable_net_pnl_cents'])} | "
            f"{int(row['legacy_not_executable'])} | {int(row['stale_anchor_after_future_reference'])} | "
            f"{fmt_cents(row['net_delta_cents'])} |"
        )
    invalid = [row for row in rows if int(row["legacy_not_executable"]) > 0]
    lines += ["", "## Read", ""]
    if invalid:
        locks = ", ".join(f"`{row['lock']}`/{row['dataset']}" for row in invalid)
        lines.append(f"- Non-executable legacy rows were found for: {locks}.")
        lines.append("- Session-switch evidence should use the executable selector, not the legacy recomputed selector.")
    else:
        lines.append("- No stale-anchor lookahead was found in the audited session-switch locks.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows: List[Dict[str, Any]] = []
    details: List[pd.DataFrame] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = loader()
        for lock_name, path in LOCKS:
            row, detail = run_dataset(dataset, side_rows, lock_name, path)
            rows.append(row)
            details.append(detail)
    detail_df = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    detail_df.to_csv(DETAIL_CSV, index=False)
    detail_df.to_csv(OUT_DIR / f"session_switch_executability_audit_details_{generated}.csv", index=False)
    write_report(generated, rows, detail_df)
    payload = {"generated_utc": generated, "rows": rows, "detail_csv": str(DETAIL_CSV)}
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamp_json = OUT_DIR / f"session_switch_executability_audit_{generated}.json"
    stamp_json.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamp_md = OUT_DIR / f"session_switch_executability_audit_{generated}.md"
    stamp_md.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("Session switch executability audit complete")
    print(f"rows={len(rows)} non_executable={sum(int(row['legacy_not_executable']) for row in rows)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
