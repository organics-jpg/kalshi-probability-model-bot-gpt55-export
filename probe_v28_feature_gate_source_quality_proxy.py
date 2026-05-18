"""Observable source-quality proxy scan for the v28 feature-gate branch.

Research-only; no live bot changes or orders.

The near-gate feature branch is blocked by a small excess of
rejected/reconstructed rows. This probe tests whether observable execution and
market-quality fields can reduce source fragility without using source labels
for selection. Source labels are audit-only after each selection rule.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import as_float, load_or_create_state, market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, raw_edge, rule_name
from probe_v28_feature_gate_coverage_size_shrink import (
    ANCHOR_RULE,
    REPAIR_RULE,
    repair_weight,
    row_key,
    summarize_policy,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_quality_proxy_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_quality_proxy_latest.md"
STATE_JSON = OUT_DIR / "v28_feature_gate_source_quality_proxy_state.json"

POLICY = "repair_low_absd_quarter_else_half"
MAX_RECON_SHARE = 0.35
WATCH_VARIANTS = {
    "stc_gte_240": "Require at least four minutes to close; diagnostic rows suggest later observations reduce source fragility while preserving full-loss cushion.",
    "p_side_gte_75": "Require stronger model-side probability; source quality improves but coverage and cushion need forward proof.",
    "raw_edge_gte_4": "Require at least four raw edge points; improves source share but under-covers diagnostically.",
}


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


def load_or_create_proxy_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_source_quality_proxy",
        "parent": "v28_feature_gate_coverage_size_shrink",
        "watch_variants": WATCH_VARIANTS,
        "strict_forward_note": "Rows before this timestamp are diagnostic only; watch rows must prove themselves post-freeze.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def p_side(row: dict[str, Any]) -> float:
    return fnum(row.get("p_side"))


def ask(row: dict[str, Any]) -> float:
    return fnum(row.get("ask_prob"))


def book_age(row: dict[str, Any]) -> float:
    return fnum(row.get("book_age_ms"), 999999.0)


def btc_age(row: dict[str, Any]) -> float:
    return fnum(row.get("btc_age_ms"), 999999.0)


def depth(row: dict[str, Any]) -> float:
    return fnum(row.get("eligible_depth"))


def seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("seconds_to_close"))


def side_obs_index(row: dict[str, Any]) -> float:
    return fnum(row.get("market_side_observation_index"), 999999.0)


def market_obs_index(row: dict[str, Any]) -> float:
    return fnum(row.get("market_observation_index"), 999999.0)


def raw_score(row: dict[str, Any]) -> float:
    return fnum(raw_edge(row), -999.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def selected_by_market(
    rows: list[dict[str, Any]],
    ranker: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=ranker) for items in grouped.values()]


def rank_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (raw_score(row), abs_d(row), -recross(row), str(row.get("ts_wall") or ""))


def rank_depth_fresh_raw(row: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        raw_score(row) + 0.015 * math.log1p(depth(row)) - 0.00002 * book_age(row) - 0.00002 * btc_age(row),
        raw_score(row),
        abs_d(row),
        -recross(row),
        str(row.get("ts_wall") or ""),
    )


def rank_early_observation_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (-side_obs_index(row), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


def rank_depth_first(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (math.log1p(depth(row)), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


def rank_fresh_first(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (-(book_age(row) + btc_age(row)), raw_score(row), abs_d(row), str(row.get("ts_wall") or ""))


RANKERS: dict[str, Callable[[dict[str, Any]], tuple[Any, ...]]] = {
    "raw_edge": rank_raw,
    "depth_fresh_raw": rank_depth_fresh_raw,
    "early_observation_raw": rank_early_observation_raw,
    "depth_first": rank_depth_first,
    "fresh_first": rank_fresh_first,
}


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "book_age_ms": row.get("book_age_ms"),
        "btc_age_ms": row.get("btc_age_ms"),
        "eligible_depth": row.get("eligible_depth"),
        "seconds_to_close": row.get("seconds_to_close"),
        "market_observation_index": row.get("market_observation_index"),
        "market_side_observation_index": row.get("market_side_observation_index"),
        "side_won": row.get("side_won"),
    }


def feature_contrast(selected: list[dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "raw_edge",
        "p_side",
        "ask_prob",
        "abs_d_sigma",
        "recross_hazard_score",
        "book_age_ms",
        "btc_age_ms",
        "eligible_depth",
        "seconds_to_close",
        "market_side_observation_index",
    ]
    out: dict[str, Any] = {}
    by_source = {
        "approved": [row for row in selected if source(row) == "approved_entry"],
        "reconstructed": [row for row in selected if source(row) != "approved_entry"],
    }
    for field in fields:
        out[field] = {}
        for label, rows in by_source.items():
            values = []
            for row in rows:
                value = raw_edge(row) if field == "raw_edge" else as_float(row.get(field))
                if value is not None:
                    values.append(float(value))
            values.sort()
            if not values:
                out[field][label] = None
                continue
            out[field][label] = {
                "n": len(values),
                "avg": sum(values) / len(values),
                "min": values[0],
                "p50": values[len(values) // 2],
                "max": values[-1],
            }
    return out


def observable_filters() -> list[tuple[str, Callable[[dict[str, Any]], bool]]]:
    filters: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [("none", lambda row: True)]
    for threshold in [250, 500, 1000, 1500, 2000]:
        filters.append((f"book_age_lte_{threshold}", lambda row, threshold=threshold: book_age(row) <= threshold))
    for threshold in [250, 500, 1000, 1500, 2000]:
        filters.append((f"btc_age_lte_{threshold}", lambda row, threshold=threshold: btc_age(row) <= threshold))
    for threshold in [250, 500, 750, 1000, 1500, 2000]:
        filters.append((f"depth_gte_{threshold}", lambda row, threshold=threshold: depth(row) >= threshold))
    for threshold in [0, 1, 2, 3, 4]:
        filters.append((f"side_obs_lte_{threshold}", lambda row, threshold=threshold: side_obs_index(row) <= threshold))
    for threshold in [60, 120, 180, 240]:
        filters.append((f"stc_gte_{threshold}", lambda row, threshold=threshold: seconds_to_close(row) >= threshold))
    for threshold in [240, 360, 480, 600, 720]:
        filters.append((f"stc_lte_{threshold}", lambda row, threshold=threshold: seconds_to_close(row) <= threshold))
    for threshold in [0.65, 0.70, 0.75, 0.80, 0.85]:
        filters.append((f"p_side_gte_{int(threshold * 100)}", lambda row, threshold=threshold: p_side(row) >= threshold))
    for threshold in [0.45, 0.50, 0.55, 0.60, 0.65]:
        filters.append((f"ask_gte_{int(threshold * 100)}", lambda row, threshold=threshold: ask(row) >= threshold))
    for threshold in [0.04, 0.05, 0.06, 0.07]:
        filters.append((f"raw_edge_gte_{int(threshold * 100)}", lambda row, threshold=threshold: raw_score(row) >= threshold))
    combo_specs = [
        ("fresh_depth500", lambda row: book_age(row) <= 1000 and btc_age(row) <= 1000 and depth(row) >= 500),
        ("fresh_depth1000", lambda row: book_age(row) <= 1000 and btc_age(row) <= 1000 and depth(row) >= 1000),
        ("early_fresh", lambda row: side_obs_index(row) <= 1 and book_age(row) <= 1000 and btc_age(row) <= 1000),
        ("confident_depth500", lambda row: p_side(row) >= 0.70 and depth(row) >= 500),
        ("not_cheap_depth500", lambda row: ask(row) >= 0.50 and depth(row) >= 500),
        ("raw04_fresh", lambda row: raw_score(row) >= 0.04 and book_age(row) <= 1000 and btc_age(row) <= 1000),
        ("raw04_depth500", lambda row: raw_score(row) >= 0.04 and depth(row) >= 500),
    ]
    filters.extend(combo_specs)
    return filters


def watch_filter_names() -> set[str]:
    return {
        "filter_stc_gte_240_rank_raw",
        "filter_p_side_gte_75_rank_raw",
        "filter_raw_edge_gte_4_rank_raw",
    }


def evaluate_variant(
    lane: str,
    label: str,
    selected: list[dict[str, Any]],
    denominator: int,
    anchor_keys: set[tuple[str, str]],
) -> dict[str, Any]:
    summary = summarize_policy(lane, POLICY, selected, denominator, anchor_keys)
    counts = source_counts(selected)
    summary.update({
        "candidate_id": label,
        "source_counts": counts,
        "selected_rows": [row_view(row) for row in selected],
        "feature_contrast": feature_contrast(selected),
    })
    return summary


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any], strict_forward: bool) -> dict[str, Any]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_pool = [row for row in rows if passes_rule(row, ANCHOR_RULE)]
    anchor_rows = selected_by_market(anchor_pool, rank_raw)
    anchor_keys = {row_key(row) for row in anchor_rows}
    base_pool = [row for row in rows if passes_rule(row, REPAIR_RULE)]
    variants: list[dict[str, Any]] = []

    for rank_name, ranker in RANKERS.items():
        variants.append(evaluate_variant(
            label,
            f"rank_{rank_name}",
            selected_by_market(base_pool, ranker),
            denominator,
            anchor_keys,
        ))

    for filter_name, predicate in observable_filters():
        filtered = [row for row in base_pool if predicate(row)]
        if not filtered:
            continue
        variants.append(evaluate_variant(
            label,
            f"filter_{filter_name}_rank_raw",
            selected_by_market(filtered, rank_raw),
            denominator,
            anchor_keys,
        ))
        if filter_name != "none":
            variants.append(evaluate_variant(
                label,
                f"filter_{filter_name}_rank_depth_fresh_raw",
                selected_by_market(filtered, rank_depth_fresh_raw),
                denominator,
                anchor_keys,
            ))

    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            row.get("row_reconstructed_share") is None or row.get("row_reconstructed_share") > MAX_RECON_SHARE,
            -float(row.get("weighted_net_cents") or -999999.0),
            -float(row.get("coverage_pct") or 0.0),
        )
    )
    source_clean_positive = [
        row for row in variants
        if not (row.get("blockers") or [])
    ]
    watch_rows = [row for row in variants if row.get("candidate_id") in watch_filter_names()]
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "strict_forward": strict_forward,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "repair_rule": rule_name(REPAIR_RULE),
        "anchor_entries": len(anchor_rows),
        "base_pool_rows": len(base_pool),
        "top_variants": variants[:30],
        "gate_clear_variants": source_clean_positive[:20],
        "watch_variants": watch_rows,
        "variant_count": len(variants),
    }


def build_report() -> dict[str, Any]:
    feature_state = load_or_create_state()
    proxy_state = load_or_create_proxy_state()
    feature_freeze_ts = str(feature_state["freeze_ts_utc"])
    proxy_freeze_ts = str(proxy_state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": feature_freeze_ts,
        "proxy_watch_freeze_ts_utc": proxy_freeze_ts,
        "proxy_state": proxy_state,
        "purpose": "Scan observable execution/source-quality proxies for the near-gate feature branch.",
        "lanes": [
            evaluate_lane("diagnostic_feature_freeze_entry", feature_freeze_ts, entry_surfaces, False),
            evaluate_lane("diagnostic_feature_freeze_bridge", feature_freeze_ts, bridge_surfaces, False),
            evaluate_lane("post_source_proxy_birth_entry", proxy_freeze_ts, entry_surfaces, True),
            evaluate_lane("post_source_proxy_birth_bridge", proxy_freeze_ts, bridge_surfaces, True),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Source labels are audit-only; all variants select using observable row fields.",
    ]
    for lane in report.get("lanes") or []:
        clear = lane.get("gate_clear_variants") or []
        best = (lane.get("top_variants") or [{}])[0]
        if clear:
            first = clear[0]
            notes.append(
                f"{lane.get('lane')}: {len(clear)} observable source-quality variant(s) clear current gates; "
                f"best {first.get('candidate_id')} has {first.get('entries')}/{lane.get('future_denominator')} entries, "
                f"W/L {first.get('wins')}/{first.get('losses')}, weighted net {first.get('weighted_net_cents')}c, "
                f"row recon {first.get('row_reconstructed_share')}."
            )
        else:
            notes.append(
                f"{lane.get('lane')}: no observable proxy clears all gates. Best {best.get('candidate_id')} has "
                f"{best.get('entries')}/{lane.get('future_denominator')} entries, W/L {best.get('wins')}/{best.get('losses')}, "
                f"weighted net {best.get('weighted_net_cents')}c, row recon {best.get('row_reconstructed_share')}, "
                f"blockers {best.get('blockers')}."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source-Quality Proxy Scan",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Source-proxy watch freeze UTC: `{report.get('proxy_watch_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Freeze UTC: `{lane.get('freeze_ts_utc')}`",
            f"- Strict forward: `{lane.get('strict_forward')}`",
            f"- Anchor rule: `{lane.get('anchor_rule')}`",
            f"- Repair rule: `{lane.get('repair_rule')}`",
            f"- Anchor/base-pool rows: `{lane.get('anchor_entries')}/{lane.get('base_pool_rows')}`",
            "",
            "| candidate | entries | settled | W/L | coverage | weighted net | row recon | exposure recon | cushion | source | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for row in lane.get("top_variants") or []:
            source_summary = row.get("source_counts") or {}
            lines.append(
                f"| {row.get('candidate_id')} | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))}% | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('exposure_reconstructed_share'))} | {row.get('full_loss_cushion')} | "
                f"{source_summary} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
