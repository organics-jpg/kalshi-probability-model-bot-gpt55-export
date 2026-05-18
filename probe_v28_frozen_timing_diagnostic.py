"""Timing/side diagnostic for frozen v28 forward candidates."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import parse_ts


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_forward_candidates_latest.json"
THRESHOLD_JSON = OUT_DIR / "v28_frozen_threshold_challengers_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_timing_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_timing_diagnostic_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def selected_rows(payload: dict[str, Any], gate: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for summary in payload.get("summary") or []:
        policy = str(summary.get("policy") or "")
        for row in summary.get("selected_forward_rows") or []:
            out.append({"gate": gate, "policy": policy, **row})
    return out


def seconds_between(a: datetime | None, b: datetime | None) -> float | None:
    if a is None or b is None:
        return None
    return (a - b).total_seconds()


def build_report() -> dict[str, Any]:
    rows = selected_rows(load_json(FROZEN_JSON), "primary_p60")
    rows.extend(selected_rows(load_json(THRESHOLD_JSON), "threshold_p58"))
    markets = sorted({str(row.get("market") or "") for row in rows if row.get("market")})
    market_rows: list[dict[str, Any]] = []
    for market in markets:
        mrows = [row for row in rows if row.get("market") == market]
        parsed = [(row, parse_ts(row.get("ts_wall"))) for row in mrows]
        first_ts = min((ts for _, ts in parsed if ts is not None), default=None)
        first_side = next((row.get("side") for row, ts in parsed if ts == first_ts), None)
        for row, ts in sorted(parsed, key=lambda item: str(item[0].get("ts_wall") or "")):
            market_rows.append({
                "market": market,
                "gate": row.get("gate"),
                "policy": row.get("policy"),
                "ts_wall": row.get("ts_wall"),
                "delay_vs_first_seconds": seconds_between(ts, first_ts),
                "side": row.get("side"),
                "same_side_as_first": row.get("side") == first_side,
                "p_eff": row.get("p_eff"),
                "p_side": row.get("p_side"),
                "ask_prob": row.get("ask_prob"),
                "eff_edge_prob": row.get("eff_edge_prob"),
                "seconds_to_close": row.get("seconds_to_close"),
                "side_won": row.get("side_won"),
                "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            })
    return {
        "markets": len(markets),
        "rows": market_rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Timing Diagnostic",
        "",
        "Compares entry timing and side disagreement among frozen forward candidates.",
        "",
        f"- Markets with selected rows: `{report['markets']}`",
        "",
        "| market | gate | policy | delay s | side | same side first | p_eff | raw p | ask | edge | stc | won | net c |",
        "|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row.get('market')} | {row.get('gate')} | {row.get('policy')} | {fmt(row.get('delay_vs_first_seconds'))} | "
            f"{row.get('side')} | {row.get('same_side_as_first')} | {fmt(row.get('p_eff'))} | {fmt(row.get('p_side'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('eff_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
