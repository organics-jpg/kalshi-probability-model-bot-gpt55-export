"""Score settled frozen-forward evidence for v28 successor candidates.

Research-only. This is the probability-first scorer for rows that were:

1. predicted and frozen before market close;
2. joined to labels only after resolution;
3. kept separate from diagnostic/posthoc rows.

The current expected output is blocked/empty because no real frozen forward
rows have settled yet.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

LABELED_CSV = OUT_DIR / "forward_labeled_predictions_latest.csv"
METRICS_CSV = EDGE_DIR / "v28_successor_forward_evidence_metrics_latest.csv"
BINS_CSV = EDGE_DIR / "v28_successor_forward_evidence_bins_latest.csv"
AUDIT_JSON = EDGE_DIR / "v28_successor_forward_evidence_score_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_forward_evidence_score_latest.md"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40
EPS = 1e-9

METRIC_FIELDS = [
    "candidate_id",
    "model_hash",
    "model_type",
    "model_track",
    "slice",
    "rows",
    "markets",
    "candidate_brier",
    "v28_brier",
    "delta_brier_candidate_minus_v28",
    "candidate_logloss",
    "v28_logloss",
    "delta_logloss_candidate_minus_v28",
    "candidate_side_accuracy",
    "v28_side_accuracy",
    "delta_side_accuracy_candidate_minus_v28",
    "candidate_ece_10bin",
    "v28_ece_10bin",
    "candidate_shadow_net_pnl_cents",
    "candidate_shadow_expected_ev_cents",
]

BIN_FIELDS = [
    "candidate_id",
    "probability_source",
    "bin",
    "p_min",
    "p_max",
    "rows",
    "avg_pred",
    "win_rate",
    "brier",
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def clamp_probability(value: Any) -> float | None:
    parsed = as_float(value)
    if parsed is None:
        return None
    return min(1.0 - EPS, max(EPS, parsed))


def brier(p: float | None, y: float | None) -> float | None:
    if p is None or y is None:
        return None
    return (p - y) ** 2


def logloss(p: float | None, y: float | None) -> float | None:
    if p is None or y is None:
        return None
    p = min(1.0 - EPS, max(EPS, p))
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def p_bucket(p: float, bins: int = 10) -> int:
    return min(bins - 1, max(0, int(p * bins)))


def clean_forward_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("label_join_status") or "") != "joined_post_resolution":
            continue
        if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction":
            continue
        if str(row.get("label_join_blockers") or "").strip():
            continue
        if clamp_probability(row.get("candidate_p_yes")) is None or clamp_probability(row.get("v28_p_yes")) is None:
            continue
        if as_float(row.get("y_yes_win")) is None:
            continue
        out.append(row)
    return out


def side_probability(p_yes: float | None, side: str) -> float | None:
    if p_yes is None:
        return None
    if side == "yes":
        return p_yes
    if side == "no":
        return 1.0 - p_yes
    return max(p_yes, 1.0 - p_yes)


def side_label(y_yes: float | None, side: str) -> float | None:
    if y_yes is None:
        return None
    if side == "yes":
        return y_yes
    if side == "no":
        return 1.0 - y_yes
    return y_yes


def row_slice(row: dict[str, Any], slice_name: str) -> bool:
    if slice_name == "all_rows":
        return True
    if slice_name == "near_boundary_abs_d_lte_1":
        abs_d = as_float(row.get("v28_d_sigma"))
        return abs_d is not None and abs(abs_d) <= 1.0
    if slice_name == "late_lte_180s":
        seconds = as_float(row.get("seconds_to_close"))
        return seconds is not None and seconds <= 180.0
    if slice_name == "side_yes":
        return str(row.get("side") or "").lower() == "yes"
    if slice_name == "side_no":
        return str(row.get("side") or "").lower() == "no"
    if slice_name == "book_disagreement_gt_10c":
        book = as_float(row.get("book_implied_yes_from_side_ask"))
        v28 = clamp_probability(row.get("v28_p_yes"))
        return book is not None and v28 is not None and abs(book - v28) >= 0.10
    return False


def expected_calibration_error(rows: list[dict[str, Any]], source: str, bins: int = 10) -> float | None:
    if not rows:
        return None
    total = len(rows)
    ece = 0.0
    key = "candidate_p_yes" if source == "candidate" else "v28_p_yes"
    for bucket in range(bins):
        members = [
            row
            for row in rows
            if (p := clamp_probability(row.get(key))) is not None and p_bucket(p, bins) == bucket
        ]
        if not members:
            continue
        avg_pred = sum(clamp_probability(row.get(key)) or 0.0 for row in members) / len(members)
        win_rate = sum(as_float(row.get("y_yes_win")) or 0.0 for row in members) / len(members)
        ece += len(members) / total * abs(avg_pred - win_rate)
    return ece


def metric_row(rows: list[dict[str, Any]], candidate_id: str, slice_name: str) -> dict[str, Any]:
    selected = [row for row in rows if str(row.get("candidate_id") or "") == candidate_id and row_slice(row, slice_name)]
    if not selected:
        base = next((row for row in rows if str(row.get("candidate_id") or "") == candidate_id), {})
        return {
            "candidate_id": candidate_id,
            "model_hash": base.get("model_hash", ""),
            "model_type": base.get("model_type", ""),
            "model_track": base.get("model_track", ""),
            "slice": slice_name,
            "rows": 0,
            "markets": 0,
            "candidate_brier": None,
            "v28_brier": None,
            "delta_brier_candidate_minus_v28": None,
            "candidate_logloss": None,
            "v28_logloss": None,
            "delta_logloss_candidate_minus_v28": None,
            "candidate_side_accuracy": None,
            "v28_side_accuracy": None,
            "delta_side_accuracy_candidate_minus_v28": None,
            "candidate_ece_10bin": None,
            "v28_ece_10bin": None,
            "candidate_shadow_net_pnl_cents": 0.0,
            "candidate_shadow_expected_ev_cents": 0.0,
        }
    candidate_briers: list[float] = []
    v28_briers: list[float] = []
    candidate_losses: list[float] = []
    v28_losses: list[float] = []
    candidate_side_correct = 0
    v28_side_correct = 0
    side_checked = 0
    shadow_net = 0.0
    shadow_ev = 0.0
    for row in selected:
        y = as_float(row.get("y_yes_win"))
        p_candidate = clamp_probability(row.get("candidate_p_yes"))
        p_v28 = clamp_probability(row.get("v28_p_yes"))
        cand_b = brier(p_candidate, y)
        base_b = brier(p_v28, y)
        cand_l = logloss(p_candidate, y)
        base_l = logloss(p_v28, y)
        if cand_b is not None:
            candidate_briers.append(cand_b)
        if base_b is not None:
            v28_briers.append(base_b)
        if cand_l is not None:
            candidate_losses.append(cand_l)
        if base_l is not None:
            v28_losses.append(base_l)
        side = str(row.get("side") or "").lower()
        side_y = side_label(y, side)
        cand_side_p = side_probability(p_candidate, side)
        v28_side_p = side_probability(p_v28, side)
        if side_y is not None and cand_side_p is not None and v28_side_p is not None:
            side_checked += 1
            candidate_side_correct += int((cand_side_p >= 0.5) == (side_y >= 0.5))
            v28_side_correct += int((v28_side_p >= 0.5) == (side_y >= 0.5))
        ask = as_float(row.get("ask_cents"))
        fair_side = as_float(row.get("candidate_fair_side_cents"))
        if ask is not None and fair_side is not None:
            edge = fair_side - ask
            side_y_for_pnl = side_y
            if edge > 0.0 and side_y_for_pnl is not None:
                shadow_net += 100.0 * side_y_for_pnl - ask
                shadow_ev += edge
    cand_brier = sum(candidate_briers) / len(candidate_briers) if candidate_briers else None
    v28_brier = sum(v28_briers) / len(v28_briers) if v28_briers else None
    cand_logloss = sum(candidate_losses) / len(candidate_losses) if candidate_losses else None
    v28_logloss = sum(v28_losses) / len(v28_losses) if v28_losses else None
    cand_acc = candidate_side_correct / side_checked if side_checked else None
    v28_acc = v28_side_correct / side_checked if side_checked else None
    first = selected[0]
    return {
        "candidate_id": candidate_id,
        "model_hash": first.get("model_hash", ""),
        "model_type": first.get("model_type", ""),
        "model_track": first.get("model_track", ""),
        "slice": slice_name,
        "rows": len(selected),
        "markets": len({row.get("market_ticker") for row in selected}),
        "candidate_brier": cand_brier,
        "v28_brier": v28_brier,
        "delta_brier_candidate_minus_v28": (cand_brier - v28_brier) if cand_brier is not None and v28_brier is not None else None,
        "candidate_logloss": cand_logloss,
        "v28_logloss": v28_logloss,
        "delta_logloss_candidate_minus_v28": (cand_logloss - v28_logloss) if cand_logloss is not None and v28_logloss is not None else None,
        "candidate_side_accuracy": cand_acc,
        "v28_side_accuracy": v28_acc,
        "delta_side_accuracy_candidate_minus_v28": (cand_acc - v28_acc) if cand_acc is not None and v28_acc is not None else None,
        "candidate_ece_10bin": expected_calibration_error(selected, "candidate"),
        "v28_ece_10bin": expected_calibration_error(selected, "v28"),
        "candidate_shadow_net_pnl_cents": shadow_net,
        "candidate_shadow_expected_ev_cents": shadow_ev,
    }


def calibration_bins(rows: list[dict[str, Any]], candidate_id: str, source: str, bins: int = 10) -> list[dict[str, Any]]:
    key = "candidate_p_yes" if source == "candidate" else "v28_p_yes"
    selected = [row for row in rows if str(row.get("candidate_id") or "") == candidate_id]
    out: list[dict[str, Any]] = []
    for bucket in range(bins):
        members = [
            row
            for row in selected
            if (p := clamp_probability(row.get(key))) is not None and p_bucket(p, bins) == bucket
        ]
        if not members:
            out.append(
                {
                    "candidate_id": candidate_id,
                    "probability_source": source,
                    "bin": bucket,
                    "p_min": bucket / bins,
                    "p_max": (bucket + 1) / bins,
                    "rows": 0,
                    "avg_pred": None,
                    "win_rate": None,
                    "brier": None,
                }
            )
            continue
        probs = [clamp_probability(row.get(key)) or 0.0 for row in members]
        labels = [as_float(row.get("y_yes_win")) or 0.0 for row in members]
        out.append(
            {
                "candidate_id": candidate_id,
                "probability_source": source,
                "bin": bucket,
                "p_min": bucket / bins,
                "p_max": (bucket + 1) / bins,
                "rows": len(members),
                "avg_pred": sum(probs) / len(probs),
                "win_rate": sum(labels) / len(labels),
                "brier": sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(members),
            }
        )
    return out


def candidate_gate(metric: dict[str, Any], near_boundary: dict[str, Any] | None) -> dict[str, Any]:
    fail_reasons: list[str] = []
    rows = int(metric.get("rows") or 0)
    markets = int(metric.get("markets") or 0)
    row_shortfall = max(0, MIN_FORWARD_ROWS - rows)
    market_shortfall = max(0, MIN_FORWARD_MARKETS - markets)
    rows_per_market = (rows / markets) if markets > 0 else None
    estimated_markets_to_row_floor = (
        int(math.ceil(row_shortfall / rows_per_market)) if rows_per_market and row_shortfall else 0
    )
    estimated_additional_markets_needed = max(market_shortfall, estimated_markets_to_row_floor)
    if rows < MIN_FORWARD_ROWS:
        fail_reasons.append("insufficient_forward_rows")
    if markets < MIN_FORWARD_MARKETS:
        fail_reasons.append("insufficient_forward_markets")
    if metric.get("delta_brier_candidate_minus_v28") is None or float(metric["delta_brier_candidate_minus_v28"]) >= 0.0:
        fail_reasons.append("forward_brier_not_better_than_v28")
    if metric.get("delta_logloss_candidate_minus_v28") is None or float(metric["delta_logloss_candidate_minus_v28"]) >= 0.0:
        fail_reasons.append("forward_logloss_not_better_than_v28")
    near_boundary_rows = int((near_boundary or {}).get("rows") or 0)
    near_boundary_delta_brier = (near_boundary or {}).get("delta_brier_candidate_minus_v28")
    if near_boundary and int(near_boundary.get("rows") or 0) > 0:
        delta_boundary = near_boundary.get("delta_brier_candidate_minus_v28")
        if delta_boundary is None or float(delta_boundary) > 0.0:
            fail_reasons.append("near_boundary_brier_degraded")
    else:
        fail_reasons.append("near_boundary_forward_rows_missing")
    return {
        "candidate_id": metric.get("candidate_id"),
        "forward_evidence_promotable": not fail_reasons,
        "status": "pass" if not fail_reasons else "fail",
        "fail_reasons": fail_reasons,
        "rows": rows,
        "required_rows": MIN_FORWARD_ROWS,
        "row_shortfall": row_shortfall,
        "markets": markets,
        "required_markets": MIN_FORWARD_MARKETS,
        "market_shortfall": market_shortfall,
        "rows_per_market": rows_per_market,
        "estimated_markets_to_row_floor": estimated_markets_to_row_floor,
        "estimated_additional_markets_needed": estimated_additional_markets_needed,
        "delta_brier_candidate_minus_v28": metric.get("delta_brier_candidate_minus_v28"),
        "delta_logloss_candidate_minus_v28": metric.get("delta_logloss_candidate_minus_v28"),
        "near_boundary_rows": near_boundary_rows,
        "near_boundary_delta_brier_candidate_minus_v28": near_boundary_delta_brier,
    }


def score_rows(raw_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = clean_forward_rows(raw_rows)
    candidate_ids = sorted({str(row.get("candidate_id") or "") for row in rows if row.get("candidate_id")})
    slices = [
        "all_rows",
        "near_boundary_abs_d_lte_1",
        "late_lte_180s",
        "side_yes",
        "side_no",
        "book_disagreement_gt_10c",
    ]
    metrics = [metric_row(rows, candidate_id, slice_name) for candidate_id in candidate_ids for slice_name in slices]
    bins = [
        item
        for candidate_id in candidate_ids
        for source in ("candidate", "v28")
        for item in calibration_bins(rows, candidate_id, source)
    ]
    gates = []
    for candidate_id in candidate_ids:
        all_metric = next(row for row in metrics if row["candidate_id"] == candidate_id and row["slice"] == "all_rows")
        near = next((row for row in metrics if row["candidate_id"] == candidate_id and row["slice"] == "near_boundary_abs_d_lte_1"), None)
        gates.append(candidate_gate(all_metric, near))
    status_counts = Counter(row.get("label_join_status", "") for row in raw_rows)
    source_counts = Counter(row.get("source_status", "") for row in raw_rows)
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "evidence_status": "scored_forward_evidence" if rows else "blocked_no_joined_forward_rows",
        "raw_rows": len(raw_rows),
        "clean_forward_rows": len(rows),
        "clean_forward_markets": len({row.get("market_ticker") for row in rows}),
        "candidate_count": len(candidate_ids),
        "candidate_ids": candidate_ids,
        "metrics_rows": len(metrics),
        "bin_rows": len(bins),
        "status_counts": dict(sorted(status_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "candidate_gates": gates,
        "promotable_candidate_count": sum(1 for row in gates if row["forward_evidence_promotable"]),
        "promotion_status": {
            "allowed": False,
            "reason": "forward evidence scoring is necessary but promotion also requires source contract and promotion verifier",
        },
        "inputs": {
            "labeled_csv": rel_path(LABELED_CSV),
            "labeled_hash": sha256_file(LABELED_CSV),
        },
        "outputs": {
            "metrics_csv": rel_path(METRICS_CSV),
            "bins_csv": rel_path(BINS_CSV),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }
    return metrics, bins, summary


def build(labeled_csv: Path = LABELED_CSV) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    return score_rows(read_csv_rows(labeled_csv))


def write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], metrics: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Evidence Score",
        "",
        "Research-only scorer for settled frozen-forward evidence. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Evidence status: `{summary['evidence_status']}`",
        f"- Raw joined-label rows: `{summary['raw_rows']}`",
        f"- Clean forward rows: `{summary['clean_forward_rows']}`",
        f"- Clean forward markets: `{summary['clean_forward_markets']}`",
        f"- Candidates: `{summary['candidate_count']}`",
        f"- Promotable by forward evidence alone: `{summary['promotable_candidate_count']}`",
        f"- Promotion allowed: `{summary['promotion_status']['allowed']}`",
        "",
        "## Candidate Gates",
        "",
        "| candidate | status | rows | markets | est. addl markets | brier delta | logloss delta | fail reasons |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for gate in summary["candidate_gates"]:
        row_progress = f"{gate['rows']}/{gate['required_rows']}"
        market_progress = f"{gate['markets']}/{gate['required_markets']}"
        lines.append(
            f"| `{gate['candidate_id']}` | `{gate['status']}` | {row_progress} | {market_progress} | "
            f"{gate['estimated_additional_markets_needed']} | {gate['delta_brier_candidate_minus_v28']} | "
            f"{gate['delta_logloss_candidate_minus_v28']} | `{gate['fail_reasons']}` |"
        )
    lines.extend(["", "## All-Rows Metrics", "", "| candidate | rows | markets | cand brier | v28 brier | cand logloss | v28 logloss |", "|---|---:|---:|---:|---:|---:|---:|"])
    for row in metrics:
        if row["slice"] != "all_rows":
            continue
        lines.append(
            f"| `{row['candidate_id']}` | {row['rows']} | {row['markets']} | {row['candidate_brier']} | "
            f"{row['v28_brier']} | {row['candidate_logloss']} | {row['v28_logloss']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This scorer only accepts rows joined after frozen prediction and resolution.",
            "- Probability metrics are scored before any economics fields.",
            "- Empty output is expected until real frozen forward rows settle.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(metrics: list[dict[str, Any]], bins: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(metrics, METRIC_FIELDS, METRICS_CSV)
    write_csv_rows(bins, BIN_FIELDS, BINS_CSV)
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "metrics": metrics, "bins": bins[:200]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, metrics, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write forward evidence score artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--labeled-csv", type=Path, default=LABELED_CSV, help="Joined forward-label CSV.")
    args = parser.parse_args()
    metrics, bins, summary = build(labeled_csv=args.labeled_csv)
    if args.write and not args.dry_run:
        write_outputs(metrics, bins, summary)
    print(
        json.dumps(
            {
                "evidence_status": summary["evidence_status"],
                "clean_forward_rows": summary["clean_forward_rows"],
                "clean_forward_markets": summary["clean_forward_markets"],
                "candidate_count": summary["candidate_count"],
                "promotable_candidate_count": summary["promotable_candidate_count"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
