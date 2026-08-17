import pytest
from astrology.models import BirthDetails
from services.horoscope_service import HoroscopeService
from astrology.exceptions import InvalidBirthDataError


def test_horoscope_service_validation():
    service = HoroscopeService()
    with pytest.raises(InvalidBirthDataError):
        service.generate_horoscope(BirthDetails(name="", date="2002-08-10", time="05:30:00", latitude=10.0, longitude=78.0, timezone="Asia/Kolkata"))


def test_horoscope_service_generates_horoscope():
    service = HoroscopeService()
    birth = BirthDetails(name="Test", date="2002-08-10", time="05:30:00", latitude=10.7905, longitude=78.7047, timezone="Asia/Kolkata")
    horoscope = service.generate_horoscope(birth)
    assert horoscope.birth.name == "Test"
    assert horoscope.lagna.sign_tamil != ""
    assert len(horoscope.planets) == 9
    assert horoscope.panchangam.nakshatra != ""
    assert horoscope.panchangam.yoga != ""
    assert len(horoscope.rasi_chart.signs) == 12
    assert len(horoscope.navamsa_chart.planets) == 9
    assert horoscope.navamsa_chart.planets[0]["navamsa_pada"] >= 1
    assert 1 <= horoscope.navamsa_chart.planets[0]["navamsa_pada"] <= 4
