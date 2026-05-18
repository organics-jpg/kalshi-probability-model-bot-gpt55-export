"""Delta report for registered-signal readiness snapshots.

This makes each refresh cycle's effect visible by comparing the newest
registered-signal readiness CSV with the prior stamped snapshot.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_market_interval_80coverage import OUT_DIR, clean_json, pct


STAMP_RE = re.compile(r"profit_lock_registered_signal_readiness_(\d{8}_\d{6}Z)\.csv$")


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def stamped_csvs() -> List[tuple[str, Path]]:
    rows: List[tuple[str, Path]] = []
    for path in OUT_DIR.glob("profit_lock_registered_signal_readiness_*.csv"):
        match = STAMP_RE.match(path.name)
        if match:
            rows.append((match.group(1), path))
    rows.sort(key=lambda item: item[0])
    return rows


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes"}


def numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([0.0] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0.0)


def fmt_num(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if pd.isna(number):
        return "NA"
    return f"{number:.{digits}f}"


def build_delta(previous: pd.DataFrame, current: pd.DataFrame) -> List[Dict[str, Any]]:
    prev = previous.copy()
    curr = current.copy()
    prev["name"] = prev["name"].astype(str)
    curr["name"] = curr["name"].astype(str)
    merged = curr.merge(prev, on="name", how="outer", suffixes=("_current", "_previous"))
    rows: List[Dict[str, Any]] = []
    for _, item in merged.iterrows():
        name = str(item["name"])
        row: Dict[str, Any] = {"name": name}
        for col in ["registered", "resolved", "pending", "wins", "losses"]:
            current_value = item.get(f"{col}_current")
            previous_value = item.get(f"{col}_previous")
            current_num = 0 if pd.isna(current_value) else int(float(current_value))
            previous_num = 0 if pd.isna(previous_value) else int(float(previous_value))
            row[col] = current_num
            row[f"delta_{col}"] = current_num - previous_num
        for col in [
            "accuracy",
            "break_even",
            "wilson95_lower",
            "prob_win_rate_gt_break_even",
            "posterior_p05_edge_cents",
            "registered_coverage",
            "resolved_coverage",
            "net_pnl_cents",
            "net_roi_on_cost",
        ]:
            current_value = item.get(f"{col}_current")
            previous_value = item.get(f"{col}_previous")
            current_num = None if pd.isna(current_value) else float(current_value)
            previous_num = None if pd.isna(previous_value) else float(previous_value)
            row[col] = current_num
            row[f"delta_{col}"] = (
                current_num - previous_num
                if current_num is not None and previous_num is not None
                else None
            )
        for col in ["registered_ready", "registered_bayesian_ready"]:
            current_value = bool_value(item.get(f"{col}_current"))
            previous_value = bool_value(item.get(f"{col}_previous"))
            row[col] = current_value
            row[f"delta_{col}"] = int(current_value) - int(previous_value)
        rows.append(row)
    rows.sort(
        key=lambda row: (
            abs(float(row.get("delta_net_pnl_cents") or 0.0)),
            abs(int(row.get("delta_resolved") or 0)),
            abs(int(row.get("delta_registered") or 0)),
        ),
        reverse=True,
    )
    return rows


def changed(row: Dict[str, Any]) -> bool:
    delta_cols = [
        "delta_registered",
        "delta_resolved",
        "delta_pending",
        "delta_wins",
        "delta_losses",
        "delta_net_pnl_cents",
        "delta_prob_win_rate_gt_break_even",
        "delta_registered_ready",
        "delta_registered_bayesian_ready",
    ]
    return any(abs(float(row.get(col) or 0.0)) > 1e-9 for col in delta_cols)


def write_report(generated: str, previous_stamp: str | None, current_stamp: str | None, rows: List[Dict[str, Any]]) -> None:
    changed_rows = [row for row in rows if changed(row)]
    lines = [
        "# Profit Lock Registered-Signal Delta",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only report; no orders are submitted and no bot files or live processes are touched.",
        "- Compares the newest registered-signal readiness snapshot with the prior stamped snapshot.",
        "",
        f"- Previous snapshot: `{previous_stamp or 'none'}`",
        f"- Current snapshot: `{current_stamp or 'none'}`",
        "",
        "## Changed Locks",
        "",
        "| lock | reg/res/pending delta | wins/losses delta | net delta | acc | P(p>BE) | p05 edge | ready delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if not changed_rows:
        lines.append("| none | 0/0/0 | 0/0 | 0.0c | NA | NA | NA | 0/0 |")
    for row in changed_rows:
        lines.append(
            f"| {row['name']} | "
            f"{row['delta_registered']:+d}/{row['delta_resolved']:+d}/{row['delta_pending']:+d} | "
            f"{row['delta_wins']:+d}/{row['delta_losses']:+d} | "
            f"{fmt_cents(row.get('delta_net_pnl_cents'))} | "
            f"{pct(row.get('accuracy'))} | {fmt_num(row.get('prob_win_rate_gt_break_even'))} | "
            f"{fmt_cents(row.get('posterior_p05_edge_cents'))} | "
            f"{row['delta_registered_ready']:+d}/{row['delta_registered_bayesian_ready']:+d} |"
        )
    lines += ["", "## Read", ""]
    if changed_rows:
        numeric_rows = [row for row in changed_rows if row.get("delta_net_pnl_cents") is not None]
        if numeric_rows:
            best = max(numeric_rows, key=lambda row: float(row.get("delta_net_pnl_cents") or 0.0))
            worst = min(numeric_rows, key=lambda row: float(row.get("delta_net_pnl_cents") or 0.0))
            lines.append(f"- Best net delta: {best['name']} at {fmt_cents(best.get('delta_net_pnl_cents'))}.")
            lines.append(f"- Worst net delta: {worst['name']} at {fmt_cents(worst.get('delta_net_pnl_cents'))}.")
        else:
            lines.append("- Registered counts changed, but no resolved net P&L changed.")
    else:
        lines.append("- No registered readiness fields changed from the prior snapshot.")

    md_latest = OUT_DIR / "profit_lock_registered_signal_delta_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_registered_signal_delta_{generated}.md"
    csv_latest = OUT_DIR / "profit_lock_registered_signal_delta_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_registered_signal_delta_{generated}.csv"
    json_latest = OUT_DIR / "profit_lock_registered_signal_delta_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_registered_signal_delta_{generated}.json"
    for path in [md_latest, md_stamp]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(csv_latest, index=False)
    pd.DataFrame(rows).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "previous_snapshot": previous_stamp,
        "current_snapshot": current_stamp,
        "rows": rows,
        "changed_count": len(changed_rows),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    stamps = stamped_csvs()
    if len(stamps) < 2:
        write_report(generated, None, stamps[-1][0] if stamps else None, [])
        print("Profit lock registered-signal delta complete")
        print("changed=0")
        print(f"report={OUT_DIR / 'profit_lock_registered_signal_delta_latest.md'}")
        return 0
    previous_stamp, previous_path = stamps[-2]
    current_stamp, current_path = stamps[-1]
    previous = pd.read_csv(previous_path)
    current = pd.read_csv(current_path)
    rows = build_delta(previous, current)
    write_report(generated, previous_stamp, current_stamp, rows)
    print("Profit lock registered-signal delta complete")
    print(f"changed={sum(changed(row) for row in rows)}")
    print(f"report={OUT_DIR / 'profit_lock_registered_signal_delta_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
