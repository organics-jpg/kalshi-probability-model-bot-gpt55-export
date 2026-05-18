from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Callable, Literal, Mapping, Sequence

from .calibrators import OnlineLogitCalibrator
from .dynamic_particle_replay import DynamicParticleSpec, RollingVolEstimator
from .replay_runner import (
    ProbabilityScorecard,
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .terminal_projection import brownian_terminal_probability
from .validation import brier_score, log_loss


VariantContext = Mapping[str, float]
VariantFn = Callable[[VariantContext], float]
UpdateMode = Literal["candidate", "market_mean"]


@dataclass(frozen=True)
class OnlineLogitParticleRow:
    name: str
    raw_source_name: str
    candidate_count: int
    selected_count: int
    coverage_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    brier: float
    log_loss: float
    raw_source_brier: float
    raw_source_log_loss: float
    online_beats_raw_source: bool
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    update_count: int
    update_mode: str
    final_bias: float
    final_slope: float


@dataclass(frozen=True)
class OnlineLogitParticleReport:
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    all_candidate_denominator: bool
    learning_rate: float
    l2: float
    update_mode: str
    rows: tuple[OnlineLogitParticleRow, ...]
    best_by_brier: OnlineLogitParticleRow
    best_by_pnl: OnlineLogitParticleRow
    promotion_safe: bool
    note: str


def evaluate_online_logit_particle_variants(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
    *,
    learning_rate: float = 0.03,
    l2: float = 0.001,
    update_mode: UpdateMode = "candidate",
) -> OnlineLogitParticleReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    contexts = _variant_contexts(sorted_rows)
    labels = [1 if row.label.result_yes else 0 for row in sorted_rows]
    summaries: list[OnlineLogitParticleRow] = []
    for raw_source_name, fn in _variant_registry():
        raw_probs = [_clamp01(fn(context)) for context in contexts]
        raw_score = ProbabilityScorecard(
            brier_score(raw_probs, labels),
            log_loss(raw_probs, labels),
        )
        calibrator = OnlineLogitCalibrator(learning_rate=learning_rate, l2=l2)
        pending_updates: list[tuple[datetime, float, int]] = []
        pending_market_updates: dict[str, MarketUpdate] = {}
        calibrated_rows: list[ReplayInput] = []
        calibrated_probs: list[float] = []
        update_count = 0
        for row, raw_p, label_int in zip(sorted_rows, raw_probs, labels):
            if update_mode == "candidate":
                update_count += _apply_available_updates(
                    pending_updates,
                    row.snapshot.decision_ts_utc,
                    calibrator,
                )
            elif update_mode == "market_mean":
                update_count += _apply_available_market_updates(
                    pending_market_updates,
                    row.snapshot.decision_ts_utc,
                    calibrator,
                )
            else:
                raise ValueError(f"unsupported update_mode: {update_mode}")
            calibrated_p = _clamp01(calibrator.predict(raw_p))
            calibrated_probs.append(calibrated_p)
            calibrated_rows.append(replace(row, particle_p_yes=calibrated_p))
            if update_mode == "candidate":
                pending_updates.append((row.label.label_available_ts_utc, raw_p, label_int))
            else:
                _add_market_update(
                    pending_market_updates,
                    row.snapshot.market_ticker,
                    row.label.label_available_ts_utc,
                    label_int,
                    raw_p,
                )
        if update_mode == "candidate":
            update_count += _apply_available_updates(
                pending_updates,
                datetime.max.replace(tzinfo=timezone.utc),
                calibrator,
            )
        else:
            update_count += _apply_available_market_updates(
                pending_market_updates,
                datetime.max.replace(tzinfo=timezone.utc),
                calibrator,
            )
        online_score = ProbabilityScorecard(
            brier_score(calibrated_probs, labels),
            log_loss(calibrated_probs, labels),
        )
        replay = evaluate_replay(calibrated_rows, cfg)
        row_name = (
            f"online_logit_{raw_source_name}"
            if update_mode == "candidate"
            else f"online_logit_{update_mode}_{raw_source_name}"
        )
        summaries.append(
            OnlineLogitParticleRow(
                name=row_name,
                raw_source_name=raw_source_name,
                candidate_count=replay.candidate_count,
                selected_count=replay.selected_count,
                coverage_rate=replay.selected_count / replay.candidate_count,
                total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                avg_counterfactual_pnl_cents_per_candidate=(
                    replay.avg_counterfactual_pnl_cents_per_candidate
                ),
                avg_counterfactual_pnl_cents_per_selected=(
                    replay.avg_counterfactual_pnl_cents_per_selected
                ),
                brier=online_score.brier,
                log_loss=online_score.log_loss,
                raw_source_brier=raw_score.brier,
                raw_source_log_loss=raw_score.log_loss,
                online_beats_raw_source=(
                    online_score.brier < raw_score.brier
                    and online_score.log_loss < raw_score.log_loss
                ),
                beats_brownian=replay.particle_beats_brownian,
                beats_market=replay.particle_beats_market,
                beats_current_calibrated=replay.particle_beats_current_calibrated,
                ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                update_count=update_count,
                update_mode=update_mode,
                final_bias=calibrator.bias,
                final_slope=calibrator.slope,
            )
        )
    best_by_brier = min(summaries, key=lambda row: (row.brier, row.log_loss))
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents)
    return OnlineLogitParticleReport(
        candidate_count=len(sorted_rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        all_candidate_denominator=True,
        learning_rate=learning_rate,
        l2=l2,
        update_mode=update_mode,
        rows=tuple(summaries),
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=False,
        note=(
            "Online-logit calibration variants are locked-run diagnostics only. "
            "They update only after label_available_ts_utc and do not promote a "
            "strategy without a fresh predeclared OOS/shadow run."
        ),
    )


def write_online_logit_particle_report(
    report: OnlineLogitParticleReport,
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
        description="Evaluate label-gated online-logit probability variants on a strict labeled denominator."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="online_logit_particle_replay")
    parser.add_argument("--learning-rate", default=0.03, type=float)
    parser.add_argument("--l2", default=0.001, type=float)
    parser.add_argument(
        "--update-mode",
        choices=["candidate", "market_mean"],
        default="candidate",
        help="candidate updates once per candidate; market_mean updates once per resolved market using mean raw p",
    )
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--default-annualized-vol", default=None, type=float)
    parser.add_argument("--allow-missing-labels", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_replay_inputs_from_jsonl(
        args.candidates,
        args.labels,
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
    )
    source_candidate_count = _line_count(args.candidates)
    skipped_unlabeled_count = max(0, source_candidate_count - len(rows))
    denominator_scope = "resolved_labeled_subset" if args.allow_missing_labels else "all_labeled_candidates"
    report = replace(
        evaluate_online_logit_particle_variants(
            rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
            learning_rate=args.learning_rate,
            l2=args.l2,
            update_mode=args.update_mode,
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_online_logit_particle_report(report, args.output_dir, args.stem)
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"best_by_brier={report.best_by_brier.name}")
    print(f"best_by_brier_brier={report.best_by_brier.brier:.6f}")
    print(f"best_by_pnl={report.best_by_pnl.name}")
    print(f"best_by_pnl_total_counterfactual_pnl_cents={report.best_by_pnl.total_counterfactual_pnl_cents:.4f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _variant_contexts(rows: Sequence[ReplayInput]) -> list[dict[str, float]]:
    specs = (
        DynamicParticleSpec(
            name="rv300",
            lookback_seconds=300.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
        DynamicParticleSpec(
            name="rv600",
            lookback_seconds=600.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
    )
    estimators = {spec.name: RollingVolEstimator(spec) for spec in specs}
    contexts: list[dict[str, float]] = []
    for row in rows:
        seconds_to_close = max(
            0.0,
            (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds(),
        )
        dynamic: dict[str, float] = {}
        for spec in specs:
            vol = estimators[spec.name].observe_and_estimate(
                row.snapshot.decision_ts_utc,
                row.snapshot.spot,
            )
            dynamic[spec.name] = brownian_terminal_probability(
                row.snapshot.spot,
                row.snapshot.strike,
                seconds_to_close,
                vol,
            )
        contexts.append(
            {
                "particle": row.particle_p_yes,
                "brownian": row.brownian_p_yes,
                "market": row.market_p_yes,
                "current": row.current_calibrated_p_yes,
                **dynamic,
            }
        )
    return contexts


def _variant_registry() -> tuple[tuple[str, VariantFn], ...]:
    return (
        ("particle", lambda ctx: ctx["particle"]),
        ("current_calibrated", lambda ctx: ctx["current"]),
        ("rolling_vol_300s", lambda ctx: ctx["rv300"]),
        ("rolling_vol_600s", lambda ctx: ctx["rv600"]),
        (
            "median_current_rv300_rv600",
            lambda ctx: median((ctx["current"], ctx["rv300"], ctx["rv600"])),
        ),
        (
            "blend_50current_25particle_25rv600",
            lambda ctx: 0.50 * ctx["current"] + 0.25 * ctx["particle"] + 0.25 * ctx["rv600"],
        ),
    )


@dataclass
class MarketUpdate:
    label_available_ts_utc: datetime
    label: int
    raw_probs: list[float]


def _apply_available_updates(
    pending_updates: list[tuple[datetime, float, int]],
    as_of_ts_utc: datetime,
    calibrator: OnlineLogitCalibrator,
) -> int:
    ready = [update for update in pending_updates if update[0] <= as_of_ts_utc]
    if not ready:
        return 0
    ready.sort(key=lambda update: update[0])
    remaining = [update for update in pending_updates if update[0] > as_of_ts_utc]
    pending_updates.clear()
    pending_updates.extend(remaining)
    for _, p_raw, label in ready:
        calibrator.update_with_label(p_raw, label)
    return len(ready)


def _add_market_update(
    pending_updates: dict[str, MarketUpdate],
    market_ticker: str,
    label_available_ts_utc: datetime,
    label: int,
    raw_p: float,
) -> None:
    update = pending_updates.get(market_ticker)
    if update is None:
        pending_updates[market_ticker] = MarketUpdate(
            label_available_ts_utc=label_available_ts_utc,
            label=label,
            raw_probs=[raw_p],
        )
        return
    if update.label != label:
        raise ValueError(f"{market_ticker} has inconsistent labels in clustered update")
    if update.label_available_ts_utc != label_available_ts_utc:
        raise ValueError(f"{market_ticker} has inconsistent label availability in clustered update")
    update.raw_probs.append(raw_p)


def _apply_available_market_updates(
    pending_updates: dict[str, MarketUpdate],
    as_of_ts_utc: datetime,
    calibrator: OnlineLogitCalibrator,
) -> int:
    ready = [
        (market_ticker, update)
        for market_ticker, update in pending_updates.items()
        if update.label_available_ts_utc <= as_of_ts_utc
    ]
    if not ready:
        return 0
    ready.sort(key=lambda item: item[1].label_available_ts_utc)
    for market_ticker, update in ready:
        mean_raw_p = sum(update.raw_probs) / len(update.raw_probs)
        calibrator.update_with_label(mean_raw_p, update.label)
        del pending_updates[market_ticker]
    return len(ready)


def _markdown(report: OnlineLogitParticleReport) -> str:
    lines = [
        "# Online Logit Particle Replay Report",
        "",
        f"- candidate_count: {report.candidate_count}",
        f"- source_candidate_count: {report.source_candidate_count}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- all_candidate_denominator: {report.all_candidate_denominator}",
        f"- learning_rate: {report.learning_rate:.6f}",
        f"- l2: {report.l2:.6f}",
        f"- update_mode: {report.update_mode}",
        f"- best_by_brier: {report.best_by_brier.name}",
        f"- best_by_pnl: {report.best_by_pnl.name}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
        "| variant | raw_source | update_mode | brier | log_loss | raw_brier | raw_log_loss | pnl_cents | selected | coverage | beats_raw | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | updates | final_bias | final_slope |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report.rows:
        lines.append(
            "| {name} | {raw_source_name} | {update_mode} | {brier:.6f} | {log_loss:.6f} | "
            "{raw_source_brier:.6f} | {raw_source_log_loss:.6f} | "
            "{total_counterfactual_pnl_cents:.4f} | {selected_count} | "
            "{coverage_rate:.4f} | {online_beats_raw_source} | "
            "{beats_brownian} | {beats_market} | {beats_current_calibrated} | "
            "{ev_rank_correlation_sign:.6f} | {top_ev_bucket_pnl_cents:.4f} | "
            "{update_count} | {final_bias:.6f} | {final_slope:.6f} |".format(**asdict(row))
        )
    return "\n".join(lines) + "\n"


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
