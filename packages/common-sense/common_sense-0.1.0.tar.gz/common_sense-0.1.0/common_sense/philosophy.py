"""Witty, wise, and sarcastic helpers for life and code."""
import random

def obvious(x):
    """Return a sarcastic 'obviously' statement about x.
    >>> obvious('water is wet')
    'Obviously, water is wet.'
    """
    return f"Obviously, {x}."

def wisdom():
    """Return a random piece of common sense wisdom."""
    return random.choice([
        "Don’t argue with code — it always wins.",
        "If it works, don’t touch it.",
        "Premature optimization is the root of all evil.",
        "Your code is fine, but reality disagrees.",
        "Read the docs. Then read them again.",
        "If you can't explain it simply, you don't understand it well enough.",
        "The best code is no code at all.",
        "Bugs love confident programmers.",
        "If you think nobody cares, try missing a few deadlines.",
        "The best debugger is a good night's sleep.",
        "You can’t fix stupid, but you can document it.",
        "If it was easy, it would already be done.",
        "The code you write today is the legacy you debug tomorrow.",
        "Always code as if the person who ends up maintaining your code is a violent psychopath who knows where you live.",
        "There are two hard things in computer science: cache invalidation, naming things, and off-by-one errors.",
        "A comment a day keeps the confusion away.",
        "If you don’t like testing your code, most likely your code won’t like being tested.",
        "The best way to get a project done faster is to start sooner.",
        "Weeks of coding can save you hours of planning.",
        "If you don’t know what you’re doing, do it neatly.",
        "The sooner you start to code, the longer the program will take.",
        "If you don’t make mistakes, you’re not working on hard enough problems.",
        "The only constant in software is change.",
        "If you want to go fast, go alone. If you want to go far, go together.",
        "Don’t repeat yourself. Unless you’re debugging.",
        "The best code is the one you never have to write.",
        "If you don’t document it, it doesn’t exist.",
        "The best way to predict the future is to invent it.",
        "If you want a job done right, automate it.",
        "If you want to make enemies, try to change something.",
        "If you want to keep a secret, don’t write it in code.",
        "If you want to be happy, lower your expectations.",
        "If you want to be successful, double your failure rate.",
        "If you want to be creative, remove all constraints.",
        "If you want to be productive, take more breaks.",
        "If you want to be healthy, sleep more.",
        "If you want to be rich, spend less than you earn.",
        "If you want to be wise, listen more than you speak.",
        "If you want to be loved, love yourself first.",
        "If you want to be respected, respect others.",
        "If you want to be trusted, tell the truth.",
        "If you want to be remembered, do something worth remembering.",
        "If you want to be happy, help others be happy.",
        "If you want to be lucky, work harder.",
        "If you want to be smart, ask more questions.",
        "If you want to be strong, face your fears.",
        "If you want to be brave, do something that scares you every day.",
        "If you want to be kind, be kind to yourself first.",
        "If you want to be patient, practice waiting.",
        "If you want to be grateful, count your blessings.",
        "If you want to be generous, give more than you take.",
        "If you want to be honest, admit your mistakes.",
        "If you want to be humble, remember you’re not the center of the universe.",
        "If you want to be wise, learn from your mistakes.",
        "If you want to be happy, let go of what you can’t control."
    ])

def shrug(msg=None):
    """Return a shrug emoji with an optional message."""
    if msg:
        return f"{msg} ¯\\_(ツ)_/¯"
    return "¯\\_(ツ)_/¯"

def sarcastic(msg):
    """Return a sarcastic version of the message."""
    responses = [
        f"Oh, really? {msg}",
        f"Wow, {msg}. Groundbreaking.",
        f"I'm shocked. {msg}",
        f"Sure, {msg}. Whatever you say.",
        f"If you say so: {msg}",
        f"Let me pretend to care: {msg}",
        f"Yawn... {msg}",
        f"Did you Google that yourself? {msg}",
        f"I’ll alert the media: {msg}",
        f"Congratulations, {msg} is now obvious."
    ]
    return random.choice(responses)

def future_truth():
    """Return a random 'future truth' statement."""
    return random.choice([
        "In the future, your code will still have bugs.",
        "Tomorrow’s problems are today’s typos.",
        "AI will not fix your spaghetti code.",
        "You will still forget a semicolon.",
        "The cloud is just someone else’s computer.",
        "You will still blame the compiler.",
        "You will still write TODOs you never fix.",
        "You will still debug with print().",
        "You will still forget to commit your code.",
        "You will still break production on a Friday."
    ])

def agree(msg):
    """Return a witty agreement with the message."""
    return random.choice([
        f"Absolutely, {msg}.",
        f"I couldn't agree more: {msg}.",
        f"You nailed it: {msg}.",
        f"Preach! {msg}.",
        f"So true: {msg}."
    ])

def disagree(msg):
    """Return a witty disagreement with the message."""
    return random.choice([
        f"I beg to differ: {msg}.",
        f"Not quite: {msg}.",
        f"I see it differently: {msg}.",
        f"That’s debatable: {msg}.",
        f"I respectfully disagree: {msg}."
    ])
