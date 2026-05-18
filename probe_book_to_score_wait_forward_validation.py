"""Forward validation for locked book-to-score wait candidate.

Research-only: no orders are submitted and no bot files or live processes are
modified. Recomputed fresh rows are diagnostic; strict pre-registered rows are
the promotion authority.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_lock_pending_signal_monitor import (
    BOOK_EARLY_SCORE_GAP020_WAIT_LOCK_PATH,
    BOOK_SCORE_GAP020_WAIT_LOCK_PATH,
    select_book_to_score_wait_rows,
)
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_v2_conditional_wait_forward_validation import (
    metric_for_strict_registry,
    metric_row,
    registry_recompute_divergence,
    strict_registry_rows,
)


VALIDATION_SPECS = [
    {
        "name": "book_early_score_gap020_wait",
        "title": "Book Early Score Gap020 Wait",
        "lock_path": BOOK_EARLY_SCORE_GAP020_WAIT_LOCK_PATH,
        "report_stem": "profit_book_early_score_gap020_wait_validation",
    },
    {
        "name": "book_score_gap020_wait",
        "title": "Book Score Gap020 Wait",
        "lock_path": BOOK_SCORE_GAP020_WAIT_LOCK_PATH,
        "report_stem": "profit_book_score_gap020_wait_validation",
    },
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_lock(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def select_for_validation(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return enrich_selected(select_book_to_score_wait_rows(rows, lock))


def fresh_scope(
    side_rows: pd.DataFrame,
    base: pd.DataFrame,
    lock: Dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    boundary = effective_lock_dt(lock)
    if pd.isna(boundary):
        return base.iloc[0:0].copy(), base.iloc[0:0].copy()
    close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce")
    fresh_base = base[close_dt.gt(boundary)].copy()
    if fresh_base.empty:
        return fresh_base, base.iloc[0:0].copy()
    entry_dt = pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce")
    fresh_side_rows = side_rows[
        entry_dt.gt(boundary) & side_rows["market"].isin(set(fresh_base["market"]))
    ].copy()
    return fresh_base, select_for_validation(fresh_side_rows, fresh_base, lock)


def write_report(
    path: Path,
    generated: str,
    name: str,
    title: str,
    lock_path: Path,
    lock: Dict[str, Any],
    all_metric: Dict[str, Any],
    fresh_metric: Dict[str, Any],
    strict_metric: Dict[str, Any],
    divergence: Dict[str, Any],
) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        f"# {title} Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- The locked candidate requires an early book-margin setup, then waits for a later score_min60_gap020 row.",
        "- Recomputed fresh metrics can drift; strict registered rows are the promotion authority.",
        "",
        "## Locked Policy",
        "",
        f"- Name: `{name}`",
        f"- Wait rule: `{lock.get('wait_rule', {}).get('label')}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{lock_path}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        metric_row("all current ledger", all_metric),
        metric_row("recomputed fresh after lock", fresh_metric),
        metric_row("strict registered fresh", strict_metric),
        "",
        "## Recompute Drift Check",
        "",
        f"- Compared strict and recomputed rows: {divergence['compared']}.",
        f"- Mismatched rows: {divergence['mismatches']}; missing recomputed rows: {divergence['missing_recompute']}.",
    ]
    for example in divergence["examples"]:
        lines.append(f"- `{example['market']}` strict `{example['strict']}` vs recomputed `{example['recomputed']}`.")
    lines += ["", "## Read", ""]
    if strict_metric["base_markets"] == 0:
        lines.append("- The lock is waiting for post-boundary resolved markets.")
    elif strict_metric["positive_net"] and strict_metric["coverage_pass"]:
        lines.append("- Strict registered fresh sample is positive and coverage-valid so far, but sample size is still required.")
    else:
        lines.append("- Strict registered fresh sample is not promotion-quality proof.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = load_side_rows()
    base = market_base(side_rows)
    summaries = []
    for spec in VALIDATION_SPECS:
        name = str(spec["name"])
        title = str(spec["title"])
        lock_path = Path(spec["lock_path"])
        report_stem = str(spec["report_stem"])
        lock = load_lock(lock_path)
        selected = select_for_validation(side_rows, base, lock)
        all_metric = metric_for_scope(base, selected)
        fresh_base, fresh_selected = fresh_scope(side_rows, base, lock)
        fresh_metric = metric_for_scope(fresh_base, fresh_selected)
        boundary = effective_lock_dt(lock)
        strict_rows = strict_registry_rows(name, fresh_base, boundary)
        strict_metric = metric_for_strict_registry(fresh_base, strict_rows)
        divergence = registry_recompute_divergence(fresh_selected, strict_rows)

        md_latest = OUT_DIR / f"{report_stem}_latest.md"
        md_stamp = OUT_DIR / f"{report_stem}_{generated}.md"
        json_latest = OUT_DIR / f"{report_stem}_latest.json"
        json_stamp = OUT_DIR / f"{report_stem}_{generated}.json"
        for path in [md_latest, md_stamp]:
            write_report(path, generated, name, title, lock_path, lock, all_metric, fresh_metric, strict_metric, divergence)
        payload = {
            "generated_utc": generated,
            "name": name,
            "lock": lock,
            "all_metric": all_metric,
            "fresh_metric": fresh_metric,
            "strict_registered_metric": strict_metric,
            "registry_recompute_divergence": divergence,
        }
        for path in [json_latest, json_stamp]:
            path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
        summaries.append((name, md_latest, strict_metric))
    print("Book-to-score wait forward validation complete")
    for name, report, strict_metric in summaries:
        print(
            f"{name}: strict_fresh_markets={int(strict_metric['markets'])} "
            f"fresh_base={int(strict_metric['base_markets'])} "
            f"fresh_net={float(strict_metric['net_pnl_cents'] or 0.0)}c report={report}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
