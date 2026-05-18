from __future__ import annotations

import ast
import html
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LEGACY = Path(__file__).with_name("dashboard.py")
KEEP_ASSIGN = {"ROOT","DISPLAY_POSITION_SIZE","KALSHI_TAKER_FEE_RATE","EQUITY_RANGE_OPTIONS","MA_TZ","HEARTBEAT_RE","WATCH_RE","ENTRY_RE","EXIT_RE","LATENCY_RE","LEVEL_RE","VIRTUAL_DATASET_CONFIGS","STRATEGY_PROFILE_DEFAULTS","BOT_CONTROL_CONFIGS","START_RE"}
KEEP_FUNC = {"sanitize_strategy_tag","current_strategy_tag","parse_launcher_env_assignments","load_launcher_env_assignments","humanize_strategy_tag","dataset_uses_actuals","dataset_paths","discover_datasets","read_text_forgiving","read_tail_text_forgiving","discover_log_files","filter_lines_for_dataset","load_log","load_log_bundle","load_trades","load_summary","load_market_results","parse_ts","maybe_num","ensure_ma_datetime","format_ma_time","display_text","format_cents","format_money","format_pct","estimate_kalshi_fee_dollars","normalize_trades","enrich_trades_with_market_results","parse_log_state","make_equity_curve","filter_equity_curve","make_price_series"}

def load_helpers() -> dict[str, Any]:
    tree = ast.parse(LEGACY.read_text(encoding="utf-8"), filename=str(LEGACY))
    body: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            body.append(node)
        elif isinstance(node, ast.Assign):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if names & KEEP_ASSIGN:
                body.append(node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in KEEP_ASSIGN:
            body.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in KEEP_FUNC:
            body.append(node)
    ns: dict[str, Any] = {"__file__": str(LEGACY)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])), str(LEGACY), "exec"), ns)
    return ns

for _k, _v in load_helpers().items():
    if _k in KEEP_ASSIGN or _k in KEEP_FUNC:
        globals()[_k] = _v

st.set_page_config(page_title="BTC15M Overview", page_icon="o", layout="wide", initial_sidebar_state="expanded")


def styles() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');
    .stApp{background:radial-gradient(circle at top left,rgba(132,174,255,.42),transparent 26%),radial-gradient(circle at top right,rgba(255,210,222,.42),transparent 22%),linear-gradient(180deg,#f8f9fc,#eef2f7 60%,#e9eef5);color:#122034;font-family:"Manrope","Avenir Next",sans-serif}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(255,255,255,.84),rgba(247,249,252,.84));border-right:1px solid rgba(94,112,138,.10)}
    .hero,.glass,.metric{background:linear-gradient(180deg,rgba(255,255,255,.86),rgba(247,249,252,.78));border:1px solid rgba(255,255,255,.65);box-shadow:0 20px 60px rgba(28,42,66,.10);backdrop-filter:blur(20px)}
    .hero{border-radius:34px;padding:1.6rem 1.8rem;margin-bottom:1rem}.hero h1{margin:.15rem 0 0 0;font-size:2.45rem;line-height:1.02;letter-spacing:-.05em}.hero p{margin:.85rem 0 0 0;color:#66758b;max-width:58rem;line-height:1.6}
    .kick{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:#5d7697;font-weight:800}
    .chips{display:flex;gap:.65rem;flex-wrap:wrap;margin-top:1rem}.chip{padding:.52rem .82rem;border-radius:999px;background:rgba(255,255,255,.56);border:1px solid rgba(94,112,138,.11);font-size:.83rem;font-weight:700}.live{color:#0e6a4d;background:rgba(23,150,106,.12)}.stale{color:#956a18;background:rgba(184,131,31,.12)}.off{color:#9b3d4b;background:rgba(212,79,95,.12)}
    .metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.9rem;margin-bottom:1rem}.metric{border-radius:26px;padding:1rem 1.05rem}.ml{font-size:.78rem;text-transform:uppercase;letter-spacing:.12em;color:#6d7d95;font-weight:800}.mv{margin-top:.5rem;font-size:2rem;font-weight:800;letter-spacing:-.05em}.mn{margin-top:.32rem;font-size:.87rem;color:#62748d;font-weight:700}
    .spot{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.95rem;margin-bottom:1rem}.glass{border-radius:28px;padding:1rem 1.05rem}.sk{font-size:.73rem;text-transform:uppercase;letter-spacing:.13em;color:#6880a2;font-weight:800}.st{margin-top:.45rem;font-size:1.12rem;font-weight:800;letter-spacing:-.03em}.ss{margin-top:.25rem;color:#66758b;font-size:.92rem;line-height:1.55}.mini{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem;margin-top:.85rem}.cell{border-radius:18px;padding:.75rem .8rem;background:rgba(244,247,251,.82);border:1px solid rgba(94,112,138,.10)}.cl{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:#72839c;font-weight:800}.cv{margin-top:.28rem;font-size:1rem;font-weight:800}.cn{margin-top:.18rem;font-size:.8rem;color:#66758b;line-height:1.45}
    .banner{margin-bottom:1rem;border-radius:24px;padding:1rem 1.05rem;background:linear-gradient(135deg,rgba(238,247,255,.95),rgba(227,239,255,.80));border:1px solid rgba(74,125,230,.16)}
    .trade-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem}.trade{border-radius:24px;padding:1rem;background:linear-gradient(180deg,rgba(255,255,255,.90),rgba(246,248,252,.82));border:1px solid rgba(255,255,255,.68);box-shadow:0 16px 42px rgba(28,42,66,.08)}.tt{display:flex;justify-content:space-between;gap:.8rem;margin-bottom:.75rem}.tm{font-weight:800;font-size:.96rem}.ts{font-size:.84rem;color:#66758b;margin-top:.2rem}.tg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.6rem}.ti{border-radius:15px;padding:.68rem .72rem;background:rgba(244,247,251,.9);border:1px solid rgba(94,112,138,.08)}.ti span{display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.09em;color:#6e7f97;font-weight:800}.ti strong{display:block;margin-top:.26rem;font-size:.96rem}
    .badge{display:inline-flex;border-radius:999px;padding:.2rem .55rem;font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.bw{background:rgba(23,150,106,.12);color:#0f7754}.bl{background:rgba(212,79,95,.12);color:#a43e4d}.bo{background:rgba(51,120,255,.10);color:#225dcc}.bwarn{background:rgba(184,131,31,.12);color:#996d1c}.berr{background:rgba(212,79,95,.12);color:#a43e4d}
    .feed{display:grid;gap:.65rem}.item{border-radius:18px;padding:.78rem .82rem;background:rgba(255,255,255,.82);border:1px solid rgba(94,112,138,.10)}.fh{display:flex;justify-content:space-between;gap:.8rem;font-size:.82rem;font-weight:800;margin-bottom:.2rem}.fc{color:#66758b;font-size:.87rem;line-height:1.5}
    .mono{border-radius:24px;padding:.95rem 1rem;background:linear-gradient(180deg,rgba(20,27,39,.96),rgba(16,22,33,.98));color:#e4eefc;border:1px solid rgba(54,76,111,.45);font-family:"IBM Plex Mono",Consolas,monospace;font-size:.79rem;line-height:1.58;max-height:34rem;overflow:auto;white-space:pre-wrap}
    .side{border-radius:24px;padding:1rem;background:rgba(255,255,255,.72);border:1px solid rgba(94,112,138,.10);box-shadow:0 16px 42px rgba(28,42,66,.08);margin-bottom:.85rem}.side h3{margin:.1rem 0 .25rem 0;font-size:1rem}.side p,.side .meta{font-size:.88rem;color:#66758b;line-height:1.55}.row{display:flex;justify-content:space-between;gap:.75rem;padding:.45rem 0;border-bottom:1px solid rgba(94,112,138,.08)}.row:last-child{border-bottom:none}.row strong{color:#16253d;font-size:.83rem}
    table{width:100%;border-collapse:collapse}th{text-align:left;font-size:.75rem;text-transform:uppercase;letter-spacing:.09em;color:#71839c;padding:.78rem .84rem;border-bottom:1px solid rgba(94,112,138,.14)}td{padding:.84rem;border-bottom:1px solid rgba(94,112,138,.08);font-size:.88rem}tr:last-child td{border-bottom:none}.pos{color:#0f7754;font-weight:800}.neg{color:#a43e4d;font-weight:800}.neu{color:#5e6f87;font-weight:700}
    @media (max-width:1100px){.metric-grid,.spot,.trade-grid,.mini{grid-template-columns:1fr}}
    </style>
    """, unsafe_allow_html=True)


def pnl_cols(df: pd.DataFrame) -> tuple[str, str]:
    if "actual_net_pnl_dollars" in df.columns and "actual_net_pnl_percent" in df.columns:
        return "actual_net_pnl_dollars", "actual_net_pnl_percent"
    if "scaled_net_pnl_dollars" in df.columns and "scaled_net_pnl_percent" in df.columns:
        return "scaled_net_pnl_dollars", "scaled_net_pnl_percent"
    return "gross_pnl_dollars", "gross_pnl_percent"


def mcard(label: str, value: str, note: str) -> str:
    return f'<div class="metric"><div class="ml">{html.escape(label)}</div><div class="mv">{html.escape(value)}</div><div class="mn">{html.escape(note)}</div></div>'


def stat(label: str, value: str, note: str) -> str:
    return f'<div class="cell"><div class="cl">{html.escape(label)}</div><div class="cv">{html.escape(value)}</div><div class="cn">{html.escape(note)}</div></div>'


def status_chip(status: str, detail: str) -> str:
    cls = "chip off"
    if str(status).lower() == "live": cls = "chip live"
    elif str(status).lower() == "stale": cls = "chip stale"
    return f'<div class="{cls}">{html.escape(status)} <span style="color:#6a7a91">{html.escape(detail)}</span></div>'


def chart(fig: go.Figure, *, height: int) -> go.Figure:
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hoverlabel=dict(bgcolor="#fefefe", bordercolor="rgba(104,122,148,.18)", font=dict(color="#12223c")))
    return fig


def equity_fig(curve: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if curve.empty:
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), annotations=[dict(text="No scored trades yet", x=.5, y=.5, xref="paper", yref="paper", showarrow=False, font=dict(size=15, color="#6b7c95"))])
        return chart(fig, height=360)
    good = float(curve["equity"].iloc[-1]) >= 0
    color = "#1b8f69" if good else "#d44f5f"
    fill = "rgba(27,143,105,.12)" if good else "rgba(212,79,95,.12)"
    fig.add_trace(go.Scatter(x=curve["ts"], y=curve["equity"], mode="lines", line=dict(color=color, width=3.2, shape="spline", smoothing=.55), fill="tozeroy", fillcolor=fill, hovertemplate="$%{y:,.2f}<extra></extra>", showlegend=False))
    fig.add_hline(y=0, line_width=1, line_color="rgba(92,110,135,.24)")
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#71839c", size=11))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(104,122,148,.08)", tickprefix="$", tickfont=dict(color="#71839c", size=11))
    return chart(fig, height=360)


def asks_fig(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), annotations=[dict(text="No heartbeat price history yet", x=.5, y=.5, xref="paper", yref="paper", showarrow=False, font=dict(size=15, color="#6b7c95"))])
        return chart(fig, height=260)
    fig.add_trace(go.Scatter(x=df["ts"], y=df["yes_ask"], mode="lines", name="YES ask", line=dict(color="#4685ff", width=2.6)))
    fig.add_trace(go.Scatter(x=df["ts"], y=df["no_ask"], mode="lines", name="NO ask", line=dict(color="#76b4ff", width=2.6)))
    fig.update_yaxes(range=[0,100], showgrid=True, gridcolor="rgba(104,122,148,.08)", title="cents", tickfont=dict(color="#71839c", size=11))
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#71839c", size=11))
    fig.update_layout(legend=dict(orientation="h", y=1.1, x=0, bgcolor="rgba(0,0,0,0)"))
    return chart(fig, height=260)


def latency_fig(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), annotations=[dict(text="No latency rows yet", x=.5, y=.5, xref="paper", yref="paper", showarrow=False, font=dict(size=15, color="#6b7c95"))])
        return chart(fig, height=240)
    work = df.copy(); work["ts"] = pd.to_datetime(work["ts"], errors="coerce")
    fig.add_trace(go.Scatter(x=work["ts"], y=work["feed_age_ms"], mode="lines+markers", name="Feed age", line=dict(color="#3378ff", width=2.2), marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=work["ts"], y=work["local_reaction_ms"], mode="lines+markers", name="Reaction", line=dict(color="#111f38", width=2.2), marker=dict(size=5)))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(104,122,148,.08)", title="ms", tickfont=dict(color="#71839c", size=11))
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#71839c", size=11))
    fig.update_layout(legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"))
    return chart(fig, height=240)


def recent_trades(trades: pd.DataFrame, results: pd.DataFrame) -> None:
    if trades.empty:
        st.info("No scored trades yet."); return
    pnlc, pctc = pnl_cols(trades)
    recent = enrich_trades_with_market_results(trades, results).sort_values([c for c in ["entry_ts","exit_ts"] if c in trades.columns], ascending=False).head(6)
    cards = []
    for _, row in recent.iterrows():
        outcome = str(row.get("display_outcome","open") or "open").lower()
        badge = "bw" if outcome == "win" else "bl" if outcome == "loss" else "bo"
        pnl = pd.to_numeric(pd.Series([row.get(pnlc)]), errors="coerce").iloc[0]
        pct = pd.to_numeric(pd.Series([row.get(pctc)]), errors="coerce").iloc[0]
        qty = int(float(row.get("display_qty", row.get("qty", 0)) or 0))
        cards.append(f'<div class="trade"><div class="tt"><div><div class="tm">{html.escape(str(row.get("market","")))}</div><div class="ts">{html.escape(str(row.get("side","")).upper())} | qty {qty}</div></div><span class="badge {badge}">{html.escape(outcome.replace("_"," "))}</span></div><div class="tg"><div class="ti"><span>Entry</span><strong>{format_cents(row.get("entry_fill_cents_used"))}</strong></div><div class="ti"><span>Exit</span><strong>{format_cents(row.get("exit_fill_cents_used"))}</strong></div><div class="ti"><span>Net P and L</span><strong>{format_money(pnl)}</strong></div><div class="ti"><span>Return</span><strong>{format_pct(pct)}</strong></div></div><div class="ts" style="margin-top:.78rem">{html.escape(str(row.get("ma_time","NA")))}</div></div>')
    st.markdown(f'<div class="trade-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def feed(items: list[dict[str, Any]], kind: str) -> None:
    rows = [x for x in reversed(items) if x.get("kind") == kind][:10]
    if not rows:
        st.info(f"No recent {kind} events yet."); return
    badge = "bwarn" if kind == "warning" else "berr" if kind == "error" else "bo"
    html_rows = []
    for item in rows:
        html_rows.append(f'<div class="item"><div class="fh"><span>{html.escape(format_ma_time(item.get("ts")))}</span><span class="badge {badge}">{html.escape(kind)}</span></div><div class="fc">{html.escape(str(item.get("msg","")))}</div></div>')
    st.markdown(f'<div class="feed">{"".join(html_rows)}</div>', unsafe_allow_html=True)


def warnings_panel(warnings: list[dict[str, Any]]) -> None:
    if not warnings:
        st.success("No recent warnings or errors."); return
    rows = []
    for item in reversed(warnings[-10:]):
        level = str(item.get("level","INFO")).upper(); badge = "bwarn" if level == "WARNING" else "berr"
        rows.append(f'<div class="item"><div class="fh"><span>{html.escape(format_ma_time(item.get("ts")))}</span><span class="badge {badge}">{html.escape(level)}</span></div><div class="fc">{html.escape(str(item.get("msg","")))}</div></div>')
    st.markdown(f'<div class="feed">{"".join(rows)}</div>', unsafe_allow_html=True)


def wins_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No closed trades yet."); return
    closed = df[df["display_outcome"].isin(["win","loss"])].copy()
    if closed.empty:
        st.info("No winning or losing trades yet."); return
    pnlc, pctc = pnl_cols(closed)
    exit_ts = pd.to_datetime(closed.get("exit_ts"), errors="coerce"); entry_ts = pd.to_datetime(closed.get("entry_ts"), errors="coerce")
    closed["__sort"] = exit_ts.where(exit_ts.notna(), entry_ts)
    closed = closed.sort_values(["__sort","market","side"], ascending=[False,True,True], na_position="last").head(50)
    rows = []
    for _, row in closed.iterrows():
        pnl = pd.to_numeric(pd.Series([row.get(pnlc)]), errors="coerce").iloc[0]; pct = pd.to_numeric(pd.Series([row.get(pctc)]), errors="coerce").iloc[0]
        cls = "pos" if pd.notna(pnl) and pnl > 0 else "neg" if pd.notna(pnl) and pnl < 0 else "neu"
        rows.append(f"<tr><td>{html.escape(str(row.get('ma_time','NA')))}</td><td>{html.escape(str(row.get('market','')))}</td><td>{html.escape(str(row.get('side','')).upper())}</td><td>{html.escape(format_cents(row.get('entry_fill_cents_used')))}</td><td>{html.escape(format_cents(row.get('exit_fill_cents_used')))}</td><td class='{cls}'>{html.escape(format_pct(pct))}</td><td class='{cls}'>{html.escape(format_money(pnl))}</td></tr>")
    st.markdown('<div class="glass"><table><thead><tr><th>Time</th><th>Market</th><th>Side</th><th>Entry</th><th>Exit</th><th>Return</th><th>P and L</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>', unsafe_allow_html=True)


def ssum(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").fillna(0.0).sum())


def main() -> None:
    styles()
    st.session_state.setdefault("overview_refresh", 3)
    st.session_state.setdefault("overview_tag", current_strategy_tag())
    st.session_state.setdefault("overview_range", "ALL")
    datasets = discover_datasets(); lookup = {d["tag"]: d for d in datasets}
    if datasets and st.session_state.overview_tag not in lookup: st.session_state.overview_tag = datasets[0]["tag"]
    with st.sidebar:
        st.markdown('<div class="side"><div class="kick">Overview Studio</div><h3>New dashboard surface</h3><p>A cleaner one-tab operating view built around the same scored trades, market heartbeat, and execution tape as the current dashboard.</p></div>', unsafe_allow_html=True)
        tags = [d["tag"] for d in datasets]
        st.session_state.overview_tag = st.selectbox("Dataset", tags, index=tags.index(st.session_state.overview_tag) if tags else 0, format_func=humanize_strategy_tag)
        st.session_state.overview_refresh = st.select_slider("Refresh interval", options=[1,2,3,5,10,15,30], value=st.session_state.overview_refresh)
        active = lookup.get(st.session_state.overview_tag, {"tag": st.session_state.overview_tag, **dataset_paths(st.session_state.overview_tag)})
        st.markdown(f'<div class="side meta"><h3>Dataset sources</h3><div class="row"><span>Tag</span><strong>{html.escape(humanize_strategy_tag(active["tag"]))}</strong></div><div class="row"><span>Log</span><strong>{html.escape(str(active["log_path"].relative_to(ROOT)))}</strong></div><div class="row"><span>Trades</span><strong>{html.escape(str(active["trades_path"].relative_to(ROOT)))}</strong></div><div class="row"><span>Summary</span><strong>{html.escape(str(active["summary_path"].relative_to(ROOT)))}</strong></div><div class="row"><span>Refresh</span><strong>Every {int(st.session_state.overview_refresh)}s</strong></div></div>', unsafe_allow_html=True)
    run_every = f"{int(st.session_state.overview_refresh)}s"

    @st.fragment(run_every=run_every)
    def overview() -> None:
        active = lookup.get(st.session_state.overview_tag, {"tag": st.session_state.overview_tag, **dataset_paths(st.session_state.overview_tag)})
        lines = filter_lines_for_dataset(load_log(str(active["log_path"])), active["tag"])
        all_lines, _ = load_log_bundle(str(active["log_dir"])); all_lines = filter_lines_for_dataset(all_lines, active["tag"])
        if not all_lines: all_lines = lines
        trades = normalize_trades(load_trades(str(active["trades_path"])), active["tag"])
        results = load_market_results(str(active["market_results_path"])); trades = enrich_trades_with_market_results(trades, results)
        summary = load_summary(str(active["summary_path"])); state = parse_log_state(all_lines); hb = state.get("latest_heartbeat") or {}; watch = state.get("latest_watch") or {}
        price = make_price_series(all_lines); latency = pd.DataFrame(state.get("latency_rows") or [])
        closed = trades[trades["display_outcome"].isin(["win","loss"])] if not trades.empty else pd.DataFrame(); wins = int((closed["display_outcome"] == "win").sum()) if not closed.empty else 0; losses = int((closed["display_outcome"] == "loss").sum()) if not closed.empty else 0
        open_pos = int((trades["display_outcome"] == "open").sum()) if not trades.empty else int(summary.get("open_positions", 0) or 0); entries = int(len(trades)) if not trades.empty else int(summary.get("entries_total", 0) or 0); win_rate = round((wins / max(wins + losses, 1)) * 100.0, 2) if wins + losses else 0.0
        if dataset_uses_actuals(active["tag"]) and not trades.empty and "actual_net_pnl_dollars" in trades.columns:
            net = ssum(trades["actual_net_pnl_dollars"]); basis = ssum(trades.get("actual_entry_notional_dollars", pd.Series(dtype=float))); pct = (net / basis * 100.0) if basis else 0.0; pnl_label = "Net P and L"
        elif not trades.empty and "scaled_net_pnl_dollars" in trades.columns:
            net = ssum(trades["scaled_net_pnl_dollars"]); basis = ssum(trades.get("scaled_entry_notional_dollars", pd.Series(dtype=float))); pct = (net / basis * 100.0) if basis else 0.0; pnl_label = f"Net P and L @ {DISPLAY_POSITION_SIZE}"
        else:
            net = float(summary.get("gross_pnl_total_dollars", 0) or 0); pct = float(summary.get("gross_pnl_total_percent", 0) or 0); pnl_label = "Net P and L"
        hb_ts = parse_ts(str(hb.get("ts") or "")) if hb else None; hb_age = f"{(datetime.now() - hb_ts).total_seconds():.0f}s ago" if hb_ts else "No heartbeat"
        yb, ya, nb, na = hb.get("yes_bid"), hb.get("yes_ask"), hb.get("no_bid"), hb.get("no_ask")
        ys, ns = ((ya - yb) if ya is not None and yb is not None else None), ((na - nb) if na is not None and nb is not None else None)
        bias = "Balanced"
        if ya is not None and na is not None: bias = "NO pressure" if ya - na >= 8 else "YES pressure" if na - ya >= 8 else "Two-way"
        lat = latency.tail(1).iloc[0] if not latency.empty else None; feed_age = f"{lat['feed_age_ms']:.1f} ms" if lat is not None else "NA"; react = f"{lat['local_reaction_ms']:.1f} ms" if lat is not None else "NA"
        status = str(state.get("status") or "No feed"); market = str(watch.get("market", hb.get("watch", "NA"))); close_label = format_ma_time(watch.get("close_time")) if watch else "NA"; warning_count = len(state.get("warnings") or []); warning_note = state["warnings"][-1]["msg"] if state.get("warnings") else "No recent warnings or errors."; last_entry = state.get("latest_entry"); last_exit = state.get("latest_exit")
        st.markdown('<div class="hero"><div class="kick">BTC15M Overview</div><h1>Live execution, scored trades, and market texture in one glance.</h1><p>A calmer, lighter operating view for ' + html.escape(humanize_strategy_tag(active["tag"])) + '. This version keeps every major Overview element from the current dashboard, but reorganizes the page around the questions you ask first.</p><div class="chips">' + status_chip(status, hb_age) + f'<div class="chip">Market <span style="color:#1f3250">{html.escape(market)}</span></div><div class="chip">Refresh <span style="color:#1f3250">{int(st.session_state.overview_refresh)}s</span></div><div class="chip">Warnings <span style="color:#1f3250">{warning_count}</span></div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-grid">' + ''.join([mcard(pnl_label, format_money(net), format_pct(pct)), mcard("Win rate", format_pct(win_rate), f"{wins} wins / {losses} losses"), mcard("Entries", str(entries), f"{open_pos} open positions"), mcard("Execution", status, hb_age)]) + '</div>', unsafe_allow_html=True)
        launcher = load_launcher_env_assignments(active["tag"]) if active["tag"] in BOT_CONTROL_CONFIGS else {}
        if launcher.get("PRE_ENTRY_RANGE30_FILTER_ENABLED", "").strip().lower() in {"1","true","yes","on"}:
            st.markdown(f'<div class="banner"><div class="kick" style="margin-bottom:.35rem">Entry Guardrail</div><div style="font-weight:800;color:#123566">30 second same-side range gate enabled</div><div style="font-size:.9rem;color:#516682;line-height:1.6;margin-top:.15rem">New entries are blocked when the same-side bid range over the last {html.escape(str(launcher.get("PRE_ENTRY_RANGE30_WINDOW_SECONDS", "30")))} seconds exceeds {html.escape(str(launcher.get("PRE_ENTRY_RANGE30_MAX_CENTS", "8")))} cents.</div></div>', unsafe_allow_html=True)
        le_val = f"{last_entry['side'].upper()} {last_entry['qty']} @ {last_entry['limit']}c" if last_entry else "No entry yet"; le_note = f"{format_ma_time(last_entry['ts'])} | {last_entry['market']}" if last_entry else "Waiting for a logged entry signal."
        lx_val = f"{last_exit['side'].upper()} {last_exit['qty']} @ {last_exit['limit']}c" if last_exit else "No exit yet"; lx_note = f"{format_ma_time(last_exit['ts'])} | {last_exit['market']}" if last_exit else "Waiting for a logged exit signal."
        telem = "ready" if Path(active["execution_events_path"]).exists() else "missing"
        st.markdown('<div class="spot"><div class="glass"><div class="sk">Market Pulse</div><div class="st">' + html.escape(market) + '</div><div class="ss">Top of book, directional pressure, and close timing for the active watch.</div><div class="mini">' + stat("YES ask", format_cents(ya), f"bid {format_cents(yb)} | spread {format_cents(ys)}") + stat("NO ask", format_cents(na), f"bid {format_cents(nb)} | spread {format_cents(ns)}") + stat("Bias", bias, f"Trust {display_text(hb.get('trust'))}") + stat("Close", close_label, f"Status {display_text(watch.get('status'))}") + '</div></div><div class="glass"><div class="sk">Execution Health</div><div class="st">Feed integrity and routing state</div><div class="ss">Heartbeat freshness, latency, order readiness, and telemetry coverage.</div><div class="mini">' + stat("Feed age", feed_age, f"Reaction {react}") + stat("Warnings", str(warning_count), f"Telemetry {telem}") + stat("Book ready", display_text(hb.get('book_ready')), f"Pending {display_text(hb.get('pending'))}") + stat("Position live", display_text(hb.get('position')), f"Dry run {display_text(hb.get('dry_run'))}") + '</div></div><div class="glass"><div class="sk">Signal Journal</div><div class="st">Most recent order intent</div><div class="ss">Latest entry, latest exit, current run id, and the newest warning surfaced into the top fold.</div><div class="mini">' + stat("Last entry", le_val, le_note) + stat("Last exit", lx_val, lx_note) + stat("Run id", str((hb.get('run_id') or watch.get('run_id') or 'NA'))[-8:], f"Refresh every {int(st.session_state.overview_refresh)}s") + stat("Latest warning", state['warnings'][-1]['level'] if state.get('warnings') else 'Clear', warning_note) + '</div></div></div>', unsafe_allow_html=True)
        left, right = st.columns([1.7, 1.0], gap="large")
        with left:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Equity</div>', unsafe_allow_html=True)
            curve = make_equity_curve(trades); curve = filter_equity_curve(curve, st.session_state.overview_range) if not curve.empty else curve
            st.markdown('<div class="glass">', unsafe_allow_html=True); st.plotly_chart(equity_fig(curve), width="stretch", key=f"apple-equity-{active['tag']}"); st.radio("Equity timeframe", EQUITY_RANGE_OPTIONS, horizontal=True, label_visibility="collapsed", key="overview_range"); st.markdown('</div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Live asks</div>', unsafe_allow_html=True); st.markdown('<div class="glass">', unsafe_allow_html=True); st.plotly_chart(asks_fig(price.tail(120)), width="stretch", key=f"apple-asks-{active['tag']}"); st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:.85rem"></div>', unsafe_allow_html=True); st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Latency</div>', unsafe_allow_html=True); st.markdown('<div class="glass">', unsafe_allow_html=True); st.plotly_chart(latency_fig(latency), width="stretch", key=f"apple-latency-{active['tag']}"); st.markdown('</div>', unsafe_allow_html=True)
        lower_left, lower_right = st.columns([1.7, 1.0], gap="large")
        with lower_left:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Recent scored trades</div>', unsafe_allow_html=True); recent_trades(trades, results)
        with lower_right:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Event tape</div>', unsafe_allow_html=True); st.markdown('<div class="glass">', unsafe_allow_html=True); feed(state.get("events") or [], "entry"); st.markdown('<div style="height:.85rem"></div>', unsafe_allow_html=True); feed(state.get("events") or [], "exit"); st.markdown('</div>', unsafe_allow_html=True)
        final_left, final_right = st.columns([1.45, 1.0], gap="large")
        with final_left:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Wins and losses</div>', unsafe_allow_html=True); wins_table(trades)
        with final_right:
            st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Warnings and errors</div>', unsafe_allow_html=True); st.markdown('<div class="glass">', unsafe_allow_html=True); warnings_panel(state.get("warnings") or []); st.markdown('</div>', unsafe_allow_html=True); st.markdown('<div style="height:.85rem"></div>', unsafe_allow_html=True); st.markdown('<div class="kick" style="margin:0 0 .55rem 0">Live log tail</div>', unsafe_allow_html=True); st.markdown('<div class="mono">' + '<br>'.join(html.escape(x) for x in (state.get("log_tail") or [])[-80:]) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="kick" style="margin-bottom:.65rem">Overview Only</div><div style="color:#66758b;font-size:.9rem;line-height:1.55;margin-bottom:.5rem">This new surface focuses on the operating overview first. Research Lab, visualizer, loss diagnostics, and optimizer views are intentionally not in this file yet.</div>', unsafe_allow_html=True)
    overview()

if __name__ == "__main__":
    main()
