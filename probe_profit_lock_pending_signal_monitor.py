"""Pre-resolution signal registry for locked BTC 15m profit candidates.

Fresh validation is strongest when the candidate's would-trade decision is
recorded before the market outcome is known. This monitor reads raw live
heartbeat rows, keeps unresolved rows, applies the existing locked EV policies,
and registers the first eligible post-lock signal per market. Later runs update
only the outcome fields; they do not rewrite the original registered signal.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_profit_frontier import estimated_order_fee_cents, fmt_cents
from probe_live_heartbeat_two_side_fv import add_composite_scores, heartbeat_two_side_rows
from probe_live_heartbeat_physics_priors import attach_physics
from probe_live_v28_fv_accuracy_volume import BOT_LOG, parse_bot_log
from shadow_live_v28_physics_validator import closed_market_outcomes_only
from probe_locked_profit_candidate_blocker_overlays import Overlay as BaseOverlay
from probe_locked_profit_candidate_blocker_overlays import overlay_mask as base_overlay_mask
from probe_market_interval_80coverage import (
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    pct,
)
from probe_profit_frontier_fresh_validation import LOCK_PATH as ORIGINAL_LOCK_PATH
from probe_profit_frontier_fresh_validation import policy_from_record as original_policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_profit_challenger_fresh_validation import CHALLENGER_LOCK_PATH, overlay_from_lock
from probe_profit_touch_hazard_fresh_validation import TOUCH_LOCK_PATH, policy_from_record as touch_policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask
from probe_physics_probability_blend_audit import add_blend_scores
from probe_touch_hazard_blocker_overlays import Overlay as TouchOverlay
from probe_touch_hazard_blocker_overlays import overlay_mask as touch_overlay_mask
from probe_touch_hazard_overlay_fresh_validation import TOUCH_OVERLAY_LOCK_PATH, overlay_from_lock as touch_overlay_from_lock
from probe_profit_kinetic_touch_fresh_validation import KINETIC_TOUCH_LOCK_PATH
from probe_kinetic_guard_fresh_validation import KINETIC_GUARD_LOCK_PATH, overlay_from_lock as kinetic_guard_overlay_from_lock
from probe_kinetic_price_guard_fresh_validation import (
    KINETIC_PRICE_GUARD_LOCK_PATH,
    overlay_from_lock as kinetic_price_guard_overlay_from_lock,
)
from probe_kinetic_combo_price_guard_fresh_validation import KINETIC_COMBO_PRICE_GUARD_LOCK_PATH
from probe_kinetic_touch_blocker_overlays import overlay_mask as kinetic_overlay_mask
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_v2_conditional_wait_forward_validation import (
    CONDITIONAL_WAIT_LOCK_PATH,
    ensure_lock as ensure_conditional_wait_lock,
    select_conditional_wait_rows,
)
from probe_v2_rich_conditional_wait_forward_validation import (
    RICH_CONDITIONAL_WAIT_LOCK_PATH,
    ensure_lock as ensure_rich_conditional_wait_lock,
)


FRONTIER_V2_CONTINUOUS_LOCK_PATH = OUT_DIR / "profit_frontier_v2_continuous_lock.json"
BOOK_MARGIN_LOCK_PATH = OUT_DIR / "profit_frontier_book_margin_lock.json"
BOOK_P80_PROFIT_FRONTIER_LOCK_PATH = OUT_DIR / "profit_book_p80_profit_frontier_fresh_lock.json"
BOOK_P80_ASK90_FRONTIER_LOCK_PATH = OUT_DIR / "profit_book_p80_ask90_frontier_fresh_lock.json"
BOOK_MARGIN_EARLY_LOCK_PATH = OUT_DIR / "profit_frontier_book_margin_early_lock.json"
BOOK_MARGIN_GAP015_LOCK_PATH = OUT_DIR / "profit_frontier_book_margin_gap015_lock.json"
BOOK_MARGIN_ADVERSE100_LOCK_PATH = OUT_DIR / "profit_frontier_book_margin_adverse100_lock.json"
BOOK_MARGIN_DELAYED_ADV100_BROWNIAN55_LOCK_PATH = OUT_DIR / "profit_book_margin_delayed_adv100_brownian55_lock.json"
BOOK_HOUR04_V2_SWITCH_LOCK_PATH = OUT_DIR / "profit_book_hour04_v2_switch_lock.json"
BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH = OUT_DIR / "profit_book_refmargin_score_switch_lock.json"
SCORE_MIN60_LOCK_PATH = OUT_DIR / "profit_frontier_score_min60_lock.json"
SCORE_MIN60_GAP020_LOCK_PATH = OUT_DIR / "profit_frontier_score_min60_gap020_lock.json"
BOOK_EARLY_SCORE_GAP020_WAIT_LOCK_PATH = OUT_DIR / "profit_book_early_score_gap020_wait_lock.json"
BOOK_SCORE_GAP020_WAIT_LOCK_PATH = OUT_DIR / "profit_book_score_gap020_wait_lock.json"
HAZARD_MEAN_TOUCH80_LOCK_PATH = OUT_DIR / "profit_hazard_mean_touch80_fresh_lock.json"
HAZARD_MEAN_TOUCH80_ASK76_LOCK_PATH = OUT_DIR / "profit_hazard_mean_touch80_ask76_fresh_lock.json"
LOGIT_BLEND_EDGE10_LOCK_PATH = OUT_DIR / "profit_logit_blend_edge10_fresh_lock.json"
LOGIT_BLEND_THRESH55_EDGE15_LOCK_PATH = OUT_DIR / "profit_logit_blend_thresh55_edge15_fresh_lock.json"
HAZARD_FALLBACK_LOGIT55_LOCK_PATH = OUT_DIR / "profit_hazard_fallback_logit55_fresh_lock.json"
HAZARD_FALLBACK_LOGIT55_WAIT8_LOCK_PATH = OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_lock.json"
HAZARD_FALLBACK_SCORE60_LOCK_PATH = OUT_DIR / "profit_hazard_fallback_score60_fresh_lock.json"
IMPULSE_REVERSAL_FADE_LOCK_PATH = OUT_DIR / "profit_impulse_reversal_book_margin_fade_fresh_lock.json"
REGISTRY_PATH = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
REPORT_LATEST = OUT_DIR / "profit_lock_pending_signal_monitor_latest.md"
JSON_LATEST = OUT_DIR / "profit_lock_pending_signal_monitor_latest.json"


LOCK_SPECS = [
    ("original", ORIGINAL_LOCK_PATH, "base"),
    ("frontier_v2", FRONTIER_V2_LOCK_PATH, "base"),
    ("frontier_v2_continuous", FRONTIER_V2_CONTINUOUS_LOCK_PATH, "base"),
    ("book_margin", BOOK_MARGIN_LOCK_PATH, "base"),
    ("book_p80_profit_frontier", BOOK_P80_PROFIT_FRONTIER_LOCK_PATH, "base"),
    ("book_p80_ask90_frontier", BOOK_P80_ASK90_FRONTIER_LOCK_PATH, "base"),
    ("book_margin_early", BOOK_MARGIN_EARLY_LOCK_PATH, "base"),
    ("book_margin_gap015", BOOK_MARGIN_GAP015_LOCK_PATH, "base_veto"),
    ("book_margin_adverse100", BOOK_MARGIN_ADVERSE100_LOCK_PATH, "base_veto"),
    ("book_margin_delayed_adv100_brownian55", BOOK_MARGIN_DELAYED_ADV100_BROWNIAN55_LOCK_PATH, "delayed_base"),
    ("book_hour04_v2_switch", BOOK_HOUR04_V2_SWITCH_LOCK_PATH, "session_switch"),
    ("book_refmargin_score_switch", BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH, "session_switch"),
    ("score_min60", SCORE_MIN60_LOCK_PATH, "base"),
    ("score_min60_gap020", SCORE_MIN60_GAP020_LOCK_PATH, "base_veto"),
    ("book_early_score_gap020_wait", BOOK_EARLY_SCORE_GAP020_WAIT_LOCK_PATH, "book_to_score_wait"),
    ("book_score_gap020_wait", BOOK_SCORE_GAP020_WAIT_LOCK_PATH, "book_to_score_wait"),
    ("v2_wait_score_min60_early", CONDITIONAL_WAIT_LOCK_PATH, "conditional_wait"),
    ("v2_wait_score_min60_brownian70_early", RICH_CONDITIONAL_WAIT_LOCK_PATH, "rich_conditional_wait"),
    ("challenger", CHALLENGER_LOCK_PATH, "base"),
    ("touch_hazard", TOUCH_LOCK_PATH, "touch_hazard"),
    ("touch_overlay", TOUCH_OVERLAY_LOCK_PATH, "touch_overlay"),
    ("kinetic_touch", KINETIC_TOUCH_LOCK_PATH, "touch_hazard"),
    ("hazard_mean_touch80", HAZARD_MEAN_TOUCH80_LOCK_PATH, "touch_hazard"),
    ("hazard_mean_touch80_ask76", HAZARD_MEAN_TOUCH80_ASK76_LOCK_PATH, "touch_hazard"),
    ("logit_blend_edge10", LOGIT_BLEND_EDGE10_LOCK_PATH, "blend_edge"),
    ("logit_blend_thresh55_edge15", LOGIT_BLEND_THRESH55_EDGE15_LOCK_PATH, "blend_edge"),
    ("hazard_fallback_logit55", HAZARD_FALLBACK_LOGIT55_LOCK_PATH, "hazard_fallback"),
    ("hazard_fallback_logit55_wait8", HAZARD_FALLBACK_LOGIT55_WAIT8_LOCK_PATH, "hazard_fallback"),
    ("hazard_fallback_score60", HAZARD_FALLBACK_SCORE60_LOCK_PATH, "hazard_fallback"),
    ("impulse_reversal_book_margin_fade", IMPULSE_REVERSAL_FADE_LOCK_PATH, "impulse_fade"),
    ("kinetic_guard", KINETIC_GUARD_LOCK_PATH, "kinetic_guard"),
    ("kinetic_price_guard", KINETIC_PRICE_GUARD_LOCK_PATH, "kinetic_price_guard"),
    ("kinetic_combo_price_guard", KINETIC_COMBO_PRICE_GUARD_LOCK_PATH, "kinetic_price_guard"),
]


SIGNAL_COLS = [
    "lock_name",
    "market",
    "registered_utc",
    "lock_close_dt",
    "entry_dt",
    "close_dt",
    "side",
    "ask_cents",
    "bid_cents",
    "seconds_to_close",
    "source_line_no",
    "decision_key",
    "chooser",
    "score_value",
    "overlay",
    "book_p_side",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "margin_dollars",
    "margin_per_rv_sigma_15m",
    "signed_move_3m",
    "signed_move_5m",
    "signed_move_15m",
    "signed_move_30m",
    "impulse_3_5m",
    "impulse_3_5m_over_margin",
    "fade_trigger_side",
    "fade_trigger_ask_cents",
    "fade_trigger_score_value",
    "fade_trigger_margin_dollars",
    "fade_trigger_signed_move_3m",
    "fade_trigger_signed_move_5m",
    "fade_trigger_impulse_3_5m",
    "fade_trigger_impulse_3_5m_over_margin",
    "abs_book_rv15_gap",
    "adverse_move_15m",
    "touch_loss_rv_15m",
    "touch_survival_rv_15m",
    "book_touch_blend_15",
    "hazard_discounted_mean_15",
    "kinetic_touch_score_15",
    "blend_logit_book_rv_hazard_mean",
    "fair_edge_cents",
    "outcome_available",
    "outcome",
    "win",
    "entry_fee_cents",
    "net_pnl_cents",
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
    return str(value).lower() in {"true", "1", "yes"}


def simple_condition_mask(rows: pd.DataFrame, condition: Dict[str, Any]) -> pd.Series:
    values = pd.to_numeric(rows.get(condition["feature"]), errors="coerce")
    threshold = float(condition["threshold"])
    if condition["op"] == "<=":
        return values.le(threshold).fillna(False)
    if condition["op"] == ">=":
        return values.ge(threshold).fillna(False)
    raise ValueError(f"unknown condition op: {condition['op']}")


def base_policy_eligible_rows(rows: pd.DataFrame, policy: Policy, veto: Dict[str, Any] | None = None) -> pd.DataFrame:
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen
    selected_rows = chosen[gate_mask(chosen, policy)].copy()
    if selected_rows.empty:
        return selected_rows
    if veto:
        selected_rows = selected_rows[simple_condition_mask(selected_rows, veto)].copy()
        if selected_rows.empty:
            return selected_rows
    selected_rows["chooser"] = policy.chooser
    selected_rows["score_value"] = selected_rows[policy.chooser] if policy.chooser in selected_rows.columns else np.nan
    return selected_rows.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def first_base_policy_selection(rows: pd.DataFrame, policy: Policy, veto: Dict[str, Any] | None = None) -> pd.DataFrame:
    selected_rows = base_policy_eligible_rows(rows, policy, veto)
    if selected_rows.empty:
        return selected_rows
    selected = (
        selected_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return selected


def condition_matches(row: pd.Series, condition: Dict[str, Any]) -> bool:
    value = pd.to_numeric(pd.Series([row.get(condition["feature"])]), errors="coerce").iloc[0]
    if pd.isna(value):
        return False
    threshold = float(condition["threshold"])
    if condition["op"] == "<=":
        return bool(value <= threshold)
    if condition["op"] == ">=":
        return bool(value >= threshold)
    raise ValueError(f"unknown condition op: {condition['op']}")


def all_conditions_mask(rows: pd.DataFrame, conditions: List[Dict[str, Any]]) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    for condition in conditions:
        mask &= simple_condition_mask(rows, condition)
    return mask.fillna(False)


def select_book_to_score_wait_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    if rows.empty:
        return rows.iloc[0:0].copy()
    anchor_policy = original_policy_from_record(lock["anchor_policy"])
    reference_policy = original_policy_from_record(lock["reference_policy"])
    anchor = first_base_policy_selection(rows, anchor_policy, lock.get("anchor_veto"))
    reference = first_base_policy_selection(rows, reference_policy, lock.get("reference_veto"))
    if anchor.empty:
        return anchor
    if not reference.empty:
        reference["entry_dt"] = pd.to_datetime(reference["entry_dt"], utc=True, errors="coerce")
    reference_by_market = {
        str(market): part.sort_values(["entry_dt", "market"]).copy()
        for market, part in reference.groupby("market", sort=False)
    } if not reference.empty else {}
    rule = lock["wait_rule"]
    condition = rule.get("condition") or {}
    mode = str(rule.get("mode") or "enter_ref")
    selected: List[pd.Series] = []
    for _, row in anchor.sort_values(["entry_dt", "market"]).iterrows():
        if not condition_matches(row, condition):
            out = row.copy()
            out["conditional_source"] = "book_anchor_immediate"
            selected.append(out)
            continue
        candidates = reference_by_market.get(str(row["market"]))
        if candidates is None or candidates.empty:
            continue
        row_dt = pd.to_datetime(row["entry_dt"], utc=True, errors="coerce")
        if pd.isna(row_dt):
            continue
        later = candidates[pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce").ge(row_dt)]
        if later.empty:
            continue
        out = later.iloc[0].copy()
        if mode == "switch_only" and str(out.get("side")) == str(row.get("side")):
            continue
        out["conditional_source"] = "score_gap020_after_early_book"
        out["conditional_trigger_dt"] = row_dt.isoformat()
        selected.append(out)
    if not selected:
        return anchor.iloc[0:0].copy()
    out = pd.DataFrame(selected).drop_duplicates(subset=["market"], keep="first")
    return out.sort_values(["entry_dt", "market"]).reset_index(drop=True)


def _entry_hour_utc(row: pd.Series) -> int | None:
    entry = pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce")
    if pd.isna(entry):
        return None
    return int(entry.hour)


def select_session_switch_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    if rows.empty:
        return rows.iloc[0:0].copy()
    anchor_policy = original_policy_from_record(lock["anchor_policy"])
    reference_policy = original_policy_from_record(lock["reference_policy"])
    anchor_candidates = base_policy_eligible_rows(rows, anchor_policy, lock.get("anchor_veto"))
    reference_candidates = base_policy_eligible_rows(rows, reference_policy, lock.get("reference_veto"))
    anchor = first_base_policy_selection(rows, anchor_policy, lock.get("anchor_veto"))
    reference = first_base_policy_selection(rows, reference_policy, lock.get("reference_veto"))
    if anchor.empty and reference.empty:
        return rows.iloc[0:0].copy()

    switch_rule = lock.get("switch_rule", {})
    switch_hours = {int(hour) for hour in switch_rule.get("anchor_entry_hours_utc", [])}
    switch_condition = switch_rule.get("condition")
    condition_source = str(switch_rule.get("condition_source") or "anchor")
    use_ref_when_anchor_missing = bool(switch_rule.get("use_reference_when_anchor_missing", True))
    false_reference_fallback = str(switch_rule.get("condition_false_anchor_fallback") or "")
    anchor_by_market = {str(row["market"]): row for _, row in anchor.iterrows()}
    reference_by_market = {str(row["market"]): row for _, row in reference.iterrows()}
    anchor_candidates_by_market = {
        str(market): part.sort_values(["entry_dt", "market"]).copy()
        for market, part in anchor_candidates.groupby("market", sort=False)
    } if not anchor_candidates.empty else {}

    selected: List[pd.Series] = []

    def append_selected(row: pd.Series, policy: Policy, overlay_label: str) -> None:
        out = row.copy()
        out["chooser"] = policy.chooser
        out["score_value"] = out.get(policy.chooser, np.nan)
        out["overlay"] = overlay_label
        selected.append(out)

    for market in sorted(set(anchor_by_market) | set(reference_by_market)):
        anchor_row = anchor_by_market.get(market)
        reference_row = reference_by_market.get(market)
        anchor_label = switch_rule.get("anchor_label", "session_switch:book_margin")
        reference_label = switch_rule.get("reference_label", "session_switch:frontier_v2")

        if anchor_row is None:
            if reference_row is None or not use_ref_when_anchor_missing:
                continue
            if switch_condition and condition_source == "reference" and not condition_matches(reference_row, switch_condition):
                continue
            append_selected(reference_row, reference_policy, reference_label)
            continue

        if switch_hours:
            trigger = _entry_hour_utc(anchor_row) in switch_hours
            if trigger:
                if reference_row is not None:
                    append_selected(reference_row, reference_policy, reference_label)
                continue
            append_selected(anchor_row, anchor_policy, anchor_label)
            continue

        if switch_condition:
            if condition_source == "anchor":
                trigger = condition_matches(anchor_row, switch_condition)
                if trigger:
                    if reference_row is not None:
                        append_selected(reference_row, reference_policy, reference_label)
                    continue
                append_selected(anchor_row, anchor_policy, anchor_label)
                continue
            if condition_source == "reference":
                if reference_row is None:
                    continue
                trigger = condition_matches(reference_row, switch_condition)
                if trigger:
                    append_selected(reference_row, reference_policy, reference_label)
                    continue
                reference_dt = pd.to_datetime(reference_row.get("entry_dt"), utc=True, errors="coerce")
                anchor_dt = pd.to_datetime(anchor_row.get("entry_dt"), utc=True, errors="coerce")
                if pd.isna(reference_dt) or pd.isna(anchor_dt):
                    continue
                if reference_dt > anchor_dt:
                    if false_reference_fallback != "first_anchor_at_or_after_reference":
                        continue
                    candidates = anchor_candidates_by_market.get(market)
                    if candidates is None or candidates.empty:
                        continue
                    candidate_dt = pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce")
                    delayed_anchor = candidates[candidate_dt.ge(reference_dt)]
                    if delayed_anchor.empty:
                        continue
                    fallback_label = switch_rule.get("condition_false_anchor_label", anchor_label)
                    append_selected(delayed_anchor.iloc[0], anchor_policy, fallback_label)
                    continue
                append_selected(anchor_row, anchor_policy, anchor_label)
                continue
            raise ValueError(f"unknown session switch condition_source: {condition_source}")

        append_selected(anchor_row, anchor_policy, anchor_label)

    if not selected:
        return rows.iloc[0:0].copy()
    out = pd.DataFrame(selected).drop_duplicates(subset=["market"], keep="first")
    return out.sort_values(["entry_dt", "market"]).reset_index(drop=True)


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        return pd.DataFrame(columns=SIGNAL_COLS)
    df = pd.read_csv(REGISTRY_PATH)
    for col in SIGNAL_COLS:
        if col not in df.columns:
            df[col] = np.nan
    return df[SIGNAL_COLS].copy()


def load_lock(name: str, path: Path, kind: str) -> Dict[str, Any]:
    if kind == "conditional_wait" and not path.exists():
        ensure_conditional_wait_lock()
    if kind == "rich_conditional_wait" and not path.exists():
        ensure_rich_conditional_wait_lock()
    if not path.exists():
        raise SystemExit(f"Missing {name} lock: {path}")
    lock = json.loads(path.read_text(encoding="utf-8"))
    if kind == "book_to_score_wait":
        policy = original_policy_from_record(lock["anchor_policy"])
    elif kind == "session_switch":
        policy = original_policy_from_record(lock["anchor_policy"])
    elif kind == "delayed_base":
        policy = original_policy_from_record(lock["policy"])
    elif kind in {"conditional_wait", "rich_conditional_wait"}:
        policy = original_policy_from_record(lock["v2_policy"])
    elif kind == "blend_edge":
        record = lock["policy"]
        policy = Policy(
            record["chooser"],
            float(record.get("min_score", 0.0)),
            float(record.get("ask_max", 95.0)),
            float(record.get("min_seconds_to_close", 60.0)),
            str(record.get("gate", "none")),
        )
    elif kind == "hazard_fallback":
        policy = touch_policy_from_record(lock["primary_policy"])
    elif kind == "impulse_fade":
        policy = original_policy_from_record(lock["base_policy"])
    else:
        policy = touch_policy_from_record(lock["policy"]) if kind.startswith("touch") or kind.startswith("kinetic") else original_policy_from_record(lock["policy"])
    overlay: Any = BaseOverlay("none", ("none",))
    if kind == "touch_overlay":
        overlay = touch_overlay_from_lock(lock)
    elif kind == "kinetic_guard":
        overlay = kinetic_guard_overlay_from_lock(lock)
    elif kind == "kinetic_price_guard":
        overlay = kinetic_price_guard_overlay_from_lock(lock)
    elif kind != "touch_hazard" and "overlay" in lock:
        overlay = overlay_from_lock(lock)
    return {
        "name": name,
        "kind": kind,
        "path": str(path),
        "lock": lock,
        "policy": policy,
        "overlay": overlay,
        "lock_close_dt": effective_lock_dt(lock),
    }


def filter_registry_to_effective_locks(registry: pd.DataFrame, specs: List[Dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    effective_by_name = {str(spec["name"]): spec["lock_close_dt"] for spec in specs}
    out = registry.copy()
    out["entry_dt_tmp"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    keep = []
    for _, row in out.iterrows():
        boundary = effective_by_name.get(str(row["lock_name"]))
        if boundary is None or pd.isna(boundary):
            keep.append(True)
        else:
            keep.append(bool(row["entry_dt_tmp"] > boundary))
    out = out.loc[keep].drop(columns=["entry_dt_tmp"])
    return out.reindex(columns=SIGNAL_COLS)


def filter_registry_to_pre_resolution(registry: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if registry.empty:
        return registry, 0
    out = registry.copy()
    registered_dt = pd.to_datetime(out["registered_utc"], utc=True, errors="coerce")
    close_dt = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    keep = registered_dt.notna() & close_dt.notna() & registered_dt.lt(close_dt)
    removed = int((~keep).sum())
    return out.loc[keep].reindex(columns=SIGNAL_COLS), removed


def raw_side_rows(*, fetch_btc_candles: bool = False) -> pd.DataFrame:
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    raw = heartbeat_two_side_rows(markets, outcomes)
    if raw.empty:
        return raw
    physics, _ = attach_physics(raw, fetch_btc_candles=fetch_btc_candles)
    if physics.empty:
        return physics
    physics = add_composite_scores(physics)
    if "book_p_side" in physics.columns and "brownian_p_rv_15m" in physics.columns:
        physics["abs_book_rv15_gap"] = (physics["book_p_side"] - physics["brownian_p_rv_15m"]).abs()
    physics = add_blend_scores(physics)
    physics["entry_dt"] = pd.to_datetime(physics["entry_dt"], utc=True, errors="coerce")
    physics["seconds_to_close"] = pd.to_numeric(physics["seconds_to_close"], errors="coerce")
    physics["close_dt"] = physics["entry_dt"] + pd.to_timedelta(physics["seconds_to_close"], unit="s")
    for col in [
        "ask_cents",
        "bid_cents",
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "margin_per_rv_sigma_15m",
        "margin_dollars",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_10m",
        "signed_move_15m",
        "signed_move_30m",
        "abs_book_rv15_gap",
        "adverse_move_15m",
        "hazard_discounted_mean_15",
        "blend_logit_book_rv_hazard_mean",
        "source_line_no",
    ]:
        if col in physics.columns:
            physics[col] = pd.to_numeric(physics[col], errors="coerce")
    return physics.sort_values(["entry_dt", "decision_key", "side"]).reset_index(drop=True)


def add_impulse_fields(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    for col in [
        "margin_dollars",
        "margin_per_rv_sigma_15m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_10m",
        "signed_move_15m",
        "signed_move_30m",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["abs_margin_dollars"] = out["margin_dollars"].abs()
    out["impulse_3_5m"] = out[["signed_move_3m", "signed_move_5m"]].max(axis=1)
    out["signed_move_5m_over_margin"] = out["signed_move_5m"] - out["abs_margin_dollars"]
    out["impulse_3_5m_over_margin"] = out["impulse_3_5m"] - out["abs_margin_dollars"]
    return out


def impulse_overreaction_mask(rows: pd.DataFrame, rule: Dict[str, Any], chooser: str) -> pd.Series:
    impulse_col = str(rule.get("impulse_col", "impulse_3_5m"))
    over_col = f"{impulse_col}_over_margin"
    impulse = pd.to_numeric(rows.get(impulse_col), errors="coerce")
    over_margin = pd.to_numeric(rows.get(over_col), errors="coerce")
    margin_sigma = pd.to_numeric(rows.get("margin_per_rv_sigma_15m"), errors="coerce")
    seconds = pd.to_numeric(rows.get("seconds_to_close"), errors="coerce")
    score = pd.to_numeric(rows.get(chooser), errors="coerce")
    return (
        impulse.ge(float(rule.get("impulse_abs_min", 60.0)))
        & over_margin.ge(float(rule.get("over_margin_min", 20.0)))
        & seconds.ge(float(rule.get("min_seconds_to_close", 600.0)))
        & margin_sigma.le(float(rule.get("max_margin_sigma", 0.75)))
        & score.le(float(rule.get("max_chosen_score", 0.82)))
    ).fillna(False)


def opposite_side_rows(rows: pd.DataFrame, triggers: pd.DataFrame, max_fade_ask: float) -> pd.DataFrame:
    if rows.empty or triggers.empty:
        return rows.iloc[0:0].copy()
    key_cols = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in rows.columns]
    trigger_cols = [
        col
        for col in [
            "side",
            "ask_cents",
            "fade_trigger_score_value",
            "margin_dollars",
            "signed_move_3m",
            "signed_move_5m",
            "impulse_3_5m",
            "impulse_3_5m_over_margin",
        ]
        if col in triggers.columns
    ]
    trigger = triggers[key_cols + trigger_cols].rename(
        columns={
            "side": "trigger_side",
            "ask_cents": "fade_trigger_ask_cents",
            "margin_dollars": "fade_trigger_margin_dollars",
            "signed_move_3m": "fade_trigger_signed_move_3m",
            "signed_move_5m": "fade_trigger_signed_move_5m",
            "impulse_3_5m": "fade_trigger_impulse_3_5m",
            "impulse_3_5m_over_margin": "fade_trigger_impulse_3_5m_over_margin",
        }
    ).copy()
    faded = rows.merge(trigger, on=key_cols, how="inner")
    faded = faded[faded["side"].astype(str).ne(faded["trigger_side"].astype(str))].copy()
    if faded.empty:
        return faded
    faded["fade_trigger_side"] = faded["trigger_side"]
    faded = faded[pd.to_numeric(faded["ask_cents"], errors="coerce").le(float(max_fade_ask))].copy()
    return faded.drop(columns=["trigger_side"], errors="ignore")


def select_impulse_fade_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = add_impulse_fields(rows)
    base_policy = original_policy_from_record(lock["base_policy"])
    chosen = choose_decision_sides(rows, base_policy.chooser)
    if chosen.empty:
        return chosen
    base_rows = chosen[gate_mask(chosen, base_policy)].copy()
    if base_rows.empty:
        return base_rows

    rule = lock.get("impulse_rule", {})
    fade_rule = lock.get("fade_rule", {})
    reaction = impulse_overreaction_mask(base_rows, rule, base_policy.chooser)
    normal = base_rows[~reaction].copy()
    if not normal.empty:
        normal["overlay"] = fade_rule.get("base_label", "base")

    triggers = base_rows[reaction].copy()
    if not triggers.empty:
        triggers["fade_trigger_score_value"] = (
            triggers[base_policy.chooser] if base_policy.chooser in triggers.columns else np.nan
        )
    faded = opposite_side_rows(rows, triggers, float(fade_rule.get("max_fade_ask", 45.0)))
    if not faded.empty:
        faded["overlay"] = fade_rule.get("label", "fade_impulse")

    selected_rows = pd.concat([normal, faded], ignore_index=True, sort=False)
    if selected_rows.empty:
        return selected_rows
    selected = (
        selected_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["chooser"] = base_policy.chooser
    selected["score_value"] = selected[base_policy.chooser] if base_policy.chooser in selected.columns else np.nan
    return selected


def select_signals(rows: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    lock_close_dt = spec["lock_close_dt"]
    if rows.empty or pd.isna(lock_close_dt):
        return rows.iloc[0:0].copy()
    policy = spec["policy"]
    overlay = spec["overlay"]
    eligible_rows = rows[
        rows["entry_dt"].gt(lock_close_dt)
        & rows["close_dt"].gt(lock_close_dt)
        & rows["seconds_to_close"].gt(0)
    ].copy()
    if eligible_rows.empty:
        return eligible_rows
    if spec["kind"] in {"conditional_wait", "rich_conditional_wait"}:
        selected = select_conditional_wait_rows(eligible_rows, spec["lock"])
        if selected.empty:
            return selected
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        selected["overlay"] = spec["lock"].get("wait_rule", {}).get("label", "conditional_wait")
        return selected
    if spec["kind"] == "book_to_score_wait":
        selected = select_book_to_score_wait_rows(eligible_rows, spec["lock"])
        if selected.empty:
            return selected
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        selected["overlay"] = spec["lock"].get("wait_rule", {}).get("label", "book_to_score_wait")
        return selected
    if spec["kind"] == "session_switch":
        selected = select_session_switch_rows(eligible_rows, spec["lock"])
        if selected.empty:
            return selected
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        if "overlay" not in selected.columns:
            selected["overlay"] = spec["lock"].get("switch_rule", {}).get("label", "session_switch")
        return selected
    if spec["kind"] == "impulse_fade":
        selected = select_impulse_fade_rows(eligible_rows, spec["lock"])
        if selected.empty:
            return selected
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        return selected
    if spec["kind"] == "hazard_fallback":
        primary_policy: HazardPolicy = policy
        primary_chosen = choose_decision_sides(eligible_rows, primary_policy.chooser)
        if primary_chosen.empty:
            primary_selected = primary_chosen.copy()
        else:
            primary_selected = primary_chosen[touch_gate_mask(primary_chosen, primary_policy)].copy()
        if not primary_selected.empty:
            primary_selected = (
                primary_selected.sort_values(["market", "entry_dt"])
                .groupby("market", as_index=False, sort=False)
                .first()
                .sort_values(["entry_dt", "market"])
                .reset_index(drop=True)
            )
            primary_selected["chooser"] = primary_policy.chooser
            primary_selected["score_value"] = primary_selected[primary_policy.chooser]
            primary_selected["overlay"] = spec["lock"]["primary_policy"].get("label", "hazard_primary")

        fallback = spec["lock"]["fallback_policy"]
        fallback_chooser = str(fallback["chooser"])
        fallback_chosen = choose_decision_sides(eligible_rows, fallback_chooser)
        if fallback_chosen.empty:
            fallback_selected = fallback_chosen.copy()
        else:
            scores = pd.to_numeric(fallback_chosen[fallback_chooser], errors="coerce")
            asks = pd.to_numeric(fallback_chosen["ask_cents"], errors="coerce")
            fees = pd.Series(
                [estimated_order_fee_cents(ask, 1) for ask in asks.fillna(100.0)],
                index=fallback_chosen.index,
                dtype=float,
            )
            fair_edge = 100.0 * scores - asks - fees
            fallback_selected = fallback_chosen[
                scores.ge(float(fallback.get("min_score", 0.0)))
                & asks.le(float(fallback.get("ask_max", 95.0)))
                & pd.to_numeric(fallback_chosen["seconds_to_close"], errors="coerce").ge(
                    float(fallback.get("min_seconds_to_close", 60.0))
                )
                & fair_edge.ge(float(fallback.get("edge_floor_cents", -100.0)))
            ].copy()
            if fallback.get("max_seconds_to_close") is not None and not fallback_selected.empty:
                fallback_selected = fallback_selected[
                    pd.to_numeric(fallback_selected["seconds_to_close"], errors="coerce").le(
                        float(fallback["max_seconds_to_close"])
                    )
                ].copy()
            if not fallback_selected.empty:
                fallback_selected["fair_edge_cents"] = fair_edge.loc[fallback_selected.index]
                fallback_selected = (
                    fallback_selected.sort_values(["market", "entry_dt"])
                    .groupby("market", as_index=False, sort=False)
                    .first()
                    .sort_values(["entry_dt", "market"])
                    .reset_index(drop=True)
                )
                fallback_selected["chooser"] = fallback_chooser
                fallback_selected["score_value"] = fallback_selected[fallback_chooser]
                fallback_selected["overlay"] = fallback.get("label", "fallback")

        frames: List[pd.DataFrame] = []
        if not primary_selected.empty:
            primary_selected = primary_selected.copy()
            primary_selected["selector_priority"] = 0
            frames.append(primary_selected)
        if not fallback_selected.empty:
            fallback_selected = fallback_selected.copy()
            fallback_selected["selector_priority"] = 1
            frames.append(fallback_selected)
        selected = pd.concat(frames, ignore_index=True, sort=False) if frames else eligible_rows.iloc[0:0].copy()
        if selected.empty:
            return selected
        selected["entry_dt"] = pd.to_datetime(selected["entry_dt"], utc=True, errors="coerce")
        selected = (
            selected.sort_values(["market", "entry_dt", "selector_priority"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
            .drop(columns=["selector_priority"], errors="ignore")
        )
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        return selected
    chosen = choose_decision_sides(eligible_rows, policy.chooser)
    if chosen.empty:
        return chosen
    if spec["kind"] == "delayed_base":
        base_policy: Policy = policy
        conditions = list(spec["lock"].get("delay_conditions") or [])
        selected_rows = chosen[
            gate_mask(chosen, base_policy)
            & base_overlay_mask(chosen, overlay)
            & all_conditions_mask(chosen, conditions)
        ].copy()
        if selected_rows.empty:
            return selected_rows
        selected = (
            selected_rows.sort_values(["market", "entry_dt"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
        )
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        selected["chooser"] = policy.chooser
        selected["score_value"] = selected[policy.chooser] if policy.chooser in selected.columns else np.nan
        selected["overlay"] = spec["lock"].get("delay_rule", {}).get("label", "delayed_base")
        return selected
    if spec["kind"] == "base_veto":
        base_policy: Policy = policy
        selected_rows = chosen[gate_mask(chosen, base_policy) & base_overlay_mask(chosen, overlay)].copy()
        if selected_rows.empty:
            return selected_rows
        selected = (
            selected_rows.sort_values(["market", "entry_dt"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
        )
        veto = spec["lock"].get("veto")
        if veto:
            selected = selected[simple_condition_mask(selected, veto)].copy()
        if selected.empty:
            return selected
        selected["lock_name"] = spec["name"]
        selected["lock_close_dt"] = lock_close_dt
        selected["chooser"] = policy.chooser
        selected["score_value"] = selected[policy.chooser] if policy.chooser in selected.columns else np.nan
        selected["overlay"] = spec["lock"].get("policy", {}).get("label", "base_veto")
        return selected
    if spec["kind"] == "blend_edge":
        scores = pd.to_numeric(chosen[policy.chooser], errors="coerce")
        asks = pd.to_numeric(chosen["ask_cents"], errors="coerce")
        fees = pd.Series(
            [estimated_order_fee_cents(ask, 1) for ask in asks.fillna(100.0)],
            index=chosen.index,
            dtype=float,
        )
        fair_edge = 100.0 * scores - asks - fees
        selected_rows = chosen[
            scores.notna()
            & scores.ge(float(spec["lock"]["policy"].get("min_score", 0.0)))
            & asks.le(float(spec["lock"]["policy"].get("ask_max", 95.0)))
            & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(
                float(spec["lock"]["policy"].get("min_seconds_to_close", 60.0))
            )
            & fair_edge.ge(float(spec["lock"]["edge_rule"]["edge_floor_cents"]))
        ].copy()
        if not selected_rows.empty:
            selected_rows["fair_edge_cents"] = fair_edge.loc[selected_rows.index]
    elif spec["kind"] == "touch_hazard":
        touch_policy: HazardPolicy = policy
        selected_rows = chosen[touch_gate_mask(chosen, touch_policy)].copy()
    elif spec["kind"] == "touch_overlay":
        touch_policy = policy
        touch_gate = touch_gate_mask(chosen, touch_policy)
        selected_rows = chosen[touch_gate & touch_overlay_mask(chosen, overlay)].copy()
    elif spec["kind"] == "kinetic_guard":
        touch_policy = policy
        touch_gate = touch_gate_mask(chosen, touch_policy)
        selected_rows = chosen[touch_gate & kinetic_overlay_mask(chosen, overlay)].copy()
    elif spec["kind"] == "kinetic_price_guard":
        touch_policy = policy
        touch_gate = touch_gate_mask(chosen, touch_policy)
        selected_rows = chosen[touch_gate & kinetic_overlay_mask(chosen, overlay)].copy()
    else:
        base_policy: Policy = policy
        selected_rows = chosen[gate_mask(chosen, base_policy) & base_overlay_mask(chosen, overlay)].copy()
    if selected_rows.empty:
        return selected_rows
    selected = (
        selected_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["lock_name"] = spec["name"]
    selected["lock_close_dt"] = lock_close_dt
    selected["chooser"] = policy.chooser
    selected["score_value"] = selected[policy.chooser] if policy.chooser in selected.columns else np.nan
    selected["overlay"] = overlay.label
    return selected


def signal_record(row: pd.Series, registered_utc: str) -> Dict[str, Any]:
    outcome_available = bool_value(row.get("outcome_available"))
    outcome = row.get("outcome")
    side = str(row.get("side"))
    ask = float(row.get("ask_cents"))
    fee = estimated_order_fee_cents(ask, 1)
    win = bool(side == outcome) if outcome_available and outcome in {"yes", "no"} else None
    net = (100.0 - ask - fee) if win is True else (-ask - fee) if win is False else None
    return {
        "lock_name": row.get("lock_name"),
        "market": row.get("market"),
        "registered_utc": registered_utc,
        "lock_close_dt": pd.to_datetime(row.get("lock_close_dt"), utc=True, errors="coerce").isoformat(),
        "entry_dt": pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce").isoformat(),
        "close_dt": pd.to_datetime(row.get("close_dt"), utc=True, errors="coerce").isoformat(),
        "side": side,
        "ask_cents": ask,
        "bid_cents": row.get("bid_cents"),
        "seconds_to_close": row.get("seconds_to_close"),
        "source_line_no": row.get("source_line_no"),
        "decision_key": row.get("decision_key"),
        "chooser": row.get("chooser"),
        "score_value": row.get("score_value"),
        "overlay": row.get("overlay"),
        "book_p_side": row.get("book_p_side"),
        "brownian_p_rv_15m": row.get("brownian_p_rv_15m"),
        "brownian_p_rv_30m": row.get("brownian_p_rv_30m"),
        "margin_dollars": row.get("margin_dollars"),
        "margin_per_rv_sigma_15m": row.get("margin_per_rv_sigma_15m"),
        "signed_move_3m": row.get("signed_move_3m"),
        "signed_move_5m": row.get("signed_move_5m"),
        "signed_move_15m": row.get("signed_move_15m"),
        "signed_move_30m": row.get("signed_move_30m"),
        "impulse_3_5m": row.get("impulse_3_5m"),
        "impulse_3_5m_over_margin": row.get("impulse_3_5m_over_margin"),
        "fade_trigger_side": row.get("fade_trigger_side") or row.get("trigger_side"),
        "fade_trigger_ask_cents": row.get("fade_trigger_ask_cents"),
        "fade_trigger_score_value": row.get("fade_trigger_score_value"),
        "fade_trigger_margin_dollars": row.get("fade_trigger_margin_dollars"),
        "fade_trigger_signed_move_3m": row.get("fade_trigger_signed_move_3m"),
        "fade_trigger_signed_move_5m": row.get("fade_trigger_signed_move_5m"),
        "fade_trigger_impulse_3_5m": row.get("fade_trigger_impulse_3_5m"),
        "fade_trigger_impulse_3_5m_over_margin": row.get("fade_trigger_impulse_3_5m_over_margin"),
        "abs_book_rv15_gap": row.get("abs_book_rv15_gap"),
        "adverse_move_15m": row.get("adverse_move_15m"),
        "touch_loss_rv_15m": row.get("touch_loss_rv_15m"),
        "touch_survival_rv_15m": row.get("touch_survival_rv_15m"),
        "book_touch_blend_15": row.get("book_touch_blend_15"),
        "hazard_discounted_mean_15": row.get("hazard_discounted_mean_15"),
        "kinetic_touch_score_15": row.get("kinetic_touch_score_15"),
        "blend_logit_book_rv_hazard_mean": row.get("blend_logit_book_rv_hazard_mean"),
        "fair_edge_cents": row.get("fair_edge_cents"),
        "outcome_available": outcome_available,
        "outcome": outcome if outcome_available else "",
        "win": win,
        "entry_fee_cents": fee,
        "net_pnl_cents": net,
    }


def update_outcomes(registry: pd.DataFrame, outcomes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    for idx, row in out.iterrows():
        outcome = outcomes.get(str(row["market"]), {}).get("outcome")
        if outcome not in {"yes", "no"}:
            out.at[idx, "outcome_available"] = False
            out.at[idx, "outcome"] = ""
            out.at[idx, "win"] = ""
            out.at[idx, "net_pnl_cents"] = np.nan
            continue
        side = str(row["side"])
        ask = float(row["ask_cents"])
        fee = int(row["entry_fee_cents"]) if not pd.isna(row.get("entry_fee_cents")) else estimated_order_fee_cents(ask, 1)
        win = side == outcome
        out.at[idx, "outcome_available"] = True
        out.at[idx, "outcome"] = outcome
        out.at[idx, "win"] = win
        out.at[idx, "entry_fee_cents"] = fee
        out.at[idx, "net_pnl_cents"] = (100.0 - ask - fee) if win else (-ask - fee)
    return out


def summarize(registry: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if registry.empty:
        return rows
    work = registry.copy()
    work["outcome_available"] = work["outcome_available"].map(bool_value)
    work["win"] = work["win"].map(bool_value)
    work["net_pnl_cents"] = pd.to_numeric(work["net_pnl_cents"], errors="coerce")
    for lock_name, part in work.groupby("lock_name", sort=False):
        resolved = part[part["outcome_available"]].copy()
        pending = part[~part["outcome_available"]].copy()
        wins = int(resolved["win"].sum()) if not resolved.empty else 0
        n = int(len(resolved))
        rows.append(
            {
                "lock_name": lock_name,
                "registered": int(len(part)),
                "pending": int(len(pending)),
                "resolved": n,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": float(resolved["net_pnl_cents"].sum()) if n else 0.0,
                "first_pending_market": str(pending.iloc[0]["market"]) if not pending.empty else "",
            }
        )
    return rows


def write_report(path: Path, generated: str, summary_rows: List[Dict[str, Any]], new_records: int, removed_post_close_records: int) -> None:
    lines = [
        "# Profit Lock Pending Signal Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only pre-resolution registry; no orders are submitted and no bot files or live processes are touched.",
        "- Applies existing locked EV policies to raw heartbeat rows, including unresolved markets.",
        "- Registers the first eligible post-lock signal per market before outcome is available; later runs only update outcomes.",
        "",
        f"- New records registered this run: {new_records}",
        f"- Post-close/non-causal registry records removed this run: {removed_post_close_records}",
        "",
        "## Registry Summary",
        "",
        "| lock | registered | pending | resolved | wins/losses | acc | resolved net P&L | first pending |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['lock_name']} | {row['registered']} | {row['pending']} | {row['resolved']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['accuracy'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"`{row['first_pending_market']}` |"
        )
    if not summary_rows:
        lines.append("| none | 0 | 0 | 0 | 0/0 | NA | 0.0c |  |")
    lines += ["", "## Read", ""]
    if any(row["pending"] > 0 for row in summary_rows):
        lines.append("- At least one lock has pre-registered unresolved market signals waiting for settlement.")
    else:
        lines.append("- No unresolved lock signals are pending right now.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registered_utc = datetime.now(timezone.utc).isoformat()
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    rows = raw_side_rows(fetch_btc_candles=bool(args.fetch_btc_candles))
    specs = [load_lock(name, path, kind) for name, path, kind in LOCK_SPECS]
    registry = load_registry()
    registry = filter_registry_to_effective_locks(registry, specs)
    registry, removed_post_close_records = filter_registry_to_pre_resolution(registry)
    existing_keys = set()
    if not registry.empty:
        existing_keys = set(zip(registry["lock_name"].astype(str), registry["market"].astype(str)))
    now_dt = pd.Timestamp.now(tz="UTC")
    new_records: List[Dict[str, Any]] = []
    enrich_cols = [
        "fade_trigger_side",
        "fade_trigger_ask_cents",
        "fade_trigger_score_value",
        "fade_trigger_margin_dollars",
        "fade_trigger_signed_move_3m",
        "fade_trigger_signed_move_5m",
        "fade_trigger_impulse_3_5m",
        "fade_trigger_impulse_3_5m_over_margin",
    ]
    for spec in specs:
        selected = select_signals(rows, spec)
        if not selected.empty:
            selected = selected[
                pd.to_datetime(selected["close_dt"], utc=True, errors="coerce").gt(now_dt)
                & ~selected["outcome_available"].map(bool_value)
            ].copy()
        for _, row in selected.iterrows():
            key = (str(spec["name"]), str(row.get("market")))
            if key in existing_keys:
                if spec["kind"] == "impulse_fade" and not registry.empty:
                    mask = registry["lock_name"].astype(str).eq(key[0]) & registry["market"].astype(str).eq(key[1])
                    for col in enrich_cols:
                        if col in registry.columns and col in row.index and pd.notna(row.get(col)):
                            if col == "fade_trigger_side":
                                registry[col] = registry[col].astype(object)
                            missing = registry.loc[mask, col].isna() | registry.loc[mask, col].astype(str).eq("")
                            registry.loc[mask & missing, col] = row.get(col)
                continue
            new_records.append(signal_record(row, registered_utc))
            existing_keys.add(key)
    if new_records:
        new_frame = pd.DataFrame(new_records)
        new_frame = new_frame.reindex(columns=SIGNAL_COLS)
        registry = (
            new_frame
            if registry.empty
            else pd.concat([registry.dropna(axis=1, how="all"), new_frame.dropna(axis=1, how="all")], ignore_index=True)
        )
        registry = registry.reindex(columns=SIGNAL_COLS)
    registry = update_outcomes(registry, outcomes)
    registry = registry[SIGNAL_COLS].sort_values(["lock_name", "entry_dt", "market"]).reset_index(drop=True)
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(REGISTRY_PATH, index=False)
    stamp_csv = OUT_DIR / f"profit_lock_pending_signal_registry_{generated}.csv"
    registry.to_csv(stamp_csv, index=False)
    summary_rows = summarize(registry)
    write_report(REPORT_LATEST, generated, summary_rows, len(new_records), removed_post_close_records)
    stamp_md = OUT_DIR / f"profit_lock_pending_signal_monitor_{generated}.md"
    write_report(stamp_md, generated, summary_rows, len(new_records), removed_post_close_records)
    payload = {
        "generated_utc": generated,
        "new_records": len(new_records),
        "removed_post_close_records": removed_post_close_records,
        "registry_path": str(REGISTRY_PATH),
        "summary": summary_rows,
    }
    JSON_LATEST.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamp_json = OUT_DIR / f"profit_lock_pending_signal_monitor_{generated}.json"
    stamp_json.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock pending signal monitor complete")
    print(f"new_records={len(new_records)} registered={len(registry)}")
    print(f"removed_post_close_records={removed_post_close_records}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
