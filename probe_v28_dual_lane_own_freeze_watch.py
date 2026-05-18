"""Own-freeze watch for the best v28 dual-lane overlap.

Research-only; no live bot changes or orders.

The diagnostic dual-lane overlap is high PnL, but it is blocked because the
union itself was not born before the rows it scores. This probe creates that
birth timestamp and scores only rows after it.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_continuous_penalty import (
    PENALTIES,
    selected_rows,
)
from probe_v28_boundary_clock_feature_gate_candidate import source
from probe_v28_boundary_clock_feature_gate_candidate import net as feature_gate_net
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_top_component_mix_portfolio import live_cents
from probe_v28_top_component_parent_fill_repair_child import (
    score_variant,
    strict_rows_for_child,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_state.json"
DUAL_DIAG_JSON = OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.md"

PRIMARY_RULE = "diagnostic_observable_mid_confidence_parent_fill_quarter"
SIDECAR_PENALTY = "cheap_penalty025_rank_only"
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
FORCE_FULL_SIDECAR_BEFORE_SAMPLE = False
MARKET_INTERVAL_MINUTES = 15


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def force_replay_enabled() -> bool:
    return str(os.environ.get("V28_DUAL_FORCE_REPLAY") or "").strip().lower() in {"1", "true", "yes", "on"}


def parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def local_time_iso(value: str | None) -> str | None:
    parsed = parse_ts(value or "")
    if parsed is None:
        return None
    return parsed.astimezone().isoformat()


def possible_market_windows_since(freeze_ts: str) -> int:
    parsed = parse_ts(freeze_ts)
    if parsed is None:
        return 0
    elapsed = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
    return int(elapsed // (MARKET_INTERVAL_MINUTES * 60))


def earliest_min_sample_time(freeze_ts: str) -> str | None:
    parsed = parse_ts(freeze_ts)
    if parsed is None:
        return None
    return (parsed + timedelta(minutes=MIN_SETTLED * MARKET_INTERVAL_MINUTES)).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "dual_lane_own_freeze_watch",
        "primary_rule": PRIMARY_RULE,
        "sidecar_penalty": SIDECAR_PENALTY,
        "note": (
            "Freeze created after dual-lane overlap diagnostic rows cleared "
            "PnL/coverage/source shape but lacked their own combined birth."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def net(row: dict[str, Any]) -> float:
    for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents", "net_cents"):
        if row.get(field) is not None:
            return fnum(row.get(field))
    return 0.0


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (market(row), str(row.get("side") or ""))


def compact_sidecar_row(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    item["component"] = f"continuous_penalty:{SIDECAR_PENALTY}"
    item["weighted_net_cents"] = feature_gate_net(row)
    return item


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    entries = len(rows)
    total = sum(net(row) for row in rows)
    wins = sum(1 for row in rows if net(row) > 0)
    losses = sum(1 for row in rows if net(row) < 0)
    counts = Counter(source(row) for row in rows)
    approved = int(counts.get("approved_entry") or 0)
    reconstructed = max(0, entries - approved)
    reconstructed_share = reconstructed / entries if entries else None
    coverage = 100.0 * entries / denominator if denominator else None
    return {
        "entries": entries,
        "settled": entries,
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": total,
        "avg_net_cents": total / entries if entries else 0.0,
        "source_counts": dict(counts),
        "reconstructed_share": reconstructed_share,
        "source_gate_row_margin": int(math.floor(MAX_RECONSTRUCTED_SHARE * entries)) - reconstructed if entries else None,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "worst_loss_cents": min((net(row) for row in rows), default=0.0),
    }


def hard_blockers(summary: dict[str, Any], live: float) -> list[str]:
    blockers: list[str] = []
    settled = int(summary.get("settled") or 0)
    net_cents = fnum(summary.get("net_cents"))
    coverage = summary.get("coverage_pct")
    coverage_f = fnum(coverage, math.nan) if coverage is not None else math.nan
    recon = summary.get("reconstructed_share")
    recon_f = fnum(recon, math.nan) if recon is not None else math.nan
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if net_cents <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net_cents) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if coverage is None or not math.isfinite(coverage_f):
        blockers.append("coverage_unknown")
    elif coverage_f < TARGET_COVERAGE_MIN:
        blockers.append("coverage_lt_75pct")
    elif coverage_f > TARGET_COVERAGE_MAX:
        blockers.append("coverage_gt_90pct")
    if recon is None or not math.isfinite(recon_f):
        blockers.append("source_share_unknown")
    elif recon_f > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    elif int(summary.get("source_gate_row_margin") or 0) <= 0:
        blockers.append("source_gate_zero_row_margin")
    if net_cents <= live:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return blockers


def primary_lane(freeze_ts: str) -> dict[str, Any]:
    rows, denominator, diagnostics = strict_rows_for_child(freeze_ts)
    scored = score_variant(PRIMARY_RULE, rows, denominator, True)
    scored_rows = [row for row in scored.get("rows") or [] if isinstance(row, dict)]
    return {
        "source": "top_component_parent_fill_repair_child",
        "policy": scored.get("label"),
        "rule": PRIMARY_RULE,
        "denominator": denominator,
        "rows": scored_rows,
        "summary": summarize(scored_rows, denominator),
        "diagnostics": diagnostics,
        "parent_score": {key: scored.get(key) for key in ("entries", "settled", "wins", "losses", "coverage_pct", "net_cents", "blockers")},
    }


def sidecar_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    penalty = PENALTIES[SIDECAR_PENALTY]
    rows = [compact_sidecar_row(row) for row in selected_rows(all_rows, penalty) if row.get("side_won") is not None]
    return {
        "source": "boundary_clock_feature_gate_continuous_penalty",
        "policy": f"{label}_{SIDECAR_PENALTY}",
        "lane": label,
        "denominator": int(denominator or 0),
        "rows": rows,
        "summary": summarize(rows, int(denominator or 0)),
    }


def sidecar_stub(label: str, reason: str, denominator: int) -> dict[str, Any]:
    return {
        "source": "boundary_clock_feature_gate_continuous_penalty",
        "policy": f"{label}_{SIDECAR_PENALTY}",
        "lane": label,
        "denominator": denominator,
        "rows": [],
        "summary": summarize([], denominator),
        "skipped": True,
        "skip_reason": reason,
    }


def diagnostic_reference() -> dict[str, Any]:
    payload = load_json(DUAL_DIAG_JSON)
    top = (payload.get("top_portfolios") or [{}])[0]
    strict = (payload.get("top_strict_post_portfolios") or [{}])[0]
    return {
        "generated_at_utc": payload.get("generated_at_utc"),
        "best_diagnostic": {
            "primary": ((top.get("primary") or {}).get("policy")),
            "sidecar": ((top.get("sidecar") or {}).get("policy")),
            "union": top.get("union") or {},
            "sidecar_add_entries": top.get("sidecar_add_entries"),
            "sidecar_add_net_cents": top.get("sidecar_add_net_cents"),
            "shared_markets": top.get("shared_markets"),
            "blockers": top.get("blockers") or [],
        },
        "best_strict_post_context": {
            "primary": ((strict.get("primary") or {}).get("policy")),
            "sidecar": ((strict.get("sidecar") or {}).get("policy")),
            "union": strict.get("union") or {},
            "sidecar_add_entries": strict.get("sidecar_add_entries"),
            "sidecar_add_net_cents": strict.get("sidecar_add_net_cents"),
            "shared_markets": strict.get("shared_markets"),
            "blockers": strict.get("blockers") or [],
        },
    }


def union_lane(primary: dict[str, Any], sidecar: dict[str, Any], live: float) -> dict[str, Any]:
    primary_rows = [row for row in primary.get("rows") or [] if isinstance(row, dict)]
    sidecar_rows = [row for row in sidecar.get("rows") or [] if isinstance(row, dict)]
    primary_by_market = {market(row): row for row in primary_rows if market(row)}
    sidecar_by_market = {market(row): row for row in sidecar_rows if market(row)}
    sidecar_add_rows = [row for row in sidecar_rows if market(row) and market(row) not in primary_by_market]
    union_rows = primary_rows + sidecar_add_rows
    denominator = max(int(primary.get("denominator") or 0), int(sidecar.get("denominator") or 0), len({market(row) for row in union_rows if market(row)}))
    summary = summarize(union_rows, denominator)
    shared = sorted(set(primary_by_market) & set(sidecar_by_market))
    shared_same_side = sum(1 for item in shared if row_key(primary_by_market[item]) == row_key(sidecar_by_market[item]))
    blockers = hard_blockers(summary, live)
    return {
        "primary": {key: primary.get(key) for key in ("source", "policy", "rule", "denominator", "summary", "parent_score", "diagnostics")},
        "sidecar": {key: sidecar.get(key) for key in ("source", "policy", "lane", "denominator", "summary")},
        "summary": summary,
        "blockers": blockers,
        "live_ready": not blockers,
        "strict_forward": True,
        "shared_markets": len(shared),
        "shared_same_side": shared_same_side,
        "shared_opposite_side": len(shared) - shared_same_side,
        "sidecar_add_entries": len(sidecar_add_rows),
        "sidecar_add_net_cents": sum(net(row) for row in sidecar_add_rows),
        "sidecar_add_losses": sum(1 for row in sidecar_add_rows if net(row) < 0),
        "rows": sorted(union_rows, key=net)[:30],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    live = live_cents()
    possible_windows = possible_market_windows_since(freeze_ts)
    force_replay = force_replay_enabled()
    windows_remaining = max(0, MIN_SETTLED - possible_windows)
    min_sample_time = earliest_min_sample_time(freeze_ts)
    diagnostic = diagnostic_reference()
    if possible_windows < MIN_SETTLED and not force_replay:
        empty_summary = summarize([], max(1, possible_windows))
        stub_sidecars = [
            sidecar_stub(
                "post_dual_union_birth_entry",
                f"possible_market_windows_{possible_windows}_lt_{MIN_SETTLED}",
                max(1, possible_windows),
            ),
            sidecar_stub(
                "post_dual_union_birth_bridge",
                f"possible_market_windows_{possible_windows}_lt_{MIN_SETTLED}",
                max(1, possible_windows),
            ),
        ]
        unions = []
        for sidecar in stub_sidecars:
            summary = dict(empty_summary)
            blockers = hard_blockers(summary, live)
            unions.append({
                "primary": {
                    "source": "top_component_parent_fill_repair_child",
                    "policy": PRIMARY_RULE,
                    "rule": PRIMARY_RULE,
                    "denominator": max(1, possible_windows),
                    "summary": empty_summary,
                    "parent_score": {},
                    "diagnostics": {
                        "freeze_ts_utc": freeze_ts,
                        "possible_market_windows_since_freeze": possible_windows,
                        "pre_sample_short_circuit": True,
                    },
                },
                "sidecar": {key: sidecar.get(key) for key in ("source", "policy", "lane", "denominator", "summary", "skipped", "skip_reason")},
                "summary": summary,
                "blockers": blockers,
                "live_ready": False,
                "strict_forward": True,
                "shared_markets": 0,
                "shared_same_side": 0,
                "shared_opposite_side": 0,
                "sidecar_add_entries": 0,
                "sidecar_add_net_cents": 0,
                "sidecar_add_losses": 0,
                "rows": [],
            })
        report = {
            "generated_at_utc": utc_now_iso(),
            "state": state,
            "live_baseline_cents": live,
            "readiness_requirements": {
                "min_settled": MIN_SETTLED,
                "coverage_min_pct": TARGET_COVERAGE_MIN,
                "coverage_max_pct": TARGET_COVERAGE_MAX,
                "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
                "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
                "must_beat_live_baseline_cents": live,
                "strict_forward_only": True,
            },
            "diagnostic_source": str(DUAL_DIAG_JSON),
            "diagnostic_reference": diagnostic,
            "possible_market_windows_since_freeze": possible_windows,
            "market_windows_remaining_to_min_sample": windows_remaining,
            "earliest_min_sample_utc": min_sample_time,
            "freeze_local_time": local_time_iso(freeze_ts),
            "earliest_min_sample_local_time": local_time_iso(min_sample_time),
            "pre_sample_short_circuit": True,
            "force_replay": force_replay,
            "unions": unions,
            "interpretation": [
                "Research-only own-freeze dual-lane watch; no live bot changes or orders.",
                "This is the frozen-forward birth for the top-component parent-fill repair plus continuous cheap-side penalty union.",
                (
                    f"Only about {possible_windows} BTC 15m market windows can have occurred since freeze; "
                    f"{MIN_SETTLED} settled rows are required before live readiness is possible, so the heavy strict replay is skipped."
                ),
                (
                    f"Earliest possible {MIN_SETTLED}-window sample time is {min_sample_time}; "
                    f"{windows_remaining} more 15m windows must pass before this watch can even attempt the sample gate."
                ),
            ],
        }
        return report
    primary = primary_lane(freeze_ts)
    primary_denominator = int(primary.get("denominator") or 0)
    if primary_denominator < MIN_SETTLED and not FORCE_FULL_SIDECAR_BEFORE_SAMPLE and not force_replay:
        skip_reason = (
            f"primary_future_denominator_{primary_denominator}_lt_{MIN_SETTLED}; "
            "union cannot clear sample gate yet"
        )
        sidecars = [
            sidecar_stub("post_dual_union_birth_entry", skip_reason, primary_denominator),
            sidecar_stub("post_dual_union_birth_bridge", skip_reason, primary_denominator),
        ]
    else:
        sidecars = [
            sidecar_lane("post_dual_union_birth_entry", freeze_ts, entry_surfaces),
            sidecar_lane("post_dual_union_birth_bridge", freeze_ts, bridge_surfaces),
        ]
    unions = [union_lane(primary, sidecar, live) for sidecar in sidecars]
    unions.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum((row.get("summary") or {}).get("net_cents"), -999999.0),
        )
    )
    best = unions[0] if unions else {}
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "live_baseline_cents": live,
        "readiness_requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_min_pct": TARGET_COVERAGE_MIN,
            "coverage_max_pct": TARGET_COVERAGE_MAX,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
            "must_beat_live_baseline_cents": live,
            "strict_forward_only": True,
        },
        "diagnostic_source": str(DUAL_DIAG_JSON),
        "diagnostic_reference": diagnostic,
        "possible_market_windows_since_freeze": possible_windows,
        "market_windows_remaining_to_min_sample": windows_remaining,
        "earliest_min_sample_utc": min_sample_time,
        "freeze_local_time": local_time_iso(freeze_ts),
        "earliest_min_sample_local_time": local_time_iso(min_sample_time),
        "pre_sample_short_circuit": False,
        "force_replay": force_replay,
        "unions": unions,
        "interpretation": [
            "Research-only own-freeze dual-lane watch; no live bot changes or orders.",
            "This is the frozen-forward birth for the top-component parent-fill repair plus continuous cheap-side penalty union.",
            (
                f"Best own-freeze union has {(best.get('summary') or {}).get('settled')} settled, "
                f"W/L {(best.get('summary') or {}).get('wins')}/{(best.get('summary') or {}).get('losses')}, "
                f"net {(best.get('summary') or {}).get('net_cents')}c, "
                f"coverage {(best.get('summary') or {}).get('coverage_pct')}%, "
                f"source share {(best.get('summary') or {}).get('reconstructed_share')}, "
                f"blockers {best.get('blockers')}."
            ) if best else "No own-freeze rows scored yet.",
        ],
    }
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def write_md(report: dict[str, Any]) -> None:
    req = report.get("readiness_requirements") or {}
    diag = report.get("diagnostic_reference") or {}
    best_diag = diag.get("best_diagnostic") or {}
    best_diag_union = best_diag.get("union") or {}
    best_strict = diag.get("best_strict_post_context") or {}
    best_strict_union = best_strict.get("union") or {}
    lines = [
        "# v28 Dual-Lane Own-Freeze Watch",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Freeze local time: `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Possible 15m windows since freeze: `{report.get('possible_market_windows_since_freeze')}`",
        f"- Windows remaining to 30-row sample gate: `{report.get('market_windows_remaining_to_min_sample')}`",
        f"- Earliest possible 30-window sample UTC: `{report.get('earliest_min_sample_utc')}`",
        f"- Earliest possible 30-window sample local time: `{report.get('earliest_min_sample_local_time')}`",
        f"- Pre-sample short-circuit: `{report.get('pre_sample_short_circuit')}`",
        f"- Manual force replay: `{report.get('force_replay')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Live-Ready Requirements",
            "",
            f"- Settled own-freeze rows: `>= {req.get('min_settled')}`",
            f"- Coverage: `{req.get('coverage_min_pct')}%` to `{req.get('coverage_max_pct')}%`",
            f"- Reconstructed/rejected share: `<= {100.0 * fnum(req.get('max_reconstructed_share')):.1f}%`",
            f"- Full-loss cushion: `>= {req.get('min_full_loss_cushion')}`",
            f"- Net PnL must beat refreshed live baseline: `>{fmt(req.get('must_beat_live_baseline_cents'))}c`",
            "- Evidence must be strict post-freeze only: `true`",
            "",
            "## Diagnostic Reference",
            "",
            "| context | primary | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | blockers |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            (
                f"| best diagnostic | `{best_diag.get('primary')}` | `{best_diag.get('sidecar')}` | "
                f"{best_diag_union.get('settled')} | {best_diag_union.get('wins')}/{best_diag_union.get('losses')} | "
                f"{fmt(best_diag_union.get('coverage_pct'))}% | {money(best_diag_union.get('net_cents'))} | "
                f"{fmt(100.0 * fnum(best_diag_union.get('reconstructed_share')) if best_diag_union.get('reconstructed_share') is not None else None)}% | "
                f"{best_diag_union.get('full_loss_cushion')} | {money(best_diag.get('sidecar_add_net_cents'))} | "
                f"{best_diag.get('shared_markets')} | {', '.join(best_diag.get('blockers') or []) or 'none'} |"
            ),
            (
                f"| best strict/post context | `{best_strict.get('primary')}` | `{best_strict.get('sidecar')}` | "
                f"{best_strict_union.get('settled')} | {best_strict_union.get('wins')}/{best_strict_union.get('losses')} | "
                f"{fmt(best_strict_union.get('coverage_pct'))}% | {money(best_strict_union.get('net_cents'))} | "
                f"{fmt(100.0 * fnum(best_strict_union.get('reconstructed_share')) if best_strict_union.get('reconstructed_share') is not None else None)}% | "
                f"{best_strict_union.get('full_loss_cushion')} | {money(best_strict.get('sidecar_add_net_cents'))} | "
                f"{best_strict.get('shared_markets')} | {', '.join(best_strict.get('blockers') or []) or 'none'} |"
            ),
            "",
            "## Own-Freeze Unions",
            "",
            "| rank | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | live ready | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for idx, row in enumerate(report.get("unions") or [], 1):
        summary = row.get("summary") or {}
        sidecar = row.get("sidecar") or {}
        blockers = ", ".join(str(item) for item in row.get("blockers") or []) or "none"
        lines.append(
            f"| {idx} | `{sidecar.get('policy')}` | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
            f"{money(summary.get('net_cents'))} | {fmt(100.0 * fnum(summary.get('reconstructed_share')) if summary.get('reconstructed_share') is not None else None)}% | "
            f"{summary.get('full_loss_cushion')} | {money(row.get('sidecar_add_net_cents'))} | "
            f"{row.get('shared_markets')} | `{row.get('live_ready')}` | {blockers} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_json(OUT_JSON, report)
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
