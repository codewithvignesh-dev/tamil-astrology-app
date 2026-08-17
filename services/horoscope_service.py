from collections import Counter
from datetime import datetime
from typing import List

from astrology.constants import SIGNS_TAMIL, SIGNS_ENGLISH
from astrology.models import BirthDetails, Horoscope, Lagna, PlanetPosition, House, RasiChart, NavamsaChart, PanchangamResult, DasaPeriod
from astrology.ephemeris import calculate_julian_day, calculate_ayanamsa, calculate_planets, calculate_paava_chakram
from astrology.houses import calculate_houses
from astrology.lagna import calculate_lagna
from astrology.nakshatra import nakshatra_from_longitude, yoga_from_longitudes, thithi_from_longitudes, karana_from_longitudes, calculate_sunrise_sunset, calculate_vimshottari_dasha
from astrology.rasi import navamsa_from_longitude, sign_from_longitude
from astrology.time_utils import parse_birth_datetime
from astrology.exceptions import InvalidBirthDataError


class HoroscopeService:
    def _validate_birth_details(self, birth: BirthDetails) -> None:
        if not birth.name:
            raise InvalidBirthDataError("பெயர் தேவை.")
        if not birth.date:
            raise InvalidBirthDataError("பிறந்த தேதி தேவை.")
        if not birth.time:
            raise InvalidBirthDataError("பிறந்த நேரம் தேவை.")
        if not (-90.0 <= birth.latitude <= 90.0):
            raise InvalidBirthDataError("Latitude -90 to 90 இருக்க வேண்டும்.")
        if not (-180.0 <= birth.longitude <= 180.0):
            raise InvalidBirthDataError("Longitude -180 to 180 இருக்க வேண்டும்.")

    def _abbreviate_planet_labels(self, grouped_names: dict[int, list[str]]) -> dict[int, list[str]]:
        planet_label_map = {
            "சூரியன்": "சூ",
            "சந்திரன்": "சந்",
            "செவ்வாய்": "செ",
            "புதன்": "பு",
            "குரு": "கு",
            "சுக்கிரன்": "சுக்",
            "சனி": "சனி",
            "ராகு": "ரா",
            "கேது": "கே",
            "மாந்தி": "மா",
        }
        labels_by_sign = {}
        for sign_index, names in grouped_names.items():
            labels = [planet_label_map.get(name, name[:1]) for name in names]
            duplicate_letters = {label for label, count in Counter(labels).items() if count > 1}
            # produce base labels, but leave room to append markers (அ/வ) later
            base_labels = [
                (name[:2] if label in duplicate_letters else label)
                for name, label in zip(names, labels)
            ]
            # By default there are no markers here; markers will be added by caller when needed
            labels_by_sign[sign_index] = base_labels
        return labels_by_sign

    def generate_horoscope(self, birth: BirthDetails) -> Horoscope:
        self._validate_birth_details(birth)
        local_dt, utc_dt = parse_birth_datetime(birth.date, birth.time, birth.timezone)
        julian_day = calculate_julian_day(
            local_dt.year,
            local_dt.month,
            local_dt.day,
            local_dt.hour,
            local_dt.minute,
            local_dt.second,
            birth.timezone,
        )

        sunrise, sunset = calculate_sunrise_sunset(
            julian_day_ut=julian_day,
            latitude=birth.latitude,
            longitude=birth.longitude,  
            timezone_name=birth.timezone,
        )

        ayanamsa = calculate_ayanamsa(julian_day)
        planet_data = calculate_planets(julian_day, birth.latitude, birth.longitude, birth.timezone)
        lagna_data = calculate_lagna(julian_day, birth.latitude, birth.longitude)
        houses = calculate_houses(julian_day, birth.latitude, birth.longitude)
        paava_chakram = calculate_paava_chakram(jd_ut=julian_day, latitude=birth.latitude, longitude=birth.longitude, planets=planet_data,)
        rasi_grouped_names = {i: [] for i in range(12)}
        navamsa_grouped_names = {i: [] for i in range(12)}
        planet_flags_by_tamil: dict[str, dict[str, bool]] = {}

        asthangam_thresholds = {
            "Mercury": 11.0,
            "Venus": 10.0,
            "Mars": 6.0,
            "Jupiter": 12.0,
            "Saturn": 15.0,
        }

        sun_longitude = planet_data.get("Sun", {}).get("longitude", 0.0)
        moon_sidereal_longitude = planet_data["Moon"]["longitude"]
        dasa = calculate_vimshottari_dasha(
            birth_datetime=local_dt,
            moon_sidereal_longitude=moon_sidereal_longitude,
        )

        def _angle_diff(a: float, b: float) -> float:
            d = abs(a - b) % 360.0
            return d if d <= 180.0 else 360.0 - d

        for planet_key, planet in planet_data.items():
            sign = sign_from_longitude(planet["longitude"])
            nakshatra = nakshatra_from_longitude(planet["longitude"])
            navamsa = navamsa_from_longitude(planet["longitude"])
            # compute asthangam (combustion) based on distance from Sun (defaults above)
            asthangam = False
            if planet_key in asthangam_thresholds and "Sun" in planet_data:
                diff = _angle_diff(planet["longitude"], sun_longitude)
                asthangam = diff <= asthangam_thresholds[planet_key]
            # vakram flag follows retrograde; Ketu uses reversed logic
            vakram = bool(planet.get("retrograde", False))
            # Ketu and Rahu use reversed vakram logic
            if planet_key in ("Ketu", "Rahu"):
                vakram = not vakram
            planet["sign_tamil"] = sign["sign_tamil"]
            planet["sign_english"] = sign["sign_english"]
            planet["sign_index"] = sign["index"]
            planet["nakshatra"] = nakshatra["name_tamil"]
            planet["nakshatra_index"] = nakshatra["index"]
            planet["pada"] = nakshatra["pada"]
            planet["navamsa_sign_tamil"] = navamsa["sign_tamil"]
            planet["navamsa_sign_english"] = navamsa["sign_english"]
            planet["navamsa_sign_index"] = navamsa["sign_index"]
            planet["navamsa_number"] = navamsa["navamsa_number"]
            planet["navamsa_degree"] = navamsa["degree_in_navamsa"]
            planet["navamsa_pada"] = navamsa["navamsa_pada"]
            planet["asthangam"] = asthangam
            planet["vakram"] = vakram
            rasi_grouped_names[planet["sign_index"]].append(planet["name_tamil"])
            navamsa_grouped_names[planet["navamsa_sign_index"]].append(planet["name_tamil"])
            planet_flags_by_tamil[planet["name_tamil"]] = {"asthangam": asthangam, "vakram": vakram}

        rasi_base_labels = self._abbreviate_planet_labels(rasi_grouped_names)
        navamsa_base_labels = self._abbreviate_planet_labels(navamsa_grouped_names)

        # attach markers (அ for Asthangam, வ for Vakram) inside parentheses next to the label
        def _apply_markers(base_labels: dict[int, list[str]], grouped_names: dict[int, list[str]]) -> dict[int, list[str]]:
            final = {}
            for sign_idx, labels in base_labels.items():
                names = grouped_names.get(sign_idx, [])
                out = []
                for name, base in zip(names, labels):
                    flags = planet_flags_by_tamil.get(name, {})
                    markers = ""
                    if flags.get("asthangam"):
                        markers += "அ"
                    if flags.get("vakram"):
                        markers += "வ"
                    if markers:
                        out.append(f"{base}({markers})")
                    else:
                        out.append(base)
                final[sign_idx] = out
            return final

        rasi_labels = _apply_markers(rasi_base_labels, rasi_grouped_names)
        navamsa_labels = _apply_markers(navamsa_base_labels, navamsa_grouped_names)

        panchangam_nakshatra = planet_data["Moon"]["nakshatra"]
        yoga = yoga_from_longitudes(planet_data["Sun"]["longitude"], planet_data["Moon"]["longitude"])
        thithi = thithi_from_longitudes(planet_data["Sun"]["longitude"], planet_data["Moon"]["longitude"])
        karana = karana_from_longitudes(planet_data["Sun"]["longitude"], planet_data["Moon"]["longitude"])

        planets = [
            PlanetPosition(
                name_tamil=item["name_tamil"],
                name_english=item["name_english"],
                longitude=item["longitude"],
                latitude=item["latitude"],
                distance=item["distance"],
                speed_longitude=item["speed_longitude"],
                retrograde=item["retrograde"],
                sign_index=item["sign_index"],
                sign_tamil=item.get("sign_tamil", ""),
                sign_english=item.get("sign_english", ""),
                degree=item["degree"],
                    minute=item["minute"],
                    second=0,
                nakshatra=item.get("nakshatra", ""),
                nakshatra_index=item.get("nakshatra_index", -1),
                pada=item.get("pada", -1),
                navamsa_pada=item.get("navamsa_pada", -1),
                raw=item.get("raw", {}),
            )
            for item in planet_data.values()
        ]
        horoscope = Horoscope(
            birth=birth,
            julian_day_ut=julian_day,
            utc_datetime=utc_dt,
            local_datetime=local_dt,
            ayanamsa=ayanamsa,
            lagna=Lagna(
                longitude=lagna_data["longitude"],
                sign_index=lagna_data["sign_index"],
                sign_tamil=lagna_data["sign"],
                sign_english="",
                degree=lagna_data["degree"]["degree"],
                minute=lagna_data["degree"]["minute"],
                second=0,
                nakshatra=lagna_data["nakshatra"],
                pada=lagna_data["pada"],
                raw={"houses": lagna_data.get("houses", [])},
            ),
            planets=planets,
            houses=[House(number=i + 1, cusp=0.0, sign_index=0, sign_tamil="", sign_english="") for i in range(12)],
            rasi_chart=RasiChart(signs=[
                {
                    "sign_index": sign_index,
                    "sign_tamil": sign_name["sign_tamil"],
                    "sign_english": sign_name["sign_english"],
                    "planets": rasi_labels[sign_index],
                }
                for sign_index, sign_name in enumerate([
                    {"sign_tamil": "மேஷம்", "sign_english": "Aries"},
                    {"sign_tamil": "ரிஷபம்", "sign_english": "Taurus"},
                    {"sign_tamil": "மிதுனம்", "sign_english": "Gemini"},
                    {"sign_tamil": "கடகம்", "sign_english": "Cancer"},
                    {"sign_tamil": "சிம்மம்", "sign_english": "Leo"},
                    {"sign_tamil": "கன்னி", "sign_english": "Virgo"},
                    {"sign_tamil": "துலாம்", "sign_english": "Libra"},
                    {"sign_tamil": "விருச்சிகம்", "sign_english": "Scorpio"},
                    {"sign_tamil": "தனுசு", "sign_english": "Sagittarius"},
                    {"sign_tamil": "மகரம்", "sign_english": "Capricorn"},
                    {"sign_tamil": "கும்பம்", "sign_english": "Aquarius"},
                    {"sign_tamil": "மீனம்", "sign_english": "Pisces"},
                ])
            ], houses=houses),
            navamsa_chart=NavamsaChart(signs=[
                {
                    "sign_index": i,
                    "sign_tamil": SIGNS_TAMIL[i],
                    "sign_english": SIGNS_ENGLISH[i],
                    "planets": navamsa_labels[i],
                }
                for i in range(12)
            ], planets=[
                {
                    "planet": item["name_tamil"],
                    "planet_english": item["name_english"],
                    "navamsa_sign_index": item["navamsa_sign_index"],
                    "navamsa_sign_tamil": item["navamsa_sign_tamil"],
                    "navamsa_sign_english": item["navamsa_sign_english"],
                    "navamsa_number": item["navamsa_number"],
                    "navamsa_pada": item["navamsa_pada"],
                    "navamsa_degree": item["navamsa_degree"],
                }
                for item in planet_data.values()
            ]),
            paava_chakram=paava_chakram,
            panchangam=PanchangamResult(
                vara="",
                tithi=thithi["name_tamil"],
                paksha="",
                nakshatra=panchangam_nakshatra,
                yoga=yoga["name_tamil"],
                karana=karana["name_tamil"],
                sunrise=sunrise.strftime("%I:%M %p"),
                sunset=sunset.strftime("%I:%M %p"),
                moonrise=None,
                moonset=None,
                rahu_kalam=None,
                yamagandam=None,
                gulikai=None,
                abhijit=None,
                durmuhurtham=None,
                amritakalam=None,
            ),
            dasa=dasa,
        )
        return horoscope
