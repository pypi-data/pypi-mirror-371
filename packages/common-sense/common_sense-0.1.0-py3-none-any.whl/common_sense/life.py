"""Life helpers for the obvious and not-so-obvious moments."""
import random
import datetime

def should_sleep(time):
    """Return True if it's a good time to sleep (after 10pm or before 6am).
    >>> should_sleep(datetime.time(23, 0))
    True
    """
    return time.hour >= 22 or time.hour < 6

def should_eat(hour):
    """Return True if it's a common meal time (7-9am, 12-2pm, 6-8pm).
    >>> should_eat(13)
    True
    """
    return 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 20

def caffeine_needed(cups):
    """Return a witty response about caffeine needs.
    >>> caffeine_needed(0)
    'You need coffee.'
    """
    if cups == 0:
        return "You need coffee."
    elif cups < 3:
        return "You could use another cup."
    else:
        return "Maybe switch to water."

def hydration_reminder():
    """Return a random hydration reminder."""
    return random.choice([
        "Drink water!",
        "Stay hydrated!",
        "Your brain is 75% water.",
        "Hydration is key to debugging.",
        "Water: the original energy drink."
    ])

def should_exercise(day):
    """Return True if it's not a weekend (so you should exercise)."""
    return day.weekday() < 5

def is_hungry(last_meal_hours_ago):
    """Return True if it's been more than 4 hours since last meal."""
    return last_meal_hours_ago > 4

def is_thirsty(last_water_hours_ago):
    """Return True if it's been more than 2 hours since last water."""
    return last_water_hours_ago > 2

def nap_time(hour):
    """Return True if it's a good time for a nap (2-4pm)."""
    return 14 <= hour <= 16

def should_work(today):
    """Return True if today is a weekday."""
    return today.weekday() < 5

def should_relax(today):
    """Return True if today is a weekend."""
    return today.weekday() >= 5

def random_life_tip():
    """Return a random life tip."""
    return random.choice([
        "Take a break!",
        "Go for a walk.",
        "Call a friend.",
        "Eat something healthy.",
        "Stretch your legs."
    ])

def is_bored(activity_count):
    """Return True if activity count is low (<=1)."""
    return activity_count <= 1

def is_overworked(hours):
    """Return True if working more than 9 hours."""
    return hours > 9

def should_meditate(stress_level):
    """Return True if stress level is high (>7)."""
    return stress_level > 7

def random_excuse():
    """Return a random common excuse."""
    return random.choice([
        "My code was working yesterday.",
        "It works on my machine.",
        "I thought you were handling that.",
        "I must have missed that email.",
        "I was just about to do that."
    ])
