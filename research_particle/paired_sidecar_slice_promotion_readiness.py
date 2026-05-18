from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paired_sidecar_slice_lock_comparison import DEFAULT_OUTPUT_JSON as DEFAULT_COMPARISON_JSON
from .paired_sidecar_slice_retirement import DEFAULT_OUTPUT_JSON as DEFAULT_RETIREMENT_JSON
from .paired_sidecar_slice_stability import DEFAULT_OUTPUT_JSON as DEFAULT_STABILITY_JSON
from .paired_sidecar_slice_trajectory import DEFAULT_OUTPUT_JSON as DEFAULT_TRAJECTORY_JSON


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_promotion_readiness_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_promotion_readiness_latest.md"
)


@dataclass(frozen=True)
class SlicePromotionReadinessRow:
    hypothesis_id: str
    model: str
    bucket: str
    particle_like_model: bool
    selected_pnl_cents: float
    top_ev_bucket_pnl_cents: float
    v28_brier_delta: float | None
    v28_logloss_delta: float | None
    v28_selected_pnl_delta_cents: float | None
    v28_top_ev_pnl_delta_cents: float | None
    locked_oos_promotion_safe: bool
    particle_edge_candidate: bool
    stability_screen_pass: bool | None
    trajectory_screen_pass: bool | None
    retirement_recommendation: str
    blockers: tuple[str, ...]
    readiness_candidate: bool


@dataclass(frozen=True)
class SlicePromotionReadinessReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_comparison_json: str
    input_stability_json: str
    input_trajectory_json: str
    input_retirement_json: str
    output_json: str
    output_md: str
    row_count: int
    particle_like_count: int
    readiness_candidate_count: int
    hard_veto_count: int
    rows: tuple[SlicePromotionReadinessRow, ...]
    conclusion: str


def build_slice_promotion_readiness_report(
    *,
    comparison_json: Path = DEFAULT_COMPARISON_JSON,
    stability_json: Path = DEFAULT_STABILITY_JSON,
    trajectory_json: Path = DEFAULT_TRAJECTORY_JSON,
    retirement_json: Path = DEFAULT_RETIREMENT_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
) -> SlicePromotionReadinessReport:
    comparison = _load_json(comparison_json)
    stability_by_id = _rows_by_hypothesis(stability_json)
    trajectory_by_id = _rows_by_hypothesis(trajectory_json)
    retirement_by_id = _rows_by_hypothesis(retirement_json)
    rows = tuple(
        _readiness_row(
            comparison_row=_mapping(row),
            stability_row=stability_by_id.get(str(_mapping(row).get("hypothesis_id") or "")),
            trajectory_row=trajectory_by_id.get(str(_mapping(row).get("hypothesis_id") or "")),
            retirement_row=retirement_by_id.get(str(_mapping(row).get("hypothesis_id") or "")),
        )
        for row in comparison.get("rows") or []
        if isinstance(row, Mapping)
    )
    particle_rows = [row for row in rows if row.particle_like_model]
    ready_rows = [row for row in rows if row.readiness_candidate]
    hard_veto_rows = [row for row in particle_rows if row.blockers]
    return SlicePromotionReadinessReport(
        schema_version="paired-sidecar-slice-promotion-readiness-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "promotion readiness is a diagnostic preflight and cannot approve live trading",
        },
        input_comparison_json=str(comparison_json),
        input_stability_json=str(stability_json),
        input_trajectory_json=str(trajectory_json),
        input_retirement_json=str(retirement_json),
        output_json=str(output_json),
        output_md=str(output_md),
        row_count=len(rows),
        particle_like_count=len(particle_rows),
        readiness_candidate_count=len(ready_rows),
        hard_veto_count=len(hard_veto_rows),
        rows=rows,
        conclusion=_conclusion(rows, ready_rows),
    )


def write_slice_promotion_readiness_report(report: SlicePromotionReadinessReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine paired sidecar slice comparison, stability, trajectory, and retirement screens."
    )
    parser.add_argument("--comparison-json", type=Path, default=DEFAULT_COMPARISON_JSON)
    parser.add_argument("--stability-json", type=Path, default=DEFAULT_STABILITY_JSON)
    parser.add_argument("--trajectory-json", type=Path, default=DEFAULT_TRAJECTORY_JSON)
    parser.add_argument("--retirement-json", type=Path, default=DEFAULT_RETIREMENT_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_promotion_readiness_report(
        comparison_json=args.comparison_json,
        stability_json=args.stability_json,
        trajectory_json=args.trajectory_json,
        retirement_json=args.retirement_json,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_slice_promotion_readiness_report(report)
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"row_count={report.row_count}")
    print(f"particle_like_count={report.particle_like_count}")
    print(f"readiness_candidate_count={report.readiness_candidate_count}")
    print(f"hard_veto_count={report.hard_veto_count}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _readiness_row(
    *,
    comparison_row: Mapping[str, Any],
    stability_row: Mapping[str, Any] | None,
    trajectory_row: Mapping[str, Any] | None,
    retirement_row: Mapping[str, Any] | None,
) -> SlicePromotionReadinessRow:
    hypothesis_id = str(comparison_row.get("hypothesis_id") or "")
    model = str(comparison_row.get("model") or "")
    particle_like = bool(comparison_row.get("particle_like_model"))
    selected_pnl = _float(comparison_row.get("selected_pnl_cents"))
    top_ev_pnl = _float(comparison_row.get("top_ev_bucket_pnl_cents"))
    v28_brier_delta = _float_or_none(comparison_row.get("v28_brier_delta"))
    v28_logloss_delta = _float_or_none(comparison_row.get("v28_logloss_delta"))
    v28_selected_delta = _float_or_none(comparison_row.get("v28_selected_pnl_delta_cents"))
    v28_top_ev_delta = _float_or_none(comparison_row.get("v28_top_ev_pnl_delta_cents"))
    locked_safe = bool(comparison_row.get("promotion_safe"))
    particle_edge_candidate = bool(comparison_row.get("particle_edge_candidate"))
    stability_pass = None if stability_row is None else bool(stability_row.get("stability_screen_pass"))
    trajectory_pass = None if trajectory_row is None else bool(trajectory_row.get("trajectory_screen_pass"))
    retirement_recommendation = "" if retirement_row is None else str(retirement_row.get("recommendation") or "")
    blockers = _blockers(
        particle_like=particle_like,
        selected_pnl=selected_pnl,
        top_ev_pnl=top_ev_pnl,
        v28_brier_delta=v28_brier_delta,
        v28_logloss_delta=v28_logloss_delta,
        v28_selected_delta=v28_selected_delta,
        v28_top_ev_delta=v28_top_ev_delta,
        locked_safe=locked_safe,
        stability_pass=stability_pass,
        trajectory_pass=trajectory_pass,
        retirement_recommendation=retirement_recommendation,
    )
    return SlicePromotionReadinessRow(
        hypothesis_id=hypothesis_id,
        model=model,
        bucket=str(comparison_row.get("bucket") or ""),
        particle_like_model=particle_like,
        selected_pnl_cents=selected_pnl,
        top_ev_bucket_pnl_cents=top_ev_pnl,
        v28_brier_delta=v28_brier_delta,
        v28_logloss_delta=v28_logloss_delta,
        v28_selected_pnl_delta_cents=v28_selected_delta,
        v28_top_ev_pnl_delta_cents=v28_top_ev_delta,
        locked_oos_promotion_safe=locked_safe,
        particle_edge_candidate=particle_edge_candidate,
        stability_screen_pass=stability_pass,
        trajectory_screen_pass=trajectory_pass,
        retirement_recommendation=retirement_recommendation,
        blockers=blockers,
        readiness_candidate=particle_like and not blockers,
    )


def _blockers(
    *,
    particle_like: bool,
    selected_pnl: float,
    top_ev_pnl: float,
    v28_brier_delta: float | None,
    v28_logloss_delta: float | None,
    v28_selected_delta: float | None,
    v28_top_ev_delta: float | None,
    locked_safe: bool,
    stability_pass: bool | None,
    trajectory_pass: bool | None,
    retirement_recommendation: str,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if not particle_like:
        return ("control_not_particle_like",)
    if selected_pnl <= 0.0:
        blockers.append("nonpositive_selected_pnl")
    if top_ev_pnl <= 0.0:
        blockers.append("nonpositive_top_ev_pnl")
    if v28_brier_delta is None or v28_brier_delta >= 0.0:
        blockers.append("does_not_beat_v28_brier")
    if v28_logloss_delta is None or v28_logloss_delta >= 0.0:
        blockers.append("does_not_beat_v28_logloss")
    if v28_selected_delta is None or v28_selected_delta <= 0.0:
        blockers.append("does_not_beat_v28_selected_pnl")
    if v28_top_ev_delta is None or v28_top_ev_delta <= 0.0:
        blockers.append("does_not_beat_v28_top_ev_pnl")
    if not locked_safe:
        blockers.append("locked_oos_promotion_safe_false")
    if stability_pass is not True:
        blockers.append("stability_screen_not_passed")
    if trajectory_pass is not True:
        blockers.append("trajectory_screen_not_passed")
    if retirement_recommendation and retirement_recommendation != "candidate_for_broader_audit":
        blockers.append(f"retirement_{retirement_recommendation}")
    return tuple(blockers)


def _conclusion(
    rows: tuple[SlicePromotionReadinessRow, ...],
    ready_rows: list[SlicePromotionReadinessRow],
) -> str:
    if ready_rows:
        names = ", ".join(row.hypothesis_id for row in ready_rows)
        return f"Diagnostic only: {names} clears the combined readiness screen, but live trading is still not authorized."
    if rows:
        return "No particle-like lock clears the combined readiness screen; keep all locks shadow-only."
    return "No slice rows are available for readiness analysis."


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _rows_by_hypothesis(path: Path) -> dict[str, Mapping[str, Any]]:
    payload = _load_json(path)
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


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed == parsed else default


def _float_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SlicePromotionReadinessReport) -> str:
    lines = [
        "# Paired Sidecar Slice Promotion Readiness",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- row_count: `{report.row_count}`",
        f"- particle_like_count: `{report.particle_like_count}`",
        f"- readiness_candidate_count: `{report.readiness_candidate_count}`",
        f"- hard_veto_count: `{report.hard_veto_count}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | pnl c | top EV c | dBrier | dLogloss | dPnL | dTopEV | safe | stability | trajectory | retirement | blockers | ready |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(
            "| "
            f"`{row.hypothesis_id}` | "
            f"`{row.model}` | "
            f"`{row.selected_pnl_cents:.1f}` | "
            f"`{row.top_ev_bucket_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.v28_brier_delta)}` | "
            f"`{_fmt_optional(row.v28_logloss_delta)}` | "
            f"`{_fmt_optional(row.v28_selected_pnl_delta_cents)}` | "
            f"`{_fmt_optional(row.v28_top_ev_pnl_delta_cents)}` | "
            f"`{row.locked_oos_promotion_safe}` | "
            f"`{row.stability_screen_pass}` | "
            f"`{row.trajectory_screen_pass}` | "
            f"`{row.retirement_recommendation}` | "
            f"`{', '.join(row.blockers)}` | "
            f"`{row.readiness_candidate}` |"
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
