from common_sense import flatten, unique, chunk, first, last

def test_flatten():
    assert flatten([[1,2],[3,4]]) == [1,2,3,4]

def test_unique():
    assert unique([1,2,2,3]) == [1,2,3]

def test_chunk():
    assert chunk([1,2,3,4,5], 2) == [[1,2],[3,4],[5]]

def test_first():
    assert first([1,2,3]) == 1
    assert first([]) is None

def test_last():
    assert last([1,2,3]) == 3
    assert last([]) is None
