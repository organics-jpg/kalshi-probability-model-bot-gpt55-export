from __future__ import annotations

import re
from pathlib import Path
from typing import Any


FAMILY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("research_os", ("research_os", "project_os", "strategy_memory_decision_engine", "candidate_foundry")),
    ("dashboard_ui", ("living_analytics", "dashboard", "chrome_living_dashboard", "chrome_reference_art")),
    ("rv600", ("rv600",)),
    ("ou_mispricing", ("ou_", "ou-", "carr", "lopez", "mispricing")),
    ("v28_successor", ("v28_successor", "sidecar", "boundary", "live_pnl_policy", "v28_successor", "probe_v", "book_", "hazard_", "impulse_", "interval_", "cross_dataset_", "current_fv", "current_strategy", "candidate_tradeable", "codex_entry_", "arxiv_strategy")),
    ("particle_sim", ("particle_", "gauss45", "consensuslock", "residlock", "rvtermlock", "dynamic_particle", "side_safety", "side_consensus", "fixed_terminal", "next_second_particle", "rolling_vol", "rolling-vol")),
    ("ninety_touch", ("90_touch", "threshold_touch", "touch_entry", "ninety_touch")),
    ("truffle", ("truffle",)),
    ("live_v28", ("mushroom_v28", "phi_reward", "common_clock", "mushroom_v21", "codex_smoke_v28", "handoff_gpt55_v28")),
    ("legacy_live", ("entry_90", "live_87", "live_90", "liquidity_dwell")),
    ("infrastructure", ("launcher", "default", "setup_", "reset_", "score_bot_log", "research_ingestor", "research_pipeline", "research_optimizer", "project_tree", "copy_manifest", "trial_archives", "research_lab", "gauntlet")),
    ("strategy_research", ("physics_automation", "automation_runs", "strategy_priority", "strategy_projection", "strategy_stress", "strategy_remaining")),
)

EVIDENCE_RANK = {
    "unknown": 0,
    "metadata_only": 1,
    "diagnostic": 2,
    "backtest": 3,
    "replay": 4,
    "live_stats": 5,
    "forward_shadow": 6,
    "live_forward": 7,
}

STATUS_RANK = {
    "unknown": 0,
    "archived": 1,
    "diagnostic_only": 2,
    "rejected": 3,
    "needs_more_proof": 4,
    "blocked": 5,
    "active": 6,
    "worth_watching": 7,
    "strong_candidate": 8,
    "health_issue": 9,
}

STATUS_LABELS = {
    "strong_candidate": "Strong candidate",
    "worth_watching": "Worth watching",
    "needs_more_proof": "Needs more proof",
    "blocked": "Blocked",
    "rejected": "Rejected",
    "active": "Active",
    "archived": "Archived",
    "diagnostic_only": "Diagnostic only",
    "unknown": "Unknown",
    "health_issue": "Health notice",
}


def slugify(value: Any, fallback: str = "item") -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        text = fallback
    text = Path(text).name if "/" in text else text
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_.")
    return text[:180] or fallback


def infer_family(*values: Any) -> str:
    haystack = " ".join(str(v or "") for v in values).lower()
    for family, needles in FAMILY_RULES:
        if any(needle in haystack for needle in needles):
            return family
    return "unclassified"


def best_evidence(current: str, candidate: str) -> str:
    return candidate if EVIDENCE_RANK.get(candidate, 0) > EVIDENCE_RANK.get(current, 0) else current


def best_status(current: str, candidate: str) -> str:
    return candidate if STATUS_RANK.get(candidate, 0) > STATUS_RANK.get(current, 0) else current


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, "Unknown")


def evidence_from_name(name: str) -> str:
    lowered = name.lower()
    if "live_forward" in lowered or "forward_packet" in lowered:
        return "live_forward"
    if "shadow" in lowered or "oos" in lowered or "forward" in lowered:
        return "forward_shadow"
    if "live" in lowered or "stats" in lowered:
        return "live_stats"
    if "replay" in lowered:
        return "replay"
    if "backtest" in lowered or "sweep" in lowered:
        return "backtest"
    if "probe" in lowered or "diagnostic" in lowered or "audit" in lowered:
        return "diagnostic"
    return "metadata_only"
