from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_NATIVE_JSON = Path("logs/particle_research/reports/rv600_native_forward_opportunity_latest.json")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_meta_label_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_meta_label_rescue_latest.md")
DEFAULT_ROOT_BASE = Path("logs/particle_research/real_shadow")

MODELING_OPTIONS = [
    {
        "method": "meta_label_filter",
        "source": "Joubert 2022, Meta-Labeling: Theory and Framework",
        "source_url": "https://ssrn.com/abstract=4032018",
        "fit": "Best fit: preserves RV600 as the primary signal and learns only whether to accept or suppress a candidate.",
        "decision": "chosen",
    },
    {
        "method": "conformal_time_series_abstention",
        "source": "Xu and Xie 2020/2023, Conformal prediction for time series",
        "source_url": "https://arxiv.org/abs/2010.09107",
        "fit": "Useful for uncertainty bands, but current labels are sparse settled trade outcomes rather than a long residual stream.",
        "decision": "deferred",
    },
    {
        "method": "sequential_conformal_inference",
        "source": "Xu and Xie 2022, Sequential Predictive Conformal Inference for Time Series",
        "source_url": "https://arxiv.org/abs/2212.03463",
        "fit": "Handles non-exchangeable time series, but needs a larger sequential residual history than the current RV600 sample.",
        "decision": "deferred",
    },
    {
        "method": "post_hoc_probability_calibration",
        "source": "Guo et al. 2017, On Calibration of Modern Neural Networks",
        "source_url": "https://arxiv.org/abs/1706.04599",
        "fit": "Can improve probability reliability, but the immediate blocker is trade acceptance/profitability after fees and fills.",
        "decision": "deferred",
    },
    {
        "method": "online_expert_weighting",
        "source": "Freund and Schapire 1997, A Decision-Theoretic Generalization of On-Line Learning",
        "source_url": "https://doi.org/10.1006/jcss.1997.1504",
        "fit": "Plausible for adapting among candidate families, but every existing family is already rejected and the sample is too small.",
        "decision": "deferred",
    },
]


@dataclass(frozen=True)
class CandidateDecision:
    root_name: str
    market_ticker: str
    decision_ts_utc: str
    side: str
    ask_cents: float
    pnl_cents: float
    matched_v28_pnl_cents: float
    best_ev_cents: float
    seconds_to_close: float
    selected_p: float
    current_p: float
    market_p: float
    ask_spread_cents: float
    depth_count: float
    abs_spot_strike: float


@dataclass(frozen=True)
class FilterSpec:
    name: str
    description: str
    fn: Callable[[CandidateDecision], bool]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _label_path(root: Path) -> Path:
    return root / "pipeline_work" / "label_contexts_full_refresh.ndjson"


def _candidate_path(root: Path) -> Path:
    return root / "candidate_snapshots" / "candidate_snapshots.ndjson"


def _load_label(root: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    path = _label_path(root)
    if not path.exists():
        return labels
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            result = str(payload.get("binary_result") or payload.get("result") or "").lower()
            market = str(payload.get("market_ticker") or payload.get("market") or "")
            if market and result in {"yes", "no"}:
                labels[market] = result
    return labels


def _expected_ev(p_win: float, ask: float, fee: float, fill_prob: float = 1.0) -> float:
    return fill_prob * (p_win * (100.0 - ask - fee) - (1.0 - p_win) * ask)


def _side_from_probability(p_yes: float, yes_ask: float, no_ask: float, fee: float, fill_prob: float) -> tuple[str, float]:
    ev_yes = _expected_ev(p_yes, yes_ask, fee, fill_prob)
    ev_no = _expected_ev(1.0 - p_yes, no_ask, fee, fill_prob)
    return ("yes", ev_yes) if ev_yes >= ev_no else ("no", ev_no)


def _realized_pnl(result: str, side: str, ask: float, fee: float) -> float:
    if result == side:
        return 100.0 - ask - fee
    return -ask


def _load_root_decisions(root_base: Path, root_name: str) -> list[CandidateDecision]:
    root = root_base / root_name
    labels = _load_label(root)
    path = _candidate_path(root)
    if not labels or not path.exists():
        return []
    decisions: list[CandidateDecision] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            snapshot = payload.get("snapshot") or {}
            extra = payload.get("extra") or {}
            market = str(snapshot.get("market_ticker") or "")
            result = labels.get(market)
            if result not in {"yes", "no"}:
                continue
            selected_p = _float(extra.get("particle_calibrated_p_yes"), _float(extra.get("particle_p_yes"), 0.5))
            current_p = _float(extra.get("current_calibrated_p_yes"), _float(snapshot.get("current_calibrated_p_yes"), 0.5))
            market_p = _float(extra.get("market_p_yes"), 0.5)
            yes_ask = _float(snapshot.get("yes_ask_cents"))
            no_ask = _float(snapshot.get("no_ask_cents"))
            yes_bid = _float(snapshot.get("yes_bid_cents"), 100.0 - no_ask)
            no_bid = _float(snapshot.get("no_bid_cents"), 100.0 - yes_ask)
            fee = _float(snapshot.get("fee_cents"), 2.0)
            fill_prob = _float(snapshot.get("fill_prob"), 1.0)
            side, best_ev = _side_from_probability(selected_p, yes_ask, no_ask, fee, fill_prob)
            current_side, _ = _side_from_probability(current_p, yes_ask, no_ask, fee, fill_prob)
            ask = yes_ask if side == "yes" else no_ask
            matched_ask = yes_ask if current_side == "yes" else no_ask
            decisions.append(
                CandidateDecision(
                    root_name=root_name,
                    market_ticker=market,
                    decision_ts_utc=str(snapshot.get("decision_ts_utc") or ""),
                    side=side,
                    ask_cents=ask,
                    pnl_cents=_realized_pnl(result, side, ask, fee),
                    matched_v28_pnl_cents=_realized_pnl(result, current_side, matched_ask, fee),
                    best_ev_cents=best_ev,
                    seconds_to_close=_float(extra.get("seconds_to_close"), _float(snapshot.get("seconds_to_close"))),
                    selected_p=selected_p,
                    current_p=current_p,
                    market_p=market_p,
                    ask_spread_cents=max(0.0, (yes_ask - yes_bid) if side == "yes" else (no_ask - no_bid)),
                    depth_count=_float(extra.get("depth_count"), _float(snapshot.get("depth_count"))),
                    abs_spot_strike=abs(_float(snapshot.get("spot")) - _float(snapshot.get("strike"))),
                )
            )
    return sorted(decisions, key=lambda item: (item.decision_ts_utc, item.market_ticker, item.side))


def _dedupe_one_per_side(decisions: list[CandidateDecision]) -> list[CandidateDecision]:
    seen: set[tuple[str, str]] = set()
    accepted: list[CandidateDecision] = []
    for decision in decisions:
        key = (decision.market_ticker, decision.side)
        if key in seen:
            continue
        seen.add(key)
        accepted.append(decision)
    return accepted


def _filters() -> list[FilterSpec]:
    specs: list[FilterSpec] = [FilterSpec("base_all", "primary rv600 candidate only", lambda d: True)]
    for threshold in (5.0, 10.0, 15.0, 20.0, 25.0):
        specs.append(FilterSpec(f"ev_ge_{int(threshold)}", f"best EV >= {threshold}c", lambda d, t=threshold: d.best_ev_cents >= t))
    for low, high in ((70.0, 180.0), (70.0, 300.0), (120.0, 420.0), (180.0, 600.0), (70.0, 600.0)):
        specs.append(FilterSpec(f"window_{int(low)}_{int(high)}", f"{low}s <= seconds_to_close <= {high}s", lambda d, lo=low, hi=high: lo <= d.seconds_to_close <= hi))
    for threshold in (0.03, 0.05, 0.08, 0.10, 0.15):
        specs.append(FilterSpec(f"rv_market_gap_ge_{int(threshold*100)}pct", f"abs(rv600-market probability gap) >= {threshold}", lambda d, t=threshold: abs(d.selected_p - d.market_p) >= t))
        specs.append(FilterSpec(f"rv_v28_gap_le_{int(threshold*100)}pct", f"abs(rv600-v28 probability gap) <= {threshold}", lambda d, t=threshold: abs(d.selected_p - d.current_p) <= t))
    for cap in (30.0, 50.0, 70.0, 85.0):
        specs.append(FilterSpec(f"ask_le_{int(cap)}", f"selected ask <= {cap}c", lambda d, c=cap: d.ask_cents <= c))
    for threshold in (3.0, 10.0, 50.0, 100.0):
        specs.append(FilterSpec(f"depth_ge_{int(threshold)}", f"visible depth >= {threshold}", lambda d, t=threshold: d.depth_count >= t))
    for threshold in (10.0, 25.0, 50.0, 100.0):
        specs.append(FilterSpec(f"spot_strike_abs_le_{int(threshold)}", f"abs spot-strike <= {threshold}", lambda d, t=threshold: d.abs_spot_strike <= t))
    specs.append(FilterSpec("side_yes_only", "YES only", lambda d: d.side == "yes"))
    specs.append(FilterSpec("side_no_only", "NO only", lambda d: d.side == "no"))
    return specs


def _score(decisions_by_root: dict[str, list[CandidateDecision]], roots: list[str], spec: FilterSpec) -> dict[str, Any]:
    accepted: list[CandidateDecision] = []
    root_rows: list[dict[str, Any]] = []
    for root in roots:
        root_decisions = [d for d in decisions_by_root.get(root, []) if spec.fn(d)]
        root_accepted = _dedupe_one_per_side(root_decisions)
        accepted.extend(root_accepted)
        root_pnl = sum(d.pnl_cents for d in root_accepted)
        root_rows.append(
            {
                "root": root,
                "accepted_entries": len(root_accepted),
                "distinct_markets": len({d.market_ticker for d in root_accepted}),
                "selected_pnl_cents": root_pnl,
                "matched_v28_control_pnl_cents": sum(d.matched_v28_pnl_cents for d in root_accepted),
            }
        )
    markets = {d.market_ticker for d in accepted}
    pnl = sum(d.pnl_cents for d in accepted)
    matched = sum(d.matched_v28_pnl_cents for d in accepted)
    market_pnls: dict[str, float] = defaultdict(float)
    for decision in accepted:
        market_pnls[decision.market_ticker] += decision.pnl_cents
    max_market_share = 0.0
    if pnl > 0.0 and market_pnls:
        max_market_share = max(max(0.0, value) for value in market_pnls.values()) / pnl
    positive_roots = sum(1 for row in root_rows if row["selected_pnl_cents"] > 0.0)
    positive_markets = sum(1 for value in market_pnls.values() if value > 0.0)
    last_window = sum(d.pnl_cents for d in accepted[-20:])
    return {
        "filter": spec.name,
        "description": spec.description,
        "accepted_entries": len(accepted),
        "distinct_markets": len(markets),
        "selected_pnl_cents": pnl,
        "matched_v28_control_pnl_cents": matched,
        "matched_v28_delta_cents": pnl - matched,
        "avg_pnl_per_entry_cents": pnl / len(accepted) if accepted else 0.0,
        "positive_root_rate": positive_roots / len(root_rows) if root_rows else 0.0,
        "positive_market_rate": positive_markets / len(market_pnls) if market_pnls else 0.0,
        "max_single_market_pnl_share": max_market_share,
        "last_window_pnl_cents": last_window,
        "root_rows": root_rows,
    }


def _passes_train_gate(score: dict[str, Any]) -> bool:
    if score["accepted_entries"] < 25:
        return False
    if score["selected_pnl_cents"] <= 0.0:
        return False
    if score["avg_pnl_per_entry_cents"] < 10.0:
        return False
    if score["positive_root_rate"] < 0.60:
        return False
    if score["positive_market_rate"] < 0.60:
        return False
    if score["max_single_market_pnl_share"] > 0.25:
        return False
    if score["last_window_pnl_cents"] <= 0.0:
        return False
    if score["matched_v28_delta_cents"] <= 0.0:
        return False
    return True


def _select_filter(decisions_by_root: dict[str, list[CandidateDecision]], roots: list[str], specs: list[FilterSpec]) -> tuple[FilterSpec | None, dict[str, Any] | None, bool]:
    scored = [(spec, _score(decisions_by_root, roots, spec)) for spec in specs]
    passing = [(spec, score) for spec, score in scored if _passes_train_gate(score)]
    if passing:
        return max(passing, key=lambda item: item[1]["selected_pnl_cents"]) + (True,)
    diagnostic = max(scored, key=lambda item: item[1]["selected_pnl_cents"], default=(None, None))
    return diagnostic[0], diagnostic[1], False


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    native = _load_json(args.native_json)
    roots = list(native.get("roots") or [])
    decisions_by_root = {root: _load_root_decisions(args.root_base, root) for root in roots}
    usable_roots = [root for root in roots if decisions_by_root.get(root)]
    specs = _filters()
    split_rows: list[dict[str, Any]] = []
    for test_index in range(args.min_train_roots, len(usable_roots)):
        train_roots = usable_roots[:test_index]
        test_root = usable_roots[test_index]
        selected, train_score, gate_pass = _select_filter(decisions_by_root, train_roots, specs)
        if selected is None or train_score is None:
            continue
        test_score = _score(decisions_by_root, [test_root], selected)
        split_rows.append(
            {
                "split_index": len(split_rows),
                "train_root_count": len(train_roots),
                "test_root": test_root,
                "selected_filter": selected.name,
                "selection_basis": "train_gate_pass" if gate_pass else "diagnostic_best_train_pnl",
                "train_gate_pass": gate_pass,
                "train_selected_pnl_cents": train_score["selected_pnl_cents"],
                "train_accepted_entries": train_score["accepted_entries"],
                "train_avg_pnl_per_entry_cents": train_score["avg_pnl_per_entry_cents"],
                "test_selected_pnl_cents": test_score["selected_pnl_cents"],
                "test_matched_v28_control_pnl_cents": test_score["matched_v28_control_pnl_cents"],
                "test_matched_v28_delta_cents": test_score["matched_v28_delta_cents"],
                "test_accepted_entries": test_score["accepted_entries"],
                "test_distinct_markets": test_score["distinct_markets"],
            }
        )
    total_entries = sum(row["test_accepted_entries"] for row in split_rows)
    total_pnl = sum(row["test_selected_pnl_cents"] for row in split_rows)
    total_matched = sum(row["test_matched_v28_control_pnl_cents"] for row in split_rows)
    locked_selection_count = sum(1 for row in split_rows if row["selection_basis"] == "train_gate_pass")
    positive_splits = sum(1 for row in split_rows if row["test_selected_pnl_cents"] > 0.0)
    gate_pass = (
        locked_selection_count > 0
        and total_entries >= 25
        and total_pnl > 0.0
        and total_pnl - total_matched > 0.0
        and (total_pnl / total_entries if total_entries else 0.0) >= 10.0
        and (positive_splits / len(split_rows) if split_rows else 0.0) >= 0.60
    )
    report = {
        "schema_version": "rv600-meta-label-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "method_choice": "Meta-label style one-feature filter over the RV600 primary signal with anchored prequential selection.",
        "modeling_options": MODELING_OPTIONS,
        "roots": usable_roots,
        "filter_count": len(specs),
        "min_train_roots": args.min_train_roots,
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
    return report


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


def _markdown(report: dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "# RV600 Meta-Label Rescue Probe",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- method_choice: {report['method_choice']}",
        f"- usable_roots: {len(report['roots'])}",
        f"- filter_count: {report['filter_count']}",
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
        "| split | selected filter | basis | test root | entries | pnl_c | v28_delta_c |",
        "|---:|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report["split_rows"]:
        lines.append(
            "| {split_index} | `{selected_filter}` | {selection_basis} | `{test_root}` | {test_accepted_entries} | {test_selected_pnl_cents:.1f} | {test_matched_v28_delta_cents:.1f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Method Notes",
            "",
            "This is a research-only meta-labeling rescue attempt: RV600 remains the primary signal, while a one-feature filter is selected from prior roots only and tested on the next root.",
            "Diagnostic selections are reported for visibility but are not promotable unless a prior-root training window already passed the same anti-overfitting gates.",
            "",
            "References: Lopez de Prado style meta-labeling, sequential/prequential validation, and the existing RV600 anti-overfitting gates.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-only RV600 meta-label rescue probe.")
    parser.add_argument("--native-json", type=Path, default=DEFAULT_NATIVE_JSON)
    parser.add_argument("--root-base", type=Path, default=DEFAULT_ROOT_BASE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-train-roots", type=int, default=5)
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
