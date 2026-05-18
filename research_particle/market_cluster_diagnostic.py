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
class MarketClusterRow:
    run: str
    market_ticker: str
    candidate_count: int
    selected_count: int
    settlement_result_yes: bool
    total_counterfactual_pnl_cents: float
    avg_candidate_pnl_cents: float
    avg_predicted_ev_cents: float
    top_predicted_ev_cents: float
    yes_ev_share: float
    particle_p_yes: float
    brownian_p_yes: float
    market_p_yes: float
    current_calibrated_p_yes: float


@dataclass(frozen=True)
class MarketModelSummaryRow:
    model: str
    market_count: int
    brier: float
    log_loss: float
    mean_abs_calibration_error: float


@dataclass(frozen=True)
class MarketEVBucketRow:
    bucket: str
    market_count: int
    candidate_count: int
    selected_count: int
    avg_predicted_ev_cents: float
    total_counterfactual_pnl_cents: float
    avg_market_candidate_pnl_cents: float
    positive_market_count: int


@dataclass(frozen=True)
class MarketRunSummaryRow:
    run: str
    market_count: int
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    avg_market_candidate_pnl_cents: float
    best_model_by_brier: str
    ev_rank_correlation_sign: float
    top_ev_bucket_avg_market_candidate_pnl_cents: float


@dataclass(frozen=True)
class MarketClusterDiagnosticReport:
    source_reports: tuple[str, ...]
    run_count: int
    market_count: int
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    ev_rank_correlation_sign: float
    top_ev_bucket_avg_market_candidate_pnl_cents: float
    best_probability_model_by_market_brier: str
    best_probability_model_by_market_log_loss: str
    market_rows: tuple[MarketClusterRow, ...]
    model_summary_rows: tuple[MarketModelSummaryRow, ...]
    ev_bucket_rows: tuple[MarketEVBucketRow, ...]
    run_summary_rows: tuple[MarketRunSummaryRow, ...]
    conclusion: str


def build_market_cluster_diagnostic(
    report_paths: Sequence[Path],
    *,
    ev_bucket_count: int = 5,
) -> MarketClusterDiagnosticReport:
    if not report_paths:
        raise ValueError("at least one replay report is required")
    if ev_bucket_count < 1:
        raise ValueError("ev_bucket_count must be positive")

    run_decisions = [(_run_name(path), _load_decisions(path)) for path in report_paths]
    if any(not decisions for _, decisions in run_decisions):
        raise ValueError("each replay report must include decisions")
    market_rows = tuple(
        row
        for run, decisions in run_decisions
        for row in _market_rows_for_run(run, decisions)
    )
    if not market_rows:
        raise ValueError("no market rows could be built")
    model_summaries = tuple(_model_summaries(market_rows))
    ev_buckets = tuple(_ev_buckets(market_rows, ev_bucket_count))
    run_summaries = tuple(_run_summaries(market_rows, ev_bucket_count))
    best_brier = min(model_summaries, key=lambda row: (row.brier, row.log_loss)).model
    best_log_loss = min(model_summaries, key=lambda row: (row.log_loss, row.brier)).model
    ev_rank = pairwise_rank_correlation_sign(
        [row.avg_predicted_ev_cents for row in market_rows],
        [row.avg_candidate_pnl_cents for row in market_rows],
    )
    top_bucket = next((row for row in ev_buckets if row.bucket == "ev_rank_1_highest"), None)
    top_bucket_avg = (
        top_bucket.avg_market_candidate_pnl_cents
        if top_bucket is not None
        else 0.0
    )
    conclusion = (
        "Market-clustered probability and EV signals are directionally positive, but this report "
        "is an overfit guard only and does not replace all-candidate locked-OOS promotion gates."
        if ev_rank > 0.0 and top_bucket_avg > 0.0
        else "Market-clustered diagnostics do not support promotion: equal-market EV ranking or "
        "top-bucket profitability is weak."
    )
    return MarketClusterDiagnosticReport(
        source_reports=tuple(str(path) for path in report_paths),
        run_count=len(run_decisions),
        market_count=len(market_rows),
        candidate_count=sum(row.candidate_count for row in market_rows),
        selected_count=sum(row.selected_count for row in market_rows),
        total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in market_rows),
        ev_rank_correlation_sign=ev_rank,
        top_ev_bucket_avg_market_candidate_pnl_cents=top_bucket_avg,
        best_probability_model_by_market_brier=best_brier,
        best_probability_model_by_market_log_loss=best_log_loss,
        market_rows=market_rows,
        model_summary_rows=model_summaries,
        ev_bucket_rows=ev_buckets,
        run_summary_rows=run_summaries,
        conclusion=conclusion,
    )


def write_market_cluster_diagnostic(
    report: MarketClusterDiagnosticReport,
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
        description="Collapse replay decisions by market to diagnose label-cluster overfitting."
    )
    parser.add_argument("--report", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="market_cluster_diagnostic")
    parser.add_argument("--ev-bucket-count", default=5, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_market_cluster_diagnostic(args.report, ev_bucket_count=args.ev_bucket_count)
    json_path, md_path = write_market_cluster_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"market_count={report.market_count}")
    print(f"candidate_count={report.candidate_count}")
    print(f"selected_count={report.selected_count}")
    print(f"ev_rank_correlation_sign={report.ev_rank_correlation_sign:.6f}")
    print(f"top_ev_bucket_avg_market_candidate_pnl_cents={report.top_ev_bucket_avg_market_candidate_pnl_cents:.6f}")
    print(f"best_probability_model_by_market_brier={report.best_probability_model_by_market_brier}")
    print(f"best_probability_model_by_market_log_loss={report.best_probability_model_by_market_log_loss}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _market_rows_for_run(
    run: str,
    decisions: Sequence[Mapping[str, Any]],
) -> list[MarketClusterRow]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for decision in decisions:
        grouped.setdefault(str(decision.get("market_ticker") or "unknown"), []).append(decision)
    rows: list[MarketClusterRow] = []
    for market_ticker in sorted(grouped):
        market_decisions = grouped[market_ticker]
        selected = [row for row in market_decisions if row.get("selected")]
        labels = {bool(row.get("settlement_result_yes")) for row in market_decisions}
        if len(labels) != 1:
            raise ValueError(f"{run}:{market_ticker} has inconsistent settlement labels")
        total_pnl = _sum_pnl(market_decisions)
        rows.append(
            MarketClusterRow(
                run=run,
                market_ticker=market_ticker,
                candidate_count=len(market_decisions),
                selected_count=len(selected),
                settlement_result_yes=labels.pop(),
                total_counterfactual_pnl_cents=total_pnl,
                avg_candidate_pnl_cents=total_pnl / len(market_decisions),
                avg_predicted_ev_cents=_mean(_predicted_ev(row) for row in market_decisions),
                top_predicted_ev_cents=max(_predicted_ev(row) for row in market_decisions),
                yes_ev_share=_mean(1.0 if _ev_side(row) == "yes" else 0.0 for row in market_decisions),
                particle_p_yes=_mean(_prob(row, "particle_p_yes") for row in market_decisions),
                brownian_p_yes=_mean(_prob(row, "brownian_p_yes") for row in market_decisions),
                market_p_yes=_mean(_prob(row, "market_p_yes") for row in market_decisions),
                current_calibrated_p_yes=_mean(_prob(row, "current_calibrated_p_yes") for row in market_decisions),
            )
        )
    return rows


def _model_summaries(rows: Sequence[MarketClusterRow]) -> list[MarketModelSummaryRow]:
    labels = [1 if row.settlement_result_yes else 0 for row in rows]
    summaries: list[MarketModelSummaryRow] = []
    for model, field in MODEL_FIELDS.items():
        probs = [float(getattr(row, field)) for row in rows]
        summaries.append(
            MarketModelSummaryRow(
                model=model,
                market_count=len(rows),
                brier=brier_score(probs, labels),
                log_loss=log_loss(probs, labels),
                mean_abs_calibration_error=_mean_abs_calibration_error(probs, labels),
            )
        )
    return sorted(summaries, key=lambda row: (row.brier, row.log_loss))


def _ev_buckets(rows: Sequence[MarketClusterRow], bucket_count: int) -> list[MarketEVBucketRow]:
    ordered = sorted(rows, key=lambda row: row.avg_predicted_ev_cents, reverse=True)
    grouped: dict[int, list[MarketClusterRow]] = {idx: [] for idx in range(1, bucket_count + 1)}
    for rank, row in enumerate(ordered):
        bucket_idx = min(bucket_count, int((rank * bucket_count) / len(ordered)) + 1)
        grouped[bucket_idx].append(row)
    bucket_rows: list[MarketEVBucketRow] = []
    for idx in range(1, bucket_count + 1):
        bucket_markets = grouped[idx]
        if not bucket_markets:
            continue
        total_pnl = sum(row.total_counterfactual_pnl_cents for row in bucket_markets)
        bucket_rows.append(
            MarketEVBucketRow(
                bucket=_ev_bucket_name(idx, bucket_count),
                market_count=len(bucket_markets),
                candidate_count=sum(row.candidate_count for row in bucket_markets),
                selected_count=sum(row.selected_count for row in bucket_markets),
                avg_predicted_ev_cents=_mean(row.avg_predicted_ev_cents for row in bucket_markets),
                total_counterfactual_pnl_cents=total_pnl,
                avg_market_candidate_pnl_cents=_mean(row.avg_candidate_pnl_cents for row in bucket_markets),
                positive_market_count=sum(1 for row in bucket_markets if row.avg_candidate_pnl_cents > 0.0),
            )
        )
    return bucket_rows


def _run_summaries(rows: Sequence[MarketClusterRow], bucket_count: int) -> list[MarketRunSummaryRow]:
    grouped: dict[str, list[MarketClusterRow]] = {}
    for row in rows:
        grouped.setdefault(row.run, []).append(row)
    summaries: list[MarketRunSummaryRow] = []
    for run in sorted(grouped):
        run_rows = grouped[run]
        model_summary = _model_summaries(run_rows)
        ev_buckets = _ev_buckets(run_rows, min(bucket_count, len(run_rows)))
        top_bucket = next((row for row in ev_buckets if row.bucket == "ev_rank_1_highest"), None)
        summaries.append(
            MarketRunSummaryRow(
                run=run,
                market_count=len(run_rows),
                candidate_count=sum(row.candidate_count for row in run_rows),
                selected_count=sum(row.selected_count for row in run_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in run_rows),
                avg_market_candidate_pnl_cents=_mean(row.avg_candidate_pnl_cents for row in run_rows),
                best_model_by_brier=model_summary[0].model,
                ev_rank_correlation_sign=pairwise_rank_correlation_sign(
                    [row.avg_predicted_ev_cents for row in run_rows],
                    [row.avg_candidate_pnl_cents for row in run_rows],
                ),
                top_ev_bucket_avg_market_candidate_pnl_cents=(
                    top_bucket.avg_market_candidate_pnl_cents if top_bucket else 0.0
                ),
            )
        )
    return summaries


def _mean_abs_calibration_error(probs: Sequence[float], labels: Sequence[int]) -> float:
    return _mean(abs(prob - label) for prob, label in zip(probs, labels))


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


def _predicted_ev(row: Mapping[str, Any]) -> float:
    return max(float(row.get("ev_yes_cents") or 0.0), float(row.get("ev_no_cents") or 0.0))


def _ev_side(row: Mapping[str, Any]) -> str:
    return "yes" if float(row.get("ev_yes_cents") or 0.0) >= float(row.get("ev_no_cents") or 0.0) else "no"


def _prob(row: Mapping[str, Any], field: str) -> float:
    return min(1.0, max(0.0, float(row.get(field) or 0.0)))


def _sum_pnl(rows: Iterable[Mapping[str, Any]]) -> float:
    return sum(float(row.get("counterfactual_pnl_cents") or 0.0) for row in rows)


def _mean(values: Iterable[float | int]) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _markdown(report: MarketClusterDiagnosticReport) -> str:
    lines = [
        "# Market Cluster Diagnostic",
        "",
        f"- run_count: {report.run_count}",
        f"- market_count: {report.market_count}",
        f"- candidate_count: {report.candidate_count}",
        f"- selected_count: {report.selected_count}",
        f"- total_counterfactual_pnl_cents: {report.total_counterfactual_pnl_cents:.4f}",
        f"- ev_rank_correlation_sign: {report.ev_rank_correlation_sign:.6f}",
        f"- top_ev_bucket_avg_market_candidate_pnl_cents: {report.top_ev_bucket_avg_market_candidate_pnl_cents:.6f}",
        f"- best_probability_model_by_market_brier: {report.best_probability_model_by_market_brier}",
        f"- best_probability_model_by_market_log_loss: {report.best_probability_model_by_market_log_loss}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Model Summary",
        "",
        "| model | markets | brier | log_loss | mean_abs_cal_error |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report.model_summary_rows:
        lines.append(
            "| "
            f"{row.model} | "
            f"{row.market_count} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} | "
            f"{row.mean_abs_calibration_error:.6f} |"
        )
    lines.extend(
        [
            "",
            "## EV Buckets",
            "",
            "| bucket | markets | candidates | selected | avg_ev_cents | total_pnl_cents | avg_market_candidate_pnl | positive_markets |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.ev_bucket_rows:
        lines.append(
            "| "
            f"{row.bucket} | "
            f"{row.market_count} | "
            f"{row.candidate_count} | "
            f"{row.selected_count} | "
            f"{row.avg_predicted_ev_cents:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_market_candidate_pnl_cents:.4f} | "
            f"{row.positive_market_count}/{row.market_count} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | markets | candidates | selected | pnl_cents | avg_market_candidate_pnl | best_model_brier | ev_rank | top_bucket_avg_market_pnl |",
            "|---|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
    )
    for row in report.run_summary_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.market_count} | "
            f"{row.candidate_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_market_candidate_pnl_cents:.4f} | "
            f"{row.best_model_by_brier} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_avg_market_candidate_pnl_cents:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Markets",
            "",
            "| run | market | candidates | selected | result_yes | avg_particle | avg_market | avg_current | avg_ev | avg_pnl | yes_ev_share |",
            "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.market_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.market_ticker} | "
            f"{row.candidate_count} | "
            f"{row.selected_count} | "
            f"{row.settlement_result_yes} | "
            f"{row.particle_p_yes:.6f} | "
            f"{row.market_p_yes:.6f} | "
            f"{row.current_calibrated_p_yes:.6f} | "
            f"{row.avg_predicted_ev_cents:.4f} | "
            f"{row.avg_candidate_pnl_cents:.4f} | "
            f"{row.yes_ev_share:.4f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
