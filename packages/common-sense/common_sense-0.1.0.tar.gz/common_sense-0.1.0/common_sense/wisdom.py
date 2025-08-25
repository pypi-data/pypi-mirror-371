"""Wisdom, daily quotes, Zen of Python plus, and more."""
import random

def random_wisdom():
    """Return a random piece of wisdom."""
    return random.choice([
        "Don’t argue with code — it always wins.",
        "If it works, don’t touch it.",
        "Premature optimization is the root of all evil.",
        "Your code is fine, but reality disagrees.",
        "Read the docs. Then read them again.",
        "The best code is no code at all.",
        "Bugs love confident programmers.",
        "If you think nobody cares, try missing a few deadlines.",
        "The best debugger is a good night's sleep.",
        "You can’t fix stupid, but you can document it."
    ])

def daily_quote():
    """Return a daily quote (rotates by day)."""
    quotes = [
        "Code is like humor. When you have to explain it, it’s bad.",
        "Simplicity is the soul of efficiency.",
        "Before software can be reusable it first has to be usable.",
        "Make it work, make it right, make it fast.",
        "Deleted code is debugged code."
    ]
    import datetime
    return quotes[datetime.date.today().day % len(quotes)]

def zen_of_python_plus():
    """Return a Zen of Python line with a twist."""
    return random.choice([
        "Beautiful is better than ugly. Unless it’s legacy code.",
        "Explicit is better than implicit. Except in regex.",
        "Simple is better than complex. Unless you’re bored.",
        "Complex is better than complicated. Unless you wrote it.",
        "Flat is better than nested. Unless you love recursion."
    ])

def overengineer_tip():
    """Return a tip for overengineering (sarcastic)."""
    return random.choice([
        "Add another layer of abstraction.",
        "Rewrite it in Rust.",
        "Use microservices for everything.",
        "Add a blockchain.",
        "Invent a new framework."
    ])

def common_sense_law():
    """Return a law of common sense."""
    return random.choice([
        "If it’s stupid and it works, it’s not stupid.",
        "Never test for an error you don’t know how to handle.",
        "The best way to finish a project is to stop working on it.",
        "If you can’t fix it, feature it.",
        "The first 90% of the code accounts for the first 90% of the development time. The remaining 10% accounts for the other 90%."
    ])
