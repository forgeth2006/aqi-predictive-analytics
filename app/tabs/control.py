"""Control chart tab. Owner: Member 2. Replace this placeholder.

Reads: outputs/control_chart.csv
Columns: month (YYYY-MM), value, centre, ucl, lcl, out_of_control (0 or 1)
"""
import streamlit as st


def render() -> None:
    st.subheader("Control chart")
    st.info("Placeholder. Member 2 builds this tab (monthly AQI with control limits and flagged months).")
