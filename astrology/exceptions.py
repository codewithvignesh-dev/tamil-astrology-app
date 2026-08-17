class AstrologyError(Exception):
    pass


class InvalidBirthDataError(AstrologyError):
    pass


class InvalidCoordinatesError(AstrologyError):
    pass


class EphemerisError(AstrologyError):
    pass


class CalculationError(AstrologyError):
    pass
