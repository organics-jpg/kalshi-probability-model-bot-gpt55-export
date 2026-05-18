"""Compare pre-registered signals with recomputed fresh selections.

The recomputed fresh validators rebuild first eligible rows from the latest log
snapshot. If late rows arrive after settlement, recomputation can disagree with
the immutable pre-resolution registry. This audit quantifies those differences
so promotion gates can prefer registered evidence.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from probe_market_interval_80coverage import OUT_DIR, clean_json
from probe_profit_lock_time_boundary import effective_lock_dt


MAIN_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"

LOCK_FILES = {
    "challenger": OUT_DIR / "profit_challenger_fresh_validation_latest.json",
    "touch_hazard": OUT_DIR / "profit_touch_hazard_fresh_validation_latest.json",
    "touch_overlay": OUT_DIR / "profit_touch_hazard_overlay_fresh_validation_latest.json",
    "kinetic_touch": OUT_DIR / "profit_kinetic_touch_fresh_validation_latest.json",
    "hazard_mean_touch80": OUT_DIR / "profit_hazard_mean_touch80_fresh_validation_latest.json",
    "logit_blend_edge10": OUT_DIR / "profit_logit_blend_edge10_fresh_validation_latest.json",
    "logit_blend_thresh55_edge15": OUT_DIR / "profit_logit_blend_thresh55_edge15_fresh_validation_latest.json",
    "hazard_fallback_logit55": OUT_DIR / "profit_hazard_fallback_logit55_fresh_validation_latest.json",
    "hazard_fallback_logit55_wait8": OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_validation_latest.json",
    "hazard_fallback_score60": OUT_DIR / "profit_hazard_fallback_score60_fresh_validation_latest.json",
    "kinetic_guard": OUT_DIR / "profit_kinetic_guard_fresh_validation_latest.json",
    "kinetic_price_guard": OUT_DIR / "profit_kinetic_price_guard_fresh_validation_latest.json",
    "kinetic_combo_price_guard": OUT_DIR / "profit_kinetic_combo_price_guard_fresh_validation_latest.json",
}

SELECTED_FILES = {
    "challenger": OUT_DIR / "profit_challenger_selected_latest.csv",
    "touch_hazard": OUT_DIR / "profit_touch_hazard_selected_latest.csv",
    "touch_overlay": OUT_DIR / "profit_touch_hazard_overlay_selected_latest.csv",
    "kinetic_touch": OUT_DIR / "profit_kinetic_touch_selected_latest.csv",
    "hazard_mean_touch80": OUT_DIR / "profit_hazard_mean_touch80_selected_latest.csv",
    "logit_blend_edge10": OUT_DIR / "profit_logit_blend_edge10_selected_latest.csv",
    "logit_blend_thresh55_edge15": OUT_DIR / "profit_logit_blend_thresh55_edge15_selected_latest.csv",
    "hazard_fallback_logit55": OUT_DIR / "profit_hazard_fallback_logit55_selected_latest.csv",
    "hazard_fallback_logit55_wait8": OUT_DIR / "profit_hazard_fallback_logit55_wait8_selected_latest.csv",
    "hazard_fallback_score60": OUT_DIR / "profit_hazard_fallback_score60_selected_latest.csv",
    "kinetic_guard": OUT_DIR / "profit_kinetic_guard_selected_latest.csv",
    "kinetic_price_guard": OUT_DIR / "profit_kinetic_price_guard_selected_latest.csv",
    "kinetic_combo_price_guard": OUT_DIR / "profit_kinetic_combo_price_guard_selected_latest.csv",
}

COMPARE_COLS = [
    "lock_name",
    "market",
    "registry_entry_dt",
    "selected_entry_dt",
    "registry_side",
    "selected_side",
    "registry_ask",
    "selected_ask",
    "registry_win",
    "selected_win",
    "registry_net",
    "selected_net",
    "entry_dt_diff_sec",
    "ask_diff",
    "net_diff",
    "mismatch_reasons",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def load_lock_boundary(path: Path) -> pd.Timestamp:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return effective_lock_dt(payload.get("lock", {}))


def load_registry() -> pd.DataFrame:
    if not MAIN_REGISTRY.exists():
        return pd.DataFrame()
    rows = pd.read_csv(MAIN_REGISTRY)
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    registered_dt = pd.to_datetime(rows.get("registered_utc"), utc=True, errors="coerce")
    close_dt = pd.to_datetime(rows.get("close_dt"), utc=True, errors="coerce")
    rows = rows[registered_dt.notna() & close_dt.notna() & registered_dt.lt(close_dt)].copy()
    if rows.empty:
        return rows
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value).fillna(False)
    rows["win_bool"] = rows["win"].map(bool_value)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "net_pnl_cents"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def load_selected(lock_name: str) -> pd.DataFrame:
    path = SELECTED_FILES[lock_name]
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    boundary = load_lock_boundary(LOCK_FILES[lock_name])
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows = rows[rows["entry_dt"].gt(boundary)].copy()
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in ["ask_cents", "net_pnl_cents"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows.sort_values(["market", "entry_dt"]).groupby("market", as_index=False, sort=False).first()


def compare_lock(lock_name: str, registry: pd.DataFrame) -> tuple[Dict[str, Any], pd.DataFrame]:
    selected = load_selected(lock_name)
    registered = registry[
        registry["lock_name"].eq(lock_name)
        & registry["outcome_available_bool"]
    ].copy() if not registry.empty else pd.DataFrame()
    registered = registered.sort_values(["market", "entry_dt"]).groupby("market", as_index=False, sort=False).first()

    selected_by_market = {str(row["market"]): row for _, row in selected.iterrows()}
    registered_by_market = {str(row["market"]): row for _, row in registered.iterrows()}
    markets = sorted(set(selected_by_market) | set(registered_by_market))
    diff_rows: list[Dict[str, Any]] = []
    for market in markets:
        reg = registered_by_market.get(market)
        sel = selected_by_market.get(market)
        reasons: list[str] = []
        if reg is None:
            reasons.append("selected_only")
        if sel is None:
            reasons.append("registry_only")
        reg_entry = reg.get("entry_dt") if reg is not None else pd.NaT
        sel_entry = sel.get("entry_dt") if sel is not None else pd.NaT
        entry_diff = None
        if pd.notna(reg_entry) and pd.notna(sel_entry):
            entry_diff = abs((sel_entry - reg_entry).total_seconds())
            if entry_diff > 1.0:
                reasons.append("entry_dt")
        reg_side = str(reg.get("side")) if reg is not None else ""
        sel_side = str(sel.get("side")) if sel is not None else ""
        if reg is not None and sel is not None and reg_side != sel_side:
            reasons.append("side")
        reg_ask = float(reg.get("ask_cents")) if reg is not None and pd.notna(reg.get("ask_cents")) else None
        sel_ask = float(sel.get("ask_cents")) if sel is not None and pd.notna(sel.get("ask_cents")) else None
        ask_diff = None
        if reg_ask is not None and sel_ask is not None:
            ask_diff = sel_ask - reg_ask
            if abs(ask_diff) > 0.001:
                reasons.append("ask")
        reg_win = bool_value(reg.get("win")) if reg is not None else None
        sel_win = bool_value(sel.get("win")) if sel is not None else None
        if reg is not None and sel is not None and reg_win != sel_win:
            reasons.append("win")
        reg_net = float(reg.get("net_pnl_cents")) if reg is not None and pd.notna(reg.get("net_pnl_cents")) else None
        sel_net = float(sel.get("net_pnl_cents")) if sel is not None and pd.notna(sel.get("net_pnl_cents")) else None
        net_diff = None
        if reg_net is not None and sel_net is not None:
            net_diff = sel_net - reg_net
            if abs(net_diff) > 0.001:
                reasons.append("net")
        if reasons:
            diff_rows.append({
                "lock_name": lock_name,
                "market": market,
                "registry_entry_dt": reg_entry,
                "selected_entry_dt": sel_entry,
                "registry_side": reg_side,
                "selected_side": sel_side,
                "registry_ask": reg_ask,
                "selected_ask": sel_ask,
                "registry_win": reg_win,
                "selected_win": sel_win,
                "registry_net": reg_net,
                "selected_net": sel_net,
                "entry_dt_diff_sec": entry_diff,
                "ask_diff": ask_diff,
                "net_diff": net_diff,
                "mismatch_reasons": ",".join(reasons),
            })
    diffs = pd.DataFrame(diff_rows, columns=COMPARE_COLS)
    summary = {
        "lock_name": lock_name,
        "registered_resolved": int(len(registered)),
        "recomputed_selected": int(len(selected)),
        "common_markets": int(len(set(selected_by_market) & set(registered_by_market))),
        "registry_only": int(diffs["mismatch_reasons"].str.contains("registry_only", na=False).sum()) if not diffs.empty else 0,
        "selected_only": int(diffs["mismatch_reasons"].str.contains("selected_only", na=False).sum()) if not diffs.empty else 0,
        "entry_mismatches": int(diffs["mismatch_reasons"].str.contains("entry_dt", na=False).sum()) if not diffs.empty else 0,
        "side_mismatches": int(diffs["mismatch_reasons"].str.contains("side", na=False).sum()) if not diffs.empty else 0,
        "win_mismatches": int(diffs["mismatch_reasons"].str.contains("win", na=False).sum()) if not diffs.empty else 0,
        "net_delta_selected_minus_registry": float(diffs["net_diff"].dropna().sum()) if not diffs.empty else 0.0,
        "mismatch_markets": int(len(diffs)),
    }
    return summary, diffs


def write_report(path: Path, generated: str, summaries: list[Dict[str, Any]], diffs: pd.DataFrame) -> None:
    lines = [
        "# Profit Lock Registry/Recompute Divergence Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Compares pre-registered resolved first signals with recomputed fresh selected rows.",
        "- Any divergence means recomputed fresh metrics are diagnostic, not promotion evidence, for that market.",
        "",
        "## Summary",
        "",
        "| lock | registered | recomputed | common | mismatches | entry | side | win | registry-only | selected-only | net delta sel-reg |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['lock_name']} | {row['registered_resolved']} | {row['recomputed_selected']} | "
            f"{row['common_markets']} | {row['mismatch_markets']} | {row['entry_mismatches']} | "
            f"{row['side_mismatches']} | {row['win_mismatches']} | {row['registry_only']} | "
            f"{row['selected_only']} | {row['net_delta_selected_minus_registry']:.1f}c |"
        )
    lines += ["", "## Material Differences", ""]
    material = diffs[
        diffs["mismatch_reasons"].str.contains("side|win|registry_only|selected_only", na=False)
    ].copy() if not diffs.empty else pd.DataFrame()
    if material.empty:
        lines.append("- No material side/win/coverage divergences found.")
    else:
        for _, row in material.head(30).iterrows():
            lines.append(
                f"- {row['lock_name']} {row['market']}: {row['mismatch_reasons']} "
                f"registry={row['registry_side']} {row['registry_ask']}c win={row['registry_win']} net={row['registry_net']}c; "
                f"recomputed={row['selected_side']} {row['selected_ask']}c win={row['selected_win']} net={row['selected_net']}c."
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registry = load_registry()
    summaries: list[Dict[str, Any]] = []
    diff_frames: list[pd.DataFrame] = []
    for lock_name in SELECTED_FILES:
        summary, diffs = compare_lock(lock_name, registry)
        summaries.append(summary)
        if not diffs.empty:
            diff_frames.append(diffs)
    diff_records: list[Dict[str, Any]] = []
    for frame in diff_frames:
        clean_frame = frame.dropna(how="all")
        if not clean_frame.empty:
            diff_records.extend(clean_frame.to_dict("records"))
    all_diffs = pd.DataFrame(diff_records, columns=COMPARE_COLS)
    md_latest = OUT_DIR / "profit_lock_registry_recompute_divergence_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_registry_recompute_divergence_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_registry_recompute_divergence_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_registry_recompute_divergence_{generated}.json"
    csv_latest = OUT_DIR / "profit_lock_registry_recompute_divergence_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_registry_recompute_divergence_{generated}.csv"
    write_report(md_latest, generated, summaries, all_diffs)
    write_report(md_stamp, generated, summaries, all_diffs)
    all_diffs.to_csv(csv_latest, index=False)
    all_diffs.to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "summaries": summaries,
        "diff_count": int(len(all_diffs)),
        "material_diff_count": int(
            all_diffs["mismatch_reasons"].str.contains("side|win|registry_only|selected_only", na=False).sum()
        ) if not all_diffs.empty else 0,
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock registry/recompute divergence audit complete")
    print(f"diff_count={payload['diff_count']}")
    print(f"material_diff_count={payload['material_diff_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
