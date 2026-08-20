from flask import Blueprint, render_template, request
from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from calendar import monthrange
from astrology.models import BirthDetails
from astrology.angles import decimal_to_dms
from astrology.constants import SIGN_RULERS, PLANET_NAMES_TAMIL, DOB_to_DAY
from astrology.angles import decimal_to_dms
from astrology.nakshatra import calculate_tamil_solar_date
from services.horoscope_service import HoroscopeService
from astrology.exceptions import InvalidBirthDataError

web_blueprint = Blueprint("web", __name__)


def _parse_birth_details() -> BirthDetails:
    # Accept district name and map to lat/lon using data/districts.json
    name = request.form.get("name", "").strip()
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    timezone = request.form.get("timezone", "Asia/Kolkata").strip() or "Asia/Kolkata"
    district = request.form.get("district", "").strip()

    lat = 0.0
    lon = 0.0
    if district:
        data_path = Path(__file__).resolve().parents[1] / "data" / "districts.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                districts = json.load(f)
            for d in districts:
                if d.get("district", "").strip().lower() == district.lower():
                    lat = float(d.get("latitude", 0.0))
                    lon = float(d.get("longitude", 0.0))
                    break

    return BirthDetails(
        name=name,
        date=date,
        time=time,
        latitude=lat,
        longitude=lon,
        timezone=timezone,
    )

def _render_horoscope_template(birth_details: BirthDetails):
    service = HoroscopeService()
    horoscope_data = service.generate_horoscope(birth_details)

    planet_context = {}

    for planet in horoscope_data.planets:
        vakram = bool(planet.retrograde)

        if planet.name_english in ("Rahu", "Ketu"):
            vakram = not vakram

        full_deg, full_min, full_sec = decimal_to_dms(
            planet.longitude
        )

        planet_context[planet.name_tamil] = {
            "sign": planet.sign_tamil,
            "degree": {
                "degree": planet.degree,
                "minute": planet.minute,
            },
            "position": {
                "degree": full_deg,
                "minute": full_min,
            },
            "nakshatra": planet.nakshatra,
            "pada": planet.pada,
            "vakram": vakram,
            "retrograde": planet.retrograde,
        }

    moon = next(
        (
            p
            for p in horoscope_data.planets
            if p.name_english == "Moon"
        ),
        None,
    )

    moon_sign = moon.sign_tamil if moon else ""
    moon_pada = moon.pada if moon else ""

    raasi_adhipathi = ""
    lagna_adhipathi = ""

    if moon:
        ruler_key = SIGN_RULERS[moon.sign_index]
        raasi_adhipathi = PLANET_NAMES_TAMIL.get(
            ruler_key,
            ruler_key,
        )

    if horoscope_data.lagna:
        lagna_ruler_key = SIGN_RULERS[
            horoscope_data.lagna.sign_index
        ]

        lagna_adhipathi = PLANET_NAMES_TAMIL.get(
            lagna_ruler_key,
            lagna_ruler_key,
        )

    soorya_udhayam = (
        horoscope_data.panchangam.sunrise
        if getattr(
            horoscope_data.panchangam,
            "sunrise",
            None,
        )
        else ""
    )

    soorya_asthamanam = (
        horoscope_data.panchangam.sunset
        if getattr(
            horoscope_data.panchangam,
            "sunset",
            None,
        )
        else ""
    )

    dob = datetime.strptime(horoscope_data.birth.date, "%Y-%m-%d").strftime("%d-%b-%Y")
    tob = datetime.strptime(horoscope_data.birth.time, "%H:%M").strftime("%I:%M %p")
    day = datetime.strptime(horoscope_data.birth.date, "%Y-%m-%d").strftime("%A")
    day = DOB_to_DAY.get(day,day)
    try:
        birth_datetime = datetime.strptime(
            f"{horoscope_data.birth.date} {horoscope_data.birth.time}",
            "%Y-%m-%d %H:%M"
        )
        tamil_date_data = calculate_tamil_solar_date(
            birth_datetime=birth_datetime,
            latitude=horoscope_data.birth.latitude,
            longitude=horoscope_data.birth.longitude,
            timezone_name="Asia/Kolkata",
        )
        tamil_birth_date = tamil_date_data["formatted"]
    except Exception as e:
        print(f"Error calculating Tamil solar date: {e}")
    basic_details = {
        "dob": dob,
        "day": day,
        "tamil_birth_date": tamil_birth_date,
        "tob": tob,
        "raasi": moon_sign,
        "lagna": horoscope_data.lagna.sign_tamil,
        "pada": moon_pada,
        "raasi_adhipathi": raasi_adhipathi,
        "lagna_adhipathi": lagna_adhipathi,
        "soorya_udhayam": soorya_udhayam,
        "soorya_asthamanam": soorya_asthamanam,
    }

    rasi_chart = horoscope_data.rasi_chart
    paava_chakram = horoscope_data.paava_chakram

    sign_names_tamil = [
        "மேஷம்",
        "ரிஷபம்",
        "மிதுனம்",
        "கடகம்",
        "சிம்மம்",
        "கன்னி",
        "துலாம்",
        "விருச்சிகம்",
        "தனுசு",
        "மகரம்",
        "கும்பம்",
        "மீனம்",
    ]

    navamsa_signs = [
        {
            "sign_index": i,
            "sign_tamil": sign_names_tamil[i],
            "planets": [],
        }
        for i in range(12)
    ]

    navamsa_size = 30.0 / 9.0

    def get_navamsa_sign(longitude):
        longitude %= 360.0

        rasi_index = int(longitude / 30.0)
        degree_in_rasi = longitude % 30.0

        navamsa_index = int(
            degree_in_rasi / navamsa_size
        )

        if navamsa_index > 8:
            navamsa_index = 8

        if rasi_index in (0, 3, 6, 9):
            start_index = rasi_index
        elif rasi_index in (1, 4, 7, 10):
            start_index = (rasi_index + 8) % 12
        else:
            start_index = (rasi_index + 4) % 12

        return (start_index + navamsa_index) % 12

    planet_labels = {
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

    for planet in horoscope_data.planets:
        navamsa_sign_index = get_navamsa_sign(
            planet.longitude
        )

        planet_name = planet_labels.get(
            planet.name_tamil,
            planet.name_tamil,
        )

        navamsa_signs[
            navamsa_sign_index
        ]["planets"].append(
            planet_name
        )

    navamsa_lagna_sign_index = get_navamsa_sign(
        horoscope_data.lagna.longitude
    )

    navamsa_signs[
        navamsa_lagna_sign_index]["planets"].insert(
        0,
        "ல",
    )

    navamsa_chart = {
        "signs": navamsa_signs,
        "lagna_sign_index": navamsa_lagna_sign_index,
    }

    paava_chakram["sign_planets"] = {
        sign_index: [
            planet_labels.get(planet, planet)
            for planet in planets
        ]
        for sign_index, planets in paava_chakram["sign_planets"].items()
    }
    
    def remaining_ymd(start, end):
        years = end.year - start.year
        months = end.month - start.month
        days = end.day - start.day

        if days < 0:
            months -= 1

            previous_month = end.month - 1 or 12
            previous_year = end.year - (end.month == 1)

            days += monthrange(
                previous_year,
                previous_month
            )[1]

        if months < 0:
            years -= 1
            months += 12

        return years, months, days

    try:
        birth_datetime = datetime.strptime(
            f"{horoscope_data.birth.date} {horoscope_data.birth.time}",
            "%Y-%m-%d %H:%M"
        ).replace(
            tzinfo=ZoneInfo(horoscope_data.birth.timezone)
        )
        for dasha in horoscope_data.dasa:
            if dasha["start"] <= birth_datetime < dasha["end"]:

                years, months, days = remaining_ymd(
                    birth_datetime,
                    dasha["end"]
                )

                current_dasha = {
                    "planet": dasha["planet"],
                    "start": dasha["start"],
                    "end": dasha["end"],
                    "remaining_years": years,
                    "remaining_months": months,
                    "remaining_days": days,
                }
    except Exception as e:
        print(f"Error calculating current dasha: {e}")
    
    return render_template(
        "chart.html",
        name=horoscope_data.birth.name,
        lagna=horoscope_data.lagna,
        planets=planet_context,
        basic_details=basic_details,
        panchangam=horoscope_data.panchangam,
        rasi_chart=rasi_chart,
        navamsa_chart=navamsa_chart,
        paava_chart=paava_chakram,
        dasa=horoscope_data.dasa,
        current_dasha=current_dasha,
        planet_labels=planet_labels,
    )

@web_blueprint.route("/")
def index():
    # Load district list for the form so user only selects district name
        data_path = Path(__file__).resolve().parents[1] / "data" / "districts.json"
        districts = []
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                districts = [d.get("district") for d in json.load(f)]
    
        if request.method == "GET":
            return render_template("chart.html", districts=districts)


@web_blueprint.route("/chart", methods=["GET", "POST"])
def chart():
    # Load district list for the form so user only selects district name
    data_path = Path(__file__).resolve().parents[1] / "data" / "districts.json"
    districts = []
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            districts = [d.get("district") for d in json.load(f)]

    if request.method == "GET":
        return render_template("chart.html", districts=districts)

    try:
        birth_details = _parse_birth_details()
        return _render_horoscope_template(birth_details)
    except InvalidBirthDataError as exc:
        return render_template("error.html", message=str(exc))
    except Exception as e:
        return render_template("error.html", message="கணக்கீட்டில் பிழை ஏற்பட்டுள்ளது. தயவுசெய்து சரிபார்க்கவும்." + str(e),)


@web_blueprint.route("/horoscope", methods=["POST"])
def horoscope():
    try:
        birth_details = _parse_birth_details()
        return _render_horoscope_template(birth_details)
    except InvalidBirthDataError as exc:
        return render_template("error.html", message=str(exc))
    except Exception:
        return render_template(
            "error.html",
            message="கணக்கீட்டில் பிழை ஏற்பட்டுள்ளது. தயவுசெய்து தரவுகளை சரிபார்க்கவும்.",
        )


@web_blueprint.route("/panchangam")
def panchangam_form():
    return render_template("panchangam.html")


@web_blueprint.route("/panchangam", methods=["POST"])
def panchangam():
    try:
        birth_details = BirthDetails(
            name=request.form.get("name", "").strip(),
            date=request.form.get("date", ""),
            time=request.form.get("time", ""),
            latitude=float(request.form.get("latitude", "0")),
            longitude=float(request.form.get("longitude", "0")),
            timezone=request.form.get("timezone", "Asia/Kolkata").strip() or "Asia/Kolkata",
        )
        service = HoroscopeService()
        horoscope_data = service.generate_horoscope(birth_details)
        return render_template("panchangam.html", horoscope=horoscope_data)
    except InvalidBirthDataError as exc:
        return render_template("error.html", message=str(exc))
    except Exception:
        return render_template(
            "error.html",
            message="பஞ்சாங்கம் கணக்கிடும்போது பிழை ஏற்பட்டது. தரவை சரிபார்க்கவும்.",
        )
