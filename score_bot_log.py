from __future__ import annotations

import base64
import collections
import csv
import json
import os
import re
import time
from decimal import Decimal, InvalidOperation
from typing import cast
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - production env includes python-dotenv.
    load_dotenv = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
ACCOUNTING_FILLS_ENDPOINT = "/portfolio/fills"
ACCOUNTING_HISTORICAL_FILLS_ENDPOINT = "/historical/fills"
ACCOUNTING_RECONCILIATION_FILENAME = "kalshi_accounting_reconciliation.json"

ENTRY_RE = re.compile(
    r"ENTRY signal \| .*?market=(?P<market>\S+).*?action=buy.*?side=(?P<side>yes|no).*?trigger=(?P<trigger>\d+)\D*.*?limit=(?P<limit>\d+)\D*.*?qty=(?P<qty>\d+)",
    re.IGNORECASE,
)

EXIT_RE = re.compile(
    r"EXIT signal \| .*?market=(?P<market>\S+).*?action=sell.*?side=(?P<side>yes|no).*?trigger=(?P<trigger>\d+)\D*.*?limit=(?P<limit>\d+)\D*.*?qty=(?P<qty>\d+)",
    re.IGNORECASE,
)

ENTRY_FILL_RE = re.compile(
    r"ENTRY(?: immediate)? fill(?:ed)? \| market=(?P<market>\S+) side=(?P<side>yes|no).*?qty=(?P<qty>\d+(?:\.\d+)?)"
    r"(?:.*?limit=(?P<limit>\d+(?:\.\d+)?)\D*)?(?:.*?fill=(?P<fill>\d+(?:\.\d+)?)\D*)?(?:.*?fee=(?P<fee>\d+(?:\.\d+)?)\D*)?",
    re.IGNORECASE,
)

EXIT_FILL_RE = re.compile(
    r"EXIT(?: immediate)? fill(?:ed)? \| market=(?P<market>\S+) side=(?P<side>yes|no).*?qty=(?P<qty>\d+(?:\.\d+)?)"
    r"(?:.*?fill=(?P<fill>\d+(?:\.\d+)?)\D*)?(?:.*?fee=(?P<fee>\d+(?:\.\d+)?)\D*)?",
    re.IGNORECASE,
)

DRY_ENTRY_FILL_RE = re.compile(
    r"DRY RUN: simulated filled entry (?P<market>\S+) side=(?P<side>yes|no) qty=(?P<qty>\d+)",
    re.IGNORECASE,
)

DRY_EXIT_FILL_RE = re.compile(
    r"DRY RUN: simulated filled exit (?P<market>\S+) side=(?P<side>yes|no) qty=(?P<qty>\d+)",
    re.IGNORECASE,
)

WATCH_RE = re.compile(
    r"Watching market (?P<market>\S+) close_time=(?P<close_time>\S+) status=(?P<status>\S+)"
    r"(?:\s+run_id=(?P<run_id>\S+))?",
    re.IGNORECASE,
)

HEARTBEAT_RE = re.compile(
    r"Heartbeat \| watch=(?P<watch>\S+) yes_bid=(?P<yes_bid>None|\d+) yes_ask=(?P<yes_ask>None|\d+) "
    r"no_bid=(?P<no_bid>None|\d+) no_ask=(?P<no_ask>None|\d+) book_ready=(?P<book_ready>True|False) "
    r"position=(?P<position>True|False) pending=(?P<pending>True|False) dry_run=(?P<dry_run>True|False)"
    r"(?:\s+trust=(?P<trust>\S+))?(?:\s+run_id=(?P<run_id>\S+))?",
    re.IGNORECASE,
)

TS_RE = re.compile(r"^(?P<ts>\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2})")
START_RE = re.compile(r"Starting WS bot\. (?:run_id=\S+ )?dry_run=(?P<dry_run>True|False)", re.IGNORECASE)


def sanitize_strategy_tag(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._-") or "default"


def resolve_strategy_paths() -> tuple[str, str, str, Path, Path, Path, Path, Path, Path, Path]:
    output_tag = sanitize_strategy_tag(os.getenv("OUTPUT_STRATEGY_TAG", os.getenv("STRATEGY_TAG", "default")))
    source_tag = sanitize_strategy_tag(os.getenv("LOG_SOURCE_TAG", os.getenv("STRATEGY_TAG", output_tag)))
    score_mode = str(os.getenv("SCORE_MODE", "all")).strip().lower() or "all"
    if score_mode not in {"all", "live_only", "dry_run_only"}:
        score_mode = "all"
    log_dir = ROOT / "logs" / source_tag
    execution_events_path = log_dir / "execution_events.ndjson"
    out_dir = ROOT / "stats" / output_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    return (
        output_tag,
        source_tag,
        score_mode,
        log_dir,
        out_dir / "trades.csv",
        out_dir / "summary.json",
        out_dir / "market_results.csv",
        out_dir / "market_results.json",
        out_dir / "market_result_cache.json",
        execution_events_path,
    )


def resolve_lease_paths() -> tuple[Path, Path, Path]:
    _, source_tag, _, _, csv_path, _, _, _, _, _ = resolve_strategy_paths()
    out_dir = csv_path.parent
    return (
        ROOT / "logs" / source_tag / "lease_events.ndjson",
        out_dir / "lease_events.csv",
        out_dir / "lease_summary.json",
    )


def score_refresh_lock_path() -> Path:
    output_tag, _, _, _, _, _, _, _, _, _ = resolve_strategy_paths()
    return ROOT / "stats" / output_tag / ".score_refresh.lock"


def execution_exit_state_path() -> Path:
    output_tag, _, _, _, _, _, _, _, _, _ = resolve_strategy_paths()
    return ROOT / "stats" / output_tag / ".execution_exit_state.json"


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def save_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_score_refresh_lock(status: str) -> None:
    lock_path = score_refresh_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    save_json_file(
        lock_path,
        {
            "pid": os.getpid(),
            "status": status,
            "strategy_tag": os.getenv("OUTPUT_STRATEGY_TAG", os.getenv("STRATEGY_TAG", "default")),
            "updated_at": datetime.now().isoformat(),
        },
    )


def clear_score_refresh_lock() -> None:
    try:
        score_refresh_lock_path().unlink(missing_ok=True)
    except Exception:
        pass


def read_text_forgiving(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def discover_log_files(log_dir: Path) -> list[Path]:
    if not log_dir.exists():
        return []

    def sort_key(path: Path) -> tuple[float, str]:
        return (path.stat().st_mtime, path.name)

    bot_log = log_dir / "bot.log"
    if bot_log.exists() and bot_log.is_file():
        extra_logs = [
            log_dir / "live_trial_monitor.log",
            log_dir / "monitor.log",
        ]
        files = [bot_log]
        files.extend(p for p in extra_logs if p.exists() and p.is_file())
        return sorted(dict.fromkeys(files), key=sort_key)

    def is_log_like(path: Path) -> bool:
        lowered = path.name.lower()
        if lowered.startswith(("launcher_stderr_", "monitor_stdout_", "monitor_stderr_")):
            return False
        return ".log" in lowered or lowered.endswith(".txt")

    files = [p for p in log_dir.glob("*") if p.is_file() and is_log_like(p)]
    return sorted(files, key=sort_key)


def get_ts(line: str) -> str:
    m = TS_RE.search(line)
    return m.group("ts") if m else ""


def normalize_ts_wall_to_local(value: Any) -> str:
    if not value:
        return ""
    text = str(value).strip()
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return text[:19].replace("T", " ") if "T" in text else text[:19]
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


def load_execution_exit_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    state_path = execution_exit_state_path()
    state = load_json_file(state_path)
    rows = cast(list[dict[str, Any]], state.get("rows") if isinstance(state.get("rows"), list) else [])
    pending = str(state.get("pending") or "")
    offset = int(state.get("offset") or 0)
    tracked_path = str(state.get("path") or "")
    file_size = path.stat().st_size
    if tracked_path != str(path) or offset < 0 or offset > file_size:
        rows = []
        pending = ""
        offset = 0
    seen = {
        (str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("order_id") or ""), str(row.get("exit_ts") or ""))
        for row in rows
    }
    event_priority = {"exit_reconciled": 3, "exit_submit_full": 2, "exit_submit_success": 1}
    with path.open("rb") as handle:
        handle.seek(offset)
        chunk = handle.read()
    if chunk:
        data = pending + chunk.decode("utf-8", errors="ignore")
        parts = data.split("\n")
        if data.endswith("\n"):
            pending = ""
        else:
            pending = parts.pop()
        for raw in parts:
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            event_type = str(payload.get("event_type") or "")
            if event_type not in event_priority:
                continue
            if str(payload.get("result") or "").lower() != "executed":
                continue
            try:
                fill_count = int(float(payload.get("fill_count") or 0))
            except Exception:
                fill_count = 0
            if fill_count <= 0:
                continue
            market = str(payload.get("market") or "").strip()
            side = str(payload.get("side") or "").strip().lower()
            order_id = str(payload.get("order_id") or payload.get("client_order_id") or "")
            ts_wall = normalize_ts_wall_to_local(payload.get("ts_wall"))
            dedupe_key = (market, side, order_id, ts_wall)
            if not market or not side or dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            fill_price = payload.get("actual_fill_price_cents")
            if fill_price in (None, ""):
                fill_price = payload.get("top_of_book_limit_cents")
            if fill_price in (None, ""):
                fill_price = payload.get("yes_bid_cents") if side == "yes" else payload.get("no_bid_cents")
            try:
                fill_price_int = int(float(fill_price)) if fill_price not in (None, "") else 0
            except Exception:
                fill_price_int = 0
            try:
                fee_cents = round(float(payload.get("actual_fee_cents") or 0), 4)
            except Exception:
                fee_cents = 0
            rows.append(
                {
                    "market": market,
                    "side": side,
                    "qty": fill_count,
                    "exit_ts": ts_wall,
                    "fill_cents": fill_price_int,
                    "fee_cents": fee_cents,
                    "event_type": event_type,
                    "priority": event_priority[event_type],
                    "order_id": order_id,
                }
            )
    rows.sort(key=lambda row: (row.get("exit_ts", ""), row.get("priority", 0)))
    save_json_file(
        state_path,
        {
            "offset": file_size,
            "path": str(path),
            "pending": pending,
            "rows": rows,
            "updated_at": datetime.now().isoformat(),
        },
    )
    return rows


def quantity_number(value: Any) -> float:
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def cents_to_dollars(cents: float, qty: float) -> float:
    return round((cents * qty) / 100.0, 4)


def pct(pnl: float, basis: float) -> float:
    if not basis:
        return 0.0
    return round((pnl / basis) * 100.0, 4)


def fee_cents_number(value: Any) -> float:
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def net_pnl_after_fees(gross_pnl: float, entry_fee_cents: Any, exit_fee_cents: Any) -> float:
    fees_cents = fee_cents_number(entry_fee_cents) + fee_cents_number(exit_fee_cents)
    return round(gross_pnl - (fees_cents / 100.0), 4)


def weighted_cents(current_value: Any, current_qty: float, added_value: Any, added_qty: float) -> int | str:
    if added_qty <= 0:
        return current_value
    if current_qty <= 0:
        if added_value in (None, ""):
            return ""
        return int(round(float(added_value)))
    if current_value in (None, "") or added_value in (None, ""):
        return ""
    total_qty = current_qty + added_qty
    if total_qty <= 0:
        return ""
    weighted = ((float(current_value) * current_qty) + (float(added_value) * added_qty)) / total_qty
    return int(round(weighted))


def parse_cents_override(value: Any) -> float | str:
    if value in (None, ""):
        return ""
    try:
        return round(float(value), 4)
    except Exception:
        return ""


def cents_number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def parse_iso_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def local_trade_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S").astimezone()
        except Exception:
            continue
    return parse_iso_datetime(text)


def dollars_to_cents(value: Any) -> float | str:
    if value in (None, ""):
        return ""
    try:
        return round(float(value) * 100.0, 4)
    except Exception:
        return ""


def decimal_or_none(value: Any) -> Decimal | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def decimal_cents(value: Any) -> Decimal | None:
    cents = dollars_to_cents(value)
    if cents == "":
        return None
    return decimal_or_none(cents)


def decimal_float(value: Decimal, places: int = 4) -> float:
    quant = Decimal("1").scaleb(-places)
    return float(value.quantize(quant))


def opposite_side(side: str) -> str:
    return "no" if side == "yes" else "yes" if side == "no" else ""


def append_timestamp_list(existing: Any, value: Any) -> str:
    timestamps = [part.strip() for part in str(existing or "").split("|") if part.strip()]
    text = str(value or "").strip()
    if text and text not in timestamps:
        timestamps.append(text)
    return "|".join(timestamps)


def match_datetimes(value: Any) -> list[datetime]:
    if isinstance(value, (list, tuple, set)):
        raw_values = [str(item or "") for item in value]
    else:
        raw_values = [part for part in str(value or "").split("|")]
    parsed: list[datetime] = []
    for raw in raw_values:
        dt = local_trade_datetime(raw)
        if dt is not None:
            parsed.append(dt)
    return parsed


def fill_created_datetime(fill: dict[str, Any]) -> datetime | None:
    created = parse_iso_datetime(fill.get("created_time") or fill.get("created_at"))
    if created is not None:
        return created if created.tzinfo else created.replace(tzinfo=timezone.utc)
    ts = fill.get("ts") or fill.get("created_ts")
    if ts in (None, ""):
        return None
    try:
        numeric_ts = float(ts)
    except (TypeError, ValueError):
        return None
    if numeric_ts > 10_000_000_000:
        numeric_ts /= 1000.0
    try:
        return datetime.fromtimestamp(numeric_ts, timezone.utc)
    except Exception:
        return None


def fill_created_text(fill: dict[str, Any]) -> str:
    text = str(fill.get("created_time") or fill.get("created_at") or "").strip()
    if text:
        return text
    created = fill_created_datetime(fill)
    return created.isoformat() if created is not None else str(fill.get("ts") or "")


def cents_from_fill(fill: dict[str, Any], dollars_key: str, cents_key: str) -> float | str:
    value = dollars_to_cents(fill.get(dollars_key))
    if value != "":
        return value
    cents_value = decimal_or_none(fill.get(cents_key))
    return decimal_float(cents_value, 4) if cents_value is not None else ""


def fee_cents_from_fill(fill: dict[str, Any]) -> float | str:
    value = dollars_to_cents(fill.get("fee_cost"))
    if value != "":
        return value
    fee_cents = decimal_or_none(fill.get("fee_cents"))
    return decimal_float(fee_cents, 4) if fee_cents is not None else ""


def normalize_exchange_fill(fill: dict[str, Any], *, source: str, endpoint: str = "") -> dict[str, Any] | None:
    market = str(fill.get("market_ticker") or fill.get("ticker") or "").strip()
    action = str(fill.get("action") or "").strip().lower()
    if not market or action not in {"buy", "sell"}:
        return None
    fill_id = str(fill.get("fill_id") or fill.get("trade_id") or "").strip()
    if not fill_id:
        fill_id = "|".join(
            [
                str(fill.get("order_id") or "").strip(),
                fill_created_text(fill),
                market,
                action,
                str(fill.get("side") or fill.get("outcome_side") or "").strip().lower(),
            ]
        )
    return {
        "fill_id": fill_id,
        "market": market,
        "action": action,
        "side": str(fill.get("side") or fill.get("outcome_side") or "").strip().lower(),
        "created": fill_created_datetime(fill),
        "created_text": fill_created_text(fill),
        "order_id": str(fill.get("order_id") or "").strip(),
        "fee_cents": fee_cents_from_fill(fill),
        "count_contracts": decimal_or_none(fill.get("count_fp") or fill.get("count")),
        "yes_cents": cents_from_fill(fill, "yes_price_dollars", "yes_price_cents"),
        "no_cents": cents_from_fill(fill, "no_price_dollars", "no_price_cents"),
        "source": source,
        "endpoint": endpoint,
    }


def load_exchange_candidate_fills(log_dir: Path) -> list[dict[str, Any]]:
    ledger_path = log_dir / "exchange_reconciliation.ndjson"
    if not ledger_path.exists():
        return []
    fills_by_id: dict[str, dict[str, Any]] = {}
    try:
        lines = ledger_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    for raw in lines:
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        fills = payload.get("candidate_recent_fills_since_run")
        if not isinstance(fills, list):
            continue
        for fill in fills:
            if not isinstance(fill, dict):
                continue
            fill_id = str(fill.get("fill_id") or fill.get("trade_id") or "")
            if not fill_id:
                fill_id = "|".join(
                    [
                        str(fill.get("order_id") or ""),
                        str(fill.get("created_time") or fill.get("ts") or ""),
                        str(fill.get("market_ticker") or fill.get("ticker") or ""),
                    ]
                )
            fills_by_id[fill_id] = fill
    rows: list[dict[str, Any]] = []
    for fill in fills_by_id.values():
        row = normalize_exchange_fill(fill, source="exchange_reconciliation_log", endpoint=str(ledger_path))
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda row: (str(row.get("created_text") or ""), row.get("market", ""), row.get("action", "")))
    return rows


class KalshiAccountingClient:
    def __init__(self, *, api_key_id: str, private_key_path: Path, base_url: str, subaccount: int | None, timeout_seconds: float) -> None:
        self.api_key_id = api_key_id
        self.private_key_path = private_key_path
        self.base_url = base_url.rstrip("/")
        self.subaccount = subaccount
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "kalshi-btc15m-accounting/1.0"})
        with self.private_key_path.open("rb") as fh:
            self.private_key = serialization.load_pem_private_key(
                fh.read(),
                password=None,
                backend=default_backend(),
            )

    def _sign_request(self, timestamp_ms: str, method: str, path: str) -> str:
        message = f"{timestamp_ms}{method.upper()}{path.split('?')[0]}".encode("utf-8")
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _auth_headers(self, method: str, endpoint_path: str) -> dict[str, str]:
        timestamp_ms = str(int(time.time() * 1000))
        path = urlparse(self.base_url + endpoint_path).path
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
            "KALSHI-ACCESS-SIGNATURE": self._sign_request(timestamp_ms, method, path),
        }

    def request(self, method: str, endpoint_path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.request(
            method=method.upper(),
            url=self.base_url + endpoint_path,
            params=params,
            headers=self._auth_headers(method, endpoint_path),
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {response.text[:500]}",
                response=response,
            )
        if not response.text:
            return {}
        return cast(dict[str, Any], response.json())

    def get_fills(self, endpoint_path: str, *, ticker: str, limit: int, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"ticker": ticker, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        if endpoint_path == ACCOUNTING_FILLS_ENDPOINT and self.subaccount is not None:
            params["subaccount"] = self.subaccount
        return self.request("GET", endpoint_path, params=params)


_ENV_LOADED = False


def load_dotenv_once() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    env_path = ROOT / ".env"
    if load_dotenv is not None:
        load_dotenv(env_path)
        return
    if not env_path.exists():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except Exception:
        return


def env_flag(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", "disabled"}


def env_int(name: str, default: int, *, min_value: int = 1, max_value: int = 1000) -> int:
    try:
        value = int(str(os.getenv(name, str(default))).strip())
    except (TypeError, ValueError):
        value = default
    return max(min_value, min(max_value, value))


def compact_error(exc: Exception) -> str:
    text = str(exc).replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"(KALSHI-ACCESS-[A-Z-]+:\s*)\S+", r"\1<redacted>", text, flags=re.IGNORECASE)
    return text[:500]


def build_kalshi_accounting_client() -> tuple[KalshiAccountingClient | None, str]:
    load_dotenv_once()
    api_key_id = str(os.getenv("KALSHI_API_KEY_ID") or "").strip()
    private_key_raw = str(os.getenv("KALSHI_PRIVATE_KEY_PATH") or "").strip()
    if not api_key_id or not private_key_raw:
        return None, "missing KALSHI_API_KEY_ID or KALSHI_PRIVATE_KEY_PATH"
    private_key_path = Path(private_key_raw)
    if not private_key_path.is_absolute():
        private_key_path = (ROOT / private_key_path).resolve()
    if not private_key_path.exists():
        return None, f"private key file not found at {private_key_path}"
    subaccount_raw = str(os.getenv("KALSHI_ACCOUNTING_SUBACCOUNT", os.getenv("KALSHI_SUBACCOUNT_NUMBER", "0"))).strip()
    subaccount: int | None
    if subaccount_raw == "":
        subaccount = None
    else:
        try:
            subaccount = int(subaccount_raw)
        except ValueError:
            subaccount = 0
    timeout_seconds = float(os.getenv("KALSHI_ACCOUNTING_TIMEOUT_SECONDS", "20") or 20)
    base_url = str(os.getenv("KALSHI_BASE_URL", BASE_URL)).strip().rstrip("/") or BASE_URL
    try:
        return (
            KalshiAccountingClient(
                api_key_id=api_key_id,
                private_key_path=private_key_path,
                base_url=base_url,
                subaccount=subaccount,
                timeout_seconds=timeout_seconds,
            ),
            "",
        )
    except Exception as exc:  # noqa: BLE001
        return None, compact_error(exc)


def accounting_reconciliation_path(out_dir: Path) -> Path:
    return out_dir / ACCOUNTING_RECONCILIATION_FILENAME


def write_accounting_reconciliation(out_dir: Path, summary: dict[str, Any]) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        accounting_reconciliation_path(out_dir).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        return


def fetch_kalshi_api_accounting_fills(final_rows: list[dict[str, Any]], out_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    markets = sorted({str(row.get("market") or "").strip() for row in final_rows if str(row.get("market") or "").strip()})
    summary: dict[str, Any] = {
        "enabled": env_flag("KALSHI_ACCOUNTING_API_ENABLED", True),
        "authenticated": False,
        "source_label": "disabled",
        "markets_requested": len(markets),
        "api_fill_count": 0,
        "normalized_api_fill_count": 0,
        "endpoint_errors": [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if not summary["enabled"]:
        write_accounting_reconciliation(out_dir, summary)
        return [], summary
    if not markets:
        summary["source_label"] = "no_markets_to_reconcile"
        write_accounting_reconciliation(out_dir, summary)
        return [], summary

    client, client_error = build_kalshi_accounting_client()
    if client is None:
        summary["source_label"] = "missing_kalshi_api_credentials"
        summary["client_error"] = client_error
        write_accounting_reconciliation(out_dir, summary)
        return [], summary

    summary["authenticated"] = True
    summary["source_label"] = "kalshi_api"
    limit = env_int("KALSHI_ACCOUNTING_FILL_LIMIT", 1000, min_value=1, max_value=1000)
    max_pages = env_int("KALSHI_ACCOUNTING_MAX_PAGES_PER_MARKET", 4, min_value=1, max_value=25)
    include_historical = env_flag("KALSHI_ACCOUNTING_INCLUDE_HISTORICAL", True)
    endpoint_paths = [ACCOUNTING_FILLS_ENDPOINT]
    if include_historical:
        endpoint_paths.append(ACCOUNTING_HISTORICAL_FILLS_ENDPOINT)
    summary["endpoint_paths"] = endpoint_paths
    fills_by_id: dict[str, dict[str, Any]] = {}
    raw_fill_count = 0
    historical_unavailable = False

    for market in markets:
        for endpoint_path in endpoint_paths:
            if historical_unavailable and endpoint_path == ACCOUNTING_HISTORICAL_FILLS_ENDPOINT:
                continue
            cursor = ""
            for _ in range(max_pages):
                try:
                    payload = client.get_fills(endpoint_path, ticker=market, limit=limit, cursor=cursor)
                except requests.HTTPError as exc:
                    status_code = exc.response.status_code if exc.response is not None else None
                    if endpoint_path == ACCOUNTING_HISTORICAL_FILLS_ENDPOINT and status_code == 404:
                        historical_unavailable = True
                    errors = cast(list[str], summary["endpoint_errors"])
                    if len(errors) < 8:
                        errors.append(f"{endpoint_path} {market}: {compact_error(exc)}")
                    break
                except Exception as exc:  # noqa: BLE001
                    errors = cast(list[str], summary["endpoint_errors"])
                    if len(errors) < 8:
                        errors.append(f"{endpoint_path} {market}: {compact_error(exc)}")
                    break
                raw_fills = payload.get("fills", [])
                if not isinstance(raw_fills, list):
                    raw_fills = []
                raw_fill_count += len(raw_fills)
                for fill in raw_fills:
                    if not isinstance(fill, dict):
                        continue
                    normalized = normalize_exchange_fill(fill, source="kalshi_api", endpoint=endpoint_path)
                    if normalized is None:
                        continue
                    fills_by_id[str(normalized.get("fill_id") or "")] = normalized
                cursor = str(payload.get("cursor") or "").strip()
                if not cursor:
                    break

    rows = sorted(fills_by_id.values(), key=lambda row: (str(row.get("created_text") or ""), row.get("market", ""), row.get("action", "")))
    summary["api_fill_count"] = raw_fill_count
    summary["normalized_api_fill_count"] = len(rows)
    summary["historical_unavailable"] = historical_unavailable
    if summary["authenticated"] and not rows:
        summary["source_label"] = "kalshi_api_no_matching_fills"
    write_accounting_reconciliation(out_dir, summary)
    return rows, summary


def apply_exchange_fill_overrides(final_rows: list[dict[str, Any]], log_dir: Path, api_fills: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    log_fills = load_exchange_candidate_fills(log_dir)
    api_fill_rows = list(api_fills or [])
    combined_by_id: dict[str, dict[str, Any]] = {}
    for fill in log_fills:
        fill_id = str(fill.get("fill_id") or "")
        combined_by_id[fill_id] = fill
    for fill in api_fill_rows:
        fill_id = str(fill.get("fill_id") or "")
        combined_by_id[fill_id] = fill
    exchange_fills = sorted(
        combined_by_id.values(),
        key=lambda row: (str(row.get("created_text") or ""), row.get("market", ""), row.get("action", ""), row.get("source", "")),
    )
    summary: dict[str, Any] = {
        "log_fill_count": len(log_fills),
        "api_fill_count": len(api_fill_rows),
        "combined_fill_count": len(exchange_fills),
        "rows_total": len(final_rows),
        "entry_rows_matched": 0,
        "entry_rows_matched_api": 0,
        "exit_rows_matched": 0,
        "exit_rows_matched_api": 0,
        "settled_rows_with_api_entry": 0,
        "realized_exit_rows": 0,
        "unmatched_entries": 0,
        "unmatched_realized_exits": 0,
        "source_label": "bot_log_estimate",
    }
    if not exchange_fills:
        for row in final_rows:
            row.setdefault("entry_accounting_source", "bot_log_estimate")
            row.setdefault("exit_accounting_source", "none")
            row.setdefault("accounting_source", "bot_log_estimate")
        return summary

    used_fill_ids: set[str] = set()

    def fill_matches_side(fill: dict[str, Any], action: str, side: str) -> bool:
        fill_side = str(fill.get("side") or "").strip().lower()
        if not fill_side:
            return True
        if action == "buy":
            return fill_side == side
        # Kalshi sell fills often report the complementary side while the price
        # fields still contain the actual sold-side price.
        return fill_side in {side, opposite_side(side)}

    def fill_price_cents(fill: dict[str, Any], side: str) -> Decimal | None:
        return decimal_or_none(fill.get(f"{side}_cents"))

    def aggregate_fills(
        market: str,
        action: str,
        side: str,
        trade_ts: Any,
        target_qty: float,
    ) -> dict[str, Any] | None:
        candidates = [
            fill for fill in exchange_fills
            if normalize_key(str(fill.get("market") or "")) == normalize_key(market)
            and str(fill.get("action") or "") == action
            and fill_matches_side(fill, action, side)
            and str(fill.get("fill_id") or "") not in used_fill_ids
            and fill_price_cents(fill, side) is not None
        ]
        if not candidates:
            return None
        target_dts = match_datetimes(trade_ts)
        if not target_dts:
            return None

        def distance(fill: dict[str, Any]) -> float:
            created = fill.get("created")
            if not isinstance(created, datetime):
                return float("inf")
            distances: list[float] = []
            for target_dt in target_dts:
                try:
                    distances.append(abs((created.astimezone() - target_dt).total_seconds()))
                except Exception:
                    continue
            return min(distances) if distances else float("inf")

        def source_rank(fill: dict[str, Any]) -> int:
            return 0 if str(fill.get("source") or "") == "kalshi_api" else 1

        candidates = [fill for fill in candidates if distance(fill) <= 30.0]
        if not candidates:
            return None
        anchor = min(candidates, key=lambda fill: (distance(fill), source_rank(fill)))
        anchor_order = str(anchor.get("order_id") or "")
        selected: list[dict[str, Any]]
        if anchor_order:
            selected = [fill for fill in candidates if str(fill.get("order_id") or "") == anchor_order]
        else:
            selected = [anchor]
        selected_ids = {str(fill.get("fill_id") or "") for fill in selected}
        target = max(Decimal("0.000001"), Decimal(str(quantity_number(target_qty))))

        def selected_qty(fills: list[dict[str, Any]]) -> Decimal:
            total = Decimal("0")
            missing = 0
            for fill in fills:
                count = fill.get("count_contracts")
                if isinstance(count, Decimal) and count > 0:
                    total += count
                else:
                    missing += 1
            if missing:
                total += max(Decimal("0"), target - total)
            return total

        if selected_qty(selected) < target:
            for fill in sorted(candidates, key=lambda item: (distance(item), source_rank(item))):
                fill_id = str(fill.get("fill_id") or "")
                if fill_id in selected_ids:
                    continue
                selected.append(fill)
                selected_ids.add(fill_id)
                if selected_qty(selected) >= target:
                    break

        total_qty = Decimal("0")
        total_notional_cents = Decimal("0")
        total_fee_cents = Decimal("0")
        missing_qty_count = 0
        known_qty = Decimal("0")
        for fill in selected:
            count = fill.get("count_contracts")
            if isinstance(count, Decimal) and count > 0:
                known_qty += count
            else:
                missing_qty_count += 1
        missing_qty_each = Decimal("0")
        if missing_qty_count:
            missing_qty_each = max(Decimal("0"), target - known_qty) / Decimal(missing_qty_count)
        for fill in selected:
            count = fill.get("count_contracts")
            qty = count if isinstance(count, Decimal) and count > 0 else missing_qty_each
            price = fill_price_cents(fill, side)
            if qty <= 0 or price is None:
                continue
            total_qty += qty
            total_notional_cents += qty * price
            fee = decimal_or_none(fill.get("fee_cents"))
            if fee is not None:
                total_fee_cents += fee
        if total_qty <= 0:
            return None
        for fill in selected:
            fill_id = str(fill.get("fill_id") or "")
            if fill_id:
                used_fill_ids.add(fill_id)
        avg_price_cents = total_notional_cents / total_qty
        sources = sorted({str(fill.get("source") or "") for fill in selected if str(fill.get("source") or "")})
        api_fill_ids = [
            str(fill.get("fill_id") or "")
            for fill in selected
            if str(fill.get("source") or "") == "kalshi_api" and str(fill.get("fill_id") or "")
        ]
        source_label = "kalshi_api" if api_fill_ids and len(api_fill_ids) == len(selected) else (
            "kalshi_api+exchange_reconciliation_log" if api_fill_ids else "exchange_reconciliation_log"
        )
        return {
            "fill_ids": [str(fill.get("fill_id") or "") for fill in selected if str(fill.get("fill_id") or "")],
            "api_fill_ids": api_fill_ids,
            "qty": decimal_float(total_qty, 6),
            "price_cents": decimal_float(avg_price_cents, 4),
            "notional_cents": decimal_float(total_notional_cents, 4),
            "notional_dollars": decimal_float(total_notional_cents / Decimal("100"), 4),
            "fee_cents": decimal_float(total_fee_cents, 4),
            "sources": sources,
            "source_label": source_label,
            "has_api": bool(api_fill_ids),
        }

    for row in final_rows:
        row.setdefault("entry_accounting_source", "bot_log_estimate")
        row.setdefault("exit_accounting_source", "none")
        row.setdefault("accounting_source", "bot_log_estimate")
        market = str(row.get("market") or "")
        side = str(row.get("side") or "").lower()
        qty = quantity_number(row.get("qty", 0))
        if not market or side not in {"yes", "no"} or qty <= 0:
            continue
        entry_match_ts = row.get("entry_fill_event_ts_list") or row.get("entry_ts")
        entry_fill = aggregate_fills(market, "buy", side, entry_match_ts, qty)
        has_realized_exit = bool(str(row.get("exit_ts") or "").strip()) or str(row.get("outcome") or "") == "exited_before_settlement"
        if has_realized_exit:
            summary["realized_exit_rows"] = int(summary["realized_exit_rows"]) + 1
        exit_match_ts = row.get("exit_fill_event_ts_list") or row.get("exit_ts")
        exit_fill = aggregate_fills(market, "sell", side, exit_match_ts, qty) if has_realized_exit else None
        manual_override = bool(row.get("manual_accounting_override"))
        if manual_override and entry_fill and not entry_fill.get("has_api"):
            entry_fill = None
        if manual_override and exit_fill and not exit_fill.get("has_api"):
            exit_fill = None
        if entry_fill:
            summary["entry_rows_matched"] = int(summary["entry_rows_matched"]) + 1
            if entry_fill.get("has_api"):
                summary["entry_rows_matched_api"] = int(summary["entry_rows_matched_api"]) + 1
            entry_price = entry_fill.get("price_cents")
            if entry_price not in (None, ""):
                row["entry_fill_cents_actual"] = parse_cents_override(entry_price)
                row["entry_fill_cents_used"] = cents_number(row["entry_fill_cents_actual"])
                row["entry_notional_dollars"] = entry_fill.get("notional_dollars", "")
                row["entry_exchange_qty"] = entry_fill.get("qty", "")
                row["entry_exchange_fill_ids"] = "|".join(entry_fill.get("fill_ids", []))
                row["entry_api_fill_ids"] = "|".join(entry_fill.get("api_fill_ids", []))
                row["entry_accounting_source"] = entry_fill.get("source_label", "exchange_reconciliation_log")
            if entry_fill.get("fee_cents") not in (None, ""):
                row["entry_fee_cents"] = round(float(entry_fill["fee_cents"]), 4)
        else:
            summary["unmatched_entries"] = int(summary["unmatched_entries"]) + 1
        if exit_fill:
            summary["exit_rows_matched"] = int(summary["exit_rows_matched"]) + 1
            if exit_fill.get("has_api"):
                summary["exit_rows_matched_api"] = int(summary["exit_rows_matched_api"]) + 1
            exit_price = exit_fill.get("price_cents")
            if exit_price not in (None, ""):
                row["exit_fill_cents_actual"] = parse_cents_override(exit_price)
                row["exit_fill_cents_used"] = cents_number(row["exit_fill_cents_actual"])
                row["exit_notional_dollars"] = exit_fill.get("notional_dollars", "")
                row["exit_exchange_qty"] = exit_fill.get("qty", "")
                row["exit_exchange_fill_ids"] = "|".join(exit_fill.get("fill_ids", []))
                row["exit_api_fill_ids"] = "|".join(exit_fill.get("api_fill_ids", []))
                row["exit_accounting_source"] = exit_fill.get("source_label", "exchange_reconciliation_log")
            if exit_fill.get("fee_cents") not in (None, ""):
                row["exit_fee_cents"] = round(float(exit_fill["fee_cents"]), 4)
        elif has_realized_exit:
            summary["unmatched_realized_exits"] = int(summary["unmatched_realized_exits"]) + 1
        entry_used = cents_number(row.get("entry_fill_cents_used") or 0)
        exit_used = cents_number(row.get("exit_fill_cents_used") or 0)
        entry_qty = float(row.get("entry_exchange_qty") or qty)
        exit_qty = float(row.get("exit_exchange_qty") or qty)
        entry_notional_cents = float(entry_fill.get("notional_cents")) if entry_fill else entry_used * qty
        exit_notional_cents = float(exit_fill.get("notional_cents")) if exit_fill else exit_used * qty
        entry_fee_cents = fee_cents_number(row.get("entry_fee_cents", 0))
        exit_fee_cents = fee_cents_number(row.get("exit_fee_cents", 0))
        row["total_fees_dollars"] = round((entry_fee_cents + exit_fee_cents) / 100.0, 4)
        if has_realized_exit and entry_used > 0 and exit_used > 0:
            gross_pnl = round((exit_notional_cents - entry_notional_cents) / 100.0, 4)
            net_pnl = net_pnl_after_fees(gross_pnl, entry_fee_cents, exit_fee_cents)
            row["gross_pnl_dollars"] = gross_pnl
            row["net_pnl_dollars"] = net_pnl
            row["gross_pnl_percent"] = pct(gross_pnl, float(row.get("entry_notional_dollars", 0.0) or 0.0))
            row["net_pnl_percent"] = pct(net_pnl, float(row.get("entry_notional_dollars", 0.0) or 0.0))
            row["accounting_source"] = (
                "kalshi_api"
                if entry_fill and exit_fill and entry_fill.get("has_api") and exit_fill.get("has_api")
                else "kalshi_api_partial"
                if (entry_fill and entry_fill.get("has_api")) or (exit_fill and exit_fill.get("has_api"))
                else "exchange_reconciliation_log"
            )
            continue
        result = str(row.get("result") or row.get("market_result") or "").lower()
        if entry_used > 0 and result in {"yes", "no"}:
            settlement_payout_cents = (100.0 * entry_qty) if side == result else 0.0
            gross_pnl = round((settlement_payout_cents - entry_notional_cents) / 100.0, 4)
            net_pnl = net_pnl_after_fees(gross_pnl, entry_fee_cents, exit_fee_cents)
            row["gross_pnl_dollars"] = gross_pnl
            row["net_pnl_dollars"] = net_pnl
            row["gross_pnl_percent"] = pct(gross_pnl, float(row.get("entry_notional_dollars", 0.0) or 0.0))
            row["net_pnl_percent"] = pct(net_pnl, float(row.get("entry_notional_dollars", 0.0) or 0.0))
            if entry_fill and entry_fill.get("has_api"):
                summary["settled_rows_with_api_entry"] = int(summary["settled_rows_with_api_entry"]) + 1
                row["exit_accounting_source"] = "kalshi_market_result_api"
                row["accounting_source"] = "kalshi_api_fills+market_result"
            elif entry_fill:
                row["exit_accounting_source"] = "kalshi_market_result_api"
                row["accounting_source"] = "exchange_reconciliation_log+market_result"
        elif entry_fill and entry_fill.get("has_api"):
            row["accounting_source"] = "kalshi_api_open"
        elif entry_fill:
            row["accounting_source"] = "exchange_reconciliation_log"

    if int(summary["entry_rows_matched_api"]) or int(summary["exit_rows_matched_api"]):
        summary["source_label"] = "kalshi_api"
    elif int(summary["entry_rows_matched"]) or int(summary["exit_rows_matched"]):
        summary["source_label"] = "exchange_reconciliation_log"
    return summary


def finalize_exit_trade(
    trade: dict[str, Any],
    *,
    exit_ts: str,
    exit_trigger_cents: Any,
    exit_fill_assumed: Any,
    exit_fill_actual: Any,
    exit_fee_cents: float,
    resolution_source: str,
    exit_fill_event_ts: Any = "",
) -> dict[str, Any] | None:
    qty = quantity_number(trade.get("qty"))
    if qty <= 0:
        return None

    entry_fill_used = cents_number(trade.get("entry_fill_cents_used") or 0)
    exit_fill_actual_value = parse_cents_override(exit_fill_actual)
    exit_fill_assumed_value = parse_cents_override(exit_fill_assumed)
    exit_fill_used = cents_number(exit_fill_actual_value or exit_fill_assumed_value or 0)
    if exit_fill_used <= 0:
        return None

    exit_notional = cents_to_dollars(exit_fill_used, qty)
    pnl = round(((exit_fill_used - entry_fill_used) * qty) / 100.0, 4)
    entry_fee_cents = fee_cents_number(trade.get("entry_fee_cents", 0))
    exit_fee_cents = fee_cents_number(exit_fee_cents)
    net_pnl = net_pnl_after_fees(pnl, entry_fee_cents, exit_fee_cents)
    net_pnl_percent = pct(net_pnl, float(trade.get("entry_notional_dollars", 0.0) or 0.0))
    pnl_percent = pct(pnl, float(trade.get("entry_notional_dollars", 0.0) or 0.0))

    trade["exit_ts"] = exit_ts
    trade["exit_trigger_cents"] = exit_trigger_cents
    trade["exit_fill_cents_assumed"] = exit_fill_assumed_value
    trade["exit_fill_cents_actual"] = exit_fill_actual_value
    trade["exit_fill_cents_used"] = exit_fill_used
    trade["exit_fee_cents"] = exit_fee_cents
    trade["total_fees_dollars"] = round((entry_fee_cents + exit_fee_cents) / 100.0, 4)
    trade["exit_notional_dollars"] = exit_notional
    trade["exit_fill_event_ts_list"] = append_timestamp_list(trade.get("exit_fill_event_ts_list", ""), exit_fill_event_ts or exit_ts)
    trade["gross_pnl_dollars"] = pnl
    trade["net_pnl_dollars"] = net_pnl
    trade["net_pnl_percent"] = net_pnl_percent
    trade["gross_pnl_percent"] = pnl_percent
    trade["outcome"] = "exited_before_settlement"
    trade["resolution_source"] = resolution_source
    trade["market_result"] = ""
    return trade.copy()


def load_cache() -> dict[str, dict[str, Any]]:
    _, _, _, _, _, _, _, _, market_cache_json, _ = resolve_strategy_paths()
    if not market_cache_json.exists():
        return {}
    try:
        raw = json.loads(market_cache_json.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
    except Exception:
        pass
    return {}


def save_cache(cache: dict[str, dict[str, Any]]) -> None:
    _, _, _, _, _, _, _, _, market_cache_json, _ = resolve_strategy_paths()
    market_cache_json.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def normalize_key(value: str) -> str:
    return value.strip().upper()


def load_manual_exclusions() -> tuple[set[str], set[str]]:
    _, _, _, _, csv_path, _, _, _, _, _ = resolve_strategy_paths()
    exclusions_path = csv_path.parent / "manual_exclusions.json"
    if not exclusions_path.exists():
        return set(), set()
    try:
        raw = json.loads(exclusions_path.read_text(encoding="utf-8"))
    except Exception:
        return set(), set()
    if not isinstance(raw, dict):
        return set(), set()
    exclude_markets = {
        normalize_key(str(value))
        for value in raw.get("exclude_markets", [])
        if str(value).strip()
    }
    exclude_entries = {
        normalize_key(str(value))
        for value in raw.get("exclude_entry_keys", [])
        if str(value).strip()
    }
    return exclude_markets, exclude_entries


def load_manual_trade_overrides() -> dict[str, dict[str, Any]]:
    _, _, _, _, csv_path, _, _, _, _, _ = resolve_strategy_paths()
    overrides_path = csv_path.parent / "manual_trade_overrides.json"
    if not overrides_path.exists():
        return {}
    try:
        raw = json.loads(overrides_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    overrides: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        norm_key = normalize_key(str(key))
        if not norm_key or not isinstance(value, dict):
            continue
        overrides[norm_key] = value
    return overrides


def apply_manual_trade_overrides(final_rows: list[dict[str, Any]]) -> None:
    overrides = load_manual_trade_overrides()
    if not overrides:
        return
    for row in final_rows:
        key = normalize_key(f"{row.get('market', '')}|{row.get('side', '')}|{row.get('entry_ts', '')}")
        override = overrides.get(key)
        if not override:
            continue
        qty = quantity_number(row.get("qty", 0))
        if qty <= 0:
            continue
        row["manual_accounting_override"] = True
        row["accounting_source"] = "manual_override"

        entry_assumed = cents_number(row.get("entry_fill_cents_assumed", 0) or 0)
        entry_actual = row.get("entry_fill_cents_actual", "")
        if "entry_fill_cents_actual" in override:
            entry_actual = parse_cents_override(override["entry_fill_cents_actual"])
            row["entry_fill_cents_actual"] = entry_actual
        if "entry_fee_cents" in override:
            row["entry_fee_cents"] = round(float(override["entry_fee_cents"]), 4)
        entry_used = cents_number(entry_actual or entry_assumed or 0)
        row["entry_fill_cents_used"] = entry_used
        row["entry_notional_dollars"] = cents_to_dollars(entry_used, qty)

        exit_assumed = cents_number(row.get("exit_fill_cents_assumed", 0) or 0)
        exit_actual = row.get("exit_fill_cents_actual", "")
        if "exit_fill_cents_actual" in override:
            exit_actual = parse_cents_override(override["exit_fill_cents_actual"])
            row["exit_fill_cents_actual"] = exit_actual
        if "exit_fee_cents" in override:
            row["exit_fee_cents"] = round(float(override["exit_fee_cents"]), 4)
        exit_used = cents_number(exit_actual or exit_assumed or 0)
        row["exit_fill_cents_used"] = exit_used if exit_used > 0 else ""
        row["exit_notional_dollars"] = cents_to_dollars(exit_used, qty) if exit_used > 0 else row.get("exit_notional_dollars", "")
        row["total_fees_dollars"] = round(
            (fee_cents_number(row.get("entry_fee_cents", 0)) + fee_cents_number(row.get("exit_fee_cents", 0))) / 100.0,
            4,
        )

        if "result" in override:
            row["result"] = str(override["result"] or "").lower()
            row["market_result"] = row["result"]
            row["resolution_source"] = "manual_override"
        if "market_status" in override:
            row["market_status"] = str(override["market_status"] or "")
        if "settlement_ts" in override:
            row["settlement_ts"] = str(override["settlement_ts"] or "")

        outcome = str(row.get("outcome") or "")
        result = str(row.get("result") or "").lower()
        basis = float(row.get("entry_notional_dollars") or 0.0)
        if outcome == "exited_before_settlement" and exit_used > 0:
            pnl = round(((exit_used - entry_used) * qty) / 100.0, 4)
            row["gross_pnl_dollars"] = pnl
            row["net_pnl_dollars"] = net_pnl_after_fees(pnl, row.get("entry_fee_cents", 0), row.get("exit_fee_cents", 0))
            row["net_pnl_percent"] = pct(float(row["net_pnl_dollars"]), basis)
            row["gross_pnl_percent"] = pct(pnl, basis)
        elif result in {"yes", "no"}:
            if str(row.get("side") or "") == result:
                pnl = round(((100 - entry_used) * qty) / 100.0, 4)
                row["outcome"] = "win"
            else:
                pnl = round((0 - entry_used * qty) / 100.0, 4)
                row["outcome"] = "loss"
            row["gross_pnl_dollars"] = pnl
            row["net_pnl_dollars"] = net_pnl_after_fees(pnl, row.get("entry_fee_cents", 0), row.get("exit_fee_cents", 0))
            row["net_pnl_percent"] = pct(float(row["net_pnl_dollars"]), basis)
            row["gross_pnl_percent"] = pct(pnl, basis)
        elif outcome == "void":
            row["gross_pnl_dollars"] = 0.0
            row["net_pnl_dollars"] = 0.0
            row["net_pnl_percent"] = 0.0
            row["gross_pnl_percent"] = 0.0


def filter_lines_by_score_mode(all_lines: list[str], score_mode: str) -> list[str]:
    if score_mode == "all":
        return all_lines
    keep_dry_run = score_mode == "dry_run_only"
    current_dry_run: bool | None = None
    filtered: list[str] = []
    for line in all_lines:
        start_match = START_RE.search(line)
        if start_match:
            current_dry_run = start_match.group("dry_run").lower() == "true"
        if current_dry_run is None:
            continue
        if current_dry_run == keep_dry_run:
            filtered.append(line)
    return filtered


def is_final_market(payload: dict[str, Any]) -> bool:
    result = str(payload.get("result") or "").lower()
    status = str(payload.get("status") or "").lower()
    return result in {"yes", "no", "void"} or status in {"settled", "resolved", "finalized", "final"}


def fetch_market_result(session: requests.Session, market_ticker: str) -> dict[str, Any]:
    url = f"{BASE_URL}/markets/{market_ticker}"
    r = session.get(url, timeout=15)
    r.raise_for_status()
    market = r.json().get("market", {})
    return {
        "market": market_ticker,
        "result": market.get("result") or "",
        "status": market.get("status") or "",
        "settlement_ts": market.get("settlement_ts") or "",
        "close_time": market.get("close_time") or market.get("expiration_time") or "",
        "source": "kalshi_api",
    }


def collect_market_rows(all_lines: list[str]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in all_lines:
        ts = get_ts(line)
        m = WATCH_RE.search(line)
        if m:
            market = m.group("market")
            row = rows.setdefault(
                market,
                {
                    "market": market,
                    "watch_close_time": "",
                    "watch_status": "",
                    "first_seen_ts": ts,
                    "last_seen_ts": ts,
                    "heartbeat_count": 0,
                },
            )
            row["watch_close_time"] = m.group("close_time") or row.get("watch_close_time") or ""
            row["watch_status"] = m.group("status") or row.get("watch_status") or ""
            if ts:
                if not row.get("first_seen_ts") or ts < row.get("first_seen_ts"):
                    row["first_seen_ts"] = ts
                if not row.get("last_seen_ts") or ts > row.get("last_seen_ts"):
                    row["last_seen_ts"] = ts
            continue
        m = HEARTBEAT_RE.search(line)
        if m:
            market = m.group("watch")
            row = rows.setdefault(
                market,
                {
                    "market": market,
                    "watch_close_time": "",
                    "watch_status": "",
                    "first_seen_ts": ts,
                    "last_seen_ts": ts,
                    "heartbeat_count": 0,
                },
            )
            row["heartbeat_count"] = int(row.get("heartbeat_count") or 0) + 1
            if ts:
                if not row.get("first_seen_ts") or ts < row.get("first_seen_ts"):
                    row["first_seen_ts"] = ts
                if not row.get("last_seen_ts") or ts > row.get("last_seen_ts"):
                    row["last_seen_ts"] = ts
    return rows


def load_execution_entry_attempt_summary(path: Path) -> dict[str, int]:
    summary = {
        "approved_signals": 0,
        "entry_signals": 0,
        "order_submit_start": 0,
        "order_submit_success": 0,
        "zero_fill_orders": 0,
        "filled_entry_orders": 0,
    }
    if not path.exists():
        return summary
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return summary
    for raw in lines:
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        event_type = str(payload.get("event_type") or "")
        if event_type == "mushroom_v28_approved":
            summary["approved_signals"] += 1
        elif event_type == "signal_seen":
            summary["entry_signals"] += 1
        elif event_type == "order_submit_start":
            summary["order_submit_start"] += 1
        elif event_type == "order_submit_success":
            summary["order_submit_success"] += 1
            try:
                fill_count = int(float(payload.get("fill_count") or 0))
            except Exception:
                fill_count = 0
            if fill_count > 0:
                summary["filled_entry_orders"] += 1
            else:
                summary["zero_fill_orders"] += 1
    return summary


def load_lifecycle_summary(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": str(path),
        "present": path.exists(),
        "events": 0,
        "event_counts": {},
        "actions": {},
        "buckets": {},
        "reward_delta_cents": 0.0,
        "entry_quality_cents": 0.0,
        "exit_quality_cents": 0.0,
        "addon_impact_cents": 0.0,
        "fee_saved_cents": 0.0,
        "suppressed_exits": 0,
        "delayed_exits": 0,
        "addon_caps": 0,
    }
    if not path.exists():
        return summary
    event_counts: collections.Counter[str] = collections.Counter()
    actions: collections.Counter[str] = collections.Counter()
    buckets: collections.Counter[str] = collections.Counter()
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return summary
    for raw in lines:
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        summary["events"] += 1
        event = str(payload.get("event") or "")
        action = str(payload.get("action") or "")
        bucket = str(payload.get("bucket") or "")
        if event:
            event_counts[event] += 1
        if action:
            actions[action] += 1
            if action.startswith("suppress"):
                summary["suppressed_exits"] += 1
            if action.startswith("delay"):
                summary["delayed_exits"] += 1
            if action == "cap_addon":
                summary["addon_caps"] += 1
        if bucket:
            buckets[bucket] += 1
        if event == "lifecycle_settlement_reward":
            summary["reward_delta_cents"] += float(payload.get("reward_delta_cents") or 0.0)
            summary["entry_quality_cents"] += float(payload.get("entry_quality_cents") or 0.0)
            summary["exit_quality_cents"] += float(payload.get("exit_quality_cents") or 0.0)
            summary["addon_impact_cents"] += float(payload.get("addon_impact_cents") or 0.0)
            summary["fee_saved_cents"] += float(payload.get("fee_saved_cents") or 0.0)
    summary["event_counts"] = dict(event_counts)
    summary["actions"] = dict(actions)
    summary["buckets"] = dict(buckets)
    for key in ("reward_delta_cents", "entry_quality_cents", "exit_quality_cents", "addon_impact_cents", "fee_saved_cents"):
        summary[key] = round(float(summary[key]), 4)
    return summary


def load_lease_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, int]]:
    if not path.exists():
        return [], {}, {}
    rows_by_market: dict[str, dict[str, Any]] = {}
    event_counts: collections.Counter[str] = collections.Counter()
    for raw in read_text_forgiving(path).splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        event_type = str(payload.get("event_type") or "")
        if not event_type:
            continue
        event_counts[event_type] += 1
        if event_type != "lease_issued":
            continue
        market = str(payload.get("market") or "").strip()
        if not market:
            continue
        row = {
            "market": market,
            "ts_wall": normalize_ts_wall_to_local(payload.get("ts_wall")),
            "mode": str(payload.get("mode") or ""),
            "issuer": str(payload.get("issuer") or ""),
            "decision": str(payload.get("decision") or ""),
            "valid": bool(payload.get("valid")),
            "parse_error": str(payload.get("parse_error") or ""),
            "candidate_profile_if_allowed": str(payload.get("candidate_profile_if_allowed") or ""),
            "confidence": payload.get("confidence", ""),
            "rationale_code": str(payload.get("rationale_code") or ""),
            "summary_reason": str(payload.get("summary_reason") or ""),
        }
        rows_by_market[market] = row
    rows = sorted(rows_by_market.values(), key=lambda row: (str(row.get("ts_wall") or ""), str(row.get("market") or "")))
    return rows, rows_by_market, dict(event_counts)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> None:
    strategy_tag, source_tag, score_mode, log_dir, csv_path, json_path, market_results_csv, market_results_json, _, execution_events_path = resolve_strategy_paths()
    lease_events_path, lease_events_csv, lease_summary_json = resolve_lease_paths()
    log_files = discover_log_files(log_dir)
    if not log_files:
        raise SystemExit(f"No log files found in {log_dir}")

    all_lines: list[str] = []
    for lf in log_files:
        all_lines.extend(read_text_forgiving(lf).splitlines())
    all_lines = filter_lines_by_score_mode(all_lines, score_mode)

    raw_entry_lines = [line for line in all_lines if "ENTRY signal |" in line]
    raw_exit_lines = [line for line in all_lines if "EXIT signal |" in line]

    market_rows = collect_market_rows(all_lines)
    traded_markets: set[str] = set()
    exclude_markets, exclude_entry_keys = load_manual_exclusions()

    open_trades: list[dict[str, Any]] = []
    final_rows: list[dict[str, Any]] = []
    latest_entry_signal: dict[tuple[str, str], dict[str, Any]] = {}
    latest_exit_signal: dict[tuple[str, str], dict[str, Any]] = {}

    for line in all_lines:
        m = ENTRY_RE.search(line)
        if m:
            market = m.group("market")
            if normalize_key(market) in exclude_markets:
                continue
            traded_markets.add(market)
            side = m.group("side")
            latest_entry_signal[(market, side)] = {
                "entry_ts": get_ts(line),
                "trigger": int(m.group("trigger")),
                "limit": int(m.group("limit")),
                "qty": quantity_number(m.group("qty")),
            }
            continue

        m = EXIT_RE.search(line)
        if m:
            market = m.group("market")
            if normalize_key(market) in exclude_markets:
                continue
            traded_markets.add(market)
            side = m.group("side")
            latest_exit_signal[(market, side)] = {
                "exit_ts": get_ts(line),
                "trigger": int(m.group("trigger")),
                "limit": int(m.group("limit")),
                "qty": quantity_number(m.group("qty")),
            }
            continue

        m = ENTRY_FILL_RE.search(line) or DRY_ENTRY_FILL_RE.search(line)
        if m:
            market = m.group("market")
            side = m.group("side")
            if normalize_key(market) in exclude_markets:
                continue
            qty = quantity_number(m.group("qty"))
            traded_markets.add(market)
            signal = latest_entry_signal.get((market, side), {})
            entry_fill_assumed = cents_number(m.group("limit")) if m.groupdict().get("limit") else cents_number(signal.get("limit", 0) or 0)
            entry_fill_actual = cents_number(m.group("fill")) if m.groupdict().get("fill") else ""
            entry_fee_cents = fee_cents_number(m.group("fee")) if m.groupdict().get("fee") else 0
            entry_fill_used = entry_fill_actual or entry_fill_assumed
            if entry_fill_used <= 0:
                continue
            entry_ts = signal.get("entry_ts") or get_ts(line)
            entry_fill_event_ts = get_ts(line) or entry_ts
            exclusion_key = normalize_key(f"{market}|{side}|{entry_ts}")
            if exclusion_key in exclude_entry_keys:
                continue
            entry_basis = cents_to_dollars(entry_fill_used, qty)
            existing_open = None
            for tr in reversed(open_trades):
                if tr["market"] == market and tr["side"] == side and tr["outcome"] == "open":
                    existing_open = tr
                    break
            if existing_open is not None:
                prior_qty = quantity_number(existing_open.get("qty"))
                existing_open["qty"] = prior_qty + qty
                existing_open["entry_fill_cents_assumed"] = weighted_cents(existing_open.get("entry_fill_cents_assumed", ""), prior_qty, entry_fill_assumed, qty)
                existing_open["entry_fill_cents_actual"] = weighted_cents(existing_open.get("entry_fill_cents_actual", ""), prior_qty, entry_fill_actual, qty)
                existing_open["entry_fill_cents_used"] = weighted_cents(existing_open.get("entry_fill_cents_used", ""), prior_qty, entry_fill_used, qty)
                existing_open["entry_fee_cents"] = round(
                    fee_cents_number(existing_open.get("entry_fee_cents", 0)) + entry_fee_cents,
                    4,
                )
                existing_open["total_fees_dollars"] = round(
                    (fee_cents_number(existing_open.get("entry_fee_cents", 0)) + fee_cents_number(existing_open.get("exit_fee_cents", 0))) / 100.0,
                    4,
                )
                existing_open["entry_notional_dollars"] = round(float(existing_open.get("entry_notional_dollars", 0.0) or 0.0) + entry_basis, 4)
                if not existing_open.get("entry_ts"):
                    existing_open["entry_ts"] = entry_ts
                if not existing_open.get("entry_trigger_cents"):
                    existing_open["entry_trigger_cents"] = signal.get("trigger", "")
                existing_open["entry_fill_event_ts_list"] = append_timestamp_list(existing_open.get("entry_fill_event_ts_list", ""), entry_fill_event_ts)
                continue
            open_trades.append(
                {
                    "entry_ts": entry_ts,
                    "entry_fill_event_ts_list": entry_fill_event_ts,
                    "market": market,
                    "side": side,
                    "qty": qty,
                    "entry_trigger_cents": signal.get("trigger", ""),
                    "entry_fill_cents_assumed": entry_fill_assumed,
                    "entry_fill_cents_actual": entry_fill_actual,
                    "entry_fill_cents_used": entry_fill_used,
                    "entry_fee_cents": entry_fee_cents,
                    "exit_fee_cents": 0,
                    "total_fees_dollars": round(entry_fee_cents / 100.0, 4),
                    "entry_notional_dollars": entry_basis,
                    "exit_ts": "",
                    "exit_trigger_cents": "",
                    "exit_fill_cents_assumed": "",
                    "exit_fill_cents_actual": "",
                    "exit_fill_cents_used": "",
                    "exit_fill_event_ts_list": "",
                    "exit_notional_dollars": "",
                    "outcome": "open",
                    "resolution_source": "",
                    "result": "",
                    "gross_pnl_dollars": "",
                    "net_pnl_dollars": "",
                    "net_pnl_percent": "",
                    "gross_pnl_percent": "",
                    "market_status": "",
                    "market_result": "",
                    "settlement_ts": "",
                }
            )
            continue

        m = EXIT_FILL_RE.search(line) or DRY_EXIT_FILL_RE.search(line)
        if m:
            market = m.group("market")
            side = m.group("side")
            if normalize_key(market) in exclude_markets:
                continue
            traded_markets.add(market)
            signal = latest_exit_signal.get((market, side), {})
            for tr in reversed(open_trades):
                if tr["market"] == market and tr["side"] == side and tr["outcome"] == "open":
                    final_row = finalize_exit_trade(
                        tr,
                        exit_ts=str(signal.get("exit_ts") or get_ts(line) or ""),
                        exit_trigger_cents=signal.get("trigger", ""),
                        exit_fill_assumed=signal.get("limit", 0) or 0,
                        exit_fill_actual=cents_number(m.group("fill")) if m.groupdict().get("fill") else "",
                        exit_fee_cents=fee_cents_number(m.group("fee")) if m.groupdict().get("fee") else 0,
                        resolution_source="bot_exit_signal",
                        exit_fill_event_ts=get_ts(line),
                    )
                    if final_row is None:
                        break
                    final_rows.append(final_row)
                    tr["outcome"] = "paired_and_closed"
                    break
            continue

        m = HEARTBEAT_RE.search(line)
        if m and score_mode != "live_only" and str(m.group("position") or "").lower() == "false":
            market = m.group("watch")
            if normalize_key(market) in exclude_markets:
                continue
            heartbeat_ts = get_ts(line)
            for tr in reversed(open_trades):
                if tr["market"] != market or tr["outcome"] != "open":
                    continue
                side = str(tr.get("side") or "")
                signal = latest_exit_signal.get((market, side), {})
                signal_ts = str(signal.get("exit_ts") or "")
                if not signal_ts:
                    continue
                entry_ts = str(tr.get("entry_ts") or "")
                if entry_ts and signal_ts < entry_ts:
                    continue
                if heartbeat_ts and signal_ts and heartbeat_ts < signal_ts:
                    continue
                final_row = finalize_exit_trade(
                    tr,
                    exit_ts=heartbeat_ts or signal_ts,
                    exit_trigger_cents=signal.get("trigger", ""),
                    exit_fill_assumed=signal.get("limit", 0) or 0,
                    exit_fill_actual="",
                    exit_fee_cents=0,
                    resolution_source="bot_exit_signal_heartbeat_confirmed",
                    exit_fill_event_ts=heartbeat_ts or signal_ts,
                )
                if final_row is None:
                    continue
                final_rows.append(final_row)
                tr["outcome"] = "paired_and_closed"
            continue

    for market in traded_markets:
        if normalize_key(market) in exclude_markets:
            continue
        market_rows.setdefault(
            market,
            {
                "market": market,
                "watch_close_time": "",
                "watch_status": "",
                "first_seen_ts": "",
                "last_seen_ts": "",
                "heartbeat_count": 0,
            },
        )

    exit_events = load_execution_exit_events(execution_events_path)
    for event in exit_events:
        market = str(event.get("market") or "")
        side = str(event.get("side") or "")
        if normalize_key(market) in exclude_markets:
            continue
        signal = latest_exit_signal.get((market, side), {})
        for tr in reversed(open_trades):
            if tr["market"] == market and tr["side"] == side and tr["outcome"] == "open":
                entry_ts = str(tr.get("entry_ts") or "")
                event_ts = str(event.get("exit_ts") or "")
                signal_ts = str(signal.get("exit_ts") or "")
                if entry_ts and event_ts and event_ts < entry_ts:
                    continue
                if entry_ts and signal_ts and signal_ts < entry_ts:
                    signal = {}
                final_row = finalize_exit_trade(
                    tr,
                    exit_ts=str(signal.get("exit_ts") or event.get("exit_ts") or ""),
                    exit_trigger_cents=signal.get("trigger", ""),
                    exit_fill_assumed=int(signal.get("limit", 0) or event.get("fill_cents") or 0),
                    exit_fill_actual=int(event.get("fill_cents") or 0) if int(event.get("fill_cents") or 0) > 0 else "",
                    exit_fee_cents=fee_cents_number(event.get("fee_cents") or 0),
                    resolution_source="execution_telemetry_exit",
                    exit_fill_event_ts=event.get("exit_ts") or "",
                )
                if final_row is None:
                    break
                final_rows.append(final_row)
                tr["outcome"] = "paired_and_closed"
                break

    cache = load_cache()
    session = requests.Session()
    session.headers.update({"User-Agent": "kalshi-btc15m-score/1.0"})

    result_rows: list[dict[str, Any]] = []
    for market in sorted(market_rows.keys()):
        if normalize_key(market) in exclude_markets:
            continue
        cached = cache.get(market, {})
        payload: dict[str, Any]
        if cached and is_final_market(cached):
            payload = dict(cached)
            payload["source"] = payload.get("source") or "cache"
        else:
            try:
                payload = fetch_market_result(session, market)
                cache[market] = payload
            except Exception as exc:
                payload = dict(cached) if cached else {"market": market}
                payload.setdefault("result", "")
                payload.setdefault("status", "")
                payload.setdefault("settlement_ts", "")
                payload.setdefault("close_time", "")
                payload["source"] = f"api_error: {exc}"

        meta = market_rows.get(market, {})
        result_rows.append(
            {
                "market": market,
                "result": payload.get("result", ""),
                "status": payload.get("status", ""),
                "settlement_ts": payload.get("settlement_ts", ""),
                "close_time": payload.get("close_time", "") or meta.get("watch_close_time", ""),
                "watch_close_time": meta.get("watch_close_time", ""),
                "watch_status": meta.get("watch_status", ""),
                "first_seen_ts": meta.get("first_seen_ts", ""),
                "last_seen_ts": meta.get("last_seen_ts", ""),
                "heartbeat_count": meta.get("heartbeat_count", 0),
                "source": payload.get("source", ""),
            }
        )

    save_cache(cache)

    result_lookup = {row["market"]: row for row in result_rows}

    for tr in open_trades:
        if tr["outcome"] != "open":
            continue
        info = result_lookup.get(tr["market"], {})
        result = str(info.get("result") or "").lower()
        status = str(info.get("status") or "")
        settlement_ts = str(info.get("settlement_ts") or "")

        tr["result"] = result
        tr["market_result"] = result
        tr["market_status"] = status
        tr["settlement_ts"] = settlement_ts
        tr["resolution_source"] = str(info.get("source") or "")

        basis = tr["entry_notional_dollars"]
        qty = tr["qty"]
        entry_fill = tr["entry_fill_cents_used"]

        if result in {"yes", "no"}:
            if tr["side"] == result:
                pnl = round(((100 - entry_fill) * qty) / 100.0, 4)
                tr["outcome"] = "win"
            else:
                pnl = round((0 - entry_fill * qty) / 100.0, 4)
                tr["outcome"] = "loss"
            tr["gross_pnl_dollars"] = pnl
            tr["net_pnl_dollars"] = net_pnl_after_fees(pnl, tr.get("entry_fee_cents", 0), tr.get("exit_fee_cents", 0))
            tr["net_pnl_percent"] = pct(float(tr["net_pnl_dollars"]), basis)
            tr["gross_pnl_percent"] = pct(pnl, basis)
        elif result == "void":
            tr["outcome"] = "void"
            tr["gross_pnl_dollars"] = 0.0
            tr["net_pnl_dollars"] = 0.0
            tr["net_pnl_percent"] = 0.0
            tr["gross_pnl_percent"] = 0.0
        else:
            tr["outcome"] = "open"

        final_rows.append(tr)

    final_rows = sorted(final_rows, key=lambda x: (x.get("entry_ts", ""), x.get("market", ""), x.get("side", "")))
    apply_manual_trade_overrides(final_rows)
    api_accounting_fills, api_accounting_summary = fetch_kalshi_api_accounting_fills(final_rows, csv_path.parent)
    accounting_summary = apply_exchange_fill_overrides(final_rows, log_dir, api_accounting_fills)
    accounting_summary["api_fetch"] = api_accounting_summary
    accounting_summary["reconciliation_json"] = str(accounting_reconciliation_path(csv_path.parent))
    lease_rows, lease_by_market, lease_event_counts = load_lease_events(lease_events_path)

    entries_total = len(final_rows)
    completed_round_trips = sum(1 for r in final_rows if r["outcome"] == "exited_before_settlement")
    confirmed_wins = sum(1 for r in final_rows if r["outcome"] == "win")
    confirmed_losses = sum(1 for r in final_rows if r["outcome"] == "loss")
    confirmed_wins_by_sign = sum(
        1
        for r in final_rows
        if str(r.get("gross_pnl_dollars", "")) != "" and float(r.get("gross_pnl_dollars", 0.0) or 0.0) > 0
    )
    confirmed_losses_by_sign = sum(
        1
        for r in final_rows
        if str(r.get("gross_pnl_dollars", "")) != "" and float(r.get("gross_pnl_dollars", 0.0) or 0.0) < 0
    )
    voids = sum(1 for r in final_rows if r["outcome"] == "void")
    open_positions = sum(1 for r in final_rows if r["outcome"] == "open")

    gross_cost_basis_dollars = round(
        sum(float(r["entry_notional_dollars"]) for r in final_rows if str(r["entry_notional_dollars"]) != ""),
        4,
    )
    gross_pnl_total_dollars = round(
        sum(float(r["gross_pnl_dollars"]) for r in final_rows if str(r["gross_pnl_dollars"]) != ""),
        4,
    )
    gross_pnl_total_percent = pct(gross_pnl_total_dollars, gross_cost_basis_dollars)
    net_pnl_total_dollars = round(sum(float(r["net_pnl_dollars"]) for r in final_rows if str(r.get("net_pnl_dollars", "")) != ""), 4)
    net_pnl_total_percent = pct(net_pnl_total_dollars, gross_cost_basis_dollars)

    trades_by_market: dict[str, list[dict[str, Any]]] = {}
    for row in final_rows:
        trades_by_market.setdefault(str(row.get("market") or ""), []).append(row)
    for lease_row in lease_rows:
        trade_rows = trades_by_market.get(str(lease_row.get("market") or ""), [])
        lease_row["trade_count"] = len(trade_rows)
        lease_row["trade_net_pnl_total_dollars"] = round(
            sum(float(tr.get("net_pnl_dollars", 0.0) or 0.0) for tr in trade_rows if str(tr.get("net_pnl_dollars", "")) != ""),
            4,
        )
        lease_row["trade_outcomes"] = ",".join(str(tr.get("outcome") or "") for tr in trade_rows)

    blocked_trade_rows = [
        row for row in final_rows
        if str(lease_by_market.get(str(row.get("market") or ""), {}).get("decision") or "") == "BLOCK_NEXT_MARKET"
    ]
    allowed_trade_rows = [
        row for row in final_rows
        if str(lease_by_market.get(str(row.get("market") or ""), {}).get("decision") or "") == "ALLOW_90_78_NEXT_MARKET"
    ]
    blocked_trade_net_pnl_total_dollars = round(
        sum(float(row.get("net_pnl_dollars", 0.0) or 0.0) for row in blocked_trade_rows if str(row.get("net_pnl_dollars", "")) != ""),
        4,
    )
    allowed_trade_net_pnl_total_dollars = round(
        sum(float(row.get("net_pnl_dollars", 0.0) or 0.0) for row in allowed_trade_rows if str(row.get("net_pnl_dollars", "")) != ""),
        4,
    )
    lease_summary = {
        "lease_events_path": str(lease_events_path),
        "lease_events_present": lease_events_path.exists(),
        "lease_markets_issued": len(lease_rows),
        "lease_allow_markets": sum(1 for row in lease_rows if str(row.get("decision") or "") == "ALLOW_90_78_NEXT_MARKET"),
        "lease_block_markets": sum(1 for row in lease_rows if str(row.get("decision") or "") == "BLOCK_NEXT_MARKET"),
        "lease_invalid_issue_count": sum(1 for row in lease_rows if not bool(row.get("valid"))),
        "lease_cache_miss_count": int(lease_event_counts.get("lease_cache_miss", 0)),
        "lease_invalid_runtime_count": int(lease_event_counts.get("lease_invalid", 0)),
        "lease_stale_count": int(lease_event_counts.get("lease_stale", 0)),
        "lease_shadow_block_count": int(lease_event_counts.get("lease_shadow_block", 0)),
        "lease_enforced_block_count": int(lease_event_counts.get("lease_enforced_block", 0)),
        "blocked_trade_count": len(blocked_trade_rows),
        "blocked_trade_wins": sum(1 for row in blocked_trade_rows if float(row.get("net_pnl_dollars", 0.0) or 0.0) > 0),
        "blocked_trade_losses": sum(1 for row in blocked_trade_rows if float(row.get("net_pnl_dollars", 0.0) or 0.0) < 0),
        "blocked_trade_net_pnl_total_dollars": blocked_trade_net_pnl_total_dollars,
        "allowed_trade_count": len(allowed_trade_rows),
        "allowed_trade_net_pnl_total_dollars": allowed_trade_net_pnl_total_dollars,
    }

    write_csv(
        csv_path,
        final_rows,
        [
            "entry_ts",
            "market",
            "side",
            "qty",
            "entry_trigger_cents",
            "entry_fill_event_ts_list",
            "entry_fill_cents_assumed",
            "entry_fill_cents_actual",
            "entry_fill_cents_used",
            "entry_accounting_source",
            "entry_fee_cents",
            "entry_notional_dollars",
            "entry_exchange_qty",
            "entry_exchange_fill_ids",
            "entry_api_fill_ids",
            "exit_ts",
            "exit_trigger_cents",
            "exit_fill_event_ts_list",
            "exit_fill_cents_assumed",
            "exit_fill_cents_actual",
            "exit_fill_cents_used",
            "exit_accounting_source",
            "exit_fee_cents",
            "exit_notional_dollars",
            "exit_exchange_qty",
            "exit_exchange_fill_ids",
            "exit_api_fill_ids",
            "total_fees_dollars",
            "outcome",
            "resolution_source",
            "accounting_source",
            "result",
            "gross_pnl_dollars",
            "net_pnl_dollars",
            "net_pnl_percent",
            "gross_pnl_percent",
            "market_status",
            "market_result",
            "settlement_ts",
        ],
    )

    result_rows_sorted = sorted(result_rows, key=lambda x: (x.get("close_time", ""), x.get("market", "")))
    write_csv(
        market_results_csv,
        result_rows_sorted,
        [
            "market",
            "result",
            "status",
            "settlement_ts",
            "close_time",
            "watch_close_time",
            "watch_status",
            "first_seen_ts",
            "last_seen_ts",
            "heartbeat_count",
            "source",
        ],
    )
    market_results_json.write_text(json.dumps(result_rows_sorted, indent=2), encoding="utf-8")
    if lease_rows:
        write_csv(
            lease_events_csv,
            lease_rows,
            [
                "ts_wall",
                "market",
                "mode",
                "issuer",
                "decision",
                "valid",
                "parse_error",
                "candidate_profile_if_allowed",
                "confidence",
                "rationale_code",
                "summary_reason",
                "trade_count",
                "trade_net_pnl_total_dollars",
                "trade_outcomes",
            ],
        )
    lease_summary_json.write_text(json.dumps(lease_summary, indent=2), encoding="utf-8")

    entry_attempt_summary = load_execution_entry_attempt_summary(execution_events_path)
    lifecycle_summary = load_lifecycle_summary(log_dir / "v28_trade_lifecycle.ndjson")

    diagnosis = "ok"
    if raw_entry_lines and not entries_total and entry_attempt_summary.get("zero_fill_orders", 0) > 0:
        diagnosis = "entry signals submitted but zero filled; no filled entries to score"
    elif raw_entry_lines and not entries_total:
        diagnosis = "entry lines exist but no filled entry lines were found"
    elif not raw_entry_lines:
        diagnosis = "no entry lines found in scanned logs"

    resolved_markets = sum(1 for row in result_rows if str(row.get("result") or "").lower() in {"yes", "no", "void"})
    unresolved_markets = sum(1 for row in result_rows if str(row.get("result") or "").lower() not in {"yes", "no", "void"})

    summary = {
        "log_files_scanned": [str(x) for x in log_files],
        "raw_entry_lines_found": len(raw_entry_lines),
        "raw_exit_lines_found": len(raw_exit_lines),
        "entries_total": entries_total,
        "completed_round_trips": completed_round_trips,
        "confirmed_wins": confirmed_wins,
        "confirmed_losses": confirmed_losses,
        "confirmed_wins_by_sign": confirmed_wins_by_sign,
        "confirmed_losses_by_sign": confirmed_losses_by_sign,
        "voids": voids,
        "open_positions": open_positions,
        "gross_cost_basis_dollars": gross_cost_basis_dollars,
        "gross_pnl_total_dollars": gross_pnl_total_dollars,
        "net_pnl_total_dollars": net_pnl_total_dollars,
        "net_pnl_total_percent": net_pnl_total_percent,
        "gross_pnl_total_percent": gross_pnl_total_percent,
        "resolved_markets": resolved_markets,
        "unresolved_markets": unresolved_markets,
        "strategy_tag": strategy_tag,
        "log_source_tag": source_tag,
        "score_mode": score_mode,
        "csv": str(csv_path),
        "market_results_csv": str(market_results_csv),
        "execution_events_path": str(execution_events_path),
        "execution_events_present": execution_events_path.exists(),
        "accounting_source": accounting_summary.get("source_label", "bot_log_estimate"),
        "accounting_reconciliation_json": str(accounting_reconciliation_path(csv_path.parent)),
        "accounting": accounting_summary,
        "kalshi_api_accounting_enabled": bool(api_accounting_summary.get("enabled")),
        "kalshi_api_accounting_authenticated": bool(api_accounting_summary.get("authenticated")),
        "kalshi_api_accounting_fill_count": int(api_accounting_summary.get("normalized_api_fill_count") or 0),
        "accounting_entry_rows_matched_api": int(accounting_summary.get("entry_rows_matched_api") or 0),
        "accounting_exit_rows_matched_api": int(accounting_summary.get("exit_rows_matched_api") or 0),
        "accounting_unmatched_entries": int(accounting_summary.get("unmatched_entries") or 0),
        "accounting_unmatched_realized_exits": int(accounting_summary.get("unmatched_realized_exits") or 0),
        "entry_attempt_summary": entry_attempt_summary,
        "lifecycle_summary": lifecycle_summary,
        "lease_events_path": str(lease_events_path),
        "lease_events_present": lease_events_path.exists(),
        "lease_events_csv": str(lease_events_csv),
        "lease_summary_json": str(lease_summary_json),
        "lease_markets_issued": lease_summary["lease_markets_issued"],
        "lease_block_markets": lease_summary["lease_block_markets"],
        "blocked_trade_count": lease_summary["blocked_trade_count"],
        "blocked_trade_net_pnl_total_dollars": lease_summary["blocked_trade_net_pnl_total_dollars"],
        "diagnosis": diagnosis,
    }

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print()
    print(f"Wrote {csv_path}")
    print(f"Wrote {market_results_csv}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    write_score_refresh_lock("running")
    try:
        main()
    finally:
        clear_score_refresh_lock()
