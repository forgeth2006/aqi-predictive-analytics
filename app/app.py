"""Streamlit app: Delhi AQI, explore, predict, forecast and monitor.

Run locally from the repo root:
    streamlit run app/app.py

The app only READS files the notebooks already produced. It never trains a model.
Each tab lives in its own module in app/tabs/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))   # lets us import src.* and app.tabs.*

import streamlit as st  # noqa: E402

from app.tabs import control, eda, forecast, performance, predict  # noqa: E402
from src.utils import CITY, DATA_CLEAN, load_clean  # noqa: E402

st.set_page_config(page_title=f"{CITY} AQI: predict and forecast", page_icon="🌫️", layout="wide")


@st.cache_data
def get_clean():
    return load_clean()


def overview() -> None:
    st.subheader("What this app does")
    st.write(
        "This project studies daily air quality (AQI) in Delhi from 2015 to 2019. It explores the data, "
        "measures which pollutants drive AQI, predicts AQI and the chance of a Poor day from pollutant readings, "
        "forecasts monthly AQI six months ahead, and uses control charts to find when air quality went out of "
        "statistical control."
    )
    if DATA_CLEAN.exists():
        df = get_clean()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Days of data", f"{len(df):,}")
        c2.metric("Period", f"{df['Date'].min():%Y} to {df['Date'].max():%Y}")
        c3.metric("Mean AQI", f"{df['AQI'].mean():.0f}")
        c4.metric("Days Poor or worse", f"{df['Poor_Flag'].mean():.0%}")
    else:
        st.info("Cleaned dataset not found. Run notebooks/01_wrangling.ipynb first.")

    st.markdown("#### Key findings")
    st.markdown(
        "- **Particulates drive AQI.** PM2.5 and PM10 correlate 0.88 with AQI and have the largest standardised "
        "coefficients; PM2.5 alone explains 78% of daily variation.\n"
        "- **Seasonality is huge.** November averages about 400 and July-August about 135. Winter has no Good or "
        "Satisfactory day in five years.\n"
        "- **Prediction works.** Polynomial regression: test R² 0.885 (RMSE 40). Logistic regression for a Poor day: "
        "accuracy 0.94, ROC-AUC 0.98.\n"
        "- **Forecasting.** A trend-plus-month regression beats SARIMA, Holt-Winters and VAR over 19 rolling origins "
        "(27% better than 'same month last year') and shows AQI falling about 19 points a year.\n"
        "- **Out of control.** The control charts flag the November 2016 smog episode, a sustained improvement from "
        "2017, and March-June 2020, when the COVID-19 lockdown pushed AQI 36% below the forecast."
    )
    st.caption("Academic prototype for the 23XWA8 Predictive Analytics course. "
               "Not a health advisory and not an official forecast.")


def show(module) -> None:
    """Render a tab; show a friendly note if its input files are not there yet."""
    try:
        module.render()
    except FileNotFoundError as err:
        st.info(f"This tab is waiting for a file that has not been produced yet: {err}")


st.title(f"{CITY} air quality: explore, predict, forecast")

tab_names = ["Overview", "EDA", "Predict", "Forecast", "Control charts", "Model performance"]
tabs = st.tabs(tab_names)
with tabs[0]:
    overview()
with tabs[1]:
    show(eda)
with tabs[2]:
    show(predict)
with tabs[3]:
    show(forecast)
with tabs[4]:
    show(control)
with tabs[5]:
    show(performance)
