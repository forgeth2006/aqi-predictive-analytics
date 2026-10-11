"""Forecast tab. Owner: Member 2. Replace this placeholder.

Reads: outputs/forecast_monthly.csv
Columns: month (YYYY-MM), actual (blank for future months), forecast, lower_95, upper_95, model
Never fit ARIMA here. Read the precomputed file.
"""
import streamlit as st


def render() -> None:
    st.subheader("Monthly AQI forecast")
    st.info("Placeholder. Member 2 builds this tab (history plus 6-month forecast with interval, RMSE and MAPE).")
