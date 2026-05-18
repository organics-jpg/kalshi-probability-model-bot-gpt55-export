from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
DEFAULT_OUTPUT_JSON = DEFAULT_REPORT_DIR / "paired_sidecar_slice_lock_comparison_latest.json"
DEFAULT_OUTPUT_MD = DEFAULT_REPORT_DIR / "paired_sidecar_slice_lock_comparison_latest.md"


@dataclass(frozen=True)
class SliceLockComparisonRow:
    hypothesis_id: str
    model: str
    bucket: str
    locked_after_utc: str
    promotion_safe: bool
    fresh_candidate_rows: int
    fresh_markets: int
    slice_rows: int
    slice_markets: int
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_pnl_cents: float
    brier: float
    logloss: float
    ev_rank_correlation: float
    v28_brier_delta: float | None
    v28_logloss_delta: float | None
    v28_selected_pnl_delta_cents: float | None
    v28_top_ev_pnl_delta_cents: float | None
    beats_v28_brier: bool
    beats_v28_logloss: bool
    beats_v28_selected_pnl: bool
    beats_v28_top_ev_pnl: bool
    particle_like_model: bool
    particle_edge_candidate: bool


@dataclass(frozen=True)
class SliceLockComparisonReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_report_dir: str
    input_pattern: str
    output_json: str
    output_md: str
    report_count: int
    promotion_safe_count: int
    particle_like_count: int
    particle_edge_candidate_count: int
    best_selected_pnl_hypothesis_id: str
    best_selected_pnl_cents: float
    best_v28_brier_delta_hypothesis_id: str
    best_v28_brier_delta: float | None
    rows: tuple[SliceLockComparisonRow, ...]
    conclusion: str


def build_slice_lock_comparison(
    *,
    report_dir: Path = DEFAULT_REPORT_DIR,
    pattern: str = "paired_sidecar_slice_oos_PSLICELOCK*_latest.json",
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
) -> SliceLockComparisonReport:
    payloads = [_load_json(path) for path in sorted(report_dir.glob(pattern))]
    rows = tuple(_comparison_row(payload) for payload in payloads if payload)
    particle_rows = [row for row in rows if row.particle_like_model]
    edge_rows = [row for row in rows if row.particle_edge_candidate]
    nonempty_rows = [row for row in rows if row.slice_rows > 0]
    best_pnl = max(nonempty_rows, key=lambda row: row.selected_pnl_cents, default=None)
    comparable = [row for row in rows if row.v28_brier_delta is not None]
    best_brier_delta = min(comparable, key=lambda row: row.v28_brier_delta or 0.0, default=None)
    conclusion = _conclusion(rows, edge_rows)
    return SliceLockComparisonReport(
        schema_version="paired-sidecar-slice-lock-comparison-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "slice lock comparison is diagnostic only and cannot approve live trading",
        },
        input_report_dir=str(report_dir),
        input_pattern=pattern,
        output_json=str(output_json),
        output_md=str(output_md),
        report_count=len(rows),
        promotion_safe_count=sum(1 for row in rows if row.promotion_safe),
        particle_like_count=len(particle_rows),
        particle_edge_candidate_count=len(edge_rows),
        best_selected_pnl_hypothesis_id="" if best_pnl is None else best_pnl.hypothesis_id,
        best_selected_pnl_cents=0.0 if best_pnl is None else best_pnl.selected_pnl_cents,
        best_v28_brier_delta_hypothesis_id="" if best_brier_delta is None else best_brier_delta.hypothesis_id,
        best_v28_brier_delta=None if best_brier_delta is None else best_brier_delta.v28_brier_delta,
        rows=rows,
        conclusion=conclusion,
    )


def write_slice_lock_comparison(report: SliceLockComparisonReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare frozen paired sidecar slice locks against the v28 control."
    )
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--pattern", default="paired_sidecar_slice_oos_PSLICELOCK*_latest.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_lock_comparison(
        report_dir=args.report_dir,
        pattern=args.pattern,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_slice_lock_comparison(report)
    print(f"report_count={report.report_count}")
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"promotion_safe_count={report.promotion_safe_count}")
    print(f"particle_like_count={report.particle_like_count}")
    print(f"particle_edge_candidate_count={report.particle_edge_candidate_count}")
    print(f"best_selected_pnl_hypothesis_id={report.best_selected_pnl_hypothesis_id}")
    print(f"best_selected_pnl_cents={report.best_selected_pnl_cents:.4f}")
    print(f"best_v28_brier_delta_hypothesis_id={report.best_v28_brier_delta_hypothesis_id}")
    print(f"best_v28_brier_delta={report.best_v28_brier_delta}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _comparison_row(payload: Mapping[str, Any]) -> SliceLockComparisonRow:
    selected = _mapping(payload.get("selected_metrics"))
    baselines = [_mapping(item) for item in payload.get("baseline_metrics") or []]
    by_model = {str(item.get("model") or ""): item for item in baselines}
    model = str(payload.get("model") or selected.get("model") or "")
    v28 = by_model.get("v28")
    particle_like = model not in {"", "v28", "market_side_ask", "candle_brownian"}
    brier = _float(selected.get("brier"))
    logloss = _float(selected.get("logloss"))
    selected_pnl = _float(selected.get("selected_pnl_cents"))
    top_ev_pnl = _float(selected.get("top_ev_bucket_pnl_cents"))
    v28_brier_delta = None if v28 is None else brier - _float(v28.get("brier"))
    v28_logloss_delta = None if v28 is None else logloss - _float(v28.get("logloss"))
    v28_selected_delta = None if v28 is None else selected_pnl - _float(v28.get("selected_pnl_cents"))
    v28_top_ev_delta = None if v28 is None else top_ev_pnl - _float(v28.get("top_ev_bucket_pnl_cents"))
    beats_v28_brier = bool(v28_brier_delta is not None and v28_brier_delta < 0.0)
    beats_v28_logloss = bool(v28_logloss_delta is not None and v28_logloss_delta < 0.0)
    beats_v28_selected = bool(v28_selected_delta is not None and v28_selected_delta > 0.0)
    beats_v28_top = bool(v28_top_ev_delta is not None and v28_top_ev_delta > 0.0)
    return SliceLockComparisonRow(
        hypothesis_id=str(payload.get("hypothesis_id") or ""),
        model=model,
        bucket=str(payload.get("bucket") or ""),
        locked_after_utc=str(payload.get("locked_after_utc") or ""),
        promotion_safe=bool(payload.get("promotion_safe")),
        fresh_candidate_rows=int(payload.get("fresh_candidate_rows", 0) or 0),
        fresh_markets=int(payload.get("fresh_markets", 0) or 0),
        slice_rows=int(payload.get("slice_rows", 0) or 0),
        slice_markets=int(payload.get("slice_markets", 0) or 0),
        selected_count=int(selected.get("selected_count", 0) or 0),
        selected_pnl_cents=selected_pnl,
        top_ev_bucket_pnl_cents=top_ev_pnl,
        brier=brier,
        logloss=logloss,
        ev_rank_correlation=_float(selected.get("ev_rank_correlation")),
        v28_brier_delta=v28_brier_delta,
        v28_logloss_delta=v28_logloss_delta,
        v28_selected_pnl_delta_cents=v28_selected_delta,
        v28_top_ev_pnl_delta_cents=v28_top_ev_delta,
        beats_v28_brier=beats_v28_brier,
        beats_v28_logloss=beats_v28_logloss,
        beats_v28_selected_pnl=beats_v28_selected,
        beats_v28_top_ev_pnl=beats_v28_top,
        particle_like_model=particle_like,
        particle_edge_candidate=bool(
            particle_like
            and beats_v28_brier
            and beats_v28_logloss
            and beats_v28_selected
            and beats_v28_top
            and bool(payload.get("promotion_safe"))
        ),
    )


def _conclusion(rows: tuple[SliceLockComparisonRow, ...], edge_rows: list[SliceLockComparisonRow]) -> str:
    if not rows:
        return "No slice lock reports found."
    if edge_rows:
        names = ", ".join(row.hypothesis_id for row in edge_rows)
        return f"Diagnostic only: {names} clears the particle-vs-v28 comparison screen, but live promotion still depends on the broader goal audit."
    positive = [row for row in rows if row.selected_pnl_cents > 0]
    if positive:
        names = ", ".join(row.hypothesis_id for row in positive)
        return (
            "Positive locked-slice PnL exists, but no particle-like lock beats v28 "
            f"on Brier, log-loss, selected PnL, top-EV PnL, and promotion gates. Positive rows: {names}."
        )
    return "No slice lock has positive selected PnL yet; all remain non-promotable."


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    if parsed != parsed:
        return 0.0
    return parsed


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SliceLockComparisonReport) -> str:
    lines = [
        "# Paired Sidecar Slice Lock Comparison",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- report_count: `{report.report_count}`",
        f"- promotion_safe_count: `{report.promotion_safe_count}`",
        f"- particle_like_count: `{report.particle_like_count}`",
        f"- particle_edge_candidate_count: `{report.particle_edge_candidate_count}`",
        f"- best_selected_pnl_hypothesis_id: `{report.best_selected_pnl_hypothesis_id}`",
        f"- best_selected_pnl_cents: `{report.best_selected_pnl_cents:.1f}`",
        f"- best_v28_brier_delta_hypothesis_id: `{report.best_v28_brier_delta_hypothesis_id}`",
        f"- best_v28_brier_delta: `{_fmt_optional(report.best_v28_brier_delta)}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | rows/markets | selected | pnl c | top EV c | Brier | logloss | dBrier vs v28 | dLogloss vs v28 | dPnL vs v28 | particle edge | safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
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
            f"`{row.brier:.6f}` | "
            f"`{row.logloss:.6f}` | "
            f"`{_fmt_optional(row.v28_brier_delta)}` | "
            f"`{_fmt_optional(row.v28_logloss_delta)}` | "
            f"`{_fmt_optional(row.v28_selected_pnl_delta_cents)}` | "
            f"`{row.particle_edge_candidate}` | "
            f"`{row.promotion_safe}` |"
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
