from common_sense.utils import random_choice_weighted, uuid_short, retry_call, is_iterable, print_banner

def test_random_choice_weighted():
    choices = ['a', 'b', 'c']
    weights = [0, 0, 1]
    assert random_choice_weighted(choices, weights) == 'c'

def test_uuid_short():
    val = uuid_short()
    assert isinstance(val, str)
    assert len(val) == 8

def test_retry_call_success():
    def f(): return 42
    assert retry_call(f) == 42

def test_retry_call_fail():
    def f(): raise ValueError('fail')
    assert retry_call(f, retries=2, exceptions=(ValueError,)) is None

def test_is_iterable():
    assert is_iterable([1,2,3])
    assert not is_iterable('abc')
    assert not is_iterable(42)

def test_print_banner(capsys):
    print_banner('Hello')
    out = capsys.readouterr().out
    assert '*' in out and 'Hello' in out
