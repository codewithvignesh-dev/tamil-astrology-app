import swisseph as swe

from config import Config
from astrology.angles import normalize_degree, decimal_to_dms
from astrology.houses import calculate_ascendant, calculate_houses
from astrology.nakshatra import nakshatra_from_longitude
from astrology.rasi import sign_from_longitude


def _set_sidereal_mode() -> None:
    mode = getattr(Config, "SIDEREAL_MODE", "LAHIRI").upper()
    if mode == "LAHIRI":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif mode == "DELUCE":
        swe.set_sid_mode(swe.SIDM_DELUCE)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)


def calculate_lagna(jd_ut: float, latitude: float, longitude: float, house_system: str | None = None) -> dict:
    if house_system is None:
        house_system = getattr(Config, "HOUSE_SYSTEM", "P")

    _set_sidereal_mode()
    asc_sign = calculate_ascendant(jd_ut, latitude, longitude, house_system)
    # use the raw ascendant longitude (full precision) for nakshatra/pada
    ascendant = asc_sign.get("raw_longitude") if asc_sign.get("raw_longitude") is not None else normalize_degree(asc_sign["degree"] + asc_sign["index"] * 30.0)
    nakshatra = nakshatra_from_longitude(ascendant)
    houses = calculate_houses(jd_ut, latitude, longitude, house_system)

    # For display, compute DMS from the raw ascendant within its sign
    degree, minute, second = decimal_to_dms(ascendant % 30.0)

    return {
        "longitude": ascendant,
        "sign": asc_sign["sign_tamil"],
        "sign_index": asc_sign["index"],
        "degree": {"degree": degree, "minute": minute, "second": second},
        "nakshatra": nakshatra["name_tamil"],
        "pada": nakshatra["pada"],
        "houses": [house.cusp for house in houses],
    }
