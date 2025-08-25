from common_sense.ai import random_ai_name, ai_excuse, ai_easter_egg

def test_random_ai_name():
    assert isinstance(random_ai_name(), str)
    assert len(random_ai_name()) > 0

def test_ai_excuse():
    assert isinstance(ai_excuse(), str)
    assert len(ai_excuse()) > 0

def test_ai_easter_egg():
    assert ai_easter_egg() == "I'm sorry, Dave. I'm afraid I can't do that."
