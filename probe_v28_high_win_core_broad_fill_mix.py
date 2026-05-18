"""Mix high-win feature-gate cores with broad raw03 fillers.

Research-only; no live bot changes or orders.

This probes a concrete mix/match idea: use high-win, high-conviction
feature-gate source-quality proxy rows as the core, then fill back to broad
75% participation from the observable raw03 feature-gate lane. Source labels
are audit-only.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
SOURCE_PROXY_JSON = OUT_DIR / "v28_feature_gate_source_quality_proxy_latest.json"
OUT_JSON = OUT_DIR / "v28_high_win_core_broad_fill_mix_latest.json"
OUT_MD = OUT_DIR / "v28_high_win_core_broad_fill_mix_latest.md"

MIN_SETTLED = 30
COVERAGE_FLOOR = 75.0
COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_CUSHION = 3


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


def fnum(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def row_net(row: dict[str, Any]) -> float:
    if row.get("weighted_net_cents") is not None:
        return fnum(row.get("weighted_net_cents"))
    return fnum(row.get("net_cents"))


def source_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    bad = sum(1 for row in rows if row.get("source") != "approved_entry")
    return bad / len(rows)


def rank_score(row: dict[str, Any], rank: str) -> float:
    if rank == "raw_edge":
        return fnum(row.get("raw_edge"))
    if rank == "p_side":
        return fnum(row.get("p_side") or row.get("raw_edge"))
    if rank == "absd":
        return fnum(row.get("abs_d_sigma"))
    if rank == "low_recross":
        return -fnum(row.get("recross_hazard_score"))
    if rank == "ask_confirm":
        ask = fnum(row.get("ask_prob"))
        return ask if ask >= 0.5 else 1.0 - ask
    if rank == "source_proxy_score":
        return (
            2.0 * fnum(row.get("p_side") or 0.0)
            + 0.35 * fnum(row.get("abs_d_sigma"))
            + 0.20 * fnum(row.get("raw_edge"))
            - 0.75 * fnum(row.get("recross_hazard_score"))
        )
    return fnum(row.get("raw_edge"))


def summarize(rows: list[dict[str, Any]], denominator: int, label: str, strict_forward: bool) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(row_net(row) for row in rows)
    wins = sum(1 for row in settled if row_net(row) > 0)
    losses = sum(1 for row in settled if row_net(row) < 0)
    recon = source_share(rows)
    coverage = 100.0 * len(rows) / denominator if denominator else None
    blockers: list[str] = []
    if not strict_forward:
        blockers.append("diagnostic_only_prefreeze")
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0:
        blockers.append("net_not_positive")
    if recon is None or recon > MAX_RECON_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if int(max(0.0, net) // 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "candidate": label,
        "strict_forward": strict_forward,
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "reconstructed_share": recon,
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "source_counts": {
            "approved_entry": sum(1 for row in rows if row.get("source") == "approved_entry"),
            "reconstructed_or_rejected": sum(1 for row in rows if row.get("source") != "approved_entry"),
        },
        "blockers": blockers,
        "worst_rows": sorted(rows, key=row_net)[:8],
    }


def feature_gate_variant(feature_gate: dict[str, Any], lane_name: str, candidate: str) -> tuple[int, list[dict[str, Any]]]:
    lane = next((item for item in feature_gate.get("lanes") or [] if item.get("lane") == lane_name), {})
    variant = next((item for item in lane.get("variants") or [] if item.get("candidate") == candidate), {})
    return int(fnum(lane.get("future_denominator"))), list(variant.get("rows") or [])


def high_win_cores(source_proxy: dict[str, Any], lane_name: str) -> list[dict[str, Any]]:
    lane = next((item for item in source_proxy.get("lanes") or [] if item.get("lane") == lane_name), {})
    variants = []
    for variant in lane.get("top_variants") or []:
        settled = int(fnum(variant.get("settled")))
        wins = int(fnum(variant.get("wins")))
        losses = int(fnum(variant.get("losses")))
        if settled < 14:
            continue
        win_rate = wins / settled if settled else 0.0
        if win_rate < 0.88:
            continue
        variants.append(
            {
                "core_id": variant.get("candidate_id") or variant.get("policy"),
                "policy": variant.get("policy"),
                "settled": settled,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "net_cents": variant.get("weighted_net_cents"),
                "coverage_pct": variant.get("coverage_pct"),
                "reconstructed_share": variant.get("row_reconstructed_share"),
                "rows": list(variant.get("selected_rows") or []),
            }
        )
    variants.sort(key=lambda row: (-row["win_rate"], -fnum(row.get("net_cents")), -row["settled"]))
    return variants[:8]


def mix_core_with_fillers(
    core: dict[str, Any],
    broad_rows: list[dict[str, Any]],
    denominator: int,
    lane_name: str,
    rank: str,
    strict_forward: bool,
) -> dict[str, Any]:
    required = math.ceil(COVERAGE_FLOOR * denominator / 100.0)
    selected_by_key = {row_key(row): dict(row) for row in core.get("rows") or []}
    filler_pool = [row for row in broad_rows if row_key(row) not in selected_by_key]
    filler_pool.sort(key=lambda row: (-rank_score(row, rank), row.get("market") or "", row.get("side") or ""))
    added = []
    for row in filler_pool:
        if len(selected_by_key) >= required:
            break
        selected_by_key[row_key(row)] = dict(row)
        added.append(row)
    rows = list(selected_by_key.values())
    summary = summarize(
        rows,
        denominator,
        f"{lane_name}_{core.get('core_id')}_fill_{rank}",
        strict_forward=strict_forward,
    )
    summary.update(
        {
            "lane": lane_name,
            "core_id": core.get("core_id"),
            "core_win_rate": core.get("win_rate"),
            "core_settled": core.get("settled"),
            "core_net_cents": core.get("net_cents"),
            "filler_rank": rank,
            "filler_rows_added": len(added),
            "filler_net_cents": sum(row_net(row) for row in added),
            "filler_source_counts": {
                "approved_entry": sum(1 for row in added if row.get("source") == "approved_entry"),
                "reconstructed_or_rejected": sum(1 for row in added if row.get("source") != "approved_entry"),
            },
        }
    )
    return summary


def build_report() -> dict[str, Any]:
    feature_gate = load_json(FEATURE_GATE_JSON)
    source_proxy = load_json(SOURCE_PROXY_JSON)
    lane_pairs = [
        ("post_feature_freeze_entry", "diagnostic_feature_freeze_entry"),
        ("post_feature_freeze_bridge", "diagnostic_feature_freeze_bridge"),
    ]
    ranks = ["raw_edge", "p_side", "absd", "low_recross", "ask_confirm", "source_proxy_score"]
    rows = []
    for feature_lane, proxy_lane in lane_pairs:
        denominator, broad_rows = feature_gate_variant(
            feature_gate,
            feature_lane,
            f"{feature_lane}_raw03_recross70_abs075",
        )
        strict_forward = False
        for core in high_win_cores(source_proxy, proxy_lane):
            for rank in ranks:
                rows.append(mix_core_with_fillers(core, broad_rows, denominator, feature_lane, rank, strict_forward))
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum(row.get("net_cents")),
            -fnum(row.get("coverage_pct")),
            row.get("candidate") or "",
        )
    )
    interpretation = [
        "This is diagnostic mix/match only because the high-win cores are pre source-proxy-freeze rows.",
        "The test asks whether high-win p_side/source-quality cores can be filled back to 75% coverage from broad raw03 rows using observable rankings.",
    ]
    if rows:
        best = rows[0]
        interpretation.append(
            f"Best mix {best['candidate']} has {best['settled']} settled, W/L {best['wins']}/{best['losses']}, "
            f"coverage {best['coverage_pct']}%, net {best['net_cents']}c, recon {best['reconstructed_share']}, "
            f"blockers {best['blockers']}."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": (feature_gate.get("state") or {}).get("freeze_ts_utc"),
        "source_proxy_freeze_ts_utc": (source_proxy.get("proxy_state") or {}).get("freeze_ts_utc"),
        "purpose": "Diagnostic high-win core plus broad filler mix.",
        "interpretation": interpretation,
        "rows": rows,
    }


def fmt_cents(value: Any) -> str:
    return f"{fnum(value):.0f}c"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 High-Win Core Broad-Fill Mix",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Source-proxy freeze UTC: `{report.get('source_proxy_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Top Mix Rows",
            "",
            "| rank | lane | core | fill | settled | W/L | coverage | net | recon | cushion | filler added | filler net | blockers |",
            "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate((report.get("rows") or [])[:30], start=1):
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('core_id')}` | `{row.get('filler_rank')}` | "
            f"{row.get('settled')} | {row.get('wins')}/{row.get('losses')} | {fmt_pct(row.get('coverage_pct'))} | "
            f"{fmt_cents(row.get('net_cents'))} | {fmt_pct(100.0 * fnum(row.get('reconstructed_share')))} | "
            f"{row.get('full_loss_cushion')} | {row.get('filler_rows_added')} | {fmt_cents(row.get('filler_net_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
