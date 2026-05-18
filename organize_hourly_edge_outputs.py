from __future__ import annotations

import csv
import html
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDGE = ROOT / "logs" / "edge_research"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


LATEST_REPORTS = [
    "codex_stop_touch_research_latest.json",
    "codex_terminal_path_research_latest.json",
    "codex_terminal_salvage_all_trades_latest.json",
    "codex_terminal_confirmation_research_latest.json",
    "codex_calibrated_utility_research_latest.json",
    "codex_calibrated_ev_research_latest.json",
    "codex_entry_timing_research_latest.json",
    "codex_entry_path_geometry_research_latest.json",
    "codex_entry_clock_decay_research_latest.json",
    "codex_entry_logit_snr_research_latest.json",
    "codex_entry_microstructure_research_latest.json",
    "codex_entry_timing_persistence_latest.json",
]


def load_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def n(value, default=None):
    try:
        if value in (None, ""):
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except Exception:
        return default


def money(value) -> str:
    value = n(value)
    return "" if value is None else f"${value:,.2f}"


def pct(value) -> str:
    value = n(value)
    return "" if value is None else f"{value * 100:.1f}%"


def md_link(path: Path, label: str | None = None) -> str:
    return f"[{label or path.name}](<{path.resolve()}>)"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summary_pnl(summary: dict) -> float | None:
    for key in ("sim_pnl", "holdout_sim_pnl", "full_sim_pnl", "best_sim_pnl"):
        value = n(summary.get(key))
        if value is not None:
            return value
    return None


def hurdle_edge(summary: dict) -> float | None:
    # Entry admission strategies should clear skip-all/no-trade. Exit strategies
    # should clear no-stop hold where available, then actual bot behavior.
    for key in (
        "delta_vs_no_trade_all",
        "holdout_delta_vs_no_trade_all",
        "delta_vs_no_stop",
        "holdout_delta_vs_no_stop",
        "delta_vs_hold",
        "delta_vs_actual",
        "holdout_delta_vs_actual",
    ):
        value = n(summary.get(key))
        if value is not None:
            return value
    return None


def action_count(summary: dict) -> float | None:
    for key in ("entries", "holdout_entries", "exits", "full_entries", "n"):
        value = n(summary.get(key))
        if value is not None and value > 0:
            return value
    return None


def contract_count(summary: dict) -> float | None:
    for key in ("total_contracts", "full_total_contracts"):
        value = n(summary.get(key))
        if value is not None and value > 0:
            return value
    return None


def win_rate(summary: dict) -> float | None:
    for key in ("entry_win_rate", "holdout_entry_win_rate", "full_entry_win_rate"):
        value = n(summary.get(key))
        if value is not None:
            return value
    return None


def scope_from_summary(summary: dict) -> str:
    if "entries" in summary or "holdout_entries" in summary or "entry_win_rate" in summary:
        return "entry_admission"
    if "exits" in summary or "false_exit_rate" in summary:
        return "exit_rule"
    return "research_strategy"


def edge_per_action(summary: dict, pnl: float | None = None) -> float | None:
    for key in (
        "holdout_net_edge_per_trade",
        "full_net_edge_per_trade",
        "net_edge_per_trade",
    ):
        value = n(summary.get(key))
        if value is not None:
            return value
    pnl = summary_pnl(summary) if pnl is None else pnl
    actions = action_count(summary)
    if pnl is None or actions in (None, 0):
        return None
    return pnl / actions


def edge_per_contract(summary: dict, pnl: float | None = None) -> float | None:
    for key in ("holdout_net_edge_per_contract", "full_net_edge_per_contract"):
        value = n(summary.get(key))
        if value is not None:
            return value
    pnl = summary_pnl(summary) if pnl is None else pnl
    contracts = contract_count(summary)
    if pnl is None or contracts in (None, 0):
        return None
    return pnl / contracts


def summarize_status(projected_pnl, projected_edge, basis: str, full_pnl=None) -> str:
    projected_pnl = n(projected_pnl)
    projected_edge = n(projected_edge)
    full_pnl = n(full_pnl)
    validation = basis in {
        "train_selected_holdout",
        "robust_positive_split",
        "persistence_holdout",
        "fixed_rule_holdout",
    }
    if validation and projected_pnl is not None and projected_edge is not None:
        if basis == "robust_positive_split":
            if projected_pnl > 10 and projected_edge > 10:
                return "candidate_needs_locked_forward_test"
            if projected_pnl > 0 and projected_edge > 0:
                return "watchlist_positive"
            return "reject_or_do_not_promote"
        if projected_pnl > 10 and projected_edge > 10:
            return "candidate"
        if projected_pnl > 0 and projected_edge > 0:
            return "watchlist_positive"
        return "reject_or_do_not_promote"
    if full_pnl is not None and full_pnl > 0:
        return "full_sample_only_watchlist"
    return "weak_or_failed"


def make_row(
    *,
    source_file: Path,
    generated_at: str,
    family: str,
    strategy_id: str,
    variant: str,
    basis: str,
    summary: dict,
    params=None,
    theorem: str = "",
    equation: str = "",
    full_summary: dict | None = None,
    train_summary: dict | None = None,
) -> dict:
    full_summary = full_summary or {}
    train_summary = train_summary or {}
    projected_pnl = summary_pnl(summary)
    projected_edge = hurdle_edge(summary)
    full_pnl = summary_pnl(full_summary) if full_summary else None
    full_edge = hurdle_edge(full_summary) if full_summary else None
    train_pnl = summary_pnl(train_summary) if train_summary else None
    row = {
        "family": family,
        "strategy_id": strategy_id,
        "variant": variant,
        "evidence_basis": basis,
        "scope": scope_from_summary(summary),
        "projected_pnl": projected_pnl,
        "projected_edge_vs_hurdle": projected_edge,
        "edge_per_action": edge_per_action(summary, projected_pnl),
        "edge_per_contract": edge_per_contract(summary, projected_pnl),
        "actions": action_count(summary),
        "win_rate": win_rate(summary),
        "full_pnl": full_pnl,
        "full_edge_vs_hurdle": full_edge,
        "train_pnl": train_pnl,
        "delta_vs_actual": n(summary.get("delta_vs_actual") or summary.get("holdout_delta_vs_actual")),
        "delta_vs_no_stop": n(summary.get("delta_vs_no_stop") or summary.get("holdout_delta_vs_no_stop")),
        "delta_vs_no_trade_all": n(summary.get("delta_vs_no_trade_all") or summary.get("holdout_delta_vs_no_trade_all")),
        "false_exit_rate": n(summary.get("false_exit_rate")),
        "false_exits": n(summary.get("false_exit_settlement_winners") or summary.get("false_exits")),
        "missed_true_losers": n(summary.get("missed_true_losers")),
        "worst_trade": n(summary.get("worst_trade")),
        "status": "",
        "params": json.dumps(params or {}, sort_keys=True),
        "theorem": theorem,
        "equation": equation,
        "generated_at": generated_at,
        "source_file": str(source_file.resolve()),
    }
    row["status"] = summarize_status(
        row["projected_pnl"], row["projected_edge_vs_hurdle"], basis, row["full_pnl"]
    )
    return row


def extract_hourly_rows() -> list[dict]:
    rows = []
    seen = set()
    for path in sorted(EDGE.glob("hourly_edge_research_*.json")):
        if "latest" in path.name:
            continue
        data = load_json(path)
        for item in data.get("strategy_results", []) or []:
            summary = item.get("summary", {}) or {}
            strategy_id = item.get("strategy_id") or summary.get("label") or ""
            key = (strategy_id, path.name)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                make_row(
                    source_file=path,
                    generated_at=data.get("generated_at", ""),
                    family=item.get("family", ""),
                    strategy_id=strategy_id,
                    variant="legacy_hourly_full_sample",
                    basis="full_sample_only",
                    summary=summary,
                    params=item.get("params", {}),
                    theorem=item.get("theorem", ""),
                    equation=item.get("equation", ""),
                    full_summary=summary,
                )
            )
    return rows


def extract_best_by_family_rows(path: Path, data: dict) -> list[dict]:
    rows = []
    for family, item in (data.get("best_by_family") or {}).items():
        summary = item.get("summary", {}) or {}
        strategy_id = item.get("strategy_id") or summary.get("label") or family
        rows.append(
            make_row(
                source_file=path,
                generated_at=data.get("generated_at", ""),
                family=item.get("family", family),
                strategy_id=strategy_id,
                variant="full_sample_best",
                basis="full_sample_best",
                summary=summary,
                params=item.get("params", {}),
                theorem=item.get("theorem", ""),
                equation=item.get("equation", ""),
                full_summary=summary,
            )
        )
    return rows


def extract_walk_forward_rows(path: Path, data: dict) -> list[dict]:
    rows = []
    wf = data.get("walk_forward")
    if not isinstance(wf, dict):
        return rows
    for family, item in (wf.get("families") or {}).items():
        holdout = item.get("holdout_summary") or {}
        if not holdout:
            continue
        rows.append(
            make_row(
                source_file=path,
                generated_at=data.get("generated_at", ""),
                family=family,
                strategy_id=item.get("selected_strategy_id") or holdout.get("label") or family,
                variant="train_selected",
                basis="train_selected_holdout",
                summary=holdout,
                params=item.get("selected_params", {}),
                full_summary=item.get("full_summary", {}),
                train_summary=item.get("train_summary", {}),
            )
        )
    return rows


def extract_robust_scan_rows(path: Path, data: dict) -> list[dict]:
    rows = []
    for family, items in (data.get("robust_positive_scan") or {}).items():
        for rank, item in enumerate(items or [], 1):
            summary = {
                "sim_pnl": item.get("holdout_sim_pnl"),
                "delta_vs_no_trade_all": item.get("holdout_sim_pnl"),
                "entries": item.get("holdout_entries"),
                "entry_win_rate": item.get("holdout_entry_win_rate"),
            }
            full_summary = {
                "sim_pnl": (
                    n(item.get("train_sim_pnl"), 0.0) + n(item.get("holdout_sim_pnl"), 0.0)
                ),
                "delta_vs_no_trade_all": (
                    n(item.get("train_sim_pnl"), 0.0) + n(item.get("holdout_sim_pnl"), 0.0)
                ),
                "entries": n(item.get("train_entries"), 0.0) + n(item.get("holdout_entries"), 0.0),
            }
            rows.append(
                make_row(
                    source_file=path,
                    generated_at=data.get("generated_at", ""),
                    family=family,
                    strategy_id=item.get("strategy_id") or f"{family}_robust_{rank}",
                    variant=f"robust_positive_scan_{rank}",
                    basis="robust_positive_split",
                    summary=summary,
                    params=item.get("params", {}),
                    full_summary=full_summary,
                    train_summary={
                        "sim_pnl": item.get("train_sim_pnl"),
                        "entries": item.get("train_entries"),
                        "entry_win_rate": item.get("train_entry_win_rate"),
                    },
                )
            )
    return rows


def extract_terminal_fixed_rows(path: Path, data: dict) -> list[dict]:
    rows = []
    terminal = data.get("terminal_fixed")
    if isinstance(terminal, dict) and terminal.get("summary"):
        summary = terminal.get("summary") or {}
        rows.append(
            make_row(
                source_file=path,
                generated_at=data.get("generated_at", ""),
                family="terminal_window_salvage_fixed_all_trades",
                strategy_id=terminal.get("label") or summary.get("label") or "terminal_window_salvage_fixed",
                variant="fixed_full_sample",
                basis="full_sample_best",
                summary=summary,
                params=terminal.get("params", {}),
                full_summary=summary,
            )
        )
    fixed_wf = data.get("walk_forward_fixed")
    if isinstance(fixed_wf, dict) and fixed_wf.get("holdout"):
        rows.append(
            make_row(
                source_file=path,
                generated_at=data.get("generated_at", ""),
                family="terminal_window_salvage_fixed_all_trades",
                strategy_id="terminal_window_salvage_fixed",
                variant="fixed_train_selected",
                basis="fixed_rule_holdout",
                summary=fixed_wf.get("holdout") or {},
                params=terminal.get("params", {}) if isinstance(terminal, dict) else {},
                train_summary=fixed_wf.get("train", {}),
            )
        )
    return rows


def extract_persistence_rows(path: Path, data: dict) -> list[dict]:
    rows = []
    for item in data.get("summary_rows", []) or []:
        summary = {
            "sim_pnl": item.get("holdout_sim_pnl"),
            "delta_vs_no_trade_all": item.get("holdout_sim_pnl"),
            "entries": item.get("holdout_entries"),
            "entry_win_rate": item.get("holdout_entry_win_rate"),
            "holdout_net_edge_per_trade": item.get("holdout_net_edge_per_trade"),
            "holdout_net_edge_per_contract": item.get("holdout_net_edge_per_contract"),
            "delta_vs_actual": item.get("holdout_delta_vs_actual"),
            "delta_vs_no_stop": item.get("holdout_delta_vs_no_stop"),
        }
        full_summary = {
            "sim_pnl": item.get("full_sim_pnl"),
            "delta_vs_no_trade_all": item.get("full_sim_pnl"),
            "entries": item.get("full_entries"),
            "entry_win_rate": item.get("full_entry_win_rate"),
            "full_net_edge_per_trade": item.get("full_net_edge_per_trade"),
            "full_net_edge_per_contract": item.get("full_net_edge_per_contract"),
        }
        rows.append(
            make_row(
                source_file=path,
                generated_at=data.get("generated_at", ""),
                family=item.get("family", ""),
                strategy_id=item.get("strategy_id", ""),
                variant=f"persistence_{item.get('variant', '')}",
                basis="persistence_holdout",
                summary=summary,
                params=json.loads(item.get("params") or "{}") if isinstance(item.get("params"), str) else item.get("params", {}),
                full_summary=full_summary,
                train_summary={
                    "sim_pnl": item.get("train_sim_pnl"),
                    "entries": item.get("train_entries"),
                    "holdout_net_edge_per_trade": item.get("train_net_edge_per_trade"),
                },
            )
        )
        rows[-1]["active_day_positive_rate"] = item.get("positive_active_day_rate")
        rows[-1]["oos_block_positive_rate"] = item.get("positive_oos_block_rate")
        rows[-1]["max_entered_trade_drawdown"] = item.get("max_entered_trade_drawdown")
    return rows


def extract_all_rows() -> list[dict]:
    rows = extract_hourly_rows()
    for name in LATEST_REPORTS:
        path = EDGE / name
        if not path.exists():
            continue
        data = load_json(path)
        if name == "codex_entry_timing_persistence_latest.json":
            rows.extend(extract_persistence_rows(path, data))
            continue
        rows.extend(extract_best_by_family_rows(path, data))
        rows.extend(extract_walk_forward_rows(path, data))
        rows.extend(extract_robust_scan_rows(path, data))
        rows.extend(extract_terminal_fixed_rows(path, data))

    deduped = {}
    basis_rank = {
        "persistence_holdout": 5,
        "train_selected_holdout": 4,
        "fixed_rule_holdout": 4,
        "robust_positive_split": 3,
        "full_sample_best": 2,
        "full_sample_only": 1,
    }
    for row in rows:
        key = (
            row.get("family"),
            row.get("strategy_id"),
            row.get("variant"),
            row.get("evidence_basis"),
            row.get("source_file"),
        )
        old = deduped.get(key)
        if not old:
            deduped[key] = row
            continue
        if basis_rank.get(row["evidence_basis"], 0) >= basis_rank.get(old["evidence_basis"], 0):
            deduped[key] = row
    return list(deduped.values())


def choose_family_rank_rows(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["family"]].append(row)

    validation_bases = {
        "persistence_holdout",
        "train_selected_holdout",
        "fixed_rule_holdout",
        "robust_positive_split",
    }
    ranked = []
    for family, items in grouped.items():
        validation = [r for r in items if r["evidence_basis"] in validation_bases]
        pool = validation or items
        best = max(
            pool,
            key=lambda r: (
                n(r.get("projected_pnl"), -1e18),
                n(r.get("projected_edge_vs_hurdle"), -1e18),
                n(r.get("edge_per_action"), -1e18),
            ),
        )
        best_full = max(items, key=lambda r: n(r.get("full_pnl") or r.get("projected_pnl"), -1e18))
        projected_pnl = n(best.get("projected_pnl"))
        projected_edge = n(best.get("projected_edge_vs_hurdle"))
        ranked.append(
            {
                "family": family,
                "strategy_id": best.get("strategy_id"),
                "variant": best.get("variant"),
                "evidence_basis": best.get("evidence_basis"),
                "scope": best.get("scope"),
                "projected_pnl": projected_pnl,
                "projected_edge_vs_hurdle": projected_edge,
                "edge_per_action": best.get("edge_per_action"),
                "edge_per_contract": best.get("edge_per_contract"),
                "actions": best.get("actions"),
                "win_rate": best.get("win_rate"),
                "status": best.get("status"),
                "full_sample_best_pnl": best_full.get("full_pnl") or best_full.get("projected_pnl"),
                "full_sample_best_edge": best_full.get("full_edge_vs_hurdle") or best_full.get("projected_edge_vs_hurdle"),
                "tests_or_rows": len(items),
                "source_file": best.get("source_file"),
                "params": best.get("params"),
            }
        )
    ranked.sort(
        key=lambda r: (
            n(r.get("projected_pnl"), -1e18),
            n(r.get("projected_edge_vs_hurdle"), -1e18),
            n(r.get("edge_per_action"), -1e18),
        ),
        reverse=True,
    )
    for i, row in enumerate(ranked, 1):
        row["rank"] = i
    return ranked


def inventory_rows() -> list[dict]:
    rows = []
    categories = {
        ".json": "json_results",
        ".md": "markdown_reports",
        ".csv": "csv_tables",
        ".svg": "charts",
        ".gz": "compressed_case_data",
        ".jsonl": "idea_ledger",
    }
    for path in sorted(EDGE.glob("*")):
        if not path.is_file():
            continue
        category = categories.get(path.suffix.lower(), "other")
        family = path.name
        if path.name.startswith("codex_hourly_edge"):
            family = "organized_output_artifact"
        elif path.name.startswith("hourly_edge_research"):
            family = "hourly_exit_hypotheses"
        elif path.name.startswith("codex_stop_touch"):
            family = "corrected_stop_touch"
        elif path.name.startswith("codex_terminal_path"):
            family = "terminal_path"
        elif path.name.startswith("codex_terminal_salvage"):
            family = "terminal_salvage_all_trades"
        elif path.name.startswith("codex_terminal_confirmation"):
            family = "terminal_confirmation"
        elif path.name.startswith("codex_calibrated_utility"):
            family = "calibrated_utility"
        elif path.name.startswith("codex_calibrated_ev"):
            family = "calibrated_ev"
        elif path.name.startswith("codex_entry_timing_persistence"):
            family = "entry_timing_persistence"
        elif path.name.startswith("codex_entry_timing"):
            family = "entry_timing"
        elif path.name.startswith("codex_entry_path_geometry"):
            family = "entry_path_geometry"
        elif path.name.startswith("codex_entry_clock_decay"):
            family = "entry_clock_decay"
        elif path.name.startswith("codex_entry_logit_snr"):
            family = "entry_logit_snr"
        elif path.name.startswith("codex_entry_microstructure"):
            family = "entry_microstructure"
        elif path.name.startswith("morning_edge"):
            family = "morning_summary_artifact"
        rows.append(
            {
                "group": family,
                "category": category,
                "file": str(path.resolve()),
                "bytes": path.stat().st_size,
                "last_write_time": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }
        )
    return rows


def write_svg(path: Path, rows: list[dict], limit: int = 18) -> None:
    top = [r for r in rows if n(r.get("projected_pnl")) is not None][:limit]
    width = 1100
    bar_h = 26
    pad_l = 330
    pad_r = 120
    pad_t = 44
    height = pad_t + len(top) * (bar_h + 8) + 50
    values = [n(r["projected_pnl"], 0.0) for r in top]
    min_v = min([0.0] + values)
    max_v = max([0.0] + values)
    scale = (width - pad_l - pad_r) / (max_v - min_v or 1)
    zero_x = pad_l + (0 - min_v) * scale
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        '<text x="24" y="28" font-family="Segoe UI, Arial" font-size="18" font-weight="700" fill="#202020">Ranked projected PnL by strategy family</text>',
        f'<line x1="{zero_x:.1f}" y1="{pad_t-8}" x2="{zero_x:.1f}" y2="{height-24}" stroke="#777" stroke-width="1"/>',
    ]
    for i, row in enumerate(top):
        y = pad_t + i * (bar_h + 8)
        v = n(row["projected_pnl"], 0.0)
        x = min(zero_x, zero_x + v * scale)
        w = abs(v * scale)
        color = "#287c71" if v >= 0 else "#b94d4d"
        label = f"{row['rank']}. {row['family']} ({row['evidence_basis']})"
        parts.append(
            f'<text x="24" y="{y+18}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{html.escape(label[:48])}</text>'
        )
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="{max(w,1):.1f}" height="{bar_h}" rx="3" fill="{color}" opacity="0.88"/>'
        )
        parts.append(
            f'<text x="{max(x+w+6, zero_x+6):.1f}" y="{y+18}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{money(v)}</text>'
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_report(
    path: Path,
    rows: list[dict],
    ranked: list[dict],
    inventory: list[dict],
    all_rows_csv: Path,
    ranked_csv: Path,
    inventory_csv: Path,
    chart_svg: Path,
) -> None:
    counts = Counter(r["evidence_basis"] for r in rows)
    status_counts = Counter(r["status"] for r in ranked)
    groups = Counter(r["group"] for r in inventory)
    positives = [r for r in ranked if n(r.get("projected_pnl"), 0) > 0]
    candidate_statuses = {"candidate", "candidate_needs_locked_forward_test", "watchlist_positive"}
    candidates = [r for r in ranked if r.get("status") in candidate_statuses]

    lines = [
        "# Organized Hourly Codex Edge Search Outputs",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`",
        f"- Source folder: `{EDGE.resolve()}`",
        "- Scope: research-only organization of local edge-search outputs. No live entry logic, exit logic, production configs, or bot processes were changed.",
        f"- Parsed evidence rows: `{len(rows)}` across `{len(ranked)}` strategy families.",
        f"- Positive projected-PnL families: `{len(positives)}`; candidate/watchlist-positive families: `{len(candidates)}`.",
        "",
        "## Ranking Method",
        "",
        "- Projected PnL uses validation/holdout PnL when available; otherwise it falls back to full-sample PnL and marks the row as full-sample only.",
        "- Hurdle edge is skip-all/no-trade for entry-admission rules, no-stop hold for exit rules when available, then actual bot behavior as a fallback.",
        "- Rank order is projected PnL first, hurdle edge second, then edge per action.",
        "",
        "## Top Ranked Strategy Families",
        "",
        "| Rank | Family | Variant | Basis | Projected PnL | Hurdle edge | Edge/action | Actions | Win rate | Status |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            "| {rank} | `{family}` | `{variant}` | `{basis}` | {pnl} | {edge} | {epa} | {actions} | {wr} | `{status}` |".format(
                rank=row["rank"],
                family=row["family"],
                variant=row["variant"],
                basis=row["evidence_basis"],
                pnl=money(row["projected_pnl"]),
                edge=money(row["projected_edge_vs_hurdle"]),
                epa=money(row["edge_per_action"]),
                actions="" if n(row.get("actions")) is None else f"{n(row.get('actions')):,.0f}",
                wr=pct(row.get("win_rate")),
                status=row["status"],
            )
        )
    lines.extend(
        [
            "",
            "## Main Reads",
            "",
        ]
    )
    for row in ranked[:8]:
        lines.append(
            f"- `{row['family']}` ranks #{row['rank']} on `{row['evidence_basis']}`: projected {money(row['projected_pnl'])}, edge {money(row['projected_edge_vs_hurdle'])}, edge/action {money(row['edge_per_action'])}."
        )
    lines.extend(
        [
            "",
            "## Evidence Mix",
            "",
        ]
    )
    for basis, count in sorted(counts.items()):
        lines.append(f"- `{basis}`: `{count}` rows")
    lines.extend(["", "## Status Counts", ""])
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: `{count}` families")
    lines.extend(["", "## Output Groups", ""])
    for group, count in sorted(groups.items()):
        lines.append(f"- `{group}`: `{count}` files")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- {md_link(path, 'organized markdown report')}",
            f"- {md_link(ranked_csv, 'ranked strategy family CSV')}",
            f"- {md_link(all_rows_csv, 'all normalized strategy evidence rows CSV')}",
            f"- {md_link(inventory_csv, 'output inventory CSV')}",
            f"- {md_link(chart_svg, 'ranked projected PnL chart')}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    EDGE.mkdir(parents=True, exist_ok=True)
    rows = extract_all_rows()
    ranked = choose_family_rank_rows(rows)
    inventory = inventory_rows()

    all_rows_csv = EDGE / f"codex_hourly_edge_all_strategy_rows_{STAMP}.csv"
    ranked_csv = EDGE / f"codex_hourly_edge_ranked_strategy_families_{STAMP}.csv"
    inventory_csv = EDGE / f"codex_hourly_edge_output_inventory_{STAMP}.csv"
    report_md = EDGE / f"codex_hourly_edge_outputs_organized_{STAMP}.md"
    chart_svg = EDGE / f"codex_hourly_edge_ranked_projected_pnl_{STAMP}.svg"

    write_csv(all_rows_csv, rows)
    write_csv(ranked_csv, ranked)
    write_csv(inventory_csv, inventory)
    write_svg(chart_svg, ranked)
    write_report(report_md, rows, ranked, inventory, all_rows_csv, ranked_csv, inventory_csv, chart_svg)

    latest_report = EDGE / "codex_hourly_edge_outputs_organized_latest.md"
    latest_ranked = EDGE / "codex_hourly_edge_ranked_strategy_families_latest.csv"
    latest_rows = EDGE / "codex_hourly_edge_all_strategy_rows_latest.csv"
    latest_inventory = EDGE / "codex_hourly_edge_output_inventory_latest.csv"
    latest_chart = EDGE / "codex_hourly_edge_ranked_projected_pnl_latest.svg"
    latest_report.write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")
    latest_ranked.write_text(ranked_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_rows.write_text(all_rows_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_inventory.write_text(inventory_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_chart.write_text(chart_svg.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps({
        "report": str(report_md.resolve()),
        "ranked_csv": str(ranked_csv.resolve()),
        "all_rows_csv": str(all_rows_csv.resolve()),
        "inventory_csv": str(inventory_csv.resolve()),
        "chart_svg": str(chart_svg.resolve()),
        "ranked_families": len(ranked),
        "evidence_rows": len(rows),
    }, indent=2))


if __name__ == "__main__":
    main()
