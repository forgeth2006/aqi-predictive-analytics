"""Forecast tab.

Reads: outputs/forecast_monthly.csv (written by notebook 05)
Columns: month, actual, forecast, lower_95, upper_95, model, segment, observed_2020, test_rmse, test_mape
and outputs/tables/forecast_comparison.csv. Nothing is fitted here.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import FORECAST_CSV, TS_COMPARE_CSV


@st.cache_data
def _load():
    if not FORECAST_CSV.exists():
        raise FileNotFoundError(FORECAST_CSV.name + " (run notebooks/05_timeseries.ipynb)")
    fc = pd.read_csv(FORECAST_CSV)
    fc["date"] = pd.to_datetime(fc["month"] + "-01")
    comp = pd.read_csv(TS_COMPARE_CSV) if TS_COMPARE_CSV.exists() else None
    return fc, comp


def render() -> None:
    fc, comp = _load()
    model = fc.loc[fc["segment"] == "future", "model"].iloc[0]
    st.subheader("Monthly AQI forecast")
    st.caption(f"Selected model: **{model}**, chosen by rolling-origin evaluation over 19 forecast origins.")

    test = fc[fc["segment"].str.startswith("test")]
    fut = fc[fc["segment"] == "future"]
    k1, k2, k3 = st.columns(3)
    k1.metric("Test RMSE (Jul-Dec 2019)", f"{fc['test_rmse'].iloc[0]:.1f} AQI")
    k2.metric("Test MAPE", f"{fc['test_mape'].iloc[0]:.1f}%")
    if comp is not None and "Skill vs seasonal naive %" in comp:
        k3.metric("Skill vs seasonal naive", f"{comp.loc[comp['Model'] == model, 'Skill vs seasonal naive %'].iloc[0]:.0f}%",
                  help="Reduction in rolling-origin RMSE compared with 'same month last year'.")

    show_2020 = st.toggle("Show what actually happened in 2020 (COVID-19 lockdown, not used for fitting)", value=True)
    hist = fc[fc["actual"].notna()]
    fig = go.Figure()
    fig.add_scatter(x=hist["date"], y=hist["actual"], mode="lines+markers", name="Actual 2015-2019",
                    line=dict(color="black", width=1.5), marker=dict(size=4))
    fig.add_scatter(x=test["date"], y=test["forecast"], mode="lines+markers", name="Test forecast (made in June 2019)",
                    line=dict(color="#ff7f0e", dash="dash"))
    fig.add_scatter(x=pd.concat([fut["date"], fut["date"][::-1]]), y=pd.concat([fut["upper_95"], fut["lower_95"][::-1]]),
                    fill="toself", fillcolor="rgba(31,119,180,0.18)", line=dict(width=0), name="95% prediction interval",
                    hoverinfo="skip")
    fig.add_scatter(x=fut["date"], y=fut["forecast"], mode="lines+markers", name="Forecast Jan-Jun 2020",
                    line=dict(color="#1f77b4", width=2.5))
    if show_2020:
        fig.add_scatter(x=fut["date"], y=fut["observed_2020"], mode="lines+markers", name="Actual 2020",
                        line=dict(color="#d62728", dash="dot"), marker=dict(symbol="square", size=7))
        fig.add_vline(x=pd.Timestamp("2020-03-25").timestamp() * 1000, line_dash="dot", line_color="#d62728",
                      annotation_text="Lockdown", annotation_position="top left")
    fig.update_layout(height=430, yaxis_title="Monthly mean AQI", margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, width="stretch")

    table = fut[["month", "forecast", "lower_95", "upper_95", "observed_2020"]].rename(
        columns={"forecast": "Forecast", "lower_95": "95% low", "upper_95": "95% high", "observed_2020": "Actual 2020"})
    if not show_2020:
        table = table.drop(columns="Actual 2020")
    st.dataframe(table.round(1), hide_index=True, width="stretch")
    if show_2020:
        jf = fut[fut["month"].isin(["2020-01", "2020-02"])]
        aj = fut[fut["month"].isin(["2020-04", "2020-05", "2020-06"])]
        st.info(f"Jan-Feb 2020 (normal conditions): mean error {(jf['observed_2020'] - jf['forecast']).mean():+.1f} AQI. "
                f"Apr-Jun 2020 (lockdown): actual AQI was {(1 - aj['observed_2020'].sum() / aj['forecast'].sum()):.0%} "
                "below the no-lockdown forecast, a rough estimate of the lockdown effect.")

    if comp is not None:
        with st.expander("Compare all forecasting models"):
            cols = [c for c in ["Model", "Test RMSE", "Test MAPE %", "Rolling RMSE", "Rolling MAPE %",
                                "Skill vs seasonal naive %"] if c in comp]
            st.dataframe(comp[cols].round(2), hide_index=True, width="stretch")
            st.caption("Rolling-origin evaluation refits every model at 19 origins (Dec 2017 to Jun 2019) and forecasts "
                       "1-6 months ahead using only data available at the time. Lower is better.")
