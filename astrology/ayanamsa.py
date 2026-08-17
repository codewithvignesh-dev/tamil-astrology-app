from typing import Dict, Any
import swisseph as swe

from astrology.angles import decimal_to_dms
from astrology.constants import SIDEREAL_MODES
from astrology.exceptions import EphemerisError


def get_ayanamsa(jd_ut: float, sidereal_mode: str = "LAHIRI") -> Dict[str, Any]:
    try:
        if sidereal_mode.upper() == "LAHIRI":
            sid_mode = swe.SIDM_LAHIRI
        elif sidereal_mode.upper() == "DELUCE":
            sid_mode = swe.SIDM_DELUCE
        else:
            sid_mode = swe.SIDM_LAHIRI
        ayanamsa = swe.get_ayanamsa_ut(jd_ut, sid_mode)
        d, m, s = decimal_to_dms(ayanamsa)
        return {
            "degrees": ayanamsa,
            "dms": {"degree": d, "minute": m, "second": s},
            "mode": sidereal_mode,
        }
    except Exception as exc:
        raise EphemerisError("Ayanamsa calculation failed") from exc
