"""Conflict-arbitration audit for pre-registered profit-lock signals.

Recent strict forward failures often came from whole families flipping to the
wrong side together, or from one family disagreeing with the rest of the stack.
This probe stays inside the existing pre-resolution registries and tests a
small fixed set of market-level vote/consensus rules.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows here are exploratory diagnostics only; they would need a
new frozen pre-registered forward monitor before any promotion.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from probe_cross_dataset_profit_frontier import estimated_order_fee_cents, fmt_cents, fmt_roi
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, pct
from probe_profit_lock_bayesian_ev_monitor import (
    POSTERIOR_PROB_GATE,
    extra_perfect_wins_for_posterior,
    posterior_stats,
)


MAIN_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
PATH_REGISTRY = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"

REPORT_MD = OUT_DIR / "profit_lock_signal_conflict_arbitration_audit_latest.md"
REPORT_JSON = OUT_DIR / "profit_lock_signal_conflict_arbitration_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "profit_lock_signal_conflict_arbitration_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "profit_lock_signal_conflict_arbitration_blocks_latest.csv"
PENDING_CSV = OUT_DIR / "profit_lock_signal_conflict_arbitration_pending_latest.csv"

MIN_SELECTED_MARKETS = 30
BLOCK_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.70


@dataclass(frozen=True)
class Candidate:
    name: str
    label: str
    min_vote_share: float
    min_vote_margin: int
    min_votes: int = 8
    include_families: Tuple[str, ...] = ()
    exclude_families: Tuple[str, ...] = ()
    required_agree_families: Tuple[str, ...] = ()
    veto_disagree_families: Tuple[str, ...] = ()
    max_opposing_votes: Optional[int] = None


CANDIDATES: Tuple[Candidate, ...] = (
    Candidate("all_majority", "all registered locks; simple majority", 0.50, 1),
    Candidate("all_share60_margin4", "all registered locks; share>=60%; vote margin>=4", 0.60, 4),
    Candidate("all_share70_margin8", "all registered locks; share>=70%; vote margin>=8", 0.70, 8),
    Candidate("all_opposition_le4", "all registered locks; opposing votes<=4", 0.50, 1, max_opposing_votes=4),
    Candidate(
        "core_no_impulse_share60_margin4",
        "exclude impulse family; share>=60%; vote margin>=4",
        0.60,
        4,
        exclude_families=("impulse",),
    ),
    Candidate(
        "core_no_impulse_share70_margin8",
        "exclude impulse family; share>=70%; vote margin>=8",
        0.70,
        8,
        exclude_families=("impulse",),
    ),
    Candidate(
        "core_no_path_share60_margin4",
        "exclude path-confirmation; share>=60%; vote margin>=4",
        0.60,
        4,
        exclude_families=("path",),
    ),
    Candidate(
        "book_touch_agree_majority",
        "book and touch family majorities must agree with market majority",
        0.50,
        1,
        required_agree_families=("book", "touch"),
    ),
    Candidate(
        "book_hazard_agree_majority",
        "book and hazard family majorities must agree with market majority",
        0.50,
        1,
        required_agree_families=("book", "hazard"),
    ),
    Candidate(
        "book_v2_touch_agree_majority",
        "book, v2/frontier, and touch family majorities must agree",
        0.50,
        1,
        required_agree_families=("book", "v2", "touch"),
    ),
    Candidate(
        "book_score_touch_agree_majority",
        "book, score, and touch family majorities must agree",
        0.50,
        1,
        required_agree_families=("book", "score", "touch"),
    ),
    Candidate(
        "majority60_touch_veto",
        "share>=60%; margin>=4; skip if touch family disagrees",
        0.60,
        4,
        veto_disagree_families=("touch",),
    ),
    Candidate(
        "majority60_hazard_veto",
        "share>=60%; margin>=4; skip if hazard family disagrees",
        0.60,
        4,
        veto_disagree_families=("hazard",),
    ),
    Candidate(
        "majority60_path_veto",
        "share>=60%; margin>=4; skip if path-confirmation disagrees",
        0.60,
        4,
        veto_disagree_families=("path",),
    ),
    Candidate(
        "touch_hazard_consensus",
        "only touch and hazard locks vote; require their majority",
        0.50,
        1,
        min_votes=2,
        include_families=("touch", "hazard"),
    ),
    Candidate(
        "book_family_consensus",
        "only book locks vote; require book-family majority",
        0.50,
        1,
        min_votes=3,
        include_families=("book",),
    ),
)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def family_for(lock_name: str, source: str) -> str:
    name = str(lock_name)
    if source == "path" or name == "kinetic_path_confirm":
        return "path"
    if name.startswith("impulse"):
        return "impulse"
    if name.startswith("book_"):
        return "book"
    if name.startswith("score_"):
        return "score"
    if name.startswith("hazard"):
        return "hazard"
    if name.startswith("touch"):
        return "touch"
    if name.startswith("kinetic"):
        return "kinetic"
    if name.startswith("frontier") or name.startswith("v2_") or name in {"original", "challenger"}:
        return "v2"
    if name.startswith("logit"):
        return "logit"
    return "other"


def load_registry(path: Any, source: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    rows = rows.copy()
    rows["source_registry"] = source
    for col in ["registered_utc", "entry_dt", "close_dt", "lock_close_dt"]:
        if col in rows.columns:
            rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    registered = rows.get("registered_utc")
    close_dt = rows.get("close_dt")
    if registered is not None and close_dt is not None:
        rows = rows[registered.notna() & close_dt.notna() & registered.lt(close_dt)].copy()
    rows["lock_name"] = rows["lock_name"].astype(str)
    rows["side"] = rows["side"].astype(str).str.lower()
    rows = rows[rows["side"].isin({"yes", "no"})].copy()
    rows["family"] = [family_for(lock, source) for lock in rows["lock_name"]]
    rows["outcome_available_bool"] = bool_series(rows.get("outcome_available", pd.Series(False, index=rows.index)))
    rows["win_bool"] = bool_series(rows.get("win", pd.Series(False, index=rows.index)))
    for col in ["ask_cents", "entry_fee_cents", "net_pnl_cents"]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def side_counts(rows: pd.DataFrame) -> Dict[str, int]:
    return {side: int(count) for side, count in rows["side"].value_counts().items()}


def dominant_side(rows: pd.DataFrame) -> Tuple[Optional[str], int, int, float]:
    counts = side_counts(rows)
    yes = counts.get("yes", 0)
    no = counts.get("no", 0)
    total = yes + no
    if total <= 0 or yes == no:
        return None, total, 0, 0.0
    side = "yes" if yes > no else "no"
    top = max(yes, no)
    margin = abs(yes - no)
    return side, total, margin, top / total


def family_majorities(rows: pd.DataFrame) -> Dict[str, Optional[str]]:
    out: Dict[str, Optional[str]] = {}
    for family, part in rows.groupby("family"):
        side, _, _, _ = dominant_side(part)
        out[str(family)] = side
    return out


def candidate_vote_rows(rows: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    out = rows.copy()
    if candidate.include_families:
        out = out[out["family"].isin(candidate.include_families)].copy()
    if candidate.exclude_families:
        out = out[~out["family"].isin(candidate.exclude_families)].copy()
    return out


def selected_signal(rows: pd.DataFrame, candidate: Candidate) -> Optional[Dict[str, Any]]:
    vote_rows = candidate_vote_rows(rows, candidate)
    if len(vote_rows) < candidate.min_votes:
        return None
    side, total, margin, share = dominant_side(vote_rows)
    if side is None or share < candidate.min_vote_share or margin < candidate.min_vote_margin:
        return None
    counts = side_counts(vote_rows)
    opposing = counts.get("no" if side == "yes" else "yes", 0)
    if candidate.max_opposing_votes is not None and opposing > candidate.max_opposing_votes:
        return None

    fam_sides = family_majorities(rows)
    for family in candidate.required_agree_families:
        if fam_sides.get(family) != side:
            return None
    for family in candidate.veto_disagree_families:
        fam_side = fam_sides.get(family)
        if fam_side is not None and fam_side != side:
            return None

    reps = vote_rows[vote_rows["side"].eq(side)].copy()
    if reps.empty:
        return None
    reps = reps.sort_values(["entry_dt", "ask_cents", "lock_name"], na_position="last")
    rep = reps.iloc[0]
    ask = float(rep["ask_cents"]) if pd.notna(rep.get("ask_cents")) else 100.0
    fee = rep.get("entry_fee_cents")
    fee_value = float(fee) if pd.notna(fee) else float(estimated_order_fee_cents(ask, 1))
    net = rep.get("net_pnl_cents")
    net_value = float(net) if pd.notna(net) else None
    if net_value is None and bool(rep.get("outcome_available_bool")):
        net_value = (100.0 - ask - fee_value) if bool(rep.get("win_bool")) else -(ask + fee_value)
    return {
        "candidate": candidate.name,
        "candidate_label": candidate.label,
        "market": rep.get("market"),
        "close_dt": rep.get("close_dt"),
        "entry_dt": rep.get("entry_dt"),
        "side": side,
        "representative_lock": rep.get("lock_name"),
        "representative_family": rep.get("family"),
        "ask_cents": ask,
        "entry_fee_cents": fee_value,
        "entry_cost_cents": ask + fee_value,
        "outcome_available": bool(rep.get("outcome_available_bool")),
        "win": bool(rep.get("win_bool")),
        "net_pnl_cents": net_value,
        "vote_total": total,
        "vote_yes": counts.get("yes", 0),
        "vote_no": counts.get("no", 0),
        "vote_margin": margin,
        "vote_share": share,
        "families": ",".join(sorted(set(str(value) for value in rows["family"].dropna()))),
    }


def selected_for_candidate(rows: pd.DataFrame, markets: Iterable[str], candidate: Candidate) -> pd.DataFrame:
    selected: List[Dict[str, Any]] = []
    for market in markets:
        part = rows[rows["market"].eq(market)]
        signal = selected_signal(part, candidate)
        if signal is not None:
            selected.append(signal)
    return pd.DataFrame(selected)


def block_summary(universe: pd.DataFrame, selected: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    if universe.empty:
        return pd.DataFrame()
    base = universe[["market", "close_dt"]].drop_duplicates().sort_values(["close_dt", "market"]).reset_index(drop=True)
    base["block"] = base.index // BLOCK_MARKETS
    selected_markets = selected.set_index("market") if not selected.empty else pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for block, part in base.groupby("block"):
        markets = set(part["market"])
        if selected.empty:
            sel = pd.DataFrame()
        else:
            sel = selected[selected["market"].isin(markets)]
        net = float(pd.to_numeric(sel.get("net_pnl_cents", pd.Series(dtype=float)), errors="coerce").fillna(0.0).sum()) if not sel.empty else 0.0
        rows.append(
            {
                "candidate": candidate.name,
                "block": int(block),
                "start_close_dt": part["close_dt"].min(),
                "end_close_dt": part["close_dt"].max(),
                "base_markets": int(len(part)),
                "selected_markets": int(len(sel)),
                "coverage": (len(sel) / len(part)) if len(part) else None,
                "wins": int(sel["win"].sum()) if not sel.empty else 0,
                "losses": int(len(sel) - int(sel["win"].sum())) if not sel.empty else 0,
                "net_pnl_cents": net,
                "positive_and_coverage": bool(net > 0.0 and len(part) and (len(sel) / len(part)) >= MARKET_COVERAGE_FLOOR),
            }
        )
    return pd.DataFrame(rows)


def summarize_candidate(
    candidate: Candidate,
    resolved_universe: pd.DataFrame,
    pending_universe: pd.DataFrame,
    resolved_selected: pd.DataFrame,
    pending_selected: pd.DataFrame,
    blocks: pd.DataFrame,
) -> Dict[str, Any]:
    n = int(len(resolved_selected))
    wins = int(resolved_selected["win"].sum()) if n else 0
    losses = n - wins
    net = float(pd.to_numeric(resolved_selected.get("net_pnl_cents", pd.Series(dtype=float)), errors="coerce").fillna(0.0).sum()) if n else 0.0
    entry_cost = float(pd.to_numeric(resolved_selected.get("entry_cost_cents", pd.Series(dtype=float)), errors="coerce").fillna(0.0).sum()) if n else None
    avg_entry_cost = entry_cost / n if n and entry_cost is not None else None
    break_even = avg_entry_cost / 100.0 if avg_entry_cost is not None else None
    accuracy = wins / n if n else None
    coverage = n / len(resolved_universe) if len(resolved_universe) else None
    pending_n = int(len(pending_selected))
    registered_coverage = (n + pending_n) / (len(resolved_universe) + len(pending_universe)) if (len(resolved_universe) + len(pending_universe)) else None
    wilson = wilson_lower(wins, n) if n else None
    posterior = posterior_stats(wins, losses, break_even, avg_entry_cost, seed_offset=30_000 + len(candidate.name))
    extra_wins = extra_perfect_wins_for_posterior(wins, losses, break_even, avg_entry_cost)
    positive_blocks = int(blocks["positive_and_coverage"].sum()) if not blocks.empty else 0
    supported_blocks = int(len(blocks)) if not blocks.empty else 0
    positive_block_rate = positive_blocks / supported_blocks if supported_blocks else None
    worst_block = float(pd.to_numeric(blocks.get("net_pnl_cents", pd.Series(dtype=float)), errors="coerce").min()) if not blocks.empty else None
    ready_like = (
        n >= MIN_SELECTED_MARKETS
        and (coverage or 0.0) >= MARKET_COVERAGE_FLOOR
        and net > 0.0
        and wilson is not None
        and break_even is not None
        and wilson >= break_even
        and (posterior.get("prob_win_rate_gt_break_even") or 0.0) >= POSTERIOR_PROB_GATE
        and (posterior.get("posterior_p05_edge_cents") or -1.0) > 0.0
        and (positive_block_rate or 0.0) >= POSITIVE_BLOCK_RATE_FLOOR
    )
    return {
        "candidate": candidate.name,
        "label": candidate.label,
        "resolved_markets": n,
        "pending_markets": pending_n,
        "universe_resolved_markets": int(len(resolved_universe)),
        "wins": wins,
        "losses": losses,
        "accuracy": accuracy,
        "break_even": break_even,
        "wilson95_lower": wilson,
        "wilson_minus_break_even": (wilson - break_even) if wilson is not None and break_even is not None else None,
        "coverage": coverage,
        "registered_coverage": registered_coverage,
        "net_pnl_cents": net,
        "roi": (net / entry_cost) if entry_cost else None,
        "avg_entry_cost_cents": avg_entry_cost,
        "positive_block_rate": positive_block_rate,
        "worst_block_net_pnl_cents": worst_block,
        "posterior_extra_perfect_wins_to_gate": extra_wins,
        "ready_like_stress_pass": ready_like,
        **posterior,
    }


def fmt_num(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.{digits}f}"


def write_report(
    generated: str,
    summary: pd.DataFrame,
    blocks: pd.DataFrame,
    pending: pd.DataFrame,
    rows_count: int,
    resolved_markets: int,
    pending_markets: int,
) -> None:
    lines = [
        "# Profit Lock Signal Conflict Arbitration Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit using existing pre-resolution registries.",
        "- Tests market-level vote/consensus arbitration rules over signals already registered before outcomes.",
        "- Stress-pass rows are diagnostic only; they are not promotion authority without a new frozen forward monitor.",
        "",
        "## Inputs",
        "",
        f"- Registry rows read: `{rows_count}`",
        f"- Resolved market universe: `{resolved_markets}`",
        f"- Pending market universe: `{pending_markets}`",
        f"- Coverage floor: `{pct(MARKET_COVERAGE_FLOOR)}`",
        f"- Positive block-rate floor: `{pct(POSITIVE_BLOCK_RATE_FLOOR)}` with `{BLOCK_MARKETS}` markets/block",
        "",
        "## Candidate Summary",
        "",
        "| candidate | resolved/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | coverage | reg coverage | net P&L | ROI | +wins | block+cov | stress pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in summary.head(24).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {int(row['resolved_markets'])}/{int(row['pending_markets'])} | "
            f"{int(row['wins'])}/{int(row['losses'])} | {pct(row['accuracy'])} | {pct(row['break_even'])} | "
            f"{pct(row['wilson95_lower'])} | {fmt_num(row['prob_win_rate_gt_break_even'])} | "
            f"{fmt_cents(row['posterior_p05_edge_cents'])} | {pct(row['coverage'])} | "
            f"{pct(row['registered_coverage'])} | {fmt_cents(row['net_pnl_cents'])} | {fmt_roi(row['roi'])} | "
            f"{row['posterior_extra_perfect_wins_to_gate'] if pd.notna(row['posterior_extra_perfect_wins_to_gate']) else 'NA'} | "
            f"{pct(row['positive_block_rate'])} | {bool(row['ready_like_stress_pass'])} |"
        )
    lines.extend(["", "## Pending Arbitration", ""])
    if pending.empty:
        lines.append("- No currently pending markets selected by these arbitration rules.")
    else:
        lines.append("| candidate | market | side | rep lock | vote yes/no | vote share | entry |")
        lines.append("|---|---|---|---|---:|---:|---|")
        for _, row in pending.sort_values(["market", "candidate"]).head(40).iterrows():
            entry = row.get("entry_dt")
            if isinstance(entry, pd.Timestamp):
                entry_text = entry.isoformat()
            else:
                entry_text = str(entry)
            lines.append(
                f"| `{row['candidate']}` | `{row['market']}` | {row['side']} | `{row['representative_lock']}` | "
                f"{int(row['vote_yes'])}/{int(row['vote_no'])} | {pct(row['vote_share'])} | `{entry_text}` |"
            )
    if any(bool(value) for value in summary.get("ready_like_stress_pass", [])):
        lines.extend(
            [
                "",
                "## Read",
                "",
                "- At least one arbitration row passes the diagnostic stress checks, but this is still exploratory because the rule was not frozen before these outcomes.",
            ]
        )
    else:
        lines.extend(["", "## Read", "", "- No arbitration rule clears the diagnostic stress checks."])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "generated_utc": generated,
        "inputs": {
            "main_registry": str(MAIN_REGISTRY),
            "path_registry": str(PATH_REGISTRY),
            "rows_count": rows_count,
            "resolved_markets": resolved_markets,
            "pending_markets": pending_markets,
        },
        "thresholds": {
            "min_selected_markets": MIN_SELECTED_MARKETS,
            "market_coverage_floor": MARKET_COVERAGE_FLOOR,
            "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
            "posterior_prob_gate": POSTERIOR_PROB_GATE,
        },
        "rows": summary.to_dict(orient="records"),
        "pending": pending.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2), encoding="utf-8")
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCKS_CSV, index=False)
    pending.to_csv(PENDING_CSV, index=False)


def main() -> None:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    main_registry = load_registry(MAIN_REGISTRY, "main")
    path_registry = load_registry(PATH_REGISTRY, "path")
    rows = pd.concat([frame for frame in [main_registry, path_registry] if not frame.empty], ignore_index=True)
    if rows.empty:
        write_report(generated, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0, 0, 0)
        print("Profit lock signal conflict arbitration audit complete")
        print(f"report={REPORT_MD}")
        return

    market_state = (
        rows.sort_values(["close_dt", "market"])
        .groupby("market", as_index=False)
        .agg(close_dt=("close_dt", "first"), outcome_available=("outcome_available_bool", "max"))
        .sort_values(["close_dt", "market"])
        .reset_index(drop=True)
    )
    resolved_universe = market_state[market_state["outcome_available"]].copy()
    pending_universe = market_state[~market_state["outcome_available"]].copy()
    resolved_markets = list(resolved_universe["market"])
    pending_markets = list(pending_universe["market"])

    summary_rows: List[Dict[str, Any]] = []
    block_frames: List[pd.DataFrame] = []
    pending_frames: List[pd.DataFrame] = []
    for candidate in CANDIDATES:
        resolved_selected = selected_for_candidate(rows[rows["outcome_available_bool"]], resolved_markets, candidate)
        pending_selected = selected_for_candidate(rows[~rows["outcome_available_bool"]], pending_markets, candidate)
        blocks = block_summary(resolved_universe, resolved_selected, candidate)
        summary_rows.append(
            summarize_candidate(candidate, resolved_universe, pending_universe, resolved_selected, pending_selected, blocks)
        )
        if not blocks.empty:
            block_frames.append(blocks)
        if not pending_selected.empty:
            pending_frames.append(pending_selected)

    summary = pd.DataFrame(summary_rows).sort_values(
        ["ready_like_stress_pass", "net_pnl_cents", "coverage"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    blocks = pd.concat(block_frames, ignore_index=True) if block_frames else pd.DataFrame()
    pending = pd.concat(pending_frames, ignore_index=True) if pending_frames else pd.DataFrame()

    write_report(
        generated,
        summary,
        blocks,
        pending,
        rows_count=int(len(rows)),
        resolved_markets=int(len(resolved_universe)),
        pending_markets=int(len(pending_universe)),
    )
    print("Profit lock signal conflict arbitration audit complete")
    print(f"stress_pass={int(summary['ready_like_stress_pass'].sum()) if not summary.empty else 0}")
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
