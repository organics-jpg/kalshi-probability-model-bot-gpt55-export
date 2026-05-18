"""Book-vs-Brownian side arbitration audit.

Recent strict forward rows show a repeatable failure mode: the Brownian/RV15
side can point to a cheap early contract while the live book points the other
way, and the book side wins. This probe tests a small, fixed arbitration set:
pure book, pure Brownian70, consensus-only variants, and Brownian70 with a
book-side override on disagreement.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is historical diagnostic evidence only; strict
pre-registered forward validation remains required before promotion.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


REPORT_MD = OUT_DIR / "book_brownian_arbitration_audit_latest.md"
REPORT_JSON = OUT_DIR / "book_brownian_arbitration_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "book_brownian_arbitration_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "book_brownian_arbitration_blocks_latest.csv"
SLICES_CSV = OUT_DIR / "book_brownian_arbitration_slices_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.70


@dataclass(frozen=True)
class Candidate:
    name: str
    mode: str
    brownian_min: float = 0.70
    book_min: float = 0.60
    ask_max: float = 95.0
    min_seconds_to_close: float = 120.0
    require_margin_gate_for_book: bool = True

    @property
    def label(self) -> str:
        return (
            f"{self.mode}; brownian>={self.brownian_min:g}; book>={self.book_min:g}; "
            f"ask<={self.ask_max:g}; sec>={self.min_seconds_to_close:g}; "
            f"book_margin_gate={self.require_margin_gate_for_book}"
        )


CANDIDATES = [
    Candidate("book_margin_locked", "book_margin"),
    Candidate("brownian70_sec120", "brownian70"),
    Candidate("score_min60_lock_equiv", "score_min60"),
    Candidate("brownian70_skip_book_conflict", "brownian70_skip_conflict"),
    Candidate("book_margin_skip_brownian_conflict", "book_skip_conflict"),
    Candidate("book_margin_conflict_only", "book_conflict_only"),
    Candidate("book_conflict_only_no_margin", "book_conflict_only", require_margin_gate_for_book=False),
    Candidate("brownian70_conflict_only", "brownian_conflict_only"),
    Candidate("brownian70_override_book60_on_conflict", "brownian70_override_book"),
    Candidate("brownian70_override_book65_on_conflict", "brownian70_override_book", book_min=0.65),
    Candidate(
        "brownian70_override_book55_no_margin_on_conflict",
        "brownian70_override_book",
        book_min=0.55,
        require_margin_gate_for_book=False,
    ),
    Candidate(
        "brownian70_override_book60_no_margin_on_conflict",
        "brownian70_override_book",
        require_margin_gate_for_book=False,
    ),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def policy_selected(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    rows = side_rows.drop(columns=["split"], errors="ignore").merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    selected = select_markets_from_chosen(chosen, policy)
    if not selected.empty:
        selected["arb_source"] = policy.chooser
        selected["book_brownian_conflict"] = False
    return enrich_selected(selected)


def add_choice_sides(rows: pd.DataFrame) -> pd.DataFrame:
    book = choose_decision_sides(rows, "book_p_side")[["decision_key", "side"]].rename(columns={"side": "book_choice_side"})
    brownian = choose_decision_sides(rows, "brownian_p_rv_15m")[["decision_key", "side"]].rename(
        columns={"side": "brownian_choice_side"}
    )
    out = rows.merge(book, on="decision_key", how="left").merge(brownian, on="decision_key", how="left")
    out["book_brownian_conflict"] = out["book_choice_side"].ne(out["brownian_choice_side"])
    return out


def arbitration_selected(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    if candidate.mode == "book_margin":
        return policy_selected(
            side_rows,
            base,
            Policy("book_p_side", candidate.book_min, candidate.ask_max, candidate.min_seconds_to_close, "margin_rv15>=0"),
        )
    if candidate.mode == "brownian70":
        return policy_selected(
            side_rows,
            base,
            Policy("brownian_p_rv_15m", candidate.brownian_min, candidate.ask_max, candidate.min_seconds_to_close, "none"),
        )
    if candidate.mode == "score_min60":
        return policy_selected(
            side_rows,
            base,
            Policy("score_min_book_rv15", 0.60, candidate.ask_max, candidate.min_seconds_to_close, "none"),
        )

    rows = side_rows.drop(columns=["split"], errors="ignore").merge(base[["market", "split"]], on="market", how="inner")
    rows = add_choice_sides(rows)
    book_rows = rows[rows["side"].eq(rows["book_choice_side"])].copy()
    brownian_rows = rows[rows["side"].eq(rows["brownian_choice_side"])].copy()

    if candidate.mode == "brownian70_skip_conflict":
        eligible = brownian_rows[~brownian_rows["book_brownian_conflict"]].copy()
        eligible["arb_source"] = "brownian_agree"
    elif candidate.mode == "book_skip_conflict":
        eligible = book_rows[~book_rows["book_brownian_conflict"]].copy()
        eligible["arb_source"] = "book_agree"
    elif candidate.mode == "book_conflict_only":
        eligible = book_rows[book_rows["book_brownian_conflict"]].copy()
        eligible["arb_source"] = "book_conflict"
    elif candidate.mode == "brownian_conflict_only":
        eligible = brownian_rows[brownian_rows["book_brownian_conflict"]].copy()
        eligible["arb_source"] = "brownian_conflict"
    elif candidate.mode == "brownian70_override_book":
        agree = brownian_rows[~brownian_rows["book_brownian_conflict"]].copy()
        agree["arb_source"] = "brownian_agree"
        conflict = book_rows[book_rows["book_brownian_conflict"]].copy()
        conflict["arb_source"] = "book_conflict_override"
        eligible = pd.concat([agree, conflict], ignore_index=True, sort=False)
    else:
        raise ValueError(f"unknown arbitration mode: {candidate.mode}")

    if eligible.empty:
        return enrich_selected(eligible)

    base_mask = (
        pd.to_numeric(eligible["ask_cents"], errors="coerce").le(candidate.ask_max)
        & pd.to_numeric(eligible["seconds_to_close"], errors="coerce").ge(candidate.min_seconds_to_close)
    )
    book_source = eligible["arb_source"].astype(str).str.startswith("book")
    brownian_source = eligible["arb_source"].astype(str).str.startswith("brownian")
    source_mask = pd.Series(False, index=eligible.index)
    source_mask |= book_source & pd.to_numeric(eligible["book_p_side"], errors="coerce").ge(candidate.book_min)
    source_mask |= brownian_source & pd.to_numeric(eligible["brownian_p_rv_15m"], errors="coerce").ge(candidate.brownian_min)
    if candidate.require_margin_gate_for_book:
        source_mask &= ~book_source | pd.to_numeric(eligible["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)
    eligible = eligible[(base_mask & source_mask).fillna(False)].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt", "arb_source"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["candidate"] = candidate.name
    selected["candidate_label"] = candidate.label
    return enrich_selected(selected)


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {"dataset": dataset, "candidate": candidate.name, "label": candidate.label}
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )
    row["all_splits_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["oos_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["validation", "holdout"]
    )
    row["conflict_share"] = (
        float(selected["book_brownian_conflict"].astype(bool).mean())
        if not selected.empty and "book_brownian_conflict" in selected.columns
        else 0.0
    )
    return row


def block_base(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    return out


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = block_base(base)
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": coverage,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
                "median_ask": float(pd.to_numeric(part.get("ask_cents"), errors="coerce").median()) if n else None,
            }
        )
    return rows


def bucket(value: Any, cuts: list[float], labels: list[str]) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    for cut, label in zip(cuts, labels):
        if number <= cut:
            return label
    return labels[-1]


def slice_rows(dataset: str, candidate: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    if selected.empty:
        return []
    frame = selected.copy()
    frame["entry_dt"] = pd.to_datetime(frame["entry_dt"], utc=True, errors="coerce")
    frame["entry_hour_utc"] = frame["entry_dt"].dt.hour.astype("Int64").astype(str)
    frame["ask_bucket"] = [
        bucket(value, [60, 70, 80, 95], ["ask<=60", "ask<=70", "ask<=80", "ask<=95", "ask>95"])
        for value in pd.to_numeric(frame["ask_cents"], errors="coerce")
    ]
    frame["time_bucket"] = [
        bucket(value, [300, 600, 900], ["sec<=300", "sec<=600", "sec<=900", "sec>900"])
        for value in pd.to_numeric(frame["seconds_to_close"], errors="coerce")
    ]
    frame["conflict_bucket"] = frame.get("book_brownian_conflict", False).astype(str)
    out: List[Dict[str, Any]] = []
    for group_type, col in [
        ("split", "split"),
        ("side", "side"),
        ("source", "arb_source"),
        ("conflict", "conflict_bucket"),
        ("hour", "entry_hour_utc"),
        ("ask", "ask_bucket"),
        ("time", "time_bucket"),
    ]:
        if col not in frame.columns:
            continue
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            wins = int(part["win"].astype(bool).sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            out.append(
                {
                    "dataset": dataset,
                    "candidate": candidate,
                    "group_type": group_type,
                    "group": str(group),
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n if n else None,
                    "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
                }
            )
    return out


def block_summary(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return pd.DataFrame()
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        positive = int(part["positive_net"].sum())
        both = int((part["positive_net"] & part["coverage_pass"]).sum())
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": positive / len(part) if len(part) else None,
                "positive_coverage_block_rate": both / len(part) if len(part) else None,
                "worst_block_net_pnl_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
            }
        )
    return pd.DataFrame(rows)


def combined_rows(summary: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    bsum = block_summary(blocks)
    rows: List[Dict[str, Any]] = []
    for candidate, part in summary.groupby("candidate", sort=True):
        current = part[part["dataset"].eq("current")]
        v21 = part[part["dataset"].eq("v21")]
        if current.empty or v21.empty:
            continue
        block_part = bsum[bsum["candidate"].eq(candidate)] if not bsum.empty else pd.DataFrame()
        min_block = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        worst_block = float(block_part["worst_block_net_pnl_cents"].min()) if not block_part.empty else 0.0
        coverage = bool(current.iloc[0]["coverage_pass"]) and bool(v21.iloc[0]["coverage_pass"])
        all_splits = bool(current.iloc[0]["all_splits_positive"]) and bool(v21.iloc[0]["all_splits_positive"])
        oos = bool(current.iloc[0]["oos_positive"]) and bool(v21.iloc[0]["oos_positive"])
        robust = coverage and all_splits and oos and min_block >= POSITIVE_BLOCK_RATE_FLOOR
        rows.append(
            {
                "candidate": candidate,
                "combined_net_pnl_cents": float(current.iloc[0]["all_net_pnl_cents"] or 0.0)
                + float(v21.iloc[0]["all_net_pnl_cents"] or 0.0),
                "current_net_pnl_cents": float(current.iloc[0]["all_net_pnl_cents"] or 0.0),
                "v21_net_pnl_cents": float(v21.iloc[0]["all_net_pnl_cents"] or 0.0),
                "current_coverage": current.iloc[0]["all_coverage"],
                "v21_coverage": v21.iloc[0]["all_coverage"],
                "current_accuracy": current.iloc[0]["all_accuracy"],
                "v21_accuracy": v21.iloc[0]["all_accuracy"],
                "coverage_pass": coverage,
                "all_splits_positive": all_splits,
                "oos_positive": oos,
                "min_positive_coverage_block_rate": min_block,
                "worst_block_net_pnl_cents": worst_block,
                "robust": robust,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["robust", "combined_net_pnl_cents", "min_positive_coverage_block_rate"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame, combined: pd.DataFrame) -> None:
    lines = [
        "# Book-Brownian Arbitration Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests fixed book-vs-Brownian side arbitration rules on current and v21 datasets.",
        "- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Combined Read",
        "",
        "| candidate | combined net | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min positive+coverage blocks | worst block | robust |",
        "|---|---:|---:|---:|---:|---|---|---|---:|---:|---|",
    ]
    for _, row in combined.head(18).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {fmt_cents(row['combined_net_pnl_cents'])} | "
            f"{fmt_cents(row['current_net_pnl_cents'])}/{fmt_cents(row['v21_net_pnl_cents'])} | "
            f"{pct(row['current_accuracy'])}/{pct(row['v21_accuracy'])} | "
            f"{pct(row['current_coverage'])}/{pct(row['v21_coverage'])} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} | "
            f"{pct(row['min_positive_coverage_block_rate'])} | {fmt_cents(row['worst_block_net_pnl_cents'])} | "
            f"{bool(row['robust'])} |"
        )

    lines += [
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | conflict share | coverage | all splits | OOS |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {pct(row['conflict_share'])} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )

    bsum = block_summary(blocks)
    lines += [
        "",
        "## Block Summary",
        "",
        "| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in bsum.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | {int(row['blocks'])} | "
            f"{pct(row['positive_block_rate'])} | {pct(row['positive_coverage_block_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} |"
        )

    supported_slices = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported_slices.sort_values("net_pnl_cents", ascending=True).head(18) if not supported_slices.empty else supported_slices
    lines += [
        "",
        "## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
        "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst_slices.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | {row['group_type']}=`{row['group']}` | "
            f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
            f"{fmt_cents(row['median_ask'])} |"
        )

    robust_rows = combined[combined["robust"].astype(bool)] if not combined.empty else combined
    lines += [
        "",
        "## Read",
        "",
    ]
    if robust_rows.empty:
        lines.append("- No book-vs-Brownian arbitration row clears the full robustness gate.")
        lines.append("- Side-conflict behavior remains useful failure attribution, not promotion evidence.")
    else:
        best = robust_rows.iloc[0]
        lines.append(
            f"- Best robust diagnostic row: `{best['candidate']}` with combined net "
            f"{fmt_cents(best['combined_net_pnl_cents'])}."
        )
        lines.append("- This still requires fresh strict pre-registered validation before promotion.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    current_rows = load_side_rows()
    v21_rows = load_v21_side_rows()
    datasets = {
        "current": (market_base(current_rows), current_rows),
        "v21": (market_base(v21_rows), v21_rows),
    }
    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    selected_payload: Dict[str, Any] = {}
    for dataset, (base, side_rows) in datasets.items():
        for candidate in CANDIDATES:
            selected = arbitration_selected(side_rows, base, candidate)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_out.extend(block_rows(dataset, candidate.name, base, selected))
            slice_out.extend(slice_rows(dataset, candidate.name, selected))
            selected_payload[f"{dataset}:{candidate.name}"] = {
                "markets": int(len(selected)),
                "wins": int(selected["win"].astype(bool).sum()) if not selected.empty else 0,
            }

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    combined = combined_rows(summary, blocks)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCKS_CSV, index=False)
    slices.to_csv(SLICES_CSV, index=False)
    summary.to_csv(OUT_DIR / f"book_brownian_arbitration_summary_{generated}.csv", index=False)
    blocks.to_csv(OUT_DIR / f"book_brownian_arbitration_blocks_{generated}.csv", index=False)
    slices.to_csv(OUT_DIR / f"book_brownian_arbitration_slices_{generated}.csv", index=False)
    write_report(generated, summary, blocks, slices, combined)
    payload = {
        "generated_utc": generated,
        "candidates": [candidate.__dict__ | {"label": candidate.label} for candidate in CANDIDATES],
        "combined": combined.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
        "block_summary": block_summary(blocks).to_dict(orient="records"),
        "selected": selected_payload,
        "report": str(REPORT_MD),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"book_brownian_arbitration_audit_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (OUT_DIR / f"book_brownian_arbitration_audit_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8"
    )
    robust_count = int(combined["robust"].astype(bool).sum()) if not combined.empty else 0
    print("Book-Brownian arbitration audit complete")
    print(f"candidates={len(CANDIDATES)} robust={robust_count}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
