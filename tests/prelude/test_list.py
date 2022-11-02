from src.prelude import *


def test_to_list():
  assert to_list(1,2,3,[4,5,6], (4,4,4), unique=True, sort=True) == [1,2,3,4,5,6]
  assert to_list([1,1,1],unique=True) == [1]
  assert to_list([3,1,2,3,3,2,1],unique=True) == [3,1,2]
  assert to_list([3,1,2,3,3,2,1],sort=True,unique=True) == [1,2,3]
  assert to_list(['a','b',['c','d','e'],[],['e']], unique=True) == list('abcde')
