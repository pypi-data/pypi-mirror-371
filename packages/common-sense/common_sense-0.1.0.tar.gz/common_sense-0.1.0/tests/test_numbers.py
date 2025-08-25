from common_sense import safe_divide, percent, clamp, is_prime

def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0

def test_percent():
    assert percent(2, 8) == 25.0
    assert percent(1, 0) == 0.0

def test_clamp():
    assert clamp(5, 1, 10) == 5
    assert clamp(0, 1, 10) == 1
    assert clamp(20, 1, 10) == 10

def test_is_prime():
    assert is_prime(7)
    assert not is_prime(8)
