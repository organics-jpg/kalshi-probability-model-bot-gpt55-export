from __future__ import annotations

from pathlib import Path

from project_os.candidate_readiness import write_candidate_readiness
from project_os.registry import build_registry


def main() -> int:
    root = Path(".").resolve()
    registry = build_registry(root, write=True)
    json_path, md_path, payload = write_candidate_readiness(registry, root)
    refreshed = build_registry(root, write=True)
    print(f"candidate_count={payload['summary']['candidate_count']}")
    print(f"controlled_live_test_ready_count={payload['summary']['controlled_live_test_ready_count']}")
    print(f"live_shadow_ready_count={payload['summary']['live_shadow_ready_count']}")
    print(f"registry_nodes={len(refreshed.nodes)}")
    print(f"registry_edges={len(refreshed.edges)}")
    print(f"registry_issues={len(refreshed.issues)}")
    print(f"json={json_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
