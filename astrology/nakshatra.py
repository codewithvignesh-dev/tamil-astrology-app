from astrology.constants import *
from astrology.angles import normalize_degree, decimal_to_dms

from datetime import datetime, timedelta, timezone
from calendar import monthrange
from zoneinfo import ZoneInfo
import swisseph as swe


def nakshatra_from_longitude(longitude: float) -> dict:
    full_longitude = normalize_degree(longitude)
    d, m, s = decimal_to_dms(full_longitude)
    display_longitude = d + (m / 60.0)
    pada_longitude = full_longitude

    nakshatra_size = 360.0 / 27.0
    pada_size = nakshatra_size / 4.0

    index = int(pada_longitude / nakshatra_size)

    index = min(max(index, 0), 26)

    position = pada_longitude - (index * nakshatra_size)

    pada = int(position + 1e-10) // int(pada_size) + 1
    pada = min(max(pada, 1), 4)

    return {
        "index": index,
        "name_tamil": NAKSHATRAS_TAMIL[index],
        "name_english": NAKSHATRAS_ENGLISH[index],
        "longitude": display_longitude,
        "position_in_nakshatra": position,
        "pada": pada,
    }

def yoga_from_longitudes(sun_longitude: float, moon_longitude: float) -> dict:
    total_longitude = normalize_degree(sun_longitude + moon_longitude)
    yoga_size = 360.0 / 27.0
    index = int(total_longitude / yoga_size)
    position = total_longitude % yoga_size
    return {
        "index": index,
        "name_tamil": YOGAS_TAMIL[index],
        "name_english": YOGAS_ENGLISH[index],
        "longitude": total_longitude,
        "position_in_yoga": position,
    }

def thithi_from_longitudes(sun_longitude: float, moon_longitude: float) -> dict:
    elongation = normalize_degree(moon_longitude - sun_longitude)

    thithi_size = 360.0 / 30.0
    index = int(elongation / thithi_size)

    paksha = "சுக்ல பக்ஷம்" if index < 15 else "கிருஷ்ண பக்ஷம்"

    return {
        "index": index,
        "name_tamil": THITHI_TAMIL[index],
        "name_english": THITHI_ENGLISH[index],   
        "number": index + 1,
        "paksha": paksha,
        "elongation": elongation,
        "position_in_thithi": elongation % thithi_size,
    }

def karana_from_longitudes(sun_longitude: float, moon_longitude: float) -> dict:
    elongation = (moon_longitude - sun_longitude) % 360.0
    raw_index = int(elongation / 6.0)
    
    if raw_index == 0:
        name_array_idx = 10
    elif 1 <= raw_index <= 56:
        name_array_idx = (raw_index - 1) % 7
    elif raw_index == 57:
        name_array_idx = 7
    elif raw_index == 58:
        name_array_idx = 8
    elif raw_index == 59:
        name_array_idx = 9

    return {
        "raw_index_60": raw_index + 1,
        "array_index_11": name_array_idx,
        "index": name_array_idx,
        "name_tamil": KARANA_TAMIL[name_array_idx],
        "name_english": KARANA_ENGLISH[name_array_idx],
        "elongation": elongation,
        "position_in_karana": elongation % 6.0,
    }

def utc_to_local(
    utc_dt: datetime,
    timezone_name: str,
) -> datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    return utc_dt.astimezone(ZoneInfo(timezone_name))


def calculate_sunrise_sunset(
    julian_day_ut: float,
    latitude: float,
    longitude: float,
    timezone_name: str,
):
    geopos = (
        float(longitude),
        float(latitude),
        0.0,
    )

    sunrise_result = swe.rise_trans(
        float(julian_day_ut),
        swe.SUN,
        swe.CALC_RISE,
        geopos,
    )

    sunset_result = swe.rise_trans(
        float(julian_day_ut),
        swe.SUN,
        swe.CALC_SET,
        geopos,
    )

    sunrise_jd = sunrise_result[1][0]
    sunset_jd = sunset_result[1][0]

    sunrise_parts = swe.revjul(
        sunrise_jd,
        swe.GREG_CAL,
    )

    sunset_parts = swe.revjul(
        sunset_jd,
        swe.GREG_CAL,
    )

    sunrise_year = int(sunrise_parts[0])
    sunrise_month = int(sunrise_parts[1])
    sunrise_day = int(sunrise_parts[2])
    sunrise_hour = float(sunrise_parts[3])

    sunset_year = int(sunset_parts[0])
    sunset_month = int(sunset_parts[1])
    sunset_day = int(sunset_parts[2])
    sunset_hour = float(sunset_parts[3])

    sunrise_utc = (
        datetime(
            sunrise_year,
            sunrise_month,
            sunrise_day,
            tzinfo=timezone.utc,
        )
        + timedelta(hours=sunrise_hour)
    )

    sunset_utc = (
        datetime(
            sunset_year,
            sunset_month,
            sunset_day,
            tzinfo=timezone.utc,
        )
        + timedelta(hours=sunset_hour)
    )

    sunrise_local = utc_to_local(
        sunrise_utc,
        timezone_name,
    )

    sunset_local = utc_to_local(
        sunset_utc,
        timezone_name,
    )

    return sunrise_local, sunset_local

def calculate_vimshottari_dasha(
    birth_datetime: datetime,
    moon_sidereal_longitude: float,
):
    NAKSHATRA_SPAN = 360.0 / 27.0

    moon_sidereal_longitude %= 360.0

    nakshatra_index = int(
        moon_sidereal_longitude / NAKSHATRA_SPAN
    )

    nakshatra_lord = NAKSHATRA_LORDS_TAMIL[nakshatra_index]

    nakshatra_start = nakshatra_index * NAKSHATRA_SPAN

    degrees_into_nakshatra = (
        moon_sidereal_longitude - nakshatra_start
    )

    nakshatra_fraction_completed = (
        degrees_into_nakshatra / NAKSHATRA_SPAN
    )

    nakshatra_fraction_remaining = (
        1.0 - nakshatra_fraction_completed
    )

    first_dasha_years = (
        VIMSHOTTARI_YEARS_TAMIL[nakshatra_lord]
    )

    first_dasha_remaining_years = (
        first_dasha_years
        * nakshatra_fraction_remaining
    )

    first_dasha_remaining_days = (
        first_dasha_remaining_years
        * 365.2425
    )

    start_index = VIMSHOTTARI_SEQUENCE_TAMIL.index(
        nakshatra_lord
    )

    first_dasha_end = (
        birth_datetime
        + timedelta(days=first_dasha_remaining_days)
    )

    first_dasha_start = (
        first_dasha_end
        - timedelta(days=first_dasha_years * 365.2425)
    )

    dashas = []

    current_start = first_dasha_start

    for cycle_index in range(9):

        planet_index = (
            start_index + cycle_index
        ) % 9

        planet = VIMSHOTTARI_SEQUENCE_TAMIL[planet_index]

        total_years = VIMSHOTTARI_YEARS_TAMIL[planet]

        if cycle_index == 0:
            current_end = first_dasha_end
        else:
            current_end = (
                current_start
                + timedelta(days=total_years * 365.2425)
            )

        bhuktis = []

        bhukti_start = current_start

        planet_position = (
            VIMSHOTTARI_SEQUENCE_TAMIL.index(planet)
        )

        for bhukti_offset in range(9):

            bhukti_index = (
                planet_position + bhukti_offset
            ) % 9

            bhukti_planet = (
                VIMSHOTTARI_SEQUENCE_TAMIL[bhukti_index]
            )

            bhukti_planet_years = (
                VIMSHOTTARI_YEARS_TAMIL[bhukti_planet]
            )

            bhukti_years = (
                total_years
                * bhukti_planet_years
                / 120.0
            )

            bhukti_end = (
                bhukti_start
                + timedelta(days=bhukti_years * 365.2425)
            )

            if bhukti_end > current_end:
                bhukti_end = current_end

            if cycle_index == 0:

                if bhukti_end <= birth_datetime:
                    bhukti_start = bhukti_end
                    continue

                display_start = max(
                    bhukti_start,
                    birth_datetime
                )

                bhuktis.append({
                    "planet": bhukti_planet,
                    "start": display_start,
                    "end": bhukti_end,
                })

            else:

                bhuktis.append({
                    "planet": bhukti_planet,
                    "start": bhukti_start,
                    "end": bhukti_end,
                })

            bhukti_start = bhukti_end

            if bhukti_end >= current_end:
                break

        dashas.append({
            "planet": planet,
            "start": current_start,
            "end": current_end,
            "bhuktis": bhuktis,
        })

        current_start = current_end

    return dashas

def calculate_tamil_solar_date(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> dict:
    if birth_datetime.tzinfo is None:
        birth_datetime = birth_datetime.replace(
            tzinfo=ZoneInfo(timezone_name)
        )

    birth_utc = birth_datetime.astimezone(timezone.utc)

    jd_ut = swe.julday(
        birth_utc.year,
        birth_utc.month,
        birth_utc.day,
        birth_utc.hour
        + birth_utc.minute / 60.0
        + birth_utc.second / 3600.0
        + birth_utc.microsecond / 3600000000.0,
    )

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    sun_result = swe.calc_ut(
        jd_ut,
        swe.SUN,
        flags,
    )

    sun_longitude = sun_result[0][0] % 360.0

    sun_sign_index = int(sun_longitude // 30.0)

    tamil_month = TAMIL_SOLAR_MONTHS[sun_sign_index]

    target_longitude = sun_sign_index * 30.0

    def get_relative_sun_longitude(jd):
        result = swe.calc_ut(
            jd,
            swe.SUN,
            flags,
        )

        longitude = result[0][0] % 360.0

        return (longitude - target_longitude) % 360.0

    search_start = jd_ut - 40.0
    search_end = jd_ut
    step = 0.25

    previous_jd = search_start
    previous_position = get_relative_sun_longitude(
        previous_jd
    )

    ingress_jd = None
    current_jd = search_start + step

    while current_jd <= search_end:
        current_position = get_relative_sun_longitude(
            current_jd
        )

        if current_position < previous_position:
            low_jd = previous_jd
            high_jd = current_jd

            for _ in range(50):
                mid_jd = (low_jd + high_jd) / 2.0

                mid_position = get_relative_sun_longitude(
                    mid_jd
                )

                if mid_position < 180.0:
                    high_jd = mid_jd
                else:
                    low_jd = mid_jd

            ingress_jd = (low_jd + high_jd) / 2.0
            break

        previous_jd = current_jd
        previous_position = current_position
        current_jd += step

    if ingress_jd is None:
        raise ValueError(
            "Unable to determine Tamil solar month ingress"
        )

    ingress_parts = swe.revjul(
        ingress_jd,
        swe.GREG_CAL,
    )

    ingress_year = int(ingress_parts[0])
    ingress_month = int(ingress_parts[1])
    ingress_day = int(ingress_parts[2])
    ingress_hour = float(ingress_parts[3])

    ingress_utc = (
        datetime(
            ingress_year,
            ingress_month,
            ingress_day,
            tzinfo=timezone.utc,
        )
        + timedelta(hours=ingress_hour)
    )

    ingress_local = ingress_utc.astimezone(
        ZoneInfo(timezone_name)
    )

    birth_local_date = birth_datetime.astimezone(
        ZoneInfo(timezone_name)
    ).date()

    tamil_month_date = (
        birth_local_date - ingress_local.date()
    ).days + 1

    return {
        "month": tamil_month,
        "date": tamil_month_date,
        "formatted": f"{tamil_month} {tamil_month_date}",
        "solar_sign_index": sun_sign_index,
        "solar_longitude": sun_longitude,
        "ingress": ingress_local,
    }