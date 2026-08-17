from astrology.ephemeris import calculate_julian_day
from astrology.lagna import calculate_lagna
from astrology.time_utils import parse_birth_datetime

local_dt, utc_dt = parse_birth_datetime('2003-08-04', '11:05:00', 'Asia/Kolkata')
jd = calculate_julian_day(local_dt.year, local_dt.month, local_dt.day, local_dt.hour, local_dt.minute, local_dt.second, 'Asia/Kolkata')
lagna = calculate_lagna(jd, 8.764166, 78.134834)
print('local_dt:', local_dt)
print('utc_dt:', utc_dt)
print('lagna:', lagna)
