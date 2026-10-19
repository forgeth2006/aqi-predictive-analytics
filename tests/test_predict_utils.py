"""The app's JSON-based predictions must behave sensibly."""
import math

import pytest

from src.predict_utils import (load_classifiers, load_regression, predict_aqi, predict_group,
                               predict_poor_prob, predict_tree_poor)
from src.utils import POLLUTANTS

REG, CLF = load_regression(), load_classifiers()


def _day(season):
    return dict(REG["season_medians"][season])


@pytest.mark.parametrize("season", ["Winter", "Summer", "Monsoon", "Post-monsoon"])
def test_outputs_are_valid(season):
    x = _day(season)
    mean, lo, hi = predict_aqi(x, season, REG)
    assert lo < mean < hi and math.isfinite(mean)
    p = predict_poor_prob(x, season, CLF)
    assert 0 <= p <= 1
    cls, share = predict_tree_poor(x, CLF)
    assert cls in (0, 1) and 0 <= share <= 1
    g = predict_group(x, CLF)
    assert set(g) == {"Low", "Moderate", "High"} and sum(g.values()) == pytest.approx(1.0)


def test_winter_is_worse_than_monsoon():
    w, m = _day("Winter"), _day("Monsoon")
    assert predict_aqi(w, "Winter", REG)[0] > predict_aqi(m, "Monsoon", REG)[0] + 100
    assert predict_poor_prob(w, "Winter", CLF) > 0.9 > 0.1 > predict_poor_prob(m, "Monsoon", CLF)


def test_more_pm25_means_higher_aqi_within_range():
    x = _day("Summer")
    lo, hi, _ = REG["ranges"]["PM2.5"]
    a = predict_aqi({**x, "PM2.5": lo}, "Summer", REG)[0]
    b = predict_aqi({**x, "PM2.5": hi}, "Summer", REG)[0]
    assert b > a


def test_every_pollutant_has_a_range():
    for p in POLLUTANTS:
        lo, hi, med = REG["ranges"][p]
        assert lo < hi
