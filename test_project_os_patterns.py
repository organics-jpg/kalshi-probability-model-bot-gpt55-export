from __future__ import annotations

import unittest

from project_os.models import ProjectEdge, ProjectNode, ProjectRegistry
from project_os.patterns import (
    candidate_signature,
    candidate_visual_quality,
    failure_motif_rows,
    family_gap_rows,
    lineage_gap_rows,
    nearest_prior_rows,
    node_pattern_tags,
    normalized_metric_snapshot,
    positive_blocked_rows,
    research_move_cards,
    signature_similarity,
)


def registry(nodes: list[ProjectNode], edges: list[ProjectEdge] | None = None) -> ProjectRegistry:
    return ProjectRegistry(generated_at_utc="2026-05-18T00:00:00Z", root="fixture", nodes=nodes, edges=edges or [])


class ProjectOsPatternTests(unittest.TestCase):
    def test_metric_normalization_keeps_ambiguous_pnl_low_confidence(self) -> None:
        node = ProjectNode(
            id="report:rv600:ambiguous",
            kind="report",
            label="RV600 ambiguous replay",
            family="rv600",
            evidence_level="replay",
            metrics={"gross_pnl": 99.0, "net_pnl": "12.5", "entries": "31", "markets": 4, "win_rate": 0.75},
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_key"], "net_pnl")
        self.assertEqual(snapshot["pnl_unit"], "ambiguous")
        self.assertEqual(snapshot["pnl_confidence"], "low")
        self.assertEqual(snapshot["entries"], 31)
        self.assertEqual(snapshot["markets"], 4)
        self.assertEqual(snapshot["win_rate"], 75.0)
        self.assertTrue(any("ambiguous" in warning for warning in snapshot["metric_warnings"]))

    def test_metric_normalization_converts_known_cents(self) -> None:
        node = ProjectNode(
            id="report:rv600:cents",
            kind="report",
            label="RV600 cents",
            family="rv600",
            metrics={"selected_pnl_cents": 350, "entry_count": 9},
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_unit"], "cents")
        self.assertEqual(snapshot["pnl_confidence"], "high")
        self.assertEqual(snapshot["pnl_value"], 3.5)
        self.assertIn("350c", snapshot["pnl_display"])

    def test_metric_snapshot_separates_source_pnl_from_weekly_pnl(self) -> None:
        node = ProjectNode(
            id="candidate:particle:weekly",
            kind="candidate",
            label="weekly standardized",
            family="particle_sim",
            metrics={
                "net_pnl": 9600.0,
                "net_pnl_unit_hint": "cents",
                "pnl_7d_dollars": 672.0,
                "pnl_7d_display": "$672.00",
                "pnl_observed_window_days": 1.0,
                "pnl_observed_window_confidence": "assumed",
                "pnl_standardization_status": "standardized",
            },
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_key"], "net_pnl")
        self.assertAlmostEqual(snapshot["pnl_value"], 96.0)
        self.assertAlmostEqual(snapshot["pnl_7d_value"], 672.0)
        self.assertEqual(snapshot["pnl_7d_display"], "$672.00")
        self.assertEqual(snapshot["pnl_window_display"], "1d (assumed)")

    def test_metric_normalization_honors_adapter_source_unit_hint(self) -> None:
        node = ProjectNode(
            id="report:rv600:adapter_cents",
            kind="report",
            label="RV600 adapter cents",
            family="rv600",
            metrics={"net_pnl": 350, "net_pnl_source_key": "selected_pnl_cents", "net_pnl_unit_hint": "cents"},
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_unit"], "cents")
        self.assertEqual(snapshot["pnl_value"], 3.5)

    def test_metric_normalization_uses_candidate_pnl_not_v28_comparison_pnl(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:policy",
            kind="candidate",
            label="policy",
            family="v28_successor",
            metrics={
                "net_pnl": 70.0,
                "net_pnl_unit_hint": "cents",
                "primary_v28_net_pnl_cents": -692.3,
                "primary_delta_vs_v28_cents": 762.3,
            },
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_key"], "net_pnl")
        self.assertAlmostEqual(snapshot["pnl_value"], 0.70)

    def test_metric_normalization_uses_actual_markets_not_shortfall_fields(self) -> None:
        node = ProjectNode(
            id="candidate:v28_successor:micro",
            kind="candidate",
            label="micro",
            family="v28_successor",
            metrics={
                "forward_gate_estimated_additional_markets_needed": 30,
                "forward_gate_market_shortfall": 30,
                "forward_gate_required_markets": 40,
                "markets": 10,
            },
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["markets"], 10)

    def test_metric_normalization_marks_empty_decision_pnl_explicitly(self) -> None:
        node = ProjectNode(
            id="candidate:rv600:no_source",
            kind="candidate",
            label="RV600 no source",
            family="rv600",
            metrics={"pnl_status": "no_source_pnl", "pnl_missing_reason": "locked plan has no realized P&L"},
        )

        snapshot = normalized_metric_snapshot(node)

        self.assertEqual(snapshot["pnl_display"], "n/a")
        self.assertEqual(snapshot["pnl_confidence"], "none")
        self.assertIn("locked plan has no realized P&L", snapshot["metric_warnings"])

    def test_candidate_visual_quality_scores_positive_and_negative_pnl(self) -> None:
        positive = ProjectNode(
            id="candidate:rv600:positive",
            kind="candidate",
            label="positive",
            family="rv600",
            status="worth_watching",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 17528.0, "net_pnl_unit_hint": "cents"},
        )
        negative = ProjectNode(
            id="candidate:rv600:negative",
            kind="candidate",
            label="negative",
            family="rv600",
            status="rejected",
            evidence_level="forward_shadow",
            metrics={"net_pnl": -28864.0, "net_pnl_unit_hint": "cents"},
        )

        positive_quality = candidate_visual_quality(positive)
        negative_quality = candidate_visual_quality(negative)

        self.assertGreater(positive_quality["score"], 0)
        self.assertLess(negative_quality["score"], 0)
        self.assertIn(positive_quality["label"], {"positive", "excellent"})
        self.assertIn(negative_quality["label"], {"bad", "awful"})

    def test_candidate_visual_quality_prefers_weekly_pnl_over_source_pnl(self) -> None:
        raw_positive_weekly_negative = ProjectNode(
            id="candidate:rv600:raw_positive_weekly_negative",
            kind="candidate",
            label="raw positive weekly negative",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            metrics={
                "net_pnl": 200000.0,
                "net_pnl_unit_hint": "cents",
                "pnl_7d_dollars": -1000.0,
                "pnl_7d_display": "$-1000.00",
            },
        )
        raw_negative_weekly_positive = ProjectNode(
            id="candidate:rv600:raw_negative_weekly_positive",
            kind="candidate",
            label="raw negative weekly positive",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            metrics={
                "net_pnl": -100000.0,
                "net_pnl_unit_hint": "cents",
                "pnl_7d_dollars": 90.0,
                "pnl_7d_display": "$90.00",
            },
        )

        negative_quality = candidate_visual_quality(raw_positive_weekly_negative)
        positive_quality = candidate_visual_quality(raw_negative_weekly_positive)

        self.assertLess(negative_quality["score"], 0)
        self.assertGreater(positive_quality["score"], 0)
        self.assertGreater(positive_quality["score"], negative_quality["score"])
        self.assertEqual(negative_quality["pnl_7d_display"], "$-1000.00")
        self.assertEqual(positive_quality["pnl_7d_display"], "$90.00")

    def test_candidate_visual_quality_penalizes_positive_blocked_trap(self) -> None:
        open_watch = ProjectNode(
            id="candidate:rv600:watch",
            kind="candidate",
            label="watch",
            family="rv600",
            status="worth_watching",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 339.0, "net_pnl_unit_hint": "cents"},
        )
        blocked = ProjectNode(
            id="candidate:rv600:blocked",
            kind="candidate",
            label="blocked",
            family="rv600",
            status="blocked",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 339.0, "net_pnl_unit_hint": "cents"},
            blockers=["does_not_beat_matched_v28_by_20pct"],
        )

        open_quality = candidate_visual_quality(open_watch)
        blocked_quality = candidate_visual_quality(blocked)

        self.assertGreater(open_quality["score"], blocked_quality["score"])
        self.assertTrue(blocked_quality["blocked_positive"])
        self.assertIn(blocked_quality["label"], {"weak", "bad", "awful"})

    def test_candidate_visual_quality_dampens_ambiguous_raw_pnl(self) -> None:
        high_confidence = ProjectNode(
            id="candidate:rv600:net",
            kind="candidate",
            label="net",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 1200.0, "net_pnl_unit_hint": "cents"},
        )
        ambiguous = ProjectNode(
            id="candidate:rv600:raw",
            kind="candidate",
            label="raw",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 12.0},
        )

        self.assertGreater(candidate_visual_quality(high_confidence)["score"], candidate_visual_quality(ambiguous)["score"])
        self.assertEqual(candidate_visual_quality(ambiguous)["pnl_confidence"], "low")

    def test_candidate_visual_quality_is_deterministic_for_missing_pnl(self) -> None:
        candidate = ProjectNode(
            id="candidate:rv600:unknown",
            kind="candidate",
            label="unknown",
            family="rv600",
            status="unknown",
            evidence_level="metadata_only",
        )

        first = candidate_visual_quality(candidate)
        second = candidate_visual_quality(candidate)

        self.assertEqual(first, second)
        self.assertFalse(first["has_pnl"])
        self.assertEqual(first["label"], "neutral")

    def test_motif_tags_include_evidence_and_blocker_motifs(self) -> None:
        node = ProjectNode(
            id="report:live_v28:phi",
            kind="report",
            label="common clock phi reward lifecycle exit",
            family="live_v28",
            status="blocked",
            evidence_level="forward_shadow",
            blockers=["source_quality stale book and does_not_beat_matched_v28_by_20pct"],
            metrics={"net_pnl_total_dollars": 14.0},
        )

        tags = node_pattern_tags(node)

        self.assertIn("forward_oos", tags)
        self.assertIn("common_clock", tags)
        self.assertIn("phi_memory", tags)
        self.assertIn("source_quality", tags)
        self.assertIn("baseline_compare", tags)

    def test_signature_is_deterministic_and_similarity_detects_siblings(self) -> None:
        first = ProjectNode(
            id="candidate:rv600:a",
            kind="candidate",
            label="RV600 locked forward shadow breadth guard",
            family="rv600",
            status="blocked",
            evidence_level="forward_shadow",
            blockers=["positive_markets_below_60pct"],
            metrics={"selected_pnl_cents": 140},
        )
        second = ProjectNode(
            id="candidate:rv600:b",
            kind="candidate",
            label="RV600 locked forward shadow breadth guard v2",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            blockers=["positive_markets_below_60pct"],
            metrics={"selected_pnl_cents": 240},
        )
        other = ProjectNode(
            id="report:ou:c",
            kind="report",
            label="OU mispricing backtest diagnostic",
            family="ou_mispricing",
            evidence_level="backtest",
            metrics={"gross_pnl": 99},
        )

        self.assertEqual(candidate_signature(first), candidate_signature(first))
        self.assertGreater(signature_similarity(first, second), 0.75)
        self.assertLess(signature_similarity(first, other), 0.45)

    def test_nearest_prior_rows_reports_repeat_warning(self) -> None:
        older = ProjectNode(
            id="candidate:rv600:old",
            kind="candidate",
            label="RV600 locked forward shadow breadth guard",
            family="rv600",
            status="blocked",
            evidence_level="forward_shadow",
            updated_at_utc="2026-05-17T00:00:00Z",
            blockers=["positive_markets_below_60pct"],
            metrics={"selected_pnl_cents": 140},
        )
        newer = ProjectNode(
            id="candidate:rv600:new",
            kind="candidate",
            label="RV600 locked forward shadow breadth guard v2",
            family="rv600",
            status="needs_more_proof",
            evidence_level="forward_shadow",
            updated_at_utc="2026-05-18T00:00:00Z",
            blockers=["positive_markets_below_60pct"],
            metrics={"selected_pnl_cents": 240},
        )

        rows = nearest_prior_rows(registry([older, newer]))
        row = next(item for item in rows if item["Label"] == newer.label)

        self.assertIn("RV600 locked", row["Nearest Prior"])
        self.assertGreaterEqual(row["Similarity"], 0.75)
        self.assertIn("repeat", row["Repeat Warning"].lower())

    def test_positive_blocked_rows_treats_positive_pnl_as_trap(self) -> None:
        node = ProjectNode(
            id="report:v28:blocked",
            kind="report",
            label="v28 successor blocked positive forward shadow",
            family="v28_successor",
            status="blocked",
            evidence_level="forward_shadow",
            metrics={"net_pnl": 1739.7, "markets": 24, "entries": 48},
            blockers=["does_not_beat_matched_v28_by_20pct"],
        )

        rows = positive_blocked_rows(registry([node]))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Label"], node.label)
        self.assertIn("Blocked", rows[0]["Status"])
        self.assertIn("cannot", rows[0]["Why It Is Blocked"])
        self.assertIn("Reconcile", rows[0]["Do Next"])

    def test_positive_blocked_rows_reports_weekly_pnl_and_source_window(self) -> None:
        short_window = ProjectNode(
            id="candidate:rv600:short",
            kind="candidate",
            label="short-window trap",
            family="rv600",
            status="blocked",
            evidence_level="forward_shadow",
            blockers=["underpowered_markets"],
            metrics={
                "net_pnl": 100.0,
                "net_pnl_unit_hint": "cents",
                "pnl_7d_dollars": 200.0,
                "pnl_7d_display": "$200.00",
                "pnl_observed_window_days": 0.035,
                "pnl_observed_window_confidence": "assumed",
            },
        )
        long_window = ProjectNode(
            id="candidate:rv600:long",
            kind="candidate",
            label="long-window trap",
            family="rv600",
            status="blocked",
            evidence_level="forward_shadow",
            blockers=["underpowered_markets"],
            metrics={
                "net_pnl": 5000.0,
                "net_pnl_unit_hint": "cents",
                "pnl_7d_dollars": 50.0,
                "pnl_7d_display": "$50.00",
                "pnl_observed_window_days": 7.0,
                "pnl_observed_window_confidence": "exact",
            },
        )

        rows = positive_blocked_rows(registry([long_window, short_window]))

        self.assertEqual(rows[0]["Label"], "short-window trap")
        self.assertEqual(rows[0]["P&L/7d"], "$200.00")
        self.assertEqual(rows[0]["P&L"], "100c (~$1.00)")
        self.assertIn("assumed", rows[0]["Window"])

    def test_failure_motif_rows_normalizes_blockers(self) -> None:
        nodes = [
            ProjectNode(
                id="report:v28:a",
                kind="report",
                label="blocked a",
                family="v28_successor",
                status="blocked",
                blockers=["fewer_than_25_entries and source_quality"],
            ),
            ProjectNode(
                id="report:v28:b",
                kind="report",
                label="blocked b",
                family="v28_successor",
                status="blocked",
                blockers=["fewer than 25 entries"],
            ),
        ]

        rows = failure_motif_rows(registry(nodes))
        motif_counts = {(row["Family"], row["Failure Motif"]): row["Count"] for row in rows}

        self.assertEqual(motif_counts[("v28_successor", "fewer_than_25_entries")], 2)
        self.assertEqual(motif_counts[("v28_successor", "source_quality")], 1)

    def test_family_gap_flags_and_lineage_priority(self) -> None:
        nodes = [
            ProjectNode(
                id="report:ou:diagnostic",
                kind="report",
                label="OU positive diagnostic",
                family="ou_mispricing",
                status="diagnostic_only",
                evidence_level="backtest",
                metrics={"net_pnl": 11.0},
            ),
            ProjectNode(
                id="report:ou:blocked",
                kind="report",
                label="OU blocked sample",
                family="ou_mispricing",
                status="blocked",
                evidence_level="backtest",
                blockers=["underpowered_markets"],
            ),
        ]

        gaps = family_gap_rows(registry(nodes))
        ou_gap = next(row for row in gaps if row["Family"] == "ou_mispricing")
        lineage = lineage_gap_rows(registry(nodes))

        self.assertIn("NO_CANDIDATE", ou_gap["Gap Flags"])
        self.assertIn("NO_FORWARD_EVIDENCE", ou_gap["Gap Flags"])
        self.assertIn("POSITIVE_DIAGNOSTIC_NO_FREEZE", ou_gap["Gap Flags"])
        self.assertEqual(next(row for row in lineage if row["Label"] == "OU blocked sample")["Priority"], "High")

    def test_research_move_cards_assign_lanes(self) -> None:
        nodes = [
            ProjectNode(
                id="report:v28:trap",
                kind="report",
                label="v28 positive blocked trap",
                family="v28_successor",
                status="blocked",
                evidence_level="forward_shadow",
                blockers=["does_not_beat_matched_v28_by_20pct"],
                metrics={"net_pnl_total_dollars": 12.0},
            ),
            ProjectNode(
                id="candidate:rv600:watch",
                kind="candidate",
                label="RV600 forward watch candidate",
                family="rv600",
                status="worth_watching",
                evidence_level="forward_shadow",
                metrics={"net_pnl_total_dollars": 3.0},
            ),
            ProjectNode(
                id="report:ou:diag",
                kind="report",
                label="OU diagnostic positive",
                family="ou_mispricing",
                status="diagnostic_only",
                evidence_level="backtest",
                metrics={"net_pnl": 5.0},
            ),
        ]

        lanes = {card["Lane"] for card in research_move_cards(registry(nodes))}

        self.assertIn("Do Not Repeat", lanes)
        self.assertIn("Test Next", lanes)
        self.assertIn("Frontier", lanes)


if __name__ == "__main__":
    unittest.main()
