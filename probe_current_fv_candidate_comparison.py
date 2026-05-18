"""Current FV candidate comparison and gate.

Research-only. Consolidates retrospective and strict-forward evidence for the
current BTC 15m high-coverage FV candidates. This is not a scorer and does not
touch the live bot or order path.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "current_fv_candidate_comparison_latest.md"
REPORT_JSON = OUT_DIR / "current_fv_candidate_comparison_latest.json"

MIN_FORWARD_FINALIZED = 50
MIN_FORWARD_DAYS = 2
MIN_FORWARD_COVERAGE = 0.75


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def one_row(df: pd.DataFrame, mask: pd.Series) -> dict[str, Any]:
    if df.empty:
        return {}
    rows = df[mask].copy()
    if rows.empty:
        return {}
    return rows.iloc[0].to_dict()


def forward_metrics(registry_path: Path, denominator_path: Path) -> dict[str, Any]:
    registry = load_csv(registry_path)
    denom = load_json(denominator_path)
    market_count = int(denom.get("market_count") or 0)
    if registry.empty:
        return {
            "registered": 0,
            "finalized": 0,
            "days": 0,
            "coverage": 0.0 if market_count else None,
            "market_count": market_count,
            "fee_net_cents": 0.0,
            "fee_1c_cents": 0.0,
            "gross_cents": 0.0,
            "pass": False,
        }
    registry["entry_dt"] = pd.to_datetime(registry.get("entry_dt"), utc=True, errors="coerce")
    status = registry.get("status", pd.Series([], dtype=str)).astype(str).str.lower()
    finalized = registry[status.isin(["exited", "settled"])].copy()
    finalized["entry_day_utc"] = finalized["entry_dt"].dt.strftime("%Y-%m-%d")
    fee_net = float(pd.to_numeric(finalized.get("fee_net_cents"), errors="coerce").fillna(0.0).sum())
    fee_1c = float(pd.to_numeric(finalized.get("fee_net_1c_entry_cents"), errors="coerce").fillna(0.0).sum())
    gross = float(pd.to_numeric(finalized.get("gross_pnl_cents"), errors="coerce").fillna(0.0).sum())
    markets = int(registry["market"].astype(str).nunique()) if "market" in registry.columns else int(len(registry))
    raw_coverage = float(markets / market_count) if market_count else None
    coverage = min(raw_coverage, 1.0) if raw_coverage is not None else None
    days = int(finalized["entry_day_utc"].nunique()) if not finalized.empty else 0
    checks = {
        "finalized": int(len(finalized)) >= MIN_FORWARD_FINALIZED,
        "days": days >= MIN_FORWARD_DAYS,
        "coverage": coverage is not None and coverage >= MIN_FORWARD_COVERAGE,
        "fee_1c_positive": fee_1c > 0.0,
    }
    return {
        "registered": int(len(registry)),
        "registered_markets": markets,
        "finalized": int(len(finalized)),
        "days": days,
        "coverage": coverage,
        "raw_coverage": raw_coverage,
        "market_count": market_count,
        "fee_net_cents": fee_net,
        "fee_1c_cents": fee_1c,
        "gross_cents": gross,
        "checks": checks,
        "pass": all(checks.values()),
    }


def probability_record(v42_json: dict[str, Any], candidate: str, split: str = "holdout") -> dict[str, Any]:
    for row in v42_json.get("probability_records") or []:
        if row.get("candidate") == candidate and row.get("split") == split:
            return row
    return {}


def candidate_payload() -> list[dict[str, Any]]:
    v38 = load_csv(OUT_DIR / "v38_edge_hole80_exit_frontier_summary_latest.csv")
    v42 = load_csv(OUT_DIR / "v42_edgehole_latent_fv_strategy_summary_latest.csv")
    v43 = load_csv(OUT_DIR / "v43_latent_hole_weight_sweep_summary_latest.csv")
    v45 = load_csv(OUT_DIR / "v45_latent_disagreement_switch_strategy_summary_latest.csv")
    v47 = load_csv(OUT_DIR / "v47_recross_hazard_fv_strategy_summary_latest.csv")
    v50 = load_csv(OUT_DIR / "v50_v47_thin_edge_certainty_fv_strategy_summary_latest.csv")
    v52 = load_csv(OUT_DIR / "v52_weak_recross_hazard_fv_strategy_summary_latest.csv")
    v53 = load_csv(OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_strategy_summary_latest.csv")
    v55 = load_csv(OUT_DIR / "v55_book_anchor_recross_fv_strategy_summary_latest.csv")
    v56 = load_csv(OUT_DIR / "v56_book_edge_recross_fv_strategy_summary_latest.csv")
    v57 = load_csv(OUT_DIR / "v57_cross_surface_exit_strategy_summary_latest.csv")
    v58 = load_csv(OUT_DIR / "v58_v55_exit_persistence_refine_summary_latest.csv")
    v62 = load_csv(OUT_DIR / "v62_diffusion_bridge_fv_strategy_summary_latest.csv")
    v66 = load_csv(OUT_DIR / "v66_no_bookgap_fv_strategy_summary_latest.csv")
    v68 = load_csv(OUT_DIR / "v68_regularized_physics_logit_fv_strategy_summary_latest.csv")
    v69 = load_csv(OUT_DIR / "v69_v55_entry_v66_exit_strategy_summary_latest.csv")
    v70 = load_csv(OUT_DIR / "v70_v55_entry_v66_margin_exit_strategy_summary_latest.csv")
    v71 = load_csv(OUT_DIR / "v71_v55_entry_v68_exit_strategy_summary_latest.csv")
    v44 = load_csv(OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_summary_latest.csv")
    v42_json = load_json(OUT_DIR / "v42_edgehole_latent_fv_strategy_latest.json")
    v43_json = load_json(OUT_DIR / "v43_latent_hole_weight_sweep_latest.json")
    v45_json = load_json(OUT_DIR / "v45_latent_disagreement_switch_strategy_latest.json")
    v47_json = load_json(OUT_DIR / "v47_recross_hazard_fv_strategy_latest.json")
    v50_json = load_json(OUT_DIR / "v50_v47_thin_edge_certainty_fv_strategy_latest.json")
    v52_json = load_json(OUT_DIR / "v52_weak_recross_hazard_fv_strategy_latest.json")
    v53_json = load_json(OUT_DIR / "v53_weak_recross_thin_edge_combo_fv_strategy_latest.json")
    v55_json = load_json(OUT_DIR / "v55_book_anchor_recross_fv_strategy_latest.json")
    v56_json = load_json(OUT_DIR / "v56_book_edge_recross_fv_strategy_latest.json")
    v62_json = load_json(OUT_DIR / "v62_diffusion_bridge_fv_strategy_latest.json")
    v66_json = load_json(OUT_DIR / "v66_no_bookgap_fv_strategy_latest.json")
    v68_json = load_json(OUT_DIR / "v68_regularized_physics_logit_fv_strategy_latest.json")
    v44_json = load_json(OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_latest.json")

    candidates: list[dict[str, Any]] = [
        {
            "name": "v38_explicit_veto_current_best_12_20",
            "kind": "explicit_entry_veto",
            "retro": one_row(
                v38,
                v38.get("veto_policy", pd.Series(dtype=str)).eq("block_first_edge_12_20")
                & v38.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v38.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": {},
            "probability": {},
        },
        {
            "name": "v38_explicit_veto_legacy_10_20_forward",
            "kind": "explicit_entry_veto_legacy_forward",
            "retro": one_row(
                v38,
                v38.get("veto_policy", pd.Series(dtype=str)).eq("block_first_edge_10_20")
                & v38.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v38.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v38_edge_hole80_shadow_registry_latest.csv",
                OUT_DIR / "v38_edge_hole80_forward_denominator_latest.json",
            ),
            "probability": {},
        },
        {
            "name": "v43_latent_hole_bookblend90_leader",
            "kind": "fv_latent_book_blend",
            "retro": one_row(
                v43,
                v43.get("model", pd.Series(dtype=str)).eq("v43_latent_hole_bookblend90")
                & v43.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v43.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v43_latent_hole_bookblend90_shadow_registry_latest.csv",
                OUT_DIR / "v43_latent_hole_bookblend90_forward_denominator_latest.json",
            ),
            "probability": probability_record(v43_json, "v43_latent_hole_bookblend90"),
        },
        {
            "name": "v45_latent_disagree_book_else_blend90",
            "kind": "fv_latent_disagreement_switch",
            "retro": one_row(
                v45,
                v45.get("model", pd.Series(dtype=str)).eq("v45_latent_disagree_book_else_blend90")
                & v45.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v45.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v45_latent_disagreement_shadow_registry_latest.csv",
                OUT_DIR / "v45_latent_disagreement_forward_denominator_latest.json",
            ),
            "probability": probability_record(v45_json, "v45_latent_disagree_book_else_blend90"),
        },
        {
            "name": "v47_recross_sigma1_v3cap68",
            "kind": "fv_recross_hazard_cap",
            "retro": one_row(
                v47,
                v47.get("model", pd.Series(dtype=str)).eq("v47_recross_sigma1_v3cap68")
                & v47.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v47.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v47_recross_hazard_shadow_registry_latest.csv",
                OUT_DIR / "v47_recross_hazard_forward_denominator_latest.json",
            ),
            "probability": probability_record(v47_json, "v47_recross_sigma1_v3cap68"),
        },
        {
            "name": "v50_thinedge_ask90_edge1_stc450_cap75",
            "kind": "fv_thin_edge_certainty_cap",
            "retro": one_row(
                v50,
                v50.get("model", pd.Series(dtype=str)).eq("v50_thinedge_ask90_edge1_stc450_cap75")
                & v50.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v50.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v50_thin_edge_certainty_shadow_registry_latest.csv",
                OUT_DIR / "v50_thin_edge_certainty_forward_denominator_latest.json",
            ),
            "probability": probability_record(v50_json, "v50_thinedge_ask90_edge1_stc450_cap75"),
        },
        {
            "name": "v52_weakrecross_sigma08_v3p15_cap68",
            "kind": "fv_weak_recross_hazard_cap",
            "retro": one_row(
                v52,
                v52.get("model", pd.Series(dtype=str)).eq("v52_weakrecross_sigma08_v3p15_cap68")
                & v52.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v52.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": {},
            "probability": probability_record(v52_json, "v52_weakrecross_sigma08_v3p15_cap68"),
        },
        {
            "name": "v53_weakrecross_thinedge_risk_adjusted",
            "kind": "fv_weak_recross_thin_edge_combo",
            "retro": one_row(
                v53,
                v53.get("model", pd.Series(dtype=str)).eq(
                    "v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75"
                )
                & v53.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v53.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v53_weak_recross_thin_edge_shadow_registry_latest.csv",
                OUT_DIR / "v53_weak_recross_thin_edge_forward_denominator_latest.json",
            ),
            "probability": probability_record(
                v53_json,
                "v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75",
            ),
        },
        {
            "name": "v55_bookanchor_m10_v20_g05_book_plus2",
            "kind": "fv_book_anchor_recross",
            "retro": one_row(
                v55,
                v55.get("model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v55.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v55.get("exit_policy", pd.Series(dtype=str)).eq("prob52"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v55_book_anchor_recross_shadow_registry_latest.csv",
                OUT_DIR / "v55_book_anchor_recross_forward_denominator_latest.json",
            ),
            "probability": probability_record(v55_json, "v55_bookanchor_m10_v20_g05_book_plus2"),
        },
        {
            "name": "v56_bookedge_best_calibration_not_tradable",
            "kind": "fv_book_edge_calibration",
            "retro": one_row(
                v56,
                v56.get("model", pd.Series(dtype=str)).eq("v56_bedge1_m11_v15_g05_book_else_plus2")
                & v56.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v56.get("exit_policy", pd.Series(dtype=str)).eq("prob52"),
            ),
            "forward": {},
            "probability": probability_record(v56_json, "v56_bedge1_m11_v15_g05_book_else_plus2"),
        },
        {
            "name": "v57_v55_bookanchor_hold15_prob52",
            "kind": "fv_book_anchor_recross_hold15_exit",
            "retro": one_row(
                v57,
                v57.get("entry_model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v57.get("exit_model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v57.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v57.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob52"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v57_v55_hold15_shadow_registry_latest.csv",
                OUT_DIR / "v57_v55_hold15_forward_denominator_latest.json",
            ),
            "probability": probability_record(v55_json, "v55_bookanchor_m10_v20_g05_book_plus2"),
        },
        {
            "name": "v58_v55_bookanchor_hold15_prob52_marginlte0p25",
            "kind": "fv_book_anchor_recross_yes_axis_margin_exit",
            "retro": one_row(
                v58,
                v58.get("model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v58.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v58.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob52_marginlte0p25"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v58_v55_margin_exit_shadow_registry_latest.csv",
                OUT_DIR / "v58_v55_margin_exit_forward_denominator_latest.json",
            ),
            "probability": probability_record(v55_json, "v55_bookanchor_m10_v20_g05_book_plus2"),
        },
        {
            "name": "v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25",
            "kind": "fv_book_anchor_recross_no_side_yes_axis_margin_exit",
            "retro": one_row(
                v58,
                v58.get("model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v58.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v58.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob52_noside_marginlte0p25"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v60_v55_no_side_margin_exit_shadow_registry_latest.csv",
                OUT_DIR / "v60_v55_no_side_margin_exit_forward_denominator_latest.json",
            ),
            "probability": probability_record(v55_json, "v55_bookanchor_m10_v20_g05_book_plus2"),
        },
        {
            "name": "v61_v55_bookanchor_hold15_prob56_noside_marginlte0p25",
            "kind": "fv_book_anchor_recross_no_side_prob56_yes_axis_margin_exit",
            "retro": one_row(
                v58,
                v58.get("model", pd.Series(dtype=str)).eq("v55_bookanchor_m10_v20_g05_book_plus2")
                & v58.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v58.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob56_noside_marginlte0p25"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v61_v55_no_side_prob56_margin_exit_shadow_registry_latest.csv",
                OUT_DIR / "v61_v55_no_side_prob56_margin_exit_forward_denominator_latest.json",
            ),
            "probability": probability_record(v55_json, "v55_bookanchor_m10_v20_g05_book_plus2"),
        },
        {
            "name": "v62_diffusion_best_calibration_not_tradable",
            "kind": "fv_diffusion_bridge_calibration",
            "retro": one_row(
                v62,
                v62.get("model", pd.Series(dtype=str)).eq("v62_diff_m100_t125_w25")
                & v62.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.66_stc0-600")
                & v62.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": {},
            "probability": probability_record(v62_json, "v62_diff_m100_t125_w25"),
        },
        {
            "name": "v66_no_bookgap_best_calibration_robust",
            "kind": "fv_no_side_book_gap_shrink",
            "retro": one_row(
                v66,
                v66.get("model", pd.Series(dtype=str)).eq("v66_no_bookgap_g05_bookplus00")
                & v66.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.66_stc0-570")
                & v66.get("exit_policy", pd.Series(dtype=str)).eq("prob56"),
            ),
            "forward": {},
            "probability": probability_record(v66_json, "v66_no_bookgap_g05_bookplus00"),
        },
        {
            "name": "v66_no_bookgap_balanced_min_split",
            "kind": "fv_no_side_book_gap_shrink",
            "retro": one_row(
                v66,
                v66.get("model", pd.Series(dtype=str)).eq("v66_no_bookgap_g08_blend75")
                & v66.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v66.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v66_no_bookgap_balanced_shadow_registry_latest.csv",
                OUT_DIR / "v66_no_bookgap_balanced_forward_denominator_latest.json",
            ),
            "probability": probability_record(v66_json, "v66_no_bookgap_g08_blend75"),
        },
        {
            "name": "v68_regularized_physics_logit_best_calibration_not_tradable",
            "kind": "fv_regularized_physics_logit_calibration",
            "retro": one_row(
                v68,
                v68.get("model", pd.Series(dtype=str)).eq("v68_l2_C0p05")
                & v68.get("entry_policy", pd.Series(dtype=str)).eq("edge1_ask100_p0.65_stc0-780")
                & v68.get("exit_policy", pd.Series(dtype=str)).eq("hold"),
            ),
            "forward": {},
            "probability": probability_record(v68_json, "v68_l2_C1p0"),
        },
        {
            "name": "v69_v55_entry_v66_exit_hold15_prob52",
            "kind": "fv_cross_surface_v55_entry_v66_exit",
            "retro": one_row(
                v69,
                v69.get("model", pd.Series(dtype=str)).eq("v55_entry__v66_bal_exit")
                & v69.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v69.get("exit_policy", pd.Series(dtype=str)).eq("hold15_v66_bal_prob52"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v69_v55_entry_v66_exit_shadow_registry_latest.csv",
                OUT_DIR / "v69_v55_entry_v66_exit_forward_denominator_latest.json",
            ),
            "probability": probability_record(v66_json, "v66_no_bookgap_g08_blend75"),
        },
        {
            "name": "v70_v55_entry_v66_bal_margin_exit_prob52_noside_marginlte0p25",
            "kind": "fv_cross_surface_v55_entry_v66_exit_margin_gate",
            "retro": one_row(
                v70,
                v70.get("model", pd.Series(dtype=str)).eq("v55_entry__v66_bal_margin_exit")
                & v70.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v70.get("exit_surface", pd.Series(dtype=str)).eq("v66_bal")
                & v70.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob52_noside_marginlte0p25"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v70_v55_entry_v66_margin_exit_shadow_registry_latest.csv",
                OUT_DIR / "v70_v55_entry_v66_margin_exit_forward_denominator_latest.json",
            ),
            "probability": probability_record(v66_json, "v66_no_bookgap_g08_blend75"),
        },
        {
            "name": "v71_v55_entry_v68_exit_best_calibrated_exit_rejected",
            "kind": "fv_cross_surface_v55_entry_v68_exit_calibration_rejected",
            "retro": one_row(
                v71,
                v71.get("model", pd.Series(dtype=str)).eq("v55_entry__v68_C0p05_exit")
                & v71.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v71.get("exit_surface", pd.Series(dtype=str)).eq("v68_C0p05")
                & v71.get("exit_policy", pd.Series(dtype=str)).eq("hold15_prob56_marginlte0p25"),
            ),
            "forward": {},
            "probability": probability_record(v68_json, "v68_l2_C0p05"),
        },
        {
            "name": "v42_latent_hole_flat_profit",
            "kind": "fv_latent_flat",
            "retro": one_row(
                v42,
                v42.get("model", pd.Series(dtype=str)).eq("v42_latent_hole_flat")
                & v42.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v42.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": {},
            "probability": probability_record(v42_json, "v42_latent_hole_flat"),
        },
        {
            "name": "v42_latent_hole_book_fvclean",
            "kind": "fv_latent_book",
            "retro": one_row(
                v42,
                v42.get("model", pd.Series(dtype=str)).eq("v42_latent_hole_book")
                & v42.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.64_stc0-600")
                & v42.get("exit_policy", pd.Series(dtype=str)).eq("prob52"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v42_latent_hole_book_shadow_registry_latest.csv",
                OUT_DIR / "v42_latent_hole_book_forward_denominator_latest.json",
            ),
            "probability": probability_record(v42_json, "v42_latent_hole_book"),
        },
        {
            "name": "v42_latent_hole_book_p65_delayed_challenger",
            "kind": "fv_latent_book",
            "retro": one_row(
                v42,
                v42.get("model", pd.Series(dtype=str)).eq("v42_latent_hole_book")
                & v42.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc120-600")
                & v42.get("exit_policy", pd.Series(dtype=str)).eq("prob52"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v42_latent_hole_book_p65_delayed_shadow_registry_latest.csv",
                OUT_DIR / "v42_latent_hole_book_p65_delayed_forward_denominator_latest.json",
            ),
            "probability": probability_record(v42_json, "v42_latent_hole_book"),
        },
        {
            "name": "v42_latent_hole_bookblend80_balanced",
            "kind": "fv_latent_book_blend",
            "retro": one_row(
                v42,
                v42.get("model", pd.Series(dtype=str)).eq("v42_latent_hole_bookblend80")
                & v42.get("entry_policy", pd.Series(dtype=str)).eq("edge0_ask100_p0.65_stc0-600")
                & v42.get("exit_policy", pd.Series(dtype=str)).eq("prob54"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v42_latent_hole_bookblend80_shadow_registry_latest.csv",
                OUT_DIR / "v42_latent_hole_bookblend80_forward_denominator_latest.json",
            ),
            "probability": probability_record(v42_json, "v42_latent_hole_bookblend80"),
        },
        {
            "name": "v44_bookres_l230_holeblend100_challenger",
            "kind": "fv_physics_bookres_latent_book",
            "retro": one_row(
                v44,
                v44.get("model", pd.Series(dtype=str)).eq("v44_v41_v38_bookres_l230_holeblend100")
                & v44.get("entry_policy", pd.Series(dtype=str)).eq("edge1_ask100_p0.64_stc0-780")
                & v44.get("exit_policy", pd.Series(dtype=str)).eq("prob50"),
            ),
            "forward": forward_metrics(
                OUT_DIR / "v44_bookres_challenger_shadow_registry_latest.csv",
                OUT_DIR / "v44_bookres_challenger_forward_denominator_latest.json",
            ),
            "probability": probability_record(v44_json, "v44_v41_v38_bookres_l230_holeblend100"),
        },
    ]
    for cand in candidates:
        retro = cand.get("retro") or {}
        forward = cand.get("forward") or {}
        retro_pass = bool(retro) and float(retro.get("min_split_coverage") or 0.0) >= 0.80 and float(
            retro.get("min_split_net_after_fees_1c_entry_dollars") or 0.0
        ) > 0.0
        if "positive_1c_days" in retro and "total_days" in retro:
            retro_pass = retro_pass and int(retro.get("positive_1c_days") or 0) == int(retro.get("total_days") or 0)
        cand["retro_pass"] = retro_pass
        cand["forward_pass"] = bool(forward.get("pass"))
        cand["promotion_ready"] = bool(retro_pass and forward.get("pass"))
    return candidates


def write_report(candidates: list[dict[str, Any]]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Current FV Candidate Comparison",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Compares current v38/v42/v43/v44/v45/v47/v50/v52/v53/v55/v56/v57/v58/v60/v61/v62/v66/v68/v69/v70/v71 BTC 15m high-coverage fair-value candidates.",
        "- Requires retrospective 80%+ coverage, fee+1c positive splits, day stability, and strict-forward sample before promotion.",
        "- Research-only; live bot untouched.",
        "",
        "## Retrospective",
        "",
        "| candidate | kind | min cov | min 1c | all 1c | days | block10 | trades | holdout Brier | holdout logloss |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cand in candidates:
        retro = cand.get("retro") or {}
        prob = cand.get("probability") or {}
        lines.append(
            f"| `{cand['name']}` | `{cand['kind']}` | "
            f"{pct(retro.get('min_split_coverage'))} | "
            f"{dollars(retro.get('min_split_net_after_fees_1c_entry_dollars'))} | "
            f"{dollars(retro.get('all_net_after_fees_1c_entry_dollars'))} | "
            f"{int(retro.get('positive_1c_days') or 0)}/{int(retro.get('total_days') or 0)} | "
            f"{int(retro.get('block10_positive') or 0)}/10 | "
            f"{int(retro.get('all_trades') or 0)} | "
            f"{'' if not prob else f'{float(prob.get('brier')):.5f}'} | "
            f"{'' if not prob else f'{float(prob.get('logloss')):.5f}'} |"
        )
    lines += [
        "",
        "## Strict Forward",
        "",
        "| candidate | registered | finalized | days | coverage | fee+1c | forward pass |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cand in candidates:
        fwd = cand.get("forward") or {}
        lines.append(
            f"| `{cand['name']}` | {int(fwd.get('registered') or 0)} | {int(fwd.get('finalized') or 0)} | "
            f"{int(fwd.get('days') or 0)} | {pct(fwd.get('coverage'))} | {dollars_cents(fwd.get('fee_1c_cents', 0.0))} | "
            f"`{bool(fwd.get('pass'))}` |"
        )
    lines += ["", "## Read", ""]
    ready = [cand for cand in candidates if cand.get("promotion_ready")]
    if ready:
        lines.append("- At least one candidate passes the configured retrospective and strict-forward gates.")
    else:
        lines.append("- No candidate is promotion-ready. The missing requirement is strict-forward live sample size/stability.")
    best_retro = sorted(
        [c for c in candidates if c.get("retro")],
        key=lambda c: (
            float((c.get("retro") or {}).get("min_split_net_after_fees_1c_entry_dollars") or -999.0),
            float((c.get("retro") or {}).get("all_net_after_fees_1c_entry_dollars") or -999.0),
        ),
        reverse=True,
    )[0]
    best_all = sorted(
        [c for c in candidates if c.get("retro")],
        key=lambda c: float((c.get("retro") or {}).get("all_net_after_fees_1c_entry_dollars") or -999.0),
        reverse=True,
    )[0]
    with_prob = [c for c in candidates if c.get("probability")]
    best_calibration = (
        sorted(with_prob, key=lambda c: float((c.get("probability") or {}).get("brier") or 999.0))[0]
        if with_prob
        else None
    )
    lines.append(f"- Best retrospective min-split PnL is `{best_retro['name']}`.")
    if best_calibration:
        lines.append(
            f"- Best all-market PnL is currently `{best_all['name']}`; best holdout calibration is "
            f"`{best_calibration['name']}`."
        )
    else:
        lines.append(f"- Best all-market PnL is currently `{best_all['name']}`.")
    lines.append(
        "- v68 is the best holdout probability calibration evidence so far, but its high-PnL strategy rows fail split robustness."
    )
    lines.append(
        "- v69 improves worst-split cushion by combining v55 entry with the v66 balanced exit surface, but it gives up all-market PnL versus v57/v60."
    )
    lines.append(
        "- v70 keeps v69's worst-split cushion while adding the v60 NO-side margin-gated exit; it is the current balanced cross-surface strategy to shadow forward."
    )
    lines.append(
        "- v71 shows v68's better probability calibration does not transfer into better exits for the v55 entry universe."
    )
    lines.append(
        "- v66 materially improves calibration and min-split cushion, but it gives up all-market PnL versus v55/v57, so it is a robustness lens rather than the current profit leader."
    )
    if best_all["name"] in {
        "v58_v55_bookanchor_hold15_prob52_marginlte0p25",
        "v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25",
    }:
        lines.append(
            "- The margin-gated v58/v60/v61 branch is overfit-prone until proven forward: the v59/v61 audits show the upside is still tied to NO-side saved exits."
        )
    lines.append(
        "- Strict-forward rows are still far below the 50+ finalized / 2+ day gate; the freshest v57/v60/v61 rows are mixed to negative, so none should be promoted."
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(clean_json({"generated_utc": generated, "candidates": candidates}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    candidates = candidate_payload()
    write_report(candidates)
    print("current FV candidate comparison complete")
    print(f"report={REPORT_MD}")
    print(f"promotion_ready={any(c['promotion_ready'] for c in candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
