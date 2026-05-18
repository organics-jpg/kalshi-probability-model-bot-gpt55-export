"""Promotion-gate tests for arXiv/Truffle-inspired v28 candidates.

Research-only. This script applies stricter validation gates suggested by the
Truffle synthesis:

- CPCV-style purged combinatorial test paths
- train-only CPCV parameter selection for each family
- e-process-inspired anytime edge monitoring
- ACI-style adaptive calibration checks

These diagnostics are not live-trading logic. They read recorded v28 data and
write a report under logs/edge_research.
"""
from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable

import probe_arxiv_strategy_projection as projection
import probe_arxiv_strategy_stress_validation as stress
import probe_arxiv_strategy_walkforward_deepening as deepening


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MARKET_RESULTS_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
OUT_JSON = OUT_DIR / "arxiv_strategy_promotion_gates_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_promotion_gates_latest.md"

Predicate = Callable[[dict[str, Any]], bool]

CPCV_FOLDS = 5
CPCV_TEST_FOLDS = 2
CPCV_EMBARGO_TRADES = 12
ACI_TARGET_COVERAGE = 0.90
ACI_ALPHA = 1.0 - ACI_TARGET_COVERAGE
ACI_GAMMA = 0.02
ACI_WARMUP = 50
E_PROCESS_LAMBDAS = (0.05, 0.10, 0.20)
E_PROCESS_SCALE_CENTS = 200.0


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = projection.as_float(value)
    return default if parsed is None else parsed


def ge(value: Any, threshold: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and parsed >= threshold


def le(value: Any, threshold: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and parsed <= threshold


def between(value: Any, low: float, high: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and low <= parsed <= high


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return projection.trade_stats(rows, denominator)


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


def coefficient_of_variation(values: list[float]) -> float | None:
    if not values:
        return None
    avg = mean(values)
    if abs(avg) < 1e-9:
        return None
    return pstdev(values) / abs(avg)


def load_market_results() -> dict[str, str]:
    out: dict[str, str] = {}
    if not MARKET_RESULTS_CSV.exists():
        return out
    with MARKET_RESULTS_CSV.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            result = str(row.get("result") or "").strip().lower()
            status = str(row.get("status") or "").strip().lower()
            if market and result in {"yes", "no"} and status == "finalized":
                out[market] = result
    return out


def load_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics = projection.load_matched_live_trades()
    market_results = load_market_results()
    enriched = []
    for row in rows:
        row = dict(row)
        result = market_results.get(str(row.get("market") or ""))
        side = str(row.get("side") or "").lower()
        if result in {"yes", "no"} and side in {"yes", "no"}:
            row["settlement_result"] = result
            row["side_correct"] = 1 if side == result else 0
            p_side = projection.as_float(row.get("p28"))
            if p_side is not None:
                row["conformal_score"] = abs(float(row["side_correct"]) - p_side)
        enriched.append(row)
    enriched.sort(key=lambda item: item["_entry_dt"])
    diagnostics["settled_label_rows"] = sum(1 for row in enriched if row.get("side_correct") in {0, 1})
    return enriched, diagnostics


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    role: str
    params: dict[str, Any]
    predicate: Predicate


def build_candidates() -> list[Candidate]:
    return [
        Candidate(
            name="brownian_fpt_current",
            family="brownian_fpt_sanity",
            role="FPT sanity gate current replay leader",
            params={"min_edge_cents": 3.0, "min_seconds_to_close": 120.0, "min_abs_d_sigma": 0.70, "max_abs_d_sigma": 1.10},
            predicate=lambda row: ge(row.get("edge28_cents"), 3.0)
            and ge(row.get("seconds_to_close"), 120.0)
            and between(row.get("abs_d_sigma"), 0.70, 1.10),
        ),
        Candidate(
            name="depth_decay_current",
            family="depth_decay_fillability",
            role="Depth-decay/fillability current gate",
            params={"min_depth_ratio": 3.0, "max_book_age_ms": 750.0, "max_ask_cents": 80.0, "min_seconds_to_close": 600.0},
            predicate=lambda row: ge(row.get("depth_ratio"), 3.0)
            and le(row.get("book_age_ms"), 750.0)
            and le(row.get("ask_cents"), 80.0)
            and ge(row.get("seconds_to_close"), 600.0),
        ),
        Candidate(
            name="hybrid_fpt_depth_current",
            family="hybrid_fpt_depth",
            role="Hybrid FPT + fillability current gate",
            params={
                "min_edge_cents": 3.0,
                "min_depth_ratio": 8.0,
                "max_book_age_ms": 750.0,
                "max_ask_cents": 83.0,
                "min_seconds_to_close": 120.0,
                "min_abs_d_sigma": 0.85,
                "max_abs_d_sigma": 1.10,
            },
            predicate=lambda row: ge(row.get("edge28_cents"), 3.0)
            and ge(row.get("depth_ratio"), 8.0)
            and le(row.get("book_age_ms"), 750.0)
            and le(row.get("ask_cents"), 83.0)
            and ge(row.get("seconds_to_close"), 120.0)
            and between(row.get("abs_d_sigma"), 0.85, 1.10),
        ),
        Candidate(
            name="hybrid_fpt_depth_robust_rank1",
            family="hybrid_fpt_depth",
            role="Hybrid robust replay rank 1 from multi-schedule deepening",
            params={
                "min_edge_cents": 3.0,
                "min_depth_ratio": 8.0,
                "max_book_age_ms": 750.0,
                "max_ask_cents": 85.0,
                "min_seconds_to_close": 120.0,
                "min_abs_d_sigma": 0.80,
                "max_abs_d_sigma": 1.10,
            },
            predicate=lambda row: ge(row.get("edge28_cents"), 3.0)
            and ge(row.get("depth_ratio"), 8.0)
            and le(row.get("book_age_ms"), 750.0)
            and le(row.get("ask_cents"), 85.0)
            and ge(row.get("seconds_to_close"), 120.0)
            and between(row.get("abs_d_sigma"), 0.80, 1.10),
        ),
        Candidate(
            name="consensus_gap_robust_rank1",
            family="consensus_probability_gap",
            role="Consensus/disagreement supervisor candidate",
            params={"max_probability_gap": 0.10, "min_edge_cents": 3.0},
            predicate=lambda row: le(row.get("probability_gap"), 0.10) and ge(row.get("edge28_cents"), 3.0),
        ),
    ]


def cpcv_splits(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    n = len(rows)
    fold_ranges = []
    for fold in range(CPCV_FOLDS):
        start = int(fold * n / CPCV_FOLDS)
        end = int((fold + 1) * n / CPCV_FOLDS)
        fold_ranges.append((start, end))
    paths = []
    all_indices = set(range(n))
    for path_id, test_folds in enumerate(itertools.combinations(range(CPCV_FOLDS), CPCV_TEST_FOLDS), start=1):
        test_indices: set[int] = set()
        embargo_indices: set[int] = set()
        for fold in test_folds:
            start, end = fold_ranges[fold]
            test_indices.update(range(start, end))
            embargo_indices.update(range(max(0, start - CPCV_EMBARGO_TRADES), min(n, end + CPCV_EMBARGO_TRADES)))
        train_indices = sorted(all_indices - embargo_indices)
        paths.append(
            {
                "path_id": path_id,
                "test_folds": list(test_folds),
                "train_rows": [rows[idx] for idx in train_indices],
                "test_rows": [rows[idx] for idx in sorted(test_indices)],
                "embargoed_rows": len(embargo_indices - test_indices),
            }
        )
    return paths


def cpcv_fixed_candidate(rows: list[dict[str, Any]], candidate: Candidate) -> dict[str, Any]:
    path_rows = []
    for path in cpcv_splits(rows):
        test_rows = path["test_rows"]
        selected_rows = selected(test_rows, candidate.predicate)
        path_stats = stats(selected_rows, len(test_rows))
        path_rows.append(
            {
                "path_id": path["path_id"],
                "test_folds": path["test_folds"],
                "test_entries": len(test_rows),
                "selected_entries": len(selected_rows),
                "avg_cents_per_entry": path_stats.get("avg_cents_per_entry"),
                "net_cents": path_stats.get("net_cents"),
                "win_rate_ex_flats": path_stats.get("win_rate_ex_flats"),
                "stats": path_stats,
            }
        )
    path_edges = [fnum(row.get("avg_cents_per_entry")) for row in path_rows if row.get("selected_entries")]
    path_nets = [fnum(row.get("net_cents")) for row in path_rows]
    total_positive = sum(value for value in path_nets if value > 0)
    largest_path_share = max(path_nets) / total_positive if total_positive > 0 and path_nets else None
    return {
        "candidate": candidate.name,
        "paths": path_rows,
        "path_count": len(path_rows),
        "positive_paths": sum(1 for value in path_nets if value > 0),
        "median_path_edge_cents": median(path_edges) if path_edges else None,
        "p25_path_edge_cents": quantile(path_edges, 0.25),
        "path_edge_cv": coefficient_of_variation(path_edges),
        "largest_positive_path_share": largest_path_share,
        "passes_cpcv_gate": bool(
            path_edges
            and (median(path_edges) > 0)
            and (quantile(path_edges, 0.25) or -1) > 0
            and (coefficient_of_variation(path_edges) is not None)
            and (coefficient_of_variation(path_edges) or 99) < 0.75
            and (largest_path_share is not None)
            and largest_path_share < 0.50
        ),
    }


def cpcv_dynamic_family(rows: list[dict[str, Any]]) -> dict[str, Any]:
    families = {family.name: family for family in stress.build_families()}
    paths = cpcv_splits(rows)
    out = {}
    for family_name in ("consensus_probability_gap", "depth_decay_fillability", "brownian_fpt_sanity", "hybrid_fpt_depth"):
        family = families[family_name]
        param_pool = deepening.build_param_pool(rows, family)
        path_reports = []
        combined_selected = []
        combined_test = []
        for path in paths:
            params, selection_info = deepening.choose_params(family, param_pool, path["train_rows"], "stable_subsplit")
            test_rows = path["test_rows"]
            if params is None:
                selected_rows: list[dict[str, Any]] = []
                param_dict = None
            else:
                predicate = family.builder(params)
                selected_rows = selected(test_rows, predicate)
                param_dict = {name: value for name, value in zip(family.param_names, params)}
            combined_selected.extend(selected_rows)
            combined_test.extend(test_rows)
            path_stats = stats(selected_rows, len(test_rows))
            live_stats = stats(test_rows, len(test_rows))
            path_reports.append(
                {
                    "path_id": path["path_id"],
                    "test_folds": path["test_folds"],
                    "selected_params": param_dict,
                    "selection_info": selection_info,
                    "test_entries": len(test_rows),
                    "selected_entries": len(selected_rows),
                    "stats": path_stats,
                    "live_stats": live_stats,
                    "delta_vs_live_cents": fnum(path_stats.get("net_cents")) - fnum(live_stats.get("net_cents")),
                }
            )
        combined_stats = stats(combined_selected, len(combined_test))
        combined_live = stats(combined_test, len(combined_test))
        path_nets = [fnum(row["stats"].get("net_cents")) for row in path_reports]
        out[family_name] = {
            "param_pool_size": len(param_pool),
            "paths": path_reports,
            "combined": combined_stats,
            "combined_live": combined_live,
            "positive_paths": sum(1 for value in path_nets if value > 0),
            "beat_live_paths": sum(1 for row in path_reports if fnum(row.get("delta_vs_live_cents")) > 0),
            "median_path_net_cents": median(path_nets) if path_nets else None,
            "min_path_net_cents": min(path_nets) if path_nets else None,
        }
    return out


def e_process(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = []
    for lam in E_PROCESS_LAMBDAS:
        capital = 1.0
        max_capital = 1.0
        cross_20_at = None
        cross_100_at = None
        min_capital = 1.0
        for idx, row in enumerate(rows, start=1):
            clipped = max(-1.0, min(1.0, fnum(row.get("pnl_cents")) / E_PROCESS_SCALE_CENTS))
            capital *= max(0.001, 1.0 + lam * clipped)
            max_capital = max(max_capital, capital)
            min_capital = min(min_capital, capital)
            if cross_20_at is None and capital >= 20.0:
                cross_20_at = idx
            if cross_100_at is None and capital >= 100.0:
                cross_100_at = idx
        outputs.append(
            {
                "lambda": lam,
                "final_capital": capital,
                "max_capital": max_capital,
                "min_capital": min_capital,
                "cross_20_at": cross_20_at,
                "cross_100_at": cross_100_at,
            }
        )
    best = max(outputs, key=lambda item: fnum(item.get("max_capital")))
    return {
        "scale_cents": E_PROCESS_SCALE_CENTS,
        "lambda_rows": outputs,
        "best_max_capital": best.get("max_capital"),
        "best_lambda": best.get("lambda"),
        "crossed_20_any": any(row.get("cross_20_at") for row in outputs),
        "crossed_100_any": any(row.get("cross_100_at") for row in outputs),
    }


def aci_sequence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q = 0.50
    sequence = []
    for idx, row in enumerate(rows, start=1):
        score = projection.as_float(row.get("conformal_score"))
        q_pre = q
        covered = None
        if score is not None:
            covered = score <= q_pre
            miss = 0.0 if covered else 1.0
            q = min(1.0, max(0.01, q + ACI_GAMMA * (miss - ACI_ALPHA)))
        sequence.append(
            {
                "idx": idx,
                "market": row.get("market"),
                "q_pre": q_pre,
                "score": score,
                "covered": covered,
                "pnl_cents": row.get("pnl_cents"),
                "side_correct": row.get("side_correct"),
            }
        )
    return sequence


def aci_for_candidate(all_rows: list[dict[str, Any]], candidate: Candidate) -> dict[str, Any]:
    seq = aci_sequence(all_rows)
    seq_by_idx = {item["idx"]: item for item in seq}
    selected_indices = [idx for idx, row in enumerate(all_rows, start=1) if candidate.predicate(row)]
    selected_seq = [seq_by_idx[idx] for idx in selected_indices if idx in seq_by_idx and idx > ACI_WARMUP]
    usable = [item for item in selected_seq if item.get("covered") is not None]
    if not usable:
        return {"candidate": candidate.name, "usable_rows": 0}
    coverage = sum(1 for item in usable if item["covered"]) / len(usable)
    q_values = [fnum(item.get("q_pre")) for item in usable]
    q_med = median(q_values)
    low_q = [item for item in usable if fnum(item.get("q_pre")) <= q_med]
    high_q = [item for item in usable if fnum(item.get("q_pre")) > q_med]
    low_net = sum(fnum(item.get("pnl_cents")) for item in low_q)
    high_net = sum(fnum(item.get("pnl_cents")) for item in high_q)
    low_hit = sum(1 for item in low_q if item.get("side_correct") == 1) / len(low_q) if low_q else None
    high_hit = sum(1 for item in high_q if item.get("side_correct") == 1) / len(high_q) if high_q else None
    return {
        "candidate": candidate.name,
        "target_coverage": ACI_TARGET_COVERAGE,
        "gamma": ACI_GAMMA,
        "warmup": ACI_WARMUP,
        "usable_rows": len(usable),
        "coverage": coverage,
        "median_q_pre": q_med,
        "low_uncertainty_rows": len(low_q),
        "low_uncertainty_net_cents": low_net,
        "low_uncertainty_side_hit_rate": low_hit,
        "high_uncertainty_rows": len(high_q),
        "high_uncertainty_net_cents": high_net,
        "high_uncertainty_side_hit_rate": high_hit,
        "uncertainty_useful": bool(
            len(low_q) >= 10
            and len(high_q) >= 10
            and low_net > high_net
            and (low_hit is not None)
            and (high_hit is not None)
            and low_hit >= high_hit
        ),
        "passes_coverage_band": 0.85 <= coverage <= 0.95,
    }


def available_feature_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    wanted = {
        "p28": "raw p_model/probability",
        "probability_gap": "model disagreement proxy",
        "conformal_score": "post-outcome conformal score",
        "depth_ratio": "fillability depth/required",
        "book_age_ms": "book freshness",
        "seconds_to_close": "time-to-close",
        "abs_d_sigma": "FPT normalized distance proxy",
        "pnl_cents": "realized after-exit PnL",
        "side_correct": "settlement side correctness",
    }
    missing_future = [
        "native conformal interval width",
        "e_process_value at decision time",
        "ACI threshold q_t at decision time",
        "Brownian FPT probability",
        "jump-diffusion FPT probability",
        "order arrival/cancel/execution counts",
        "queue position",
        "depth decay slope per market",
        "CPCV path ID in live shadow logs",
    ]
    availability = {}
    for key, desc in wanted.items():
        count = sum(1 for row in rows if row.get(key) is not None)
        availability[key] = {"description": desc, "rows_present": count, "share": count / len(rows) if rows else None}
    return {"available": availability, "missing_or_not_native": missing_future}


def build_report() -> dict[str, Any]:
    rows, diagnostics = load_rows()
    candidates = build_candidates()
    candidate_reports = {}
    for candidate in candidates:
        candidate_rows = selected(rows, candidate.predicate)
        candidate_reports[candidate.name] = {
            "family": candidate.family,
            "role": candidate.role,
            "params": candidate.params,
            "all": stats(candidate_rows, len(rows)),
            "cpcv_fixed": cpcv_fixed_candidate(rows, candidate),
            "e_process": e_process(candidate_rows),
            "aci": aci_for_candidate(rows, candidate),
        }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only promotion-gate diagnostics from Truffle arXiv synthesis.",
        "diagnostics": diagnostics,
        "live_baseline": stats(rows, len(rows)),
        "feature_audit": available_feature_audit(rows),
        "cpcv_config": {
            "folds": CPCV_FOLDS,
            "test_folds_per_path": CPCV_TEST_FOLDS,
            "embargo_trades": CPCV_EMBARGO_TRADES,
        },
        "candidate_reports": candidate_reports,
        "dynamic_family_cpcv": cpcv_dynamic_family(rows),
    }


def money(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"{100.0 * parsed:.1f}%"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# arXiv Promotion Gates",
        "",
        "Research-only diagnostics based on the Truffle synthesis. These tests are stricter than the earlier replay reports and should be treated as promotion blockers unless confirmed forward.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Settled labels for ACI: `{report.get('diagnostics', {}).get('settled_label_rows')}`",
        f"- CPCV: `{CPCV_FOLDS}` folds, `{CPCV_TEST_FOLDS}` test folds/path, `{CPCV_EMBARGO_TRADES}` trade embargo",
        "",
        "## Fixed Candidate Gates",
        "",
        "| candidate | replay PnL | W/L | CPCV pass | CPCV pos paths | median path edge | p25 edge | edge CV | e max | e>=20 | ACI cov | ACI useful |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for name, row in (report.get("candidate_reports") or {}).items():
        all_stats = row.get("all") or {}
        cpcv = row.get("cpcv_fixed") or {}
        eproc = row.get("e_process") or {}
        aci = row.get("aci") or {}
        lines.append(
            f"| {name} | {money(all_stats.get('net_dollars'))} | {wl(all_stats)} | "
            f"{cpcv.get('passes_cpcv_gate')} | {cpcv.get('positive_paths')}/{cpcv.get('path_count')} | "
            f"{cents(cpcv.get('median_path_edge_cents'))} | {cents(cpcv.get('p25_path_edge_cents'))} | "
            f"{fnum(cpcv.get('path_edge_cv')):.2f} | {fnum(eproc.get('best_max_capital')):.2f} | "
            f"{eproc.get('crossed_20_any')} | {pct(aci.get('coverage'))} | {aci.get('uncertainty_useful')} |"
        )
    lines.extend(
        [
            "",
            "## Dynamic Family CPCV",
            "",
            "For each CPCV path, parameters are selected on train-only rows using the stable-subsplit rule, then evaluated on the held-out test folds.",
            "",
            "| family | combined PnL | W/L | positive paths | beat-live paths | median path PnL | min path PnL |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for family, row in (report.get("dynamic_family_cpcv") or {}).items():
        combined = row.get("combined") or {}
        lines.append(
            f"| {family} | {money(combined.get('net_dollars'))} | {wl(combined)} | "
            f"{row.get('positive_paths')}/{len(row.get('paths') or [])} | {row.get('beat_live_paths')}/{len(row.get('paths') or [])} | "
            f"{cents(row.get('median_path_net_cents'))} | {cents(row.get('min_path_net_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Feature Recording Audit",
            "",
            "| field | rows present | share |",
            "|---|---:|---:|",
        ]
    )
    for key, value in ((report.get("feature_audit") or {}).get("available") or {}).items():
        lines.append(f"| {key} | {value.get('rows_present')} | {pct(value.get('share'))} |")
    missing = ", ".join((report.get("feature_audit") or {}).get("missing_or_not_native") or [])
    lines.extend(
        [
            "",
            f"Missing/not-native future validation fields: {missing}",
            "",
            "## Interpretation",
            "",
            "- CPCV pass here requires positive median and 25th-percentile path edge, edge CV below 0.75, and no single path contributing more than 50% of positive path PnL.",
            "- The e-process row is an anytime-monitoring approximation over realized PnL, not a theorem-valid proof of edge yet.",
            "- ACI uses settlement side correctness and v28 p_side; it checks whether adaptive uncertainty is calibrated and whether high uncertainty actually marks worse trades.",
            "- Any candidate that looks good here still needs frozen forward shadow collection before live promotion.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
