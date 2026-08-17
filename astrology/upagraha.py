from typing import Any, Dict
from datetime import datetime, timezone as dt_timezone, timedelta

import pytz
import swisseph as swe


MAANDI_NAME_TAMIL = "மாந்தி"
MAANDI_NAME_ENGLISH = "Maandi"

MAANDI_DAY_VALUES = (
    26,
    22,
    18,
    14,
    10,
    6,
    2,
)

MAANDI_NIGHT_VALUES = (
    10,
    6,
    2,
    26,
    22,
    18,
    14,
)


def calculate_maandi(
    julian_day_ut: float,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> Dict[str, Any]:

    jd_ut = float(julian_day_ut)
    latitude = float(latitude)
    longitude = float(longitude)

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    geopos = (
        longitude,
        latitude,
        0.0,
    )

    rise_flags = (
        swe.CALC_RISE
        | swe.BIT_DISC_CENTER
        | swe.BIT_NO_REFRACTION
    )

    set_flags = (
        swe.CALC_SET
        | swe.BIT_DISC_CENTER
        | swe.BIT_NO_REFRACTION
    )

    def sun_event(
        search_jd: float,
        event_flags: int,
    ) -> float:

        result = swe.rise_trans(
            search_jd,
            swe.SUN,
            event_flags,
            geopos,
        )

        if not result or len(result) < 2:
            raise ValueError(
                "Unable to calculate Sun event"
            )

        return float(result[1][0])

    sunrise = sun_event(
        jd_ut - 1.0,
        rise_flags,
    )

    sunset = sun_event(
        sunrise + 0.001,
        set_flags,
    )

    next_sunrise = sun_event(
        sunset + 0.001,
        rise_flags,
    )

    if not (
        sunrise < sunset < next_sunrise
    ):
        raise ValueError(
            "Invalid sunrise/sunset sequence"
        )

    if sunrise <= jd_ut < sunset:

        is_night = False

        interval_start = sunrise
        interval_end = sunset

        vedic_day_sunrise = sunrise

    elif sunset <= jd_ut < next_sunrise:

        is_night = True

        interval_start = sunset
        interval_end = next_sunrise

        vedic_day_sunrise = sunrise

    else:

        previous_sunrise = sun_event(
            sunrise - 0.5,
            rise_flags,
        )

        previous_sunset = sun_event(
            previous_sunrise + 0.001,
            set_flags,
        )

        if (
            previous_sunset
            <= jd_ut
            < sunrise
        ):

            is_night = True

            interval_start = previous_sunset
            interval_end = sunrise

            vedic_day_sunrise = previous_sunrise

        else:

            raise ValueError(
                "Unable to determine Vedic day/night interval"
            )

    def jd_to_local_datetime(
        jd: float,
    ) -> datetime:

        year, month, day, hour = swe.revjul(
            jd,
            swe.GREG_CAL,
        )

        total_seconds = int(
            round(hour * 3600.0)
        )

        day_offset, seconds = divmod(
            total_seconds,
            86400,
        )

        utc_dt = datetime(
            int(year),
            int(month),
            int(day),
            tzinfo=dt_timezone.utc,
        )

        utc_dt += timedelta(
            days=day_offset,
            seconds=seconds,
        )

        return utc_dt.astimezone(
            pytz.timezone(timezone_name)
        )

    local_sunrise = jd_to_local_datetime(
        vedic_day_sunrise
    )

    weekday_index = (
        local_sunrise.weekday() + 1
    ) % 7

    if is_night:

        maandi_value = MAANDI_NIGHT_VALUES[
            weekday_index
        ]

    else:

        maandi_value = MAANDI_DAY_VALUES[
            weekday_index
        ]

    interval_duration = (
        interval_end - interval_start
    )

    maandi_fraction = (
        maandi_value / 30.0
    )

    maandi_jd = (
        interval_start
        + interval_duration * maandi_fraction
    )

    maandi_cusps, maandi_ascmc = swe.houses_ex(
        maandi_jd,
        latitude,
        longitude,
        b"P",
        swe.FLG_SIDEREAL,
    )

    maandi_longitude = (
        float(maandi_ascmc[0])
        % 360.0
    )

    sign_index = int(
        maandi_longitude // 30.0
    )

    sign_degree = (
        maandi_longitude
        - sign_index * 30.0
    )

    degree = int(sign_degree)

    minute_float = (
        sign_degree - degree
    ) * 60.0

    minute = int(minute_float)

    second = int(
        round(
            (minute_float - minute)
            * 60.0
        )
    )

    if second >= 60:

        second = 0
        minute += 1

    if minute >= 60:

        minute = 0
        degree += 1

    if degree >= 30:

        degree = 0

        sign_index = (
            sign_index + 1
        ) % 12

    nakshatra_size = (
        360.0 / 27.0
    )

    pada_size = (
        nakshatra_size / 4.0
    )

    nakshatra_index = int(
        maandi_longitude
        / nakshatra_size
    )

    nakshatra_index = min(
        max(nakshatra_index, 0),
        26,
    )

    nakshatra_position = (
        maandi_longitude
        - nakshatra_index
        * nakshatra_size
    )

    pada = (
        int(
            nakshatra_position
            / pada_size
        )
        + 1
    )

    pada = min(
        max(pada, 1),
        4,
    )

    return {
        "name_tamil": MAANDI_NAME_TAMIL,
        "name_english": MAANDI_NAME_ENGLISH,
        "longitude": maandi_longitude,
        "latitude": 0.0,
        "distance": 0.0,
        "speed_longitude": 0.0,
        "retrograde": False,
        "sign_index": sign_index,
        "degree": degree,
        "minute": minute,
        "second": second,
        "nakshatra_index": nakshatra_index,
        "pada": pada,
        "raw": {
            "sunrise_jd": sunrise,
            "sunset_jd": sunset,
            "next_sunrise_jd": next_sunrise,
            "vedic_day_sunrise_jd": vedic_day_sunrise,
            "is_night_birth": is_night,
            "vedic_weekday_index": weekday_index,
            "maandi_value": maandi_value,
            "interval_start_jd": interval_start,
            "interval_end_jd": interval_end,
            "interval_duration_days": interval_duration,
            "maandi_fraction": maandi_fraction,
            "maandi_jd": maandi_jd,
            "maandi_ascendant": maandi_longitude,
        },
    }