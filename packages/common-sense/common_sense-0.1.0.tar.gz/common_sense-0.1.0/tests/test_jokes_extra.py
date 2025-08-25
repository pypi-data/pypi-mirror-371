from common_sense.jokes import random_python_joke, random_stackoverflow_joke, random_commit_message

def test_random_python_joke():
    assert isinstance(random_python_joke(), str)
    assert len(random_python_joke()) > 0

def test_random_stackoverflow_joke():
    assert isinstance(random_stackoverflow_joke(), str)
    assert len(random_stackoverflow_joke()) > 0

def test_random_commit_message():
    assert isinstance(random_commit_message(), str)
    assert len(random_commit_message()) > 0
