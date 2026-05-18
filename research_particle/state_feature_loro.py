from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Sequence

from .meta_probability_loro import (
    MetaModelSpec,
    _clamp01,
    _load_run,
    _logit,
    _predict_model,
    _train_model,
)
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay


@dataclass(frozen=True)
class StateFeatureHoldoutRow:
    holdout_run: str
    model: str
    train_run_count: int
    train_market_count: int
    holdout_candidate_count: int
    holdout_market_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    strict_gate_pass: bool
    train_loss: float
    weights: tuple[float, ...]


@dataclass(frozen=True)
class StateFeatureSummaryRow:
    model: str
    holdout_count: int
    total_counterfactual_pnl_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    strict_gate_count: int
    strict_all_holdouts: bool


@dataclass(frozen=True)
class StateFeatureLOROReport:
    run_inputs: tuple[object, ...]
    holdout_rows: tuple[StateFeatureHoldoutRow, ...]
    summary_rows: tuple[StateFeatureSummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_state_feature_loro_report(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    learning_rate: float = 0.05,
    l2: float = 0.50,
    epochs: int = 1200,
) -> StateFeatureLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]
    holdout_rows: list[StateFeatureHoldoutRow] = []
    for holdout_name, holdout_meta, holdout_rows_raw in loaded_runs:
        train = [
            row
            for run_name, _, rows in loaded_runs
            if run_name != holdout_name
            for row in rows
        ]
        train_market_count = len({row.snapshot.market_ticker for row in train})
        for spec in _state_specs():
            model = _train_model(
                spec,
                train,
                learning_rate=learning_rate,
                l2=l2,
                epochs=epochs,
            )
            variant_rows = [
                replace(row, particle_p_yes=_clamp01(_predict_model(model, row)))
                for row in holdout_rows_raw
            ]
            replay = evaluate_replay(variant_rows, cfg)
            strict = (
                replay.total_counterfactual_pnl_cents > 0.0
                and replay.particle_beats_brownian
                and replay.particle_beats_market
                and replay.particle_beats_current_calibrated
                and replay.ev_rank_correlation_sign > 0.0
                and replay.top_ev_bucket_pnl_cents > 0.0
            )
            holdout_rows.append(
                StateFeatureHoldoutRow(
                    holdout_run=holdout_name,
                    model=spec.name,
                    train_run_count=len(run_roots) - 1,
                    train_market_count=train_market_count,
                    holdout_candidate_count=replay.candidate_count,
                    holdout_market_count=holdout_meta.market_count,
                    selected_count=replay.selected_count,
                    total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                    brier=replay.particle.brier,
                    log_loss=replay.particle.log_loss,
                    beats_brownian=replay.particle_beats_brownian,
                    beats_market=replay.particle_beats_market,
                    beats_current_calibrated=replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                    strict_gate_pass=strict,
                    train_loss=model.train_loss,
                    weights=model.weights,
                )
            )
    summaries = tuple(_summarize(holdout_rows))
    promotion_safe = any(row.strict_all_holdouts for row in summaries)
    conclusion = (
        "At least one state-feature model passes every strict locked holdout; still predeclare "
        "a fresh locked OOS run before promotion."
        if promotion_safe
        else "No timestamp-available state-feature model passes strict locked holdout gates."
    )
    return StateFeatureLOROReport(
        run_inputs=tuple(meta for _, meta, _ in loaded_runs),
        holdout_rows=tuple(holdout_rows),
        summary_rows=summaries,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_state_feature_loro_report(
    report: StateFeatureLOROReport,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train small state-feature probability models on all-but-one locked runs and replay holdouts."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="state_feature_loro")
    parser.add_argument("--learning-rate", default=0.05, type=float)
    parser.add_argument("--l2", default=0.50, type=float)
    parser.add_argument("--epochs", default=1200, type=int)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_state_feature_loro_report(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        learning_rate=args.learning_rate,
        l2=args.l2,
        epochs=args.epochs,
    )
    json_path, md_path = write_state_feature_loro_report(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _state_specs() -> tuple[MetaModelSpec, ...]:
    return (
        MetaModelSpec(
            "state_moneyness_time",
            ("moneyness_bps", "abs_moneyness_bps", "sqrt_time_frac", "time_frac"),
            lambda row: (
                _moneyness_bps(row),
                abs(_moneyness_bps(row)),
                math.sqrt(max(0.0, _time_frac(row))),
                _time_frac(row),
            ),
        ),
        MetaModelSpec(
            "state_book_cost",
            (
                "moneyness_bps",
                "time_frac",
                "yes_ask_norm",
                "no_ask_norm",
                "spread_norm",
                "fee_norm",
                "fill_prob",
            ),
            lambda row: (
                _moneyness_bps(row),
                _time_frac(row),
                row.snapshot.yes_ask_cents / 100.0,
                row.snapshot.no_ask_cents / 100.0,
                (row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0) / 100.0,
                row.snapshot.fee_cents / 100.0,
                row.snapshot.fill_prob,
            ),
        ),
        MetaModelSpec(
            "state_plus_market_current",
            (
                "moneyness_bps",
                "time_frac",
                "spread_norm",
                "logit_market",
                "logit_current",
            ),
            lambda row: (
                _moneyness_bps(row),
                _time_frac(row),
                (row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0) / 100.0,
                _logit(row.market_p_yes),
                _logit(row.current_calibrated_p_yes),
            ),
        ),
        MetaModelSpec(
            "state_plus_residuals",
            (
                "moneyness_bps",
                "time_frac",
                "logit_current",
                "market_minus_current",
                "particle_minus_current",
                "yes_fill",
                "no_fill",
            ),
            lambda row: (
                _moneyness_bps(row),
                _time_frac(row),
                _logit(row.current_calibrated_p_yes),
                row.market_p_yes - row.current_calibrated_p_yes,
                row.particle_p_yes - row.current_calibrated_p_yes,
                row.snapshot.yes_fill_prob if row.snapshot.yes_fill_prob is not None else row.snapshot.fill_prob,
                row.snapshot.no_fill_prob if row.snapshot.no_fill_prob is not None else row.snapshot.fill_prob,
            ),
        ),
    )


def _moneyness_bps(row: ReplayInput) -> float:
    if row.snapshot.strike <= 0.0 or row.snapshot.spot <= 0.0:
        return 0.0
    return 10_000.0 * math.log(row.snapshot.spot / row.snapshot.strike)


def _time_frac(row: ReplayInput) -> float:
    seconds = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
    return min(1.5, seconds / 900.0)


def _summarize(rows: Sequence[StateFeatureHoldoutRow]) -> list[StateFeatureSummaryRow]:
    grouped: dict[str, list[StateFeatureHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.model, []).append(row)
    summaries: list[StateFeatureSummaryRow] = []
    for model in sorted(grouped):
        model_rows = grouped[model]
        strict_count = sum(1 for row in model_rows if row.strict_gate_pass)
        summaries.append(
            StateFeatureSummaryRow(
                model=model,
                holdout_count=len(model_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in model_rows),
                mean_brier=_mean(row.brier for row in model_rows),
                mean_log_loss=_mean(row.log_loss for row in model_rows),
                positive_pnl_count=sum(1 for row in model_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in model_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in model_rows if row.beats_market),
                beats_current_count=sum(1 for row in model_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in model_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in model_rows if row.top_ev_bucket_pnl_cents > 0.0),
                strict_gate_count=strict_count,
                strict_all_holdouts=(strict_count == len(model_rows) and bool(model_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_holdouts,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _mean(values) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _markdown(report: StateFeatureLOROReport) -> str:
    lines = [
        "# State Feature LORO Report",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| model | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.model} | "
            f"{row.holdout_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.holdout_count} | "
            f"{row.beats_brownian_count}/{row.holdout_count} | "
            f"{row.beats_market_count}/{row.holdout_count} | "
            f"{row.beats_current_count}/{row.holdout_count} | "
            f"{row.positive_ev_rank_count}/{row.holdout_count} | "
            f"{row.positive_top_bucket_count}/{row.holdout_count} | "
            f"{row.strict_gate_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| holdout | model | train_markets | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.holdout_run} | "
            f"{row.model} | "
            f"{row.train_market_count} | "
            f"{row.holdout_candidate_count} | "
            f"{row.holdout_market_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} | "
            f"{row.beats_brownian} | "
            f"{row.beats_market} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(
        [
            "",
            "## Run Inputs",
            "",
            "| run | rows | markets | candidate_path | label_path |",
            "|---|---:|---:|---|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"`{row.candidate_path}` | "
            f"`{row.label_path}` |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
