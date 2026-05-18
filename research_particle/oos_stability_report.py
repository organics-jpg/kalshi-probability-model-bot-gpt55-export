from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable


@dataclass(frozen=True)
class VariantRunRow:
    run_name: str
    source: str
    name: str
    candidate_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float


@dataclass(frozen=True)
class VariantStabilityRow:
    source: str
    name: str
    run_count: int
    total_candidate_count: int
    total_selected_count: int
    total_counterfactual_pnl_cents: float
    mean_pnl_cents_per_run: float
    mean_brier: float
    mean_log_loss: float
    mean_ev_rank_correlation_sign: float
    mean_top_ev_bucket_pnl_cents: float
    pnl_std_cents: float
    positive_pnl_run_count: int
    positive_ev_rank_run_count: int
    positive_top_bucket_run_count: int
    beats_brownian_run_count: int
    beats_market_run_count: int
    beats_current_run_count: int
    stable_all_runs: bool


@dataclass(frozen=True)
class OOSStabilityReport:
    run_count: int
    runs: tuple[str, ...]
    min_runs_for_stability: int
    variant_rows: tuple[VariantRunRow, ...]
    stability_rows: tuple[VariantStabilityRow, ...]
    best_by_total_pnl: VariantStabilityRow | None
    best_by_mean_brier: VariantStabilityRow | None
    stable_candidate_count: int
    stable_candidates: tuple[VariantStabilityRow, ...]
    promotion_safe: bool
    note: str


def build_oos_stability_report(
    report_roots: Iterable[Path],
    *,
    min_runs_for_stability: int = 2,
) -> OOSStabilityReport:
    roots = tuple(report_roots)
    variant_rows: list[VariantRunRow] = []
    runs: list[str] = []
    for root in roots:
        report_dir = root / "reports" if (root / "reports").exists() else root
        run_name = root.name if report_dir.name == "reports" else report_dir.parent.name
        runs.append(run_name)
        variant_rows.extend(_load_rows_for_run(report_dir, run_name))
    stability_rows = tuple(_summarize(variant_rows, min_runs_for_stability=min_runs_for_stability))
    stable_candidates = tuple(row for row in stability_rows if row.stable_all_runs)
    best_pool = tuple(row for row in stability_rows if row.run_count >= min_runs_for_stability) or stability_rows
    best_by_total_pnl = (
        max(best_pool, key=lambda row: row.total_counterfactual_pnl_cents)
        if best_pool
        else None
    )
    best_by_mean_brier = min(best_pool, key=lambda row: row.mean_brier) if best_pool else None
    return OOSStabilityReport(
        run_count=len(roots),
        runs=tuple(runs),
        min_runs_for_stability=int(min_runs_for_stability),
        variant_rows=tuple(variant_rows),
        stability_rows=stability_rows,
        best_by_total_pnl=best_by_total_pnl,
        best_by_mean_brier=best_by_mean_brier,
        stable_candidate_count=len(stable_candidates),
        stable_candidates=stable_candidates,
        promotion_safe=False,
        note=(
            "This is a locked-run stability diagnostic. It does not promote a "
            "strategy by itself; any new variant selected from this table needs "
            "a predeclared fresh OOS run."
        ),
    )


def write_oos_stability_report(
    report: OOSStabilityReport,
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
        description="Summarize variant stability across locked OOS report directories."
    )
    parser.add_argument("--report-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="oos_stability_report")
    parser.add_argument("--min-runs-for-stability", default=2, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_oos_stability_report(
        args.report_root,
        min_runs_for_stability=args.min_runs_for_stability,
    )
    json_path, md_path = write_oos_stability_report(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"variant_row_count={len(report.variant_rows)}")
    print(f"stability_row_count={len(report.stability_rows)}")
    print(f"stable_candidate_count={len(report.stable_candidates)}")
    if report.best_by_total_pnl:
        print(
            "best_by_total_pnl="
            f"{report.best_by_total_pnl.source}:{report.best_by_total_pnl.name}"
        )
        print(
            "best_by_total_pnl_cents="
            f"{report.best_by_total_pnl.total_counterfactual_pnl_cents:.4f}"
        )
    if report.best_by_mean_brier:
        print(
            "best_by_mean_brier="
            f"{report.best_by_mean_brier.source}:{report.best_by_mean_brier.name}"
        )
        print(f"best_by_mean_brier_value={report.best_by_mean_brier.mean_brier:.6f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_rows_for_run(report_dir: Path, run_name: str) -> list[VariantRunRow]:
    rows: list[VariantRunRow] = []
    passive_path = report_dir / "passive_particle_replay_locked_oos.json"
    if passive_path.exists():
        payload = _read_json(passive_path)
        rows.append(
            _variant_row_from_mapping(
                run_name,
                "static",
                "particle",
                {
                    "candidate_count": payload.get("candidate_count"),
                    "selected_count": payload.get("selected_count"),
                    "total_counterfactual_pnl_cents": payload.get("total_counterfactual_pnl_cents"),
                    "avg_counterfactual_pnl_cents_per_candidate": payload.get(
                        "avg_counterfactual_pnl_cents_per_candidate"
                    ),
                    "avg_counterfactual_pnl_cents_per_selected": payload.get(
                        "avg_counterfactual_pnl_cents_per_selected"
                    ),
                    "brier": (payload.get("particle") or {}).get("brier"),
                    "log_loss": (payload.get("particle") or {}).get("log_loss"),
                    "beats_brownian": payload.get("particle_beats_brownian"),
                    "beats_market": payload.get("particle_beats_market"),
                    "beats_current_calibrated": payload.get("particle_beats_current_calibrated"),
                    "ev_rank_correlation_sign": payload.get("ev_rank_correlation_sign"),
                    "top_ev_bucket_pnl_cents": payload.get("top_ev_bucket_pnl_cents"),
                },
            )
        )
    for path in sorted(report_dir.glob("probability_variants*.json")):
        payload = _read_json(path)
        for row in payload.get("rows", ()):
            rows.append(_variant_row_from_mapping(run_name, "probability", row.get("name", ""), row))
    for path in sorted(report_dir.glob("dynamic_particle*.json")):
        if "dynamic_particle_oos" in path.name:
            continue
        payload = _read_json(path)
        for row in payload.get("rows", ()):
            rows.append(_variant_row_from_mapping(run_name, "dynamic", row.get("name", ""), row))
    for path in sorted(report_dir.glob("ensemble_particle*.json")):
        payload = _read_json(path)
        for row in payload.get("rows", ()):
            rows.append(_variant_row_from_mapping(run_name, "ensemble", row.get("name", ""), row))
    for path in sorted(report_dir.glob("online_logit_particle*.json")):
        payload = _read_json(path)
        for row in payload.get("rows", ()):
            rows.append(_variant_row_from_mapping(run_name, "online_logit", row.get("name", ""), row))
    for path in sorted(report_dir.glob("side_consensus_oos*.json")):
        rows.append(_side_consensus_row_from_report(report_dir, run_name, path))
    for path in sorted(report_dir.glob("residual_blend_oos*.json")):
        rows.append(_residual_blend_row_from_report(run_name, path))
    for path in sorted(report_dir.glob("fixed_terminal_oos*.json")):
        rows.append(_fixed_terminal_row_from_report(run_name, path))
    for path in sorted(report_dir.glob("spot_realized_vol_terminal_oos*.json")):
        rows.append(_spot_realized_vol_terminal_row_from_report(run_name, path))
    for path in sorted(report_dir.glob("materialized_*.json")):
        payload = _read_json(path)
        rows.append(
            _variant_row_from_mapping(
                run_name,
                "materialized",
                path.stem.removeprefix("materialized_"),
                {
                    "candidate_count": payload.get("candidate_count"),
                    "selected_count": payload.get("selected_count"),
                    "total_counterfactual_pnl_cents": payload.get("total_counterfactual_pnl_cents"),
                    "avg_counterfactual_pnl_cents_per_candidate": payload.get(
                        "avg_counterfactual_pnl_cents_per_candidate"
                    ),
                    "avg_counterfactual_pnl_cents_per_selected": payload.get(
                        "avg_counterfactual_pnl_cents_per_selected"
                    ),
                    "brier": (payload.get("particle") or {}).get("brier"),
                    "log_loss": (payload.get("particle") or {}).get("log_loss"),
                    "beats_brownian": payload.get("particle_beats_brownian"),
                    "beats_market": payload.get("particle_beats_market"),
                    "beats_current_calibrated": payload.get("particle_beats_current_calibrated"),
                    "ev_rank_correlation_sign": payload.get("ev_rank_correlation_sign"),
                    "top_ev_bucket_pnl_cents": payload.get("top_ev_bucket_pnl_cents"),
                },
            )
        )
    return rows


def _summarize(
    rows: Iterable[VariantRunRow],
    *,
    min_runs_for_stability: int,
) -> list[VariantStabilityRow]:
    grouped: dict[tuple[str, str], list[VariantRunRow]] = {}
    for row in rows:
        grouped.setdefault((row.source, row.name), []).append(row)
    summaries: list[VariantStabilityRow] = []
    for (source, name), group in sorted(grouped.items()):
        pnls = [row.total_counterfactual_pnl_cents for row in group]
        run_count = len(group)
        positive_pnl = sum(1 for row in group if row.total_counterfactual_pnl_cents > 0.0)
        positive_ev_rank = sum(1 for row in group if row.ev_rank_correlation_sign > 0.0)
        positive_top_bucket = sum(1 for row in group if row.top_ev_bucket_pnl_cents > 0.0)
        beats_brownian = sum(1 for row in group if row.beats_brownian)
        beats_market = sum(1 for row in group if row.beats_market)
        beats_current = sum(1 for row in group if row.beats_current_calibrated)
        stable_all_runs = (
            run_count >= min_runs_for_stability
            and positive_pnl == run_count
            and positive_ev_rank == run_count
            and positive_top_bucket == run_count
            and beats_brownian == run_count
            and beats_market == run_count
            and beats_current == run_count
        )
        summaries.append(
            VariantStabilityRow(
                source=source,
                name=name,
                run_count=run_count,
                total_candidate_count=sum(row.candidate_count for row in group),
                total_selected_count=sum(row.selected_count for row in group),
                total_counterfactual_pnl_cents=sum(pnls),
                mean_pnl_cents_per_run=mean(pnls),
                mean_brier=mean(row.brier for row in group),
                mean_log_loss=mean(row.log_loss for row in group),
                mean_ev_rank_correlation_sign=mean(row.ev_rank_correlation_sign for row in group),
                mean_top_ev_bucket_pnl_cents=mean(row.top_ev_bucket_pnl_cents for row in group),
                pnl_std_cents=(pstdev(pnls) if len(pnls) > 1 else 0.0),
                positive_pnl_run_count=positive_pnl,
                positive_ev_rank_run_count=positive_ev_rank,
                positive_top_bucket_run_count=positive_top_bucket,
                beats_brownian_run_count=beats_brownian,
                beats_market_run_count=beats_market,
                beats_current_run_count=beats_current,
                stable_all_runs=stable_all_runs,
            )
        )
    return summaries


def _variant_row_from_mapping(
    run_name: str,
    source: str,
    name: str,
    row: dict[str, Any],
) -> VariantRunRow:
    return VariantRunRow(
        run_name=run_name,
        source=source,
        name=str(name),
        candidate_count=int(row.get("candidate_count") or 0),
        selected_count=int(row.get("selected_count") or 0),
        total_counterfactual_pnl_cents=float(row.get("total_counterfactual_pnl_cents") or 0.0),
        avg_counterfactual_pnl_cents_per_candidate=float(
            row.get("avg_counterfactual_pnl_cents_per_candidate") or 0.0
        ),
        avg_counterfactual_pnl_cents_per_selected=float(
            row.get("avg_counterfactual_pnl_cents_per_selected") or 0.0
        ),
        brier=float(row.get("brier") or 0.0),
        log_loss=float(row.get("log_loss") or 0.0),
        beats_brownian=bool(row.get("beats_brownian")),
        beats_market=bool(row.get("beats_market")),
        beats_current_calibrated=bool(row.get("beats_current_calibrated")),
        ev_rank_correlation_sign=float(row.get("ev_rank_correlation_sign") or 0.0),
        top_ev_bucket_pnl_cents=float(row.get("top_ev_bucket_pnl_cents") or 0.0),
    )


def _side_consensus_row_from_report(
    report_dir: Path,
    run_name: str,
    path: Path,
) -> VariantRunRow:
    payload = _read_json(path)
    passive = _read_json(report_dir / "passive_particle_replay_locked_oos.json")
    particle = passive.get("particle") or {}
    return _variant_row_from_mapping(
        run_name,
        "side_consensus",
        str(payload.get("hypothesis_id") or path.stem),
        {
            "candidate_count": payload.get("candidate_count"),
            "selected_count": payload.get("consensus_selected_count"),
            "total_counterfactual_pnl_cents": payload.get(
                "consensus_total_counterfactual_pnl_cents"
            ),
            "avg_counterfactual_pnl_cents_per_candidate": (
                float(payload.get("consensus_total_counterfactual_pnl_cents") or 0.0)
                / max(1, int(payload.get("candidate_count") or 0))
            ),
            "avg_counterfactual_pnl_cents_per_selected": payload.get(
                "consensus_avg_counterfactual_pnl_cents_per_selected"
            ),
            "brier": particle.get("brier", 1.0),
            "log_loss": particle.get("log_loss", 999.0),
            "beats_brownian": passive.get("particle_beats_brownian", False),
            "beats_market": passive.get("particle_beats_market", False),
            "beats_current_calibrated": passive.get("particle_beats_current_calibrated", False),
            "ev_rank_correlation_sign": payload.get("consensus_ev_rank_correlation_sign"),
            "top_ev_bucket_pnl_cents": payload.get("consensus_top_ev_bucket_pnl_cents"),
        },
    )


def _residual_blend_row_from_report(run_name: str, path: Path) -> VariantRunRow:
    payload = _read_json(path)
    selected = payload.get("selected_variant") or {}
    return _variant_row_from_mapping(
        run_name,
        "residual_blend",
        str(payload.get("hypothesis_id") or selected.get("name") or path.stem),
        {
            "candidate_count": selected.get("candidate_count", payload.get("candidate_count")),
            "selected_count": selected.get("selected_count"),
            "total_counterfactual_pnl_cents": selected.get("total_counterfactual_pnl_cents"),
            "avg_counterfactual_pnl_cents_per_candidate": selected.get(
                "avg_counterfactual_pnl_cents_per_candidate"
            ),
            "avg_counterfactual_pnl_cents_per_selected": selected.get(
                "avg_counterfactual_pnl_cents_per_selected"
            ),
            "brier": selected.get("brier"),
            "log_loss": selected.get("log_loss"),
            "beats_brownian": selected.get("beats_brownian"),
            "beats_market": selected.get("beats_market"),
            "beats_current_calibrated": selected.get("beats_current_calibrated"),
            "ev_rank_correlation_sign": selected.get("ev_rank_correlation_sign"),
            "top_ev_bucket_pnl_cents": selected.get("top_ev_bucket_pnl_cents"),
        },
    )


def _fixed_terminal_row_from_report(run_name: str, path: Path) -> VariantRunRow:
    payload = _read_json(path)
    selected = payload.get("selected_variant") or {}
    candidate_count = int(selected.get("candidate_count") or payload.get("candidate_count") or 0)
    selected_count = int(selected.get("selected_count") or 0)
    total_pnl = float(selected.get("total_counterfactual_pnl_cents") or 0.0)
    return _variant_row_from_mapping(
        run_name,
        "fixed_terminal",
        str(payload.get("hypothesis_id") or selected.get("name") or path.stem),
        {
            "candidate_count": candidate_count,
            "selected_count": selected_count,
            "total_counterfactual_pnl_cents": total_pnl,
            "avg_counterfactual_pnl_cents_per_candidate": (
                total_pnl / max(1, candidate_count)
            ),
            "avg_counterfactual_pnl_cents_per_selected": selected.get(
                "avg_counterfactual_pnl_cents_per_selected"
            ),
            "brier": selected.get("brier"),
            "log_loss": selected.get("log_loss"),
            "beats_brownian": selected.get("beats_brownian"),
            "beats_market": selected.get("beats_market"),
            "beats_current_calibrated": selected.get("beats_current_calibrated"),
            "ev_rank_correlation_sign": selected.get("ev_rank_correlation_sign"),
            "top_ev_bucket_pnl_cents": selected.get("top_ev_bucket_pnl_cents"),
        },
    )


def _spot_realized_vol_terminal_row_from_report(run_name: str, path: Path) -> VariantRunRow:
    payload = _read_json(path)
    selected = payload.get("selected_variant") or {}
    candidate_count = int(selected.get("candidate_count") or payload.get("candidate_count") or 0)
    selected_count = int(selected.get("selected_count") or 0)
    total_pnl = float(selected.get("total_counterfactual_pnl_cents") or 0.0)
    return _variant_row_from_mapping(
        run_name,
        "spot_realized_vol_terminal",
        str(payload.get("hypothesis_id") or selected.get("name") or path.stem),
        {
            "candidate_count": candidate_count,
            "selected_count": selected_count,
            "total_counterfactual_pnl_cents": total_pnl,
            "avg_counterfactual_pnl_cents_per_candidate": (
                total_pnl / max(1, candidate_count)
            ),
            "avg_counterfactual_pnl_cents_per_selected": selected.get(
                "avg_counterfactual_pnl_cents_per_selected"
            ),
            "brier": selected.get("brier"),
            "log_loss": selected.get("log_loss"),
            "beats_brownian": selected.get("beats_brownian"),
            "beats_market": selected.get("beats_market"),
            "beats_current_calibrated": selected.get("beats_current_calibrated"),
            "ev_rank_correlation_sign": selected.get("ev_rank_correlation_sign"),
            "top_ev_bucket_pnl_cents": selected.get("top_ev_bucket_pnl_cents"),
        },
    )


def _read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _markdown(report: OOSStabilityReport) -> str:
    lines = [
        "# OOS Stability Report",
        "",
        f"- run_count: {report.run_count}",
        f"- runs: {', '.join(report.runs)}",
        f"- min_runs_for_stability: {report.min_runs_for_stability}",
        f"- variant_row_count: {len(report.variant_rows)}",
        f"- stability_row_count: {len(report.stability_rows)}",
        f"- stable_candidate_count: {len(report.stable_candidates)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
        "## Stability Rows",
        "",
        "| source | variant | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | positive_ev_rank | positive_top_bucket | beats_brownian | beats_market | beats_current | stable_all_runs |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(
        report.stability_rows,
        key=lambda item: (not item.stable_all_runs, -item.total_counterfactual_pnl_cents),
    ):
        lines.append(
            "| {source} | {name} | {run_count} | {total_counterfactual_pnl_cents:.4f} | "
            "{mean_brier:.6f} | {mean_log_loss:.6f} | {positive_pnl_run_count} | "
            "{positive_ev_rank_run_count} | {positive_top_bucket_run_count} | "
            "{beats_brownian_run_count} | {beats_market_run_count} | {beats_current_run_count} | "
            "{stable_all_runs} |".format(**asdict(row))
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
