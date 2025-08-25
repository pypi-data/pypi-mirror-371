import datetime
import pytest
from common_sense import is_weekend, days_until, pretty_date, next_weekday

def test_is_weekend():
    assert is_weekend(datetime.date(2023, 8, 26))
    assert not is_weekend(datetime.date(2023, 8, 23))

def test_days_until():
    today = datetime.date.today()
    assert days_until(today) == 0
    assert days_until(today + datetime.timedelta(days=5)) == 5

def test_pretty_date():
    d = datetime.date(2023, 8, 26)
    assert pretty_date(d).startswith('Saturday')

def test_next_weekday():
    monday = next_weekday('Monday')
    assert monday.weekday() == 0
