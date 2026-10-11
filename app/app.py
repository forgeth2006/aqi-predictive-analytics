"""Streamlit app: Delhi AQI, predict and forecast. Owner: Member 1.

Run locally from the repo root:
    streamlit run app/app.py

The app only READS files the notebooks already produced. It never trains a model.
Each tab lives in app/tabs/ so the two members edit different files.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))   # lets us import src.* and app.tabs.*

import streamlit as st  # noqa: E402

from app.tabs import control, eda, forecast, performance, predict  # noqa: E402
from src.utils import CITY, DATA_CLEAN, load_clean  # noqa: E402

st.set_page_config(page_title=f"{CITY} AQI: predict and forecast", layout="wide")


@st.cache_data
def get_clean():
    return load_clean()


def overview() -> None:
    st.subheader("What this app does")
    st.write(
        "This project studies daily air quality (AQI) for one Indian city. It explores the "
        "data, predicts AQI from pollutant readings, forecasts monthly AQI, and checks when "
        "air quality goes out of statistical control."
    )
    if DATA_CLEAN.exists():
        df = get_clean()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Days of data", f"{len(df):,}")
        c2.metric("From", df["Date"].min().strftime("%Y-%m-%d"))
        c3.metric("To", df["Date"].max().strftime("%Y-%m-%d"))
        c4.metric("Mean AQI", f"{df['AQI'].mean():.0f}")
    else:
        st.info("Cleaned dataset not available yet (arrives at Gate M1).")
    st.caption(
        "Academic prototype for the 23XWA8 Predictive Analytics course. "
        "Not a health advisory and not an official forecast."
    )


def show(module) -> None:
    """Render a tab; show a friendly note if its input files are not there yet."""
    try:
        module.render()
    except FileNotFoundError as err:
        st.info(f"This tab is waiting for a file that has not been produced yet: {err}")


st.title(f"{CITY} air quality: predict and forecast")

tab_names = ["Overview", "EDA", "Predict", "Forecast", "Control chart", "Model performance"]
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
