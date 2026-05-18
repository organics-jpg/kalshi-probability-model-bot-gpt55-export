from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence

from .ensemble_particle_replay import _variant_contexts
from .ev_decision import expected_pnl_cents
from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .schemas import Side
from .validation import brier_score, log_loss, top_bucket_mean_pnl


@dataclass(frozen=True)
class ResidualBlendCoefficient:
    name: str
    market_residual: float
    rv300_residual: float
    rv600_residual: float
    particle_residual: float


@dataclass(frozen=True)
class ResidualBlendRunFastRow:
    coefficient: ResidualBlendCoefficient
    run_name: str
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    current_baseline_total_counterfactual_pnl_cents: float
    beats_current_probability: bool
    beats_current_pnl: bool
    top_ev_bucket_pnl_cents: float


@dataclass(frozen=True)
class ResidualBlendRunExactRow:
    coefficient: ResidualBlendCoefficient
    run_name: str
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    brier: float
    log_loss: float
    current_baseline_total_counterfactual_pnl_cents: float
    beats_brownian: bool
    beats_market: bool
    beats_current_probability: bool
    beats_current_pnl: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float


@dataclass(frozen=True)
class ResidualBlendAggregateRow:
    coefficient: ResidualBlendCoefficient
    run_count: int
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    current_baseline_total_counterfactual_pnl_cents: float
    pnl_delta_vs_current_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_run_count: int
    beats_current_probability_run_count: int
    beats_current_pnl_run_count: int
    positive_ev_rank_run_count: int
    positive_top_bucket_run_count: int
    stable_all_runs: bool
    rows: tuple[ResidualBlendRunExactRow, ...]


@dataclass(frozen=True)
class ResidualBlendLoroPick:
    holdout_run: str
    selected_coefficient: ResidualBlendCoefficient
    train_run_count: int
    train_total_counterfactual_pnl_cents: float
    train_positive_pnl_run_count: int
    train_positive_top_bucket_run_count: int
    train_beats_current_probability_run_count: int
    holdout_exact: ResidualBlendRunExactRow


@dataclass(frozen=True)
class ResidualBlendLoroReport:
    report_roots: tuple[str, ...]
    run_count: int
    coefficient_count: int
    formula: str
    fast_global_leaders: tuple[dict[str, object], ...]
    exact_global_rows: tuple[ResidualBlendAggregateRow, ...]
    best_global_exact: ResidualBlendAggregateRow | None
    loro_picks: tuple[ResidualBlendLoroPick, ...]
    candidate_for_fresh_oos: ResidualBlendCoefficient | None
    promotion_safe: bool
    note: str


@dataclass(frozen=True)
class _RunBundle:
    name: str
    rows: tuple[ReplayInput, ...]
    contexts: tuple[dict[str, float], ...]
    current_baseline_total_counterfactual_pnl_cents: float
    current_baseline_brier: float
    current_baseline_log_loss: float


def evaluate_residual_blend_loro(
    report_roots: Sequence[Path],
    config: ReplayConfig | None = None,
    *,
    default_annualized_vol: float | None = None,
    allow_missing_labels: bool = False,
    max_exact_global: int = 5,
) -> ResidualBlendLoroReport:
    if not report_roots:
        raise ValueError("at least one report root is required")
    cfg = config or ReplayConfig()
    bundles = tuple(
        _load_run_bundle(
            root,
            cfg,
            default_annualized_vol=default_annualized_vol,
            allow_missing_labels=allow_missing_labels,
        )
        for root in report_roots
    )
    coefficients = tuple(_coefficient_grid())
    fast_by_name: dict[str, list[ResidualBlendRunFastRow]] = {coef.name: [] for coef in coefficients}
    for coefficient in coefficients:
        for bundle in bundles:
            fast_by_name[coefficient.name].append(_fast_evaluate_run(bundle, coefficient, cfg))

    fast_leaders = _fast_global_leaders(fast_by_name, limit=max(20, max_exact_global))
    exact_global_rows = tuple(
        _exact_aggregate(
            bundles,
            _coefficient_from_name(coefficients, str(row["name"])),
            cfg,
        )
        for row in fast_leaders[:max_exact_global]
    )
    exact_global_rows = tuple(sorted(exact_global_rows, key=_exact_sort_key, reverse=True))
    best_global = exact_global_rows[0] if exact_global_rows else None
    loro_picks = tuple(
        _loro_pick(
            holdout=bundle,
            train=[candidate for candidate in bundles if candidate.name != bundle.name],
            coefficients=coefficients,
            fast_by_name=fast_by_name,
            config=cfg,
        )
        for bundle in bundles
    )
    candidate = best_global.coefficient if best_global is not None else None
    return ResidualBlendLoroReport(
        report_roots=tuple(str(root) for root in report_roots),
        run_count=len(bundles),
        coefficient_count=len(coefficients),
        formula=(
            "p = current + a*(market-current) + b*(rv300-current) "
            "+ c*(rv600-current) + d*(particle-current)"
        ),
        fast_global_leaders=tuple(fast_leaders),
        exact_global_rows=exact_global_rows,
        best_global_exact=best_global,
        loro_picks=loro_picks,
        candidate_for_fresh_oos=candidate,
        promotion_safe=False,
        note=(
            "Residual blends are same-evidence diagnostics. Any selected "
            "coefficient is a new hypothesis and requires a fresh predeclared "
            "locked OOS shadow run before it can count toward promotion."
        ),
    )


def materialize_residual_blend_rows(
    rows: Sequence[ReplayInput],
    coefficient: ResidualBlendCoefficient,
) -> tuple[ReplayInput, ...]:
    sorted_rows = tuple(sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker)))
    contexts = tuple(_variant_contexts(sorted_rows))
    return tuple(
        replace(row, particle_p_yes=_blend_probability(context, coefficient))
        for row, context in zip(sorted_rows, contexts)
    )


def write_residual_blend_loro_report(
    report: ResidualBlendLoroReport,
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
        description=(
            "Run a research-only residual probability blend grid with leave-one-run-out diagnostics."
        )
    )
    parser.add_argument("--report-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="residual_blend_loro")
    parser.add_argument("--max-exact-global", default=5, type=int)
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
    report = evaluate_residual_blend_loro(
        args.report_root,
        ReplayConfig(
            min_ev_cents=args.min_ev_cents,
            min_fill_prob=args.min_fill_prob,
            no_fill_penalty_cents=args.no_fill_penalty_cents,
            counterfactual_fill_policy=args.counterfactual_fill_policy,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
        max_exact_global=args.max_exact_global,
    )
    json_path, md_path = write_residual_blend_loro_report(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"coefficient_count={report.coefficient_count}")
    if report.best_global_exact is not None:
        print(f"best_global_exact={report.best_global_exact.coefficient.name}")
        print(f"best_global_total_counterfactual_pnl_cents={report.best_global_exact.total_counterfactual_pnl_cents:.4f}")
        print(f"best_global_pnl_delta_vs_current_cents={report.best_global_exact.pnl_delta_vs_current_cents:.4f}")
        print(f"best_global_beats_current_pnl_run_count={report.best_global_exact.beats_current_pnl_run_count}")
        print(f"best_global_positive_ev_rank_run_count={report.best_global_exact.positive_ev_rank_run_count}")
        print(f"best_global_positive_top_bucket_run_count={report.best_global_exact.positive_top_bucket_run_count}")
    print(f"loro_pick_count={len(report.loro_picks)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_run_bundle(
    root: Path,
    config: ReplayConfig,
    *,
    default_annualized_vol: float | None,
    allow_missing_labels: bool,
) -> _RunBundle:
    candidates, labels = _resolve_replay_paths(root)
    rows = tuple(
        sorted(
            load_replay_inputs_from_jsonl(
                candidates,
                labels,
                default_annualized_vol=default_annualized_vol,
                allow_missing_labels=allow_missing_labels,
            ),
            key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker),
        )
    )
    if not rows:
        raise ValueError(f"{root} produced no replay rows")
    contexts = tuple(_variant_contexts(rows))
    current_rows = tuple(replace(row, particle_p_yes=row.current_calibrated_p_yes) for row in rows)
    current_report = evaluate_replay(current_rows, config)
    name = root.name
    return _RunBundle(
        name=name,
        rows=rows,
        contexts=contexts,
        current_baseline_total_counterfactual_pnl_cents=current_report.total_counterfactual_pnl_cents,
        current_baseline_brier=current_report.particle.brier,
        current_baseline_log_loss=current_report.particle.log_loss,
    )


def _resolve_replay_paths(root: Path) -> tuple[Path, Path]:
    candidates = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_options = (
        root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        root / "settlement_labels" / "settlement_labels.ndjson",
    )
    if not candidates.exists():
        raise FileNotFoundError(f"missing candidate snapshots: {candidates}")
    for labels in label_options:
        if labels.exists():
            return candidates, labels
    raise FileNotFoundError(f"missing labels under {root}")


def _coefficient_grid() -> Iterable[ResidualBlendCoefficient]:
    values = (-0.20, -0.10, 0.0, 0.10, 0.20, 0.30)
    seen: set[tuple[float, float, float, float]] = set()
    for market in values:
        for rv300 in values:
            for rv600 in values:
                for particle in values:
                    key = (market, rv300, rv600, particle)
                    if sum(abs(value) for value in key) > 0.50:
                        continue
                    if key in seen:
                        continue
                    seen.add(key)
                    yield ResidualBlendCoefficient(
                        name=_coefficient_name(*key),
                        market_residual=market,
                        rv300_residual=rv300,
                        rv600_residual=rv600,
                        particle_residual=particle,
                    )


def _fast_evaluate_run(
    bundle: _RunBundle,
    coefficient: ResidualBlendCoefficient,
    config: ReplayConfig,
) -> ResidualBlendRunFastRow:
    labels: list[int] = []
    probabilities: list[float] = []
    selected_ev: list[float] = []
    pnl_values: list[float] = []
    selected_count = 0
    for row, context in zip(bundle.rows, bundle.contexts):
        p_yes = _blend_probability(context, coefficient)
        labels.append(1 if row.label.result_yes else 0)
        probabilities.append(p_yes)
        ev_yes = expected_pnl_cents(
            p_win=p_yes,
            ask_cents=row.snapshot.yes_ask_cents,
            fee_if_win_cents=row.snapshot.fee_cents,
            fill_prob=_fill_prob_for(row, "yes"),
            no_fill_penalty_cents=config.no_fill_penalty_cents,
        )
        ev_no = expected_pnl_cents(
            p_win=1.0 - p_yes,
            ask_cents=row.snapshot.no_ask_cents,
            fee_if_win_cents=row.snapshot.fee_cents,
            fill_prob=_fill_prob_for(row, "no"),
            no_fill_penalty_cents=config.no_fill_penalty_cents,
        )
        side: Side = "yes" if ev_yes >= ev_no else "no"
        selected_ev.append(max(ev_yes, ev_no))
        fill_prob = _fill_prob_for(row, side)
        selected = fill_prob >= config.min_fill_prob and max(ev_yes, ev_no) >= config.min_ev_cents
        if not selected:
            pnl_values.append(0.0)
            continue
        selected_count += 1
        if not _counterfactual_filled(fill_prob, config):
            pnl_values.append(-config.no_fill_penalty_cents)
            continue
        won = row.label.result_yes if side == "yes" else not row.label.result_yes
        ask = row.snapshot.yes_ask_cents if side == "yes" else row.snapshot.no_ask_cents
        pnl_values.append(100.0 - ask - row.snapshot.fee_cents if won else -ask)
    score_brier = brier_score(probabilities, labels)
    score_log_loss = log_loss(probabilities, labels)
    total_pnl = sum(pnl_values)
    return ResidualBlendRunFastRow(
        coefficient=coefficient,
        run_name=bundle.name,
        candidate_count=len(bundle.rows),
        selected_count=selected_count,
        total_counterfactual_pnl_cents=total_pnl,
        brier=score_brier,
        log_loss=score_log_loss,
        current_baseline_total_counterfactual_pnl_cents=bundle.current_baseline_total_counterfactual_pnl_cents,
        beats_current_probability=(
            score_brier < bundle.current_baseline_brier
            and score_log_loss < bundle.current_baseline_log_loss
        ),
        beats_current_pnl=total_pnl > bundle.current_baseline_total_counterfactual_pnl_cents,
        top_ev_bucket_pnl_cents=top_bucket_mean_pnl(selected_ev, pnl_values, top_fraction=0.25),
    )


def _exact_evaluate_run(
    bundle: _RunBundle,
    coefficient: ResidualBlendCoefficient,
    config: ReplayConfig,
) -> ResidualBlendRunExactRow:
    variant_rows = materialize_residual_blend_rows(bundle.rows, coefficient)
    replay = evaluate_replay(variant_rows, config)
    return ResidualBlendRunExactRow(
        coefficient=coefficient,
        run_name=bundle.name,
        candidate_count=replay.candidate_count,
        selected_count=replay.selected_count,
        total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
        avg_counterfactual_pnl_cents_per_candidate=replay.avg_counterfactual_pnl_cents_per_candidate,
        avg_counterfactual_pnl_cents_per_selected=replay.avg_counterfactual_pnl_cents_per_selected,
        brier=replay.particle.brier,
        log_loss=replay.particle.log_loss,
        current_baseline_total_counterfactual_pnl_cents=bundle.current_baseline_total_counterfactual_pnl_cents,
        beats_brownian=replay.particle_beats_brownian,
        beats_market=replay.particle_beats_market,
        beats_current_probability=replay.particle_beats_current_calibrated,
        beats_current_pnl=(
            replay.total_counterfactual_pnl_cents
            > bundle.current_baseline_total_counterfactual_pnl_cents
        ),
        ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
        top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
    )


def _exact_aggregate(
    bundles: Sequence[_RunBundle],
    coefficient: ResidualBlendCoefficient,
    config: ReplayConfig,
) -> ResidualBlendAggregateRow:
    rows = tuple(_exact_evaluate_run(bundle, coefficient, config) for bundle in bundles)
    total_pnl = sum(row.total_counterfactual_pnl_cents for row in rows)
    current_total = sum(row.current_baseline_total_counterfactual_pnl_cents for row in rows)
    run_count = len(rows)
    return ResidualBlendAggregateRow(
        coefficient=coefficient,
        run_count=run_count,
        candidate_count=sum(row.candidate_count for row in rows),
        selected_count=sum(row.selected_count for row in rows),
        total_counterfactual_pnl_cents=total_pnl,
        current_baseline_total_counterfactual_pnl_cents=current_total,
        pnl_delta_vs_current_cents=total_pnl - current_total,
        mean_brier=sum(row.brier for row in rows) / run_count,
        mean_log_loss=sum(row.log_loss for row in rows) / run_count,
        positive_pnl_run_count=sum(1 for row in rows if row.total_counterfactual_pnl_cents > 0.0),
        beats_current_probability_run_count=sum(1 for row in rows if row.beats_current_probability),
        beats_current_pnl_run_count=sum(1 for row in rows if row.beats_current_pnl),
        positive_ev_rank_run_count=sum(1 for row in rows if row.ev_rank_correlation_sign > 0.0),
        positive_top_bucket_run_count=sum(1 for row in rows if row.top_ev_bucket_pnl_cents > 0.0),
        stable_all_runs=all(
            row.total_counterfactual_pnl_cents > 0.0
            and row.beats_current_probability
            and row.beats_current_pnl
            and row.ev_rank_correlation_sign > 0.0
            and row.top_ev_bucket_pnl_cents > 0.0
            for row in rows
        ),
        rows=rows,
    )


def _loro_pick(
    *,
    holdout: _RunBundle,
    train: Sequence[_RunBundle],
    coefficients: Sequence[ResidualBlendCoefficient],
    fast_by_name: dict[str, list[ResidualBlendRunFastRow]],
    config: ReplayConfig,
) -> ResidualBlendLoroPick:
    train_names = {bundle.name for bundle in train}
    ranked: list[tuple[tuple[float, ...], ResidualBlendCoefficient, list[ResidualBlendRunFastRow]]] = []
    for coefficient in coefficients:
        rows = [row for row in fast_by_name[coefficient.name] if row.run_name in train_names]
        ranked.append((_fast_sort_key(rows), coefficient, rows))
    ranked.sort(key=lambda item: item[0], reverse=True)
    _, coefficient, rows = ranked[0]
    holdout_exact = _exact_evaluate_run(holdout, coefficient, config)
    return ResidualBlendLoroPick(
        holdout_run=holdout.name,
        selected_coefficient=coefficient,
        train_run_count=len(rows),
        train_total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in rows),
        train_positive_pnl_run_count=sum(1 for row in rows if row.total_counterfactual_pnl_cents > 0.0),
        train_positive_top_bucket_run_count=sum(1 for row in rows if row.top_ev_bucket_pnl_cents > 0.0),
        train_beats_current_probability_run_count=sum(1 for row in rows if row.beats_current_probability),
        holdout_exact=holdout_exact,
    )


def _fast_global_leaders(
    fast_by_name: dict[str, list[ResidualBlendRunFastRow]],
    *,
    limit: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, run_rows in fast_by_name.items():
        coefficient = run_rows[0].coefficient
        total_pnl = sum(row.total_counterfactual_pnl_cents for row in run_rows)
        current_total = sum(row.current_baseline_total_counterfactual_pnl_cents for row in run_rows)
        rows.append(
            {
                "name": name,
                "coefficient": asdict(coefficient),
                "run_count": len(run_rows),
                "candidate_count": sum(row.candidate_count for row in run_rows),
                "selected_count": sum(row.selected_count for row in run_rows),
                "total_counterfactual_pnl_cents": total_pnl,
                "current_baseline_total_counterfactual_pnl_cents": current_total,
                "pnl_delta_vs_current_cents": total_pnl - current_total,
                "mean_brier": sum(row.brier for row in run_rows) / len(run_rows),
                "mean_log_loss": sum(row.log_loss for row in run_rows) / len(run_rows),
                "positive_pnl_run_count": sum(1 for row in run_rows if row.total_counterfactual_pnl_cents > 0.0),
                "beats_current_probability_run_count": sum(1 for row in run_rows if row.beats_current_probability),
                "beats_current_pnl_run_count": sum(1 for row in run_rows if row.beats_current_pnl),
                "positive_top_bucket_run_count": sum(1 for row in run_rows if row.top_ev_bucket_pnl_cents > 0.0),
            }
        )
    rows.sort(key=_fast_leader_sort_key, reverse=True)
    return rows[:limit]


def _fast_sort_key(rows: Sequence[ResidualBlendRunFastRow]) -> tuple[float, ...]:
    return (
        float(sum(1 for row in rows if row.top_ev_bucket_pnl_cents > 0.0)),
        float(sum(1 for row in rows if row.total_counterfactual_pnl_cents > 0.0)),
        float(sum(1 for row in rows if row.beats_current_probability)),
        float(sum(1 for row in rows if row.beats_current_pnl)),
        sum(row.total_counterfactual_pnl_cents for row in rows),
        -sum(row.brier for row in rows) / len(rows),
    )


def _fast_leader_sort_key(row: dict[str, object]) -> tuple[float, ...]:
    return (
        float(row["positive_top_bucket_run_count"]),
        float(row["positive_pnl_run_count"]),
        float(row["beats_current_probability_run_count"]),
        float(row["beats_current_pnl_run_count"]),
        float(row["total_counterfactual_pnl_cents"]),
        -float(row["mean_brier"]),
    )


def _exact_sort_key(row: ResidualBlendAggregateRow) -> tuple[float, ...]:
    return (
        float(row.positive_top_bucket_run_count),
        float(row.positive_pnl_run_count),
        float(row.beats_current_probability_run_count),
        float(row.beats_current_pnl_run_count),
        row.total_counterfactual_pnl_cents,
        -row.mean_brier,
    )


def _blend_probability(context: dict[str, float], coefficient: ResidualBlendCoefficient) -> float:
    current = float(context["current"])
    return _clamp01(
        current
        + coefficient.market_residual * (float(context["market"]) - current)
        + coefficient.rv300_residual * (float(context["rv300"]) - current)
        + coefficient.rv600_residual * (float(context["rv600"]) - current)
        + coefficient.particle_residual * (float(context["particle"]) - current)
    )


def _coefficient_from_name(
    coefficients: Sequence[ResidualBlendCoefficient],
    name: str,
) -> ResidualBlendCoefficient:
    for coefficient in coefficients:
        if coefficient.name == name:
            return coefficient
    raise KeyError(name)


def _coefficient_name(
    market: float,
    rv300: float,
    rv600: float,
    particle: float,
) -> str:
    return (
        "resid_m{market}_r300{rv300}_r600{rv600}_p{particle}"
        .format(
            market=_fmt_coeff(market),
            rv300=_fmt_coeff(rv300),
            rv600=_fmt_coeff(rv600),
            particle=_fmt_coeff(particle),
        )
    )


def _fmt_coeff(value: float) -> str:
    sign = "p" if value >= 0.0 else "n"
    return sign + str(abs(value)).replace(".", "")


def _fill_prob_for(row: ReplayInput, side: Side) -> float:
    if side == "yes" and row.snapshot.yes_fill_prob is not None:
        return row.snapshot.yes_fill_prob
    if side == "no" and row.snapshot.no_fill_prob is not None:
        return row.snapshot.no_fill_prob
    return row.snapshot.fill_prob


def _counterfactual_filled(fill_prob: float, config: ReplayConfig) -> bool:
    if config.counterfactual_fill_policy == "always_fill":
        return True
    if config.counterfactual_fill_policy == "never_fill":
        return False
    return fill_prob >= config.counterfactual_fill_threshold


def _markdown(report: ResidualBlendLoroReport) -> str:
    lines = [
        "# Residual Blend LORO Report",
        "",
        f"- run_count: {report.run_count}",
        f"- coefficient_count: {report.coefficient_count}",
        f"- formula: `{report.formula}`",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
    ]
    if report.best_global_exact is not None:
        best = report.best_global_exact
        lines.extend(
            [
                "## Best Exact Global Diagnostic",
                "",
                f"- name: {best.coefficient.name}",
                f"- total_counterfactual_pnl_cents: {best.total_counterfactual_pnl_cents:.4f}",
                f"- current_baseline_total_counterfactual_pnl_cents: {best.current_baseline_total_counterfactual_pnl_cents:.4f}",
                f"- pnl_delta_vs_current_cents: {best.pnl_delta_vs_current_cents:.4f}",
                f"- mean_brier: {best.mean_brier:.6f}",
                f"- mean_log_loss: {best.mean_log_loss:.6f}",
                f"- beats_current_probability_run_count: {best.beats_current_probability_run_count}/{best.run_count}",
                f"- beats_current_pnl_run_count: {best.beats_current_pnl_run_count}/{best.run_count}",
                f"- positive_ev_rank_run_count: {best.positive_ev_rank_run_count}/{best.run_count}",
                f"- positive_top_bucket_run_count: {best.positive_top_bucket_run_count}/{best.run_count}",
                f"- stable_all_runs: {best.stable_all_runs}",
                "",
            ]
        )
    lines.extend(
        [
            "## Exact Global Rows",
            "",
            "| coefficient | pnl_cents | delta_vs_current | mean_brier | beats_current_prob | beats_current_pnl | ev_rank_pos | top_bucket_pos | stable_all_runs |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.exact_global_rows:
        lines.append(
            "| {name} | {pnl:.4f} | {delta:.4f} | {brier:.6f} | {prob}/{runs} | "
            "{pnl_runs}/{runs} | {ev}/{runs} | {top}/{runs} | {stable} |".format(
                name=row.coefficient.name,
                pnl=row.total_counterfactual_pnl_cents,
                delta=row.pnl_delta_vs_current_cents,
                brier=row.mean_brier,
                prob=row.beats_current_probability_run_count,
                pnl_runs=row.beats_current_pnl_run_count,
                ev=row.positive_ev_rank_run_count,
                top=row.positive_top_bucket_run_count,
                runs=row.run_count,
                stable=row.stable_all_runs,
            )
        )
    lines.extend(
        [
            "",
            "## Leave One Run Out Picks",
            "",
            "| holdout | selected_coefficient | train_pnl_cents | holdout_pnl_cents | holdout_delta_vs_current | holdout_beats_current_prob | holdout_ev_rank | holdout_top_bucket_pnl |",
            "|---|---|---:|---:|---:|---|---:|---:|",
        ]
    )
    for pick in report.loro_picks:
        row = pick.holdout_exact
        lines.append(
            "| {holdout} | {coef} | {train_pnl:.4f} | {holdout_pnl:.4f} | "
            "{delta:.4f} | {beats_prob} | {ev:.6f} | {top:.4f} |".format(
                holdout=pick.holdout_run,
                coef=pick.selected_coefficient.name,
                train_pnl=pick.train_total_counterfactual_pnl_cents,
                holdout_pnl=row.total_counterfactual_pnl_cents,
                delta=(
                    row.total_counterfactual_pnl_cents
                    - row.current_baseline_total_counterfactual_pnl_cents
                ),
                beats_prob=row.beats_current_probability,
                ev=row.ev_rank_correlation_sign,
                top=row.top_ev_bucket_pnl_cents,
            )
        )
    return "\n".join(lines) + "\n"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
