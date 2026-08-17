import os
from datetime import datetime
from typing import Dict, Any

import pytz
import swisseph as swe

from astrology.upagraha import calculate_maandi
from config import Config
from astrology.angles import normalize_degree, decimal_to_dms
from astrology.constants import PLANET_IDS, PLANET_NAMES_TAMIL, PLANET_NAMES_ENGLISH, SIGNS_TAMIL, SIGNS_ENGLISH
from astrology.exceptions import EphemerisError


swe.set_ephe_path(os.path.abspath(Config.EPHEMERIS_PATH))


def _resolve_sidereal_mode() -> int:
    mode = getattr(Config, "SIDEREAL_MODE", "LAHIRI").upper()
    if mode == "LAHIRI":
        return swe.SIDM_LAHIRI
    if mode == "DELUCE":
        return swe.SIDM_DELUCE
    return mode


def _set_sidereal_mode() -> None:
    swe.set_sid_mode(_resolve_sidereal_mode())


def julian_day_from_datetime(utc_datetime: datetime) -> float:
    return swe.julday(utc_datetime.year, utc_datetime.month, utc_datetime.day, utc_datetime.hour + utc_datetime.minute / 60.0 + utc_datetime.second / 3600.0,)


def calculate_julian_day(year: int, month: int, day: int, hour: int, minute: int, second: int, timezone_name: str,) -> float:
    timezone = pytz.timezone(timezone_name)
    local_dt = timezone.localize(datetime(year, month, day, hour, minute, second))
    utc_dt = local_dt.astimezone(pytz.UTC)
    return julian_day_from_datetime(utc_dt)


def calculate_ayanamsa(jd_ut: float) -> Dict[str, Any]:
    try:
        _set_sidereal_mode()
        ayanamsa = swe.get_ayanamsa_ut(jd_ut)
        d, m, s = decimal_to_dms(ayanamsa)
        return {
            "degrees": ayanamsa,
            "dms": {"degree": d, "minute": m, "second": s},
        }
    except Exception as exc:
        raise EphemerisError("Ayanamsa calculation failed") from exc


def calculate_planet_position(jd_ut: float, planet_key: str, node_mode: str = "MEAN", latitude: float = 0.0, longitude: float = 0.0, timezone_name: str = "Asia/Kolkata") -> Dict[str, Any]:
    if planet_key == "Maandi":
        return calculate_maandi(jd_ut, latitude, longitude, "Asia/Kolkata")
    if planet_key not in PLANET_IDS:
        raise EphemerisError(f"Unknown planet key: {planet_key}")

    _set_sidereal_mode()
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    use_true_node = node_mode.upper() == "TRUE"

    try:
        if planet_key in ("Rahu", "Ketu"):
            node_id = swe.TRUE_NODE if use_true_node else swe.MEAN_NODE
            result = swe.calc_ut(jd_ut, node_id, flags)[0]
            node_longitude = normalize_degree(result[0])
            longitude = normalize_degree(node_longitude + (180.0 if planet_key == "Ketu" else 0.0))
        else:
            body_id = PLANET_IDS[planet_key]
            result = swe.calc_ut(jd_ut, body_id, flags)[0]
            longitude = normalize_degree(result[0])

        # small manual adjustments (reduce by given seconds) per user request
        # values are seconds to subtract from the longitude
        adjustments_seconds = {
            "Sun": 67,    # 1'7" = 67 seconds
            "Moon": 69,   # 1'9" = 69 seconds
            "Saturn": 69, # 1'9" = 69 seconds
        }
        if planet_key in adjustments_seconds:
            # subtract the adjustment (convert seconds to degrees)
            adj_deg = -adjustments_seconds[planet_key] / 3600.0
            longitude = normalize_degree(longitude + adj_deg)

        latitude = float(result[1])
        distance = float(result[2]) if len(result) > 2 else 0.0
        speed_longitude = float(result[3]) if len(result) > 3 else 0.0
        retrograde = speed_longitude < 0.0
        sign_idx = int(longitude // 30)
        degree, minute, second = decimal_to_dms(longitude % 30.0)

        return {
            "name_tamil": PLANET_NAMES_TAMIL[planet_key],
            "name_english": PLANET_NAMES_ENGLISH[planet_key],
            "longitude": longitude,
            "latitude": latitude,
            "distance": distance,
            "speed_longitude": speed_longitude,
            "retrograde": retrograde,
            "sign_index": sign_idx,
            "sign_tamil": "",
            "sign_english": "",
            "degree": degree,
            "minute": minute,
            "second": second,
            "nakshatra": "",
            "nakshatra_index": -1,
            "pada": -1,
            "raw": {"result": result},
        }
    except Exception as exc:
        raise EphemerisError(f"Planet calculation failed for {planet_key}") from exc


def calculate_planets(jd_ut: float, latitude: float, longitude: float, timezone_name: str, node_mode: str = "MEAN") -> Dict[str, Dict[str, Any]]:
    planets = {}
    for planet_key in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Maandi"]:
        planets[planet_key] = calculate_planet_position(jd_ut, planet_key, node_mode, latitude, longitude, timezone_name)
    return planets

def calculate_paava_chakram(
    jd_ut: float,
    latitude: float,
    longitude: float,
    planets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:

    _set_sidereal_mode()

    cusps, ascmc = swe.houses_ex(
        jd_ut,
        float(latitude),
        float(longitude),
        b'P',
        swe.FLG_SIDEREAL,
    )

    asc = float(ascmc[0]) % 360.0
    mc = float(ascmc[1]) % 360.0

    desc = (asc + 180.0) % 360.0
    ic = (mc + 180.0) % 360.0

    def forward_arc(start, end):
        return (end - start) % 360.0

    def divide_arc(start, end, fraction):
        return (
            start +
            forward_arc(start, end) * fraction
        ) % 360.0

    def circular_midpoint(a, b):
        return (
            a +
            forward_arc(a, b) / 2.0
        ) % 360.0

    def dms(value):
        value %= 360.0

        degree = int(value)
        remainder = (value - degree) * 60.0

        minute = int(remainder)
        second = round((remainder - minute) * 60.0)

        if second >= 60:
            second = 0
            minute += 1

        if minute >= 60:
            minute = 0
            degree = (degree + 1) % 360

        return degree, minute, second

    bhava_midpoints = [
        asc,
        divide_arc(asc, ic, 1 / 3),
        divide_arc(asc, ic, 2 / 3),
        ic,
        divide_arc(ic, desc, 1 / 3),
        divide_arc(ic, desc, 2 / 3),
        desc,
        divide_arc(desc, mc, 1 / 3),
        divide_arc(desc, mc, 2 / 3),
        mc,
        divide_arc(mc, asc, 1 / 3),
        divide_arc(mc, asc, 2 / 3),
    ]

    def contains_longitude(start, longitude_value, end):
        total = forward_arc(start, end)
        position = forward_arc(start, longitude_value)
        return position < total or abs(position - total) < 1e-10

    houses = []

    for index in range(12):

        previous_mid = bhava_midpoints[(index - 1) % 12]
        current_mid = bhava_midpoints[index]
        next_mid = bhava_midpoints[(index + 1) % 12]

        start = circular_midpoint(
            previous_mid,
            current_mid,
        )

        end = circular_midpoint(
            current_mid,
            next_mid,
        )

        mid_degree, mid_minute, mid_second = dms(current_mid)
        start_degree, start_minute, start_second = dms(start)
        end_degree, end_minute, end_second = dms(end)

        house_planets = []
        house_planet_keys = []

        for planet_key, planet in planets.items():

            planet_longitude = float(
                planet["longitude"]
            ) % 360.0

            if contains_longitude(
                start,
                planet_longitude,
                end,
            ):
                house_planet_keys.append(planet_key)
                house_planets.append(
                    planet.get(
                        "name_tamil",
                        planet_key,
                    )
                )

        houses.append({
            "house": index + 1,

            "start": start,
            "start_degree": start_degree,
            "start_minute": start_minute,
            "start_second": start_second,

            "mid": current_mid,
            "degree": mid_degree,
            "minute": mid_minute,
            "second": mid_second,

            "end": end,
            "end_degree": end_degree,
            "end_minute": end_minute,
            "end_second": end_second,

            "planet_keys": house_planet_keys,
            "planets": house_planets,
        })

    planet_house_map = {}

    for planet_key, planet in planets.items():

        planet_longitude = float(
            planet["longitude"]
        ) % 360.0

        assigned_house = None

        for house in houses:

            if contains_longitude(
                house["start"],
                planet_longitude,
                house["end"],
            ):
                assigned_house = house["house"]
                break

        planet_house_map[planet_key] = assigned_house

    return {
        "lagna": asc,

        "angles": {
            "ascendant": asc,
            "mc": mc,
            "descendant": desc,
            "ic": ic,
        },

        "houses": houses,

        "planets": planet_house_map,

        "house_system": "Sripati",

        "source_house_system": "Sripati",

        "julian_day": jd_ut,
        "latitude": latitude,
        "longitude": longitude,
    }