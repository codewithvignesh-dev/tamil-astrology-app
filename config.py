import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-please")
    TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
    SIDEREAL_MODE = os.environ.get("SIDEREAL_MODE", "LAHIRI")
    NODE_MODE = os.environ.get("NODE_MODE", "MEAN")
    HOUSE_SYSTEM = os.environ.get("HOUSE_SYSTEM", "P")
    EPHEMERIS_PATH = os.environ.get("EPHEMERIS_PATH", "./ephemeris")
    DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")
