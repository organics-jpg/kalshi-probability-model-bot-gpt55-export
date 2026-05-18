from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig
from research_particle.rv600_variation_test import build_rv600_variation_report


DEFAULT_REAL_SHADOW_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_parameter_plateau_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_parameter_plateau_audit_latest.md")

WINDOW_ORDER = (
    "late_70_180",
    "late_70_240",
    "late_70_300",
    "base_70_420",
    "mid_120_420",
    "mid_180_420",
    "broad_70_600",
)
EV_ORDER = (0, 2, 4, 6, 8, 10, 12, 15, 20)
VARIANT_RE = re.compile(
    r"^(?P<prefix>.+)_(?P<window>late_70_180|late_70_240|late_70_300|base_70_420|mid_120_420|mid_180_420|broad_70_600)_ev(?P<ev>\d+)$"
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_variant(variant: str) -> dict[str, Any] | None:
    match = VARIANT_RE.match(variant)
    if not match:
        return None
    window = match.group("window")
    ev = int(match.group("ev"))
    if window not in WINDOW_ORDER or ev not in EV_ORDER:
        return None
    return {
        "prefix": match.group("prefix"),
        "window": window,
        "window_idx": WINDOW_ORDER.index(window),
        "ev": ev,
        "ev_idx": EV_ORDER.index(ev),
    }


def _compact_row(row: dict[str, Any]) -> dict[str, Any]:
    parsed = _parse_variant(str(row.get("variant") or "")) or {}
    return {
        "variant": row.get("variant"),
        "prefix": parsed.get("prefix"),
        "window": parsed.get("window"),
        "ev": parsed.get("ev"),
        "accounting_mode": row.get("accounting_mode"),
        "gate_count": _int(row.get("gate_count")),
        "accepted_entries": _int(row.get("accepted_entries")),
        "distinct_markets": _int(row.get("distinct_markets")),
        "selected_pnl_cents": _float(row.get("selected_pnl_cents")),
        "matched_v28_delta_cents": _float(row.get("matched_v28_delta_cents")),
        "avg_pnl_per_entry_cents": _float(row.get("avg_pnl_per_entry_cents")),
        "positive_root_rate": _float(row.get("positive_root_rate")),
        "positive_market_rate": _float(row.get("positive_market_rate")),
        "max_single_market_pnl_share": _float(row.get("max_single_market_pnl_share")),
        "last_window_pnl_cents": _float(row.get("last_window_pnl_cents")),
        "rejection_reason": row.get("rejection_reason") or "",
    }


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _base_gate_ok(row: dict[str, Any]) -> bool:
    return (
        row.get("accounting_mode") == "position_capped"
        and _int(row.get("gate_count")) <= 3
        and _int(row.get("accepted_entries")) >= 25
        and _float(row.get("selected_pnl_cents")) > 0.0
        and _float(row.get("matched_v28_delta_cents")) > 0.0
        and _float(row.get("avg_pnl_per_entry_cents")) >= 10.0
        and _float(row.get("avg_pnl_per_market_cents")) > 0.0
        and _float(row.get("max_single_market_pnl_share")) <= 0.25
        and _float(row.get("last_window_pnl_cents")) > 0.0
    )


def _rejection_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for item in str(row.get("rejection_reason") or "").split(";"):
            if item:
                counter[item] += 1
    return dict(counter.most_common(8))


def _grid_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.grid_json is not None:
        return _load_json(args.grid_json), {"grid_json": str(args.grid_json)}
    roots = tuple(
        args.root
        or discover_roots(args.base_dir, args.reports_dir, args.min_root_name)
    )
    variation_report = build_rv600_variation_report(
        roots,
        phase="grid",
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=(
            _parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None
        ),
    )
    return (
        {
            "generated_utc": variation_report.generated_utc,
            "phase": variation_report.phase,
            "root_count": variation_report.root_count,
            "roots": list(variation_report.roots),
            "variant_count": variation_report.variant_count,
            "summary_rows": [asdict(row) for row in variation_report.summary_rows],
        },
        {
            "source": "settled_bounded_roots",
            "roots": [str(root) for root in roots],
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
        },
    )


def _plateau_for(center: dict[str, Any], by_key: dict[tuple[str, int, int, str], dict[str, Any]]) -> dict[str, Any]:
    parsed = _parse_variant(str(center.get("variant") or ""))
    if not parsed:
        return {}
    neighbors: list[dict[str, Any]] = []
    for window_idx in range(parsed["window_idx"] - 1, parsed["window_idx"] + 2):
        for ev_idx in range(parsed["ev_idx"] - 1, parsed["ev_idx"] + 2):
            key = (parsed["prefix"], window_idx, ev_idx, str(center.get("accounting_mode")))
            row = by_key.get(key)
            if row is not None:
                neighbors.append(row)
    positive_pnl = [row for row in neighbors if _float(row.get("selected_pnl_cents")) > 0.0]
    positive_delta = [row for row in neighbors if _float(row.get("matched_v28_delta_cents")) > 0.0]
    breadth_ok = [
        row
        for row in neighbors
        if _float(row.get("positive_root_rate")) >= 0.60
        and _float(row.get("positive_market_rate")) >= 0.60
    ]
    base_gate = [row for row in neighbors if _base_gate_ok(row)]
    support = (
        _base_gate_ok(center)
        and len(neighbors) >= 4
        and len(positive_pnl) / len(neighbors) >= 0.75
        and len(positive_delta) / len(neighbors) >= 0.75
        and len(breadth_ok) / len(neighbors) >= 0.50
        and len(base_gate) >= 2
        and _median([_float(row.get("positive_root_rate")) for row in neighbors]) >= 0.55
        and _median([_float(row.get("positive_market_rate")) for row in neighbors]) >= 0.55
    )
    return {
        "center": _compact_row(center),
        "neighborhood_size": len(neighbors),
        "positive_pnl_rate": len(positive_pnl) / len(neighbors) if neighbors else 0.0,
        "positive_delta_rate": len(positive_delta) / len(neighbors) if neighbors else 0.0,
        "breadth_ok_rate": len(breadth_ok) / len(neighbors) if neighbors else 0.0,
        "base_gate_neighbor_count": len(base_gate),
        "median_selected_pnl_cents": _median([_float(row.get("selected_pnl_cents")) for row in neighbors]),
        "median_matched_v28_delta_cents": _median(
            [_float(row.get("matched_v28_delta_cents")) for row in neighbors]
        ),
        "median_positive_root_rate": _median([_float(row.get("positive_root_rate")) for row in neighbors]),
        "median_positive_market_rate": _median([_float(row.get("positive_market_rate")) for row in neighbors]),
        "max_neighbor_single_market_share": max(
            [_float(row.get("max_single_market_pnl_share")) for row in neighbors],
            default=0.0,
        ),
        "neighbor_rejection_counts": _rejection_counts(neighbors),
        "support": support,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    grid, grid_input = _grid_payload(args)
    rows = list(grid.get("summary_rows") or [])
    if not rows:
        raise SystemExit("grid report has no summary_rows")
    parsed_rows = []
    by_key: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in rows:
        parsed = _parse_variant(str(row.get("variant") or ""))
        if not parsed:
            continue
        if row.get("accounting_mode") != "position_capped":
            continue
        parsed_rows.append(row)
        key = (
            str(parsed["prefix"]),
            int(parsed["window_idx"]),
            int(parsed["ev_idx"]),
            str(row.get("accounting_mode")),
        )
        by_key[key] = row
    candidates = sorted(
        parsed_rows,
        key=lambda row: (
            _base_gate_ok(row),
            _float(row.get("matched_v28_delta_cents")),
            _float(row.get("selected_pnl_cents")),
            _float(row.get("avg_pnl_per_entry_cents")),
        ),
        reverse=True,
    )
    plateaus = [_plateau_for(row, by_key) for row in candidates[: int(args.max_centers)]]
    plateaus = [row for row in plateaus if row]
    support_plateaus = [row for row in plateaus if row["support"]]
    best_by_score = sorted(
        plateaus,
        key=lambda row: (
            row["support"],
            row["breadth_ok_rate"],
            row["positive_delta_rate"],
            row["median_matched_v28_delta_cents"],
            row["median_selected_pnl_cents"],
        ),
        reverse=True,
    )
    decision = "parameter_plateau_support_found" if support_plateaus else "parameter_plateau_rejected"
    report = {
        "schema_version": "rv600-parameter-plateau-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "modeling_choice": (
            "Use a local parameter-neighborhood plateau test over existing RV600 grid variants. "
            "A candidate is not supported unless nearby timing-window and EV-threshold variants "
            "also retain positive PnL, matched-v28 edge, and root/market breadth. This targets "
            "fragile single-row selection without adding a new live strategy family."
        ),
        "sources_considered": [
            {
                "label": "selected: parameter stability / robust optimization plateau heuristic",
                "url": "https://quanthop.com/learn/validation-robustness/stability-testing",
                "reason": "Directly motivates preferring broad parameter plateaus over isolated optima.",
            },
            {
                "label": "supporting: Probability of Backtest Overfitting / CSCV",
                "url": "https://core.ac.uk/display/24041876",
                "reason": "Motivates rejecting parameter choices that do not keep out-of-sample rank across splits.",
            },
            {
                "label": "supporting: Model Confidence Set",
                "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=522382",
                "reason": "Motivates treating several statistically indistinguishable candidate rules as a set.",
            },
            {
                "label": "supporting: Stability Selection",
                "url": "https://arxiv.org/abs/0809.2932",
                "reason": "Motivates requiring repeated support under nearby/subsampled selections.",
            },
            {
                "label": "not selected as implementation: online expert weighting",
                "url": "https://arxiv.org/search/cs?query=online+learning+expert+advice+trading+transaction+costs&searchtype=all",
                "reason": "Already covered by the online-expert rescue; the current blocker is parameter fragility.",
            },
        ],
        "grid": {
            "generated_utc": grid.get("generated_utc") or "",
            "phase": grid.get("phase") or "",
            "root_count": _int(grid.get("root_count")),
            "variant_count": _int(grid.get("variant_count")),
            "summary_row_count": len(rows),
            "position_capped_parsed_row_count": len(parsed_rows),
        },
        "thresholds": {
            "min_neighbors": 4,
            "min_positive_pnl_rate": 0.75,
            "min_positive_delta_rate": 0.75,
            "min_breadth_ok_rate": 0.50,
            "min_base_gate_neighbors": 2,
            "min_median_positive_root_rate": 0.55,
            "min_median_positive_market_rate": 0.55,
        },
        "support_count": len(support_plateaus),
        "best_plateaus": best_by_score[:10],
        "interpretation": _interpretation(decision, best_by_score),
        "inputs": {
            **grid_input,
            "grid_json": str(args.grid_json) if args.grid_json else "",
            "output_json": str(args.output_json),
            "output_md": str(args.output_md),
        },
    }
    return report


def _interpretation(decision: str, plateaus: list[dict[str, Any]]) -> str:
    if decision == "parameter_plateau_support_found":
        return (
            "At least one RV600 candidate has local parameter-neighborhood support. Freeze the simplest "
            "supported center before counting any new forward-shadow evidence."
        )
    if not plateaus:
        return "No parseable RV600 parameter neighborhoods were available."
    best = plateaus[0]
    center = best["center"]
    return (
        "No RV600 candidate has a stable local parameter plateau. The best neighborhood still fails "
        f"breadth support: center={center.get('variant')}, median_positive_root_rate="
        f"{best['median_positive_root_rate']:.3f}, median_positive_market_rate="
        f"{best['median_positive_market_rate']:.3f}, breadth_ok_rate={best['breadth_ok_rate']:.3f}."
    )


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RV600 Parameter Plateau Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- support_count: {report['support_count']}",
        "",
        "## Modeling Choice",
        "",
        report["modeling_choice"],
        "",
        "## Sources Considered",
        "",
    ]
    for source in report["sources_considered"]:
        lines.append(f"- {source['label']}: {source['url']} - {source['reason']}")
    grid = report["grid"]
    thresholds = report["thresholds"]
    lines.extend(
        [
            "",
            "## Grid",
            "",
            f"- root_count: {grid['root_count']}",
            f"- variant_count: {grid['variant_count']}",
            f"- summary_row_count: {grid['summary_row_count']}",
            f"- position_capped_parsed_row_count: {grid['position_capped_parsed_row_count']}",
            "",
            "## Thresholds",
            "",
        ]
    )
    for key, value in thresholds.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Best Plateaus",
            "",
            "| support | center | neighbors | pos pnl | pos delta | breadth | median pnl | median delta | median root | median market | rejection counts |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for plateau in report["best_plateaus"]:
        center = plateau["center"]
        rejection_counts = "; ".join(
            f"{key}={value}" for key, value in plateau["neighbor_rejection_counts"].items()
        )
        row = {
            **plateau,
            "variant": center["variant"],
            "rejection_counts": rejection_counts,
        }
        lines.append(
            "| {support} | `{variant}` | {neighborhood_size} | {positive_pnl_rate:.2f} | {positive_delta_rate:.2f} | {breadth_ok_rate:.2f} | {median_selected_pnl_cents:.1f} | {median_matched_v28_delta_cents:.1f} | {median_positive_root_rate:.2f} | {median_positive_market_rate:.2f} | `{rejection_counts}` |".format(
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit RV600 local parameter plateau stability.")
    parser.add_argument("--grid-json", type=Path, default=None)
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_REAL_SHADOW_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--max-centers", type=int, default=250)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"support_count={report['support_count']}")
    best = (report.get("best_plateaus") or [{}])[0]
    if best:
        center = best.get("center") or {}
        print(f"best_center={center.get('variant')}")
        print(f"best_breadth_ok_rate={best.get('breadth_ok_rate'):.4f}")
        print(f"best_median_positive_root_rate={best.get('median_positive_root_rate'):.4f}")
        print(f"best_median_positive_market_rate={best.get('median_positive_market_rate'):.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
