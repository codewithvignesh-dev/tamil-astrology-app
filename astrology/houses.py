from typing import List

import swisseph as swe

from config import Config
from astrology.angles import normalize_degree
from astrology.models import House
from astrology.rasi import sign_from_longitude


def _set_sidereal_mode() -> None:
    mode = getattr(Config, "SIDEREAL_MODE", "LAHIRI").upper()
    if mode == "LAHIRI":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif mode == "DELUCE":
        swe.set_sid_mode(swe.SIDM_DELUCE)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)


def calculate_houses(jd_ut: float, latitude: float, longitude: float, house_system: str = 'P') -> List[House]:
    _set_sidereal_mode()
    houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system.encode('ascii'), swe.FLG_SIDEREAL)
    result = []
    for index, cusp in enumerate(houses[:12], start=1):
        sign = sign_from_longitude(normalize_degree(cusp))
        result.append(House(number=index, cusp=normalize_degree(cusp), sign_index=sign['index'], sign_tamil=sign['sign_tamil'], sign_english=sign['sign_english']))
    return result


def calculate_ascendant(jd_ut: float, latitude: float, longitude: float, house_system: str = 'P') -> dict:
    _set_sidereal_mode()
    houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system.encode('ascii'), swe.FLG_SIDEREAL)
    asc = normalize_degree(ascmc[0])
    sign = sign_from_longitude(asc)
    # include raw ascendant longitude (full precision) for callers who need it
    sign["raw_longitude"] = asc
    return sign
