from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class LOROHoldoutRow:
    selector: str
    holdout_run: str
    source: str
    name: str
    train_run_count: int
    train_total_counterfactual_pnl_cents: float
    train_mean_brier: float
    train_positive_pnl_run_count: int
    train_beats_current_run_count: int
    holdout_total_counterfactual_pnl_cents: float
    holdout_brier: float
    holdout_log_loss: float
    holdout_beats_brownian: bool
    holdout_beats_market: bool
    holdout_beats_current_calibrated: bool
    holdout_ev_rank_positive: bool
    holdout_top_bucket_positive: bool
    holdout_passes_strict_gates: bool


@dataclass(frozen=True)
class LOROSelectorSummaryRow:
    selector: str
    holdout_count: int
    total_holdout_pnl_cents: float
    mean_holdout_brier: float
    positive_pnl_holdout_count: int
    beats_brownian_holdout_count: int
    beats_market_holdout_count: int
    beats_current_holdout_count: int
    positive_ev_rank_holdout_count: int
    positive_top_bucket_holdout_count: int
    strict_gate_holdout_count: int
    strict_all_holdouts: bool


@dataclass(frozen=True)
class VariantLOROSelectionDiagnosticReport:
    source_stability_report: str
    run_count: int
    variant_row_count: int
    holdout_rows: tuple[LOROHoldoutRow, ...]
    selector_summary_rows: tuple[LOROSelectorSummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_variant_loro_selection_diagnostic(stability_report_path: Path) -> VariantLOROSelectionDiagnosticReport:
    payload = json.loads(stability_report_path.read_text(encoding="utf-8", errors="replace"))
    variant_rows = [
        row
        for row in payload.get("variant_rows", [])
        if isinstance(row, Mapping) and row.get("run_name") and row.get("source") and row.get("name")
    ]
    if not variant_rows:
        raise ValueError("stability report must include variant_rows")
    runs = sorted({str(row["run_name"]) for row in variant_rows})
    holdout_rows: list[LOROHoldoutRow] = []
    for holdout_run in runs:
        train_rows = [row for row in variant_rows if str(row["run_name"]) != holdout_run]
        holdout_by_key = {
            _variant_key(row): row
            for row in variant_rows
            if str(row["run_name"]) == holdout_run
        }
        train_groups = _group_by_variant(train_rows)
        selectable = [
            _variant_train_summary(key, rows)
            for key, rows in train_groups.items()
            if key in holdout_by_key
        ]
        if not selectable:
            continue
        for selector, summary in _select_variants(selectable).items():
            holdout = holdout_by_key[summary["key"]]
            holdout_rows.append(_holdout_row(selector, holdout_run, summary, holdout))
    selector_summary_rows = tuple(_summarize_selectors(holdout_rows))
    promotion_safe = any(row.strict_all_holdouts for row in selector_summary_rows)
    conclusion = (
        "At least one leave-one-run-out selector passes all strict holdout gates; still predeclare "
        "a fresh locked OOS run before any promotion."
        if promotion_safe
        else "No leave-one-run-out selector passes the strict holdout gates across locked runs."
    )
    return VariantLOROSelectionDiagnosticReport(
        source_stability_report=str(stability_report_path),
        run_count=len(runs),
        variant_row_count=len(variant_rows),
        holdout_rows=tuple(holdout_rows),
        selector_summary_rows=selector_summary_rows,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_variant_loro_selection_diagnostic(
    report: VariantLOROSelectionDiagnosticReport,
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
        description="Run leave-one-run-out selection diagnostics over a locked OOS stability report."
    )
    parser.add_argument("--stability-report", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="variant_loro_selection_diagnostic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_variant_loro_selection_diagnostic(args.stability_report)
    json_path, md_path = write_variant_loro_selection_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"variant_row_count={report.variant_row_count}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _select_variants(summaries: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        "train_best_total_pnl": max(
            summaries,
            key=lambda row: (
                row["train_total_counterfactual_pnl_cents"],
                row["train_positive_pnl_run_count"],
                -row["train_mean_brier"],
            ),
        ),
        "train_best_mean_brier": min(
            summaries,
            key=lambda row: (
                row["train_mean_brier"],
                row["train_mean_log_loss"],
                -row["train_total_counterfactual_pnl_cents"],
            ),
        ),
        "train_best_gate_score": max(
            summaries,
            key=lambda row: (
                row["train_beats_current_run_count"],
                row["train_beats_market_run_count"],
                row["train_beats_brownian_run_count"],
                row["train_positive_top_bucket_run_count"],
                row["train_positive_ev_rank_run_count"],
                row["train_positive_pnl_run_count"],
                row["train_total_counterfactual_pnl_cents"],
            ),
        ),
    }


def _variant_train_summary(key: tuple[str, str], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    train_run_count = len(rows)
    return {
        "key": key,
        "source": key[0],
        "name": key[1],
        "train_run_count": train_run_count,
        "train_total_counterfactual_pnl_cents": sum(_float(row, "total_counterfactual_pnl_cents") for row in rows),
        "train_mean_brier": _mean(_float(row, "brier") for row in rows),
        "train_mean_log_loss": _mean(_float(row, "log_loss") for row in rows),
        "train_positive_pnl_run_count": sum(1 for row in rows if _float(row, "total_counterfactual_pnl_cents") > 0.0),
        "train_positive_ev_rank_run_count": sum(1 for row in rows if _float(row, "ev_rank_correlation_sign") > 0.0),
        "train_positive_top_bucket_run_count": sum(1 for row in rows if _float(row, "top_ev_bucket_pnl_cents") > 0.0),
        "train_beats_brownian_run_count": sum(1 for row in rows if bool(row.get("beats_brownian"))),
        "train_beats_market_run_count": sum(1 for row in rows if bool(row.get("beats_market"))),
        "train_beats_current_run_count": sum(1 for row in rows if bool(row.get("beats_current_calibrated"))),
    }


def _holdout_row(
    selector: str,
    holdout_run: str,
    train_summary: Mapping[str, Any],
    holdout: Mapping[str, Any],
) -> LOROHoldoutRow:
    pnl = _float(holdout, "total_counterfactual_pnl_cents")
    ev_rank_positive = _float(holdout, "ev_rank_correlation_sign") > 0.0
    top_bucket_positive = _float(holdout, "top_ev_bucket_pnl_cents") > 0.0
    beats_brownian = bool(holdout.get("beats_brownian"))
    beats_market = bool(holdout.get("beats_market"))
    beats_current = bool(holdout.get("beats_current_calibrated"))
    return LOROHoldoutRow(
        selector=selector,
        holdout_run=holdout_run,
        source=str(train_summary["source"]),
        name=str(train_summary["name"]),
        train_run_count=int(train_summary["train_run_count"]),
        train_total_counterfactual_pnl_cents=float(train_summary["train_total_counterfactual_pnl_cents"]),
        train_mean_brier=float(train_summary["train_mean_brier"]),
        train_positive_pnl_run_count=int(train_summary["train_positive_pnl_run_count"]),
        train_beats_current_run_count=int(train_summary["train_beats_current_run_count"]),
        holdout_total_counterfactual_pnl_cents=pnl,
        holdout_brier=_float(holdout, "brier"),
        holdout_log_loss=_float(holdout, "log_loss"),
        holdout_beats_brownian=beats_brownian,
        holdout_beats_market=beats_market,
        holdout_beats_current_calibrated=beats_current,
        holdout_ev_rank_positive=ev_rank_positive,
        holdout_top_bucket_positive=top_bucket_positive,
        holdout_passes_strict_gates=(
            pnl > 0.0
            and ev_rank_positive
            and top_bucket_positive
            and beats_brownian
            and beats_market
            and beats_current
        ),
    )


def _summarize_selectors(rows: Sequence[LOROHoldoutRow]) -> list[LOROSelectorSummaryRow]:
    grouped: dict[str, list[LOROHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.selector, []).append(row)
    summaries: list[LOROSelectorSummaryRow] = []
    for selector in sorted(grouped):
        selector_rows = grouped[selector]
        total_pnl = sum(row.holdout_total_counterfactual_pnl_cents for row in selector_rows)
        strict_count = sum(1 for row in selector_rows if row.holdout_passes_strict_gates)
        summaries.append(
            LOROSelectorSummaryRow(
                selector=selector,
                holdout_count=len(selector_rows),
                total_holdout_pnl_cents=total_pnl,
                mean_holdout_brier=_mean(row.holdout_brier for row in selector_rows),
                positive_pnl_holdout_count=sum(1 for row in selector_rows if row.holdout_total_counterfactual_pnl_cents > 0.0),
                beats_brownian_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_brownian),
                beats_market_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_market),
                beats_current_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_current_calibrated),
                positive_ev_rank_holdout_count=sum(1 for row in selector_rows if row.holdout_ev_rank_positive),
                positive_top_bucket_holdout_count=sum(1 for row in selector_rows if row.holdout_top_bucket_positive),
                strict_gate_holdout_count=strict_count,
                strict_all_holdouts=(strict_count == len(selector_rows) and bool(selector_rows)),
            )
        )
    return summaries


def _group_by_variant(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(_variant_key(row), []).append(row)
    return grouped


def _variant_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return str(row["source"]), str(row["name"])


def _float(row: Mapping[str, Any], field: str) -> float:
    return float(row.get(field) or 0.0)


def _mean(values: Sequence[float] | Any) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _markdown(report: VariantLOROSelectionDiagnosticReport) -> str:
    lines = [
        "# Variant LORO Selection Diagnostic",
        "",
        f"- source_stability_report: `{report.source_stability_report}`",
        f"- run_count: {report.run_count}",
        f"- variant_row_count: {report.variant_row_count}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Selector Summary",
        "",
        "| selector | holdouts | total_holdout_pnl | mean_brier | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.selector_summary_rows:
        lines.append(
            "| "
            f"{row.selector} | "
            f"{row.holdout_count} | "
            f"{row.total_holdout_pnl_cents:.4f} | "
            f"{row.mean_holdout_brier:.6f} | "
            f"{row.positive_pnl_holdout_count}/{row.holdout_count} | "
            f"{row.beats_brownian_holdout_count}/{row.holdout_count} | "
            f"{row.beats_market_holdout_count}/{row.holdout_count} | "
            f"{row.beats_current_holdout_count}/{row.holdout_count} | "
            f"{row.positive_ev_rank_holdout_count}/{row.holdout_count} | "
            f"{row.positive_top_bucket_holdout_count}/{row.holdout_count} | "
            f"{row.strict_gate_holdout_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| selector | holdout | variant | train_runs | train_pnl | train_brier | holdout_pnl | holdout_brier | beats_brownian | beats_market | beats_current | ev_rank_pos | top_bucket_pos | strict |",
            "|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.selector} | "
            f"{row.holdout_run} | "
            f"{row.source}:{row.name} | "
            f"{row.train_run_count} | "
            f"{row.train_total_counterfactual_pnl_cents:.4f} | "
            f"{row.train_mean_brier:.6f} | "
            f"{row.holdout_total_counterfactual_pnl_cents:.4f} | "
            f"{row.holdout_brier:.6f} | "
            f"{row.holdout_beats_brownian} | "
            f"{row.holdout_beats_market} | "
            f"{row.holdout_beats_current_calibrated} | "
            f"{row.holdout_ev_rank_positive} | "
            f"{row.holdout_top_bucket_positive} | "
            f"{row.holdout_passes_strict_gates} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
