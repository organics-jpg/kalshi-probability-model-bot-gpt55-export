"""Join audit for recross loss-churn guard against exit-clock rows.

Research-only; no live bot changes or orders.

The continuous scorecard has recross_hazard_score but no exit_ts. The common
exit-clock rows have exit_ts but no recross feature. This audit tests whether a
timestamp-tolerant row join is stable enough to support a future frozen watch.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import build_scored_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
MATERIALIZED_EXIT_CLOCK_JSON = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.json"
OUT_JSON = OUT_DIR / "v28_loss_churn_recross_exit_clock_join_audit_latest.json"
OUT_MD = OUT_DIR / "v28_loss_churn_recross_exit_clock_join_audit_latest.md"

JOIN_TOLERANCE_SECONDS = 0.5
RECROSS_FLOOR = 0.45


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def build_scorecard_index(rows: list[dict[str, Any]]) -> dict[tuple[Any, Any], list[dict[str, Any]]]:
    index: dict[tuple[Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index[(row.get("market"), row.get("side"))].append(row)
    for bucket in index.values():
        bucket.sort(key=lambda row: parse_ts(row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
    return index


def closest_match(
    exit_row: dict[str, Any],
    scorecard_index: dict[tuple[Any, Any], list[dict[str, Any]]],
    tolerance_seconds: float,
) -> tuple[dict[str, Any] | None, float | None, int]:
    exit_ts = parse_ts(exit_row.get("entry_ts"))
    if exit_ts is None:
        return None, None, 0
    candidates: list[tuple[float, dict[str, Any]]] = []
    for candidate in scorecard_index.get((exit_row.get("market"), exit_row.get("side")), []):
        candidate_ts = parse_ts(candidate.get("entry_ts"))
        if candidate_ts is None:
            continue
        diff = abs((exit_ts - candidate_ts).total_seconds())
        if diff <= tolerance_seconds:
            candidates.append((diff, candidate))
    if len(candidates) != 1:
        return None, None, len(candidates)
    diff, row = candidates[0]
    return row, diff, 1


def joined_rows(
    exit_rows: list[dict[str, Any]],
    scorecard_rows: list[dict[str, Any]],
    tolerance_seconds: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    index = build_scorecard_index(scorecard_rows)
    matched: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for exit_row in exit_rows:
        score_row, diff, candidate_count = closest_match(exit_row, index, tolerance_seconds)
        if candidate_count == 0:
            unmatched.append(exit_row)
            continue
        if candidate_count > 1 or score_row is None:
            ambiguous.append({**exit_row, "join_candidate_count": candidate_count})
            continue
        actual = fnum(exit_row.get("actual_gross_cents"))
        hold = fnum(exit_row.get("hold_gross_cents"))
        matched.append({
            **exit_row,
            "join_diff_seconds": diff,
            "recross_hazard_score": score_row.get("recross_hazard_score"),
            "scorecard_entry_ts": score_row.get("entry_ts"),
            "scorecard_actual_gross_cents": score_row.get("actual_gross_cents"),
            "scorecard_hold_gross_cents": score_row.get("hold_gross_cents"),
            "hold_delta_cents": hold - actual,
        })
    return matched, unmatched, ambiguous


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [
        row for row in rows
        if row.get("recross_hazard_score") is not None
        and fnum(row.get("recross_hazard_score"), -1.0) >= RECROSS_FLOOR
    ]
    current_net = sum(fnum(row.get("actual_gross_cents")) for row in rows)
    selected_current = sum(fnum(row.get("actual_gross_cents")) for row in selected)
    selected_hold = sum(fnum(row.get("hold_gross_cents")) for row in selected)
    candidate_net = current_net - selected_current + selected_hold
    helpful = [row for row in selected if fnum(row.get("hold_gross_cents")) > fnum(row.get("actual_gross_cents"))]
    harmful = [row for row in selected if fnum(row.get("hold_gross_cents")) < fnum(row.get("actual_gross_cents"))]
    flats = [row for row in selected if fnum(row.get("hold_gross_cents")) == fnum(row.get("actual_gross_cents"))]
    return {
        "rows": len(rows),
        "selected_rows": len(selected),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_cents": selected_hold - selected_current,
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flats),
        "loss_flips": sum(
            1 for row in selected
            if fnum(row.get("actual_gross_cents")) < 0 <= fnum(row.get("hold_gross_cents"))
        ),
        "new_losses": sum(
            1 for row in selected
            if fnum(row.get("actual_gross_cents")) >= 0 > fnum(row.get("hold_gross_cents"))
        ),
        "max_join_diff_seconds": max((fnum(row.get("join_diff_seconds")) for row in rows), default=0.0),
        "selected_examples": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "entry_ts": row.get("entry_ts"),
                "scorecard_entry_ts": row.get("scorecard_entry_ts"),
                "exit_ts": row.get("exit_ts"),
                "exit_reason": row.get("exit_reason"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "actual_gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "hold_delta_cents": row.get("hold_delta_cents"),
                "join_diff_seconds": row.get("join_diff_seconds"),
            }
            for row in selected[:12]
        ],
    }


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    scorecard_rows = [row for row in scorecard.get("rows") or [] if isinstance(row, dict)]
    snapshot = load_json(MATERIALIZED_EXIT_CLOCK_JSON)
    exit_rows = [row for row in snapshot.get("rows") or [] if isinstance(row, dict)]
    source = str(MATERIALIZED_EXIT_CLOCK_JSON)
    if not exit_rows:
        exit_rows = list(build_scored_rows())
        source = "probe_v28_exit_policy_common_clock_watch.build_scored_rows"
    exact, exact_unmatched, exact_ambiguous = joined_rows(exit_rows, scorecard_rows, 0.0)
    matched, unmatched, ambiguous = joined_rows(exit_rows, scorecard_rows, JOIN_TOLERANCE_SECONDS)
    summary = summarize(matched)
    blockers = ["research_only", "not_frozen_forward", "join_audit_not_watch"]
    if unmatched:
        blockers.append("unmatched_exit_clock_rows_present")
    if ambiguous:
        blockers.append("ambiguous_join_rows_present")
    if summary["selected_rows"] < 30:
        blockers.append("selected_decisions_lt_30")
    if summary["delta_cents"] <= 0:
        blockers.append("delta_not_positive")
    interpretation = [
        "Exact entry timestamp join is not viable because artifacts differ by small capture offsets.",
        f"A {JOIN_TOLERANCE_SECONDS}s join is stable if unmatched and ambiguous counts are zero.",
        "The joined exit-clock denominator is the relevant surface for any future recross exit watch; it is smaller than the continuous-scorecard replay.",
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scorecard_rows": len(scorecard_rows),
        "exit_clock_rows": len(exit_rows),
        "exit_clock_source": source,
        "materialized_snapshot_generated_at_utc": snapshot.get("generated_at_utc"),
        "rule": {"recross_hazard_score_min": RECROSS_FLOOR},
        "exact_join": {
            "matched": len(exact),
            "unmatched": len(exact_unmatched),
            "ambiguous": len(exact_ambiguous),
        },
        "tolerance_join": {
            "tolerance_seconds": JOIN_TOLERANCE_SECONDS,
            "matched": len(matched),
            "unmatched": len(unmatched),
            "ambiguous": len(ambiguous),
            "summary": summary,
        },
        "blockers": blockers,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    join = report.get("tolerance_join") or {}
    summary = join.get("summary") or {}
    lines = [
        "# v28 Loss-Churn Recross Exit-Clock Join Audit",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Exit-clock source: `{report.get('exit_clock_source')}`",
        f"- Scorecard / exit-clock rows: `{report.get('scorecard_rows')}` / `{report.get('exit_clock_rows')}`",
        f"- Exact join matched/unmatched/ambiguous: `{report.get('exact_join', {}).get('matched')}` / `{report.get('exact_join', {}).get('unmatched')}` / `{report.get('exact_join', {}).get('ambiguous')}`",
        f"- Tolerance join seconds: `{join.get('tolerance_seconds')}`",
        f"- Tolerance join matched/unmatched/ambiguous: `{join.get('matched')}` / `{join.get('unmatched')}` / `{join.get('ambiguous')}`",
        f"- Selected rows: `{summary.get('selected_rows')}`",
        f"- Delta / candidate net: `{money(summary.get('delta_cents'))}` / `{money(summary.get('candidate_net_cents'))}`",
        f"- Helpful/harmful/flat/new-loss: `{summary.get('helpful_rows')}` / `{summary.get('harmful_rows')}` / `{summary.get('flat_rows')}` / `{summary.get('new_losses')}`",
        f"- Max join diff seconds: `{summary.get('max_join_diff_seconds')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Selected Examples",
        "",
        "| market | side | entry ts | scorecard ts | exit ts | recross | actual | hold | delta | join diff |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in summary.get("selected_examples") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | `{row.get('entry_ts')}` | "
            f"`{row.get('scorecard_entry_ts')}` | `{row.get('exit_ts')}` | "
            f"{row.get('recross_hazard_score')} | {money(row.get('actual_gross_cents'))} | "
            f"{money(row.get('hold_gross_cents'))} | {money(row.get('hold_delta_cents'))} | "
            f"{row.get('join_diff_seconds')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
