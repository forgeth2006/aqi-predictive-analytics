"""Predict tab.

Reads: models/regression_model.json and models/classifier_models.json
(written by notebooks 03 and 04). Nothing is trained here.
"""
import pandas as pd
import streamlit as st

from src.predict_utils import (load_classifiers, load_regression, predict_aqi,
                               predict_group, predict_poor_prob, predict_tree_poor)
from src.utils import POLLUTANTS, SEASONS, aqi_bucket

UNITS = {p: "µg/m³" for p in POLLUTANTS}
UNITS["CO"] = "mg/m³"


@st.cache_data
def _models():
    return load_regression(), load_classifiers()


def _apply_preset(reg: dict, season: str) -> None:
    med = reg.get("season_medians", {}).get(season)
    if not med:
        return
    for p in POLLUTANTS:
        lo, hi, _ = reg["ranges"][p]
        st.session_state[f"in_{p}"] = round(min(max(med[p], lo), hi), 2)


def render() -> None:
    reg, clf = _models()

    st.subheader("Predict AQI from pollutant readings")
    st.caption("Academic prototype for the 23XWA8 Predictive Analytics course. "
               "Not a health advisory and not an official forecast.")

    c1, c2 = st.columns([2, 3])
    season = c1.selectbox("Season", SEASONS, index=0)
    c2.write("")
    if c2.button(f"Fill in a typical {season.lower()} day (seasonal medians)"):
        _apply_preset(reg, season)

    st.markdown("**Pollutant readings** (slider range = 1st to 99th percentile of the 2015-2019 days)")
    cols = st.columns(3)
    inputs = {}
    for i, p in enumerate(POLLUTANTS):
        lo, hi, med = reg["ranges"][p]
        lo, hi, med = round(lo, 2), round(hi, 2), round(min(max(med, lo), hi), 2)
        key = f"in_{p}"
        if key not in st.session_state:
            st.session_state[key] = med
        inputs[p] = cols[i % 3].slider(f"{p} ({UNITS[p]})", lo, hi, step=0.01, key=key)

    mean, lo_i, hi_i = predict_aqi(inputs, season, reg)
    p_poor = predict_poor_prob(inputs, season, clf)
    tree_class, tree_p = predict_tree_poor(inputs, clf)
    groups = predict_group(inputs, clf)
    t_cost = clf["logit"].get("threshold_cost3", 0.5)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Predicted AQI", f"{mean:.0f}", help="Polynomial regression (PM2.5 centred plus a squared term).")
        st.caption(f"Band: **{aqi_bucket(mean)}**")
        st.caption(f"95% prediction interval for one day: {max(lo_i, 0):.0f} to {hi_i:.0f} (approximate)")
    with c2:
        st.metric("Chance of a Poor day (AQI above 200)", f"{p_poor:.0%}", help="Logistic regression.")
        st.caption(f"Warning issued at the cost-tuned threshold ({t_cost:.2f}): "
                   f"**{'Yes' if p_poor >= t_cost else 'No'}**")
        st.caption(f"Decision tree says: **{'Poor' if tree_class else 'Not Poor'}** "
                   f"({tree_p:.0%} of similar training days were Poor)")
    with c3:
        st.markdown("**AQI group probabilities**")
        st.bar_chart(pd.Series(groups, name="Probability"), horizontal=True)
        st.caption("Multinomial regression: Low up to 100, Moderate 101 to 200, High above 200.")

    with st.expander("How to read this, and its limits"):
        st.markdown(
            "- The models were fitted on Delhi daily data, 2015 to 2019, so they do not apply to other cities or to 2020.\n"
            "- AQI is itself computed from the pollutant readings, so these models partly recover the AQI formula. "
            "They show which pollutants drive AQI, not new atmospheric science.\n"
            "- The prediction interval assumes constant error variance, but the real spread grows with AQI, so treat it as approximate.\n"
            f"- The warning threshold {t_cost:.2f} treats a missed Poor day as 3 times as costly as a false alarm.\n"
            "- The three models are separate and can disagree near the boundaries (AQI about 100 and 200).\n"
            f"- Data used for fitting: {reg.get('source', 'n/a')} ({reg.get('n_train', '?')} training days)."
        )
