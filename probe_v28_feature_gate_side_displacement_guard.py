"""Same-market side-displacement guard scan for the v28 feature-gate branch.

Research-only. This tests whether an observable high-ask side-priority guard
can repair cheap-side displacement without using source labels. It is a
settled-row replay over the already frozen feature-gate post-freeze rows, not a
promotion candidate.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_side_displacement_guard_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_side_displacement_guard_latest.md"

CANDIDATE = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"

LANES = ("post_feature_freeze_entry", "post_feature_freeze_bridge")
BASE_SUFFIXES = ("raw05_recross60_abs085", "raw03_recross70_abs075")
ASK65_SUFFIX = "raw05_recross60_abs085_ask65"


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


def cents(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def live_net_cents() -> float:
    live = load_json(LIVE_SUMMARY)
    return round(cents(live.get("net_pnl_total_dollars")) * 100.0, 6)


def fmt_cents(value: Any) -> str:
    return f"{cents(value):.0f}c"


def fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def fmt_num(value: Any, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def market_key(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def row_net(row: dict[str, Any]) -> float:
    return cents(row.get("net_cents"))


def selected_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    rows = variant.get("rows") if isinstance(variant.get("rows"), list) else []
    return [row for row in rows if isinstance(row, dict)]


def variant_map(lane: dict[str, Any]) -> dict[str, dict[str, Any]]:
    variants = lane.get("variants") if isinstance(lane.get("variants"), list) else []
    return {
        str(variant.get("candidate") or ""): variant
        for variant in variants
        if isinstance(variant, dict)
    }


def find_variant(vmap: dict[str, dict[str, Any]], lane_name: str, suffix: str) -> dict[str, Any]:
    exact = f"{lane_name}_{suffix}"
    if exact in vmap:
        return vmap[exact]
    return next((row for key, row in vmap.items() if key.endswith(suffix)), {})


def tag_row(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if row.get("source") != "approved_entry":
        tags.append("source_quality_error")
    if row_net(row) < 0:
        tags.append("realized_loss")
    else:
        tags.append("realized_win")
    ask = row.get("ask_prob")
    raw = row.get("raw_edge")
    abs_d = row.get("abs_d_sigma")
    if ask is not None and float(ask) < 0.10:
        tags.append("cheap_tail_ask_lt10")
    if ask is not None and float(ask) >= 0.85:
        tags.append("high_ask_gte85")
    if raw is not None and float(raw) < 0.07:
        tags.append("thin_raw_edge_lt07")
    if abs_d is not None and float(abs_d) < 0.85:
        tags.append("weak_boundary_distance")
    return tags


def summarize_rows(rows: list[dict[str, Any]], entries: int | None, denominator: int | None, live_cents: float) -> dict[str, Any]:
    wins = losses = 0
    net = 0.0
    source_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    for row in rows:
        pnl = row_net(row)
        net += pnl
        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1
        source_counts[str(row.get("source") or "")] += 1
        for tag in tag_row(row):
            tag_counts[tag] += 1

    row_count = len(rows)
    rejected = row_count - int(source_counts.get("approved_entry", 0))
    coverage = (float(entries) / float(denominator) * 100.0) if entries and denominator else None
    return {
        "entries": entries,
        "settled_replay_rows": row_count,
        "coverage_pct": coverage,
        "wins": wins,
        "losses": losses,
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "settled_reconstructed_share": (rejected / row_count if row_count else None),
        "source_counts": dict(source_counts),
        "full_loss_cushion": int(net // 100) if net > 0 else 0,
        "tag_counts": dict(tag_counts),
    }


def official_entries(variant: dict[str, Any]) -> int | None:
    summary = variant.get("candidate_summary") if isinstance(variant.get("candidate_summary"), dict) else {}
    value = summary.get("entries")
    return int(value) if value is not None else None


def replacement_scan(
    base: dict[str, Any],
    ask65: dict[str, Any],
    min_preferred_ask: float,
    max_base_ask: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_rows = selected_rows(base)
    ask_rows_by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected_rows(ask65):
        ask_rows_by_market[market_key(row)].append(row)

    replay: list[dict[str, Any]] = []
    replacements: list[dict[str, Any]] = []
    for row in base_rows:
        base_ask = row.get("ask_prob")
        alternatives = [
            alt
            for alt in ask_rows_by_market.get(market_key(row), [])
            if row_key(alt) != row_key(row)
            and alt.get("ask_prob") is not None
            and float(alt.get("ask_prob")) >= min_preferred_ask
        ]
        if base_ask is not None and float(base_ask) <= max_base_ask and alternatives:
            alt = sorted(alternatives, key=lambda item: float(item.get("ask_prob") or 0.0), reverse=True)[0]
            replay.append(alt)
            replacements.append(
                {
                    "market": row.get("market"),
                    "old_side": row.get("side"),
                    "old_source": row.get("source"),
                    "old_ask_prob": row.get("ask_prob"),
                    "old_net_cents": row_net(row),
                    "new_side": alt.get("side"),
                    "new_source": alt.get("source"),
                    "new_ask_prob": alt.get("ask_prob"),
                    "new_net_cents": row_net(alt),
                    "delta_cents": row_net(alt) - row_net(row),
                }
            )
        else:
            replay.append(row)
    return replay, replacements


def scan_lane(lane: dict[str, Any], live_cents: float) -> dict[str, Any]:
    lane_name = str(lane.get("lane") or "")
    denominator = int(lane.get("future_denominator") or 0)
    vmap = variant_map(lane)
    ask65 = find_variant(vmap, lane_name, ASK65_SUFFIX)

    policies = []
    for suffix in BASE_SUFFIXES:
        base = find_variant(vmap, lane_name, suffix)
        base_rows = selected_rows(base)
        base_entries = official_entries(base)
        policies.append(
            {
                "policy": f"{suffix}_control",
                "base_candidate": base.get("candidate"),
                "guard": "none",
                "summary": summarize_rows(base_rows, base_entries, denominator, live_cents),
                "replacements": [],
            }
        )
        for min_ask, max_ask, label in [
            (0.65, 0.65, "ask65_any_conflict_priority"),
            (0.85, 0.10, "ask85_over_cheap10_priority"),
            (0.85, 0.50, "ask85_over_sub50_priority"),
        ]:
            replay, replacements = replacement_scan(base, ask65, min_preferred_ask=min_ask, max_base_ask=max_ask)
            policies.append(
                {
                    "policy": f"{suffix}_{label}",
                    "base_candidate": base.get("candidate"),
                    "guard": {
                        "preferred_min_ask": min_ask,
                        "base_max_ask": max_ask,
                    },
                    "summary": summarize_rows(replay, base_entries, denominator, live_cents),
                    "replacement_count": len(replacements),
                    "replacement_net_delta_cents": sum(cents(item.get("delta_cents")) for item in replacements),
                    "replacements": replacements,
                }
            )

    policies.sort(
        key=lambda item: (
            -cents((item.get("summary") or {}).get("net_cents")),
            -cents((item.get("summary") or {}).get("coverage_pct")),
        )
    )
    return {
        "lane": lane_name,
        "future_denominator": denominator,
        "ask65_candidate": ask65.get("candidate"),
        "policies": policies,
    }


def build_report() -> dict[str, Any]:
    candidate = load_json(CANDIDATE)
    live_cents = live_net_cents()
    lanes_by_name = {
        str(lane.get("lane")): lane
        for lane in candidate.get("lanes", [])
        if isinstance(lane, dict) and lane.get("lane") in LANES
    }
    lanes = [scan_lane(lanes_by_name[name], live_cents) for name in LANES if name in lanes_by_name]

    interpretation = [
        "Research-only same-market side-displacement guard scan; no live bot changes or orders.",
        "The guard is observable: when a cheap selected side conflicts with a same-market opposite side that passes the ask65 core, prefer the high-ask side.",
        "The broad any-ask65 replacement is not attractive because it includes the known 67c ask false-positive loser.",
        "The narrower ask>=85 over cheap/sub50 guards improve source quality and some PnL, but they still do not solve broad coverage or live-baseline gates.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "candidate_generated_at_utc": candidate.get("generated_at_utc"),
        "feature_gate_freeze_ts_utc": (candidate.get("state") or {}).get("freeze_ts_utc"),
        "live_net_cents": live_cents,
        "sources": {
            "candidate": str(CANDIDATE),
            "live_summary": str(LIVE_SUMMARY),
        },
        "lanes": lanes,
        "interpretation": interpretation,
    }


def wl(summary: dict[str, Any]) -> str:
    return f"{int(summary.get('wins') or 0)}/{int(summary.get('losses') or 0)}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Feature-Gate Side-Displacement Guard",
        "",
        "Research-only settled-row replay. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate source UTC: `{report.get('candidate_generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Live baseline: `{fmt_cents(report.get('live_net_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])

    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| rank | policy | entries | settled replay | W/L | coverage | net | delta live | replay recon | cushion | replacements | repl delta |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for idx, policy in enumerate(lane.get("policies") or [], start=1):
            summary = policy.get("summary") or {}
            recon = summary.get("settled_reconstructed_share")
            recon_text = f"{float(recon):.3f}" if recon is not None else "n/a"
            lines.append(
                "| "
                f"{idx} | "
                f"`{policy.get('policy')}` | "
                f"{summary.get('entries') or 0} | "
                f"{summary.get('settled_replay_rows') or 0} | "
                f"{wl(summary)} | "
                f"{fmt_pct(summary.get('coverage_pct'))} | "
                f"{fmt_cents(summary.get('net_cents'))} | "
                f"{fmt_cents(summary.get('delta_vs_live_cents'))} | "
                f"{recon_text} | "
                f"{summary.get('full_loss_cushion') or 0} | "
                f"{policy.get('replacement_count') or 0} | "
                f"{fmt_cents(policy.get('replacement_net_delta_cents'))} |"
            )

        best = (lane.get("policies") or [{}])[0]
        replacements = best.get("replacements") or []
        if replacements:
            lines.extend(
                [
                    "",
                    f"### Best Policy Replacements: `{best.get('policy')}`",
                    "",
                    "| market | old side | old ask | old net | new side | new ask | new net | delta |",
                    "|---|---|---:|---:|---|---:|---:|---:|",
                ]
            )
            for item in replacements[:10]:
                lines.append(
                    "| "
                    f"`{item.get('market')}` | "
                    f"`{item.get('old_side')}` | "
                    f"{fmt_num(item.get('old_ask_prob'))} | "
                    f"{fmt_cents(item.get('old_net_cents'))} | "
                    f"`{item.get('new_side')}` | "
                    f"{fmt_num(item.get('new_ask_prob'))} | "
                    f"{fmt_cents(item.get('new_net_cents'))} | "
                    f"{fmt_cents(item.get('delta_cents'))} |"
                )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
