from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .validation import brier_score, log_loss


PROBABILITY_FIELDS = (
    "particle_p_yes",
    "brownian_p_yes",
    "market_p_yes",
    "current_calibrated_p_yes",
)


@dataclass(frozen=True)
class ModelDiagnostics:
    brier: float
    log_loss: float
    mean_p_yes: float
    mean_abs_error: float


@dataclass(frozen=True)
class SideDiagnostics:
    selected_count: int
    win_count: int
    win_rate: float
    total_pnl_cents: float


@dataclass(frozen=True)
class MarketDiagnostics:
    market_ticker: str
    candidate_count: int
    selected_count: int
    settlement_result_yes: bool
    total_counterfactual_pnl_cents: float
    mean_particle_minus_market: float
    mean_particle_minus_current: float
    models: dict[str, ModelDiagnostics]
    sides: dict[str, SideDiagnostics]


@dataclass(frozen=True)
class BucketDiagnostics:
    bucket: str
    candidate_count: int
    selected_count: int
    avg_predicted_ev_cents: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents: float
    win_rate: float


@dataclass(frozen=True)
class ReplayDiagnosticsReport:
    source_report: str
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    particle_brier_minus_market_brier: float
    particle_brier_minus_current_brier: float
    particle_logloss_minus_market_logloss: float
    particle_logloss_minus_current_logloss: float
    selected_yes_count: int
    selected_no_count: int
    selected_yes_pnl_cents: float
    selected_no_pnl_cents: float
    markets: tuple[MarketDiagnostics, ...]
    ev_buckets: tuple[BucketDiagnostics, ...]
    worst_decisions: tuple[dict[str, Any], ...]


def build_diagnostics(report_path: Path) -> ReplayDiagnosticsReport:
    payload = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("report JSON must include non-empty decisions")
    selected = [row for row in decisions if row.get("selected")]
    selected_yes = [row for row in selected if row.get("side") == "yes"]
    selected_no = [row for row in selected if row.get("side") == "no"]
    markets = tuple(
        _market_diagnostics(market, rows)
        for market, rows in _group_by_market(decisions).items()
    )
    ev_buckets = tuple(_ev_buckets(decisions, bucket_count=5))
    worst = tuple(
        _compact_decision(row)
        for row in sorted(
            selected,
            key=lambda row: float(row.get("counterfactual_pnl_cents") or 0.0),
        )[:10]
    )
    return ReplayDiagnosticsReport(
        source_report=str(report_path),
        candidate_count=int(payload.get("candidate_count") or len(decisions)),
        selected_count=int(payload.get("selected_count") or len(selected)),
        total_counterfactual_pnl_cents=float(payload.get("total_counterfactual_pnl_cents") or 0.0),
        particle_brier_minus_market_brier=_score_delta(payload, "particle", "market", "brier"),
        particle_brier_minus_current_brier=_score_delta(payload, "particle", "current_calibrated", "brier"),
        particle_logloss_minus_market_logloss=_score_delta(payload, "particle", "market", "log_loss"),
        particle_logloss_minus_current_logloss=_score_delta(payload, "particle", "current_calibrated", "log_loss"),
        selected_yes_count=len(selected_yes),
        selected_no_count=len(selected_no),
        selected_yes_pnl_cents=_sum_pnl(selected_yes),
        selected_no_pnl_cents=_sum_pnl(selected_no),
        markets=markets,
        ev_buckets=ev_buckets,
        worst_decisions=worst,
    )


def write_diagnostics(
    report: ReplayDiagnosticsReport,
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
        description="Summarize real replay failure modes by market, side, baseline gap, and EV bucket."
    )
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="replay_diagnostics")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_diagnostics(args.report)
    json_path, md_path = write_diagnostics(report, args.output_dir, args.stem)
    print(f"candidate_count={report.candidate_count}")
    print(f"selected_count={report.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
    print(f"particle_brier_minus_market_brier={report.particle_brier_minus_market_brier:.6f}")
    print(f"particle_brier_minus_current_brier={report.particle_brier_minus_current_brier:.6f}")
    print(f"selected_yes_pnl_cents={report.selected_yes_pnl_cents:.4f}")
    print(f"selected_no_pnl_cents={report.selected_no_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _market_diagnostics(market: str, rows: list[dict[str, Any]]) -> MarketDiagnostics:
    selected = [row for row in rows if row.get("selected")]
    label = bool(rows[0].get("settlement_result_yes"))
    return MarketDiagnostics(
        market_ticker=market,
        candidate_count=len(rows),
        selected_count=len(selected),
        settlement_result_yes=label,
        total_counterfactual_pnl_cents=_sum_pnl(selected),
        mean_particle_minus_market=_mean(
            float(row["particle_p_yes"]) - float(row["market_p_yes"]) for row in rows
        ),
        mean_particle_minus_current=_mean(
            float(row["particle_p_yes"]) - float(row["current_calibrated_p_yes"]) for row in rows
        ),
        models={
            name: _model_diagnostics(rows, name)
            for name in PROBABILITY_FIELDS
        },
        sides={
            "yes": _side_diagnostics(row for row in selected if row.get("side") == "yes"),
            "no": _side_diagnostics(row for row in selected if row.get("side") == "no"),
        },
    )


def _model_diagnostics(rows: list[dict[str, Any]], field: str) -> ModelDiagnostics:
    probs = [float(row[field]) for row in rows]
    labels = [1 if row.get("settlement_result_yes") else 0 for row in rows]
    return ModelDiagnostics(
        brier=brier_score(probs, labels),
        log_loss=log_loss(probs, labels),
        mean_p_yes=_mean(probs),
        mean_abs_error=_mean(abs(p - y) for p, y in zip(probs, labels)),
    )


def _side_diagnostics(rows_iter: Iterable[dict[str, Any]]) -> SideDiagnostics:
    rows = list(rows_iter)
    wins = sum(1 for row in rows if row.get("won"))
    return SideDiagnostics(
        selected_count=len(rows),
        win_count=wins,
        win_rate=(wins / len(rows) if rows else 0.0),
        total_pnl_cents=_sum_pnl(rows),
    )


def _ev_buckets(decisions: list[dict[str, Any]], *, bucket_count: int) -> list[BucketDiagnostics]:
    rows = sorted(
        decisions,
        key=lambda row: max(float(row.get("ev_yes_cents") or 0.0), float(row.get("ev_no_cents") or 0.0)),
        reverse=True,
    )
    buckets: list[BucketDiagnostics] = []
    for idx in range(bucket_count):
        start = idx * len(rows) // bucket_count
        end = (idx + 1) * len(rows) // bucket_count
        chunk = rows[start:end]
        selected = [row for row in chunk if row.get("selected")]
        wins = sum(1 for row in selected if row.get("won"))
        pnl = _sum_pnl(selected)
        buckets.append(
            BucketDiagnostics(
                bucket=f"ev_rank_{idx + 1}_of_{bucket_count}",
                candidate_count=len(chunk),
                selected_count=len(selected),
                avg_predicted_ev_cents=_mean(
                    max(float(row.get("ev_yes_cents") or 0.0), float(row.get("ev_no_cents") or 0.0))
                    for row in chunk
                ),
                total_counterfactual_pnl_cents=pnl,
                avg_counterfactual_pnl_cents=(pnl / len(selected) if selected else 0.0),
                win_rate=(wins / len(selected) if selected else 0.0),
            )
        )
    return buckets


def _group_by_market(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("market_ticker") or ""), []).append(row)
    return grouped


def _score_delta(payload: dict[str, Any], lhs: str, rhs: str, metric: str) -> float:
    return float(payload[lhs][metric]) - float(payload[rhs][metric])


def _sum_pnl(rows: Iterable[dict[str, Any]]) -> float:
    return sum(float(row.get("counterfactual_pnl_cents") or 0.0) for row in rows)


def _mean(values: Iterable[float]) -> float:
    rows = list(values)
    return sum(rows) / len(rows) if rows else 0.0


def _compact_decision(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market_ticker": row.get("market_ticker"),
        "decision_ts_utc": row.get("decision_ts_utc"),
        "side": row.get("side"),
        "won": row.get("won"),
        "counterfactual_pnl_cents": row.get("counterfactual_pnl_cents"),
        "particle_p_yes": row.get("particle_p_yes"),
        "market_p_yes": row.get("market_p_yes"),
        "current_calibrated_p_yes": row.get("current_calibrated_p_yes"),
        "ev_yes_cents": row.get("ev_yes_cents"),
        "ev_no_cents": row.get("ev_no_cents"),
        "settlement_result_yes": row.get("settlement_result_yes"),
    }


def _markdown(report: ReplayDiagnosticsReport) -> str:
    lines = [
        "# Replay Diagnostics",
        "",
        f"- source_report: `{report.source_report}`",
        f"- candidate_count: {report.candidate_count}",
        f"- selected_count: {report.selected_count}",
        f"- total_counterfactual_pnl_cents: {report.total_counterfactual_pnl_cents:.4f}",
        f"- particle_brier_minus_market_brier: {report.particle_brier_minus_market_brier:.6f}",
        f"- particle_brier_minus_current_brier: {report.particle_brier_minus_current_brier:.6f}",
        f"- particle_logloss_minus_market_logloss: {report.particle_logloss_minus_market_logloss:.6f}",
        f"- particle_logloss_minus_current_logloss: {report.particle_logloss_minus_current_logloss:.6f}",
        f"- selected_yes_count: {report.selected_yes_count}",
        f"- selected_yes_pnl_cents: {report.selected_yes_pnl_cents:.4f}",
        f"- selected_no_count: {report.selected_no_count}",
        f"- selected_no_pnl_cents: {report.selected_no_pnl_cents:.4f}",
        "",
        "## Markets",
        "",
    ]
    for market in report.markets:
        lines.extend(
            [
                f"### {market.market_ticker}",
                "",
                f"- candidate_count: {market.candidate_count}",
                f"- selected_count: {market.selected_count}",
                f"- settlement_result_yes: {market.settlement_result_yes}",
                f"- total_counterfactual_pnl_cents: {market.total_counterfactual_pnl_cents:.4f}",
                f"- mean_particle_minus_market: {market.mean_particle_minus_market:.6f}",
                f"- mean_particle_minus_current: {market.mean_particle_minus_current:.6f}",
                f"- yes_selected: {market.sides['yes'].selected_count}, pnl={market.sides['yes'].total_pnl_cents:.4f}, win_rate={market.sides['yes'].win_rate:.4f}",
                f"- no_selected: {market.sides['no'].selected_count}, pnl={market.sides['no'].total_pnl_cents:.4f}, win_rate={market.sides['no'].win_rate:.4f}",
                "",
            ]
        )
    lines.extend(["## EV Buckets", ""])
    for bucket in report.ev_buckets:
        lines.append(
            "- {bucket}: candidates={candidate_count}, selected={selected_count}, "
            "avg_pred_ev={avg_predicted_ev_cents:.4f}, pnl={total_counterfactual_pnl_cents:.4f}, "
            "avg_pnl={avg_counterfactual_pnl_cents:.4f}, win_rate={win_rate:.4f}".format(
                **asdict(bucket)
            )
        )
    lines.extend(["", "## Worst Decisions", ""])
    for row in report.worst_decisions:
        lines.append(
            "- {market_ticker} {decision_ts_utc} side={side} pnl={counterfactual_pnl_cents} "
            "particle={particle_p_yes} market={market_p_yes} current={current_calibrated_p_yes}".format(**row)
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
