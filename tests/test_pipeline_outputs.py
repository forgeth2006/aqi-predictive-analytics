"""Integration tests: the files the notebooks write are complete and consistent."""
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from src.utils import (CONTROL_CSV, DATA_2020, DATA_CLEAN, FORECAST_CSV, PCHART_CSV, POLLUTANTS, ROOT,
                       TABLES_DIR, load_clean)


def test_contract_checker_passes():
    res = subprocess.run([sys.executable, str(ROOT / "src" / "check_contract.py")], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout


def test_clean_data_shape_and_no_hidden_zeros():
    df = load_clean()
    assert len(df) == 1826
    assert (df["CO"] > 0).all(), "CO zeros are sensor outages and must be recoded"
    assert df[POLLUTANTS + ["AQI"]].notna().all().all()


def test_holdout_is_2020_only():
    h = pd.read_csv(DATA_2020, parse_dates=["Date"])
    assert (h["Date"].dt.year == 2020).all()


def test_forecast_file():
    fc = pd.read_csv(FORECAST_CSV)
    for c in ["month", "actual", "forecast", "lower_95", "upper_95", "model"]:
        assert c in fc.columns
    fut = fc[fc["segment"] == "future"]
    assert len(fut) == 6 and fut["actual"].isna().all()
    assert (fut["lower_95"] <= fut["forecast"]).all() and (fut["forecast"] <= fut["upper_95"]).all()


def test_control_files():
    cc = pd.read_csv(CONTROL_CSV)
    assert {"month", "value", "centre", "ucl", "lcl", "out_of_control"} <= set(cc.columns)
    assert (cc["lcl"] < cc["centre"]).all() and (cc["centre"] < cc["ucl"]).all()
    beyond = (cc["value"] > cc["ucl"]) | (cc["value"] < cc["lcl"])
    assert (cc.loc[beyond, "out_of_control"] == 1).all(), "every point beyond 3 sigma must be flagged"
    pc = pd.read_csv(PCHART_CSV)
    assert pc["p"].between(0, 1).all()


@pytest.mark.parametrize("name", ["regression_comparison", "classifier_comparison", "forecast_comparison"])
def test_comparison_tables_exist(name):
    t = pd.read_csv(TABLES_DIR / f"{name}.csv")
    assert len(t) >= 3 and t.select_dtypes("number").notna().any().any()
