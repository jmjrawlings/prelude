from src.prelude import *

def test_make():
  assert lst.make(1,2,3,[4,5,6], (4,4,4)) == [1,2,3,4,5,6,4,4,4]


def test_sort():
  assert lst.sort([3,1,2,3,3,2,1]) == [1,1,2,2,3,3,3]