from src.prelude.collections import *


def test_to_list():
  assert to_list(1,2,3,[4,5,6], (4,4,4), unique=True, sort=True) == [1,2,3,4,5,6]
  assert to_list([1,1,1],unique=True) == [1]
  assert to_list(DataFrame(dict(a=[1,2,3],b=[5,3,1])), field='b', sort=True) == [1,3,5]
  assert to_list([3,1,2,3,3,2,1],unique=True) == [3,1,2]
  assert to_list([3,1,2,3,3,2,1],sort=True,unique=True) == [1,2,3]
  assert to_list(['a','b',['c','d','e'],[],['e']], unique=True) == list('abcde')
  assert to_list(DataFrame(dict(a=[1,2,3]), index=['a','b','c'])) == ['a','b','c']
  assert to_list(DataFrame(dict(a=[1,2,3]), index=['a','b','c']), field='a') == [1,2,3]
  assert to_set(Series([1,2,3], index=['a','b','a'])) == {1,2,3}
  assert to_sorted_set(Series([4,2,10,10,2], index=['a','b','a', 'c', 'd'])) == {2, 4, 10}
  

def test_to_set():
  assert to_set(1,2,{1,2,3},[3,2,1]) == {1,2,3}
  assert to_set({3},{2},{10},1,[2,3,4], sort=True) == {1,2,3,4,10}


def test_pairwise():
  assert list(pairwise([1,2,3])) == [(1,2),(2,3)]


def test_venn_diagram():
  left,middle,right = venn_diagram([1,1,1,1,1],[22,3,3,2,3,2])
  assert left == {1}
  assert middle == set()
  assert right == {22,3,2}
  
  left,mid,right = venn_diagram(['a','b','c'],['c','d','a'])
  assert left == {'b'}
  assert mid == {'a','c'}
  assert right == {'d'}