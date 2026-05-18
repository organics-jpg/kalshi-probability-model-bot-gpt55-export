"""Pending-outcome sensitivity for frozen book-edge FV lanes.

Research-only; no live bot changes or orders.

This shows how unresolved frozen book-edge rows would affect FV calibration if
the selected side wins or loses. It is explicitly not settlement evidence.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_frozen_book_edge_fv_calibration import probability_variants


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LANES = [
    ("p50_book_plus_05_edge_nonnegative", OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"),
    ("book_plus_05", OUT_DIR / "v28_frozen_book_plus05_entry_latest.json"),
    ("book_plus_05_no_cheap_yes_boundary", OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"),
]
OUT_JSON = OUT_DIR / "v28_frozen_book_edge_pending_sensitivity_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_book_edge_pending_sensitivity_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def clipped(p: float) -> float:
    return min(0.999, max(0.001, p))


def brier(p: float, y: float) -> float:
    return (clipped(p) - y) ** 2


def logloss(p: float, y: float) -> float:
    p = clipped(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def variant_deltas(row: dict[str, Any], y: float) -> list[dict[str, Any]]:
    variants = probability_variants(row)
    raw = variants.get("raw_v28")
    if raw is None:
        return []
    raw_brier = brier(raw, y)
    raw_logloss = logloss(raw, y)
    out = []
    for name, p in variants.items():
        out.append({
            "variant": name,
            "p": p,
            "brier_delta_vs_raw": brier(p, y) - raw_brier,
            "logloss_delta_vs_raw": logloss(p, y) - raw_logloss,
        })
    return sorted(out, key=lambda item: (item["brier_delta_vs_raw"], item["logloss_delta_vs_raw"], item["variant"]))


def pending_rows(lane: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    out = []
    for row in rows:
        if row.get("side_won") is not None:
            continue
        out.append({
            "lane": lane,
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "status": row.get("status"),
            "result": row.get("result"),
            "p_side": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "ask_cents": row.get("ask_cents"),
            "edge_cents": row.get("edge_cents"),
            "seconds_to_close": row.get("seconds_to_close"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "if_win": variant_deltas(row, 1.0),
            "if_loss": variant_deltas(row, 0.0),
        })
    return out


def build_report() -> dict[str, Any]:
    rows = []
    lane_summaries = []
    for lane, path in LANES:
        payload = load_json(path)
        pending = pending_rows(lane, payload)
        rows.extend(pending)
        summary = payload.get("summary") or {}
        lane_summaries.append({
            "lane": lane,
            "future_denominator_markets": payload.get("future_denominator_markets"),
            "entries": summary.get("entries"),
            "settled": summary.get("settled"),
            "pending": len(pending),
            "blockers": payload.get("blockers") or [],
        })
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("market") or ""), str(row.get("side") or ""))
        item = unique.setdefault(key, {
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_side": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "edge_cents": row.get("edge_cents"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "seconds_to_close": row.get("seconds_to_close"),
            "lanes": [],
            "if_win": row.get("if_win"),
            "if_loss": row.get("if_loss"),
        })
        item["lanes"].append(row.get("lane"))
    return {
        "pending_rows": len(rows),
        "unique_pending_markets": len(unique),
        "lane_summaries": lane_summaries,
        "unique_rows": list(unique.values()),
        "rows": rows,
        "interpretation": [
            "Pending sensitivity is pre-settlement only; it shows what evidence would look like under each outcome.",
            "A robust FV candidate should not depend on one pending row resolving in the favorable direction.",
            "Unique pending markets are grouped separately because related lanes may select the same market.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Book-Edge Pending Sensitivity",
        "",
        "Pre-settlement sensitivity for frozen book-edge FV lanes. No live orders.",
        "",
        f"- Pending rows: `{report.get('pending_rows')}`",
        f"- Unique pending markets: `{report.get('unique_pending_markets')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Lane Summaries",
        "",
        "| lane | denominator | entries | settled | pending | blockers |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("lane_summaries") or []:
        lines.append(
            f"| {row.get('lane')} | {row.get('future_denominator_markets')} | {row.get('entries')} | "
            f"{row.get('settled')} | {row.get('pending')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Unique Pending Markets", ""])
    for row in report.get("unique_rows") or []:
        win = (row.get("if_win") or [{}])[0]
        loss = (row.get("if_loss") or [{}])[0]
        lines.append(
            f"- `{row.get('market')}` `{row.get('side')}` lanes `{', '.join(str(item) for item in row.get('lanes') or [])}`: "
            f"p/ask/edge/recross/stc `{row.get('p_side')}/{row.get('ask_prob')}/{row.get('edge_cents')}/{row.get('recross_hazard_score')}/{row.get('seconds_to_close')}`; "
            f"if win best `{win.get('variant')}` d `{fmt(win.get('brier_delta_vs_raw'))}/{fmt(win.get('logloss_delta_vs_raw'))}`, "
            f"if loss best `{loss.get('variant')}` d `{fmt(loss.get('brier_delta_vs_raw'))}/{fmt(loss.get('logloss_delta_vs_raw'))}`"
        )
    lines.extend(["", "## Pending Rows", ""])
    for row in report.get("rows") or []:
        lines.append(
            f"- `{row.get('lane')}` `{row.get('market')}` `{row.get('side')}` source `{row.get('source')}`: "
            f"p/ask/edge/recross/stc `{row.get('p_side')}/{row.get('ask_prob')}/{row.get('edge_cents')}/{row.get('recross_hazard_score')}/{row.get('seconds_to_close')}`"
        )
        for outcome_key, label in [("if_win", "if selected side wins"), ("if_loss", "if selected side loses")]:
            best = (row.get(outcome_key) or [{}])[0]
            lines.append(
                f"  - {label}: best `{best.get('variant')}` p `{fmt(best.get('p'))}`, "
                f"Brier/logloss d `{fmt(best.get('brier_delta_vs_raw'))}/{fmt(best.get('logloss_delta_vs_raw'))}`"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
