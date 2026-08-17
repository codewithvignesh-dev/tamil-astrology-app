from astrology.constants import SIGNS_TAMIL, SIGNS_ENGLISH
from astrology.angles import normalize_degree, degree_in_sign


def sign_from_longitude(longitude: float) -> dict:
    longitude = normalize_degree(longitude)
    index = int(longitude // 30)
    return {
        "index": index,
        "sign_tamil": SIGNS_TAMIL[index],
        "sign_english": SIGNS_ENGLISH[index],
        "degree": degree_in_sign(longitude),
    }


def navamsa_from_longitude(longitude: float) -> dict:
    longitude = normalize_degree(longitude)
    navamsa_size = 30.0 / 9.0
    sign_index = int(longitude // 30)
    position_in_sign = longitude % 30.0
    navamsa_index = int(position_in_sign / navamsa_size)
    navamsa_pada = int((position_in_sign % navamsa_size) / (navamsa_size / 4)) + 1

    navamsa_start = [
        0,  # Aries -> Aries
        3,  # Taurus -> Cancer
        2,  # Gemini -> Gemini
        5,  # Cancer -> Virgo
        4,  # Leo -> Leo
        7,  # Virgo -> Scorpio
        6,  # Libra -> Libra
        9,  # Scorpio -> Sagittarius
        8,  # Sagittarius -> Sagittarius
        11, # Capricorn -> Aquarius
        10, # Aquarius -> Aquarius
        0,  # Pisces -> Aries
    ]

    navamsa_sign_index = (navamsa_start[sign_index] + navamsa_index) % 12
    return {
        "sign_index": navamsa_sign_index,
        "sign_tamil": SIGNS_TAMIL[navamsa_sign_index],
        "sign_english": SIGNS_ENGLISH[navamsa_sign_index],
        "navamsa_number": navamsa_index + 1,
        "navamsa_pada": navamsa_pada,
        "degree_in_navamsa": round(position_in_sign % navamsa_size, 6),
    }
