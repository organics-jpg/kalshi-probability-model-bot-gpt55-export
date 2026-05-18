from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Callable, Iterable, Sequence

from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl


FeatureFn = Callable[[ReplayInput], tuple[float, ...]]


@dataclass(frozen=True)
class MetaModelSpec:
    name: str
    feature_names: tuple[str, ...]
    feature_fn: FeatureFn


@dataclass(frozen=True)
class TrainedMetaModel:
    spec: MetaModelSpec
    means: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    train_loss: float
    train_market_count: int


@dataclass(frozen=True)
class RunInputSet:
    name: str
    root: str
    candidate_path: str
    label_path: str
    row_count: int
    market_count: int


@dataclass(frozen=True)
class MetaProbabilityHoldoutRow:
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
class MetaProbabilitySummaryRow:
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
class MetaProbabilityLOROReport:
    run_inputs: tuple[RunInputSet, ...]
    holdout_rows: tuple[MetaProbabilityHoldoutRow, ...]
    summary_rows: tuple[MetaProbabilitySummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_meta_probability_loro_report(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    learning_rate: float = 0.08,
    l2: float = 0.20,
    epochs: int = 1200,
) -> MetaProbabilityLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]
    holdout_rows: list[MetaProbabilityHoldoutRow] = []
    for holdout_name, holdout_meta, holdout_rows_raw in loaded_runs:
        train = [
            row
            for run_name, _, rows in loaded_runs
            if run_name != holdout_name
            for row in rows
        ]
        train_market_count = len({row.snapshot.market_ticker for row in train})
        for spec in _model_specs():
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
                MetaProbabilityHoldoutRow(
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
    summary_rows = tuple(_summarize_holdouts(holdout_rows))
    promotion_safe = any(row.strict_all_holdouts for row in summary_rows)
    conclusion = (
        "At least one simple meta-probability model passes every strict locked holdout; "
        "still treat it as a candidate requiring a fresh predeclared shadow run."
        if promotion_safe
        else "No simple market-cluster-trained meta-probability model passes strict locked holdout gates."
    )
    return MetaProbabilityLOROReport(
        run_inputs=tuple(meta for _, meta, _ in loaded_runs),
        holdout_rows=tuple(holdout_rows),
        summary_rows=summary_rows,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_meta_probability_loro_report(
    report: MetaProbabilityLOROReport,
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
        description="Train simple meta-probability models on all-but-one locked runs and replay held-out runs."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="meta_probability_loro")
    parser.add_argument("--learning-rate", default=0.08, type=float)
    parser.add_argument("--l2", default=0.20, type=float)
    parser.add_argument("--epochs", default=1200, type=int)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_meta_probability_loro_report(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        learning_rate=args.learning_rate,
        l2=args.l2,
        epochs=args.epochs,
    )
    json_path, md_path = write_meta_probability_loro_report(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_run(root: Path) -> tuple[str, RunInputSet, list[ReplayInput]]:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = _find_label_path(root)
    rows = load_replay_inputs_from_jsonl(candidate_path, label_path)
    meta = RunInputSet(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
    )
    return root.name, meta, rows


def _find_label_path(root: Path) -> Path:
    candidates = (
        root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        root / "pipeline_work" / "label_contexts_full.ndjson",
        root / "pipeline_work" / "label_contexts.ndjson",
        root / "settlement_labels" / "settlement_labels.ndjson",
    )
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"no label file found under {root}")


def _model_specs() -> tuple[MetaModelSpec, ...]:
    return (
        MetaModelSpec(
            "logit_current",
            ("logit_current",),
            lambda row: (_logit(row.current_calibrated_p_yes),),
        ),
        MetaModelSpec(
            "logit_market_current",
            ("logit_market", "logit_current"),
            lambda row: (_logit(row.market_p_yes), _logit(row.current_calibrated_p_yes)),
        ),
        MetaModelSpec(
            "logit_market_current_particle",
            ("logit_market", "logit_current", "logit_particle"),
            lambda row: (
                _logit(row.market_p_yes),
                _logit(row.current_calibrated_p_yes),
                _logit(row.particle_p_yes),
            ),
        ),
        MetaModelSpec(
            "current_with_residuals",
            ("logit_current", "market_minus_current", "particle_minus_current"),
            lambda row: (
                _logit(row.current_calibrated_p_yes),
                row.market_p_yes - row.current_calibrated_p_yes,
                row.particle_p_yes - row.current_calibrated_p_yes,
            ),
        ),
    )


def _train_model(
    spec: MetaModelSpec,
    rows: Sequence[ReplayInput],
    *,
    learning_rate: float,
    l2: float,
    epochs: int,
) -> TrainedMetaModel:
    samples = _market_mean_samples(spec, rows)
    if not samples:
        raise ValueError("no training samples")
    raw_features = [sample[0] for sample in samples]
    labels = [sample[1] for sample in samples]
    means, scales = _feature_standardizer(raw_features)
    features = [_standardize(values, means, scales) for values in raw_features]
    weights = [0.0 for _ in range(len(spec.feature_names) + 1)]
    for _ in range(max(1, epochs)):
        grads = [0.0 for _ in weights]
        loss = 0.0
        for values, label in zip(features, labels):
            x = (1.0, *values)
            pred = _sigmoid(_dot(weights, x))
            loss += _log_loss_one(pred, label)
            for idx, value in enumerate(x):
                grads[idx] += (pred - label) * value
        for idx in range(1, len(weights)):
            grads[idx] += l2 * weights[idx]
        scale = 1.0 / len(features)
        for idx in range(len(weights)):
            weights[idx] -= learning_rate * grads[idx] * scale
    train_loss = _regularized_loss(weights, features, labels, l2)
    return TrainedMetaModel(
        spec=spec,
        means=means,
        scales=scales,
        weights=tuple(weights),
        train_loss=train_loss,
        train_market_count=len(samples),
    )


def _market_mean_samples(spec: MetaModelSpec, rows: Sequence[ReplayInput]) -> list[tuple[tuple[float, ...], int]]:
    grouped: dict[str, list[ReplayInput]] = {}
    for row in rows:
        grouped.setdefault(row.snapshot.market_ticker, []).append(row)
    samples: list[tuple[tuple[float, ...], int]] = []
    for market_rows in grouped.values():
        label = 1 if market_rows[0].label.result_yes else 0
        features = [spec.feature_fn(row) for row in market_rows]
        averaged = tuple(
            sum(values[idx] for values in features) / len(features)
            for idx in range(len(features[0]))
        )
        samples.append((averaged, label))
    return samples


def _predict_model(model: TrainedMetaModel, row: ReplayInput) -> float:
    raw = model.spec.feature_fn(row)
    features = _standardize(raw, model.means, model.scales)
    return _sigmoid(_dot(model.weights, (1.0, *features)))


def _summarize_holdouts(rows: Sequence[MetaProbabilityHoldoutRow]) -> list[MetaProbabilitySummaryRow]:
    grouped: dict[str, list[MetaProbabilityHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.model, []).append(row)
    summaries: list[MetaProbabilitySummaryRow] = []
    for model in sorted(grouped):
        model_rows = grouped[model]
        total_pnl = sum(row.total_counterfactual_pnl_cents for row in model_rows)
        strict_count = sum(1 for row in model_rows if row.strict_gate_pass)
        summaries.append(
            MetaProbabilitySummaryRow(
                model=model,
                holdout_count=len(model_rows),
                total_counterfactual_pnl_cents=total_pnl,
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


def _feature_standardizer(rows: Sequence[tuple[float, ...]]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    width = len(rows[0])
    means: list[float] = []
    scales: list[float] = []
    for idx in range(width):
        values = [row[idx] for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        scale = math.sqrt(variance)
        if scale < 1e-9:
            scale = 1.0
        means.append(mean)
        scales.append(scale)
    return tuple(means), tuple(scales)


def _standardize(values: Sequence[float], means: Sequence[float], scales: Sequence[float]) -> tuple[float, ...]:
    return tuple((float(value) - mean) / scale for value, mean, scale in zip(values, means, scales))


def _regularized_loss(
    weights: Sequence[float],
    features: Sequence[tuple[float, ...]],
    labels: Sequence[int],
    l2: float,
) -> float:
    loss = 0.0
    for values, label in zip(features, labels):
        pred = _sigmoid(_dot(weights, (1.0, *values)))
        loss += _log_loss_one(pred, label)
    loss /= len(labels)
    loss += 0.5 * l2 * sum(weight * weight for weight in weights[1:]) / len(labels)
    return loss


def _logit(prob: float) -> float:
    p = _clamp01(prob)
    p = min(1.0 - 1e-4, max(1e-4, p))
    return math.log(p / (1.0 - p))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _log_loss_one(prob: float, label: int) -> float:
    p = min(1.0 - 1e-12, max(1e-12, prob))
    return -(label * math.log(p) + (1 - label) * math.log(1.0 - p))


def _dot(weights: Sequence[float], values: Sequence[float]) -> float:
    return sum(weight * value for weight, value in zip(weights, values))


def _mean(values: Iterable[float]) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _markdown(report: MetaProbabilityLOROReport) -> str:
    lines = [
        "# Meta Probability LORO Report",
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
