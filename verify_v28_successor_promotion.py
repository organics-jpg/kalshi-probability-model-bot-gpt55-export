"""Strict promotion verifier for the v28 successor FV pipeline.

Research-only. This is the final hard gate before any candidate could be
considered for forward registry or live review. It reads diagnostic candidate
artifacts, metrics, and the forward registry, then independently verifies the
spec gates:

- chronological holdout Brier and logloss better than v28;
- near-boundary calibration/accuracy not degraded;
- source quality is forward-registered, not diagnostic/posthoc;
- broad market coverage;
- frozen forward registry evidence exists and is settled/scored;
- fee-aware shadow economics are reported after probability metrics.

Current expected verdict is blocked because the available rows are diagnostic
and there are zero post-lock forward rows.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

FORWARD_REGISTRY_JSON = EDGE_DIR / "v28_successor_forward_registry_latest.json"
FORWARD_EVIDENCE_SCORE_JSON = EDGE_DIR / "v28_successor_forward_evidence_score_latest.json"
SOURCE_CONTRACT_JSON = EDGE_DIR / "v28_successor_source_contract_latest.json"

VARIANTS = {
    "seed_diagnostic": {
        "candidate_manifest": OUT_DIR / "candidate_manifests_latest.json",
        "calibration_json": EDGE_DIR / "v28_successor_calibration_latest.json",
        "metrics_csv": EDGE_DIR / "v28_successor_calibration_metrics_latest.csv",
    },
    "logged_events_diagnostic": {
        "candidate_manifest": OUT_DIR / "candidate_manifests_logged_events_latest.json",
        "calibration_json": EDGE_DIR / "v28_successor_logged_event_calibration_latest.json",
        "metrics_csv": EDGE_DIR / "v28_successor_logged_event_calibration_metrics_latest.csv",
    },
}

VERIFIER_JSON = EDGE_DIR / "v28_successor_promotion_verifier_latest.json"
VERIFIER_MD = EDGE_DIR / "v28_successor_promotion_verifier_latest.md"
VERIFIER_CSV = EDGE_DIR / "v28_successor_promotion_verifier_latest.csv"

MIN_HOLDOUT_MARKETS = 20
MIN_HOLDOUT_ROWS = 100
MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    evidence: str

    def as_dict(self) -> dict[str, Any]:
        return {"gate": self.name, "passed": self.passed, "evidence": self.evidence}


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    return out


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def metric_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (str(row.get("candidate_id")), str(row.get("split")), str(row.get("slice"))): row
        for row in rows
    }


def metric(metrics: dict[tuple[str, str, str], dict[str, Any]], candidate_id: str, split: str, slice_name: str) -> dict[str, Any] | None:
    return metrics.get((candidate_id, split, slice_name))


def lower_is_better(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None, key: str) -> bool:
    cand = as_float(candidate.get(key)) if candidate else None
    base = as_float(baseline.get(key)) if baseline else None
    return cand is not None and base is not None and cand < base


def not_degraded(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None, key: str) -> bool:
    cand = as_float(candidate.get(key)) if candidate else None
    base = as_float(baseline.get(key)) if baseline else None
    return cand is not None and base is not None and cand <= base


def rows_count(row: dict[str, Any] | None) -> int:
    parsed = as_float(row.get("rows")) if row else None
    return int(parsed or 0)


def markets_count(row: dict[str, Any] | None) -> int:
    parsed = as_float(row.get("markets")) if row else None
    return int(parsed or 0)


def shadow_metric_present(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    return as_float(row.get("shadow_net_pnl_cents")) is not None and as_float(row.get("shadow_expected_ev_cents")) is not None


def simple_inspectable_manifest(manifest: dict[str, Any]) -> bool:
    return (
        bool(str(manifest.get("model_hash") or "").strip())
        and as_bool(manifest.get("allowed_for_forward_collection"))
        and str(manifest.get("model_type") or "")
        in {"regularized_logistic", "monotonic_tabular_calibration", "fixed_logit_residual"}
    )


def evaluate_candidate(
    *,
    variant: str,
    manifest: dict[str, Any],
    metrics: dict[tuple[str, str, str], dict[str, Any]],
    forward_registry: dict[str, Any],
    forward_evidence: dict[str, Any],
    source_contract: dict[str, Any],
) -> dict[str, Any]:
    candidate_id = str(manifest.get("candidate_id"))
    holdout = metric(metrics, candidate_id, "chronological_holdout", "all_rows")
    baseline_holdout = metric(metrics, "v28_raw", "chronological_holdout", "all_rows")
    proxy_boundary = metric(metrics, candidate_id, "chronological_holdout", "near_boundary_v28_40_60")
    baseline_proxy_boundary = metric(metrics, "v28_raw", "chronological_holdout", "near_boundary_v28_40_60")
    true_boundary = metric(metrics, candidate_id, "chronological_holdout", "near_boundary_abs_d_lte_1")
    baseline_true_boundary = metric(metrics, "v28_raw", "chronological_holdout", "near_boundary_abs_d_lte_1")
    high_recross = metric(metrics, candidate_id, "chronological_holdout", "high_recross")
    baseline_high_recross = metric(metrics, "v28_raw", "chronological_holdout", "high_recross")
    forward_rows = int(forward_registry.get("row_count") or 0)
    forward_markets = int(forward_registry.get("market_count") or 0)
    if not forward_markets:
        forward_markets = int(forward_registry.get("feature_forward_row_ids") or 0)
    forward_evidence_summary = forward_evidence.get("summary", {}) if isinstance(forward_evidence, dict) else {}
    source_contract_summary = source_contract.get("summary", {}) if isinstance(source_contract, dict) else {}
    forward_evidence_gate = next(
        (
            gate
            for gate in forward_evidence_summary.get("candidate_gates", [])
            if str(gate.get("candidate_id") or "") == candidate_id
        ),
        {},
    )

    true_boundary_available = rows_count(baseline_true_boundary) > 0
    proxy_boundary_available = rows_count(baseline_proxy_boundary) > 0
    if true_boundary_available:
        boundary_candidate = true_boundary
        boundary_baseline = baseline_true_boundary
        boundary_name = "near_boundary_abs_d_lte_1"
    else:
        boundary_candidate = proxy_boundary
        boundary_baseline = baseline_proxy_boundary
        boundary_name = "near_boundary_v28_40_60"

    candidate_gate = manifest.get("promotion_gate", {})
    gates = [
        GateResult(
            "candidate_is_not_baseline",
            candidate_id != "v28_raw",
            f"candidate_id={candidate_id}",
        ),
        GateResult(
            "holdout_coverage",
            rows_count(holdout) >= MIN_HOLDOUT_ROWS and markets_count(holdout) >= MIN_HOLDOUT_MARKETS,
            f"rows={rows_count(holdout)} markets={markets_count(holdout)} required_rows={MIN_HOLDOUT_ROWS} required_markets={MIN_HOLDOUT_MARKETS}",
        ),
        GateResult(
            "holdout_brier_better_than_v28",
            lower_is_better(holdout, baseline_holdout, "brier"),
            f"candidate={fmt_metric(holdout, 'brier')} baseline={fmt_metric(baseline_holdout, 'brier')}",
        ),
        GateResult(
            "holdout_logloss_better_than_v28",
            lower_is_better(holdout, baseline_holdout, "logloss"),
            f"candidate={fmt_metric(holdout, 'logloss')} baseline={fmt_metric(baseline_holdout, 'logloss')}",
        ),
        GateResult(
            "boundary_brier_not_degraded",
            (true_boundary_available or proxy_boundary_available) and not_degraded(boundary_candidate, boundary_baseline, "brier"),
            f"slice={boundary_name} candidate={fmt_metric(boundary_candidate, 'brier')} baseline={fmt_metric(boundary_baseline, 'brier')} rows={rows_count(boundary_candidate)}",
        ),
        GateResult(
            "recross_brier_not_degraded_or_unavailable",
            rows_count(baseline_high_recross) == 0 or not_degraded(high_recross, baseline_high_recross, "brier"),
            f"candidate={fmt_metric(high_recross, 'brier')} baseline={fmt_metric(baseline_high_recross, 'brier')} rows={rows_count(high_recross)}",
        ),
        GateResult(
            "shadow_economics_reported",
            shadow_metric_present(holdout),
            f"shadow_net_pnl_cents={fmt_metric(holdout, 'shadow_net_pnl_cents')} shadow_expected_ev_cents={fmt_metric(holdout, 'shadow_expected_ev_cents')}",
        ),
        GateResult(
            "source_quality_forward_registered",
            as_bool(source_contract_summary.get("promotion_contract_ready"))
            and forward_evidence_summary.get("evidence_status") == "scored_forward_evidence"
            and int(forward_evidence_summary.get("clean_forward_rows") or 0) >= MIN_FORWARD_ROWS
            and int(forward_evidence_summary.get("clean_forward_markets") or 0) >= MIN_FORWARD_MARKETS,
            (
                f"source_contract_ready={source_contract_summary.get('promotion_contract_ready')} "
                f"evidence_status={forward_evidence_summary.get('evidence_status')} "
                f"clean_rows={forward_evidence_summary.get('clean_forward_rows')} "
                f"clean_markets={forward_evidence_summary.get('clean_forward_markets')}"
            ),
        ),
        GateResult(
            "source_contract_promotion_ready",
            as_bool(source_contract_summary.get("promotion_contract_ready")),
            (
                f"promotion_contract_ready={source_contract_summary.get('promotion_contract_ready')} "
                f"overall_verdict={source_contract_summary.get('overall_verdict')} "
                f"missing_required_forward_datasets={source_contract_summary.get('missing_required_forward_datasets')}"
            ),
        ),
        GateResult(
            "frozen_forward_registry_present",
            as_bool(forward_registry.get("promotion_ready")) and forward_rows >= MIN_FORWARD_ROWS,
            f"registry_status={forward_registry.get('registry_status')} rows={forward_rows} required_rows={MIN_FORWARD_ROWS}",
        ),
        GateResult(
            "forward_market_coverage",
            forward_markets >= MIN_FORWARD_MARKETS,
            f"forward_markets={forward_markets} required_markets={MIN_FORWARD_MARKETS}",
        ),
        GateResult(
            "forward_evidence_scored_and_promotable",
            forward_evidence_summary.get("evidence_status") == "scored_forward_evidence"
            and as_bool(forward_evidence_gate.get("forward_evidence_promotable")),
            (
                f"evidence_status={forward_evidence_summary.get('evidence_status')} "
                f"clean_rows={forward_evidence_summary.get('clean_forward_rows')} "
                f"clean_markets={forward_evidence_summary.get('clean_forward_markets')} "
                f"candidate_gate={forward_evidence_gate}"
            ),
        ),
        GateResult(
            "candidate_manifest_frozen_and_inspectable",
            simple_inspectable_manifest(manifest),
            (
                f"model_type={manifest.get('model_type')} model_hash={manifest.get('model_hash')} "
                f"allowed_for_forward_collection={manifest.get('allowed_for_forward_collection')} "
                f"diagnostic_promotion_status={candidate_gate.get('status')}"
            ),
        ),
    ]
    passed = all(gate.passed for gate in gates)
    return {
        "variant": variant,
        "candidate_id": candidate_id,
        "model_type": manifest.get("model_type"),
        "model_track": manifest.get("model_track"),
        "model_hash": manifest.get("model_hash"),
        "verdict": "promotable" if passed else "blocked",
        "failed_gates": [gate.name for gate in gates if not gate.passed],
        "passed_gates": [gate.name for gate in gates if gate.passed],
        "gates": [gate.as_dict() for gate in gates],
    }


def fmt_metric(row: dict[str, Any] | None, key: str) -> str:
    if not row:
        return "NA"
    value = as_float(row.get(key))
    if value is None:
        return "NA"
    return f"{value:.8f}"


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    forward_registry = read_json(FORWARD_REGISTRY_JSON) or {}
    forward_evidence = read_json(FORWARD_EVIDENCE_SCORE_JSON) or {}
    source_contract = read_json(SOURCE_CONTRACT_JSON) or {}
    evaluations: list[dict[str, Any]] = []
    inputs: dict[str, Any] = {
        "forward_registry": rel_path(FORWARD_REGISTRY_JSON),
        "forward_evidence_score": rel_path(FORWARD_EVIDENCE_SCORE_JSON),
        "source_contract": rel_path(SOURCE_CONTRACT_JSON),
    }
    for variant, paths in VARIANTS.items():
        manifests = read_json(paths["candidate_manifest"]) or []
        metrics = metric_lookup(read_csv_rows(paths["metrics_csv"]))
        calibration = read_json(paths["calibration_json"]) or {}
        inputs[variant] = {
            "candidate_manifest": rel_path(paths["candidate_manifest"]),
            "metrics_csv": rel_path(paths["metrics_csv"]),
            "calibration_json": rel_path(paths["calibration_json"]),
            "calibration_promotion_verdict": (calibration.get("summary") or {}).get("promotion_verdict"),
        }
        for manifest in manifests:
            evaluations.append(
                evaluate_candidate(
                    variant=variant,
                    manifest=manifest,
                    metrics=metrics,
                    forward_registry=forward_registry,
                    forward_evidence=forward_evidence,
                    source_contract=source_contract,
                )
            )
    promotable = [row for row in evaluations if row["verdict"] == "promotable"]
    blocked_candidate_hard_blockers = sorted(
        {
            gate
            for row in evaluations
            if row["verdict"] == "blocked"
            for gate in row["failed_gates"]
            if not (gate == "candidate_manifest_frozen_and_inspectable" and row["candidate_id"] == "v28_raw")
            if gate in {
                "source_quality_forward_registered",
                "source_contract_promotion_ready",
                "frozen_forward_registry_present",
                "forward_market_coverage",
                "forward_evidence_scored_and_promotable",
                "candidate_manifest_frozen_and_inspectable",
            }
        }
    )
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "overall_verdict": "promotable" if promotable else "blocked",
        "promotable_candidates": promotable,
        "candidate_count": len(evaluations),
        "blocked_candidate_count": sum(1 for row in evaluations if row["verdict"] == "blocked"),
        "inputs": inputs,
        "hard_blockers": [] if promotable else blocked_candidate_hard_blockers,
        "blocked_candidate_hard_blockers": blocked_candidate_hard_blockers,
        "outputs": {
            "json": rel_path(VERIFIER_JSON),
            "markdown": rel_path(VERIFIER_MD),
            "csv": rel_path(VERIFIER_CSV),
        },
    }
    return evaluations, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["variant", "candidate_id", "model_type", "model_track", "model_hash", "verdict", "failed_gates", "passed_gates"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: ";".join(row[key]) if key in {"failed_gates", "passed_gates"} else row.get(key)
                    for key in fieldnames
                }
            )


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Promotion Verifier",
        "",
        "Research-only hard gate. This report does not touch live bot state, orders, thresholds, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Overall verdict: `{summary['overall_verdict']}`",
        f"- Candidate count: `{summary['candidate_count']}`",
        f"- Blocked candidates: `{summary['blocked_candidate_count']}`",
        f"- Promotable candidates: `{len(summary['promotable_candidates'])}`",
        f"- Hard blockers: `{summary['hard_blockers']}`",
        "",
        "## Candidate Verdicts",
        "",
        "| variant | candidate | type | track | verdict | failed gates |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | `{row['candidate_id']}` | `{row['model_type']}` | `{row['model_track']}` | "
            f"`{row['verdict']}` | {', '.join(f'`{gate}`' for gate in row['failed_gates'])} |"
        )
    lines.extend(["", "## Gate Detail", ""])
    for row in rows:
        lines.extend([f"### {row['variant']} / {row['candidate_id']}", "", "| gate | pass | evidence |", "|---|---:|---|"])
        for gate in row["gates"]:
            lines.append(f"| `{gate['gate']}` | {gate['passed']} | {escape_cell(gate['evidence'])} |")
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- No candidate is promotable unless every gate passes at once.",
            "- Probability quality gates are checked before economics.",
            "- Frozen forward registry and source-quality gates are hard blockers, so diagnostic/posthoc wins cannot pass.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    VERIFIER_JSON.write_text(json.dumps({"summary": summary, "candidates": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(rows, VERIFIER_CSV)
    write_markdown(rows, summary, VERIFIER_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write verifier artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    rows, summary = build()
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "overall_verdict": summary["overall_verdict"],
                "candidate_count": summary["candidate_count"],
                "blocked_candidate_count": summary["blocked_candidate_count"],
                "hard_blockers": summary["hard_blockers"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
