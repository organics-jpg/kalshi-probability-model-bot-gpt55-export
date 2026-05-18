"""Exit attribution for the near-promotion boundary-clock feature gate.

Research-only; no live bot changes or orders.

The near-promotion watch shows the broad post-freeze bridge is close on sample,
PnL, and cushion but source-heavy. This probe asks whether its losing rows are
exit-policy failures, or whether current v28 exits already helped and the
remaining problem is entry/FV/source quality.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
NEAR_JSON = OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.json"
EXIT_SOURCES = {
    "reduce": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
    "book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "loss_guard_v1": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
}
OUT_JSON = OUT_DIR / "v28_feature_gate_near_promotion_exit_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_near_promotion_exit_attribution_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def net(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents")) or 0.0)


def candidate_suffix(candidate: str) -> str:
    for prefix in ("post_feature_freeze_entry_", "post_feature_freeze_bridge_"):
        if candidate.startswith(prefix):
            return candidate[len(prefix):]
    return candidate


def exit_current(row: dict[str, Any]) -> float | None:
    return as_float(row.get("current_cents") if "current_cents" in row else row.get("current_net_cents"))


def exit_hold(row: dict[str, Any]) -> float | None:
    if "hold_cents" in row:
        return as_float(row.get("hold_cents"))
    if "candidate_cents" in row:
        return as_float(row.get("candidate_cents"))
    return as_float(row.get("candidate_net_cents"))


def load_exit_index() -> dict[str, dict[tuple[str, str], list[dict[str, Any]]]]:
    output: dict[str, dict[tuple[str, str], list[dict[str, Any]]]] = {}
    for name, path in EXIT_SOURCES.items():
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if isinstance(row, dict):
                grouped[(market(row), side(row))].append(row)
        for rows in grouped.values():
            rows.sort(key=lambda item: parse_ts(item.get("exit_ts") or item.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
        output[name] = grouped
    return output


def choose_exit(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return rows[-1]


def classify_exit(current: float | None, hold: float | None) -> str:
    if current is None or hold is None:
        return "no_numeric_exit"
    if current < 0 and hold > current:
        return "exit_hurt_or_clipped_winner"
    if current < 0 and hold <= current:
        return "exit_helped_vs_hold"
    if current >= 0 and hold < current:
        return "exit_preserved_profit"
    if current >= 0 and hold > current:
        return "exit_clipped_profit"
    return "exit_neutral"


def selected_rows_for(candidate: str, lane_name: str) -> list[dict[str, Any]]:
    payload = load_json(FEATURE_JSON)
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != lane_name:
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict) and variant.get("candidate") == candidate:
                return [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    return []


def classify_row(row: dict[str, Any], exits: dict[str, dict[tuple[str, str], list[dict[str, Any]]]]) -> dict[str, Any]:
    key = (market(row), side(row))
    exit_matches = {}
    class_counts = Counter()
    best_delta: float | None = None
    for name, index in exits.items():
        match = choose_exit(index.get(key) or [])
        if not match:
            continue
        current = exit_current(match)
        hold = exit_hold(match)
        delta = None if current is None or hold is None else hold - current
        classification = classify_exit(current, hold)
        class_counts[classification] += 1
        if delta is not None and (best_delta is None or abs(delta) > abs(best_delta)):
            best_delta = delta
        exit_matches[name] = {
            "current_cents": current,
            "hold_cents": hold,
            "hold_minus_current_cents": delta,
            "classification": classification,
            "exit_reason": match.get("exit_reason"),
            "p_hold": match.get("p_hold"),
            "fair_drawdown_cents": match.get("fair_drawdown_cents"),
            "hold_book_gap": match.get("hold_book_gap"),
            "suppressed": match.get("suppressed"),
            "exit_ts": match.get("exit_ts"),
        }
    if not exit_matches:
        primary_class = "no_exit_observation"
    elif class_counts.get("exit_helped_vs_hold", 0) >= max(class_counts.values()):
        primary_class = "entry_or_fv_failure_exit_helped"
    elif class_counts.get("exit_hurt_or_clipped_winner", 0):
        primary_class = "exit_policy_failure_candidate"
    else:
        primary_class = class_counts.most_common(1)[0][0]
    return {
        "market": market(row),
        "side": side(row),
        "source": source(row),
        "entry_net_cents": net(row),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "raw_edge": row.get("raw_edge"),
        "primary_failure_class": primary_class,
        "best_hold_minus_current_cents": best_delta,
        "exit_matches": exit_matches,
    }


def build_report() -> dict[str, Any]:
    near = load_json(NEAR_JSON)
    best_candidate = str(near.get("best_candidate") or "")
    best = next((row for row in near.get("rows") or [] if row.get("candidate") == best_candidate), {})
    lane_name = str(best.get("lane") or "")
    selected = selected_rows_for(best_candidate, lane_name)
    losses = [row for row in selected if net(row) < 0]
    exits = load_exit_index()
    attributed = [classify_row(row, exits) for row in losses]
    class_counts = Counter(row["primary_failure_class"] for row in attributed)
    source_counts = Counter(row["source"] for row in attributed)
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_source": str(FEATURE_JSON),
        "near_watch_source": str(NEAR_JSON),
        "candidate": best_candidate,
        "lane": lane_name,
        "candidate_net_cents": best.get("net_cents"),
        "candidate_settled": best.get("settled"),
        "candidate_missing_gates": best.get("missing_gates"),
        "loss_rows": len(attributed),
        "loss_source_counts": dict(source_counts),
        "failure_class_counts": dict(class_counts),
        "rows": attributed,
        "interpretation": [
            "This attribution uses frozen exit artifacts as evidence only; it does not change exit logic.",
            "If losses are mostly exit_helped_vs_hold, the remaining failure is entry/FV/source quality rather than clipped exits.",
            f"{best_candidate} has failure classes {dict(class_counts)} across {len(attributed)} losing rows.",
        ],
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Near-Promotion Exit Attribution",
        "",
        "Research-only attribution. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Candidate net: `{fmt_cents(report.get('candidate_net_cents'))}`",
        f"- Candidate settled: `{report.get('candidate_settled')}`",
        f"- Candidate missing gates: `{report.get('candidate_missing_gates')}`",
        f"- Loss rows: `{report.get('loss_rows')}`",
        f"- Loss source counts: `{report.get('loss_source_counts')}`",
        f"- Failure class counts: `{report.get('failure_class_counts')}`",
        "",
        "## Loss Rows",
        "",
        "| market | source | side | entry net | primary class | best hold-current | exit summaries |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for row in report.get("rows") or []:
        exit_bits = []
        for name, match in (row.get("exit_matches") or {}).items():
            exit_bits.append(
                f"{name}: {match.get('classification')} current={fmt_cents(match.get('current_cents'))} hold={fmt_cents(match.get('hold_cents'))} reason={match.get('exit_reason')}"
            )
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {fmt_cents(row.get('entry_net_cents'))} | "
            f"{row.get('primary_failure_class')} | {fmt_cents(row.get('best_hold_minus_current_cents'))} | {'; '.join(exit_bits) or 'no match'} |"
        )
    lines.extend(["", "## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
