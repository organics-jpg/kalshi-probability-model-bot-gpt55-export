"""Build the research-only v28 successor live P&L policy lab artifacts.

This script adds the first trading-policy layer on top of the v28 successor FV
forward artifacts. It is intentionally a sidecar/offline research tool:

- no live bot code is imported,
- no order or account endpoint is called,
- no state, threshold, secret, or live process is mutated,
- policy decisions are created from already-frozen pre-resolution FV rows,
- labels are joined only from the post-resolution labeled file.

Rows whose market decisions happened before the policy hash was created are
kept as diagnostic evidence only. They are useful for exercising the lab and
rejecting bad policy shapes, but they receive no primary live-forward credit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

FROZEN_CSV = OUT_DIR / "sidecar_bundle_batch_frozen_latest.csv"
LABELED_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"
PACKETS_CSV = OUT_DIR / "sidecar_bundle_batch_packets_latest.csv"

POLICY_REGISTRY_CSV = OUT_DIR / "live_pnl_policy_registry_latest.csv"
POLICY_REGISTRY_JSON = OUT_DIR / "live_pnl_policy_registry_latest.json"
LABELED_DECISIONS_CSV = OUT_DIR / "live_pnl_labeled_decisions_latest.csv"
LABELED_DECISIONS_JSON = OUT_DIR / "live_pnl_labeled_decisions_latest.json"

BASELINE_JSON = EDGE_DIR / "v28_successor_live_pnl_baseline_latest.json"
BASELINE_MD = EDGE_DIR / "v28_successor_live_pnl_baseline_latest.md"
POLICY_SCORE_JSON = EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.json"
POLICY_SCORE_MD = EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.md"
POLICY_SCORE_CSV = EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.csv"
READINESS_JSON = EDGE_DIR / "v28_successor_live_pnl_readiness_latest.json"
READINESS_MD = EDGE_DIR / "v28_successor_live_pnl_readiness_latest.md"
DECISION_LOG_MD = EDGE_DIR / "v28_successor_live_pnl_research_decision_log_latest.md"
SOURCE_CONTRACT_JSON = EDGE_DIR / "v28_successor_live_pnl_source_contract_latest.json"
VERIFIER_JSON = EDGE_DIR / "v28_successor_live_pnl_verifier_latest.json"
CAPTURE_HEALTH_JSON = EDGE_DIR / "v28_successor_live_pnl_capture_health_latest.json"
FILL_MODEL_AUDIT_JSON = EDGE_DIR / "v28_successor_live_pnl_fill_model_audit_latest.json"
EXPERIMENT_LEDGER_CSV = EDGE_DIR / "v28_successor_live_pnl_policy_experiment_ledger_latest.csv"
TEST_RUN_JSON = EDGE_DIR / "v28_successor_live_pnl_test_run_latest.json"

EPS = 1e-9


DEFAULT_POLICY_SPEC: dict[str, Any] = {
    "policy_id": "v28s_live_pnl_midband_no_fade_yes_v019",
    "policy_family": "inspectable_rule_surface",
    "policy_version": 19,
    "plain_english_rule": (
        "Use v28's failed cheap-NO clusters as an inspectable fade signal. "
        "Enter one shadow YES contract only on the selected "
        "v28s_boundary_monotonic_light_v001 YES row when the same-timestamp NO "
        "row has v28 fee-adjusted NO edge of at least 5c, that NO ask is below "
        "45c, the visible YES ask is between 65c and 80c, the row is frozen "
        "between five and fifteen minutes before close, and basic book/spot "
        "freshness and fillability gates pass. Skip all NO-side rows, all other "
        "candidate-model rows, YES asks outside the 65c-80c band, and books "
        "wider than 30c. Allow at most one post-hash policy entry per market. "
        "v019 replaces v018 because v018 was correctly causal and lossless but "
        "still produced no entries, while fresh live-forward labels showed two "
        "YES-settled markets where the paired cheap-NO fade trigger appeared in "
        "the 65c-74c region before later high-ask confirmation. The new band "
        "keeps the diagnostic 80c ceiling, avoids the known 80s/90s expansion "
        "damage, and tests whether the live tape is asking for earlier mid-band "
        "YES entry rather than a narrower expensive-only confirmation. Only "
        "post-v019-hash rows may count as primary proof."
    ),
    "parameters": {
        "primary_entry_edge_source": "v28_low_ask_no_fade_yes_signal",
        "candidate_id_filter": ["v28s_boundary_monotonic_light_v001"],
        "allowed_policy_sides": ["yes"],
        "base_min_policy_net_edge_after_fees_cents": 5.0,
        "max_policy_entries_per_market": 1,
        "fade_trigger_no_v28_min_net_edge_cents": 5.0,
        "fade_trigger_no_max_ask_cents": 45.0,
        "base_min_successor_net_edge_after_fees_cents": 0.0,
        "reference_v28_min_net_edge_after_fees_cents": 2.0,
        "successor_fv_only_min_net_edge_after_fees_cents": 0.0,
        "book_only_min_net_edge_after_fees_cents": 2.0,
        "slippage_buffer_cents": 0.25,
        "min_seconds_to_close": 300.0,
        "max_seconds_to_close": 900.0,
        "min_ask_cents": 65.0,
        "max_ask_cents": 80.0,
        "max_book_width_cents": 30.0,
        "max_btc_tick_age_ms": 180000.0,
        "max_abs_v28_d_sigma": 3.5,
        "book_confirmed_no_min_ask_cents": 90.0,
        "book_confirmed_no_min_edge_after_fees_cents": 3.0,
        "book_confirmed_no_min_seconds_to_close": 240.0,
        "opposing_veto_candidate_id": "",
        "opposing_veto_side": "yes",
        "opposing_veto_applies_to_sides": [],
        "opposing_veto_min_net_edge_cents": 35.0,
        "opposing_veto_book_confirm_min_ask_cents": 80.0,
        "near_boundary_abs_d_sigma": 0.35,
        "near_boundary_extra_edge_cents": 0.0,
        "late_seconds_to_close": 120.0,
        "late_extra_edge_cents": 0.0,
        "stale_btc_age_ms": 60000.0,
        "stale_btc_extra_edge_cents": 0.0,
        "min_book_source_event_count": 1,
    },
    "fill_model": {
        "fill_model_id": "one_contract_visible_taker_ask_hold_to_settlement_v001",
        "contract_count": 1,
        "entry_price": "visible side ask cents",
        "exit_policy": "hold_to_settlement",
        "fee_model": "conservative local v28 taker fee: ceil(0.07*C*P*(1-P)) to whole cents",
        "fee_source_urls": [
            "https://kalshi.com/docs/kalshi-fee-schedule.pdf",
            "https://kalshi.com/fee-schedule",
            "https://docs.kalshi.com/getting_started/fee_rounding",
        ],
        "maker_credit": "not assumed",
        "position_sizing": "unit normalized; exactly one shadow contract",
    },
    "diagnostic_origin": {
        "retired_policies": [
            {
                "policy_id": "v28s_live_pnl_v28_boundary_abstention_v002",
                "policy_hash": "72c5a3308492baad1240df244176259c",
                "status": "retired_diagnostic_underperformed_v28",
                "decision": "retire_and_replace",
                "reason": "v002 matched regular v28 on the first primary forward market and lost money; scoring also revealed repeated per-candidate rows could overstate opportunity count",
            },
            {
                "policy_id": "v28s_live_pnl_yes_residual_tilt_v003",
                "policy_hash": "a73acc599c08a24aa947d2e92105d1f9",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "retire_or_replace_before_next_forward_credit",
                "reason": "v003 produced positive delta versus regular v28 on its first settled live-forward market, but absolute primary net P&L was -6 cents",
            },
            {
                "policy_id": "v28s_live_pnl_preclose_yes_residual_tilt_v004",
                "policy_hash": "8e8c05685b02648ac0085d46cbb68e9e",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "retire_or_replace_before_next_forward_credit",
                "reason": "v004 produced positive delta versus regular v28 but lost -41 cents absolute net P&L on two pre-five-minute cheap YES entries",
            },
            {
                "policy_id": "v28s_live_pnl_mature_yes_residual_tilt_v005",
                "policy_hash": "05e6d861831d551c1f7a30cc79a2645b",
                "status": "retired_no_entry_standdown_not_pnl_proof",
                "decision": "replace_for_more_active_existing_candidate",
                "reason": "v005 avoided v28 losses but produced zero entries and zero absolute P&L across its first settled live-forward rows",
            },
            {
                "policy_id": "v28s_live_pnl_no_monotonic_tabular_v006",
                "policy_hash": "e7101b160ec3584ae935c2e67dd1611c",
                "status": "retired_no_entry_negative_delta",
                "decision": "replace_with_existing_light_boundary_no_surface",
                "reason": "v006 produced zero entries and 0c absolute P&L across its first 10 joined primary rows, but underperformed regular v28 by -16.9c by skipping two v28 NO winners",
            },
            {
                "policy_id": "v28s_live_pnl_boundary_light_no_v007",
                "policy_hash": "3353691227124e31f31a99d85a1fbe08",
                "status": "retired_failed_primary_forward_pnl",
                "decision": "replace_with_opposing_yes_physics_veto",
                "reason": "v007 entered three post-hash NO rows in the 12:15Z market and lost all three, producing -197c net P&L with no delta versus regular v28",
            },
            {
                "policy_id": "v28s_live_pnl_boundary_light_no_yes_veto_v008",
                "policy_hash": "fcd2522f32fb964be1c73d05065bbddc",
                "status": "retired_no_entry_negative_delta",
                "decision": "replace_with_lower_book_confirmation_veto",
                "reason": "v008 produced zero entries across its first four joined primary rows and underperformed regular v28 by -28c because its 90c veto skipped two 12:45Z NO winners",
            },
            {
                "policy_id": "v28s_live_pnl_boundary_light_no_yes_veto_v009",
                "policy_hash": "52348ef71e1632c84df63d85e131e391",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "retire_or_replace_before_next_forward_credit",
                "reason": "v009 entered one post-hash NO row at 29c with only 2.38c net edge and lost, leaving primary net P&L -31c and delta versus regular v28 -17.2c across five labeled primary rows",
            },
            {
                "policy_id": "v28s_live_pnl_boundary_light_no_strict_selective_v010",
                "policy_hash": "4f104f77a3241febdaa2abb3dbff7ffc",
                "status": "replace_required_failed_primary_forward_delta",
                "decision": "replace_with_book_confirmed_late_high_ask_repair",
                "reason": "v010 was positive absolute P&L at +15.6c but underperformed regular v28 by -7.3c after skipping a late 91.7c NO winner that v28 entered",
            },
            {
                "policy_id": "v28s_live_pnl_boundary_light_book_confirmed_v011",
                "policy_hash": "eff64a606862ecb60a47d5003b8c4284",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "replace_no_loss_filter_with_yes_boundary_physics_entry",
                "reason": "v011 produced strong positive delta versus regular v28 by skipping a cluster of v28 NO losses, but its two actual post-hash primary NO entries both lost in the 15:00Z market, leaving absolute primary net P&L -73c despite +1076.6c delta versus v28",
            },
            {
                "policy_id": "v28s_live_pnl_yes_boundary_physics_reversal_v012",
                "policy_hash": "54444ab3221556f12d9155ab3c6ac81b",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "add_one_entry_per_market_loss_cluster_cap",
                "reason": "v012 entered six post-hash YES rows in its first market and lost all six, producing -124c net P&L and -124c delta versus regular v28; the failure was primarily repeated exposure to one false market-level signal, not six independent errors",
            },
            {
                "policy_id": "v28s_live_pnl_yes_boundary_physics_one_entry_v013",
                "policy_hash": "85c66e12bc23d6fbe6ea08cd34229636",
                "status": "replace_required_cap_counted_pre_hash_diagnostic_rows",
                "decision": "fix_market_cap_to_ignore_pre_hash_rows",
                "reason": "v013 correctly added a one-entry-per-market cap, but the first capture showed a code-level evidence bug: pre-hash diagnostic rows in the same market consumed the cap and caused all post-hash primary rows to be skipped as market_entry_cap_reached",
            },
            {
                "policy_id": "v28s_live_pnl_yes_boundary_physics_one_entry_v014",
                "policy_hash": "da15088eaae5a2a480104fb794825135",
                "status": "replace_required_failed_primary_forward_pnl",
                "decision": "replace_yes_physics_with_existing_book_reliability_no_surface",
                "reason": "v014 correctly limited exposure to one YES boundary-physics entry, but its first post-hash market still lost -20c net and -20c versus regular v28, confirming that the issue was not only repeated exposure but a false-positive surface in the fresh regime",
            },
            {
                "policy_id": "v28s_live_pnl_no_book_reliability_one_entry_v015",
                "policy_hash": "480e4638220b4ad8665bd71202705023",
                "status": "replace_required_no_entry_negative_delta",
                "decision": "replace_with_capped_high_ask_v28_feature_policy",
                "reason": "v015 produced two finalized post-hash markets with 36 labeled primary rows, zero entries, zero absolute P&L, and -53c delta versus regular v28 after skipping profitable v28 NO entries",
            },
            {
                "policy_id": "v28s_live_pnl_v28_high_ask_no_one_entry_v016",
                "policy_hash": "b5a6dc41cd93755fcc0d1a87287dc511",
                "status": "retired_no_entry_standdown_not_pnl_proof",
                "decision": "replace_loss_filter_with_complementary_yes_fade",
                "reason": "v016 produced three finalized post-hash markets with 53 labeled primary rows, zero entries, zero absolute P&L, and +831c delta versus regular v28 by avoiding cheap-NO loss clusters; useful filter behavior, but still no profit engine",
            },
            {
                "policy_id": "v28s_live_pnl_low_ask_v28_no_fade_yes_v017",
                "policy_hash": "897d5b3679d55d62e330ed95bf079ca1",
                "status": "retired_no_entry_standdown_not_pnl_proof",
                "decision": "replace_with_expensive_confirmed_yes_fade_band",
                "reason": "v017 produced three finalized post-hash markets with 24 labeled primary rows, zero entries, zero absolute P&L, and +49c delta versus regular v28; it avoided one 62c YES loser but missed later 80c-ish YES winners, showing the 60c cap was too quiet for current live conditions",
            },
            {
                "policy_id": "v28s_live_pnl_expensive_confirmed_no_fade_yes_v018",
                "policy_hash": "375dd20718510cebc1c5c96e268750db",
                "status": "retired_no_entry_standdown_not_pnl_proof",
                "decision": "replace_with_midband_yes_fade_band",
                "reason": "v018 produced two finalized post-hash markets with 36 labeled primary rows, zero entries, zero absolute P&L, and zero delta versus regular v28. Both markets settled YES while v018 rejected every row, first because 65c-74c YES asks were below its 75c floor and later because 82c-99.9c asks were above its 80c ceiling or too close to close. The live tape argues for testing an earlier 65c-80c mid-band entry while preserving the 80c diagnostic ceiling.",
            },
        ],
        "previous_policy_id": "v28s_live_pnl_expensive_confirmed_no_fade_yes_v018",
        "previous_policy_hash": "375dd20718510cebc1c5c96e268750db",
        "problem": "v018 converted v17's too-cheap YES fade into a narrow 75c-80c expensive-confirmed band, but it still produced no entries over two finalized live-forward markets. Fresh labels showed the earliest tradable fade rows at 65c-74c also won, while later 80s/90s rows remained too expensive or too close to close.",
        "solution_families_considered": [
            "one-entry-per-market hard exposure cap",
            "risk-constrained or fractional Kelly sizing",
            "conformal risk-controlled abstention",
            "book/FV disagreement confirmation before entry",
            "Brownian-bridge or first-passage recross filters",
            "late-window cheap-tail hazard filters",
        ],
        "implemented_reason": "the smallest inspectable replacement keeps the same cross-side fade trigger and one-entry cap, lowers only the YES ask floor from 75c to 65c, and keeps the 80c ceiling. Diagnostic one-entry-per-market replay over joined rows favored the 65c-80c, 5c-signal band over broader 80s/90s expansions: +79c across 14 diagnostic entries and +66c across the two newly labeled v018 primary markets, while 65c-85c/90c variants were roughly flat to negative diagnostically. This is not promotion evidence; it is only the reason to freeze v019 before collecting new primary rows.",
        "research_source_urls": [
            "https://arxiv.org/abs/2603.24704",
            "https://arxiv.org/abs/2208.12084",
            "https://arxiv.org/abs/2604.11577",
            "https://arxiv.org/abs/1603.06183",
            "https://arxiv.org/abs/0708.3562",
            "https://arxiv.org/abs/0811.2629",
            "https://aclanthology.org/2021.acl-long.84/",
        ],
    },
}


REGISTRY_FIELDS = [
    "policy_decision_id",
    "policy_id",
    "policy_hash",
    "policy_created_utc",
    "policy_registered_utc",
    "allowed_for_primary_live_pnl_evidence",
    "primary_evidence_blockers",
    "evidence_tier",
    "frozen_prediction_id",
    "frozen_utc",
    "row_id",
    "market_ticker",
    "market_close_ts_utc",
    "decision_ts_utc",
    "side",
    "strike",
    "seconds_to_close",
    "candidate_id",
    "candidate_model_hash",
    "candidate_model_type",
    "candidate_model_track",
    "candidate_p_yes",
    "candidate_fair_side_cents",
    "v28_p_yes",
    "v28_fair_side_cents",
    "ask_cents",
    "bid_cents",
    "book_width_cents",
    "book_mid_yes_cents",
    "book_implied_yes_from_side_ask",
    "book_source_event_count",
    "btc_tick_age_ms",
    "btc_stale_flag",
    "v28_d_sigma",
    "abs_v28_d_sigma",
    "v28_sigma_t_dollars",
    "v28_arrow",
    "v28_transport_recent_n",
    "v28_transport_long_n",
    "policy_candidate_selected",
    "entry_fee_cents",
    "slippage_buffer_cents",
    "candidate_gross_edge_cents",
    "candidate_net_edge_after_fees_cents",
    "v28_gross_edge_cents",
    "v28_net_edge_after_fees_cents",
    "book_only_fair_side_cents",
    "book_only_gross_edge_cents",
    "book_only_net_edge_after_fees_cents",
    "policy_signal_edge_source",
    "policy_signal_gross_edge_cents",
    "policy_signal_net_edge_after_fees_cents",
    "opposing_veto_candidate_id",
    "opposing_veto_side",
    "opposing_veto_net_edge_after_fees_cents",
    "opposing_veto_book_confirm_min_ask_cents",
    "opposing_veto_status",
    "dynamic_threshold_cents",
    "policy_action",
    "policy_skip_reason",
    "successor_fv_only_action",
    "successor_fv_only_skip_reason",
    "v28_reference_action",
    "v28_reference_skip_reason",
    "book_only_action",
    "book_only_skip_reason",
    "source_status",
    "source_quality_status",
    "source_quality_blockers",
    "features_used_json",
]


LABELED_FIELDS = REGISTRY_FIELDS + [
    "labeled_row_id",
    "label_join_status",
    "label_join_blockers",
    "y_yes_win",
    "side_win",
    "settlement_price",
    "settlement_margin_dollars",
    "settlement_side",
    "settlement_ts_utc",
    "label_available_ts_utc",
    "settlement_source",
    "policy_gross_pnl_cents",
    "policy_net_pnl_cents",
    "policy_net_pnl_dollars",
    "successor_fv_only_gross_pnl_cents",
    "successor_fv_only_net_pnl_cents",
    "successor_fv_only_net_pnl_dollars",
    "v28_reference_gross_pnl_cents",
    "v28_reference_net_pnl_cents",
    "v28_reference_net_pnl_dollars",
    "book_only_gross_pnl_cents",
    "book_only_net_pnl_cents",
    "book_only_net_pnl_dollars",
    "policy_delta_net_cents_vs_v28",
    "policy_delta_net_cents_vs_successor_fv_only",
    "policy_delta_net_cents_vs_book_only",
    "policy_delta_net_cents_vs_always_skip",
    "policy_outcome",
]


SCORE_FIELDS = [
    "policy_id",
    "policy_hash",
    "slice",
    "rows",
    "markets",
    "entered_rows",
    "skipped_rows",
    "wins",
    "losses",
    "win_rate",
    "net_pnl_cents",
    "net_pnl_dollars",
    "net_cents_per_entered_contract",
    "net_cents_per_observed_row",
    "v28_net_pnl_cents",
    "successor_fv_only_net_pnl_cents",
    "book_only_net_pnl_cents",
    "always_skip_net_pnl_cents",
    "delta_net_cents_vs_v28",
    "delta_net_cents_vs_successor_fv_only",
    "delta_net_cents_vs_book_only",
    "delta_net_cents_vs_always_skip",
    "pct_delta_vs_v28",
    "max_drawdown_cents",
    "worst_loss_streak",
    "remove_best_1_market_net_pnl_cents",
    "market_level_mean_net_cents",
    "market_level_lcb_net_cents",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def as_bool(value: Any) -> bool | None:
    text = str(value or "").strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def fmt_float(value: Any, places: int = 6) -> str:
    parsed = as_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.{places}f}"


def stable_hash(parts: list[Any], length: int = 24) -> str:
    digest = hashlib.sha256()
    for part in parts:
        if isinstance(part, (dict, list)):
            text = json.dumps(part, sort_keys=True, separators=(",", ":"))
        else:
            text = str(part if part is not None else "")
        digest.update(text.encode("utf-8"))
        digest.update(b"\x1f")
    return digest.hexdigest()[:length]


def policy_hash(policy_spec: dict[str, Any]) -> str:
    return stable_hash([policy_spec], length=32)


def existing_policy_created_utc_for_hash(phash: str) -> datetime | None:
    if not POLICY_REGISTRY_JSON.exists():
        return None
    try:
        rows = json.loads(POLICY_REGISTRY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("policy_hash") or "") != phash:
            continue
        created = parse_ts(row.get("policy_created_utc"))
        if created is not None:
            return created
    return None


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
            if limit_rows is not None and len(rows) >= limit_rows:
                break
    return rows


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def estimated_taker_fee_cents(price_cents: Any, count: int = 1) -> int:
    price = as_float(price_cents)
    if price is None:
        return 0
    bounded_price = max(1, min(99, int(round(price))))
    bounded_count = max(1, int(count))
    numerator = 7 * bounded_count * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def fair_side_cents(row: dict[str, Any], prefix: str) -> float | None:
    side = str(row.get("side") or "").strip().lower()
    if prefix == "candidate":
        direct = as_float(row.get("candidate_fair_side_cents"))
        if direct is not None:
            return direct
    yes = as_float(row.get(f"{prefix}_fair_yes_cents"))
    no = as_float(row.get(f"{prefix}_fair_no_cents"))
    if side == "yes":
        return yes
    if side == "no":
        return no
    return None


def book_only_fair_side_cents(row: dict[str, Any]) -> float | None:
    mid_yes = as_float(row.get("book_mid_yes_cents"))
    side = str(row.get("side") or "").strip().lower()
    if mid_yes is None:
        return None
    if side == "yes":
        return mid_yes
    if side == "no":
        return 100.0 - mid_yes
    return None


def packet_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("row_id") or ""),
        str(row.get("candidate_id") or ""),
        str(row.get("model_hash") or row.get("candidate_model_hash") or ""),
        str(row.get("side") or "").lower(),
    )


def packet_index(packet_rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    return {packet_key(row): row for row in packet_rows}


def decision_candidate_key(
    row: dict[str, Any],
    *,
    candidate_id: str | None = None,
    side: str | None = None,
) -> tuple[str, str, str, str]:
    return (
        str(row.get("market_ticker") or ""),
        str(row.get("decision_ts_utc") or ""),
        str(candidate_id if candidate_id is not None else row.get("candidate_id") or ""),
        str(side if side is not None else row.get("side") or "").lower(),
    )


def merged_source_row(frozen: dict[str, Any], packets: dict[tuple[str, str, str, str], dict[str, Any]]) -> dict[str, Any]:
    packet = packets.get(packet_key(frozen), {})
    merged = {**packet, **frozen}
    if "model_hash" in frozen:
        merged["candidate_model_hash"] = frozen.get("model_hash")
    return merged


def source_quality_blockers(row: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    frozen_ts = parse_ts(row.get("frozen_utc"))
    close_ts = parse_ts(row.get("market_close_ts_utc"))
    if decision_ts is None:
        blockers.append("missing_or_bad_decision_ts")
    if frozen_ts is None:
        blockers.append("missing_or_bad_frozen_utc")
    if close_ts is None:
        blockers.append("missing_or_bad_market_close_ts")
    if decision_ts and close_ts and decision_ts >= close_ts:
        blockers.append("decision_not_before_close")
    if frozen_ts and close_ts and frozen_ts >= close_ts:
        blockers.append("freeze_not_before_close")
    if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction":
        blockers.append("source_status_not_frozen_pre_resolution_prediction")
    ask = as_float(row.get("ask_cents"))
    if ask is None:
        blockers.append("missing_ask_cents")
    elif ask <= 0 or ask >= 100:
        blockers.append("ask_outside_tradeable_range")
    if fair_side_cents(row, "candidate") is None:
        blockers.append("missing_candidate_fair_side")
    if fair_side_cents(row, "v28") is None:
        blockers.append("missing_v28_fair_side")
    return blockers


def primary_evidence_blockers(row: dict[str, Any], policy_created: datetime, quality_blockers: list[str]) -> list[str]:
    blockers = list(quality_blockers)
    decision_ts = parse_ts(row.get("decision_ts_utc"))
    if decision_ts and decision_ts < policy_created:
        blockers.append("decision_before_policy_hash_created")
    return blockers


def is_book_confirmed_no_row(row: dict[str, Any], params: dict[str, Any]) -> bool:
    side = str(row.get("side") or "").lower()
    ask = as_float(row.get("ask_cents"))
    min_ask = as_float(params.get("book_confirmed_no_min_ask_cents"))
    return bool(side == "no" and ask is not None and min_ask is not None and ask >= min_ask)


def minimum_seconds_to_close(row: dict[str, Any], params: dict[str, Any]) -> float:
    minimum = float(params["min_seconds_to_close"])
    book_confirmed_minimum = as_float(params.get("book_confirmed_no_min_seconds_to_close"))
    if is_book_confirmed_no_row(row, params) and book_confirmed_minimum is not None:
        return min(minimum, book_confirmed_minimum)
    return minimum


def dynamic_threshold_cents(row: dict[str, Any], params: dict[str, Any]) -> float:
    threshold = float(
        params.get(
            "base_min_policy_net_edge_after_fees_cents",
            params["base_min_successor_net_edge_after_fees_cents"],
        )
    )
    book_confirmed_threshold = as_float(params.get("book_confirmed_no_min_edge_after_fees_cents"))
    if is_book_confirmed_no_row(row, params) and book_confirmed_threshold is not None:
        threshold = min(threshold, book_confirmed_threshold)
    abs_d = as_float(row.get("abs_v28_d_sigma"))
    seconds = as_float(row.get("seconds_to_close"))
    btc_age = as_float(row.get("btc_tick_age_ms"))
    if abs_d is not None and abs_d <= float(params["near_boundary_abs_d_sigma"]):
        threshold += float(params["near_boundary_extra_edge_cents"])
    if seconds is not None and seconds <= float(params["late_seconds_to_close"]):
        threshold += float(params["late_extra_edge_cents"])
    if btc_age is not None and btc_age >= float(params["stale_btc_age_ms"]):
        threshold += float(params["stale_btc_extra_edge_cents"])
    return threshold


def policy_signal_edges(
    candidate_gross_edge: float | None,
    candidate_net_edge: float | None,
    v28_gross_edge: float | None,
    v28_net_edge: float | None,
    params: dict[str, Any],
) -> tuple[str, float | None, float | None]:
    source = str(params.get("primary_entry_edge_source") or "successor_net_edge_after_fees")
    if source == "v28_reference_net_edge_after_fees":
        return source, v28_gross_edge, v28_net_edge
    return source, candidate_gross_edge, candidate_net_edge


def low_ask_no_fade_yes_signal(
    row: dict[str, Any],
    source_lookup: dict[tuple[str, str, str, str], dict[str, Any]],
    params: dict[str, Any],
    *,
    slippage: float,
    contract_count: int,
) -> tuple[str, float | None, float | None]:
    source = "v28_low_ask_no_fade_yes_signal"
    if str(row.get("side") or "").lower() != "yes":
        return source, None, None
    no_row = source_lookup.get(
        decision_candidate_key(
            row,
            candidate_id=str(row.get("candidate_id") or ""),
            side="no",
        )
    )
    if no_row is None:
        return source, None, None
    no_ask = as_float(no_row.get("ask_cents"))
    no_fair = fair_side_cents(no_row, "v28")
    no_fee = estimated_taker_fee_cents(no_ask, count=contract_count) if no_ask is not None else 0
    no_net = None if no_ask is None or no_fair is None else no_fair - no_ask - no_fee - slippage
    max_no_ask = as_float(params.get("fade_trigger_no_max_ask_cents"))
    min_no_edge = as_float(params.get("fade_trigger_no_v28_min_net_edge_cents"))
    if (
        no_net is None
        or no_ask is None
        or max_no_ask is None
        or min_no_edge is None
        or no_ask >= max_no_ask
        or no_net < min_no_edge
    ):
        return source, None, None
    return source, no_net, no_net


def opposing_veto_status(
    *,
    row: dict[str, Any],
    source_lookup: dict[tuple[str, str, str, str], dict[str, Any]],
    params: dict[str, Any],
    slippage: float,
    contract_count: int,
) -> tuple[list[str], dict[str, Any]]:
    veto_candidate = str(params.get("opposing_veto_candidate_id") or "")
    veto_side = str(params.get("opposing_veto_side") or "").lower()
    applies = {str(value).lower() for value in params.get("opposing_veto_applies_to_sides", [])}
    side = str(row.get("side") or "").lower()
    if not veto_candidate or not veto_side or (applies and side not in applies):
        return [], {
            "opposing_veto_candidate_id": veto_candidate,
            "opposing_veto_side": veto_side,
            "opposing_veto_net_edge_after_fees_cents": None,
            "opposing_veto_book_confirm_min_ask_cents": as_float(
                params.get("opposing_veto_book_confirm_min_ask_cents")
            ),
            "opposing_veto_status": "not_applicable",
        }

    opposing = source_lookup.get(decision_candidate_key(row, candidate_id=veto_candidate, side=veto_side))
    book_confirm = as_float(params.get("opposing_veto_book_confirm_min_ask_cents"))
    min_veto_edge = as_float(params.get("opposing_veto_min_net_edge_cents"))
    if opposing is None:
        return [], {
            "opposing_veto_candidate_id": veto_candidate,
            "opposing_veto_side": veto_side,
            "opposing_veto_net_edge_after_fees_cents": None,
            "opposing_veto_book_confirm_min_ask_cents": book_confirm,
            "opposing_veto_status": "missing_opposing_candidate_row",
        }

    opposing_ask = as_float(opposing.get("ask_cents"))
    opposing_fair = fair_side_cents(opposing, "candidate")
    opposing_fee = estimated_taker_fee_cents(opposing_ask, count=contract_count) if opposing_ask is not None else 0
    opposing_net = (
        None
        if opposing_ask is None or opposing_fair is None
        else opposing_fair - opposing_ask - opposing_fee - slippage
    )
    ask = as_float(row.get("ask_cents"))
    vetoed = (
        opposing_net is not None
        and min_veto_edge is not None
        and book_confirm is not None
        and ask is not None
        and opposing_net >= min_veto_edge
        and ask < book_confirm
    )
    status = "blocked_by_opposing_veto" if vetoed else "pass"
    blockers = ["opposing_yes_physics_veto"] if vetoed else []
    return blockers, {
        "opposing_veto_candidate_id": veto_candidate,
        "opposing_veto_side": veto_side,
        "opposing_veto_net_edge_after_fees_cents": opposing_net,
        "opposing_veto_book_confirm_min_ask_cents": book_confirm,
        "opposing_veto_status": status,
    }


def guard_blockers(row: dict[str, Any], params: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    seconds = as_float(row.get("seconds_to_close"))
    ask = as_float(row.get("ask_cents"))
    width = as_float(row.get("book_width_cents"))
    btc_age = as_float(row.get("btc_tick_age_ms"))
    abs_d = as_float(row.get("abs_v28_d_sigma"))
    event_count = as_float(row.get("book_source_event_count"))
    if seconds is None:
        blockers.append("missing_seconds_to_close")
    else:
        if seconds < minimum_seconds_to_close(row, params):
            blockers.append("too_close_to_close")
        if seconds > float(params["max_seconds_to_close"]):
            blockers.append("too_far_from_close_window")
    if ask is None:
        blockers.append("missing_ask_cents")
    else:
        if ask < float(params["min_ask_cents"]):
            blockers.append("ask_too_low")
        if ask > float(params["max_ask_cents"]):
            blockers.append("ask_too_high")
    if width is not None and width > float(params["max_book_width_cents"]):
        blockers.append("book_width_too_wide")
    if btc_age is not None and btc_age > float(params["max_btc_tick_age_ms"]):
        blockers.append("btc_tick_too_stale")
    if abs_d is not None and abs_d > float(params["max_abs_v28_d_sigma"]):
        blockers.append("boundary_distance_extreme")
    if event_count is not None and event_count < float(params["min_book_source_event_count"]):
        blockers.append("insufficient_book_event_count")
    return blockers


def action_from_edge(
    *,
    net_edge: float | None,
    threshold: float,
    blockers: list[str],
    prefix: str,
) -> tuple[str, str]:
    if blockers:
        return "skip", ";".join(blockers)
    if net_edge is None:
        return "skip", f"{prefix}_missing_net_edge"
    if net_edge >= threshold:
        return "enter", ""
    return "skip", f"{prefix}_edge_below_threshold"


def build_policy_registry_rows(
    frozen_rows: list[dict[str, Any]],
    packet_rows: list[dict[str, Any]] | None = None,
    *,
    policy_spec: dict[str, Any] | None = None,
    policy_created_utc: datetime | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    spec = policy_spec or DEFAULT_POLICY_SPEC
    params = spec["parameters"]
    phash = policy_hash(spec)
    created = policy_created_utc or existing_policy_created_utc_for_hash(phash) or utc_now()
    created_text = iso_z(created)
    packets = packet_index(packet_rows or [])
    source_rows = [merged_source_row(frozen, packets) for frozen in frozen_rows]
    source_lookup = {decision_candidate_key(row): row for row in source_rows}
    candidate_filter = {str(value) for value in params.get("candidate_id_filter", [])}
    allowed_policy_sides = {str(value).lower() for value in params.get("allowed_policy_sides", [])}
    registry: list[dict[str, Any]] = []
    source_counter: Counter[str] = Counter()
    blocker_counter: Counter[str] = Counter()
    policy_entries_by_market: Counter[str] = Counter()
    max_entries_per_market = as_float(params.get("max_policy_entries_per_market"))

    for frozen in source_rows:
        row = frozen
        ask = as_float(row.get("ask_cents"))
        candidate_fair = fair_side_cents(row, "candidate")
        v28_fair = fair_side_cents(row, "v28")
        book_fair = book_only_fair_side_cents(row)
        fee = estimated_taker_fee_cents(ask, count=int(spec["fill_model"]["contract_count"])) if ask is not None else 0
        slippage = float(params["slippage_buffer_cents"])
        candidate_gross_edge = None if candidate_fair is None or ask is None else candidate_fair - ask
        candidate_net_edge = None if candidate_gross_edge is None else candidate_gross_edge - fee - slippage
        v28_gross_edge = None if v28_fair is None or ask is None else v28_fair - ask
        v28_net_edge = None if v28_gross_edge is None else v28_gross_edge - fee - slippage
        book_gross_edge = None if book_fair is None or ask is None else book_fair - ask
        book_net_edge = None if book_gross_edge is None else book_gross_edge - fee - slippage
        policy_signal_source, policy_gross_edge, policy_net_edge = policy_signal_edges(
            candidate_gross_edge,
            candidate_net_edge,
            v28_gross_edge,
            v28_net_edge,
            params,
        )
        if str(params.get("primary_entry_edge_source") or "") == "v28_low_ask_no_fade_yes_signal":
            policy_signal_source, policy_gross_edge, policy_net_edge = low_ask_no_fade_yes_signal(
                row,
                source_lookup,
                params,
                slippage=slippage,
                contract_count=int(spec["fill_model"]["contract_count"]),
            )

        v28_d_sigma = as_float(row.get("v28_d_sigma"))
        row["abs_v28_d_sigma"] = "" if v28_d_sigma is None else abs(v28_d_sigma)

        source_blockers = source_quality_blockers(row)
        guard_reasons = guard_blockers(row, params)
        veto_reasons, veto_fields = opposing_veto_status(
            row=row,
            source_lookup=source_lookup,
            params=params,
            slippage=slippage,
            contract_count=int(spec["fill_model"]["contract_count"]),
        )
        side = str(frozen.get("side") or "").lower()
        candidate_id = str(frozen.get("candidate_id") or "")
        selection_blockers: list[str] = []
        if candidate_filter and candidate_id not in candidate_filter:
            selection_blockers.append("candidate_model_not_selected_for_policy")
        if allowed_policy_sides and side not in allowed_policy_sides:
            selection_blockers.append("side_not_allowed_for_policy")
        policy_candidate_selected = not selection_blockers
        threshold = dynamic_threshold_cents(row, params)
        primary_blockers = primary_evidence_blockers(row, created, source_blockers)
        primary_blockers.extend(selection_blockers)
        if primary_blockers:
            evidence_tier = "diagnostic_existing_or_invalid_policy_row"
        else:
            evidence_tier = "frozen_live_incoming_policy_row"
        for blocker in primary_blockers:
            blocker_counter[blocker] += 1

        policy_action, policy_skip = action_from_edge(
            net_edge=policy_net_edge,
            threshold=threshold,
            blockers=source_blockers + guard_reasons + selection_blockers + veto_reasons,
            prefix="policy",
        )
        cap_applies_to_row = not primary_blockers
        if (
            policy_action == "enter"
            and cap_applies_to_row
            and max_entries_per_market is not None
            and policy_entries_by_market[str(frozen.get("market_ticker") or "")] >= int(max_entries_per_market)
        ):
            policy_action = "skip"
            policy_skip = "market_entry_cap_reached"
        elif policy_action == "enter" and cap_applies_to_row:
            policy_entries_by_market[str(frozen.get("market_ticker") or "")] += 1
        successor_action, successor_skip = action_from_edge(
            net_edge=candidate_net_edge,
            threshold=float(params["successor_fv_only_min_net_edge_after_fees_cents"]),
            blockers=source_blockers,
            prefix="successor_fv_only",
        )
        v28_action, v28_skip = action_from_edge(
            net_edge=v28_net_edge,
            threshold=float(params["reference_v28_min_net_edge_after_fees_cents"]),
            blockers=source_blockers,
            prefix="v28_reference",
        )
        book_action, book_skip = action_from_edge(
            net_edge=book_net_edge,
            threshold=float(params["book_only_min_net_edge_after_fees_cents"]),
            blockers=source_blockers,
            prefix="book_only",
        )

        decision_id = stable_hash(
            [
                spec["policy_id"],
                phash,
                frozen.get("frozen_prediction_id"),
                frozen.get("row_id"),
                frozen.get("candidate_id"),
                frozen.get("model_hash"),
                frozen.get("side"),
            ]
        )
        source_quality_status = "pass" if not source_blockers else "blocked"
        source_counter[source_quality_status] += 1

        registry.append(
            {
                "policy_decision_id": decision_id,
                "policy_id": spec["policy_id"],
                "policy_hash": phash,
                "policy_created_utc": created_text,
                "policy_registered_utc": created_text,
                "allowed_for_primary_live_pnl_evidence": str(not primary_blockers),
                "primary_evidence_blockers": ";".join(primary_blockers),
                "evidence_tier": evidence_tier,
                "frozen_prediction_id": frozen.get("frozen_prediction_id", ""),
                "frozen_utc": frozen.get("frozen_utc", ""),
                "row_id": frozen.get("row_id", ""),
                "market_ticker": frozen.get("market_ticker", ""),
                "market_close_ts_utc": frozen.get("market_close_ts_utc", ""),
                "decision_ts_utc": frozen.get("decision_ts_utc", ""),
                "side": side,
                "strike": frozen.get("strike", ""),
                "seconds_to_close": fmt_float(frozen.get("seconds_to_close"), 3),
                "candidate_id": candidate_id,
                "candidate_model_hash": frozen.get("model_hash", ""),
                "candidate_model_type": frozen.get("model_type", ""),
                "candidate_model_track": frozen.get("model_track", ""),
                "candidate_p_yes": fmt_float(frozen.get("candidate_p_yes"), 10),
                "candidate_fair_side_cents": fmt_float(candidate_fair),
                "v28_p_yes": fmt_float(frozen.get("v28_p_yes"), 10),
                "v28_fair_side_cents": fmt_float(v28_fair),
                "ask_cents": fmt_float(ask),
                "bid_cents": fmt_float(row.get("bid_cents")),
                "book_width_cents": fmt_float(row.get("book_width_cents")),
                "book_mid_yes_cents": fmt_float(row.get("book_mid_yes_cents")),
                "book_implied_yes_from_side_ask": fmt_float(row.get("book_implied_yes_from_side_ask"), 10),
                "book_source_event_count": fmt_float(row.get("book_source_event_count"), 0),
                "btc_tick_age_ms": fmt_float(row.get("btc_tick_age_ms"), 3),
                "btc_stale_flag": str(row.get("btc_stale_flag", "")),
                "v28_d_sigma": fmt_float(v28_d_sigma),
                "abs_v28_d_sigma": fmt_float(row.get("abs_v28_d_sigma")),
                "v28_sigma_t_dollars": fmt_float(row.get("v28_sigma_t_dollars")),
                "v28_arrow": fmt_float(row.get("v28_arrow")),
                "v28_transport_recent_n": fmt_float(row.get("v28_transport_recent_n"), 0),
                "v28_transport_long_n": fmt_float(row.get("v28_transport_long_n"), 0),
                "policy_candidate_selected": str(policy_candidate_selected),
                "entry_fee_cents": str(fee),
                "slippage_buffer_cents": fmt_float(slippage),
                "candidate_gross_edge_cents": fmt_float(candidate_gross_edge),
                "candidate_net_edge_after_fees_cents": fmt_float(candidate_net_edge),
                "v28_gross_edge_cents": fmt_float(v28_gross_edge),
                "v28_net_edge_after_fees_cents": fmt_float(v28_net_edge),
                "book_only_fair_side_cents": fmt_float(book_fair),
                "book_only_gross_edge_cents": fmt_float(book_gross_edge),
                "book_only_net_edge_after_fees_cents": fmt_float(book_net_edge),
                "policy_signal_edge_source": policy_signal_source,
                "policy_signal_gross_edge_cents": fmt_float(policy_gross_edge),
                "policy_signal_net_edge_after_fees_cents": fmt_float(policy_net_edge),
                "opposing_veto_candidate_id": veto_fields["opposing_veto_candidate_id"],
                "opposing_veto_side": veto_fields["opposing_veto_side"],
                "opposing_veto_net_edge_after_fees_cents": fmt_float(
                    veto_fields["opposing_veto_net_edge_after_fees_cents"]
                ),
                "opposing_veto_book_confirm_min_ask_cents": fmt_float(
                    veto_fields["opposing_veto_book_confirm_min_ask_cents"]
                ),
                "opposing_veto_status": veto_fields["opposing_veto_status"],
                "dynamic_threshold_cents": fmt_float(threshold),
                "policy_action": policy_action,
                "policy_skip_reason": policy_skip,
                "successor_fv_only_action": successor_action,
                "successor_fv_only_skip_reason": successor_skip,
                "v28_reference_action": v28_action,
                "v28_reference_skip_reason": v28_skip,
                "book_only_action": book_action,
                "book_only_skip_reason": book_skip,
                "source_status": frozen.get("source_status", ""),
                "source_quality_status": source_quality_status,
                "source_quality_blockers": ";".join(source_blockers),
                "features_used_json": json.dumps(
                    {
                        "candidate_net_edge_after_fees_cents": candidate_net_edge,
                        "v28_net_edge_after_fees_cents": v28_net_edge,
                        "book_only_net_edge_after_fees_cents": book_net_edge,
                        "policy_signal_edge_source": policy_signal_source,
                        "policy_signal_net_edge_after_fees_cents": policy_net_edge,
                        "opposing_veto_net_edge_after_fees_cents": veto_fields[
                            "opposing_veto_net_edge_after_fees_cents"
                        ],
                        "opposing_veto_status": veto_fields["opposing_veto_status"],
                        "seconds_to_close": as_float(row.get("seconds_to_close")),
                        "book_width_cents": as_float(row.get("book_width_cents")),
                        "btc_tick_age_ms": as_float(row.get("btc_tick_age_ms")),
                        "abs_v28_d_sigma": as_float(row.get("abs_v28_d_sigma")),
                    },
                    sort_keys=True,
                ),
            }
        )

    summary = {
        "policy_id": spec["policy_id"],
        "policy_hash": phash,
        "policy_created_utc": created_text,
        "rows": len(registry),
        "markets": len({row["market_ticker"] for row in registry if row.get("market_ticker")}),
        "source_quality_counts": dict(source_counter),
        "source_quality_blocker_counts": dict(blocker_counter),
        "primary_evidence_rows": sum(1 for row in registry if row["allowed_for_primary_live_pnl_evidence"] == "True"),
        "diagnostic_rows": sum(1 for row in registry if row["allowed_for_primary_live_pnl_evidence"] != "True"),
        "policy_spec": spec,
    }
    return registry, summary


def label_index(label_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    joined: dict[str, dict[str, Any]] = {}
    for row in label_rows:
        if str(row.get("label_join_status") or "") != "joined_post_resolution":
            continue
        joined[str(row.get("frozen_prediction_id") or "")] = row
    return joined


def side_win_from_label(row: dict[str, Any]) -> float | None:
    y_yes = as_float(row.get("y_yes_win"))
    side = str(row.get("side") or "").strip().lower()
    if y_yes is None:
        return None
    if side == "yes":
        return 1.0 if y_yes >= 0.5 else 0.0
    if side == "no":
        return 0.0 if y_yes >= 0.5 else 1.0
    return None


def pnl_for_action(action: str, side_win: float | None, ask_cents: Any, entry_fee_cents: Any) -> tuple[float, float, str]:
    if action != "enter":
        return 0.0, 0.0, "skipped"
    win = side_win
    ask = as_float(ask_cents)
    fee = as_float(entry_fee_cents) or 0.0
    if win is None or ask is None:
        return 0.0, 0.0, "unscorable"
    payout = 100.0 if win >= 0.5 else 0.0
    gross = payout - ask
    net = gross - fee
    return gross, net, "win" if win >= 0.5 else "loss"


def build_labeled_decision_rows(
    registry_rows: list[dict[str, Any]],
    label_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    labels = label_index(label_rows)
    out: list[dict[str, Any]] = []
    label_status_counts: Counter[str] = Counter()
    for reg in registry_rows:
        label = labels.get(str(reg.get("frozen_prediction_id") or ""))
        merged = dict(reg)
        if label is None:
            merged.update(
                {
                    "labeled_row_id": "",
                    "label_join_status": "missing_label",
                    "label_join_blockers": "missing_settlement_label",
                    "y_yes_win": "",
                    "side_win": "",
                    "settlement_price": "",
                    "settlement_margin_dollars": "",
                    "settlement_side": "",
                    "settlement_ts_utc": "",
                    "label_available_ts_utc": "",
                    "settlement_source": "",
                }
            )
            label_status_counts["missing_label"] += 1
        else:
            side_win = side_win_from_label({**label, "side": reg.get("side")})
            close_ts = parse_ts(reg.get("market_close_ts_utc"))
            label_ts = parse_ts(label.get("label_available_ts_utc"))
            blockers = []
            if str(label.get("label_join_status") or "") != "joined_post_resolution":
                blockers.append("label_status_not_joined_post_resolution")
            if close_ts is None or label_ts is None:
                blockers.append("missing_close_or_label_available_ts")
            elif label_ts <= close_ts:
                blockers.append("label_available_not_after_close")
            merged.update(
                {
                    "labeled_row_id": label.get("labeled_row_id", ""),
                    "label_join_status": "joined_post_resolution" if not blockers else "blocked_label_quality",
                    "label_join_blockers": ";".join(blockers),
                    "y_yes_win": fmt_float(label.get("y_yes_win"), 0),
                    "side_win": "" if side_win is None else fmt_float(side_win, 0),
                    "settlement_price": label.get("settlement_price", ""),
                    "settlement_margin_dollars": label.get("settlement_margin_dollars", ""),
                    "settlement_side": label.get("settlement_side", ""),
                    "settlement_ts_utc": label.get("settlement_ts_utc", ""),
                    "label_available_ts_utc": label.get("label_available_ts_utc", ""),
                    "settlement_source": label.get("settlement_source", ""),
                }
            )
            label_status_counts[merged["label_join_status"]] += 1

        side_win = as_float(merged.get("side_win"))
        policy_gross, policy_net, outcome = pnl_for_action(
            str(merged.get("policy_action") or ""),
            side_win,
            merged.get("ask_cents"),
            merged.get("entry_fee_cents"),
        )
        successor_gross, successor_net, _successor_outcome = pnl_for_action(
            str(merged.get("successor_fv_only_action") or ""),
            side_win,
            merged.get("ask_cents"),
            merged.get("entry_fee_cents"),
        )
        v28_gross, v28_net, _v28_outcome = pnl_for_action(
            str(merged.get("v28_reference_action") or ""),
            side_win,
            merged.get("ask_cents"),
            merged.get("entry_fee_cents"),
        )
        book_gross, book_net, _book_outcome = pnl_for_action(
            str(merged.get("book_only_action") or ""),
            side_win,
            merged.get("ask_cents"),
            merged.get("entry_fee_cents"),
        )
        merged.update(
            {
                "policy_gross_pnl_cents": fmt_float(policy_gross),
                "policy_net_pnl_cents": fmt_float(policy_net),
                "policy_net_pnl_dollars": fmt_float(policy_net / 100.0),
                "successor_fv_only_gross_pnl_cents": fmt_float(successor_gross),
                "successor_fv_only_net_pnl_cents": fmt_float(successor_net),
                "successor_fv_only_net_pnl_dollars": fmt_float(successor_net / 100.0),
                "v28_reference_gross_pnl_cents": fmt_float(v28_gross),
                "v28_reference_net_pnl_cents": fmt_float(v28_net),
                "v28_reference_net_pnl_dollars": fmt_float(v28_net / 100.0),
                "book_only_gross_pnl_cents": fmt_float(book_gross),
                "book_only_net_pnl_cents": fmt_float(book_net),
                "book_only_net_pnl_dollars": fmt_float(book_net / 100.0),
                "policy_delta_net_cents_vs_v28": fmt_float(policy_net - v28_net),
                "policy_delta_net_cents_vs_successor_fv_only": fmt_float(policy_net - successor_net),
                "policy_delta_net_cents_vs_book_only": fmt_float(policy_net - book_net),
                "policy_delta_net_cents_vs_always_skip": fmt_float(policy_net),
                "policy_outcome": outcome,
            }
        )
        out.append(merged)

    summary = {
        "rows": len(out),
        "joined_rows": label_status_counts.get("joined_post_resolution", 0),
        "missing_label_rows": label_status_counts.get("missing_label", 0),
        "pending_or_unjoined_label_rows": label_status_counts.get("missing_label", 0)
        + label_status_counts.get("blocked_label_quality", 0),
        "label_status_counts": dict(label_status_counts),
    }
    return out, summary


def max_drawdown(values: list[float]) -> float:
    peak = 0.0
    equity = 0.0
    max_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return max_dd


def worst_loss_streak(rows: list[dict[str, Any]]) -> int:
    streak = 0
    worst = 0
    for row in rows:
        if str(row.get("policy_action")) != "enter":
            continue
        net = as_float(row.get("policy_net_pnl_cents")) or 0.0
        if net < 0:
            streak += 1
            worst = max(worst, streak)
        elif net > 0:
            streak = 0
    return worst


def lower_confidence_bound(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    stderr = math.sqrt(variance / len(values))
    return mean - 1.64 * stderr


def pct_delta(delta: float, baseline: float) -> str:
    if abs(baseline) < EPS:
        return ""
    return fmt_float(100.0 * delta / abs(baseline), 4)


def score_slice(rows: list[dict[str, Any]], slice_name: str) -> dict[str, Any]:
    entered = [row for row in rows if row.get("policy_action") == "enter"]
    wins = [row for row in entered if (as_float(row.get("policy_net_pnl_cents")) or 0.0) > 0]
    losses = [row for row in entered if (as_float(row.get("policy_net_pnl_cents")) or 0.0) < 0]
    policy_values = [as_float(row.get("policy_net_pnl_cents")) or 0.0 for row in rows]
    v28_values = [as_float(row.get("v28_reference_net_pnl_cents")) or 0.0 for row in rows]
    successor_values = [as_float(row.get("successor_fv_only_net_pnl_cents")) or 0.0 for row in rows]
    book_values = [as_float(row.get("book_only_net_pnl_cents")) or 0.0 for row in rows]
    net = sum(policy_values)
    v28_net = sum(v28_values)
    successor_net = sum(successor_values)
    book_net = sum(book_values)
    always_skip_net = 0.0
    by_market: dict[str, float] = defaultdict(float)
    for row in rows:
        by_market[str(row.get("market_ticker") or "")] += as_float(row.get("policy_net_pnl_cents")) or 0.0
    market_values = list(by_market.values())
    without_best = sorted(market_values, reverse=True)[1:]
    return {
        "policy_id": rows[0].get("policy_id", "") if rows else "",
        "policy_hash": rows[0].get("policy_hash", "") if rows else "",
        "slice": slice_name,
        "rows": len(rows),
        "markets": len({row.get("market_ticker") for row in rows if row.get("market_ticker")}),
        "entered_rows": len(entered),
        "skipped_rows": len(rows) - len(entered),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": fmt_float(len(wins) / len(entered), 4) if entered else "",
        "net_pnl_cents": fmt_float(net),
        "net_pnl_dollars": fmt_float(net / 100.0),
        "net_cents_per_entered_contract": fmt_float(net / len(entered)) if entered else "",
        "net_cents_per_observed_row": fmt_float(net / len(rows)) if rows else "",
        "v28_net_pnl_cents": fmt_float(v28_net),
        "successor_fv_only_net_pnl_cents": fmt_float(successor_net),
        "book_only_net_pnl_cents": fmt_float(book_net),
        "always_skip_net_pnl_cents": fmt_float(always_skip_net),
        "delta_net_cents_vs_v28": fmt_float(net - v28_net),
        "delta_net_cents_vs_successor_fv_only": fmt_float(net - successor_net),
        "delta_net_cents_vs_book_only": fmt_float(net - book_net),
        "delta_net_cents_vs_always_skip": fmt_float(net - always_skip_net),
        "pct_delta_vs_v28": pct_delta(net - v28_net, v28_net),
        "max_drawdown_cents": fmt_float(max_drawdown(policy_values)),
        "worst_loss_streak": worst_loss_streak(rows),
        "remove_best_1_market_net_pnl_cents": fmt_float(sum(without_best)) if without_best else "",
        "market_level_mean_net_cents": fmt_float(sum(market_values) / len(market_values)) if market_values else "",
        "market_level_lcb_net_cents": fmt_float(lower_confidence_bound(market_values)),
    }


def score_labeled_decisions(labeled_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    joined = [row for row in labeled_rows if row.get("label_join_status") == "joined_post_resolution"]
    primary = [row for row in joined if row.get("allowed_for_primary_live_pnl_evidence") == "True"]
    diagnostic = [row for row in joined if row.get("allowed_for_primary_live_pnl_evidence") != "True"]
    scores = [
        score_slice(joined, "all_joined_rows"),
        score_slice(primary, "primary_live_forward_rows_after_policy_hash"),
        score_slice(diagnostic, "diagnostic_rows_not_primary_credit"),
    ]
    summary = {
        "score_status": "scored" if joined else "blocked_no_joined_rows",
        "joined_rows": len(joined),
        "primary_live_forward_rows_after_policy_hash": len(primary),
        "diagnostic_rows_not_primary_credit": len(diagnostic),
        "primary_markets": len({row.get("market_ticker") for row in primary if row.get("market_ticker")}),
        "diagnostic_markets": len({row.get("market_ticker") for row in diagnostic if row.get("market_ticker")}),
        "no_retroactive_credit_enforced": True,
    }
    return scores, summary


def build_capture_health(
    registry_rows: list[dict[str, Any]],
    labeled_rows: list[dict[str, Any]],
    *,
    frozen_csv: Path,
    labeled_csv: Path,
    packets_csv: Path,
) -> dict[str, Any]:
    expected = len(read_csv_rows(frozen_csv))
    captured = len(registry_rows)
    joined = sum(1 for row in labeled_rows if row.get("label_join_status") == "joined_post_resolution")
    closes = [parse_ts(row.get("market_close_ts_utc")) for row in registry_rows]
    closes = [value for value in closes if value is not None]
    return {
        "capture_health_status": "pass_scaffold" if captured == expected and captured > 0 else "blocked_missing_rows",
        "expected_frozen_rows": expected,
        "captured_policy_rows": captured,
        "missed_frozen_rows": max(0, expected - captured),
        "joined_label_rows": joined,
        "observed_markets": len({row.get("market_ticker") for row in registry_rows if row.get("market_ticker")}),
        "latest_market_close_ts_utc": iso_z(max(closes)) if closes else "",
        "input_hashes": {
            "frozen_csv": sha256_file(frozen_csv),
            "labeled_csv": sha256_file(labeled_csv),
            "packets_csv": sha256_file(packets_csv),
        },
        "input_paths": {
            "frozen_csv": rel_path(frozen_csv),
            "labeled_csv": rel_path(labeled_csv),
            "packets_csv": rel_path(packets_csv),
        },
        "note": (
            "This health report accounts for rows available in the current frozen sidecar batch. "
            "It is not a guarantee that every exchange market was observed unless paired with "
            "the market-coverage loop output."
        ),
    }


def build_source_contract(registry_summary: dict[str, Any], label_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_status": "pass_scaffold_primary_blocked_until_future_rows"
        if registry_summary["rows"]
        else "blocked_no_policy_rows",
        "research_only_guardrails": {
            "live_order_logic_touched": False,
            "orders_placed": False,
            "live_bot_process_touched": False,
            "secrets_read": False,
            "account_endpoint_called": False,
        },
        "required_source_rules": {
            "decision_before_close": True,
            "freeze_before_close": True,
            "labels_joined_after_close": True,
            "policy_hash_created_before_primary_credit": True,
            "no_retroactive_credit": True,
        },
        "registry_summary": registry_summary,
        "label_summary": label_summary,
    }


def build_fill_model_audit(policy_spec: dict[str, Any]) -> dict[str, Any]:
    examples = []
    for price in [10, 30, 50, 70, 90]:
        examples.append(
            {
                "price_cents": price,
                "contract_count": 1,
                "estimated_taker_fee_cents": estimated_taker_fee_cents(price, 1),
            }
        )
    return {
        "fill_model_status": "explicit_assumption_report",
        "fill_model": policy_spec["fill_model"],
        "fee_formula": "max(1, ceil(7 * count * price_cents * (100 - price_cents) / 10000))",
        "fee_formula_examples": examples,
        "limitations": [
            "Assumes one whole contract and integer-cent visible taker ask.",
            "Does not assume maker fills, rebates, queue priority, or partial exits.",
            "Does not reconcile actual exchange fills because this is shadow research.",
            "Official fees and product-specific fee schedules can change; refresh before any controlled live test.",
        ],
    }


def build_readiness_report(
    registry_summary: dict[str, Any],
    label_summary: dict[str, Any],
    score_summary: dict[str, Any],
    capture_health: dict[str, Any],
) -> dict[str, Any]:
    test_run_status = "not_found"
    if TEST_RUN_JSON.exists():
        try:
            test_run = json.loads(TEST_RUN_JSON.read_text(encoding="utf-8"))
            test_run_status = str(test_run.get("status") or "unknown")
        except (OSError, json.JSONDecodeError):
            test_run_status = "unreadable"
    primary_policy_rows = int(registry_summary.get("primary_evidence_rows") or 0)
    joined_primary_rows = int(score_summary.get("primary_live_forward_rows_after_policy_hash") or 0)
    primary_markets = int(score_summary.get("primary_markets") or 0)
    checks = [
        {
            "item": "reproducible research-only live policy capture pipeline",
            "status": "pass" if registry_summary["rows"] else "blocked",
            "evidence": "live_pnl_policy_registry_latest.csv",
        },
        {
            "item": "at least one frozen inspectable policy version",
            "status": "pass" if registry_summary.get("policy_hash") else "blocked",
            "evidence": registry_summary.get("policy_hash", ""),
        },
        {
            "item": "frozen pre-resolution policy rows for incoming live markets",
            "status": "pass" if registry_summary["rows"] else "blocked",
            "evidence": f"{registry_summary['rows']} converted frozen FV rows",
        },
        {
            "item": "validation rows occur after policy hash creation",
            "status": "pass" if primary_policy_rows > 0 else "blocked",
            "evidence": f"{primary_policy_rows} captured primary policy rows after hash",
        },
        {
            "item": "post-resolution labels joined after settlement for primary rows",
            "status": "pass" if joined_primary_rows > 0 else "pending_settlement_labels" if primary_policy_rows > 0 else "blocked",
            "evidence": f"{joined_primary_rows} joined primary rows after hash; {label_summary['joined_rows']} total joined diagnostic+primary rows",
        },
        {
            "item": "fee-aware same-row comparison against regular v28 and successor FV-only",
            "status": "pass" if score_summary["joined_rows"] else "blocked",
            "evidence": "v28_successor_live_pnl_policy_score_latest.json",
        },
        {
            "item": "bootstrap sample count of 10 finalized close windows or 25 paired opportunities",
            "status": "pass" if primary_markets >= 10 or joined_primary_rows >= 25 else "blocked",
            "evidence": f"{primary_markets} labeled primary markets, {joined_primary_rows} labeled primary paired opportunities",
        },
        {
            "item": "denominator reporting",
            "status": "pass" if registry_summary["rows"] else "blocked",
            "evidence": "readiness, score, and capture-health reports",
        },
        {
            "item": "source-quality verification",
            "status": "pass",
            "evidence": "v28_successor_live_pnl_source_contract_latest.json",
        },
        {
            "item": "capture-health evidence",
            "status": "pass" if capture_health["captured_policy_rows"] == capture_health["expected_frozen_rows"] else "blocked",
            "evidence": "v28_successor_live_pnl_capture_health_latest.json",
        },
        {
            "item": "fill-model audit or explicit assumptions report",
            "status": "pass",
            "evidence": "v28_successor_live_pnl_fill_model_audit_latest.json",
        },
        {
            "item": "tests for causality, fee math, policy hash freezing, and no retroactive credit",
            "status": "pass" if test_run_status == "pass" else "pending_external_test_run",
            "evidence": f"test_v28_successor_live_pnl_policy_lab.py; test_run_status={test_run_status}",
        },
        {
            "item": "experiment ledger includes failed and deprecated policies",
            "status": "pass",
            "evidence": "v28_successor_live_pnl_policy_experiment_ledger_latest.csv",
        },
        {
            "item": "bootstrap continue/retire/replace report",
            "status": "pass",
            "evidence": "v28_successor_live_pnl_readiness_latest.md",
        },
    ]
    incomplete = [check for check in checks if check["status"] not in {"pass"}]
    verdict = (
        "level_1_bootstrap_complete"
        if not incomplete
        else "not_complete_collect_future_live_rows_after_policy_hash"
    )
    return {
        "readiness_verdict": verdict,
        "level_1_complete": verdict == "level_1_bootstrap_complete",
        "level_2_controlled_live_test_ready": False,
        "primary_policy_rows_after_hash": primary_policy_rows,
        "joined_primary_rows_after_policy_hash": joined_primary_rows,
        "primary_rows_after_policy_hash": joined_primary_rows,
        "primary_markets_after_policy_hash": primary_markets,
        "diagnostic_rows_not_primary_credit": score_summary.get("diagnostic_rows_not_primary_credit", 0),
        "checks": checks,
        "next_actions": [
            "Run the live sidecar policy capture after this policy hash exists.",
            "Score only future rows as primary live-forward policy evidence.",
            "Keep existing pre-policy rows as diagnostic scaffolding only.",
        ],
    }


def primary_score_row(score_rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in score_rows:
        if row.get("slice") == "primary_live_forward_rows_after_policy_hash":
            return row
    return {}


def build_experiment_ledger_row(
    registry_summary: dict[str, Any],
    readiness: dict[str, Any],
    score_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    primary = primary_score_row(score_rows)
    primary_rows = int(readiness.get("primary_rows_after_policy_hash") or 0)
    primary_entered = int(primary.get("entered_rows") or 0)
    net_cents = as_float(primary.get("net_pnl_cents"))
    delta_cents = as_float(primary.get("delta_net_cents_vs_v28"))
    if primary_rows > 0 and primary_entered > 0 and (
        net_cents is None or net_cents <= 0 or delta_cents is None or delta_cents < 0
    ):
        status = "replace_required_failed_primary_forward_pnl"
        decision = "retire_or_replace_before_next_forward_credit"
        reason = (
            f"primary forward evidence failed profitability gates: net_cents={net_cents}, "
            f"delta_vs_v28_cents={delta_cents}"
        )
    elif primary_rows > 0 and primary_entered > 0 and delta_cents == 0:
        status = "active_collect_future_rows_delta_not_positive_yet"
        decision = "continue_collecting_until_positive_delta_or_failure"
        reason = (
            f"primary forward evidence has positive net P&L but zero delta versus regular v28: "
            f"net_cents={net_cents}, delta_vs_v28_cents={delta_cents}"
        )
    elif primary_rows > 0 and primary_entered <= 0:
        status = "active_collect_future_rows_no_entries_yet"
        decision = "continue_collecting_until_policy_entry"
        reason = "post-hash rows are settled but the policy has not entered yet; no-entry avoidance is useful but not proof of positive P&L"
    elif not readiness["level_1_complete"]:
        status = "active_collect_future_rows"
        decision = "continue_collecting_future_live_rows"
        reason = "policy lab scaffold is ready but needs more future rows"
    else:
        status = "bootstrap_complete_collect_profit_evidence"
        decision = "continue_collecting_profit_goal_evidence"
        reason = "bootstrap evidence exists but profit-goal gates still require broader positive forward evidence"
    return {
        "policy_id": registry_summary["policy_id"],
        "policy_hash": registry_summary["policy_hash"],
        "policy_created_utc": registry_summary["policy_created_utc"],
        "status": status,
        "primary_rows_after_policy_hash": readiness["primary_rows_after_policy_hash"],
        "diagnostic_rows_not_primary_credit": readiness["diagnostic_rows_not_primary_credit"],
        "decision": decision,
        "reason": reason,
    }


def build_experiment_ledger_rows(
    registry_summary: dict[str, Any],
    readiness: dict[str, Any],
    score_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    origin = registry_summary.get("policy_spec", {}).get("diagnostic_origin", {})
    retired_policies = origin.get("retired_policies", []) if isinstance(origin, dict) else []
    if retired_policies:
        for retired in retired_policies:
            rows.append(
                {
                    "policy_id": retired.get("policy_id", ""),
                    "policy_hash": retired.get("policy_hash", ""),
                    "policy_created_utc": "",
                    "status": retired.get("status", "retired"),
                    "primary_rows_after_policy_hash": 0,
                    "diagnostic_rows_not_primary_credit": readiness["diagnostic_rows_not_primary_credit"],
                    "decision": retired.get("decision", "retire_and_replace"),
                    "reason": retired.get("reason", ""),
                }
            )
    elif origin:
        rows.append(
            {
                "policy_id": origin.get("previous_policy_id", ""),
                "policy_hash": origin.get("previous_policy_hash", ""),
                "policy_created_utc": "",
                "status": "retired_diagnostic_underperformed_v28",
                "primary_rows_after_policy_hash": 0,
                "diagnostic_rows_not_primary_credit": readiness["diagnostic_rows_not_primary_credit"],
                "decision": "retire_and_replace",
                "reason": origin.get("problem", ""),
            }
        )
    rows.append(build_experiment_ledger_row(registry_summary, readiness, score_rows))
    return rows


def write_markdown_reports(
    *,
    registry_summary: dict[str, Any],
    score_rows: list[dict[str, Any]],
    score_summary: dict[str, Any],
    readiness: dict[str, Any],
    capture_health: dict[str, Any],
    fill_model: dict[str, Any],
) -> None:
    diagnostic_origin = registry_summary.get("policy_spec", {}).get("diagnostic_origin", {})
    primary = primary_score_row(score_rows)
    primary_rows = int(score_summary.get("primary_live_forward_rows_after_policy_hash") or 0)
    primary_entered = int(primary.get("entered_rows") or 0)
    primary_net = as_float(primary.get("net_pnl_cents"))
    primary_delta = as_float(primary.get("delta_net_cents_vs_v28"))
    if primary_rows > 0 and primary_entered > 0 and (
        primary_net is None or primary_net <= 0 or primary_delta is None or primary_delta < 0
    ):
        current_decision = "retire_or_replace_before_next_forward_credit"
        current_reason = (
            f"primary forward evidence failed profitability gates: net_cents={primary_net}, "
            f"delta_vs_v28_cents={primary_delta}"
        )
    elif primary_rows > 0 and primary_entered > 0 and primary_delta == 0:
        current_decision = "continue_collecting_until_positive_delta_or_failure"
        current_reason = (
            f"primary forward evidence is positive net but has zero delta versus regular v28: "
            f"net_cents={primary_net}, delta_vs_v28_cents={primary_delta}"
        )
    elif primary_rows > 0 and primary_entered <= 0:
        current_decision = "continue_collecting_until_policy_entry"
        current_reason = "settled primary rows exist, but the policy has not entered yet; no-entry avoidance is not positive P&L proof"
    else:
        current_decision = "continue_collecting_future_live_rows"
        current_reason = "the lab can produce policy rows, label joins, fee-aware paired P&L, source checks, capture health, and readiness output"
    source_lines = []
    for url in diagnostic_origin.get("research_source_urls", []):
        source_lines.append(f"- {url}")
    BASELINE_MD.write_text(
        "\n".join(
            [
                "# v28 Successor Live P&L Baseline",
                "",
                "Research-only baseline view. No live order logic, state, thresholds, or secrets were changed.",
                "",
                f"- Policy id: `{registry_summary['policy_id']}`",
                f"- Policy hash: `{registry_summary['policy_hash']}`",
                f"- Converted rows: `{registry_summary['rows']}`",
                f"- Primary rows after policy hash: `{score_summary['primary_live_forward_rows_after_policy_hash']}`",
                f"- Diagnostic rows not primary credit: `{score_summary['diagnostic_rows_not_primary_credit']}`",
                "",
                "The baselines here are paired shadow rules using the same row, side, ask, fee, and timestamp: regular v28, successor-FV-only, book-mid-only, and always-skip. They are not live-order mutations.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# v28 Successor Live P&L Policy Score",
        "",
        "Research-only score for the first inspectable live-P&L policy layer.",
        "",
        f"- Score status: `{score_summary['score_status']}`",
        f"- Joined rows: `{score_summary['joined_rows']}`",
        f"- Primary rows after policy hash: `{score_summary['primary_live_forward_rows_after_policy_hash']}`",
        f"- No retroactive credit enforced: `{score_summary['no_retroactive_credit_enforced']}`",
        "",
        "| slice | rows | markets | entered | net cents | v28 net | successor net | book net | skip net | delta vs v28 | max drawdown |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in score_rows:
        lines.append(
            f"| `{row['slice']}` | {row['rows']} | {row['markets']} | {row['entered_rows']} | "
            f"{row['net_pnl_cents']} | {row['v28_net_pnl_cents']} | "
            f"{row['successor_fv_only_net_pnl_cents']} | {row['book_only_net_pnl_cents']} | "
            f"{row['always_skip_net_pnl_cents']} | {row['delta_net_cents_vs_v28']} | {row['max_drawdown_cents']} |"
        )
    lines.extend(
        [
            "",
            "Rows in `diagnostic_rows_not_primary_credit` are deliberately not proof of a forward policy edge when they predate the policy hash.",
        ]
    )
    POLICY_SCORE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    readiness_lines = [
        "# v28 Successor Live P&L Readiness",
        "",
        f"- Verdict: `{readiness['readiness_verdict']}`",
        f"- Level 1 complete: `{readiness['level_1_complete']}`",
        f"- Level 2 controlled-live-test ready: `{readiness['level_2_controlled_live_test_ready']}`",
        f"- Captured primary policy rows after hash: `{readiness['primary_policy_rows_after_hash']}`",
        f"- Joined labeled primary rows after hash: `{readiness['joined_primary_rows_after_policy_hash']}`",
        f"- Diagnostic rows not primary credit: `{readiness['diagnostic_rows_not_primary_credit']}`",
        "",
        "## Checks",
        "",
        "| item | status | evidence |",
        "|---|---|---|",
    ]
    for check in readiness["checks"]:
        readiness_lines.append(f"| {check['item']} | `{check['status']}` | `{check['evidence']}` |")
    readiness_lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "- Run the live sidecar policy capture after this policy hash exists.",
            "- Score only future rows as primary live-forward policy evidence.",
            "- Keep existing pre-policy rows as diagnostic scaffolding only.",
        ]
    )
    READINESS_MD.write_text("\n".join(readiness_lines) + "\n", encoding="utf-8")

    DECISION_LOG_MD.write_text(
        "\n".join(
            [
                "# v28 Successor Live P&L Research Decision Log",
                "",
                "## Bootstrap Policy v002",
                "",
                f"- Policy id: `{registry_summary['policy_id']}`",
                f"- Policy hash: `{registry_summary['policy_hash']}`",
                f"- Decision: `{current_decision}`",
                f"- Reason: {current_reason}.",
                "",
                "## Fee Model Note",
                "",
                f"- Fill model status: `{fill_model['fill_model_status']}`",
                "- Official fee source URLs are recorded in the fill-model audit.",
                f"- Capture health status: `{capture_health['capture_health_status']}`",
                "",
                "## Problem-Solving Research",
                "",
                f"- Problem: {diagnostic_origin.get('problem', 'not recorded')}",
                f"- Implemented: {diagnostic_origin.get('implemented_reason', 'not recorded')}",
                "- Solution families considered: "
                + ", ".join(diagnostic_origin.get("solution_families_considered", [])),
                "",
                "## Research Sources",
                "",
                *(source_lines or ["- not recorded"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def build(
    *,
    frozen_csv: Path = FROZEN_CSV,
    labeled_csv: Path = LABELED_CSV,
    packets_csv: Path = PACKETS_CSV,
    limit_rows: int | None = None,
    policy_created_utc: datetime | None = None,
) -> dict[str, Any]:
    frozen_rows = read_csv_rows(frozen_csv, limit_rows=limit_rows)
    packet_rows = read_csv_rows(packets_csv, limit_rows=None)
    label_rows = read_csv_rows(labeled_csv, limit_rows=None)
    registry_rows, registry_summary = build_policy_registry_rows(
        frozen_rows,
        packet_rows,
        policy_created_utc=policy_created_utc,
    )
    labeled_rows, label_summary = build_labeled_decision_rows(registry_rows, label_rows)
    score_rows, score_summary = score_labeled_decisions(labeled_rows)
    capture_health = build_capture_health(
        registry_rows,
        labeled_rows,
        frozen_csv=frozen_csv,
        labeled_csv=labeled_csv,
        packets_csv=packets_csv,
    )
    source_contract = build_source_contract(registry_summary, label_summary)
    fill_model = build_fill_model_audit(DEFAULT_POLICY_SPEC)
    readiness = build_readiness_report(registry_summary, label_summary, score_summary, capture_health)
    verifier = {
        "verifier_status": "pass_scaffold_primary_evidence_blocked" if registry_rows else "blocked_no_rows",
        "objective": "research-only live-forward P&L lab for v28 successor FV engine",
        "no_live_trading_touched": True,
        "no_retroactive_credit_enforced": True,
        "policy_hash": registry_summary.get("policy_hash", ""),
        "readiness_verdict": readiness["readiness_verdict"],
        "artifacts_checked": [
            rel_path(POLICY_REGISTRY_CSV),
            rel_path(LABELED_DECISIONS_CSV),
            rel_path(POLICY_SCORE_JSON),
            rel_path(READINESS_JSON),
            rel_path(SOURCE_CONTRACT_JSON),
            rel_path(CAPTURE_HEALTH_JSON),
            rel_path(FILL_MODEL_AUDIT_JSON),
        ],
    }
    baseline = {
        "baseline_status": "paired_reference_shadow_built" if registry_rows else "blocked_no_rows",
        "regular_v28_baseline": "v28_reference_shadow_rule_on_same_rows",
        "successor_fv_only_baseline": "successor_fv_only_edge_rule_on_same_rows",
        "book_only_baseline": "book_mid_fair_value_edge_rule_on_same_rows",
        "always_skip_baseline_net_pnl_cents": 0.0,
        "score_summary": score_summary,
    }
    experiment_ledger = build_experiment_ledger_rows(registry_summary, readiness, score_rows) if registry_rows else []
    return {
        "registry_rows": registry_rows,
        "labeled_rows": labeled_rows,
        "score_rows": score_rows,
        "registry_summary": registry_summary,
        "label_summary": label_summary,
        "score_summary": score_summary,
        "baseline": baseline,
        "source_contract": source_contract,
        "capture_health": capture_health,
        "fill_model": fill_model,
        "readiness": readiness,
        "verifier": verifier,
        "experiment_ledger": experiment_ledger,
    }


def write_outputs(bundle: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(bundle["registry_rows"], REGISTRY_FIELDS, POLICY_REGISTRY_CSV)
    POLICY_REGISTRY_JSON.write_text(json.dumps(bundle["registry_rows"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(bundle["labeled_rows"], LABELED_FIELDS, LABELED_DECISIONS_CSV)
    LABELED_DECISIONS_JSON.write_text(json.dumps(bundle["labeled_rows"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(bundle["score_rows"], SCORE_FIELDS, POLICY_SCORE_CSV)
    BASELINE_JSON.write_text(json.dumps(bundle["baseline"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    POLICY_SCORE_JSON.write_text(
        json.dumps(
            {
                "summary": bundle["score_summary"],
                "scores": bundle["score_rows"],
                "registry_summary": bundle["registry_summary"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    READINESS_JSON.write_text(json.dumps(bundle["readiness"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SOURCE_CONTRACT_JSON.write_text(json.dumps(bundle["source_contract"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    VERIFIER_JSON.write_text(json.dumps(bundle["verifier"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CAPTURE_HEALTH_JSON.write_text(json.dumps(bundle["capture_health"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FILL_MODEL_AUDIT_JSON.write_text(json.dumps(bundle["fill_model"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(
        bundle["experiment_ledger"],
        [
            "policy_id",
            "policy_hash",
            "policy_created_utc",
            "status",
            "primary_rows_after_policy_hash",
            "diagnostic_rows_not_primary_credit",
            "decision",
            "reason",
        ],
        EXPERIMENT_LEDGER_CSV,
    )
    write_markdown_reports(
        registry_summary=bundle["registry_summary"],
        score_rows=bundle["score_rows"],
        score_summary=bundle["score_summary"],
        readiness=bundle["readiness"],
        capture_health=bundle["capture_health"],
        fill_model=bundle["fill_model"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write live-P&L policy lab artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional row limit for quick checks.")
    parser.add_argument("--frozen-csv", type=Path, default=FROZEN_CSV)
    parser.add_argument("--labeled-csv", type=Path, default=LABELED_CSV)
    parser.add_argument("--packets-csv", type=Path, default=PACKETS_CSV)
    args = parser.parse_args()
    bundle = build(
        frozen_csv=args.frozen_csv,
        labeled_csv=args.labeled_csv,
        packets_csv=args.packets_csv,
        limit_rows=args.limit_rows,
    )
    if args.write and not args.dry_run:
        write_outputs(bundle)
    print(
        json.dumps(
            {
                "policy_id": bundle["registry_summary"].get("policy_id", ""),
                "policy_hash": bundle["registry_summary"].get("policy_hash", ""),
                "registry_rows": bundle["registry_summary"].get("rows", 0),
                "joined_rows": bundle["label_summary"].get("joined_rows", 0),
                "primary_rows_after_policy_hash": bundle["score_summary"].get(
                    "primary_live_forward_rows_after_policy_hash", 0
                ),
                "diagnostic_rows_not_primary_credit": bundle["score_summary"].get(
                    "diagnostic_rows_not_primary_credit", 0
                ),
                "readiness_verdict": bundle["readiness"].get("readiness_verdict"),
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
