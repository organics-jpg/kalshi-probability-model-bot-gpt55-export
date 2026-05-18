"""Ask-floor tradeoff autopsy for the v28 boundary-clock feature-gate branch.

Research-only. This compares the current strict post-feature-freeze clean
ask-floor lane against the wider raw05 and raw03 observable lanes. It does not
change live bot logic or candidate rules.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_ask_floor_tradeoff_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_ask_floor_tradeoff_autopsy_latest.md"

CANDIDATE = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"

LANES = ("post_feature_freeze_entry", "post_feature_freeze_bridge")
ASK65_SUFFIX = "raw05_recross60_abs085_ask65"
RAW05_SUFFIX = "raw05_recross60_abs085"
RAW03_SUFFIX = "raw03_recross70_abs075"


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


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def market_key(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def row_net(row: dict[str, Any]) -> float:
    return cents(row.get("net_cents"))


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    source = row.get("source")
    raw = row.get("raw_edge")
    recross = row.get("recross_hazard_score")
    abs_d = row.get("abs_d_sigma")
    ask = row.get("ask_prob")
    net = row_net(row)

    if source != "approved_entry":
        tags.append("source_quality_error")
    if net < 0:
        tags.append("realized_loss")
    elif net > 0:
        tags.append("realized_win")
    else:
        tags.append("flat")
    if ask is not None and float(ask) < 0.65:
        tags.append("below_ask65")
    if ask is not None and float(ask) < 0.50:
        tags.append("cheap_touch_lt50")
    if ask is not None and float(ask) >= 0.85:
        tags.append("expensive_touch_gte85")
    if abs_d is not None and float(abs_d) < 0.85:
        tags.append("weak_boundary_distance")
    if recross is not None and float(recross) > 0.30:
        tags.append("moderate_recross_gt30")
    if raw is not None and float(raw) < 0.07:
        tags.append("thin_raw_edge_lt07")
    if raw is not None and float(raw) > 0.20 and net < 0:
        tags.append("large_raw_edge_false_positive")
    return tags


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tag_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    source_net: defaultdict[str, float] = defaultdict(float)
    wins = losses = flats = 0
    net = 0.0
    raw_values: list[float] = []
    recross_values: list[float] = []
    abs_values: list[float] = []
    ask_values: list[float] = []

    for row in rows:
        pnl = row_net(row)
        net += pnl
        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1
        else:
            flats += 1
        source = str(row.get("source") or "")
        source_counts[source] += 1
        source_net[source] += pnl
        for tag in row_tags(row):
            tag_counts[tag] += 1
        for target, values in [
            ("raw_edge", raw_values),
            ("recross_hazard_score", recross_values),
            ("abs_d_sigma", abs_values),
            ("ask_prob", ask_values),
        ]:
            value = row.get(target)
            if value is not None:
                values.append(float(value))

    count = len(rows)
    rejected = count - int(source_counts.get("approved_entry", 0))
    return {
        "rows": count,
        "net_cents": net,
        "wins": wins,
        "losses": losses,
        "flats": flats,
        "reconstructed_share": (rejected / count if count else None),
        "source_counts": dict(source_counts),
        "source_net_cents": dict(source_net),
        "avg_raw_edge": (sum(raw_values) / len(raw_values) if raw_values else None),
        "avg_recross_hazard_score": (sum(recross_values) / len(recross_values) if recross_values else None),
        "avg_abs_d_sigma": (sum(abs_values) / len(abs_values) if abs_values else None),
        "avg_ask_prob": (sum(ask_values) / len(ask_values) if ask_values else None),
        "tag_counts": dict(tag_counts),
    }


def selected_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    rows = variant.get("rows") if isinstance(variant.get("rows"), list) else []
    return [row for row in rows if isinstance(row, dict)]


def summarize_variant(variant: dict[str, Any], live_cents: float) -> dict[str, Any]:
    summary = variant.get("candidate_summary") if isinstance(variant.get("candidate_summary"), dict) else {}
    net = cents(summary.get("net_cents"))
    return {
        "candidate": variant.get("candidate"),
        "entries": summary.get("entries"),
        "settled": summary.get("settled"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "reconstructed_share": variant.get("reconstructed_share"),
        "source_counts": variant.get("source_counts"),
        "full_loss_cushion": variant.get("full_loss_cushion_estimate"),
        "blockers": variant.get("blockers") or [],
    }


def diff_rows(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    """Rows selected by left but not by right, keyed by market and side."""
    right_keys = {row_key(row) for row in selected_rows(right)}
    return [row for row in selected_rows(left) if row_key(row) not in right_keys]


def diff_bucket(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    rows = diff_rows(left, right)
    right_rows = selected_rows(right)
    right_markets = {market_key(row) for row in right_rows}
    right_by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in right_rows:
        right_by_market[market_key(row)].append(row)

    summary = summarize_rows(rows)
    displaced = [row for row in rows if market_key(row) in right_markets]
    summary["same_market_displacement_rows"] = len(displaced)
    summary["new_market_rows"] = len(rows) - len(displaced)
    examples = []
    for row in displaced[:8]:
        alternatives = right_by_market.get(market_key(row), [])
        examples.append(
            {
                "market": row.get("market"),
                "left_side": row.get("side"),
                "left_source": row.get("source"),
                "left_net_cents": row_net(row),
                "left_ask_prob": row.get("ask_prob"),
                "right_alternatives": [
                    {
                        "side": alt.get("side"),
                        "source": alt.get("source"),
                        "net_cents": row_net(alt),
                        "ask_prob": alt.get("ask_prob"),
                    }
                    for alt in alternatives
                ],
            }
        )
    summary["same_market_displacement_examples"] = examples
    return summary


def lane_report(lane: dict[str, Any], live_cents: float) -> dict[str, Any]:
    lane_name = str(lane.get("lane") or "")
    vmap = variant_map(lane)
    ask65 = find_variant(vmap, lane_name, ASK65_SUFFIX)
    raw05 = find_variant(vmap, lane_name, RAW05_SUFFIX)
    raw03 = find_variant(vmap, lane_name, RAW03_SUFFIX)

    comparisons = {
        "raw05_added_vs_ask65": diff_bucket(raw05, ask65),
        "raw03_added_vs_raw05": diff_bucket(raw03, raw05),
        "raw03_added_vs_ask65": diff_bucket(raw03, ask65),
        "ask65_rows_not_in_raw05": diff_bucket(ask65, raw05),
    }

    return {
        "lane": lane_name,
        "freeze_ts": lane.get("freeze_ts"),
        "future_denominator": lane.get("future_denominator"),
        "variants": {
            "ask65_clean_core": summarize_variant(ask65, live_cents),
            "raw05_source_cleaner_coverage": summarize_variant(raw05, live_cents),
            "raw03_broad_coverage": summarize_variant(raw03, live_cents),
        },
        "comparisons": comparisons,
    }


def build_report() -> dict[str, Any]:
    candidate = load_json(CANDIDATE)
    live_cents = live_net_cents()
    lane_payloads = {
        str(lane.get("lane")): lane
        for lane in candidate.get("lanes", [])
        if isinstance(lane, dict) and lane.get("lane") in LANES
    }
    lanes = [lane_report(lane_payloads[name], live_cents) for name in LANES if name in lane_payloads]

    interpretation = [
        "Research-only ask-floor tradeoff autopsy; no live bot changes or orders.",
        f"Live baseline for deltas is {fmt_cents(live_cents)} from the refreshed live-only score.",
        "The ask65 lane remains the cleanest source-quality core but is far below broad-entry coverage and sample/cushion gates.",
        "The raw05 lane adds coverage while staying near the 35% source gate, but it still misses 75% coverage and does not beat live.",
        "The raw03 lane is the broadest current post-freeze feature-gate lane, but the extra coverage comes with too much rejected/reconstructed share and weak cushion.",
    ]

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "candidate": str(CANDIDATE),
            "live_summary": str(LIVE_SUMMARY),
        },
        "candidate_generated_at_utc": candidate.get("generated_at_utc"),
        "feature_gate_freeze_ts_utc": (candidate.get("state") or {}).get("freeze_ts_utc"),
        "live_net_cents": live_cents,
        "lanes": lanes,
        "interpretation": interpretation,
    }


def wl(summary: dict[str, Any]) -> str:
    return f"{int(summary.get('wins') or 0)}/{int(summary.get('losses') or 0)}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Feature-Gate Ask-Floor Tradeoff Autopsy",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
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
                "| variant | entries | settled | W/L | coverage | net | delta live | recon | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for label, variant in (lane.get("variants") or {}).items():
            blockers = ", ".join(str(item) for item in variant.get("blockers") or []) or "none"
            recon = variant.get("reconstructed_share")
            recon_text = f"{float(recon):.3f}" if recon is not None else "n/a"
            lines.append(
                "| "
                f"`{label}` | "
                f"{variant.get('entries') or 0} | "
                f"{variant.get('settled') or 0} | "
                f"{wl(variant)} | "
                f"{fmt_pct(variant.get('coverage_pct'))} | "
                f"{fmt_cents(variant.get('net_cents'))} | "
                f"{fmt_cents(variant.get('delta_vs_live_cents'))} | "
                f"{recon_text} | "
                f"{variant.get('full_loss_cushion') or 0} | "
                f"{blockers} |"
            )

        lines.extend(
            [
                "",
                "### Added/Omitted Row Buckets",
                "",
                "| bucket | rows | displaced | new markets | W/L/F | net | recon | avg ask | avg abs d | avg recross | top tags |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for label, bucket in (lane.get("comparisons") or {}).items():
            tags = sorted(
                (bucket.get("tag_counts") or {}).items(),
                key=lambda item: (-int(item[1]), item[0]),
            )[:6]
            tag_text = ", ".join(f"{tag}:{count}" for tag, count in tags) or "none"
            recon = bucket.get("reconstructed_share")
            recon_text = f"{float(recon):.3f}" if recon is not None else "n/a"
            lines.append(
                "| "
                f"`{label}` | "
                f"{bucket.get('rows') or 0} | "
                f"{bucket.get('same_market_displacement_rows') or 0} | "
                f"{bucket.get('new_market_rows') or 0} | "
                f"{bucket.get('wins') or 0}/{bucket.get('losses') or 0}/{bucket.get('flats') or 0} | "
                f"{fmt_cents(bucket.get('net_cents'))} | "
                f"{recon_text} | "
                f"{fmt_num(bucket.get('avg_ask_prob'))} | "
                f"{fmt_num(bucket.get('avg_abs_d_sigma'))} | "
                f"{fmt_num(bucket.get('avg_recross_hazard_score'))} | "
                f"{tag_text} |"
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
