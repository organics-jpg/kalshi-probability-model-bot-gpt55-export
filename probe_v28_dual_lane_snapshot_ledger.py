"""Append-only snapshot ledger for v28 dual-lane live-market validation.

Research-only; no live bot changes and no orders.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
UPDATE_JSON = OUT_DIR / "v28_dual_lane_live_market_update_latest.json"
CHECKLIST_JSON = OUT_DIR / "v28_dual_lane_readiness_checklist_latest.json"
LEDGER_JSONL = OUT_DIR / "v28_dual_lane_live_market_snapshot_ledger.jsonl"
LEDGER_CSV = OUT_DIR / "v28_dual_lane_live_market_snapshot_ledger.csv"
OUT_MD = OUT_DIR / "v28_dual_lane_live_market_snapshot_ledger_latest.md"

FIELDS = [
    "snapshot_at_utc",
    "snapshot_signature",
    "update_generated_at_utc",
    "checklist_generated_at_utc",
    "freeze_ts_utc",
    "freeze_local_time",
    "decision",
    "live_baseline_cents",
    "possible_windows_since_freeze",
    "windows_remaining_to_30",
    "post_freeze_events",
    "post_freeze_entry_rows",
    "post_freeze_distinct_markets",
    "post_freeze_settled_exit_clock_rows",
    "post_freeze_pending_exit_clock_rows",
    "sidecar_entries",
    "sidecar_settled",
    "sidecar_wins",
    "sidecar_losses",
    "sidecar_pnl_wins",
    "sidecar_pnl_losses",
    "sidecar_net_cents",
    "sidecar_coverage_pct",
    "sidecar_reconstructed_share",
    "primary_entries",
    "primary_settled",
    "primary_wins",
    "primary_losses",
    "primary_pnl_wins",
    "primary_pnl_losses",
    "primary_net_cents",
    "primary_coverage_pct",
    "primary_reconstructed_share",
    "own_freeze_policy",
    "own_freeze_settled",
    "own_freeze_wins",
    "own_freeze_losses",
    "own_freeze_net_cents",
    "own_freeze_coverage_pct",
    "own_freeze_reconstructed_share",
    "own_freeze_full_loss_cushion",
    "own_freeze_live_ready",
    "parent_shrink_freeze_ts_utc",
    "parent_shrink_windows_since_freeze",
    "parent_shrink_windows_remaining_to_30",
    "parent_shrink_policy",
    "parent_shrink_settled",
    "parent_shrink_wins",
    "parent_shrink_losses",
    "parent_shrink_net_cents",
    "parent_shrink_coverage_pct",
    "parent_shrink_reconstructed_share",
    "parent_shrink_full_loss_cushion",
    "parent_shrink_live_ready",
    "frontier_freeze_ts_utc",
    "frontier_windows_since_freeze",
    "frontier_windows_remaining_to_30",
    "frontier_label",
    "frontier_weight",
    "frontier_policy",
    "frontier_settled",
    "frontier_wins",
    "frontier_losses",
    "frontier_net_cents",
    "frontier_coverage_pct",
    "frontier_reconstructed_share",
    "frontier_full_loss_cushion",
    "frontier_live_ready",
    "blocked_checks",
    "hard_blockers",
]


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


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def scalar(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return value


def cents(value: Any) -> str:
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return "n/a"
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def pct(value: Any, already_pct: bool = True) -> str:
    amount = fnum(value, math.nan)
    if not math.isfinite(amount):
        return "n/a"
    if not already_pct:
        amount *= 100.0
    return f"{amount:.2f}%"


def build_snapshot() -> dict[str, Any]:
    update = load_json(UPDATE_JSON)
    checklist = load_json(CHECKLIST_JSON)
    sidecar = update.get("sidecar_preview") if isinstance(update.get("sidecar_preview"), dict) else {}
    primary = update.get("primary_proxy_preview") if isinstance(update.get("primary_proxy_preview"), dict) else {}
    policies = update.get("own_freeze_policies") if isinstance(update.get("own_freeze_policies"), list) else []
    own = policies[0] if policies and isinstance(policies[0], dict) else {}
    parent_shrink = update.get("parent_shrink_watch") if isinstance(update.get("parent_shrink_watch"), dict) else {}
    parent_best = parent_shrink.get("best_union") if isinstance(parent_shrink.get("best_union"), dict) else {}
    parent_summary = parent_best.get("summary") if isinstance(parent_best.get("summary"), dict) else {}
    parent_sidecar = parent_best.get("sidecar") if isinstance(parent_best.get("sidecar"), dict) else {}
    frontier = update.get("parent_shrink_frontier_watch") if isinstance(update.get("parent_shrink_frontier_watch"), dict) else {}
    frontier_best = frontier.get("best_union") if isinstance(frontier.get("best_union"), dict) else {}
    frontier_summary = frontier_best.get("summary") if isinstance(frontier_best.get("summary"), dict) else {}
    frontier_sidecar = frontier_best.get("sidecar") if isinstance(frontier_best.get("sidecar"), dict) else {}
    signature_parts = [
        update.get("live_baseline_cents"),
        update.get("post_freeze_entry_rows"),
        update.get("post_freeze_distinct_markets"),
        update.get("post_freeze_settled_exit_clock_rows"),
        update.get("possible_windows_since_freeze"),
        sidecar.get("entries"),
        sidecar.get("settled"),
        sidecar.get("wins"),
        sidecar.get("losses"),
        sidecar.get("net_cents"),
        primary.get("entries"),
        primary.get("settled"),
        primary.get("wins"),
        primary.get("losses"),
        primary.get("net_cents"),
        own.get("settled"),
        own.get("net_cents"),
        own.get("coverage_pct"),
        own.get("reconstructed_share"),
        parent_shrink.get("possible_market_windows_since_freeze"),
        parent_summary.get("settled"),
        parent_summary.get("net_cents"),
        parent_summary.get("coverage_pct"),
        frontier.get("possible_market_windows_since_freeze"),
        frontier_best.get("frontier_label"),
        frontier_best.get("frontier_weight"),
        frontier_summary.get("settled"),
        frontier_summary.get("net_cents"),
        frontier_summary.get("coverage_pct"),
    ]
    return {
        "snapshot_at_utc": utc_now_iso(),
        "snapshot_signature": "|".join(str(part) for part in signature_parts),
        "update_generated_at_utc": update.get("generated_at_utc"),
        "checklist_generated_at_utc": checklist.get("generated_at_utc"),
        "freeze_ts_utc": update.get("freeze_ts_utc"),
        "freeze_local_time": update.get("freeze_local_time"),
        "decision": update.get("decision"),
        "live_baseline_cents": update.get("live_baseline_cents"),
        "possible_windows_since_freeze": update.get("possible_windows_since_freeze"),
        "windows_remaining_to_30": update.get("windows_remaining_to_30"),
        "post_freeze_events": update.get("post_freeze_events"),
        "post_freeze_entry_rows": update.get("post_freeze_entry_rows"),
        "post_freeze_distinct_markets": update.get("post_freeze_distinct_markets"),
        "post_freeze_settled_exit_clock_rows": update.get("post_freeze_settled_exit_clock_rows"),
        "post_freeze_pending_exit_clock_rows": update.get("post_freeze_pending_exit_clock_rows"),
        "sidecar_entries": sidecar.get("entries"),
        "sidecar_settled": sidecar.get("settled"),
        "sidecar_wins": sidecar.get("wins"),
        "sidecar_losses": sidecar.get("losses"),
        "sidecar_pnl_wins": sidecar.get("pnl_wins"),
        "sidecar_pnl_losses": sidecar.get("pnl_losses"),
        "sidecar_net_cents": sidecar.get("net_cents"),
        "sidecar_coverage_pct": sidecar.get("coverage_pct"),
        "sidecar_reconstructed_share": sidecar.get("reconstructed_share"),
        "primary_entries": primary.get("entries"),
        "primary_settled": primary.get("settled"),
        "primary_wins": primary.get("wins"),
        "primary_losses": primary.get("losses"),
        "primary_pnl_wins": primary.get("pnl_wins"),
        "primary_pnl_losses": primary.get("pnl_losses"),
        "primary_net_cents": primary.get("net_cents"),
        "primary_coverage_pct": primary.get("coverage_pct"),
        "primary_reconstructed_share": primary.get("reconstructed_share"),
        "own_freeze_policy": own.get("policy"),
        "own_freeze_settled": own.get("settled"),
        "own_freeze_wins": own.get("wins"),
        "own_freeze_losses": own.get("losses"),
        "own_freeze_net_cents": own.get("net_cents"),
        "own_freeze_coverage_pct": own.get("coverage_pct"),
        "own_freeze_reconstructed_share": own.get("reconstructed_share"),
        "own_freeze_full_loss_cushion": own.get("full_loss_cushion"),
        "own_freeze_live_ready": own.get("live_ready"),
        "parent_shrink_freeze_ts_utc": parent_shrink.get("freeze_ts_utc"),
        "parent_shrink_windows_since_freeze": parent_shrink.get("possible_market_windows_since_freeze"),
        "parent_shrink_windows_remaining_to_30": parent_shrink.get("market_windows_remaining_to_min_sample"),
        "parent_shrink_policy": parent_sidecar.get("policy"),
        "parent_shrink_settled": parent_summary.get("settled"),
        "parent_shrink_wins": parent_summary.get("wins"),
        "parent_shrink_losses": parent_summary.get("losses"),
        "parent_shrink_net_cents": parent_summary.get("net_cents"),
        "parent_shrink_coverage_pct": parent_summary.get("coverage_pct"),
        "parent_shrink_reconstructed_share": parent_summary.get("reconstructed_share"),
        "parent_shrink_full_loss_cushion": parent_summary.get("full_loss_cushion"),
        "parent_shrink_live_ready": parent_best.get("live_ready"),
        "frontier_freeze_ts_utc": frontier.get("freeze_ts_utc"),
        "frontier_windows_since_freeze": frontier.get("possible_market_windows_since_freeze"),
        "frontier_windows_remaining_to_30": frontier.get("market_windows_remaining_to_min_sample"),
        "frontier_label": frontier_best.get("frontier_label"),
        "frontier_weight": frontier_best.get("frontier_weight"),
        "frontier_policy": frontier_sidecar.get("policy"),
        "frontier_settled": frontier_summary.get("settled"),
        "frontier_wins": frontier_summary.get("wins"),
        "frontier_losses": frontier_summary.get("losses"),
        "frontier_net_cents": frontier_summary.get("net_cents"),
        "frontier_coverage_pct": frontier_summary.get("coverage_pct"),
        "frontier_reconstructed_share": frontier_summary.get("reconstructed_share"),
        "frontier_full_loss_cushion": frontier_summary.get("full_loss_cushion"),
        "frontier_live_ready": frontier_best.get("live_ready"),
        "blocked_checks": checklist.get("blocked_checks") if isinstance(checklist.get("blocked_checks"), list) else [],
        "hard_blockers": update.get("hard_blockers") if isinstance(update.get("hard_blockers"), list) else [],
    }


def read_ledger() -> list[dict[str, Any]]:
    if not LEDGER_JSONL.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in LEDGER_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def append_snapshot(snapshot: dict[str, Any], rows: list[dict[str, Any]]) -> bool:
    signature = snapshot.get("snapshot_signature")
    if signature and any(row.get("snapshot_signature") == signature for row in rows):
        return False
    key = snapshot.get("update_generated_at_utc")
    if not signature and key and any(row.get("update_generated_at_utc") == key for row in rows):
        return False
    with LEDGER_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot, sort_keys=True, default=str) + "\n")
    return True


def write_csv(rows: list[dict[str, Any]]) -> None:
    with LEDGER_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: scalar(row.get(field)) for field in FIELDS})


def score_signature(row: dict[str, Any]) -> str:
    if row.get("snapshot_signature"):
        return str(row.get("snapshot_signature"))
    parts = [
        row.get("live_baseline_cents"),
        row.get("post_freeze_entry_rows"),
        row.get("post_freeze_distinct_markets"),
        row.get("post_freeze_settled_exit_clock_rows"),
        row.get("possible_windows_since_freeze"),
        row.get("sidecar_entries"),
        row.get("sidecar_settled"),
        row.get("sidecar_wins"),
        row.get("sidecar_losses"),
        row.get("sidecar_net_cents"),
        row.get("primary_entries"),
        row.get("primary_settled"),
        row.get("primary_wins"),
        row.get("primary_losses"),
        row.get("primary_net_cents"),
        row.get("own_freeze_settled"),
        row.get("own_freeze_net_cents"),
        row.get("own_freeze_coverage_pct"),
        row.get("own_freeze_reconstructed_share"),
        row.get("parent_shrink_windows_since_freeze"),
        row.get("parent_shrink_settled"),
        row.get("parent_shrink_net_cents"),
        row.get("parent_shrink_coverage_pct"),
        row.get("frontier_windows_since_freeze"),
        row.get("frontier_label"),
        row.get("frontier_weight"),
        row.get("frontier_settled"),
        row.get("frontier_net_cents"),
        row.get("frontier_coverage_pct"),
    ]
    return "|".join(str(part) for part in parts)


def unique_score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        sig = score_signature(row)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(row)
    return out


def delta(new: Any, old: Any) -> float | None:
    left = fnum(new, math.nan)
    right = fnum(old, math.nan)
    if not math.isfinite(left) or not math.isfinite(right):
        return None
    return left - right


def write_md(rows: list[dict[str, Any]], appended: bool) -> None:
    score_rows = unique_score_rows(rows)
    latest = score_rows[-1] if score_rows else {}
    first = score_rows[0] if score_rows else {}
    prev = score_rows[-2] if len(score_rows) >= 2 else {}
    sidecar_delta = delta(latest.get("sidecar_net_cents"), prev.get("sidecar_net_cents")) if prev else None
    primary_delta = delta(latest.get("primary_net_cents"), prev.get("primary_net_cents")) if prev else None
    since_first_sidecar = delta(latest.get("sidecar_net_cents"), first.get("sidecar_net_cents")) if first else None
    since_first_primary = delta(latest.get("primary_net_cents"), first.get("primary_net_cents")) if first else None
    lines = [
        "# v28 Dual-Lane Live Market Snapshot Ledger",
        "",
        "Research-only. Append-only score ledger; no live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{utc_now_iso()}`",
        f"- Rows: `{len(rows)}`",
        f"- Unique score states: `{len(score_rows)}`",
        f"- Appended this run: `{appended}`",
        f"- Latest update UTC: `{latest.get('update_generated_at_utc')}`",
        f"- Freeze UTC/local: `{latest.get('freeze_ts_utc')}` / `{latest.get('freeze_local_time')}`",
        f"- Decision: `{latest.get('decision')}`",
        f"- Live baseline: `{cents(latest.get('live_baseline_cents'))}`",
        "",
        "## Latest Snapshot",
        "",
        "| metric | sidecar | primary proxy | own-freeze promotion | parent-shrink repair | shrink frontier |",
        "|---|---:|---:|---:|---:|---:|",
        (
            f"| entries | {latest.get('sidecar_entries')} | {latest.get('primary_entries')} | "
            f"{latest.get('own_freeze_settled')} settled | {latest.get('parent_shrink_settled')} settled | "
            f"{latest.get('frontier_settled')} settled |"
        ),
        (
            f"| W/L | {latest.get('sidecar_wins')}/{latest.get('sidecar_losses')} | "
            f"{latest.get('primary_wins')}/{latest.get('primary_losses')} | "
            f"{latest.get('own_freeze_wins')}/{latest.get('own_freeze_losses')} | "
            f"{latest.get('parent_shrink_wins')}/{latest.get('parent_shrink_losses')} | "
            f"{latest.get('frontier_wins')}/{latest.get('frontier_losses')} |"
        ),
        (
            f"| PnL W/L | {latest.get('sidecar_pnl_wins')}/{latest.get('sidecar_pnl_losses')} | "
            f"{latest.get('primary_pnl_wins')}/{latest.get('primary_pnl_losses')} | n/a | n/a | n/a |"
        ),
        (
            f"| net | {cents(latest.get('sidecar_net_cents'))} | {cents(latest.get('primary_net_cents'))} | "
            f"{cents(latest.get('own_freeze_net_cents'))} | {cents(latest.get('parent_shrink_net_cents'))} | "
            f"{cents(latest.get('frontier_net_cents'))} |"
        ),
        (
            f"| coverage | {pct(latest.get('sidecar_coverage_pct'))} | {pct(latest.get('primary_coverage_pct'))} | "
            f"{pct(latest.get('own_freeze_coverage_pct'))} | {pct(latest.get('parent_shrink_coverage_pct'))} | "
            f"{pct(latest.get('frontier_coverage_pct'))} |"
        ),
        (
            f"| recon | {pct(latest.get('sidecar_reconstructed_share'), False)} | "
            f"{pct(latest.get('primary_reconstructed_share'), False)} | "
            f"{pct(latest.get('own_freeze_reconstructed_share'), False)} | "
            f"{pct(latest.get('parent_shrink_reconstructed_share'), False)} | "
            f"{pct(latest.get('frontier_reconstructed_share'), False)} |"
        ),
        (
            f"| label | n/a | n/a | n/a | n/a | "
            f"`{latest.get('frontier_label')}` / `{latest.get('frontier_weight')}` |"
        ),
        "",
        "## Trend",
        "",
        f"- Sidecar net delta vs previous snapshot: `{cents(sidecar_delta)}`",
        f"- Primary proxy net delta vs previous snapshot: `{cents(primary_delta)}`",
        f"- Sidecar net delta since ledger start: `{cents(since_first_sidecar)}`",
        f"- Primary proxy net delta since ledger start: `{cents(since_first_primary)}`",
        f"- Windows since freeze / remaining: `{latest.get('possible_windows_since_freeze')}` / `{latest.get('windows_remaining_to_30')}`",
        f"- Parent-shrink windows since freeze / remaining: `{latest.get('parent_shrink_windows_since_freeze')}` / `{latest.get('parent_shrink_windows_remaining_to_30')}`",
        f"- Frontier windows since freeze / remaining: `{latest.get('frontier_windows_since_freeze')}` / `{latest.get('frontier_windows_remaining_to_30')}`",
        f"- Post-freeze events / entry rows / markets: `{latest.get('post_freeze_events')}` / `{latest.get('post_freeze_entry_rows')}` / `{latest.get('post_freeze_distinct_markets')}`",
        "",
        "## Current Blockers",
        "",
    ]
    blocked = latest.get("blocked_checks") or latest.get("hard_blockers") or []
    if blocked:
        lines.extend(f"- `{item}`" for item in blocked)
    else:
        lines.append("- none")
    tail = score_rows[-10:]
    if tail:
        lines.extend(
            [
                "",
                "## Recent Rows",
                "",
                "| update UTC | windows | markets | sidecar W/L | sidecar net | primary W/L | primary net | decision |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in tail:
            lines.append(
                f"| `{row.get('update_generated_at_utc')}` | {row.get('possible_windows_since_freeze')} | "
                f"{row.get('post_freeze_distinct_markets')} | {row.get('sidecar_wins')}/{row.get('sidecar_losses')} | "
                f"{cents(row.get('sidecar_net_cents'))} | {row.get('primary_wins')}/{row.get('primary_losses')} | "
                f"{cents(row.get('primary_net_cents'))} | `{row.get('decision')}` |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_ledger()
    snapshot = build_snapshot()
    appended = append_snapshot(snapshot, rows)
    if appended:
        rows.append(snapshot)
    write_csv(rows)
    write_md(rows, appended)
    print(OUT_MD)


if __name__ == "__main__":
    main()
