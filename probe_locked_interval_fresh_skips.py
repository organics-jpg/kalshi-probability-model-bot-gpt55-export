"""Research-only audit of fresh intervals skipped by locked candidates.

The locked interval monitors currently sit right on the user's 80% recurring
market coverage floor. This probe explains which fresh markets were skipped and
what the best available physics/book states looked like inside those markets.

It reads existing research artifacts and writes only under logs/edge_research.
No orders are submitted and no live bot files are imported or modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct


LOCK_PATH = OUT_DIR / "locked_interval_candidates.json"
SOURCES = [
    ("locked_interval_candidates", OUT_DIR / "locked_interval_candidates_selected_latest.csv"),
    ("locked_interval_pure_physics", OUT_DIR / "locked_interval_pure_physics_selected_latest.csv"),
    ("locked_interval_logit", OUT_DIR / "locked_interval_logit_selected_latest.csv"),
    ("market_interval_fixed", OUT_DIR / "market_interval_80coverage_selected_latest.csv"),
]

SCORE_COLUMNS = [
    "score_min_book_rv15",
    "score_regime_blend",
    "brownian_p_rv_30m",
    "brownian_p_rv_15m",
    "book_p_side",
    "drift_p_5m_rv_15m",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_lock_close() -> pd.Timestamp:
    if not LOCK_PATH.exists():
        raise SystemExit(f"Missing locked interval candidate manifest: {LOCK_PATH}")
    payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    lock_close = payload.get("lock_close_dt")
    if not lock_close:
        raise SystemExit(f"Missing lock_close_dt in {LOCK_PATH}")
    parsed = pd.to_datetime(lock_close, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise SystemExit(f"Could not parse lock_close_dt={lock_close!r}")
    return parsed


def fmt(value: Any, decimals: int = 2) -> str:
    if value is None:
        return "NA"
    try:
        fvalue = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(fvalue):
        return "NA"
    return f"{fvalue:.{decimals}f}"


def load_selected(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    if df.empty:
        return df
    if "close_dt" in df.columns:
        df["close_dt"] = pd.to_datetime(df["close_dt"], utc=True, errors="coerce")
    if "candidate" not in df.columns:
        df["candidate"] = path.stem.replace("_selected_latest", "")
    if "market" in df.columns:
        df["market"] = df["market"].astype(str)
    return df


def candidate_groups(df: pd.DataFrame) -> Iterable[tuple[str, pd.DataFrame]]:
    if df.empty:
        return []
    return [(str(candidate), part.copy()) for candidate, part in df.groupby("candidate", sort=True)]


def best_row(rows: pd.DataFrame, score_col: str, mask: Optional[pd.Series] = None) -> Optional[pd.Series]:
    if score_col not in rows.columns:
        return None
    part = rows if mask is None else rows[mask].copy()
    part = part.dropna(subset=[score_col, "entry_dt", "ask_cents", "seconds_to_close"])
    if part.empty:
        return None
    part = part.sort_values([score_col, "entry_dt"], ascending=[False, True])
    return part.iloc[0]


def summarize_row(row: Optional[pd.Series], score_col: str) -> Dict[str, Any]:
    if row is None:
        return {
            f"{score_col}_max": None,
            f"{score_col}_side": None,
            f"{score_col}_ask": None,
            f"{score_col}_sec": None,
            f"{score_col}_win": None,
        }
    return {
        f"{score_col}_max": float(row.get(score_col)) if pd.notna(row.get(score_col)) else None,
        f"{score_col}_side": row.get("side"),
        f"{score_col}_ask": float(row.get("ask_cents")) if pd.notna(row.get("ask_cents")) else None,
        f"{score_col}_sec": float(row.get("seconds_to_close")) if pd.notna(row.get("seconds_to_close")) else None,
        f"{score_col}_win": bool(row.get("win")) if pd.notna(row.get("win")) else None,
    }


def market_diagnostics(side_rows: pd.DataFrame, market: str) -> Dict[str, Any]:
    rows = side_rows[side_rows["market"].astype(str) == market].copy()
    if rows.empty:
        return {"market": market, "heartbeat_rows": 0}
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    out: Dict[str, Any] = {
        "market": market,
        "heartbeat_rows": int(len(rows)),
        "first_entry_dt": rows["entry_dt"].min(),
        "last_entry_dt": rows["entry_dt"].max(),
        "close_dt": rows["close_dt"].max(),
        "outcome": rows["outcome"].dropna().iloc[0] if rows["outcome"].notna().any() else None,
        "min_ask": float(rows["ask_cents"].min()) if rows["ask_cents"].notna().any() else None,
        "median_ask": float(rows["ask_cents"].median()) if rows["ask_cents"].notna().any() else None,
        "max_seconds_to_close": float(rows["seconds_to_close"].max()) if rows["seconds_to_close"].notna().any() else None,
        "min_seconds_to_close": float(rows["seconds_to_close"].min()) if rows["seconds_to_close"].notna().any() else None,
    }
    for score_col in SCORE_COLUMNS:
        out.update(summarize_row(best_row(rows, score_col), score_col))

    economical_mask = rows["ask_cents"].le(95) & rows["seconds_to_close"].ge(60)
    economical_best = best_row(rows, "score_min_book_rv15", economical_mask)
    out.update({f"economical_{key}": value for key, value in summarize_row(economical_best, "score_min_book_rv15").items()})
    return out


def write_report(
    path: Path,
    generated: str,
    lock_close: pd.Timestamp,
    fresh_base: pd.DataFrame,
    summary_rows: List[Dict[str, Any]],
    skip_rows: List[Dict[str, Any]],
) -> None:
    lines = [
        "# Locked Interval Fresh Skip Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files are modified.",
        "- Fresh denominator is recurring BTC 15-minute markets with close time after the frozen lock.",
        f"- Lock close time: `{lock_close.isoformat()}`",
        f"- Fresh resolved interval denominator: {len(fresh_base)}",
        "",
        "## Candidate Fresh Coverage",
        "",
        "| source | candidate | selected fresh | skipped fresh | fresh coverage |",
        "|---|---|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| `{row['source']}` | `{row['candidate']}` | "
            f"{row['fresh_selected']}/{row['fresh_base']} | {row['fresh_skipped']} | {pct(row['fresh_coverage'])} |"
        )

    lines += ["", "## Skipped Fresh Markets", ""]
    if not skip_rows:
        lines.append("No skipped fresh markets were found.")
    else:
        lines.append(
            "| source | candidate | market | close | outcome | best score_min ask/sec/win | best regime ask/sec/win | best rv30 ask/sec/win | economical best ask/sec/win |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for row in skip_rows:
            lines.append(
                f"| `{row['source']}` | `{row['candidate']}` | `{row['market']}` | "
                f"{row.get('close_dt')} | {row.get('outcome')} | "
                f"{fmt(row.get('score_min_book_rv15_max'))} @ {fmt(row.get('score_min_book_rv15_ask'), 1)}c/"
                f"{fmt(row.get('score_min_book_rv15_sec'), 1)}s/{row.get('score_min_book_rv15_win')} | "
                f"{fmt(row.get('score_regime_blend_max'))} @ {fmt(row.get('score_regime_blend_ask'), 1)}c/"
                f"{fmt(row.get('score_regime_blend_sec'), 1)}s/{row.get('score_regime_blend_win')} | "
                f"{fmt(row.get('brownian_p_rv_30m_max'))} @ {fmt(row.get('brownian_p_rv_30m_ask'), 1)}c/"
                f"{fmt(row.get('brownian_p_rv_30m_sec'), 1)}s/{row.get('brownian_p_rv_30m_win')} | "
                f"{fmt(row.get('economical_score_min_book_rv15_max'))} @ {fmt(row.get('economical_score_min_book_rv15_ask'), 1)}c/"
                f"{fmt(row.get('economical_score_min_book_rv15_sec'), 1)}s/{row.get('economical_score_min_book_rv15_win')} |"
            )

    lines += ["", "## Read", ""]
    if skip_rows:
        unique_markets = sorted({str(row["market"]) for row in skip_rows})
        lines.append(f"- Unique skipped fresh markets: {len(unique_markets)} ({', '.join(unique_markets)}).")
        if any(row.get("score_min_book_rv15_win") is False for row in skip_rows):
            lines.append("- At least one skipped market had a high-scoring state that would have lost; forcing coverage could damage accuracy.")
        if any((row.get("economical_score_min_book_rv15_max") or 0.0) >= 0.80 for row in skip_rows):
            lines.append("- The skipped set includes an economical-looking state; this is a candidate for further physics falsification, not immediate promotion.")
    lines.append("- Current fresh coverage is fragile until more post-lock markets resolve.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock_close = load_lock_close()
    side_rows = load_side_rows()
    base = market_base(side_rows)
    base["close_dt"] = pd.to_datetime(base["close_dt"], utc=True, errors="coerce")
    fresh_base = base[base["close_dt"] > lock_close].copy()
    fresh_markets = set(fresh_base["market"].astype(str))

    summary_rows: List[Dict[str, Any]] = []
    skip_rows: List[Dict[str, Any]] = []

    for source, path in SOURCES:
        selected_all = load_selected(path)
        for candidate, selected in candidate_groups(selected_all):
            if "close_dt" in selected.columns:
                selected = selected[pd.to_datetime(selected["close_dt"], utc=True, errors="coerce") > lock_close].copy()
            selected_markets = set(selected["market"].astype(str)) if "market" in selected.columns else set()
            skipped = sorted(fresh_markets - selected_markets)
            summary_rows.append(
                {
                    "source": source,
                    "candidate": candidate,
                    "fresh_base": int(len(fresh_base)),
                    "fresh_selected": int(len(selected_markets & fresh_markets)),
                    "fresh_skipped": int(len(skipped)),
                    "fresh_coverage": (len(selected_markets & fresh_markets) / len(fresh_base)) if len(fresh_base) else None,
                }
            )
            for market in skipped:
                row = market_diagnostics(side_rows, market)
                row["source"] = source
                row["candidate"] = candidate
                skip_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    skip_df = pd.DataFrame(skip_rows)
    for frame in [summary_df, skip_df]:
        for col in frame.columns:
            if pd.api.types.is_datetime64_any_dtype(frame[col]):
                frame[col] = frame[col].astype(str)

    summary_latest = OUT_DIR / "locked_interval_fresh_skip_summary_latest.csv"
    skip_latest = OUT_DIR / "locked_interval_fresh_skips_latest.csv"
    md_latest = OUT_DIR / "locked_interval_fresh_skips_latest.md"
    json_latest = OUT_DIR / "locked_interval_fresh_skips_latest.json"
    summary_stamp = OUT_DIR / f"locked_interval_fresh_skip_summary_{generated}.csv"
    skip_stamp = OUT_DIR / f"locked_interval_fresh_skips_{generated}.csv"
    md_stamp = OUT_DIR / f"locked_interval_fresh_skips_{generated}.md"
    json_stamp = OUT_DIR / f"locked_interval_fresh_skips_{generated}.json"

    summary_df.to_csv(summary_latest, index=False)
    summary_df.to_csv(summary_stamp, index=False)
    skip_df.to_csv(skip_latest, index=False)
    skip_df.to_csv(skip_stamp, index=False)
    write_report(md_latest, generated, lock_close, fresh_base, summary_rows, skip_rows)
    write_report(md_stamp, generated, lock_close, fresh_base, summary_rows, skip_rows)

    payload = {
        "generated_utc": generated,
        "lock_close_dt": lock_close.isoformat(),
        "fresh_base_markets": int(len(fresh_base)),
        "summary": summary_rows,
        "skips": skip_rows,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Locked interval fresh skip audit complete")
    print(f"fresh_markets={len(fresh_base)} candidate_rows={len(summary_rows)} skip_rows={len(skip_rows)}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
