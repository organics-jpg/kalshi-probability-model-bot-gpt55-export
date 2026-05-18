from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_particle.replay_runner import ReplayConfig
from research_particle.rv600_variation_test import build_rv600_variation_report


DEFAULT_NATIVE_JSON = Path("logs/particle_research/reports/rv600_native_forward_opportunity_latest.json")
DEFAULT_ROOT_BASE = Path("logs/particle_research/real_shadow")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_online_expert_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_online_expert_rescue_latest.md")

MODELING_OPTIONS = [
    {
        "method": "multiplicative_weights",
        "source": "Freund and Schapire 1997, A Decision-Theoretic Generalization of On-Line Learning",
        "source_url": "https://doi.org/10.1006/jcss.1997.1504",
        "fit": "Best fit: choose among existing plan variants online from prior-root rewards without inventing new strategy families.",
        "decision": "chosen",
    },
    {
        "method": "prediction_with_expert_advice",
        "source": "Cesa-Bianchi and Lugosi 2006, Prediction, Learning, and Games",
        "source_url": "https://doi.org/10.1017/CBO9780511546921",
        "fit": "General framework for sequentially competing with a reference class of experts; used here as an audit framing.",
        "decision": "chosen_as_validation_frame",
    },
    {
        "method": "second_order_expert_bounds",
        "source": "Cesa-Bianchi, Mansour, and Stoltz 2006, Improved Second-Order Bounds for Prediction with Expert Advice",
        "source_url": "https://arxiv.org/abs/math/0602629",
        "fit": "Interesting for payoff scale adaptation, but heavier than needed for the current small root count.",
        "decision": "deferred",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _row_dict(row: Any) -> dict[str, Any]:
    return asdict(row) if not isinstance(row, dict) else row


def _selected_roots(native_json: Path, root_base: Path) -> list[Path]:
    native = _load_json(native_json)
    roots: list[Path] = []
    for name in native.get("roots") or []:
        path = root_base / str(name)
        if path.exists():
            roots.append(path)
    return roots


def _reward(row: dict[str, Any], reward_scale: float) -> float:
    # Bounded reward keeps one wild root from dominating the expert weights.
    return math.tanh(_float(row.get("selected_pnl_cents")) / max(1.0, reward_scale))


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entries = sum(_int(row.get("accepted_entries")) for row in rows)
    pnl = sum(_float(row.get("selected_pnl_cents")) for row in rows)
    matched = sum(_float(row.get("matched_v28_control_pnl_cents")) for row in rows)
    added = sum(_int(row.get("added_entry_count")) for row in rows)
    added_pnl = sum(_float(row.get("added_entry_pnl_cents")) for row in rows)
    positive_roots = sum(1 for row in rows if _float(row.get("selected_pnl_cents")) > 0.0)
    last_window = sum(_float(row.get("selected_pnl_cents")) for row in rows[-5:])
    distinct_markets = sum(_int(row.get("distinct_markets")) for row in rows)
    max_share = max((_float(row.get("max_single_market_pnl_share")) for row in rows), default=0.0)
    positive_market_weighted = 0.0
    market_denominator = 0
    for row in rows:
        markets = _int(row.get("distinct_markets"))
        market_denominator += markets
        positive_market_weighted += markets * _float(row.get("positive_market_rate"))
    return {
        "accepted_entries": entries,
        "distinct_markets_root_sum": distinct_markets,
        "selected_pnl_cents": pnl,
        "matched_v28_control_pnl_cents": matched,
        "matched_v28_delta_cents": pnl - matched,
        "avg_pnl_per_entry_cents": pnl / entries if entries else 0.0,
        "avg_pnl_per_market_cents": pnl / distinct_markets if distinct_markets else 0.0,
        "positive_root_rate": positive_roots / len(rows) if rows else 0.0,
        "positive_market_rate_weighted": positive_market_weighted / market_denominator if market_denominator else 0.0,
        "max_root_single_market_pnl_share": max_share,
        "last_5_root_pnl_cents": last_window,
        "added_entry_count": added,
        "added_entry_pnl_cents": added_pnl,
        "avg_added_entry_pnl_cents": added_pnl / added if added else 0.0,
    }


def _passes_train_gate(position_rows: list[dict[str, Any]], one_per_side_rows: list[dict[str, Any]], gate_count: int) -> bool:
    score = _aggregate(position_rows)
    one_score = _aggregate(one_per_side_rows)
    if gate_count > 3:
        return False
    if score["accepted_entries"] < 25:
        return False
    if score["selected_pnl_cents"] <= 0.0:
        return False
    if score["avg_pnl_per_entry_cents"] < 10.0:
        return False
    if score["avg_pnl_per_market_cents"] <= 0.0:
        return False
    if score["positive_root_rate"] < 0.60:
        return False
    if score["positive_market_rate_weighted"] < 0.60:
        return False
    if score["max_root_single_market_pnl_share"] > 0.25:
        return False
    if score["last_5_root_pnl_cents"] <= 0.0:
        return False
    if score["matched_v28_delta_cents"] <= 0.0:
        return False
    if one_score["selected_pnl_cents"] <= 0.0:
        return False
    if score["added_entry_count"] and score["added_entry_pnl_cents"] <= 0.0:
        return False
    return True


def _gate_rejection(position_rows: list[dict[str, Any]], one_per_side_rows: list[dict[str, Any]], gate_count: int) -> str:
    score = _aggregate(position_rows)
    one_score = _aggregate(one_per_side_rows)
    reasons: list[str] = []
    if gate_count > 3:
        reasons.append("gate_count_above_3")
    if score["accepted_entries"] < 25:
        reasons.append("fewer_than_25_entries")
    if score["selected_pnl_cents"] <= 0.0:
        reasons.append("nonpositive_pnl")
    if score["avg_pnl_per_entry_cents"] < 10.0:
        reasons.append("avg_entry_below_10c")
    if score["avg_pnl_per_market_cents"] <= 0.0:
        reasons.append("avg_market_nonpositive")
    if score["positive_root_rate"] < 0.60:
        reasons.append("positive_root_rate_below_60pct")
    if score["positive_market_rate_weighted"] < 0.60:
        reasons.append("positive_market_rate_below_60pct")
    if score["max_root_single_market_pnl_share"] > 0.25:
        reasons.append("single_market_share_above_25pct")
    if score["last_5_root_pnl_cents"] <= 0.0:
        reasons.append("recent_roots_nonpositive")
    if score["matched_v28_delta_cents"] <= 0.0:
        reasons.append("does_not_beat_matched_v28")
    if one_score["selected_pnl_cents"] <= 0.0:
        reasons.append("deduped_one_per_side_nonpositive")
    if score["added_entry_count"] and score["added_entry_pnl_cents"] <= 0.0:
        reasons.append("added_entries_nonpositive")
    return ";".join(reasons)


def _aggregate_rejection(gate_pass: bool, locked_selection_count: int, total_entries: int, total_pnl: float, total_matched: float, positive_splits: int, split_count: int) -> str:
    if gate_pass:
        return ""
    reasons: list[str] = []
    if locked_selection_count <= 0:
        reasons.append("no_train_gate_selection")
    if total_entries < 25:
        reasons.append("fewer_than_25_test_entries")
    if total_pnl <= 0.0:
        reasons.append("nonpositive_test_pnl")
    if total_entries and total_pnl / total_entries < 10.0:
        reasons.append("avg_test_entry_below_10c")
    if total_pnl - total_matched <= 0.0:
        reasons.append("does_not_beat_matched_v28")
    if split_count and positive_splits / split_count < 0.60:
        reasons.append("positive_test_splits_below_60pct")
    return ";".join(reasons)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root_paths = _selected_roots(args.native_json, args.root_base)
    variation = build_rv600_variation_report(
        tuple(root_paths),
        phase="grid",
        output_json=args.grid_cache_json,
        output_md=args.grid_cache_md,
        config=ReplayConfig(
            min_fill_prob=0.0,
            no_fill_penalty_cents=0.0,
            counterfactual_fill_policy="threshold",
            counterfactual_fill_threshold=0.5,
        ),
    )
    run_rows = [_row_dict(row) for row in variation.run_rows]
    rows_by_variant_mode_root: dict[tuple[str, str, str], dict[str, Any]] = {}
    gate_by_variant: dict[str, int] = {}
    variants: set[str] = set()
    for row in run_rows:
        variant = str(row.get("variant") or "")
        if "v28_primary" in variant:
            continue
        root = str(row.get("root_name") or "")
        mode = str(row.get("accounting_mode") or "")
        rows_by_variant_mode_root[(variant, mode, root)] = row
        if mode == "position_capped":
            variants.add(variant)
            gate_by_variant[variant] = _int(row.get("gate_count"))
    roots = list(variation.roots)
    split_rows: list[dict[str, Any]] = []
    for test_index in range(args.min_train_roots, len(roots)):
        train_roots = roots[:test_index]
        test_root = roots[test_index]
        scored: list[dict[str, Any]] = []
        for variant in sorted(variants):
            position_train = [rows_by_variant_mode_root[(variant, "position_capped", root)] for root in train_roots if (variant, "position_capped", root) in rows_by_variant_mode_root]
            one_train = [rows_by_variant_mode_root[(variant, "one_per_side_per_market", root)] for root in train_roots if (variant, "one_per_side_per_market", root) in rows_by_variant_mode_root]
            if len(position_train) != len(train_roots):
                continue
            reward = sum(_reward(row, args.reward_scale_cents) for row in position_train)
            weight = math.exp(args.eta * reward)
            train_score = _aggregate(position_train)
            train_gate_pass = _passes_train_gate(position_train, one_train, gate_by_variant.get(variant, 99))
            scored.append(
                {
                    "variant": variant,
                    "weight": weight,
                    "reward": reward,
                    "train_gate_pass": train_gate_pass,
                    "train_score": train_score,
                    "train_rejection_reason": _gate_rejection(position_train, one_train, gate_by_variant.get(variant, 99)),
                }
            )
        passing = [row for row in scored if row["train_gate_pass"]]
        if passing:
            selected = max(passing, key=lambda row: (row["weight"], row["train_score"]["selected_pnl_cents"]))
            selection_basis = "train_gate_pass_weighted"
        else:
            selected = max(scored, key=lambda row: (row["weight"], row["train_score"]["selected_pnl_cents"]))
            selection_basis = "diagnostic_best_weight"
        test_position = rows_by_variant_mode_root.get((selected["variant"], "position_capped", test_root), {})
        split_rows.append(
            {
                "split_index": len(split_rows),
                "train_root_count": len(train_roots),
                "test_root": test_root,
                "selected_variant": selected["variant"],
                "selection_basis": selection_basis,
                "selected_weight": selected["weight"],
                "selected_reward": selected["reward"],
                "train_gate_pass": selected["train_gate_pass"],
                "train_selected_pnl_cents": selected["train_score"]["selected_pnl_cents"],
                "train_accepted_entries": selected["train_score"]["accepted_entries"],
                "train_avg_pnl_per_entry_cents": selected["train_score"]["avg_pnl_per_entry_cents"],
                "train_rejection_reason": selected["train_rejection_reason"],
                "test_selected_pnl_cents": _float(test_position.get("selected_pnl_cents")),
                "test_matched_v28_control_pnl_cents": _float(test_position.get("matched_v28_control_pnl_cents")),
                "test_matched_v28_delta_cents": _float(test_position.get("matched_v28_delta_cents")),
                "test_accepted_entries": _int(test_position.get("accepted_entries")),
                "test_distinct_markets": _int(test_position.get("distinct_markets")),
                "test_avg_pnl_per_entry_cents": _float(test_position.get("avg_pnl_per_entry_cents")),
                "test_rejection_reason": str(test_position.get("rejection_reason") or ""),
            }
        )
    total_entries = sum(row["test_accepted_entries"] for row in split_rows)
    total_pnl = sum(row["test_selected_pnl_cents"] for row in split_rows)
    total_matched = sum(row["test_matched_v28_control_pnl_cents"] for row in split_rows)
    locked_selection_count = sum(1 for row in split_rows if row["selection_basis"] == "train_gate_pass_weighted")
    positive_splits = sum(1 for row in split_rows if row["test_selected_pnl_cents"] > 0.0)
    gate_pass = (
        locked_selection_count > 0
        and total_entries >= 25
        and total_pnl > 0.0
        and total_pnl - total_matched > 0.0
        and (total_pnl / total_entries if total_entries else 0.0) >= 10.0
        and (positive_splits / len(split_rows) if split_rows else 0.0) >= 0.60
    )
    return {
        "schema_version": "rv600-online-expert-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "method_choice": "Multiplicative-weights expert selection over existing RV600 plan variants using prior-root rewards only.",
        "modeling_options": MODELING_OPTIONS,
        "roots": roots,
        "variant_count": variation.variant_count,
        "expert_count": len(variants),
        "min_train_roots": args.min_train_roots,
        "eta": args.eta,
        "reward_scale_cents": args.reward_scale_cents,
        "split_rows": split_rows,
        "aggregate": {
            "split_count": len(split_rows),
            "train_gate_selection_count": locked_selection_count,
            "diagnostic_selection_count": len(split_rows) - locked_selection_count,
            "test_total_entries": total_entries,
            "test_selected_pnl_cents": total_pnl,
            "test_matched_v28_control_pnl_cents": total_matched,
            "test_matched_v28_delta_cents": total_pnl - total_matched,
            "test_avg_pnl_per_entry_cents": total_pnl / total_entries if total_entries else 0.0,
            "positive_test_split_rate": positive_splits / len(split_rows) if split_rows else 0.0,
            "preliminary_gate_pass": gate_pass,
            "rejection_reason": _aggregate_rejection(gate_pass, locked_selection_count, total_entries, total_pnl, total_matched, positive_splits, len(split_rows)),
        },
        "inputs": {
            "native_json": str(args.native_json),
            "root_base": str(args.root_base),
        },
    }


def _markdown(report: dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "# RV600 Online Expert Rescue Probe",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- method_choice: {report['method_choice']}",
        f"- usable_roots: {len(report['roots'])}",
        f"- variant_count: {report['variant_count']}",
        f"- expert_count: {report['expert_count']}",
        f"- eta: {report['eta']}",
        f"- reward_scale_cents: {report['reward_scale_cents']}",
        f"- split_count: {aggregate['split_count']}",
        f"- train_gate_selection_count: {aggregate['train_gate_selection_count']}",
        f"- diagnostic_selection_count: {aggregate['diagnostic_selection_count']}",
        f"- test_total_entries: {aggregate['test_total_entries']}",
        f"- test_selected_pnl_cents: {aggregate['test_selected_pnl_cents']:.1f}",
        f"- test_matched_v28_delta_cents: {aggregate['test_matched_v28_delta_cents']:.1f}",
        f"- preliminary_gate_pass: {aggregate['preliminary_gate_pass']}",
        f"- rejection_reason: {aggregate['rejection_reason']}",
        "",
        "## Modeling Choice",
        "",
        "| method | decision | source | fit |",
        "|---|---|---|---|",
    ]
    for option in report["modeling_options"]:
        lines.append(
            f"| `{option['method']}` | {option['decision']} | [{option['source']}]({option['source_url']}) | {option['fit']} |"
        )
    lines.extend(
        [
            "",
            "## Split Rows",
            "",
            "| split | selected variant | basis | test root | entries | pnl_c | v28_delta_c |",
            "|---:|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report["split_rows"]:
        lines.append(
            "| {split_index} | `{selected_variant}` | {selection_basis} | `{test_root}` | {test_accepted_entries} | {test_selected_pnl_cents:.1f} | {test_matched_v28_delta_cents:.1f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Method Notes",
            "",
            "This is a research-only expert-advice rescue: every expert is an existing RV600-derived plan variant, scored with position-capped accounting. Pure `v28_primary` variants are excluded as controls, not RV600-derived candidates.",
            "Selections are made from prior roots only. If the selected expert did not pass prior-root anti-overfitting gates, its next-root row is diagnostic and not promotable.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-only RV600 online expert weighting rescue probe.")
    parser.add_argument("--native-json", type=Path, default=DEFAULT_NATIVE_JSON)
    parser.add_argument("--root-base", type=Path, default=DEFAULT_ROOT_BASE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--grid-cache-json", type=Path, default=Path("logs/particle_research/reports/rv600_online_expert_grid_cache.json"))
    parser.add_argument("--grid-cache-md", type=Path, default=Path("logs/particle_research/reports/rv600_online_expert_grid_cache.md"))
    parser.add_argument("--min-train-roots", type=int, default=5)
    parser.add_argument("--eta", type=float, default=1.0)
    parser.add_argument("--reward-scale-cents", type=float, default=100.0)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    aggregate = report["aggregate"]
    print(f"preliminary_gate_pass={aggregate['preliminary_gate_pass']}")
    print(f"split_count={aggregate['split_count']}")
    print(f"train_gate_selection_count={aggregate['train_gate_selection_count']}")
    print(f"test_selected_pnl_cents={aggregate['test_selected_pnl_cents']:.1f}")
    print(f"rejection_reason={aggregate['rejection_reason']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
