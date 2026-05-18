from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "particle_research" / "reports"
JSON_OUT = OUT_DIR / "particle_adapter_readiness_latest.json"
MD_OUT = OUT_DIR / "particle_adapter_readiness_latest.md"

CORE_FIELDS = {
    "market_ticker",
    "decision_ts_utc",
    "recv_ts_utc",
    "strike",
    "spot",
    "yes_ask_cents",
    "no_ask_cents",
    "fee_cents",
    "fill_prob",
    "settlement_price",
}

PROBABILITY_FIELDS = {
    "particle_p_yes",
    "brownian_p_yes",
    "market_p_yes",
    "current_calibrated_p_yes",
}

ALIASES = {
    "market": "market_ticker",
    "ticker": "market_ticker",
    "entry_ts": "decision_ts_utc",
    "ts": "decision_ts_utc",
    "timestamp": "decision_ts_utc",
    "strike_price": "strike",
    "btc_price": "spot",
    "spot_price": "spot",
    "yes_ask": "yes_ask_cents",
    "no_ask": "no_ask_cents",
    "fee": "fee_cents",
    "fees": "fee_cents",
    "p28": "current_calibrated_p_yes",
    "p_cal": "current_calibrated_p_yes",
    "p_calibrated": "current_calibrated_p_yes",
    "brownian_terminal": "brownian_p_yes",
    "brownian_terminal_p": "brownian_p_yes",
    "market_p": "market_p_yes",
    "market_prob": "market_p_yes",
    "settlement": "settlement_price",
    "settle_price": "settlement_price",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for path in iter_artifact_paths():
        sample = sample_artifact(path)
        if not sample:
            continue
        normalized = normalize_keys(sample.keys())
        matched_core = sorted(CORE_FIELDS & normalized)
        matched_probs = sorted(PROBABILITY_FIELDS & normalized)
        score = len(matched_core) + len(matched_probs)
        candidate_like = bool({"market_ticker", "decision_ts_utc"} & normalized) or bool(
            {"p_cal", "p28", "brownian_terminal", "depth_ratio"} & set(sample.keys())
        )
        if score or candidate_like:
            artifacts.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "suffix": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                    "sample_keys": sorted(str(k) for k in sample.keys())[:80],
                    "normalized_fields": sorted(normalized),
                    "matched_core": matched_core,
                    "matched_probability": matched_probs,
                    "missing_core": sorted(CORE_FIELDS - normalized),
                    "missing_probability": sorted(PROBABILITY_FIELDS - normalized),
                    "readiness_score": score,
                    "adapter_ready": CORE_FIELDS <= normalized and PROBABILITY_FIELDS <= normalized,
                }
            )

    artifacts.sort(key=lambda row: (row["adapter_ready"], row["readiness_score"], row["size_bytes"]), reverse=True)
    summary = {
        "artifact_count": len(artifacts),
        "adapter_ready_count": sum(1 for row in artifacts if row["adapter_ready"]),
        "top_artifacts": artifacts[:30],
        "field_coverage": field_coverage(artifacts),
        "conclusion": conclusion(artifacts),
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    MD_OUT.write_text(markdown(summary), encoding="utf-8")
    print(f"particle adapter readiness complete")
    print(f"adapter_ready_count={summary['adapter_ready_count']}")
    print(f"artifact_count={summary['artifact_count']}")
    print(f"report={MD_OUT}")
    return 0


def iter_artifact_paths() -> Iterable[Path]:
    roots = [ROOT / "logs", ROOT / "stats", ROOT / "state"]
    suffixes = {".json", ".jsonl", ".ndjson", ".csv"}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if "particle_research" in path.parts:
                continue
            if path.stat().st_size > 20_000_000:
                continue
            yield path


def sample_artifact(path: Path) -> Mapping[str, Any]:
    try:
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                row = next(reader, None)
                return row or {}
        if path.suffix.lower() in {".jsonl", ".ndjson"}:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        value = json.loads(line)
                        return flatten_one(value)
                return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return flatten_one(value)
    except Exception as exc:
        return {"_read_error": str(exc)}


def flatten_one(value: Any) -> Mapping[str, Any]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, Mapping):
                return item
        return {}
    if isinstance(value, Mapping):
        flattened = dict(value)
        for nested_key in ("rows", "candidates", "trades", "records", "data", "items"):
            nested = value.get(nested_key)
            if isinstance(nested, list):
                for item in nested:
                    if isinstance(item, Mapping):
                        flattened.update({f"{nested_key}.{k}": v for k, v in item.items()})
                        flattened.update(item)
                        break
        return flattened
    return {}


def normalize_keys(keys: Iterable[str]) -> set[str]:
    out = set()
    for key in keys:
        k = str(key).strip()
        bare = k.split(".")[-1]
        out.add(k)
        out.add(bare)
        out.add(ALIASES.get(k, k))
        out.add(ALIASES.get(bare, bare))
    return out


def field_coverage(artifacts: list[Mapping[str, Any]]) -> Mapping[str, int]:
    counts: Counter[str] = Counter()
    for row in artifacts:
        for field in row["normalized_fields"]:
            if field in CORE_FIELDS or field in PROBABILITY_FIELDS:
                counts[field] += 1
    return dict(sorted(counts.items()))


def conclusion(artifacts: list[Mapping[str, Any]]) -> str:
    ready = [row for row in artifacts if row["adapter_ready"]]
    if ready:
        return "At least one artifact appears adapter-ready for strict particle replay."
    if not artifacts:
        return "No candidate-like artifacts found in logs/stats/state."
    best = artifacts[0]
    missing = best["missing_core"] + best["missing_probability"]
    return (
        "No existing artifact has every required strict replay field. "
        f"Best candidate is {best['path']} but it is missing: {', '.join(missing)}."
    )


def markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Particle Adapter Readiness",
        "",
        f"- artifact_count: {summary['artifact_count']}",
        f"- adapter_ready_count: {summary['adapter_ready_count']}",
        f"- conclusion: {summary['conclusion']}",
        "",
        "## Top Artifacts",
        "",
        "| score | ready | path | missing core | missing probability |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in summary["top_artifacts"][:20]:
        lines.append(
            "| {score} | {ready} | `{path}` | {core} | {prob} |".format(
                score=row["readiness_score"],
                ready=row["adapter_ready"],
                path=row["path"],
                core=", ".join(row["missing_core"]) or "-",
                prob=", ".join(row["missing_probability"]) or "-",
            )
        )
    lines.extend(["", "## Field Coverage", ""])
    for field, count in summary["field_coverage"].items():
        lines.append(f"- `{field}`: {count}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

