from datetime import datetime, timedelta
from typing import Tuple
import pytz


def parse_birth_datetime(date_text: str, time_text: str, timezone_name: str) -> Tuple[datetime, datetime]:
    tz = pytz.timezone(timezone_name)
    date_parts = [int(part) for part in date_text.split("-")]
    time_parts = [int(part) for part in time_text.split(":")]
    if len(time_parts) == 2:
        time_parts.append(0)
    local = tz.localize(
        datetime(date_parts[0], date_parts[1], date_parts[2], time_parts[0], time_parts[1], time_parts[2])
    )
    utc = local.astimezone(pytz.UTC)
    return local, utc


def datetime_to_julian_day(utc_datetime: datetime) -> float:
    from astrology import ephemeris
    return ephemeris.julian_day_from_datetime(utc_datetime)


def format_local_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_timezone(timezone_name: str) -> str:
    return timezone_name
