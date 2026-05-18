"""Promotion gate checker for the v38 edge-hole candidate.

Research-only. Reads existing artifacts and live-shadow registry; does not
modify live bot code, processes, or orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v38_edge_hole_shadow_monitor as shadow
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RETRO_JSON = OUT_DIR / "v38_edge_hole_veto_candidate_latest.json"
TEMPORAL_JSON = OUT_DIR / "v38_edge_hole_temporal_stability_latest.json"
LODO_JSON = OUT_DIR / "v38_edge_hole_lodo_audit_latest.json"
REGISTRY_CSV = OUT_DIR / "v38_edge_hole_shadow_registry_latest.csv"
FUNNEL_JSON = OUT_DIR / "v38_edge_hole_shadow_funnel_latest.json"
DENOMINATOR_JSON = OUT_DIR / "v38_edge_hole_forward_denominator_latest.json"
REPORT_MD = OUT_DIR / "v38_edge_hole_promotion_gate_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_promotion_gate_latest.json"

PRIMARY = "block_market_first_edge_8_20"

MIN_RETRO_COVERAGE = 0.75
MIN_FORWARD_FINALIZED = 50
MIN_FORWARD_MARKETS = 50
MIN_FORWARD_DAYS = 2
MIN_FORWARD_COVERAGE = 0.75


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not np.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def retro_gate() -> dict[str, Any]:
    payload = load_json(RETRO_JSON)
    records = payload.get("records") or []
    primary = next((row for row in records if row.get("candidate") == PRIMARY), None)
    if not primary:
        return {"pass": False, "reason": "primary retrospective record missing"}
    checks = {
        "coverage": float(primary.get("min_split_coverage") or 0.0) >= MIN_RETRO_COVERAGE,
        "fee_net": float(primary.get("min_split_net_after_fees_dollars") or 0.0) > 0.0,
        "fee_1c_entry": float(primary.get("min_split_net_after_fees_1c_entry_dollars") or 0.0) > 0.0,
        "block10": int((primary.get("block10") or {}).get("positive_blocks") or 0) >= 7,
    }
    return {"pass": all(checks.values()), "checks": checks, "record": primary}


def temporal_gate() -> dict[str, Any]:
    payload = load_json(TEMPORAL_JSON)
    primary = (payload.get("candidates") or {}).get(PRIMARY) or {}
    if not primary:
        return {"pass": False, "reason": "temporal primary record missing"}
    positive_days = int(primary.get("positive_1c_days") or 0)
    total_days = int(primary.get("total_days") or 0)
    worst = primary.get("worst_1c_day_cents")
    checks = {
        "all_days_positive": total_days > 0 and positive_days == total_days,
        "worst_day_positive": worst is not None and float(worst) > 0.0,
    }
    return {"pass": all(checks.values()), "checks": checks, "record": primary}


def lodo_gate() -> dict[str, Any]:
    payload = load_json(LODO_JSON)
    records = payload.get("lodo") or []
    if not records:
        return {"pass": False, "reason": "LODO records missing"}
    checks = {
        "selected_all_positive": all(float(row.get("selected_holdout_1c") or 0.0) > 0.0 for row in records),
        "primary_all_positive": all(float(row.get("primary_holdout_1c") or 0.0) > 0.0 for row in records),
    }
    return {"pass": all(checks.values()), "checks": checks, "records": records}


def forward_gate() -> dict[str, Any]:
    if not REGISTRY_CSV.exists() or REGISTRY_CSV.stat().st_size == 0:
        return {"pass": False, "reason": "forward registry missing"}
    rows = pd.read_csv(REGISTRY_CSV, low_memory=False)
    if rows.empty:
        return {"pass": False, "reason": "forward registry empty"}
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    finalized = rows[rows["status"].astype(str).str.lower().isin(["exited", "settled"])].copy()
    finalized["fee_net_cents"] = pd.to_numeric(finalized.get("fee_net_cents"), errors="coerce").fillna(0.0)
    finalized["fee_net_1c_entry_cents"] = pd.to_numeric(finalized.get("fee_net_1c_entry_cents"), errors="coerce").fillna(0.0)
    finalized["cost_cents"] = pd.to_numeric(finalized.get("selected_ask_cents"), errors="coerce").fillna(0.0) * shadow.QTY
    finalized["entry_day_utc"] = finalized["entry_dt"].dt.strftime("%Y-%m-%d")
    fee_net = float(finalized["fee_net_cents"].sum())
    fee_1c = float(finalized["fee_net_1c_entry_cents"].sum())
    cost = float(finalized["cost_cents"].sum())
    days = int(finalized["entry_day_utc"].nunique()) if not finalized.empty else 0
    markets = int(rows["market"].astype(str).nunique())
    denominator = load_json(DENOMINATOR_JSON)
    denominator_markets = int(denominator.get("market_count") or 0)
    funnel = load_json(FUNNEL_JSON)
    funnel_markets = int(((funnel.get("post_lock_opportunities") or {}).get("markets")) or 0)
    post_lock_markets = denominator_markets or funnel_markets
    denominator_source = "forward_denominator" if denominator_markets else "shadow_funnel"
    forward_coverage = float(markets / post_lock_markets) if post_lock_markets else None
    checks = {
        "min_finalized": int(len(finalized)) >= MIN_FORWARD_FINALIZED,
        "min_registered_markets": markets >= MIN_FORWARD_MARKETS,
        "min_days": days >= MIN_FORWARD_DAYS,
        "fee_net_positive": fee_net > 0.0,
        "fee_1c_positive": fee_1c > 0.0,
        "coverage": forward_coverage is not None and forward_coverage >= MIN_FORWARD_COVERAGE,
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "registered": int(len(rows)),
        "finalized": int(len(finalized)),
        "markets": markets,
        "post_lock_markets": post_lock_markets,
        "denominator_source": denominator_source,
        "coverage": forward_coverage,
        "days": days,
        "fee_net_cents": fee_net,
        "fee_1c_entry_cents": fee_1c,
        "cost_cents": cost,
        "fee_net_roi": float(fee_net / cost) if cost > 0 else None,
    }


def build() -> dict[str, Any]:
    retro = retro_gate()
    temporal = temporal_gate()
    lodo = lodo_gate()
    forward = forward_gate()
    gates = {
        "retrospective": retro,
        "temporal": temporal,
        "leave_one_day_out": lodo,
        "strict_forward": forward,
    }
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": PRIMARY,
        "thresholds": {
            "min_retro_coverage": MIN_RETRO_COVERAGE,
            "min_forward_finalized": MIN_FORWARD_FINALIZED,
            "min_forward_markets": MIN_FORWARD_MARKETS,
            "min_forward_days": MIN_FORWARD_DAYS,
            "min_forward_coverage": MIN_FORWARD_COVERAGE,
        },
        "gates": gates,
        "pass": all(gate.get("pass") for gate in gates.values()),
    }


def write_report(payload: dict[str, Any]) -> None:
    forward = payload["gates"]["strict_forward"]
    lines = [
        "# v38 Edge-Hole Promotion Gate",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Candidate: `{payload['candidate']}`",
        "",
        "## Result",
        "",
        f"- Overall pass: `{payload['pass']}`",
        f"- Retrospective pass: `{payload['gates']['retrospective'].get('pass')}`",
        f"- Temporal pass: `{payload['gates']['temporal'].get('pass')}`",
        f"- Leave-one-day-out pass: `{payload['gates']['leave_one_day_out'].get('pass')}`",
        f"- Strict-forward pass: `{forward.get('pass')}`",
        "",
        "## Strict Forward",
        "",
        f"- Registered rows: {forward.get('registered', 0)}",
        f"- Finalized rows: {forward.get('finalized', 0)} / required {MIN_FORWARD_FINALIZED}",
        f"- Registered markets: {forward.get('markets', 0)} / required {MIN_FORWARD_MARKETS}",
        f"- Forward days: {forward.get('days', 0)} / required {MIN_FORWARD_DAYS}",
        f"- Forward coverage vs post-lock observed markets: {pct(forward.get('coverage'))} / required {pct(MIN_FORWARD_COVERAGE)}",
        f"- Forward denominator source: `{forward.get('denominator_source', 'unknown')}`",
        f"- Fee-adjusted P&L: {dollars_cents(forward.get('fee_net_cents', 0.0))}",
        f"- Fee-adjusted P&L with 1c entry haircut: {dollars_cents(forward.get('fee_1c_entry_cents', 0.0))}",
        f"- Fee-adjusted ROI: {pct(forward.get('fee_net_roi'))}",
        "",
        "## Read",
        "",
    ]
    if payload["pass"]:
        lines.append("- Candidate passes the configured promotion gate.")
    else:
        lines.append("- Candidate does not pass promotion gate. The current blocker is strict-forward sample size/coverage.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    write_report(payload)
    print("v38 edge-hole promotion gate complete")
    print(f"pass={payload['pass']} report={REPORT_MD}")
    print(
        "forward "
        f"registered={payload['gates']['strict_forward'].get('registered', 0)} "
        f"finalized={payload['gates']['strict_forward'].get('finalized', 0)} "
        f"coverage={payload['gates']['strict_forward'].get('coverage')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
