from common_sense import obvious, wisdom, shrug, sarcastic, future_truth, agree, disagree

def test_obvious():
    assert obvious('water is wet').startswith('Obviously')

def test_wisdom():
    assert isinstance(wisdom(), str)
    assert len(wisdom()) > 0

def test_shrug():
    assert '¯\\_(ツ)_/¯' in shrug()
    assert '¯\\_(ツ)_/¯' in shrug('Oops')

def test_sarcastic():
    assert isinstance(sarcastic('test'), str)

def test_future_truth():
    assert isinstance(future_truth(), str)

def test_agree():
    possible = [
        f"Absolutely, Python is great.",
        f"I couldn't agree more: Python is great.",
        f"You nailed it: Python is great.",
        f"Preach! Python is great.",
        f"So true: Python is great."
    ]
    assert agree('Python is great') in possible

def test_disagree():
    possible = [
        f"I beg to differ: No way.",
        f"Not quite: No way.",
        f"I see it differently: No way.",
        f"That’s debatable: No way.",
        f"I respectfully disagree: No way."
    ]
    assert disagree('No way') in possible
