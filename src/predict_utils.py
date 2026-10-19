"""Prediction from the exported models (models/*.json).

Pure numpy and the standard library: no statsmodels, no scikit-learn, no pickles.
The notebooks export the fitted models as plain numbers, and this module
rebuilds the predictions from them, so the deployed app cannot break on a
library version mismatch.
"""
from __future__ import annotations

import json
import math

import numpy as np

from src.utils import MODELS_DIR, POLLUTANTS

CLASSES3 = ["Low", "Moderate", "High"]


def _load(name: str) -> dict:
    path = MODELS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path.name} (run notebooks 03 and 04 to create it)")
    return json.loads(path.read_text(encoding="utf-8"))


def load_regression() -> dict:
    return _load("regression_model")


def load_classifiers() -> dict:
    return _load("classifier_models")


# --------------------------------------------------------------------------
# Regression: polynomial model with a 95% prediction interval
# --------------------------------------------------------------------------
def _regression_row(reg: dict, inputs: dict, season: str) -> np.ndarray:
    pm = float(inputs["PM2.5"])
    row = {"const": 1.0}
    for col in reg["final_cols"]:
        if col == "PM2.5":
            row[col] = pm - reg["pm_mean"]                      # centred
        elif col in reg["season_dummies"]:
            row[col] = 1.0 if season == col else 0.0            # Winter = baseline
        else:
            row[col] = float(inputs[col])
    row["PM2.5_sq"] = (pm - reg["pm_mean"]) ** 2
    return np.array([row[c] for c in reg["columns"]], dtype=float)


def predict_aqi(inputs: dict, season: str, reg: dict | None = None, z: float = 1.96):
    """Return (predicted AQI, lower, upper) for one day.

    The interval is the classical 95% prediction interval, which assumes constant
    error variance. The real spread grows with AQI (Breusch-Pagan test), so it is
    approximate.
    """
    reg = reg or load_regression()
    x = _regression_row(reg, inputs, season)
    beta = np.array([reg["params"][c] for c in reg["columns"]], dtype=float)
    cov = np.array(reg["cov"], dtype=float)
    mean = float(x @ beta)
    half = z * math.sqrt(float(x @ cov @ x) + reg["scale"])
    return mean, mean - half, mean + half


# --------------------------------------------------------------------------
# Logistic regression: probability of a Poor day (AQI above 200)
# --------------------------------------------------------------------------
def predict_poor_prob(inputs: dict, season: str, clf: dict | None = None) -> float:
    clf = clf or load_classifiers()
    cols, params = clf["logit"]["columns"], clf["logit"]["params"]
    eta = 0.0
    for c in cols:
        if c == "const":
            v = 1.0
        elif c in POLLUTANTS:
            v = float(inputs[c])
        else:
            v = 1.0 if season == c else 0.0
        eta += params[c] * v
    return 1.0 / (1.0 + math.exp(-eta))


# --------------------------------------------------------------------------
# CART tree: Poor day or not, from the exported tree arrays
# --------------------------------------------------------------------------
def predict_tree_poor(inputs: dict, clf: dict | None = None):
    """Return (predicted class 0/1, share of Poor days in the leaf)."""
    clf = clf or load_classifiers()
    t = clf["tree_poor"]
    x = [float(inputs[f]) for f in t["feature_names"]]
    node = 0
    while t["children_left"][node] != -1:
        if x[t["feature"][node]] <= t["threshold"][node]:
            node = t["children_left"][node]
        else:
            node = t["children_right"][node]
    counts = t["value"][node]
    p_poor = counts[1] / sum(counts)
    return int(p_poor >= 0.5), float(p_poor)


# --------------------------------------------------------------------------
# Multinomial regression: probabilities of Low / Moderate / High
# --------------------------------------------------------------------------
def predict_group(inputs: dict, clf: dict | None = None) -> dict:
    clf = clf or load_classifiers()
    m = clf["multinomial"]
    raw = np.array([float(inputs[p]) for p in m["pollutants"]])
    z = (raw - np.array(m["scaler_mean"])) / np.array(m["scaler_scale"])
    x = np.concatenate([[1.0], z])                     # const first, as in training
    eta = x @ np.array(m["params"], dtype=float)       # columns: Moderate, High vs Low
    logits = np.concatenate([[0.0], eta])
    p = np.exp(logits - logits.max())
    p = p / p.sum()
    return {name: float(v) for name, v in zip(m["classes"], p)}
