"""Predict tab. Owner: Member 1.

Now: a working input form with a dummy output, so the layout is ready.
Gate M2 onwards: load models/*.joblib and show the real predictions.
"""
import streamlit as st

# Slider ranges are placeholders; tighten them from the real data after Gate M1.
INPUTS = {
    "PM2.5": (0.0, 500.0, 100.0),
    "PM10": (0.0, 800.0, 200.0),
    "NO": (0.0, 150.0, 20.0),
    "NO2": (0.0, 200.0, 50.0),
    "NOx": (0.0, 250.0, 60.0),
    "NH3": (0.0, 100.0, 30.0),
    "CO": (0.0, 50.0, 1.5),
    "SO2": (0.0, 100.0, 15.0),
    "O3": (0.0, 200.0, 40.0),
}


def render() -> None:
    st.subheader("Predict AQI from pollutant readings")
    st.caption("Academic prototype. Not a health advisory.")

    cols = st.columns(3)
    values = {}
    for i, (name, (lo, hi, default)) in enumerate(INPUTS.items()):
        values[name] = cols[i % 3].slider(name, lo, hi, default)
    season = st.selectbox("Season", ["Winter", "Summer", "Monsoon", "Post-monsoon"])

    st.divider()
    st.write("Predicted AQI: not available yet")
    st.info("Placeholder. The saved models arrive at Gate M2; this form already collects the inputs.")
    with st.expander("Inputs that will go to the model"):
        st.json({**values, "Season": season})
