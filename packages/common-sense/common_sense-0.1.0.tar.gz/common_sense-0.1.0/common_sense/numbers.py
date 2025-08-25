"""Number helpers that make sense (and cents)."""
def safe_divide(a, b, default=0):
    """Safely divide a by b, return default if b is zero.
    >>> safe_divide(10, 2)
    5.0
    >>> safe_divide(10, 0)
    0
    """
    try:
        return a / b
    except Exception:
        return default

def percent(part, whole):
    """Return the percentage of part out of whole.
    >>> percent(2, 8)
    25.0
    """
    if whole == 0:
        return 0.0
    return (part / whole) * 100

def clamp(value, min_val, max_val):
    """Clamp value between min_val and max_val.
    >>> clamp(5, 1, 10)
    5
    >>> clamp(0, 1, 10)
    1
    """
    return max(min_val, min(value, max_val))

def is_prime(n):
    """Return True if n is a prime number.
    >>> is_prime(7)
    True
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_even(n):
    """Return True if n is even."""
    return n % 2 == 0

def is_odd(n):
    """Return True if n is odd."""
    return n % 2 == 1

def factorial(n):
    """Return the factorial of n."""
    if n < 0:
        return None
    result = 1
    for i in range(2, n+1):
        result *= i
    return result

def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n < 0:
        return None
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def average(lst):
    """Return the average of a list of numbers."""
    if not lst:
        return 0
    return sum(lst) / len(lst)

def median(lst):
    """Return the median of a list of numbers."""
    n = len(lst)
    if n == 0:
        return 0
    s = sorted(lst)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid-1] + s[mid]) / 2
    return s[mid]

def mode(lst):
    """Return the mode of a list of numbers."""
    from collections import Counter
    if not lst:
        return None
    c = Counter(lst)
    return c.most_common(1)[0][0]

def range_inclusive(start, end):
    """Return a list from start to end, inclusive."""
    return list(range(start, end+1))

def sum_digits(n):
    """Return the sum of the digits of n."""
    return sum(int(d) for d in str(abs(n)))

def digits(n):
    """Return a list of the digits of n."""
    return [int(d) for d in str(abs(n))]

def gcd(a, b):
    """Return the greatest common divisor of a and b."""
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a, b):
    """Return the least common multiple of a and b."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)
