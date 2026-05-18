from __future__ import annotations

import argparse
import bisect
import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl
from .spot_context_merge import SpotTickRow, load_spot_ticks
from .terminal_projection import brownian_terminal_probability


SECONDS_PER_YEAR = 365.0 * 24.0 * 60.0 * 60.0


@dataclass(frozen=True)
class SpotRealizedVolSpec:
    name: str
    window_seconds: int
    floor_annualized_vol: float
    cap_annualized_vol: float
    fallback_annualized_vol: float = 0.65
    fixed_blend_weight: float = 0.0


@dataclass(frozen=True)
class SpotRealizedVolRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    spot_tick_path: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class SpotRealizedVolRunRow:
    run: str
    spec: str
    candidate_count: int
    market_count: int
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
    fallback_row_count: int
    mean_annualized_vol: float


@dataclass(frozen=True)
class SpotRealizedVolSummaryRow:
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
    strict_gate_count: int
    strict_all_runs: bool
    fallback_row_count: int
    mean_annualized_vol: float


@dataclass(frozen=True)
class SpotRealizedVolTerminalDiagnosticReport:
    run_inputs: tuple[SpotRealizedVolRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    spec_count: int
    run_rows: tuple[SpotRealizedVolRunRow, ...]
    summary_rows: tuple[SpotRealizedVolSummaryRow, ...]
    best_by_brier: SpotRealizedVolSummaryRow | None
    best_by_pnl: SpotRealizedVolSummaryRow | None
    promotion_safe: bool
    conclusion: str


def build_spot_realized_vol_terminal_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
) -> SpotRealizedVolTerminalDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[SpotRealizedVolRunInput, list[ReplayInput], list[SpotTickRow]]] = []
    skipped: list[str] = []
    for root in run_roots:
        spot_path = root / "independent_spot_ticks.ndjson"
        candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        if not spot_path.exists() or not candidate_path.exists():
            skipped.append(str(root))
            continue
        label_path = _find_label_path(root)
        rows = load_replay_inputs_from_jsonl(candidate_path, label_path)
        ticks = load_spot_ticks(spot_path)
        loaded_runs.append(
            (
                SpotRealizedVolRunInput(
                    name=root.name,
                    root=str(root),
                    candidate_path=str(candidate_path),
                    label_path=str(label_path),
                    spot_tick_path=str(spot_path),
                    row_count=len(rows),
                    market_count=len({row.snapshot.market_ticker for row in rows}),
                    spot_tick_count=len(ticks),
                ),
                rows,
                ticks,
            )
        )
    specs = _spec_registry()
    run_rows: list[SpotRealizedVolRunRow] = []
    for run_meta, rows, ticks in loaded_runs:
        times = [tick.available_ts_utc for tick in ticks]
        prices = [float(tick.price) for tick in ticks]
        for spec in specs:
            variant_rows: list[ReplayInput] = []
            vols: list[float] = []
            fallback_count = 0
            for row in rows:
                ann_vol, used_fallback = realized_annualized_vol_at_decision(
                    row.snapshot.decision_ts_utc,
                    times,
                    prices,
                    spec.window_seconds,
                    fallback_annualized_vol=spec.fallback_annualized_vol,
                    floor_annualized_vol=spec.floor_annualized_vol,
                    cap_annualized_vol=spec.cap_annualized_vol,
                )
                vols.append(ann_vol)
                fallback_count += int(used_fallback)
                rv_prob = brownian_terminal_probability(
                    row.snapshot.spot,
                    row.snapshot.strike,
                    max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds()),
                    ann_vol,
                )
                p_yes = (
                    spec.fixed_blend_weight * row.brownian_p_yes
                    + (1.0 - spec.fixed_blend_weight) * rv_prob
                )
                variant_rows.append(replace(row, particle_p_yes=_clamp01(p_yes)))
            replay = evaluate_replay(variant_rows, cfg)
            strict = (
                replay.total_counterfactual_pnl_cents > 0.0
                and replay.particle_beats_brownian
                and replay.particle_beats_market
                and replay.particle_beats_current_calibrated
                and replay.ev_rank_correlation_sign > 0.0
                and replay.top_ev_bucket_pnl_cents > 0.0
            )
            run_rows.append(
                SpotRealizedVolRunRow(
                    run=run_meta.name,
                    spec=spec.name,
                    candidate_count=replay.candidate_count,
                    market_count=run_meta.market_count,
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
                    fallback_row_count=fallback_count,
                    mean_annualized_vol=_mean(vols),
                )
            )
    summaries = tuple(_summarize(run_rows))
    best_by_brier = min(summaries, key=lambda row: (row.mean_brier, row.mean_log_loss), default=None)
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents, default=None)
    strict_candidates = [row for row in summaries if row.strict_all_runs]
    conclusion = (
        "At least one timestamp-available realized-vol terminal variant cleared every eligible run, "
        "but this diagnostic was not predeclared before capture and remains research-only."
        if strict_candidates
        else "No timestamp-available realized-vol terminal variant clears strict eligible-run gates."
    )
    return SpotRealizedVolTerminalDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        spec_count=len(specs),
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=False,
        conclusion=conclusion,
    )


def realized_annualized_vol_at_decision(
    decision_ts_utc: datetime,
    times: Sequence[datetime],
    prices: Sequence[float],
    window_seconds: int,
    *,
    fallback_annualized_vol: float,
    floor_annualized_vol: float,
    cap_annualized_vol: float,
) -> tuple[float, bool]:
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    end = bisect.bisect_right(times, decision_ts_utc)
    if end <= 1:
        return _clamp(fallback_annualized_vol, floor_annualized_vol, cap_annualized_vol), True
    start_ts = decision_ts_utc - timedelta(seconds=window_seconds)
    start = bisect.bisect_left(times, start_ts, 0, end)
    window_times = times[start:end]
    window_prices = prices[start:end]
    if len(window_prices) < 3:
        return _clamp(fallback_annualized_vol, floor_annualized_vol, cap_annualized_vol), True
    log_returns = [
        math.log(window_prices[idx] / window_prices[idx - 1])
        for idx in range(1, len(window_prices))
        if window_prices[idx] > 0.0 and window_prices[idx - 1] > 0.0
    ]
    elapsed_seconds = max(1e-9, (window_times[-1] - window_times[0]).total_seconds())
    if len(log_returns) < 2 or elapsed_seconds <= 0.0:
        return _clamp(fallback_annualized_vol, floor_annualized_vol, cap_annualized_vol), True
    rv = math.sqrt(sum(value * value for value in log_returns) * SECONDS_PER_YEAR / elapsed_seconds)
    return _clamp(rv, floor_annualized_vol, cap_annualized_vol), False


def write_spot_realized_vol_terminal_diagnostic(
    report: SpotRealizedVolTerminalDiagnosticReport,
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
        description="Evaluate timestamp-available independent-spot realized-vol Brownian terminal variants."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_realized_vol_terminal_diagnostic")
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_realized_vol_terminal_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_spot_realized_vol_terminal_diagnostic(
        report,
        args.output_dir,
        args.stem,
    )
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={report.spec_count}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    if report.best_by_brier:
        print(f"best_by_brier={report.best_by_brier.spec}")
        print(f"best_by_brier_brier={report.best_by_brier.mean_brier:.6f}")
    if report.best_by_pnl:
        print(f"best_by_pnl={report.best_by_pnl.spec}")
        print(f"best_by_pnl_total_counterfactual_pnl_cents={report.best_by_pnl.total_counterfactual_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _spec_registry() -> tuple[SpotRealizedVolSpec, ...]:
    return (
        SpotRealizedVolSpec("rv34_floor20_cap150", 34, 0.20, 1.50),
        SpotRealizedVolSpec("rv89_floor20_cap150", 89, 0.20, 1.50),
        SpotRealizedVolSpec("rv233_floor20_cap150", 233, 0.20, 1.50),
        SpotRealizedVolSpec("rv610_floor20_cap200", 610, 0.20, 2.00),
        SpotRealizedVolSpec("rv89_blend50_fixed65", 89, 0.20, 1.50, fixed_blend_weight=0.50),
        SpotRealizedVolSpec("rv233_blend50_fixed65", 233, 0.20, 1.50, fixed_blend_weight=0.50),
        SpotRealizedVolSpec("rv610_blend50_fixed65", 610, 0.20, 2.00, fixed_blend_weight=0.50),
    )


def _summarize(rows: Sequence[SpotRealizedVolRunRow]) -> list[SpotRealizedVolSummaryRow]:
    grouped: dict[str, list[SpotRealizedVolRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[SpotRealizedVolSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            SpotRealizedVolSummaryRow(
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
                strict_gate_count=strict_count,
                strict_all_runs=(strict_count == len(spec_rows) and bool(spec_rows)),
                fallback_row_count=sum(row.fallback_row_count for row in spec_rows),
                mean_annualized_vol=_mean(row.mean_annualized_vol for row in spec_rows),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_runs,
            row.strict_gate_count,
            row.beats_brownian_count,
            -row.mean_brier,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _markdown(report: SpotRealizedVolTerminalDiagnosticReport) -> str:
    lines = [
        "# Spot Realized-Vol Terminal Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- spec_count: {report.spec_count}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | fallback_rows | mean_vol | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
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
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.fallback_row_count} | "
            f"{row.mean_annualized_vol:.4f} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Run Rows",
            "",
            "| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | fallback_rows | mean_vol | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|",
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
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} | "
            f"{row.beats_brownian} | "
            f"{row.beats_market} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.fallback_row_count} | "
            f"{row.mean_annualized_vol:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(
        [
            "",
            "## Run Inputs",
            "",
            "| run | rows | markets | spot_ticks | candidate_path | label_path | spot_tick_path |",
            "|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"{row.spot_tick_count} | "
            f"`{row.candidate_path}` | "
            f"`{row.label_path}` | "
            f"`{row.spot_tick_path}` |"
        )
    return "\n".join(lines) + "\n"


def _mean(values) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _clamp(value: float, low: float, high: float) -> float:
    if high < low:
        raise ValueError("cap_annualized_vol must be >= floor_annualized_vol")
    return min(high, max(low, float(value)))


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
