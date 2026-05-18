from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

import numpy as np

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay, load_replay_inputs_from_jsonl
from .spot_context_merge import SpotTickRow, load_spot_ticks
from .spot_rv_anchor_switch_loro import _market_ev_metrics


@dataclass(frozen=True)
class EmpiricalSecondParticleSpec:
    name: str
    lookback_seconds: int
    particle_count: int
    max_draws_per_particle: int
    recency_half_life_seconds: float
    return_cap_bps: float
    mean_weight: float
    brownian_blend_weight: float
    min_return_count: int


@dataclass(frozen=True)
class EmpiricalSecondParticleRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    spot_tick_path: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class EmpiricalSecondParticleRunRow:
    run: str
    spec: str
    candidate_count: int
    market_count: int
    selected_count: int
    fallback_count: int
    avg_return_count: float
    avg_spot_age_ms: float
    avg_empirical_ann_vol: float
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    market_ev_rank_correlation_sign: float
    top_market_ev_bucket_avg_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class EmpiricalSecondParticleSummaryRow:
    spec: str
    run_count: int
    total_counterfactual_pnl_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    positive_market_ev_rank_count: int
    positive_market_top_bucket_count: int
    strict_gate_count: int
    strict_all_runs: bool
    fallback_count: int
    avg_return_count: float
    avg_spot_age_ms: float
    avg_empirical_ann_vol: float


@dataclass(frozen=True)
class EmpiricalSecondParticleDiagnosticReport:
    run_inputs: tuple[EmpiricalSecondParticleRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    specs: tuple[EmpiricalSecondParticleSpec, ...]
    run_rows: tuple[EmpiricalSecondParticleRunRow, ...]
    summary_rows: tuple[EmpiricalSecondParticleSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


@dataclass(frozen=True)
class EmpiricalProbabilityDiagnostics:
    probability_yes: float
    used_fallback: bool
    return_count: int
    spot_age_ms: float
    empirical_ann_vol: float


@dataclass(frozen=True)
class SecondReturnCache:
    available_times: tuple[datetime, ...]
    log_returns: np.ndarray


SECONDS_PER_YEAR = 365.0 * 24.0 * 60.0 * 60.0


def build_empirical_next_second_particle_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    max_spot_age_ms: float = 5_000.0,
) -> EmpiricalSecondParticleDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[EmpiricalSecondParticleRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root)
        if loaded is None:
            skipped.append(str(root))
            continue
        loaded_runs.append(loaded)

    specs = _specs()
    run_rows: list[EmpiricalSecondParticleRunRow] = []
    for meta, rows, ticks in loaded_runs:
        times = [tick.available_ts_utc for tick in ticks]
        prices = [float(tick.price) for tick in ticks]
        for spec in specs:
            materialized, diagnostics = materialize_empirical_second_particle_rows(
                rows,
                times,
                prices,
                spec,
                run_name=meta.name,
                max_spot_age_ms=max_spot_age_ms,
            )
            replay = evaluate_replay(materialized, cfg)
            market_ev_rank, top_market_bucket = _market_ev_metrics(replay)
            run_rows.append(
                EmpiricalSecondParticleRunRow(
                    run=meta.name,
                    spec=spec.name,
                    candidate_count=replay.candidate_count,
                    market_count=meta.market_count,
                    selected_count=replay.selected_count,
                    fallback_count=int(diagnostics["fallback_count"]),
                    avg_return_count=float(diagnostics["avg_return_count"]),
                    avg_spot_age_ms=float(diagnostics["avg_spot_age_ms"]),
                    avg_empirical_ann_vol=float(diagnostics["avg_empirical_ann_vol"]),
                    total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                    brier=replay.particle.brier,
                    log_loss=replay.particle.log_loss,
                    beats_brownian=replay.particle_beats_brownian,
                    beats_market=replay.particle_beats_market,
                    beats_current_calibrated=replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                    market_ev_rank_correlation_sign=market_ev_rank,
                    top_market_ev_bucket_avg_pnl_cents=top_market_bucket,
                    strict_gate_pass=_strict_gate(replay),
                )
            )
    summaries = tuple(_summarize(run_rows))
    candidate_ready = any(row.strict_all_runs for row in summaries)
    conclusion = (
        "At least one empirical next-second particle spec cleared every eligible locked run. "
        "Because this is same-evidence research, it only nominates a fresh predeclared shadow run."
        if candidate_ready
        else "No empirical next-second particle spec cleared strict eligible locked-run gates."
    )
    return EmpiricalSecondParticleDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        specs=specs,
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def materialize_empirical_second_particle_rows(
    rows: Sequence[ReplayInput],
    times: Sequence[datetime],
    prices: Sequence[float],
    spec: EmpiricalSecondParticleSpec,
    *,
    run_name: str = "",
    max_spot_age_ms: float = 5_000.0,
) -> tuple[tuple[ReplayInput, ...], dict[str, float | int]]:
    if not rows:
        raise ValueError("at least one replay row is required")
    return_cache = build_second_return_cache(times, prices)
    materialized: list[ReplayInput] = []
    fallback_count = 0
    return_counts: list[float] = []
    spot_ages: list[float] = []
    empirical_vols: list[float] = []
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        result = empirical_second_particle_probability(
            row,
            times,
            prices,
            spec,
            run_name=run_name,
            max_spot_age_ms=max_spot_age_ms,
            return_cache=return_cache,
        )
        fallback_count += int(result.used_fallback)
        return_counts.append(float(result.return_count))
        spot_ages.append(float(result.spot_age_ms))
        empirical_vols.append(float(result.empirical_ann_vol))
        p_yes = spec.brownian_blend_weight * row.brownian_p_yes + (
            1.0 - spec.brownian_blend_weight
        ) * result.probability_yes
        materialized.append(replace(row, particle_p_yes=_clamp01(p_yes)))
    return (
        tuple(materialized),
        {
            "fallback_count": fallback_count,
            "avg_return_count": _mean(return_counts),
            "avg_spot_age_ms": _mean(spot_ages),
            "avg_empirical_ann_vol": _mean(empirical_vols),
        },
    )


def empirical_second_particle_probability(
    row: ReplayInput,
    times: Sequence[datetime],
    prices: Sequence[float],
    spec: EmpiricalSecondParticleSpec,
    *,
    run_name: str = "",
    max_spot_age_ms: float = 5_000.0,
    return_cache: SecondReturnCache | None = None,
) -> EmpiricalProbabilityDiagnostics:
    _validate_spec(spec)
    decision_ts = row.snapshot.decision_ts_utc
    horizon = max(0, int(round((row.label.settlement_ts_utc - decision_ts).total_seconds())))
    if horizon <= 0:
        return EmpiricalProbabilityDiagnostics(
            probability_yes=1.0 if row.snapshot.spot > row.snapshot.strike else 0.0,
            used_fallback=False,
            return_count=0,
            spot_age_ms=0.0,
            empirical_ann_vol=0.0,
        )
    end = bisect.bisect_right(times, decision_ts)
    if end <= 0:
        return _fallback(row, 0, 0.0, spec)
    latest_age_ms = 1000.0 * (decision_ts - times[end - 1]).total_seconds()
    if latest_age_ms > max_spot_age_ms:
        return _fallback(row, 0, latest_age_ms, spec)
    cache = return_cache or build_second_return_cache(times, prices)
    return_end = bisect.bisect_right(cache.available_times, decision_ts)
    return_start = bisect.bisect_left(
        cache.available_times,
        decision_ts - timedelta(seconds=spec.lookback_seconds),
        0,
        return_end,
    )
    returns_array = cache.log_returns[return_start:return_end]
    if len(returns_array) < spec.min_return_count:
        return _fallback(row, len(returns_array), latest_age_ms, spec)

    returns_array = np.asarray(returns_array, dtype=float)
    if spec.return_cap_bps > 0.0:
        cap = spec.return_cap_bps / 10_000.0
        returns_array = np.clip(returns_array, -cap, cap)
    weights = _recency_weights(len(returns_array), spec.recency_half_life_seconds)
    raw_mean = float(np.average(returns_array, weights=weights))
    centered = returns_array - raw_mean
    target_mean = raw_mean * spec.mean_weight
    empirical_second_var = float(np.average(centered * centered, weights=weights))
    empirical_ann_vol = math.sqrt(max(0.0, empirical_second_var) * SECONDS_PER_YEAR)
    draw_count = max(1, min(horizon, spec.max_draws_per_particle))
    rng = np.random.default_rng(_seed_for(row, spec, run_name))
    indices = rng.choice(
        len(returns_array),
        size=(spec.particle_count, draw_count),
        replace=True,
        p=weights,
    )
    sampled_centered = centered[indices]
    compressed_noise = sampled_centered.sum(axis=1) * math.sqrt(horizon / draw_count)
    terminal_log_returns = horizon * target_mean + compressed_noise
    start_spot = float(prices[end - 1])
    log_threshold = math.log(row.snapshot.strike / start_spot)
    probability_yes = float(np.mean(terminal_log_returns > log_threshold))
    return EmpiricalProbabilityDiagnostics(
        probability_yes=_clamp01(probability_yes),
        used_fallback=False,
        return_count=int(len(returns_array)),
        spot_age_ms=latest_age_ms,
        empirical_ann_vol=empirical_ann_vol,
    )


def build_second_return_cache(times: Sequence[datetime], prices: Sequence[float]) -> SecondReturnCache:
    """Build conservative one-second return samples from public spot ticks.

    A return for bucket [t, t+1s) is marked available at t+1s. This intentionally
    ignores partial current-second information at a decision timestamp, avoiding
    accidental leakage from later ticks in the same wall-clock second.
    """
    if len(times) < 2 or len(prices) < 2:
        return SecondReturnCache(available_times=(), log_returns=np.asarray([], dtype=float))
    closes_by_second: dict[datetime, float] = {}
    for ts, price in zip(times, prices):
        if price <= 0.0:
            continue
        second = ts.astimezone(timezone.utc).replace(microsecond=0)
        closes_by_second[second] = float(price)
    if len(closes_by_second) < 2:
        return SecondReturnCache(available_times=(), log_returns=np.asarray([], dtype=float))
    seconds = sorted(closes_by_second)
    cursor = seconds[0]
    end = seconds[-1]
    last_price = closes_by_second[cursor]
    previous_price = last_price
    available_times: list[datetime] = []
    log_returns: list[float] = []
    while cursor < end:
        cursor = cursor + timedelta(seconds=1)
        if cursor in closes_by_second:
            last_price = closes_by_second[cursor]
        if previous_price > 0.0 and last_price > 0.0:
            available_times.append(cursor + timedelta(seconds=1))
            log_returns.append(math.log(last_price / previous_price))
        previous_price = last_price
    return SecondReturnCache(available_times=tuple(available_times), log_returns=np.asarray(log_returns, dtype=float))


def write_empirical_next_second_particle_diagnostic(
    report: EmpiricalSecondParticleDiagnosticReport,
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
        description="Evaluate empirical next-second particle probabilities on eligible locked shadow roots."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="empirical_next_second_particle_diagnostic")
    parser.add_argument("--max-spot-age-ms", default=5_000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_empirical_next_second_particle_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_empirical_next_second_particle_diagnostic(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={len(report.specs)}")
    print(f"run_row_count={len(report.run_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_eligible_run(
    root: Path,
) -> tuple[EmpiricalSecondParticleRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]] | None:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    spot_path = root / "independent_spot_ticks.ndjson"
    if not candidate_path.exists() or not spot_path.exists():
        return None
    label_path = _find_label_path(root)
    rows = tuple(
        sorted(
            load_replay_inputs_from_jsonl(candidate_path, label_path),
            key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker),
        )
    )
    ticks = tuple(load_spot_ticks(spot_path))
    if not rows or not ticks:
        return None
    meta = EmpiricalSecondParticleRunInput(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        spot_tick_path=str(spot_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
        spot_tick_count=len(ticks),
    )
    return meta, rows, ticks


def _specs() -> tuple[EmpiricalSecondParticleSpec, ...]:
    return (
        EmpiricalSecondParticleSpec("emp1s_233_center_blend50_p96_d48", 233, 96, 48, 89.0, 5.0, 0.0, 0.50, 20),
        EmpiricalSecondParticleSpec("emp1s_610_center_blend50_p96_d48", 610, 96, 48, 233.0, 5.0, 0.0, 0.50, 30),
        EmpiricalSecondParticleSpec("emp1s_610_mean25_blend25_p128_d64", 610, 128, 64, 233.0, 5.0, 0.25, 0.25, 30),
        EmpiricalSecondParticleSpec("emp1s_987_mean25_blend25_p128_d64", 987, 128, 64, 377.0, 7.5, 0.25, 0.25, 40),
    )


def _recent_second_returns(times: Sequence[datetime], prices: Sequence[float]) -> list[float]:
    if len(times) < 2 or len(prices) < 2:
        return []
    closes_by_second: dict[datetime, float] = {}
    for ts, price in zip(times, prices):
        if price <= 0.0:
            continue
        second = ts.astimezone(timezone.utc).replace(microsecond=0)
        closes_by_second[second] = float(price)
    if len(closes_by_second) < 2:
        return []
    seconds = sorted(closes_by_second)
    cursor = seconds[0]
    end = seconds[-1]
    last_price = closes_by_second[cursor]
    previous_price = last_price
    returns: list[float] = []
    while cursor < end:
        cursor = cursor + timedelta(seconds=1)
        if cursor in closes_by_second:
            last_price = closes_by_second[cursor]
        if previous_price > 0.0 and last_price > 0.0:
            returns.append(math.log(last_price / previous_price))
        previous_price = last_price
    return returns


def _recency_weights(count: int, half_life_seconds: float) -> np.ndarray:
    if count <= 0:
        raise ValueError("count must be positive")
    if half_life_seconds <= 0.0:
        return np.full(count, 1.0 / count, dtype=float)
    ages = np.arange(count - 1, -1, -1, dtype=float)
    weights = np.exp(-math.log(2.0) * ages / float(half_life_seconds))
    total = float(weights.sum())
    if total <= 0.0:
        return np.full(count, 1.0 / count, dtype=float)
    return weights / total


def _fallback(
    row: ReplayInput,
    return_count: int,
    spot_age_ms: float,
    spec: EmpiricalSecondParticleSpec,
) -> EmpiricalProbabilityDiagnostics:
    return EmpiricalProbabilityDiagnostics(
        probability_yes=_clamp01(row.brownian_p_yes),
        used_fallback=True,
        return_count=return_count,
        spot_age_ms=spot_age_ms,
        empirical_ann_vol=0.0,
    )


def _validate_spec(spec: EmpiricalSecondParticleSpec) -> None:
    if spec.lookback_seconds <= 0:
        raise ValueError("lookback_seconds must be positive")
    if spec.particle_count <= 0:
        raise ValueError("particle_count must be positive")
    if spec.max_draws_per_particle <= 0:
        raise ValueError("max_draws_per_particle must be positive")
    if spec.min_return_count <= 0:
        raise ValueError("min_return_count must be positive")
    if not 0.0 <= spec.mean_weight <= 1.0:
        raise ValueError("mean_weight must be in [0, 1]")
    if not 0.0 <= spec.brownian_blend_weight <= 1.0:
        raise ValueError("brownian_blend_weight must be in [0, 1]")


def _strict_gate(report: ReplayReport) -> bool:
    return (
        report.total_counterfactual_pnl_cents > 0.0
        and report.particle_beats_brownian
        and report.particle_beats_market
        and report.particle_beats_current_calibrated
        and report.ev_rank_correlation_sign > 0.0
        and report.top_ev_bucket_pnl_cents > 0.0
    )


def _summarize(rows: Sequence[EmpiricalSecondParticleRunRow]) -> list[EmpiricalSecondParticleSummaryRow]:
    grouped: dict[str, list[EmpiricalSecondParticleRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[EmpiricalSecondParticleSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            EmpiricalSecondParticleSummaryRow(
                spec=spec,
                run_count=len(spec_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in spec_rows),
                mean_brier=_mean(row.brier for row in spec_rows),
                mean_log_loss=_mean(row.log_loss for row in spec_rows),
                positive_pnl_count=sum(1 for row in spec_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in spec_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in spec_rows if row.beats_market),
                beats_current_count=sum(1 for row in spec_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in spec_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in spec_rows if row.top_ev_bucket_pnl_cents > 0.0),
                positive_market_ev_rank_count=sum(
                    1 for row in spec_rows if row.market_ev_rank_correlation_sign > 0.0
                ),
                positive_market_top_bucket_count=sum(
                    1 for row in spec_rows if row.top_market_ev_bucket_avg_pnl_cents > 0.0
                ),
                strict_gate_count=strict_count,
                strict_all_runs=(strict_count == len(spec_rows) and bool(spec_rows)),
                fallback_count=sum(row.fallback_count for row in spec_rows),
                avg_return_count=_mean(row.avg_return_count for row in spec_rows),
                avg_spot_age_ms=_mean(row.avg_spot_age_ms for row in spec_rows),
                avg_empirical_ann_vol=_mean(row.avg_empirical_ann_vol for row in spec_rows),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_runs,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _markdown(report: EmpiricalSecondParticleDiagnosticReport) -> str:
    lines = [
        "# Empirical Next-Second Particle Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- spec_count: {len(report.specs)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | fallback | avg_returns | avg_spot_age_ms | avg_ann_vol | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.run_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.run_count} | "
            f"{row.beats_brownian_count}/{row.run_count} | "
            f"{row.beats_market_count}/{row.run_count} | "
            f"{row.beats_current_count}/{row.run_count} | "
            f"{row.positive_ev_rank_count}/{row.run_count} | "
            f"{row.positive_top_bucket_count}/{row.run_count} | "
            f"{row.positive_market_ev_rank_count}/{row.run_count} | "
            f"{row.positive_market_top_bucket_count}/{row.run_count} | "
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.fallback_count} | "
            f"{row.avg_return_count:.2f} | "
            f"{row.avg_spot_age_ms:.2f} | "
            f"{row.avg_empirical_ann_vol:.6f} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | spec | candidates | markets | selected | fallback | avg_returns | avg_spot_age_ms | avg_ann_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.spec} | "
            f"{row.candidate_count} | "
            f"{row.market_count} | "
            f"{row.selected_count} | "
            f"{row.fallback_count} | "
            f"{row.avg_return_count:.2f} | "
            f"{row.avg_spot_age_ms:.2f} | "
            f"{row.avg_empirical_ann_vol:.6f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.market_ev_rank_correlation_sign:.6f} | "
            f"{row.top_market_ev_bucket_avg_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks |", "|---|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(f"| {row.name} | {row.row_count} | {row.market_count} | {row.spot_tick_count} |")
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{root}`" for root in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


def _seed_for(row: ReplayInput, spec: EmpiricalSecondParticleSpec, run_name: str) -> int:
    raw = "|".join(
        [
            run_name,
            spec.name,
            row.snapshot.market_ticker,
            row.snapshot.decision_ts_utc.isoformat(),
        ]
    )
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
