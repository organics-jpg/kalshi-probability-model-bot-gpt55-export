from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from .dynamic_particle_replay import DynamicParticleSpec, RollingVolEstimator, SECONDS_PER_YEAR
from .ev_decision import break_even_probability, expected_pnl_cents
from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    load_replay_inputs_from_jsonl,
)
from .schemas import Side
from .terminal_projection import brownian_terminal_probability
from .v28_rolling_vol_transfer_diagnostic import (
    DEFAULT_REAL_SHADOW_DIR,
    discover_shadow_roots,
)


ProbabilityMode = Literal[
    "rv600_primary",
    "v28_primary",
    "blend_95_5",
    "blend_90_10",
    "blend_80_20",
]
EntryRule = Literal[
    "single_market",
    "side_flip_only",
    "same_side_refresh_60s",
    "same_side_refresh_120s",
    "same_side_ev_step_3c",
    "same_side_ev_step_5c",
    "max_2_entries",
    "max_3_entries",
    "risk_cap_100c",
    "risk_cap_200c",
]
SideFilter = Literal[
    "both_sides",
    "yes_only",
    "no_only",
    "side_by_rv_gap",
    "side_by_v28_agreement",
    "side_by_v28_disagreement",
]
AccountingMode = Literal["all_entries", "one_per_side_per_market", "position_capped"]
EvaluationPhase = Literal["first_candidates", "grid", "locked"]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = ROOT / "logs" / "particle_research" / "reports" / "rv600_variation_test_latest.json"
DEFAULT_OUTPUT_MD = ROOT / "logs" / "particle_research" / "reports" / "rv600_variation_test_latest.md"


@dataclass(frozen=True)
class RV600VariantSpec:
    name: str
    probability_mode: ProbabilityMode = "rv600_primary"
    min_seconds_to_close: float = 70.0
    max_seconds_to_close: float = 420.0
    min_ev_cents: float = 10.0
    entry_rule: EntryRule = "single_market"
    max_entries_per_market: int = 1
    risk_cap_cents: float | None = None
    side_filter: SideFilter = "both_sides"
    rv_gap_threshold: float | None = None
    soft_veto_cents: float | None = None
    vol_filter: str = "none"
    micro_filter: str = "none"
    price_filter: str = "none"

    @property
    def declared_position_cap_cents(self) -> float:
        if self.risk_cap_cents is not None:
            return self.risk_cap_cents
        return max(100.0, 100.0 * max(1, self.max_entries_per_market))

    @property
    def gate_count(self) -> int:
        count = 3  # timing window, EV threshold, entry rule.
        count += int(self.probability_mode != "rv600_primary")
        count += int(self.side_filter != "both_sides")
        count += int(self.soft_veto_cents is not None)
        count += int(self.vol_filter != "none")
        count += int(self.micro_filter != "none")
        count += int(self.price_filter != "none")
        return count


@dataclass(frozen=True)
class RV600CandidateMetrics:
    row: ReplayInput
    rv600_p_yes: float
    rv300_p_yes: float
    rv600_annualized_vol: float
    rv300_annualized_vol: float
    seconds_to_close: float
    book_age_ms: float | None
    depth_ratio: float | None
    spread_cents: float


@dataclass(frozen=True)
class CandidateDecision:
    market_ticker: str
    decision_ts_utc: datetime
    side: Side
    selected_ev_cents: float
    ask_cents: float
    risk_cents: float
    pnl_cents: float
    expected_pnl_cents: float
    matched_v28_pnl_cents: float
    matched_v28_ev_cents: float
    matched_v28_side: Side
    won: bool
    filled_counterfactual: bool
    is_added_entry: bool


@dataclass(frozen=True)
class RV600VariantRunRow:
    root_name: str
    variant: str
    accounting_mode: AccountingMode
    gate_count: int
    candidate_rows: int
    accepted_entries: int
    distinct_markets: int
    entries_per_market_max: int
    entries_per_market_distribution: dict[str, int]
    selected_pnl_cents: float
    fill_adjusted_expected_pnl_cents: float
    no_fill_penalty_pnl_cents: float
    matched_v28_control_pnl_cents: float
    matched_v28_delta_cents: float
    avg_pnl_per_entry_cents: float
    avg_pnl_per_market_cents: float
    win_count: int
    loss_count: int
    positive_market_rate: float
    max_single_market_pnl_share: float
    last_window_pnl_cents: float
    added_entry_count: int
    added_entry_pnl_cents: float
    avg_added_entry_pnl_cents: float
    worst_market_pnl_cents: float
    root_pass: bool
    rejection_reason: str


@dataclass(frozen=True)
class RV600VariantSummaryRow:
    variant: str
    accounting_mode: AccountingMode
    gate_count: int
    run_count: int
    candidate_rows: int
    accepted_entries: int
    distinct_markets: int
    selected_pnl_cents: float
    fill_adjusted_expected_pnl_cents: float
    no_fill_penalty_pnl_cents: float
    matched_v28_control_pnl_cents: float
    matched_v28_delta_cents: float
    avg_pnl_per_entry_cents: float
    avg_pnl_per_market_cents: float
    positive_root_count: int
    positive_root_rate: float
    positive_market_rate: float
    max_single_market_pnl_share: float
    last_window_pnl_cents: float
    added_entry_count: int
    added_entry_pnl_cents: float
    avg_added_entry_pnl_cents: float
    worst_market_pnl_cents: float
    retrospective_gate_pass: bool
    repeated_entry_gate_pass: bool
    locked_candidate_eligible: bool
    rejection_reason: str


@dataclass(frozen=True)
class RV600VariationReport:
    schema_version: str
    generated_utc: str
    phase: EvaluationPhase
    promotion_allowed: bool
    output_json: str
    output_md: str
    root_count: int
    roots: tuple[str, ...]
    variant_count: int
    best_by_total_pnl: str
    best_locked_candidate: str
    locked_candidates: tuple[str, ...]
    summary_rows: tuple[RV600VariantSummaryRow, ...]
    run_rows: tuple[RV600VariantRunRow, ...]
    conclusion: str


def first_candidate_specs() -> tuple[RV600VariantSpec, ...]:
    return (
        RV600VariantSpec(
            name="rv600_single_70_420_ev10",
            entry_rule="single_market",
            max_entries_per_market=1,
            min_ev_cents=10.0,
        ),
        RV600VariantSpec(
            name="rv600_max2_refresh120_70_420_ev10",
            entry_rule="same_side_refresh_120s",
            max_entries_per_market=2,
            min_ev_cents=10.0,
        ),
        RV600VariantSpec(
            name="rv600_max2_evstep5_70_420_ev10",
            entry_rule="same_side_ev_step_5c",
            max_entries_per_market=2,
            min_ev_cents=10.0,
        ),
        RV600VariantSpec(
            name="rv600_max3_risk200_70_420_ev10",
            entry_rule="risk_cap_200c",
            max_entries_per_market=3,
            risk_cap_cents=200.0,
            min_ev_cents=10.0,
        ),
        RV600VariantSpec(
            name="rv600_v28_softveto6_max2_70_420_ev8",
            entry_rule="same_side_refresh_120s",
            max_entries_per_market=2,
            min_ev_cents=8.0,
            soft_veto_cents=6.0,
        ),
        RV600VariantSpec(
            name="v28_95_rv600_05_70_420_ev8",
            probability_mode="blend_95_5",
            entry_rule="single_market",
            max_entries_per_market=1,
            min_ev_cents=8.0,
        ),
    )


def grid_specs() -> tuple[RV600VariantSpec, ...]:
    windows = (
        ("late_70_180", 70.0, 180.0),
        ("late_70_240", 70.0, 240.0),
        ("late_70_300", 70.0, 300.0),
        ("base_70_420", 70.0, 420.0),
        ("mid_120_420", 120.0, 420.0),
        ("mid_180_420", 180.0, 420.0),
        ("broad_70_600", 70.0, 600.0),
    )
    ev_thresholds = (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0)
    entry_rules: tuple[tuple[EntryRule, int, float | None], ...] = (
        ("single_market", 1, None),
        ("side_flip_only", 2, None),
        ("same_side_refresh_60s", 3, None),
        ("same_side_refresh_120s", 3, None),
        ("same_side_ev_step_3c", 3, None),
        ("same_side_ev_step_5c", 3, None),
        ("max_2_entries", 2, None),
        ("max_3_entries", 3, None),
        ("risk_cap_100c", 3, 100.0),
        ("risk_cap_200c", 3, 200.0),
    )
    probability_modes: tuple[tuple[ProbabilityMode, float | None], ...] = (
        ("rv600_primary", None),
        ("blend_95_5", None),
        ("blend_90_10", None),
        ("blend_80_20", None),
        ("rv600_primary", 6.0),
        ("rv600_primary", 10.0),
    )
    specs: list[RV600VariantSpec] = []
    seen: set[str] = set()
    for window_name, min_s, max_s in windows:
        for min_ev in ev_thresholds:
            for entry_rule, max_entries, risk_cap in entry_rules:
                for probability_mode, soft_veto in probability_modes:
                    prefix = probability_mode
                    if soft_veto is not None:
                        prefix = f"rv600_softveto{int(soft_veto)}"
                    name = (
                        f"{prefix}_{entry_rule}_{window_name}_ev{_fmt_cents(min_ev)}"
                    )
                    if name in seen:
                        continue
                    seen.add(name)
                    specs.append(
                        RV600VariantSpec(
                            name=name,
                            probability_mode=probability_mode,
                            min_seconds_to_close=min_s,
                            max_seconds_to_close=max_s,
                            min_ev_cents=min_ev,
                            entry_rule=entry_rule,
                            max_entries_per_market=max_entries,
                            risk_cap_cents=risk_cap,
                            soft_veto_cents=soft_veto,
                        )
                    )
    base_filters: list[RV600VariantSpec] = []
    for min_ev in (8.0, 10.0):
        for entry_rule, max_entries, risk_cap in (
            ("single_market", 1, None),
            ("same_side_refresh_120s", 2, None),
            ("same_side_ev_step_5c", 2, None),
        ):
            for side_filter, gap in (
                ("yes_only", None),
                ("no_only", None),
                ("side_by_v28_agreement", None),
                ("side_by_v28_disagreement", None),
                ("side_by_rv_gap", 0.05),
                ("side_by_rv_gap", 0.08),
                ("side_by_rv_gap", 0.10),
                ("side_by_rv_gap", 0.15),
            ):
                base_filters.append(
                    RV600VariantSpec(
                        name=(
                            f"rv600_{entry_rule}_{side_filter}"
                            f"{'' if gap is None else str(int(gap * 100)).zfill(2)}"
                            f"_70_420_ev{_fmt_cents(min_ev)}"
                        ),
                        min_ev_cents=min_ev,
                        entry_rule=entry_rule,
                        max_entries_per_market=max_entries,
                        risk_cap_cents=risk_cap,
                        side_filter=side_filter,  # type: ignore[arg-type]
                        rv_gap_threshold=gap,
                    )
                )
            for vol_filter in ("vol_mid", "vol_high", "vol_low", "vol_accel", "vol_decel", "strike_near", "strike_far"):
                base_filters.append(
                    RV600VariantSpec(
                        name=f"rv600_{entry_rule}_{vol_filter}_70_420_ev{_fmt_cents(min_ev)}",
                        min_ev_cents=min_ev,
                        entry_rule=entry_rule,
                        max_entries_per_market=max_entries,
                        risk_cap_cents=risk_cap,
                        vol_filter=vol_filter,
                    )
                )
            for micro_filter in (
                "book_age_250",
                "book_age_500",
                "depth_ratio_3",
                "depth_ratio_6",
                "spread_3c",
                "spread_5c",
                "fill_prob_50",
                "fill_prob_70",
            ):
                base_filters.append(
                    RV600VariantSpec(
                        name=f"rv600_{entry_rule}_{micro_filter}_70_420_ev{_fmt_cents(min_ev)}",
                        min_ev_cents=min_ev,
                        entry_rule=entry_rule,
                        max_entries_per_market=max_entries,
                        risk_cap_cents=risk_cap,
                        micro_filter=micro_filter,
                    )
                )
            for price_filter in ("ask_le_90", "ask_le_85", "ask_40_85", "cheap_tail", "rich_tail"):
                base_filters.append(
                    RV600VariantSpec(
                        name=f"rv600_{entry_rule}_{price_filter}_70_420_ev{_fmt_cents(min_ev)}",
                        min_ev_cents=min_ev,
                        entry_rule=entry_rule,
                        max_entries_per_market=max_entries,
                        risk_cap_cents=risk_cap,
                        price_filter=price_filter,
                    )
                )
    for spec in base_filters:
        if spec.name not in seen:
            seen.add(spec.name)
            specs.append(spec)
    return tuple(specs)


def locked_candidate_specs() -> tuple[RV600VariantSpec, ...]:
    return (
        RV600VariantSpec(
            name="rv600_primary_side_flip_only_broad_70_600_ev4",
            min_seconds_to_close=70.0,
            max_seconds_to_close=600.0,
            min_ev_cents=4.0,
            entry_rule="side_flip_only",
            max_entries_per_market=2,
        ),
        RV600VariantSpec(
            name="rv600_primary_max_3_entries_mid_120_420_ev12",
            min_seconds_to_close=120.0,
            max_seconds_to_close=420.0,
            min_ev_cents=12.0,
            entry_rule="max_3_entries",
            max_entries_per_market=3,
        ),
        RV600VariantSpec(
            name="rv600_primary_max_3_entries_base_70_420_ev12",
            min_seconds_to_close=70.0,
            max_seconds_to_close=420.0,
            min_ev_cents=12.0,
            entry_rule="max_3_entries",
            max_entries_per_market=3,
        ),
        RV600VariantSpec(
            name="rv600_primary_risk_cap_200c_mid_120_420_ev12",
            min_seconds_to_close=120.0,
            max_seconds_to_close=420.0,
            min_ev_cents=12.0,
            entry_rule="risk_cap_200c",
            max_entries_per_market=3,
            risk_cap_cents=200.0,
        ),
        RV600VariantSpec(
            name="rv600_primary_risk_cap_200c_base_70_420_ev12",
            min_seconds_to_close=70.0,
            max_seconds_to_close=420.0,
            min_ev_cents=12.0,
            entry_rule="risk_cap_200c",
            max_entries_per_market=3,
            risk_cap_cents=200.0,
        ),
        RV600VariantSpec(
            name="rv600_primary_max_2_entries_mid_120_420_ev12",
            min_seconds_to_close=120.0,
            max_seconds_to_close=420.0,
            min_ev_cents=12.0,
            entry_rule="max_2_entries",
            max_entries_per_market=2,
        ),
    )


def build_rv600_variation_report(
    roots: Sequence[Path] | None = None,
    *,
    phase: EvaluationPhase = "first_candidates",
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    config: ReplayConfig | None = None,
    min_decision_ts_utc: datetime | None = None,
) -> RV600VariationReport:
    selected_roots = tuple(roots) if roots is not None else discover_shadow_roots(DEFAULT_REAL_SHADOW_DIR)
    if phase == "first_candidates":
        specs = first_candidate_specs()
    elif phase == "locked":
        specs = locked_candidate_specs()
    else:
        specs = grid_specs()
    cfg = config or ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5)
    run_rows: list[RV600VariantRunRow] = []
    included_roots: list[str] = []
    for root in selected_roots:
        rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
        if min_decision_ts_utc is not None:
            rows = [
                row for row in rows
                if row.snapshot.decision_ts_utc >= min_decision_ts_utc
            ]
        if not rows:
            continue
        included_roots.append(root.name)
        extras_by_key = _extras_by_key(_candidate_path(root))
        metrics = materialize_rv600_metrics(rows, extras_by_key=extras_by_key)
        run_rows.extend(evaluate_variant_specs(metrics, specs, root_name=root.name, config=cfg))
    summary_rows = _summarize(run_rows)
    best_by_total = max(summary_rows, key=lambda row: row.selected_pnl_cents).variant if summary_rows else ""
    locked_candidates = tuple(row.variant for row in _locked_candidates(summary_rows))
    best_locked = locked_candidates[0] if locked_candidates else ""
    conclusion = _conclusion(summary_rows, locked_candidates, phase)
    return RV600VariationReport(
        schema_version="rv600-variation-test-v1",
        generated_utc=_utc_now(),
        phase=phase,
        promotion_allowed=False,
        output_json=str(output_json),
        output_md=str(output_md),
        root_count=len(included_roots),
        roots=tuple(included_roots),
        variant_count=len(specs),
        best_by_total_pnl=best_by_total,
        best_locked_candidate=best_locked,
        locked_candidates=locked_candidates,
        summary_rows=tuple(summary_rows),
        run_rows=tuple(run_rows),
        conclusion=conclusion,
    )


def materialize_rv600_metrics(
    rows: Sequence[ReplayInput],
    *,
    extras_by_key: Mapping[tuple[str, str], Mapping[str, Any]] | None = None,
) -> list[RV600CandidateMetrics]:
    if not rows:
        return []
    extras = extras_by_key or {}
    spec600 = DynamicParticleSpec(
        name="rv600",
        lookback_seconds=600.0,
        fallback_annualized_vol=0.65,
        min_annualized_vol=0.20,
        max_annualized_vol=2.50,
        min_distinct_observations=3,
    )
    spec300 = DynamicParticleSpec(
        name="rv300",
        lookback_seconds=300.0,
        fallback_annualized_vol=0.65,
        min_annualized_vol=0.20,
        max_annualized_vol=2.50,
        min_distinct_observations=3,
    )
    est600 = RollingVolEstimator(spec600)
    est300 = RollingVolEstimator(spec300)
    metrics_by_key: dict[tuple[str, str], RV600CandidateMetrics] = {}
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        vol600 = est600.observe_and_estimate(row.snapshot.decision_ts_utc, row.snapshot.spot)
        vol300 = est300.observe_and_estimate(row.snapshot.decision_ts_utc, row.snapshot.spot)
        seconds_to_close = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
        rv600_p = brownian_terminal_probability(row.snapshot.spot, row.snapshot.strike, seconds_to_close, vol600)
        rv300_p = brownian_terminal_probability(row.snapshot.spot, row.snapshot.strike, seconds_to_close, vol300)
        extra = extras.get(_row_key(row), {})
        depth_ratio = _optional_float(extra, "depth_ratio")
        if depth_ratio is None:
            depth_ratio = _optional_float(extra, "depth_count")
        metrics_by_key[_row_key(row)] = RV600CandidateMetrics(
            row=row,
            rv600_p_yes=_clamp01(rv600_p),
            rv300_p_yes=_clamp01(rv300_p),
            rv600_annualized_vol=vol600,
            rv300_annualized_vol=vol300,
            seconds_to_close=seconds_to_close,
            book_age_ms=_optional_float(extra, "book_age_ms"),
            depth_ratio=depth_ratio,
            spread_cents=max(0.0, row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0),
        )
    return [metrics_by_key[_row_key(row)] for row in rows]


def evaluate_variant_specs(
    metrics: Sequence[RV600CandidateMetrics],
    specs: Sequence[RV600VariantSpec],
    *,
    root_name: str,
    config: ReplayConfig | None = None,
) -> tuple[RV600VariantRunRow, ...]:
    cfg = config or ReplayConfig()
    rows: list[RV600VariantRunRow] = []
    sorted_metrics = sorted(metrics, key=lambda item: (item.row.snapshot.decision_ts_utc, item.row.snapshot.market_ticker))
    for spec in specs:
        accepted = _accepted_decisions(sorted_metrics, spec, cfg)
        rows.extend(_run_rows_for_accounting_modes(root_name, spec, len(metrics), accepted, cfg))
    return tuple(rows)


def write_rv600_variation_report(report: RV600VariationReport, *, include_run_rows: bool | None = None) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    include_runs = include_run_rows
    if include_runs is None:
        include_runs = len(report.run_rows) <= 5000
    payload = asdict(report)
    if not include_runs:
        payload["run_rows_omitted"] = len(report.run_rows)
        payload["run_rows"] = []
    else:
        payload["run_rows_omitted"] = 0
    output_json.write_text(json.dumps(payload, default=_json_default, indent=2, sort_keys=True), encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate RV600 strategy variations with repeated-entry, fill/fee, and matched-v28 accounting."
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--phase", choices=["first_candidates", "grid", "locked"], default="first_candidates")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument(
        "--min-decision-ts-utc",
        default="",
        help="optional ISO timestamp; only score candidate decisions at or after this UTC time",
    )
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_rv600_variation_report(
        tuple(args.root) if args.root else None,
        phase=args.phase,
        output_json=args.output_json,
        output_md=args.output_md,
        config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            no_fill_penalty_cents=args.no_fill_penalty_cents,
            counterfactual_fill_policy=args.counterfactual_fill_policy,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        min_decision_ts_utc=(_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None),
    )
    if args.write:
        write_rv600_variation_report(report)
    print(f"phase={report.phase}")
    print(f"root_count={report.root_count}")
    print(f"variant_count={report.variant_count}")
    print(f"best_by_total_pnl={report.best_by_total_pnl}")
    print(f"best_locked_candidate={report.best_locked_candidate}")
    print(f"locked_candidates={','.join(report.locked_candidates)}")
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _accepted_decisions(
    metrics: Sequence[RV600CandidateMetrics],
    spec: RV600VariantSpec,
    cfg: ReplayConfig,
) -> list[CandidateDecision]:
    state: dict[str, list[CandidateDecision]] = defaultdict(list)
    accepted: list[CandidateDecision] = []
    for metric in metrics:
        row = metric.row
        if not spec.min_seconds_to_close <= metric.seconds_to_close <= spec.max_seconds_to_close:
            continue
        p_strategy = _probability_for_mode(metric, spec.probability_mode)
        strategy_eval = _side_eval(row, p_strategy, cfg)
        if strategy_eval.best_ev_cents < spec.min_ev_cents:
            continue
        if strategy_eval.selected_fill_prob < cfg.min_fill_prob:
            continue
        v28_eval = _side_eval(row, row.current_calibrated_p_yes, cfg)
        if not _passes_side_filter(metric, strategy_eval, v28_eval, spec):
            continue
        if not _passes_v28_soft_veto(strategy_eval, v28_eval, spec):
            continue
        if not _passes_vol_filter(metric, spec.vol_filter):
            continue
        if not _passes_micro_filter(metric, strategy_eval.side, spec.micro_filter):
            continue
        if not _passes_price_filter(strategy_eval.ask_cents, spec.price_filter):
            continue
        previous = state[row.snapshot.market_ticker]
        if not _passes_entry_rule(previous, strategy_eval, spec, row.snapshot.decision_ts_utc):
            continue
        filled = _counterfactual_filled(strategy_eval.selected_fill_prob, cfg)
        pnl = _realized_pnl(row, strategy_eval.side, filled, cfg)
        matched_filled = _counterfactual_filled(v28_eval.selected_fill_prob, cfg)
        matched_pnl = _realized_pnl(row, v28_eval.side, matched_filled, cfg)
        decision = CandidateDecision(
            market_ticker=row.snapshot.market_ticker,
            decision_ts_utc=row.snapshot.decision_ts_utc,
            side=strategy_eval.side,
            selected_ev_cents=strategy_eval.best_ev_cents,
            ask_cents=strategy_eval.ask_cents,
            risk_cents=strategy_eval.ask_cents,
            pnl_cents=pnl,
            expected_pnl_cents=strategy_eval.best_ev_cents,
            matched_v28_pnl_cents=matched_pnl,
            matched_v28_ev_cents=v28_eval.best_ev_cents,
            matched_v28_side=v28_eval.side,
            won=_won(row, strategy_eval.side),
            filled_counterfactual=filled,
            is_added_entry=bool(previous),
        )
        previous.append(decision)
        accepted.append(decision)
    return accepted


@dataclass(frozen=True)
class _SideEval:
    side: Side
    ev_yes_cents: float
    ev_no_cents: float
    best_ev_cents: float
    selected_fill_prob: float
    ask_cents: float


def _side_eval(row: ReplayInput, p_yes: float, cfg: ReplayConfig) -> _SideEval:
    snapshot = row.snapshot
    ev_yes = expected_pnl_cents(
        p_win=_clamp01(p_yes),
        ask_cents=snapshot.yes_ask_cents,
        fee_if_win_cents=snapshot.fee_cents,
        fill_prob=_fill_prob_for(row, "yes"),
        no_fill_penalty_cents=cfg.no_fill_penalty_cents,
    )
    ev_no = expected_pnl_cents(
        p_win=1.0 - _clamp01(p_yes),
        ask_cents=snapshot.no_ask_cents,
        fee_if_win_cents=snapshot.fee_cents,
        fill_prob=_fill_prob_for(row, "no"),
        no_fill_penalty_cents=cfg.no_fill_penalty_cents,
    )
    side: Side = "yes" if ev_yes >= ev_no else "no"
    return _SideEval(
        side=side,
        ev_yes_cents=ev_yes,
        ev_no_cents=ev_no,
        best_ev_cents=max(ev_yes, ev_no),
        selected_fill_prob=_fill_prob_for(row, side),
        ask_cents=snapshot.yes_ask_cents if side == "yes" else snapshot.no_ask_cents,
    )


def _run_rows_for_accounting_modes(
    root_name: str,
    spec: RV600VariantSpec,
    candidate_rows: int,
    accepted: Sequence[CandidateDecision],
    cfg: ReplayConfig,
) -> tuple[RV600VariantRunRow, ...]:
    return (
        _build_run_row(root_name, spec, "all_entries", candidate_rows, list(accepted), cfg),
        _build_run_row(root_name, spec, "one_per_side_per_market", candidate_rows, _one_per_side(accepted), cfg),
        _build_run_row(
            root_name,
            spec,
            "position_capped",
            candidate_rows,
            _position_capped(accepted, spec.declared_position_cap_cents),
            cfg,
        ),
    )


def _build_run_row(
    root_name: str,
    spec: RV600VariantSpec,
    accounting_mode: AccountingMode,
    candidate_rows: int,
    accepted: Sequence[CandidateDecision],
    cfg: ReplayConfig,
) -> RV600VariantRunRow:
    by_market: dict[str, list[CandidateDecision]] = defaultdict(list)
    for decision in accepted:
        by_market[decision.market_ticker].append(decision)
    market_pnls = {market: sum(decision.pnl_cents for decision in decisions) for market, decisions in by_market.items()}
    entries_distribution: dict[str, int] = defaultdict(int)
    for decisions in by_market.values():
        entries_distribution[str(len(decisions))] += 1
    total_pnl = sum(decision.pnl_cents for decision in accepted)
    expected_pnl = sum(decision.expected_pnl_cents for decision in accepted)
    matched_v28_pnl = sum(decision.matched_v28_pnl_cents for decision in accepted)
    no_fill_penalty_pnl = (
        sum(
            decision.pnl_cents if decision.filled_counterfactual else -cfg.no_fill_penalty_cents
            for decision in accepted
        )
        if accepted
        else 0.0
    )
    win_count = sum(1 for decision in accepted if decision.won)
    loss_count = len(accepted) - win_count
    added = [decision for decision in accepted if decision.is_added_entry]
    max_share = _max_single_market_share(market_pnls, total_pnl)
    last_window = sum(decision.pnl_cents for decision in list(accepted)[-20:])
    positive_market_rate = (
        sum(1 for pnl in market_pnls.values() if pnl > 0.0) / len(market_pnls)
        if market_pnls
        else 0.0
    )
    rejection = _run_rejection_reason(
        accepted_count=len(accepted),
        distinct_markets=len(by_market),
        total_pnl=total_pnl,
        avg_entry=total_pnl / len(accepted) if accepted else 0.0,
        positive_market_rate=positive_market_rate,
        max_share=max_share,
        last_window=last_window,
        expected_pnl=expected_pnl,
    )
    return RV600VariantRunRow(
        root_name=root_name,
        variant=spec.name,
        accounting_mode=accounting_mode,
        gate_count=spec.gate_count,
        candidate_rows=candidate_rows,
        accepted_entries=len(accepted),
        distinct_markets=len(by_market),
        entries_per_market_max=max((len(decisions) for decisions in by_market.values()), default=0),
        entries_per_market_distribution=dict(sorted(entries_distribution.items(), key=lambda item: int(item[0]))),
        selected_pnl_cents=total_pnl,
        fill_adjusted_expected_pnl_cents=expected_pnl,
        no_fill_penalty_pnl_cents=no_fill_penalty_pnl,
        matched_v28_control_pnl_cents=matched_v28_pnl,
        matched_v28_delta_cents=total_pnl - matched_v28_pnl,
        avg_pnl_per_entry_cents=total_pnl / len(accepted) if accepted else 0.0,
        avg_pnl_per_market_cents=total_pnl / len(by_market) if by_market else 0.0,
        win_count=win_count,
        loss_count=loss_count,
        positive_market_rate=positive_market_rate,
        max_single_market_pnl_share=max_share,
        last_window_pnl_cents=last_window,
        added_entry_count=len(added),
        added_entry_pnl_cents=sum(decision.pnl_cents for decision in added),
        avg_added_entry_pnl_cents=(sum(decision.pnl_cents for decision in added) / len(added) if added else 0.0),
        worst_market_pnl_cents=min(market_pnls.values()) if market_pnls else 0.0,
        root_pass=(rejection == ""),
        rejection_reason=rejection,
    )


def _summarize(run_rows: Sequence[RV600VariantRunRow]) -> tuple[RV600VariantSummaryRow, ...]:
    grouped: dict[tuple[str, AccountingMode], list[RV600VariantRunRow]] = defaultdict(list)
    for row in run_rows:
        grouped[(row.variant, row.accounting_mode)].append(row)
    summaries: list[RV600VariantSummaryRow] = []
    for (variant, accounting_mode), rows in grouped.items():
        market_count = sum(row.distinct_markets for row in rows)
        accepted = sum(row.accepted_entries for row in rows)
        total_pnl = sum(row.selected_pnl_cents for row in rows)
        expected_pnl = sum(row.fill_adjusted_expected_pnl_cents for row in rows)
        no_fill_pnl = sum(row.no_fill_penalty_pnl_cents for row in rows)
        matched_v28_pnl = sum(row.matched_v28_control_pnl_cents for row in rows)
        candidate_rows = sum(row.candidate_rows for row in rows)
        positive_roots = sum(1 for row in rows if row.selected_pnl_cents > 0.0)
        weighted_market_rate = (
            sum(row.positive_market_rate * row.distinct_markets for row in rows) / market_count
            if market_count
            else 0.0
        )
        max_market_contribution = max(
            (
                row.max_single_market_pnl_share * row.selected_pnl_cents
                if row.selected_pnl_cents > 0.0
                else 0.0
            )
            for row in rows
        )
        max_share = max_market_contribution / total_pnl if total_pnl > 0.0 else 0.0
        last_window = sum(row.last_window_pnl_cents for row in rows[-1:])
        added_entries = sum(row.added_entry_count for row in rows)
        added_pnl = sum(row.added_entry_pnl_cents for row in rows)
        summary = RV600VariantSummaryRow(
            variant=variant,
            accounting_mode=accounting_mode,
            gate_count=max(row.gate_count for row in rows),
            run_count=len(rows),
            candidate_rows=candidate_rows,
            accepted_entries=accepted,
            distinct_markets=market_count,
            selected_pnl_cents=total_pnl,
            fill_adjusted_expected_pnl_cents=expected_pnl,
            no_fill_penalty_pnl_cents=no_fill_pnl,
            matched_v28_control_pnl_cents=matched_v28_pnl,
            matched_v28_delta_cents=total_pnl - matched_v28_pnl,
            avg_pnl_per_entry_cents=(total_pnl / accepted if accepted else 0.0),
            avg_pnl_per_market_cents=(total_pnl / market_count if market_count else 0.0),
            positive_root_count=positive_roots,
            positive_root_rate=(positive_roots / len(rows) if rows else 0.0),
            positive_market_rate=weighted_market_rate,
            max_single_market_pnl_share=max_share,
            last_window_pnl_cents=last_window,
            added_entry_count=added_entries,
            added_entry_pnl_cents=added_pnl,
            avg_added_entry_pnl_cents=(added_pnl / added_entries if added_entries else 0.0),
            worst_market_pnl_cents=min((row.worst_market_pnl_cents for row in rows), default=0.0),
            retrospective_gate_pass=False,
            repeated_entry_gate_pass=False,
            locked_candidate_eligible=False,
            rejection_reason="pending",
        )
        summaries.append(summary)
    summary_lookup = {
        (row.variant, row.accounting_mode): row
        for row in summaries
    }
    final_rows = [
        _with_summary_gates(row, _matching_single_market_baseline(row, summary_lookup))
        for row in summaries
    ]
    return tuple(
        sorted(
            final_rows,
            key=lambda row: (
                row.locked_candidate_eligible,
                row.retrospective_gate_pass,
                row.repeated_entry_gate_pass,
                row.selected_pnl_cents,
                row.matched_v28_delta_cents,
            ),
            reverse=True,
        )
    )


def _with_summary_gates(
    row: RV600VariantSummaryRow,
    single_market: RV600VariantSummaryRow | None,
) -> RV600VariantSummaryRow:
    reasons: list[str] = []
    if row.accepted_entries < 25:
        reasons.append("fewer_than_25_entries")
    if row.selected_pnl_cents <= 0.0:
        reasons.append("nonpositive_pnl")
    if row.avg_pnl_per_entry_cents < 10.0:
        reasons.append("avg_entry_below_10c")
    if row.positive_root_rate < 0.60:
        reasons.append("positive_roots_below_60pct")
    if row.positive_market_rate < 0.60:
        reasons.append("positive_markets_below_60pct")
    if row.max_single_market_pnl_share > 0.25:
        reasons.append("single_market_share_above_25pct")
    if row.last_window_pnl_cents <= 0.0:
        reasons.append("last_window_nonpositive")
    if row.matched_v28_control_pnl_cents > 0.0 and row.selected_pnl_cents < 1.20 * row.matched_v28_control_pnl_cents:
        reasons.append("does_not_beat_matched_v28_by_20pct")
    if row.no_fill_penalty_pnl_cents <= 0.0:
        reasons.append("no_fill_penalty_nonpositive")
    retrospective = not reasons

    repeated_reasons: list[str] = []
    repeated_variant = _is_repeated_entry_variant(row.variant)
    if repeated_variant:
        if single_market is None:
            repeated_reasons.append("missing_single_market_benchmark")
        elif row.selected_pnl_cents <= single_market.selected_pnl_cents:
            repeated_reasons.append("does_not_beat_single_market")
        if row.added_entry_count <= 0 or row.avg_added_entry_pnl_cents <= 0.0:
            repeated_reasons.append("added_entries_nonpositive")
        if single_market is not None and row.avg_pnl_per_market_cents <= single_market.avg_pnl_per_market_cents:
            repeated_reasons.append("avg_market_not_improved")
        if single_market is not None and _drawdown_worse(row.worst_market_pnl_cents, single_market.worst_market_pnl_cents):
            repeated_reasons.append("market_drawdown_worse_than_25pct")
    elif row.accounting_mode == "all_entries" and row.variant == "rv600_single_70_420_ev10":
        repeated_reasons.append("single_market_benchmark")
    repeated = retrospective and not repeated_reasons
    locked = (
        retrospective
        and (not repeated_variant or repeated)
        and row.accounting_mode != "all_entries"
        and row.gate_count <= 3
    )
    rejection = ";".join(reasons + repeated_reasons)
    return RV600VariantSummaryRow(
        **{
            **asdict(row),
            "retrospective_gate_pass": retrospective,
            "repeated_entry_gate_pass": repeated,
            "locked_candidate_eligible": locked,
            "rejection_reason": rejection,
        }
    )


def _matching_single_market_baseline(
    row: RV600VariantSummaryRow,
    summary_lookup: Mapping[tuple[str, AccountingMode], RV600VariantSummaryRow],
) -> RV600VariantSummaryRow | None:
    if not _is_repeated_entry_variant(row.variant):
        return None
    baseline_name = _single_market_baseline_name(row.variant)
    candidates: list[tuple[str, AccountingMode]] = []
    if baseline_name:
        candidates.append((baseline_name, row.accounting_mode))
        candidates.append((baseline_name, "all_entries"))
    candidates.append(("rv600_single_70_420_ev10", row.accounting_mode))
    candidates.append(("rv600_single_70_420_ev10", "all_entries"))
    for key in candidates:
        baseline = summary_lookup.get(key)
        if baseline is not None and baseline.variant != row.variant:
            return baseline
    return None


def _single_market_baseline_name(variant: str) -> str | None:
    first_candidate_map = {
        "rv600_max2_refresh120_70_420_ev10": "rv600_single_70_420_ev10",
        "rv600_max2_evstep5_70_420_ev10": "rv600_single_70_420_ev10",
        "rv600_max3_risk200_70_420_ev10": "rv600_single_70_420_ev10",
        "rv600_v28_softveto6_max2_70_420_ev8": "rv600_single_70_420_ev10",
    }
    if variant in first_candidate_map:
        return first_candidate_map[variant]
    for rule in sorted(_REPEATED_ENTRY_RULE_NAMES, key=len, reverse=True):
        marker = f"_{rule}_"
        if marker in variant:
            return variant.replace(marker, "_single_market_", 1)
    return None


def _is_repeated_entry_variant(variant: str) -> bool:
    return (
        variant in {
            "rv600_max2_refresh120_70_420_ev10",
            "rv600_max2_evstep5_70_420_ev10",
            "rv600_max3_risk200_70_420_ev10",
            "rv600_v28_softveto6_max2_70_420_ev8",
        }
        or any(f"_{rule}_" in variant for rule in _REPEATED_ENTRY_RULE_NAMES)
    )


_REPEATED_ENTRY_RULE_NAMES = (
    "side_flip_only",
    "same_side_refresh_60s",
    "same_side_refresh_120s",
    "same_side_ev_step_3c",
    "same_side_ev_step_5c",
    "max_2_entries",
    "max_3_entries",
    "risk_cap_100c",
    "risk_cap_200c",
)


def _locked_candidates(summary_rows: Sequence[RV600VariantSummaryRow]) -> tuple[RV600VariantSummaryRow, ...]:
    chosen: list[RV600VariantSummaryRow] = []
    seen: set[str] = set()
    for row in summary_rows:
        if not row.locked_candidate_eligible:
            continue
        if row.variant in seen:
            continue
        chosen.append(row)
        seen.add(row.variant)
        if len(chosen) >= 5:
            break
    return tuple(chosen)


def _one_per_side(accepted: Sequence[CandidateDecision]) -> list[CandidateDecision]:
    seen: set[tuple[str, Side]] = set()
    kept: list[CandidateDecision] = []
    for decision in accepted:
        key = (decision.market_ticker, decision.side)
        if key in seen:
            continue
        seen.add(key)
        kept.append(decision)
    return kept


def _position_capped(accepted: Sequence[CandidateDecision], cap_cents: float) -> list[CandidateDecision]:
    risk_by_market: dict[str, float] = defaultdict(float)
    kept: list[CandidateDecision] = []
    for decision in accepted:
        if risk_by_market[decision.market_ticker] + decision.risk_cents > cap_cents:
            continue
        risk_by_market[decision.market_ticker] += decision.risk_cents
        kept.append(decision)
    return kept


def _passes_entry_rule(
    previous: Sequence[CandidateDecision],
    side_eval: _SideEval,
    spec: RV600VariantSpec,
    decision_ts: datetime,
) -> bool:
    if len(previous) >= spec.max_entries_per_market:
        return False
    if spec.risk_cap_cents is not None:
        if sum(decision.risk_cents for decision in previous) + side_eval.ask_cents > spec.risk_cap_cents:
            return False
    if not previous:
        return True
    if spec.entry_rule == "single_market":
        return False
    if spec.entry_rule == "side_flip_only":
        return all(decision.side != side_eval.side for decision in previous)
    if spec.entry_rule in ("max_2_entries", "max_3_entries", "risk_cap_100c", "risk_cap_200c"):
        return True
    same_side = [decision for decision in previous if decision.side == side_eval.side]
    if not same_side:
        return True
    last_same = same_side[-1]
    if spec.entry_rule == "same_side_refresh_60s":
        return (decision_ts - last_same.decision_ts_utc).total_seconds() >= 60.0
    if spec.entry_rule == "same_side_refresh_120s":
        return (decision_ts - last_same.decision_ts_utc).total_seconds() >= 120.0
    if spec.entry_rule == "same_side_ev_step_3c":
        return side_eval.best_ev_cents >= last_same.selected_ev_cents + 3.0
    if spec.entry_rule == "same_side_ev_step_5c":
        return side_eval.best_ev_cents >= last_same.selected_ev_cents + 5.0
    return False


def _passes_side_filter(
    metric: RV600CandidateMetrics,
    strategy_eval: _SideEval,
    v28_eval: _SideEval,
    spec: RV600VariantSpec,
) -> bool:
    if spec.side_filter == "both_sides":
        return True
    if spec.side_filter == "yes_only":
        return strategy_eval.side == "yes"
    if spec.side_filter == "no_only":
        return strategy_eval.side == "no"
    if spec.side_filter == "side_by_v28_agreement":
        return strategy_eval.side == v28_eval.side
    if spec.side_filter == "side_by_v28_disagreement":
        return strategy_eval.side != v28_eval.side
    if spec.side_filter == "side_by_rv_gap":
        threshold = spec.rv_gap_threshold or 0.0
        row = metric.row
        if strategy_eval.side == "yes":
            gap = abs(metric.rv600_p_yes - break_even_probability(row.snapshot.yes_ask_cents, row.snapshot.fee_cents))
        else:
            gap = abs((1.0 - metric.rv600_p_yes) - break_even_probability(row.snapshot.no_ask_cents, row.snapshot.fee_cents))
        return gap >= threshold
    return True


def _passes_v28_soft_veto(strategy_eval: _SideEval, v28_eval: _SideEval, spec: RV600VariantSpec) -> bool:
    if spec.soft_veto_cents is None:
        return True
    if strategy_eval.side == v28_eval.side:
        return True
    return (v28_eval.best_ev_cents - strategy_eval.best_ev_cents) < spec.soft_veto_cents


def _passes_vol_filter(metric: RV600CandidateMetrics, vol_filter: str) -> bool:
    if vol_filter == "none":
        return True
    vol = metric.rv600_annualized_vol
    if vol_filter == "vol_mid":
        return 0.4 <= vol <= 1.5
    if vol_filter == "vol_high":
        return vol > 1.5
    if vol_filter == "vol_low":
        return vol < 0.4
    ratio = metric.rv300_annualized_vol / vol if vol > 0.0 else 0.0
    if vol_filter == "vol_accel":
        return ratio > 1.2
    if vol_filter == "vol_decel":
        return ratio < 0.8
    if vol_filter in ("strike_near", "strike_far"):
        sigma = metric.row.snapshot.spot * vol * math.sqrt(max(metric.seconds_to_close, 0.0) / SECONDS_PER_YEAR)
        if sigma <= 0.0:
            return False
        distance_sigma = abs(metric.row.snapshot.spot - metric.row.snapshot.strike) / sigma
        return distance_sigma <= 1.25 if vol_filter == "strike_near" else distance_sigma > 1.25
    return True


def _passes_micro_filter(metric: RV600CandidateMetrics, side: Side, micro_filter: str) -> bool:
    if micro_filter == "none":
        return True
    if micro_filter == "book_age_250":
        return metric.book_age_ms is not None and metric.book_age_ms <= 250.0
    if micro_filter == "book_age_500":
        return metric.book_age_ms is not None and metric.book_age_ms <= 500.0
    if micro_filter == "depth_ratio_3":
        return metric.depth_ratio is not None and metric.depth_ratio >= 3.0
    if micro_filter == "depth_ratio_6":
        return metric.depth_ratio is not None and metric.depth_ratio >= 6.0
    if micro_filter == "spread_3c":
        return metric.spread_cents <= 3.0
    if micro_filter == "spread_5c":
        return metric.spread_cents <= 5.0
    fill_prob = _fill_prob_for(metric.row, side)
    if micro_filter == "fill_prob_50":
        return fill_prob >= 0.50
    if micro_filter == "fill_prob_70":
        return fill_prob >= 0.70
    return True


def _passes_price_filter(ask_cents: float, price_filter: str) -> bool:
    if price_filter == "none":
        return True
    if price_filter == "ask_le_90":
        return ask_cents <= 90.0
    if price_filter == "ask_le_85":
        return ask_cents <= 85.0
    if price_filter == "ask_40_85":
        return 40.0 <= ask_cents <= 85.0
    if price_filter == "cheap_tail":
        return ask_cents <= 30.0
    if price_filter == "rich_tail":
        return ask_cents >= 80.0
    return True


def _probability_for_mode(metric: RV600CandidateMetrics, mode: ProbabilityMode) -> float:
    current = metric.row.current_calibrated_p_yes
    rv600 = metric.rv600_p_yes
    if mode == "rv600_primary":
        return rv600
    if mode == "v28_primary":
        return current
    if mode == "blend_95_5":
        return _clamp01(0.95 * current + 0.05 * rv600)
    if mode == "blend_90_10":
        return _clamp01(0.90 * current + 0.10 * rv600)
    if mode == "blend_80_20":
        return _clamp01(0.80 * current + 0.20 * rv600)
    raise ValueError(f"unsupported probability mode: {mode}")


def _run_rejection_reason(
    *,
    accepted_count: int,
    distinct_markets: int,
    total_pnl: float,
    avg_entry: float,
    positive_market_rate: float,
    max_share: float,
    last_window: float,
    expected_pnl: float,
) -> str:
    reasons: list[str] = []
    if accepted_count == 0:
        reasons.append("no_entries")
    if distinct_markets == 0:
        reasons.append("no_markets")
    if total_pnl <= 0.0:
        reasons.append("nonpositive_pnl")
    if expected_pnl <= 0.0:
        reasons.append("nonpositive_fill_adjusted_ev")
    if avg_entry < 10.0:
        reasons.append("avg_entry_below_10c")
    if positive_market_rate < 0.60:
        reasons.append("positive_markets_below_60pct")
    if max_share > 0.25:
        reasons.append("single_market_share_above_25pct")
    if last_window <= 0.0:
        reasons.append("last_window_nonpositive")
    return ";".join(reasons)


def _extras_by_key(candidate_path: Path) -> dict[tuple[str, str], Mapping[str, Any]]:
    extras: dict[tuple[str, str], Mapping[str, Any]] = {}
    with candidate_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            raw = payload.get("snapshot", payload)
            extra = payload.get("extra", {})
            key = (str(raw["market_ticker"]), _parse_dt(raw["decision_ts_utc"]).isoformat())
            extras[key] = dict(extra)
    return extras


def _row_key(row: ReplayInput) -> tuple[str, str]:
    return (row.snapshot.market_ticker, row.snapshot.decision_ts_utc.isoformat())


def _candidate_path(root: Path) -> Path:
    return root / "candidate_snapshots" / "candidate_snapshots.ndjson"


def _label_path(root: Path) -> Path:
    return root / "pipeline_work" / "label_contexts_full_refresh.ndjson"


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _optional_float(raw: Mapping[str, Any], name: str) -> float | None:
    if name not in raw or raw[name] in (None, ""):
        return None
    return float(raw[name])


def _fill_prob_for(row: ReplayInput, side: Side) -> float:
    snapshot = row.snapshot
    if side == "yes" and snapshot.yes_fill_prob is not None:
        return snapshot.yes_fill_prob
    if side == "no" and snapshot.no_fill_prob is not None:
        return snapshot.no_fill_prob
    return snapshot.fill_prob


def _counterfactual_filled(fill_prob: float, cfg: ReplayConfig) -> bool:
    if cfg.counterfactual_fill_policy == "always_fill":
        return True
    if cfg.counterfactual_fill_policy == "never_fill":
        return False
    return fill_prob >= cfg.counterfactual_fill_threshold


def _won(row: ReplayInput, side: Side) -> bool:
    return row.label.result_yes if side == "yes" else not row.label.result_yes


def _realized_pnl(row: ReplayInput, side: Side, filled: bool, cfg: ReplayConfig) -> float:
    if not filled:
        return -cfg.no_fill_penalty_cents
    won = _won(row, side)
    ask = row.snapshot.yes_ask_cents if side == "yes" else row.snapshot.no_ask_cents
    if won:
        return 100.0 - ask - row.snapshot.fee_cents
    return -ask


def _max_single_market_share(market_pnls: Mapping[str, float], total_pnl: float) -> float:
    if total_pnl <= 0.0 or not market_pnls:
        return 0.0
    return max(max(0.0, pnl) for pnl in market_pnls.values()) / total_pnl


def _drawdown_worse(worst: float, baseline_worst: float) -> bool:
    if worst >= 0.0:
        return False
    if baseline_worst >= 0.0:
        return True
    return abs(worst) > 1.25 * abs(baseline_worst)


def _conclusion(
    summary_rows: Sequence[RV600VariantSummaryRow],
    locked_candidates: Sequence[str],
    phase: EvaluationPhase,
) -> str:
    if not summary_rows:
        return "No eligible roots were found."
    best = summary_rows[0]
    if locked_candidates:
        return (
            f"{phase} found retrospective locked-candidate candidates, led by {locked_candidates[0]}. "
            "Promotion is still blocked until fresh forward shadow reaches the predeclared sample gates."
        )
    return (
        f"{phase} found best total PnL row {best.variant}/{best.accounting_mode} at "
        f"{best.selected_pnl_cents:.1f}c, but no candidate cleared the locked simplification gates. "
        "Keep RV600 research-only."
    )


def _markdown(report: RV600VariationReport) -> str:
    lines = [
        "# RV600 Variation Test Report",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- phase: {report.phase}",
        f"- promotion_allowed: {report.promotion_allowed}",
        f"- root_count: {report.root_count}",
        f"- variant_count: {report.variant_count}",
        f"- best_by_total_pnl: {report.best_by_total_pnl}",
        f"- best_locked_candidate: {report.best_locked_candidate}",
        f"- locked_candidates: {', '.join(report.locked_candidates) if report.locked_candidates else 'none'}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Top Summary Rows",
        "",
        "| variant | accounting | gates | entries | markets | pnl_c | v28_delta_c | avg_entry_c | avg_market_c | +roots | +markets | max_market_share | last20_c | added_avg_c | locked? | reject |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report.summary_rows[:40]:
        lines.append(
            "| {variant} | {accounting_mode} | {gate_count} | {accepted_entries} | {distinct_markets} | "
            "{selected_pnl_cents:.1f} | {matched_v28_delta_cents:.1f} | "
            "{avg_pnl_per_entry_cents:.2f} | {avg_pnl_per_market_cents:.2f} | "
            "{positive_root_count}/{run_count} | {positive_market_rate:.2f} | "
            "{max_single_market_pnl_share:.2f} | {last_window_pnl_cents:.1f} | "
            "{avg_added_entry_pnl_cents:.2f} | {locked_candidate_eligible} | {rejection_reason} |".format(
                **asdict(row)
            )
        )
    lines.extend(["", "## Roots", ""])
    for root in report.roots:
        lines.append(f"- {root}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is discovery/shadow research only; it does not place orders or change live v28 logic.",
            "- Repeated-entry variants are reported under all_entries, one_per_side_per_market, and position_capped accounting.",
            "- Locked-candidate eligibility is retrospective only and still requires forward-shadow validation before any live pilot.",
        ]
    )
    return "\n".join(lines) + "\n"


def _fmt_cents(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value).replace(".", "p")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


if __name__ == "__main__":
    raise SystemExit(main())
