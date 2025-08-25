"""Developer tools: timeit, profile, bench, retry, safe_import, and more."""
import time
import importlib
import functools

def timeit(func, *args, **kwargs):
    """Time how long a function takes to run."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return end - start, result

def profile(func, *args, **kwargs):
    """Profile a function's execution time (alias for timeit)."""
    return timeit(func, *args, **kwargs)

def bench(func, n=1000):
    """Benchmark a function by running it n times."""
    start = time.time()
    for _ in range(n):
        func()
    end = time.time()
    return (end - start) / n

def retry(func, retries=3, exceptions=(Exception,), delay=0):
    """Retry a function up to retries times if exceptions occur."""
    for i in range(retries):
        try:
            return func()
        except exceptions:
            if i < retries - 1 and delay:
                time.sleep(delay)
    return None

def safe_import(package):
    """Safely import a package, return None if not found."""
    try:
        return importlib.import_module(package)
    except ImportError:
        return None
