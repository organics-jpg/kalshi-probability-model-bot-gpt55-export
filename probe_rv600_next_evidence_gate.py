from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from research_particle.v28_event_sources import describe_execution_event_source, latest_execution_events_path


DEFAULT_FAILURE_PATTERN_JSON = Path("logs/particle_research/reports/rv600_failure_pattern_audit_latest.json")
DEFAULT_OBJECTIVE_JSON = Path("logs/particle_research/reports/rv600_objective_state_latest.json")
DEFAULT_LOCKED_PLAN_DIR = Path("logs/particle_research/locked_oos_plans")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_next_evidence_gate_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_next_evidence_gate_latest.md")
DEFAULT_KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
BTC15M_SERIES = "KXBTC15M"
BTC15M_TICKER_PREFIX = "KXBTC15M-"


@dataclass(frozen=True)
class RequirementRow:
    status: str
    requirement: str
    evidence: str
    next_action: str


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_locked_plan(path: Path) -> Path | None:
    if path.is_file():
        return path
    if not path.exists():
        return None
    plans = sorted(
        (
            candidate
            for candidate in path.glob("*_locked_plan.json")
            if _is_rv600_locked_plan(candidate)
        ),
        key=lambda item: (_plan_generated_utc(item) or datetime.fromtimestamp(item.stat().st_mtime, timezone.utc)),
    )
    return plans[-1] if plans else None


def _is_rv600_locked_plan(path: Path) -> bool:
    plan = _load_json(path)
    candidate = plan.get("candidate") or {}
    plan_id = str(plan.get("plan_id") or "")
    variant = str(candidate.get("variant") or "")
    return (
        plan.get("research_only") is True
        and (plan_id.startswith("RV600") or variant.startswith(("rv600", "v28_")))
    )


def _plan_generated_utc(path: Path) -> datetime | None:
    return _parse_dt(str(_load_json(path).get("generated_utc") or ""))


def _latest_execution_events(workspace: Path) -> Path | None:
    return latest_execution_events_path(workspace)


def _status(ok: bool) -> str:
    return "pass" if ok else "fail"


def _row(status: str, requirement: str, evidence: str, next_action: str) -> RequirementRow:
    return RequirementRow(status, requirement, evidence, next_action)


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _get_env_value(key: str) -> str:
    value = os.getenv(key, "").strip()
    if value:
        return value
    env_path = Path(".env")
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        name, raw_value = raw.split("=", 1)
        if name.strip() == key:
            return raw_value.strip().strip('"').strip("'")
    return ""


def _load_btc15m_markets(base_url: str, *, limit: int, timeout_seconds: float) -> tuple[list[dict[str, Any]], str]:
    query_params = [
        {"series_ticker": BTC15M_SERIES, "status": "open", "limit": int(limit)},
        {"series_ticker": BTC15M_SERIES, "limit": int(limit)},
    ]
    markets_by_ticker: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for params in query_params:
        query = urllib.parse.urlencode(params)
        url = f"{base_url.rstrip('/')}/markets?{query}"
        request = urllib.request.Request(url, headers={"User-Agent": "rv600-next-evidence-gate/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=max(1.0, timeout_seconds)) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            errors.append(f"http_error={exc.code}; params={params}; body={body[:160]}")
            continue
        except Exception as exc:  # noqa: BLE001
            errors.append(f"request_error={type(exc).__name__}; params={params}: {exc}")
            continue
        for market in payload.get("markets") or []:
            ticker = str(market.get("ticker") or "")
            if ticker:
                markets_by_ticker[ticker] = dict(market)
    if not markets_by_ticker and errors:
        return [], "; ".join(errors)
    return list(markets_by_ticker.values()), ""


def _market_window_report(args: argparse.Namespace) -> dict[str, Any]:
    if args.skip_market_window_check:
        return {
            "enabled": False,
            "ready": True,
            "evidence": "market_window_check_skipped",
            "next_action": "Manual override: only launch collection if a BTC15M market is active or about to open.",
        }

    base_url = (_get_env_value("KALSHI_BASE_URL") or DEFAULT_KALSHI_BASE_URL).rstrip("/")
    now = datetime.now(timezone.utc)
    markets, error = _load_btc15m_markets(
        base_url,
        limit=args.market_lookup_limit,
        timeout_seconds=args.market_lookup_timeout_seconds,
    )
    if error:
        return {
            "enabled": True,
            "ready": False,
            "base_url": base_url,
            "evidence": error,
            "next_action": "Retry the gate later; do not launch a collection while market availability is unknown.",
        }

    future: list[dict[str, Any]] = []
    for market in markets:
        ticker = str(market.get("ticker") or "")
        if not ticker.startswith(BTC15M_TICKER_PREFIX):
            continue
        close_time = _parse_dt(str(market.get("close_time") or ""))
        if close_time is None or close_time < now:
            continue
        item = dict(market)
        item["_close_dt"] = close_time
        future.append(item)
    future.sort(key=lambda item: item["_close_dt"])

    if not future:
        return {
            "enabled": True,
            "ready": False,
            "base_url": base_url,
            "market_count": len(markets),
            "evidence": f"no_future_{BTC15M_SERIES}_markets_found",
            "next_action": "Retry the gate later; do not launch a collection without a future BTC15M market.",
        }

    market = future[0]
    close_time = market["_close_dt"]
    seconds_to_close = (close_time - now).total_seconds()
    latest_start = close_time - timedelta(seconds=float(args.run_seconds))
    recommended_start = latest_start
    if recommended_start < now:
        recommended_start = now
    ready = (
        seconds_to_close >= float(args.min_market_seconds_remaining)
        and seconds_to_close <= float(args.run_seconds) + float(args.market_window_buffer_seconds)
    )
    ticker = str(market.get("ticker") or "")
    status = str(market.get("status") or "")
    evidence = (
        f"next_market={ticker}; status={status}; close_time={close_time.isoformat()}; "
        f"seconds_to_close={seconds_to_close:.1f}; run_seconds={float(args.run_seconds):.1f}"
    )
    if ready:
        next_action = "Launch bounded passive collection now."
    else:
        next_action = (
            "Wait for the BTC15M market window; recommended_start_utc="
            f"{recommended_start.replace(microsecond=0).isoformat()}"
        )
    return {
        "enabled": True,
        "ready": ready,
        "base_url": base_url,
        "market_count": len(markets),
        "next_market_ticker": ticker,
        "next_market_status": status,
        "next_market_close_time": close_time.isoformat(),
        "seconds_to_close": seconds_to_close,
        "recommended_start_utc": recommended_start.replace(microsecond=0).isoformat(),
        "evidence": evidence,
        "next_action": next_action,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    workspace = args.workspace.resolve()
    failure = _load_json(args.failure_pattern_json)
    objective = _load_json(args.objective_json)
    locked_plan_path = _latest_locked_plan(args.locked_plan_json or args.locked_plan_dir)
    locked_plan = _load_json(locked_plan_path) if locked_plan_path is not None else {}
    failure_generated = _parse_dt(str(failure.get("generated_utc") or ""))
    locked_plan_generated = _parse_dt(str(locked_plan.get("generated_utc") or ""))
    failure_decision = str(failure.get("decision") or "")
    revision_supported = failure_decision == "candidate_revision_supported"
    revision_frozen = (
        revision_supported
        and bool(locked_plan)
        and locked_plan.get("research_only") is True
        and locked_plan_generated is not None
        and (failure_generated is None or locked_plan_generated >= failure_generated)
    )
    sample_ready_for_collection = failure_decision == "no_current_plan_revision_supported" or revision_frozen
    latest_events = _latest_execution_events(workspace)
    latest_event_source = describe_execution_event_source(latest_events)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    latest_event_mtime = _parse_dt(str(latest_event_source.get("mtime_utc") or ""))
    latest_event_age_seconds = (
        (generated_at - latest_event_mtime).total_seconds()
        if latest_event_mtime is not None
        else None
    )
    latest_event_source["age_seconds"] = latest_event_age_seconds
    market_window = _market_window_report(args)
    run_id = generated_at.strftime("%Y%m%dT%H%M%SZ")
    dataset = f"rv600_next_evidence_shadow_{run_id}"
    artifact_root = Path("logs") / "particle_research" / "real_shadow" / dataset
    offline_v28_tool = workspace / "probe_rv600_native_offline_v28_contexts.py"
    offline_v28_engine = workspace / "btc_mushroom_forecaster_v28_fast.py"
    paired_cmd = (
        "python -m research_particle.paired_passive_shadow_run "
        f"--dataset {dataset} "
        f"--artifact-root \"{artifact_root}\" "
        f"--run-seconds {int(args.run_seconds)} "
        "--record-independent-spot "
        "--independent-spot-feed coinbase "
        "--require-independent-spot "
        "--offline-v28-control "
        "--strategy-tag rv600_research_shadow_readonly "
        "--bot-tag rv600_research_shadow_readonly"
    )
    pipeline_cmd = (
        "Use the `pipeline_command` printed by paired_passive_shadow_run; in offline-v28 mode it will point "
        "at `offline_v28_contexts.ndjson` inside the generated artifact root. "
        "then refresh labels with `python probe_rv600_forward_shadow_refresh.py --write`, "
        "score with `python probe_rv600_native_forward_opportunity.py --write`, "
        "and rerun `python probe_rv600_objective_state_audit.py --write`."
    )
    checklist = [
        _row(
            _status((workspace / "docs" / "research" / "RV600_VARIATION_TEST_PLAN.md").exists()),
            "RV600 plan exists",
            str(workspace / "docs" / "research" / "RV600_VARIATION_TEST_PLAN.md"),
            "Keep new evidence tied to this plan or document a new plan revision before scoring.",
        ),
        _row(
            _status(sample_ready_for_collection),
            "Current sample is exhausted or supported revision is frozen before new collection",
            (
                f"failure_decision={failure_decision}; support_row_count={(failure.get('grid') or {}).get('support_row_count')}; "
                f"locked_plan={locked_plan_path}; plan_id={locked_plan.get('plan_id')}; "
                f"plan_generated_utc={locked_plan.get('generated_utc')}; revision_frozen={revision_frozen}"
            ),
            "Collect materially new shadow evidence only after unsupported samples are exhausted or a supported revision is pre-registered.",
        ),
        _row(
            _status(objective.get("objective_complete") is False),
            "Objective is not already complete",
            f"objective_decision={objective.get('decision')}; blocked_by={objective.get('blocked_by')}",
            "Leave the goal active until fresh shadow evidence meets all gates.",
        ),
        _row(
            _status((workspace / "research_particle" / "paired_passive_shadow_run.py").exists()),
            "Bounded passive collector exists",
            str(workspace / "research_particle" / "paired_passive_shadow_run.py"),
            "Use the bounded paired collector; do not restart or modify live v28.",
        ),
        _row(
            _status((workspace / "research_native_passive_ws_recorder.py").exists()),
            "Native passive websocket recorder exists",
            str(workspace / "research_native_passive_ws_recorder.py"),
            "Recorder is passive and tagged `passive_no_order_submission` in metadata.",
        ),
        _row(
            _status(
                offline_v28_tool.exists()
                and offline_v28_engine.exists()
                and (workspace / "research_particle" / "passive_checkpoint_source.py").exists()
            ),
            "Matched v28 control can be rebuilt offline and causally",
            (
                f"offline_tool={offline_v28_tool}; engine={offline_v28_engine}; "
                "input=passive checkpoints + independent Coinbase spot ticks"
            ),
            (
                "Use `--offline-v28-control`; do not depend on sparse live v28 policy telemetry."
            ),
        ),
        _row(
            _status((workspace / ".env").exists()),
            "Local `.env` is available for read-only API credentials",
            str(workspace / ".env"),
            "Use existing credentials only for passive market data; do not place orders.",
        ),
        _row(
            _status(bool(market_window.get("ready"))),
            "A BTC15M market is inside the bounded collection window",
            str(market_window.get("evidence") or ""),
            str(market_window.get("next_action") or ""),
        ),
    ]
    ready = all(item.status == "pass" for item in checklist)
    report = {
        "schema_version": "rv600-next-evidence-gate-v1",
        "generated_utc": generated_at.isoformat(),
        "research_only": True,
        "ready_for_bounded_shadow_collection": ready,
        "decision": "ready_collect_new_shadow_evidence" if ready else "not_ready_collect_new_shadow_evidence",
        "minimum_completion_sample": {
            "accepted_entries": 100,
            "distinct_markets": 40,
            "calendar_days": 10,
            "weekend_sessions": 2,
            "positive_pnl_after_fees_fills": True,
            "matched_v28_edge_min_percent": 20,
        },
        "market_window": market_window,
        "matched_v28_event_source": latest_event_source,
        "matched_v28_control": {
            "mode": "offline_v28_public_btc_replay",
            "tool": str(offline_v28_tool),
            "engine": str(offline_v28_engine),
            "inputs": [
                "passive orderbook checkpoints",
                "independent Coinbase BTC spot ticks",
                "public Coinbase warmup candles",
                "public Kalshi market metadata",
            ],
            "research_only": True,
            "causal_replay": True,
        },
        "active_locked_plan": {
            "path": str(locked_plan_path) if locked_plan_path is not None else "",
            "plan_id": locked_plan.get("plan_id"),
            "variant": (locked_plan.get("candidate") or {}).get("variant"),
            "generated_utc": locked_plan.get("generated_utc"),
            "forward_evidence_starts_after_utc": (locked_plan.get("pre_registration") or {}).get("forward_evidence_starts_after_utc"),
            "revision_frozen": revision_frozen,
        },
        "checklist": [asdict(item) for item in checklist],
        "commands": {
            "bounded_passive_collection": paired_cmd,
            "post_collection_pipeline": pipeline_cmd,
        },
        "guardrails": [
            "Research-only: no live trades.",
            "Do not change live v28 order logic.",
            "Do not restart the live bot.",
            "Require independent spot for merged context rows so stale/missing spot cannot silently pass through.",
            "Build the matched v28/current control by causal offline v28 replay from public BTC data and captured independent spot.",
            "Live 90-touch v28 policy-eval telemetry is optional diagnostic evidence, not a collection blocker.",
            "Any future candidate must be frozen before counting fresh forward-shadow evidence.",
            "Do not call update_goal until the objective audit is green against fresh evidence.",
        ],
        "inputs": {
            "workspace": str(workspace),
            "failure_pattern_json": str(args.failure_pattern_json),
            "objective_json": str(args.objective_json),
            "locked_plan_json": str(locked_plan_path) if locked_plan_path is not None else "",
        },
    }
    return report


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RV600 Next Evidence Gate",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- ready_for_bounded_shadow_collection: {report['ready_for_bounded_shadow_collection']}",
        "",
        "## Checklist",
        "",
        "| status | requirement | evidence | next action |",
        "|---|---|---|---|",
    ]
    for item in report["checklist"]:
        lines.append(
            f"| {item['status']} | {item['requirement']} | `{item['evidence']}` | {item['next_action']} |"
        )
    lines.append("")
    market_window = report.get("market_window") or {}
    if market_window:
        lines.extend(
            [
                "## Market Window",
                "",
                f"- enabled: {market_window.get('enabled')}",
                f"- ready: {market_window.get('ready')}",
                f"- evidence: `{market_window.get('evidence')}`",
                f"- next_action: {market_window.get('next_action')}",
                "",
            ]
        )
    matched_source = report.get("matched_v28_event_source") or {}
    if matched_source:
        lines.extend(
            [
                "## Optional Live V28 Source",
                "",
                f"- path: `{matched_source.get('path')}`",
                f"- mtime_utc: `{matched_source.get('mtime_utc')}`",
                f"- age_seconds: `{matched_source.get('age_seconds')}`",
                f"- compatible_tail_rows: `{matched_source.get('compatible_tail_rows')}`",
                f"- schema_counts: `{matched_source.get('schema_counts')}`",
                "",
            ]
        )
    matched_control = report.get("matched_v28_control") or {}
    if matched_control:
        lines.extend(
            [
                "## Matched V28 Control",
                "",
                f"- mode: `{matched_control.get('mode')}`",
                f"- tool: `{matched_control.get('tool')}`",
                f"- engine: `{matched_control.get('engine')}`",
                f"- research_only: `{matched_control.get('research_only')}`",
                f"- causal_replay: `{matched_control.get('causal_replay')}`",
                "",
            ]
        )
    active_plan = report.get("active_locked_plan") or {}
    if active_plan:
        lines.extend(
            [
                "## Active Locked Plan",
                "",
                f"- path: `{active_plan.get('path')}`",
                f"- plan_id: `{active_plan.get('plan_id')}`",
                f"- variant: `{active_plan.get('variant')}`",
                f"- generated_utc: `{active_plan.get('generated_utc')}`",
                f"- forward_evidence_starts_after_utc: `{active_plan.get('forward_evidence_starts_after_utc')}`",
                f"- revision_frozen: `{active_plan.get('revision_frozen')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Commands",
            "",
            "Bounded passive collection:",
            "",
            "```powershell",
            report["commands"]["bounded_passive_collection"],
            "```",
            "",
            "Post-collection pipeline:",
            "",
            report["commands"]["post_collection_pipeline"],
            "",
            "## Guardrails",
            "",
        ]
    )
    for item in report["guardrails"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Minimum Completion Sample",
            "",
            f"- accepted_entries: {report['minimum_completion_sample']['accepted_entries']}",
            f"- distinct_markets: {report['minimum_completion_sample']['distinct_markets']}",
            f"- calendar_days: {report['minimum_completion_sample']['calendar_days']}",
            f"- weekend_sessions: {report['minimum_completion_sample']['weekend_sessions']}",
            f"- matched_v28_edge_min_percent: {report['minimum_completion_sample']['matched_v28_edge_min_percent']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the research-only next-evidence gate for RV600.")
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--failure-pattern-json", type=Path, default=DEFAULT_FAILURE_PATTERN_JSON)
    parser.add_argument("--objective-json", type=Path, default=DEFAULT_OBJECTIVE_JSON)
    parser.add_argument("--locked-plan-dir", type=Path, default=DEFAULT_LOCKED_PLAN_DIR)
    parser.add_argument("--locked-plan-json", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--run-seconds", type=float, default=900.0)
    parser.add_argument("--market-lookup-limit", type=int, default=100)
    parser.add_argument("--market-lookup-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--market-window-buffer-seconds", type=float, default=120.0)
    parser.add_argument("--min-market-seconds-remaining", type=float, default=120.0)
    parser.add_argument("--max-v28-event-age-seconds", type=float, default=300.0)
    parser.add_argument("--skip-market-window-check", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"ready_for_bounded_shadow_collection={report['ready_for_bounded_shadow_collection']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
