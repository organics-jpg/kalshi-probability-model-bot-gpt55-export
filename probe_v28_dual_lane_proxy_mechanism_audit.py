"""Mechanism audit for the v28 dual-lane post-freeze preview.

Research-only; no live bot changes and no orders.

The dual-lane own-freeze scorer remains authoritative for promotion. This audit
only explains the current post-freeze preview rows so the live-readiness
bottlenecks are explicit rather than hand-waved.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PREVIEW_JSON = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_proxy_mechanism_audit_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_proxy_mechanism_audit_latest.md"


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


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def cents(value: Any) -> str:
    if value is None:
        return ""
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return str(value)
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def pct(value: Any) -> str:
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return "n/a"
    return f"{100.0 * amount:.2f}%"


def row_flags(row: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    source = str(row.get("source") or "")
    raw_edge = fnum(row.get("raw_edge"))
    adjusted = fnum(row.get("adjusted_edge"))
    recross = fnum(row.get("recross_hazard_score"))
    abs_d = fnum(row.get("abs_d_sigma"))
    ask = fnum(row.get("ask_prob"))
    missing = set(str(item) for item in row.get("sidecar_missing") or [])

    if source != "approved_entry":
        flags.append("source_quality")
    if math.isfinite(raw_edge) and raw_edge < 0.0:
        flags.append("negative_fv_edge")
    elif math.isfinite(raw_edge) and raw_edge < 0.05:
        flags.append("weak_fv_edge")
    if math.isfinite(adjusted) and adjusted < 0.0:
        flags.append("cheap_side_penalty_negative")
    if math.isfinite(abs_d) and abs_d < 0.85:
        flags.append("low_distance_confidence")
    if math.isfinite(ask) and ask < 0.65:
        flags.append("cheap_low_ask")
    if math.isfinite(recross) and recross > 0.60:
        flags.append("high_recross")
    for reason in sorted(missing):
        flags.append(f"sidecar_missing_{reason}")
    return flags


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None and row.get("net_cents") is not None]
    net = sum(fnum(row.get("net_cents"), 0.0) for row in settled)
    flag_counts = Counter(flag for row in rows for flag in row_flags(row))
    source_counts = Counter(str(row.get("source") or "unknown") for row in rows)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "pnl_wins": sum(1 for row in settled if fnum(row.get("net_cents"), 0.0) > 0.0),
        "pnl_losses": sum(1 for row in settled if fnum(row.get("net_cents"), 0.0) < 0.0),
        "pnl_flats": sum(1 for row in settled if fnum(row.get("net_cents"), 0.0) == 0.0),
        "net_cents": net,
        "source_counts": dict(source_counts),
        "flag_counts": dict(flag_counts),
        "avg_raw_edge": (
            sum(fnum(row.get("raw_edge"), 0.0) for row in rows if math.isfinite(fnum(row.get("raw_edge"))))
            / max(1, sum(1 for row in rows if math.isfinite(fnum(row.get("raw_edge")))))
        ),
        "avg_abs_d_sigma": (
            sum(fnum(row.get("abs_d_sigma"), 0.0) for row in rows if math.isfinite(fnum(row.get("abs_d_sigma"))))
            / max(1, sum(1 for row in rows if math.isfinite(fnum(row.get("abs_d_sigma")))))
        ),
        "avg_recross_hazard": (
            sum(
                fnum(row.get("recross_hazard_score"), 0.0)
                for row in rows
                if math.isfinite(fnum(row.get("recross_hazard_score")))
            )
            / max(1, sum(1 for row in rows if math.isfinite(fnum(row.get("recross_hazard_score")))))
        ),
        "avg_ask_prob": (
            sum(fnum(row.get("ask_prob"), 0.0) for row in rows if math.isfinite(fnum(row.get("ask_prob"))))
            / max(1, sum(1 for row in rows if math.isfinite(fnum(row.get("ask_prob")))))
        ),
    }


def decision_read(sidecar: dict[str, Any], primary: dict[str, Any]) -> list[str]:
    reads: list[str] = []
    sidecar_entries = int(sidecar.get("entries") or 0)
    primary_entries = int(primary.get("entries") or 0)
    sidecar_net = fnum(sidecar.get("net_cents"), 0.0)
    primary_net = fnum(primary.get("net_cents"), 0.0)
    primary_flags = primary.get("flag_counts") if isinstance(primary.get("flag_counts"), dict) else {}

    if sidecar_entries and sidecar_net > 0:
        reads.append("sidecar_live_shadow_shape_is_constructive")
    if sidecar_entries and int(sidecar.get("pnl_wins") or 0) > int(sidecar.get("wins") or 0):
        reads.append("sidecar_exit_policy_can_win_when_settlement_loses")
    if primary_entries and int(primary_flags.get("source_quality") or 0) == primary_entries:
        reads.append("primary_proxy_is_all_source_quality_risk")
    if primary_entries and int(primary_flags.get("negative_fv_edge") or 0) == primary_entries:
        reads.append("primary_proxy_is_all_negative_fv_edge")
    if primary_entries and int(primary_flags.get("low_distance_confidence") or 0) == primary_entries:
        reads.append("primary_proxy_is_below_sidecar_distance_band")
    if primary_entries and (
        primary_net <= 0
        or int(primary_flags.get("source_quality") or 0) == primary_entries
        or int(primary_flags.get("low_distance_confidence") or 0) == primary_entries
    ):
        reads.append("do_not_use_primary_proxy_as_live_ready_evidence")
    reads.append("own_freeze_strict_rows_remain_authoritative")
    return reads


def build_report() -> dict[str, Any]:
    preview = load_json(PREVIEW_JSON)
    sidecar_rows = [row for row in preview.get("sidecar_preview_rows") or [] if isinstance(row, dict)]
    primary_rows = [row for row in preview.get("primary_pocket_rows") or [] if isinstance(row, dict)]
    sidecar = summarize_rows(sidecar_rows)
    primary = summarize_rows(primary_rows)
    return {
        "generated_at_utc": utc_now_iso(),
        "source_preview": str(PREVIEW_JSON),
        "preview_generated_at_utc": preview.get("generated_at_utc"),
        "freeze_ts_utc": preview.get("freeze_ts_utc"),
        "freeze_local_time": preview.get("freeze_local_time"),
        "live_baseline_cents": preview.get("live_baseline_cents"),
        "sidecar_summary": sidecar,
        "primary_proxy_summary": primary,
        "mechanism_read": decision_read(sidecar, primary),
        "primary_proxy_rows": [
            {
                "market": row.get("market"),
                "source": row.get("source"),
                "side": row.get("side"),
                "side_won": row.get("side_won"),
                "net_cents": row.get("net_cents"),
                "raw_edge": row.get("raw_edge"),
                "adjusted_edge": row.get("adjusted_edge"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "ask_prob": row.get("ask_prob"),
                "flags": row_flags(row),
            }
            for row in primary_rows
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    sidecar = report.get("sidecar_summary") if isinstance(report.get("sidecar_summary"), dict) else {}
    primary = report.get("primary_proxy_summary") if isinstance(report.get("primary_proxy_summary"), dict) else {}
    lines = [
        "# v28 Dual-Lane Proxy Mechanism Audit",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Preview generated UTC: `{report.get('preview_generated_at_utc')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        "",
        "## Mechanism Read",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.get("mechanism_read") or [])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| lane preview | entries | settled | W/L | net | avg raw edge | avg abs d | avg recross | avg ask | source counts |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            (
                f"| sidecar exact observable | {sidecar.get('entries')} | {sidecar.get('settled')} | "
                f"{sidecar.get('wins')}/{sidecar.get('losses')} | {cents(sidecar.get('net_cents'))} | "
                f"{fnum(sidecar.get('avg_raw_edge'), 0.0):.3f} | {fnum(sidecar.get('avg_abs_d_sigma'), 0.0):.3f} | "
                f"{fnum(sidecar.get('avg_recross_hazard'), 0.0):.3f} | {fnum(sidecar.get('avg_ask_prob'), 0.0):.3f} | "
                f"`{sidecar.get('source_counts')}` |"
            ),
            (
                f"| primary sizing-pocket proxy | {primary.get('entries')} | {primary.get('settled')} | "
                f"{primary.get('wins')}/{primary.get('losses')} | {cents(primary.get('net_cents'))} | "
                f"{fnum(primary.get('avg_raw_edge'), 0.0):.3f} | {fnum(primary.get('avg_abs_d_sigma'), 0.0):.3f} | "
                f"{fnum(primary.get('avg_recross_hazard'), 0.0):.3f} | {fnum(primary.get('avg_ask_prob'), 0.0):.3f} | "
                f"`{primary.get('source_counts')}` |"
            ),
            "",
            "## Realized PnL Sign",
            "",
            "| lane preview | settlement W/L | PnL W/L/flat | read |",
            "|---|---:|---:|---|",
            (
                f"| sidecar exact observable | {sidecar.get('wins')}/{sidecar.get('losses')} | "
                f"{sidecar.get('pnl_wins')}/{sidecar.get('pnl_losses')}/{sidecar.get('pnl_flats')} | "
                "exit policy can make realized PnL differ from settlement direction |"
            ),
            (
                f"| primary sizing-pocket proxy | {primary.get('wins')}/{primary.get('losses')} | "
                f"{primary.get('pnl_wins')}/{primary.get('pnl_losses')}/{primary.get('pnl_flats')} | "
                "source-quality and FV-risk proxy only |"
            ),
            "",
            "## Primary Proxy Failure Flags",
            "",
            "| flag | rows | share |",
            "|---|---:|---:|",
        ]
    )
    primary_entries = int(primary.get("entries") or 0)
    for flag, count in sorted((primary.get("flag_counts") or {}).items(), key=lambda item: (-int(item[1]), str(item[0]))):
        share = (int(count) / primary_entries) if primary_entries else math.nan
        lines.append(f"| `{flag}` | {count} | {pct(share)} |")
    rows = report.get("primary_proxy_rows") or []
    if rows:
        lines.extend(
            [
                "",
                "## Primary Proxy Rows",
                "",
                "| market | source | side | won | net | raw | adjusted | recross | abs d | ask | flags |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in rows:
            flags = ", ".join(str(item) for item in row.get("flags") or [])
            lines.append(
                f"| `{row.get('market')}` | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{cents(row.get('net_cents'))} | {fnum(row.get('raw_edge'), 0.0):.3f} | "
                f"{fnum(row.get('adjusted_edge'), 0.0):.3f} | {fnum(row.get('recross_hazard_score'), 0.0):.3f} | "
                f"{fnum(row.get('abs_d_sigma'), 0.0):.3f} | {fnum(row.get('ask_prob'), 0.0):.3f} | {flags} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
