"""Shared helpers for the AQI predictive analytics project.

Owner: Member 1. Member 2 may import from here but should ask before editing.

Every path in the project is built from ROOT so notebooks, the app and the
deployed server all find the same files.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw" / "city_day.csv"
DATA_CLEAN = ROOT / "data" / "processed" / "aqi_delhi_clean.csv"
MODELS_DIR = ROOT / "models"
TABLES_DIR = ROOT / "outputs" / "tables"
FIGURES_DIR = ROOT / "outputs" / "figures"
FORECAST_CSV = ROOT / "outputs" / "forecast_monthly.csv"
CONTROL_CSV = ROOT / "outputs" / "control_chart.csv"

# --------------------------------------------------------------------------
# Shared settings (see tab 5, Shared Standards)
# --------------------------------------------------------------------------
SEED = 42
ALPHA = 0.05            # significance level
CONF_LEVEL = 0.95       # confidence level
TEST_SIZE = 0.2         # random 80/20 split for regression and classification

CITY = "Delhi"
WINDOW_START = "2015-01-01"
WINDOW_END = "2019-12-31"
TS_TRAIN_END = "2019-06"    # monthly time series: train 2015-01 to 2019-06
TS_TEST_START = "2019-07"   # test 2019-07 to 2019-12

POLLUTANTS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3"]
SEASONS = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
BUCKETS = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
GROUPS = ["Low", "Moderate", "High"]

CONTRACT_COLUMNS = (
    ["Date"] + POLLUTANTS
    + ["AQI", "AQI_Bucket", "Year", "Month", "Season", "Poor_Flag", "AQI_Group"]
)


# --------------------------------------------------------------------------
# Derived-column rules (the single source of truth for both members)
# --------------------------------------------------------------------------
def season_of(month: int) -> str:
    """Winter Dec-Feb, Summer Mar-May, Monsoon Jun-Sep, Post-monsoon Oct-Nov."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Summer"
    if month in (6, 7, 8, 9):
        return "Monsoon"
    return "Post-monsoon"


def aqi_bucket(aqi: float) -> str:
    """Indian AQI bands: 0-50, 51-100, 101-200, 201-300, 301-400, above 400."""
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Satisfactory"
    if aqi <= 200:
        return "Moderate"
    if aqi <= 300:
        return "Poor"
    if aqi <= 400:
        return "Very Poor"
    return "Severe"


def aqi_group(aqi: float) -> str:
    """Three-class target: Low (up to 100), Moderate (101-200), High (above 200)."""
    if aqi <= 100:
        return "Low"
    if aqi <= 200:
        return "Moderate"
    return "High"


def poor_flag(aqi: float) -> int:
    """Binary target: 1 when AQI is above 200."""
    return int(aqi > 200)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_clean(index_by_date: bool = False) -> pd.DataFrame:
    """Load the cleaned dataset delivered by Member 2 (Gate M1)."""
    if not DATA_CLEAN.exists():
        raise FileNotFoundError(
            f"{DATA_CLEAN} not found. It arrives at Gate M1 from Member 2."
        )
    df = pd.read_csv(DATA_CLEAN, parse_dates=["Date"])
    return df.set_index("Date") if index_by_date else df


def save_table(df: pd.DataFrame, name: str, index: bool = False) -> Path:
    """Save a result table to outputs/tables/<name>.csv and return the path."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLES_DIR / (name if name.endswith(".csv") else f"{name}.csv")
    df.to_csv(path, index=index)
    return path


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def mape(y_true, y_pred) -> float:
    """Mean absolute percentage error, in percent. Ignores zero actuals."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def regression_metrics(y_true, y_pred, n_features: int | None = None) -> dict:
    """R-squared, adjusted R-squared (needs n_features), RMSE, MAE."""
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    n = len(y_true)
    r2 = r2_score(y_true, y_pred)
    adj = np.nan
    if n_features is not None and n - n_features - 1 > 0:
        adj = 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
    return {
        "R2": float(r2),
        "Adj_R2": float(adj),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
    }


def classification_metrics(y_true, y_pred, y_proba=None) -> dict:
    """Accuracy, precision, recall, F1 and ROC-AUC.

    Two classes: binary scores for the positive class (label 1) and
    ROC-AUC from y_proba as a 1-D array of P(class 1).
    More than two classes: macro-averaged scores and one-vs-rest ROC-AUC
    from y_proba as an (n_samples, n_classes) array in sorted-label order.
    """
    from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                                 recall_score, roc_auc_score)

    classes = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
    binary = len(classes) <= 2
    avg = "binary" if binary else "macro"
    out = {
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "Precision": float(precision_score(y_true, y_pred, average=avg, zero_division=0)),
        "Recall": float(recall_score(y_true, y_pred, average=avg, zero_division=0)),
        "F1": float(f1_score(y_true, y_pred, average=avg, zero_division=0)),
        "ROC_AUC": np.nan,
    }
    if y_proba is not None:
        if binary:
            out["ROC_AUC"] = float(roc_auc_score(y_true, y_proba))
        else:
            out["ROC_AUC"] = float(
                roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
            )
    return out


# --------------------------------------------------------------------------
# Plot style
# --------------------------------------------------------------------------
def set_plot_style() -> None:
    """One consistent look for every figure. Call once at the top of a notebook."""
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.figsize": (8, 4.5),
        "figure.dpi": 110,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "legend.frameon": False,
    })


def save_figure(fig, name: str) -> Path:
    """Save a matplotlib figure to outputs/figures/<name>.png."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / (name if name.endswith(".png") else f"{name}.png")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    return path
