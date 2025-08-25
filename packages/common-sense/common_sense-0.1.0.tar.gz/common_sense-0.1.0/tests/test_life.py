import datetime
from common_sense import should_sleep, should_eat, caffeine_needed, hydration_reminder

def test_should_sleep():
    assert should_sleep(datetime.time(23, 0))
    assert not should_sleep(datetime.time(9, 0))

def test_should_eat():
    assert should_eat(8)
    assert not should_eat(3)

def test_caffeine_needed():
    assert caffeine_needed(0) == 'You need coffee.'
    assert caffeine_needed(2) == 'You could use another cup.'
    assert caffeine_needed(5) == 'Maybe switch to water.'

def test_hydration_reminder():
    assert isinstance(hydration_reminder(), str)
