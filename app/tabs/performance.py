"""Model performance tab. Owner: Member 1.

Reads: outputs/tables/regression_comparison.csv, outputs/tables/classifier_comparison.csv
"""
import pandas as pd
import streamlit as st

from src.utils import TABLES_DIR


def _show_table(title: str, filename: str) -> None:
    path = TABLES_DIR / filename
    st.markdown(f"**{title}**")
    if path.exists():
        st.dataframe(pd.read_csv(path), use_container_width=True)
    else:
        st.info(f"{filename} not produced yet.")


def render() -> None:
    st.subheader("Model performance")
    _show_table("Regression models (R-squared, adjusted R-squared, RMSE, MAE)", "regression_comparison.csv")
    _show_table("Classifiers (accuracy, precision, recall, F1, ROC-AUC)", "classifier_comparison.csv")
