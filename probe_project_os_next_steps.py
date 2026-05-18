from __future__ import annotations

import argparse
from pathlib import Path

from project_os.next_steps import OUTCOME_JSON, OUTCOME_MD, build_next_step_outcomes, write_next_step_outcomes
from project_os.registry import REGISTRY_DIR, LATEST_NAME, build_registry, load_registry


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review Research OS candidate/family next steps against local atlas evidence.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-registry", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    registry_path = args.registry
    if args.refresh_registry:
        registry = build_registry(root, write=True)
        registry_path = root / REGISTRY_DIR / LATEST_NAME
    else:
        registry = load_registry(registry_path or root / REGISTRY_DIR / LATEST_NAME)
    if args.write:
        json_path, md_path, payload = write_next_step_outcomes(root, registry_path=registry_path)
    else:
        payload = build_next_step_outcomes(registry)
        json_path = root / OUTCOME_JSON
        md_path = root / OUTCOME_MD
    counts = payload.get("counts") or {}
    outcomes = list(payload.get("outcomes") or [])
    print(f"outcomes={len(outcomes)}")
    print(f"completed={counts.get('completed', 0)} blocked={counts.get('blocked', 0)} pending={counts.get('pending', 0)}")
    for outcome in outcomes:
        if outcome.get("kind") == "candidate":
            print(
                f"{outcome.get('label')}: {outcome.get('completion_status')} "
                f"{outcome.get('status')} -> {outcome.get('next_action')}"
            )
    print(f"output_json={json_path}")
    print(f"output_md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
