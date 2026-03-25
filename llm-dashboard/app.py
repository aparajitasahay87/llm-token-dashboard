import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

C = {
    "bg":       "#07070f",
    "surface":  "#0f0f1a",
    "surface2": "#161624",
    "border":   "#1e1e32",
    "accent":   "#7c6dfa",
    "green":    "#34d399",
    "yellow":   "#fbbf24",
    "red":      "#f87171",
    "text":     "#e2e2f0",
    "muted":    "#55556a",
    "gpt4":     "#7c6dfa",
    "gpt4mini": "#34d399",
    "gpt35":    "#fbbf24",
}
FONT = "'IBM Plex Mono', monospace"

def hex_rgba(h, a=0.12):
    h = h.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def model_color(m):
    m = str(m)
    if "gpt-4o" in m and "mini" not in m: return C["gpt4"]
    if "gpt-4o-mini" in m:               return C["gpt4mini"]
    if "gpt-3.5" in m:                   return C["gpt35"]
    return C["muted"]

def fetch_all():
    try:
        res = supabase.table("usage_logs").select("*").order("timestamp", desc=False).execute()
        if not res.data: return pd.DataFrame()
        df = pd.DataFrame(res.data)
        df["timestamp"]    = pd.to_datetime(df["timestamp"], utc=True)
        df["cost_usd"]     = pd.to_numeric(df["cost_usd"],     errors="coerce").fillna(0)
        df["total_tokens"] = pd.to_numeric(df["total_tokens"], errors="coerce").fillna(0)
        df["input_tokens"] = pd.to_numeric(df.get("input_tokens",  0), errors="coerce").fillna(0)
        df["output_tokens"]= pd.to_numeric(df.get("output_tokens", 0), errors="coerce").fillna(0)
        df["latency_ms"]   = pd.to_numeric(df["latency_ms"],   errors="coerce").fillna(0)
        return df
    except Exception as e:
        print(f"Fetch error: {e}")
        return pd.DataFrame()

def sessions_from(df):
    if df.empty or "session_id" not in df.columns: return pd.DataFrame()
    d = df[df["session_id"].notna() & (df["session_id"] != "")].copy()
    if d.empty: return pd.DataFrame()
    s = d.groupby("session_id").agg(
        session_start  =("timestamp",     "min"),
        total_calls    =("id",            "count"),
        total_tokens   =("total_tokens",  "sum"),
        total_cost     =("cost_usd",      "sum"),
        total_latency  =("latency_ms",    "sum"),
        models         =("model", lambda x: " · ".join(sorted(set(str(v) for v in x if v))))
    ).reset_index().sort_values("session_start", ascending=False)
    return s

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(color=C["text"], family=FONT, size=11),
    margin=dict(l=8, r=8, t=8, b=8),
    legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12)
)

def fig_cost_timeline(df):
    fig = go.Figure()
    if df.empty: return fig
    for m in df["model"].dropna().unique():
        sub = df[df["model"]==m].sort_values("timestamp")
        col = model_color(m)
        fig.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["cost_usd"].cumsum(),
            mode="lines+markers", name=str(m),
            line=dict(color=col, width=2), marker=dict(size=5, color=col),
            fill="tozeroy", fillcolor=hex_rgba(col)
        ))
    fig.update_layout(**BASE, height=220,
        xaxis=dict(showgrid=False, tickfont=dict(size=10), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=C["border"], tickprefix="$", tickfont=dict(size=10), zeroline=False)
    )
    return fig

def fig_latency(df):
    fig = go.Figure()
    if df.empty: return fig
    for m in df["model"].dropna().unique():
        sub = df[df["model"]==m].sort_values("timestamp")
        col = model_color(m)
        fig.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["latency_ms"],
            mode="markers", name=str(m),
            marker=dict(size=7, color=col, opacity=0.85)
        ))
    fig.update_layout(**BASE, height=220,
        xaxis=dict(showgrid=False, tickfont=dict(size=10), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=C["border"], ticksuffix="ms", tickfont=dict(size=10), zeroline=False)
    )
    return fig

def fig_tokens_by_model(df):
    if df.empty: return go.Figure()
    g = df.groupby("model")["total_tokens"].sum().reset_index().sort_values("total_tokens")
    fig = go.Figure()
    for _, r in g.iterrows():
        fig.add_trace(go.Bar(
            x=[r["total_tokens"]], y=[r["model"]], orientation="h",
            marker_color=model_color(r["model"]), marker_line_width=0,
            text=[f"{int(r['total_tokens']):,}"], textposition="outside",
            textfont=dict(size=10, color=C["text"]), showlegend=False
        ))
    fig.update_layout(**BASE, height=180, showlegend=False, bargap=0.35,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11))
    )
    return fig

def fig_cost_by_model(df):
    if df.empty: return go.Figure()
    g = df.groupby("model")["cost_usd"].sum().reset_index().sort_values("cost_usd")
    fig = go.Figure()
    for _, r in g.iterrows():
        fig.add_trace(go.Bar(
            x=[r["cost_usd"]], y=[r["model"]], orientation="h",
            marker_color=model_color(r["model"]), marker_line_width=0,
            text=[f"${float(r['cost_usd']):.5f}"], textposition="outside",
            textfont=dict(size=10, color=C["text"]), showlegend=False
        ))
    fig.update_layout(**BASE, height=180, showlegend=False, bargap=0.35,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11))
    )
    return fig

def fig_call_type_donut(df):
    if df.empty: return go.Figure()
    g = df.groupby("call_type")["cost_usd"].sum().reset_index()
    palette = [C["accent"], C["green"], C["yellow"], C["red"], "#a78bfa", "#fb923c"]
    fig = go.Figure(go.Pie(
        labels=g["call_type"], values=g["cost_usd"], hole=0.6,
        marker=dict(colors=palette[:len(g)], line=dict(width=0)),
        textfont=dict(size=10, family=FONT), textposition="outside"
    ))
    fig.update_layout(**BASE, height=220)
    return fig

def fig_session_cost(sessions):
    if sessions.empty: return go.Figure()
    s = sessions.head(10).sort_values("session_start")
    labels = [str(sid)[:8] for sid in s["session_id"]]
    fig = go.Figure(go.Bar(
        x=labels, y=s["total_cost"].astype(float),
        marker_color=C["accent"], marker_line_width=0,
        text=[f"${float(v):.4f}" for v in s["total_cost"]],
        textposition="outside", textfont=dict(size=9, color=C["text"])
    ))
    fig.update_layout(**BASE, height=200, showlegend=False, bargap=0.35,
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor=C["border"], tickprefix="$", tickfont=dict(size=10), zeroline=False)
    )
    return fig

def card(children, extra=None):
    s = {"background":C["surface"],"border":f"1px solid {C['border']}","borderRadius":"10px","padding":"18px 20px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)

def lbl(t):
    return html.P(t, style={"fontSize":"9px","letterSpacing":"0.14em","textTransform":"uppercase",
        "color":C["muted"],"fontFamily":FONT,"margin":"0 0 10px 0",
        "borderBottom":f"1px solid {C['border']}","paddingBottom":"6px"})

def metric(title, val, sub=None, color=None):
    return card([
        html.P(title, style={"fontSize":"9px","letterSpacing":"0.12em","textTransform":"uppercase",
            "color":C["muted"],"fontFamily":FONT,"margin":"0 0 6px 0"}),
        html.H2(val, style={"fontSize":"26px","fontWeight":"700","color":color or C["text"],
            "fontFamily":FONT,"margin":"0","letterSpacing":"-0.02em"}),
        html.P(sub, style={"fontSize":"10px","color":C["muted"],"fontFamily":FONT,"margin":"4px 0 0 0"}) if sub else None
    ])

def gchart(title, fig):
    return card([lbl(title), dcc.Graph(figure=fig, config={"displayModeBar":False})])

def btn(text, btn_id, active):
    is_active = btn_id == active
    return html.Button(text, id=btn_id, n_clicks=0, style={
        "background": C["accent"] if is_active else "transparent",
        "color": C["text"] if is_active else C["muted"],
        "border": f"1px solid {C['accent'] if is_active else C['border']}",
        "borderRadius":"6px","padding":"6px 16px","fontSize":"10px",
        "letterSpacing":"0.1em","fontFamily":FONT,"cursor":"pointer","textTransform":"uppercase"
    })

def session_tbl(sessions):
    if sessions.empty:
        return html.P("No sessions yet.", style={"color":C["muted"],"fontFamily":FONT,"fontSize":"12px"})
    hs = {"padding":"8px 12px","fontSize":"9px","letterSpacing":"0.12em","textTransform":"uppercase",
          "color":C["muted"],"fontFamily":FONT,"borderBottom":f"1px solid {C['border']}","textAlign":"left"}
    cols = ["Session","Time","Calls","Tokens","Cost","Latency","Models"]
    def row(r):
        c = {"padding":"10px 12px","fontFamily":FONT,"fontSize":"11px","borderBottom":f"1px solid {C['border']}"}
        cost_col = C["green"] if float(r["total_cost"])<0.01 else C["yellow"] if float(r["total_cost"])<0.05 else C["red"]
        return html.Tr([
            html.Td(str(r["session_id"])[:8]+"...", style={**c,"color":C["accent"],"fontWeight":"500"}),
            html.Td(str(r["session_start"])[:16],   style={**c,"color":C["muted"],"fontSize":"10px"}),
            html.Td(str(int(r["total_calls"])),      style={**c,"color":C["text"]}),
            html.Td(f"{int(r['total_tokens']):,}",   style={**c,"color":C["text"]}),
            html.Td(f"${float(r['total_cost']):.5f}",style={**c,"color":cost_col,"fontWeight":"600"}),
            html.Td(f"{int(r['total_latency']):,}ms",style={**c,"color":C["muted"]}),
            html.Td(str(r.get("models",""))[:40],    style={**c,"color":C["muted"],"fontSize":"10px"}),
        ])
    return html.Table([
        html.Thead(html.Tr([html.Th(c, style=hs) for c in cols])),
        html.Tbody([row(r) for _,r in sessions.iterrows()])
    ], style={"width":"100%","borderCollapse":"collapse"})

def calls_tbl(df):
    if df.empty:
        return html.P("No data.", style={"color":C["muted"],"fontFamily":FONT,"fontSize":"12px"})
    recent = df.sort_values("timestamp", ascending=False).head(20)
    hs = {"padding":"8px 12px","fontSize":"9px","letterSpacing":"0.12em","textTransform":"uppercase",
          "color":C["muted"],"fontFamily":FONT,"borderBottom":f"1px solid {C['border']}","textAlign":"left"}
    cols = ["Time","Session","Model","Call Type","Input","Output","Cost","Latency"]
    def row(r):
        c = {"padding":"9px 12px","fontFamily":FONT,"fontSize":"11px","borderBottom":f"1px solid {C['border']}"}
        col = model_color(r.get("model",""))
        sid = str(r.get("session_id",""))[:8] if r.get("session_id") else "—"
        return html.Tr([
            html.Td(str(r.get("timestamp",""))[:16],            style={**c,"color":C["muted"],"fontSize":"10px"}),
            html.Td(sid,                                        style={**c,"color":C["accent"],"fontSize":"10px"}),
            html.Td(str(r.get("model","")),                    style={**c,"color":col,"fontWeight":"500"}),
            html.Td(str(r.get("call_type","")),                style={**c,"color":C["text"]}),
            html.Td(f"{int(r.get('input_tokens',0)):,}",       style={**c,"color":C["muted"]}),
            html.Td(f"{int(r.get('output_tokens',0)):,}",      style={**c,"color":C["muted"]}),
            html.Td(f"${float(r.get('cost_usd',0)):.5f}",     style={**c,"color":C["green"],"fontWeight":"600"}),
            html.Td(f"{int(r.get('latency_ms',0)):,}ms",       style={**c,"color":C["muted"]}),
        ])
    return html.Table([
        html.Thead(html.Tr([html.Th(c, style=hs) for c in cols])),
        html.Tbody([row(r) for _,r in recent.iterrows()])
    ], style={"width":"100%","borderCollapse":"collapse"})

# ── App ────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="LLM Token Dashboard",
    external_stylesheets=["https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&display=swap"])

app.layout = html.Div([
    dcc.Interval(id="iv", interval=60_000, n_intervals=0),
    html.Div([
        html.Div([
            html.H1("LLM Token Dashboard", style={"margin":"0","fontSize":"18px","fontWeight":"700",
                "color":C["text"],"fontFamily":FONT,"letterSpacing":"-0.02em"}),
            html.P("token economy · observability · real time", style={"margin":"2px 0 0 0",
                "fontSize":"10px","color":C["muted"],"fontFamily":FONT,"letterSpacing":"0.1em"})
        ]),
        html.Span("● LIVE", style={"fontSize":"10px","color":C["green"],"fontFamily":FONT,"letterSpacing":"0.12em"})
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"center",
        "padding":"18px 28px","borderBottom":f"1px solid {C['border']}","background":C["surface"]}),

    html.Div([
        html.Button("Overview", id="btn-overview", n_clicks=0),
        html.Button("Sessions", id="btn-sessions", n_clicks=0),
        html.Button("Models",   id="btn-models",   n_clicks=0),
        html.Button("Calls",    id="btn-calls",    n_clicks=0),
    ], id="tabbar", style={"display":"flex","gap":"8px","padding":"14px 28px",
        "borderBottom":f"1px solid {C['border']}","background":C["surface"]}),

    html.Div(id="content", style={"padding":"24px 28px","maxWidth":"1440px","margin":"0 auto"})

], style={"background":C["bg"],"minHeight":"100vh","fontFamily":FONT})

@app.callback(
    Output("content","children"),
    Output("tabbar","children"),
    Input("btn-overview","n_clicks"),
    Input("btn-sessions","n_clicks"),
    Input("btn-models",  "n_clicks"),
    Input("btn-calls",   "n_clicks"),
    Input("iv","n_intervals"),
    prevent_initial_call=False
)
def render(n1,n2,n3,n4,ni):
    from dash import ctx
    tid = ctx.triggered_id or "btn-overview"
    tab = {"btn-overview":"overview","btn-sessions":"sessions",
           "btn-models":"models","btn-calls":"calls"}.get(tid,"overview")

    tabs = [
        ("Overview","btn-overview","overview"),
        ("Sessions","btn-sessions","sessions"),
        ("Models",  "btn-models",  "models"),
        ("Calls",   "btn-calls",   "calls"),
    ]
    tabbar = [btn(t[0],t[1],tab) for t in tabs]

    df       = fetch_all()
    sessions = sessions_from(df)

    total_cost   = float(df["cost_usd"].sum())     if not df.empty else 0
    total_tokens = int(df["total_tokens"].sum())   if not df.empty else 0
    total_calls  = len(df)                         if not df.empty else 0
    n_sessions   = len(sessions)                   if not sessions.empty else 0
    avg_lat      = int(df["latency_ms"].mean())    if not df.empty else 0
    avg_sess     = total_cost / n_sessions         if n_sessions > 0 else 0

    gpt4_cost = float(df[df["model"].str.contains("gpt-4o",na=False) &
                         ~df["model"].str.contains("mini",na=False)
                        ]["cost_usd"].sum()) if not df.empty else 0
    gpt4_pct  = int(gpt4_cost/total_cost*100) if total_cost>0 else 0

    ROW = {"display":"flex","gap":"10px","marginBottom":"16px","flexWrap":"wrap"}
    ROW2= {"display":"flex","gap":"14px","marginBottom":"14px"}

    if tab == "overview":
        content = html.Div([
            html.Div([
                metric("Total Cost",   f"${total_cost:.4f}",   "all time",          C["accent"]),
                metric("Total Tokens", f"{total_tokens:,}",    "all calls"),
                metric("Sessions",     str(n_sessions),         "analyze() calls"),
                metric("LLM Calls",    str(total_calls),        f"{total_calls//n_sessions if n_sessions else 0} per session"),
                metric("Avg Latency",  f"{avg_lat:,}ms",       "per call"),
                metric("Avg/Session",  f"${avg_sess:.4f}",     f"gpt-4o={gpt4_pct}%", C["yellow"]),
            ], style=ROW),
            html.Div([
                gchart("Cumulative cost over time — by model", fig_cost_timeline(df)),
                gchart("Latency per call",                     fig_latency(df)),
            ], style=ROW2),
            html.Div([
                gchart("Token usage — by model",        fig_tokens_by_model(df)),
                gchart("Cost — by call type",           fig_call_type_donut(df)),
                gchart("Cost — by model",               fig_cost_by_model(df)),
            ], style=ROW2),
            card([html.P(
                f"💡  gpt-4o = {gpt4_pct}% of spend  ·  avg session = ${avg_sess:.4f}  ·  "
                f"{total_tokens:,} tokens  ·  {n_sessions} sessions",
                style={"margin":"0","fontSize":"11px","color":C["muted"],"fontFamily":FONT}
            )], extra={"borderLeft":f"3px solid {C['accent']}","borderRadius":"8px"})
        ])

    elif tab == "sessions":
        content = html.Div([
            html.Div([
                metric("Sessions",    str(n_sessions),          "analyze() calls"),
                metric("Total Cost",  f"${total_cost:.4f}",     "all sessions",    C["accent"]),
                metric("Avg/Session", f"${avg_sess:.4f}",       "per analyze()",   C["yellow"]),
                metric("Total Calls", str(total_calls),          f"{total_calls//n_sessions if n_sessions else 0} calls/session"),
            ], style=ROW),
            gchart("Session cost — most recent 10", fig_session_cost(sessions)),
            html.Div(style={"height":"16px"}),
            card([lbl("All sessions — grouped by session_id"),
                  html.Div(session_tbl(sessions), style={"overflowX":"auto"})])
        ])

    elif tab == "models":
        model_stats = df.groupby("model").agg(
            calls        =("id",            "count"),
            total_tokens =("total_tokens",  "sum"),
            input_tokens =("input_tokens",  "sum"),
            output_tokens=("output_tokens", "sum"),
            total_cost   =("cost_usd",      "sum"),
            avg_latency  =("latency_ms",    "mean")
        ).reset_index().sort_values("total_cost",ascending=False) if not df.empty else pd.DataFrame()

        hs = {"padding":"8px 12px","fontSize":"9px","letterSpacing":"0.12em","textTransform":"uppercase",
              "color":C["muted"],"fontFamily":FONT,"borderBottom":f"1px solid {C['border']}","textAlign":"left"}

        def mrow(r):
            c = {"padding":"10px 12px","fontFamily":FONT,"fontSize":"11px","borderBottom":f"1px solid {C['border']}"}
            col = model_color(r["model"])
            pct = f"{float(r['total_cost'])/total_cost*100:.0f}%" if total_cost>0 else "0%"
            return html.Tr([
                html.Td(str(r["model"]),              style={**c,"color":col,"fontWeight":"600"}),
                html.Td(str(int(r["calls"])),         style={**c,"color":C["text"]}),
                html.Td(f"{int(r['total_tokens']):,}",style={**c,"color":C["text"]}),
                html.Td(f"{int(r['input_tokens']):,}",style={**c,"color":C["muted"]}),
                html.Td(f"{int(r['output_tokens']):,}",style={**c,"color":C["muted"]}),
                html.Td(f"${float(r['total_cost']):.5f}",style={**c,"color":C["green"],"fontWeight":"600"}),
                html.Td(pct,                          style={**c,"color":C["yellow"],"fontWeight":"600"}),
                html.Td(f"{int(r['avg_latency']):,}ms",style={**c,"color":C["muted"]}),
            ])

        mtbl = html.Table([
            html.Thead(html.Tr([html.Th(c,style=hs) for c in
                ["Model","Calls","Total Tokens","Input","Output","Cost","% Spend","Avg Latency"]])),
            html.Tbody([mrow(r) for _,r in model_stats.iterrows()] if not model_stats.empty else [
                html.Tr(html.Td("No data",colSpan=8,style={"padding":"20px","color":C["muted"],
                    "fontFamily":FONT,"fontSize":"12px","textAlign":"center"}))
            ])
        ], style={"width":"100%","borderCollapse":"collapse"})

        content = html.Div([
            html.Div([
                metric("Models Used",  str(len(model_stats)) if not model_stats.empty else "0"),
                metric("gpt-4o Cost",  f"${gpt4_cost:.4f}",  f"{gpt4_pct}% of total", C["gpt4"]),
                metric("Total Tokens", f"{total_tokens:,}",   "all models"),
                metric("Total Cost",   f"${total_cost:.4f}",  "all models", C["accent"]),
            ], style=ROW),
            html.Div([
                gchart("Tokens by model", fig_tokens_by_model(df)),
                gchart("Cost by model",   fig_cost_by_model(df)),
            ], style=ROW2),
            card([lbl("Model performance breakdown"),
                  html.Div(mtbl, style={"overflowX":"auto"})])
        ])

    else:
        content = html.Div([
            html.Div([
                metric("Total Calls", str(total_calls),      "all time"),
                metric("Total Cost",  f"${total_cost:.4f}",  "all calls",  C["accent"]),
                metric("Avg Cost",    f"${total_cost/total_calls:.5f}" if total_calls else "$0","per call"),
                metric("Avg Latency", f"{avg_lat:,}ms",      "per call"),
            ], style=ROW),
            card([lbl("Recent LLM calls — last 20"),
                  html.Div(calls_tbl(df), style={"overflowX":"auto"})])
        ])

    return content, tabbar


if __name__ == "__main__":
    app.run(debug=True, port=8050)