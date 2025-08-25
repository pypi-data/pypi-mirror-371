from common_sense import why_none, why_empty, why_false, explain_type

def test_why_none():
    assert why_none(None) == "Because you never assigned it."
    assert why_none(1) == "It's not None."

def test_why_empty():
    assert why_empty([]) == "Because you forgot to fill it."
    assert why_empty([1]) == "It's not empty."

def test_why_false():
    assert why_false(False) == "Because it is literally False."
    assert why_false(True) == "It's not False."

def test_explain_type():
    assert explain_type(42) == 'int'
    assert explain_type('hi') == 'str'
