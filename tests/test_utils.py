"""Unit tests for the shared rules in src/utils.py."""
import numpy as np
import pytest

from src.utils import aqi_bucket, aqi_group, mape, poor_flag, regression_metrics, season_of


@pytest.mark.parametrize("aqi,bucket", [(0, "Good"), (50, "Good"), (51, "Satisfactory"), (100, "Satisfactory"),
                                        (101, "Moderate"), (200, "Moderate"), (201, "Poor"), (300, "Poor"),
                                        (301, "Very Poor"), (400, "Very Poor"), (401, "Severe"), (999, "Severe")])
def test_aqi_bucket_boundaries(aqi, bucket):
    assert aqi_bucket(aqi) == bucket


def test_targets_agree_with_bands():
    for a in range(0, 600, 7):
        assert poor_flag(a) == int(aqi_bucket(a) in ("Poor", "Very Poor", "Severe"))
        g = aqi_group(a)
        assert g == ("Low" if a <= 100 else "Moderate" if a <= 200 else "High")


def test_seasons_cover_every_month_once():
    seasons = [season_of(m) for m in range(1, 13)]
    assert seasons.count("Winter") == 3 and seasons.count("Summer") == 3
    assert seasons.count("Monsoon") == 4 and seasons.count("Post-monsoon") == 2
    assert season_of(12) == "Winter" and season_of(10) == "Post-monsoon"


def test_metrics():
    y = np.array([100.0, 200.0, 300.0])
    assert mape(y, y) == 0
    assert mape(y, y * 1.1) == pytest.approx(10.0)
    m = regression_metrics(y, y + 10, n_features=1)
    assert m["RMSE"] == pytest.approx(10.0) and m["MAE"] == pytest.approx(10.0)
