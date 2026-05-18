from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paired_sidecar_slice_lock_comparison import (
    DEFAULT_REPORT_DIR,
    SliceLockComparisonRow,
    build_slice_lock_comparison,
)
from .paired_sidecar_slice_stability import DEFAULT_OUTPUT_JSON as DEFAULT_STABILITY_JSON
from .paired_sidecar_slice_trajectory import DEFAULT_OUTPUT_JSON as DEFAULT_TRAJECTORY_JSON


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = DEFAULT_REPORT_DIR / "paired_sidecar_slice_retirement_latest.json"
DEFAULT_OUTPUT_MD = DEFAULT_REPORT_DIR / "paired_sidecar_slice_retirement_latest.md"


@dataclass(frozen=True)
class SliceRetirementRow:
    hypothesis_id: str
    model: str
    bucket: str
    slice_rows: int
    slice_markets: int
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_pnl_cents: float
    v28_brier_delta: float | None
    v28_logloss_delta: float | None
    v28_selected_pnl_delta_cents: float | None
    v28_top_ev_pnl_delta_cents: float | None
    particle_like_model: bool
    particle_edge_candidate: bool
    stability_screen_pass: bool | None
    stability_warnings: tuple[str, ...]
    stability_market_count: int
    stability_positive_market_fraction: float | None
    stability_max_abs_market_pnl_share: float | None
    trajectory_screen_pass: bool | None
    trajectory_warnings: tuple[str, ...]
    trajectory_market_count: int
    trajectory_last_n_selected_pnl_cents: float | None
    trajectory_last_n_selected_pnl_delta_vs_v28_cents: float | None
    recommendation: str
    reason: str


@dataclass(frozen=True)
class SliceRetirementReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_report_dir: str
    input_pattern: str
    output_json: str
    output_md: str
    row_count: int
    particle_like_count: int
    retire_count: int
    watchlist_count: int
    stability_blocked_count: int
    trajectory_blocked_count: int
    continue_shadow_count: int
    control_count: int
    candidate_for_broader_audit_count: int
    rows: tuple[SliceRetirementRow, ...]
    conclusion: str


def build_slice_retirement_report(
    *,
    report_dir: Path = DEFAULT_REPORT_DIR,
    pattern: str = "paired_sidecar_slice_oos_PSLICELOCK*_latest.json",
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    stability_json: Path = DEFAULT_STABILITY_JSON,
    trajectory_json: Path = DEFAULT_TRAJECTORY_JSON,
    min_retire_markets: int = 5,
) -> SliceRetirementReport:
    comparison = build_slice_lock_comparison(report_dir=report_dir, pattern=pattern)
    stability_by_id = _stability_by_hypothesis(stability_json)
    trajectory_by_id = _rows_by_hypothesis(trajectory_json)
    rows = tuple(
        _retirement_row(
            row,
            stability_row=stability_by_id.get(row.hypothesis_id),
            trajectory_row=trajectory_by_id.get(row.hypothesis_id),
            min_retire_markets=min_retire_markets,
        )
        for row in comparison.rows
    )
    retire_count = sum(1 for row in rows if row.recommendation == "retire_negative_forward_evidence")
    watchlist_count = sum(1 for row in rows if row.recommendation == "watchlist_negative_underpowered")
    stability_blocked_count = sum(
        1 for row in rows if row.particle_like_model and row.stability_screen_pass is False
    )
    trajectory_blocked_count = sum(
        1 for row in rows if row.particle_like_model and row.trajectory_screen_pass is False
    )
    continue_count = sum(1 for row in rows if row.recommendation == "continue_shadow_only")
    control_count = sum(1 for row in rows if row.recommendation == "control_reference_only")
    candidate_count = sum(1 for row in rows if row.recommendation == "candidate_for_broader_audit")
    particle_like_count = sum(1 for row in rows if row.particle_like_model)
    return SliceRetirementReport(
        schema_version="paired-sidecar-slice-retirement-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "slice retirement is diagnostic/research-only and cannot approve live trading",
        },
        input_report_dir=str(report_dir),
        input_pattern=pattern,
        output_json=str(output_json),
        output_md=str(output_md),
        row_count=len(rows),
        particle_like_count=particle_like_count,
        retire_count=retire_count,
        watchlist_count=watchlist_count,
        stability_blocked_count=stability_blocked_count,
        trajectory_blocked_count=trajectory_blocked_count,
        continue_shadow_count=continue_count,
        control_count=control_count,
        candidate_for_broader_audit_count=candidate_count,
        rows=rows,
        conclusion=_conclusion(
            retire_count,
            watchlist_count,
            stability_blocked_count,
            trajectory_blocked_count,
            candidate_count,
            particle_like_count,
        ),
    )


def write_slice_retirement_report(report: SliceRetirementReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify frozen paired sidecar slice locks into research-only retirement/watchlist states."
    )
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--pattern", default="paired_sidecar_slice_oos_PSLICELOCK*_latest.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--stability-json", type=Path, default=DEFAULT_STABILITY_JSON)
    parser.add_argument("--trajectory-json", type=Path, default=DEFAULT_TRAJECTORY_JSON)
    parser.add_argument("--min-retire-markets", type=int, default=5)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_retirement_report(
        report_dir=args.report_dir,
        pattern=args.pattern,
        output_json=args.output_json,
        output_md=args.output_md,
        stability_json=args.stability_json,
        trajectory_json=args.trajectory_json,
        min_retire_markets=args.min_retire_markets,
    )
    if args.write:
        write_slice_retirement_report(report)
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"row_count={report.row_count}")
    print(f"particle_like_count={report.particle_like_count}")
    print(f"retire_count={report.retire_count}")
    print(f"watchlist_count={report.watchlist_count}")
    print(f"stability_blocked_count={report.stability_blocked_count}")
    print(f"trajectory_blocked_count={report.trajectory_blocked_count}")
    print(f"continue_shadow_count={report.continue_shadow_count}")
    print(f"control_count={report.control_count}")
    print(f"candidate_for_broader_audit_count={report.candidate_for_broader_audit_count}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _retirement_row(
    row: SliceLockComparisonRow,
    *,
    stability_row: Mapping[str, Any] | None = None,
    trajectory_row: Mapping[str, Any] | None = None,
    min_retire_markets: int,
) -> SliceRetirementRow:
    recommendation, reason = _recommendation(
        row,
        stability_row=stability_row,
        trajectory_row=trajectory_row,
        min_retire_markets=min_retire_markets,
    )
    stability_warnings = _stability_warnings(stability_row)
    trajectory_warnings = _trajectory_warnings(trajectory_row)
    return SliceRetirementRow(
        hypothesis_id=row.hypothesis_id,
        model=row.model,
        bucket=row.bucket,
        slice_rows=row.slice_rows,
        slice_markets=row.slice_markets,
        selected_count=row.selected_count,
        selected_pnl_cents=row.selected_pnl_cents,
        top_ev_bucket_pnl_cents=row.top_ev_bucket_pnl_cents,
        v28_brier_delta=row.v28_brier_delta,
        v28_logloss_delta=row.v28_logloss_delta,
        v28_selected_pnl_delta_cents=row.v28_selected_pnl_delta_cents,
        v28_top_ev_pnl_delta_cents=row.v28_top_ev_pnl_delta_cents,
        particle_like_model=row.particle_like_model,
        particle_edge_candidate=row.particle_edge_candidate,
        stability_screen_pass=None if stability_row is None else bool(stability_row.get("stability_screen_pass")),
        stability_warnings=stability_warnings,
        stability_market_count=0 if stability_row is None else int(stability_row.get("market_count", 0) or 0),
        stability_positive_market_fraction=(
            None if stability_row is None else _float_or_none(stability_row.get("positive_market_fraction"))
        ),
        stability_max_abs_market_pnl_share=(
            None if stability_row is None else _float_or_none(stability_row.get("max_abs_market_pnl_share"))
        ),
        trajectory_screen_pass=None if trajectory_row is None else bool(trajectory_row.get("trajectory_screen_pass")),
        trajectory_warnings=trajectory_warnings,
        trajectory_market_count=0 if trajectory_row is None else int(trajectory_row.get("market_count", 0) or 0),
        trajectory_last_n_selected_pnl_cents=(
            None if trajectory_row is None else _float_or_none(trajectory_row.get("last_n_selected_pnl_cents"))
        ),
        trajectory_last_n_selected_pnl_delta_vs_v28_cents=(
            None
            if trajectory_row is None
            else _float_or_none(trajectory_row.get("last_n_selected_pnl_delta_vs_v28_cents"))
        ),
        recommendation=recommendation,
        reason=reason,
    )


def _recommendation(
    row: SliceLockComparisonRow,
    *,
    stability_row: Mapping[str, Any] | None,
    trajectory_row: Mapping[str, Any] | None,
    min_retire_markets: int,
) -> tuple[str, str]:
    if row.particle_edge_candidate:
        return (
            "candidate_for_broader_audit",
            "Particle-like lock clears the comparison screen, but broader goal gates still control promotion.",
        )
    if not row.particle_like_model:
        return "control_reference_only", "Non-particle baseline/control lock."
    if row.slice_rows <= 0:
        return "await_fresh_rows", "No post-lock slice rows yet."
    selected_negative = row.selected_pnl_cents < 0.0
    top_negative = row.top_ev_bucket_pnl_cents < 0.0
    if selected_negative and top_negative and row.slice_markets >= min_retire_markets:
        return (
            "retire_negative_forward_evidence",
            "Negative selected PnL and negative top-EV bucket across enough forward markets.",
        )
    if selected_negative and top_negative:
        return (
            "watchlist_negative_underpowered",
            "Negative selected PnL and top-EV bucket, but sample remains below retirement market floor.",
        )
    if row.particle_like_model and trajectory_row is not None and not bool(trajectory_row.get("trajectory_screen_pass")):
        warnings = _trajectory_warnings(trajectory_row)
        warning_text = ", ".join(warnings) if warnings else "trajectory screen failed"
        return (
            "trajectory_blocked_shadow_only",
            f"Trajectory screen blocks promotion: {warning_text}.",
        )
    if row.particle_like_model and stability_row is not None and not bool(stability_row.get("stability_screen_pass")):
        warnings = _stability_warnings(stability_row)
        warning_text = ", ".join(warnings) if warnings else "stability screen failed"
        return (
            "stability_blocked_shadow_only",
            f"Market-stability screen blocks promotion: {warning_text}.",
        )
    if row.v28_selected_pnl_delta_cents is not None and row.v28_selected_pnl_delta_cents <= 0.0:
        return (
            "continue_shadow_only",
            "Nonnegative clue does not beat the same-slice v28 control on selected PnL.",
        )
    return (
        "continue_shadow_only",
        "Some forward evidence is nonnegative, but the lock has not cleared particle-vs-v28 and promotion gates.",
    )


def _conclusion(
    retire_count: int,
    watchlist_count: int,
    stability_blocked_count: int,
    trajectory_blocked_count: int,
    candidate_count: int,
    particle_like_count: int,
) -> str:
    if candidate_count:
        return "At least one particle-like lock needs broader audit review; this report still cannot promote live trading."
    if retire_count:
        return f"{retire_count} particle-like lock(s) should be retired from strategy consideration under the current evidence."
    if watchlist_count:
        return f"{watchlist_count} particle-like lock(s) have negative underpowered evidence and should remain watchlist-only."
    if trajectory_blocked_count:
        return f"{trajectory_blocked_count} particle-like lock(s) are blocked by trajectory diagnostics and remain shadow-only."
    if stability_blocked_count:
        return f"{stability_blocked_count} particle-like lock(s) are blocked by market-stability diagnostics and remain shadow-only."
    if particle_like_count:
        return "Particle-like locks remain shadow-only; none clears comparison or promotion gates."
    return "No particle-like locks are present."


def _stability_by_hypothesis(stability_json: Path) -> dict[str, Mapping[str, Any]]:
    return _rows_by_hypothesis(stability_json)


def _rows_by_hypothesis(path: Path) -> dict[str, Mapping[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    rows = payload.get("rows") if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return {}
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if isinstance(row, Mapping):
            hypothesis_id = str(row.get("hypothesis_id") or "")
            if hypothesis_id:
                result[hypothesis_id] = row
    return result


def _stability_warnings(stability_row: Mapping[str, Any] | None) -> tuple[str, ...]:
    if stability_row is None:
        return ()
    warnings = stability_row.get("stability_warnings") or ()
    if not isinstance(warnings, (list, tuple)):
        return ()
    return tuple(str(item) for item in warnings)


def _trajectory_warnings(trajectory_row: Mapping[str, Any] | None) -> tuple[str, ...]:
    if trajectory_row is None:
        return ()
    warnings = trajectory_row.get("trajectory_warnings") or ()
    if not isinstance(warnings, (list, tuple)):
        return ()
    return tuple(str(item) for item in warnings)


def _float_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SliceRetirementReport) -> str:
    lines = [
        "# Paired Sidecar Slice Retirement",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- row_count: `{report.row_count}`",
        f"- particle_like_count: `{report.particle_like_count}`",
        f"- retire_count: `{report.retire_count}`",
        f"- watchlist_count: `{report.watchlist_count}`",
        f"- stability_blocked_count: `{report.stability_blocked_count}`",
        f"- trajectory_blocked_count: `{report.trajectory_blocked_count}`",
        f"- continue_shadow_count: `{report.continue_shadow_count}`",
        f"- control_count: `{report.control_count}`",
        f"- candidate_for_broader_audit_count: `{report.candidate_for_broader_audit_count}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | rows/markets | selected | pnl c | top EV c | dPnL vs v28 | dBrier vs v28 | stability pass | trajectory pass | recent c | recent dPnL | warnings | recommendation |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in report.rows:
        lines.append(
            "| "
            f"`{row.hypothesis_id}` | "
            f"`{row.model}` | "
            f"`{row.slice_rows}` / `{row.slice_markets}` | "
            f"`{row.selected_count}` | "
            f"`{row.selected_pnl_cents:.1f}` | "
            f"`{row.top_ev_bucket_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.v28_selected_pnl_delta_cents)}` | "
            f"`{_fmt_optional(row.v28_brier_delta)}` | "
            f"`{row.stability_screen_pass}` | "
            f"`{row.trajectory_screen_pass}` | "
            f"`{_fmt_optional(row.trajectory_last_n_selected_pnl_cents)}` | "
            f"`{_fmt_optional(row.trajectory_last_n_selected_pnl_delta_vs_v28_cents)}` | "
            f"`{', '.join(row.stability_warnings + row.trajectory_warnings)}` | "
            f"`{row.recommendation}` |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            report.conclusion,
            "",
            "This report is diagnostic only and never authorizes live trading.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
