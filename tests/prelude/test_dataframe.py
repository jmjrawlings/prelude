from src.prelude.pandas_utils import *
from src.prelude.list_utils import *
from src.prelude.set_utils import *

def test_to_list():
  assert to_list(DataFrame(dict(a=[1,2,3]), index=['a','b','c'])) == ['a','b','c']
  assert to_list(DataFrame(dict(a=[1,2,3]), index=['a','b','c']), field='a') == [1,2,3]
  assert to_list(DataFrame(dict(a=[1,2,3],b=[5,3,1])), field='b', sort=True) == [1,3,5]

def test_to_set():
  assert to_set(Series([1,2,3], index=['a','b','a'])) == {1,2,3}
  assert to_sorted_set(Series([4,2,10,10,2], index=['a','b','a', 'c', 'd'])) == {2, 4, 10}