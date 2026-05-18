from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from research_particle.v28_event_adapter import adapt_v28_events_file


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "particle_research" / "v28_event_contexts"
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only adapter from v28 execution_events.ndjson to particle candidate contexts."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--stem", default="v28_event_contexts_latest")
    parser.add_argument("--annualized-vol", default=None, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / f"{args.stem}.ndjson"
    issue_path = OUT_DIR / f"{args.stem}_issues.ndjson"
    adapted_count, issue_count = adapt_v28_events_file(
        args.input,
        output_path,
        issue_path,
        annualized_vol=args.annualized_vol,
    )
    issue_reasons = Counter()
    if issue_path.exists():
        with issue_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    issue_reasons[json.loads(line)["reason"]] += 1
    report = {
        "input": str(args.input),
        "output": str(output_path),
        "issues": str(issue_path),
        "adapted_count": adapted_count,
        "issue_count": issue_count,
        "issue_reasons": dict(issue_reasons),
        "usable_for_strict_collection": adapted_count > 0,
    }
    report_json = REPORT_DIR / f"{args.stem}.json"
    report_md = REPORT_DIR / f"{args.stem}.md"
    report_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    report_md.write_text(markdown(report), encoding="utf-8")
    print("particle v28 event context adapter complete")
    print(f"adapted_count={adapted_count}")
    print(f"issue_count={issue_count}")
    print(f"report={report_md}")
    return 0


def markdown(report: dict) -> str:
    lines = [
        "# Particle v28 Event Context Adapter",
        "",
        f"- input: `{report['input']}`",
        f"- output: `{report['output']}`",
        f"- issues: `{report['issues']}`",
        f"- adapted_count: {report['adapted_count']}",
        f"- issue_count: {report['issue_count']}",
        f"- usable_for_strict_collection: {report['usable_for_strict_collection']}",
        "",
        "## Issue Reasons",
        "",
    ]
    for reason, count in sorted(report["issue_reasons"].items()):
        lines.append(f"- `{reason}`: {count}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

