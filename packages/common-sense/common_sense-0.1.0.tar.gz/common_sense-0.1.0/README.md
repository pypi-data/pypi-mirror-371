# 🤯 common-sense

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourname/common-sense)
[![Made with ❤️](https://img.shields.io/badge/made%20with-%E2%9D%A4-red)](https://python.org)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://python.org)

> This library prevents you from doing stupid things (sometimes).

## Installation

```bash
pip install common-sense
```

## Quick Usage

```python
from common_sense import *

# Dates
is_weekend(datetime.date.today())
days_until(datetime.date(2025, 12, 31))
pretty_date(datetime.date.today())
next_weekday('Monday')

# Debug
why_none(None)
why_empty([])
why_false(False)
explain_type(42)

# Philosophy
wisdom()
sarcastic('I love bugs')
shrug('It failed')
future_truth()
agree('Python is awesome')
disagree('Monday is the best')

# Life
should_sleep(datetime.time(23, 0))
should_eat(13)
caffeine_needed(0)
hydration_reminder()

# Strings
slugify('Hello World!')
humanize_number(1000)
camel_to_snake('CamelCase')
truncate('Hello world', 5)

# Numbers
safe_divide(10, 0)
percent(2, 8)
clamp(5, 1, 10)
is_prime(7)

# Utils
flatten([[1,2],[3,4]])
unique([1,2,2,3])
chunk([1,2,3,4,5], 2)
first([1,2,3])
last([1,2,3])
```

## Why?
Because common sense is not so common. Now it is — in Python!

---

## Fun Notes
- 100+ witty helpers and one-liners.
- "If it works, don’t touch it."
- "Don’t argue with code — it always wins."
- "This library prevents you from doing stupid things (sometimes)."

## Testing

```bash
pytest
```

---

## License
MIT