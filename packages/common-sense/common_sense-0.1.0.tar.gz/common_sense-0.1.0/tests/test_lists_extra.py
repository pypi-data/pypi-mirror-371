from common_sense.lists import random_sublist, split_by_value, interleave, remove_duplicates, pad_list

def test_random_sublist():
    lst = [1,2,3,4,5]
    out = random_sublist(lst, 3)
    assert len(out) == 3
    assert all(x in lst for x in out)

def test_split_by_value():
    assert split_by_value([1,0,2,0,3], 0) == [[1],[2],[3]]

def test_interleave():
    assert interleave([1,2,3],[4,5,6]) == [1,4,2,5,3,6]

def test_remove_duplicates():
    assert remove_duplicates([1,2,2,3,1]) == [1,2,3]

def test_pad_list():
    assert pad_list([1,2], 4, 0) == [1,2,0,0]
    assert pad_list([1,2,3,4], 2) == [1,2]
