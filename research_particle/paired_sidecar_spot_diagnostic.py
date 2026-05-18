from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .terminal_projection import brownian_terminal_probability


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABELED_CSV = ROOT / "research_particle" / "v28_successor" / "sidecar_bundle_batch_labeled_latest.csv"


@dataclass(frozen=True)
class SidecarSpotDiagnosticSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    enriched_csv: str
    labeled_csv: str
    output_json: str
    output_md: str
    annualized_vol: float
    enriched_rows_read: int
    joined_rows: int
    joined_markets: int
    issue_count: int
    diagnostic_ready: bool
    candidate_ready_for_predeclared_shadow: bool
    best_model_by_brier: str
    best_model_by_logloss: str
    best_model_by_pnl: str
    tick_brownian_delta_brier_vs_candle: float | None
    tick_brownian_delta_logloss_vs_candle: float | None


MODEL_FIELDS = [
    "candidate",
    "v28",
    "candle_brownian",
    "tick_brownian",
    "market_side_ask",
]


def build_sidecar_spot_diagnostic(
    *,
    enriched_csv: Path,
    labeled_csv: Path = DEFAULT_LABELED_CSV,
    output_json: Path | None = None,
    output_md: Path | None = None,
    annualized_vol: float = 0.65,
    min_rows_for_shadow: int = 200,
    min_markets_for_shadow: int = 40,
) -> tuple[SidecarSpotDiagnosticSummary, list[dict[str, Any]], list[dict[str, Any]]]:
    output_json = output_json or enriched_csv.with_name("sidecar_spot_tick_vs_candle_diagnostic.json")
    output_md = output_md or enriched_csv.with_name("sidecar_spot_tick_vs_candle_diagnostic.md")
    enriched_rows = _read_csv_rows(enriched_csv)
    labels = _labels_by_key(_read_csv_rows(labeled_csv))
    diagnostic_rows: list[dict[str, Any]] = []
    issue_count = 0
    for row in enriched_rows:
        label = labels.get(_row_key(row))
        if not label:
            issue_count += 1
            continue
        try:
            diagnostic_rows.append(_diagnostic_row(row, label, annualized_vol=annualized_vol))
        except Exception:
            issue_count += 1
    model_rows = _model_summaries(diagnostic_rows)
    joined_markets = len({row["market_ticker"] for row in diagnostic_rows})
    by_model = {row["model"]: row for row in model_rows}
    best_brier = min(model_rows, key=lambda row: float(row["brier"]), default={})
    best_logloss = min(model_rows, key=lambda row: float(row["logloss"]), default={})
    best_pnl = max(model_rows, key=lambda row: float(row["top_ev_bucket_pnl_cents"]), default={})
    candle = by_model.get("candle_brownian")
    tick = by_model.get("tick_brownian")
    summary = SidecarSpotDiagnosticSummary(
        schema_version="sidecar-spot-tick-vs-candle-diagnostic-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "tick-vs-candle sidecar diagnostic is underpowered instrumentation evidence; promotion requires locked OOS probability, EV-rank, and PnL gates",
        },
        enriched_csv=str(enriched_csv),
        labeled_csv=str(labeled_csv),
        output_json=str(output_json),
        output_md=str(output_md),
        annualized_vol=float(annualized_vol),
        enriched_rows_read=len(enriched_rows),
        joined_rows=len(diagnostic_rows),
        joined_markets=joined_markets,
        issue_count=issue_count,
        diagnostic_ready=bool(diagnostic_rows),
        candidate_ready_for_predeclared_shadow=(
            len(diagnostic_rows) >= min_rows_for_shadow and joined_markets >= min_markets_for_shadow
        ),
        best_model_by_brier=str(best_brier.get("model", "")),
        best_model_by_logloss=str(best_logloss.get("model", "")),
        best_model_by_pnl=str(best_pnl.get("model", "")),
        tick_brownian_delta_brier_vs_candle=(
            float(tick["brier"]) - float(candle["brier"])
            if tick and candle
            else None
        ),
        tick_brownian_delta_logloss_vs_candle=(
            float(tick["logloss"]) - float(candle["logloss"])
            if tick and candle
            else None
        ),
    )
    return summary, model_rows, diagnostic_rows


def write_sidecar_spot_diagnostic(
    summary: SidecarSpotDiagnosticSummary,
    model_rows: list[dict[str, Any]],
    diagnostic_rows: list[dict[str, Any]],
) -> None:
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(
            {
                "summary": asdict(summary),
                "model_rows": model_rows,
                "diagnostic_rows": diagnostic_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary, model_rows), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare stale candle spot and no-future independent tick spot on settled sidecar packets."
    )
    parser.add_argument("--enriched-csv", required=True, type=Path)
    parser.add_argument("--labeled-csv", type=Path, default=DEFAULT_LABELED_CSV)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--annualized-vol", type=float, default=0.65)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary, model_rows, diagnostic_rows = build_sidecar_spot_diagnostic(
        enriched_csv=args.enriched_csv,
        labeled_csv=args.labeled_csv,
        output_json=args.output_json,
        output_md=args.output_md,
        annualized_vol=args.annualized_vol,
    )
    if args.write:
        write_sidecar_spot_diagnostic(summary, model_rows, diagnostic_rows)
    print(f"diagnostic_ready={summary.diagnostic_ready}")
    print(f"candidate_ready_for_predeclared_shadow={summary.candidate_ready_for_predeclared_shadow}")
    print(f"joined_rows={summary.joined_rows}")
    print(f"joined_markets={summary.joined_markets}")
    print(f"best_model_by_brier={summary.best_model_by_brier}")
    print(f"best_model_by_logloss={summary.best_model_by_logloss}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"output_json={summary.output_json}")
    return 0


def _diagnostic_row(
    row: Mapping[str, Any],
    label: Mapping[str, Any],
    *,
    annualized_vol: float,
) -> dict[str, Any]:
    y_yes = 1 if _truthy(label.get("y_yes_win")) else 0
    strike = _required_float(row.get("strike"), "strike")
    seconds_to_close = _required_float(row.get("seconds_to_close"), "seconds_to_close")
    candle_spot = _required_float(row.get("btc_spot"), "btc_spot")
    tick_spot = _required_float(row.get("independent_spot_price"), "independent_spot_price")
    candle_brownian = brownian_terminal_probability(candle_spot, strike, seconds_to_close, annualized_vol)
    tick_brownian = brownian_terminal_probability(tick_spot, strike, seconds_to_close, annualized_vol)
    side = str(row.get("side") or "").lower()
    ask = _required_float(row.get("ask_cents"), "ask_cents")
    probs = {
        "candidate": _required_float(row.get("candidate_p_yes"), "candidate_p_yes"),
        "v28": _required_float(row.get("v28_p_yes"), "v28_p_yes"),
        "candle_brownian": candle_brownian,
        "tick_brownian": tick_brownian,
        "market_side_ask": _market_p_yes(row),
    }
    out = {
        "row_id": row.get("row_id", ""),
        "market_ticker": row.get("market_ticker", ""),
        "decision_ts_utc": row.get("decision_ts_utc", ""),
        "side": side,
        "candidate_id": row.get("candidate_id", ""),
        "y_yes_win": y_yes,
        "ask_cents": ask,
        "candle_spot": candle_spot,
        "tick_spot": tick_spot,
        "spot_delta_bps": _safe_float(row.get("independent_spot_vs_candle_bps")),
        "independent_spot_age_ms": _safe_float(row.get("independent_spot_age_ms")),
    }
    for model, p_yes in probs.items():
        p_side = p_yes if side == "yes" else 1.0 - p_yes
        side_won = bool(y_yes) if side == "yes" else not bool(y_yes)
        ev = p_side * 100.0 - ask
        pnl = (100.0 - ask) if side_won else -ask
        out[f"{model}_p_yes"] = p_yes
        out[f"{model}_brier"] = _brier(p_yes, y_yes)
        out[f"{model}_logloss"] = _logloss(p_yes, y_yes)
        out[f"{model}_side_ev_cents"] = ev
        out[f"{model}_side_pnl_if_selected_cents"] = pnl if ev > 0.0 else 0.0
    return out


def _model_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for model in MODEL_FIELDS:
        if not rows:
            summaries.append(_empty_summary(model))
            continue
        brier = _mean(float(row[f"{model}_brier"]) for row in rows)
        logloss = _mean(float(row[f"{model}_logloss"]) for row in rows)
        evs = [float(row[f"{model}_side_ev_cents"]) for row in rows]
        pnls = [float(row[f"{model}_side_pnl_if_selected_cents"]) for row in rows]
        selected = [pnl for ev, pnl in zip(evs, pnls) if ev > 0.0]
        top_count = max(1, math.ceil(len(rows) * 0.2))
        ranked = sorted(
            zip(evs, pnls),
            key=lambda item: item[0],
            reverse=True,
        )[:top_count]
        summaries.append(
            {
                "model": model,
                "rows": len(rows),
                "markets": len({row["market_ticker"] for row in rows}),
                "brier": brier,
                "logloss": logloss,
                "mean_side_ev_cents": _mean(evs),
                "selected_count": len(selected),
                "selected_pnl_cents": sum(selected),
                "top_ev_bucket_count": len(ranked),
                "top_ev_bucket_pnl_cents": sum(pnl for _ev, pnl in ranked),
                "promotion_safe": False,
            }
        )
    return summaries


def _empty_summary(model: str) -> dict[str, Any]:
    return {
        "model": model,
        "rows": 0,
        "markets": 0,
        "brier": 0.0,
        "logloss": 0.0,
        "mean_side_ev_cents": 0.0,
        "selected_count": 0,
        "selected_pnl_cents": 0.0,
        "top_ev_bucket_count": 0,
        "top_ev_bucket_pnl_cents": 0.0,
        "promotion_safe": False,
    }


def _labels_by_key(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    return {_row_key(row): row for row in rows if str(row.get("label_join_status") or "") == "joined_post_resolution"}


def _row_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("row_id") or ""),
        str(row.get("market_ticker") or ""),
        str(row.get("candidate_id") or ""),
        str(row.get("side") or "").lower(),
    )


def _market_p_yes(row: Mapping[str, Any]) -> float:
    implied = _required_float(row.get("book_implied_yes_from_side_ask"), "book_implied_yes_from_side_ask")
    if 0.0 <= implied <= 1.0:
        return implied
    if 0.0 <= implied <= 100.0:
        return implied / 100.0
    return implied


def _brier(p: float, y: int) -> float:
    return (min(1.0, max(0.0, p)) - y) ** 2


def _logloss(p: float, y: int) -> float:
    p = min(1.0 - 1e-12, max(1e-12, p))
    return -(y * math.log(p) + (1 - y) * math.log(1.0 - p))


def _mean(values: Any) -> float:
    seq = list(values)
    return sum(seq) / len(seq) if seq else 0.0


def _required_float(value: Any, name: str) -> float:
    parsed = _safe_float(value)
    if parsed is None:
        raise ValueError(f"missing numeric {name}")
    return parsed


def _safe_float(value: Any) -> float | None:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _markdown(summary: SidecarSpotDiagnosticSummary, model_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Sidecar Spot Tick vs Candle Diagnostic",
        "",
        "Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary.generated_utc}`",
        f"- Promotion allowed: `{summary.promotion_allowed}`",
        f"- Diagnostic ready: `{summary.diagnostic_ready}`",
        f"- Candidate ready for predeclared shadow: `{summary.candidate_ready_for_predeclared_shadow}`",
        f"- Joined rows / markets: `{summary.joined_rows}` / `{summary.joined_markets}`",
        f"- Issue count: `{summary.issue_count}`",
        f"- Best model by Brier: `{summary.best_model_by_brier}`",
        f"- Best model by log loss: `{summary.best_model_by_logloss}`",
        f"- Tick Brownian delta Brier vs candle: `{summary.tick_brownian_delta_brier_vs_candle}`",
        f"- Tick Brownian delta log loss vs candle: `{summary.tick_brownian_delta_logloss_vs_candle}`",
        "",
        "## Model Rows",
        "",
        "| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            f"| `{row['model']}` | {row['rows']} | {row['markets']} | {row['brier']} | "
            f"{row['logloss']} | {row['selected_count']} | {row['selected_pnl_cents']} | "
            f"{row['top_ev_bucket_pnl_cents']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.",
            "- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
