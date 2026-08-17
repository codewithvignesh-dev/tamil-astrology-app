from astrology.ephemeris import calculate_julian_day
from astrology.lagna import calculate_lagna


def test_calculate_lagna_returns_valid_ascendant():
    jd = calculate_julian_day(2002, 8, 10, 5, 30, 0, "Asia/Kolkata")
    lagna = calculate_lagna(jd, 10.7905, 78.7047)

    assert 0 <= lagna["sign_index"] <= 11
    assert lagna["sign"] != ""
    assert lagna["degree"]["degree"] >= 0
    assert 1 <= lagna["pada"] <= 4
    assert len(lagna["houses"]) == 12
