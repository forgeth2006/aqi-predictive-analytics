"""Model performance tab.

Reads: outputs/tables/regression_comparison.csv, classifier_comparison.csv, forecast_comparison.csv
"""
import pandas as pd
import streamlit as st

from src.utils import TABLES_DIR


def _show_table(title: str, filename: str, caption: str, cols=None) -> None:
    path = TABLES_DIR / filename
    st.markdown(f"**{title}**")
    if path.exists():
        t = pd.read_csv(path)
        if cols:
            t = t[[c for c in cols if c in t.columns]]
        st.dataframe(t.round(3), hide_index=True, width="stretch")
        st.caption(caption)
    else:
        st.info(f"{filename} has not been produced yet.")


def render() -> None:
    st.subheader("Model performance")
    st.caption("Regression and classification scores are on held-out test days (random 80/20 split, seed 42), "
               "plus cross-validation and a stricter forward-in-time test (train 2015-2018, test 2019).")

    _show_table(
        "Regression models (predicting the day's AQI from that day's pollutants)",
        "regression_comparison.csv",
        "Lower RMSE/MAE and higher R² are better. The polynomial regression is best among the regression equations on "
        "adjusted R², AIC, cross-validation and the 2019 test; the CART regression tree ties it on RMSE with the lowest MAE.",
        ["Model", "k", "R2", "Adj_R2", "RMSE", "MAE", "AIC", "CV10 RMSE mean", "2019 test RMSE", "2019 test R2"],
    )
    _show_table(
        "Classifiers (Poor day, and the 3 AQI groups)",
        "classifier_comparison.csv",
        "Compare models only within a task. The 3-class rows use macro-averaged scores and one-vs-rest ROC-AUC. "
        "Gini = 2 × ROC-AUC - 1. Logistic regression wins the Poor-day task; the random forest is a beyond-syllabus "
        "benchmark and does not beat it.",
    )
    _show_table(
        "Monthly forecasting models (6 months ahead)",
        "forecast_comparison.csv",
        "Test = Jul-Dec 2019 forecast from June 2019. Rolling = 19 origins, horizons 1-6. Skill is the RMSE reduction "
        "over the seasonal naive benchmark ('same month last year').",
    )
