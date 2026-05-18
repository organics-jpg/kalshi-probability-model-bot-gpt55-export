from __future__ import annotations

import unittest

from project_os.graph import KIND_SYMBOLS, STATUS_COLORS, build_figure, collapse_graph
from project_os.models import ProjectEdge, ProjectNode


def node(
    node_id: str,
    *,
    kind: str = "candidate",
    family: str = "rv600",
    status: str = "needs_more_proof",
    evidence_level: str = "backtest",
    metrics: dict | None = None,
    blockers: list[str] | None = None,
    tags: list[str] | None = None,
    summary: str = "",
) -> ProjectNode:
    return ProjectNode(
        id=node_id,
        kind=kind,
        label=node_id.split(":")[-1],
        family=family,
        status=status,
        evidence_level=evidence_level,
        metrics=metrics or {},
        blockers=blockers or [],
        tags=tags or [],
        summary=summary,
    )


class ProjectOsGraphTests(unittest.TestCase):
    def test_health_and_sensitive_nodes_are_not_red_x_repair_markers(self) -> None:
        self.assertNotEqual(KIND_SYMBOLS["health_issue"], "x")
        self.assertNotEqual(KIND_SYMBOLS["secret"], "cross")
        self.assertNotIn(STATUS_COLORS["health_issue"].lower(), {"#f43f5e", "#ff4d6d"})

    def test_lod_collapse_keeps_decision_and_health_nodes_visible(self) -> None:
        important = [
            node("family:rv600", kind="family", status="active", evidence_level="metadata_only"),
            node("candidate:rv600:alpha", status="strong_candidate", evidence_level="forward_shadow"),
            node("health:rv600:issue", kind="health_issue", status="health_issue", evidence_level="diagnostic"),
            node("stats:rv600:latest", kind="stats", status="active", evidence_level="live_stats"),
        ]
        high_volume = [
            node(f"log:rv600:{idx}", kind="log", status="archived", evidence_level="metadata_only")
            for idx in range(500)
        ]
        graph_nodes, _graph_edges, collapsed = collapse_graph(important + high_volume, [], threshold=900, lod_threshold=10)
        visible_ids = {item.id for item in graph_nodes}

        self.assertTrue({item.id for item in important}.issubset(visible_ids))
        self.assertTrue(collapsed)
        self.assertTrue(any(item.kind == "artifact" and item.metrics.get("collapsed_children") for item in graph_nodes))

    def test_hover_text_adds_motifs_signature_and_primary_blocker(self) -> None:
        candidate = node(
            "candidate:rv600:edge_case",
            status="blocked",
            evidence_level="replay",
            metrics={"repeat_signature": "rv600 / fill quality / exit risk"},
            blockers=["avg_entry_below_10c"],
            tags=["fill_quality", "exit_risk"],
            summary="blocked replay report",
        )
        fig = build_figure([candidate], [], mode="vault atlas", obsidian=True)
        selectable_trace = fig.data[-1]
        hover = selectable_trace.hovertext[0]

        self.assertIn("<b>Motifs:</b>", hover)
        self.assertIn("<b>Signature:</b> rv600 / fill quality / exit risk", hover)
        self.assertIn("<b>Primary blocker:</b> avg_entry_below_10c", hover)

    def test_selected_neighborhood_edges_are_promoted_without_hiding_node_trace(self) -> None:
        nodes = [
            node("family:rv600", kind="family", status="active", evidence_level="metadata_only"),
            node("candidate:rv600:alpha", status="strong_candidate", evidence_level="forward_shadow"),
            node("report:rv600:alpha", kind="report", status="blocked", evidence_level="replay", blockers=["fill drift"]),
            node("stats:rv600:alpha", kind="stats", status="active", evidence_level="live_stats"),
        ]
        edges = [
            ProjectEdge("family:rv600", "candidate:rv600:alpha", "contains", evidence_level="metadata_only"),
            ProjectEdge("candidate:rv600:alpha", "report:rv600:alpha", "validates", evidence_level="replay"),
            ProjectEdge("candidate:rv600:alpha", "stats:rv600:alpha", "scores", evidence_level="live_stats"),
        ]
        fig = build_figure(nodes, edges, mode="vault atlas", obsidian=True, selected_id="candidate:rv600:alpha")

        self.assertEqual(tuple(fig.data[-1].customdata), tuple(item.id for item in nodes))
        self.assertIn("markers+text", fig.data[-1].mode)
        self.assertTrue(any(getattr(trace, "mode", "") == "lines" and trace.line.width == 3.0 for trace in fig.data[:-1]))
        self.assertLessEqual(len(fig.data), 14)

    def test_vault_family_regions_show_readable_labels_and_shapes(self) -> None:
        nodes = [
            node("family:rv600", kind="family", status="active", evidence_level="metadata_only"),
            node("candidate:rv600:alpha", status="worth_watching", evidence_level="forward_shadow"),
            node("candidate:rv600:beta", status="blocked", evidence_level="replay", blockers=["source quality"]),
            node("stats:rv600:latest", kind="stats", status="active", evidence_level="live_stats"),
        ]
        fig = build_figure(nodes, [], mode="vault atlas", obsidian=True, lens="failure")

        self.assertGreaterEqual(len(fig.layout.shapes), 2)
        family_label_trace = fig.data[-7]
        label_text = " ".join(str(item) for item in family_label_trace.text)
        self.assertIn("Rv600", label_text)
        self.assertIn("cand", label_text)

    def test_candidate_pnl_quality_controls_size_and_color(self) -> None:
        nodes = [
            node(
                "candidate:rv600:positive",
                status="worth_watching",
                evidence_level="forward_shadow",
                metrics={"net_pnl": 17528.0, "net_pnl_unit_hint": "cents"},
            ),
            node(
                "candidate:rv600:negative",
                status="rejected",
                evidence_level="forward_shadow",
                metrics={"net_pnl": -28864.0, "net_pnl_unit_hint": "cents"},
                blockers=["nonpositive_pnl"],
            ),
        ]
        fig = build_figure(nodes, [], mode="vault atlas", obsidian=True)
        trace = fig.data[-1]
        index_by_id = {node_id: index for index, node_id in enumerate(trace.customdata)}
        positive_index = index_by_id["candidate:rv600:positive"]
        negative_index = index_by_id["candidate:rv600:negative"]

        self.assertGreater(trace.marker.size[positive_index], trace.marker.size[negative_index])
        self.assertIn(trace.marker.color[positive_index], {"#22c55e", "#84cc16", "#a3e635"})
        self.assertIn(trace.marker.color[negative_index], {"#ef4444", "#b91c1c"})
        self.assertIn("Atlas quality:", trace.hovertext[positive_index])

    def test_candidate_atlas_size_and_color_use_weekly_pnl_first(self) -> None:
        nodes = [
            node(
                "candidate:rv600:raw_positive_weekly_bad",
                status="needs_more_proof",
                evidence_level="forward_shadow",
                metrics={
                    "net_pnl": 200000.0,
                    "net_pnl_unit_hint": "cents",
                    "pnl_7d_dollars": -1000.0,
                    "pnl_7d_display": "$-1000.00",
                },
            ),
            node(
                "candidate:rv600:raw_negative_weekly_good",
                status="needs_more_proof",
                evidence_level="forward_shadow",
                metrics={
                    "net_pnl": -100000.0,
                    "net_pnl_unit_hint": "cents",
                    "pnl_7d_dollars": 90.0,
                    "pnl_7d_display": "$90.00",
                },
            ),
        ]
        fig = build_figure(nodes, [], mode="vault atlas", obsidian=True)
        trace = fig.data[-1]
        index_by_id = {node_id: index for index, node_id in enumerate(trace.customdata)}
        weekly_bad_index = index_by_id["candidate:rv600:raw_positive_weekly_bad"]
        weekly_good_index = index_by_id["candidate:rv600:raw_negative_weekly_good"]

        self.assertGreater(trace.marker.size[weekly_good_index], trace.marker.size[weekly_bad_index])
        self.assertIn(trace.marker.color[weekly_good_index], {"#22c55e", "#84cc16", "#a3e635"})
        self.assertIn(trace.marker.color[weekly_bad_index], {"#ef4444", "#b91c1c"})
        self.assertIn("P&L/7d $90.00", trace.hovertext[weekly_good_index])
        self.assertIn("P&L/7d $-1000.00", trace.hovertext[weekly_bad_index])

    def test_promising_candidate_without_pnl_gets_watch_visual_hint(self) -> None:
        nodes = [
            node("candidate:rv600:promising", status="strong_candidate", evidence_level="forward_shadow"),
            node("candidate:rv600:unknown", status="unknown", evidence_level="metadata_only"),
        ]
        fig = build_figure(nodes, [], mode="vault atlas", obsidian=True)
        trace = fig.data[-1]
        index_by_id = {node_id: index for index, node_id in enumerate(trace.customdata)}
        promising_index = index_by_id["candidate:rv600:promising"]
        unknown_index = index_by_id["candidate:rv600:unknown"]

        self.assertGreater(trace.marker.size[promising_index], trace.marker.size[unknown_index])
        self.assertIn(trace.marker.color[promising_index], {"#84cc16", "#a3e635"})
        self.assertEqual(trace.marker.color[unknown_index], "#f59e0b")


if __name__ == "__main__":
    unittest.main()
