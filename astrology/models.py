from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class BirthDetails:
    name: str
    gender: str
    date: str
    time: str
    latitude: float
    longitude: float
    timezone: str


@dataclass
class AdditionalDetails:
    kulam: str
    kothiram: str
    caste: str
    land: str
    work: str
    salary: int
    family_details: list


@dataclass
class AngleDMS:
    degree: int
    minute: int
    second: int


@dataclass
class PlanetPosition:
    name_tamil: str
    name_english: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float
    retrograde: bool
    sign_index: int
    sign_tamil: str
    sign_english: str
    degree: int
    minute: int
    second: int
    nakshatra: str
    nakshatra_index: int
    pada: int
    navamsa_pada: int
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Lagna:
    longitude: float
    sign_index: int
    sign_tamil: str
    sign_english: str
    degree: int
    minute: int
    second: int
    nakshatra: str
    pada: int
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NakshatraPosition:
    name: str
    index: int
    pada: int
    longitude: float
    position_in_nakshatra: float


@dataclass
class House:
    number: int
    cusp: float
    sign_index: int
    sign_tamil: str
    sign_english: str


@dataclass
class PanchangamResult:
    vara: str
    tithi: str
    paksha: str
    nakshatra: str
    yoga: str
    karana: str
    sunrise: str
    sunset: str
    moonrise: Optional[str]
    moonset: Optional[str]
    rahu_kalam: Optional[str]
    yamagandam: Optional[str]
    gulikai: Optional[str]
    abhijit: Optional[str]
    durmuhurtham: Optional[str]
    amritakalam: Optional[str]


@dataclass
class RasiChart:
    signs: List[Dict[str, Any]]
    houses: List[House]


@dataclass
class NavamsaChart:
    signs: List[Dict[str, Any]]
    planets: List[Dict[str, Any]]


@dataclass
class DasaPeriod:
    name: str
    start: datetime
    end: datetime
    level: str


@dataclass
class Horoscope:
    birth: BirthDetails
    julian_day_ut: float
    utc_datetime: datetime
    local_datetime: datetime
    ayanamsa: Dict[str, Any]
    lagna: Lagna
    planets: List[PlanetPosition]
    houses: List[House]
    rasi_chart: RasiChart
    navamsa_chart: NavamsaChart
    panchangam: PanchangamResult
    dasa: List[DasaPeriod]
    paava_chakram: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "birth": self.birth.__dict__,
            "julian_day_ut": self.julian_day_ut,
            "utc_datetime": self.utc_datetime.isoformat(),
            "local_datetime": self.local_datetime.isoformat(),
            "ayanamsa": self.ayanamsa,
            "lagna": self.lagna.__dict__,
            "planets": [p.__dict__ for p in self.planets],
            "houses": [h.__dict__ for h in self.houses],
            "rasi_chart": self.rasi_chart.__dict__,
            "navamsa_chart": self.navamsa_chart.__dict__,
            "panchangam": self.panchangam.__dict__,
            "dasa": [
                {
                    "name": d.name,
                    "start": d.start.isoformat(),
                    "end": d.end.isoformat(),
                    "level": d.level,
                }
                for d in self.dasa
            ],
        }
