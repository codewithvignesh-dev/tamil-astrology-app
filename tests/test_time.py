from astrology.time_utils import parse_birth_datetime


def test_parse_birth_datetime_utc_conversion():
    local_dt, utc_dt = parse_birth_datetime("2002-08-10", "05:30:00", "Asia/Kolkata")
    assert local_dt.tzinfo.zone == "Asia/Kolkata"
    assert utc_dt.tzinfo.zone == "UTC"
    assert utc_dt.hour == 0 or utc_dt.hour == 23
