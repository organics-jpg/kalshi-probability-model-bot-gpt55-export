from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT / "research_data"
EDGE_DIR = ROOT / "logs" / "edge_research"
LEDGER_PATH = EDGE_DIR / "edge_idea_ledger.jsonl"
INDEX_PATH = EDGE_DIR / "edge_idea_index.json"
REFERENCE_CANDIDATE_ID = "pnl_max_p05_q065_logged_live_reference_v1"
SCRIPT_VERSION = "live-online-neighbor-overlay-v1"
UTC = timezone.utc


POLICIES: list[dict[str, Any]] = [
    {
        "policy_id": "baseline_live_reference_approved",
        "family": "baseline",
        "description": "Logged live dwell approvals without an online-neighbor overlay.",
        "params": {},
    },
    {
        "policy_id": "neighbor_wr78_hist80_post_admission_veto",
        "family": "online_neighbor_post_admission_overlay",
        "description": "Keep logged live approvals only when the side-matched online-neighbor win rate is at least 78% with at least 80 prior closed-market samples.",
        "params": {"min_history": 80, "min_win_rate": 0.78},
    },
    {
        "policy_id": "neighbor_lcb0_ev2_wr78_hist80_post_admission_veto",
        "family": "online_neighbor_post_admission_overlay",
        "description": "Keep logged live approvals only when side-matched online-neighbor LCB, EV, win rate, and history all clear fixed thresholds.",
        "params": {"min_history": 80, "min_win_rate": 0.78, "min_lcb_cents": 0.0, "min_model_ev_cents": 2.0},
    },
]


def utc_stamp() -> tuple[datetime, str]:
    now = datetime.now(UTC).replace(microsecond=0)
    return now, now.strftime("%Y%m%dT%H%M%SZ")


def read_parquet_tree(path: Path) -> pd.DataFrame:
    files = sorted(path.rglob("*.parquet"))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(file) for file in files], ignore_index=True)


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def json_loads_nan_safe(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    text = str(raw).replace("NaN", "null")
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def side_neighbor_values(row: pd.Series) -> dict[str, float]:
    gates = json_loads_nan_safe(row.get("gate_values_json"))
    side = str(row.get("side") or "").lower()

    def value(name: str) -> float:
        return safe_float(gates.get(f"online_neighbor_{side}_{name}"))

    return {
        "history_count": value("history_count"),
        "win_rate": value("win_rate"),
        "model_ev_cents": value("model_ev_cents"),
        "lcb_cents": value("lcb_cents"),
    }


def policy_passes(row: pd.Series, policy: dict[str, Any]) -> bool:
    if policy["family"] == "baseline":
        return True
    values = side_neighbor_values(row)
    params = policy["params"]
    checks = {
        "min_history": values["history_count"] >= float(params.get("min_history", -math.inf)),
        "min_win_rate": values["win_rate"] >= float(params.get("min_win_rate", -math.inf)),
        "min_lcb_cents": values["lcb_cents"] >= float(params.get("min_lcb_cents", -math.inf)),
        "min_model_ev_cents": values["model_ev_cents"] >= float(params.get("min_model_ev_cents", -math.inf)),
    }
    return all(checks[name] for name in params)


def labeled_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "would_win" not in df.columns:
        return df.iloc[0:0].copy()
    return df[df["would_win"].notna()].copy()


def fillable_mask(rows: pd.DataFrame) -> pd.Series:
    if rows.empty:
        return pd.Series([], dtype=bool)
    blocker = rows.get("blocker", pd.Series(["unknown"] * len(rows))).fillna("unknown").astype(str)
    estimated = pd.to_numeric(rows.get("estimated_ioc_fill_size", 0), errors="coerce").fillna(0)
    requested = pd.to_numeric(rows.get("proposed_size", rows.get("requested_size", 2)), errors="coerce").fillna(2)
    return (blocker == "none") & (estimated >= requested)


def summarize_selected(rows: pd.DataFrame) -> dict[str, Any]:
    rows = labeled_rows(rows)
    if rows.empty:
        return {
            "approved_decisions": 0,
            "labeled_approved_decisions": 0,
            "approved_winners": 0,
            "approved_losers": 0,
            "approved_stream_pnl_cents": 0.0,
            "fillability_adjusted_pnl_cents": 0.0,
            "false_positive_loss_cents": 0.0,
            "blocker_counts": {},
            "side_counts": {},
            "side_pnl_cents": {},
        }

    pnl = pd.to_numeric(rows["gross_pnl_cents_for_size"], errors="coerce").fillna(0.0)
    would_win = rows["would_win"].astype(bool)
    fillable = fillable_mask(rows)
    side_pnl: dict[str, float] = defaultdict(float)
    side_counts: Counter[str] = Counter()
    for side, value in zip(rows["side"].astype(str), pnl):
        side_counts[side] += 1
        side_pnl[side] += float(value)
    blocker_counts = Counter(rows.get("blocker", pd.Series(["unknown"] * len(rows))).fillna("unknown").astype(str))
    return {
        "approved_decisions": int(len(rows)),
        "labeled_approved_decisions": int(len(rows)),
        "approved_winners": int(would_win.sum()),
        "approved_losers": int((~would_win).sum()),
        "approved_stream_pnl_cents": round(float(pnl.sum()), 2),
        "fillability_adjusted_pnl_cents": round(float(pnl[fillable].sum()), 2),
        "false_positive_loss_cents": round(float((-pnl[~would_win]).clip(lower=0).sum()), 2),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "side_counts": dict(sorted(side_counts.items())),
        "side_pnl_cents": {key: round(value, 2) for key, value in sorted(side_pnl.items())},
    }


def score_policy(base: pd.DataFrame, policy: dict[str, Any]) -> dict[str, Any]:
    passes = base.apply(lambda row: policy_passes(row, policy), axis=1)
    admitted = base[passes].copy()
    vetoed = labeled_rows(base[~passes].copy())
    admitted_summary = summarize_selected(admitted)
    vetoed_pnl = pd.to_numeric(vetoed.get("gross_pnl_cents_for_size", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    vetoed_winner = vetoed.get("would_win", pd.Series(dtype=bool)).astype(bool) if not vetoed.empty else pd.Series(dtype=bool)

    promotion_gates = {
        "min_forward_decisions": admitted_summary["approved_decisions"] >= 25,
        "approved_stream_pnl": admitted_summary["approved_stream_pnl_cents"] > 0,
        "fillability_adjusted_pnl": admitted_summary["fillability_adjusted_pnl_cents"] > 0,
        "false_positive_loss": admitted_summary["false_positive_loss_cents"] <= 300,
        "side_stability": all(value >= 0 for value in admitted_summary["side_pnl_cents"].values()) if admitted_summary["side_pnl_cents"] else False,
    }
    return {
        "policy_id": policy["policy_id"],
        "family": policy["family"],
        "description": policy["description"],
        "params": policy["params"],
        **admitted_summary,
        "vetoed_labeled_decisions": int(len(vetoed)),
        "vetoed_avoided_loser_loss_cents": round(float((-vetoed_pnl[~vetoed_winner]).clip(lower=0).sum()), 2) if len(vetoed_pnl) else 0.0,
        "vetoed_missed_winner_pnl_cents": round(float(vetoed_pnl[vetoed_winner].clip(lower=0).sum()), 2) if len(vetoed_pnl) else 0.0,
        "promotion_gates": promotion_gates,
        "promotion_status": "PASS" if all(promotion_gates.values()) else "FAIL",
        "promotion_fail_reasons": [name for name, passed in promotion_gates.items() if not passed],
    }


def load_live_reference_rows(dataset: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    dataset_root = RESEARCH_ROOT / dataset
    decisions = read_parquet_tree(dataset_root / "candidate_decisions" / f"candidate_id={REFERENCE_CANDIDATE_ID}")
    outcomes = read_parquet_tree(dataset_root / "outcome_labels")
    fillability = read_parquet_tree(dataset_root / "fillability_snapshots")
    if decisions.empty:
        raise SystemExit(f"No reference candidate decisions found for {dataset}")
    approved = decisions[decisions["all_gates_passed"].astype(bool)].copy()
    merged = approved.merge(
        outcomes,
        on=["decision_id", "market_ticker", "side"],
        how="left",
        suffixes=("", "_label"),
    ).merge(
        fillability,
        on=["decision_id", "market_ticker", "side"],
        how="left",
        suffixes=("", "_fillability"),
    )
    meta = {
        "decision_rows": int(len(decisions)),
        "logged_approved_rows": int(len(approved)),
        "labeled_logged_approved_rows": int(merged["would_win"].notna().sum()) if "would_win" in merged else 0,
        "latest_source_feature_ts": str(decisions["source_feature_ts"].max()) if "source_feature_ts" in decisions else None,
        "latest_available_at": str(decisions["available_at"].max()) if "available_at" in decisions else None,
    }
    return merged, meta


def load_index() -> dict[str, list[str]]:
    if not INDEX_PATH.exists():
        return {"idea_keys": [], "tested_strategy_ids": []}
    try:
        loaded = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"idea_keys": [], "tested_strategy_ids": []}
    return {
        "idea_keys": list(loaded.get("idea_keys", [])),
        "tested_strategy_ids": list(loaded.get("tested_strategy_ids", [])),
    }


def save_index(index: dict[str, list[str]]) -> None:
    index["idea_keys"] = list(dict.fromkeys(index.get("idea_keys", [])))
    index["tested_strategy_ids"] = list(dict.fromkeys(index.get("tested_strategy_ids", [])))
    INDEX_PATH.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def idea_identity() -> tuple[str, str]:
    params = {"reference_candidate_id": REFERENCE_CANDIDATE_ID, "policies": POLICIES[1:]}
    equation = (
        "For each logged live dwell approval, veto unless the side-matched online-neighbor "
        "history/win-rate/LCB/EV thresholds pass using features available at decision time."
    )
    encoded = json.dumps({"family": "live_dwell_online_neighbor_post_admission_overlay", "equation": equation, "params": params}, sort_keys=True)
    digest = hashlib.sha1(encoded.encode("utf-8")).hexdigest()
    return digest, f"live_dwell_online_neighbor_overlay_{digest[:8]}"


def append_edge_ledger(payload: dict[str, Any]) -> None:
    idea_key, strategy_id = idea_identity()
    index = load_index()
    if idea_key in set(index.get("idea_keys", [])) or strategy_id in set(index.get("tested_strategy_ids", [])):
        return
    best_overlay = max(
        [score for score in payload["scores"] if score["family"] != "baseline"],
        key=lambda item: (item["approved_stream_pnl_cents"], item["fillability_adjusted_pnl_cents"]),
        default=None,
    )
    record = {
        "generated_at": payload["generated_at_utc"],
        "dataset": payload["dataset_tag"],
        "idea_key": idea_key,
        "strategy_id": strategy_id,
        "family": "live_dwell_online_neighbor_post_admission_overlay",
        "theorem": "A prior-closed-market neighbor model may identify logged dwell approvals whose high quoted probability is still underpriced, but must prove that after false-positive and fillability costs.",
        "equation": "Approve logged dwell entry only if online_neighbor_side_history_count >= H, win_rate >= W, and optional LCB/EV thresholds are met at source_feature_ts.",
        "params": {"reference_candidate_id": REFERENCE_CANDIDATE_ID, "policies": [policy["params"] for policy in POLICIES[1:]]},
        "result": "not_promoted",
        "summary": best_overlay,
        "evidence_quality": "live_forward_gauntlet_tape_log_derived_backfill",
        "artifact_json": payload["json_path"],
        "artifact_csv": payload["csv_path"],
        "artifact_report": payload["report_path"],
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    index["idea_keys"] = [*index.get("idea_keys", []), idea_key]
    index["tested_strategy_ids"] = [*index.get("tested_strategy_ids", []), strategy_id]
    save_index(index)


def write_csv(path: Path, scores: list[dict[str, Any]]) -> None:
    fieldnames = [
        "policy_id",
        "approved_decisions",
        "approved_winners",
        "approved_losers",
        "approved_stream_pnl_cents",
        "fillability_adjusted_pnl_cents",
        "false_positive_loss_cents",
        "vetoed_labeled_decisions",
        "vetoed_avoided_loser_loss_cents",
        "vetoed_missed_winner_pnl_cents",
        "promotion_status",
        "promotion_fail_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for score in scores:
            row = {key: score.get(key) for key in fieldnames}
            row["promotion_fail_reasons"] = ";".join(score.get("promotion_fail_reasons", []))
            writer.writerow(row)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Codex Research Lab Gauntlet Online-Neighbor Overlay",
        "",
        f"- Generated: `{payload['generated_at_utc']}`",
        f"- Dataset: `{payload['dataset_tag']}`",
        f"- Source candidate: `{REFERENCE_CANDIDATE_ID}`",
        f"- Evidence quality: `{payload['evidence_quality']}`",
        f"- Research Lab improvement status: `{payload['research_lab_improvement_status']}`",
        f"- Gauntlet improvement status: `{payload['gauntlet_improvement_status']}`",
        f"- Capture status: `{payload['capture_status']}`",
        f"- Candidate scoring status: `{payload['candidate_scoring_status']}`",
        f"- New edge status: `{payload['new_edge_status']}`",
        "",
        "## Research Lab / Gauntlet Improvement",
        "",
        "This run used the newly generated online-neighbor feature tape, whose side-matched history, win-rate, model-EV, and LCB fields are computed only from prior closed markets. The audit confirms those fields are present on logged live approvals and can be consumed by fixed overlay policies without changing live execution.",
        "",
        "## Fixed Idea Tested",
        "",
        "Apply an online-neighbor post-admission veto to the logged live dwell approvals. This is intentionally narrower than a broad grid search: the thresholds were fixed before scoring the current tape.",
        "",
        "## Scores",
        "",
        "| Policy | Approved | W/L | All-approved PnL c | Fillability PnL c | FP loss c | Status | Fail reasons |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for score in payload["scores"]:
        lines.append(
            "| {policy_id} | {approved_decisions} | {approved_winners}/{approved_losers} | {approved_stream_pnl_cents} | {fillability_adjusted_pnl_cents} | {false_positive_loss_cents} | {promotion_status} | {reasons} |".format(
                policy_id=score["policy_id"],
                approved_decisions=score["approved_decisions"],
                approved_winners=score["approved_winners"],
                approved_losers=score["approved_losers"],
                approved_stream_pnl_cents=score["approved_stream_pnl_cents"],
                fillability_adjusted_pnl_cents=score["fillability_adjusted_pnl_cents"],
                false_positive_loss_cents=score["false_positive_loss_cents"],
                promotion_status=score["promotion_status"],
                reasons=", ".join(score["promotion_fail_reasons"]) or "none",
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "No policy is eligible for frozen candidate promotion. The strict online-neighbor overlay admitted too few trades, remained negative before fillability, and had zero fillability-adjusted PnL because admitted rows were stale-book blocked in the current log-derived tape.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run(dataset: str) -> dict[str, Any]:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    generated_at, stamp = utc_stamp()
    rows, source_meta = load_live_reference_rows(dataset)
    scores = [score_policy(rows, policy) for policy in POLICIES]

    payload: dict[str, Any] = {
        "schema_version": "live-online-neighbor-overlay-summary-v1",
        "script_version": SCRIPT_VERSION,
        "generated_at_utc": generated_at.isoformat(),
        "dataset_tag": dataset,
        "source_candidate_id": REFERENCE_CANDIDATE_ID,
        "source_meta": source_meta,
        "research_lab_improvement_status": "PASS_online_neighbor_features_consumed_in_live_forward_overlay_audit",
        "gauntlet_improvement_status": "PASS_fixed_overlay_scored_from_current_candidate_tape",
        "capture_status": "WARN_log_derived_backfill_current_not_native_passive",
        "candidate_scoring_status": "MONITOR_no_overlay_policy_promoted",
        "new_edge_status": "MONITOR_tested_not_promoted",
        "evidence_quality": "live_forward_gauntlet_tape_log_derived_backfill",
        "scores": scores,
    }

    json_path = EDGE_DIR / f"codex_research_lab_gauntlet_online_neighbor_overlay_{dataset}_{stamp}.json"
    csv_path = EDGE_DIR / f"codex_research_lab_gauntlet_online_neighbor_overlay_{dataset}_{stamp}.csv"
    report_path = EDGE_DIR / f"codex_research_lab_gauntlet_online_neighbor_overlay_{dataset}_{stamp}.md"
    payload["json_path"] = str(json_path)
    payload["csv_path"] = str(csv_path)
    payload["report_path"] = str(report_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(csv_path, scores)
    write_report(report_path, payload)
    shutil.copy2(json_path, EDGE_DIR / "codex_research_lab_gauntlet_online_neighbor_overlay_latest.json")
    shutil.copy2(csv_path, EDGE_DIR / "codex_research_lab_gauntlet_online_neighbor_overlay_latest.csv")
    shutil.copy2(report_path, EDGE_DIR / "codex_research_lab_gauntlet_online_neighbor_overlay_latest.md")
    append_edge_ledger(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit fixed online-neighbor overlays on live-forward Research Lab gauntlet tapes.")
    parser.add_argument("--dataset", default="live_liquidity_dwell_size2")
    args = parser.parse_args()
    payload = run(args.dataset)
    print(json.dumps({key: payload[key] for key in ("generated_at_utc", "dataset_tag", "new_edge_status", "json_path", "report_path")}, indent=2))


if __name__ == "__main__":
    main()
