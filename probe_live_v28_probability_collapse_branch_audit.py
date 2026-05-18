"""Research-only audit for the v28 probability-collapse exit branch.

The broad exit audit shows the live v28 exit engine is valuable overall, but
`mushroom_v28_probability_collapse_full` is currently negative versus holding
the same entries to settlement. This script isolates that branch and scans
small "suppress this collapse exit and hold instead" diagnostics.

No bot files are imported or modified, and no orders are submitted.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ROWS_PATH = OUT_DIR / "live_v28_exit_value_audit_rows_latest.csv"
BRANCH_REASON = "mushroom_v28_probability_collapse_full"
LOCAL_TZ = ZoneInfo("America/New_York")

MIN_SUPPRESSED_EXITS = 3
MAX_SUPPRESSED_SHARE = 0.70


@dataclass(frozen=True)
class Condition:
    column: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"{self.column}{self.op}{self.threshold:g}"

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        values = pd.to_numeric(rows.get(self.column), errors="coerce")
        if self.op == ">=":
            out = values.ge(self.threshold)
        elif self.op == "<=":
            out = values.le(self.threshold)
        else:
            raise ValueError(f"unsupported operator: {self.op}")
        return out.fillna(False)


@dataclass(frozen=True)
class Rule:
    conditions: tuple[Condition, ...]

    @property
    def label(self) -> str:
        return " AND ".join(condition.label for condition in self.conditions)

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        keep = pd.Series(True, index=rows.index)
        for condition in self.conditions:
            keep &= condition.mask(rows)
        return keep


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def local_to_utc(value: Any) -> pd.Timestamp:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    if ts.tzinfo is None:
        ts = ts.tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous="NaT")
    return ts.tz_convert("UTC")


def load_branch_rows() -> pd.DataFrame:
    if not ROWS_PATH.exists():
        raise SystemExit(f"Missing exit audit rows: {ROWS_PATH}. Run probe_live_v28_exit_value_audit.py first.")
    rows = pd.read_csv(ROWS_PATH)
    branch = rows[rows["exit_exit_reason"].astype(str).eq(BRANCH_REASON)].copy()
    if branch.empty:
        raise SystemExit(f"No {BRANCH_REASON} rows found in {ROWS_PATH}")
    for col in [
        "entry_fill_cents_used",
        "exit_exit_bid_cents",
        "exit_entry_basis_cents",
        "exit_p_hold",
        "exit_fair_hold_cents",
        "exit_fair_drawdown_cents",
        "exit_d_sigma",
        "exit_sigma_t_dollars",
        "exit_btc_age_ms",
        "exit_book_age_ms",
        "net_pnl_dollars",
        "hold_to_settlement_pnl_dollars",
        "exit_value_delta_dollars",
    ]:
        branch[col] = pd.to_numeric(branch.get(col), errors="coerce")
    branch["entry_dt_utc"] = branch["entry_ts"].map(local_to_utc)
    branch["exit_dt_utc"] = pd.to_datetime(branch["exit_dt_utc"], utc=True, errors="coerce")
    branch["position_seconds"] = (branch["exit_dt_utc"] - branch["entry_dt_utc"]).dt.total_seconds()
    branch["entry_to_exit_loss_cents"] = branch["entry_fill_cents_used"] - branch["exit_exit_bid_cents"]
    branch["fair_minus_exit_bid_cents"] = branch["exit_fair_hold_cents"] - branch["exit_exit_bid_cents"]
    branch["exit_was_hurtful"] = branch["exit_value_delta_dollars"].lt(0)
    branch["exit_was_helpful"] = branch["exit_value_delta_dollars"].gt(0)
    branch = branch.sort_values(["exit_dt_utc", "market", "side"]).reset_index(drop=True)
    return branch


def aggregate(rows: pd.DataFrame) -> dict[str, Any]:
    return {
        "n": int(len(rows)),
        "actual_exit_net_dollars": float(rows["net_pnl_dollars"].sum()),
        "hold_to_settlement_net_dollars": float(rows["hold_to_settlement_pnl_dollars"].sum()),
        "exit_value_delta_dollars": float(rows["exit_value_delta_dollars"].sum()),
        "hurtful_exits": int(rows["exit_was_hurtful"].sum()),
        "helpful_exits": int(rows["exit_was_helpful"].sum()),
    }


def split_baseline(rows: pd.DataFrame) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for split in ["train", "validation", "holdout"]:
        subset = rows[rows["split"].astype(str).eq(split)]
        out[split] = aggregate(subset)
    return out


def condition_candidates(rows: pd.DataFrame) -> list[Condition]:
    specs: dict[str, list[tuple[str, float]]] = {
        "exit_exit_bid_cents": [
            ("<=", 45.0),
            ("<=", 50.0),
            (">=", 50.0),
            (">=", 55.0),
            (">=", 60.0),
            (">=", 65.0),
        ],
        "exit_entry_basis_cents": [
            ("<=", 65.0),
            ("<=", 70.0),
            (">=", 65.0),
            (">=", 70.0),
            (">=", 75.0),
            (">=", 80.0),
        ],
        "exit_p_hold": [
            ("<=", 0.55),
            ("<=", 0.60),
            (">=", 0.60),
            (">=", 0.65),
            (">=", 0.68),
            (">=", 0.70),
        ],
        "exit_fair_drawdown_cents": [
            ("<=", 0.0),
            ("<=", 4.0),
            ("<=", 8.0),
            ("<=", 10.0),
            ("<=", 12.0),
            ("<=", 15.0),
            ("<=", 18.0),
            (">=", 15.0),
            (">=", 18.0),
            (">=", 20.0),
        ],
        "exit_sigma_t_dollars": [
            ("<=", 35.0),
            ("<=", 50.0),
            (">=", 50.0),
            (">=", 75.0),
            (">=", 100.0),
            (">=", 150.0),
        ],
        "exit_btc_age_ms": [
            ("<=", 100.0),
            ("<=", 300.0),
            ("<=", 500.0),
            (">=", 500.0),
            (">=", 800.0),
        ],
        "position_seconds": [
            ("<=", 45.0),
            ("<=", 90.0),
            ("<=", 180.0),
            (">=", 90.0),
            (">=", 180.0),
        ],
        "entry_to_exit_loss_cents": [
            ("<=", 10.0),
            (">=", 10.0),
            (">=", 15.0),
            (">=", 20.0),
        ],
        "fair_minus_exit_bid_cents": [
            ("<=", 0.0),
            (">=", 0.0),
            (">=", 5.0),
            (">=", 10.0),
            (">=", 15.0),
        ],
    }
    conditions: list[Condition] = []
    for column, column_specs in specs.items():
        if column not in rows.columns:
            continue
        if pd.to_numeric(rows[column], errors="coerce").notna().sum() < MIN_SUPPRESSED_EXITS:
            continue
        for op, threshold in column_specs:
            conditions.append(Condition(column, op, threshold))
    return conditions


def rules(rows: pd.DataFrame) -> list[Rule]:
    conditions = condition_candidates(rows)
    out = [Rule((condition,)) for condition in conditions]
    for i, first in enumerate(conditions):
        for second in conditions[i + 1 :]:
            if first.column == second.column and first.op == second.op:
                continue
            out.append(Rule((first, second)))
    return out


def evaluate_rules(rows: pd.DataFrame) -> list[dict[str, Any]]:
    baseline_actual = float(rows["net_pnl_dollars"].sum())
    split_actual = {
        split: float(rows.loc[rows["split"].astype(str).eq(split), "net_pnl_dollars"].sum())
        for split in ["train", "validation", "holdout"]
    }
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rule in rules(rows):
        label = f"suppress_collapse_exit_if_{rule.label}"
        if label in seen:
            continue
        seen.add(label)
        suppress = rule.mask(rows)
        suppressed_count = int(suppress.sum())
        if suppressed_count < MIN_SUPPRESSED_EXITS:
            continue
        suppressed_share = float(suppress.mean())
        if suppressed_share > MAX_SUPPRESSED_SHARE:
            continue
        adjusted = rows["net_pnl_dollars"].copy()
        adjusted.loc[suppress] = rows.loc[suppress, "hold_to_settlement_pnl_dollars"]
        split_adjusted: dict[str, float] = {}
        split_suppressed: dict[str, int] = {}
        for split in ["train", "validation", "holdout"]:
            split_mask = rows["split"].astype(str).eq(split)
            split_adjusted[split] = float(adjusted.loc[split_mask].sum())
            split_suppressed[split] = int(suppress.loc[split_mask].sum())
        row = {
            "rule": label,
            "suppressed_exits": suppressed_count,
            "suppressed_share": suppressed_share,
            "adjusted_net_dollars": float(adjusted.sum()),
            "delta_vs_branch_actual_dollars": float(adjusted.sum() - baseline_actual),
            "hurtful_exits_suppressed": int(rows.loc[suppress, "exit_was_hurtful"].sum()),
            "helpful_exits_suppressed": int(rows.loc[suppress, "exit_was_helpful"].sum()),
            "train_adjusted_net": split_adjusted["train"],
            "validation_adjusted_net": split_adjusted["validation"],
            "holdout_adjusted_net": split_adjusted["holdout"],
            "train_suppressed": split_suppressed["train"],
            "validation_suppressed": split_suppressed["validation"],
            "holdout_suppressed": split_suppressed["holdout"],
        }
        row["all_splits_nonworse"] = bool(
            row["train_adjusted_net"] >= split_actual["train"]
            and row["validation_adjusted_net"] >= split_actual["validation"]
            and row["holdout_adjusted_net"] >= split_actual["holdout"]
        )
        row["diagnostic_pass"] = bool(
            row["delta_vs_branch_actual_dollars"] > 0.0
            and row["all_splits_nonworse"]
            and row["hurtful_exits_suppressed"] > row["helpful_exits_suppressed"]
        )
        candidates.append(row)
    candidates.sort(
        key=lambda row: (
            row["diagnostic_pass"],
            row["delta_vs_branch_actual_dollars"],
            row["holdout_adjusted_net"],
            row["suppressed_exits"],
        ),
        reverse=True,
    )
    return candidates


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    generated: str,
    rows: pd.DataFrame,
    summary: dict[str, Any],
    splits: dict[str, dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> None:
    lines = [
        "# Live v28 Probability Collapse Exit Branch Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        f"- Research-only audit of `{BRANCH_REASON}` exits from the current live v28 fill tape.",
        "- Positive suppress delta means holding to settlement would have beaten the live collapse exit.",
        "- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.",
        "- No live bot files or processes are touched and no orders are submitted.",
        "",
        "## Branch Baseline",
        "",
        f"- Matched resolved collapse exits: {summary['n']}",
        f"- Actual collapse-exit net: ${summary['actual_exit_net_dollars']:.2f}",
        f"- Hold-to-settlement net for same entries: ${summary['hold_to_settlement_net_dollars']:.2f}",
        f"- Exit value added: ${summary['exit_value_delta_dollars']:.2f}",
        f"- Hurtful/helpful exits: {summary['hurtful_exits']} / {summary['helpful_exits']}",
        "",
        "## Split Baseline",
        "",
        "| split | n | actual | hold | exit value | hurtful/helpful |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for split in ["train", "validation", "holdout"]:
        row = splits[split]
        lines.append(
            f"| {split} | {row['n']} | ${row['actual_exit_net_dollars']:.2f} | "
            f"${row['hold_to_settlement_net_dollars']:.2f} | ${row['exit_value_delta_dollars']:.2f} | "
            f"{row['hurtful_exits']}/{row['helpful_exits']} |"
        )
    lines += [
        "",
        "## Suppress-Collapse Diagnostics",
        "",
        "| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in candidates[:25]:
        lines.append(
            f"| `{row['rule']}` | {row['diagnostic_pass']} | {row['suppressed_exits']} ({row['suppressed_share']:.2%}) | "
            f"${row['adjusted_net_dollars']:.2f} | ${row['delta_vs_branch_actual_dollars']:.2f} | "
            f"{row['hurtful_exits_suppressed']}/{row['helpful_exits_suppressed']} | "
            f"${row['train_adjusted_net']:.2f}/${row['validation_adjusted_net']:.2f}/${row['holdout_adjusted_net']:.2f} | "
            f"{row['train_suppressed']}/{row['validation_suppressed']}/{row['holdout_suppressed']} |"
        )
    if not candidates:
        lines.append("| none | False | 0 | $0.00 | $0.00 | 0/0 | $0.00/$0.00/$0.00 | 0/0/0 |")
    lines += [
        "",
        "## Read",
        "",
    ]
    if candidates:
        best = candidates[0]
        lines.append(
            f"- Best diagnostic rule: `{best['rule']}` improves the branch by "
            f"${best['delta_vs_branch_actual_dollars']:.2f} while suppressing "
            f"{best['hurtful_exits_suppressed']} hurtful and {best['helpful_exits_suppressed']} helpful exits."
        )
        lines.append(
            "- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high "
            "and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition."
        )
        if best["validation_suppressed"] == 0:
            lines.append(
                "- Caution: the top rule suppresses no validation-split exits, so it can only be forward-shadowed, not trusted."
            )
    else:
        lines.append("- No useful collapse-branch suppression diagnostic was found.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows = load_branch_rows()
    summary = aggregate(rows)
    splits = split_baseline(rows)
    candidates = evaluate_rules(rows)

    rows.to_csv(OUT_DIR / "live_v28_probability_collapse_branch_rows_latest.csv", index=False)
    write_csv(OUT_DIR / "live_v28_probability_collapse_branch_rules_latest.csv", candidates)
    write_csv(OUT_DIR / f"live_v28_probability_collapse_branch_rules_{generated}.csv", candidates)
    payload = {
        "generated_utc": generated,
        "branch_reason": BRANCH_REASON,
        "summary": summary,
        "splits": splits,
        "diagnostic_pass_count": int(sum(1 for row in candidates if row["diagnostic_pass"])),
        "top_candidates": candidates[:25],
    }
    for json_path in [
        OUT_DIR / "live_v28_probability_collapse_branch_audit_latest.json",
        OUT_DIR / f"live_v28_probability_collapse_branch_audit_{generated}.json",
    ]:
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for md_path in [
        OUT_DIR / "live_v28_probability_collapse_branch_audit_latest.md",
        OUT_DIR / f"live_v28_probability_collapse_branch_audit_{generated}.md",
    ]:
        write_report(md_path, generated, rows, summary, splits, candidates)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
