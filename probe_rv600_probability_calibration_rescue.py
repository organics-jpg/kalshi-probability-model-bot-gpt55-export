from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_NATIVE_JSON = Path("logs/particle_research/reports/rv600_native_forward_opportunity_latest.json")
DEFAULT_ROOT_BASE = Path("logs/particle_research/real_shadow")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_probability_calibration_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_probability_calibration_rescue_latest.md")

MODELING_OPTIONS = [
    {
        "method": "platt_scaling",
        "source": "Platt 1999, Probabilistic Outputs for Support Vector Machines",
        "source_url": "https://www.researchgate.net/publication/2594015_Probabilistic_Outputs_for_Support_Vector_Machines_and_Comparisons_to_Regularized_Likelihood_Methods",
        "fit": "Small parametric logit recalibration; feasible with little data if selected only from prior roots.",
        "decision": "chosen_as_grid_platt",
    },
    {
        "method": "temperature_scaling",
        "source": "Guo et al. 2017, On Calibration of Modern Neural Networks",
        "source_url": "https://arxiv.org/abs/1706.04599",
        "fit": "One-parameter confidence scaling; useful as a low-complexity RV600 shrink/expand check.",
        "decision": "chosen_as_fixed_candidates",
    },
    {
        "method": "isotonic_calibration",
        "source": "Niculescu-Mizil and Caruana 2005, Predicting Good Probabilities with Supervised Learning",
        "source_url": "https://icml.cc/Conferences/2005/proceedings/papers/079_GoodProbabilities_NiculescuMizilCaruana.pdf",
        "fit": "Flexible but too easy to overfit with the current small number of settled markets.",
        "decision": "deferred",
    },
    {
        "method": "venn_abers",
        "source": "Vovk and Petej 2012, Venn-Abers predictors",
        "source_url": "https://arxiv.org/abs/1211.0025",
        "fit": "Attractive calibration intervals, but assumes a larger calibration set than the current forward market count.",
        "decision": "deferred",
    },
]


@dataclass(frozen=True)
class CandidateRow:
    root_name: str
    market_ticker: str
    decision_ts_utc: datetime
    result: str
    rv600_p_yes: float
    current_p_yes: float
    market_p_yes: float
    yes_ask_cents: float
    no_ask_cents: float
    yes_fill_prob: float
    no_fill_prob: float
    fee_cents: float
    seconds_to_close: float


@dataclass(frozen=True)
class StrategySpec:
    name: str
    min_seconds_to_close: float
    max_seconds_to_close: float
    min_ev_cents: float
    entry_rule: str
    max_entries_per_market: int
    risk_cap_cents: float | None = None

    @property
    def declared_position_cap_cents(self) -> float:
        if self.risk_cap_cents is not None:
            return self.risk_cap_cents
        return max(100.0, 100.0 * max(1, self.max_entries_per_market))


@dataclass(frozen=True)
class CalibrationFit:
    name: str
    description: str
    params: dict[str, float]
    fn: Callable[[CandidateRow], float]


@dataclass(frozen=True)
class AcceptedDecision:
    root_name: str
    market_ticker: str
    decision_ts_utc: datetime
    side: str
    ask_cents: float
    risk_cents: float
    selected_ev_cents: float
    matched_v28_ev_cents: float
    pnl_cents: float
    matched_v28_pnl_cents: float
    is_added_entry: bool


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_dt(value: Any) -> datetime:
    text = str(value or "")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _label_path(root: Path) -> Path:
    return root / "pipeline_work" / "label_contexts_full_refresh.ndjson"


def _candidate_path(root: Path) -> Path:
    return root / "candidate_snapshots" / "candidate_snapshots.ndjson"


def _load_label(root: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    path = _label_path(root)
    if not path.exists():
        return labels
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            result = str(payload.get("binary_result") or payload.get("result") or "").lower()
            market = str(payload.get("market_ticker") or payload.get("market") or "")
            if market and result in {"yes", "no"}:
                labels[market] = result
    return labels


def _load_root_rows(root_base: Path, root_name: str) -> list[CandidateRow]:
    root = root_base / root_name
    labels = _load_label(root)
    path = _candidate_path(root)
    if not labels or not path.exists():
        return []
    rows: list[CandidateRow] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            snapshot = payload.get("snapshot") or {}
            extra = payload.get("extra") or {}
            market = str(snapshot.get("market_ticker") or "")
            result = labels.get(market)
            if result not in {"yes", "no"}:
                continue
            yes_ask = _float(snapshot.get("yes_ask_cents"))
            no_ask = _float(snapshot.get("no_ask_cents"))
            rows.append(
                CandidateRow(
                    root_name=root_name,
                    market_ticker=market,
                    decision_ts_utc=_parse_dt(snapshot.get("decision_ts_utc")),
                    result=result,
                    rv600_p_yes=_clamp01(_float(extra.get("particle_calibrated_p_yes"), _float(extra.get("particle_p_yes"), 0.5))),
                    current_p_yes=_clamp01(_float(extra.get("current_calibrated_p_yes"), _float(snapshot.get("current_calibrated_p_yes"), 0.5))),
                    market_p_yes=_clamp01(_float(extra.get("market_p_yes"), yes_ask / max(1.0, yes_ask + no_ask))),
                    yes_ask_cents=yes_ask,
                    no_ask_cents=no_ask,
                    yes_fill_prob=_clamp01(_float(snapshot.get("yes_fill_prob"), _float(snapshot.get("fill_prob"), 1.0))),
                    no_fill_prob=_clamp01(_float(snapshot.get("no_fill_prob"), _float(snapshot.get("fill_prob"), 1.0))),
                    fee_cents=_float(snapshot.get("fee_cents"), 2.0),
                    seconds_to_close=_float(extra.get("seconds_to_close"), _float(snapshot.get("seconds_to_close"))),
                )
            )
    return sorted(rows, key=lambda item: (item.decision_ts_utc, item.market_ticker))


def _calibration_fits(train_rows: list[CandidateRow]) -> list[CalibrationFit]:
    fits: list[CalibrationFit] = [
        CalibrationFit("rv600_raw", "raw RV600 probability", {}, lambda row: row.rv600_p_yes),
        CalibrationFit("temp_0_75", "temperature scaling T=0.75", {"temperature": 0.75}, lambda row: _temperature(row.rv600_p_yes, 0.75)),
        CalibrationFit("temp_1_50", "temperature scaling T=1.50", {"temperature": 1.50}, lambda row: _temperature(row.rv600_p_yes, 1.50)),
        CalibrationFit("temp_2_00", "temperature scaling T=2.00", {"temperature": 2.00}, lambda row: _temperature(row.rv600_p_yes, 2.00)),
        CalibrationFit("shrink_current_25", "75% RV600 + 25% current/v28", {"current_weight": 0.25}, lambda row: _mix(row.rv600_p_yes, row.current_p_yes, 0.25)),
        CalibrationFit("shrink_current_50", "50% RV600 + 50% current/v28", {"current_weight": 0.50}, lambda row: _mix(row.rv600_p_yes, row.current_p_yes, 0.50)),
        CalibrationFit("shrink_market_25", "75% RV600 + 25% market", {"market_weight": 0.25}, lambda row: _mix(row.rv600_p_yes, row.market_p_yes, 0.25)),
        CalibrationFit("shrink_market_50", "50% RV600 + 50% market", {"market_weight": 0.50}, lambda row: _mix(row.rv600_p_yes, row.market_p_yes, 0.50)),
    ]
    platt = _fit_platt_grid(train_rows)
    if platt is not None:
        fits.append(platt)
    return fits


def _fit_platt_grid(train_rows: list[CandidateRow]) -> CalibrationFit | None:
    market_rows: dict[str, CandidateRow] = {}
    for row in train_rows:
        market_rows.setdefault(row.market_ticker, row)
    rows = list(market_rows.values())
    if len(rows) < 10:
        return None
    best: tuple[float, float, float] | None = None
    for slope in (0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 2.0):
        for bias in (-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0):
            loss = 0.0
            for row in rows:
                p = _sigmoid(slope * _logit(row.rv600_p_yes) + bias)
                y = 1.0 if row.result == "yes" else 0.0
                loss += -(y * math.log(_clamp(p, 0.001, 0.999)) + (1.0 - y) * math.log(_clamp(1.0 - p, 0.001, 0.999)))
            candidate = (loss / len(rows), slope, bias)
            if best is None or candidate < best:
                best = candidate
    if best is None:
        return None
    _, slope, bias = best
    return CalibrationFit(
        "platt_grid_market_deduped",
        "grid Platt scaling fit on one earliest candidate per prior-root market",
        {"slope": slope, "bias": bias},
        lambda row, s=slope, b=bias: _sigmoid(s * _logit(row.rv600_p_yes) + b),
    )


def _strategy_specs() -> list[StrategySpec]:
    return [
        StrategySpec("single_70_420_ev8", 70.0, 420.0, 8.0, "single_market", 1),
        StrategySpec("single_70_420_ev10", 70.0, 420.0, 10.0, "single_market", 1),
        StrategySpec("max2_refresh120_70_420_ev8", 70.0, 420.0, 8.0, "same_side_refresh_120s", 2),
        StrategySpec("max2_refresh120_70_420_ev10", 70.0, 420.0, 10.0, "same_side_refresh_120s", 2),
        StrategySpec("max2_evstep5_70_420_ev8", 70.0, 420.0, 8.0, "same_side_ev_step_5c", 2),
        StrategySpec("max2_evstep5_70_420_ev10", 70.0, 420.0, 10.0, "same_side_ev_step_5c", 2),
        StrategySpec("max3_risk200_70_420_ev8", 70.0, 420.0, 8.0, "risk_cap_200c", 3, 200.0),
        StrategySpec("max3_risk200_70_420_ev10", 70.0, 420.0, 10.0, "risk_cap_200c", 3, 200.0),
    ]


def _accepted_decisions(rows: list[CandidateRow], cal: CalibrationFit, spec: StrategySpec) -> list[AcceptedDecision]:
    accepted: list[AcceptedDecision] = []
    state: dict[str, list[AcceptedDecision]] = defaultdict(list)
    for row in sorted(rows, key=lambda item: (item.decision_ts_utc, item.market_ticker)):
        if not spec.min_seconds_to_close <= row.seconds_to_close <= spec.max_seconds_to_close:
            continue
        p_yes = _clamp01(cal.fn(row))
        side, ev, ask, fill_prob = _side_eval(row, p_yes)
        if ev < spec.min_ev_cents:
            continue
        previous = state[row.market_ticker]
        if not _passes_entry_rule(previous, side, ev, ask, row.decision_ts_utc, spec):
            continue
        matched_side, matched_ev, matched_ask, matched_fill = _side_eval(row, row.current_p_yes)
        pnl = _realized_pnl(row, side, ask, fill_prob)
        matched_pnl = _realized_pnl(row, matched_side, matched_ask, matched_fill)
        decision = AcceptedDecision(
            root_name=row.root_name,
            market_ticker=row.market_ticker,
            decision_ts_utc=row.decision_ts_utc,
            side=side,
            ask_cents=ask,
            risk_cents=ask,
            selected_ev_cents=ev,
            matched_v28_ev_cents=matched_ev,
            pnl_cents=pnl,
            matched_v28_pnl_cents=matched_pnl,
            is_added_entry=bool(previous),
        )
        previous.append(decision)
        accepted.append(decision)
    return accepted


def _score(rows_by_root: dict[str, list[CandidateRow]], roots: list[str], cal: CalibrationFit, spec: StrategySpec) -> dict[str, Any]:
    all_entries: list[AcceptedDecision] = []
    root_rows: list[dict[str, Any]] = []
    for root in roots:
        accepted = _accepted_decisions(rows_by_root.get(root, []), cal, spec)
        capped = _position_capped(accepted, spec.declared_position_cap_cents)
        all_entries.extend(capped)
        root_rows.append(
            {
                "root": root,
                "accepted_entries": len(capped),
                "distinct_markets": len({item.market_ticker for item in capped}),
                "selected_pnl_cents": sum(item.pnl_cents for item in capped),
                "matched_v28_control_pnl_cents": sum(item.matched_v28_pnl_cents for item in capped),
            }
        )
    modes = {
        "all_entries": [item for root in roots for item in _accepted_decisions(rows_by_root.get(root, []), cal, spec)],
        "one_per_side_per_market": _one_per_side(all_entries),
        "position_capped": all_entries,
    }
    mode_scores = {name: _score_decisions(decisions) for name, decisions in modes.items()}
    main = mode_scores["position_capped"]
    main.update(
        {
            "calibration": cal.name,
            "calibration_description": cal.description,
            "calibration_params": cal.params,
            "strategy": spec.name,
            "accounting_mode": "position_capped",
            "root_rows": root_rows,
            "accounting_modes": mode_scores,
            "train_gate_pass": _passes_gate(main, mode_scores, spec),
            "rejection_reason": _rejection_reason(main, mode_scores, spec),
        }
    )
    return main


def _score_decisions(decisions: list[AcceptedDecision]) -> dict[str, Any]:
    pnl = sum(item.pnl_cents for item in decisions)
    matched = sum(item.matched_v28_pnl_cents for item in decisions)
    market_pnls: dict[str, float] = defaultdict(float)
    root_pnls: dict[str, float] = defaultdict(float)
    side_pnls: dict[str, float] = defaultdict(float)
    for decision in decisions:
        market_pnls[decision.market_ticker] += decision.pnl_cents
        root_pnls[decision.root_name] += decision.pnl_cents
        side_pnls[decision.side] += decision.pnl_cents
    added = [item for item in decisions if item.is_added_entry]
    return {
        "accepted_entries": len(decisions),
        "distinct_markets": len(market_pnls),
        "selected_pnl_cents": pnl,
        "matched_v28_control_pnl_cents": matched,
        "matched_v28_delta_cents": pnl - matched,
        "avg_pnl_per_entry_cents": pnl / len(decisions) if decisions else 0.0,
        "avg_pnl_per_market_cents": pnl / len(market_pnls) if market_pnls else 0.0,
        "positive_root_rate": (sum(1 for value in root_pnls.values() if value > 0.0) / len(root_pnls)) if root_pnls else 0.0,
        "positive_market_rate": (sum(1 for value in market_pnls.values() if value > 0.0) / len(market_pnls)) if market_pnls else 0.0,
        "max_single_market_pnl_share": _max_market_share(market_pnls, pnl),
        "last_window_pnl_cents": sum(item.pnl_cents for item in decisions[-20:]),
        "added_entry_count": len(added),
        "added_entry_pnl_cents": sum(item.pnl_cents for item in added),
        "avg_added_entry_pnl_cents": (sum(item.pnl_cents for item in added) / len(added)) if added else 0.0,
        "side_pnls": dict(side_pnls),
    }


def _passes_gate(main: dict[str, Any], mode_scores: dict[str, dict[str, Any]], spec: StrategySpec) -> bool:
    if main["accepted_entries"] < 25:
        return False
    if main["distinct_markets"] < 10:
        return False
    if main["selected_pnl_cents"] <= 0.0:
        return False
    if main["avg_pnl_per_entry_cents"] < 10.0:
        return False
    if main["avg_pnl_per_market_cents"] <= 0.0:
        return False
    if main["positive_root_rate"] < 0.60:
        return False
    if main["positive_market_rate"] < 0.60:
        return False
    if main["max_single_market_pnl_share"] > 0.25:
        return False
    if main["last_window_pnl_cents"] <= 0.0:
        return False
    if main["matched_v28_delta_cents"] <= 0.0:
        return False
    if mode_scores["one_per_side_per_market"]["selected_pnl_cents"] <= 0.0:
        return False
    if spec.max_entries_per_market > 1 and main["added_entry_pnl_cents"] <= 0.0:
        return False
    return True


def _rejection_reason(main: dict[str, Any], mode_scores: dict[str, dict[str, Any]], spec: StrategySpec) -> str:
    reasons: list[str] = []
    if main["accepted_entries"] < 25:
        reasons.append("fewer_than_25_entries")
    if main["distinct_markets"] < 10:
        reasons.append("fewer_than_10_markets")
    if main["selected_pnl_cents"] <= 0.0:
        reasons.append("nonpositive_pnl")
    if main["avg_pnl_per_entry_cents"] < 10.0:
        reasons.append("avg_entry_below_10c")
    if main["avg_pnl_per_market_cents"] <= 0.0:
        reasons.append("avg_market_nonpositive")
    if main["positive_root_rate"] < 0.60:
        reasons.append("positive_root_rate_below_60pct")
    if main["positive_market_rate"] < 0.60:
        reasons.append("positive_market_rate_below_60pct")
    if main["max_single_market_pnl_share"] > 0.25:
        reasons.append("single_market_share_above_25pct")
    if main["last_window_pnl_cents"] <= 0.0:
        reasons.append("last_window_nonpositive")
    if main["matched_v28_delta_cents"] <= 0.0:
        reasons.append("does_not_beat_matched_v28")
    if mode_scores["one_per_side_per_market"]["selected_pnl_cents"] <= 0.0:
        reasons.append("deduped_one_per_side_nonpositive")
    if spec.max_entries_per_market > 1 and main["added_entry_pnl_cents"] <= 0.0:
        reasons.append("added_entries_nonpositive")
    return ";".join(reasons)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    native = _load_json(args.native_json)
    roots = list(native.get("roots") or [])
    rows_by_root = {root: _load_root_rows(args.root_base, root) for root in roots}
    usable_roots = [root for root in roots if rows_by_root.get(root)]
    strategies = _strategy_specs()
    split_rows: list[dict[str, Any]] = []
    for test_index in range(args.min_train_roots, len(usable_roots)):
        train_roots = usable_roots[:test_index]
        test_root = usable_roots[test_index]
        train_rows = [row for root in train_roots for row in rows_by_root[root]]
        train_scores: list[dict[str, Any]] = []
        for cal in _calibration_fits(train_rows):
            for spec in strategies:
                train_scores.append(_score(rows_by_root, train_roots, cal, spec))
        passing = [score for score in train_scores if score["train_gate_pass"]]
        if passing:
            selected = max(passing, key=lambda item: item["selected_pnl_cents"])
            selection_basis = "train_gate_pass"
        else:
            selected = max(train_scores, key=lambda item: item["selected_pnl_cents"])
            selection_basis = "diagnostic_best_train_pnl"
        selected_cal = _calibration_by_name(train_rows, selected["calibration"])
        selected_spec = next(item for item in strategies if item.name == selected["strategy"])
        test_score = _score(rows_by_root, [test_root], selected_cal, selected_spec)
        split_rows.append(
            {
                "split_index": len(split_rows),
                "train_root_count": len(train_roots),
                "test_root": test_root,
                "selected_calibration": selected["calibration"],
                "selected_strategy": selected["strategy"],
                "selection_basis": selection_basis,
                "train_gate_pass": bool(passing),
                "train_selected_pnl_cents": selected["selected_pnl_cents"],
                "train_accepted_entries": selected["accepted_entries"],
                "train_distinct_markets": selected["distinct_markets"],
                "train_avg_pnl_per_entry_cents": selected["avg_pnl_per_entry_cents"],
                "train_rejection_reason": selected["rejection_reason"],
                "test_selected_pnl_cents": test_score["selected_pnl_cents"],
                "test_matched_v28_control_pnl_cents": test_score["matched_v28_control_pnl_cents"],
                "test_matched_v28_delta_cents": test_score["matched_v28_delta_cents"],
                "test_accepted_entries": test_score["accepted_entries"],
                "test_distinct_markets": test_score["distinct_markets"],
                "test_avg_pnl_per_entry_cents": test_score["avg_pnl_per_entry_cents"],
                "test_rejection_reason": test_score["rejection_reason"],
            }
        )
    total_entries = sum(row["test_accepted_entries"] for row in split_rows)
    total_pnl = sum(row["test_selected_pnl_cents"] for row in split_rows)
    total_matched = sum(row["test_matched_v28_control_pnl_cents"] for row in split_rows)
    locked_selection_count = sum(1 for row in split_rows if row["selection_basis"] == "train_gate_pass")
    positive_splits = sum(1 for row in split_rows if row["test_selected_pnl_cents"] > 0.0)
    gate_pass = (
        locked_selection_count > 0
        and total_entries >= 25
        and total_pnl > 0.0
        and total_pnl - total_matched > 0.0
        and (total_pnl / total_entries if total_entries else 0.0) >= 10.0
        and (positive_splits / len(split_rows) if split_rows else 0.0) >= 0.60
    )
    return {
        "schema_version": "rv600-probability-calibration-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "method_choice": "Low-complexity probability calibration over RV600 with anchored prequential strategy selection.",
        "modeling_options": MODELING_OPTIONS,
        "roots": usable_roots,
        "min_train_roots": args.min_train_roots,
        "strategy_count": len(strategies),
        "split_rows": split_rows,
        "aggregate": {
            "split_count": len(split_rows),
            "train_gate_selection_count": locked_selection_count,
            "diagnostic_selection_count": len(split_rows) - locked_selection_count,
            "test_total_entries": total_entries,
            "test_selected_pnl_cents": total_pnl,
            "test_matched_v28_control_pnl_cents": total_matched,
            "test_matched_v28_delta_cents": total_pnl - total_matched,
            "test_avg_pnl_per_entry_cents": total_pnl / total_entries if total_entries else 0.0,
            "positive_test_split_rate": positive_splits / len(split_rows) if split_rows else 0.0,
            "preliminary_gate_pass": gate_pass,
            "rejection_reason": _aggregate_rejection(gate_pass, locked_selection_count, total_entries, total_pnl, total_matched, positive_splits, len(split_rows)),
        },
        "inputs": {
            "native_json": str(args.native_json),
            "root_base": str(args.root_base),
        },
    }


def _calibration_by_name(train_rows: list[CandidateRow], name: str) -> CalibrationFit:
    for cal in _calibration_fits(train_rows):
        if cal.name == name:
            return cal
    raise KeyError(name)


def _aggregate_rejection(gate_pass: bool, locked_selection_count: int, total_entries: int, total_pnl: float, total_matched: float, positive_splits: int, split_count: int) -> str:
    if gate_pass:
        return ""
    reasons: list[str] = []
    if locked_selection_count <= 0:
        reasons.append("no_train_gate_selection")
    if total_entries < 25:
        reasons.append("fewer_than_25_test_entries")
    if total_pnl <= 0.0:
        reasons.append("nonpositive_test_pnl")
    if total_entries and total_pnl / total_entries < 10.0:
        reasons.append("avg_test_entry_below_10c")
    if total_pnl - total_matched <= 0.0:
        reasons.append("does_not_beat_matched_v28")
    if split_count and positive_splits / split_count < 0.60:
        reasons.append("positive_test_splits_below_60pct")
    return ";".join(reasons)


def _markdown(report: dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "# RV600 Probability Calibration Rescue Probe",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- method_choice: {report['method_choice']}",
        f"- usable_roots: {len(report['roots'])}",
        f"- strategy_count: {report['strategy_count']}",
        f"- split_count: {aggregate['split_count']}",
        f"- train_gate_selection_count: {aggregate['train_gate_selection_count']}",
        f"- diagnostic_selection_count: {aggregate['diagnostic_selection_count']}",
        f"- test_total_entries: {aggregate['test_total_entries']}",
        f"- test_selected_pnl_cents: {aggregate['test_selected_pnl_cents']:.1f}",
        f"- test_matched_v28_delta_cents: {aggregate['test_matched_v28_delta_cents']:.1f}",
        f"- preliminary_gate_pass: {aggregate['preliminary_gate_pass']}",
        f"- rejection_reason: {aggregate['rejection_reason']}",
        "",
        "## Modeling Choice",
        "",
        "| method | decision | source | fit |",
        "|---|---|---|---|",
    ]
    for option in report["modeling_options"]:
        lines.append(
            f"| `{option['method']}` | {option['decision']} | [{option['source']}]({option['source_url']}) | {option['fit']} |"
        )
    lines.extend(
        [
            "",
            "## Split Rows",
            "",
            "| split | selected calibration | selected strategy | basis | test root | entries | pnl_c | v28_delta_c |",
            "|---:|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report["split_rows"]:
        lines.append(
            "| {split_index} | `{selected_calibration}` | `{selected_strategy}` | {selection_basis} | `{test_root}` | {test_accepted_entries} | {test_selected_pnl_cents:.1f} | {test_matched_v28_delta_cents:.1f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Method Notes",
            "",
            "This is a research-only calibration rescue attempt. Each split fits or selects calibration parameters using prior roots only, then tests the selected calibration and RV600 entry rule on the next root.",
            "Diagnostic selections are not promotable unless the prior-root window already passed anti-overfitting gates.",
            "",
        ]
    )
    return "\n".join(lines)


def _side_eval(row: CandidateRow, p_yes: float) -> tuple[str, float, float, float]:
    ev_yes = _expected_ev(p_yes, row.yes_ask_cents, row.fee_cents, row.yes_fill_prob)
    ev_no = _expected_ev(1.0 - p_yes, row.no_ask_cents, row.fee_cents, row.no_fill_prob)
    if ev_yes >= ev_no:
        return "yes", ev_yes, row.yes_ask_cents, row.yes_fill_prob
    return "no", ev_no, row.no_ask_cents, row.no_fill_prob


def _expected_ev(p_win: float, ask: float, fee: float, fill_prob: float) -> float:
    return fill_prob * (p_win * (100.0 - ask - fee) - (1.0 - p_win) * ask)


def _realized_pnl(row: CandidateRow, side: str, ask: float, fill_prob: float) -> float:
    if fill_prob < 0.5:
        return 0.0
    if row.result == side:
        return 100.0 - ask - row.fee_cents
    return -ask


def _passes_entry_rule(
    previous: list[AcceptedDecision],
    side: str,
    ev: float,
    ask: float,
    decision_ts: datetime,
    spec: StrategySpec,
) -> bool:
    if len(previous) >= spec.max_entries_per_market:
        return False
    if spec.risk_cap_cents is not None and sum(item.risk_cents for item in previous) + ask > spec.risk_cap_cents:
        return False
    if not previous:
        return True
    if spec.entry_rule == "single_market":
        return False
    if spec.entry_rule == "risk_cap_200c":
        return True
    same_side = [item for item in previous if item.side == side]
    if not same_side:
        return True
    last_same = same_side[-1]
    if spec.entry_rule == "same_side_refresh_120s":
        return (decision_ts - last_same.decision_ts_utc).total_seconds() >= 120.0
    if spec.entry_rule == "same_side_ev_step_5c":
        return ev >= last_same.selected_ev_cents + 5.0
    return False


def _one_per_side(decisions: list[AcceptedDecision]) -> list[AcceptedDecision]:
    seen: set[tuple[str, str]] = set()
    kept: list[AcceptedDecision] = []
    for decision in decisions:
        key = (decision.market_ticker, decision.side)
        if key in seen:
            continue
        seen.add(key)
        kept.append(decision)
    return kept


def _position_capped(decisions: list[AcceptedDecision], cap_cents: float) -> list[AcceptedDecision]:
    risk: dict[str, float] = defaultdict(float)
    kept: list[AcceptedDecision] = []
    for decision in decisions:
        if risk[decision.market_ticker] + decision.risk_cents > cap_cents:
            continue
        risk[decision.market_ticker] += decision.risk_cents
        kept.append(decision)
    return kept


def _max_market_share(market_pnls: dict[str, float], total_pnl: float) -> float:
    if total_pnl <= 0.0 or not market_pnls:
        return 0.0
    return max(max(0.0, value) for value in market_pnls.values()) / total_pnl


def _temperature(p: float, temperature: float) -> float:
    return _sigmoid(_logit(p) / max(0.001, temperature))


def _mix(primary: float, anchor: float, anchor_weight: float) -> float:
    return _clamp01((1.0 - anchor_weight) * primary + anchor_weight * anchor)


def _logit(p: float) -> float:
    p = _clamp(float(p), 0.001, 0.999)
    return math.log(p / (1.0 - p))


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _clamp01(value: float) -> float:
    return _clamp(value, 0.0, 1.0)


def _clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, float(value)))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-only RV600 probability calibration rescue probe.")
    parser.add_argument("--native-json", type=Path, default=DEFAULT_NATIVE_JSON)
    parser.add_argument("--root-base", type=Path, default=DEFAULT_ROOT_BASE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-train-roots", type=int, default=5)
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
    aggregate = report["aggregate"]
    print(f"preliminary_gate_pass={aggregate['preliminary_gate_pass']}")
    print(f"split_count={aggregate['split_count']}")
    print(f"train_gate_selection_count={aggregate['train_gate_selection_count']}")
    print(f"test_selected_pnl_cents={aggregate['test_selected_pnl_cents']:.1f}")
    print(f"rejection_reason={aggregate['rejection_reason']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
