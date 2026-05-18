"""Actual-approved book-edge actionability audit for v28.

Research-only; no live bot changes or orders.

Book anchoring is currently the cleanest actual-approved FV calibration lead.
This probe asks whether that better FV would have changed entry decisions in a
profitable way while retaining at least 75% of actual v28-approved entries.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_frozen_approved_entry_book_fv import load_or_create_state, parse_ts
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_approved_entry_book_edge_actionability_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_book_edge_actionability_latest.md"

MIN_RETAINED_SETTLED = 30
MIN_RETAINED_COVERAGE = 75.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["raw_probability"](row)))


def book_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["book_probability"](row)))


def ask_probability(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    cents = as_float(row.get("ask_cents") if row.get("ask_cents") is not None else row.get("entry_cents"))
    return None if cents is None else cents / 100.0


def seconds_to_close(row: dict[str, Any]) -> float | None:
    return as_float(row.get("seconds_to_close"))


def net_cents(row: dict[str, Any]) -> float | None:
    return as_float(row.get("actual_gross_cents"))


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "").lower()


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    out = []
    for raw in approved_entry_rows():
        entry_dt = parse_ts(raw.get("entry_ts"))
        if freeze_dt is not None and entry_dt is not None and entry_dt < freeze_dt:
            continue
        if raw.get("side_won") is None:
            continue
        row = dict(raw)
        ask = ask_probability(row)
        if ask is None:
            continue
        row["ask_prob"] = ask
        raw_p = raw_probability(row)
        book_p = book_probability(row)
        row["raw_probability"] = raw_p
        row["book_probability"] = book_p
        row["raw_edge_prob"] = raw_p - ask
        row["book_edge_prob"] = book_p - ask
        row["book_discount_prob"] = raw_p - book_p
        row["book_minus_raw_prob"] = book_p - raw_p
        out.append(row)
    return out


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    wins = sum(1 for row in settled if row.get("side_won") is True)
    losses = sum(1 for row in settled if row.get("side_won") is False)
    net = sum(net_cents(row) or 0.0 for row in settled)
    raw_briers = []
    book_briers = []
    raw_losses = []
    book_losses = []
    for row in settled:
        outcome = 1.0 if row.get("side_won") is True else 0.0
        raw_p = float(row["raw_probability"])
        book_p = float(row["book_probability"])
        raw_briers.append((raw_p - outcome) ** 2)
        book_briers.append((book_p - outcome) ** 2)
        raw_losses.append(logloss(raw_p, outcome))
        book_losses.append(logloss(book_p, outcome))
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "win_rate": None if not settled else wins / len(settled),
        "coverage_pct": None if denominator <= 0 else 100.0 * len(rows) / denominator,
        "net_cents": net,
        "avg_net_cents": None if not settled else net / len(settled),
        "raw_avg_brier": None if not raw_briers else sum(raw_briers) / len(raw_briers),
        "book_avg_brier": None if not book_briers else sum(book_briers) / len(book_briers),
        "book_brier_delta_vs_raw": None if not raw_briers else (sum(book_briers) - sum(raw_briers)) / len(raw_briers),
        "raw_avg_logloss": None if not raw_losses else sum(raw_losses) / len(raw_losses),
        "book_avg_logloss": None if not book_losses else sum(book_losses) / len(book_losses),
        "book_logloss_delta_vs_raw": None if not raw_losses else (sum(book_losses) - sum(raw_losses)) / len(raw_losses),
    }


PolicyFn = Callable[[dict[str, Any]], bool]


def policy_defs() -> list[tuple[str, str, PolicyFn]]:
    return [
        ("keep_all", "Control: keep every future actual v28-approved entry.", lambda row: False),
        ("skip_book_edge_lt_0", "Skip if book FV is below executable ask.", lambda row: float(row["book_edge_prob"]) < 0.0),
        ("skip_book_edge_lt_2pp", "Skip if book FV edge is below 2pp.", lambda row: float(row["book_edge_prob"]) < 0.02),
        (
            "skip_discount10_book_edge_lt_5pp",
            "Skip if raw exceeds book by at least 10pp and book edge is below 5pp.",
            lambda row: float(row["book_discount_prob"]) >= 0.10 and float(row["book_edge_prob"]) < 0.05,
        ),
        (
            "skip_discount15_book_edge_lt_5pp",
            "Skip if raw exceeds book by at least 15pp and book edge is below 5pp.",
            lambda row: float(row["book_discount_prob"]) >= 0.15 and float(row["book_edge_prob"]) < 0.05,
        ),
        (
            "skip_no_discount10",
            "Skip NO entries when raw exceeds book by at least 10pp.",
            lambda row: side(row) == "no" and float(row["book_discount_prob"]) >= 0.10,
        ),
        (
            "skip_late_discount10",
            "Skip late entries when raw exceeds book by at least 10pp.",
            lambda row: (seconds_to_close(row) is not None and float(seconds_to_close(row) or 999.0) < 240.0)
            and float(row["book_discount_prob"]) >= 0.10,
        ),
        (
            "skip_high_recross_book_edge_lt_5pp",
            "Skip high-recross entries when book edge is below 5pp.",
            lambda row: (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75
            and float(row["book_edge_prob"]) < 0.05,
        ),
    ]


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "entry_ts": row.get("entry_ts"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "gross_cents": row.get("actual_gross_cents"),
        "ask_prob": row.get("ask_prob"),
        "raw_probability": row.get("raw_probability"),
        "book_probability": row.get("book_probability"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "book_edge_prob": row.get("book_edge_prob"),
        "book_discount_prob": row.get("book_discount_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
    }


def evaluate_policy(name: str, note: str, rows: list[dict[str, Any]], denominator: int, control_net: float) -> dict[str, Any]:
    fn = next(fn for policy_name, _policy_note, fn in policy_defs() if policy_name == name)
    skipped = [row for row in rows if fn(row)]
    retained = [row for row in rows if not fn(row)]
    retained_summary = summarize(retained, denominator)
    skipped_summary = summarize(skipped, denominator)
    retained_net = as_float(retained_summary.get("net_cents")) or 0.0
    blockers = []
    if int(as_float(retained_summary.get("settled")) or 0) < MIN_RETAINED_SETTLED:
        blockers.append("retained_settled_lt_30")
    coverage = as_float(retained_summary.get("coverage_pct"))
    if coverage is None or coverage < MIN_RETAINED_COVERAGE:
        blockers.append("retained_coverage_lt_75")
    if retained_net <= control_net:
        blockers.append("net_not_better_than_keep_all")
    return {
        "policy": name,
        "note": note,
        "retained": retained_summary,
        "skipped": skipped_summary,
        "delta_net_vs_keep_all_cents": retained_net - control_net,
        "blockers": blockers,
        "skipped_rows": [compact(row) for row in skipped],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = future_rows(str(state["freeze_ts_utc"]))
    denominator = len(rows)
    control = summarize(rows, denominator)
    control_net = as_float(control.get("net_cents")) or 0.0
    policies = [evaluate_policy(name, note, rows, denominator, control_net) for name, note, _fn in policy_defs()]
    ranked = sorted(
        policies,
        key=lambda row: (
            len(row.get("blockers") or []),
            -(as_float(row.get("delta_net_vs_keep_all_cents")) or -999999.0),
            -(as_float((row.get("retained") or {}).get("coverage_pct")) or 0.0),
        ),
    )
    useful = [
        row for row in ranked
        if row["policy"] != "keep_all"
        and not row.get("blockers")
        and (as_float(row.get("delta_net_vs_keep_all_cents")) or 0.0) > 0.0
    ]
    interpretation = [
        f"Scored {denominator} future actual-approved v28 entries from book-FV freeze {state.get('freeze_ts_utc')}.",
        f"Keep-all control net is {control.get('net_cents')}c with {control.get('settled')} settled rows.",
        f"Useful retained-coverage policies found: {len(useful)}.",
    ]
    if useful:
        best = useful[0]
        retained = best.get("retained") or {}
        skipped = best.get("skipped") or {}
        interpretation.append(
            f"Best clean policy {best.get('policy')} keeps coverage {retained.get('coverage_pct')}%, "
            f"improves net by {best.get('delta_net_vs_keep_all_cents')}c, and skipped rows were "
            f"{skipped.get('wins')}/{skipped.get('losses')} for {skipped.get('net_cents')}c."
        )
    else:
        interpretation.append("No actionability rule currently beats keep-all while retaining at least 75% coverage and 30 settled rows.")
    return {
        "diagnostic": "approved_entry_book_edge_actionability",
        "freeze": state,
        "future_entries": denominator,
        "control": control,
        "ranked": ranked,
        "useful": useful,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Approved-Entry Book-Edge Actionability",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Future actual-approved entries: `{report.get('future_entries')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Policy Ranking",
        "",
        "| policy | retained settled | retained W/L | retained coverage | retained net c | skipped W/L | skipped net c | delta c | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("ranked") or []:
        retained = row.get("retained") or {}
        skipped = row.get("skipped") or {}
        lines.append(
            f"| `{row.get('policy')}` | {retained.get('settled')} | {retained.get('wins')}/{retained.get('losses')} | "
            f"{fmt(retained.get('coverage_pct'))} | {fmt(retained.get('net_cents'))} | "
            f"{skipped.get('wins')}/{skipped.get('losses')} | {fmt(skipped.get('net_cents'))} | "
            f"{fmt(row.get('delta_net_vs_keep_all_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Useful Policy Skips", ""])
    useful = report.get("useful") or []
    if not useful:
        lines.append("- none")
    for row in useful[:3]:
        lines.append(f"- `{row.get('policy')}`: {row.get('note')}")
        for skipped in (row.get("skipped_rows") or [])[:8]:
            lines.append(
                f"  - `{skipped.get('market')}` `{skipped.get('side')}` won `{skipped.get('side_won')}` "
                f"gross `{fmt(skipped.get('gross_cents'))}c`, raw/book/ask "
                f"`{fmt(skipped.get('raw_probability'))}/{fmt(skipped.get('book_probability'))}/{fmt(skipped.get('ask_prob'))}`"
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
