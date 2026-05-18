"""Audit true-loser hold risk before broadening v28 exit suppression.

Research-only; no live bot changes or orders.

Exit repairs are useful only when the current exit clipped a future winner.
The dangerous mirror image is a true FV/entry-timing loser where suppressing
the exit would turn a controlled loss into a larger settlement loss. This
report keeps those populations separate so future exit watches do not learn
from clipped-winner rows and accidentally hold true losers.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOSS_ESCAPE_JSON = OUT_DIR / "v28_live_loss_escape_analysis_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_true_loser_hold_risk_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_true_loser_hold_risk_audit_latest.md"


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def hold_delta(row: dict[str, Any]) -> float | None:
    actual = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    if actual is None or hold is None:
        return None
    return hold - actual


def best_effect(row: dict[str, Any]) -> dict[str, Any]:
    effect = row.get("best_policy_effect")
    return effect if isinstance(effect, dict) else {}


def derived_tags(row: dict[str, Any]) -> set[str]:
    tags = {str(tag) for tag in row.get("physics_tags") or []}
    ask = as_float(row.get("ask_cents"))
    abs_d = as_float(row.get("abs_d_sigma"))
    depth = as_float(row.get("eligible_depth"))
    p_side = as_float(row.get("p_side"))
    exit_cents = as_float(row.get("exit_cents") or best_effect(row).get("exit_cents"))
    p_hold = as_float(best_effect(row).get("p_hold"))

    if ask is not None:
        if ask < 55:
            tags.add("ask_lt55")
        if ask >= 70:
            tags.add("ask_gte70")
    if abs_d is not None:
        if abs_d <= 0.25:
            tags.add("absd_lte025")
        if abs_d <= 0.50:
            tags.add("absd_lte050")
        if abs_d >= 0.85:
            tags.add("absd_gte085")
    if depth is not None:
        if depth <= 150:
            tags.add("depth_lte150")
        if depth <= 384:
            tags.add("depth_lte384")
    if p_side is not None:
        if p_side < 0.60:
            tags.add("p_side_lt60")
        if p_side >= 0.85:
            tags.add("p_side_gte85")
    if exit_cents is not None:
        if exit_cents <= 40:
            tags.add("exit_cents_lte40")
        if exit_cents >= 60:
            tags.add("exit_cents_gte60")
    if p_hold is not None:
        if p_hold < 0.60:
            tags.add("exit_p_hold_lt60")
        if 0.60 <= p_hold < 0.75:
            tags.add("exit_p_hold_60_75")
        if p_hold >= 0.75:
            tags.add("exit_p_hold_gte75")
    return tags


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    known_hold = [row for row in rows if hold_delta(row) is not None]
    helpful = [row for row in known_hold if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in known_hold if (hold_delta(row) or 0.0) < 0.0]
    return {
        "rows": len(rows),
        "actual_loss_cents": sum(as_float(row.get("actual_gross_cents")) or 0.0 for row in rows),
        "hold_delta_cents": sum(hold_delta(row) or 0.0 for row in known_hold),
        "known_hold_rows": len(known_hold),
        "hold_helpful_rows": len(helpful),
        "hold_harmful_rows": len(harmful),
        "hold_unknown_rows": len(rows) - len(known_hold),
    }


def bucket_report(
    true_loser_rows: list[dict[str, Any]],
    clipped_winner_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    true_by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    clip_by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in true_loser_rows:
        for tag in derived_tags(row):
            true_by_tag[tag].append(row)
    for row in clipped_winner_rows:
        for tag in derived_tags(row):
            clip_by_tag[tag].append(row)

    rows = []
    for tag in sorted(set(true_by_tag) | set(clip_by_tag)):
        true_rows = true_by_tag.get(tag, [])
        clip_rows = clip_by_tag.get(tag, [])
        true_summary = summarize(true_rows)
        clip_summary = summarize(clip_rows)
        true_count = true_summary["rows"]
        clip_count = clip_summary["rows"]
        if true_count == 0 and clip_count < 3:
            continue
        net_hold_delta = true_summary["hold_delta_cents"] + clip_summary["hold_delta_cents"]
        if true_count >= 3 and true_count >= clip_count:
            read = "avoid_broad_hold"
        elif clip_count >= 3 and clip_count > true_count:
            read = "possible_clip_repair_context"
        else:
            read = "mixed_or_sparse"
        rows.append({
            "tag": tag,
            "true_loser_rows": true_count,
            "true_loser_actual_loss_cents": true_summary["actual_loss_cents"],
            "true_loser_hold_delta_cents": true_summary["hold_delta_cents"],
            "clipped_winner_rows": clip_count,
            "clipped_winner_actual_loss_cents": clip_summary["actual_loss_cents"],
            "clipped_winner_hold_delta_cents": clip_summary["hold_delta_cents"],
            "combined_hold_delta_cents": net_hold_delta,
            "read": read,
        })
    return sorted(
        rows,
        key=lambda row: (
            row["read"] != "avoid_broad_hold",
            -row["true_loser_rows"],
            row["true_loser_hold_delta_cents"],
        ),
    )


def examples(rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: hold_delta(row) if hold_delta(row) is not None else 0.0)
    out = []
    for row in ranked[:limit]:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "actual_cents": row.get("actual_gross_cents"),
            "hold_cents": row.get("hold_gross_cents"),
            "hold_delta_cents": hold_delta(row),
            "ask_cents": row.get("ask_cents"),
            "p_side": row.get("p_side"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "exit_cents": row.get("exit_cents") or best_effect(row).get("exit_cents"),
            "p_hold": best_effect(row).get("p_hold"),
            "tags": sorted(derived_tags(row)),
        })
    return out


def build_report() -> dict[str, Any]:
    source = load_json(LOSS_ESCAPE_JSON)
    rows = source.get("loss_rows_with_details") or []
    if not isinstance(rows, list):
        rows = []

    true_loser_rows = [
        row for row in rows
        if row.get("failure_class") == "fv_or_entry_timing_error"
        or ((hold_delta(row) or 0.0) < 0.0)
    ]
    clipped_winner_rows = [
        row for row in rows
        if row.get("failure_class") == "exit_policy_cost"
        and ((hold_delta(row) or 0.0) > 0.0)
    ]
    repair_flipped_rows = [
        row for row in rows
        if row.get("escape_class") == "repair_flips_loss"
    ]
    bucket_rows = bucket_report(true_loser_rows, clipped_winner_rows)
    avoid_tags = [
        row for row in bucket_rows
        if row["read"] == "avoid_broad_hold"
        and row["true_loser_rows"] >= 3
        and row["true_loser_hold_delta_cents"] < 0
    ][:12]

    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(LOSS_ESCAPE_JSON),
        "summary": {
            "loss_rows": len(rows),
            "true_loser_rows": len(true_loser_rows),
            "clipped_winner_rows": len(clipped_winner_rows),
            "repair_flipped_rows": len(repair_flipped_rows),
            "true_loser": summarize(true_loser_rows),
            "clipped_winner": summarize(clipped_winner_rows),
            "repair_flipped": summarize(repair_flipped_rows),
            "avoid_broad_hold_tag_count": len(avoid_tags),
        },
        "avoid_broad_hold_tags": avoid_tags,
        "bucket_rows": bucket_rows,
        "worst_true_loser_hold_examples": examples(true_loser_rows),
        "best_clipped_winner_hold_examples": examples(
            sorted(clipped_winner_rows, key=lambda row: -(hold_delta(row) or 0.0))
        ),
        "interpretation": [
            "Research-only audit; this does not create or promote an exit rule.",
            "True-loser rows are FV/entry-timing failures or rows where holding worsens the loss.",
            "Broad exit suppression should avoid tags that are dominated by true-loser hold harm unless a stricter forward watch proves otherwise.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    true_summary = summary["true_loser"]
    clip_summary = summary["clipped_winner"]
    lines = [
        "# v28 Exit True-Loser Hold Risk Audit",
        "",
        "Research-only guardrail. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Loss rows: `{summary['loss_rows']}`",
        f"- True-loser hold-risk rows: `{summary['true_loser_rows']}`",
        f"- Clipped-winner hold-helpful rows: `{summary['clipped_winner_rows']}`",
        f"- Repair-flipped rows: `{summary['repair_flipped_rows']}`",
        "",
        "## Interpretation",
        "",
        "- This audit separates exits that clipped winners from exits that prevented larger FV/entry-timing losses.",
        f"- True-loser rows have hold delta `{cents(true_summary['hold_delta_cents'])}` across `{true_summary['rows']}` rows.",
        f"- Clipped-winner rows have hold delta `{cents(clip_summary['hold_delta_cents'])}` across `{clip_summary['rows']}` rows.",
        "- Future exit watches should prove they avoid the true-loser tags under strict post-freeze evidence before broad suppression is trusted.",
        "",
        "## Avoid Broad Hold Tags",
        "",
        "| tag | true rows | true hold delta | clipped rows | clipped hold delta | combined hold delta | read |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["avoid_broad_hold_tags"]:
        lines.append(
            f"| `{row['tag']}` | {row['true_loser_rows']} | {cents(row['true_loser_hold_delta_cents'])} | "
            f"{row['clipped_winner_rows']} | {cents(row['clipped_winner_hold_delta_cents'])} | "
            f"{cents(row['combined_hold_delta_cents'])} | `{row['read']}` |"
        )

    lines.extend([
        "",
        "## Bucket Contrast",
        "",
        "| tag | true rows | true hold delta | clipped rows | clipped hold delta | combined hold delta | read |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report["bucket_rows"][:30]:
        lines.append(
            f"| `{row['tag']}` | {row['true_loser_rows']} | {cents(row['true_loser_hold_delta_cents'])} | "
            f"{row['clipped_winner_rows']} | {cents(row['clipped_winner_hold_delta_cents'])} | "
            f"{cents(row['combined_hold_delta_cents'])} | `{row['read']}` |"
        )

    lines.extend([
        "",
        "## Worst True-Loser Hold Examples",
        "",
        "| market | side/result | actual | hold | hold delta | ask | p_side | abs d | exit | p_hold | tags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report["worst_true_loser_hold_examples"][:10]:
        lines.append(
            f"| `{row['market']}` | {row.get('side')}/{row.get('result')} | "
            f"{cents(row.get('actual_cents'))} | {cents(row.get('hold_cents'))} | {cents(row.get('hold_delta_cents'))} | "
            f"{row.get('ask_cents')} | {row.get('p_side')} | {row.get('abs_d_sigma')} | "
            f"{row.get('exit_cents')} | {row.get('p_hold')} | {', '.join(row.get('tags') or [])} |"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
