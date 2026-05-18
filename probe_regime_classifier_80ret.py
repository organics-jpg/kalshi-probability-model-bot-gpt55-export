"""Research-only 80% retention regime classifier probe.

This probe works from the broad two-sided heartbeat ledger and asks a narrower
question than the earlier FV scans: can an interpretable physics/book regime
classifier keep at least 80% of opportunities while lifting realized accuracy
toward 95% on chronological validation and holdout splits?

It reads existing research artifacts and writes under logs/edge_research. It
does not import the live bot, submit orders, or control any process.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd


OUT_DIR = Path("logs/edge_research")
TWO_SIDE_LEDGER = OUT_DIR / "live_heartbeat_two_side_fv_ledger_latest.csv"
PRIMARY_MODE = "two_side_minute_bucket"

TARGET_ACCURACY = 0.95
RETENTION_FLOOR = 0.80
MIN_SELECTED_ROWS = 75
MIN_HOLDOUT_ROWS = 15


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, tuple):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if not math.isfinite(float(value)):
            return None
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    needed = [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
    ]
    for col in needed:
        if col not in out.columns:
            out[col] = np.nan
    out["score_mean_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].mean(axis=1)
    out["score_mean_book_rv30"] = out[["book_p_side", "brownian_p_rv_30m"]].mean(axis=1)
    out["score_mean_book_rv15_drift5"] = out[
        ["book_p_side", "brownian_p_rv_15m", "drift_p_5m_rv_15m"]
    ].mean(axis=1)
    out["score_min_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].min(axis=1)
    out["score_min_book_rv15_drift5"] = out[
        ["book_p_side", "brownian_p_rv_15m", "drift_p_5m_rv_15m"]
    ].min(axis=1)
    out["score_regime_blend"] = (
        0.50 * out["book_p_side"]
        + 0.30 * out["brownian_p_rv_15m"]
        + 0.20 * out["drift_p_5m_rv_15m"]
    )
    out["abs_book_rv15_gap"] = (out["book_p_side"] - out["brownian_p_rv_15m"]).abs()
    out["abs_book_rv30_gap"] = (out["book_p_side"] - out["brownian_p_rv_30m"]).abs()
    return out


def load_primary() -> pd.DataFrame:
    if not TWO_SIDE_LEDGER.exists():
        raise SystemExit(f"Missing two-sided ledger: {TWO_SIDE_LEDGER}")
    df = pd.read_csv(TWO_SIDE_LEDGER, low_memory=False)
    if "two_side_mode" not in df.columns:
        raise SystemExit(f"Ledger lacks two_side_mode: {TWO_SIDE_LEDGER}")
    df = df[df["two_side_mode"] == PRIMARY_MODE].copy()
    if df.empty:
        raise SystemExit(f"No rows for mode {PRIMARY_MODE} in {TWO_SIDE_LEDGER}")
    df["entry_dt"] = pd.to_datetime(df["entry_dt"], utc=True, errors="coerce")
    df = df.dropna(subset=["entry_dt", "opportunity_key", "side"]).copy()
    df["win"] = bool_series(df["win"])
    df["outcome_available"] = bool_series(df["outcome_available"])
    df = df[df["outcome_available"]].copy()
    numeric_cols = [
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "book_p_side",
        "book_other_mid_cents",
        "book_margin_cents",
        "spread_cents",
        "spot",
        "strike",
        "seconds_to_close",
        "margin_dollars",
        "margin_per_sqrt_sec",
        "margin_per_sqrt_min",
        "rv_sigma_t_15m",
        "rv_sigma_t_30m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_15m",
        "adverse_move_1m",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_15m",
        "drift_projected_margin_5m",
        "drift_projected_margin_15m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = add_scores(df)
    return df.sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


def split_base(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = (
        df.sort_values(["entry_dt", "opportunity_key"])
        .drop_duplicates("opportunity_key", keep="first")[["opportunity_key", "entry_dt", "market"]]
        .reset_index(drop=True)
    )
    n = len(base)
    train_end = int(math.floor(n * 0.60))
    val_end = int(math.floor(n * 0.80))
    split = np.full(n, "holdout", dtype=object)
    split[:train_end] = "train"
    split[train_end:val_end] = "validation"
    base["split"] = split
    side_rows = df.merge(base[["opportunity_key", "split"]], on="opportunity_key", how="inner")
    return base, side_rows


@dataclass(frozen=True)
class Gate:
    family: str
    label: str
    func: Callable[[pd.DataFrame], pd.Series]


@dataclass(frozen=True)
class Candidate:
    chooser: str
    gate: Gate


def col_ge(col: str, threshold: float) -> Gate:
    return Gate(
        family=col,
        label=f"{col}>={threshold:g}",
        func=lambda df, c=col, t=threshold: df[c].ge(t),
    )


def col_le(col: str, threshold: float) -> Gate:
    return Gate(
        family=col,
        label=f"{col}<={threshold:g}",
        func=lambda df, c=col, t=threshold: df[c].le(t),
    )


def abs_col_le(col: str, threshold: float) -> Gate:
    return Gate(
        family=col,
        label=f"abs({col})<={threshold:g}",
        func=lambda df, c=col, t=threshold: df[c].abs().le(t),
    )


def and_gate(left: Gate, right: Gate) -> Gate:
    return Gate(
        family="physics_pair",
        label=f"{left.label} and {right.label}",
        func=lambda df, l=left, r=right: l.func(df).fillna(False) & r.func(df).fillna(False),
    )


def make_gates() -> List[Gate]:
    gates: List[Gate] = [
        Gate("none", "keep_all", lambda df: pd.Series(True, index=df.index)),
    ]
    for col in [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "score_mean_book_rv15",
        "score_min_book_rv15",
        "score_min_book_rv15_drift5",
        "score_regime_blend",
    ]:
        for threshold in [0.50, 0.52, 0.55, 0.58, 0.60, 0.62, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
            gates.append(col_ge(col, threshold))

    for col, thresholds in [
        ("ask_cents", [90, 95, 100]),
        ("spread_cents", [2, 4, 6, 10]),
        ("abs_book_rv15_gap", [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]),
        ("abs_book_rv30_gap", [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]),
        ("rv_sigma_t_15m", [50, 75, 100, 125, 150, 200, 300]),
        ("rv_sigma_t_30m", [50, 75, 100, 125, 150, 200, 300]),
        ("adverse_move_1m", [0, 5, 10, 25, 50, 100]),
        ("adverse_move_5m", [0, 5, 10, 25, 50, 100]),
        ("adverse_move_15m", [0, 5, 10, 25, 50, 100]),
    ]:
        for threshold in thresholds:
            gates.append(col_le(col, threshold))

    for col, thresholds in [
        ("seconds_to_close", [120, 180, 300, 450, 600, 750]),
        ("rv_sigma_t_15m", [50, 75, 100, 125, 150]),
        ("margin_per_rv_sigma_15m", [-0.25, 0.0, 0.25, 0.50, 0.75, 1.0]),
        ("signed_move_5m", [-100, -50, -25, 0, 25, 50]),
        ("signed_move_15m", [-100, -50, -25, 0, 25, 50]),
    ]:
        for threshold in thresholds:
            gates.append(col_ge(col, threshold))

    gates.extend(
        [
            Gate(
                "physics_composite",
                "book>=0.55 and brownian15>=0.55",
                lambda df: df["book_p_side"].ge(0.55) & df["brownian_p_rv_15m"].ge(0.55),
            ),
            Gate(
                "physics_composite",
                "book>=0.55 and abs(book-rv15)<=0.20",
                lambda df: df["book_p_side"].ge(0.55) & df["abs_book_rv15_gap"].le(0.20),
            ),
            Gate(
                "physics_composite",
                "rv15>=0.55 and adverse15<=25",
                lambda df: df["brownian_p_rv_15m"].ge(0.55) & df["adverse_move_15m"].le(25),
            ),
            Gate(
                "physics_composite",
                "adverse15<=10 or margin_rv15>=0.5",
                lambda df: df["adverse_move_15m"].le(10) | df["margin_per_rv_sigma_15m"].ge(0.5),
            ),
            Gate(
                "physics_composite",
                "low_gap_or_high_blend",
                lambda df: df["abs_book_rv15_gap"].le(0.15) | df["score_regime_blend"].ge(0.60),
            ),
        ]
    )

    mild_pair_terms = [
        col_ge("book_p_side", 0.55),
        col_ge("brownian_p_rv_15m", 0.55),
        col_ge("brownian_p_rv_30m", 0.55),
        col_ge("score_regime_blend", 0.58),
        col_ge("score_min_book_rv15", 0.55),
        col_le("abs_book_rv15_gap", 0.30),
        col_le("abs_book_rv30_gap", 0.30),
        col_le("adverse_move_5m", 50),
        col_le("adverse_move_15m", 50),
        col_le("rv_sigma_t_15m", 200),
        col_le("spread_cents", 4),
        col_ge("margin_per_rv_sigma_15m", 0.0),
        col_ge("seconds_to_close", 180),
    ]
    for idx, left in enumerate(mild_pair_terms):
        for right in mild_pair_terms[idx + 1 :]:
            gates.append(and_gate(left, right))
    return gates


def make_candidates(score_features: Iterable[str], gates: Iterable[Gate]) -> List[Candidate]:
    return [Candidate(chooser=score, gate=gate) for score in score_features for gate in gates]


def choose_by_score(side_rows: pd.DataFrame, score_feature: str) -> pd.DataFrame:
    if score_feature not in side_rows.columns:
        return side_rows.iloc[0:0].copy()
    usable = side_rows[side_rows[score_feature].notna()].copy()
    if usable.empty:
        return usable
    chosen = (
        usable.sort_values(
            ["opportunity_key", score_feature, "book_p_side", "entry_dt"],
            ascending=[True, False, False, True],
        )
        .groupby("opportunity_key", as_index=False, sort=False)
        .first()
    )
    return chosen.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


def selected_for_candidate(side_rows: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    chosen = choose_by_score(side_rows, candidate.chooser)
    if chosen.empty:
        return chosen
    mask = candidate.gate.func(chosen).fillna(False)
    return chosen[mask].copy().reset_index(drop=True)


def split_metrics(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    total = int(len(base_part))
    losses = rows - wins
    return {
        "rows": rows,
        "wins": wins,
        "losses": losses,
        "base_rows": total,
        "accuracy": wins / rows if rows else None,
        "retention": rows / total if total else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metrics(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def pass_80(metrics: Dict[str, Dict[str, Any]]) -> bool:
    for split in ["all", "train", "validation", "holdout"]:
        if (metrics[split]["retention"] or 0.0) < RETENTION_FLOOR:
            return False
    return True


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    if not pass_80(metrics):
        return False
    for split in ["all", "train", "validation", "holdout"]:
        if (metrics[split]["accuracy"] or 0.0) < TARGET_ACCURACY:
            return False
    if metrics["all"]["rows"] < MIN_SELECTED_ROWS:
        return False
    if metrics["holdout"]["rows"] < MIN_HOLDOUT_ROWS:
        return False
    return True


def flatten_result(candidate: Candidate, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "chooser": candidate.chooser,
        "gate_family": candidate.gate.family,
        "gate": candidate.gate.label,
        "pass_80_retention": pass_80(metrics),
        "target_pass": target_pass(metrics),
    }
    test_accs = [metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0]
    test_rets = [metrics["validation"]["retention"] or 0.0, metrics["holdout"]["retention"] or 0.0]
    row["min_test_accuracy"] = min(test_accs)
    row["min_test_retention"] = min(test_rets)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["target_pass"]),
        int(row["pass_80_retention"]),
        row["min_test_accuracy"],
        row["holdout_accuracy"] or 0.0,
        row["validation_accuracy"] or 0.0,
        row["all_accuracy"] or 0.0,
        row["min_test_retention"],
    )


def scan_candidates(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    score_features = [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "score_mean_book_rv15",
        "score_mean_book_rv30",
        "score_mean_book_rv15_drift5",
        "score_min_book_rv15",
        "score_min_book_rv15_drift5",
        "score_regime_blend",
    ]
    score_features = [col for col in score_features if col in side_rows.columns]
    rows: List[Dict[str, Any]] = []
    for candidate in make_candidates(score_features, make_gates()):
        selected = selected_for_candidate(side_rows, candidate)
        metrics = metrics_for(base, selected)
        rows.append(flatten_result(candidate, metrics))
    rows.sort(key=rank_key, reverse=True)
    return pd.DataFrame(rows)


def feature_frontier(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    """Train-threshold top-80% frontier for each side-choice score."""
    rows: List[Dict[str, Any]] = []
    features = [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "score_mean_book_rv15",
        "score_min_book_rv15",
        "score_regime_blend",
    ]
    for feature in [f for f in features if f in side_rows.columns]:
        chosen = choose_by_score(side_rows, feature)
        train_scores = chosen.loc[chosen["split"] == "train", feature].dropna()
        if train_scores.empty:
            continue
        threshold = float(train_scores.quantile(1.0 - RETENTION_FLOOR))
        selected = chosen[chosen[feature] >= threshold].copy()
        metrics = metrics_for(base, selected)
        row = {
            "feature": feature,
            "train_top80_threshold": threshold,
            "target_pass": target_pass(metrics),
            "pass_80_retention": pass_80(metrics),
        }
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{split}_{key}"] = value
        rows.append(row)
    return pd.DataFrame(rows).sort_values(
        ["pass_80_retention", "validation_accuracy", "holdout_accuracy", "all_accuracy"],
        ascending=[False, False, False, False],
    )


def block_needed(metric: Dict[str, Any]) -> Optional[int]:
    rows = int(metric["rows"])
    wins = int(metric["wins"])
    if rows <= 0:
        return None
    if wins / rows >= TARGET_ACCURACY:
        return 0
    max_rows_at_target = math.floor(wins / TARGET_ACCURACY)
    return max(0, rows - max_rows_at_target)


def write_report(
    path: Path,
    generated: str,
    base: pd.DataFrame,
    candidates: pd.DataFrame,
    frontier: pd.DataFrame,
) -> None:
    lines: List[str] = []
    lines.append("# 80% Retention Regime Classifier Probe")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append(f"- Source: `{TWO_SIDE_LEDGER}`.")
    lines.append(f"- Primary live websocket view: `{PRIMARY_MODE}`.")
    lines.append("- Each candidate chooses one side per opportunity, then applies one interpretable regime gate.")
    lines.append("- Retention floor is 80% on all, train, validation, and holdout splits.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Primary opportunities: {len(base)}")
    for split in ["train", "validation", "holdout"]:
        lines.append(f"- {split.title()} opportunities: {int((base['split'] == split).sum())}")
    lines.append(f"- Candidate regime rules scanned: {len(candidates)}")
    lines.append(f"- Rules keeping >=80% on every split: {int(candidates['pass_80_retention'].sum())}")
    lines.append(f"- Target-pass rules at >=95% accuracy and >=80% retention: {int(candidates['target_pass'].sum())}")
    lines.append("")
    lines.append("## Best 80%-Retention Candidates")
    lines.append("")
    pass80 = candidates[candidates["pass_80_retention"]].head(15)
    if pass80.empty:
        lines.append("No candidate retained at least 80% on all chronological splits.")
    else:
        lines.append(
            "| rank | chooser | gate | all acc | all ret | train acc | val acc | val ret | holdout acc | holdout ret | selected | target |"
        )
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for idx, row in enumerate(pass80.to_dict("records"), start=1):
            lines.append(
                f"| {idx} | `{row['chooser']}` | `{row['gate']}` | {pct(row['all_accuracy'])} | "
                f"{pct(row['all_retention'])} | {pct(row['train_accuracy'])} | "
                f"{pct(row['validation_accuracy'])} | {pct(row['validation_retention'])} | "
                f"{pct(row['holdout_accuracy'])} | {pct(row['holdout_retention'])} | "
                f"{int(row['all_rows'])} | {row['target_pass']} |"
            )
    lines.append("")
    lines.append("## Train-Threshold Top-80 Frontier")
    lines.append("")
    lines.append(
        "These rows pick the score threshold from the train split only, retaining the top 80% of train opportunities, then apply that fixed threshold forward."
    )
    lines.append("")
    lines.append("| feature | threshold | all acc | all ret | val acc | val ret | holdout acc | holdout ret | target |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in frontier.to_dict("records"):
        lines.append(
            f"| `{row['feature']}` | {row['train_top80_threshold']:.6g} | {pct(row['all_accuracy'])} | "
            f"{pct(row['all_retention'])} | {pct(row['validation_accuracy'])} | "
            f"{pct(row['validation_retention'])} | {pct(row['holdout_accuracy'])} | "
            f"{pct(row['holdout_retention'])} | {row['target_pass']} |"
        )
    lines.append("")
    lines.append("## Physics Read")
    lines.append("")
    if pass80.empty:
        best = candidates.iloc[0].to_dict()
    else:
        best = pass80.iloc[0].to_dict()
    lines.append(
        f"- Best >=80% retained candidate by validation/holdout balance: `{best['chooser']}` with gate `{best['gate']}`."
    )
    lines.append(
        f"- It selected {int(best['all_rows'])}/{int(best['all_base_rows'])} opportunities "
        f"({pct(best['all_retention'])}) at {pct(best['all_accuracy'])} all accuracy."
    )
    lines.append(
        f"- Validation was {pct(best['validation_accuracy'])} at {pct(best['validation_retention'])}; "
        f"holdout was {pct(best['holdout_accuracy'])} at {pct(best['holdout_retention'])}."
    )
    for split in ["validation", "holdout"]:
        metric = {
            "rows": best[f"{split}_rows"],
            "wins": best[f"{split}_wins"],
        }
        needed = block_needed(metric)
        lines.append(
            f"- To reach 95% on {split} from this candidate without losing wins, another {needed} selected losses would need to be blocked."
        )
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    if int(candidates["target_pass"].sum()) > 0:
        lines.append(
            "At least one interpretable regime candidate cleared 95% accuracy while keeping 80% of opportunities on chronological splits. This remains heartbeat telemetry, not filled-trade promotion evidence."
        )
    else:
        lines.append(
            "No interpretable regime candidate cleared 95% accuracy while keeping 80% of opportunities on chronological splits."
        )
        lines.append(
            "The current frontier is still an accuracy-volume problem: high-confidence book/physics states are real, but at an 80% trade-retention floor the validation split remains far below the promotion target."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    side_rows_raw = load_primary()
    base, side_rows = split_base(side_rows_raw)
    candidates = scan_candidates(base, side_rows)
    frontier = feature_frontier(base, side_rows)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    candidates_latest = OUT_DIR / "regime_classifier_80ret_candidates_latest.csv"
    candidates_stamp = OUT_DIR / f"regime_classifier_80ret_candidates_{generated}.csv"
    frontier_latest = OUT_DIR / "regime_classifier_80ret_frontier_latest.csv"
    frontier_stamp = OUT_DIR / f"regime_classifier_80ret_frontier_{generated}.csv"
    report_latest = OUT_DIR / "regime_classifier_80ret_latest.md"
    report_stamp = OUT_DIR / f"regime_classifier_80ret_{generated}.md"
    json_latest = OUT_DIR / "regime_classifier_80ret_latest.json"
    json_stamp = OUT_DIR / f"regime_classifier_80ret_{generated}.json"

    candidates.to_csv(candidates_latest, index=False)
    candidates.to_csv(candidates_stamp, index=False)
    frontier.to_csv(frontier_latest, index=False)
    frontier.to_csv(frontier_stamp, index=False)
    write_report(report_latest, generated, base, candidates, frontier)
    write_report(report_stamp, generated, base, candidates, frontier)

    summary = {
        "generated_utc": generated,
        "source": str(TWO_SIDE_LEDGER),
        "primary_mode": PRIMARY_MODE,
        "retention_floor": RETENTION_FLOOR,
        "target_accuracy": TARGET_ACCURACY,
        "opportunities": int(len(base)),
        "split_counts": {split: int((base["split"] == split).sum()) for split in ["train", "validation", "holdout"]},
        "candidate_count": int(len(candidates)),
        "pass_80_count": int(candidates["pass_80_retention"].sum()),
        "target_pass_count": int(candidates["target_pass"].sum()),
        "top_pass80": candidates[candidates["pass_80_retention"]].head(10).to_dict("records"),
        "frontier": frontier.to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("80% retention regime classifier probe complete")
    print(f"opportunities={len(base)} candidates={len(candidates)}")
    print(
        f"pass_80={int(candidates['pass_80_retention'].sum())} "
        f"target_pass={int(candidates['target_pass'].sum())}"
    )
    print(f"report={report_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
