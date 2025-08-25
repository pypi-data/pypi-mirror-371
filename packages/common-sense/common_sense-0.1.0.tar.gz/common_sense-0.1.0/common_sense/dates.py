"""Date utilities that feel like common sense."""
import datetime
import random

def is_weekend(date):
    """Return True if the date is a weekend (Saturday or Sunday).
    >>> is_weekend(datetime.date(2023, 8, 26))
    True
    """
    return date.weekday() >= 5

def days_until(date):
    """Return the number of days from today until the given date.
    >>> days_until(datetime.date.today() + datetime.timedelta(days=3))
    3
    """
    today = datetime.date.today()
    delta = date - today
    return max(delta.days, 0)

def pretty_date(date):
    """Return a human-friendly string for the date.
    >>> pretty_date(datetime.date(2023, 8, 26))
    'Saturday, August 26, 2023'
    """
    return date.strftime('%A, %B %d, %Y')

def next_weekday(dayname):
    """Return the next date for the given weekday name (e.g. 'Monday').
    >>> next_weekday('Monday')
    datetime.date(...)
    """
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    today = datetime.date.today()
    target = days.index(dayname.capitalize())
    days_ahead = (target - today.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + datetime.timedelta(days=days_ahead)

# 20+ more fun date helpers

def is_today(date):
    """Return True if the date is today."""
    return date == datetime.date.today()

def is_past(date):
    """Return True if the date is in the past."""
    return date < datetime.date.today()

def is_future(date):
    """Return True if the date is in the future."""
    return date > datetime.date.today()

def random_date(start, end):
    """Return a random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))

def weekday_name(date):
    """Return the weekday name for the date."""
    return date.strftime('%A')

def is_leap_year(year):
    """Return True if the year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year, month):
    """Return the number of days in a given month."""
    if month == 12:
        next_month = datetime.date(year+1, 1, 1)
    else:
        next_month = datetime.date(year, month+1, 1)
    this_month = datetime.date(year, month, 1)
    return (next_month - this_month).days

def add_days(date, days):
    """Return a new date with days added."""
    return date + datetime.timedelta(days=days)

def subtract_days(date, days):
    """Return a new date with days subtracted."""
    return date - datetime.timedelta(days=days)

def start_of_week(date):
    """Return the Monday of the week for the given date."""
    return date - datetime.timedelta(days=date.weekday())

def end_of_week(date):
    """Return the Sunday of the week for the given date."""
    return date + datetime.timedelta(days=(6 - date.weekday()))

def is_monday(date):
    """Return True if the date is a Monday."""
    return date.weekday() == 0

def is_friday(date):
    """Return True if the date is a Friday."""
    return date.weekday() == 4

def days_ago(days):
    """Return the date N days ago from today."""
    return datetime.date.today() - datetime.timedelta(days=days)

def days_from_now(days):
    """Return the date N days from today."""
    return datetime.date.today() + datetime.timedelta(days=days)

def random_weekday():
    """Return a random weekday name."""
    return random.choice(['Monday','Tuesday','Wednesday','Thursday','Friday'])

def random_weekend():
    """Return a random weekend day name."""
    return random.choice(['Saturday','Sunday'])

def is_workday(date):
    """Return True if the date is a workday (Mon-Fri)."""
    return date.weekday() < 5
