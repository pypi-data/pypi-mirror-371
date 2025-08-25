"""Debugging helpers that tell you what you should have known."""
import types

def why_none(x):
    """Explain why a value is None.
    >>> why_none(None)
    'Because you never assigned it.'
    """
    if x is not None:
        return "It's not None."
    return "Because you never assigned it."

def why_empty(x):
    """Explain why a value is empty (list, string, etc).
    >>> why_empty([])
    'Because you forgot to fill it.'
    """
    if x:
        return "It's not empty."
    return "Because you forgot to fill it."

def why_false(x):
    """Explain why a value is False.
    >>> why_false(False)
    'Because it is literally False.'
    """
    if x:
        return "It's not False."
    return "Because it is literally False."

def explain_type(x):
    """Return the type of x as a string.
    >>> explain_type(42)
    'int'
    """
    return type(x).__name__

def is_iterable(x):
    """Return True if x is iterable (but not a string)."""
    return isinstance(x, (list, tuple, set, dict)) or hasattr(x, '__iter__') and not isinstance(x, str)

def is_callable(x):
    """Return True if x is callable."""
    return callable(x)

def is_module(x):
    """Return True if x is a module."""
    return isinstance(x, types.ModuleType)

def is_class(x):
    """Return True if x is a class."""
    return isinstance(x, type)

def is_function(x):
    """Return True if x is a function."""
    return isinstance(x, types.FunctionType)

def is_method(x):
    """Return True if x is a method."""
    return isinstance(x, types.MethodType)

def is_generator(x):
    """Return True if x is a generator."""
    return hasattr(x, '__iter__') and not hasattr(x, '__len__') and not isinstance(x, str)

def is_truthy(x):
    """Return True if x is truthy."""
    return bool(x)

def is_falsy(x):
    """Return True if x is falsy."""
    return not bool(x)

def debug_len(x):
    """Return the length of x, or None if not applicable."""
    try:
        return len(x)
    except Exception:
        return None

def debug_dir(x):
    """Return dir(x) as a list."""
    return dir(x)

def debug_id(x):
    """Return the id of x."""
    return id(x)

def debug_repr(x):
    """Return the repr of x."""
    return repr(x)

def debug_str(x):
    """Return the str of x."""
    return str(x)
