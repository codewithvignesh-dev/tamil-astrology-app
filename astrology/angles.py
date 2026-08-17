from typing import Tuple


def normalize_degree(value: float) -> float:
    value = value % 360.0
    if value < 0:
        value += 360.0
    return value


def sign_index(longitude: float) -> int:
    longitude = normalize_degree(longitude)
    return int(longitude // 30)


def degree_in_sign(longitude: float) -> float:
    longitude = normalize_degree(longitude)
    return round(longitude % 30.0, 6)


def decimal_to_dms(value: float) -> Tuple[int, int, int]:
    value = max(0.0, abs(value))
    degree = int(value)
    minutes_full = (value - degree) * 60.0
    minute = int(minutes_full)
    second = round((minutes_full - minute) * 60.0)
    if second >= 60:
        second -= 60
        minute += 1
    if minute >= 60:
        minute -= 60
        degree += 1
    return degree, minute, second


def longitude_to_dms(longitude: float) -> Tuple[int, int, int]:
    longitude = normalize_degree(longitude)
    return decimal_to_dms(longitude)
