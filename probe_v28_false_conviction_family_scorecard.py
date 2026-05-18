"""Family scorecard for false-conviction v28 candidates.

Research-only; no live bot changes or orders.

This consolidates the current direction: early boundary/high-recross states
where executable FV edge may be false conviction. The scorecard intentionally
separates frozen-forward evidence from diagnostic/backfilled evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_false_conviction_family_scorecard_latest.json"
OUT_MD = OUT_DIR / "v28_false_conviction_family_scorecard_latest.md"
BRIDGE_SOURCE_QUALITY_JSON = OUT_DIR / "v28_fv_bridge_source_quality_latest.json"

SOURCES = [
    {
        "name": "early_no_boundary_decay_repair",
        "path": OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.json",
        "mode": "frozen_forward_stress",
        "candidate_path": ("candidate_summary",),
        "delta_path": ("delta_vs_target_cents",),
        "source_path": ("candidate_source_summary",),
        "runway_path": ("future_loss_runway",),
        "warnings_path": ("warnings",),
        "physics": "Early NO near-boundary/high-recross entries decay because the path can recross before close.",
    },
    {
        "name": "composite_false_conviction_repair",
        "path": OUT_DIR / "v28_composite_false_conviction_repair_stress_latest.json",
        "mode": "frozen_forward_stress",
        "candidate_path": ("candidate_summary",),
        "delta_path": ("delta_vs_target_cents",),
        "source_path": ("candidate_source_summary",),
        "runway_path": ("future_loss_runway",),
        "warnings_path": ("warnings",),
        "physics": "Broader false-conviction zone removes early boundary, cheap turbulence, and mid-edge traps.",
    },
    {
        "name": "goldilocks_edge_repair",
        "path": OUT_DIR / "v28_goldilocks_edge_repair_stress_latest.json",
        "mode": "diagnostic_plus_frozen",
        "candidate_path": ("frozen_future", "candidate_summary"),
        "delta_path": ("frozen_future", "delta_vs_target_cents"),
        "source_path": ("frozen_future", "candidate_source_summary"),
        "runway_path": ("frozen_future", "full_loss_runway"),
        "warnings_path": ("frozen_future", "warnings"),
        "diagnostic_candidate_path": ("diagnostic", "candidate_summary"),
        "diagnostic_delta_path": ("diagnostic", "delta_vs_target_cents"),
        "diagnostic_source_path": ("diagnostic", "candidate_source_summary"),
        "diagnostic_warnings_path": ("diagnostic", "warnings"),
        "physics": "Raw edge is non-monotonic near high-recross boundaries; modest book/model agreement can beat large apparent edge.",
    },
    {
        "name": "false_conviction_approved_repair",
        "path": OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.json",
        "mode": "frozen_forward_source_quality",
        "candidate_path": ("candidate_summary",),
        "delta_path": None,
        "source_path": None,
        "runway_path": None,
        "warnings_path": ("interpretation",),
        "physics": "Approved-entry-heavy repair tests whether false-conviction filtering survives without depending on rejected-actionable reconstruction.",
    },
    {
        "name": "false_conviction_fv_entry_bridge",
        "path": OUT_DIR / "v28_false_conviction_fv_entry_bridge_latest.json",
        "mode": "fv_bridge_diagnostic_plus_frozen",
        "bridge": True,
        "physics": "Move false-conviction and phi/recross forgetting into FV before entry selection, then thin to the 75-80% coverage band by escape energy.",
    },
    {
        "name": "target_loss_tag_repair",
        "path": OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_latest.json",
        "mode": "frozen_forward",
        "candidate_path": ("candidate_summary",),
        "delta_path": ("delta_vs_target_cents",),
        "source_path": None,
        "runway_path": None,
        "warnings_path": ("interpretation",),
        "physics": "Skip weak boundary turbulence and paid high-price thin-edge rows, then repair with cleaner rows.",
    },
    {
        "name": "mid_edge_boundary_deception_repair",
        "path": OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json",
        "mode": "frozen_forward",
        "candidate_path": ("candidate_summary",),
        "delta_path": ("delta_vs_target_cents",),
        "source_path": None,
        "runway_path": None,
        "warnings_path": ("interpretation",),
        "physics": "Early high-recross 4-8pp edge rows can be overconfident boundary deception.",
    },
]

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_RECON_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def nested(payload: dict[str, Any], path: tuple[str, ...] | None) -> Any:
    if path is None:
        return None
    value: Any = payload
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reconstructed_share(source_rows: Any) -> float | None:
    if not isinstance(source_rows, list) or not source_rows:
        return None
    total = 0.0
    reconstructed = 0.0
    for row in source_rows:
        if not isinstance(row, dict):
            continue
        entries = as_float(row.get("entries")) or 0.0
        total += entries
        if str(row.get("source") or "").lower() != "approved_entry":
            reconstructed += entries
    if total <= 0:
        return None
    return reconstructed / total


def full_loss_cushion(runway: Any) -> int | None:
    if not isinstance(runway, list):
        return None
    cushion = 0
    for row in runway:
        if isinstance(row, dict) and row.get("still_positive") is True:
            cushion = max(cushion, int(as_float(row.get("added_full_losses")) or 0))
    return cushion


def blockers(row: dict[str, Any]) -> list[str]:
    out = []
    settled = as_float(row.get("settled")) or 0.0
    coverage = as_float(row.get("coverage_pct"))
    net = as_float(row.get("net_cents")) or 0.0
    recon = as_float(row.get("reconstructed_share"))
    cushion = row.get("full_loss_cushion")
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < MIN_COVERAGE:
        out.append("coverage_too_low")
    if coverage is not None and coverage > MAX_COVERAGE:
        out.append("coverage_too_high")
    if net <= 0.0:
        out.append("net_not_positive")
    if recon is None:
        out.append("source_mix_unknown")
    elif recon > MAX_RECON_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if cushion is None:
        out.append("full_loss_cushion_unknown")
    elif cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def score_source(spec: dict[str, Any]) -> dict[str, Any]:
    payload = load_json(spec["path"])
    if spec.get("bridge"):
        return score_bridge_source(spec, payload)
    candidate = nested(payload, spec["candidate_path"]) or {}
    source_rows = nested(payload, spec.get("source_path"))
    runway = nested(payload, spec.get("runway_path"))
    row = {
        "name": spec["name"],
        "mode": spec["mode"],
        "path": str(spec["path"]),
        "physics": spec["physics"],
        "entries": candidate.get("entries"),
        "settled": candidate.get("settled"),
        "wins": candidate.get("wins"),
        "losses": candidate.get("losses"),
        "coverage_pct": candidate.get("coverage_pct"),
        "net_cents": candidate.get("net_cents"),
        "avg_net_cents": candidate.get("avg_net_cents"),
        "delta_vs_target_cents": nested(payload, spec.get("delta_path")),
        "reconstructed_share": reconstructed_share(source_rows),
        "full_loss_cushion": full_loss_cushion(runway),
        "warnings": nested(payload, spec.get("warnings_path")) or [],
        "diagnostic": None,
    }
    if spec.get("diagnostic_candidate_path"):
        diag_candidate = nested(payload, spec["diagnostic_candidate_path"]) or {}
        diag_source_rows = nested(payload, spec.get("diagnostic_source_path"))
        row["diagnostic"] = {
            "entries": diag_candidate.get("entries"),
            "settled": diag_candidate.get("settled"),
            "wins": diag_candidate.get("wins"),
            "losses": diag_candidate.get("losses"),
            "coverage_pct": diag_candidate.get("coverage_pct"),
            "net_cents": diag_candidate.get("net_cents"),
            "delta_vs_target_cents": nested(payload, spec.get("diagnostic_delta_path")),
            "reconstructed_share": reconstructed_share(diag_source_rows),
            "warnings": nested(payload, spec.get("diagnostic_warnings_path")) or [],
        }
    row["blockers"] = blockers(row)
    row["integrity_pass"] = not row["blockers"]
    return row


def bridge_rows(payload: dict[str, Any], window_name: str) -> list[dict[str, Any]]:
    for window in payload.get("windows") or []:
        if isinstance(window, dict) and window.get("window") == window_name:
            rows = window.get("ranked")
            return rows if isinstance(rows, list) else []
    return []


def bridge_best(rows: list[dict[str, Any]], *, diagnostic: bool) -> dict[str, Any]:
    usable = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("score_name") or "")
        if name.endswith("+raw_probability"):
            continue
        coverage = as_float(row.get("coverage_pct"))
        net = as_float(row.get("net_cents")) or 0.0
        if diagnostic and (coverage is None or coverage < MIN_COVERAGE or coverage > MAX_COVERAGE or net <= 0.0):
            continue
        usable.append(row)
    usable.sort(
        key=lambda row: (
            as_float(row.get("net_cents")) or -999999.0,
            -(as_float(row.get("avg_brier")) or 999.0),
            as_float(row.get("settled")) or 0.0,
        ),
        reverse=True,
    )
    return usable[0] if usable else {}


def source_quality_scenarios(payload: dict[str, Any], window_name: str) -> dict[str, dict[str, Any]]:
    for window in payload.get("windows") or []:
        if not isinstance(window, dict) or window.get("window") != window_name:
            continue
        scenarios = window.get("scenarios")
        if not isinstance(scenarios, list):
            return {}
        out = {}
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                continue
            name = scenario.get("scenario")
            if isinstance(name, str):
                out[name] = {
                    "entries": scenario.get("entries"),
                    "settled": scenario.get("settled"),
                    "wins": scenario.get("wins"),
                    "losses": scenario.get("losses"),
                    "coverage_pct": scenario.get("coverage_pct"),
                    "net_cents": scenario.get("net_cents"),
                    "reconstructed_share": scenario.get("reconstructed_share"),
                    "approved_entries": scenario.get("approved_entries"),
                    "reconstructed_entries": scenario.get("reconstructed_entries"),
                    "blockers": scenario.get("blockers") or [],
                }
        return out
    return {}


def score_bridge_source(spec: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    post = bridge_best(bridge_rows(payload, "post_freeze_candidate"), diagnostic=False)
    diag = bridge_best(bridge_rows(payload, "diagnostic_existing_false_conviction_freeze"), diagnostic=True)
    source_quality = load_json(BRIDGE_SOURCE_QUALITY_JSON)
    diagnostic_source_quality = source_quality_scenarios(source_quality, "diagnostic_existing_false_conviction_freeze")
    post_source_quality = source_quality_scenarios(source_quality, "post_freeze_candidate")
    post_source_total = as_float(post.get("approved_entry_count")) or 0.0
    post_source_total += as_float(post.get("reconstructed_count")) or 0.0
    recon = None
    if post_source_total > 0:
        recon = (as_float(post.get("reconstructed_count")) or 0.0) / post_source_total
    row = {
        "name": spec["name"],
        "mode": spec["mode"],
        "path": str(spec["path"]),
        "physics": spec["physics"],
        "entries": post.get("entries"),
        "settled": post.get("settled"),
        "wins": post.get("wins"),
        "losses": post.get("losses"),
        "coverage_pct": post.get("coverage_pct"),
        "net_cents": post.get("net_cents"),
        "avg_net_cents": post.get("avg_net_cents"),
        "delta_vs_target_cents": post.get("delta_net_vs_raw"),
        "reconstructed_share": recon,
        "full_loss_cushion": None,
        "warnings": payload.get("interpretation") or [],
        "diagnostic": None,
    }
    if diag:
        diag_total = (as_float(diag.get("approved_entry_count")) or 0.0) + (as_float(diag.get("reconstructed_count")) or 0.0)
        row["diagnostic"] = {
            "label": diag.get("score_name"),
            "entries": diag.get("entries"),
            "settled": diag.get("settled"),
            "wins": diag.get("wins"),
            "losses": diag.get("losses"),
            "coverage_pct": diag.get("coverage_pct"),
            "net_cents": diag.get("net_cents"),
            "delta_vs_target_cents": diag.get("delta_net_vs_raw"),
            "brier_delta_vs_raw": diag.get("brier_delta_vs_raw"),
            "logloss_delta_vs_raw": diag.get("logloss_delta_vs_raw"),
            "reconstructed_share": None if diag_total <= 0 else (as_float(diag.get("reconstructed_count")) or 0.0) / diag_total,
            "warnings": [
                "Bridge diagnostic is direction-only; post-freeze window must mature before promotion.",
                f"Best diagnostic bridge row: {diag.get('score_name')}",
            ],
            "source_quality": {
                "diagnostic_approved_only": diagnostic_source_quality.get("lead_approved_only"),
                "diagnostic_all_sources": diagnostic_source_quality.get("lead_all_sources"),
                "post_freeze_approved_only": post_source_quality.get("lead_approved_only"),
                "post_freeze_all_sources": post_source_quality.get("lead_all_sources"),
            },
        }
    row["blockers"] = blockers(row)
    row["integrity_pass"] = not row["blockers"]
    return row


def build_report() -> dict[str, Any]:
    rows = [score_source(spec) for spec in SOURCES]
    ranked = sorted(
        rows,
        key=lambda row: (
            row["integrity_pass"],
            as_float(row.get("net_cents")) or -999999.0,
            as_float(row.get("coverage_pct")) or 0.0,
            as_float(row.get("settled")) or 0.0,
        ),
        reverse=True,
    )
    best_forward = next((row for row in ranked if row["mode"] != "diagnostic_plus_frozen" and (as_float(row.get("settled")) or 0) > 0), None)
    goldilocks = next((row for row in rows if row["name"] == "goldilocks_edge_repair"), {})
    bridge = next((row for row in rows if row["name"] == "false_conviction_fv_entry_bridge"), {})
    bridge_source_quality = (((bridge.get("diagnostic") or {}).get("source_quality") or {}).get("diagnostic_approved_only") or {})
    return {
        "purpose": "Family-level scorecard for the selected false-conviction direction.",
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_band": [MIN_COVERAGE, MAX_COVERAGE],
            "max_reconstructed_share": MAX_RECON_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "rows": rows,
        "ranked": ranked,
        "integrity_pass_count": sum(1 for row in rows if row["integrity_pass"]),
        "current_direction": [
            "Lead with early boundary/high-recross false-conviction filtering, not broad FV sharpening.",
            f"Best forward target-coverage evidence is {best_forward.get('name') if best_forward else None} with settled {best_forward.get('settled') if best_forward else None}, net {best_forward.get('net_cents') if best_forward else None}c, coverage {best_forward.get('coverage_pct') if best_forward else None}.",
            f"Goldilocks edge is promising only as a diagnostic: {((goldilocks.get('diagnostic') or {}).get('net_cents'))}c net at {((goldilocks.get('diagnostic') or {}).get('coverage_pct'))}% coverage, but frozen future rows are {goldilocks.get('settled')}.",
            f"FV-entry bridge approved-only diagnostic support is {bridge_source_quality.get('net_cents')}c net on {bridge_source_quality.get('settled')} settled rows; this is weaker than the all-source/reconstructed read and remains non-promotable.",
            "No false-conviction family candidate currently clears integrity gates.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 False-Conviction Family Scorecard",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Direction",
        "",
    ]
    for note in report.get("current_direction") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Candidates",
        "",
        "| candidate | mode | settled | W/L | coverage | net c | delta c | recon share | loss cushion | pass | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("ranked") or []:
        lines.append(
            f"| `{row.get('name')}` | `{row.get('mode')}` | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} | "
            f"{row.get('integrity_pass')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Diagnostic-Only Notes", ""])
    for row in report.get("ranked") or []:
        diagnostic = row.get("diagnostic")
        if not diagnostic:
            continue
        lines.append(
            f"- `{row.get('name')}` diagnostic: settled `{diagnostic.get('settled')}`, "
            f"net `{fmt(diagnostic.get('net_cents'))}c`, coverage `{fmt(diagnostic.get('coverage_pct'))}`, "
            f"delta `{fmt(diagnostic.get('delta_vs_target_cents'))}c`, recon share `{fmt(diagnostic.get('reconstructed_share'))}`."
        )
        if diagnostic.get("label"):
            lines.append(f"  - label: `{diagnostic.get('label')}`")
        if diagnostic.get("brier_delta_vs_raw") is not None or diagnostic.get("logloss_delta_vs_raw") is not None:
            lines.append(
                f"  - calibration deltas: brier `{fmt(diagnostic.get('brier_delta_vs_raw'))}`, "
                f"logloss `{fmt(diagnostic.get('logloss_delta_vs_raw'))}`"
            )
        source_quality = diagnostic.get("source_quality") or {}
        for label, source_row in source_quality.items():
            if not source_row:
                continue
            lines.append(
                f"  - source quality `{label}`: settled `{source_row.get('settled')}`, "
                f"net `{fmt(source_row.get('net_cents'))}c`, coverage `{fmt(source_row.get('coverage_pct'))}`, "
                f"recon share `{fmt(source_row.get('reconstructed_share'))}`, blockers `{', '.join(source_row.get('blockers') or []) or 'none'}`"
            )
        for warning in diagnostic.get("warnings") or []:
            lines.append(f"  - warning: {warning}")
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
