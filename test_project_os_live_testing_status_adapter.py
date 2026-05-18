from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_os.adapters.live_testing_status_adapter import scan
from project_os.curation import Overrides
from project_os.registry import build_registry


class ProjectOSLiveTestingStatusAdapterTests(unittest.TestCase):
    def test_live_status_marks_candidate_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status_path = root / "logs" / "project_os" / "live_testing_status_latest.json"
            status_path.parent.mkdir(parents=True)
            status_path.write_text(
                json.dumps(
                    {
                        "schema": "project_os_live_testing_status_v1",
                        "generated_at_utc": "2026-05-18T12:00:00Z",
                        "live_tests": [
                            {
                                "node_id": "candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic",
                                "candidate_id": "v28s_boundary_monotonic_time_safe_v001",
                                "label": "v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic",
                                "family": "v28_successor",
                                "mode": "live_order",
                                "launch_status": "running",
                                "pid": 1234,
                                "position_size": 2,
                                "no_max_drawdown": True,
                            }
                        ],
                        "shadow_tests": [],
                    }
                ),
                encoding="utf-8",
            )

            out = scan(root, Overrides())

        self.assertEqual(out.summary["status_rows"], 1)
        self.assertEqual(out.nodes[0].status, "active")
        self.assertTrue(out.nodes[0].metrics["live_test_active"])
        self.assertEqual(out.nodes[0].metrics["live_test_position_size"], 2)

    def test_live_status_wins_after_readiness_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "logs" / "project_os"
            report_dir.mkdir(parents=True)
            node_id = "candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic"
            (report_dir / "candidate_readiness_reevaluation_latest.json").write_text(
                json.dumps(
                    {
                        "schema": "project_os_candidate_readiness_reevaluation_v1",
                        "candidates": [
                            {
                                "node_id": node_id,
                                "label": "v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic",
                                "family": "v28_successor",
                                "status_update": "strong_candidate",
                                "evidence_level": "forward_shadow",
                                "readiness_level": "controlled_live_test_ready",
                                "readiness_score": 100,
                                "metrics_update": {"controlled_live_test_ready": True},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (report_dir / "live_testing_status_latest.json").write_text(
                json.dumps(
                    {
                        "schema": "project_os_live_testing_status_v1",
                        "live_tests": [
                            {
                                "node_id": node_id,
                                "label": "v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic",
                                "family": "v28_successor",
                                "mode": "live_order",
                                "launch_status": "running",
                                "position_size": 2,
                                "no_max_drawdown": True,
                            }
                        ],
                        "shadow_tests": [],
                    }
                ),
                encoding="utf-8",
            )

            registry = build_registry(root, write=False)
            node = next(item for item in registry.nodes if item.id == node_id)

        self.assertEqual(node.status, "active")
        self.assertTrue(node.metrics["controlled_live_test_ready"])
        self.assertTrue(node.metrics["live_test_active"])


if __name__ == "__main__":
    unittest.main()
