"""Loss-count impact scorecard for active v28 exit repairs.

Research-only; no live bot changes or orders.

The live-readiness risk blocker is currently loss-count churn rather than
account drawdown. Most exit reports emphasize PnL delta, so this report
normalizes active exit-repair lanes by how many losing trades they remove in
their own frozen windows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_repair_loss_churn_impact_latest.json"
OUT_MD = OUT_DIR / "v28_exit_repair_loss_churn_impact_latest.md"

EXIT_SOURCES = [
    {
        "family": "reduce_suppression",
        "path": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
        "evidence": "strict_forward",
        "summary_path": ("summary",),
        "candidate_path": ("freeze", "candidate"),
        "blockers_path": ("blockers",),
    },
    {
        "family": "reduce_yes_suppression",
        "path": OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json",
        "evidence": "strict_forward",
        "summary_path": ("summary",),
        "candidate_path": ("freeze", "candidate"),
        "blockers_path": ("blockers",),
    },
    {
        "family": "book_gap_suppression",
        "path": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
        "evidence": "strict_forward",
        "summary_path": ("summary",),
        "candidate_path": ("freeze", "candidate"),
        "blockers_path": ("blockers",),
    },
    {
        "family": "book_gap_loss_guard",
        "path": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
        "evidence": "strict_forward",
        "summary_path": ("summary",),
        "candidate_path": ("freeze", "candidate"),
        "blockers_path": ("blockers",),
    },
    {
        "family": "book_gap_loss_guard_v2",
        "path": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
        "evidence": "strict_forward",
        "summary_path": ("summary",),
        "candidate_path": ("freeze", "candidate"),
        "blockers_path": ("blockers",),
    },
]

LANE_SOURCES = [
    {
        "family": "reduce_depth_gate",
        "path": OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json",
        "summary_key": "summary",
    },
    {
        "family": "reduce_observable_loss_control",
        "path": OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
        "summary_key": "summary",
    },
    {
        "family": "exit_value_reduce_depth_composite",
        "path": OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json",
        "summary_key": "summary",
    },
]


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


def get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = payload
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def loss_churn_row(
    family: str,
    candidate: str,
    evidence: str,
    path: Path,
    summary: dict[str, Any],
    blockers: list[Any],
) -> dict[str, Any]:
    current_losses = as_int(summary.get("current_losses"))
    candidate_losses = as_int(summary.get("candidate_losses"))
    losses_removed = None
    if current_losses is not None and candidate_losses is not None:
        losses_removed = current_losses - candidate_losses
    settled = as_int(summary.get("settled") if summary.get("settled") is not None else summary.get("rows"))
    delta = as_float(summary.get("delta_vs_current_cents"))
    candidate_gross = as_float(summary.get("candidate_gross_cents") if summary.get("candidate_gross_cents") is not None else summary.get("net_cents"))
    current_gross = as_float(summary.get("current_gross_cents"))
    loss_control_cost = as_float(summary.get("loss_control_cost_cents"))
    suppressed_losers = as_int(summary.get("suppressed_losers"))
    suppressed_exits = as_int(summary.get("suppressed_exits"))
    return {
        "family": family,
        "candidate": candidate,
        "evidence": evidence,
        "source": str(path),
        "settled": settled,
        "current_losses": current_losses,
        "candidate_losses": candidate_losses,
        "losses_removed": losses_removed,
        "loss_reduction_pct": (
            None if current_losses in (None, 0) or losses_removed is None else losses_removed / current_losses * 100.0
        ),
        "current_gross_cents": current_gross,
        "candidate_gross_cents": candidate_gross,
        "delta_vs_current_cents": delta,
        "suppressed_exits": suppressed_exits,
        "suppressed_losers": suppressed_losers,
        "loss_control_cost_cents": loss_control_cost,
        "full_loss_cushion_estimate": as_int(summary.get("full_loss_cushion_estimate")),
        "blockers": [str(item) for item in blockers],
    }


def top_level_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in EXIT_SOURCES:
        path = source["path"]
        payload = load_json(path)
        summary = get_path(payload, source["summary_path"])
        if not isinstance(summary, dict):
            continue
        candidate = get_path(payload, source["candidate_path"]) or source["family"]
        blockers = get_path(payload, source["blockers_path"])
        rows.append(
            loss_churn_row(
                str(source["family"]),
                str(candidate),
                str(source["evidence"]),
                path,
                summary,
                blockers if isinstance(blockers, list) else [],
            )
        )
    return rows


def lane_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in LANE_SOURCES:
        path = source["path"]
        payload = load_json(path)
        for lane in payload.get("lanes") or []:
            if not isinstance(lane, dict):
                continue
            lane_name = str(lane.get("lane") or "")
            evidence = "strict_forward" if lane_name.startswith("post_") else "diagnostic_only"
            for variant in lane.get("variants") or []:
                if not isinstance(variant, dict):
                    continue
                summary = variant.get(str(source["summary_key"]))
                if not isinstance(summary, dict):
                    continue
                rows.append(
                    loss_churn_row(
                        str(source["family"]),
                        str(variant.get("candidate") or lane_name),
                        evidence,
                        path,
                        summary,
                        variant.get("blockers") if isinstance(variant.get("blockers"), list) else [],
                    )
                )
    return rows


def rank_key(row: dict[str, Any]) -> tuple[float, float, float]:
    return (
        as_float(row.get("losses_removed")) or -999.0,
        as_float(row.get("delta_vs_current_cents")) or -999999.0,
        -(as_float(row.get("loss_control_cost_cents")) or 0.0),
    )


def build_report() -> dict[str, Any]:
    rows = top_level_rows() + lane_rows()
    rows.sort(key=rank_key, reverse=True)
    strict_rows = [row for row in rows if row.get("evidence") == "strict_forward"]
    diagnostic_rows = [row for row in rows if row.get("evidence") == "diagnostic_only"]
    report = {
        "generated_at_utc": utc_now_iso(),
        "rows": rows,
        "strict_forward_rows": strict_rows,
        "diagnostic_rows": diagnostic_rows,
        "interpretation": interpretation(strict_rows, diagnostic_rows),
    }
    return report


def interpretation(strict_rows: list[dict[str, Any]], diagnostic_rows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a loss-count impact report only; it does not promote or change exit logic.",
    ]
    best_strict = strict_rows[0] if strict_rows else {}
    best_diag = diagnostic_rows[0] if diagnostic_rows else {}
    if best_strict:
        notes.append(
            f"Best strict-forward loss-count reducer is {best_strict.get('family')} / {best_strict.get('candidate')}: "
            f"losses {best_strict.get('current_losses')} -> {best_strict.get('candidate_losses')} "
            f"({best_strict.get('losses_removed')} removed), delta {best_strict.get('delta_vs_current_cents')}c, "
            f"blockers {best_strict.get('blockers')}."
        )
    if best_diag:
        notes.append(
            f"Best diagnostic-only loss-count reducer is {best_diag.get('family')} / {best_diag.get('candidate')}: "
            f"losses {best_diag.get('current_losses')} -> {best_diag.get('candidate_losses')} "
            f"({best_diag.get('losses_removed')} removed), delta {best_diag.get('delta_vs_current_cents')}c."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Repair Loss-Churn Impact",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for section, rows in [
        ("Strict Forward Rows", report.get("strict_forward_rows") or []),
        ("Diagnostic-Only Rows", report.get("diagnostic_rows") or []),
    ]:
        lines.extend([
            "",
            f"## {section}",
            "",
            "| rank | family | candidate | settled | losses current->candidate | removed | reduction | delta c | suppressed | suppressed losers | loss cost | cushion | blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(rows, start=1):
            lines.append(
                f"| {idx} | `{row.get('family')}` | `{row.get('candidate')}` | {row.get('settled')} | "
                f"{row.get('current_losses')}->{row.get('candidate_losses')} | {row.get('losses_removed')} | "
                f"{fmt(row.get('loss_reduction_pct'))}% | {fmt(row.get('delta_vs_current_cents'))} | "
                f"{row.get('suppressed_exits')} | {row.get('suppressed_losers')} | "
                f"{fmt(row.get('loss_control_cost_cents'))} | {row.get('full_loss_cushion_estimate')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
