"""Stress audit for the v28 hybrid/boundary entry stack.

Research-only; no live bot changes or orders.

The stack has strong diagnostic PnL. This report asks whether that strength is
durable enough to keep testing: source mix, full-loss cushion, component
ablation, and post-freeze evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json"
OUT_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_stress_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_boundary_entry_stack_stress_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
WATCH_RECONSTRUCTED_SHARE = 0.45


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def find_window(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for window in payload.get("windows") or []:
        if isinstance(window, dict) and window.get("window") == name:
            return window
    return {}


def summary(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("candidate_summary") if isinstance(row.get("candidate_summary"), dict) else {}


def integrity(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("integrity_preview") if isinstance(row.get("integrity_preview"), dict) else {}


def net(row: dict[str, Any]) -> float:
    return as_float(summary(row).get("net_cents")) or 0.0


def coverage(row: dict[str, Any]) -> float | None:
    return as_float(summary(row).get("coverage_pct"))


def settled(row: dict[str, Any]) -> int:
    return int(as_float(summary(row).get("settled")) or 0)


def recon(row: dict[str, Any]) -> float | None:
    return as_float(integrity(row).get("reconstructed_share"))


def is_broad_positive(row: dict[str, Any]) -> bool:
    cov = coverage(row)
    return (
        settled(row) >= MIN_SETTLED
        and cov is not None
        and COVERAGE_MIN <= cov <= COVERAGE_MAX
        and net(row) > 0.0
    )


def compact(row: dict[str, Any]) -> dict[str, Any]:
    s = summary(row)
    i = integrity(row)
    return {
        "candidate": row.get("candidate"),
        "entries": s.get("entries"),
        "settled": s.get("settled"),
        "wins": s.get("wins"),
        "losses": s.get("losses"),
        "coverage_pct": s.get("coverage_pct"),
        "net_cents": s.get("net_cents"),
        "delta_vs_target_cents": row.get("delta_vs_target_cents"),
        "reconstructed_share": i.get("reconstructed_share"),
        "approved_entry_share": i.get("approved_entry_share"),
        "full_loss_cushion_estimate": i.get("full_loss_cushion_estimate"),
        "blockers": row.get("promotion_blockers") or [],
    }


def full_loss_runway(row: dict[str, Any]) -> list[dict[str, Any]]:
    base_net = net(row)
    base_settled = settled(row)
    out = []
    for losses in range(1, 8):
        stressed_net = base_net - 100.0 * losses
        out.append(
            {
                "added_full_losses": losses,
                "stressed_settled": base_settled + losses,
                "stressed_net_cents": stressed_net,
                "still_positive": stressed_net > 0.0,
            }
        )
    return out


def component_family(name: str) -> str:
    if str(name).startswith("hybrid_veto_plus_early_no"):
        return "hybrid_veto_plus_early_no"
    if str(name).startswith("early_no_plus_boundary_clock"):
        return "early_no_plus_boundary_clock"
    if str(name).startswith("all_three"):
        return "all_three"
    if str(name).startswith("hybrid_veto_plus_boundary_clock"):
        return "hybrid_veto_plus_boundary_clock"
    return "other"


def family_best(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(component_family(str(row.get("candidate"))), []).append(row)
    out = []
    for family, items in grouped.items():
        broad = [row for row in items if is_broad_positive(row)] or items
        best = sorted(broad, key=lambda row: net(row), reverse=True)[0]
        compacted = compact(best)
        compacted["family"] = family
        out.append(compacted)
    return sorted(out, key=lambda row: float(row.get("net_cents") or -999999.0), reverse=True)


def pick_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    broad_positive = [row for row in rows if is_broad_positive(row)]
    clean_gate = [
        row for row in broad_positive
        if (recon(row) is not None and float(recon(row) or 1.0) <= MAX_RECONSTRUCTED_SHARE)
    ]
    watch_gate = [
        row for row in broad_positive
        if (recon(row) is not None and float(recon(row) or 1.0) <= WATCH_RECONSTRUCTED_SHARE)
    ]
    best_pnl = sorted(broad_positive, key=lambda row: net(row), reverse=True)[0] if broad_positive else {}
    best_watch = sorted(watch_gate, key=lambda row: (net(row), -float(recon(row) or 1.0)), reverse=True)[0] if watch_gate else {}
    lowest_recon = sorted(broad_positive, key=lambda row: (float(recon(row) or 1.0), -net(row)))[0] if broad_positive else {}
    return {
        "best_broad_positive": compact(best_pnl) if best_pnl else {},
        "best_watch_source_broad_positive": compact(best_watch) if best_watch else {},
        "lowest_reconstructed_broad_positive": compact(lowest_recon) if lowest_recon else {},
        "clean_gate_count": len(clean_gate),
        "watch_gate_count": len(watch_gate),
        "broad_positive_count": len(broad_positive),
        "best_full_loss_runway": full_loss_runway(best_pnl) if best_pnl else [],
        "watch_full_loss_runway": full_loss_runway(best_watch) if best_watch else [],
    }


def build_report() -> dict[str, Any]:
    stack = load_json(STACK_JSON)
    diagnostic = find_window(stack, "diagnostic_existing_target_window")
    post = find_window(stack, "post_stack_freeze_window")
    diag_rows = diagnostic.get("variants") if isinstance(diagnostic.get("variants"), list) else []
    post_rows = post.get("variants") if isinstance(post.get("variants"), list) else []
    picks = pick_rows(diag_rows)
    post_picks = pick_rows(post_rows)
    return {
        "purpose": "Stress audit for the combined hybrid-veto / early-NO / boundary-clock entry stack.",
        "generated_from": str(STACK_JSON),
        "stack_generated_at_utc": stack.get("generated_at_utc"),
        "stack_freeze_utc": (stack.get("state") or {}).get("freeze_ts_utc"),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_band": [COVERAGE_MIN, COVERAGE_MAX],
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "watch_reconstructed_share": WATCH_RECONSTRUCTED_SHARE,
        },
        "diagnostic": {
            **picks,
            "family_best": family_best(diag_rows),
        },
        "post_freeze": {
            **post_picks,
            "forward_denominator": post.get("forward_denominator"),
        },
        "interpretation": interpretation(picks, post_picks, post),
    }


def interpretation(picks: dict[str, Any], post_picks: dict[str, Any], post: dict[str, Any]) -> list[str]:
    best = picks.get("best_broad_positive") or {}
    watch = picks.get("best_watch_source_broad_positive") or {}
    lowest = picks.get("lowest_reconstructed_broad_positive") or {}
    notes = []
    if best:
        notes.append(
            f"Best diagnostic broad-positive variant is {best.get('candidate')} with net {best.get('net_cents')}c, coverage {best.get('coverage_pct')}%, reconstructed share {best.get('reconstructed_share')}."
        )
    if watch:
        notes.append(
            f"Best <=45% reconstructed broad-positive variant is {watch.get('candidate')} with net {watch.get('net_cents')}c and reconstructed share {watch.get('reconstructed_share')}."
        )
    if lowest:
        notes.append(
            f"Lowest-reconstructed broad-positive variant is {lowest.get('candidate')} with net {lowest.get('net_cents')}c and reconstructed share {lowest.get('reconstructed_share')}."
        )
    if int(picks.get("clean_gate_count") or 0) == 0:
        notes.append("No diagnostic broad-positive variant clears the strict <=35% reconstructed-share gate yet.")
    if int(post.get("forward_denominator") or 0) < MIN_SETTLED:
        notes.append(
            f"Post-freeze stack evidence is immature: denominator {post.get('forward_denominator')}, best post-freeze settled {((post_picks.get('best_broad_positive') or {}).get('settled'))}."
        )
    notes.append("Keep testing, but do not promote: the edge is promising and source-quality limited.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Hybrid/Boundary Entry Stack Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Stack freeze UTC: `{report.get('stack_freeze_utc')}`",
        f"- Source stack artifact: `{report.get('generated_from')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")

    for title, key in [
        ("Diagnostic Picks", "diagnostic"),
        ("Post-Freeze Picks", "post_freeze"),
    ]:
        block = report.get(key) or {}
        lines.extend(["", f"## {title}", ""])
        lines.extend(["| pick | candidate | settled | coverage | net c | recon share | loss cushion | blockers |", "|---|---|---:|---:|---:|---:|---:|---|"])
        for label, row_key in [
            ("best_pnl", "best_broad_positive"),
            ("best_watch_source", "best_watch_source_broad_positive"),
            ("lowest_recon", "lowest_reconstructed_broad_positive"),
        ]:
            row = block.get(row_key) or {}
            lines.append(
                f"| {label} | {row.get('candidate')} | {row.get('settled')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
                f"{fmt(row.get('full_loss_cushion_estimate'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )

    lines.extend(["", "## Diagnostic Family Best", ""])
    lines.extend(["| family | candidate | settled | coverage | net c | recon share | blockers |", "|---|---|---:|---:|---:|---:|---|"])
    for row in (report.get("diagnostic") or {}).get("family_best") or []:
        lines.append(
            f"| {row.get('family')} | {row.get('candidate')} | {row.get('settled')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )

    lines.extend(["", "## Full-Loss Runway", ""])
    lines.extend(["| lane | added full losses | stressed settled | stressed net c | still positive |", "|---|---:|---:|---:|---|"])
    for lane, row_key in [("best_pnl", "best_full_loss_runway"), ("best_watch_source", "watch_full_loss_runway")]:
        for row in (report.get("diagnostic") or {}).get(row_key) or []:
            lines.append(
                f"| {lane} | {row.get('added_full_losses')} | {row.get('stressed_settled')} | "
                f"{fmt(row.get('stressed_net_cents'))} | {row.get('still_positive')} |"
            )

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
