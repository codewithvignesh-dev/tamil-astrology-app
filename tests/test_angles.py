from astrology.angles import normalize_degree, decimal_to_dms, sign_index, degree_in_sign


def test_normalize_degree_wraps_to_360():
    assert normalize_degree(360.0) == 0.0
    assert normalize_degree(-1.0) == 359.0
    assert normalize_degree(720.5) == 0.5


def test_decimal_to_dms_handles_boundaries():
    assert decimal_to_dms(183.385277) == (183, 23, 7)
    assert decimal_to_dms(59.999999) == (59, 60, 0) or decimal_to_dms(59.999999) == (60, 0, 0)


def test_sign_index_and_degree_in_sign():
    assert sign_index(0.0) == 0
    assert sign_index(30.0) == 1
    assert degree_in_sign(30.0) == 0.0
    assert degree_in_sign(359.999) == 29.999
