from __future__ import annotations

import argparse
from pathlib import Path

from project_os.rv_validation import (
    DEFAULT_OUTPUT_JSON,
    DEFAULT_OUTPUT_MD,
    build_rv_positive_validation,
    write_rv_positive_validation,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate positive-PnL RV candidate forward/OOS validation gates for Research OS."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.write:
        json_path, md_path, payload = write_rv_positive_validation(
            args.root,
            output_json=args.output_json,
            output_md=args.output_md,
            registry_path=args.registry,
        )
    else:
        payload = build_rv_positive_validation(args.root, registry_path=args.registry)
        json_path = args.output_json
        md_path = args.output_md
    print(f"positive_rv_candidate_count={payload['positive_rv_candidate_count']}")
    print(f"overall_decision={payload['overall_decision']}")
    for row in payload["candidate_results"]:
        print(
            f"{row['candidate_id']}: verdict={row['verdict']} "
            f"registry_pnl_7d={row.get('registry_pnl_7d_display') or 'n/a'} "
            f"source_pnl={row.get('registry_pnl_display') or 'n/a'} "
            f"forward_or_oos_pnl_cents={row['forward_or_oos_pnl_cents']} "
            f"blocking_gates={','.join(row['blocking_gates'])}"
        )
    print(f"output_json={json_path}")
    print(f"output_md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
