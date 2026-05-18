from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .validation import brier_score, log_loss, pairwise_rank_correlation_sign


MODEL_FIELDS = {
    "particle": "particle_p_yes",
    "brownian": "brownian_p_yes",
    "market": "market_p_yes",
    "current_calibrated": "current_calibrated_p_yes",
}


@dataclass(frozen=True)
class EVBucketRunRow:
    run: str
    bucket: str
    candidate_count: int
    selected_count: int
    win_count: int
    win_rate: float
    avg_predicted_ev_cents: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents: float
    yes_side_count: int
    no_side_count: int
    against_market_current_consensus_count: int


@dataclass(frozen=True)
class EVBucketSummaryRow:
    bucket: str
    run_count: int
    positive_run_count: int
    nonzero_run_count: int
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    min_run_pnl_cents: float
    avg_counterfactual_pnl_cents: float
    stable_positive: bool


@dataclass(frozen=True)
class ProbabilityBucketRunRow:
    run: str
    model: str
    bucket: str
    count: int
    avg_predicted_p_yes: float
    empirical_yes_rate: float
    calibration_error: float
    brier: float
    log_loss: float


@dataclass(frozen=True)
class ProbabilityModelSummaryRow:
    model: str
    count: int
    brier: float
    log_loss: float
    mean_abs_calibration_error: float
    high_confidence_count: int
    high_confidence_mean_abs_calibration_error: float


@dataclass(frozen=True)
class EVRankCalibrationDiagnosticReport:
    source_reports: tuple[str, ...]
    run_count: int
    candidate_count: int
    selected_count: int
    ev_rank_correlation_sign: float
    ev_bucket_run_rows: tuple[EVBucketRunRow, ...]
    ev_bucket_summary_rows: tuple[EVBucketSummaryRow, ...]
    probability_bucket_run_rows: tuple[ProbabilityBucketRunRow, ...]
    probability_model_summary_rows: tuple[ProbabilityModelSummaryRow, ...]
    top_ev_bucket_stable_positive: bool
    best_probability_model_by_brier: str
    best_probability_model_by_log_loss: str
    conclusion: str


def build_ev_rank_calibration_diagnostic(
    report_paths: Sequence[Path],
    *,
    ev_bucket_count: int = 5,
    probability_bucket_count: int = 10,
) -> EVRankCalibrationDiagnosticReport:
    if not report_paths:
        raise ValueError("at least one replay report is required")
    if ev_bucket_count < 1:
        raise ValueError("ev_bucket_count must be positive")
    if probability_bucket_count < 1:
        raise ValueError("probability_bucket_count must be positive")

    run_decisions = [(_run_name(path), _load_decisions(path)) for path in report_paths]
    if any(not decisions for _, decisions in run_decisions):
        raise ValueError("each replay report must include decisions")

    all_decisions = [decision for _, decisions in run_decisions for decision in decisions]
    predicted_evs = [_predicted_ev(decision) for decision in all_decisions]
    realized_pnls = [_pnl(decision) for decision in all_decisions]

    ev_bucket_run_rows = tuple(
        row
        for run, decisions in run_decisions
        for row in _build_ev_bucket_rows(run, decisions, ev_bucket_count)
    )
    ev_bucket_summary_rows = tuple(
        _summarize_ev_buckets(ev_bucket_run_rows, run_count=len(run_decisions))
    )
    probability_bucket_run_rows = tuple(
        row
        for run, decisions in run_decisions
        for row in _build_probability_bucket_rows(run, decisions, probability_bucket_count)
    )
    probability_model_summary_rows = tuple(
        _build_probability_model_summaries(all_decisions, probability_bucket_run_rows)
    )
    top_bucket = "ev_rank_1_highest"
    top_ev_stable = any(
        row.bucket == top_bucket and row.stable_positive
        for row in ev_bucket_summary_rows
    )
    best_brier = min(probability_model_summary_rows, key=lambda row: row.brier).model
    best_log_loss = min(probability_model_summary_rows, key=lambda row: row.log_loss).model
    conclusion = (
        "Top predicted EV bucket is positive in every supplied locked run; treat this as "
        "diagnostic support only, then predeclare a fresh OOS rule before promotion."
        if top_ev_stable
        else "Top predicted EV bucket is not positive in every supplied locked run; EV ranking "
        "does not yet satisfy the particle-system promotion gate."
    )

    return EVRankCalibrationDiagnosticReport(
        source_reports=tuple(str(path) for path in report_paths),
        run_count=len(run_decisions),
        candidate_count=len(all_decisions),
        selected_count=sum(1 for decision in all_decisions if decision.get("selected")),
        ev_rank_correlation_sign=pairwise_rank_correlation_sign(predicted_evs, realized_pnls),
        ev_bucket_run_rows=ev_bucket_run_rows,
        ev_bucket_summary_rows=ev_bucket_summary_rows,
        probability_bucket_run_rows=probability_bucket_run_rows,
        probability_model_summary_rows=probability_model_summary_rows,
        top_ev_bucket_stable_positive=top_ev_stable,
        best_probability_model_by_brier=best_brier,
        best_probability_model_by_log_loss=best_log_loss,
        conclusion=conclusion,
    )


def write_ev_rank_calibration_diagnostic(
    report: EVRankCalibrationDiagnosticReport,
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
        description="Diagnose EV-rank and probability-calibration stability from locked replay reports."
    )
    parser.add_argument("--report", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="ev_rank_calibration_diagnostic")
    parser.add_argument("--ev-bucket-count", default=5, type=int)
    parser.add_argument("--probability-bucket-count", default=10, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_ev_rank_calibration_diagnostic(
        args.report,
        ev_bucket_count=args.ev_bucket_count,
        probability_bucket_count=args.probability_bucket_count,
    )
    json_path, md_path = write_ev_rank_calibration_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"candidate_count={report.candidate_count}")
    print(f"selected_count={report.selected_count}")
    print(f"ev_rank_correlation_sign={report.ev_rank_correlation_sign:.6f}")
    print(f"top_ev_bucket_stable_positive={report.top_ev_bucket_stable_positive}")
    print(f"best_probability_model_by_brier={report.best_probability_model_by_brier}")
    print(f"best_probability_model_by_log_loss={report.best_probability_model_by_log_loss}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _build_ev_bucket_rows(
    run: str,
    decisions: Sequence[Mapping[str, Any]],
    bucket_count: int,
) -> list[EVBucketRunRow]:
    indexed = list(enumerate(decisions))
    indexed.sort(key=lambda item: _predicted_ev(item[1]), reverse=True)
    grouped: dict[int, list[Mapping[str, Any]]] = {idx: [] for idx in range(1, bucket_count + 1)}
    total = len(indexed)
    for rank, (_, decision) in enumerate(indexed):
        bucket_idx = min(bucket_count, int((rank * bucket_count) / total) + 1)
        grouped[bucket_idx].append(decision)

    rows: list[EVBucketRunRow] = []
    for bucket_idx in range(1, bucket_count + 1):
        bucket_rows = grouped[bucket_idx]
        rows.append(_ev_bucket_row(run, _ev_bucket_name(bucket_idx, bucket_count), bucket_rows))
    return rows


def _ev_bucket_row(
    run: str,
    bucket: str,
    rows: Sequence[Mapping[str, Any]],
) -> EVBucketRunRow:
    selected = [row for row in rows if row.get("selected")]
    wins = sum(1 for row in selected if row.get("won"))
    pnl = _sum_pnl(rows)
    yes_count = sum(1 for row in rows if _ev_side(row) == "yes")
    no_count = len(rows) - yes_count
    return EVBucketRunRow(
        run=run,
        bucket=bucket,
        candidate_count=len(rows),
        selected_count=len(selected),
        win_count=wins,
        win_rate=(wins / len(selected) if selected else 0.0),
        avg_predicted_ev_cents=_mean(_predicted_ev(row) for row in rows),
        total_counterfactual_pnl_cents=pnl,
        avg_counterfactual_pnl_cents=(pnl / len(rows) if rows else 0.0),
        yes_side_count=yes_count,
        no_side_count=no_count,
        against_market_current_consensus_count=sum(
            1 for row in rows if _against_market_current_consensus(row)
        ),
    )


def _summarize_ev_buckets(
    rows: Sequence[EVBucketRunRow],
    *,
    run_count: int,
) -> list[EVBucketSummaryRow]:
    grouped: dict[str, list[EVBucketRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.bucket, []).append(row)
    summaries: list[EVBucketSummaryRow] = []
    for bucket in sorted(grouped):
        bucket_rows = grouped[bucket]
        total_pnl = sum(row.total_counterfactual_pnl_cents for row in bucket_rows)
        candidates = sum(row.candidate_count for row in bucket_rows)
        positive = sum(1 for row in bucket_rows if row.total_counterfactual_pnl_cents > 0.0)
        nonzero = sum(1 for row in bucket_rows if row.candidate_count > 0)
        summaries.append(
            EVBucketSummaryRow(
                bucket=bucket,
                run_count=len(bucket_rows),
                positive_run_count=positive,
                nonzero_run_count=nonzero,
                candidate_count=candidates,
                selected_count=sum(row.selected_count for row in bucket_rows),
                total_counterfactual_pnl_cents=total_pnl,
                min_run_pnl_cents=min(
                    (row.total_counterfactual_pnl_cents for row in bucket_rows),
                    default=0.0,
                ),
                avg_counterfactual_pnl_cents=(total_pnl / candidates if candidates else 0.0),
                stable_positive=(
                    len(bucket_rows) == run_count
                    and nonzero == run_count
                    and positive == run_count
                ),
            )
        )
    return summaries


def _build_probability_bucket_rows(
    run: str,
    decisions: Sequence[Mapping[str, Any]],
    bucket_count: int,
) -> list[ProbabilityBucketRunRow]:
    rows: list[ProbabilityBucketRunRow] = []
    for model, field in MODEL_FIELDS.items():
        grouped: dict[int, list[Mapping[str, Any]]] = {idx: [] for idx in range(bucket_count)}
        for decision in decisions:
            prob = _prob(decision, field)
            bucket_idx = min(bucket_count - 1, int(math.floor(prob * bucket_count)))
            grouped[bucket_idx].append(decision)
        for bucket_idx in range(bucket_count):
            bucket_rows = grouped[bucket_idx]
            if not bucket_rows:
                continue
            labels = [_label(row) for row in bucket_rows]
            probs = [_prob(row, field) for row in bucket_rows]
            avg_pred = _mean(probs)
            empirical = _mean(labels)
            rows.append(
                ProbabilityBucketRunRow(
                    run=run,
                    model=model,
                    bucket=_probability_bucket_name(bucket_idx, bucket_count),
                    count=len(bucket_rows),
                    avg_predicted_p_yes=avg_pred,
                    empirical_yes_rate=empirical,
                    calibration_error=empirical - avg_pred,
                    brier=brier_score(probs, labels),
                    log_loss=log_loss(probs, labels),
                )
            )
    return rows


def _build_probability_model_summaries(
    decisions: Sequence[Mapping[str, Any]],
    bucket_rows: Sequence[ProbabilityBucketRunRow],
) -> list[ProbabilityModelSummaryRow]:
    summaries: list[ProbabilityModelSummaryRow] = []
    labels = [_label(row) for row in decisions]
    for model, field in MODEL_FIELDS.items():
        probs = [_prob(row, field) for row in decisions]
        model_buckets = [row for row in bucket_rows if row.model == model]
        total = sum(row.count for row in model_buckets)
        weighted_abs = sum(row.count * abs(row.calibration_error) for row in model_buckets)
        high_buckets = [
            row
            for row in model_buckets
            if row.avg_predicted_p_yes <= 0.20 or row.avg_predicted_p_yes >= 0.80
        ]
        high_total = sum(row.count for row in high_buckets)
        high_weighted_abs = sum(row.count * abs(row.calibration_error) for row in high_buckets)
        summaries.append(
            ProbabilityModelSummaryRow(
                model=model,
                count=len(decisions),
                brier=brier_score(probs, labels),
                log_loss=log_loss(probs, labels),
                mean_abs_calibration_error=(weighted_abs / total if total else 0.0),
                high_confidence_count=high_total,
                high_confidence_mean_abs_calibration_error=(
                    high_weighted_abs / high_total if high_total else 0.0
                ),
            )
        )
    return sorted(summaries, key=lambda row: (row.brier, row.log_loss))


def _load_decisions(path: Path) -> list[Mapping[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError(f"{path} does not contain a decisions list")
    return [row for row in decisions if isinstance(row, Mapping)]


def _run_name(path: Path) -> str:
    try:
        return path.parent.parent.name
    except Exception:
        return path.stem


def _ev_bucket_name(bucket_idx: int, bucket_count: int) -> str:
    if bucket_idx == 1:
        return "ev_rank_1_highest"
    if bucket_idx == bucket_count:
        return f"ev_rank_{bucket_idx}_lowest"
    return f"ev_rank_{bucket_idx}"


def _probability_bucket_name(bucket_idx: int, bucket_count: int) -> str:
    lower = bucket_idx / bucket_count
    upper = (bucket_idx + 1) / bucket_count
    if bucket_idx == bucket_count - 1:
        return f"{lower:.1f}_1.0"
    return f"{lower:.1f}_{upper:.1f}"


def _predicted_ev(row: Mapping[str, Any]) -> float:
    return max(float(row.get("ev_yes_cents") or 0.0), float(row.get("ev_no_cents") or 0.0))


def _ev_side(row: Mapping[str, Any]) -> str:
    return "yes" if float(row.get("ev_yes_cents") or 0.0) >= float(row.get("ev_no_cents") or 0.0) else "no"


def _side_from_probability(row: Mapping[str, Any], field: str) -> str:
    return "yes" if _prob(row, field) >= 0.5 else "no"


def _against_market_current_consensus(row: Mapping[str, Any]) -> bool:
    market_side = _side_from_probability(row, "market_p_yes")
    current_side = _side_from_probability(row, "current_calibrated_p_yes")
    return market_side == current_side and _ev_side(row) != market_side


def _prob(row: Mapping[str, Any], field: str) -> float:
    return min(1.0, max(0.0, float(row.get(field) or 0.0)))


def _label(row: Mapping[str, Any]) -> int:
    return 1 if bool(row.get("settlement_result_yes")) else 0


def _pnl(row: Mapping[str, Any]) -> float:
    return float(row.get("counterfactual_pnl_cents") or 0.0)


def _sum_pnl(rows: Iterable[Mapping[str, Any]]) -> float:
    return sum(_pnl(row) for row in rows)


def _mean(values: Iterable[float | int]) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _markdown(report: EVRankCalibrationDiagnosticReport) -> str:
    lines = [
        "# EV Rank / Calibration Diagnostic",
        "",
        f"- run_count: {report.run_count}",
        f"- candidate_count: {report.candidate_count}",
        f"- selected_count: {report.selected_count}",
        f"- ev_rank_correlation_sign: {report.ev_rank_correlation_sign:.6f}",
        f"- top_ev_bucket_stable_positive: {report.top_ev_bucket_stable_positive}",
        f"- best_probability_model_by_brier: {report.best_probability_model_by_brier}",
        f"- best_probability_model_by_log_loss: {report.best_probability_model_by_log_loss}",
        f"- conclusion: {report.conclusion}",
        "",
        "## EV Bucket Stability",
        "",
        "| bucket | positive_runs | candidates | selected | total_pnl_cents | min_run_pnl_cents | avg_pnl_cents | stable_positive |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.ev_bucket_summary_rows:
        lines.append(
            "| "
            f"{row.bucket} | "
            f"{row.positive_run_count}/{row.run_count} | "
            f"{row.candidate_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.min_run_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents:.4f} | "
            f"{row.stable_positive} |"
        )
    lines.extend(
        [
            "",
            "## Probability Model Summary",
            "",
            "| model | count | brier | log_loss | mean_abs_cal_error | high_conf_count | high_conf_abs_cal_error |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.probability_model_summary_rows:
        lines.append(
            "| "
            f"{row.model} | "
            f"{row.count} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} | "
            f"{row.mean_abs_calibration_error:.6f} | "
            f"{row.high_confidence_count} | "
            f"{row.high_confidence_mean_abs_calibration_error:.6f} |"
        )
    lines.extend(
        [
            "",
            "## EV Bucket By Run",
            "",
            "| run | bucket | candidates | selected | win_rate | avg_ev_cents | pnl_cents | avg_pnl_cents | yes | no | against_consensus |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.ev_bucket_run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.bucket} | "
            f"{row.candidate_count} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.4f} | "
            f"{row.avg_predicted_ev_cents:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents:.4f} | "
            f"{row.yes_side_count} | "
            f"{row.no_side_count} | "
            f"{row.against_market_current_consensus_count} |"
        )
    lines.extend(
        [
            "",
            "## Probability Buckets",
            "",
            "| run | model | bucket | count | avg_pred_p_yes | empirical_yes_rate | calibration_error | brier | log_loss |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.probability_bucket_run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.model} | "
            f"{row.bucket} | "
            f"{row.count} | "
            f"{row.avg_predicted_p_yes:.6f} | "
            f"{row.empirical_yes_rate:.6f} | "
            f"{row.calibration_error:.6f} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
