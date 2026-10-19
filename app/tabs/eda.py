"""EDA tab.

Reads: data/processed/aqi_delhi_clean.csv
Shows: headline numbers, AQI over time, band frequency table, distribution, season boxplots,
month-by-year heatmap and the correlation matrix, all filterable by year and season.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils import BUCKETS, POLLUTANTS, SEASONS, load_clean

BUCKET_COLORS = {"Good": "#2e9e44", "Satisfactory": "#9acd32", "Moderate": "#f2c12e",
                 "Poor": "#f08a24", "Very Poor": "#d7301f", "Severe": "#7f0000"}
SEASON_COLORS = {"Winter": "#4c78a8", "Summer": "#f58518", "Monsoon": "#54a24b", "Post-monsoon": "#b279a2"}


@st.cache_data
def _data() -> pd.DataFrame:
    return load_clean()


def render() -> None:
    df = _data()
    st.subheader("Exploratory data analysis")

    c1, c2 = st.columns([2, 3])
    years = c1.slider("Years", int(df["Year"].min()), int(df["Year"].max()),
                      (int(df["Year"].min()), int(df["Year"].max())))
    seasons = c2.multiselect("Seasons", SEASONS, default=SEASONS)
    d = df[df["Year"].between(*years) & df["Season"].isin(seasons)]
    if d.empty:
        st.warning("No days match the filters.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Days", f"{len(d):,}")
    k2.metric("Mean AQI", f"{d['AQI'].mean():.0f}")
    k3.metric("Poor or worse (AQI > 200)", f"{d['Poor_Flag'].mean():.0%}")
    k4.metric("Severe days (AQI > 400)", f"{(d['AQI_Bucket'] == 'Severe').sum():,}")

    s = d.set_index("Date")["AQI"]
    fig = go.Figure()
    fig.add_scatter(x=s.index, y=s, mode="lines", line=dict(width=0.8, color="#9e9e9e"), name="Daily AQI")
    roll = df.set_index("Date")["AQI"].rolling(30, center=True).mean().reindex(s.index)
    fig.add_scatter(x=roll.index, y=roll, mode="lines", line=dict(width=2.5, color="#d62728"), name="30-day average")
    for y0 in (100, 200, 300, 400):
        fig.add_hline(y=y0, line_dash="dot", line_width=1, line_color="#555")
    fig.update_layout(title="Daily AQI (dotted lines: band limits 100 / 200 / 300 / 400)", height=360,
                      margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=1.08, x=1, xanchor="right"))
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)
    with left:
        freq = d["AQI_Bucket"].value_counts().reindex(BUCKETS).fillna(0).astype(int)
        tab = pd.DataFrame({"AQI band": freq.index, "Days": freq.values,
                            "% of days": (freq.values / freq.sum() * 100).round(1)})
        fig = px.bar(tab, x="AQI band", y="Days", color="AQI band", color_discrete_map=BUCKET_COLORS,
                     text="Days", title="Days in each official AQI band")
        fig.update_layout(showlegend=False, height=340, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(tab, hide_index=True, width="stretch")
    with right:
        fig = px.histogram(d, x="AQI", nbins=45, color_discrete_sequence=["#4c78a8"],
                           title=f"AQI distribution (skewness {d['AQI'].skew():.2f})")
        fig.add_vline(x=d["AQI"].mean(), line_color="black", annotation_text="mean")
        fig.add_vline(x=d["AQI"].median(), line_dash="dot", line_color="black", annotation_text="median",
                      annotation_position="bottom right")
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")
        fig = px.box(d, x="Season", y="AQI", color="Season", category_orders={"Season": SEASONS},
                     color_discrete_map=SEASON_COLORS, title="AQI by season")
        fig.update_layout(showlegend=False, height=320, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)
    with left:
        hm = d.pivot_table(index="Year", columns="Month", values="AQI", aggfunc="mean").round(0)
        fig = px.imshow(hm, text_auto=".0f", color_continuous_scale="YlOrRd", aspect="auto",
                        title="Mean AQI by year and month", labels=dict(color="AQI"))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        method = st.radio("Correlation", ["pearson", "spearman"], horizontal=True)
        corr = d[POLLUTANTS + ["AQI"]].corr(method=method).round(2)
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto",
                        title=f"{method.title()} correlation matrix")
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")

    with st.expander("Descriptive statistics for the filtered days"):
        desc = d[POLLUTANTS + ["AQI"]].describe().T
        desc["skewness"] = d[POLLUTANTS + ["AQI"]].skew()
        desc["kurtosis (excess)"] = d[POLLUTANTS + ["AQI"]].kurt()
        st.dataframe(desc.round(2), width="stretch")
    st.caption("Source: Kaggle 'Air Quality Data in India (2015-2020)', city_day.csv, Delhi, cleaned in notebook 01.")
