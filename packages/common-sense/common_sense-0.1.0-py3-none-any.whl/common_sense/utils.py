def rickroll():
    """Easter egg: Never gonna give you up!"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def magic_8ball(question=None):
    """Return a random Magic 8-Ball answer."""
    import random
    responses = [
        "It is certain.", "Ask again later.", "Don't count on it.", "Yes, definitely.",
        "My sources say no.", "Outlook not so good.", "Signs point to yes.", "Reply hazy, try again.",
        "Absolutely not.", "You wish!", "In your dreams.", "¯\\_(ツ)_/¯"
    ]
    return random.choice(responses)

def coin_flip():
    """Flip a coin and return 'Heads' or 'Tails'."""
    import random
    return random.choice(['Heads', 'Tails'])

def roll_dice(sides=6):
    """Roll a dice with a given number of sides."""
    import random
    return random.randint(1, sides)

def random_ascii_art():
    """Return a random piece of ASCII art."""
    import random
    arts = [
        r"""
  (\_/)
  ( •_•)
  / >🍪 Want a cookie?
        """,
        r"""
  (╯°□°）╯︵ ┻━┻
        """,
        r"""
  (•_•) ( •_•)>⌐■-■ (⌐■_■)
        """,
        r"""
  ─=≡Σ((( つ◕ل͜◕)つ
        """
    ]
    return random.choice(arts)

def answer_to_life():
    """Return the answer to life, the universe, and everything."""
    return 42

def sarcastic_bool(val):
    """Return a sarcastic True/False message."""
    return "Obviously True." if val else "Sure, keep telling yourself that."

def random_choice_weighted(choices, weights):
    """Return a random element from choices, weighted by weights."""
    import random
    return random.choices(choices, weights=weights, k=1)[0]

def uuid_short():
    """Return a short UUID string."""
    import uuid
    return str(uuid.uuid4())[:8]

def retry_call(fn, retries=3, exceptions=(Exception,), delay=0):
    """Retry a function call up to retries times if exceptions occur."""
    import time
    for i in range(retries):
        try:
            return fn()
        except exceptions:
            if i < retries - 1 and delay:
                time.sleep(delay)
    return None

def is_iterable(obj):
    """Return True if obj is iterable (not string)."""
    try:
        iter(obj)
        return not isinstance(obj, str)
    except Exception:
        return False

def print_banner(msg):
    """Print a fun ASCII banner around a message."""
    border = '*' * (len(msg) + 4)
    print(f"{border}\n* {msg} *\n{border}")

def self_destruct():
    """Pretends to delete everything. Easter egg!"""
    return "\U0001F4A5 Just kidding. Relax."

"""General utilities that are just common sense."""
def flatten(lst):
    """Flatten a list of lists into a single list.
    >>> flatten([[1,2],[3,4]])
    [1, 2, 3, 4]
    """
    return [item for sublist in lst for item in sublist]

def unique(lst):
    """Return a list of unique elements, preserving order.
    >>> unique([1,2,2,3])
    [1, 2, 3]
    """
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def chunk(lst, size):
    """Split lst into chunks of given size.
    >>> chunk([1,2,3,4,5], 2)
    [[1,2],[3,4],[5]]
    """
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def first(lst, default=None):
    """Return the first element or default if empty."""
    return lst[0] if lst else default

def last(lst, default=None):
    """Return the last element or default if empty."""
    return lst[-1] if lst else default

def is_sorted(lst):
    """Return True if the list is sorted."""
    return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))

def flatten_dict(d, parent_key='', sep='.'): 
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def deep_get(d, keys, default=None):
    """Get a value from nested dicts by a list of keys."""
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

def safe_get(lst, idx, default=None):
    """Safely get an index from a list."""
    try:
        return lst[idx]
    except Exception:
        return default

def safe_pop(lst, idx, default=None):
    """Safely pop an index from a list."""
    try:
        return lst.pop(idx)
    except Exception:
        return default

def safe_dict_get(d, key, default=None):
    """Safely get a key from a dict."""
    return d.get(key, default)

def safe_dict_pop(d, key, default=None):
    """Safely pop a key from a dict."""
    return d.pop(key, default)
