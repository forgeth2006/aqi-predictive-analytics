"""Control chart tab.

Reads: outputs/control_chart.csv (month, value, centre, ucl, lcl, out_of_control, rule, chart)
       outputs/p_chart.csv (month, n_days, poor_days, p, centre, ucl, lcl, ucl_laney, lcl_laney, ...)
Both are written by notebook 06.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import CONTROL_CSV, PCHART_CSV

RULES = {"1": "beyond 3σ", "2": "2 of 3 beyond 2σ", "3": "4 of 5 beyond 1σ", "4": "8 in a row on one side"}


@st.cache_data
def _load():
    if not CONTROL_CSV.exists():
        raise FileNotFoundError(CONTROL_CSV.name + " (run notebooks/06_control_charts.ipynb)")
    cc = pd.read_csv(CONTROL_CSV, dtype={"rule": str})
    cc["rule"] = cc["rule"].fillna("").str.replace(r"\.0$", "", regex=True)
    pc = pd.read_csv(PCHART_CSV) if PCHART_CSV.exists() else None
    return cc, pc


def _describe(rule: str) -> str:
    return "; ".join(RULES[r] for r in rule if r in RULES)


def render() -> None:
    cc, pc = _load()
    st.subheader("Statistical process control")
    chart = st.radio("Individuals chart of", list(cc["chart"].unique())[::-1], horizontal=True,
                     help="The seasonally adjusted chart removes the calendar pattern, so signals mean "
                          "'unusual for the time of year'.")
    d = cc[cc["chart"] == chart].copy()
    d["date"] = pd.to_datetime(d["month"] + "-01")
    out = d[d["out_of_control"] == 1]

    fig = go.Figure()
    fig.add_scatter(x=d["date"], y=d["value"], mode="lines+markers", name=chart, line=dict(color="#1f77b4"),
                    marker=dict(size=5))
    fig.add_scatter(x=out["date"], y=out["value"], mode="markers", name="Signal",
                    marker=dict(color="#d62728", size=11, symbol="circle-open", line=dict(width=2)),
                    text=[_describe(r) for r in out["rule"]], hovertemplate="%{x|%b %Y}: %{y:.0f}<br>%{text}")
    for col, name, dash in (("centre", "Centre line", "solid"), ("ucl", "UCL (+3σ)", "dash"), ("lcl", "LCL (-3σ)", "dash")):
        fig.add_hline(y=d[col].iloc[0], line_dash=dash, line_color="black" if col == "centre" else "#d62728",
                      annotation_text=f"{name} {d[col].iloc[0]:.0f}", annotation_position="right")
    fig.update_layout(height=420, yaxis_title="AQI", margin=dict(l=10, r=110, t=30, b=10),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"{len(out)} of {len(d)} months signal under the Western Electric rules. "
               "Sigma is estimated from the average moving range (MR-bar / 1.128).")
    if len(out):
        st.dataframe(out.assign(why=[_describe(r) for r in out["rule"]])[["month", "value", "why"]].round(1),
                     hide_index=True, width="stretch")

    if pc is not None:
        st.markdown("**p-chart: share of Poor-or-worse days each month**")
        pc = pc.copy()
        pc["date"] = pd.to_datetime(pc["month"] + "-01")
        laney = st.checkbox("Use Laney p′ limits (corrects for over-dispersion)", value=True)
        lo, hi, flag = ("lcl_laney", "ucl_laney", "out_laney") if laney else ("lcl", "ucl", "out_of_control")
        fig = go.Figure()
        fig.add_scatter(x=pc["date"], y=pc["p"], mode="lines+markers", name="Share of Poor days", marker=dict(size=5))
        fig.add_scatter(x=pc["date"], y=pc[hi], mode="lines", name="Upper limit", line=dict(color="#d62728", dash="dash"))
        fig.add_scatter(x=pc["date"], y=pc[lo], mode="lines", name="Lower limit", line=dict(color="#d62728", dash="dash"))
        fig.add_hline(y=pc["centre"].iloc[0], line_color="black", annotation_text=f"p̄ = {pc['centre'].iloc[0]:.2f}")
        o = pc[pc[flag] == 1]
        fig.add_scatter(x=o["date"], y=o["p"], mode="markers", name="Signal",
                        marker=dict(color="#d62728", size=11, symbol="circle-open", line=dict(width=2)))
        fig.update_layout(height=360, yaxis=dict(title="Proportion", range=[-0.03, 1.05]),
                          margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.18))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"{len(o)} of {len(pc)} months outside the {'Laney' if laney else 'binomial'} limits. Poor days "
                   "cluster in multi-day smog spells, so the plain binomial limits are far too narrow.")
