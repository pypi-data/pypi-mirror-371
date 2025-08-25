from common_sense import slugify, humanize_number, camel_to_snake, truncate

def test_slugify():
    assert slugify('Hello World!') == 'hello-world'

def test_humanize_number():
    assert humanize_number(1000) == '1,000'

def test_camel_to_snake():
    assert camel_to_snake('CamelCase') == 'camel_case'

def test_truncate():
    assert truncate('Hello world', 5) == 'He...'
    assert truncate('Hi', 5) == 'Hi'
