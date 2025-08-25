"""String helpers that make sense (and sometimes nonsense)."""
import re

def slugify(text):
    """Convert text to a slug (lowercase, hyphens).
    >>> slugify('Hello World!')
    'hello-world'
    """
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def humanize_number(num):
    """Return a human-friendly string for a number.
    >>> humanize_number(1000)
    '1,000'
    """
    return f"{num:,}"

def camel_to_snake(name):
    """Convert CamelCase to snake_case.
    >>> camel_to_snake('CamelCase')
    'camel_case'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def truncate(text, length):
    """Truncate text to a given length, adding '...' if needed.
    >>> truncate('Hello world', 5)
    'He...'
    """
    if len(text) <= length:
        return text
    return text[:max(0, length-3)] + '...'

def is_palindrome(text):
    """Return True if text is a palindrome."""
    t = ''.join(c for c in text.lower() if c.isalnum())
    return t == t[::-1]

def reverse(text):
    """Return the reversed string."""
    return text[::-1]

def count_vowels(text):
    """Return the number of vowels in the text."""
    return sum(1 for c in text.lower() if c in 'aeiou')

def count_consonants(text):
    """Return the number of consonants in the text."""
    return sum(1 for c in text.lower() if c.isalpha() and c not in 'aeiou')

def is_upper(text):
    """Return True if all letters are uppercase."""
    return text.isupper()

def is_lower(text):
    """Return True if all letters are lowercase."""
    return text.islower()

def capitalize_words(text):
    """Capitalize the first letter of each word."""
    return ' '.join(w.capitalize() for w in text.split())

def swapcase(text):
    """Swap the case of all letters."""
    return text.swapcase()

def remove_digits(text):
    """Remove all digits from the text."""
    return ''.join(c for c in text if not c.isdigit())

def only_digits(text):
    """Return only the digits from the text."""
    return ''.join(c for c in text if c.isdigit())

def repeat(text, times):
    """Repeat the text a given number of times."""
    return text * times
