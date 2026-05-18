from __future__ import annotations

import argparse
import bisect
import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
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
from .spot_context_merge import SpotTickRow, load_spot_ticks


DEFAULT_WINDOWS_SECONDS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)


@dataclass(frozen=True)
class SpotMicroRunInput:
    name: str
    root: str
    row_count: int
    market_count: int
    spot_tick_path: str
    spot_tick_count: int
    rows_with_prior_spot: int
    rows_with_recent_spot: int
    max_spot_age_ms: float


@dataclass(frozen=True)
class SpotMicroHoldoutRow:
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
class SpotMicroSummaryRow:
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
class SpotMicroLOROReport:
    run_inputs: tuple[SpotMicroRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    windows_seconds: tuple[int, ...]
    holdout_rows: tuple[SpotMicroHoldoutRow, ...]
    summary_rows: tuple[SpotMicroSummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_spot_micro_loro_report(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    learning_rate: float = 0.05,
    l2: float = 0.50,
    epochs: int = 1200,
    windows_seconds: Sequence[int] = DEFAULT_WINDOWS_SECONDS,
    max_spot_age_ms: float = 5_000.0,
) -> SpotMicroLOROReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[str, SpotMicroRunInput, list[ReplayInput], dict[int, tuple[float, ...]]]] = []
    skipped: list[str] = []
    for root in run_roots:
        tick_path = root / "independent_spot_ticks.ndjson"
        if not tick_path.exists():
            skipped.append(str(root))
            continue
        run_name, base_meta, rows = _load_run(root)
        ticks = load_spot_ticks(tick_path)
        feature_map, prior_count, recent_count = _build_feature_map(
            rows,
            ticks,
            tuple(int(value) for value in windows_seconds),
            max_spot_age_ms=max_spot_age_ms,
        )
        loaded_runs.append(
            (
                run_name,
                SpotMicroRunInput(
                    name=base_meta.name,
                    root=base_meta.root,
                    row_count=base_meta.row_count,
                    market_count=base_meta.market_count,
                    spot_tick_path=str(tick_path),
                    spot_tick_count=len(ticks),
                    rows_with_prior_spot=prior_count,
                    rows_with_recent_spot=recent_count,
                    max_spot_age_ms=float(max_spot_age_ms),
                ),
                rows,
                feature_map,
            )
        )
    if len(loaded_runs) < 2:
        return SpotMicroLOROReport(
            run_inputs=tuple(meta for _, meta, _, _ in loaded_runs),
            skipped_run_roots=tuple(skipped),
            windows_seconds=tuple(int(value) for value in windows_seconds),
            holdout_rows=(),
            summary_rows=(),
            promotion_safe=False,
            conclusion="Fewer than two run roots had independent spot ticks; no LORO spot-micro diagnostic was possible.",
        )
    combined_features = {
        row_id: values
        for _, _, _, feature_map in loaded_runs
        for row_id, values in feature_map.items()
    }
    specs = _spot_specs(tuple(int(value) for value in windows_seconds), combined_features)
    holdout_rows: list[SpotMicroHoldoutRow] = []
    for holdout_name, holdout_meta, holdout_raw, _ in loaded_runs:
        train = [
            row
            for run_name, _, rows, _ in loaded_runs
            if run_name != holdout_name
            for row in rows
        ]
        train_market_count = len({row.snapshot.market_ticker for row in train})
        for spec in specs:
            model = _train_model(
                spec,
                train,
                learning_rate=learning_rate,
                l2=l2,
                epochs=epochs,
            )
            variant_rows = [
                replace(row, particle_p_yes=_clamp01(_predict_model(model, row)))
                for row in holdout_raw
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
                SpotMicroHoldoutRow(
                    holdout_run=holdout_name,
                    model=spec.name,
                    train_run_count=len(loaded_runs) - 1,
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
    promotion_safe = len(loaded_runs) >= 3 and any(row.strict_all_holdouts for row in summaries)
    if promotion_safe:
        conclusion = (
            "A spot-micro model passed every strict eligible holdout, but still needs a fresh "
            "predeclared locked capture because eligible tick-root count is small."
        )
    else:
        conclusion = (
            "No independent-spot microstructure model passes strict eligible holdout gates; "
            "eligible tick-root count is too small for promotion even if a row looks good."
        )
    return SpotMicroLOROReport(
        run_inputs=tuple(meta for _, meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        windows_seconds=tuple(int(value) for value in windows_seconds),
        holdout_rows=tuple(holdout_rows),
        summary_rows=summaries,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_spot_micro_loro_report(
    report: SpotMicroLOROReport,
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
        description="Train independent-spot next-second microfeature models on all-but-one eligible locked runs."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_micro_loro")
    parser.add_argument("--learning-rate", default=0.05, type=float)
    parser.add_argument("--l2", default=0.50, type=float)
    parser.add_argument("--epochs", default=1200, type=int)
    parser.add_argument("--max-spot-age-ms", default=5000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_micro_loro_report(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        learning_rate=args.learning_rate,
        l2=args.l2,
        epochs=args.epochs,
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_spot_micro_loro_report(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _build_feature_map(
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    windows_seconds: tuple[int, ...],
    *,
    max_spot_age_ms: float,
) -> tuple[dict[int, tuple[float, ...]], int, int]:
    times = [tick.available_ts_utc for tick in ticks]
    prices = [float(tick.price) for tick in ticks]
    feature_map: dict[int, tuple[float, ...]] = {}
    prior_count = 0
    recent_count = 0
    for row in rows:
        values, has_prior, is_recent = _features_for_row(row, times, prices, windows_seconds, max_spot_age_ms)
        feature_map[id(row)] = values
        prior_count += int(has_prior)
        recent_count += int(is_recent)
    return feature_map, prior_count, recent_count


def _features_for_row(
    row: ReplayInput,
    times: Sequence[datetime],
    prices: Sequence[float],
    windows_seconds: tuple[int, ...],
    max_spot_age_ms: float,
) -> tuple[tuple[float, ...], bool, bool]:
    decision_ts = row.snapshot.decision_ts_utc
    end = bisect.bisect_right(times, decision_ts)
    if end <= 0:
        return _zero_features(row, windows_seconds, age_seconds=10.0), False, False
    last_price = prices[end - 1]
    age_ms = 1000.0 * (decision_ts - times[end - 1]).total_seconds()
    returns: list[float] = []
    vols: list[float] = []
    counts: list[float] = []
    chops: list[float] = []
    for window in windows_seconds:
        start_ts = decision_ts - timedelta(seconds=window)
        start = bisect.bisect_left(times, start_ts, 0, end)
        window_prices = prices[start:end]
        if len(window_prices) < 2 or last_price <= 0.0 or window_prices[0] <= 0.0:
            returns.append(0.0)
            vols.append(0.0)
            counts.append(0.0)
            chops.append(0.0)
            continue
        log_returns = [
            math.log(window_prices[idx] / window_prices[idx - 1])
            for idx in range(1, len(window_prices))
            if window_prices[idx] > 0.0 and window_prices[idx - 1] > 0.0
        ]
        net_bps = 10_000.0 * math.log(last_price / window_prices[0])
        vol_bps = 10_000.0 * math.sqrt(sum(value * value for value in log_returns))
        path_bps = 10_000.0 * sum(abs(value) for value in log_returns)
        chop = path_bps / (abs(net_bps) + 1.0)
        returns.append(net_bps)
        vols.append(vol_bps)
        counts.append(math.log1p(len(window_prices)))
        chops.append(min(100.0, chop))
    age_seconds = min(10.0, max(0.0, age_ms / 1000.0))
    spot_gap_bps = 0.0
    if row.snapshot.spot > 0.0 and last_price > 0.0:
        spot_gap_bps = 10_000.0 * math.log(last_price / row.snapshot.spot)
    state = (
        _moneyness_bps(row),
        abs(_moneyness_bps(row)),
        _time_frac(row),
        (row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0) / 100.0,
        row.snapshot.fill_prob,
        age_seconds,
        spot_gap_bps,
    )
    return (*state, *returns, *vols, *counts, *chops), True, age_ms <= max_spot_age_ms


def _zero_features(row: ReplayInput, windows_seconds: tuple[int, ...], *, age_seconds: float) -> tuple[float, ...]:
    state = (
        _moneyness_bps(row),
        abs(_moneyness_bps(row)),
        _time_frac(row),
        (row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0) / 100.0,
        row.snapshot.fill_prob,
        age_seconds,
        0.0,
    )
    zero_count = len(windows_seconds) * 4
    return (*state, *(0.0 for _ in range(zero_count)))


def _spot_specs(
    windows_seconds: tuple[int, ...],
    feature_map: dict[int, tuple[float, ...]],
) -> tuple[MetaModelSpec, ...]:
    state_names = (
        "moneyness_bps",
        "abs_moneyness_bps",
        "time_frac",
        "spread_norm",
        "fill_prob",
        "spot_age_seconds",
        "spot_gap_bps",
    )
    return_names = tuple(f"ret_{window}s_bps" for window in windows_seconds)
    vol_names = tuple(f"vol_{window}s_bps" for window in windows_seconds)
    count_names = tuple(f"tick_count_{window}s_log" for window in windows_seconds)
    chop_names = tuple(f"chop_{window}s" for window in windows_seconds)
    all_names = (*state_names, *return_names, *vol_names, *count_names, *chop_names)
    return_start = len(state_names)
    vol_start = return_start + len(windows_seconds)
    count_start = vol_start + len(windows_seconds)
    chop_start = count_start + len(windows_seconds)
    short_return_indices = tuple(return_start + idx for idx, window in enumerate(windows_seconds) if window <= 13)
    all_micro_indices = tuple(range(len(all_names)))
    compact_indices = (
        0,
        2,
        3,
        4,
        5,
        *short_return_indices,
        *(vol_start + idx for idx, window in enumerate(windows_seconds) if window in (5, 13, 34, 89)),
        *(chop_start + idx for idx, window in enumerate(windows_seconds) if window in (13, 34, 89)),
    )

    def values_for(row: ReplayInput) -> tuple[float, ...]:
        return feature_map[id(row)]

    def subset(row: ReplayInput, indices: Sequence[int]) -> tuple[float, ...]:
        values = values_for(row)
        return tuple(values[idx] for idx in indices)

    return (
        MetaModelSpec(
            "spot_phi_returns",
            tuple(all_names[idx] for idx in short_return_indices),
            lambda row: subset(row, short_return_indices),
        ),
        MetaModelSpec(
            "spot_micro_compact",
            tuple(all_names[idx] for idx in compact_indices),
            lambda row: subset(row, compact_indices),
        ),
        MetaModelSpec(
            "spot_micro_all",
            all_names,
            lambda row: subset(row, all_micro_indices),
        ),
        MetaModelSpec(
            "spot_micro_plus_current",
            ("logit_current", "market_minus_current", "particle_minus_current", *tuple(all_names[idx] for idx in compact_indices)),
            lambda row: (
                _logit(row.current_calibrated_p_yes),
                row.market_p_yes - row.current_calibrated_p_yes,
                row.particle_p_yes - row.current_calibrated_p_yes,
                *subset(row, compact_indices),
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


def _summarize(rows: Sequence[SpotMicroHoldoutRow]) -> tuple[SpotMicroSummaryRow, ...]:
    grouped: dict[str, list[SpotMicroHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.model, []).append(row)
    summaries: list[SpotMicroSummaryRow] = []
    for model in sorted(grouped):
        model_rows = grouped[model]
        strict_count = sum(1 for row in model_rows if row.strict_gate_pass)
        summaries.append(
            SpotMicroSummaryRow(
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
    return tuple(
        sorted(
            summaries,
            key=lambda row: (
                row.strict_all_holdouts,
                row.strict_gate_count,
                row.beats_current_count,
                row.total_counterfactual_pnl_cents,
            ),
            reverse=True,
        )
    )


def _mean(values) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _markdown(report: SpotMicroLOROReport) -> str:
    lines = [
        "# Spot Micro LORO Report",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- windows_seconds: {', '.join(str(value) for value in report.windows_seconds)}",
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
            "| run | rows | markets | spot_ticks | rows_prior_spot | rows_recent_spot | spot_tick_path |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"{row.spot_tick_count} | "
            f"{row.rows_with_prior_spot} | "
            f"{row.rows_with_recent_spot} | "
            f"`{row.spot_tick_path}` |"
        )
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{path}`" for path in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
