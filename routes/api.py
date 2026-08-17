from flask import Blueprint, jsonify, request
from astrology.models import BirthDetails
from services.horoscope_service import HoroscopeService
from astrology.exceptions import InvalidBirthDataError

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/health")
def health():
    return jsonify(
        status="ok",
        application="Tamil Astrology",
        ephemeris="available",
    )


@api_blueprint.route("/horoscope", methods=["POST"])
def api_horoscope():
    payload = request.get_json(silent=True) or {}
    try:
        birth_details = BirthDetails(
            name=payload.get("name", "").strip(),
            date=payload.get("date", ""),
            time=payload.get("time", ""),
            latitude=float(payload.get("latitude", 0)),
            longitude=float(payload.get("longitude", 0)),
            timezone=payload.get("timezone", "Asia/Kolkata").strip() or "Asia/Kolkata",
        )
        service = HoroscopeService()
        horoscope_data = service.generate_horoscope(birth_details)
        return jsonify(horoscope_data.to_dict())
    except (InvalidBirthDataError, ValueError) as exc:
        return jsonify(error="invalid_request", message=str(exc)), 400
    except Exception as e:
        return jsonify(error="server_error", message=f"அமைப்பில் பிழை ஏற்பட்டது.<br>{str(e)}"), 500
