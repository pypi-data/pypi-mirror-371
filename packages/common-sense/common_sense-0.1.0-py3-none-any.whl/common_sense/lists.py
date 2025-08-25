def random_sublist(lst, k):
    """Return a random sublist of length k."""
    return random.sample(lst, k) if lst and k <= len(lst) else []

def split_by_value(lst, value):
    """Split list into sublists at each occurrence of value."""
    out, temp = [], []
    for x in lst:
        if x == value:
            out.append(temp)
            temp = []
        else:
            temp.append(x)
    out.append(temp)
    return out

def interleave(*lists):
    """Interleave multiple lists together."""
    return [x for t in zip(*lists) for x in t]

def remove_duplicates(lst):
    """Remove duplicates from a list, preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def pad_list(lst, size, fill=None):
    """Pad a list to a given size with fill value."""
    return lst + [fill] * (size - len(lst)) if len(lst) < size else lst[:size]
"""List utilities: flatten, unique, chunk, shuffle, pairwise, and more!"""
import random
from itertools import tee

def flatten(lst):
    """Flatten a list of lists into a single list."""
    return [item for sublist in lst for item in sublist]

def unique(lst):
    """Return a list of unique elements, preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def chunk(lst, size):
    """Split lst into chunks of given size."""
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def shuffle(lst):
    """Return a shuffled copy of the list."""
    out = lst[:]
    random.shuffle(out)
    return out

def pairwise(lst):
    """Return pairs of consecutive elements."""
    a, b = tee(lst)
    next(b, None)
    return list(zip(a, b))

def first(lst, default=None):
    """Return the first element or default if empty."""
    return lst[0] if lst else default

def last(lst, default=None):
    """Return the last element or default if empty."""
    return lst[-1] if lst else default

def count_occurrences(lst, value):
    """Count how many times value appears in lst."""
    return lst.count(value)

def remove_all(lst, value):
    """Remove all occurrences of value from lst."""
    return [x for x in lst if x != value]

def rotate(lst, n):
    """Rotate list n steps to the right."""
    n = n % len(lst) if lst else 0
    return lst[-n:] + lst[:-n] if lst else []

def flatten_once(lst):
    """Flatten one level of nesting."""
    return [item for sublist in lst for item in (sublist if isinstance(sublist, list) else [sublist])]

def is_sorted(lst):
    """Return True if the list is sorted."""
    return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))

def all_equal(lst):
    """Return True if all elements are equal."""
    return all(x == lst[0] for x in lst) if lst else True

def random_element(lst):
    """Return a random element from the list."""
    return random.choice(lst) if lst else None
