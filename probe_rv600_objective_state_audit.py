from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path("docs/research/RV600_VARIATION_TEST_PLAN.md")
DEFAULT_NOTE = Path("docs/research/RV600_LOCKED_CANDIDATES_2026-05-13.md")
DEFAULT_GOAL_AUDIT = Path("logs/particle_research/reports/rv600_goal_completion_audit_latest.json")
DEFAULT_FUTILITY = Path("logs/particle_research/reports/rv600_forward_futility_latest.json")
DEFAULT_FAMILY = Path("logs/particle_research/reports/rv600_plan_family_rejection_latest.json")
DEFAULT_GRID = Path("logs/particle_research/reports/rv600_variation_forward_grid_latest.json")
DEFAULT_LOCKED = Path("logs/particle_research/reports/rv600_variation_forward_latest.json")
DEFAULT_META_RESCUE = Path("logs/particle_research/reports/rv600_meta_label_rescue_latest.json")
DEFAULT_CALIBRATION_RESCUE = Path("logs/particle_research/reports/rv600_probability_calibration_rescue_latest.json")
DEFAULT_CONFORMAL_RESCUE = Path("logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.json")
DEFAULT_ONLINE_EXPERT_RESCUE = Path("logs/particle_research/reports/rv600_online_expert_rescue_latest.json")
DEFAULT_FAILURE_PATTERN = Path("logs/particle_research/reports/rv600_failure_pattern_audit_latest.json")
DEFAULT_NEXT_EVIDENCE = Path("logs/particle_research/reports/rv600_next_evidence_gate_latest.json")
DEFAULT_SMOKE_AUDIT = Path("logs/particle_research/reports/rv600_shadow_smoke_audit_latest.json")
DEFAULT_BOUNDED_AUDIT = Path("logs/particle_research/reports/rv600_shadow_bounded_audit_latest.json")
DEFAULT_CUMULATIVE_BOUNDED_AUDIT = Path(
    "logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json"
)
DEFAULT_MARKET_BALANCE_RESCUE = Path(
    "logs/particle_research/reports/rv600_market_balance_rescue_latest.json"
)
DEFAULT_REGIME_FILTER_RESCUE = Path(
    "logs/particle_research/reports/rv600_regime_filter_rescue_latest.json"
)
DEFAULT_GROUP_DRO_RESCUE = Path(
    "logs/particle_research/reports/rv600_group_dro_rescue_latest.json"
)
DEFAULT_PBO_STABILITY = Path(
    "logs/particle_research/reports/rv600_pbo_stability_audit_latest.json"
)
DEFAULT_STABILITY_SELECTION_RESCUE = Path(
    "logs/particle_research/reports/rv600_stability_selection_rescue_latest.json"
)
DEFAULT_LOCKED_PLAN_FORWARD_AUDIT = Path(
    "logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.json"
)
DEFAULT_REALITY_CHECK_AUDIT = Path(
    "logs/particle_research/reports/rv600_reality_check_audit_latest.json"
)
DEFAULT_SPA_BENCHMARK_AUDIT = Path(
    "logs/particle_research/reports/rv600_spa_benchmark_audit_latest.json"
)
DEFAULT_PARAMETER_PLATEAU_AUDIT = Path(
    "logs/particle_research/reports/rv600_parameter_plateau_audit_latest.json"
)
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_objective_state_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_objective_state_latest.md")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _status(ok: bool) -> str:
    return "pass" if ok else "fail"


def _row(status: str, requirement: str, evidence: str, next_action: str) -> dict[str, str]:
    return {
        "status": status,
        "requirement": requirement,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    goal = _load_json(args.goal_audit_json)
    futility = _load_json(args.futility_json)
    family = _load_json(args.family_json)
    grid = _load_json(args.grid_json)
    locked = _load_json(args.locked_json)
    meta = _load_json(args.meta_rescue_json)
    calibration = _load_json(args.calibration_rescue_json)
    conformal = _load_json(args.conformal_rescue_json)
    online_expert = _load_json(args.online_expert_rescue_json)
    failure_pattern = _load_json(args.failure_pattern_json)
    next_evidence = _load_json(args.next_evidence_json)
    smoke = _load_json(args.smoke_audit_json)
    bounded = _load_json(args.bounded_audit_json)
    cumulative_bounded = _load_json(args.cumulative_bounded_audit_json)
    market_balance = _load_json(args.market_balance_rescue_json)
    regime_filter = _load_json(args.regime_filter_rescue_json)
    group_dro = _load_json(args.group_dro_rescue_json)
    pbo = _load_json(args.pbo_stability_json)
    stability_selection = _load_json(args.stability_selection_rescue_json)
    locked_plan_forward = _load_json(args.locked_plan_forward_audit_json)
    reality_check = _load_json(args.reality_check_audit_json)
    spa_benchmark = _load_json(args.spa_benchmark_audit_json)
    parameter_plateau = _load_json(args.parameter_plateau_audit_json)
    forward_sample = goal.get("forward_shadow_sample") or {}
    status_counts = goal.get("status_counts") or {}
    family_decision = family.get("decision") or ""
    futility_decision = futility.get("decision") or ""
    grid_summary = family.get("grid") or {}
    meta_aggregate = meta.get("aggregate") or {}
    calibration_aggregate = calibration.get("aggregate") or {}
    conformal_aggregate = conformal.get("aggregate") or {}
    online_expert_aggregate = online_expert.get("aggregate") or {}
    failure_grid = failure_pattern.get("grid") or {}
    bounded_summary = bounded.get("summary") or {}
    cumulative_bounded_summary = cumulative_bounded.get("summary") or {}
    market_balance_counts = market_balance.get("counts") or {}
    market_balance_prequential = market_balance.get("prequential") or {}
    market_balance_best = market_balance.get("best_market_balanced_row") or {}
    regime_filter_prequential = regime_filter.get("prequential") or {}
    regime_filter_best = regime_filter.get("best_row") or {}
    group_dro_prequential = group_dro.get("prequential") or {}
    group_dro_best = group_dro.get("best_row") or {}
    stability_selection_aggregate = stability_selection.get("selected_test_aggregate") or {}
    locked_plan_forward_primary = locked_plan_forward.get("primary_summary") or {}
    next_active_plan = next_evidence.get("active_locked_plan") or {}
    next_plan_id = next_active_plan.get("plan_id")
    locked_plan_forward_plan_id = locked_plan_forward.get("plan_id")
    locked_plan_alignment_ok = bool(next_plan_id) and next_plan_id == locked_plan_forward_plan_id
    reality_best_delta = reality_check.get("best_by_matched_v28_delta") or {}
    spa_best = spa_benchmark.get("best_by_spa_stat") or {}
    spa_bootstrap = spa_benchmark.get("bootstrap") or {}
    parameter_plateau_best = (parameter_plateau.get("best_plateaus") or [{}])[0]
    parameter_plateau_center = parameter_plateau_best.get("center") or {}

    checklist: list[dict[str, str]] = []
    checklist.append(
        _row(
            _status(args.plan.exists()),
            "Named RV600 plan is the source artifact",
            f"{args.plan} exists={args.plan.exists()}",
            "Keep future RV600 work tied to this plan or explicitly document a new plan revision.",
        )
    )
    checklist.append(
        _row(
            _status(args.note.exists()),
            "Research note records decisions, blockers, and modeling choices",
            f"{args.note} exists={args.note.exists()}",
            "Keep appending material decisions and generated report paths to the note.",
        )
    )
    checklist.append(
        _row(
            _status(bool(grid) and _int(grid.get("variant_count")) >= 3948),
            "Plan-defined variants were built and scored",
            f"grid={args.grid_json}; variant_count={grid.get('variant_count')}; phase={grid.get('phase')}",
            "Refresh the grid only after adding new settled forward evidence or a documented new candidate family.",
        )
    )
    checklist.append(
        _row(
            _status(bool(locked) and {"all_entries", "one_per_side_per_market", "position_capped"}.issubset({row.get("accounting_mode") for row in locked.get("summary_rows", [])})),
            "Fair repeated-entry accounting exists",
            f"locked_report={args.locked_json}; accounting_modes={sorted({row.get('accounting_mode') for row in locked.get('summary_rows', [])})}",
            "Do not assess any candidate without all_entries, one_per_side_per_market, and position_capped accounting.",
        )
    )
    checklist.append(
        _row(
            _status(bool(locked) and all("matched_v28_control_pnl_cents" in row for row in locked.get("summary_rows", []))),
            "Matched v28/current controls are scored on accepted timestamps",
            f"locked_report={args.locked_json}; summary_rows={len(locked.get('summary_rows', []))}",
            "Keep matched-v28 delta in locked, forward, and prequential reports.",
        )
    )
    checklist.append(
        _row(
            _status(goal.get("goal_complete") is True),
            "Objective completion audit is green",
            f"goal_complete={goal.get('goal_complete')}; status_counts={status_counts}",
            "Do not call update_goal until this audit is green and independently consistent with the prompt.",
        )
    )
    checklist.append(
        _row(
            _status(_int(forward_sample.get("accepted_entries")) >= 100),
            "Forward shadow has at least 100 accepted entries",
            f"accepted_entries={forward_sample.get('accepted_entries')}",
            "Collect future shadow only for a newly frozen candidate; the current family is rejected.",
        )
    )
    checklist.append(
        _row(
            _status(_int(forward_sample.get("distinct_markets")) >= 40),
            "Forward shadow has at least 40 distinct markets",
            f"distinct_markets={forward_sample.get('distinct_markets')}; native_distinct_markets={forward_sample.get('native_distinct_markets')}",
            "Require native continuous evidence, not sparse sidecar-only evidence.",
        )
    )
    checklist.append(
        _row(
            _status(_int(forward_sample.get("calendar_days")) >= 10 and _int(forward_sample.get("weekend_days")) >= 2),
            "Forward shadow spans at least 10 calendar days and two weekend sessions",
            f"calendar_days={forward_sample.get('calendar_days')}; weekend_days={forward_sample.get('weekend_days')}",
            "A future candidate needs multi-day and weekend evidence before any live pilot.",
        )
    )
    checklist.append(
        _row(
            _status(_float(forward_sample.get("selected_pnl_cents")) > 0.0),
            "Forward selected PnL is positive after fees/fills",
            f"selected_pnl_cents={forward_sample.get('selected_pnl_cents')}; avg_entry={forward_sample.get('avg_pnl_per_entry_cents')}",
            "Reject or refreeze; do not continue the current family for promotion.",
        )
    )
    checklist.append(
        _row(
            _status(_float(forward_sample.get("selected_pnl_cents")) > 1.2 * max(0.0, _float(forward_sample.get("matched_v28_control_pnl_cents")))),
            "Forward selected PnL beats matched v28 by at least 20 percent",
            f"selected_pnl_cents={forward_sample.get('selected_pnl_cents')}; matched_v28_control_pnl_cents={forward_sample.get('matched_v28_control_pnl_cents')}",
            "Require positive matched-control edge for any new frozen candidate.",
        )
    )
    checklist.append(
        _row(
            _status(futility_decision != "reject_current_locked_family_for_promotion"),
            "Current locked family is not rejected by futility analysis",
            f"futility_decision={futility_decision}; reasons={futility.get('reasons')}",
            "Stop collecting the rejected family by itself; only continue with a newly frozen candidate.",
        )
    )
    checklist.append(
        _row(
            _status(family_decision != "no_existing_plan_family_viable"),
            "At least one plan-defined family remains viable on expanded forward grid",
            f"family_decision={family_decision}; grid_variant_count={grid_summary.get('variant_count')}; promotion_allowed={grid_summary.get('promotion_allowed')}",
            "No existing plan-defined replacement is viable; a new candidate requires a documented plan update and fresh locked/forward gates.",
        )
    )
    checklist.append(
        _row(
            _status(meta_aggregate.get("preliminary_gate_pass") is True),
            "Literature-backed meta-label rescue has a prequential gate pass",
            f"meta_report={args.meta_rescue_json}; preliminary_gate_pass={meta_aggregate.get('preliminary_gate_pass')}; train_gate_selection_count={meta_aggregate.get('train_gate_selection_count')}; test_selected_pnl_cents={meta_aggregate.get('test_selected_pnl_cents')}; rejection_reason={meta_aggregate.get('rejection_reason')}",
            "Treat the meta-label result as a rejection unless it produces prior-root gate passes and positive next-root PnL under the same anti-overfitting gates.",
        )
    )
    checklist.append(
        _row(
            _status(calibration_aggregate.get("preliminary_gate_pass") is True),
            "Literature-backed probability-calibration rescue has a prequential gate pass",
            f"calibration_report={args.calibration_rescue_json}; preliminary_gate_pass={calibration_aggregate.get('preliminary_gate_pass')}; train_gate_selection_count={calibration_aggregate.get('train_gate_selection_count')}; test_selected_pnl_cents={calibration_aggregate.get('test_selected_pnl_cents')}; test_matched_v28_delta_cents={calibration_aggregate.get('test_matched_v28_delta_cents')}; rejection_reason={calibration_aggregate.get('rejection_reason')}",
            "Treat the calibration result as rejected unless prior-root calibration gates pass and next-root PnL is positive with matched-v28 edge.",
        )
    )
    checklist.append(
        _row(
            _status(conformal_aggregate.get("preliminary_gate_pass") is True),
            "Literature-backed conformal-abstention rescue has a prequential gate pass",
            f"conformal_report={args.conformal_rescue_json}; preliminary_gate_pass={conformal_aggregate.get('preliminary_gate_pass')}; train_gate_selection_count={conformal_aggregate.get('train_gate_selection_count')}; test_total_entries={conformal_aggregate.get('test_total_entries')}; test_selected_pnl_cents={conformal_aggregate.get('test_selected_pnl_cents')}; rejection_reason={conformal_aggregate.get('rejection_reason')}",
            "Treat conformal abstention as rejected unless it produces enough next-root accepted entries with positive PnL and matched-v28 edge.",
        )
    )
    checklist.append(
        _row(
            _status(online_expert_aggregate.get("preliminary_gate_pass") is True),
            "Literature-backed online-expert rescue has a prequential gate pass",
            f"online_expert_report={args.online_expert_rescue_json}; preliminary_gate_pass={online_expert_aggregate.get('preliminary_gate_pass')}; train_gate_selection_count={online_expert_aggregate.get('train_gate_selection_count')}; test_total_entries={online_expert_aggregate.get('test_total_entries')}; test_selected_pnl_cents={online_expert_aggregate.get('test_selected_pnl_cents')}; test_matched_v28_delta_cents={online_expert_aggregate.get('test_matched_v28_delta_cents')}; rejection_reason={online_expert_aggregate.get('rejection_reason')}",
            "Treat the expert-weighted result as rejected unless prior-root selected experts pass gates and next-root PnL is positive with matched-v28 edge.",
        )
    )
    checklist.append(
        _row(
            _status(failure_pattern.get("plan_revision_supported") is True),
            "Failure-pattern audit supports a narrow plan revision or new frozen candidate",
            f"failure_pattern_report={args.failure_pattern_json}; decision={failure_pattern.get('decision')}; support_row_count={failure_grid.get('support_row_count')}; rescue_gate_pass_count={(failure_pattern.get('rescues') or {}).get('gate_pass_count')}",
            "Do not mine the same sample further unless this audit finds support rows, a rescue gate pass, or materially new shadow evidence.",
        )
    )
    checklist.append(
        _row(
            _status(next_evidence.get("ready_for_bounded_shadow_collection") is True),
            "Next-evidence gate is ready for bounded research-only shadow collection",
            f"next_evidence_report={args.next_evidence_json}; decision={next_evidence.get('decision')}; ready={next_evidence.get('ready_for_bounded_shadow_collection')}",
            "Only collect new evidence with the bounded passive command; do not restart live v28, change live logic, or place trades.",
        )
    )
    checklist.append(
        _row(
            _status(locked_plan_alignment_ok),
            "Next-evidence gate and locked-plan forward audit reference the same frozen RV600 plan",
            f"next_evidence_plan_id={next_plan_id}; locked_plan_forward_plan_id={locked_plan_forward_plan_id}; next_evidence_plan_path={next_active_plan.get('path')}; locked_plan_forward_plan_json={locked_plan_forward.get('plan_json')}",
            "Refresh the gate and locked-plan forward audit with the same latest RV600 locked plan before collecting or judging more forward evidence.",
        )
    )
    locked_plan_forward_pass = locked_plan_forward.get("decision") == "locked_plan_forward_gate_pass"
    checklist.append(
        _row(
            _status(locked_plan_forward_pass),
            "Frozen locked plan clears post-registration forward gates",
            f"locked_plan_forward_report={args.locked_plan_forward_audit_json}; decision={locked_plan_forward.get('decision')}; root_count={locked_plan_forward.get('root_count')}; accepted_entries={locked_plan_forward_primary.get('accepted_entries')}; distinct_markets={locked_plan_forward_primary.get('distinct_markets')}; selected_pnl_cents={locked_plan_forward_primary.get('selected_pnl_cents')}; matched_v28_delta_cents={locked_plan_forward_primary.get('matched_v28_delta_cents')}; avg_entry={locked_plan_forward_primary.get('avg_pnl_per_entry_cents')}; rejection_reason={locked_plan_forward_primary.get('rejection_reason')}",
            "Keep future-only evidence separate from pre-freeze diagnostics; reject or keep observing the frozen plan without tuning thresholds from its outcomes.",
        )
    )
    smoke_summary = smoke.get("summary") or {}
    checklist.append(
        _row(
            _status(smoke.get("decision") == "smoke_scored_no_rv600_entries"),
            "Bounded next-evidence smoke run completed and scored",
            f"smoke_report={args.smoke_audit_json}; decision={smoke.get('decision')}; candidate_rows={smoke_summary.get('candidate_rows')}; settled_markets={smoke_summary.get('settled_markets')}; locked_total_entries={smoke_summary.get('locked_total_entries')}",
            "Treat the smoke as pipeline validation only; it is far below completion sample and produced zero accepted RV600 entries.",
        )
    )
    bounded_supports_continuation = (
        bounded.get("decision") == "bounded_run_scored_with_entries"
        and (
            _float(bounded_summary.get("locked_total_pnl_cents")) > 0.0
            or _float(bounded_summary.get("best_grid_selected_pnl_cents")) > 0.0
        )
        and _float(bounded_summary.get("best_grid_matched_v28_delta_cents")) > 0.0
        and not bounded_summary.get("best_grid_rejection")
    )
    checklist.append(
        _row(
            _status(bounded_supports_continuation),
            "Latest bounded next-evidence run has positive RV600-style shadow evidence that clears gates",
            f"bounded_report={args.bounded_audit_json}; decision={bounded.get('decision')}; candidate_rows={bounded_summary.get('candidate_rows')}; settled_markets={bounded_summary.get('settled_markets')}; locked_total_entries={bounded_summary.get('locked_total_entries')}; locked_total_pnl_cents={bounded_summary.get('locked_total_pnl_cents')}; best_grid_entries={bounded_summary.get('best_grid_accepted_entries')}; best_grid_pnl_cents={bounded_summary.get('best_grid_selected_pnl_cents')}; best_grid_matched_v28_delta_cents={bounded_summary.get('best_grid_matched_v28_delta_cents')}",
            "Use this only as a small fresh-shadow slice; it cannot satisfy the goal without the full sample, concentration, and matched-v28 gates.",
        )
    )
    cumulative_bounded_gate_pass = cumulative_bounded.get("decision") == "cumulative_bounded_gate_pass"
    checklist.append(
        _row(
            _status(cumulative_bounded_gate_pass),
            "Cumulative bounded next-evidence shadow clears RV600 gates",
            f"cumulative_report={args.cumulative_bounded_audit_json}; decision={cumulative_bounded.get('decision')}; root_count={cumulative_bounded_summary.get('root_count')}; candidate_rows={cumulative_bounded_summary.get('candidate_rows')}; settled_markets={cumulative_bounded_summary.get('settled_markets')}; locked_total_entries={cumulative_bounded_summary.get('locked_total_entries')}; locked_total_pnl_cents={cumulative_bounded_summary.get('locked_total_pnl_cents')}; best_grid_entries={cumulative_bounded_summary.get('best_grid_accepted_entries')}; best_grid_pnl_cents={cumulative_bounded_summary.get('best_grid_selected_pnl_cents')}; best_grid_matched_v28_delta_cents={cumulative_bounded_summary.get('best_grid_matched_v28_delta_cents')}; best_grid_rejection={cumulative_bounded_summary.get('best_grid_rejection')}",
            "Continue bounded read-only evidence collection or freeze a new candidate only after cumulative evidence clears sample, concentration, and matched-v28 gates.",
        )
    )
    market_balance_pass = market_balance.get("decision") == "market_balance_rescue_pass"
    checklist.append(
        _row(
            _status(market_balance_pass),
            "Market-balance rescue clears concentration and stability gates",
            f"market_balance_report={args.market_balance_rescue_json}; decision={market_balance.get('decision')}; root_count={len(market_balance.get('roots') or [])}; gate_pass_rows={market_balance_counts.get('gate_pass_rows')}; positive_concentration_ok_rows={market_balance_counts.get('positive_concentration_ok_rows')}; positive_both_balance_ok_rows={market_balance_counts.get('positive_both_balance_ok_rows')}; best_variant={market_balance_best.get('variant')}; best_entries={market_balance_best.get('accepted_entries')}; best_pnl_cents={market_balance_best.get('selected_pnl_cents')}; best_rejection={market_balance_best.get('rejection_reason')}; prequential_gate_pass={market_balance_prequential.get('prequential_gate_pass')}; prequential_test_pnl_cents={market_balance_prequential.get('test_selected_pnl_cents')}",
            "Treat current RV600 grid evidence as concentrated until an existing or newly documented candidate clears this rescue and the objective audit.",
        )
    )
    regime_filter_pass = regime_filter.get("decision") == "regime_filter_rescue_pass"
    checklist.append(
        _row(
            _status(regime_filter_pass),
            "Regime-filter rescue clears stability and anchored forward gates",
            f"regime_filter_report={args.regime_filter_rescue_json}; decision={regime_filter.get('decision')}; root_count={len(regime_filter.get('roots') or [])}; predicate_count={regime_filter.get('predicate_count')}; support_row_count={regime_filter.get('support_row_count')}; best_variant={regime_filter_best.get('variant')}; best_entries={regime_filter_best.get('accepted_entries')}; best_pnl_cents={regime_filter_best.get('selected_pnl_cents')}; best_rejection={regime_filter_best.get('rejection_reason')}; prequential_gate_pass={regime_filter_prequential.get('prequential_gate_pass')}; prequential_test_pnl_cents={regime_filter_prequential.get('test_selected_pnl_cents')}; prequential_test_matched_v28_delta_cents={regime_filter_prequential.get('test_matched_v28_delta_cents')}",
            "Treat regime-conditioned filtering as rejected unless it produces a support row and anchored forward validation.",
        )
    )
    group_dro_pass = group_dro.get("decision") == "group_dro_rescue_pass"
    checklist.append(
        _row(
            _status(group_dro_pass),
            "Group-DRO rescue clears worst-root, concentration, and anchored forward gates",
            f"group_dro_report={args.group_dro_rescue_json}; decision={group_dro.get('decision')}; root_count={len(group_dro.get('roots') or [])}; support_row_count={group_dro.get('support_row_count')}; best_variant={group_dro_best.get('variant')}; best_entries={group_dro_best.get('accepted_entries')}; best_pnl_cents={group_dro_best.get('selected_pnl_cents')}; best_lower_tail={group_dro_best.get('lower_tail_root_pnl_cents')}; best_rejection={group_dro_best.get('rejection_reason')}; prequential_gate_pass={group_dro_prequential.get('prequential_gate_pass')}; prequential_test_pnl_cents={group_dro_prequential.get('test_selected_pnl_cents')}; prequential_test_matched_v28_delta_cents={group_dro_prequential.get('test_matched_v28_delta_cents')}",
            "Treat group-DRO selection as rejected unless worst-root support and anchored forward validation both pass.",
        )
    )
    pbo_pass = pbo.get("decision") == "pbo_supports_current_grid"
    checklist.append(
        _row(
            _status(pbo_pass),
            "CSCV/PBO split-rank stability audit supports the current grid",
            f"pbo_report={args.pbo_stability_json}; decision={pbo.get('decision')}; root_count={pbo.get('root_count')}; candidate_count={pbo.get('candidate_count')}; pbo={pbo.get('pbo')}; positive_split_rate={pbo.get('positive_split_rate')}; mean_selected_test_pnl_cents={pbo.get('mean_selected_test_pnl_cents')}",
            "Treat the current grid as overfit-prone until in-sample winners keep above-median out-of-sample rank across root splits.",
        )
    )
    reality_check_pass = reality_check.get("decision") == "reality_check_supports_current_grid"
    checklist.append(
        _row(
            _status(reality_check_pass),
            "Root-bootstrap reality check supports the current grid after data-snooping adjustment",
            f"reality_check_report={args.reality_check_audit_json}; decision={reality_check.get('decision')}; root_count={reality_check.get('root_count')}; candidate_count={reality_check.get('candidate_count')}; best_variant={reality_best_delta.get('variant')}; best_delta_cents={reality_best_delta.get('total_matched_v28_delta_cents')}; mean_p_value={(reality_check.get('mean_reality_check') or {}).get('p_value')}; studentized_p_value={(reality_check.get('studentized_reality_check') or {}).get('p_value')}; best_rejection={reality_best_delta.get('rejection_reason')}",
            "Treat the current grid as data-snooping-rejected unless the best matched-v28 edge survives the root-bootstrap max-statistic test and also clears the normal RV600 gates.",
        )
    )
    spa_benchmark_pass = spa_benchmark.get("decision") == "spa_benchmark_supports_current_grid"
    checklist.append(
        _row(
            _status(spa_benchmark_pass),
            "Superior-predictive-ability benchmark audit supports RV600 versus matched v28",
            f"spa_report={args.spa_benchmark_audit_json}; decision={spa_benchmark.get('decision')}; root_count={spa_benchmark.get('root_count')}; candidate_count={spa_benchmark.get('candidate_count')}; positive_delta_candidate_count={spa_benchmark.get('positive_delta_candidate_count')}; spa_screen_candidate_count={spa_benchmark.get('spa_screen_candidate_count')}; best_variant={spa_best.get('variant')}; best_delta_cents={spa_best.get('total_matched_v28_delta_cents')}; studentized_p_value={spa_bootstrap.get('studentized_p_value')}; best_rejection={spa_best.get('rejection_reason')}",
            "Treat apparent RV600 wins as benchmark-rejected unless at least one candidate beats matched v28 after the SPA-style root bootstrap and normal RV600 gates.",
        )
    )
    stability_selection_pass = stability_selection.get("decision") == "stability_selection_support_found"
    checklist.append(
        _row(
            _status(stability_selection_pass),
            "Stability-selection rescue finds a stable gate-passing RV600 candidate",
            f"stability_selection_report={args.stability_selection_rescue_json}; decision={stability_selection.get('decision')}; root_count={stability_selection.get('root_count')}; candidate_count={stability_selection.get('candidate_count')}; locked_selection_count={stability_selection.get('locked_selection_count')}; full_support_count={stability_selection.get('full_support_count')}; test_selected_pnl_cents={stability_selection_aggregate.get('test_selected_pnl_cents')}; test_avg_pnl_per_entry_cents={stability_selection_aggregate.get('test_avg_pnl_per_entry_cents')}; rejection_reason={stability_selection_aggregate.get('rejection_reason')}",
            "Treat the current grid as unstable unless one simple candidate is repeatedly selected across root subsamples and passes full-sample gates.",
        )
    )
    parameter_plateau_pass = parameter_plateau.get("decision") == "parameter_plateau_support_found"
    checklist.append(
        _row(
            _status(parameter_plateau_pass),
            "Parameter-plateau audit supports a stable RV600 neighborhood",
            f"parameter_plateau_report={args.parameter_plateau_audit_json}; decision={parameter_plateau.get('decision')}; support_count={parameter_plateau.get('support_count')}; best_center={parameter_plateau_center.get('variant')}; best_breadth_ok_rate={parameter_plateau_best.get('breadth_ok_rate')}; best_median_positive_root_rate={parameter_plateau_best.get('median_positive_root_rate')}; best_median_positive_market_rate={parameter_plateau_best.get('median_positive_market_rate')}",
            "Treat isolated high-PnL parameter rows as rejected unless nearby timing-window and EV-threshold variants also retain breadth and matched-v28 edge.",
        )
    )

    fail_count = sum(1 for item in checklist if item["status"] == "fail")
    blocked_by = [
        "current_locked_family_rejected",
        "no_existing_plan_family_viable",
        "forward_shadow_pnl_negative",
        "forward_shadow_sample_incomplete",
        "meta_label_rescue_failed",
        "probability_calibration_rescue_failed",
        "conformal_abstention_rescue_failed",
        "online_expert_rescue_failed",
        "no_current_plan_revision_supported",
        "fresh_shadow_smoke_insufficient",
        "fresh_bounded_shadow_insufficient",
        "cumulative_bounded_shadow_insufficient",
        "market_balance_rescue_failed",
        "regime_filter_rescue_failed",
        "group_dro_rescue_failed",
        "pbo_stability_rejected",
        "reality_check_rejected",
        "spa_benchmark_rejected",
        "stability_selection_rescue_failed",
        "parameter_plateau_rejected",
    ]
    if not locked_plan_forward_pass:
        blocked_by.append("locked_plan_forward_audit_failed")
    objective_complete = fail_count == 0
    decision = "complete" if objective_complete else "blocked_not_complete"
    report = {
        "schema_version": "rv600-objective-state-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "objective_complete": objective_complete,
        "decision": decision,
        "blocked_by": [] if objective_complete else blocked_by,
        "checklist": checklist,
        "summary": {
            "goal_complete": goal.get("goal_complete"),
            "status_counts": status_counts,
            "futility_decision": futility_decision,
            "family_decision": family_decision,
            "grid_variant_count": grid_summary.get("variant_count"),
            "grid_promotion_allowed": grid_summary.get("promotion_allowed"),
            "forward_entries": forward_sample.get("accepted_entries"),
            "forward_markets": forward_sample.get("distinct_markets"),
            "forward_selected_pnl_cents": forward_sample.get("selected_pnl_cents"),
            "matched_v28_control_pnl_cents": forward_sample.get("matched_v28_control_pnl_cents"),
            "meta_rescue_preliminary_gate_pass": meta_aggregate.get("preliminary_gate_pass"),
            "meta_rescue_test_selected_pnl_cents": meta_aggregate.get("test_selected_pnl_cents"),
            "meta_rescue_train_gate_selection_count": meta_aggregate.get("train_gate_selection_count"),
            "calibration_rescue_preliminary_gate_pass": calibration_aggregate.get("preliminary_gate_pass"),
            "calibration_rescue_test_selected_pnl_cents": calibration_aggregate.get("test_selected_pnl_cents"),
            "calibration_rescue_train_gate_selection_count": calibration_aggregate.get("train_gate_selection_count"),
            "conformal_rescue_preliminary_gate_pass": conformal_aggregate.get("preliminary_gate_pass"),
            "conformal_rescue_test_selected_pnl_cents": conformal_aggregate.get("test_selected_pnl_cents"),
            "conformal_rescue_train_gate_selection_count": conformal_aggregate.get("train_gate_selection_count"),
            "online_expert_rescue_preliminary_gate_pass": online_expert_aggregate.get("preliminary_gate_pass"),
            "online_expert_rescue_test_selected_pnl_cents": online_expert_aggregate.get("test_selected_pnl_cents"),
            "online_expert_rescue_train_gate_selection_count": online_expert_aggregate.get("train_gate_selection_count"),
            "failure_pattern_decision": failure_pattern.get("decision"),
            "failure_pattern_support_row_count": failure_grid.get("support_row_count"),
            "failure_pattern_plan_revision_supported": failure_pattern.get("plan_revision_supported"),
            "next_evidence_decision": next_evidence.get("decision"),
            "next_evidence_ready": next_evidence.get("ready_for_bounded_shadow_collection"),
            "next_evidence_plan_id": next_plan_id,
            "locked_plan_alignment_ok": locked_plan_alignment_ok,
            "locked_plan_forward_plan_id": locked_plan_forward_plan_id,
            "locked_plan_forward_variant": locked_plan_forward.get("variant"),
            "locked_plan_forward_single_market_benchmark_variant": locked_plan_forward.get("single_market_benchmark_variant"),
            "locked_plan_forward_decision": locked_plan_forward.get("decision"),
            "locked_plan_forward_root_count": locked_plan_forward.get("root_count"),
            "locked_plan_forward_calendar_day_count": locked_plan_forward.get("calendar_day_count"),
            "locked_plan_forward_weekend_day_count": locked_plan_forward.get("weekend_day_count"),
            "locked_plan_forward_accepted_entries": locked_plan_forward_primary.get("accepted_entries"),
            "locked_plan_forward_distinct_markets": locked_plan_forward_primary.get("distinct_markets"),
            "locked_plan_forward_selected_pnl_cents": locked_plan_forward_primary.get("selected_pnl_cents"),
            "locked_plan_forward_matched_v28_delta_cents": locked_plan_forward_primary.get("matched_v28_delta_cents"),
            "locked_plan_forward_avg_pnl_per_entry_cents": locked_plan_forward_primary.get("avg_pnl_per_entry_cents"),
            "locked_plan_forward_rejection": locked_plan_forward_primary.get("rejection_reason"),
            "smoke_decision": smoke.get("decision"),
            "smoke_candidate_rows": smoke_summary.get("candidate_rows"),
            "smoke_settled_markets": smoke_summary.get("settled_markets"),
            "smoke_locked_total_entries": smoke_summary.get("locked_total_entries"),
            "bounded_decision": bounded.get("decision"),
            "bounded_candidate_rows": bounded_summary.get("candidate_rows"),
            "bounded_settled_markets": bounded_summary.get("settled_markets"),
            "bounded_locked_total_entries": bounded_summary.get("locked_total_entries"),
            "bounded_locked_total_pnl_cents": bounded_summary.get("locked_total_pnl_cents"),
            "bounded_best_grid_accepted_entries": bounded_summary.get("best_grid_accepted_entries"),
            "bounded_best_grid_selected_pnl_cents": bounded_summary.get("best_grid_selected_pnl_cents"),
            "bounded_best_grid_matched_v28_delta_cents": bounded_summary.get("best_grid_matched_v28_delta_cents"),
            "cumulative_bounded_decision": cumulative_bounded.get("decision"),
            "cumulative_bounded_root_count": cumulative_bounded_summary.get("root_count"),
            "cumulative_bounded_candidate_rows": cumulative_bounded_summary.get("candidate_rows"),
            "cumulative_bounded_settled_markets": cumulative_bounded_summary.get("settled_markets"),
            "cumulative_bounded_locked_total_entries": cumulative_bounded_summary.get("locked_total_entries"),
            "cumulative_bounded_locked_total_pnl_cents": cumulative_bounded_summary.get("locked_total_pnl_cents"),
            "cumulative_bounded_best_grid_accepted_entries": cumulative_bounded_summary.get("best_grid_accepted_entries"),
            "cumulative_bounded_best_grid_selected_pnl_cents": cumulative_bounded_summary.get("best_grid_selected_pnl_cents"),
            "cumulative_bounded_best_grid_matched_v28_delta_cents": cumulative_bounded_summary.get("best_grid_matched_v28_delta_cents"),
            "cumulative_bounded_best_grid_rejection": cumulative_bounded_summary.get("best_grid_rejection"),
            "market_balance_decision": market_balance.get("decision"),
            "market_balance_root_count": len(market_balance.get("roots") or []),
            "market_balance_gate_pass_rows": market_balance_counts.get("gate_pass_rows"),
            "market_balance_positive_concentration_ok_rows": market_balance_counts.get("positive_concentration_ok_rows"),
            "market_balance_positive_both_balance_ok_rows": market_balance_counts.get("positive_both_balance_ok_rows"),
            "market_balance_best_variant": market_balance_best.get("variant"),
            "market_balance_best_accepted_entries": market_balance_best.get("accepted_entries"),
            "market_balance_best_selected_pnl_cents": market_balance_best.get("selected_pnl_cents"),
            "market_balance_best_matched_v28_delta_cents": market_balance_best.get("matched_v28_delta_cents"),
            "market_balance_best_rejection": market_balance_best.get("rejection_reason"),
            "market_balance_prequential_gate_pass": market_balance_prequential.get("prequential_gate_pass"),
            "market_balance_prequential_test_pnl_cents": market_balance_prequential.get("test_selected_pnl_cents"),
            "market_balance_prequential_test_matched_v28_delta_cents": market_balance_prequential.get("test_matched_v28_delta_cents"),
            "regime_filter_decision": regime_filter.get("decision"),
            "regime_filter_root_count": len(regime_filter.get("roots") or []),
            "regime_filter_predicate_count": regime_filter.get("predicate_count"),
            "regime_filter_support_row_count": regime_filter.get("support_row_count"),
            "regime_filter_best_variant": regime_filter_best.get("variant"),
            "regime_filter_best_accepted_entries": regime_filter_best.get("accepted_entries"),
            "regime_filter_best_selected_pnl_cents": regime_filter_best.get("selected_pnl_cents"),
            "regime_filter_best_matched_v28_delta_cents": regime_filter_best.get("matched_v28_delta_cents"),
            "regime_filter_best_rejection": regime_filter_best.get("rejection_reason"),
            "regime_filter_prequential_gate_pass": regime_filter_prequential.get("prequential_gate_pass"),
            "regime_filter_prequential_test_pnl_cents": regime_filter_prequential.get("test_selected_pnl_cents"),
            "regime_filter_prequential_test_matched_v28_delta_cents": regime_filter_prequential.get("test_matched_v28_delta_cents"),
            "group_dro_decision": group_dro.get("decision"),
            "group_dro_root_count": len(group_dro.get("roots") or []),
            "group_dro_support_row_count": group_dro.get("support_row_count"),
            "group_dro_best_variant": group_dro_best.get("variant"),
            "group_dro_best_accepted_entries": group_dro_best.get("accepted_entries"),
            "group_dro_best_selected_pnl_cents": group_dro_best.get("selected_pnl_cents"),
            "group_dro_best_matched_v28_delta_cents": group_dro_best.get("matched_v28_delta_cents"),
            "group_dro_best_lower_tail_root_pnl_cents": group_dro_best.get("lower_tail_root_pnl_cents"),
            "group_dro_best_rejection": group_dro_best.get("rejection_reason"),
            "group_dro_prequential_gate_pass": group_dro_prequential.get("prequential_gate_pass"),
            "group_dro_prequential_test_pnl_cents": group_dro_prequential.get("test_selected_pnl_cents"),
            "group_dro_prequential_test_matched_v28_delta_cents": group_dro_prequential.get("test_matched_v28_delta_cents"),
            "pbo_decision": pbo.get("decision"),
            "pbo_root_count": pbo.get("root_count"),
            "pbo_candidate_count": pbo.get("candidate_count"),
            "pbo": pbo.get("pbo"),
            "pbo_positive_split_rate": pbo.get("positive_split_rate"),
            "pbo_mean_selected_test_pnl_cents": pbo.get("mean_selected_test_pnl_cents"),
            "reality_check_decision": reality_check.get("decision"),
            "reality_check_root_count": reality_check.get("root_count"),
            "reality_check_candidate_count": reality_check.get("candidate_count"),
            "reality_check_best_variant": reality_best_delta.get("variant"),
            "reality_check_best_selected_pnl_cents": reality_best_delta.get("total_selected_pnl_cents"),
            "reality_check_best_matched_v28_delta_cents": reality_best_delta.get("total_matched_v28_delta_cents"),
            "reality_check_best_rejection": reality_best_delta.get("rejection_reason"),
            "reality_check_mean_p_value": (reality_check.get("mean_reality_check") or {}).get("p_value"),
            "reality_check_studentized_p_value": (reality_check.get("studentized_reality_check") or {}).get("p_value"),
            "spa_benchmark_decision": spa_benchmark.get("decision"),
            "spa_benchmark_root_count": spa_benchmark.get("root_count"),
            "spa_benchmark_candidate_count": spa_benchmark.get("candidate_count"),
            "spa_benchmark_positive_delta_candidate_count": spa_benchmark.get("positive_delta_candidate_count"),
            "spa_benchmark_screen_candidate_count": spa_benchmark.get("spa_screen_candidate_count"),
            "spa_benchmark_best_variant": spa_best.get("variant"),
            "spa_benchmark_best_selected_pnl_cents": spa_best.get("total_selected_pnl_cents"),
            "spa_benchmark_best_matched_v28_delta_cents": spa_best.get("total_matched_v28_delta_cents"),
            "spa_benchmark_best_rejection": spa_best.get("rejection_reason"),
            "spa_benchmark_studentized_p_value": spa_bootstrap.get("studentized_p_value"),
            "stability_selection_decision": stability_selection.get("decision"),
            "stability_selection_root_count": stability_selection.get("root_count"),
            "stability_selection_candidate_count": stability_selection.get("candidate_count"),
            "stability_selection_locked_selection_count": stability_selection.get("locked_selection_count"),
            "stability_selection_full_support_count": stability_selection.get("full_support_count"),
            "stability_selection_test_selected_pnl_cents": stability_selection_aggregate.get("test_selected_pnl_cents"),
            "stability_selection_test_matched_v28_delta_cents": stability_selection_aggregate.get("test_matched_v28_delta_cents"),
            "stability_selection_test_avg_pnl_per_entry_cents": stability_selection_aggregate.get("test_avg_pnl_per_entry_cents"),
            "stability_selection_rejection": stability_selection_aggregate.get("rejection_reason"),
            "parameter_plateau_decision": parameter_plateau.get("decision"),
            "parameter_plateau_support_count": parameter_plateau.get("support_count"),
            "parameter_plateau_best_center": parameter_plateau_center.get("variant"),
            "parameter_plateau_best_breadth_ok_rate": parameter_plateau_best.get("breadth_ok_rate"),
            "parameter_plateau_best_median_positive_root_rate": parameter_plateau_best.get("median_positive_root_rate"),
            "parameter_plateau_best_median_positive_market_rate": parameter_plateau_best.get("median_positive_market_rate"),
        },
        "inputs": {
            "plan": str(args.plan),
            "note": str(args.note),
            "goal_audit_json": str(args.goal_audit_json),
            "futility_json": str(args.futility_json),
            "family_json": str(args.family_json),
            "grid_json": str(args.grid_json),
            "locked_json": str(args.locked_json),
            "meta_rescue_json": str(args.meta_rescue_json),
            "calibration_rescue_json": str(args.calibration_rescue_json),
            "conformal_rescue_json": str(args.conformal_rescue_json),
            "online_expert_rescue_json": str(args.online_expert_rescue_json),
            "failure_pattern_json": str(args.failure_pattern_json),
            "next_evidence_json": str(args.next_evidence_json),
            "smoke_audit_json": str(args.smoke_audit_json),
            "bounded_audit_json": str(args.bounded_audit_json),
            "cumulative_bounded_audit_json": str(args.cumulative_bounded_audit_json),
            "market_balance_rescue_json": str(args.market_balance_rescue_json),
            "regime_filter_rescue_json": str(args.regime_filter_rescue_json),
            "group_dro_rescue_json": str(args.group_dro_rescue_json),
            "pbo_stability_json": str(args.pbo_stability_json),
            "reality_check_audit_json": str(args.reality_check_audit_json),
            "spa_benchmark_audit_json": str(args.spa_benchmark_audit_json),
            "stability_selection_rescue_json": str(args.stability_selection_rescue_json),
            "locked_plan_forward_audit_json": str(args.locked_plan_forward_audit_json),
            "parameter_plateau_audit_json": str(args.parameter_plateau_audit_json),
        },
    }
    return report


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# RV600 Objective State Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- objective_complete: {report['objective_complete']}",
        f"- decision: {report['decision']}",
        f"- blocked_by: {', '.join(report['blocked_by']) if report['blocked_by'] else 'none'}",
        "",
        "## Summary",
        "",
        f"- goal_complete: {summary['goal_complete']}",
        f"- status_counts: {summary['status_counts']}",
        f"- futility_decision: `{summary['futility_decision']}`",
        f"- family_decision: `{summary['family_decision']}`",
        f"- grid_variant_count: {summary['grid_variant_count']}",
        f"- grid_promotion_allowed: {summary['grid_promotion_allowed']}",
        f"- forward_entries: {summary['forward_entries']}",
        f"- forward_markets: {summary['forward_markets']}",
        f"- forward_selected_pnl_cents: {summary['forward_selected_pnl_cents']}",
        f"- matched_v28_control_pnl_cents: {summary['matched_v28_control_pnl_cents']}",
        f"- meta_rescue_preliminary_gate_pass: {summary['meta_rescue_preliminary_gate_pass']}",
        f"- meta_rescue_test_selected_pnl_cents: {summary['meta_rescue_test_selected_pnl_cents']}",
        f"- meta_rescue_train_gate_selection_count: {summary['meta_rescue_train_gate_selection_count']}",
        f"- calibration_rescue_preliminary_gate_pass: {summary['calibration_rescue_preliminary_gate_pass']}",
        f"- calibration_rescue_test_selected_pnl_cents: {summary['calibration_rescue_test_selected_pnl_cents']}",
        f"- calibration_rescue_train_gate_selection_count: {summary['calibration_rescue_train_gate_selection_count']}",
        f"- conformal_rescue_preliminary_gate_pass: {summary['conformal_rescue_preliminary_gate_pass']}",
        f"- conformal_rescue_test_selected_pnl_cents: {summary['conformal_rescue_test_selected_pnl_cents']}",
        f"- conformal_rescue_train_gate_selection_count: {summary['conformal_rescue_train_gate_selection_count']}",
        f"- online_expert_rescue_preliminary_gate_pass: {summary['online_expert_rescue_preliminary_gate_pass']}",
        f"- online_expert_rescue_test_selected_pnl_cents: {summary['online_expert_rescue_test_selected_pnl_cents']}",
        f"- online_expert_rescue_train_gate_selection_count: {summary['online_expert_rescue_train_gate_selection_count']}",
        f"- failure_pattern_decision: `{summary['failure_pattern_decision']}`",
        f"- failure_pattern_support_row_count: {summary['failure_pattern_support_row_count']}",
        f"- failure_pattern_plan_revision_supported: {summary['failure_pattern_plan_revision_supported']}",
        f"- next_evidence_decision: `{summary['next_evidence_decision']}`",
        f"- next_evidence_ready: {summary['next_evidence_ready']}",
        f"- next_evidence_plan_id: `{summary['next_evidence_plan_id']}`",
        f"- locked_plan_alignment_ok: {summary['locked_plan_alignment_ok']}",
        f"- locked_plan_forward_plan_id: `{summary['locked_plan_forward_plan_id']}`",
        f"- locked_plan_forward_variant: `{summary['locked_plan_forward_variant']}`",
        f"- locked_plan_forward_single_market_benchmark_variant: `{summary['locked_plan_forward_single_market_benchmark_variant']}`",
        f"- locked_plan_forward_decision: `{summary['locked_plan_forward_decision']}`",
        f"- locked_plan_forward_root_count: {summary['locked_plan_forward_root_count']}",
        f"- locked_plan_forward_calendar_day_count: {summary['locked_plan_forward_calendar_day_count']}",
        f"- locked_plan_forward_weekend_day_count: {summary['locked_plan_forward_weekend_day_count']}",
        f"- locked_plan_forward_accepted_entries: {summary['locked_plan_forward_accepted_entries']}",
        f"- locked_plan_forward_distinct_markets: {summary['locked_plan_forward_distinct_markets']}",
        f"- locked_plan_forward_selected_pnl_cents: {summary['locked_plan_forward_selected_pnl_cents']}",
        f"- locked_plan_forward_matched_v28_delta_cents: {summary['locked_plan_forward_matched_v28_delta_cents']}",
        f"- locked_plan_forward_avg_pnl_per_entry_cents: {summary['locked_plan_forward_avg_pnl_per_entry_cents']}",
        f"- locked_plan_forward_rejection: `{summary['locked_plan_forward_rejection']}`",
        f"- smoke_decision: `{summary['smoke_decision']}`",
        f"- smoke_candidate_rows: {summary['smoke_candidate_rows']}",
        f"- smoke_settled_markets: {summary['smoke_settled_markets']}",
        f"- smoke_locked_total_entries: {summary['smoke_locked_total_entries']}",
        f"- bounded_decision: `{summary['bounded_decision']}`",
        f"- bounded_candidate_rows: {summary['bounded_candidate_rows']}",
        f"- bounded_settled_markets: {summary['bounded_settled_markets']}",
        f"- bounded_locked_total_entries: {summary['bounded_locked_total_entries']}",
        f"- bounded_locked_total_pnl_cents: {summary['bounded_locked_total_pnl_cents']}",
        f"- bounded_best_grid_accepted_entries: {summary['bounded_best_grid_accepted_entries']}",
        f"- bounded_best_grid_selected_pnl_cents: {summary['bounded_best_grid_selected_pnl_cents']}",
        f"- bounded_best_grid_matched_v28_delta_cents: {summary['bounded_best_grid_matched_v28_delta_cents']}",
        f"- cumulative_bounded_decision: `{summary['cumulative_bounded_decision']}`",
        f"- cumulative_bounded_root_count: {summary['cumulative_bounded_root_count']}",
        f"- cumulative_bounded_candidate_rows: {summary['cumulative_bounded_candidate_rows']}",
        f"- cumulative_bounded_settled_markets: {summary['cumulative_bounded_settled_markets']}",
        f"- cumulative_bounded_locked_total_entries: {summary['cumulative_bounded_locked_total_entries']}",
        f"- cumulative_bounded_locked_total_pnl_cents: {summary['cumulative_bounded_locked_total_pnl_cents']}",
        f"- cumulative_bounded_best_grid_accepted_entries: {summary['cumulative_bounded_best_grid_accepted_entries']}",
        f"- cumulative_bounded_best_grid_selected_pnl_cents: {summary['cumulative_bounded_best_grid_selected_pnl_cents']}",
        f"- cumulative_bounded_best_grid_matched_v28_delta_cents: {summary['cumulative_bounded_best_grid_matched_v28_delta_cents']}",
        f"- cumulative_bounded_best_grid_rejection: `{summary['cumulative_bounded_best_grid_rejection']}`",
        f"- market_balance_decision: `{summary['market_balance_decision']}`",
        f"- market_balance_root_count: {summary['market_balance_root_count']}",
        f"- market_balance_gate_pass_rows: {summary['market_balance_gate_pass_rows']}",
        f"- market_balance_positive_concentration_ok_rows: {summary['market_balance_positive_concentration_ok_rows']}",
        f"- market_balance_positive_both_balance_ok_rows: {summary['market_balance_positive_both_balance_ok_rows']}",
        f"- market_balance_best_variant: `{summary['market_balance_best_variant']}`",
        f"- market_balance_best_accepted_entries: {summary['market_balance_best_accepted_entries']}",
        f"- market_balance_best_selected_pnl_cents: {summary['market_balance_best_selected_pnl_cents']}",
        f"- market_balance_best_matched_v28_delta_cents: {summary['market_balance_best_matched_v28_delta_cents']}",
        f"- market_balance_best_rejection: `{summary['market_balance_best_rejection']}`",
        f"- market_balance_prequential_gate_pass: {summary['market_balance_prequential_gate_pass']}",
        f"- market_balance_prequential_test_pnl_cents: {summary['market_balance_prequential_test_pnl_cents']}",
        f"- market_balance_prequential_test_matched_v28_delta_cents: {summary['market_balance_prequential_test_matched_v28_delta_cents']}",
        f"- regime_filter_decision: `{summary['regime_filter_decision']}`",
        f"- regime_filter_root_count: {summary['regime_filter_root_count']}",
        f"- regime_filter_predicate_count: {summary['regime_filter_predicate_count']}",
        f"- regime_filter_support_row_count: {summary['regime_filter_support_row_count']}",
        f"- regime_filter_best_variant: `{summary['regime_filter_best_variant']}`",
        f"- regime_filter_best_accepted_entries: {summary['regime_filter_best_accepted_entries']}",
        f"- regime_filter_best_selected_pnl_cents: {summary['regime_filter_best_selected_pnl_cents']}",
        f"- regime_filter_best_matched_v28_delta_cents: {summary['regime_filter_best_matched_v28_delta_cents']}",
        f"- regime_filter_best_rejection: `{summary['regime_filter_best_rejection']}`",
        f"- regime_filter_prequential_gate_pass: {summary['regime_filter_prequential_gate_pass']}",
        f"- regime_filter_prequential_test_pnl_cents: {summary['regime_filter_prequential_test_pnl_cents']}",
        f"- regime_filter_prequential_test_matched_v28_delta_cents: {summary['regime_filter_prequential_test_matched_v28_delta_cents']}",
        f"- group_dro_decision: `{summary['group_dro_decision']}`",
        f"- group_dro_root_count: {summary['group_dro_root_count']}",
        f"- group_dro_support_row_count: {summary['group_dro_support_row_count']}",
        f"- group_dro_best_variant: `{summary['group_dro_best_variant']}`",
        f"- group_dro_best_accepted_entries: {summary['group_dro_best_accepted_entries']}",
        f"- group_dro_best_selected_pnl_cents: {summary['group_dro_best_selected_pnl_cents']}",
        f"- group_dro_best_matched_v28_delta_cents: {summary['group_dro_best_matched_v28_delta_cents']}",
        f"- group_dro_best_lower_tail_root_pnl_cents: {summary['group_dro_best_lower_tail_root_pnl_cents']}",
        f"- group_dro_best_rejection: `{summary['group_dro_best_rejection']}`",
        f"- group_dro_prequential_gate_pass: {summary['group_dro_prequential_gate_pass']}",
        f"- group_dro_prequential_test_pnl_cents: {summary['group_dro_prequential_test_pnl_cents']}",
        f"- group_dro_prequential_test_matched_v28_delta_cents: {summary['group_dro_prequential_test_matched_v28_delta_cents']}",
        f"- pbo_decision: `{summary['pbo_decision']}`",
        f"- pbo_root_count: {summary['pbo_root_count']}",
        f"- pbo_candidate_count: {summary['pbo_candidate_count']}",
        f"- pbo: {summary['pbo']}",
        f"- pbo_positive_split_rate: {summary['pbo_positive_split_rate']}",
        f"- pbo_mean_selected_test_pnl_cents: {summary['pbo_mean_selected_test_pnl_cents']}",
        f"- reality_check_decision: `{summary['reality_check_decision']}`",
        f"- reality_check_root_count: {summary['reality_check_root_count']}",
        f"- reality_check_candidate_count: {summary['reality_check_candidate_count']}",
        f"- reality_check_best_variant: `{summary['reality_check_best_variant']}`",
        f"- reality_check_best_selected_pnl_cents: {summary['reality_check_best_selected_pnl_cents']}",
        f"- reality_check_best_matched_v28_delta_cents: {summary['reality_check_best_matched_v28_delta_cents']}",
        f"- reality_check_best_rejection: `{summary['reality_check_best_rejection']}`",
        f"- reality_check_mean_p_value: {summary['reality_check_mean_p_value']}",
        f"- reality_check_studentized_p_value: {summary['reality_check_studentized_p_value']}",
        f"- spa_benchmark_decision: `{summary['spa_benchmark_decision']}`",
        f"- spa_benchmark_root_count: {summary['spa_benchmark_root_count']}",
        f"- spa_benchmark_candidate_count: {summary['spa_benchmark_candidate_count']}",
        f"- spa_benchmark_positive_delta_candidate_count: {summary['spa_benchmark_positive_delta_candidate_count']}",
        f"- spa_benchmark_screen_candidate_count: {summary['spa_benchmark_screen_candidate_count']}",
        f"- spa_benchmark_best_variant: `{summary['spa_benchmark_best_variant']}`",
        f"- spa_benchmark_best_selected_pnl_cents: {summary['spa_benchmark_best_selected_pnl_cents']}",
        f"- spa_benchmark_best_matched_v28_delta_cents: {summary['spa_benchmark_best_matched_v28_delta_cents']}",
        f"- spa_benchmark_best_rejection: `{summary['spa_benchmark_best_rejection']}`",
        f"- spa_benchmark_studentized_p_value: {summary['spa_benchmark_studentized_p_value']}",
        f"- stability_selection_decision: `{summary['stability_selection_decision']}`",
        f"- stability_selection_root_count: {summary['stability_selection_root_count']}",
        f"- stability_selection_candidate_count: {summary['stability_selection_candidate_count']}",
        f"- stability_selection_locked_selection_count: {summary['stability_selection_locked_selection_count']}",
        f"- stability_selection_full_support_count: {summary['stability_selection_full_support_count']}",
        f"- stability_selection_test_selected_pnl_cents: {summary['stability_selection_test_selected_pnl_cents']}",
        f"- stability_selection_test_matched_v28_delta_cents: {summary['stability_selection_test_matched_v28_delta_cents']}",
        f"- stability_selection_test_avg_pnl_per_entry_cents: {summary['stability_selection_test_avg_pnl_per_entry_cents']}",
        f"- stability_selection_rejection: `{summary['stability_selection_rejection']}`",
        f"- parameter_plateau_decision: `{summary['parameter_plateau_decision']}`",
        f"- parameter_plateau_support_count: {summary['parameter_plateau_support_count']}",
        f"- parameter_plateau_best_center: `{summary['parameter_plateau_best_center']}`",
        f"- parameter_plateau_best_breadth_ok_rate: {summary['parameter_plateau_best_breadth_ok_rate']}",
        f"- parameter_plateau_best_median_positive_root_rate: {summary['parameter_plateau_best_median_positive_root_rate']}",
        f"- parameter_plateau_best_median_positive_market_rate: {summary['parameter_plateau_best_median_positive_market_rate']}",
        "",
        "## Prompt-To-Artifact Checklist",
        "",
        "| status | requirement | evidence | next action |",
        "|---|---|---|---|",
    ]
    for item in report["checklist"]:
        lines.append(
            f"| {item['status']} | {item['requirement']} | {item['evidence']} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The RV600 objective is not complete. The current locked family is rejected, the frozen locked plan failed its post-registration forward audit, every existing plan-defined family is rejected on the expanded forward grid, the meta-label, probability-calibration, conformal-abstention, online-expert, market-balance, regime-filter, group-DRO, stability-selection, and parameter-plateau rescues failed, the PBO stability, root-bootstrap reality-check, and SPA benchmark audits reject the current grid, the failure-pattern audit supports no new plan revision from this sample, and fresh bounded shadow evidence remains insufficient.",
            "The next RV600 work should be a documented plan update or a newly frozen candidate with fresh locked and forward gates; do not promote or live-test any current RV600 family.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit current RV600 objective state against the prompt requirements.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--note", type=Path, default=DEFAULT_NOTE)
    parser.add_argument("--goal-audit-json", type=Path, default=DEFAULT_GOAL_AUDIT)
    parser.add_argument("--futility-json", type=Path, default=DEFAULT_FUTILITY)
    parser.add_argument("--family-json", type=Path, default=DEFAULT_FAMILY)
    parser.add_argument("--grid-json", type=Path, default=DEFAULT_GRID)
    parser.add_argument("--locked-json", type=Path, default=DEFAULT_LOCKED)
    parser.add_argument("--meta-rescue-json", type=Path, default=DEFAULT_META_RESCUE)
    parser.add_argument("--calibration-rescue-json", type=Path, default=DEFAULT_CALIBRATION_RESCUE)
    parser.add_argument("--conformal-rescue-json", type=Path, default=DEFAULT_CONFORMAL_RESCUE)
    parser.add_argument("--online-expert-rescue-json", type=Path, default=DEFAULT_ONLINE_EXPERT_RESCUE)
    parser.add_argument("--failure-pattern-json", type=Path, default=DEFAULT_FAILURE_PATTERN)
    parser.add_argument("--next-evidence-json", type=Path, default=DEFAULT_NEXT_EVIDENCE)
    parser.add_argument("--smoke-audit-json", type=Path, default=DEFAULT_SMOKE_AUDIT)
    parser.add_argument("--bounded-audit-json", type=Path, default=DEFAULT_BOUNDED_AUDIT)
    parser.add_argument(
        "--cumulative-bounded-audit-json",
        type=Path,
        default=DEFAULT_CUMULATIVE_BOUNDED_AUDIT,
    )
    parser.add_argument(
        "--market-balance-rescue-json",
        type=Path,
        default=DEFAULT_MARKET_BALANCE_RESCUE,
    )
    parser.add_argument(
        "--regime-filter-rescue-json",
        type=Path,
        default=DEFAULT_REGIME_FILTER_RESCUE,
    )
    parser.add_argument(
        "--group-dro-rescue-json",
        type=Path,
        default=DEFAULT_GROUP_DRO_RESCUE,
    )
    parser.add_argument(
        "--pbo-stability-json",
        type=Path,
        default=DEFAULT_PBO_STABILITY,
    )
    parser.add_argument(
        "--stability-selection-rescue-json",
        type=Path,
        default=DEFAULT_STABILITY_SELECTION_RESCUE,
    )
    parser.add_argument(
        "--locked-plan-forward-audit-json",
        type=Path,
        default=DEFAULT_LOCKED_PLAN_FORWARD_AUDIT,
    )
    parser.add_argument(
        "--reality-check-audit-json",
        type=Path,
        default=DEFAULT_REALITY_CHECK_AUDIT,
    )
    parser.add_argument(
        "--spa-benchmark-audit-json",
        type=Path,
        default=DEFAULT_SPA_BENCHMARK_AUDIT,
    )
    parser.add_argument(
        "--parameter-plateau-audit-json",
        type=Path,
        default=DEFAULT_PARAMETER_PLATEAU_AUDIT,
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"objective_complete={report['objective_complete']}")
    print(f"blocked_by={';'.join(report['blocked_by'])}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
