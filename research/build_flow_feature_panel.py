#!/usr/bin/env python3
"""Build label-free causal taker-flow features at every archived KXBTC15M book snapshot."""
from __future__ import annotations

import argparse, gzip, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd

WINDOWS = (0.5, 1.0, 2.0, 5.0, 10.0, 30.0)


def iso_ns(x):
    t = pd.to_datetime(x, utc=True, errors="coerce")
    return None if pd.isna(t) else int(t.value)


def digest(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_binary(paths):
    snaps, trades = [], []
    for path in sorted(paths):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o.get("type") == "snapshot":
                    m = o.get("market") or {}
                    snaps.append({
                        "ticker": str(o.get("ticker") or m.get("ticker") or ""),
                        "received_ns": int(o["received_ns"]),
                        "open_ns": iso_ns(m.get("open_time")),
                        "close_ns": iso_ns(m.get("close_time")),
                        "capture_file": path.name,
                    })
                elif o.get("type") == "trade":
                    side = str(o.get("taker_outcome_side") or o.get("taker_side") or "").lower()
                    if side not in {"yes", "no"}:
                        continue
                    q = float(o.get("count_fp") or 0.0)
                    sign = 1.0 if side == "yes" else -1.0
                    trades.append({
                        "ticker": str(o.get("ticker") or ""),
                        "trade_id": str(o.get("trade_id") or ""),
                        "received_ns": int(o["received_ns"]),
                        "signed_contracts": sign * q,
                        "gross_contracts": q,
                        "signed_trades": sign,
                        "gross_trades": 1.0,
                        "yes_trade_price": float(o.get("yes_price_dollars") or math.nan),
                        "source_file": path.name,
                    })
    s = pd.DataFrame(snaps).sort_values(["ticker", "received_ns", "capture_file"]).drop_duplicates(["ticker", "received_ns"], keep="last")
    t = pd.DataFrame(trades).sort_values(["received_ns", "trade_id", "source_file"])
    if not t.empty:
        have_id = t.trade_id.ne("")
        t = pd.concat([t[have_id].drop_duplicates("trade_id", keep="last"), t[~have_id]], ignore_index=True).sort_values("received_ns")
    return s, t


def parse_perp(paths):
    rows = []
    for path in sorted(paths):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o.get("type") != "trade":
                    continue
                side = str(o.get("taker_side") or "").lower()
                if side not in {"bid", "ask"}:
                    continue
                q = float(o.get("count") or 0.0)
                # ask = buyer-initiated; bid = seller-initiated
                sign = 1.0 if side == "ask" else -1.0
                rows.append({
                    "trade_id": str(o.get("trade_id") or ""),
                    "received_ns": int(o["received_ns"]),
                    "signed_contracts": sign * q,
                    "gross_contracts": q,
                    "signed_trades": sign,
                    "gross_trades": 1.0,
                    "underlying_price_usd": float(o.get("underlying_price_usd") or math.nan),
                    "source_file": path.name,
                })
    t = pd.DataFrame(rows).sort_values(["received_ns", "trade_id", "source_file"])
    if not t.empty:
        have_id = t.trade_id.ne("")
        t = pd.concat([t[have_id].drop_duplicates("trade_id", keep="last"), t[~have_id]], ignore_index=True).sort_values("received_ns")
    return t


def window_features(query_ns, trades, prefix):
    n = len(query_ns)
    if trades.empty:
        return {f"{prefix}_{name}_{str(w).replace('.', 'p')}s": np.zeros(n) for w in WINDOWS for name in ("signed_contracts", "gross_contracts", "signed_trades", "gross_trades")}
    ts = trades.received_ns.to_numpy(np.int64)
    right = np.searchsorted(ts, query_ns, side="right")
    values = {name: trades[name].to_numpy(float) for name in ("signed_contracts", "gross_contracts", "signed_trades", "gross_trades")}
    csum = {name: np.r_[0.0, np.cumsum(v)] for name, v in values.items()}
    out = {}
    for w in WINDOWS:
        left = np.searchsorted(ts, query_ns - int(w * 1e9), side="left")
        tag = str(w).replace(".", "p") + "s"
        for name, cs in csum.items():
            out[f"{prefix}_{name}_{tag}"] = cs[right] - cs[left]
    return out


def build_live(snaps, binary, perp):
    pieces = []
    groups = {k: g.sort_values("received_ns") for k, g in binary.groupby("ticker", sort=False)}
    for ticker, s in snaps.groupby("ticker", sort=False):
        s = s.sort_values("received_ns").reset_index(drop=True)
        b = groups.get(ticker, pd.DataFrame(columns=binary.columns))
        qns = s.received_ns.to_numpy(np.int64)
        feat = window_features(qns, b, "binary")
        if b.empty:
            feat.update({"binary_signed_contracts_since_open": np.zeros(len(s)), "binary_gross_contracts_since_open": np.zeros(len(s)), "binary_last_trade_age_seconds": np.full(len(s), np.nan)})
        else:
            ts = b.received_ns.to_numpy(np.int64)
            right = np.searchsorted(ts, qns, side="right")
            left = np.searchsorted(ts, s.open_ns.fillna(s.received_ns).to_numpy(np.int64), side="left")
            for name in ("signed_contracts", "gross_contracts"):
                cs = np.r_[0.0, np.cumsum(b[name].to_numpy(float))]
                feat[f"binary_{name}_since_open"] = cs[right] - cs[left]
            last = right - 1
            age = np.full(len(s), np.nan)
            ok = last >= 0
            age[ok] = (qns[ok] - ts[last[ok]]) / 1e9
            feat["binary_last_trade_age_seconds"] = age
        pieces.append(pd.concat([s, pd.DataFrame(feat)], axis=1))
    live = pd.concat(pieces, ignore_index=True).sort_values(["ticker", "received_ns"]).reset_index(drop=True)
    live = pd.concat([live, pd.DataFrame(window_features(live.received_ns.to_numpy(np.int64), perp, "perp"))], axis=1)
    ratios = {}
    for prefix in ("binary", "perp"):
        for w in WINDOWS:
            tag = str(w).replace(".", "p") + "s"
            for unit in ("contracts", "trades"):
                a, b = f"{prefix}_signed_{unit}_{tag}", f"{prefix}_gross_{unit}_{tag}"
                ratios[f"{prefix}_{unit}_imbalance_{tag}"] = np.divide(live[a], live[b], out=np.zeros(len(live)), where=live[b].to_numpy() > 0)
    live = pd.concat([live, pd.DataFrame(ratios)], axis=1)
    live["market_day_utc"] = pd.to_datetime(live.close_ns, unit="ns", utc=True).dt.strftime("%Y-%m-%d")
    return live


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    bp = sorted((a.root / "kalshi_15m_live").glob("KXBTC15M-*.jsonl.gz"))
    pp = sorted((a.root / "kalshi_perp").glob("KXBTCPERP-*.jsonl.gz"))
    tp = sorted((a.root / "kalshi_ticks").glob("KXBTC15M-1s-*.csv.gz"))
    if not bp:
        raise RuntimeError("no live KXBTC15M captures")
    snaps, binary = parse_binary(bp); perp = parse_perp(pp)
    live = build_live(snaps, binary, perp)
    # The live output is label-free by construction; lockbox labels cannot leak here.
    live.to_parquet(a.output / "live_flow_features.parquet", index=False)
    tick = pd.concat([pd.read_csv(p).assign(source_file=p.name) for p in tp], ignore_index=True) if tp else pd.DataFrame()
    if not tick.empty:
        tick = tick.sort_values(["ticker", "second_utc"]).drop_duplicates(["ticker", "second_utc"], keep="last")
        tick.to_parquet(a.output / "tick_training_1s.parquet", index=False)
    sources = bp + pp + tp
    summary = {
        "binary_capture_files": len(bp), "perp_capture_files": len(pp), "tick_training_files": len(tp),
        "snapshot_rows": len(snaps), "binary_trade_rows": len(binary), "perp_trade_rows": len(perp),
        "live_feature_rows": len(live), "tick_training_rows": len(tick), "live_labels_included": False,
        "causality": "trade received_ns <= snapshot received_ns for every rolling feature",
        "source_hashes": [{"path": str(p.relative_to(a.root)), "bytes": p.stat().st_size, "sha256": digest(p)} for p in sources],
    }
    (a.output / "flow_feature_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "source_hashes"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
